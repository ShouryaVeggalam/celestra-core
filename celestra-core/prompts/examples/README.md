# Example / optional prompts (NOT loaded by default)

These templates are **domain-specific examples** for documentation and local
experiments. They are **not** part of the default Core platform surface.

| File | Classification |
|---|---|
| `hiring.screen_resume.md` | DOMAIN-SPECIFIC (example) |
| `research.company_brief.md` | EXAMPLE / OPTIONAL |

Load explicitly:

```python
from pathlib import Path
from prompts.loader import build_prompt_registry, load_prompts_from_directory

registry = build_prompt_registry()
load_prompts_from_directory(Path(__file__).resolve().parent / "examples", registry)
```

Or set `CELESTRA_LOAD_EXAMPLE_PROMPTS=true` at Core startup.
