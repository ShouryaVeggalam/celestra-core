# Architecture — Celestra Core

## Purpose

Celestra Core is the shared platform kernel. Product apps depend on it the way services depend on cloud SDKs.

```
Product Apps (Hiring AI, Revenue AI, ...)
        │ import celestra-core
        ▼
┌──────────────────────────────────────────────────┐
│ Celestra Core                                     │
│  core/  config/  database/  shared/               │
│  auth/ monitoring/ ai/ providers/ prompts/            │
│  storage/ notifications/ knowledge/                   │
│  billing/ analytics/ sdk/ (Phase 6)                   │
│  Redis/Postgres/SMTP/Stripe/OIDC (Phase 7)            │
└──────────────────────────────────────────────────┘
        │
   PostgreSQL · Redis · Prometheus scrapers
```

## Layers

| Layer | Packages |
|---|---|
| Interface / Delivery | `core/`, `auth/router.py`, `monitoring/router.py`, middleware |
| Application | `auth/service.py`, `core/container.py` |
| Domain | `auth/models.py`, `auth/rbac.py` |
| Infrastructure | `database/`, `shared/redis/`, `config/`, `shared/logging/`, `monitoring/metrics.py` |

## Request path (Phase 2)

```
HTTP
  → CORS
  → MonitoringMiddleware   (trace + Prometheus)
  → PerformanceMiddleware
  → RequestContextMiddleware
  → Auth guards (optional per-route)
  → Route
  → Exception handlers (+ error metrics)
```

## Auth model

- Access JWT (short-lived) + refresh JWT (rotating, hashed at rest)
- RBAC via roles → permissions
- API keys for machine access
- Superuser bypasses RBAC checks
- Optional OIDC authorization-code flow (`auth/oidc.py`)

## Dependency rules

1. Product apps depend on Core — never the reverse.
2. Capability modules depend on `shared/`, `config/`, `database/`.
3. Infrastructure is injected via `Container` and FastAPI `Depends`.
4. No module reads `os.environ` for app config — use `get_settings()`.

## Platform complete through Phase 7

All planned capability modules are implemented, with durable Redis/Postgres
backends and optional SMTP, Stripe, and OIDC adapters. Further work is
depth (native pgvector, full SSO user provisioning, etc.), not new top-level packages.
