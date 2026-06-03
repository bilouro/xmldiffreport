"""Tests for the renderer strategy/factory."""

from pathlib import Path

import pytest

from xmldiffreport.cli import gather_sources
from xmldiffreport.core import diff_sources, load_recipe, parse_xml
from xmldiffreport.report import DiffReport, get_renderer, list_formats, render

ROOT = Path(__file__).resolve().parents[1]


def _report():
    recipe = load_recipe("controlm")
    sources = [
        (e, lbl, parse_xml(p))
        for e, lbl, p in gather_sources([str(ROOT / "examples" / "controlm")])
    ]
    results = diff_sources(recipe, sources)
    envs = sorted({e for e, _, _ in sources})
    return DiffReport(results, envs, len(sources), "controlm")


def test_formats_registered():
    assert set(list_formats()) >= {"md", "html"}


def test_extensions():
    assert get_renderer("md").file_extension == "md"
    assert get_renderer("html").file_extension == "html"


def test_unknown_format_raises():
    with pytest.raises(ValueError):
        get_renderer("does-not-exist")


def test_markdown_output():
    out = render(_report().results, ["uat", "bench", "prod"], 6, "controlm", "md")
    assert out.startswith("# XML diff report")
    assert "GLX_INGEST_LOAD" in out


def test_html_output_is_standalone_and_escaped():
    out = get_renderer("html").render(_report())
    assert out.startswith("<!doctype html>") and out.rstrip().endswith("</html>")
    assert "<table" in out and "GLX_INGEST_LOAD" in out
    assert 'class="badge CONFLICT"' in out
    # the pipe in the ON "NOTOK|RERUN" key must not break anything (HTML escapes)
    assert "NOTOK|RERUN" in out
