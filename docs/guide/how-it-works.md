# How it works

`xmldiffreport` treats every XML document as a tree of nodes and compares **N**
of them at once, aligning nodes by a **natural key** rather than by position.

## The model

- Each element is a node with **attributes**, optional **text**, and **children**.
- A **recipe** declares, per tag: the `key` (natural identity), whether the tag
  is `inline` (its children become pseudo-attributes instead of opening a new
  level), and which attributes to ignore.
- The engine compares **N sources** simultaneously, matching nodes by identity
  (order-independent). **Only differences** end up in the result.

```mermaid
flowchart LR
  A[parse each file] --> B[index units by tag+key]
  B --> C{unit in ≥2 sources?}
  C -- no --> X[skip]
  C -- yes --> D[recursive diff per node]
  D --> E[classify CONFLICT / INFO]
  E --> F[render Markdown]
```

## Units and recursion

The recipe's `unit` (e.g. `SMART_FOLDER`) is the top comparison entity. For each
unit present in **2 or more sources**, the engine walks the tree recursively:

- **Scalar differences** — attributes (and element text) that differ become rows.
- **Leaf / inline children** (e.g. `INCOND`, `OUTCOND`, `ON`) are compared by
  their key; a row appears when one is added/removed or when one of its
  **attributes** changes (e.g. an `OUTCOND` keeps its `NAME` but flips `SIGN`).
- **Container children** (e.g. `JOB`) open a new level and are rendered as
  sub-sections; identical ones are collapsed into a count.

## Attribute-level, not just present/absent

Because elements are matched by identity, a change *inside* an element is shown
as an attribute change, not as a delete + add:

| Element · attribute | bench | uat | prod |
|---|---|---|---|
| INCOND `…STAGE-…LOAD_OK` · `AND_OR` | A | O | A |
| OUTCOND `…LOAD-…POST_OK` · `SIGN` | - | + | + |

## Volatile attributes are ignored

Attributes that change on every export without functional meaning — `VERSION`,
`CREATION_TIME`, `JOBISN`, `LAST_UPLOAD`, … — are listed in the recipe's
`ignore_attrs` and never produce a row. This is what makes the diff *semantic*
instead of noisy.

## Conflict classification

- A unit present in **≥2 non-applied** sources, with differences → **⚠️ CONFLICT**
  (two pending patches collide).
- A unit whose only counterpart is the **applied** environment (e.g. `prod`) →
  **ℹ️ INFO** — it changes something already live; verify your rebase, but it is
  not a patch-vs-patch collision.
- With no `applied_env`, every difference is reported as a plain **DIFF**.

The "applied" environment is set by the recipe (`applied_env = "prod"`) and can
be overridden with `--applied-env`.

## Namespaces & text

XML namespaces are stripped on parse (`{uri}tag` → `tag`) so tags and keys stay
readable and recipes stay simple. Element **text** is comparable too — e.g. a
sitemap `<url>` is identified by its `<loc>` text and its `<lastmod>` text is
compared as a value.
