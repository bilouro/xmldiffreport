"""Markdown renderer (summary table + N-way detail)."""

from __future__ import annotations

from ..core import ABSENT, NodeDiff
from .base import DiffReport, Renderer, register, row_status


def _value_cell(v: str, outlier: bool) -> str:
    """A value cell in a detail table: backtick-quoted (to preserve whitespace),
    italic ``_absent_`` when the element is missing, bold when it is the outlier."""
    if v == ABSENT:
        return "_absent_"
    val = " ".join(str(v).split()).replace("|", "\\|")
    cell = f"`{val or ' '}`"
    return f"**{cell}**" if outlier else cell


def _num(n: int) -> str:
    """A count for the summary: the number, or en-dash when this kind of change
    does not apply to the row (distinct from a real ``0``)."""
    return str(n) if n else "–"


def esc_pipe(label: str) -> str:
    """Escape pipes so a composite identity (e.g. ``classname|name``) does not
    split a Markdown table cell. GitHub renders ``\\|`` as a literal ``|`` even
    inside a code span."""
    return label.replace("|", "\\|")


def _diff_table(rows: list, srcs: list[str], cols: dict[str, str]) -> list[str]:
    """Detail table: a status column, the element/attribute, then one value
    column per environment."""
    head = ["", "Element / attribute", *(cols[s] for s in srcs)]
    sep = "|" + "|".join([":-:", "---", *(["---"] * len(srcs))]) + "|"
    out = ["| " + " | ".join(head) + " |", sep]
    for label, vals in rows:
        sign, outlier = row_status(vals, srcs)
        cells = [_value_cell(vals[s], s == outlier) for s in srcs]
        out.append("| " + " | ".join([sign, esc_pipe(label), *cells]) + " |")
    return out


def _presence_matrix(children: list, srcs: list[str], cols: dict[str, str]) -> list[str]:
    """Presence-only elements as a matrix (✓ present / — absent), one row per
    element — replaces the old free-text bullet list."""
    out = ["| Element | " + " | ".join(cols[s] for s in srcs) + " |"]
    out.append("|---|" + "|".join([":-:"] * len(srcs)) + "|")
    for ctag, cid, present in children:
        cells = ["✓" if present[s] else "—" for s in srcs]
        out.append(f"| {ctag} `{esc_pipe(cid)}` | " + " | ".join(cells) + " |")
    return out


def _render_node(nd: NodeDiff, srcs: list[str], depth: int, cols: dict[str, str]) -> list[str]:
    out: list[str] = []
    bullet = "  " * depth

    if nd.rows:
        head = f"Level `{nd.tag}`" if depth == 0 else "Attributes"
        out += [f"{bullet}**{head}:**", ""]
        out += _diff_table(nd.rows, srcs, cols)
        out.append("")

    total_children = nd.identical + len(nd.presence_children) + len(nd.child_diffs)
    if total_children:
        summary = f"{bullet}**Children:** {nd.identical} identical of {total_children}"
        if nd.child_diffs:
            summary += f" · {len(nd.child_diffs)} changed"
        if nd.presence_children:
            summary += f" · {len(nd.presence_children)} presence-only"
        out += [summary, ""]

    if nd.presence_children:
        out += [f"{bullet}**Presence:**", ""]
        out += _presence_matrix(nd.presence_children, srcs, cols)
        out.append("")

    for child in nd.child_diffs:
        out += [f"{bullet}**~ {child.tag} `{child.ident}`**", ""]
        out += _render_node(child, srcs, depth + 1, cols)
    return out


def _render(report: DiffReport) -> str:
    units = report.units
    env = report.source_env
    disp = report.source_display
    lines = [
        "# XML diff report",
        "",
        f"_Generated: {report.generated_at} · recipe: `{report.recipe_name}` · "
        f"{len(report.sources)} file(s)_",
        "",
        "## Sources",
        "",
    ]
    # env label -> full file path, listed once here so the tables can stay narrow
    for s in report.sources:
        lines.append(f"- `{env[s]}` — `{disp[s]}`")
    lines.append("")
    if not units:
        lines += ["No shared unit with differences. **Nothing to report.**", ""]
        return "\n".join(lines)

    lines += [
        "## Summary",
        "",
        "| Unit | Sources | Own | Presence | Changed |",
        "|---|---:|---:|---:|---:|",
    ]
    tot_src = tot_own = tot_pres = tot_chg = 0
    for i, nd in enumerate(units, 1):
        own, pres, chg = len(nd.rows), len(nd.presence_children), len(nd.child_diffs)
        tot_src += len(nd.sources)
        tot_own += own
        tot_pres += pres
        tot_chg += chg
        ident = esc_pipe(nd.ident)
        # the Unit cell links to the detail section below (explicit anchor)
        lines.append(
            f"| [`{ident}` ({nd.tag})](#unit-{i}) | {len(nd.sources)} "
            f"| {_num(own)} | {_num(pres)} | {_num(chg)} |"
        )
    if len(units) > 5:
        lines.append(
            f"| **Total** | **{tot_src}** | {_num(tot_own)} | {_num(tot_pres)} | {_num(tot_chg)} |"
        )
    lines.append("")

    lines += ["## Detail", ""]
    for i, nd in enumerate(units, 1):
        lines += [
            f'<a id="unit-{i}"></a>',
            "",
            f"### `{nd.ident}` ({nd.tag})",
            "",
            "**Sources:** " + ", ".join(f"`{env[s]}`" for s in nd.sources),
            "",
        ]
        lines += _render_node(nd, nd.sources, 0, env)
    return "\n".join(lines)


@register
class MarkdownRenderer(Renderer):
    format = "md"
    file_extension = "md"

    def render(self, report: DiffReport) -> str:
        return _render(report)
