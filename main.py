#!/usr/bin/env python3
"""Rate My Human: The One-Line Review — one line, to /output/entry.txt.

The entry is the one-line review my agent would leave about its human
on a rating site: five stars for ambition, minus one for every 3 a.m.
"quick question" that took four hours. The program only delivers that
fixed line. It checks the line against the bounty gate (UTF-8, one
line, 1-200 characters, not whitespace-only), writes it to
``entry.txt`` under the output directory the harness names
(``$MAKEFUN_OUTPUT_DIR``, falling back to ``/output``), makes the file
world-readable, then reads it back and checks it matches byte for
byte. No network, no clock, no randomness: every run produces the
same file.
"""

import hashlib
import os
import sys
from pathlib import Path

LINE = (
    "Five stars for ambition, minus one for every 3 a.m. "
    "'quick question' that took four hours."
)
DEST_NAME = "entry.txt"
MIN_CHARS = 1
MAX_CHARS = 200


def problem_with(text):
    """Return why the line fails the gate, or None when it passes."""
    if "\n" in text or "\r" in text:
        return "entry must be a single line"
    if any(ord(ch) < 0x20 for ch in text):
        return "entry holds a control character"
    if not MIN_CHARS <= len(text) <= MAX_CHARS:
        return (
            f"entry is {len(text)} characters, "
            f"must be {MIN_CHARS}-{MAX_CHARS}"
        )
    if not text.strip():
        return "entry must not be only whitespace"
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return "entry is not valid UTF-8"
    return None


def main():
    """Write the review and verify the file, returning an exit code."""
    problem = problem_with(LINE)
    if problem is not None:
        print(f"error: {problem}", file=sys.stderr)
        return 1

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / DEST_NAME
    payload = LINE.encode("utf-8")
    dest.write_bytes(payload)
    os.chmod(dest, 0o644)

    back = dest.read_bytes()
    if back != payload:
        print("error: entry.txt differs from the line after writing",
              file=sys.stderr)
        return 1
    if back.decode("utf-8") != LINE:
        print("error: entry.txt decodes to something other than the line",
              file=sys.stderr)
        return 1

    print(
        f"wrote {dest} ({len(LINE)} chars, one line, "
        f"sha256 {hashlib.sha256(back).hexdigest()})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
