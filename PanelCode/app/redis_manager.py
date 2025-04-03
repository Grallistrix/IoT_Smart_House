import redis
import os

class RedisManager:
    def __init__(self):
        self.r = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=6379,
            db=0,
            decode_responses=True
        )
