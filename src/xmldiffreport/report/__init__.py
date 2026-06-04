"""Report rendering: a strategy/factory over pluggable output formats.

    from xmldiffreport.report import render, get_renderer, list_formats

`render(report, fmt)` is a convenience wrapper; `get_renderer(fmt)` returns the
strategy for a given format ("md", "html", ...). Register new formats with
`@register`.
"""

from __future__ import annotations

from . import html as _html  # noqa: F401  (import for @register side-effect)
from . import markdown as _markdown  # noqa: F401  (import for @register side-effect)
from .base import DiffReport, Renderer, get_renderer, list_formats, register

__all__ = [
    "DiffReport",
    "Renderer",
    "get_renderer",
    "list_formats",
    "register",
    "render",
]


def render(report: DiffReport, fmt: str = "md") -> str:
    """Render a :class:`DiffReport` in the requested format (default Markdown)."""
    return get_renderer(fmt).render(report)
