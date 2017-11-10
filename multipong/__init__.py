from flask import Flask
from flask_socketio import SocketIO
from flask_session import Session
from flask_oauthlib.client import OAuth
from pymongo import MongoClient
import redis
import os
from threading import Thread
import eventlet
import json

eventlet.monkey_patch()

GAME_LOOP_THREAD = None

app = Flask(__name__)
app.config.from_object(__name__)
app.config['REDIS_URL'] = os.environ['REDIS_URL']

socketio = SocketIO(app, manage_session=False, message_queue=app.config['REDIS_URL'], async_mode='eventlet')

redis_conn = redis.from_url(app.config['REDIS_URL'])

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis_conn
Session(app)

oauth = OAuth(app)

with open('oauth_creds.json') as file:
    creds = json.load(file)

google = oauth.remote_app(
    'google',
    consumer_key=creds['google']['c_id'],
    consumer_secret=creds['google']['c_secret'],
    request_token_params={'scope': 'email'},
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

twitter = oauth.remote_app(
    'twitter',
    consumer_key=creds['twitter']['c_id'],
    consumer_secret=creds['twitter']['c_secret'],
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize'
)

from multipong.mongo import init_users

client = MongoClient(os.environ['MONGO_URL'])
users = init_users(client)


from multipong.routes import *
from multipong.sockets import *
from multipong.rooms import *
from multipong.oauth import *
import multipong.game as game

def create_app():
    return app


def main():
    global GAME_LOOP_THREAD
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    if GAME_LOOP_THREAD is None:
        GAME_LOOP_THREAD = Thread(target=game.game_loop)
        GAME_LOOP_THREAD.start()
    socketio.run(app, host="0.0.0.0", port=port)


if __name__ == '__main__':
    main()
