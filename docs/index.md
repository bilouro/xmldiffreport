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
  "softwareVersion": "0.3.0",
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
  "keywords": "xml diff, xml compare, structural diff, semantic diff, n-way diff, tree diff, control-m, maven pom diff, junit report diff, sitemap, markdown report, html report, python"
}
</script>

[![PyPI version](https://img.shields.io/pypi/v/xmldiffreport.svg?style=flat-square)](https://pypi.org/project/xmldiffreport/)
[![Python versions](https://img.shields.io/pypi/pyversions/xmldiffreport.svg?style=flat-square)](https://pypi.org/project/xmldiffreport/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](https://github.com/bilouro/xmldiffreport/blob/main/LICENSE)

**N-way structural & semantic XML diff that produces human-readable Markdown reports — driven by per-dialect recipes.**

`xmldiffreport` compares **two or more** XML files at once — **BMC Control-M**
exports, **Maven** POMs, **JUnit/xUnit** reports, **sitemaps**, or any dialect you
teach it with a small recipe — and tells you *what actually changed*, element by
element and attribute by attribute, instead of a noisy line-by-line text diff. It aligns elements by a **natural key** (not by
position), ignores **volatile attributes**, and writes a clean **Markdown
report**.

It started as a way to spot differences between **BMC Control-M** job patches
flowing through `test → uat → bench → prod`, and generalized into a recipe-driven
engine that works on any XML dialect (Control-M exports, Maven POMs, JUnit
reports, sitemaps, …).

## Quickstart

```bash
pip install xmldiffreport
```

```bash
# Compare two (or more) XML files — uses the generic recipe by default
xmldiffreport old.xml new.xml -o report.md
```

Working with a known dialect (Control-M, sitemaps, …)? Add `--recipe`. Pass
**directories** to compare every `*.xml` inside them. See
[Getting Started](getting-started/index.md) and [Inputs & file layout](guide/inputs.md).

```python
from xmldiffreport import diff

result = diff(["old.xml", "new.xml"], recipe="sitemap")   # a file, files, or dir(s)
print(result.render())                                    # Markdown — or .render("html")
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
- [How it works](guide/how-it-works.md) — the engine model and what gets reported.
- [Writing recipes](guide/recipes.md) — teach it a new XML dialect.
- [Usage harness](guide/usage.md) — run it on your own environment folders.
- [API Reference](api/index.md) — the library API.
