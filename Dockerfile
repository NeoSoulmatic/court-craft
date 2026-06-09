# All-in-one image for cloud deploy (API + static UI on one port).
# Local dev uses docker-compose with separate api + web services.

FROM node:22-alpine AS frontend-build

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY ml ./ml
COPY --from=frontend-build /frontend/dist ./static

COPY backend/docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PYTHONPATH=/app/backend:/app
ENV PYTHONUNBUFFERED=1
ENV SERVE_STATIC=1

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
