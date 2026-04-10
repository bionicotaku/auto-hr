#!/usr/bin/env bash

set -euo pipefail

source ./scripts/load-root-env.sh
./scripts/sync-web-env.sh
./scripts/check-port.sh 3000 "dev-web"

pnpm --filter auto-hr-web dev
