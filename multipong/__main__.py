import argparse
from .web import main
from .loop import gameLoop

parser = argparse.ArgumentParser(description="Multipong - Multiplayer Pong Web Game")
parser.add_argument("command")

actions = {
    'web': main,
    'loop': gameLoop,
    'worker': gameLoop
}

args = parser.parse_args()
actions[args.command]()
