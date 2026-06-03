"""Standalone HTML renderer (no external assets)."""

from __future__ import annotations

from html import escape

from ..core import NodeDiff
from .base import DiffReport, Renderer, register

_CSS = """
:root { --conf:#c0392b; --info:#2980b9; --diff:#7f8c8d; --line:#e1e4e8; }
* { box-sizing: border-box; }
body { font: 15px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
       color:#24292e; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; }
h1 { margin-bottom: .2rem; }
.meta { color:#586069; font-size:.9rem; margin-bottom:1.5rem; }
h3 { margin-top: 2rem; border-bottom:1px solid var(--line); padding-bottom:.3rem; }
table { border-collapse: collapse; width: 100%; margin:.6rem 0 1.2rem; font-size:.9rem; }
th, td { border:1px solid var(--line); padding:.35rem .55rem; text-align:left;
         vertical-align:top; word-break:break-word; }
th { background:#f6f8fa; }
code { background:#f6f8fa; padding:.05rem .3rem; border-radius:4px;
       font-family: SFMono-Regular,Consolas,monospace; font-size:.85em; }
.badge { display:inline-block; color:#fff; padding:.1rem .5rem; border-radius:10px;
         font-size:.78rem; font-weight:600; }
.badge.CONFLICT{background:var(--conf);} .badge.INFO{background:var(--info);}
.badge.DIFF{background:var(--diff);}
.src { color:#586069; font-size:.85rem; }
.absent { color:#b0b0b0; }
ul.presence { margin:.3rem 0 1rem; } .sub { margin-left:1.2rem; }
""".strip()


def _cell(v: str) -> str:
    s = " ".join(str(v).split())
    if s in ("", "−"):
        return '<span class="absent">−</span>'
    return escape(s)


def _table(header: str, rows: list, srcs: list[str]) -> str:
    head = "".join(f"<th>{escape(h)}</th>" for h in [header, *srcs])
    body = []
    for label, vals in rows:
        cells = "".join(f"<td>{_cell(vals[s])}</td>" for s in srcs)
        body.append(f"<tr><td>{_label(label)}</td>{cells}</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def _label(label: str) -> str:
    # turn markdown `code spans` into <code> and escape the rest
    out, code = [], False
    for part in label.split("`"):
        out.append(f"<code>{escape(part)}</code>" if code else escape(part))
        code = not code
    return "".join(out)


def _node(nd: NodeDiff, srcs: list[str], depth: int) -> list[str]:
    out: list[str] = []
    cls = "sub" if depth else ""
    out.append(f'<div class="{cls}">' if cls else "<div>")

    if nd.rows:
        head = f"Level {escape(nd.tag)}" if depth == 0 else "Attributes"
        out.append(f"<p><strong>{head}:</strong></p>")
        out.append(_table("Element · attribute", nd.rows, srcs))

    total = nd.identical + len(nd.presence_children) + len(nd.child_diffs)
    if total:
        s = f"<strong>Children:</strong> {nd.identical} identical of {total}"
        if nd.child_diffs:
            s += f" · {len(nd.child_diffs)} changed"
        if nd.presence_children:
            s += f" · {len(nd.presence_children)} presence-only"
        out.append(f"<p>{s}</p>")

    if nd.presence_children:
        out.append('<ul class="presence">')
        for ctag, cid, present in nd.presence_children:
            has = ", ".join(f"<code>{escape(s)}</code>" for s in srcs if present[s])
            missing = ", ".join(f"<code>{escape(s)}</code>" for s in srcs if not present[s])
            out.append(
                f"<li><strong>± {escape(ctag)} <code>{escape(cid)}</code></strong>"
                f" — in {has}; missing from {missing}</li>"
            )
        out.append("</ul>")

    for child in nd.child_diffs:
        out.append(
            f"<p><strong>~ {escape(child.tag)} <code>{escape(child.ident)}</code></strong></p>"
        )
        out += _node(child, srcs, depth + 1)

    out.append("</div>")
    return out


def _render(report: DiffReport) -> str:
    results = report.results
    head = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>XML diff report</title>"
        f"<style>{_CSS}</style></head><body>"
    )
    parts = [
        head,
        "<h1>XML diff report</h1>",
        f'<p class="meta">Generated: {escape(report.generated_at)} · recipe: '
        f"<code>{escape(report.recipe_name)}</code> · sources: "
        f"{escape(', '.join(report.envs))} · {report.n_sources} file(s)</p>",
    ]

    if not results:
        parts.append(
            "<p>No shared unit with differences. "
            "<strong>Nothing to report.</strong></p></body></html>"
        )
        return "".join(parts)

    # summary
    parts.append(
        "<h2>Summary</h2><table><thead><tr><th>Unit</th>"
        "<th>Classification</th><th>Sources</th><th>Changes</th></tr></thead><tbody>"
    )
    for r in results:
        nd = r["node"]
        chg = []
        if nd.rows:
            chg.append(f"own Δ{len(nd.rows)}")
        if nd.presence_children:
            chg.append(f"± {len(nd.presence_children)}")
        if nd.child_diffs:
            chg.append(f"~ {len(nd.child_diffs)}")
        parts.append(
            f"<tr><td><code>{escape(nd.ident)}</code> ({escape(nd.tag)})</td>"
            f'<td><span class="badge {r["cls"]}">{r["cls"]}</span></td>'
            f"<td>{len(nd.sources)}</td><td>{escape(' · '.join(chg) or '—')}</td></tr>"
        )
    parts.append("</tbody></table>")

    # detail
    parts.append("<h2>Detail</h2>")
    for r in results:
        nd = r["node"]
        parts.append(
            f'<h3><span class="badge {r["cls"]}">{r["cls"]}</span> '
            f"<code>{escape(nd.ident)}</code> ({escape(nd.tag)})</h3>"
        )
        parts.append(
            '<p class="src">Sources: '
            + ", ".join(f"<code>{escape(s)}</code>" for s in nd.sources)
            + "</p>"
        )
        parts += _node(nd, nd.sources, 0)

    parts.append("</body></html>")
    return "".join(parts)


@register
class HtmlRenderer(Renderer):
    format = "html"
    file_extension = "html"

    def render(self, report: DiffReport) -> str:
        return _render(report)
