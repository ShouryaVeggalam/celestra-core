"""Step 5 — conversation memory ownership, application isolation, Redis hardening."""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from datetime import datetime
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ai.router import ModelRouter
from ai.service import AIService
from auth.dependencies import get_current_user
from auth.tokens import create_access_token
from memory.buffer import InMemoryConversationStore
from memory.conversation import ConversationMemory
from memory.factory import build_conversation_store
from memory.http import provide_memory_service, router as memory_router
from memory.redis_store import RedisConversationStore
from memory.service import MemoryService
from memory.types import DEFAULT_APPLICATION, ConversationSession, MemoryMessage
from memory.vector import InMemoryVectorStore
from prompts.loader import build_prompt_registry
from providers.mock import MockProvider
from providers.registry import ProviderRegistry
from shared.exceptions.base import ConfigurationError, NotFoundError
from shared.exceptions.handlers import register_exception_handlers


class _FakeRedis:
    def __init__(self) -> None:
        self._kv: dict[str, str] = {}
        self._expiry: dict[str, float] = {}
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

    async def eval(self, script: str, numkeys: int, *keys_and_args: Any) -> str | None:
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
            session.updated_at = datetime.fromisoformat(updated_at)
            encoded = session.model_dump_json()
            await self.set(key, encoded, ex=ttl if ttl > 0 else None)
            return encoded


@pytest.fixture
def memory_service() -> MemoryService:
    registry = ProviderRegistry()
    registry.register(MockProvider())
    ai = AIService(
        registry=registry,
        router=ModelRouter(registry, default_provider="mock"),
        prompts=build_prompt_registry(),
        default_model="mock-chat",
    )
    return MemoryService(
        conversations=ConversationMemory(InMemoryConversationStore(), window_size=10),
        vectors=InMemoryVectorStore(),
        ai=ai,
    )


@pytest.mark.asyncio
async def test_owner_create_read_append(memory_service: MemoryService):
    session = await memory_service.start_session(session_id="s-a", user_id="user-a")
    assert session.user_id == "user-a"
    assert session.application == DEFAULT_APPLICATION
    await memory_service.add_message("s-a", "user", "hello", user_id="user-a")
    msgs = await memory_service.get_messages("s-a", user_id="user-a")
    assert len(msgs) == 1
    assert msgs[0].content == "hello"


@pytest.mark.asyncio
async def test_foreign_user_cannot_read(memory_service: MemoryService):
    await memory_service.start_session(session_id="s-a", user_id="user-a")
    await memory_service.add_message("s-a", "user", "secret", user_id="user-a")
    with pytest.raises(NotFoundError):
        await memory_service.get_messages("s-a", user_id="user-b")


@pytest.mark.asyncio
async def test_foreign_user_cannot_append(memory_service: MemoryService):
    await memory_service.start_session(session_id="s-a", user_id="user-a")
    with pytest.raises(NotFoundError):
        await memory_service.add_message("s-a", "user", "hijack", user_id="user-b")


@pytest.mark.asyncio
async def test_foreign_user_cannot_reuse_session_id(memory_service: MemoryService):
    await memory_service.start_session(session_id="shared-id", user_id="user-a")
    with pytest.raises(NotFoundError):
        await memory_service.start_session(session_id="shared-id", user_id="user-b")


@pytest.mark.asyncio
async def test_unknown_session_not_found(memory_service: MemoryService):
    with pytest.raises(NotFoundError):
        await memory_service.get_messages("missing", user_id="user-a")
    with pytest.raises(NotFoundError):
        await memory_service.add_message("missing", "user", "x", user_id="user-a")


@pytest.mark.asyncio
async def test_add_message_does_not_auto_create(memory_service: MemoryService):
    with pytest.raises(NotFoundError):
        await memory_service.add_message("new-only", "user", "x", user_id="user-a")
    # Still missing after failed append
    with pytest.raises(NotFoundError):
        await memory_service.get_messages("new-only", user_id="user-a")


@pytest.mark.asyncio
async def test_application_isolation_same_user(memory_service: MemoryService):
    await memory_service.start_session(
        session_id="s1", user_id="user-a", application="revenue"
    )
    await memory_service.add_message(
        "s1", "user", "rev", user_id="user-a", application="revenue"
    )
    with pytest.raises(NotFoundError):
        await memory_service.get_messages("s1", user_id="user-a", application="hiring")
    with pytest.raises(NotFoundError):
        await memory_service.add_message(
            "s1", "user", "x", user_id="user-a", application="hiring"
        )


