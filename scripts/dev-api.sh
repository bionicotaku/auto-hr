#!/usr/bin/env bash

set -euo pipefail

if [ ! -x "./.venv/bin/python" ]; then
  echo "[dev-api] missing ./.venv/bin/python, run ./scripts/bootstrap.sh first"
  exit 1
fi

source ./scripts/load-root-env.sh

API_PORT="${API_PORT:-8000}"
./scripts/check-port.sh "$API_PORT" "dev-api"
./scripts/migrate-api.sh

cd apps/api
../../.venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port "$API_PORT"
