from multipong import walrus_conn
import walrus
import uuid
import random
from json import JSONEncoder


DEFAULT_ARENA_SIZE = 1000
BALL_TYPES = ["normal"]
MAX_SPEED = 25


def as_int(obj) -> int:
    return int(obj.decode('utf-8'))


class Ball(walrus.Model):
    @staticmethod
    def new():
        ball = Ball.create(
            id=uuid.uuid4(),
            ballType=random.choice(BALL_TYPES)
        )
        ball.position['x'] = 500
        ball.position['y'] = 500
        ball.vector['x'] = random.randint(-MAX_SPEED, MAX_SPEED)
        ball.vector['y'] = random.randint(-MAX_SPEED, MAX_SPEED)
        ball.save()
        return ball

    def to_json(self):
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


class Room(walrus.Model):
    @staticmethod
    def new() -> 'Room':
        room = Room.create(
                id=uuid.uuid4()
        )
        return room

    def add_ball(self) -> Ball:
        ball = Ball.new()
        self.balls.append(ball.id)
        return ball

    def delete_ball(self, uid: uuid):
        del self.balls[uid]
        Ball.load(uid).delete()

    def ball_at(self, index: int) -> Ball:
        ball_id = uuid.UUID(self.balls[index].decode('utf-8'))
        return Ball.load(ball_id)

    def to_json(self) -> dict:
        all_balls = range(len(list(self.balls)))
        return dict(
                id=str(self.id),
                balls=list(map(
                    lambda index: self.ball_at(index).to_json(),
                    all_balls)),
                )

    __database__ = walrus_conn
    id = walrus.UUIDField(primary_key=True, index=True)
    balls = walrus.ListField()  # [ <uuid>, ... ]
    players = walrus.SetField()  # [ <uuid>, ... ]
    spectators = walrus.SetField()  # [ <uuid>, ... ]
    # [ {playerid: <uuid>, score: <int>}, ... ]
    leaderboard = walrus.SetField()
    arenasize = walrus.IntegerField(default=DEFAULT_ARENA_SIZE)  # <int>


class RoomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Room):
            return obj.to_json()
        return JSONEncoder.encode(self, obj)


class Player(walrus.Model):
    @staticmethod
    def new():
        player = Player.create(
            id=uuid.uuid4()
        )
        return player

    __database__ = walrus_conn
    id = walrus.UUIDField(primary_key=True, index=True)
    sid = walrus.UUIDField()  # uuid.UUID(session.sid)
    room = walrus.UUIDField()  # <uuid>
    paddle = walrus.HashField()  # {pos: <int>, width: <int>}
    username = walrus.TextField()  # <str>
    score = walrus.Field()  # int
    # {email: <str>, topscore: <int>, rank: <int>}
    reginfo = walrus.HashField()
