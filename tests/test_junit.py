"""Regression tests for the built-in ``junit`` recipe (synthetic examples)."""

from pathlib import Path

from xmldiffreport import diff

ROOT = Path(__file__).resolve().parents[1]


def _units():
    return diff(str(ROOT / "examples" / "junit"), recipe="junit").units


def _text(units):
    """Every row label that shows up anywhere in the result."""
    out = []
    for u in units:
        stack = [u]
        while stack:
            n = stack.pop()
            out += [lbl for lbl, _ in n.rows]
            out += [f"{tag} {cid}" for tag, cid, _ in n.presence_children]
            stack += n.child_diffs
    return " ".join(out)


def test_junit_units_are_the_suites():
    assert {u.ident for u in _units()} == {
        "com.globex.billing.InvoiceTest",
        "com.globex.billing.LedgerTest",
    }


def test_junit_outcome_transitions_shown():
    text = _text(_units())
    assert "appliesVat" in text and "failure" in text  # pass -> fail
    assert "balancesToZero" in text and "error" in text  # pass -> error
    assert "rejectsNegative" in text and "skipped" in text  # skipped -> pass


def test_junit_added_and_removed_tests():
    text = _text(_units())
    assert "validatesCurrency" in text  # added
    assert "handlesRefund" in text  # removed


def test_junit_ignores_volatile_timing():
    # These cases only differ in `time` (and the suite timestamp/hostname/counts),
    # which are volatile → they must not surface as differences.
    text = _text(_units())
    assert "rendersTotal" not in text
    assert "roundsHalfUp" not in text
    assert "postsEntry" not in text


def test_junit_markdown_escapes_pipe_in_identity():
    # A testcase identity is classname|name; inside a Markdown table cell the pipe
    # must be escaped so the table does not break.
    md = diff(str(ROOT / "examples" / "junit"), recipe="junit").render()
    assert "InvoiceTest\\|appliesVat" in md
