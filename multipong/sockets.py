from multipong import socketio
from flask_socketio import emit, join_room, leave_room


@socketio.on('client_connected')
def handle_client_connect_event(json):
    print('received json: {0}'.format(str(json)))


@socketio.on('user.join.room')
def user_join_room(data):
    ""

@socketio.on('user.leave.room')
def user_leave_room(data):
    ""

@socketio.on('test_event')
def test_event(json):
    emit('test_response', {'data': json})

