# Auth — Celestra Core

Platform identity for every Celestra application (Microsoft Identity–style, not app-local CRUD).

## Capabilities

- Register / login / refresh / logout
- Argon2id password hashing
- JWT access tokens + rotating refresh tokens (persisted, revocable)
- RBAC: roles → permissions
- API keys via `X-API-Key`
- FastAPI dependencies for product apps

## HTTP API (`/api/v1/auth`)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/register` | No | Create user (default role: `member`) |
| POST | `/login` | No | Issue access + refresh tokens |
| POST | `/refresh` | No | Rotate refresh token |
| POST | `/logout` | No | Revoke refresh token |
| GET | `/me` | Bearer / API key | Current user profile |
| POST | `/api-keys` | `api_keys:manage` | Create API key (plaintext once) |
| GET | `/api-keys` | Bearer | List keys |
| DELETE | `/api-keys/{id}` | Bearer | Revoke key |

## Default RBAC seed

| Role | Permissions |
|---|---|
| `admin` | `users:read`, `users:write`, `api_keys:manage`, `admin:access`, `monitoring:read` |
| `member` | `users:read`, `api_keys:manage` |
| `viewer` | `users:read`, `monitoring:read` |

Seeded automatically on API startup (idempotent).

## Product app usage

```python
from fastapi import Depends
from auth import get_current_user, require_roles, require_permissions

@app.get("/me")
async def me(user=Depends(get_current_user)):
    return {"id": str(user.id), "email": user.email}

@app.delete("/users/{id}")
async def delete_user(user=Depends(require_permissions("users:write"))):
    ...

@app.get("/admin")
async def admin_panel(user=Depends(require_roles("admin"))):
    ...
```

Headers:

```http
Authorization: Bearer <access_token>
# or
X-API-Key: cel_...
```

## Config

| Env var | Default |
|---|---|
| `CELESTRA_SECRET_KEY` | (required strong in prod) |
| `CELESTRA_JWT_ALGORITHM` | `HS256` |
| `CELESTRA_JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
| `CELESTRA_JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `14` |
| `CELESTRA_AUTH_ALLOW_REGISTRATION` | `true` |
| `CELESTRA_AUTH_DEFAULT_ROLE` | `member` |

## Files

| File | Role |
|---|---|
| `models.py` | User, Role, Permission, ApiKey, RefreshToken |
| `schemas.py` | Request/response DTOs |
| `passwords.py` | Hash / verify |
| `tokens.py` | JWT issue / decode |
| `rbac.py` | Role/permission checks |
| `repository.py` | Persistence |
| `service.py` | Application service |
| `dependencies.py` | FastAPI DI guards |
| `router.py` | HTTP routes |
| `seed.py` | Default RBAC |
