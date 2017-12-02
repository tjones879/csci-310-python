from . import socketio, app, redis_conn, thread, thread_lock
from multipong.models import Room, Player, update_ball, DEFAULT_ARENA_SIZE
from flask import request, session
from flask_socketio import emit, join_room, leave_room
import re
import json


def backgroundThread():
    p = redis_conn.pubsub(ignore_subscribe_messages=True)
    p.subscribe('serverUpdate')
    while True:
        message = p.get_message()
        while message is not None:
            message = json.loads(message.get('data').decode('utf-8'))
            roomid = message.get('roomid')
            d = message.get('payload')
            socketio.emit('serverUpdate', d, room=roomid)
            message = p.get_message()
        socketio.sleep(0.1)


@socketio.on('connect')
def handle_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=backgroundThread)

    if bool(app.config['DEBUG_MODE']):
        emit('toggledebug', {'debug': True})
    print('EVENT: connected', session)
    roomjoin()
    serverUpdate('init')


@socketio.on('clientUpdate')
def clientUpdate(data):
    data = json.loads(data)
    for b in data['balls']:
        update_ball(b['id'], b['pos'], b['vec'])

    serverUpdate()


@socketio.on('disconnect')
def handle_disconnect():
    print('EVENT: disconnect', session)
    user_logout()
    session.clear()


def serverUpdate(action='cycleUpdate'):
    roomid = session.get('room')
    room = Room.load(roomid)

    room.save()
    j = Room.load(roomid).to_json()
    j['action'] = action

    # collect room data and send back to client
    if action == 'init':
        emit('serverUpdate', j)
    else:
        socketio.emit('serverUpdate', j)


@socketio.on('toggledebug')
def toggledebug():
    app.config['DEBUG_MODE'] = not app.config['DEBUG_MODE']


def roomjoin():
    if bool(app.config['DEBUG_MODE']):
        print("EVENT: roomjoin:", session)
    isPlayer = session.get('player') is not None
    if session.get('room') is None:
        if Room.count() < 1:
            Room.create()
        rooms = list(Room.all())
        if isPlayer:
            for room in rooms:
                if len(room.players) < DEFAULT_ARENA_SIZE:
                    room.add_player(session.get('player'))
                    break
        else:
            room = rooms[0]
        session['room'] = room.id
        join_room(str(room.id))
        if "username" in session and session['username'] is not None:
            emit('roomjoin', {
                 "username": session['username'], "room": room.id},
                 room=str(room.id))
        if bool(app.config['DEBUG_MODE']):
            print("EVENT: roomjoin: user '{}' joined room '{}'. session id: {}, session: {}".format(
                session.get('username', "None"), room.id, session.sid, session))
    else:
        join_room(session['room'])


def roomleave():
    isPlayer = 'player' in session and session.get('player') is not None
    if session.get('room') is not None:
        room = Room.load(session['room'])
        leave_room(session.get('room'))
        if isPlayer:
            room.remove_player(session['player'])
        if len(room.players) == 0:
            room.delete()
        del session['room']


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
        return False
    else:
        username = validate_username(data.get('username'))
        player = Player.new(user=username)
        session['player'] = player.id

        if session.get('room') is None:
            roomjoin()

        # update room with new player, balls and send new-player game data
        room = Room.load(session['room'])
        player = room.add_player(player)

        if app.config['DEBUG_MODE']:
            emit('debug', {'msg': "{} connected".format(session['username'])})
            print(data.get('username'), 'logged in')


@socketio.on('logout')
def user_logout():
    roomleave()
    if 'player' in session and session['player'] is not None:
        if app.config['DEBUG_MODE']:
            print('EVENT: logout:', session.get('username'), session.sid)

        player = Player.load(session['player'])
        player.delete()
        del session['player']
        # Emit a user-left event to the room
