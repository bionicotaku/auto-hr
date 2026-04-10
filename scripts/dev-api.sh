#!/usr/bin/env bash

set -euo pipefail

if [ ! -x "./.venv/bin/python" ]; then
  echo "[dev-api] missing ./.venv/bin/python, run ./scripts/bootstrap.sh first"
  exit 1
fi

cd apps/api
../../.venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
