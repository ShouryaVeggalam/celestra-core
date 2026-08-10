# Folder structure — Celestra Core

## Phase 1 (foundation)

| Package | Role |
|---|---|
| `config/` | Env loader, Settings, secrets |
| `database/` | SQLAlchemy Base, sessions, Alembic |
| `core/` | App factory, DI, health, CLI |
| `shared/` | Exceptions, logging, middleware, redis, utils |
| `tests/`, `docs/`, `examples/` | Quality + docs |

## Phase 2 (implemented)

### `auth/` … see docs/AUTH.md
### `monitoring/` … see docs/MONITORING.md

## Phase 3 (implemented)

### `ai/`

| File | Role |
|---|---|
| `service.py` | Completions / embeddings facade |
| `router.py` | Model → provider routing |
| `http.py` | `/api/v1/ai/*` |
| `schemas.py` | Request/response DTOs |
| `dependencies.py` | FastAPI DI |

### `providers/`

| File | Role |
|---|---|
| `base.py` | `LLMProvider` ABC |
| `types.py` | Shared message/completion types |
| `registry.py` / `factory.py` | Registration from settings |
| `mock.py` / `openai_compatible.py` / `anthropic.py` | Adapters |

### `prompts/`

| File | Role |
|---|---|
| `template.py` | Jinja prompt template |
| `registry.py` | Versioned registry |
| `loader.py` | File + built-in loaders |
| `library/` | Markdown prompt assets |

## Phase 4 (implemented)

### `memory/` — conversation + vector memory (`docs/MEMORY.md`)
### `agents/` — tools + runtime (`docs/AGENTS.md`)
### `workflows/` — engine + Celery foundation (`docs/WORKFLOWS.md`)

## Phase 5 (implemented)

### `storage/` — object storage (`docs/STORAGE.md`)
### `notifications/` — email/webhook/in-app (`docs/NOTIFICATIONS.md`)
### `knowledge/` — RAG ingestion + query (`docs/KNOWLEDGE.md`)

## Phase 6 (implemented)

- `billing/` — plans, metering, entitlements (`docs/BILLING.md`)
- `analytics/` — product event tracking (`docs/ANALYTICS.md`)
- `sdk/` — `CelestraSDK` + `CelestraClient` (`docs/SDK.md`)

## Phase 7 (implemented)

- Redis conversation / workflow run stores
- Postgres platform tables + JSONB vector store (`docs/PHASE7.md`)
- SMTP email, Stripe Checkout, OIDC SSO helpers

Platform package surface is complete through Phase 7.
