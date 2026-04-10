#!/usr/bin/env bash

set -euo pipefail

if [ ! -x "./.venv/bin/python" ]; then
  echo "[lint] missing ./.venv/bin/python, run ./scripts/bootstrap.sh first"
  exit 1
fi

echo "[lint] running backend syntax checks"
./.venv/bin/python -m compileall apps/api/app apps/api/tests
