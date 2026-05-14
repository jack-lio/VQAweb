#!/bin/sh
set -eu

: "${PORT:=8080}"
: "${BACKEND_PORT:=3000}"

envsubst '${PORT} ${BACKEND_PORT}' \
    < /etc/nginx/templates/cloud-run.conf.template \
    > /etc/nginx/nginx.conf

nginx -g 'daemon off;' &
nginx_pid="$!"

trap 'kill "${nginx_pid}" 2>/dev/null || true' INT TERM

exec uvicorn main:app --host 127.0.0.1 --port "${BACKEND_PORT}"
