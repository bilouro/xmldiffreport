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
The exit code is **`1` when a conflict is found** (useful in CI), `0` otherwise.

!!! tip "Try it with zero setup"
    Cloned the repo? Run it on the bundled synthetic examples:
    ```bash
    xmldiffreport examples/sitemap/old/sitemap.xml \
                  examples/sitemap/new/sitemap.xml --recipe sitemap
    ```
    The `examples/` folder ships **in the repo**, not in the pip package.

## Input layouts

`xmldiffreport` accepts files and/or folders as positional arguments:

=== "Environments in sub-folders"

    ```bash
    xmldiffreport ./environments --recipe controlm -o report.md
    # environments/uat/*.xml, environments/bench/*.xml, ...
    ```

    Each sub-folder is an **environment**; each `(environment, file)` is a
    **source**. Two files in the *same* environment are also compared.

=== "A single folder"

    ```bash
    xmldiffreport ./uat --recipe controlm
    # the folder name ("uat") becomes the environment
    ```

=== "Explicit files"

    ```bash
    xmldiffreport a.xml b.xml c.xml --recipe controlm
    ```

## Choosing a recipe

A **recipe** teaches the engine about one XML dialect. Built-ins:

- `--recipe controlm` — BMC Control-M exports.
- `--recipe sitemap` — `sitemap.xml`.
- `--recipe generic` — no dialect knowledge (the default).

You can also pass a path to your own `.toml` — see
[Writing recipes](../guide/recipes.md).

## CLI options

```text
xmldiffreport [paths...] [-r RECIPE] [-o OUT] [-f FORMAT] [--applied-env ENV]

  paths             .xml files or folders (environments in sub-folders)
  -r, --recipe      built-in recipe name or path to a .toml (default: generic)
  -o, --out         output file (default: reports/YYYYMMDD_HH_MM.<ext>)
  -f, --format      output format: md (default) or html
  --applied-env     override the recipe's "already applied" environment (→ INFO)
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
