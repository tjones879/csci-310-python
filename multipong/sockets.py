from multipong import socketio, app
from flask import request, session
from flask_socketio import emit, join_room, leave_room
from multipong.models import Room
import uuid
import re
import random

MAX_ROOM_SIZE = 10  # maximum of 10 players/specs per room


@socketio.on('connect')
def handle_connect():
    if bool(app.config['DEBUG_MODE']):
        emit('toggledebug', {'debug': True})
        print('EVENT: connected', session.sid, session)
    roomjoin()
    send_gamedata('init')

@socketio.on('disconnect')
def handle_disconnect():
    roomleave()

@socketio.on('gamedata')
def send_gamedata(action='update'):
    roomid = session.get('room')
    xDir = random.choice([-1, 1])
    yDir = random.choice([-1, 1])
    xVec = random.randint(50, 150) * xDir
    yVec = random.randint(50, 150) * yDir
    roomdata = {
        "action": action,
        "id": str(roomid),
        "balls": [
            {
                'id': "wqaepiguhqawepri",
                'pos': {'x': 500, 'y': 500},
                'vec': {'x': xVec, 'y': yVec},
                'type': "normal"
            },
            {
                'id': "wqaepiguhqawepra",
                'pos': {'x': 500, 'y': 500},
                'vec': {'x': xVec+7, 'y': yVec- 10},
                'type': "normal"
            },
            {
                'id': "wqaepiguhqaweprb",
                'pos': {'x': 500, 'y': 500},
                'vec': {'x': xVec*5, 'y': yVec/5},
                'type': "normal"
            },
            {
                'id': "wqaepiguhqaweprc",
                'pos': {'x': 500, 'y': 500},
                'vec': {'x': xVec/-13, 'y': yVec*-13},
                'type': "normal"
            },
            {
                'id': "wqaepiguhqaweprd",
                'pos': {'x': 500, 'y': 500},
                'vec': {'x': xVec/-3, 'y': yVec/-3},
                'type': "normal"
            },
            {
                'id': "wqaepiguhqawepre",
                'pos': {'x': 500, 'y': 500},
                'vec': {'x': xVec*13, 'y': yVec*-13},
                'type': "normal"
            },
            {
                'id': "wqaepiguhqaweprf",
                'pos': {'x': 500, 'y': 500},
                'vec': {'x': xVec*7, 'y': yVec/6},
                'type': "normal"
            },
            {
                'id': "wqaepiguhqaweprg",
                'pos': {'x': 500, 'y': 500},
                'vec': {'x': xVec*2, 'y': yVec*1.5},
                'type': "normal"
            },
            {
                'id': "wqaepiguhqaweprh",
                'pos': {'x': 500, 'y': 500},
                'vec': {'x': xVec*-1, 'y': yVec*2},
                'type': "normal"
            },
            {
                'id': "wqaepiguhqaweprj",
                'pos': {'x': 500, 'y': 500},
                'vec': {'x': xVec/2, 'y': yVec/3},
                'type': "normal"
            },
        ],
        "players": [
            {
                'id': "piqaapohibapoe",
                'paddle': {
                    'pos': 500,
                    'width': 100
                },
                'username': "wewlad",
                'score': 0,
                'rank': 0
            },
        ]
    }
    # collect room data and send back to client
    emit('gamedata', roomdata)


@socketio.on('playerdata')
def recv_playerdata(data):
    if bool(app.config['DEBUG_MODE']):
        print('EVENT: playerdata: ', data)
    roomid = session['room']
    # update room with player's new data


@socketio.on('toggledebug')
def toggledebug():
    app.config['DEBUG_MODE'] = not app.config['DEBUG_MODE']


@socketio.on('roomjoin')
def roomjoin():
    if bool(app.config['DEBUG_MODE']):
        print("EVENT: roomjoin:", session.sid, session)
    isPlayer = session.get('username') is not None
    if session.get('room') is None:
        rooms = list(Room.all())
        if len(rooms) < 1:  # case: no rooms on server
            Room.create()
            rooms = list(Room.all())
        room = rooms[0]
        for rm in rooms:
            if isPlayer:
                if len(rm.players) < MAX_ROOM_SIZE:
                    room = rm
                    # TODO: Replace with Player object's id
                    room.players.add(session.sid)
                    break
            else:
                if len(rm.spectators) < MAX_ROOM_SIZE:
                    room = rm
                    # TODO: Replace with Player object's id
                    room.spectators.add(session.sid)
                    break
        session['room'] = room.id
        room.save()
        join_room(str(room.id))
        if bool(app.config['DEBUG_MODE']):
            print("EVENT: roomjoin: user '{}' joined room '{}'. session id: {}, session: {}".format(
                session.get('username', "None"), room.id, session.sid, session))
        if "username" in session and session['username'] is not None:
            emit('roomjoin', {
                 "username": session['username'], "room": room.id}, room=str(room.id))
    else:
        join_room(session['room'])


@socketio.on('roomleave')
def roomleave():
    isPlayer = session.get('username') is not None
    if session.get('room') is None:
        # whoops
        if app.config['DEBUG_MODE']:
            print('left room when not joined to one')
    else:
        room = list(Room.query(Room.id == session['room'])).__getitem__(
            0)  # avoids key error
        leave_room(session.get('room'))
        if isPlayer:
            room.players.remove(session.sid)
        else:
            room.spectators.remove(session.sid)
        if len(room.players) == 0 and len(room.spectators) == 0:
            room.delete()
        # remove player from room in database


def validate_username(username: str) -> str:
    '''Require that a username is no more than 20 char
       and is alphanumeric with spaces, dashes, or underscores'''
    if len(username) > 20:
        username = username[:20]
    forbidden = re.compile("[^a-zA-Z0-9 _-]")
    username = re.sub(forbidden, "", username)
    return username


@socketio.on('login')
def handle_newplayer(data):
    if bool(app.config['DEBUG_MODE']):
        print("EVENT: login: ", data, " :: ", session)
    if data.get('username') is None or len(data.get('username')) < 1:
        # HAAX
        return False
    else:
        if session.get('room') is None:
            roomjoin()
        session['username'] = validate_username(data.get('username'))
        # update room with new player
        if app.config['DEBUG_MODE']:
            emit('debug', {'msg': "{} connected".format(session['username'])})
            print(data.get('username'), 'logged in')


@socketio.on('logout')
def user_logout():
    if app.config['DEBUG_MODE']:
        print('EVENT: logout:', session.get('username'), session.sid)
    session.clear()
