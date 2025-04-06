import asyncio
import httpx  
import asyncio
import requests
from bs4 import BeautifulSoup
import re
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
grouped_data = {}

'''
FETCH_INTERVAL = 10  # seconds

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(scrap_data())
'''   

# Tworzymy instancję FastAPI
app = FastAPI()

# Funkcja do scrapowania danych
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

def sent_to_controller(data):
    try:
        response = requests.post(REDIS_CONTROLLER_URL, json=data)
        response.raise_for_status()
        print("Dane zostały wysłane pomyślnie do serwisu redis_controller.")
    except requests.RequestException as e:
        print(f"Błąd podczas wysyłania danych do serwisu redis_controller: {e}")

@app.get("/scrap_data")
async def scrap_and_send():
    try:
        # Scrapowanie danych
        dane = await scrap_data()
        print(dane)  # Można dodać zapis danych do pliku/bazy danych

        # Wysłanie danych do redis_controller
        # sent_to_controller(dane)

        return {"Dane": dane}
    except Exception as e:
        return {"error": f"Wystąpił błąd: {e}"}
