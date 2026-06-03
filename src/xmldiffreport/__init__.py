"""xmldiffreport — N-way, recipe-driven structural XML diff with reports."""

__version__ = "0.1.0"

from .core import diff_sources, load_recipe, parse_xml  # noqa: F401
from .report import get_renderer, list_formats, render  # noqa: F401
