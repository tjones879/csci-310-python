from multipong import socketio
from multipong import mongo
from multipong import app
from flask import request, session, jsonify
from flask_socketio import send, emit, join_room, leave_room
from bson import ObjectId
import random

PLAYER_COLL = mongo.get_database()['Players']
ROOMS_COLL = mongo.get_database()['Rooms']
MAX_ROOM_SIZE = 10  # maximum of 10 players/specs per room


@socketio.on('connect')
def handle_connect():
    if 'username' and 'isSpectator' and 'room' in session:
        if 'username' in session and session['username'] is not None:
            emit('user.ready', {"username": session['username']}, room=request.sid)
        else:
            emit('user.name.get', room=request.sid)
    else:
        session["username"] = None
        session["isSpectator"] = True
        session["room"] = None
        emit('user.name.get', room=request.sid)


@socketio.on('user.name.set')
def set_username(json):
    session['username'] = json['username']
    emit('user.ready', {"username": session['username']}, room=request.sid)


@socketio.on('user.room.join')
def user_join_room():
    rooms = ROOMS_COLL.find()
    if rooms.count() > 0:
        room = rooms[0]
    if rooms.count() < 1:
        room = ROOMS_COLL.find_one({"_id": create_room()})  # returns an oid for db entry of room
    elif not session.get('isSpectator'):
        while len(room['players']) < MAX_ROOM_SIZE:
            room = random.choice(rooms)
    else:
        while len(room['spectators']) < MAX_ROOM_SIZE:
            room = random.choice(list(rooms))
    session['room'] = room['_id']
    join_room(room['_id'])
    send(session.get('username') + ' has joined the room.', room=room['_id'])


@socketio.on('user.room.leave')
def user_leave_room():
    room = ROOMS_COLL.find_one({"_id": session.get('room')})
    leave_room(room['_id'])
    session['room'] = None
    send(session.get('username') + ' has left the room.', room=room['_id'])


@socketio.on('message')
def onmessage(json):
    print(json)
    print(session.get('room'))
    if session.get('room') is not None:
        print(session.get('username'))
        emit('message', {'username': session.get('username'), 'message': json['message']}, room=session.get('room'))
    else:
        "error because user should have had a room"


def create_room() -> ObjectId:
    new_room = {
        "players": [],
        "spectators": []
    }
    result = ROOMS_COLL.insert_one(new_room)
    return result.inserted_id
