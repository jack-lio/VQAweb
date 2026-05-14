#!/bin/sh
set -eu

: "${PORT:=8080}"
: "${BACKEND_PORT:=3000}"

uvicorn main:app --host 127.0.0.1 --port "${BACKEND_PORT}" &
backend_pid="$!"

envsubst '${PORT} ${BACKEND_PORT}' \
    < /etc/nginx/templates/cloud-run.conf.template \
    > /etc/nginx/nginx.conf

trap 'kill "${backend_pid}" 2>/dev/null || true' INT TERM

nginx -g 'daemon off;' &
nginx_pid="$!"

wait "${nginx_pid}"
