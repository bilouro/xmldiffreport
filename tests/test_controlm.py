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


def test_sitemap_text_and_namespace():
    """Sitemap: identity by <loc>, diffs in <lastmod>/<priority> text."""
    units = _units("sitemap", "sitemap")
    ids = {u.ident for u in units}
    assert "https://example.com/" in ids
    labels = [lbl for u in units for lbl in _all_row_labels(u)]
    assert any("(text)" in lbl for lbl in labels)
