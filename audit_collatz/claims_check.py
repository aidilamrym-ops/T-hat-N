#!/usr/bin/env python3
"""Frozen textual-claim checks for audit P2 (items H1/H2).

Usage: python3 claims_check.py CLAIMS.tsv ROOT

CLAIMS.tsv rows: '<relpath>\\t<needle>' (tab-separated; no escaping).
Reports FOUND/MISS per claim (whole-file substring containment, UTF-8 read);
exit 1 if any claim is missing.

Frozen with reports/AUDIT_COLLATZ_PREREG_2026-10-19.md.
"""
import sys
from pathlib import Path


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 64
    rows = [ln for ln in Path(argv[1]).read_text(encoding="utf-8").splitlines()
            if ln.strip()]
    root = Path(argv[2])
    misses = 0
    for ln in rows:
        rel, needle = ln.split("\t", 1)
        data = (root / rel).read_text(encoding="utf-8", errors="replace")
        ok = needle in data
        print(("FOUND  " if ok else "MISS   ") + rel + "  ::  " + needle)
        if not ok:
            misses += 1
    print("claims: %d rows, %d miss" % (len(rows), misses))
    return 1 if misses else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))


