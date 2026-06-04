You are an expert at configuring **xmldiffreport**, an N-way structural XML diff
tool. Read the XML sample at the end and produce a **recipe** — a small TOML file
that teaches the diff engine how to align and compare this XML dialect.

## What a recipe controls

- `defaults.unit` — the repeated container element that represents one logical
  "thing" being changed (the comparison unit). If unsure, pick the most prominent
  repeated child of the root.
- `[elements.<TAG>] key` — how to identify an element among its siblings, so the
  engine matches "the same" element across files instead of by position.
- `defaults.ignore_attrs` — attributes with no functional meaning that change on
  every export (versions, timestamps, internal ids, user/host, counters). These
  must be ignored or the diff becomes noise.
- `inline = true` — for elements whose meaning lives in their *children* (e.g. an
  action/handler wrapper); their children become pseudo-attributes instead of
  opening a new level.

## Key mini-language

The value of `key` is a **list of tokens**, joined by `|`. The first non-empty
combination identifies the element among its siblings.

| Token | Meaning |
|---|---|
| `@ATTR` | value of attribute `ATTR` (the most common identity) |
| `#text` | the element's own text |
| `*tag` | the tag name itself — use for singleton children compared by their text/value |
| `child:TAG@ATTR` | an attribute of a child element |
| `child:TAG#text` | the text of a child element (e.g. a URL in `<loc>`) |
| `*kinds` | a summary of child kinds / actions — for repeated elements with no stable key |

If a tag has no entry, the engine falls back to `@NAME`, then `#text`, then a
composite of all attributes.

## How to analyse the XML

1. Find the root and the repeated unit element → set `defaults.unit`.
2. For every element type, choose the most stable identifying attribute(s) for
   `key`. Prefer a single human-readable id (`NAME`/`ID`/`KEY`). Use a composite
   (`["@a", "@b"]`) only if no single attribute is unique. Use `child:TAG#text`
   when the identity lives in a child's text. Use `*tag` for singleton children
   whose *value/text* should be compared. Use `["@CODE", "*kinds"]` for
   action-like elements that repeat with the same code.
3. List the volatile attributes you can see (anything versiony / timestampy /
   id-ish / host / user / counter) in `defaults.ignore_attrs`.
4. Mark `inline = true` on any element whose semantics are carried by its child
   elements rather than its own attributes.

## Output

Return **only** a TOML recipe in a single ```toml code block. Add a one-line
comment per non-obvious choice. Do **not** invent attributes that are not in the
sample. Shape:

```toml
name = "my-dialect"

[defaults]
unit = "RECORD"
ignore_attrs = ["version", "lastModified", "internalId"]

[elements.RECORD]
key = ["@name"]

[elements.item]
key = ["@id"]
```

After generating it, the user can sanity-check the file with
`xmldiffreport-recipe validate my-dialect.toml`.

Now analyse the XML below and output the recipe.

```xml
<!-- PASTE A REPRESENTATIVE EXCERPT OF YOUR XML HERE (a few units with varied
     children is enough; you do not need the whole file) -->
```
