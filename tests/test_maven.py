"""Regression tests for the built-in ``maven-pom`` recipe (synthetic examples)."""

from pathlib import Path

from xmldiffreport import diff

ROOT = Path(__file__).resolve().parents[1]


def _units():
    return diff(str(ROOT / "examples" / "maven"), recipe="maven-pom").units


def _rows(node):
    """All (label, values) rows of a unit and its nested child diffs."""
    rows = list(node.rows)
    for child in node.child_diffs:
        rows += _rows(child)
    return rows


def _text(units):
    """Every label / presence identity that shows up anywhere in the result."""
    out = []
    for u in units:
        stack = [u]
        while stack:
            n = stack.pop()
            out += [lbl for lbl, _ in n.rows]
            out += [f"{tag} {cid}" for tag, cid, _ in n.presence_children]
            stack += n.child_diffs
    return " ".join(out)


def test_maven_units_are_the_sections():
    # No `unit` in the recipe → the <project> sections are the units. Only the
    # sections that actually changed are reported.
    assert {u.ident for u in _units()} == {"dependencies", "dependencyManagement", "build"}


def test_maven_version_bump_shown():
    rows = [(lbl, vals) for u in _units() for lbl, vals in _rows(u)]
    version_values = [set(v.values()) for lbl, v in rows if "version" in lbl]
    assert {"2.15.2", "2.16.1"} in version_values  # jackson-databind bump
    assert {"5.10.0", "5.10.1"} in version_values  # junit-jupiter bump


def test_maven_management_section_is_separate_unit():
    # The same kind of coordinate can live in both <dependencies> and
    # <dependencyManagement>; they must not collide. The mgmt bom bump shows up
    # under its own unit.
    dm = next(u for u in _units() if u.ident == "dependencyManagement")
    assert any({"2.16.0", "2.16.1"} == set(v.values()) for _, v in _rows(dm))


def test_maven_added_and_removed_dependencies():
    deps = next(u for u in _units() if u.ident == "dependencies")
    presence = {cid for _, cid, _ in deps.presence_children}
    assert "com.globex.commons|globex-metrics" in presence  # added
    assert "org.apache.commons|commons-lang3" in presence  # removed


def test_maven_unchanged_artifacts_are_silent():
    text = _text(_units())
    assert "slf4j" not in text  # identical dependency
    assert "maven-compiler-plugin" not in text  # identical plugin
    assert "java.version" not in text  # identical property
