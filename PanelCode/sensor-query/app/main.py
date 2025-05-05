from contextlib import asynccontextmanager
import csv
import asyncio
import random
import httpx
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import redis.asyncio as redis

app = FastAPI(title="SensorQuery")


@asynccontextmanager
async def lifespan(_:FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(id="job1",func=query_mock(1),trigger=CronTrigger(second=0))
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)
    
    
# Magazyn wyników: {sensor_id: {"ip": ip, "temperature": val, "humidity": val}}
sensor_data = {}
redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)



async def query_mock(sensor_id: int):
    """
    Mock funkcja zwracająca dane z czujnika na podstawie ID.
    """    
    temperature = round(random.uniform(15, 26), 1)  # Zakres 15.0–26.0
    humidity = round(random.uniform(35, 65), 1)     # Zakres 35.0–65.0
    
    return {
            "sensor_id": sensor_id,
            "temperature": f"{temperature}",
            "humidity": f"{humidity}"
    }

@app.get("/{sensor_id}/data")
async def get_sensor_data(sensor_id):

    data = await query_mock(sensor_id)
    

    await redis_client.xadd("sensor_stream", {
        "sensor_id": str(data["sensor_id"]),
        "temperature": str(data["temperature"]),
        "humidity": str(data["humidity"])
    })
    
    return {f"Dane" : data}
