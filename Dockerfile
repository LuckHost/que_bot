FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DATA_DIR=/data

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY core/ core/

# Бот работает не от root. uid фиксирован, чтобы на хосте можно было выдать права на ./data
RUN useradd --system --uid 10001 --no-create-home bot \
    && mkdir -p /data /app/core/downloads \
    && chown bot:bot /data /app/core/downloads

USER bot
WORKDIR /app/core

# python — PID 1 и сам получает SIGTERM от docker stop; aiogram на него штатно останавливается
CMD ["python", "main.py"]
