"""Regression tests using the synthetic examples."""

from pathlib import Path

from xmldiffreport import diff

ROOT = Path(__file__).resolve().parents[1]


def _units(recipe_name, example_dir):
    return diff(str(ROOT / "examples" / example_dir), recipe=recipe_name).units


def _all_row_labels(node):
    labels = [lbl for lbl, _ in node.rows]
    for child in node.child_diffs:
        labels += _all_row_labels(child)
    return labels


def test_controlm_counts():
    units = _units("controlm", "controlm")
    assert len(units) == 5  # the 5 folders that differ across the patches

    # N-way: exactly one unit is present in 3 sources
    threeway = [u for u in units if len(u.sources) == 3]
    assert len(threeway) == 1


def test_controlm_ignores_volatile():
    """Changing only VERSION/CREATION_TIME/JOBISN must not create differences."""
    for u in _units("controlm", "controlm"):
        labels = _all_row_labels(u)
        assert not any(
            tok in lbl
            for lbl in labels
            for tok in ("VERSION", "CREATION", "JOBISN", "LAST_UPLOAD")
        )


def test_controlm_attribute_level_diff():
    """An attribute of an existing element (e.g. an OUTCOND SIGN) must show up."""
    labels = [lbl for u in _units("controlm", "controlm") for lbl in _all_row_labels(u)]
    assert any("· `SIGN`" in lbl for lbl in labels)


def _write_on_job(path, actions):
    """Write a minimal Control-M export whose single JOB has one <ON> wrapping
    the given action elements (in the given order)."""
    path.write_text(
        '<?xml version="1.0"?><DEFTABLE><SMART_FOLDER FOLDER_NAME="GLX_ALERTS">'
        '<JOB JOBNAME="GLX_NOTIFY" CMDLINE="/x"><ON STMT="*" CODE="NOTOK" AND_OR="A">'
        + "".join(actions)
        + "</ON></JOB></SMART_FOLDER></DEFTABLE>",
        encoding="utf-8",
    )


_DOMAIL_P = '<DOMAIL DEST="oncall@glx" SUBJECT="primary" MESSAGE="primary on-call message" />'
_DOMAIL_A = '<DOMAIL DEST="audit@glx" SUBJECT="audit" MESSAGE="audit trail message" />'
_DOOUTPUT = '<DOOUTPUT OPTION="Copy" PAR="/opt/glx/logs/x" />'


def test_on_children_are_order_independent(tmp_path):
    """Reordering the actions inside an <ON> must not create a difference:
    neither across tags (DOMAIL/DOOUTPUT) nor for repeated tags (two DOMAIL)."""
    for actions_c in ([_DOOUTPUT, _DOMAIL_P], [_DOMAIL_A, _DOMAIL_P]):
        ordered = [_DOMAIL_P, _DOOUTPUT] if _DOOUTPUT in actions_c else [_DOMAIL_P, _DOMAIL_A]
        for name in ("a", "b"):
            (tmp_path / name).mkdir(exist_ok=True)
            _write_on_job(tmp_path / name / "export.xml", ordered)
        (tmp_path / "c").mkdir(exist_ok=True)
        _write_on_job(tmp_path / "c" / "export.xml", actions_c)
        units = diff([str(tmp_path / d) for d in ("a", "b", "c")], recipe="controlm").units
        assert units == []


def test_on_repeated_child_is_not_lost(tmp_path):
    """A second same-tag action must not be overwritten: dropping one of two
    <DOMAIL> actions is a real difference and must be reported."""
    for name in ("a", "b"):
        (tmp_path / name).mkdir()
        _write_on_job(tmp_path / name / "export.xml", [_DOMAIL_P, _DOMAIL_A])
    (tmp_path / "c").mkdir()
    _write_on_job(tmp_path / "c" / "export.xml", [_DOMAIL_P])  # audit mail removed
    units = diff([str(tmp_path / d) for d in ("a", "b", "c")], recipe="controlm").units
    assert len(units) == 1


def test_sitemap_text_and_namespace():
    """Sitemap: identity by <loc>, diffs in <lastmod>/<priority> text."""
    units = _units("sitemap", "sitemap")
    ids = {u.ident for u in units}
    assert "https://example.com/" in ids
    labels = [lbl for u in units for lbl in _all_row_labels(u)]
    assert any("(text)" in lbl for lbl in labels)
