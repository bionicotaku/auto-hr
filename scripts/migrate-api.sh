#!/usr/bin/env bash

set -euo pipefail

if [ ! -x "./.venv/bin/python" ]; then
  echo "[migrate-api] missing ./.venv/bin/python, run ./scripts/bootstrap.sh first"
  exit 1
fi

source ./scripts/load-root-env.sh

echo "[migrate-api] applying database migrations"
./.venv/bin/python -m alembic -c apps/api/alembic.ini upgrade head
