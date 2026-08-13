"""Step 7 — observability & readiness hardening tests."""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ai.router import ModelRouter
from ai.schemas import CompleteRequest, RenderPromptRequest
from ai.service import AIService
from config.settings import Settings, clear_settings_cache
from core.health import ready as ready_endpoint
from monitoring.application_context import normalize_application_label
from monitoring.errors import bridge_result_category, categorize_error
from monitoring.metrics import MetricsRegistry, init_metrics
from monitoring.middleware import MonitoringMiddleware
from monitoring.operations import timed_operation, timed_operation_sync
from prompts.loader import build_prompt_registry
from providers.mock import MockProvider
from providers.registry import ProviderRegistry
from shared.exceptions.base import (
    ConfigurationError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationAppError,
)
from shared.exceptions.handlers import register_exception_handlers
from shared.middleware.performance import PerformanceMiddleware
from shared.middleware.request_context import RequestContextMiddleware, resolve_request_id


def _captured_logs(caplog: pytest.LogCaptureFixture, capsys: pytest.CaptureFixture[str]) -> str:
    """structlog may write to stdout or stdlib logging depending on prior configure_logging."""
    parts = [capsys.readouterr().out, capsys.readouterr().err]
    for record in caplog.records:
        parts.append(str(record.getMessage()))
        parts.append(str(record.msg))
        parts.append(str(record.__dict__))
    return " ".join(parts)


@pytest.fixture(autouse=True)
def _reset_settings() -> None:
    clear_settings_cache()
    yield
    clear_settings_cache()


def _obs_app() -> FastAPI:
    app = FastAPI()
    init_metrics("celestra_test")
    app.add_middleware(MonitoringMiddleware)
    app.add_middleware(PerformanceMiddleware, enabled=False)
    app.add_middleware(RequestContextMiddleware, log_requests=False)
    register_exception_handlers(app)

    @app.get("/ping")
    async def ping() -> dict[str, str]:
        return {"status": "ok"}

    return app


def test_resolve_request_id_generates_when_absent():
    rid = resolve_request_id(None)
    assert len(rid) == 36


def test_resolve_request_id_preserves_valid():
    assert resolve_request_id("abc-123_XYZ.1") == "abc-123_XYZ.1"


def test_resolve_request_id_rejects_invalid():
    rid = resolve_request_id("bad id with spaces!!!")
    assert rid != "bad id with spaces!!!"
    assert len(rid) == 36


def test_request_id_generated_echoed_and_preserved():
    with TestClient(_obs_app()) as client:
        r1 = client.get("/ping")
        assert r1.status_code == 200
        generated = r1.headers.get("X-Request-ID")
        assert generated
        assert len(generated) == 36

        r2 = client.get("/ping", headers={"X-Request-ID": "client-req-001"})
        assert r2.headers.get("X-Request-ID") == "client-req-001"


def test_trace_id_defaults_to_request_id():
    with TestClient(_obs_app()) as client:
        r = client.get("/ping", headers={"X-Request-ID": "corr-abc-001"})
        assert r.headers.get("X-Request-ID") == "corr-abc-001"
        assert r.headers.get("X-Trace-ID") == "corr-abc-001"


def test_explicit_trace_id_preserved():
    with TestClient(_obs_app()) as client:
        r = client.get(
            "/ping",
            headers={"X-Request-ID": "req-1", "X-Trace-ID": "trace-explicit-9"},
        )
        assert r.headers.get("X-Request-ID") == "req-1"
        assert r.headers.get("X-Trace-ID") == "trace-explicit-9"


def test_application_label_vocabulary():
    assert normalize_application_label("revenue") == "revenue"
    assert normalize_application_label("CHRONA") == "chrona"
    assert normalize_application_label(None) == "default"
    assert normalize_application_label("custom-app") == "unknown"


