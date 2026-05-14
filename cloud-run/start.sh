#!/bin/sh
set -eu

: "${PORT:=8080}"
: "${BACKEND_PORT:=3000}"

envsubst '${PORT} ${BACKEND_PORT}' \
    < /etc/nginx/templates/cloud-run.conf.template \
    > /etc/nginx/nginx.conf

uvicorn main:app --host 127.0.0.1 --port "${BACKEND_PORT}" &
backend_pid="$!"

trap 'kill "${backend_pid}" 2>/dev/null || true' INT TERM

for _ in $(seq 1 120); do
    if curl -fsS "http://127.0.0.1:${BACKEND_PORT}/api/health" >/dev/null; then
        exec nginx -g 'daemon off;'
    fi

    if ! kill -0 "${backend_pid}" 2>/dev/null; then
        wait "${backend_pid}"
        exit "$?"
    fi

    sleep 2
done

echo "FastAPI did not become healthy on port ${BACKEND_PORT}" >&2
kill "${backend_pid}" 2>/dev/null || true
exit 1
