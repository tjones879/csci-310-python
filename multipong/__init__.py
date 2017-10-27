from flask import Flask
from flask_socketio import SocketIO
from flask_session import Session
import redis
import os
from threading import Thread
import eventlet

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


from multipong.routes import *
from multipong.sockets import *
from multipong.rooms import *
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