def test_error_taxonomy_mapping():
    assert categorize_error(ValidationAppError("x")) == "validation_error"
    assert categorize_error(UnauthorizedError("x")) == "authentication_error"
    assert categorize_error(ForbiddenError("x")) == "authorization_error"
    assert categorize_error(NotFoundError("x")) == "not_found"
    assert categorize_error(ConfigurationError("x")) == "configuration_error"
    assert categorize_error(RuntimeError("boom")) == "internal_error"
    assert (
        bridge_result_category(UnauthorizedError("Assertion replay detected"), success=False)
        == "replay"
    )
    assert (
        bridge_result_category(ForbiddenError("Identity mapping mismatch"), success=False)
        == "mismatch"
    )
    assert bridge_result_category(None, success=True) == "ok"


@pytest.mark.asyncio
async def test_timed_operation_emits_and_fail_soft_on_metrics():
    metrics = init_metrics("celestra_ops_test")
    async with timed_operation("ai_complete", application="revenue", provider="mock"):
        pass
    with patch.object(metrics, "track_operation", side_effect=RuntimeError("metrics down")):
        async with timed_operation("memory_append", application="default"):
            value = 42
        assert value == 42


@pytest.mark.asyncio
async def test_timed_operation_failure_does_not_swallow_business_error():
    with pytest.raises(ValidationAppError):
        async with timed_operation("memory_get", application="default"):
            raise ValidationAppError("nope")


def test_prompt_render_timing_and_no_content_in_logs(
    caplog: pytest.LogCaptureFixture,
    capsys: pytest.CaptureFixture[str],
):
    registry = ProviderRegistry()
    registry.register(MockProvider())
    ai = AIService(
        registry=registry,
        router=ModelRouter(registry, default_provider="mock"),
        prompts=build_prompt_registry(),
        default_model="mock-chat",
    )
    secret_prompt = "SUPER_SECRET_PROMPT_BODY_XYZ"
    with caplog.at_level(logging.INFO):
        rendered = ai.render_prompt(
            RenderPromptRequest(name="chat.user_turn", variables={"question": secret_prompt})
        )
    assert secret_prompt in rendered.content
    out = _captured_logs(caplog, capsys)
    assert "operation_completed" in out
    assert "prompt_render" in out
    assert secret_prompt not in out


@pytest.mark.asyncio
async def test_ai_complete_timing_no_prompt_or_completion_in_logs(
    caplog: pytest.LogCaptureFixture,
    capsys: pytest.CaptureFixture[str],
):
    registry = ProviderRegistry()
    registry.register(MockProvider())
    ai = AIService(
        registry=registry,
        router=ModelRouter(registry, default_provider="mock"),
        prompts=build_prompt_registry(),
        default_model="mock-chat",
    )
    prompt = "PRIVATE_USER_PROMPT_SHOULD_NOT_LOG"
    with caplog.at_level(logging.INFO):
        result = await ai.complete(CompleteRequest(prompt=prompt))
    assert result.content
    out = _captured_logs(caplog, capsys)
    assert "ai_complete" in out or "operation_completed" in out
    assert prompt not in out
    assert result.content not in out


@pytest.mark.asyncio
async def test_memory_timing_no_message_content(
    caplog: pytest.LogCaptureFixture,
    capsys: pytest.CaptureFixture[str],
):
    from memory.buffer import InMemoryConversationStore
    from memory.conversation import ConversationMemory
    from memory.service import MemoryService
    from memory.vector import InMemoryVectorStore

    registry = ProviderRegistry()
    registry.register(MockProvider())
    ai = AIService(
        registry=registry,
        router=ModelRouter(registry, default_provider="mock"),
        prompts=build_prompt_registry(),
    )
    service = MemoryService(
        conversations=ConversationMemory(InMemoryConversationStore(), window_size=10),
        vectors=InMemoryVectorStore(),
        ai=ai,
    )
    secret = "MEMORY_BODY_MUST_NEVER_APPEAR"
    with caplog.at_level(logging.INFO):
        async with timed_operation("memory_append", application="revenue", backend="memory"):
            await service.start_session(session_id="s1", user_id="u1", application="revenue")
            await service.add_message("s1", "user", secret, user_id="u1", application="revenue")
    out = _captured_logs(caplog, capsys)
    assert "memory_append" in out
    assert secret not in out


