from . import socketio, app, redis_conn, thread, thread_lock
from multipong.models import Room, Player, DEFAULT_ARENA_SIZE
from flask import request, session
from flask_socketio import emit, join_room, leave_room
from time import time
import re
import json


def backgroundThread():
    '''Automatically push all updates for the room to clients.'''
    p = redis_conn.pubsub(ignore_subscribe_messages=True)
    p.subscribe('serverUpdate')
    while True:
        message = p.get_message()
        while message is not None:
            message = json.loads(message.get('data').decode('utf-8'))
            roomid = message.get('roomid')
            d = message.get('payload')
            d['action'] = 'forceUpdate'
            socketio.emit('serverUpdate', d, room=roomid)
            message = p.get_message()
        socketio.sleep(0.1)


@socketio.on('connect')
def handle_connect():
    '''Assign a room for clients to spectate upon connection.

    Spawn a new background thread for updates if this is the
    first connected client.
    '''
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=backgroundThread)

    if bool(app.config['DEBUG_MODE']):
        emit('toggledebug', {'debug': True})
    print('EVENT: connected', session)
    roomjoin()
    serverUpdate('init')


@socketio.on('disconnect')
def handle_disconnect():
    print('EVENT: disconnect', session)
    user_logout()
    session.clear()


def serverUpdate(action='cycleUpdate'):
    roomid = session.get('room')
    j = Room.load(roomid).to_json()
    j['action'] = action
    emit('serverUpdate', j)


@socketio.on('toggledebug')
def toggledebug():
    app.config['DEBUG_MODE'] = not app.config['DEBUG_MODE']


def roomjoin():
    '''Attempt to assign the client a room.

    If the client already has a room (i.e. from spectating),
    let them join the same room.
    Spectators are given the first room returned by Redis and
    are automatically subscribed to any updates.
    Players must find the first room with an empty slot. The
    room they are spectating may be full, so we may need to
    send them elsewhere.
    '''
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
        else:  # Redis returns pseudo-random order of rooms, spectate the first
            room = rooms[0]
        session['room'] = room.id
        join_room(str(room.id))
        if bool(app.config['DEBUG_MODE']):
            print("EVENT: roomjoin: user '{}' joined room '{}'. session id: {}, session: {}".format(
                session.get('username', "None"), room.id, session.sid, session))
    else:
        room = Room.load(session.get('room'))
        if len(room.players) > DEFAULT_ARENA_SIZE:
            leave_room(session['room'])
            session['room'] = None
            roomjoin()
        else:
            room.add_player(session['player'])
            join_room(session['room'])
    if "username" in session and session['username'] is not None:
        # Notify the room that a new player has joined.
        emit('roomjoin', {
             "username": session['username'], "room": room.id},
             room=str(room.id))


def roomleave():
    '''Cleanly remove the client from the room and clear any session values.'''
    isPlayer = 'player' in session and session.get('player') is not None
    if session.get('room') is not None:
        room = Room.load(session['room'])
        leave_room(session.get('room'))
        if isPlayer:
            room.remove_player(session['player'])
        if len(room.players) == 0:
            room.delete()
        del session['room']
        # TODO: Emit a user-left event to the room


def validate_username(username: str) -> str:
    '''Require that a username is no more than 20 char
       and is alphanumeric with spaces, dashes, or underscores'''
    if len(username) > 20:
        username = username[:20]
    forbidden = re.compile("[^a-zA-Z0-9 _-]")
    username = re.sub(forbidden, "", username)
    return username


@socketio.on('latencyCheck')
def latencyHandshake(data):
    '''Provide the client with the correct current time for the server.

    It is recommended that the client sends their current time with this
    event. The loopback from this server with its time will provide the
    client with enough information to adjust for both hardware time drift
    and latency in later communication.
    '''
    timestamp = dict(
            serverTime=time(),
            data=data,
            )
    socketio.emit('latencyHandshake', timestamp)


@socketio.on('paddleUpdate')
def paddleUpdate(data):
    '''Take in and verify the client's information about their paddle.

    If the client's data could not be verified, the correct position will
    be sent back.
    If action field of the message is set to `paddleHit`, the response
    will show a failure or success.
    '''


@socketio.on('login')
def handle_newplayer(data):
    print("EVENT: login: ", data, " :: ", session)
    if data.get('username') is None or len(data.get('username')) < 1:
        return False
    else:
        username = validate_username(data.get('username'))
        player = Player.new(user=username)
        session['player'] = player.id

        roomjoin()

        if app.config['DEBUG_MODE']:
            emit('debug', {'msg': "{} connected".format(session['username'])})
            print(data.get('username'), 'logged in')


@socketio.on('logout')
def user_logout():
    '''Ensure that the client is not inside a room, then delete
    it from redis and clear its session.'''
    roomleave()
    if 'player' in session and session['player'] is not None:
        if app.config['DEBUG_MODE']:
            print('EVENT: logout:', session.get('username'), session.sid)

        player = Player.load(session['player'])
        player.delete()
        del session['player']
