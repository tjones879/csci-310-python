from pprint import pprint
from multipong import socketio, app
from flask import request, session
from flask_socketio import emit, join_room, leave_room
from multipong.models import Room, Player
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
    print('EVENT: disconnect', session)
    user_logout()
    session.clear()
    roomleave()


@socketio.on('gamedata')
def send_gamedata(action='cycleUpdate'):
    roomid = session.get('room')
    room = Room.load(roomid)
    
    room.save()
    j = Room.load(roomid).to_json()
    j['action'] = action
    
    # collect room data and send back to client
    pprint(j)
    emit('gamedata', j)


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
        rooms = [r for r in Room.all()]
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
    print("EVENT: login: ", data, " :: ", session)
    if data.get('username') is None or len(data.get('username')) < 1:
        # HAAX
        return False
    else:
        if session.get('room') is None:
            roomjoin()
        session['username'] = validate_username(data.get('username'))
        
        # update room with new player, balls and send new-player game data
        room = Room.load(session['room'])
        player = Player.new(session_id=session.sid, user=data.get('username'))
        player = room.add_player(player)
        session['player'] = player.id
        numPlayers = len(room.players)
        numBalls = len(room.balls)
        if numPlayers > numBalls:
            room.add_ball()
        send_gamedata('new-player')
        
        if app.config['DEBUG_MODE']:
            emit('debug', {'msg': "{} connected".format(session['username'])})
            print(data.get('username'), 'logged in')


@socketio.on('logout')
def user_logout():
    if app.config['DEBUG_MODE']:
        print('EVENT: logout:', session.get('username'), session.sid)
        
    #update room with player leaving, number of balls reduceing etc.
    room = Room.load(session['room'])
    room.remove_player(session['player'])
    player = Player.load(session['player'])
    player.delete()
    numPlayers = len(room.players)
    numBalls = len(room.balls)
    if numPlayers < numBalls:
        room.pop_last_ball()
        
    
