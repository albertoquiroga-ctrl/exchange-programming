#!/usr/bin/env python3
"""Decode base64 slide artifacts into binary assets."""
from __future__ import annotations

import argparse
import base64
import pathlib
import sys


def decode_file(path: pathlib.Path, force: bool = False) -> pathlib.Path:
    if path.suffix != '.b64':
        raise ValueError(f"{path} is not a .b64 file")
    target = path.with_suffix('')
    # Avoid overwriting the original asset unless callers explicitly opt-in.
    if target.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing file: {target}")
    data = base64.b64decode(path.read_bytes())
    target.write_bytes(data)
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "roots",
        nargs="*",
        type=pathlib.Path,
        default=[pathlib.Path('Final Project/docs/slides')],
        help="Directories or .b64 files to decode",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite existing decoded files",
    )
    args = parser.parse_args(argv)

    decoded: list[pathlib.Path] = []
    for root in args.roots:
        # Support mixing directories and files so instructors can decode just
        # one asset or the entire slides folder.
        if root.is_file():
            decoded.append(decode_file(root, force=args.force))
            continue
        if not root.exists():
            parser.error(f"Path does not exist: {root}")
        for b64_path in root.rglob('*.b64'):
            decoded.append(decode_file(b64_path, force=args.force))
    if not decoded:
        print("No .b64 files decoded", file=sys.stderr)
        return 1
    # Mirror the output paths so students know where the binary artifacts live.
    for path in decoded:
        print(f"Decoded {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
