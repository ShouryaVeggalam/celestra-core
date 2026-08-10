# Getting Started — Celestra Core

## Prerequisites

- Python 3.11+ (3.12 recommended)
- Docker Desktop

## Setup

```bash
cd celestra-core
python3.12 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
cp .env.example .env
docker compose up -d postgres redis
alembic upgrade head
uvicorn core.app:create_app --factory --reload --port 8000
```

## Verify foundation

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/metrics | head
```

## Verify auth (Phase 2)

```bash
# Register
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@celestra.dev","password":"ChangeMe123!","full_name":"You"}'

# Login
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@celestra.dev","password":"ChangeMe123!"}'

# Me (paste access_token)
curl -s http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## Tests

```bash
pytest -q
```

## Import pattern for product apps

```python
from core.app import create_app
from auth import get_current_user, require_permissions
from monitoring import get_metrics, emit_event

app = create_app()
```

Do **not** implement auth/AI inside product apps — import Core modules.
