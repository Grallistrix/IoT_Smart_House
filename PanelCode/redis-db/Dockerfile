FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Potrzebne biblioteki do buildowania zależności (np. psycopg2, numpy itp.)
RUN apt-get update && \
    apt-get install -y gcc libpq-dev python3-dev build-essential libgomp1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instalacja zależności
WORKDIR /app
COPY ./app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Nie kopiujemy kodu - będzie mountowany
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
