"""Standalone HTML renderer (no external assets)."""

from __future__ import annotations

from html import escape

from ..core import NodeDiff
from .base import DiffReport, Renderer, register

_CSS = """
:root { --line:#e1e4e8; }
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
.src { color:#586069; font-size:.85rem; }
.absent { color:#b0b0b0; }
ul.presence { margin:.3rem 0 1rem; } .sub { margin-left:1.2rem; }
a { color:#0366d6; text-decoration:none; } a:hover { text-decoration:underline; }
td.num, th.num { text-align:right; } tfoot td { font-weight:600; border-top:2px solid #d0d7de; }
""".strip()


def _cell(v: str) -> str:
    s = " ".join(str(v).split())
    if s in ("", "−"):
        return '<span class="absent">−</span>'
    return escape(s)


def _num(n: int) -> str:
    """A summary count: the number, or en-dash when this kind of change does not
    apply to the row (distinct from a real ``0``)."""
    return str(n) if n else "–"


def _table(header: str, rows: list, srcs: list[str], cols: dict[str, str]) -> str:
    head = "".join(f"<th>{escape(h)}</th>" for h in [header, *(cols[s] for s in srcs)])
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


def _node(nd: NodeDiff, srcs: list[str], depth: int, cols: dict[str, str]) -> list[str]:
    out: list[str] = []
    cls = "sub" if depth else ""
    out.append(f'<div class="{cls}">' if cls else "<div>")

    if nd.rows:
        head = f"Level {escape(nd.tag)}" if depth == 0 else "Attributes"
        out.append(f"<p><strong>{head}:</strong></p>")
        out.append(_table("Element / attribute", nd.rows, srcs, cols))

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
            has = ", ".join(f"<code>{escape(cols[s])}</code>" for s in srcs if present[s])
            missing = ", ".join(f"<code>{escape(cols[s])}</code>" for s in srcs if not present[s])
            out.append(
                f"<li><strong>± {escape(ctag)} <code>{escape(cid)}</code></strong>"
                f" — in {has}; missing from {missing}</li>"
            )
        out.append("</ul>")

    for child in nd.child_diffs:
        out.append(
            f"<p><strong>~ {escape(child.tag)} <code>{escape(child.ident)}</code></strong></p>"
        )
        out += _node(child, srcs, depth + 1, cols)

    out.append("</div>")
    return out


def _render(report: DiffReport) -> str:
    units = report.units
    head = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>XML diff report</title>"
        f"<style>{_CSS}</style></head><body>"
    )
    env = report.source_env
    disp = report.source_display
    parts = [
        head,
        "<h1>XML diff report</h1>",
        f'<p class="meta">Generated: {escape(report.generated_at)} · recipe: '
        f"<code>{escape(report.recipe_name)}</code> · "
        f"{len(report.sources)} file(s)</p>",
    ]

    # env label -> full file path, listed once so the diff tables can stay narrow
    parts.append('<h2>Sources</h2><ul class="src">')
    for s in report.sources:
        parts.append(f"<li><code>{escape(env[s])}</code> — <code>{escape(disp[s])}</code></li>")
    parts.append("</ul>")

    if not units:
        parts.append(
            "<p>No shared unit with differences. "
            "<strong>Nothing to report.</strong></p></body></html>"
        )
        return "".join(parts)

    # summary — one column per change type
    parts.append(
        "<h2>Summary</h2><table><thead><tr><th>Unit</th>"
        '<th class="num">Sources</th><th class="num">Own</th>'
        '<th class="num">Presence</th><th class="num">Changed</th></tr></thead><tbody>'
    )
    tot_src = tot_own = tot_pres = tot_chg = 0
    for i, nd in enumerate(units, 1):
        own, pres, chg = len(nd.rows), len(nd.presence_children), len(nd.child_diffs)
        tot_src += len(nd.sources)
        tot_own += own
        tot_pres += pres
        tot_chg += chg
        parts.append(
            f'<tr><td><a href="#unit-{i}"><code>{escape(nd.ident)}</code> '
            f"({escape(nd.tag)})</a></td>"
            f'<td class="num">{len(nd.sources)}</td>'
            f'<td class="num">{_num(own)}</td>'
            f'<td class="num">{_num(pres)}</td>'
            f'<td class="num">{_num(chg)}</td></tr>'
        )
    parts.append("</tbody>")
    if len(units) > 5:
        parts.append(
            "<tfoot><tr><td>Total</td>"
            f'<td class="num">{tot_src}</td>'
            f'<td class="num">{_num(tot_own)}</td>'
            f'<td class="num">{_num(tot_pres)}</td>'
            f'<td class="num">{_num(tot_chg)}</td></tr></tfoot>'
        )
    parts.append("</table>")

    # detail
    parts.append("<h2>Detail</h2>")
    for i, nd in enumerate(units, 1):
        parts.append(f'<h3 id="unit-{i}"><code>{escape(nd.ident)}</code> ({escape(nd.tag)})</h3>')
        parts.append(
            '<p class="src"><strong>Sources:</strong> '
            + ", ".join(f"<code>{escape(env[s])}</code>" for s in nd.sources)
            + "</p>"
        )
        parts += _node(nd, nd.sources, 0, env)

    parts.append("</body></html>")
    return "".join(parts)


@register
class HtmlRenderer(Renderer):
    format = "html"
    file_extension = "html"

    def render(self, report: DiffReport) -> str:
        return _render(report)
