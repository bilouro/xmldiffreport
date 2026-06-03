"""xmldiffreport command-line interface."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from . import __version__
from .core import diff_sources, load_recipe, parse_xml
from .report import get_renderer, list_formats, render


def gather_sources(paths: list[str]) -> list[tuple[str, str, Path]]:
    """Resolve paths into sources (env, label, file).

    - a folder whose sub-folders contain ``.xml`` → each sub-folder is an env;
    - a folder with ``.xml`` directly inside       → the folder itself is the env;
    - a file                                        → env = parent folder name.
    """
    out: list[tuple[str, str, Path]] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            subdirs = [d for d in sorted(p.iterdir()) if d.is_dir()]
            if any(any(d.glob("*.xml")) for d in subdirs):
                for d in subdirs:
                    for x in sorted(d.glob("*.xml")):
                        out.append((d.name, f"{d.name}:{x.name}", x))
            else:
                for x in sorted(p.glob("*.xml")):
                    out.append((p.name, f"{p.name}:{x.name}", x))
        elif p.is_file():
            out.append((p.parent.name, p.name, p))
        else:
            print(f"warning: skipped (not found): {raw}", file=sys.stderr)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="xmldiffreport",
        description="N-way structural XML diff, recipe-driven, with a Markdown or HTML report.",
    )
    ap.add_argument("paths", nargs="+", help=".xml files or folders (environments in sub-folders)")
    ap.add_argument(
        "-r",
        "--recipe",
        default="generic",
        help="built-in recipe (e.g. controlm, sitemap) or path to a .toml",
    )
    ap.add_argument("-o", "--out", help="output file (default: reports/YYYYMMDD_HH_MM.<ext>)")
    ap.add_argument(
        "-f",
        "--format",
        choices=list_formats(),
        default=None,
        help="output format (default: inferred from -o, else md)",
    )
    ap.add_argument(
        "--applied-env", help="override the recipe's 'already applied' environment (→ INFO)"
    )
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = ap.parse_args(argv)

    try:
        recipe = load_recipe(args.recipe)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if args.applied_env:
        recipe["applied_env"] = args.applied_env

    raw_sources = gather_sources(args.paths)
    if not raw_sources:
        print("error: no .xml sources found", file=sys.stderr)
        return 2

    sources, envs = [], []
    for env, label, path in raw_sources:
        try:
            sources.append((env, label, parse_xml(path)))
        except Exception as e:
            print(f"warning: skipped {label}: {e}", file=sys.stderr)
        if env not in envs:
            envs.append(env)

    # format: explicit --format > -o extension > "md"
    fmt = args.format
    if fmt is None and args.out:
        fmt = {".html": "html", ".htm": "html"}.get(Path(args.out).suffix.lower(), "md")
    fmt = fmt or "md"
    renderer = get_renderer(fmt)

    results = diff_sources(recipe, sources)
    doc = render(results, envs, len(sources), recipe.get("name", args.recipe), fmt)

    if args.out:
        out = Path(args.out)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H_%M")
        out = Path("reports") / f"{stamp}.{renderer.file_extension}"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")

    n_conf = sum(1 for r in results if r["conflict"])
    print(f"Report: {out}")
    print(f"{len(results)} unit(s) with differences · {n_conf} conflict(s)")
    return 1 if n_conf else 0


if __name__ == "__main__":
    sys.exit(main())
