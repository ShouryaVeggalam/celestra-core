"""Identity bridge — generic multi-product + Revenue compatibility tests."""

from __future__ import annotations

import time
import uuid
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest

from auth.bridge import (
    BRIDGE_PROVIDER,
    IdentityBridgeService,
    InMemoryReplayStore,
    bridge_provider_for,
)
from auth.passwords import is_unusable_password, make_unusable_password, verify_password
from auth.tokens import create_access_token, decode_token
from config.applications import require_approved_application
from config.settings import Settings, clear_settings_cache
from memory.buffer import InMemoryConversationStore
from memory.conversation import ConversationMemory
from memory.service import MemoryService
from shared.exceptions.base import ForbiddenError, UnauthorizedError, ValidationAppError


@pytest.fixture(autouse=True)
def _clear_settings() -> None:
    clear_settings_cache()
    yield
    clear_settings_cache()


def _settings(**kwargs) -> Settings:
    base = dict(
        bridge_assertion_secret="bridge-test-secret-32chars-min!!",
        bridge_issuer="revenue-ai",
        bridge_audience="celestra-core",
        bridge_clock_skew_seconds=60,
        bridge_jti_ttl_seconds=300,
        bridge_access_token_expire_seconds=120,
        secret_key="test-secret-key-not-for-prod-32b",
        jwt_algorithm="HS256",
        auth_default_role="member",
    )
    base.update(kwargs)
    return Settings(**base)  # type: ignore[arg-type]


