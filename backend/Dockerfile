# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN apt update && apt install -y build-essential \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]