"""Markdown renderer (summary table + N-way detail)."""

from __future__ import annotations

from ..core import NodeDiff
from .base import DiffReport, Renderer, register


def md_cell(v: str) -> str:
    # Collapse whitespace (a newline would break the table row) and escape pipes;
    # never truncate — the cell holds the value being compared, so keep it whole.
    v = " ".join(str(v).split()).replace("|", "\\|")
    return v or "−"


def esc_pipe(label: str) -> str:
    """Escape pipes so a composite identity (e.g. ``classname|name``) does not
    split a Markdown table cell. GitHub renders ``\\|`` as a literal ``|`` even
    inside a code span."""
    return label.replace("|", "\\|")


def _table(label_header: str, rows: list, srcs: list[str], disp: dict[str, str]) -> list[str]:
    head = [label_header, *(disp[s] for s in srcs)]
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(["---"] * len(head)) + "|"]
    for label, vals in rows:
        out.append("| " + " | ".join([esc_pipe(label), *(md_cell(vals[s]) for s in srcs)]) + " |")
    return out


def _render_node(nd: NodeDiff, srcs: list[str], depth: int, disp: dict[str, str]) -> list[str]:
    out: list[str] = []
    bullet = "  " * depth

    if nd.rows:
        head = f"Level `{nd.tag}`" if depth == 0 else "Attributes"
        out += [f"{bullet}**{head}:**", ""]
        out += _table("Element · attribute", nd.rows, srcs, disp)
        out.append("")

    total_children = nd.identical + len(nd.presence_children) + len(nd.child_diffs)
    if total_children:
        summary = f"{bullet}**Children:** {nd.identical} identical of {total_children}"
        if nd.child_diffs:
            summary += f" · {len(nd.child_diffs)} changed"
        if nd.presence_children:
            summary += f" · {len(nd.presence_children)} presence-only"
        out += [summary, ""]

    for ctag, cid, present in nd.presence_children:
        has = [s for s in srcs if present[s]]
        missing = [s for s in srcs if not present[s]]
        out.append(
            f"{bullet}- **± {ctag} `{cid}`** — in "
            + ", ".join(f"`{disp[s]}`" for s in has)
            + "; missing from "
            + ", ".join(f"`{disp[s]}`" for s in missing)
        )
    if nd.presence_children:
        out.append("")

    for child in nd.child_diffs:
        out += [f"{bullet}**~ {child.tag} `{child.ident}`**", ""]
        out += _render_node(child, srcs, depth + 1, disp)
    return out


def _render(report: DiffReport) -> str:
    units = report.units
    lines = [
        "# XML diff report",
        "",
        f"_Generated: {report.generated_at} · recipe: `{report.recipe_name}` · "
        f"{len(report.sources)} file(s)_",
        "",
    ]
    if not units:
        lines += ["No shared unit with differences. **Nothing to report.**", ""]
        return "\n".join(lines)

    lines += ["## Summary", "", "| Unit | Sources | Changes |", "|---|---|---|"]
    for i, nd in enumerate(units, 1):
        parts = []
        if nd.rows:
            parts.append(f"own Δ{len(nd.rows)}")
        if nd.presence_children:
            parts.append(f"± {len(nd.presence_children)}")
        if nd.child_diffs:
            parts.append(f"~ {len(nd.child_diffs)}")
        ident = esc_pipe(nd.ident)
        changes = " · ".join(parts) or "—"
        # link to the detail section below (explicit anchor, renderer-independent)
        lines.append(f"| [`{ident}` ({nd.tag})](#unit-{i}) | {len(nd.sources)} | {changes} |")
    lines.append("")

    disp = report.source_display
    lines += ["## Detail", ""]
    for i, nd in enumerate(units, 1):
        lines += [
            f'<a id="unit-{i}"></a>',
            "",
            f"### `{nd.ident}` ({nd.tag})",
            "",
            "Sources: " + ", ".join(f"`{disp[s]}`" for s in nd.sources),
            "",
        ]
        lines += _render_node(nd, nd.sources, 0, disp)
    return "\n".join(lines)


@register
class MarkdownRenderer(Renderer):
    format = "md"
    file_extension = "md"

    def render(self, report: DiffReport) -> str:
        return _render(report)
