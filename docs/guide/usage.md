# Usage harness

The repository separates the **tool** from **your usage**:

```
src/xmldiffreport/   the installable tool (engine, recipes, CLI) — generic
usage/               a config-driven harness to run it on YOUR files
```

The tool in `src/` knows nothing about your folders. The `usage/` folder is the
thin layer you adapt — handy when you'd rather keep paths and output settings in
one file than type them on the command line.

## Configure

```bash
cp usage/config.example.toml usage/config.toml
```

```toml
# usage/config.toml  (paths are relative to this file)
recipe = "controlm"
report_dir = "reports"
format = "md"                # or "html"

# Files and/or directories to compare (directories are scanned recursively).
inputs = [
    "/data/ctm/uat",
    "/data/ctm/bench",
    "/data/ctm/prod",
]
```

## Run

```bash
python usage/collect.py
# writes usage/reports/YYYYMMDD_HH_MM.md
```

`collect.py` collects every `*.xml` across the listed `inputs`, runs the diff,
and writes a timestamped report to `report_dir`. Exit code `1` if anything
differs.

## A typical Control-M workflow

1. Each patch (a JIRA) carries the changed `SMART_FOLDER`s as an XML attachment.
2. Download the attachments into folders (one per source — e.g. `uat/`, `bench/`,
   `prod/`), and list those folders in `inputs`.
3. Run `collect.py` before promoting a patch.
4. The report shows every folder that appears in 2+ files and differs, one column
   per environment (the parent-directory label — full paths are listed once in the
   top Sources block). You know which source is which, so you decide what's a
   collision worth blocking and what's expected.

## Privacy

`usage/config.toml`, `usage/reports/`, and any `*.xml` placed under `usage/` are
**git-ignored** — your real paths and data never get committed.
