import walrus
import uuid
import random
from json import JSONEncoder
'''
In order to use this module, the builtin identifier `builtins.walrusconn`
must be set to a correct connection to redis. This can be done by calling:

`builtins.walrus_conn = walrus.Database.from_url(<REDIS_URL>)`
'''

DEFAULT_ARENA_SIZE = 1000
BALL_TYPES = ["normal"]
MIN_SPEED = 50
MAX_SPEED = 150
NULL_UUID = uuid.uuid4()


def update_ball(id: uuid.UUID, pos: dict, vec: dict):
    ball = Ball.load(id)
    ball.position['x'] = int(pos['x'])
    ball.position['y'] = int(pos['y'])
    ball.vector['x'] = vec['x']
    ball.vector['y'] = vec['y']
    ball.save()


def as_int(obj) -> int:
    return int(obj.decode('utf-8'))


class Ball(walrus.Model):
    @staticmethod
    def new():
        ball = Ball.create(
            id=uuid.uuid4(),
            ballType=random.choice(BALL_TYPES)
        )
        ball.vector['x'] = random.randint(MIN_SPEED, MAX_SPEED) * random.choice([-1, 1])
        ball.vector['y'] = random.randint(MIN_SPEED, MAX_SPEED) * random.choice([-1, 1])
        ball.position['x'] = 500 + as_int(ball.vector['x'])
        ball.position['y'] = 500 + as_int(ball.vector['y'])
        ball.save()
        return Ball.load(ball.id)

    def to_json(self):
        '''Recursively convert fields to json-friendly output.

        Return a dict with the following schema:
        {
          id: "uuid",
          pos: {
            x: int,
            y: int,
            },
          vec: {
            x: int,
            y: int,
            },
          type: "ballType"
        }
        '''
        return dict(
                id=str(self.id),
                pos=dict(
                    x=as_int(self.position['x']),
                    y=as_int(self.position['y'])),
                vec=dict(
                    x=as_int(self.vector['x']),
                    y=as_int(self.vector['y'])),
                type=self.ballType
                )

    __database__ = walrus_conn
    id = walrus.UUIDField(primary_key=True, index=True)
    position = walrus.HashField()
    vector = walrus.HashField()
    ballType = walrus.TextField()


class Player(walrus.Model):
    @staticmethod
    def new(session_id=uuid.uuid4(), user="DUMMY") -> 'Player':
        player = Player.create(
            id=uuid.uuid4(),
            room=NULL_UUID,
            username=user,
            score=0,
        )
        player.paddle['x'] = 500
        player.paddle['y'] = 500
        player.save()
        return Player.load(player.id)

    def set_room(self, room: uuid.UUID) -> 'Player':
        self.room = room
        self.save()
        return Player.load(self.id)

    def to_json(self):
        '''Recursively convert fields to json-friendly output.

        Return a dict with the following schema:
        {
          id: "uuid",
          score: int,
          paddle: {
            x: int,
            y: int,
            },
        }
        '''
        return dict(
                id=str(self.id),
                score=self.score,
                paddle=dict(
                    x=as_int(self.paddle['x']),
                    y=as_int(self.paddle['y']),
                    ),
                )

    __database__ = walrus_conn
    id = walrus.UUIDField(primary_key=True, index=True)
    room = walrus.UUIDField()
    username = walrus.TextField()
    score = walrus.IntegerField()
    paddle = walrus.HashField()
    # TODO: reginfo = walrus.HashField()


class Room(walrus.Model):
    @staticmethod
    def new() -> 'Room':
        room = Room.create(
            id=uuid.uuid4()
        )
        return room

    def add_player(self, player) -> Player:
        '''Add a player to the room by id or instance and set their room field.

        Return the updated Player instance loaded from redis.
        id -- Type uuid.UUID or Player
        '''
        if not (isinstance(player, Player) or isinstance(player, uuid.UUID)):
                raise TypeError("Parameter must be of type"
                                "multipong.model.Player or uuid.UUID,"
                                "not {}".format(type(player)))
        if isinstance(player, Player):
            player = player.id
        self.players.add(player)
        self.__update_ball_count()
        # Return the updated player model
        added = Player.load(player).set_room(self.id)
        return added

    def __update_ball_count(self):
        ''' Check the ball count for the room to ensure that it is equal to the
        number of players currently playing.
        '''
        numPlayers = len(self.players)
        numBalls = len(self.balls)
        if numPlayers > numBalls:
            self.add_ball()
        elif numPlayers < numBalls:
            self.pop_last_ball()

    def remove_player(self, player) -> Player:
        '''Remove player from room but do not delete instance.
           We also check to make sure that the room is balanced for the number
           of current players.
        '''
        if not (isinstance(player, Player) or isinstance(player, uuid.UUID)):
                raise TypeError("Parameter must be of type"
                                "multipong.model.Player or uuid.UUID,"
                                "not {}".format(type(player)))
        if isinstance(player, Player):
            player = player.id
        self.players.remove(player)
        self.__update_ball_count()
        return Player.load(player).set_room(NULL_UUID)

    def add_ball(self) -> Ball:
        ball = Ball.new()
        self.balls.append(ball.id)
        return ball

    def delete_ball(self, uid: uuid.UUID):
        del self.balls[uid]
        Ball.load(uid).delete()

    def pop_last_ball(self):
        self.balls.popright()

    def ball_at(self, index: int) -> Ball:
        ball_id = uuid.UUID(self.balls[index].decode('utf-8'))
        return Ball.load(ball_id)

    def to_json(self) -> dict:
        '''Recursively convert fields to json-friendly output.

        Return a dict with the following schema:
        {
          id: "uuid",
          balls: [<see Ball.to_json()>],
          players: [<see Player.to_json()>]
        }
        '''
        as_uuid = lambda obj: uuid.UUID(obj.decode('utf-8'))
        return dict(
                id=str(self.id),
                balls=list(map(
                    lambda ball: Ball.load(ball).to_json(),
                    map(as_uuid, self.balls))),
                players=list(map(
                    lambda player: Player.load(player).to_json(),
                    map(as_uuid, self.players))),
                )

    __database__ = walrus_conn
    id = walrus.UUIDField(primary_key=True, index=True)
    balls = walrus.ListField()
    players = walrus.SetField()
