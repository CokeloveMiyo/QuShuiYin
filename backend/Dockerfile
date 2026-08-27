# 适配 Render 等平台注入的 PORT
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
RUN mkdir -p /app/static/videos && chmod -R 777 /app/static/videos

EXPOSE 8051

# Render 会注入 $PORT；本地默认 8051
CMD gunicorn --workers 2 --bind 0.0.0.0:${PORT:-8051} --timeout 120 app:app
