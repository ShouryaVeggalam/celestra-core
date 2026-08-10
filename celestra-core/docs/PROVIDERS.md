# Providers — Celestra Core (Phase 3)

Pluggable LLM adapters behind `LLMProvider`.

## Interface

```python
class LLMProvider(ABC):
    async def complete(request: CompletionRequest) -> CompletionResponse: ...
    async def stream(request: CompletionRequest) -> AsyncIterator[str]: ...
    async def embed(request: EmbeddingRequest) -> EmbeddingResponse: ...
```

## Built-in providers

| Name | When registered | Completions | Embeddings |
|---|---|---|---|
| `mock` | Always | Yes | Yes (8-dim deterministic) |
| `openai` | `CELESTRA_OPENAI_API_KEY` set | Yes (OpenAI-compatible HTTP) | Yes |
| `anthropic` | `CELESTRA_ANTHROPIC_API_KEY` set | Yes (Messages API) | No |

OpenAI adapter works with OpenAI, many Azure/OpenAI-compatible gateways, and local servers that speak `/v1/chat/completions`.

## Extending

```python
from providers.base import LLMProvider
from providers.registry import ProviderRegistry

class MyProvider(LLMProvider):
    name = "myco"
    async def complete(self, request): ...

registry.register(MyProvider())
```

## Files

| File | Role |
|---|---|
| `base.py` | ABC |
| `types.py` | Shared DTOs |
| `registry.py` | Name → provider |
| `factory.py` | Settings → registry |
| `mock.py` | Dev/test provider |
| `openai_compatible.py` | OpenAI HTTP |
| `anthropic.py` | Anthropic HTTP |
| `exceptions.py` | Provider errors |
