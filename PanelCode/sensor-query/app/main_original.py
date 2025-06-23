import csv
import asyncio
import httpx
from fastapi import FastAPI

app = FastAPI(title="SensorQuery")

CSV_PATH = "app/devices.csv"
FETCH_INTERVAL = 60  # seconds

# Magazyn wyników: {sensor_id: {"ip": ip, "temperature": val, "humidity": val}}
sensor_data = {}

def read_devices_from_csv(path=CSV_PATH):
    devices = {}
    with open(path, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) != 2:
                continue
            sensor_id, ip = row
            devices[sensor_id.strip()] = ip.strip()
    return devices

async def fetch_all_stats():
    while True:
        devices = read_devices_from_csv()
        async with httpx.AsyncClient(timeout=3.0) as client:
            for sensor_id, ip in devices.items():
                try:
                    resp = await client.get(f"http://{ip}/stats")
                    if resp.status_code == 200:
                        text = resp.text.strip()
                        temp, hum = parse_stats(text)
                        sensor_data[sensor_id] = {
                            "ip": ip,
                            "temperature": temp,
                            "humidity": hum
                        }
                    else:
                        sensor_data[sensor_id] = {
                            "ip": ip,
                            "error": f"HTTP {resp.status_code}"
                        }
                except Exception as e:
                    sensor_data[sensor_id] = {
                        "ip": ip,
                        "error": str(e)
                    }
        print(sensor_data)
        await asyncio.sleep(FETCH_INTERVAL)
        
        
def parse_stats(text: str):
    # Data format: "Temperature: XX, Humidity: YY"
    parts = text.split(",")
    temp = parts[0].split(":")[1].strip()
    hum = parts[1].split(":")[1].strip()
    return temp, hum

def get_latest_results():
    return sensor_data

@app.get("/readings")
def readings():
    return get_latest_results()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(fetch_all_stats())