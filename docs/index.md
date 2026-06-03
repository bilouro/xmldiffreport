# xmldiffreport

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "xmldiffreport",
  "alternateName": ["xml diff report", "N-way XML diff", "structural XML diff"],
  "applicationCategory": "DeveloperApplication",
  "applicationSubCategory": "XML diff & comparison tool",
  "operatingSystem": "Cross-platform",
  "programmingLanguage": "Python",
  "softwareVersion": "0.1.0",
  "license": "https://opensource.org/licenses/MIT",
  "url": "https://bilouro.github.io/xmldiffreport/",
  "downloadUrl": "https://pypi.org/project/xmldiffreport/",
  "codeRepository": "https://github.com/bilouro/xmldiffreport",
  "description": "N-way structural and semantic XML diff that produces human-readable Markdown and HTML reports, driven by per-dialect recipes (Control-M, sitemaps, and more).",
  "author": {
    "@type": "Person",
    "name": "Victor Bilouro",
    "url": "https://github.com/bilouro"
  },
  "keywords": "xml diff, xml compare, structural diff, semantic diff, n-way diff, tree diff, control-m, sitemap, markdown report, html report, python"
}
</script>

[![PyPI version](https://img.shields.io/pypi/v/xmldiffreport.svg?style=flat-square)](https://pypi.org/project/xmldiffreport/)
[![Python versions](https://img.shields.io/pypi/pyversions/xmldiffreport.svg?style=flat-square)](https://pypi.org/project/xmldiffreport/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](https://github.com/bilouro/xmldiffreport/blob/main/LICENSE)

**N-way structural & semantic XML diff that produces human-readable Markdown reports — driven by per-dialect recipes.**

`xmldiffreport` compares **two or more** XML files at once and tells you *what
actually changed* — element by element, attribute by attribute — instead of a
noisy line-by-line text diff. It aligns elements by a **natural key** (not by
position), ignores **volatile attributes**, and writes a clean **Markdown
report**.

It started as a way to detect conflicts between **BMC Control-M** job patches
flowing through `test → uat → bench → prod`, and generalized into a recipe-driven
engine that works on any XML dialect (Control-M exports, sitemaps, POMs, …).

## Quickstart

```bash
pip install xmldiffreport
```

```bash
# Compare two (or more) XML files — uses the generic recipe by default
xmldiffreport old.xml new.xml -o report.md
```

Working with a known dialect (Control-M, sitemaps, …)? Add `--recipe`. Comparing
files organized by environment (`uat/`, `bench/`, `prod/`)? See
[Getting Started](getting-started/index.md) and [Inputs & file layout](guide/inputs.md).

```python
from xmldiffreport import load_recipe, parse_xml, diff_sources, render

recipe = load_recipe("controlm")
sources = [
    ("uat",   "uat:patch-b.xml",   parse_xml("uat/patch-b.xml")),
    ("bench", "bench:patch-a.xml", parse_xml("bench/patch-a.xml")),
    ("prod",  "prod:hotfix-c.xml", parse_xml("prod/hotfix-c.xml")),
]
print(render(diff_sources(recipe, sources), ["uat", "bench", "prod"], 3, "controlm"))
```

## Why not a plain diff?

A text diff on XML lies — volatile attributes (`VERSION`, `CREATION_TIME`,
`JOBISN`), reordered children, and attribute order all create false changes.
`xmldiffreport` is **structural**, **N-way** (3+ files at once), and emits a
review-ready report.

| | xmldiffreport | `xmldiff` | DiffDog / Oxygen | DeltaXML |
|---|---|---|---|---|
| Match by **declared natural key** | ✅ | ❌ | ⚠️ limited | ✅ |
| **N-way** (3+ files) | ✅ | ❌ | ❌ | ❌ |
| **Markdown report** out of the box | ✅ | ❌ | ⚠️ GUI | ❌ |
| Open source | ✅ | ✅ | ❌ | ❌ |

## Next steps

- [Getting Started](getting-started/index.md) — install and run your first diff.
- [How it works](guide/how-it-works.md) — the engine model and conflict rules.
- [Writing recipes](guide/recipes.md) — teach it a new XML dialect.
- [Usage harness](guide/usage.md) — run it on your own environment folders.
- [API Reference](api/index.md) — the library API.
