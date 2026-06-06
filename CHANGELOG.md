# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.1] - 2026-06-06

### Changed
- Documentation now lives at the custom domain **https://xmldiffreport.bilouro.com/**
  (the old `bilouro.github.io/xmldiffreport/` URL 301-redirects). Project metadata
  was updated to match: the PyPI `Documentation` link and the recipe schema `$id`.

## [0.4.0] - 2026-06-06

The report output was redesigned for readability. **This changes the Markdown
and HTML structure** — downstream tools that parse the previous format may need
updating.

### Added
- A top **Sources** block lists each source once (short environment label → full
  path); diff-table columns now use the short label instead of the full path.
- The **Summary** has one column per change type — Own / Presence / Changed —
  right-aligned, with an en-dash for "not applicable" (distinct from a real 0)
  and a Total row once there are more than five units.
- **Detail** tables gained a status column: `≠` changed, `⊘` present in some,
  `±` only one source; the lone diverging value is highlighted (bold in Markdown,
  red in HTML) and missing values render as italic _absent_.
- Presence-only children are shown as a ✓ / — matrix instead of free-text
  bullets; the HTML report additionally tints detail rows by status.

### Changed
- Project maturity raised to **Beta** (`Development Status :: 4 - Beta`).
- The first detail-table column header is `Element / attribute` (plain slash).

## [0.3.2] - 2026-06-05

### Added
- Summary rows in the Markdown and HTML reports now link to the matching detail
  section (stable `unit-N` anchors), so an impacted unit can be opened directly
  from the summary instead of scrolling.

## [0.3.1] - 2026-06-05

### Added
- `defaults.unit` may now be a **list of tags**, not only a single tag.
  Validation and the JSON schema accept both forms. The built-in `controlm`
  recipe uses this to match both `<FOLDER>` and `<SMART_FOLDER>`, so exports
  that use plain `<FOLDER>` are no longer reported as having no differences.

### Changed
- Reports label each source as `parentdir/file.xml` instead of the full (often
  absolute) input path, expanding to more path components only when two sources
  would otherwise collide.

### Fixed
- Actions inside a Control-M `<ON>` (e.g. `DOMAIL`, `DOOUTPUT`) are now compared
  order-independently, and repeated same-tag actions are no longer overwritten —
  jobs that differ only in action order are no longer reported as changed.
- The Markdown report no longer truncates long cell values with an ellipsis,
  which could hide the very text that differed between sources.

## [0.3.0] - 2026-06-04

### Added
- `xmldiffreport-recipe show <name|recipe.toml>` — print a built-in recipe (by
  name) or any recipe file (by path), comments included, to read or copy as a
  starting point without digging into `site-packages`.

## [0.2.0] - 2026-06-04

### Added
- Built-in **`maven-pom`** recipe — Maven `pom.xml` dependency & plugin drift:
  `<dependency>` / `<plugin>` keyed by coordinates
  (`groupId:artifactId[:type:classifier]`), reporting version/scope changes and
  added/removed entries across `<dependencies>`, `<dependencyManagement>` and
  `<build>`. Ships with a synthetic example and tests.
- Built-in **`junit`** recipe — JUnit/xUnit test reports (Surefire, Gradle,
  pytest, …): `testsuite` by `@name`, `testcase` by `classname`+`name` (inline),
  surfacing pass↔fail↔skip transitions and added/removed tests while ignoring
  volatile `time` / `timestamp` / `hostname` and the roll-up counters. Ships with
  a synthetic example and tests.

### Fixed
- Markdown renderer escapes `|` in row and identity labels (e.g. a JUnit
  `classname|name`), so composite identities no longer break table cells.

## [0.1.0] - 2026-06-03

Initial release.

### Added
- N-way, recipe-driven structural & semantic XML diff engine
  (`xmldiffreport.core`): natural-key alignment (order-independent), volatile
  attribute filtering, inline elements, attribute-level and presence diffs.
- Pluggable report formats via a strategy/factory (`xmldiffreport.report`):
  built-in **Markdown** and **HTML** renderers, selectable with `--format`
  (also inferred from the `-o` extension). New formats are a single
  `@register`ed `Renderer` subclass.
- Command-line interface (`xmldiffreport`) and a typed library API.
- Built-in recipes — `controlm`, `sitemap`, `generic` — plus a TOML
  "key mini-language" for custom dialects.
- Recipe tooling (`xmldiffreport-recipe`): `scaffold` prints an LLM prompt that
  generates a recipe from a sample XML; `validate` checks a recipe against the
  shipped JSON Schema (`recipes/recipe.schema.json`). Dependency-free validator.
- High-level API: `diff(paths, recipe=...)` accepts a file, multiple files, and/or
  directories (scanned recursively) and returns a `DiffReport` you can `.render()`.
  The engine is generic — no notion of "environments".
- Synthetic example datasets (Control-M patches, sitemaps) and a config-driven
  usage harness (`usage/`).
- MkDocs (Material) documentation, bilingual (English + Português), deployed to
  GitHub Pages; SEO-ready (JSON-LD, sitemap, robots.txt, social cards).

[Unreleased]: https://github.com/bilouro/xmldiffreport/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/bilouro/xmldiffreport/releases/tag/v0.3.0
[0.2.0]: https://github.com/bilouro/xmldiffreport/releases/tag/v0.2.0
[0.1.0]: https://github.com/bilouro/xmldiffreport/releases/tag/v0.1.0
