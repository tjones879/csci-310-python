from multipong import socketio, mongo, app, redis_conn
from flask import request, session, jsonify
from flask_socketio import send, emit, join_room, leave_room
from multipong.rooms import Room

PLAYER_COLL = mongo.get_database()['Players']
MAX_ROOM_SIZE = 10  # maximum of 10 players/specs per room


@socketio.on('connect')
def handle_connect():
    print(list(Room.all()))
    if "username" not in session:
        user_join_room(isPlayer=False)
        emit('askusername')
    else:
        user_join_room()
        emit('playerready', {"username": session['username']})


@socketio.on('newplayer')
def handle_newplayer(json):
    session['username'] = json['username']
    session['isPlayer'] = True
    user_join_room()
    emit('playerready', {"username": session['username']}, room=request.sid)


@socketio.on('roomjoin')
def user_join_room(isPlayer=True):
    if 'room' not in session or session['room'] is None:
        rooms = Room.all()
        if len(list(rooms)) < 1:  # case: no rooms on server
            room = Room.create()
        else:
            for rm in rooms:
                if isPlayer:
                    if len(rm.players) < MAX_ROOM_SIZE:
                        room = rm
                        room.players.append(session.sid)
                        break
                    elif len(rm.spectators) < MAX_ROOM_SIZE:
                        room = rm
                        room.spectators.append(session.sid)
                        break
        session['room'] = room.id
        join_room(room.id)
        if "username" in session and session['username'] is not None:
            emit('roomjoin', {"username": session['username'], "room": room.id}, room=room.id);
    else:
        print(session['room'])
        join_room(session['room'])

@socketio.on('roomupdate')
def roomupdate(data):
    ""


@socketio.on('user.room.leave')
def user_leave_room():
    leave_room(session['room'])
    room = Room.load(str(session['room']))
    if session['isPlayer']:
        room.player.remove(session.sid)
    else:
        room.spectator.remove(session.sid)
    if session['username'] is not None:
        emit('user.room.leave', {"username": session['username']}, room=session['room'])
    session['room'] = None


@socketio.on('usermessage')
def onmessage(json):
    if session.get('room') is not None:
        emit('usermessage', {'username': session.get('username'), 'message': json['message']}, room=session.get('room'))
    else:
        "error because user should have had a room"


@socketio.on('logout')
def user_logout():
    print('logout ', session.sid)
    user_leave_room()
    session.clear()
    emit('askusername')


@socketio.on('disconnect')
def on_disconnect():
    if "username" in session:
        user_leave_room()
    print("disconnected, ", session.sid)
