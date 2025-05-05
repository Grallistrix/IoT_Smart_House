FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalacja bibliotek systemowych wymaganych do budowy niektórych paczek
RUN apt-get update && \
    apt-get install -y gcc libpq-dev python3-dev build-essential libgomp1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kopiujemy tylko requirements.txt aby zcache’ować zależności
COPY ./app/requirements.txt .

# Instalujemy zależności – ta warstwa się cache’uje
RUN pip install --no-cache-dir -r requirements.txt

# Nie kopiujemy kodu źródłowego – będzie zamontowany z hosta
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
