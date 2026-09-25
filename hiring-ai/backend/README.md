# Hiring AI backend

FastAPI service with dual auth:

- `AUTH_MODE=dev` — Bearer token is the user id (local demos)
- `AUTH_MODE=firebase` — verify Firebase ID tokens; provision via `auth_identities`

## Endpoints

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| GET | `/health` | public | Liveness |
| GET | `/ready` | public | Readiness (Postgres + Firebase when hosted) |
| GET | `/api/v1/auth/me` | user | Profile + memberships |
| POST | `/api/v1/auth/organizations` | user | Bootstrap first org as owner |
| POST | `/api/v1/organizations/{id}/invite-codes` | owner/admin | Create invite |
| GET | `/api/v1/organizations/{id}/invite-codes` | owner/admin | List invites |
| POST | `/api/v1/invite-codes/redeem` | user | Join org |
| GET | `/api/v1/candidate-portal/{token}` | public | Portal stub |

## Hosted start

```bash
bash start.sh   # alembic upgrade head && uvicorn
```
