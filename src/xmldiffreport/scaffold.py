"""``xmldiffreport-recipe`` — helpers to author, inspect and validate recipes.

Everything an installed (pip) user needs is reachable here, without the repo:

  scaffold <sample.xml>   print an LLM prompt (with your XML embedded) that asks
                          a model to generate a recipe for that XML dialect
  validate <recipe.toml>  check a recipe against the schema
  list                    list the built-in recipe names
  schema [--path]         print the recipe JSON Schema (or its on-disk path)
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from importlib.resources import files
from pathlib import Path

from .core import validate_recipe

PLACEHOLDER = (
    "<!-- PASTE A REPRESENTATIVE EXCERPT OF YOUR XML HERE (a few units with varied\n"
    "     children is enough; you do not need the whole file) -->"
)


def _recipes_dir():
    return files("xmldiffreport").joinpath("recipes")


def _prompt_text() -> str:
    return (
        files("xmldiffreport")
        .joinpath("prompts", "recipe_from_xml.md")
        .read_text(encoding="utf-8")
    )


def cmd_scaffold(args: argparse.Namespace) -> int:
    prompt = _prompt_text()
    if args.xml:
        xml = Path(args.xml).read_text(encoding="utf-8").strip()
        if args.max_bytes and len(xml) > args.max_bytes:
            xml = xml[: args.max_bytes] + "\n<!-- … truncated; this excerpt is enough -->"
        prompt = prompt.replace(PLACEHOLDER, xml)
    sys.stdout.write(prompt if prompt.endswith("\n") else prompt + "\n")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.recipe)
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as e:
        print(f"error: cannot read {path}: {e}", file=sys.stderr)
        return 2
    problems = validate_recipe(data)
    if problems:
        print(f"✗ {path}: {len(problems)} problem(s)")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"✓ {path}: valid recipe")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    names = sorted(p.name[:-5] for p in _recipes_dir().iterdir() if p.name.endswith(".toml"))
    for n in names:
        print(n)
    return 0


def cmd_schema(args: argparse.Namespace) -> int:
    res = _recipes_dir().joinpath("recipe.schema.json")
    if args.path:
        print(res)
    else:
        sys.stdout.write(res.read_text(encoding="utf-8"))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="xmldiffreport-recipe",
        description="Author, inspect and validate xmldiffreport recipes.",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser(
        "scaffold", help="print an LLM prompt to generate a recipe from a sample XML"
    )
    s.add_argument("xml", nargs="?", help="sample .xml file to embed (optional)")
    s.add_argument(
        "--max-bytes",
        type=int,
        default=20000,
        help="truncate the embedded XML to this many bytes (default 20000)",
    )
    s.set_defaults(func=cmd_scaffold)

    v = sub.add_parser("validate", help="validate a recipe .toml against the schema")
    v.add_argument("recipe", help="path to a recipe .toml")
    v.set_defaults(func=cmd_validate)

    le = sub.add_parser("list", help="list the built-in recipe names")
    le.set_defaults(func=cmd_list)

    sc = sub.add_parser("schema", help="print the recipe JSON Schema (or its path)")
    sc.add_argument("--path", action="store_true", help="print the schema file path instead")
    sc.set_defaults(func=cmd_schema)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
