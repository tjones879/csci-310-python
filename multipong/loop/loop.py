from time import time, sleep
import models
import redis
import json
import os

MAXFPS = 2
MAXSLEEP = 1 / MAXFPS
prevTime = time()
r = redis.from_url(os.environ.get('REDIS_URL'))
p = r.pubsub(ignore_subscribe_messages=True)


def constructUpdate(room: models.Room):
    data = '{"timestamp": ' + str(time())
    data += ', "roomid": "' + str(room.id)
    data += '", "payload": ' + json.dumps(room.to_json()) + '}'
    r.publish('serverUpdate', data)


def throttleTime(prevTime: float):
    '''Sleep if necessary to keep a constant refresh rate'''
    sleepTime = max((MAXSLEEP) - (time() - prevTime), 0)
    prevTime = time()
    sleep(sleepTime)


def gameLoop():
    while True:
        prevTime = time()
        for room in models.Room.all():
            constructUpdate(room)
        throttleTime(prevTime)
