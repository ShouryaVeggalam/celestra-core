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

# Neon / some hosts issue postgres:// — SQLAlchemy prefers postgresql://
if [[ "${DATABASE_URL}" == postgres://* ]]; then
  export DATABASE_URL="postgresql://${DATABASE_URL#postgres://}"
fi

# Neon requires SSL; append if the URL has no sslmode
if [[ "${DATABASE_URL}" == postgresql* ]] && [[ "${DATABASE_URL}" != *"sslmode="* ]]; then
  if [[ "${DATABASE_URL}" == *"?"* ]]; then
    export DATABASE_URL="${DATABASE_URL}&sslmode=require"
  else
    export DATABASE_URL="${DATABASE_URL}?sslmode=require"
  fi
fi

export PYTHONUNBUFFERED=1
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
