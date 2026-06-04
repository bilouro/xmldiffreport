# Contributing

Contributions are welcome — bug reports, new recipes, docs, and code.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Checks (run before a PR)

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

Or install the hooks once: `pre-commit install`.

## Adding a recipe

1. Drop a `<name>.toml` into `src/xmldiffreport/recipes/`.
2. Declare the natural `key` per element, `ignore_attrs`, and optionally `unit`
   — see [Writing recipes](guide/recipes.md).
3. Add a small **synthetic** example under `examples/<name>/` and a test.

## Adding an output format (beyond Markdown & HTML)

Report formats are a **strategy with a registry**, so a new output is a single
self-contained class — no changes to the engine, the CLI, or the usage harness.
Here is a complete worked example: a **JSON** renderer.

**1. Create `src/xmldiffreport/report/json.py`:**

```python
"""JSON renderer."""
from __future__ import annotations

import json

from .base import DiffReport, Renderer, register


@register
class JsonRenderer(Renderer):
    format = "json"             # the value used by --format / get_renderer
    file_extension = "json"     # used for the default output filename

    def render(self, report: DiffReport) -> str:
        payload = {
            "generated_at": report.generated_at,
            "recipe": report.recipe_name,
            "sources": report.sources,
            "units": [
                {"id": u.ident, "tag": u.tag, "sources": u.sources}
                for u in report.units
            ],
        }
        return json.dumps(payload, indent=2, ensure_ascii=False)
```

**2. Register it** by importing the module for its side-effect in
`src/xmldiffreport/report/__init__.py`:

```python
from . import json as _json  # noqa: F401  (import for @register side-effect)
```

**3. That's it — it's wired everywhere automatically:**

```bash
xmldiffreport examples/controlm -r controlm -f json -o report.json
# the format is also inferred when -o ends in a known extension
```

```python
from xmldiffreport.report import list_formats, get_renderer
list_formats()                       # ['html', 'json', 'md']
get_renderer("json").render(report)
```

**4. Add a test** (`tests/test_report.py`):

```python
def test_json_output_is_valid():
    import json
    out = _report().render("json")
    data = json.loads(out)                      # must parse
    assert data["recipe"] == "controlm"
    assert data["units"]                        # at least one unit differs
```

**5. Document it** — add a line to the README/CHANGELOG and, if it deserves it, a
docs note. Keep the renderer dependency-free (standard library only).

That's the whole contract: subclass `Renderer`, set `format` + `file_extension`,
implement `render(report: DiffReport) -> str`, and `@register` it. The
`DiffReport` you receive carries `units` (a list of `NodeDiff`), `sources` (the
file-path labels), `recipe_name`, and `generated_at`. See the
[API reference](api/index.md) for `NodeDiff`'s shape.

## Guidelines

- Keep the core small and dependency-free (standard library only).
- Prefer expressing new behaviour through a **recipe** over hard-coding it.
- Examples and tests must use **synthetic** data only — never real exports.
- Include tests for new features and fixes.

## Docs

```bash
pip install -e ".[docs]"
mkdocs serve         # live preview at http://127.0.0.1:8000
```

The site is bilingual (English + Português) via `mkdocs-static-i18n`; add a
`*.pt.md` next to a page to translate it.

The full guidelines live in
[`CONTRIBUTING.md`](https://github.com/bilouro/xmldiffreport/blob/main/CONTRIBUTING.md).
