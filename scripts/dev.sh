#!/usr/bin/env bash

set -euo pipefail

source ./scripts/load-root-env.sh

API_PID=""
WEB_PID=""
API_PORT="${API_PORT:-8000}"
WEB_PORT=3000

cleanup() {
  local exit_code=$?
  trap - EXIT INT TERM

  if [ -n "$API_PID" ] && kill -0 "$API_PID" >/dev/null 2>&1; then
    kill "$API_PID" >/dev/null 2>&1 || true
  fi

  if [ -n "$WEB_PID" ] && kill -0 "$WEB_PID" >/dev/null 2>&1; then
    kill "$WEB_PID" >/dev/null 2>&1 || true
  fi

  wait >/dev/null 2>&1 || true
  exit "$exit_code"
}

trap cleanup EXIT INT TERM

./scripts/check-port.sh "$API_PORT" "dev"
./scripts/check-port.sh "$WEB_PORT" "dev"

echo "[dev] starting API on http://localhost:$API_PORT"
./scripts/dev-api.sh &
API_PID=$!

echo "[dev] starting Web on http://localhost:$WEB_PORT"
./scripts/dev-web.sh &
WEB_PID=$!

echo "[dev] both services are starting"
echo "[dev] press Ctrl+C to stop both"

while true; do
  if ! kill -0 "$API_PID" >/dev/null 2>&1; then
    wait "$API_PID"
    exit $?
  fi

  if ! kill -0 "$WEB_PID" >/dev/null 2>&1; then
    wait "$WEB_PID"
    exit $?
  fi

  sleep 1
done
