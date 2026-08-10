"""
Prompts module — versioned templates and rendering for all Celestra apps.

Applications must not hardcode prompt strings; they register or load templates
through this module.
"""

from prompts.loader import build_prompt_registry, load_prompt_file, load_prompts_from_directory
from prompts.registry import PromptRegistry
from prompts.template import PromptTemplate

__all__ = [
    "PromptRegistry",
    "PromptTemplate",
    "build_prompt_registry",
    "load_prompt_file",
    "load_prompts_from_directory",
]
