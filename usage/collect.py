#!/usr/bin/env python3
"""xmldiffreport USAGE harness (not part of the distributed package).

Reads a ``config.toml`` mapping environment → folder of XMLs, collects the
files, runs the diff, and writes a Markdown/HTML report to the configured
report directory.

Use this to point the tool at your real folders (e.g. per-environment Jira
attachment downloads) while keeping the engine generic and reusable.

    python usage/collect.py                 # uses usage/config.toml
    python usage/collect.py other/config.toml
"""

from __future__ import annotations

import sys
import tomllib
from datetime import datetime
from pathlib import Path

try:  # when the package is installed
    from xmldiffreport.core import diff_sources, load_recipe, parse_xml
    from xmldiffreport.report import get_renderer, render
except ModuleNotFoundError:  # dev mode: use the repo's src/
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from xmldiffreport.core import diff_sources, load_recipe, parse_xml
    from xmldiffreport.report import get_renderer, render

HERE = Path(__file__).resolve().parent


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    cfg_path = Path(argv[0]) if argv else HERE / "config.toml"
    if not cfg_path.is_file():
        sys.exit(
            f"config not found: {cfg_path}\n"
            f"  copy {HERE / 'config.example.toml'} to config.toml and edit it."
        )

    cfg = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
    base = cfg_path.parent
    recipe = load_recipe(cfg.get("recipe", "controlm"))
    if "applied_env" in cfg:
        recipe["applied_env"] = cfg["applied_env"]
    report_dir = (base / cfg.get("report_dir", "reports")).resolve()

    sources: list = []
    envs: list[str] = []
    for env, rel in cfg.get("environments", {}).items():
        folder = base / rel
        files = sorted(folder.glob("*.xml"))
        if not files:
            print(f"warning: no .xml in {folder}", file=sys.stderr)
        for x in files:
            try:
                sources.append((env, f"{env}:{x.name}", parse_xml(x)))
            except Exception as e:
                print(f"warning: skipped {env}:{x.name}: {e}", file=sys.stderr)
        envs.append(env)

    if not sources:
        sys.exit("no XML collected — check the paths in [environments].")

    fmt = cfg.get("format", "md")
    results = diff_sources(recipe, sources)
    doc = render(results, envs, len(sources), recipe.get("name", "controlm"), fmt)
    report_dir.mkdir(parents=True, exist_ok=True)
    ext = get_renderer(fmt).file_extension
    out = report_dir / f"{datetime.now().strftime('%Y%m%d_%H_%M')}.{ext}"
    out.write_text(doc, encoding="utf-8")

    n_conf = sum(1 for r in results if r["conflict"])
    print(f"Report: {out}")
    print(f"{len(results)} unit(s) with differences · {n_conf} conflict(s)")
    return 1 if n_conf else 0


if __name__ == "__main__":
    raise SystemExit(main())
