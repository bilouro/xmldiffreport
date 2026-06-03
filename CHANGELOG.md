# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- Conflict classification driven by an "applied" environment (e.g. `prod` →
  INFO), including intra-environment comparison.
- Synthetic example datasets (Control-M patches, sitemaps) and a config-driven
  usage harness (`usage/`).
- MkDocs (Material) documentation, bilingual (English + Português), deployed to
  GitHub Pages; SEO-ready (JSON-LD, sitemap, robots.txt, social cards).

[Unreleased]: https://github.com/bilouro/xmldiffreport/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/bilouro/xmldiffreport/releases/tag/v0.1.0
