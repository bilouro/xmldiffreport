# Contributing to xmldiffreport

Thanks for your interest! Contributions of all kinds are welcome — bug reports,
new recipes, docs, and code.

## Project layout

```
src/xmldiffreport/     the installable tool (engine, recipes, CLI)
  core.py              recursive N-way diff engine
  report.py            Markdown renderer
  cli.py               command-line entry point
  recipes/*.toml       per-dialect recipes (controlm, sitemap, generic)
examples/              synthetic datasets + generator (no real data)
usage/                 a config-driven harness to run the tool on your own files
tests/                 pytest suite
```

The **engine is generic**; everything dialect-specific lives in a **recipe**.
Prefer adding a recipe over hard-coding behaviour.

## Development setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Checks (run before opening a PR)

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

Or install the git hooks once: `pre-commit install`.

## Adding a recipe

1. Drop a `<name>.toml` in `src/xmldiffreport/recipes/`.
2. Declare the natural `key` per element, `ignore_attrs`, and (optionally) the
   `unit` and `applied_env`. See `recipes/controlm.toml` for a worked example
   and the README "Key mini-language" section.
3. Add a small synthetic example under `examples/<name>/` and a test.

## Adding an output format

Report formats are a strategy with a registry. Add a class and register it:

```python
from xmldiffreport.report.base import DiffReport, Renderer, register

@register
class JsonRenderer(Renderer):
    format = "json"
    file_extension = "json"
    def render(self, report: DiffReport) -> str:
        ...
```

Import it from `xmldiffreport/report/__init__.py` (for the registration
side-effect) and it becomes available on the CLI (`--format json`) and in the
usage harness.

## Guidelines

- Keep the core small and dependency-free (standard library only).
- New behaviour should be expressible via recipes whenever possible.
- Include tests for new features and bug fixes.
- Examples and tests must use **synthetic** data only — never real exports.

## Commit messages

Conventional, imperative summaries (e.g. `feat: add sitemap recipe`,
`fix: handle empty environment folder`). Keep the subject under ~72 chars.

## Releasing

1. Bump the version in `pyproject.toml`, `src/xmldiffreport/__init__.py`, and the
   `softwareVersion` in `docs/index.md` and `docs/index.pt.md`.
2. Update `CHANGELOG.md` (move items from *Unreleased* into the new version).
3. Commit, then tag: `git tag vX.Y.Z && git push --tags`.
4. The **Release** workflow builds the sdist/wheel and publishes to PyPI via
   Trusted Publishing (configure the publisher on PyPI first). The **Docs**
   workflow redeploys the site on push to `main`.
