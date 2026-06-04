# usage/ — running xmldiffreport on your own files

This folder is **not** part of the published package. It's a thin, config-driven
wrapper that runs the tool on *your* inputs and writes a report — so you can keep
your paths and output settings in one place.

## Quick start

```bash
cp usage/config.example.toml usage/config.toml
python usage/collect.py
```

Out of the box `config.toml` points at the synthetic examples, so it runs
immediately and writes a report to `usage/reports/`.

## Point it at your data

Edit `usage/config.toml`:

```toml
recipe = "controlm"
report_dir = "reports"
format = "md"            # or "html"

# Files and/or directories (directories are scanned recursively for *.xml).
inputs = [
    "/data/ctm/uat",
    "/data/ctm/bench",
    "/data/ctm/prod",
]
```

- Every `*.xml` found across the listed inputs becomes one **source**, labelled
  by its file path.
- A **unit** (e.g. a Control-M `SMART_FOLDER`) is reported when it appears in two
  or more sources and differs. Sources that are unique to one file are ignored.
- That's it — the tool has no notion of "environments". If you care which file
  came from production, name it accordingly; the path shows up in the report.

## Privacy

`config.toml`, `usage/reports/`, and any `*.xml` you drop under `usage/` are
git-ignored — your real paths and data never get committed.
