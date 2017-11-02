from multipong import app, walrus_conn
import walrus
import uuid


class Room(walrus.Model):
    __database__ = walrus_conn
    id = walrus.UUIDField(default=str(uuid.uuid4()), index=True)
    balls = walrus.SetField()  # [ <uuid>, ... ]
    players = walrus.SetField()  # [ <uuid>, ... ]
    spectators = walrus.SetField()  # [ <uuid>, ... ]
    leaderboard = walrus.SetField()  # [ {playerid: <uuid>, score: <int>}, ... ]
    arenasize = walrus.Field()  # <int>

class Ball(walrus.Model):
    __database__ = walrus_conn
    id = walrus.UUIDField(default=str(uuid.uuid4()), index=True)
    position = walrus.HashField()
    vector = walrus.HashField()
    ballType = walrus.TextField()
    
class Player(walrus.Model):
    __database__ = walrus_conn
    id = walrus.UUIDField(default=str(uuid.uuid4()), index=True)
    sid = walrus.UUIDField()  # uuid.UUID(session.sid
    room = walrus.UUIDField()  # <uuid>
    paddle = walrus.HashField()  # {pos: <int>, width: <int>}
    username = walrus.TextField()  # <str>
    score = walrus.Field()  # int
    reginfo = walrus.HashField()  # {email: <str>, topscore: <int>, rank: <int>}
    