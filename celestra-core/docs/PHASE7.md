# Celestra Core — Phase 7 production hardening

Phase 7 does not add new top-level product modules. It hardens Phases 1–6 for multi-worker and cloud deployments.

## Backends

| Concern | Setting | Options | Default |
|---|---|---|---|
| Conversation memory | `CELESTRA_MEMORY_CONVERSATION_BACKEND` | `memory`, `redis` | `memory` |
| Vector / RAG store | `CELESTRA_MEMORY_VECTOR_BACKEND` | `memory`, `postgres` | `memory` |
| Workflow runs | `CELESTRA_WORKFLOW_RUN_BACKEND` | `memory`, `redis` | `memory` |
| Email | `CELESTRA_SMTP_*` | logging (unset) / SMTP | logging |
| Stripe Checkout | `CELESTRA_STRIPE_SECRET_KEY` + price map | optional | off |
| OIDC SSO | `CELESTRA_OIDC_*` | optional | off |

## Postgres tables (migration `0003_platform_persistence`)

- `platform_vector_records` — JSONB embeddings (pgvector-ready path later)
- `billing_subscriptions`, `billing_usage_events`
- `analytics_events`
- `knowledge_bases`, `knowledge_documents`

```bash
alembic upgrade head
```

## Recommended production profile

```bash
CELESTRA_MEMORY_CONVERSATION_BACKEND=redis
CELESTRA_MEMORY_VECTOR_BACKEND=postgres
CELESTRA_WORKFLOW_RUN_BACKEND=redis
CELESTRA_SMTP_HOST=smtp.example.com
CELESTRA_SMTP_FROM=noreply@example.com
CELESTRA_STRIPE_SECRET_KEY=sk_live_...
CELESTRA_STRIPE_PRICE_MAP=pro=price_xxx,enterprise=price_yyy
CELESTRA_OIDC_ISSUER=https://your-idp/.well-known-or-issuer
CELESTRA_OIDC_CLIENT_ID=...
CELESTRA_OIDC_CLIENT_SECRET=...
CELESTRA_OIDC_REDIRECT_URI=https://api.example.com/api/v1/auth/oidc/callback
```

## New HTTP surfaces

- `GET /api/v1/auth/oidc/authorize` — returns authorization URL + state
- `GET /api/v1/auth/oidc/callback` — exchanges code for tokens (+ optional userinfo)
- `GET /api/v1/auth/oidc/status` — configuration probe
- `POST /api/v1/billing/stripe/checkout` — Stripe Checkout Session (auth required)

## App import

```python
from auth.oidc import OIDCClient, OIDCSettings
from billing.stripe import StripeAdapter
from memory.factory import build_conversation_store, build_vector_store
from workflows.factory import build_workflow_stack
```

Product apps still import Core services only — they do not reimplement stores, SSO, or Stripe.
