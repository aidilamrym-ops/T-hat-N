#!/usr/bin/env python3
"""Engine P for audit P2 (Collatz) - direct iterative implementation.

Frozen with reports/AUDIT_COLLATZ_PREREG_2026-10-19.md. Engines P and Q are
structurally distinct implementations; the audit compares their result JSONs
for equality, and engine C (audit_collatz/collatz_sweep.c) independently
re-derives the E2 prefix digest and the E3 record prefix.

Maps (site convention for t; see captures/site_path_records.html):
  shortcut T(n) = (3n+1)//2 if n odd else n//2
  standard S(n) = 3n+1      if n odd else n//2
t_x(n) = maximum of the trajectory of n under map x until 1 (inclusive).
steps_x(n) = number of map applications until 1.

Modes: selftest | w1 | w2 | e2 | e3 (see pre-registration for command lines).
"""
import argparse
import json
import sys
import tempfile
import time
from array import array
from pathlib import Path

CAP = 10 ** 6          # step cap for battery simulations
DROP_CAP = 10 ** 6     # step cap for drop checks
PROGRESS_EVERY = 1 << 22


def sim(n, standard, cap=CAP):
    """Trajectory of n to 1. Returns (steps, max) or (-1, -1) on step cap."""
    mx = n
    c = 0
    if standard:
        while n != 1:
            n = 3 * n + 1 if n & 1 else n // 2
            if n > mx:
                mx = n
            c += 1
            if c > cap:
                return -1, -1
    else:
        while n != 1:
            n = (3 * n + 1) // 2 if n & 1 else n // 2
            if n > mx:
                mx = n
            c += 1
            if c > cap:
                return -1, -1
    return c, mx


def drop_one(n, cap=DROP_CAP):
    """First value < n under the shortcut map. Returns (steps, value) or (-1, -1)."""
    start = n
    c = 0
    while True:
        n = (3 * n + 1) // 2 if n & 1 else n // 2
        c += 1
        if n < start:
            return c, n
        if c > cap:
            return -1, -1


def read_battery(path):
    rows = []
    for line in Path(path).read_text(encoding="ascii").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        i, n, claimed = line.split()
        rows.append((int(i), int(n), int(claimed)))
    return rows


def records_below(bound):
    """All path records (running t maxima, shortcut map) for n < bound."""
    t = array("Q", [0]) * bound
    recs = []
    runmax = 0
    for n in range(1, bound):
        if n == 1:
            v = 1
        elif not (n & 1):
            prev = t[n >> 1]
            v = n if n > prev else prev
        else:
            c, v = sim(n, standard=False)
            if c < 0:
                raise RuntimeError("drop cap hit in records mode at n=%d" % n)
        t[n] = v
        if v > runmax:
            runmax = v
            recs.append({"i": len(recs) + 1, "n": n, "t": v})
    return recs


def mode_w1(args):
    prows = read_battery(args.path_battery)
    srows = read_battery(args.std_battery) if args.std_battery else []
    cap_hits = set()
    mismatch_path = []
    mismatch_std = []
    rows_path = []
    for i, n, claimed in prows:
        cs, ts = sim(n, standard=False)
        cd, td = sim(n, standard=True)
        if cs < 0 or cd < 0:
            cap_hits.add(n)
        ok = ts == claimed
        if not ok:
            mismatch_path.append(i)
        rows_path.append({"i": i, "n": n, "steps_shortcut": cs, "t_shortcut": ts,
                          "steps_std": cd, "t_std": td,
                          "claimed_t_shortcut": claimed, "ok_shortcut": ok})
    rows_std = []
    for i, n, claimed in srows:
        cd, td = sim(n, standard=True)
        if cd < 0:
            cap_hits.add(n)
        ok = td == claimed
        if not ok:
            mismatch_std.append(i)
        rows_std.append({"i": i, "n": n, "t_std": td,
                         "claimed_t_std": claimed, "ok_std": ok})
    return {"rows_path": rows_path, "rows_std": rows_std,
            "path_checked": len(prows), "std_checked": len(srows),
            "mismatch_path": mismatch_path, "mismatch_std": mismatch_std,
            "cap_hits": sorted(cap_hits)}


def mode_w2(args):
    rows = read_battery(args.battery)
    cap_hits = set()
    mismatches = []
    out = []
    for i, n, claimed in rows:
        cs, _ts = sim(n, standard=False)
        cd, _td = sim(n, standard=True)
        if cs < 0 or cd < 0:
            cap_hits.add(n)
        ok = cd == claimed
        if not ok:
            mismatches.append(i)
        out.append({"i": i, "n": n, "steps_std": cd, "steps_shortcut": cs,
                    "claimed_steps_std": claimed, "ok": ok})
    return {"rows": out, "checked": len(rows), "mismatches": mismatches,
            "cap_hits": sorted(cap_hits)}


def mode_e2(args):
    bound = args.bound
    odd_checked = 0
    maxst = 0
    argmax = 0
    total = 0
    cap_hits = []
    t0 = time.time()
    for n in range(3, bound, 2):
        st, v = drop_one(n)
        if st < 0:
            cap_hits.append(n)
            continue
        odd_checked += 1
        total += v
        if st > maxst:
            maxst, argmax = st, n
        if odd_checked % PROGRESS_EVERY == 0:
            print("progress odd_checked=%d n=%d elapsed=%.1fs"
                  % (odd_checked, n, time.time() - t0), file=sys.stderr)
    return {"bound": bound, "odd_checked": odd_checked,
            "max_steps_to_drop": maxst, "argmax": argmax,
            "sum_drop": str(total), "cap_hits": cap_hits}


