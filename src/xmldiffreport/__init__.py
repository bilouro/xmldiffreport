"""xmldiffreport — N-way, recipe-driven structural XML diff with reports.

Quick library use::

    from xmldiffreport import diff

    result = diff(["old.xml", "new.xml"], recipe="sitemap")   # a file, files, or dir(s)
    print(result.render())                                    # Markdown (or "html")
    if result:                                                # truthy if anything differs
        ...
"""

from __future__ import annotations

from .core import (  # noqa: F401
    diff_sources,
    gather_files,
    load_recipe,
    parse_xml,
    validate_recipe,
)
from .report import DiffReport, get_renderer, list_formats, render  # noqa: F401

__version__ = "0.3.2"


def diff(paths, recipe: str = "generic") -> DiffReport:
    """Diff a file, multiple files, and/or directories.

    ``paths`` is a path or an iterable of paths (files and/or directories;
    directories are scanned recursively for ``*.xml``). ``recipe`` is a built-in
    recipe name, a path to a ``.toml``, or an already-loaded recipe dict.
    Returns a :class:`DiffReport` — call ``.render()`` on it, or iterate
    ``.units``.
    """
    rec = recipe if isinstance(recipe, dict) else load_recipe(recipe)
    sources = [(label, parse_xml(p)) for label, p in gather_files(paths)]
    units = diff_sources(rec, sources)
    name = rec.get("name") or (recipe if isinstance(recipe, str) else "recipe")
    return DiffReport(units=units, sources=[lbl for lbl, _ in sources], recipe_name=name)
