#!/usr/bin/env python3
"""Engine Q for audit P2 (Collatz) - accelerated (bulk-halving) implementation.

Frozen with reports/AUDIT_COLLATZ_PREREG_2026-10-19.md. Engine Q is a
structurally distinct implementation from engine P: runs of halving steps are
collapsed with the count-trailing-zeros trick and step counts are accumulated
in bulk. The audit compares P and Q result JSONs for equality on modes w1/w2.

Maps (site convention for t; see captures/site_path_records.html):
  shortcut T(n) = (3n+1)/2 if n odd else n/2   (one application of T per event)
  standard S(n) = 3n+1     if n odd else n/2
t_x(n) = maximum of the trajectory of n under map x until 1 (inclusive).
steps_x(n) = number of map applications until 1.

Modes: selftest | w1 | w2 (see pre-registration for command lines).
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

CAP = 10 ** 6


def ctz(x):
    return (x & -x).bit_length() - 1


def sim_q(n, standard, cap=CAP):
    """Accelerated trajectory. Returns (steps, max) or (-1, -1) on step cap."""
    mx = n
    c = 0
    if standard:
        while n != 1:
            if n & 1:
                n = 3 * n + 1
                c += 1
                if n > mx:
                    mx = n
                if c > cap:
                    return -1, -1
            else:
                z = ctz(n)
                n >>= z
                c += z
                if c > cap:
                    return -1, -1
        return c, mx
    else:
        while n != 1:
            if n & 1:
                n = (3 * n + 1) >> 1
                c += 1
                if n > mx:
                    mx = n
                if c > cap:
                    return -1, -1
            else:
                z = ctz(n)
                n >>= z
                c += z
                if c > cap:
                    return -1, -1
        return c, mx


def sim_naive(n, standard, cap=CAP):
    """Reference loop used only by the selftest for internal cross-checking."""
    mx = n
    c = 0
    while n != 1:
        n = (3 * n + 1 if n & 1 else n // 2) if standard else ((3 * n + 1) // 2 if n & 1 else n // 2)
        if n > mx:
            mx = n
        c += 1
        if c > cap:
            return -1, -1
    return c, mx


def read_battery(path):
    rows = []
    for line in Path(path).read_text(encoding="ascii").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        i, n, claimed = line.split()
        rows.append((int(i), int(n), int(claimed)))
    return rows


def mode_w1(args):
    prows = read_battery(args.path_battery)
    srows = read_battery(args.std_battery) if args.std_battery else []
    cap_hits = set()
    mismatch_path = []
    mismatch_std = []
    rows_path = []
    for i, n, claimed in prows:
        cs, ts = sim_q(n, standard=False)
        cd, td = sim_q(n, standard=True)
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
        cd, td = sim_q(n, standard=True)
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
        cs, _ts = sim_q(n, standard=False)
        cd, _td = sim_q(n, standard=True)
        if cs < 0 or cd < 0:
            cap_hits.add(n)
        ok = cd == claimed
        if not ok:
            mismatches.append(i)
        out.append({"i": i, "n": n, "steps_std": cd, "steps_shortcut": cs,
                    "claimed_steps_std": claimed, "ok": ok})
    return {"rows": out, "checked": len(rows), "mismatches": mismatches,
            "cap_hits": sorted(cap_hits)}


def selftest():
    checks = 0
    for n, std, steps_exp, t_exp in [(3, False, 5, 8), (3, True, 7, 16),
                                     (6, False, 6, 8), (6, True, 8, 16),
                                     (7, False, 11, 26), (7, True, 16, 52),
                                     (15, False, 12, 80), (15, True, 17, 160)]:
        c, t = sim_q(n, standard=std)
        assert (c, t) == (steps_exp, t_exp), (n, std, c, t, steps_exp, t_exp)
        checks += 1
    for n in range(1, 513):
        for std in (False, True):
            assert sim_q(n, standard=std) == sim_naive(n, standard=std), (n, std)
        checks += 1

    class A:
        pass

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
    print("SELFTEST OK (%d checks)" % checks)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Engine Q (Collatz audit P2)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s0 = sub.add_parser("selftest")
    s1 = sub.add_parser("w1")
    s1.add_argument("--path-battery", required=True)
    s1.add_argument("--std-battery")
    s1.add_argument("--out")
    s2 = sub.add_parser("w2")
    s2.add_argument("--battery", required=True)
    s2.add_argument("--out")
    args = ap.parse_args(argv)

    if args.cmd == "selftest":
        selftest()
        return 0

    if args.cmd == "w1":
        result = mode_w1(args)
    else:
        result = mode_w2(args)

    payload = {"tool": "collatz_engine_q", "mode": args.cmd,
               "params": {"args": {k: v for k, v in vars(args).items()
                                   if k not in ("cmd",)},
                          "caps": {"sim": CAP}},
               "result": result}
    text = json.dumps(payload, indent=2, sort_keys=True)
    if getattr(args, "out", None):
        Path(args.out).write_text(text + "\n", encoding="utf-8", newline="\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
