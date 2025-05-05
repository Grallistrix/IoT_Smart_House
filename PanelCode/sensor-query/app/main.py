from contextlib import asynccontextmanager
import csv
import asyncio
import json
import random
import httpx
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import redis.asyncio as redis
from apscheduler.triggers.interval import IntervalTrigger

app = FastAPI(title="SensorQuery")


@asynccontextmanager
async def lifespan(_:FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        id="job1",
        func=lambda: get_sensor_data(1),
        trigger=IntervalTrigger(seconds=10)
    )
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)
    
    
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

@app.get("/{sensor_id}/channel")
async def get_sensor_data(sensor_id: int):
    data = await query_mock(sensor_id)
    await redis_client.publish("sensor_channel", json.dumps(data))
    
    return {"status": "published", "channel": "sensor_channel", "data": data}

@app.get("/{sensor_id}/stream")
async def get_sensor_data_stream(sensor_id):

    data = await query_mock(sensor_id)
    

    await redis_client.xadd("sensor_stream", {
        "sensor_id": str(data["sensor_id"]),
        "temperature": str(data["temperature"]),
        "humidity": str(data["humidity"])
    })
    
    return {f"Dane" : data}
