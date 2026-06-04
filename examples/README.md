# examples/

**100% synthetic, fictional data** — no real exports. A made-up company
("GLOBEX", `GLX_*`) with an invented pipeline, used by the docs, the tests, and
for trying the tool out of the box.

## Layout

```
controlm/                 a Control-M-style export split into environments
  test/   patch-d.xml
  uat/    patch-b.xml  patch-e.xml
  bench/  patch-a.xml  patch-x.xml
  prod/   hotfix-c.xml
maven/                    two Maven POMs — old/pom.xml and new/pom.xml
junit/                    two JUnit reports — old/results.xml and new/results.xml
sitemap/                  two sitemap.xml versions (old/ and new/)
build_examples.py         regenerates everything under controlm/
```

## Try it

```bash
xmldiffreport examples/controlm --recipe controlm  -o report.md
xmldiffreport examples/maven    --recipe maven-pom -o maven.md
xmldiffreport examples/junit    --recipe junit     -o junit.md
xmldiffreport examples/sitemap  --recipe sitemap   -o sitemap.md
```

## Scenarios in `controlm/`

The fixtures deliberately exercise every code path:

| Folder | Scenario |
|---|---|
| `GLX_INGEST_DAILY` | 3-way conflict (prod/uat/bench) at job & attribute level |
| `GLX_SUMMARY_DAILY` | 2-way conflict at folder level only |
| `GLX_LEDGER_DAILY` | 2-way conflict: folder **and** a shared job |
| `GLX_PRICING_DAILY` | INFO — a job differs vs `prod` |
| `GLX_RISK_SCAN` | 2-way conflict: one extra folder `INCOND` |
| `GLX_NIGHTLY_START`, `GLX_DISK_CHECK` | clean (no conflict) |

Volatile attributes (`VERSION`, `CREATION_TIME`, `JOBISN`, …) are present on
purpose, so you can confirm they are ignored.

## Scenarios in `maven/` and `junit/`

`maven/` (old vs new POM) exercises a dependency **version bump**, a **scope
change**, an **added** and a **removed** dependency, a `<dependencyManagement>`
bump in its own section, and a build-**plugin** bump. `junit/` (two CI runs)
exercises a **pass→fail**, a **pass→error**, a **skip→pass**, an **added** and a
**removed** test — with all per-run `time` / `timestamp` / `hostname` noise
ignored.

## Regenerate

```bash
python examples/build_examples.py
```

Everything under `controlm/` is generated from code; the `maven/` and `junit/`
samples are hand-written. Please keep examples synthetic — never commit real
exports.
