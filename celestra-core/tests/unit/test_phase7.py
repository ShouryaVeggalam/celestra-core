"""Unit tests — Phase 7 production hardening."""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any
from unittest.mock import AsyncMock

import pytest

from auth.oidc import OIDCClient, OIDCSettings
from billing.stripe import StripeAdapter, StripeCheckoutSessionRequest
from config.settings import Settings, clear_settings_cache
from memory.buffer import InMemoryConversationStore
from memory.factory import build_conversation_store, build_vector_store
from memory.redis_store import RedisConversationStore
from memory.types import ConversationSession, MemoryMessage
from memory.vector import InMemoryVectorStore
from notifications.channels.email import LoggingEmailSender
from notifications.channels.smtp import SMTPEmailSender
from notifications.factory import build_notification_service
from shared.exceptions.base import ConfigurationError
from workflows.factory import build_workflow_run_store
from workflows.redis_store import RedisWorkflowRunStore
from workflows.store import WorkflowRunStore
from workflows.types import WorkflowRun, WorkflowStatus


class _FakeRedis:
    """Minimal async Redis stub for store unit tests."""

    def __init__(self) -> None:
        self._kv: dict[str, str] = {}
        self._expiry: dict[str, float] = {}
        self._zsets: dict[str, dict[str, float]] = {}
        self._eval_lock = asyncio.Lock()

    def key(self, name: str) -> str:
        return f"celestra:{name}" if not name.startswith("celestra:") else name

    @property
    def raw(self) -> "_FakeRaw":
        return _FakeRaw(self)

    def _purge_if_expired(self, key: str) -> None:
        exp = self._expiry.get(key)
        if exp is not None and time.time() >= exp:
            self._kv.pop(key, None)
            self._expiry.pop(key, None)


class _FakePipeline:
    def __init__(self, parent: "_FakeRaw") -> None:
        self.parent = parent
        self.ops: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    def set(self, key: str, value: str, ex: int | None = None) -> "_FakePipeline":
        self.ops.append(("set", (key, value), {"ex": ex}))
        return self

    def zadd(self, key: str, mapping: dict[str, float]) -> "_FakePipeline":
        self.ops.append(("zadd", (key, mapping), {}))
        return self

    async def execute(self) -> list[Any]:
        results = []
        for op, args, kwargs in self.ops:
            if op == "set":
                results.append(await self.parent.set(*args, **kwargs))
            elif op == "zadd":
                results.append(await self.parent.zadd(*args))
        return results


class _FakeRaw:
    def __init__(self, client: _FakeRedis) -> None:
        self.client = client

    async def get(self, key: str) -> str | None:
        self.client._purge_if_expired(key)
        return self.client._kv.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        self.client._kv[key] = value
        if ex is not None and ex > 0:
            self.client._expiry[key] = time.time() + ex
        else:
            self.client._expiry.pop(key, None)
        return True

    async def delete(self, key: str) -> int:
        self.client._expiry.pop(key, None)
        return 1 if self.client._kv.pop(key, None) is not None else 0

    async def zadd(self, key: str, mapping: dict[str, float]) -> int:
        z = self.client._zsets.setdefault(key, {})
        z.update(mapping)
        return len(mapping)

    async def zrevrange(self, key: str, start: int, end: int) -> list[str]:
        z = self.client._zsets.get(key, {})
        ordered = sorted(z.items(), key=lambda item: item[1], reverse=True)
        ids = [item[0] for item in ordered]
        if end < 0:
            return ids[start:]
        return ids[start : end + 1]

    def pipeline(self) -> _FakePipeline:
        return _FakePipeline(self)

    async def eval(self, script: str, numkeys: int, *keys_and_args: Any) -> str | None:
        """Emulate the RedisConversationStore append Lua script atomically."""
        async with self.client._eval_lock:
            key = keys_and_args[0]
            payload = keys_and_args[1]
            updated_at = keys_and_args[2]
            ttl = int(keys_and_args[3]) if len(keys_and_args) > 3 else 0
            raw = await self.get(key)
            if raw is None:
                return None
            session = ConversationSession.model_validate_json(raw)
            incoming = [MemoryMessage.model_validate(m) for m in json.loads(payload)]
            session.messages.extend(incoming)
            from datetime import datetime

            session.updated_at = datetime.fromisoformat(updated_at)
            encoded = session.model_dump_json()
            await self.set(key, encoded, ex=ttl if ttl > 0 else None)
            return encoded


@pytest.fixture(autouse=True)
def _clear_settings() -> None:
    clear_settings_cache()
    yield
    clear_settings_cache()