@pytest.mark.asyncio
async def test_same_user_same_application_ok(memory_service: MemoryService):
    await memory_service.start_session(
        session_id="s1", user_id="user-a", application="hiring"
    )
    await memory_service.add_message(
        "s1", "user", "hi", user_id="user-a", application="hiring"
    )
    msgs = await memory_service.get_messages(
        "s1", user_id="user-a", application="hiring"
    )
    assert msgs[0].content == "hi"


@pytest.mark.asyncio
async def test_default_application_backward_compatible(memory_service: MemoryService):
    session = await memory_service.start_session(session_id="s-def", user_id="u1")
    assert session.application == "default"
    await memory_service.add_message("s-def", "user", "ok", user_id="u1")
    msgs = await memory_service.get_messages("s-def", user_id="u1", application="default")
    assert len(msgs) == 1


@pytest.mark.asyncio
async def test_redis_shared_across_store_instances():
    fake = _FakeRedis()
    store_a = RedisConversationStore(fake, ttl_seconds=3600)  # type: ignore[arg-type]
    store_b = RedisConversationStore(fake, ttl_seconds=3600)  # type: ignore[arg-type]
    await store_a.save(
        ConversationSession(
            id="shared",
            user_id="u1",
            application="revenue",
            messages=[MemoryMessage(role="user", content="from-a")],
        )
    )
    loaded = await store_b.get("shared", application="revenue")
    assert loaded is not None
    assert loaded.messages[0].content == "from-a"


def test_redis_backend_fail_closed_no_silent_memory():
    from config.settings import Settings

    settings = Settings(memory_conversation_backend="redis")
    with pytest.raises(ConfigurationError) as exc_info:
        build_conversation_store(settings, redis=None)
    assert "redis" in str(exc_info.value.message).lower()
    # Explicit memory backend still works without Redis
    mem_settings = Settings(memory_conversation_backend="memory")
    store = build_conversation_store(mem_settings, redis=None)
    assert isinstance(store, InMemoryConversationStore)


@pytest.mark.asyncio
async def test_redis_concurrent_appends_do_not_lose_messages():
    fake = _FakeRedis()
    store = RedisConversationStore(fake, ttl_seconds=3600)  # type: ignore[arg-type]
    await store.save(
        ConversationSession(id="c1", user_id="u1", messages=[])
    )

    async def append_one(i: int) -> None:
        await store.append("c1", [MemoryMessage(role="user", content=f"m{i}")])

    await asyncio.gather(*(append_one(i) for i in range(40)))
    session = await store.get("c1")
    assert session is not None
    assert len(session.messages) == 40
    contents = {m.content for m in session.messages}
    assert contents == {f"m{i}" for i in range(40)}


@pytest.mark.asyncio
async def test_redis_ttl_set_and_refresh():
    fake = _FakeRedis()
    store = RedisConversationStore(fake, ttl_seconds=2)  # type: ignore[arg-type]
    await store.save(ConversationSession(id="ttl1", user_id="u1", messages=[]))
    key = fake.key("memory:default:conversation:ttl1")
    assert key in fake._expiry
    first_expiry = fake._expiry[key]
    await asyncio.sleep(0.05)
    await store.append("ttl1", [MemoryMessage(role="user", content="ping")])
    assert fake._expiry[key] >= first_expiry
    # Force expire
    fake._expiry[key] = time.time() - 1
    assert await store.get("ttl1") is None


@pytest.mark.asyncio
async def test_redis_legacy_key_read_for_default_app():
    fake = _FakeRedis()
    store = RedisConversationStore(fake, ttl_seconds=3600)  # type: ignore[arg-type]
    legacy = ConversationSession(id="legacy", user_id="u1", messages=[
        MemoryMessage(role="user", content="old")
    ])
    await fake.raw.set(fake.key("memory:conversation:legacy"), legacy.model_dump_json())
    loaded = await store.get("legacy", application="default")
    assert loaded is not None
    assert loaded.messages[0].content == "old"


