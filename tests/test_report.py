"""Tests for the renderer strategy/factory and the high-level API."""

from pathlib import Path

import pytest

from xmldiffreport import diff
from xmldiffreport.report import get_renderer, list_formats

ROOT = Path(__file__).resolve().parents[1]


def _report():
    return diff(str(ROOT / "examples" / "controlm"), recipe="controlm")


def test_formats_registered():
    assert {"md", "html"} <= set(list_formats())


def test_extensions():
    assert get_renderer("md").file_extension == "md"
    assert get_renderer("html").file_extension == "html"


def test_unknown_format_raises():
    with pytest.raises(ValueError):
        get_renderer("does-not-exist")


def test_diffreport_is_truthy_and_has_units():
    r = _report()
    assert bool(r) is True
    assert len(r.units) == 5


def test_markdown_output():
    out = _report().render("md")
    assert out.startswith("# XML diff report")
    assert "GLX_INGEST_LOAD" in out


def test_html_output_is_standalone_and_escaped():
    out = _report().render("html")
    assert out.startswith("<!doctype html>") and out.rstrip().endswith("</html>")
    assert "<table" in out and "GLX_INGEST_LOAD" in out
    # the pipe in the ON "NOTOK|RERUN" key must not break anything (HTML escapes)
    assert "NOTOK|RERUN" in out
