from fastapi import FastAPI, HTTPException
from redis_manager import RedisManager
from pydantic import BaseModel
from typing import List

app = FastAPI()
db = RedisManager()

class ElectricityData(BaseModel):
    date: str
    time: str
    price_per_hour: float

class SensorData(BaseModel):
    sensor_number: int
    date: str
    time: str
    temperature_value: int
    humidity_value: float
    
class ElectricityUsageResponse(BaseModel):
    Day: str
    Time: str
    PricePerHour: str

class SensorDataResponse(BaseModel):
    SensorNumber: str
    Day: str
    Time: str
    TemperatureValue: str
    HumidityValue: str

@app.post("/add_electricity_data")
async def add_electricity_usage(data: ElectricityData):
    try:
        db.add_electricity_usage(data.date, data.time, data.price_per_hour)
        return {"message": "Electricity usage data added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/add_sensor_data")
async def add_sensor_data(data: SensorData):
    try:
        db.add_sensor_data(data.sensor_number, data.date, data.time, data.temperature_value, data.humidity_value)
        return {"message": "Sensor data added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/get_electricity_usage/{date}/{time}", response_model=ElectricityUsageResponse)
async def get_electricity_usage(date: str, time: str):
    data = db.get_electricity_usage(date, time)
    if not data:
        raise HTTPException(status_code=404, detail="Electricity usage not found")
    return data

@app.get("/get_sensor_data/{sensor_number}/{date}/{time}", response_model=SensorDataResponse)
async def get_sensor_data(sensor_number: int, date: str, time: str):
    data = db.get_sensor_data(sensor_number, date, time)
    if not data:
        raise HTTPException(status_code=404, detail="Sensor data not found")
    return data


@app.get("/get_last_electricity_usage/{num_values}", response_model=List[ElectricityUsageResponse])
async def get_last_electricity_usage(num_values: int):
    data = db.get_last_electricity_usage(num_values)
    if not data:
        raise HTTPException(status_code=404, detail="No electricity usage data found")
    return data

@app.get("/get_last_sensor_data/{sensor_number}/{num_values}", response_model=List[SensorDataResponse])
async def get_last_sensor_data(sensor_number: int, num_values: int):
    data = db.get_last_sensor_data(sensor_number, num_values)
    if not data:
        raise HTTPException(status_code=404, detail="No sensor data found")
    return data

