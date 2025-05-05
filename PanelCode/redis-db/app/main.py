from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import redis.asyncio as redis
import json
from typing import List
from fastapi import Query


app = FastAPI()

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
class SensorPayload(BaseModel):
    sensor_id: str
    temperature: float
    humidity: float
    
from datetime import timedelta


@app.post("/sensor")
async def store_sensor_data(data: SensorPayload):
    try:
        # Utwórz znacznik czasu w formacie DD.MM.YY.HH:MM
        timestamp = datetime.now().strftime("%d.%m.%y.%H:%M")

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
@app.post("/delete")
async def delete_all_data():
    try:
        await redis_client.flushdb()
        return {"message": "Wszystkie dane zostały usunięte z Redis"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas usuwania danych: {e}")