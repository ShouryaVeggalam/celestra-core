#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is required" >&2
  exit 1
fi

if [[ "${DATABASE_URL}" == sqlite* ]]; then
  echo "SQLite is refused for hosted start.sh" >&2
  exit 1
fi

export PYTHONUNBUFFERED=1
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
