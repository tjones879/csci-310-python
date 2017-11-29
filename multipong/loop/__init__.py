import redis
import os
import walrus
import builtins

GAME_LOOP_THREAD = None

# Define the walrus_conn for the walrus models module
builtins.walrus_conn = walrus.Database.from_url(os.environ.get('REDIS_URL'))

from .loop import gameLoop
