import walrus
import uuid
import random
import os
from time import time
from json import JSONEncoder
'''
In order to use this module, the builtin identifier `builtins.walrusconn`
must be set to a correct connection to redis. This can be done by calling:

`builtins.walrus_conn = walrus.Database.from_url(<REDIS_URL>)`
'''

walrus_conn = walrus.Database.from_url(os.environ.get('REDIS_URL'))

DEFAULT_ARENA_SIZE = 8  # Currently using an octogon for the arena
BALL_TYPES = ["normal"]
MIN_SPEED = 50
MAX_SPEED = 150
NULL_UUID = uuid.uuid4()
BOUNCE_TABLE = [[-1, 1], [1, -2], [1, 1], [-1, -1]]


def update_ball(id: uuid.UUID, pos: dict, vec: dict):
    ball = Ball.load(id)
    ball.position['x'] = int(pos['x'])
    ball.position['y'] = int(pos['y'])
    ball.vector['x'] = vec['x']
    ball.vector['y'] = vec['y']
    ball.save()


def edgeHit(ball: 'Ball', edge: int, elapsed: float):
    posx = asFloat(ball.position['x'])
    posy = asFloat(ball.position['y'])
    vecx = asFloat(ball.vector['x'])
    vecy = asFloat(ball.vector['y'])

    posx -= vecx * elapsed
    posy -= vecy * elapsed
    # Is the edge a horizontal or vertical?
    if edge < 2:
        vecx *= BOUNCE_TABLE[edge][0]
        vecy *= BOUNCE_TABLE[edge][1]
    # The edge must be a diagonal
    else:
        vecx = vecy * BOUNCE_TABLE[edge][0]
        vecy = vecx * BOUNCE_TABLE[edge][1]
    # Copy values back into redis model
    ball.position['x'] = posx
    ball.position['y'] = posy
    ball.vector['x'] = vecx
    ball.vector['y'] = vecy
    print("Ball: ", ball.id, " hit edge: ", edge)


def checkPosition(ball: 'Ball', elapsed: float):
    pos_sum = asFloat(ball.position['x']) + asFloat(ball.position['y'])
    pos_diff = asFloat(ball.position['x']) - asFloat(ball.position['y'])
    # Are we in the range of left walls?
    if asFloat(ball.position['x']) <= 292:
        if pos_sum <= 292:
            edgeHit(ball, 3, elapsed)
        elif -1*pos_diff >= 706:
            edgeHit(ball, 2, elapsed)
        elif asFloat(ball.position['x']) <= 0:
            edgeHit(ball, 0, elapsed)
    # Are we in the range of right walls?
    elif asFloat(ball.position['x']) >= 706:
        if pos_diff >= 706:
            edgeHit(ball, 2, elapsed)
        elif pos_sum >= 1706:
            edgeHit(ball, 3, elapsed)
        elif asFloat(ball.position['x']) >= 999:
            edgeHit(ball, 0, elapsed)
    else:
        if asFloat(ball.position['y']) <= 0 or asFloat(ball.position['y']) >= 999:
            edgeHit(ball, 1, elapsed)


def as_int(obj) -> int:
    return int(obj.decode('utf-8'))


def asFloat(obj) -> float:
    return float(obj.decode('utf-8'))


class Ball(walrus.Model):
    @staticmethod
    def new():
        ball = Ball.create(
            id=uuid.uuid4(),
            ballType=random.choice(BALL_TYPES)
        )
        ball.vector['x'] = random.randint(MIN_SPEED, MAX_SPEED) * random.choice([-1, 1])
        ball.vector['y'] = random.randint(MIN_SPEED, MAX_SPEED) * random.choice([-1, 1])
        ball.position['x'] = 500 + asFloat(ball.vector['x'])
        ball.position['y'] = 500 + asFloat(ball.vector['y'])
        ball.save()
        return Ball.load(ball.id)

    def move(self, elapsed: float):
        self.position['x'] = asFloat(self.position['x']) + asFloat(self.vector['x']) * elapsed
        self.position['y'] = asFloat(self.position['y']) + asFloat(self.vector['y']) * elapsed
        checkPosition(self, elapsed)
        self.save()

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
                    x=asFloat(self.position['x']),
                    y=asFloat(self.position['y'])),
                vec=dict(
                    x=asFloat(self.vector['x']),
                    y=asFloat(self.vector['y'])),
                type=self.ballType
                )

    __database__ = walrus_conn
    id = walrus.UUIDField(primary_key=True, index=True)
    position = walrus.HashField()
    vector = walrus.HashField()
    ballType = walrus.TextField()


class Player(walrus.Model):
    @staticmethod
    def new(session_id=uuid.uuid4(), user="DUMMY", wall=0) -> 'Player':
        player = Player.create(
            id=uuid.uuid4(),
            room=NULL_UUID,
            username=user,
            score=0,
        )
        player.paddle['x'] = 500
        player.paddle['y'] = 500
        player.paddle['wall'] = wall

        player.save()
        return Player.load(player.id)

    def set_room(self, wall: int, room: uuid.UUID) -> 'Player':
        self.room = room
        self.paddle['wall'] = wall
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
                    wall=as_int(self.paddle['wall']),
                    x=asFloat(self.paddle['x']),
                    y=asFloat(self.paddle['y']),
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
            id=uuid.uuid4(),
            lastUpdate=time(),
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
        self.wall += 2
        self.save()
        added = Player.load(player)
        added.set_room(self.wall - 2, self.id)
        self.__update_ball_count()
        # Return the updated player model
        added = Player.load(player)
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
        self.wall -= 2
        self.save()
        self.__update_ball_count()
        return Player.load(player).set_room(wall=-1, room=NULL_UUID)

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

    def moveBalls(self):
        elapsedTime = time() - self.lastUpdate
        self.lastUpdate = time()
        self.save()
        for ball in self.balls:
            ball = ball.decode('utf-8')
            Ball.load(ball).move(elapsedTime)

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
    wall = walrus.IntegerField(default=0)
    lastUpdate = walrus.FloatField(default=0)
