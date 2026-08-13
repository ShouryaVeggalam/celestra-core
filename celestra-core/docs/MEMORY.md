# Memory — Celestra Core

Conversation history and semantic recall for Celestra apps.

## Conversation memory (hardened)

- **Ownership**: every session is bound to the authenticated Core `user.id`.
  Foreign reads/writes return **404** (resource non-disclosure).
- **Application isolation**: product namespace (`revenue` | `hiring` | `finance` | `default`).
  Clients that omit `application` use `default` (backward compatible).
  Same user cannot access another application's session via the wrong namespace.
- **Backends**:
  - `CELESTRA_MEMORY_CONVERSATION_BACKEND=memory` — process-local (tests / single worker)
  - `CELESTRA_MEMORY_CONVERSATION_BACKEND=redis` — shared across workers; **fail-closed**
    (no silent in-memory fallback if Redis is missing/unreachable)
- **TTL**: `CELESTRA_MEMORY_CONVERSATION_TTL_SECONDS` (default 604800 = 7 days).
  Refreshed on every `save` / atomic `append`. Redis expires keys after TTL.
- **Atomic append**: Redis uses a Lua script so concurrent appends cannot overwrite each other.

Authorization is based on authenticated identity + application + ownership — **not** on
secrecy of `session_id`.

### Usage

```python
session = await memory.start_session(session_id="s1", user_id=user.id, application="revenue")
await memory.add_message("s1", "user", "Hello", user_id=user.id, application="revenue")
msgs = await memory.get_messages("s1", user_id=user.id, application="revenue")
```

`add_message` does **not** auto-create sessions. Create via `start_session` / `POST /sessions` first.

## HTTP (`/api/v1/memory`) — auth required

| Method | Path | Description |
|---|---|---|
| POST | `/sessions` | Start/get owned session (`application` optional, default `default`) |
| POST | `/messages` | Append to owned session (no auto-create) |
| GET | `/sessions/{id}/messages` | Windowed history (`?application=`) |
| POST | `/remember` | Upsert semantic memory (**not multi-user safe**) |
| POST | `/recall` | Similarity search (**not multi-user safe**) |

## Vector memory — production guard

`remember` / `recall` are **not** filtered by `user_id` or `application`.
They are unsuitable for multi-user production until scoping exists.
Do **not** enable vector memory for multi-tenant products. Conversation memory
hardening does **not** change vector APIs.

## Shared API-key products (e.g. Revenue Step 4A)

If a product shares one Core API key across all end-users, Core correctly
isolates that single Core identity — it does **not** isolate Firebase/end-users.

## Identity bridge (Step 6)

Revenue should use `POST /api/v1/auth/bridge/exchange` (service API key + signed
assertion) to obtain a short-lived Core JWT per Firebase user, then call memory
with that JWT and `application=revenue`. See `docs/IDENTITY_BRIDGE.md`.
