#!/usr/bin/env bash
set -euo pipefail

# Quick bootstrap for local development using SQLite.
# 1) Make sure you are inside your virtualenv (if any)
# 2) Run: bash scripts/dev_quickstart.sh

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

python -m pip install --upgrade pip >/dev/null
python -m pip install -r requirements/base.txt -e packages/common aiosqlite >/dev/null

export DATABASE_URL=${DATABASE_URL:-sqlite+aiosqlite:///./dev.db}
export SYNC_DATABASE_URL=${SYNC_DATABASE_URL:-sqlite:///./dev.db}
export DEFAULT_LLM_PROVIDER=${DEFAULT_LLM_PROVIDER:-mock}

echo "[quickstart] DATABASE_URL=${DATABASE_URL}"

echo "[quickstart] Starting FastAPI on http://127.0.0.1:8000 ..."
uvicorn services.api.src.main:app --reload --port 8000
