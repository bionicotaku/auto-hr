#!/usr/bin/env bash

set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "usage: $0 <port> <label>" >&2
  exit 1
fi

PORT="$1"
LABEL="$2"

if ! command -v lsof >/dev/null 2>&1; then
  exit 0
fi

if lsof_output="$(lsof -nP -iTCP:"$PORT" -sTCP:LISTEN 2>/dev/null)" && [ -n "$lsof_output" ]; then
  echo "[$LABEL] port $PORT is already in use" >&2
  echo "$lsof_output" >&2
  exit 1
fi
