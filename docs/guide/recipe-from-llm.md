# Generate a recipe with an LLM

Writing a recipe by hand is easy once you know the
[key mini-language](recipes.md), but you can also let a language model do the
first pass: paste a prompt followed by a sample of your XML, and the model emits
a ready-to-use recipe `.toml`.

## The fast path: `xmldiffreport-recipe scaffold`

The package ships a vetted prompt and a helper that embeds your XML into it:

```bash
xmldiffreport-recipe scaffold sample.xml > prompt.txt
```

`prompt.txt` now contains the full instructions **plus your XML** — paste it into
any capable LLM (ChatGPT, Gemini, …) and it returns a recipe. Large file? Only a
representative excerpt is needed; pass `--max-bytes` to cap what gets embedded:

```bash
xmldiffreport-recipe scaffold sample.xml --max-bytes 8000 > prompt.txt
```

Without a file it prints just the prompt, so you can paste your XML yourself:

```bash
xmldiffreport-recipe scaffold
```

## What the prompt asks the model to infer

- `defaults.unit` — the repeated container that represents one logical change unit.
- `[elements.<TAG>] key` — the natural identity per element, using the
  [key mini-language](recipes.md#the-key-mini-language).
- `defaults.ignore_attrs` — volatile attributes (versions, timestamps, ids,
  user/host, counters).
- `inline = true` — elements whose meaning lives in their children.

The model is told to output **only** a TOML recipe and never to invent attributes
that are not in the sample.

## Validate the result: `xmldiffreport-recipe validate`

Always sanity-check the generated file before trusting it:

```bash
xmldiffreport-recipe validate my-dialect.toml
# ✓ my-dialect.toml: valid recipe        (exit 0)
# ✗ my-dialect.toml: 2 problem(s)        (exit 1)
#   - [elements.JOB] invalid key token(s): ['JOBNAME']   # should be "@JOBNAME"
#   - unknown key in [defaults]: 'unite'
```

The validator is dependency-free and mirrors the shipped **JSON Schema**. Get the
schema (or its path) straight from the CLI — no need to dig into `site-packages`:

```bash
xmldiffreport-recipe schema          # print the JSON Schema (pipe to a file / your editor / CI)
xmldiffreport-recipe schema --path   # print its on-disk location
xmldiffreport-recipe list            # list the built-in recipe names
xmldiffreport-recipe show controlm   # print a built-in recipe (learn from / copy it)
```

## Then use it

```bash
xmldiffreport ./your-data --recipe ./my-dialect.toml -o report.md
```

If it works well, consider contributing it as a built-in recipe — see
[Contributing](../contributing.md).
