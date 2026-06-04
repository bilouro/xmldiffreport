# Writing recipes

A **recipe** is a small TOML file that teaches the generic engine about one XML
dialect. The engine stays the same; everything dialect-specific lives here.

!!! tip "Let an LLM draft it"
    You can generate a first recipe from a sample of your XML — see
    [Generate a recipe with an LLM](recipe-from-llm.md).

## Anatomy

```toml
name = "controlm"

[defaults]
unit = "SMART_FOLDER"           # the unit of comparison (default: root children)
unordered = true                # children matched by key, not by order
ignore_attrs = [                # volatile attributes never produce a diff
    "VERSION", "JOBISN", "CREATION_TIME", "LAST_UPLOAD", "..."
]

[elements.JOB]
key = ["@JOBNAME"]

[elements.OUTCOND]
key = ["@NAME"]                 # ODATE / SIGN are compared as attributes

[elements.ON]                   # no clear key → synthesize one
key = ["@CODE", "*kinds"]
inline = true                   # treat children (DOACTION, …) as pseudo-attributes
```

## The key mini-language

A `key` is a list of tokens, joined with `|`. The first non-empty combination
identifies the element among its siblings.

| Token | Meaning |
|---|---|
| `@ATTR` | value of attribute `ATTR` |
| `#text` | the element's own text |
| `*tag` | the element's tag name (use for **singletons** compared by their text) |
| `child:TAG@ATTR` | an attribute of a child element |
| `child:TAG#text` | the text of a child element (e.g. sitemap `<loc>`) |
| `*kinds` | a summary of child kinds / `DOACTION` actions (for keyless elements like `<ON>`) |

If a tag has **no** entry, the engine falls back to `@NAME`, then `#text`, then a
composite of all attributes.

### Examples

```toml
# A condition keyed by NAME; its other attributes are compared
[elements.INCOND]
key = ["@NAME"]                 # ODATE, AND_OR become comparable attributes

# A sitemap <url> identified by the text of its <loc> child
[elements.url]
key = ["child:loc#text"]

# Singletons compared by their text value (identity = the tag itself)
[elements.lastmod]
key = ["*tag"]

# An <ON STMT="*" CODE="NOTOK"> block with no stable key → use CODE + actions
[elements.ON]
key = ["@CODE", "*kinds"]       # e.g. "NOTOK|RERUN"
inline = true
```

## `inline` elements

Some elements (like Control-M's `<ON>`) carry their meaning in their children
(`DOACTION`, `DOMAIL`, `DOOUTPUT`). Marking them `inline = true` folds those
children into pseudo-attributes, so a change like *“the RERUN action was
removed”* shows up as a single row instead of a nested sub-section.

## Built-in recipes

=== "controlm"

    BMC Control-M exports: `DEFTABLE → SMART_FOLDER → JOB → INCOND / OUTCOND /
    QUANTITATIVE / CONTROL / ON`. Unit = `SMART_FOLDER`, with a broad
    `ignore_attrs` list for version/creation metadata.

=== "maven-pom"

    Maven `pom.xml`: dependency & plugin drift. A `<dependency>` / `<plugin>` is
    keyed by its coordinates (`groupId:artifactId[:type:classifier]`), so the diff
    reports **version/scope changes** and **added/removed** entries across
    `<dependencies>`, `<dependencyManagement>` and `<build>`, order-independent.
    (No `unit` is set: the POM sections are the units — this keeps the same
    coordinate appearing in both `<dependencies>` and `<dependencyManagement>`
    from colliding, and lets add/remove surface as a presence change.)

=== "junit"

    JUnit / xUnit reports (Surefire, Gradle, pytest, Jest, …). Unit = `testsuite`
    (by `@name`); a `<testcase>` is keyed by `classname` + `name` and marked
    `inline`, so **pass↔fail↔skip** transitions and added/removed tests each show
    as a single row — while volatile `time` / `timestamp` / `hostname` and the
    roll-up counters are ignored.

=== "sitemap"

    `sitemap.xml`: unit = `url`, identified by its `<loc>` text;
    `<lastmod>` / `<priority>` / `<changefreq>` are compared by text.

=== "generic"

    No dialect knowledge: units are the root's children; identity falls back to
    `@NAME` / `#text`. The default when `--recipe` is omitted.

## Using a custom recipe

Save your `.toml` anywhere and pass its path:

```bash
xmldiffreport ./data --recipe ./my-dialect.toml -o report.md
```

To contribute it as a built-in, drop it in `src/xmldiffreport/recipes/` and add a
small synthetic example + test (see [Contributing](../contributing.md)).
