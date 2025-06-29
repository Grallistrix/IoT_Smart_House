from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
import redis.asyncio as redis
import json
from typing import Dict, List
from fastapi import Query, Request
import asyncio

import redis.asyncio as redis
import json
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware



class RedisSubscriber:
    def __init__(self, redis_host="redis", redis_port=6379):
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

    async def listen(self):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe("electricity_channel")

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            channel = message["channel"]
            try:
                data = json.loads(message["data"])
                now = datetime.now()

                if channel == "electricity_channel":
                    today = now.strftime("%d.%m.%Y")
                    key = f"{data['FIRMA']}_{today}"

                    exists = await self.redis.exists(key)
                    if not exists:
                        await self.redis.set(key, json.dumps(data))
                        print(f"[INFO] [electricity] Zapisano dane pod kluczem: {key}")
                    else:
                        print(f"[INFO] [electricity] Dane już istnieją dla klucza: {key}")


            except Exception as e:
                print(f"[ERROR] [{channel}] Błąd podczas przetwarzania wiadomości: {e}")

                
                
                
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Inicjalizacja Redis
redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)


# Model danych
class ElectricityPayload(BaseModel):
    FIRMA: str
    TARYFA: str
    PRAD: str
    SUMA: str


@app.post("/electricity")
async def store_electricity_data(data: ElectricityPayload):
    try:
        # Format daty: DD.MM.YYYY
        today = datetime.now().strftime("%d.%m.%Y")
        key = f"{data.FIRMA}_{today}"

        # Sprawdzenie, czy już istnieje wpis
        existing = await redis_client.exists(key)
        if existing:
            raise HTTPException(status_code=409, detail=f"Dane dla firmy {data.FIRMA} na dzień {today} już istnieją.")

        # Zapis danych jako JSON
        json_data = json.dumps(data.dict())
        await redis_client.set(key, json_data)

        return {"message": f"Dane zapisane pod kluczem {key}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd zapisu danych: {e}")
    
    
@app.get("/electricity/date")
async def get_data_by_date(day: str = Query(..., regex=r"^\d{2}\.\d{2}\.\d{4}$")):
    try:
        pattern = f"*_{day}"
        keys = await redis_client.keys(pattern)

        if not keys:
            return {"message": f"Brak danych dla daty {day}", "results": []}

        # Pobierz wartości dla wszystkich znalezionych kluczy
        values = await redis_client.mget(keys)

        # Przekształć dane JSON do obiektów Python
        results = [json.loads(v) for v in values if v]

        return {
            "date": day,
            "count": len(results),
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd pobierania danych: {e}")

#===========================================================================
from datetime import timedelta


class SensorPayload(BaseModel):
    sensor_id: str
    temperature: float
    humidity: float
    


@app.get("/ping")
async def ping():
    try:

        return {"message": f"Server is online"}

    except Exception as e:
        raise HTTPException("Err")

@app.post("/sensor")
async def store_sensor_data(data: SensorPayload):
    try:
        # Utwórz znacznik czasu w formacie DD.MM.YY.HH:MM
        timestamp = datetime.now().strftime("%d.%m.%y.%H:%M.%S")

        # Klucz Redis: SENSOR_<ID>_MDD.MM.YY.HH:MM
        key = f"SENSOR_{data.sensor_id}_{timestamp}"

        # JSON z danymi
        json_data = json.dumps(data.dict())

        # TTL = 7 dni
        await redis_client.set(key, json_data, ex=timedelta(days=7))

        return {"message": f"Dane zapisane pod kluczem {key}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd zapisu danych z sensora: {e}")


@app.get("/sensor/{sensor_id}/values")
async def get_sensor_values(sensor_id: str, count: int = 10):
    try:
        pattern = f"SENSOR_{sensor_id}_*"
        keys = await redis_client.keys(pattern)

        # Posortuj po dacie (klucze zawierają znacznik czasu)
        sorted_keys = sorted(keys, reverse=True)[:count]

        values = await redis_client.mget(sorted_keys)
        results = [json.loads(v) for v in values if v]

        return {
            "sensor_id": sensor_id,
            "count": len(results),
            "values": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd pobierania danych: {e}")
    
#==================================================================================================================================
@app.get("/new_sensor/{sensor_id}/values")
async def get_sensor_values( sensor_id: str, count: int):
    try:
        # Pobierz ostatnie wpisy w streamie (maksymalnie 1000 do przeszukania)
        entries = await redis_client.xrevrange("sensor_stream", max="+", min="-", count=1000)

        sensor_values = []
        for message_id, fields in entries:
            if fields.get("sensor_id") == sensor_id:
                sensor_values.append({
                    "sensor_id": sensor_id,
                    "temperature": fields.get("temperature"),
                    "humidity": fields.get("humidity")
                })
                if len(sensor_values) >= count:
                    break

        # Odwracamy, by były w kolejności rosnącej czasu (najstarsze -> najnowsze)
        sensor_values.reverse()

        return {
            "sensor_id": sensor_id,
            "count": len(sensor_values),
            "values": sensor_values
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd pobierania danych: {e}")
#===
@app.delete("/delete")
async def delete_all_data():
    try:
        await redis_client.flushdb()
        return {"message": "Wszystkie dane zostały usunięte z Redis"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas usuwania danych: {e}")
    
    
@app.on_event("startup")
async def startup_event():
    subscriber = RedisSubscriber()
    asyncio.create_task(subscriber.listen())

#================================================================================================================
@app.get("/stream")
async def read_stream(last_id: str = Query("0", description="ID od którego czytać, domyślnie od początku")):

    # Pobierz dane ze strumienia
    response = await redis_client.xread({"sensor_stream": last_id}, count=50, block=1000)

    # Konwersja na czytelny JSON
    stream_data: List[Dict] = []
    for stream_name, messages in response:
        for message_id, fields in messages:
            stream_data.append({
                "id": message_id,
                "data": fields
            })

    return {"entries": stream_data}

#================================================================================================================


@app.get("/login")
async def login(request: Request):
    try:
        
        username = request.headers.get('Authorization').split(' ')[0]
        password = request.headers.get('Authorization').split(' ')[1]
        assert await redis_client.lpos("users", password) is not None, 'Invalid credentials'
        return {f"Ur login: {username}, ur password: {password}"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ERR: {e}")