def test_metrics_labels_exclude_high_cardinality():
    metrics = MetricsRegistry(namespace="celestra_label_test")
    metrics.track_operation(
        operation="memory_get",
        application="revenue",
        result="ok",
        duration_seconds=0.01,
    )
    body, _ = metrics.render_prometheus()
    text = body.decode()
    assert "celestra_label_test_operation_total" in text
    assert 'operation="memory_get"' in text
    assert 'application="revenue"' in text
    assert 'user_id="' not in text
    assert 'session_id="' not in text
    assert 'request_id="' not in text


@pytest.mark.asyncio
async def test_health_ok_when_redis_down():
    from core.health import health

    settings = Settings(env="test", secret_key="test-secret-key-not-for-prod")  # type: ignore[arg-type]
    result = await health(settings)
    assert result.status == "ok"


@pytest.mark.asyncio
async def test_ready_503_when_required_redis_unavailable():
    settings = Settings(
        env="test",
        secret_key="test-secret-key-not-for-prod",
        memory_conversation_backend="redis",
        ready_check_db=False,
    )  # type: ignore[arg-type]
    with patch("core.health._check_redis", new=AsyncMock(return_value=False)):
        response = await ready_endpoint(settings)
    from fastapi.responses import JSONResponse
    import json

    assert isinstance(response, JSONResponse)
    assert response.status_code == 503
    data = json.loads(response.body)
    assert data["status"] == "unavailable"
    assert data["redis"] is False
    assert data["redis_required"] is True


@pytest.mark.asyncio
async def test_ready_ok_when_optional_redis_unavailable():
    settings = Settings(
        env="test",
        secret_key="test-secret-key-not-for-prod",
        memory_conversation_backend="memory",
        workflow_run_backend="memory",
        ready_check_db=False,
    )  # type: ignore[arg-type]
    with patch("core.health._check_redis", new=AsyncMock(return_value=False)):
        response = await ready_endpoint(settings)
    assert response.status == "ok"  # type: ignore[union-attr]
    assert response.redis is False  # type: ignore[union-attr]
    assert response.redis_required is False  # type: ignore[union-attr]


@pytest.mark.asyncio
async def test_ready_db_check_when_enabled():
    settings = Settings(
        env="test",
        secret_key="test-secret-key-not-for-prod",
        memory_conversation_backend="memory",
        ready_check_db=True,
    )  # type: ignore[arg-type]
    with (
        patch("core.health._check_redis", new=AsyncMock(return_value=True)),
        patch("core.health._check_database", new=AsyncMock(return_value=False)),
    ):
        response = await ready_endpoint(settings)
    from fastapi.responses import JSONResponse

    assert isinstance(response, JSONResponse)
    assert response.status_code == 503


def test_privacy_no_jwt_api_key_firebase_in_operation_logs(
    caplog: pytest.LogCaptureFixture,
    capsys: pytest.CaptureFixture[str],
):
    jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.sig"
    api_key = "cel_live_secret_key_abc123"
    firebase = "firebase_id_token_should_not_appear"

    with caplog.at_level(logging.INFO):
        with timed_operation_sync("bridge_exchange", application="revenue") as op:
            op.set(provisioned=True)
            op.set(jwt=jwt_token, api_key=api_key, firebase_token=firebase)

    out = _captured_logs(caplog, capsys)
    assert jwt_token not in out
    assert api_key not in out
    assert firebase not in out
    assert "provisioned" in out


def test_observability_failure_does_not_break_sync_operation():
    with patch("monitoring.operations.logger") as mock_logger:
        mock_logger.info.side_effect = RuntimeError("log sink down")
        with timed_operation_sync("prompt_render", application="default") as op:
            op.set(prompt_name="chat.user_turn")
            done = True
        assert done is True
