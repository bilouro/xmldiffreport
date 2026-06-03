"""Regression tests using the synthetic examples."""

from pathlib import Path

from xmldiffreport.cli import gather_sources
from xmldiffreport.core import diff_sources, load_recipe, parse_xml

ROOT = Path(__file__).resolve().parents[1]


def _run(recipe_name, example_dir):
    recipe = load_recipe(recipe_name)
    sources = [
        (env, label, parse_xml(p))
        for env, label, p in gather_sources([str(ROOT / "examples" / example_dir)])
    ]
    return diff_sources(recipe, sources)


def _all_row_labels(node):
    labels = [lbl for lbl, _ in node.rows]
    for child in node.child_diffs:
        labels += _all_row_labels(child)
    return labels


def test_controlm_counts_and_classification():
    results = _run("controlm", "controlm")
    conflicts = [r for r in results if r["conflict"]]
    infos = [r for r in results if not r["conflict"]]
    assert len(results) == 5
    assert len(conflicts) == 4 and len(infos) == 1

    # N-way: exactly one unit is present in 3 sources, and it is a conflict
    threeway = [r for r in results if len(r["node"].sources) == 3]
    assert len(threeway) == 1 and threeway[0]["conflict"]

    # the INFO one (involving prod) has 2 sources
    assert len(infos[0]["node"].sources) == 2 and infos[0]["cls"] == "INFO"


def test_controlm_ignores_volatile():
    """Changing only VERSION/CREATION_TIME/JOBISN must not create differences."""
    for r in _run("controlm", "controlm"):
        labels = _all_row_labels(r["node"])
        assert not any(
            tok in lbl
            for lbl in labels
            for tok in ("VERSION", "CREATION", "JOBISN", "LAST_UPLOAD")
        )


def test_controlm_attribute_level_diff():
    """An attribute of an existing element (e.g. an OUTCOND SIGN) must show up."""
    results = _run("controlm", "controlm")
    all_labels = [lbl for r in results for lbl in _all_row_labels(r["node"])]
    assert any("· `SIGN`" in lbl for lbl in all_labels)


def test_sitemap_text_and_namespace():
    """Sitemap: identity by <loc>, diffs in <lastmod>/<priority> text."""
    results = _run("sitemap", "sitemap")
    ids = {r["node"].ident for r in results}
    assert "https://example.com/" in ids
    all_labels = [lbl for r in results for lbl in _all_row_labels(r["node"])]
    assert any("(text)" in lbl for lbl in all_labels)
