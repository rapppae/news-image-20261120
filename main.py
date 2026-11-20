"""Render the 20 November 2026 news poster to a PNG file.

The output folder comes from MAKEFUN_OUTPUT_DIR (or /output when the
variable is unset). After saving, the file is verified on disk: it must
begin with the PNG signature, measure exactly 1024 by 1024, and stay
under one mebibyte. A failed check raises instead of shipping a
broken image.
"""

import hashlib
import os
from pathlib import Path

from PIL import Image

import draw

SIGNATURE = b"\x89PNG\r\n\x1a\n"
SIDE = 1024
MAX_BYTES = 1024 * 1024


def target_path():
    """Where the poster is written."""
    folder = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "entry.png"


def verify(path):
    """Check the saved file is really the poster we meant to ship."""
    blob = path.read_bytes()
    if blob[:8] != SIGNATURE:
        raise ValueError("not a PNG file")
    with Image.open(path) as shot:
        if shot.size != (SIDE, SIDE):
            raise ValueError(f"wrong size: {shot.size}")
        dims = f"{shot.size[0]}x{shot.size[1]}"
    if len(blob) > MAX_BYTES:
        raise ValueError(f"too big: {len(blob)} bytes")
    return blob, dims


def main():
    here = Path(__file__).resolve().parent
    poster = draw.compose(str(here / "assets"))
    target = target_path()
    poster.save(target, format="PNG", optimize=True)
    blob, dims = verify(target)
    digest = hashlib.sha256(blob).hexdigest()
    print(f"wrote {target} ({dims}, {len(blob)} bytes, sha256 {digest})")


if __name__ == "__main__":
    main()
