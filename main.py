"""Entry point: render the poster to entry.png.

The grader runs `python main.py` and expects exactly one image at
/output/entry.png. The destination can be overridden with --out, or with the
MAKEFUN_OUTPUT_DIR environment variable (a plain directory path).
"""

import argparse
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from draw import build_poster


def _destination(cli_out):
    if cli_out:
        return Path(cli_out)
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    if env_dir:
        return Path(env_dir) / "entry.png"
    return Path("/output/entry.png")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Render the 20 Nov 2026 news poster.")
    parser.add_argument("--out", default=None, help="output PNG path (default: /output/entry.png)")
    args = parser.parse_args(argv)
    target = _destination(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    build_poster(str(target))
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
