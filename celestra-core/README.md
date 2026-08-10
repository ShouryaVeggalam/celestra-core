# Celestra Core

**Enterprise AI platform foundation** for every Celestra application.

> **Current status: Phase 7 complete** — production hardening on top of Phases 1–6.

## Phases

| Phase | Status | Modules |
|---|---|---|
| 1 | Done | `config/`, `database/`, `shared/`, `core/` |
| 2 | Done | `auth/`, `monitoring/` |
| 3 | Done | `ai/`, `providers/`, `prompts/` |
| 4 | Done | `agents/`, `workflows/`, `memory/` |
| 5 | Done | `storage/`, `notifications/`, `knowledge/` |
| 6 | Done | `billing/`, `analytics/`, `sdk/` |
| 7 | Done | Redis/Postgres durable stores, SMTP, Stripe, OIDC |

## Phase 7 highlights

| Capability | Location |
|---|---|
| Redis conversation + workflow run stores | `memory/redis_store.py`, `workflows/redis_store.py` |
| Postgres JSONB vectors + platform tables | `database/platform_models.py`, migration `0003` |
| SMTP email | `notifications/channels/smtp.py` |
| Stripe Checkout | `billing/stripe.py` |
| OIDC SSO helpers | `auth/oidc.py` |

## Product app import

```python
from sdk import CelestraSDK, CelestraClient
from billing import BillingService
from analytics import AnalyticsService, TrackEventRequest
from auth.oidc import OIDCClient
from billing.stripe import StripeAdapter
```

## Quick start

```bash
cd celestra-core
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
docker compose up -d postgres redis
alembic upgrade head
uvicorn core.app:create_app --factory --reload
```

## Docs

- [Phase 7](docs/PHASE7.md) · [Billing](docs/BILLING.md) · [Analytics](docs/ANALYTICS.md) · [SDK](docs/SDK.md)
- [Architecture](docs/ARCHITECTURE.md) · [Getting started](docs/GETTING_STARTED.md)
