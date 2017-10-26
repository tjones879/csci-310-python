from multipong import socketio
import time


def game_loop(tickrate=1):
    print("started game loop")
    while True:
        time.sleep(1/tickrate)
        socketio.emit('tick', broadcast=True)