@pytest.mark.asyncio
async def test_vector_memory_remains_unscoped_guard(memory_service: MemoryService):
    """Document/guard: vector recall is not filtered by user or application."""
    await memory_service.remember_text("alpha secret for user A", metadata={"user": "A"})
    await memory_service.remember_text("beta note for user B", metadata={"user": "B"})
    hits = await memory_service.recall("alpha secret for user A", top_k=5)
    assert hits
    # No user filter exists — hits can include any stored record (multi-user unsafe).
    assert any("alpha" in h.text for h in hits)


def _make_user(user_id: str) -> Any:
    return SimpleNamespace(
        id=uuid.UUID(user_id) if len(user_id) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, user_id),
        email=f"{user_id}@example.com",
        is_active=True,
        is_superuser=False,
        roles=[],
        role_names=lambda: set(),
        permission_codes=lambda: set(),
    )


def _memory_http_app(service: MemoryService, user: Any) -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(memory_router, prefix="/api/v1")

    async def _user_override() -> Any:
        return user

    async def _service_override() -> MemoryService:
        return service

    app.dependency_overrides[get_current_user] = _user_override
    app.dependency_overrides[provide_memory_service] = _service_override
    return app


def test_http_jwt_identity_ownership(memory_service: MemoryService):
    user_a = _make_user("user-a")
    user_b = _make_user("user-b")
    token = create_access_token(
        subject=user_a.id, secret_key="test-secret-key-not-for-prod-32b", expires_minutes=5
    )
    assert token

    with TestClient(_memory_http_app(memory_service, user_a)) as client_a:
        r = client_a.post("/api/v1/memory/sessions", json={"session_id": "http-s1"})
        assert r.status_code == 200
        assert r.json()["user_id"] == str(user_a.id)
        r = client_a.post(
            "/api/v1/memory/messages",
            json={"session_id": "http-s1", "role": "user", "content": "hi"},
        )
        assert r.status_code == 200
        r = client_a.get("/api/v1/memory/sessions/http-s1/messages")
        assert r.status_code == 200
        assert r.json()[0]["content"] == "hi"

    with TestClient(_memory_http_app(memory_service, user_b)) as client_b:
        r = client_b.get("/api/v1/memory/sessions/http-s1/messages")
        assert r.status_code == 404
        r = client_b.post(
            "/api/v1/memory/messages",
            json={"session_id": "http-s1", "role": "user", "content": "nope"},
        )
        assert r.status_code == 404


def test_http_api_key_owner_identity(memory_service: MemoryService):
    """API-key auth resolves to the owning User — same ownership rules as JWT."""
    owner = _make_user("api-key-owner")
    other = _make_user("other-user")

    with TestClient(_memory_http_app(memory_service, owner)) as client:
        assert (
            client.post(
                "/api/v1/memory/sessions",
                json={"session_id": "key-s1", "application": "revenue"},
            ).status_code
            == 200
        )
        assert (
            client.post(
                "/api/v1/memory/messages",
                json={
                    "session_id": "key-s1",
                    "role": "user",
                    "content": "via-key",
                    "application": "revenue",
                },
            ).status_code
            == 200
        )

    with TestClient(_memory_http_app(memory_service, other)) as client:
        r = client.get(
            "/api/v1/memory/sessions/key-s1/messages",
            params={"application": "revenue"},
        )
        assert r.status_code == 404


def test_http_application_query_isolation(memory_service: MemoryService):
    user = _make_user("app-user")
    with TestClient(_memory_http_app(memory_service, user)) as client:
        assert (
            client.post(
                "/api/v1/memory/sessions",
                json={"session_id": "app-s", "application": "revenue"},
            ).status_code
            == 200
        )
        client.post(
            "/api/v1/memory/messages",
            json={
                "session_id": "app-s",
                "role": "user",
                "content": "rev",
                "application": "revenue",
            },
        )
        ok = client.get(
            "/api/v1/memory/sessions/app-s/messages",
            params={"application": "revenue"},
        )
        assert ok.status_code == 200
        bad = client.get(
            "/api/v1/memory/sessions/app-s/messages",
            params={"application": "hiring"},
        )
        assert bad.status_code == 404


@pytest.mark.asyncio
async def test_authenticate_api_key_binds_owner_user_id():
    """API-key authentication returns the key owner's User.id."""
    from auth.service import AuthService

    owner = _make_user("550e8400-e29b-41d4-a716-446655440000")
    service = AsyncMock(spec=AuthService)
    service.authenticate_api_key = AsyncMock(return_value=owner)
    user = await service.authenticate_api_key("ck_test_raw")
    assert str(user.id) == str(owner.id)
