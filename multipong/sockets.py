from multipong import socketio
from flask import request, session
from flask_socketio import emit, join_room, leave_room
from multipong.rooms import Room

MAX_ROOM_SIZE = 10  # maximum of 10 players/specs per room


@socketio.on('connect')
def handle_connect():
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
    if session.get('room') is None:
        rooms = list(Room.all())
        if len(rooms) < 1:  # case: no rooms on server
            room = Room.create()
        else:
            room = rooms[0]
            for rm in rooms:
                if isPlayer:
                    if len(rm.players) < MAX_ROOM_SIZE:
                        room = rm
                        room.players.add(session.sid)
                        break
                    elif len(rm.spectators) < MAX_ROOM_SIZE:
                        room = rm
                        room.spectators.add(session.sid)
                        break
        session['room'] = room.id
        room.save()
        join_room(room.id)
        if "username" in session and session['username'] is not None:
            emit('roomjoin', {"username": session['username'], "room": room.id}, room=room.id)
    else:
        join_room(session['room'])

@socketio.on('roomupdate')
def roomupdate(data):
    ""


@socketio.on('user.room.leave')
def user_leave_room():
    leave_room(session['room'])
    room = list(Room.query(Room.id == session['room'])).__getitem__(0)  # avoids key error
    if session['isPlayer']:
        room.players.remove(session.sid)
    else:
        room.spectator.remove(session.sid)
    room.save()
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
