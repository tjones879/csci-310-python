from time import time, sleep
import multipong.models as models
import redis
import json
import os

MAXFPS = 27
MAXSLEEP = 1 / MAXFPS
prevTime = time()
r = redis.from_url(os.environ.get('REDIS_URL'))
p = r.pubsub(ignore_subscribe_messages=True)


def constructUpdate(room: models.Room):
    '''Construct an update for the socketio server to send out.

    All mesages are published to the 'serverUpdate' channel with
    the following schema:
    {
      "timestamp":  (float) Unix time when values were calculated,
      "roomid":    (string) Client room where the update should be sent,
      "payload": see `models.Room.to_json()`
    }
    '''
    roomJson = room.to_json()
    roomJson['timestamp'] = time()
    data = '{ "roomid": "' + str(room.id)
    data += '", "payload": ' + json.dumps(roomJson) + '}'
    r.publish('serverUpdate', data)


def throttleTime(prevTime: float):
    '''Sleep if necessary to keep a constant refresh rate'''
    sleepTime = max((MAXSLEEP) - (time() - prevTime), 0)
    sleep(sleepTime)


def gameLoop():
    while True:
        prevTime = time()
        for room in models.Room.all():
            room.moveBalls()
            constructUpdate(room)
        throttleTime(prevTime)
