#!/usr/bin/env python3
"""Comparison utilities for audit P2 (Collatz) evidence JSONs.

Frozen with reports/AUDIT_COLLATZ_PREREG_2026-10-19.md.

Modes:
  compare A.json B.json
      deep-compare the "result" subtrees; exit 0 iff equal.
  compare-fields A.json B.json F1 F2 ...
      compare A.result.Fk against B.result.Fk for each field.
  compare-prefix SWEEP.json E2.json
      compare SWEEP.result.prefix24 against the selected keys of E2.result
      (bound, odd_checked, max_steps_to_drop, argmax, sum_drop).
  check-prefix RECORDS.json BATTERY.tsv
      the records (i, n, t) with n < result.bound must equal exactly the
      battery rows below that bound (site-convention path-record battery).

Prints MATCH or MISMATCH detail; nonzero exit on mismatch.
"""
import json
import sys
from pathlib import Path

PREFIX_KEYS = ["bound", "odd_checked", "max_steps_to_drop", "argmax", "sum_drop"]


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def deep_diff(a, b, path="result"):
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            return "%s: keys differ: only_A=%s only_B=%s" % (
                path, sorted(set(a) - set(b)), sorted(set(b) - set(a)))
        for k in sorted(a):
            d = deep_diff(a[k], b[k], path + "." + str(k))
            if d:
                return d
        return None
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return "%s: length %d != %d" % (path, len(a), len(b))
        for idx, (x, y) in enumerate(zip(a, b)):
            d = deep_diff(x, y, "%s[%d]" % (path, idx))
            if d:
                return d
        return None
    if a != b:
        return "%s: %r != %r" % (path, a, b)
    return None


def read_battery(path):
    rows = []
    for line in Path(path).read_text(encoding="ascii").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        i, n, t = line.split()
        rows.append((int(i), int(n), int(t)))
    return rows


def cmd_compare(a, b):
    A, B = load(a), load(b)
    d = deep_diff(A["result"], B["result"])
    print("MISMATCH: %s" % d if d else "MATCH")
    return 1 if d else 0


def cmd_compare_fields(a, b, fields):
    A, B = load(a), load(b)
    for f in fields:
        d = deep_diff(A["result"].get(f), B["result"].get(f), "result." + f)
        if d:
            print("MISMATCH: %s" % d)
            return 1
    print("MATCH")
    return 0


def cmd_compare_prefix(sweep, e2):
    S, E = load(sweep), load(e2)
    sub = {k: S["prefix24"][k] for k in PREFIX_KEYS}
    ref = {k: E["result"][k] for k in PREFIX_KEYS}
    d = deep_diff(sub, ref, "prefix24")
    print("MISMATCH: %s" % d if d else "MATCH")
    return 1 if d else 0


def cmd_check_prefix(records, battery):
    R = load(records)
    bound = R["result"]["bound"]
    recs = [(r["i"], r["n"], r["t"]) for r in R["result"]["records"]]
    brows = [(i, n, t) for (i, n, t) in read_battery(battery) if n < bound]
    if len(recs) != len(brows):
        print("MISMATCH: length %d != %d" % (len(recs), len(brows)))
        return 1
    for idx, (x, y) in enumerate(zip(recs, brows)):
        if x != y:
            print("MISMATCH: entry %d: records=%s battery=%s" % (idx, x, y))
            return 1
    print("MATCH (%d entries)" % len(recs))
    return 0


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 64
    mode = argv[1]
    if mode == "compare" and len(argv) == 4:
        return cmd_compare(argv[2], argv[3])
    if mode == "compare-fields" and len(argv) >= 5:
        return cmd_compare_fields(argv[2], argv[3], argv[4:])
    if mode == "compare-prefix" and len(argv) == 4:
        return cmd_compare_prefix(argv[2], argv[3])
    if mode == "check-prefix" and len(argv) == 4:
        return cmd_check_prefix(argv[2], argv[3])
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
