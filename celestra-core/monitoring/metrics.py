"""Process-local metrics registry with Prometheus exposition."""

from __future__ import annotations

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)


class MetricsRegistry:
    """
    Platform metrics facade.

    Apps and Core middleware record metrics here. A single registry is shared
    per process (suitable for one uvicorn worker; multi-worker scrapes each).
    """

    def __init__(self, namespace: str = "celestra") -> None:
        self.namespace = namespace
        self.registry = CollectorRegistry()

        self.http_requests_total = Counter(
            f"{namespace}_http_requests_total",
            "Total HTTP requests",
            ["method", "path", "status"],
            registry=self.registry,
        )
        self.http_request_duration_seconds = Histogram(
            f"{namespace}_http_request_duration_seconds",
            "HTTP request latency in seconds",
            ["method", "path"],
            registry=self.registry,
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
        )
        self.http_requests_in_progress = Gauge(
            f"{namespace}_http_requests_in_progress",
            "In-flight HTTP requests",
            registry=self.registry,
        )
        self.app_info = Gauge(
            f"{namespace}_app_info",
            "Application info (always 1)",
            ["app", "env", "version"],
            registry=self.registry,
        )
        self.auth_logins_total = Counter(
            f"{namespace}_auth_logins_total",
            "Auth login attempts",
            ["result"],
            registry=self.registry,
        )
        self.errors_total = Counter(
            f"{namespace}_errors_total",
            "Application errors by code",
            ["code"],
            registry=self.registry,
        )
        self.ai_requests_total = Counter(
            f"{namespace}_ai_requests_total",
            "AI facade requests",
            ["provider", "kind", "result"],
            registry=self.registry,
        )
        self.ai_request_duration_seconds = Histogram(
            f"{namespace}_ai_request_duration_seconds",
            "AI facade request latency in seconds",
            ["provider", "kind"],
            registry=self.registry,
            buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
        )
        self.analytics_events_total = Counter(
            f"{namespace}_analytics_events_total",
            "Product analytics events",
            ["event"],
            registry=self.registry,
        )
        self.billing_usage_total = Counter(
            f"{namespace}_billing_usage_total",
            "Billing usage quantity recorded",
            ["metric"],
            registry=self.registry,
        )

    def set_app_info(self, *, app: str, env: str, version: str = "0.6.0") -> None:
        self.app_info.labels(app=app, env=env, version=version).set(1)

    def observe_request(self, *, method: str, path: str, status: int, duration_seconds: float) -> None:
        # Collapse high-cardinality path params for common UUID segments later if needed
        normalized = _normalize_path(path)
        self.http_requests_total.labels(method=method, path=normalized, status=str(status)).inc()
        self.http_request_duration_seconds.labels(method=method, path=normalized).observe(duration_seconds)

    def track_login(self, *, success: bool) -> None:
        self.auth_logins_total.labels(result="success" if success else "failure").inc()

    def track_error(self, code: str) -> None:
        self.errors_total.labels(code=code).inc()

    def render_prometheus(self) -> tuple[bytes, str]:
        return generate_latest(self.registry), CONTENT_TYPE_LATEST


def _normalize_path(path: str) -> str:
    """Reduce cardinality: replace UUID-looking segments with :id."""
    parts: list[str] = []
    for part in path.split("/"):
        if _looks_like_uuid(part):
            parts.append(":id")
        else:
            parts.append(part)
    return "/".join(parts) or "/"


def _looks_like_uuid(value: str) -> bool:
    if len(value) != 36:
        return False
    try:
        import uuid
        uuid.UUID(value)
        return True
    except ValueError:
        return False


_metrics: MetricsRegistry | None = None


def init_metrics(namespace: str = "celestra") -> MetricsRegistry:
    global _metrics
    _metrics = MetricsRegistry(namespace=namespace)
    return _metrics


def get_metrics() -> MetricsRegistry:
    if _metrics is None:
        return init_metrics()
    return _metrics
