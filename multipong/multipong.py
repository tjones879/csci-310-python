from flask import Flask, render_template
from flask_socketio import SocketIO
from pymongo import MongoClient
from flask_session import MongoDBSessionInterface, Session
import os, urllib.parse

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    MONGO_HOST=os.environ['MULTIPONG_MONGODB_HOST'],
    MONGO_PORT=os.environ['MULTIPONG_MONGODB_PORT'],
    MONGO_USERNAME=os.environ['MULTIPONG_MONGODB_USER'],
    MONGO_DBNAME=os.environ['MULTIPONG_MONGODB_DB'],
    MONGO_PASSWORD=os.environ['MULTIPONG_MONGODB_PASS'],
    SECRET_KEY="super secret dev key"
))
socketio = SocketIO(app)
mongo_url = "mongodb://{}:{}@{}:{}/{}".format(
    urllib.parse.quote_plus(app.config['MONGO_USERNAME']),
    urllib.parse.quote_plus(app.config['MONGO_PASSWORD']),
    urllib.parse.quote_plus(app.config['MONGO_HOST']),
    urllib.parse.quote_plus(app.config['MONGO_PORT']),
    urllib.parse.quote_plus(app.config['MONGO_DBNAME'])
)
mongo = MongoClient(mongo_url)
app.config['SESSION_TYPE'] = 'mongodb'
app.config['SESSION_MONGODB'] = mongo
app.config['SESSION_MONGODB_DB'] = app.config['MONGO_DBNAME']
Session(app)


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    socketio.run(app)
