ARG BUILD_FROM

FROM --platform=$BUILDPLATFORM node:22-alpine AS frontend
WORKDIR /frontend
COPY app/frontend/package*.json ./
RUN npm install
COPY app/frontend/ ./
RUN npm run build

FROM ${BUILD_FROM}

ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    QUESTMATH_DATA_DIR=/data \
    QUESTMATH_BACKUP_DIR=/data/backups

RUN apk add --no-cache python3 py3-pip py3-setuptools tzdata \
    && python3 -m venv /opt/questmath \
    && /opt/questmath/bin/pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY app/backend/requirements.txt /app/requirements.txt
RUN /opt/questmath/bin/pip install --no-cache-dir -r /app/requirements.txt

COPY app/backend/ /app/
COPY --from=frontend /frontend/dist /app/static
COPY rootfs /

RUN chmod a+x /etc/services.d/questmath/run \
    && mkdir -p /data/backups

EXPOSE 8080
