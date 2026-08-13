# Prompts — Celestra Core

Versioned Jinja2 templates for platform use.

## Principles

- Platform prompts stay domain-agnostic
- Templates are named + versioned (`name@version`)
- Required variables are validated before render
- Product-specific prompts belong in products

## Usage

```python
from prompts import build_prompt_registry

registry = build_prompt_registry()
text = registry.render("analysis.summarize", {"content": "..."})
```

## Built-in prompts (CORE PLATFORM)

| Name | Purpose |
|---|---|
| `system.assistant` | Generic system prompt |
| `chat.user_turn` | User turn + optional context |
| `analysis.summarize` | Summarization |

## Examples (OPTIONAL / DOMAIN-SPECIFIC)

Under `prompts/examples/` — **not loaded by default**:

| File | Classification |
|---|---|
| `hiring.screen_resume.md` | DOMAIN-SPECIFIC example |
| `research.company_brief.md` | EXAMPLE / OPTIONAL |

Enable with `CELESTRA_LOAD_EXAMPLE_PROMPTS=true` or `build_prompt_registry(load_examples=True)`.

## Files

| Path | Role |
|---|---|
| `template.py` | `PromptTemplate` + Jinja render |
| `registry.py` | Versioned registry |
| `loader.py` | File + default loaders |
| `library/` | Optional platform markdown (empty by default) |
| `examples/` | Non-default example prompts |
