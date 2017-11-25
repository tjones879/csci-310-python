from flask import Flask
from flask_socketio import SocketIO
from flask_session import Session
import redis
import os
from threading import Thread
import eventlet
import walrus
import builtins

eventlet.monkey_patch()

GAME_LOOP_THREAD = None

app = Flask(__name__)
app.config.from_object(__name__)
app.config['REDIS_URL'] = os.environ.get('REDIS_URL')

try:
    app.config['DEBUG_MODE'] = bool(os.environ['DEBUG'])
except:
    app.config['DEBUG_MODE'] = False

socketio = SocketIO(app, manage_session=False,
                    message_queue=app.config['REDIS_URL'], async_mode='eventlet')

redis_conn = redis.from_url(app.config['REDIS_URL'])
# Define the walrus_conn for the walrus models module
builtins.walrus_conn = walrus.Database.from_url(app.config['REDIS_URL'])
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis_conn
Session(app)


from multipong.routes import *
from multipong.sockets import *


def create_app():
    return app


def main():
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    ip = os.environ.get('IP', "0.0.0.0")
    socketio.run(app, host=ip, port=port)


if __name__ == '__main__':
    main()