def _make_generic_assertion(
    *,
    secret: str = "bridge-test-secret-32chars-min!!",
    iss: str = "hiring-ai",
    aud: str = "celestra-core",
    external_subject: str = "ext-sub-1",
    product_user_id: str = "user_abc",
    application: str = "hiring",
    ttl: int = 60,
    jti: str | None = None,
    iat_offset: int = 0,
    exp_offset: int | None = None,
) -> str:
    now = int(time.time()) + iat_offset
    exp = now + ttl if exp_offset is None else int(time.time()) + exp_offset
    payload = {
        "iss": iss,
        "aud": aud,
        "sub": product_user_id,
        "external_subject": external_subject,
        "product_user_id": product_user_id,
        "application": application,
        "iat": now,
        "exp": exp,
        "jti": jti or uuid.uuid4().hex,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def _make_revenue_legacy_assertion(
    *,
    secret: str = "bridge-test-secret-32chars-min!!",
    iss: str = "revenue-ai",
    aud: str = "celestra-core",
    firebase_uid: str = "fb-uid-1",
    revenue_user_id: str = "user_abc",
    application: str = "revenue",
    ttl: int = 60,
    jti: str | None = None,
    iat_offset: int = 0,
    exp_offset: int | None = None,
) -> str:
    now = int(time.time()) + iat_offset
    exp = now + ttl if exp_offset is None else int(time.time()) + exp_offset
    payload = {
        "iss": iss,
        "aud": aud,
        "sub": revenue_user_id,
        "firebase_uid": firebase_uid,
        "revenue_user_id": revenue_user_id,
        "application": application,
        "iat": now,
        "exp": exp,
        "jti": jti or uuid.uuid4().hex,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def _service(settings: Settings | None = None) -> IdentityBridgeService:
    return IdentityBridgeService(
        MagicMock(),
        settings or _settings(),
        replay=InMemoryReplayStore(),
    )


def _ns_user(**kwargs):
    base = dict(
        id=uuid.uuid4(),
        email="bridge@invalid",
        is_active=True,
        deleted_at=None,
        is_superuser=False,
        role_names=lambda: {"member"},
    )
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_unusable_password_cannot_verify():
    marker = make_unusable_password()
    assert is_unusable_password(marker)
    assert not verify_password("anything", marker)


def test_generic_assertion():
    svc = _service()
    claims = svc.verify_assertion(_make_generic_assertion())
    assert claims["external_subject"] == "ext-sub-1"
    assert claims["product_user_id"] == "user_abc"
    assert claims["application"] == "hiring"


def test_revenue_legacy_assertion_still_works():
    svc = _service()
    claims = svc.verify_assertion(_make_revenue_legacy_assertion())
    assert claims["external_subject"] == "fb-uid-1"
    assert claims["product_user_id"] == "user_abc"
    assert claims["application"] == "revenue"
    assert claims["legacy_revenue_claims"] == "1"


@pytest.mark.parametrize(
    "kwargs,exc",
    [
        ({"secret": "wrong-secret-xxxxxxxxxxxxxxxxxxxxx"}, UnauthorizedError),
        ({"iss": "other"}, UnauthorizedError),
        ({"aud": "other"}, UnauthorizedError),
        ({"exp_offset": -120}, UnauthorizedError),
        ({"application": "not-a-real-app"}, ValidationAppError),
        ({"iat_offset": 3600}, UnauthorizedError),
    ],
)
def test_invalid_assertions(kwargs, exc):
    svc = _service()
    assertion = _make_generic_assertion(**kwargs)
    with pytest.raises(exc):
        svc.verify_assertion(assertion)


def test_application_required():
    with pytest.raises(ValidationAppError):
        require_approved_application("")
    with pytest.raises(ValidationAppError):
        require_approved_application("unknown-product")


def test_subject_mismatch():
    svc = _service()
    now = int(time.time())
    payload = {
        "iss": "hiring-ai",
        "aud": "celestra-core",
        "sub": "user_a",
        "external_subject": "ext",
        "product_user_id": "user_b",
        "application": "hiring",
        "iat": now,
        "exp": now + 60,
        "jti": "j1",
    }
    assertion = jwt.encode(payload, "bridge-test-secret-32chars-min!!", algorithm="HS256")
    with pytest.raises(UnauthorizedError):
        svc.verify_assertion(assertion)


def test_wrong_issuer_for_application():
    svc = _service()
    assertion = _make_generic_assertion(application="hiring", iss="revenue-ai")
    with pytest.raises(UnauthorizedError, match="issuer"):
        svc.verify_assertion(assertion)


@pytest.mark.asyncio
async def test_replay_rejected():
    replay = InMemoryReplayStore()
    svc = IdentityBridgeService(MagicMock(), _settings(), replay=replay)
    assertion = _make_generic_assertion(jti="fixed-jti")
    user = _ns_user()
    identity = SimpleNamespace(
        external_user_id="user_abc",
        user=user,
        user_id=user.id,
    )
    with patch.object(svc.repo, "get_external_identity", AsyncMock(return_value=identity)):
        result = await svc.exchange(assertion)
        assert str(result.celestra_user_id) == str(user.id)
        with pytest.raises(UnauthorizedError, match="replay"):
            await svc.exchange(assertion)


@pytest.mark.asyncio
async def test_same_identity_resolves_same_user():
    svc = _service()
    assertion = _make_generic_assertion()
    user = _ns_user()
    identity = SimpleNamespace(
        external_user_id="user_abc",
        user=user,
        user_id=user.id,
    )
    with patch.object(svc.repo, "get_external_identity", AsyncMock(return_value=identity)) as get_id:
        r1 = await svc.exchange(assertion)
        r2 = await svc.exchange(_make_generic_assertion(jti=uuid.uuid4().hex))
        assert r1.celestra_user_id == r2.celestra_user_id == user.id
        assert get_id.await_args.kwargs["provider"] == "hiring"
        assert get_id.await_args.kwargs["application"] == "hiring"


@pytest.mark.asyncio
async def test_provision_new_user():
    svc = _service()
    assertion = _make_generic_assertion(external_subject="ext-new", product_user_id="user_new")
    new_user = _ns_user()
    with (
        patch.object(svc.repo, "get_external_identity", AsyncMock(return_value=None)),
        patch.object(svc.repo, "create_bridged_user", AsyncMock(return_value=new_user)) as create_user,
        patch.object(svc.repo, "create_external_identity", AsyncMock()) as create_id,
        patch.object(svc.repo, "get_user_by_id", AsyncMock(return_value=new_user)),
    ):
        result = await svc.exchange(assertion)
        assert result.provisioned is True
        assert result.celestra_user_id == new_user.id
        create_user.assert_awaited()
        create_id.assert_awaited()
        assert create_id.await_args.kwargs["external_user_id"] == "user_new"
        assert create_id.await_args.kwargs["provider"] == "hiring"


@pytest.mark.asyncio
async def test_mapping_mismatch_rejected():
    svc = _service()
    assertion = _make_generic_assertion(product_user_id="user_a")
    user = _ns_user()
    identity = SimpleNamespace(
        external_user_id="user_OTHER",
        user=user,
        user_id=user.id,
    )
    with patch.object(svc.repo, "get_external_identity", AsyncMock(return_value=identity)):
        with pytest.raises(ForbiddenError, match="mismatch"):
            await svc.exchange(assertion)


@pytest.mark.asyncio
async def test_disabled_user_rejected():
    svc = _service()
    assertion = _make_generic_assertion()
    user = _ns_user(is_active=False)
    identity = SimpleNamespace(
        external_user_id="user_abc",
        user=user,
        user_id=user.id,
    )
    with patch.object(svc.repo, "get_external_identity", AsyncMock(return_value=identity)):
        with pytest.raises(ForbiddenError, match="disabled"):
            await svc.exchange(assertion)


@pytest.mark.asyncio
async def test_core_jwt_sub_and_expiry():
    svc = _service(_settings(bridge_access_token_expire_seconds=90))
    assertion = _make_generic_assertion()
    user_id = uuid.uuid4()
    user = _ns_user(id=user_id)
    identity = SimpleNamespace(
        external_user_id="user_abc",
        user=user,
        user_id=user.id,
    )
    with patch.object(svc.repo, "get_external_identity", AsyncMock(return_value=identity)):
        result = await svc.exchange(assertion)
    payload = decode_token(
        result.access_token,
        secret_key="test-secret-key-not-for-prod-32b",
        expected_type="access",
    )
    assert payload["sub"] == str(user_id)
    assert payload["application"] == "hiring"
    assert "jti" in payload
    assert result.expires_in == 90
    exp = payload["exp"]
    if isinstance(exp, datetime):
        remaining = exp.timestamp() - time.time()
    else:
        remaining = float(exp) - time.time()
    assert 60 < remaining <= 90


@pytest.mark.asyncio
async def test_revenue_legacy_exchange_uses_revenue_provider():
    svc = _service()
    assertion = _make_revenue_legacy_assertion()
    user = _ns_user()
    identity = SimpleNamespace(
        external_user_id="user_abc",
        user=user,
        user_id=user.id,
    )
    with patch.object(svc.repo, "get_external_identity", AsyncMock(return_value=identity)) as get_id:
        result = await svc.exchange(assertion)
        assert result.application == "revenue"
        assert get_id.await_args.kwargs["provider"] == BRIDGE_PROVIDER
        assert get_id.await_args.kwargs["external_subject"] == "fb-uid-1"


@pytest.mark.asyncio
async def test_memory_accepts_exchanged_jwt_ownership():
    user_a = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    user_b = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    secret = "test-secret-key-not-for-prod-32b"
    token_a = create_access_token(
        subject=user_a,
        secret_key=secret,
        expires_seconds=300,
        extra_claims={"jti": "t1", "iss": "celestra-core", "aud": "celestra-core"},
    )
    claims = decode_token(token_a, secret_key=secret, expected_type="access")
    assert claims["sub"] == user_a

    store = InMemoryConversationStore()
    mem = MemoryService(
        conversations=ConversationMemory(store, window_size=10),
        vectors=MagicMock(),
        ai=None,
    )
    await mem.start_session(session_id="s1", user_id=user_a, application="revenue")
    await mem.add_message("s1", "user", "hello", user_id=user_a, application="revenue")
    msgs = await mem.get_messages("s1", user_id=user_a, application="revenue")
    assert msgs[0].content == "hello"

    from shared.exceptions.base import NotFoundError

    with pytest.raises(NotFoundError):
        await mem.get_messages("s1", user_id=user_b, application="revenue")
    with pytest.raises(NotFoundError):
        await mem.get_messages("s1", user_id=user_a, application="hiring")


def test_bridge_provider_for_application():
    assert bridge_provider_for("revenue") == "revenue"
    assert bridge_provider_for("hiring") == "hiring"
    assert BRIDGE_PROVIDER == "revenue"
