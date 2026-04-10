#!/usr/bin/env bash

set -euo pipefail

echo "[bootstrap] checking local toolchain"
command -v node >/dev/null 2>&1 || { echo "node is required"; exit 1; }
command -v pnpm >/dev/null 2>&1 || { echo "pnpm is required"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "python3 is required"; exit 1; }

if [ ! -d ".venv" ]; then
  echo "[bootstrap] creating root virtual environment at ./.venv"
  python3 -m venv .venv
fi

echo "[bootstrap] installing backend dependencies into ./.venv"
./.venv/bin/pip install -e "apps/api[dev]"

mkdir -p \
  data/uploads/jobs \
  data/uploads/candidates \
  data/tmp/candidate-imports \
  apps/web \
  apps/api \
  packages/ui \
  packages/config

if [ -f "apps/web/package.json" ]; then
  echo "[bootstrap] installing workspace node dependencies"
  pnpm install
fi

./scripts/sync-web-env.sh
./scripts/migrate-api.sh

echo "[bootstrap] workspace skeleton is ready"
echo "[bootstrap] python runtime: ./.venv/bin/python"
