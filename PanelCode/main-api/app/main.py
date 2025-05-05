from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.responses import Response




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
    
    
app = FastAPI(title="Gateway")
   
   
@app.get("/test", status_code=204)
def test_endpoint():
    return Response(status_code=204)

''' 
@app.post("/add_electricity_data")
async def add_electricity_usage(data: ElectricityData):


@app.post("/add_sensor_data")
async def add_sensor_data(data: SensorData):

    
@app.get("/get_electricity_usage/{date}/{time}", response_model=ElectricityUsageResponse)
async def get_electricity_usage(date: str, time: str):


@app.get("/get_sensor_data/{sensor_number}/{date}/{time}", response_model=SensorDataResponse)
async def get_sensor_data(sensor_number: int, date: str, time: str):

@app.get("/get_last_electricity_usage/{num_values}", response_model=List[ElectricityUsageResponse])
async def get_last_electricity_usage(num_values: int):


@app.get("/get_last_sensor_data/{sensor_number}/{num_values}", response_model=List[SensorDataResponse])
async def get_last_sensor_data(sensor_number: int, num_values: int):

'''