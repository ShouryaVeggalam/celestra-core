"""Prompt template model with Jinja2 rendering and required-variable validation."""

from __future__ import annotations

import re
from typing import Any

from jinja2 import BaseLoader, Environment, StrictUndefined, TemplateError, meta
from pydantic import BaseModel, Field

from shared.exceptions.base import ValidationAppError

_VAR_PATTERN = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)")


class PromptTemplate(BaseModel):
    """Versioned prompt template used across Celestra applications."""

    name: str
    version: str = "1"
    description: str = ""
    template: str
    required_variables: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"{self.name}@{self.version}"

    def discover_variables(self) -> set[str]:
        env = Environment(loader=BaseLoader(), undefined=StrictUndefined)
        ast = env.parse(self.template)
        return set(meta.find_undeclared_variables(ast))

    def render(self, variables: dict[str, Any] | None = None) -> str:
        variables = variables or {}
        required = set(self.required_variables) or self.discover_variables()
        missing = sorted(required - set(variables))
        if missing:
            raise ValidationAppError(
                "Missing prompt variables",
                details={"prompt": self.key, "missing": missing},
            )
        env = Environment(loader=BaseLoader(), undefined=StrictUndefined, autoescape=False)
        try:
            return env.from_string(self.template).render(**variables).strip()
        except TemplateError as exc:
            raise ValidationAppError(
                f"Prompt render failed: {exc}",
                details={"prompt": self.key},
            ) from exc
