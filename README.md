# xmldiffreport

[![Docs](https://img.shields.io/badge/docs-bilouro.github.io-blue)](https://bilouro.github.io/xmldiffreport/)
[![CI](https://github.com/bilouro/xmldiffreport/actions/workflows/ci.yml/badge.svg)](https://github.com/bilouro/xmldiffreport/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/xmldiffreport.svg)](https://pypi.org/project/xmldiffreport/)
[![Python](https://img.shields.io/pypi/pyversions/xmldiffreport.svg)](https://pypi.org/project/xmldiffreport/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

📖 **Documentation: <https://bilouro.github.io/xmldiffreport/>** · [Português](https://bilouro.github.io/xmldiffreport/pt/)

**N-way structural & semantic XML diff that produces human-readable Markdown reports — driven by per-dialect recipes.**

`xmldiffreport` compares **two or more** XML files at once and tells you *what
actually changed*, element by element and attribute by attribute — not a noisy
line-by-line text diff. It aligns elements by a **natural key** (not by
position), ignores **volatile attributes**, and renders a clean **Markdown
report** with a summary table plus per-element detail.

It was born from a real problem — detecting conflicts between **BMC Control-M**
job patches flowing through `test → uat → bench → prod` — and generalized into a
recipe-driven engine that works on any XML dialect (Control-M exports,
**sitemaps**, POMs, manifests, …).

> Status: early (0.1.0), but already useful. Feedback and recipes welcome.

---

## Why not a normal diff / `xmldiff`?

A plain `diff` (or git diff) on XML lies, for three reasons:

1. **Volatile attributes** — `VERSION`, `CREATION_TIME`, `JOBISN`… change on every export with no functional meaning.
2. **Reordering** — children are often unordered; a reorder is not a change.
3. **Attribute order** inside a tag is irrelevant.

Text/edit-script diffs (like the excellent [`xmldiff`](https://pypi.org/project/xmldiff/))
solve part of this but are **2-way**, **algorithm-matched** (you can't say "match
`<JOB>` by `JOBNAME`"), and output an edit script rather than a review-friendly report.

| | xmldiffreport | xmldiff | DiffDog / Oxygen | DeltaXML |
|---|---|---|---|---|
| Match by **declared natural key** | ✅ | ❌ | ⚠️ limited | ✅ |
| **N-way** (3+ files at once) | ✅ | ❌ | ❌ | ❌ |
| **Markdown report** out of the box | ✅ | ❌ (edit script) | ⚠️ GUI | ❌ (delta XML) |
| Open source | ✅ | ✅ | ❌ | ❌ |

**When to use which** — choose `xmldiffreport` for **N-way**, key-aligned,
report-first comparison (e.g. "the same folder in uat, bench and prod"); reach
for `xmldiff` to produce a **patch/edit script**, DiffDog/Oxygen for **interactive
2-way merging**, DeltaXML for **heuristic matching of keyless documents**, and
`git diff` for **raw line changes** on already-normalized XML. Full breakdown:
[How it compares](https://bilouro.github.io/xmldiffreport/comparison/).

---

## Install

```bash
pip install xmldiffreport
```

Requires Python 3.11+ (uses the standard-library `tomllib`). **No third-party dependencies.**

## Quickstart

```bash
# Compare Control-M patches spread across environment folders
xmldiffreport examples/controlm --recipe controlm -o report.md

# Compare two sitemaps (identity by <loc>, values in element text)
xmldiffreport examples/sitemap --recipe sitemap -o sitemap.md

# Ad-hoc: just a few files with the generic recipe
xmldiffreport a.xml b.xml c.xml -o out.md

# Same diff, HTML report (a standalone page) — format also inferred from .html
xmldiffreport examples/controlm --recipe controlm -f html -o report.html
```

The report format is a **pluggable strategy** — `md` (default) and `html` ship
today; adding another (e.g. JSON) is a single registered class. The exit code is
`1` when at least one **conflict** is found (handy for CI), `0` otherwise.

### Input layouts

Mental model: a **source** is an `(environment, file)` pair; a **unit** is the
recipe's `unit` element (e.g. a Control-M `SMART_FOLDER`); the engine compares
each unit across **every source that contains it** (2+).

- **A folder of environment sub-folders** (`environments/uat/*.xml`,
  `environments/bench/*.xml`, …): each sub-folder is an *environment*; every
  `(environment, file)` is a *source*. Sources in the **same** environment are
  also compared (two files in one env can conflict).
- **A single folder of `.xml`**: the folder name is the environment.
- **Explicit files**: `xmldiffreport a.xml b.xml c.xml`.
- **Scattered locations**: map each environment to any path via the
  [usage harness](usage/) `config.toml`.

→ Full, worked guide with directory trees and a complete example:
**[Inputs & file layout](https://bilouro.github.io/xmldiffreport/guide/inputs/)**.

---

## What the report looks like

For each unit (e.g. a Control-M `SMART_FOLDER`) present in **2+ sources** with
differences (names below are from the synthetic `examples/`):

> ### ⚠️ CONFLICT · `GLX_INGEST_DAILY` (SMART_FOLDER)
> Sources: `bench:patch-a.xml`, `uat:patch-b.xml`, `prod:hotfix-c.xml`
>
> **~ JOB `GLX_INGEST_LOAD`**
>
> | Element · attribute | bench:patch-a.xml | uat:patch-b.xml | prod:hotfix-c.xml |
> |---|---|---|---|
> | `CMDLINE` | …`--force` | …`--retry` | …%%P_DATE |
> | `MAXRERUN` | 0 | 5 | 3 |
> | INCOND `GLX_INGEST_STAGE-…_OK` · `AND_OR` | A | O | A |
> | OUTCOND `GLX_INGEST_LOAD-…_OK` · `SIGN` | - | + | + |
> | ON `NOTOK\|RERUN` | − | present | present |

Notice: it's **N-way** (one column per file), it shows **attribute-level**
changes of the *same* element (the `SIGN` flip, the `AND_OR` change), it
collapses identical jobs into a count, and the volatile `VERSION`/`CREATION_TIME`
noise is gone.

---

## Recipes

A **recipe** is a small TOML file that teaches the generic engine about one XML
dialect: the natural key per element, which attributes to ignore, and which
environment is "already applied".

```toml
name = "controlm"
applied_env = "prod"            # pairs involving prod → INFO (not a conflict)

[defaults]
unit = "SMART_FOLDER"           # the unit of comparison
ignore_attrs = ["VERSION", "JOBISN", "CREATION_TIME", "LAST_UPLOAD", "..."]

[elements.JOB]
key = ["@JOBNAME"]

[elements.OUTCOND]
key = ["@NAME"]                 # SIGN / ODATE are compared as attributes

[elements.ON]                   # no clear key → synthesize from CODE + DO actions
key = ["@CODE", "*kinds"]
inline = true                   # treat children as pseudo-attributes
```

### Key mini-language

A `key` is a list of tokens, joined by `|`:

| Token | Meaning |
|---|---|
| `@ATTR` | value of attribute `ATTR` |
| `#text` | the element's own text |
| `*tag` | the element's tag name (use for singletons compared by their text) |
| `child:TAG@ATTR` | attribute of a child element |
| `child:TAG#text` | text of a child element (e.g. sitemap `<loc>`) |
| `*kinds` | summary of child kinds / `DOACTION` actions (for keyless elements like `<ON>`) |

If no key is given, the engine falls back to `@NAME`, then `#text`, then a
composite of all attributes.

### Built-in recipes

- **`controlm`** — BMC Control-M exports (`DEFTABLE → SMART_FOLDER → JOB → INCOND/OUTCOND/QUANTITATIVE/CONTROL/ON`).
- **`sitemap`** — `sitemap.xml` (identity by `<loc>` text; compares `<lastmod>`/`<priority>`/`<changefreq>`).
- **`generic`** — no dialect knowledge (default).

Drop a `.toml` anywhere and pass its path to `--recipe` to add your own dialect.

### Generate & validate a recipe

Don't want to write one by hand? Let an LLM draft it from a sample of your XML:

```bash
xmldiffreport-recipe scaffold sample.xml > prompt.txt   # paste prompt.txt into any LLM
xmldiffreport-recipe validate my-dialect.toml           # check the result (ships a JSON Schema)
```

See [Generate a recipe with an LLM](https://bilouro.github.io/xmldiffreport/guide/recipe-from-llm/).

---

## How conflicts are classified

- A unit present in **≥2 non-applied** sources, with differences → **⚠️ CONFLICT**.
- A unit whose only "other side" is the **applied** environment (`prod`) →
  **ℹ️ INFO** (it changed something already live — check your rebase, but it's not
  a patch-vs-patch collision).
- Same engine, **N-way**: a Control-M folder can be in `uat` + `bench` + `prod`
  simultaneously, and the report shows all three columns at once.

---

## Project layout — tool vs. your usage

```
src/xmldiffreport/     the installable TOOL (engine, recipes, CLI) — generic, reusable
examples/              synthetic datasets + generator (no real data)
usage/                 a config-driven HARNESS to run the tool on YOUR files
tests/                 pytest suite
```

The **tool** in `src/` knows nothing about your folders. The **`usage/`** folder
is the thin layer you adapt: a `config.toml` mapping each environment to a path,
a `report_dir`, and a `collect.py` that gathers the files and writes the report.

```bash
cp usage/config.example.toml usage/config.toml   # then edit the paths
python usage/collect.py                            # writes usage/reports/<timestamp>.md
```

Your `config.toml`, reports, and any XML under `usage/` are git-ignored — real
data and paths never get committed.

---

## Library use

```python
from xmldiffreport import load_recipe, parse_xml, diff_sources, render

recipe = load_recipe("controlm")
sources = [
    ("uat",   "uat:patch-b.xml",   parse_xml("uat/patch-b.xml")),
    ("bench", "bench:patch-a.xml", parse_xml("bench/patch-a.xml")),
    ("prod",  "prod:hotfix-c.xml", parse_xml("prod/hotfix-c.xml")),
]
results = diff_sources(recipe, sources)
print(render(results, ["uat", "bench", "prod"], len(sources), "controlm"))
```

---

## Performance

Each file is parsed once into an in-memory tree (`xml.etree.ElementTree`); the
diff cost is roughly linear in the number of nodes. For typical Control-M exports
(a few MB) it's instant, and it's fine up to the order of tens of MB. It is
**not** designed for gigabyte-scale files — we deliberately favour simple,
maintainable code over incremental/streaming parsing.

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

ruff check . && ruff format --check .
mypy src
pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md). Examples and tests use **synthetic** data
only — never real exports.

## Roadmap

- Report top-level units that exist in only one source (added/removed units).
- JSON report format (Markdown and HTML already ship; formats are pluggable).
- Similarity-based matching fallback for keyless elements.
- More built-in recipes (Maven POM, Android manifest, RSS/Atom, JUnit).

## License

MIT © Victor H. Bilouro — see [LICENSE](LICENSE).
