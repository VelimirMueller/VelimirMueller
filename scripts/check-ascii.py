#!/usr/bin/env python3
"""Check the ASCII art rules from docs/presence-style.md.

Checks every ```text block in the given Markdown files and every assets/ascii/*.txt file:
- no tab characters, no trailing spaces
- printable ASCII only; U+2588 FULL BLOCK is allowed in wordmark files and in blocks
  whose first 5 rows hold only full blocks and spaces (a block wordmark)
- 80 columns or less
Exit 0: all rules pass. Exit 1: a rule fails.

Usage: python3 scripts/check-ascii.py            # README.md + assets/ascii
       python3 scripts/check-ascii.py other.md
"""
import glob
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
MAX = 80
BLOCK = "█"


def check(name, lines, allow_block):
    errors = []
    for n, line in enumerate(lines, 1):
        if "\t" in line:
            errors.append(f"{name}:{n}: tab character")
        if line != line.rstrip(" "):
            errors.append(f"{name}:{n}: trailing space")
        if len(line) > MAX:
            errors.append(f"{name}:{n}: {len(line)} columns (max {MAX})")
        for ch in line:
            if not (" " <= ch <= "~") and not (allow_block and ch == BLOCK):
                errors.append(f"{name}:{n}: character U+{ord(ch):04X} is not allowed")
                break
    return errors


def main():
    os.chdir(ROOT)
    docs = sys.argv[1:] or ["README.md"]
    errors = []
    count = 0
    for doc in docs:
        with open(doc, encoding="utf-8") as fh:
            text = fh.read()
        for m in re.finditer(r"^```text\n(.*?)^```", text, flags=re.S | re.M):
            start = text[: m.start()].count("\n") + 2
            block = m.group(1).rstrip("\n").split("\n")
            is_wordmark = any(BLOCK in line for line in block[:5]) and all(
                set(line) <= {BLOCK, " "} for line in block[:5])
            errors += check(f"{doc} (block at line {start}) row", block, is_wordmark)
            count += 1
    for path in sorted(glob.glob("assets/ascii/*.txt")):
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().rstrip("\n").split("\n")
        errors += check(path, lines, os.path.basename(path).startswith("wordmark"))
        count += 1
    for e in errors:
        print("FAIL ", e)
    print(f"{count} blocks checked, {len(errors)} problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
