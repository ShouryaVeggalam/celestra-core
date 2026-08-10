# Monitoring — Celestra Core

Observability primitives on top of Phase 1 structured logging.

## Capabilities

- Prometheus metrics registry (counters, histograms, gauges)
- HTTP request metrics middleware (latency, status, in-flight)
- Trace / span IDs propagated in logs and response headers
- Structured monitoring events
- Auth login success/failure counters
- Error-code counters via exception handlers

## Endpoints

| Path | Auth | Description |
|---|---|---|
| `GET /metrics` | No | Prometheus scrape |
| `GET /monitoring/status` | `monitoring:read` | Platform monitoring status |

## Headers

| Header | Meaning |
|---|---|
| `X-Trace-ID` | Correlation id (accepts incoming or generates) |
| `X-Span-ID` | Per-request span |
| `X-Request-ID` | From Phase 1 request middleware (also accepted as trace seed) |

## Product app usage

```python
from monitoring import get_metrics, emit_event, start_trace

metrics = get_metrics()
metrics.observe_request(method="POST", path="/jobs", status=202, duration_seconds=0.12)
emit_event("job.enqueued", job_id="...", level="info")
```

## Config

| Env var | Default |
|---|---|
| `CELESTRA_METRICS_ENABLED` | `true` |
| `CELESTRA_METRICS_NAMESPACE` | `celestra` |

## Files

| File | Role |
|---|---|
| `metrics.py` | Prometheus registry facade |
| `tracing.py` | Trace/span contextvars |
| `middleware.py` | Request metrics + trace headers |
| `events.py` | Structured event emitter |
| `router.py` | `/metrics`, `/monitoring/status` |
