# AI — Celestra Core (Phase 3)

Platform AI facade for every Celestra application (OpenAI SDK / LangChain–style, not app-local wrappers).

## Capabilities

- Unified `AIService.complete()` / `embed()`
- Model routing (`gpt-*` → OpenAI, `claude-*` → Anthropic, `mock-*` → mock)
- Prompt-driven generation via `prompt_name` + variables
- Provider registry with pluggable adapters
- HTTP API under `/api/v1/ai/*`
- Prometheus AI request metrics

## Product app usage

```python
from ai import AIService, CompleteRequest
from providers.types import Message, Role

result = await ai_service.complete(
    CompleteRequest(
        messages=[Message(role=Role.USER, content="Hello")],
        model="gpt-4o-mini",  # routes to openai when keyed; else mock fallback
    )
)

result = await ai_service.complete(
    CompleteRequest(
        prompt_name="analysis.summarize",
        prompt_variables={"content": "..."},
    )
)
```

Do **not** import `openai` / `anthropic` SDKs in product apps.

## HTTP API (`/api/v1/ai`) — requires auth

| Method | Path | Description |
|---|---|---|
| GET | `/providers` | Registered providers |
| GET | `/prompts` | Prompt catalog |
| POST | `/complete` | Chat completion |
| POST | `/embed` | Embeddings |
| POST | `/prompts/render` | Render a template |

## Config

| Env var | Default |
|---|---|
| `CELESTRA_AI_DEFAULT_PROVIDER` | `mock` |
| `CELESTRA_AI_DEFAULT_MODEL` | `mock-chat` |
| `CELESTRA_OPENAI_API_KEY` | (empty → provider skipped) |
| `CELESTRA_ANTHROPIC_API_KEY` | (empty → provider skipped) |

## Files

| Path | Role |
|---|---|
| `ai/service.py` | Facade |
| `ai/router.py` | Model → provider |
| `ai/http.py` | HTTP routes |
| `providers/*` | Adapters |
| `prompts/*` | Templates + registry |
