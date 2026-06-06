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


def test_sources_shown_as_dir_and_file_not_full_path():
    """Reports label sources as ``parent/file.xml``, not the absolute path."""
    r = _report()
    for fmt in ("md", "html"):
        out = r.render(fmt)
        assert "bench/patch-a.xml" in out  # one directory + file name
        assert str(ROOT) not in out  # never the absolute path


def _envs(tmp_path):
    """Three sources, one file per environment directory (bench/prod/uat)."""
    for envname, mode in (("bench", "a"), ("prod", "b"), ("uat", "c")):
        d = tmp_path / envname
        d.mkdir()
        (d / "export.xml").write_text(
            '<?xml version="1.0"?><DEFTABLE><SMART_FOLDER FOLDER_NAME="GLX">'
            f'<JOB JOBNAME="J" CMDLINE="/run --{mode}" /></SMART_FOLDER></DEFTABLE>',
            encoding="utf-8",
        )
    return [str(tmp_path / e) for e in ("bench", "prod", "uat")]


def test_top_sources_block_and_env_labels(tmp_path):
    """Full paths live once in a top Sources block; per-unit lines use the bold
    `**Sources:**` label with short environment names (the parent dir)."""
    r = diff(_envs(tmp_path), recipe="controlm")

    md = r.render("md")
    assert "## Sources" in md  # top block listing env -> file
    assert "**Sources:** `bench`, `prod`, `uat`" in md  # per-unit, bold, env-only

    html = r.render("html")
    assert "<h2>Sources</h2>" in html
    assert "<strong>Sources:</strong>" in html
    for e in ("bench", "prod", "uat"):
        assert f"<code>{e}</code>" in html


def test_summary_links_to_detail_anchors():
    """Each summary row links to its detail section, which carries the anchor."""
    r = _report()
    n = len(r.units)
    assert n >= 1

    md = r.render("md")
    for i in range(1, n + 1):
        assert f"](#unit-{i})" in md  # summary link
        assert f'<a id="unit-{i}"></a>' in md  # detail anchor

    html = r.render("html")
    for i in range(1, n + 1):
        assert f'href="#unit-{i}"' in html  # summary link
        assert f'id="unit-{i}"' in html  # detail anchor
