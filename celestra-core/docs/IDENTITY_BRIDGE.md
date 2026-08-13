# Identity Bridge — Celestra Core

Generic product → Core identity exchange for multi-product deployments.

## Flow

```
Product IdP (product-owned)
    → Product Backend signs assertion
    → POST /api/v1/auth/bridge/exchange  (X-API-Key)
    → Core verifies, maps, issues short-lived Core JWT
    → Product Backend calls Memory/AI with Bearer JWT
```

Browsers never receive Core JWTs, API keys, or bridge secrets.

## Canonical assertion (HS256)

| Claim | Required | Notes |
|---|---|---|
| `iss` | yes | Must match issuer configured for `application` |
| `aud` | yes | Default `celestra-core` |
| `sub` | yes | Must equal `product_user_id` |
| `external_subject` | yes | Stable IdP subject (not email) |
| `product_user_id` | yes | Product's user id |
| `application` | yes | Approved: revenue \| hiring \| finance \| chrona |
| `iat` / `exp` / `jti` | yes | Short TTL; jti replay-protected (Redis) |

## Mapping

`(provider=application, application, external_subject)` → Core user UUID  
`external_user_id` stores `product_user_id` for mismatch detection (fail closed).

## Transitional Revenue compatibility

Still accepted (isolated shim):

- `firebase_uid` → `external_subject`
- `revenue_user_id` → `product_user_id`

New products should send the canonical fields only.

## Configuration

| Env | Purpose |
|---|---|
| `CELESTRA_BRIDGE_ASSERTION_SECRET` | Shared HMAC secret |
| `CELESTRA_BRIDGE_AUDIENCE` | Default `celestra-core` |
| `CELESTRA_BRIDGE_ISSUER` | Legacy default issuer (revenue) |
| `CELESTRA_BRIDGE_ISSUERS` | `revenue=revenue-ai,hiring=hiring-ai,...` |
| `CELESTRA_BRIDGE_*_TTL` / skew / token expire | Timing |

## Security

- Service principal required for exchange
- Bridged users have unusable passwords
- Replay protection requires Redis outside test/debug
- Do not log assertions, JWTs, or external subjects by default
