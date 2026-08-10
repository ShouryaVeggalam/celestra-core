"""Load prompt templates from markdown/YAML-frontmatter files and built-ins."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from prompts.registry import PromptRegistry
from prompts.template import PromptTemplate

_FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def _parse_simple_front_matter(raw: str) -> dict[str, Any]:
    """Minimal YAML-ish front matter parser (key: value / key: [a, b])."""
    data: dict[str, Any] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [part.strip().strip("'\"") for part in inner.split(",") if part.strip()] if inner else []
        else:
            data[key] = value.strip("'\"")
    return data


def load_prompt_file(path: Path) -> PromptTemplate:
    text = path.read_text(encoding="utf-8")
    match = _FRONT_MATTER.match(text)
    if match:
        meta = _parse_simple_front_matter(match.group(1))
        body = match.group(2).strip()
    else:
        meta = {}
        body = text.strip()

    name = str(meta.get("name") or path.stem)
    version = str(meta.get("version") or "1")
    description = str(meta.get("description") or "")
    required = meta.get("required_variables") or []
    if isinstance(required, str):
        required = [required]
    return PromptTemplate(
        name=name,
        version=version,
        description=description,
        template=body,
        required_variables=list(required),
        metadata={"source": str(path)},
    )


def load_prompts_from_directory(directory: Path, registry: PromptRegistry | None = None) -> PromptRegistry:
    registry = registry or PromptRegistry()
    if not directory.exists():
        return registry
    for path in sorted(directory.glob("**/*")):
        if path.suffix.lower() not in {".md", ".j2", ".txt", ".prompt"}:
            continue
        template = load_prompt_file(path)
        registry.register(template, overwrite=True)
    return registry


DEFAULT_PROMPTS: list[PromptTemplate] = [
    PromptTemplate(
        name="system.assistant",
        version="1",
        description="Generic helpful assistant system prompt",
        template=(
            "You are {{ assistant_name | default('Celestra') }}, an enterprise AI assistant.\n"
            "Be precise, grounded, and concise. If unsure, say so."
        ),
        required_variables=[],
    ),
    PromptTemplate(
        name="chat.user_turn",
        version="1",
        description="Wrap a user question with optional context",
        template=(
            "{% if context is defined and context %}Context:\n{{ context }}\n\n{% endif %}"
            "Question:\n{{ question }}"
        ),
        required_variables=["question"],
    ),
    PromptTemplate(
        name="analysis.summarize",
        version="1",
        description="Summarize content for enterprise workflows",
        template=(
            "Summarize the following {{ content_type | default('document') }} "
            "in {{ style | default('bullet points') }}.\n\n"
            "{{ content }}"
        ),
        required_variables=["content"],
    ),
]


def build_prompt_registry(library_dir: Path | None = None) -> PromptRegistry:
    registry = PromptRegistry()
    for template in DEFAULT_PROMPTS:
        registry.register(template, overwrite=True)
    if library_dir is None:
        library_dir = Path(__file__).resolve().parent / "library"
    load_prompts_from_directory(library_dir, registry)
    return registry
