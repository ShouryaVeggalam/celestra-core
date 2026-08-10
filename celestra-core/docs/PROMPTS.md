# Prompts — Celestra Core (Phase 3)

Versioned Jinja2 templates for all Celestra apps.

## Principles

- No hardcoded prompt strings in product apps
- Templates are named + versioned (`name@version`)
- Required variables are validated before render
- File library + in-code defaults

## Usage

```python
from prompts import build_prompt_registry

registry = build_prompt_registry()
text = registry.render("analysis.summarize", {"content": "..."})
template = registry.get("hiring.screen_resume", version="1")
```

## Built-in prompts

| Name | Purpose |
|---|---|
| `system.assistant` | Generic system prompt |
| `chat.user_turn` | User turn + optional context |
| `analysis.summarize` | Summarization |

## Library files

| File | Prompt |
|---|---|
| `prompts/library/hiring.screen_resume.md` | Resume screening |
| `prompts/library/research.company_brief.md` | Company research brief |

Front matter format:

```md
---
name: my.prompt
version: 1
description: ...
required_variables: [foo, bar]
---
Template body with {{ foo }}
```

## Files

| File | Role |
|---|---|
| `template.py` | `PromptTemplate` + Jinja render |
| `registry.py` | Versioned registry |
| `loader.py` | File + default loaders |
| `library/` | Markdown prompt assets |
