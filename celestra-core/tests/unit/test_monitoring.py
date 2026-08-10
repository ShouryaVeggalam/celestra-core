"""Unit tests — monitoring metrics and tracing."""

from monitoring.metrics import MetricsRegistry, _normalize_path
from monitoring.tracing import clear_trace, get_trace_id, start_trace, trace_headers


def test_metrics_observe_and_render():
    metrics = MetricsRegistry(namespace="test")
    metrics.set_app_info(app="celestra-core", env="test", version="0.2.0")
    metrics.observe_request(method="GET", path="/api/v1/auth/me", status=200, duration_seconds=0.01)
    metrics.track_login(success=True)
    metrics.track_error("not_found")
    body, content_type = metrics.render_prometheus()
    text = body.decode("utf-8")
    assert "test_http_requests_total" in text
    assert "test_auth_logins_total" in text
    assert "prometheus" in content_type or "text/plain" in content_type


def test_path_normalization_collapses_uuids():
    path = "/api/v1/auth/api-keys/550e8400-e29b-41d4-a716-446655440000"
    assert _normalize_path(path) == "/api/v1/auth/api-keys/:id"


def test_trace_context():
    tid, sid = start_trace(trace_id="abc", span_id="def")
    assert tid == "abc"
    assert sid == "def"
    assert get_trace_id() == "abc"
    headers = trace_headers()
    assert headers["X-Trace-ID"] == "abc"
    assert headers["X-Span-ID"] == "def"
    clear_trace()
    assert get_trace_id() is None
