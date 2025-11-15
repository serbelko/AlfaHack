FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# системные зависимости для psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# обновляем pip и ставим зависимости
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
 && python -m pip install --no-cache-dir -r requirements.txt \
 && python -m pip install --no-cache-dir pytest pytest-cov pytest-asyncio httpx

# копируем проект
COPY . .

# ВАЖНО: у тебя main.py лежит прямо в back/app, а в нём должно быть:
# app = FastAPI()
#
# Запускаем FastAPI через python -m uvicorn, чтобы не зависеть от PATH
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
