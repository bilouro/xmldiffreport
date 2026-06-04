# How it compares & when to use which

`xmldiffreport` is not trying to replace every XML diff tool — it occupies a
specific niche: **N-way, key-aligned, recipe-driven, report-first**. This page is
an honest map of the landscape so you pick the right tool for the job.

## At a glance

| Tool | Kind | Ways | Match strategy | Output | Best for |
|---|---|---|---|---|---|
| **xmldiffreport** | structural | **N (2+)** | declared natural key (recipe) | Markdown / HTML report | reviewing what changed across several files/versions |
| `diff` / `git diff` | text | 2 | line-by-line | unified diff | raw line changes on already-normalized XML |
| [`xmldiff`](https://pypi.org/project/xmldiff/) | structural | 2 | algorithmic (heuristic) | edit script / patched XML | producing a *patch* that transforms doc A into doc B |
| Altova DiffDog / Oxygen | structural (GUI) | 2 | algorithmic + some keys | interactive side-by-side | hands-on visual merge of two documents |
| DeltaXML | structural | 2 | keys + heuristic | delta XML | enterprise, document-oriented XML, support contract |
| BMC Control-M compare / AAPI+git | domain | 2 | tool-specific | GUI / text | inside the Control-M product or its JSON/YAML in git |

## The alternatives, and when to reach for them

### Plain `diff` / `git diff`
Line-by-line text comparison. **Use it when** the XML is already canonicalized
(stable attribute order, no volatile fields) and you just want the raw textual
delta. **Avoid when** exports carry volatile attributes (`VERSION`, timestamps,
ids) or reorder children — it will report noise that isn't a real change.

### `xmldiff` (Python)
Excellent tree-diff that emits an **edit script** (insert/delete/update/move) or a
patched document. **Use it when** your goal is to *transform* one document into
another (apply a patch), or you want a programmatic delta between exactly two
files. **Limitations for our use:** 2-way only; it matches nodes with its own
algorithm — you can't say "match `<JOB>` by `JOBNAME`"; the output is a script,
not a human review artifact.

### Altova DiffDog / Oxygen XML compare (GUI)
Mature, interactive, side-by-side visual diff/merge. **Use it when** a human is
sitting in front of two files resolving differences by hand, especially for
mixed-content/document XML. **Limitations:** 2-way, GUI (not CI-friendly), and you
configure ignores/keys per session rather than as a reusable, versioned recipe.

### DeltaXML (commercial)
The gold standard for document-oriented XML comparison, with strong
similarity-based matching and configurable keys. **Use it when** you need
enterprise-grade matching of keyless documents, a support contract, and 2-way
document comparison at scale. **Limitations for our use:** commercial/licensed;
2-way; you still build your own reporting layer.

### BMC Control-M (built-in compare / Automation API + git)
Control-M can compare job *versions* in its UI, and many teams export the
**Automation API** JSON/YAML and `git diff` it. **Use it when** you live entirely
inside the product, or you've adopted AAPI-as-code. **Limitations:** the built-in
compare isn't a folder/job/attribute matrix; git-diffing the JSON/YAML is still
line-based and 2-way.

## Decision guide

**Choose `xmldiffreport` when:**

- You need to compare **3+ files at once** (e.g. the same folder in `uat`, `bench`
  and `prod`) and see one column per source.
- You want a **review-ready Markdown/HTML report**, not an edit script or a GUI.
- You can describe identity declaratively with a **recipe** (a stable key per
  element) — Control-M, sitemaps, POMs, and most config/export dialects qualify.
- You want a **CI gate**: non-zero exit when anything differs.
- The noise of volatile attributes/reordering is hurting a plain diff.

**Reach for something else when:**

- You need to **apply a patch** / produce an edit script → `xmldiff`.
- A human wants to **interactively merge two files** → DiffDog / Oxygen.
- You need **heuristic matching of keyless documents** at enterprise scale, with a
  vendor contract → DeltaXML.
- The XML is already normalized and you only want **raw line changes** → `git diff`.

In short: `xmldiffreport` is the tool for *“tell me, across these N exports, what
actually changed at the folder/job/attribute level, and flag the collisions”* —
not for interactive merging or patch generation.
