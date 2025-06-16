from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List
from fastapi.responses import Response
from typing import Annotated
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import httpx




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
security = HTTPBasic()

   
@app.get("/test", status_code=204)
def test_endpoint():
    return Response(status_code=204)


class User(BaseModel):
    user_id: int
    username: str
    password: str


@app.get("/users/me")
def read_current_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    return {"username": credentials.username, "password": credentials.password}



@app.get("/forward-login")
async def forward_login(request: Request):
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=400, detail="Authorization header missing")

        headers = {"Authorization": auth_header}


        target_url = "http://redis-controller:8000/login"

        async with httpx.AsyncClient() as client:
            response = await client.get(target_url, headers=headers)

        return {
            "status_code": response.status_code,
            "response": response.json()
        }

    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Request error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

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