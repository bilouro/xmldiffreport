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


def display_names(labels: list[str]) -> dict[str, str]:
    """Map each source label (a file path) to a compact display name.

    A label is shown as its file name preceded by one directory
    (``parent/file.xml``) instead of the full, often absolute, path. When two
    labels would collapse to the same short form, just enough leading path
    components are kept to keep them distinct.
    """

    def segments(label: str) -> list[str]:
        return [p for p in label.replace("\\", "/").split("/") if p]

    segs = {lbl: segments(lbl) for lbl in labels}
    out: dict[str, str] = {}
    for lbl in labels:
        parts = segs[lbl]
        if not parts:
            out[lbl] = lbl
            continue
        n = min(2, len(parts))
        while n < len(parts) and any(
            other != lbl and segs[other][-n:] == parts[-n:] for other in labels
        ):
            n += 1
        out[lbl] = "/".join(parts[-n:])
    return out


def env_labels(labels: list[str]) -> dict[str, str]:
    """Map each source label to a short *environment* name: the immediate parent
    directory (``.../bench/export.xml`` -> ``bench``).

    These are the compact column headers used in the diff tables. The full
    file paths are still listed once, at the top of the report. If two sources
    share a parent-directory name, those two fall back to ``parent/file`` so
    the columns stay distinct.
    """

    def segments(label: str) -> list[str]:
        return [p for p in label.replace("\\", "/").split("/") if p]

    def env_of(parts: list[str]) -> str:
        return parts[-2] if len(parts) >= 2 else (parts[-1] if parts else "")

    segs = {lbl: segments(lbl) for lbl in labels}
    counts: dict[str, int] = {}
    for lbl in labels:
        e = env_of(segs[lbl])
        counts[e] = counts.get(e, 0) + 1

    out: dict[str, str] = {}
    for lbl in labels:
        parts = segs[lbl]
        if not parts:
            out[lbl] = lbl
        elif counts.get(env_of(parts), 0) > 1:  # collision -> disambiguate
            out[lbl] = "/".join(parts[-2:]) if len(parts) >= 2 else parts[-1]
        else:
            out[lbl] = env_of(parts)
    return out


@dataclass
class DiffReport:
    """The result of a diff and everything a renderer needs to format it.

    ``units`` are the ``NodeDiff`` objects that differ; ``sources`` are the
    labels (file paths) that were compared. ``source_display`` maps each label
    to its ``parent/file`` form; ``source_env`` to the bare environment name.
    """

    units: list
    sources: list[str]
    recipe_name: str
    generated_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    source_display: dict[str, str] = field(init=False, default_factory=dict)
    source_env: dict[str, str] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        self.source_display = display_names(self.sources)
        self.source_env = env_labels(self.sources)

    def __bool__(self) -> bool:
        """True if any unit differs (handy for exit codes)."""
        return bool(self.units)

    def render(self, fmt: str = "md") -> str:
        """Render this report in the given format (default Markdown)."""
        return get_renderer(fmt).render(self)


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
