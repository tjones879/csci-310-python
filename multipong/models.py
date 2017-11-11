from multipong import walrus_conn
import walrus
import uuid
import random


DEFAULT_ARENA_SIZE = 1000
BALL_TYPES = ["normal"]



class Room(walrus.Model):
    @staticmethod
    def new():
        room = Room.create(
            id=uuid.uuid4(),
            arenasize=DEFAULT_ARENA_SIZE
        )
        room.save()
        return room

    __database__ = walrus_conn
    id = walrus.UUIDField(default=str(uuid.uuid4()), index=True)
    balls = walrus.ListField()  # [ <uuid>, ... ]
    players = walrus.SetField()  # [ <uuid>, ... ]
    spectators = walrus.SetField()  # [ <uuid>, ... ]
    # [ {playerid: <uuid>, score: <int>}, ... ]
    leaderboard = walrus.SetField()
    arenasize = walrus.Field()  # <int>


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
                'x': 50,
                'y': 50
            },
            ballType=random.choice(BALL_TYPES)
        )
        ball.save()
        return ball
    __database__ = walrus_conn
    id = walrus.UUIDField(default=str(uuid.uuid4()), index=True)
    position = walrus.Field()
    vector = walrus.Field()
    ballType = walrus.TextField()


class Player(walrus.Model):
    @staticmethod
    def new():
        player = Player.create(
            id=uuid.uuid4()
        )
        player.save()
        return player
    __database__ = walrus_conn
    id = walrus.UUIDField(default=str(uuid.uuid4()), index=True)
    sid = walrus.UUIDField()  # uuid.UUID(session.sid)
    room = walrus.UUIDField()  # <uuid>
    paddle = walrus.HashField()  # {pos: <int>, width: <int>}
    username = walrus.TextField()  # <str>
    score = walrus.Field()  # int
    # {email: <str>, topscore: <int>, rank: <int>}
    reginfo = walrus.HashField()
