"""xmldiffreport command-line interface."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from . import __version__
from .core import diff_sources, gather_files, load_recipe, parse_xml
from .report import DiffReport, get_renderer, list_formats


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="xmldiffreport",
        description="N-way structural XML diff of files and/or directories, "
        "recipe-driven, with a Markdown or HTML report.",
    )
    ap.add_argument(
        "paths",
        nargs="+",
        help="XML files and/or directories (directories are scanned recursively for *.xml)",
    )
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
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = ap.parse_args(argv)

    try:
        recipe = load_recipe(args.recipe)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    files = gather_files(args.paths)
    if not files:
        print("error: no .xml inputs found", file=sys.stderr)
        return 2

    sources = []
    for label, path in files:
        try:
            sources.append((label, parse_xml(path)))
        except Exception as e:
            print(f"warning: skipped {label}: {e}", file=sys.stderr)

    # format: explicit --format > -o extension > "md"
    fmt = args.format
    if fmt is None and args.out:
        fmt = {".html": "html", ".htm": "html"}.get(Path(args.out).suffix.lower(), "md")
    fmt = fmt or "md"
    renderer = get_renderer(fmt)

    units = diff_sources(recipe, sources)
    report = DiffReport(
        units=units,
        sources=[label for label, _ in sources],
        recipe_name=recipe.get("name", args.recipe),
    )
    doc = report.render(fmt)

    if args.out:
        out = Path(args.out)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H_%M")
        out = Path("reports") / f"{stamp}.{renderer.file_extension}"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")

    print(f"Report: {out}")
    print(f"{len(units)} unit(s) with differences across {len(sources)} file(s)")
    return 1 if units else 0


if __name__ == "__main__":
    sys.exit(main())
