"""In-memory prompt registry with versioning."""

from __future__ import annotations

from prompts.template import PromptTemplate
from shared.exceptions.base import NotFoundError


class PromptRegistry:
    def __init__(self) -> None:
        # name -> version -> template
        self._templates: dict[str, dict[str, PromptTemplate]] = {}

    def register(self, template: PromptTemplate, *, overwrite: bool = False) -> None:
        versions = self._templates.setdefault(template.name, {})
        if template.version in versions and not overwrite:
            raise ValueError(f"Prompt already registered: {template.key}")
        versions[template.version] = template

    def get(self, name: str, version: str | None = None) -> PromptTemplate:
        if name not in self._templates or not self._templates[name]:
            raise NotFoundError(f"Prompt '{name}' not found")
        versions = self._templates[name]
        if version is None:
            # Prefer highest semantic-ish version string; fall back to sorted
            version = sorted(versions.keys())[-1]
        if version not in versions:
            raise NotFoundError(
                f"Prompt '{name}@{version}' not found",
                details={"available_versions": sorted(versions)},
            )
        return versions[version]

    def list(self) -> list[PromptTemplate]:
        items: list[PromptTemplate] = []
        for versions in self._templates.values():
            items.extend(versions.values())
        return sorted(items, key=lambda t: (t.name, t.version))

    def names(self) -> list[str]:
        return sorted(self._templates)

    def render(self, name: str, variables: dict | None = None, *, version: str | None = None) -> str:
        return self.get(name, version=version).render(variables)
