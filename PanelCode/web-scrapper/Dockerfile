FROM python:3.11-slim

# Ustawienie katalogu roboczego
WORKDIR /app

# Instalacja zależności (bez kopiowania całego kodu)
COPY ./app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Używamy CMD, ale kodu *nie kopiujemy* – mountujemy go w docker-compose
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
