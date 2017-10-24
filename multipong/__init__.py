from flask import Flask
from flask_socketio import SocketIO
from pymongo import MongoClient
from flask_session import Session
import redis
import os
import urllib.parse


def create_app():
    return app


app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    MONGO_URL=os.environ['MONGODB_URI'],
    REDIS_URL=os.environ['REDIS_URL'],
    SECRET_KEY="super secret dev key"
))
socketio = SocketIO(app, manage_session=False)
mongo_url = app.config['MONGO_URL']
r = redis.from_url(app.config['REDIS_URL'])
mongo = MongoClient(mongo_url)
app.config['SESSION_TYPE'] = 'mongodb'
app.config['SESSION_MONGODB'] = mongo
app.config['SESSION_MONGODB_DB'] = mongo.get_database().name
Session(app)

from multipong.routes import *
from multipong.sockets import *

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0")
