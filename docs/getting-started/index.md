# Installation & Quickstart

## Install

```bash
pip install xmldiffreport
```

Requires **Python 3.11+** (uses the standard-library `tomllib`). The tool has
**no third-party dependencies**.

## Your first diff

The simplest run compares two files you already have — no options, no concepts:

```bash
xmldiffreport old.xml new.xml -o report.md
```

Open `report.md`: a **summary table** of every element that differs, then an
**N-way detail** table — one column per file. Pass more files for more columns.
The exit code is **`1` when a difference is found** (useful in CI), `0` otherwise.

!!! tip "Try it with zero setup"
    Cloned the repo? Run it on the bundled synthetic examples:
    ```bash
    xmldiffreport examples/sitemap/old/sitemap.xml \
                  examples/sitemap/new/sitemap.xml --recipe sitemap
    ```
    The `examples/` folder ships **in the repo**, not in the pip package.

## Inputs: files and/or directories

`xmldiffreport` accepts files and/or directories as positional arguments:

=== "Explicit files"

    ```bash
    xmldiffreport a.xml b.xml c.xml --recipe controlm
    ```

=== "A directory (recursive)"

    ```bash
    xmldiffreport ./dump --recipe controlm
    # every *.xml under ./dump becomes a source, labelled by its path
    ```

=== "A mix"

    ```bash
    xmldiffreport baseline.xml ./candidates --recipe controlm
    ```

Each file is a **source**; a **unit** (e.g. a Control-M `SMART_FOLDER`) is
reported when it appears in **2+ files** and differs. Full guide:
[Inputs & file layout](../guide/inputs.md).

## Choosing a recipe

A **recipe** teaches the engine about one XML dialect. Built-ins:

- `--recipe controlm` — BMC Control-M exports.
- `--recipe maven-pom` — Maven `pom.xml` dependency/plugin drift.
- `--recipe junit` — JUnit/xUnit test reports.
- `--recipe sitemap` — `sitemap.xml`.
- `--recipe generic` — no dialect knowledge (the default).

You can also pass a path to your own `.toml` — see
[Writing recipes](../guide/recipes.md).

## CLI options

```text
xmldiffreport [paths...] [-r RECIPE] [-o OUT] [-f FORMAT]

  paths             .xml files and/or directories (directories scanned recursively)
  -r, --recipe      built-in recipe name or path to a .toml (default: generic)
  -o, --out         output file (default: reports/YYYYMMDD_HH_MM.<ext>)
  -f, --format      output format: md (default) or html
```

## Output formats

The report is rendered through a pluggable strategy, so the same diff can be
emitted in different formats:

```bash
xmldiffreport examples/controlm -r controlm -f html -o report.html
# the format is also inferred from the -o extension (.html → html)
```

Built-in formats: **`md`** (Markdown, default) and **`html`** (a standalone page,
no external assets). Adding more (e.g. JSON) is a single class — see
[Contributing](../contributing.md).

Next: [How it works](../guide/how-it-works.md).
