from flask import Flask
from flask_socketio import SocketIO
from pymongo import MongoClient
from flask_session import Session
import redis
import os
from threading import Thread
import eventlet
import rom.util
eventlet.monkey_patch()

GAME_LOOP_THREAD = None

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    MONGO_URL=os.environ['MONGODB_URI'],
    REDIS_URL=os.environ['REDIS_URL'],
    SECRET_KEY="super secret dev key"
))
socketio = SocketIO(app, manage_session=False, message_queue=app.config['REDIS_URL'], async_mode='eventlet')
mongo_url = app.config['MONGO_URL']
mongo = MongoClient(mongo_url)
redis_conn = redis.from_url(app.config['REDIS_URL'])
rom.util.CONNECTION = redis_conn
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
    #redis_conn.delete('rooms')
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    if GAME_LOOP_THREAD is None:
        GAME_LOOP_THREAD = Thread(target=game.game_loop)
        GAME_LOOP_THREAD.start()
    socketio.run(app, host="0.0.0.0", port=port)


if __name__ == '__main__':
    main()
