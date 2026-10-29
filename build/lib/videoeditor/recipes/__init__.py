"""Use-case recipes. Adding one = a module here that calls `register(...)` plus a branch in
questionnaire.select_recipes. Each recipe turns a brief into an ordered list of concrete `ve` steps
and points at its playbook (the judgment calls an agent should make along the way)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

REGISTRY: dict[str, "Recipe"] = {}


@dataclass
class Recipe:
    name: str
    title: str
    summary: str
    steps: Callable[[dict], list[str]]

    @property
    def playbook(self) -> Path:
        return Path(__file__).parent / "playbooks" / f"{self.name}.md"


def register(recipe: Recipe) -> Recipe:
    REGISTRY[recipe.name] = recipe
    return recipe


def get(name: str) -> Recipe:
    from videoeditor.recipes import highlight_clips, long_form, action_montage, explainer  # noqa: F401  (registers)
    if name not in REGISTRY:
        raise SystemExit(f"unknown recipe '{name}' (have: {', '.join(sorted(REGISTRY))})")
    return REGISTRY[name]
