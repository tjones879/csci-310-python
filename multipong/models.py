from multipong import walrus_conn
import walrus
import uuid
import random


DEFAULT_ARENA_SIZE = 1000
BALL_TYPES = ["normal"]
MAX_SPEED = 25


class Ball(walrus.Model):
    @staticmethod
    def new():
        ball = Ball.create(
            id=uuid.uuid4(),
            position={
                'x': 500,
                'y': 500
            },
            vector={
                'x': random.randint(-MAX_SPEED, MAX_SPEED),
                'y': random.randint(-MAX_SPEED, MAX_SPEED)
            },
            ballType=random.choice(BALL_TYPES)
        )
        return ball

    __database__ = walrus_conn
    id = walrus.UUIDField(primary_key=True, index=True)
    position = walrus.Field()
    vector = walrus.Field()
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
        ball_id = uuid.UUID(bytes.decode(list(self.balls)[index], 'utf-8'))
        return Ball.load(ball_id)

    __database__ = walrus_conn
    id = walrus.UUIDField(index=True)
    balls = walrus.ListField()  # [ <uuid>, ... ]
    players = walrus.SetField()  # [ <uuid>, ... ]
    spectators = walrus.SetField()  # [ <uuid>, ... ]
    # [ {playerid: <uuid>, score: <int>}, ... ]
    leaderboard = walrus.SetField()
    arenasize = walrus.Field(default=DEFAULT_ARENA_SIZE)  # <int>


class Player(walrus.Model):
    @staticmethod
    def new():
        player = Player.create(
            id=uuid.uuid4()
        )
        return player

    __database__ = walrus_conn
    id = walrus.UUIDField(index=True)
    sid = walrus.UUIDField()  # uuid.UUID(session.sid)
    room = walrus.UUIDField()  # <uuid>
    paddle = walrus.HashField()  # {pos: <int>, width: <int>}
    username = walrus.TextField()  # <str>
    score = walrus.Field()  # int
    # {email: <str>, topscore: <int>, rank: <int>}
    reginfo = walrus.HashField()
