FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/Present/package*.json ./
RUN npm ci
COPY frontend/Present/ ./
RUN npm run build

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    BACKEND_PORT=3000

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx gettext-base curl \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /etc/nginx/sites-enabled/default

WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist
COPY cloud-run/nginx.conf.template /etc/nginx/templates/cloud-run.conf.template
COPY cloud-run/start.sh /app/start.sh

EXPOSE 8080

CMD ["/bin/sh", "/app/start.sh"]