def test_build_conversation_store_memory_default():
    settings = Settings(memory_conversation_backend="memory")
    store = build_conversation_store(settings, redis=None)
    assert isinstance(store, InMemoryConversationStore)


def test_build_conversation_store_redis():
    settings = Settings(memory_conversation_backend="redis")
    fake = _FakeRedis()
    store = build_conversation_store(settings, redis=fake)  # type: ignore[arg-type]
    assert isinstance(store, RedisConversationStore)


def test_build_conversation_store_redis_fail_closed_without_client():
    settings = Settings(memory_conversation_backend="redis")
    with pytest.raises(ConfigurationError):
        build_conversation_store(settings, redis=None)


def test_build_vector_store_memory_default():
    settings = Settings(memory_vector_backend="memory")
    store = build_vector_store(settings)
    assert isinstance(store, InMemoryVectorStore)


def test_build_workflow_store_backends():
    memory_settings = Settings(workflow_run_backend="memory")
    assert isinstance(build_workflow_run_store(memory_settings), WorkflowRunStore)
    redis_settings = Settings(workflow_run_backend="redis")
    fake = _FakeRedis()
    assert isinstance(build_workflow_run_store(redis_settings, fake), RedisWorkflowRunStore)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_redis_conversation_roundtrip():
    fake = _FakeRedis()
    store = RedisConversationStore(fake)  # type: ignore[arg-type]
    session = ConversationSession(id="s1", messages=[MemoryMessage(role="user", content="hi")])
    await store.save(session)
    loaded = await store.get("s1")
    assert loaded is not None
    assert loaded.messages[0].content == "hi"
    await store.append("s1", [MemoryMessage(role="assistant", content="hello")])
    again = await store.get("s1")
    assert again is not None
    assert len(again.messages) == 2


@pytest.mark.asyncio
async def test_redis_workflow_run_roundtrip():
    fake = _FakeRedis()
    store = RedisWorkflowRunStore(fake)  # type: ignore[arg-type]
    run = WorkflowRun(id="r1", workflow="demo.greeting", status=WorkflowStatus.COMPLETED, input={})
    await store.save(run)
    loaded = await store.get("r1")
    assert loaded.workflow == "demo.greeting"
    listed = await store.list(workflow="demo.greeting")
    assert len(listed) == 1


def test_notification_factory_logging_by_default():
    settings = Settings()
    service = build_notification_service(settings)
    assert isinstance(service.senders["email"], LoggingEmailSender)


def test_notification_factory_smtp_when_configured():
    settings = Settings(smtp_host="smtp.example.com", smtp_from="noreply@example.com")
    service = build_notification_service(settings)
    assert isinstance(service.senders["email"], SMTPEmailSender)


def test_stripe_requires_price_map():
    adapter = StripeAdapter(secret_key="sk_test_x", price_map={})
    with pytest.raises(ConfigurationError):
        adapter.price_id_for_plan("pro")


@pytest.mark.asyncio
async def test_stripe_checkout_posts_form(monkeypatch: pytest.MonkeyPatch):
    adapter = StripeAdapter(secret_key="sk_test_x", price_map={"pro": "price_123"})

    class _Resp:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, str]:
            return {"id": "cs_1", "url": "https://checkout.stripe.com/c/cs_1"}

    adapter._client.post = AsyncMock(return_value=_Resp())  # type: ignore[method-assign]
    session = await adapter.create_checkout_session(
        StripeCheckoutSessionRequest(
            account_id="acct",
            plan_id="pro",
            success_url="https://app/success",
            cancel_url="https://app/cancel",
        )
    )
    assert session.id == "cs_1"
    assert "checkout.stripe.com" in session.url
    await adapter.aclose()


@pytest.mark.asyncio
async def test_oidc_authorization_url(monkeypatch: pytest.MonkeyPatch):
    client = OIDCClient(
        OIDCSettings(
            issuer="https://idp.example.com",
            client_id="cid",
            client_secret="secret",
            redirect_uri="https://app/callback",
        )
    )
    client._discovered = {
        "authorization_endpoint": "https://idp.example.com/authorize",
        "token_endpoint": "https://idp.example.com/token",
        "userinfo_endpoint": "https://idp.example.com/userinfo",
    }
    url = await client.authorization_url(state="abc", nonce="n1")
    assert url.startswith("https://idp.example.com/authorize?")
    assert "client_id=cid" in url
    assert "state=abc" in url
    await client.aclose()


def test_stripe_price_map_parse():
    clear_settings_cache()
    settings = Settings(stripe_price_map="pro=price_a,enterprise=price_b")  # type: ignore[arg-type]
    assert settings.stripe_price_map == {"pro": "price_a", "enterprise": "price_b"}
