# usage/ — running xmldiffreport on your own files

This folder is **not** part of the published package. It's a thin, config-driven
harness that shows how to point the (reusable) tool at *your* environments and
collect a report — keeping the engine in `src/` generic.

## Quick start

```bash
# from the repo root, with the package importable (pip install -e . or dev mode)
cp usage/config.example.toml usage/config.toml
python usage/collect.py
```

Out of the box `config.toml` points at the synthetic examples, so it runs
immediately and writes a report to `usage/reports/`.

## Point it at your data

Edit `usage/config.toml` and map each environment to the folder that holds its
XML patches (for example, the directory where you download the Jira attachments
for that environment):

```toml
recipe = "controlm"
report_dir = "reports"

[environments]
uat   = "/data/ctm/uat"
bench = "/data/ctm/bench"
prod  = "/data/ctm/prod"
```

- Each `(environment, file)` is a *source*; two files in the **same** environment
  are also compared (intra-environment conflicts).
- The environment named `prod` (configurable via the recipe / `applied_env`) is
  treated as *already applied* → overlaps with it are reported as **INFO**, not
  conflicts.
- Reports land in `report_dir` as `YYYYMMDD_HH_MM.md`.

## Privacy

`config.toml`, `usage/reports/`, and any `*.xml` you drop under `usage/` are
git-ignored — your real data and paths never get committed.
