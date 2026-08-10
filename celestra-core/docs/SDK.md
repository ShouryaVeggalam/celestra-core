# SDK — Celestra Core (Phase 6)

First-party client surfaces for product applications.

## In-process (`CelestraSDK`)

Use when the app shares the Core process / DI container:

```python
from sdk import CelestraSDK

sdk = CelestraSDK.from_container()
await sdk.complete(...)
await sdk.run_agent(...)
sdk.track(...)
sdk.check_entitlement("acct", "agents.enabled")
```

`complete()` also records billing usage + analytics events.

## Remote HTTP (`CelestraClient`)

Use when calling a Core deployment over the network:

```python
from sdk import CelestraClient

async with CelestraClient(base_url="http://localhost:8000", token=jwt) as client:
    await client.health()
    await client.complete({"prompt": "hello"})
    await client.record_usage({"account_id": "acct", "metric": "ai.requests_per_day", "quantity": 1})
```

Auth via `token=` (Bearer JWT) or `api_key=` (`X-API-Key`).
