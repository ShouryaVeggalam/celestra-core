# Monitoring — Celestra Core

Lightweight observability on the existing **structlog + Prometheus** stack.
No OpenTelemetry, Kafka, or external monitoring SaaS.

## Request correlation

| Identifier | Policy |
|---|---|
| `request_id` | **Primary.** Accept valid `X-Request-ID` (1–128 chars: `A–Z a–z 0–9 . _ -`) or generate a UUID. Echoed on every response as `X-Request-ID`. Bound into structlog context. |
| `trace_id` | Defaults to `request_id`. If the client sends `X-Trace-ID`, that value is preserved. |
| `span_id` | Generated per request for span correlation. |

Do not treat `user_id` / `session_id` as correlation substitutes for request tracing.

## Structured logs

JSON when `CELESTRA_LOG_JSON=true`. Operation events use event name `operation_completed` with fields:

- `request_id`, `operation`, `application`, `duration_ms`, `success`, `error_category` (on failure)
- Optional: `provider`, `model`, `backend`, `provisioned`, `prompt_name`, token counts when the provider already returns them

## Metrics (Prometheus)

Scrape `GET /metrics`. Namespace defaults to `celestra` (`CELESTRA_METRICS_NAMESPACE`).

| Metric | Labels |
|---|---|
| `celestra_operation_total` | `operation`, `application`, `result` |
| `celestra_operation_duration_seconds` | `operation`, `application`, `result` |
| `celestra_operation_errors_total` | `operation`, `application`, `result` |
| `celestra_operation_ai_total` | `operation`, `application`, `result`, `provider` |

**Never** use as labels: `user_id`, `session_id`, `firebase_uid`, `request_id`, raw URLs, free-form prompt names.

### Application labels (bounded)

`revenue` | `hiring` | `finance` | `chrona` | `default` | `unknown`

Application is taken from authenticated JWT claims or validated product fields — never from an arbitrary frontend header as authority.

## Operation categories

| Operation | Where |
|---|---|
| `ai_complete` / `ai_embed` | AI facade |
| `prompt_render` | Prompt registry render path |
| `memory_session_start` / `memory_append` / `memory_get` | Memory HTTP API |
| `bridge_exchange` | Identity bridge |

Bridge `result` values: `ok`, `unauthorized`, `replay`, `mismatch`, `disabled`, `configuration_error`, `internal_error`.

## Error taxonomy

Mapped from Core exceptions to: `validation_error`, `authentication_error`, `authorization_error`, `not_found`, `conflict`, `configuration_error`, `external_service_error`, `provider_error`, `dependency_unavailable`, `timeout`, `internal_error`.

API responses keep the existing error contract (no stack traces to clients).

## Privacy policy

**Safe to log:** request_id, application, operation, duration_ms, success, status, error_category, provider, non-sensitive model name, backend, provisioned, HTTP method, normalized path, HTTP status.

**Must never log:** passwords, API keys, JWTs, Firebase tokens, assertions, prompts, AI completions, memory message bodies, conversation history, CRM/PII, secrets, database URLs, Redis URLs, credentials, raw request/response bodies.

## Health vs readiness

| Endpoint | Meaning | Dependency checks |
|---|---|---|
| `GET /health` | Liveness — is the process alive? | None (always independent of Redis/DB/providers) |
| `GET /ready` | Readiness — can this instance serve traffic? | Only **required** deps for current config |

When a required dependency is down, `/ready` returns **HTTP 503** (not 200 + `degraded`).

Redis is required when `CELESTRA_MEMORY_CONVERSATION_BACKEND=redis` or `CELESTRA_WORKFLOW_RUN_BACKEND=redis`. Optional Redis failure does not make the instance unready.

Optional DB probe: `CELESTRA_READY_CHECK_DB=true` runs `SELECT 1`.

## Config

| Env var | Default | Notes |
|---|---|---|
| `CELESTRA_METRICS_ENABLED` | `true` | |
| `CELESTRA_METRICS_NAMESPACE` | `celestra` | |
| `CELESTRA_LOG_LEVEL` | `INFO` | |
| `CELESTRA_LOG_JSON` | `true` | |
| `CELESTRA_LOG_REQUESTS` | `true` | |
| `CELESTRA_LOG_PERFORMANCE` | `true` | |
| `CELESTRA_SLOW_REQUEST_MS` | `1000` | Slow-request log threshold |
| `CELESTRA_READY_CHECK_DB` | `false` | Conservative; enable in prod if DB is required for traffic |

## Production recommendations

1. Scrape `/metrics` from each worker (process-local registry).
2. Alert on `/ready` 503 and elevated `celestra_operation_errors_total`.
3. Keep conversation backend Redis highly available when configured as `redis`.
4. Never ship prompt/completion/memory content to log aggregators via custom instrumentation.
5. Prefer `request_id` for support correlation across Core and product services.

## Files

| File | Role |
|---|---|
| `monitoring/metrics.py` | Prometheus registry |
| `monitoring/operations.py` | Fail-soft `timed_operation` |
| `monitoring/errors.py` | Error category mapping |
| `monitoring/application_context.py` | Bounded application labels |
| `monitoring/tracing.py` | Trace/span contextvars |
| `monitoring/middleware.py` | HTTP metrics + trace headers |
| `shared/middleware/request_context.py` | `request_id` policy |
| `core/health.py` | `/health`, `/ready` |
