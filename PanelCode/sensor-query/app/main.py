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
import aiohttp
import re

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



async def zapytaj_sensor(sensor_id: str):
    url = f"http://192.168.11.17/stats"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
            
            # Przykład odpowiedzi: "Temperature: 26, Humidity: 52.25"
            match = re.match(r"Temperature:\s*([\d.]+),\s*Humidity:\s*([\d.]+)", text)
            if not match:
                raise ValueError("Niepoprawny format danych z sensora")

            temperature = float(match.group(1))
            humidity = float(match.group(2))

            return {
                "sensor_id": sensor_id,
                "temperature": temperature,
                "humidity": humidity
            }

async def query_mock2(sensor_id: int):
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
    data = await zapytaj_sensor(sensor_id)
    await redis_client.publish("sensor_channel", json.dumps(data))
    
    return {"status": "published", "channel": "sensor_channel", "data": data}

@app.get("/{sensor_id}/stream")
async def get_sensor_data_stream(sensor_id):

    data = await zapytaj_sensor(sensor_id)
    

    await redis_client.xadd("sensor_stream", {
        "sensor_id": str(data["sensor_id"]),
        "temperature": str(data["temperature"]),
        "humidity": str(data["humidity"])
    })
    
    return {f"Dane" : data}
