from fastapi import FastAPI
from redis_manager import RedisManager

app = FastAPI()
db = RedisManager()