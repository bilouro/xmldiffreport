#!/usr/bin/env python3
"""xmldiffreport USAGE harness (not part of the distributed package).

Reads a ``config.toml`` that lists the inputs (files and/or directories) to
compare, runs the diff, and writes a Markdown/HTML report to the configured
directory. A thin wrapper around the library so you can keep your paths and
output settings in one place.

    python usage/collect.py                 # uses usage/config.toml
    python usage/collect.py other/config.toml
"""

from __future__ import annotations

import sys
import tomllib
from datetime import datetime
from pathlib import Path

try:  # when the package is installed
    from xmldiffreport import diff
    from xmldiffreport.report import get_renderer
except ModuleNotFoundError:  # dev mode: use the repo's src/
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from xmldiffreport import diff
    from xmldiffreport.report import get_renderer

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
    inputs = [str(base / p) for p in cfg.get("inputs", [])]
    if not inputs:
        sys.exit("no inputs configured — set `inputs = [...]` (files and/or dirs).")

    fmt = cfg.get("format", "md")
    result = diff(inputs, recipe=cfg.get("recipe", "generic"))

    report_dir = (base / cfg.get("report_dir", "reports")).resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    ext = get_renderer(fmt).file_extension
    out = report_dir / f"{datetime.now().strftime('%Y%m%d_%H_%M')}.{ext}"
    out.write_text(result.render(fmt), encoding="utf-8")

    print(f"Report: {out}")
    print(f"{len(result.units)} unit(s) with differences across {len(result.sources)} file(s)")
    return 1 if result else 0


if __name__ == "__main__":
    raise SystemExit(main())
