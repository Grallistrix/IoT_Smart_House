import asyncio
import requests
from bs4 import BeautifulSoup
import re
from fastapi import FastAPI
from pydantic import BaseModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
import asyncio
import json
import redis.asyncio as redis
import json


# Tworzymy instancję FastAPI oraz schedulujemy cronjob do sprawdzania danych
@asynccontextmanager
async def lifespan(_:FastAPI):
    print('Webscrapper uruchomiony!')
    scheduler = AsyncIOScheduler()
    scheduler.add_job(id="job1",func=publish_data,trigger=CronTrigger(second=0))
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)
    

app = FastAPI(lifespan=lifespan,title="WebScrapper")
grouped_data = {} 
        

async def scrap_data():
    grouped_data={}
    url = 'http://cena-pradu.pl/tabela.html'
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all(class_='MsoTableGrid')

        if not tables:
            raise ValueError("Nie znaleziono żadnych elementów z klasą 'MsoTableGrid'.")

        table = tables[0]
        rows = table.find_all('tr')[:-1]  # pomijamy ostatni wiersz (przypis)

        cleaned_data = []

        for i, row in enumerate(rows, start=1):
            cells = row.find_all(['td', 'th'])
            if i == 2:
                cell_texts = [re.sub(r'\s+', ' ', cell.get_text(strip=True)).replace(',', '.') for cell in cells]
            else:
                cell_texts = [cell.get_text(strip=True).replace(',', '.') for cell in cells]
            cleaned_data.append(cell_texts)

        grouped_data = []

        for col_index in range(1, len(cleaned_data[0])):
            record = {
                'FIRMA': cleaned_data[0][col_index],
                'TARYFA': cleaned_data[1][col_index],
                'PRAD': cleaned_data[2][col_index],
                'SUMA': cleaned_data[3][col_index],
            }
            grouped_data.append(record)
        return grouped_data

    except requests.RequestException as e:
        raise RuntimeError(f"Błąd podczas pobierania strony: {e}")
    except Exception as e:
        raise RuntimeError(f"Wystąpił nieoczekiwany błąd: {e}")

@app.post("/scrap_data")
async def scrap_and_send():
    try:
        result = await scrap_data()
        for record in result:
            url = "http://redis_controller:8000/electricity"
            response = requests.post(url, json=record)
            response.raise_for_status()            
        return {"Zwrot": result}
    except requests.RequestException as e:
        raise RuntimeError(f"Błąd podczas pobierania strony: {e}")
    except Exception as e:
        raise RuntimeError(f"Wystąpił nieoczekiwany błąd: {e}")
        
@app.get("/get_data")
async def get_data():
    try:
        result = await scrap_data()       
        return {"Dane":result}  
    except requests.RequestException as e:
        raise RuntimeError(f"Błąd podczas pobierania strony: {e}")
    except Exception as e:
        raise RuntimeError(f"Wystąpił nieoczekiwany błąd: {e}")     
    
@app.post("/publish_post")
async def publish_data():
    result = await scrap_data()
    for record in result:
        message = json.dumps(record)
        redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
        await redis_client.publish("electricity_channel", message)
    return {"status": "Wysłano dane do kanału Redis"}