#!/usr/bin/env bash

set -euo pipefail

source ./scripts/load-root-env.sh

API_PID=""
WEB_PID=""
API_PORT="${API_PORT:-8000}"
WEB_PORT=3000
SHUTTING_DOWN=0
EXIT_CODE=0
STARTED_PID=""

start_service() {
  python3 -c 'import os, sys; os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])' "$@" &
  STARTED_PID="$!"
}

is_running() {
  local pid="$1"
  [ -n "$pid" ] && kill -0 "$pid" >/dev/null 2>&1
}

signal_group() {
  local signal="$1"
  local pid="$2"

  if is_running "$pid"; then
    kill "-$signal" "-$pid" >/dev/null 2>&1 || true
  fi
}

wait_for_pid() {
  local pid="$1"

  if [ -n "$pid" ]; then
    wait "$pid" >/dev/null 2>&1 || true
  fi
}

stop_services() {
  local signal="$1"
  signal_group "$signal" "$API_PID"
  signal_group "$signal" "$WEB_PID"
}

force_stop() {
  echo
  echo "[dev] forcing API and Web to stop"
  stop_services KILL
}

begin_shutdown() {
  local signal="$1"
  local exit_code="$2"

  if [ "$SHUTTING_DOWN" -eq 1 ]; then
    force_stop
    return
  fi

  SHUTTING_DOWN=1
  EXIT_CODE="$exit_code"
  trap force_stop INT TERM

  echo
  echo "[dev] stopping API and Web"
  stop_services "$signal"
}

cleanup() {
  local exit_code=$?
  trap - EXIT INT TERM

  if [ "$SHUTTING_DOWN" -eq 0 ]; then
    stop_services TERM
  fi

  wait_for_pid "$API_PID"
  wait_for_pid "$WEB_PID"

  if [ "$EXIT_CODE" -ne 0 ]; then
    exit "$EXIT_CODE"
  fi

  exit "$exit_code"
}

trap cleanup EXIT
trap 'begin_shutdown INT 130' INT
trap 'begin_shutdown TERM 143' TERM

./scripts/check-port.sh "$API_PORT" "dev"
./scripts/check-port.sh "$WEB_PORT" "dev"

echo "[dev] starting API on http://localhost:$API_PORT"
start_service ./scripts/dev-api.sh
API_PID="$STARTED_PID"

echo "[dev] starting Web on http://localhost:$WEB_PORT"
start_service ./scripts/dev-web.sh
WEB_PID="$STARTED_PID"

echo "[dev] both services are starting"
echo "[dev] press Ctrl+C to stop both"

while true; do
  if [ "$SHUTTING_DOWN" -eq 1 ]; then
    if ! is_running "$API_PID" && ! is_running "$WEB_PID"; then
      exit "$EXIT_CODE"
    fi

    sleep 1
    continue
  fi

  if ! is_running "$API_PID"; then
    if wait "$API_PID"; then
      EXIT_CODE=0
    else
      EXIT_CODE=$?
    fi

    SHUTTING_DOWN=1
    echo "[dev] API exited, stopping Web"
    stop_services TERM
    wait_for_pid "$WEB_PID"
    exit "$EXIT_CODE"
  fi

  if ! is_running "$WEB_PID"; then
    if wait "$WEB_PID"; then
      EXIT_CODE=0
    else
      EXIT_CODE=$?
    fi

    SHUTTING_DOWN=1
    echo "[dev] Web exited, stopping API"
    stop_services TERM
    wait_for_pid "$API_PID"
    exit "$EXIT_CODE"
  fi

  sleep 1
done
