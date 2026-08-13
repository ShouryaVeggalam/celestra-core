"""Official HTTP CelestraClient tests."""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from sdk.client import (
    ERROR_AUTH,
    ERROR_INVALID_CONFIG,
    ERROR_INVALID_RESPONSE,
    ERROR_TIMEOUT,
    ERROR_UNAVAILABLE,
    CelestraAPIError,
    CelestraClient,
)


class _Transport(httpx.AsyncBaseTransport):
    def __init__(self, handler) -> None:
        self.handler = handler
        self.calls: list[httpx.Request] = []

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.calls.append(request)
        return self.handler(request)


def _client(handler, **kwargs: Any) -> CelestraClient:
    transport = _Transport(handler)
    client = CelestraClient(base_url="http://core.test", api_key="cel_test", **kwargs)
    # Replace underlying httpx client with transport-bound one.
    client._client = httpx.AsyncClient(
        base_url="http://core.test",
        timeout=kwargs.get("timeout", 5.0),
        transport=transport,
    )
    client._transport = transport  # type: ignore[attr-defined]
    return client


@pytest.mark.asyncio
async def test_health_and_ready():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok", "app": "celestra-core", "env": "test"})
        if request.url.path == "/ready":
            return httpx.Response(
                200,
                json={"status": "ok", "redis": True, "redis_required": False, "database": "skipped"},
            )
        return httpx.Response(404, json={"error": {"code": "not_found", "message": "no"}})

    client = _client(handler)
    assert (await client.health())["status"] == "ok"
    assert (await client.ready())["status"] == "ok"
    await client.aclose()


@pytest.mark.asyncio
async def test_complete_embed_render_prompt():
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/ai/complete"):
            return httpx.Response(200, json={"content": "hi", "model": "m", "provider": "mock", "usage": {}})
        if path.endswith("/ai/embed"):
            return httpx.Response(
                200,
                json={"embeddings": [[0.1]], "model": "e", "provider": "mock", "usage": {}, "dimensions": 1},
            )
        if path.endswith("/ai/prompts/render"):
            return httpx.Response(200, json={"name": "chat.user_turn", "version": "1", "content": "Q"})
        return httpx.Response(404, json={})

    client = _client(handler)
    assert (await client.complete({"prompt": "x"}))["content"] == "hi"
    assert (await client.embed({"input": "x"}))["dimensions"] == 1
    assert (await client.render_prompt({"name": "chat.user_turn", "variables": {"question": "x"}}))[
        "content"
    ] == "Q"
    await client.aclose()


@pytest.mark.asyncio
async def test_memory_requires_user_token():
    client = _client(lambda r: httpx.Response(200, json={}))
    with pytest.raises(CelestraAPIError) as exc:
        await client.start_session(application="chrona")
    assert exc.value.category == ERROR_INVALID_CONFIG
    await client.aclose()


@pytest.mark.asyncio
async def test_memory_methods_send_bearer_not_api_key():
    def handler(request: httpx.Request) -> httpx.Response:
        assert "X-API-Key" not in request.headers
        assert request.headers.get("Authorization") == "Bearer user-jwt"
        if request.method == "POST" and request.url.path.endswith("/memory/sessions"):
            return httpx.Response(200, json={"id": "s1", "application": "chrona", "messages": []})
        if request.method == "POST" and request.url.path.endswith("/memory/messages"):
            return httpx.Response(200, json={"id": "s1", "messages": []})
        if request.method == "GET":
            return httpx.Response(200, json=[{"role": "user", "content": "hi"}])
        return httpx.Response(404, json={})

    client = _client(handler)
    await client.start_session(application="chrona", session_id="s1", token="user-jwt")
    await client.add_message(session_id="s1", content="hi", application="chrona", token="user-jwt")
    msgs = await client.get_messages("s1", application="chrona", token="user-jwt")
    assert msgs[0]["content"] == "hi"
    await client.aclose()


@pytest.mark.asyncio
async def test_bridge_exchange_requires_api_key_and_posts_assertion():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("X-API-Key") == "cel_test"
        body = json.loads(request.content.decode())
        assert body["assertion"] == "signed-assertion-value"
        return httpx.Response(
            200,
            json={
                "access_token": "core-jwt",
                "token_type": "bearer",
                "expires_in": 300,
                "celestra_user_id": "11111111-1111-1111-1111-111111111111",
                "application": "hiring",
                "provisioned": False,
            },
        )

    client = _client(handler)
    result = await client.bridge_exchange("signed-assertion-value")
    assert result["access_token"] == "core-jwt"
    await client.aclose()


@pytest.mark.asyncio
async def test_request_id_propagation():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("X-Request-ID") == "corr-1"
        return httpx.Response(200, json={"status": "ok", "app": "x", "env": "test"})

    client = _client(handler, default_request_id="corr-1")
    await client.health()
    await client.aclose()


@pytest.mark.asyncio
async def test_timeout_category():
    class Boom(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("slow")

    client = CelestraClient(base_url="http://core.test", api_key="k")
    client._client = httpx.AsyncClient(base_url="http://core.test", transport=Boom(), timeout=0.1)
    with pytest.raises(CelestraAPIError) as exc:
        await client.health()
    assert exc.value.category == ERROR_TIMEOUT
    await client.aclose()


@pytest.mark.asyncio
async def test_unavailable_category():
    class Boom(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("down")

    client = CelestraClient(base_url="http://core.test", api_key="k")
    client._client = httpx.AsyncClient(base_url="http://core.test", transport=Boom(), timeout=0.1)
    with pytest.raises(CelestraAPIError) as exc:
        await client.health()
    assert exc.value.category == ERROR_UNAVAILABLE
    await client.aclose()


@pytest.mark.asyncio
async def test_auth_error_category():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": {"code": "unauthorized", "message": "no"}})

    client = _client(handler)
    with pytest.raises(CelestraAPIError) as exc:
        await client.complete({"prompt": "x"})
    assert exc.value.category == ERROR_AUTH
    await client.aclose()


@pytest.mark.asyncio
async def test_invalid_response_category():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not-json", headers={"content-type": "text/plain"})

    client = _client(handler)
    with pytest.raises(CelestraAPIError) as exc:
        await client.health()
    assert exc.value.category == ERROR_INVALID_RESPONSE
    await client.aclose()