def mode_e3(args):
    bound = args.bound
    if bound > (1 << 26):
        raise SystemExit("e3 bound too large for 64-bit t array")
    recs = records_below(bound)
    pc = None
    if args.path_battery:
        brows = read_battery(args.path_battery)
        in_range = [(i, n, h) for (i, n, h) in brows if n < bound]
        match = len(in_range) == len(recs)
        first_mismatch = None
        if match:
            for (i, n, h), r in zip(in_range, recs):
                if i != r["i"] or n != r["n"] or h != r["t"]:
                    match = False
                    first_mismatch = {"i": i, "n": n, "claimed": h,
                                      "computed_i": r["i"], "computed_n": r["n"],
                                      "computed_t": r["t"]}
                    break
        pc = {"battery_rows_in_range": len(in_range), "match": match,
              "first_mismatch": first_mismatch}
    return {"bound": bound, "records": recs, "record_count": len(recs),
            "prefix_compare": pc}


def selftest():
    checks = 0
    for n, std, steps_exp, t_exp in [(3, False, 5, 8), (3, True, 7, 16),
                                     (6, False, 6, 8), (6, True, 8, 16),
                                     (7, False, 11, 26), (7, True, 16, 52),
                                     (15, False, 12, 80), (15, True, 17, 160)]:
        c, t = sim(n, standard=std)
        assert (c, t) == (steps_exp, t_exp), (n, std, c, t, steps_exp, t_exp)
        checks += 1
    for n, steps_exp, val_exp in [(3, 4, 2), (7, 7, 5), (15, 7, 10), (27, 59, 23)]:
        st, v = drop_one(n)
        assert (st, v) == (steps_exp, val_exp), (n, st, v)
        checks += 1
    recs = records_below(16)
    assert [(r["n"], r["t"]) for r in recs] == [(1, 1), (2, 2), (3, 8), (7, 26), (15, 80)]
    checks += 1

    class A:
        pass

    a = A()
    a.bound = 16
    r = mode_e2(a)
    assert r["odd_checked"] == 7 and r["max_steps_to_drop"] == 7 and r["argmax"] == 7
    assert not r["cap_hits"]
    checks += 1

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        pb = td / "path.tsv"
        pb.write_text("# synthetic\n1\t2\t2\n2\t3\t8\n3\t6\t8\n4\t7\t26\n5\t15\t80\n",
                      encoding="ascii", newline="\n")
        sb = td / "std.tsv"
        sb.write_text("1\t2\t2\n2\t3\t16\n3\t7\t52\n4\t15\t160\n",
                      encoding="ascii", newline="\n")
        db = td / "delay.tsv"
        db.write_text("1\t3\t7\n2\t6\t8\n3\t7\t16\n4\t15\t17\n",
                      encoding="ascii", newline="\n")
        a1 = A()
        a1.path_battery = str(pb)
        a1.std_battery = str(sb)
        r1 = mode_w1(a1)
        assert not r1["mismatch_path"] and not r1["mismatch_std"] and not r1["cap_hits"]
        assert r1["path_checked"] == 5 and r1["std_checked"] == 4
        checks += 1
        a2 = A()
        a2.battery = str(db)
        r2 = mode_w2(a2)
        assert not r2["mismatches"] and not r2["cap_hits"] and r2["checked"] == 4
        checks += 1
        bad = td / "bad.tsv"
        bad.write_text("1\t3\t9\n", encoding="ascii", newline="\n")
        a3 = A()
        a3.path_battery = str(bad)
        a3.std_battery = None
        r3 = mode_w1(a3)
        assert r3["mismatch_path"] == [1]
        checks += 1
        eb = td / "e3.tsv"
        eb.write_text("1\t1\t1\n2\t2\t2\n3\t3\t8\n4\t7\t26\n5\t15\t80\n",
                      encoding="ascii", newline="\n")
        a4 = A()
        a4.bound = 16
        a4.path_battery = str(eb)
        r4 = mode_e3(a4)
        assert r4["prefix_compare"]["match"] and r4["record_count"] == 5
        checks += 1
    print("SELFTEST OK (%d checks)" % checks)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Engine P (Collatz audit P2)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s0 = sub.add_parser("selftest")
    s1 = sub.add_parser("w1")
    s1.add_argument("--path-battery", required=True)
    s1.add_argument("--std-battery")
    s1.add_argument("--out")
    s2 = sub.add_parser("w2")
    s2.add_argument("--battery", required=True)
    s2.add_argument("--out")
    s3 = sub.add_parser("e2")
    s3.add_argument("--bound", type=int, required=True)
    s3.add_argument("--out")
    s4 = sub.add_parser("e3")
    s4.add_argument("--bound", type=int, required=True)
    s4.add_argument("--path-battery")
    s4.add_argument("--out")
    args = ap.parse_args(argv)

    if args.cmd == "selftest":
        selftest()
        return 0

    if args.cmd == "w1":
        result = mode_w1(args)
    elif args.cmd == "w2":
        result = mode_w2(args)
    elif args.cmd == "e2":
        result = mode_e2(args)
    else:
        result = mode_e3(args)

    payload = {"tool": "collatz_engine_p", "mode": args.cmd,
               "params": {"args": {k: v for k, v in vars(args).items()
                                   if k not in ("cmd",)},
                          "caps": {"sim": CAP, "drop": DROP_CAP}},
               "result": result}
    text = json.dumps(payload, indent=2, sort_keys=True)
    if getattr(args, "out", None):
        Path(args.out).write_text(text + "\n", encoding="utf-8", newline="\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())


