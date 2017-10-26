from multipong import app
import walrus

def generate_uid(size=10) -> str:
    import random, string
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))


class Room(walrus.Model):
    __database__ = walrus.Database.from_url(app.config.get("REDIS_URL"))
    id = walrus.TextField(default="room_{}".format(generate_uid()), index=True)
    players = walrus.ListField()
    spectators = walrus.ListField()
