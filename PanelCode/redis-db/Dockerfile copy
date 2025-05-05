FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt install -y gcc libpq-dev python3-dev build-essential libgomp1


RUN pip install --upgrade pip
COPY ./app/requirements.txt .
RUN pip install  --no-cache-dir -r requirements.txt

#===

FROM builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /z


WORKDIR /app

COPY app/requirements.txt requirements.txt

RUN apt-get update
RUN apt install -y gcc libpq-dev python3-dev build-essential libgomp1

COPY app .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:5000", "--timeout", "2137"]
