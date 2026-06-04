"""Markdown renderer (summary table + N-way detail)."""

from __future__ import annotations

from ..core import NodeDiff
from .base import DiffReport, Renderer, register


def md_cell(v: str) -> str:
    v = " ".join(str(v).split()).replace("|", "\\|")
    if len(v) > 90:  # truncate in the middle (keeps suffixes)
        v = v[:43] + " … " + v[-43:]
    return v or "−"


def _table(label_header: str, rows: list, srcs: list[str]) -> list[str]:
    head = [label_header, *srcs]
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(["---"] * len(head)) + "|"]
    for label, vals in rows:
        out.append("| " + " | ".join([label, *(md_cell(vals[s]) for s in srcs)]) + " |")
    return out


def _render_node(nd: NodeDiff, srcs: list[str], depth: int) -> list[str]:
    out: list[str] = []
    bullet = "  " * depth

    if nd.rows:
        head = f"Level `{nd.tag}`" if depth == 0 else "Attributes"
        out += [f"{bullet}**{head}:**", ""]
        out += _table("Element · attribute", nd.rows, srcs)
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
            + ", ".join(f"`{s}`" for s in has)
            + "; missing from "
            + ", ".join(f"`{s}`" for s in missing)
        )
    if nd.presence_children:
        out.append("")

    for child in nd.child_diffs:
        out += [f"{bullet}**~ {child.tag} `{child.ident}`**", ""]
        out += _render_node(child, srcs, depth + 1)
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
    for nd in units:
        parts = []
        if nd.rows:
            parts.append(f"own Δ{len(nd.rows)}")
        if nd.presence_children:
            parts.append(f"± {len(nd.presence_children)}")
        if nd.child_diffs:
            parts.append(f"~ {len(nd.child_diffs)}")
        lines.append(
            f"| `{nd.ident}` ({nd.tag}) | {len(nd.sources)} | {' · '.join(parts) or '—'} |"
        )
    lines.append("")

    lines += ["## Detail", ""]
    for nd in units:
        lines += [
            f"### `{nd.ident}` ({nd.tag})",
            "",
            "Sources: " + ", ".join(f"`{s}`" for s in nd.sources),
            "",
        ]
        lines += _render_node(nd, nd.sources, 0)
    return "\n".join(lines)


@register
class MarkdownRenderer(Renderer):
    format = "md"
    file_extension = "md"

    def render(self, report: DiffReport) -> str:
        return _render(report)
