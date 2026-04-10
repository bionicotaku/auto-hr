#!/usr/bin/env bash

set -euo pipefail

if [ ! -x "./.venv/bin/python" ]; then
  echo "[test] missing ./.venv/bin/python, run ./scripts/bootstrap.sh first"
  exit 1
fi

echo "[test] running backend tests"
./.venv/bin/python -m pytest apps/api/tests
