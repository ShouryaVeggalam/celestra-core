# SDK — Celestra Core

Two surfaces exist. Products must use the **HTTP client**.

## PUBLIC PRODUCT CLIENT — `CelestraClient`

Remote HTTP access for product backends:

```python
from sdk import CelestraClient

async with CelestraClient(
    base_url="http://localhost:8001",
    api_key=SERVICE_KEY,
    default_request_id="req-123",
) as client:
    await client.health()
    await client.ready()
    await client.complete({"prompt": "hello"})
    await client.embed({"input": "hello"})
    await client.render_prompt({"name": "chat.user_turn", "variables": {"question": "Hi"}})

    # Identity: service key mints end-user Core JWT (do not send JWT to browsers)
    exchanged = await client.bridge_exchange(assertion)
    user_jwt = exchanged["access_token"]

    # Memory: requires end-user JWT — never falls back to API key
    await client.start_session(application="chrona", token=user_jwt)
    await client.add_message(
        session_id="s1",
        content="hello",
        application="chrona",
        token=user_jwt,
    )
    await client.get_messages("s1", application="chrona", token=user_jwt)
```

### Auth rules

| Operation | Credential |
|---|---|
| `health` / `ready` | none |
| `complete` / `embed` / `render_prompt` | API key or JWT |
| `bridge_exchange` | **API key required** |
| `start_session` / `add_message` / `get_messages` | **end-user JWT required** |

Failures raise `CelestraAPIError` with `.category` ∈  
`timeout` · `unavailable` · `auth_error` · `invalid_config` · `invalid_response` · `validation_error` · `not_found` · `server_error` · …

The client does **not** mint Core JWTs, store exchanged tokens, or contain product business logic.

## IN-PROCESS CORE SDK — `CelestraSDK`

```python
from sdk import CelestraSDK

sdk = CelestraSDK.from_container()
await sdk.complete(...)
```

For Core-internal / same-process use only. **Products must not depend on this** in production deployments.

## See also

`docs/PRODUCT_INTEGRATION.md`
