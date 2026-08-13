# Product Integration Guide — Celestra Core v0.8

Concise contract for greenfield products integrating with Core over HTTP.

## 1. Core base URL

Local recommendation: `http://localhost:8001` (leave `8000` for the product API).

Configure via product env, e.g. `CELESTRA_CORE_URL`.

## 2. API version

Stable product surface: **`/api/v1`**.

Ops endpoints (unversioned): `/health`, `/ready`, `/metrics`.

Breaking changes will ship as `/api/v2` with a deprecation window.

## 3. Authentication model

| Credential | Use |
|---|---|
| `X-API-Key` | Service principal (AI, prompt render, bridge exchange) |
| `Authorization: Bearer <Core JWT>` | End-user memory (after bridge exchange) |

Products authenticate **their own** users. The browser never talks to Core.

```
Browser → Product Backend → (optional) Identity Bridge → Core
```

## 4. Application identity

Approved applications (server registry):

`revenue` · `hiring` · `finance` · `chrona`

Memory may also use `default`.

Unknown application IDs are **rejected**. New IDs require a Core config/deploy change.

Never trust an arbitrary frontend header as application authority.

## 5. AI API

`POST /api/v1/ai/complete` — `{prompt|messages|system|model|provider|…}`  
`POST /api/v1/ai/embed`  
`GET /api/v1/ai/providers`

Auth: service API key or user JWT.

## 6. Prompt API

`GET /api/v1/ai/prompts`  
`POST /api/v1/ai/prompts/render` — `{name, version?, variables}`

Platform built-ins: `system.assistant`, `chat.user_turn`, `analysis.summarize`.  
Domain example prompts are **not** loaded by default (`prompts/examples/`).

Keep product-specific prompts in the product.

## 7. Memory API

`POST /api/v1/memory/sessions` — `{session_id?, application}`  
`POST /api/v1/memory/messages` — `{session_id, role, content, application}`  
`GET /api/v1/memory/sessions/{id}/messages?application=`

Requires **end-user Core JWT**. Ownership: Core `user.id` + `application`.  
Foreign / cross-app access → **404**.

Do **not** use `/memory/remember` or `/recall` for multi-tenant product data.

## 8. Identity bridge

`POST /api/v1/auth/bridge/exchange` — `{assertion}` (service API key)

Canonical assertion claims (HS256):

`iss`, `aud`, `sub`, `external_subject`, `product_user_id`, `application`, `iat`, `exp`, `jti`

- `sub` **must** equal `product_user_id`
- `application` must be approved
- `iss` must match the issuer configured for that application
- Mapping key: `(provider=application, application, external_subject)` → Core user UUID
- Mismatch of `product_user_id` for an existing subject → fail closed

**Transitional Revenue compatibility:** `firebase_uid` / `revenue_user_id` still accepted and mapped to `external_subject` / `product_user_id`. Prefer the generic fields for new products.

## 9. Health / readiness

`GET /health` — liveness (no dependency checks)  
`GET /ready` — readiness; **503** when required Redis/DB unavailable

## 10. Request ID

Send `X-Request-ID` (1–128: `A–Z a–z 0–9 . _ -`). Core echoes it.  
`X-Trace-ID` defaults to `request_id` unless explicitly provided.

## 11. Error model

```json
{"error": {"code": "...", "message": "...", "details": {}}}
```

HTTP client categories: `timeout`, `unavailable`, `auth_error`, `validation_error`, `not_found`, `server_error`, …

## 12. Security rules

Never expose to browsers: Core API keys, Core JWTs, bridge secrets, Redis/DB URLs.  
Never log: assertions, JWTs, API keys, prompts, completions, memory bodies, PII.

## 13. What products must NOT do

- Import Core internal Python modules in production
- Call Core from the frontend
- Put domain business logic into Core
- Use free-form application IDs
- Fall back from user JWT memory to a shared API key
- Treat vector remember/recall as multi-tenant safe

## 14. Local development setup

| Service | Port |
|---|---|
| Core | 8001 |
| Product API | 8000 |
| Product FE | 5173 |
| Core Postgres | 5432 |
| Product Postgres | separate |
| Redis | 6379 (Core-dedicated DB index recommended) |

```bash
# Core
docker compose up -d postgres redis
alembic upgrade head
CELESTRA_PORT=8001 uvicorn core.app:create_app --factory --reload --port 8001
```

## 15. Example product architecture

```
product-name/
  backend/app/integrations/celestra/   # thin wrapper OR sdk.CelestraClient
  backend/app/domain/                  # product models/services
  frontend/                            # product UX only
```

Use:

```python
from sdk import CelestraClient

async with CelestraClient(base_url="http://localhost:8001", api_key=KEY) as client:
    await client.health()
    result = await client.bridge_exchange(assertion)
    # use result["access_token"] only in the product backend
    await client.start_session(application="chrona", token=result["access_token"])
```

See also: `docs/IDENTITY_BRIDGE.md`, `docs/MEMORY.md`, `docs/SDK.md`, `docs/MONITORING.md`.
