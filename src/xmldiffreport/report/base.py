"""Renderer strategy + registry (factory) for diff reports.

Adding a new output format is a single class:

    from .base import DiffReport, Renderer, register

    @register
    class JsonRenderer(Renderer):
        format = "json"
        file_extension = "json"
        def render(self, report: DiffReport) -> str:
            ...
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar


@dataclass
class DiffReport:
    """Everything a renderer needs to produce an output document."""

    results: list
    envs: list[str]
    n_sources: int
    recipe_name: str
    generated_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))


class Renderer(ABC):
    """Strategy: turn a :class:`DiffReport` into a document string."""

    format: ClassVar[str]
    file_extension: ClassVar[str]

    @abstractmethod
    def render(self, report: DiffReport) -> str:  # pragma: no cover - interface
        ...


_REGISTRY: dict[str, type[Renderer]] = {}


def register(cls: type[Renderer]) -> type[Renderer]:
    """Class decorator that registers a renderer by its ``format`` name."""
    _REGISTRY[cls.format] = cls
    return cls


def get_renderer(fmt: str) -> Renderer:
    """Instantiate the renderer registered for ``fmt`` (the factory)."""
    try:
        return _REGISTRY[fmt]()
    except KeyError:
        raise ValueError(
            f"unknown format: {fmt!r}. Available: {', '.join(list_formats())}"
        ) from None


def list_formats() -> list[str]:
    """All registered format names, sorted."""
    return sorted(_REGISTRY)
