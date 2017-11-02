import redis
import os

if __name__ == "__main__":
    redis_conn = redis.Redis.from_url(os.environ['REDIS_URL'])
    redis_conn.flushdb()
    print("Cleared redis")
