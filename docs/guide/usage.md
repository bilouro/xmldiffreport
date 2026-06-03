# Usage harness

The repository separates the **tool** from **your usage**:

```
src/xmldiffreport/   the installable tool (engine, recipes, CLI) — generic
usage/               a config-driven harness to run it on YOUR files
```

The tool in `src/` knows nothing about your folders. The `usage/` folder is the
thin layer you adapt.

## Configure

```bash
cp usage/config.example.toml usage/config.toml
```

```toml
# usage/config.toml  (paths are relative to this file)
recipe = "controlm"
report_dir = "reports"
# applied_env = "prod"   # optional override

[environments]
uat   = "/data/ctm/uat"      # e.g. where you download the Jira attachments
bench = "/data/ctm/bench"
prod  = "/data/ctm/prod"
```

## Run

```bash
python usage/collect.py
# writes usage/reports/YYYYMMDD_HH_MM.md
```

`collect.py` gathers every `*.xml` under each environment folder, runs the diff,
and writes a timestamped report to `report_dir`. Exit code `1` if any conflict.

## A typical Control-M workflow

1. Each patch (a JIRA) carries the changed `SMART_FOLDER`s as an XML attachment.
2. Download the attachments into per-environment folders (`uat/`, `bench/`, …);
   `prod/` holds the recently-applied ones.
3. Run `collect.py` before promoting a patch.
4. Read the report:
    - **⚠️ CONFLICT** — two pending patches touch the same folder/job → resolve
      before promoting.
    - **ℹ️ INFO** — a pending patch overlaps something already in `prod` → confirm
      it was rebased on the current production state.

## Privacy

`usage/config.toml`, `usage/reports/`, and any `*.xml` placed under `usage/` are
**git-ignored** — your real paths and data never get committed.
