from flask import Flask
from flask_socketio import SocketIO
from pymongo import MongoClient
from flask_session import Session
import redis
import os
import urllib.parse


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


def create_app():
    return app


def main():
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host="0.0.0.0", port=port)


if __name__ == '__main__':
    main()
