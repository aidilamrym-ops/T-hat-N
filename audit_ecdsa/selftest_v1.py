#!/usr/bin/env python3
"""V1 engine selftests (mechanistic only; synthetic vectors - NOT audit evidence).

Checks:
 A) draws: E1 (pure C) == E1w (glibc weld), 7 seeds x 250 draws.
 B) draws: E2 (pure Python) == E1 on the same vectors.
 C) range: all E1 draws are 31-bit (<= 0x7FFFFFFF).
 D) candidate/scan: E1 == E2 on synthetic (t, n) for both audit formats
    (prime: per=20 shift=40 width=2; binary: per=5 shift=17 width=8); scan()
    returns the true first index (brute-force verified) and E1 scan == E2 scan,
    including a mutated (no-match) target.

Usage: selftest_v1.py --e1 E1 [--e1w E1W] [--e2 E2] [--json OUT]
Exit 0 = all checks OK; exit 1 = FAIL (freeze criterion: STOP).
"""
import argparse
import json
import subprocess
import sys

SEEDS = [0, 1, 42, 123456789, 872727272, 892391072, 893000000]
K = 250
FORMATS = {"prime": (20, 40, 2), "binary": (5, 17, 8)}
T_VALS = [0, 42, 123456789]
SUBN = [1, 2, 17]


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"FAIL: command rc={p.returncode}: {cmd}\n{p.stderr}")
    return p.stdout


def draws(py, path, t, k):
    cmd = ([sys.executable] if py else []) + [path, "draws", str(t), str(k)]
    return [int(x, 16) for x in run(cmd).split()]


def cand(py, path, t, per, shift, width, n):
    cmd = ([sys.executable] if py else []) + [path, "cand", str(t), str(per), str(shift), str(width), str(n)]
    return run(cmd).strip().upper()


def scan(py, path, t, per, shift, width, target, nmax):
    cmd = ([sys.executable] if py else []) + [path, "scan", str(t), str(per), str(shift), str(width), target, str(nmax)]
    out = run(cmd).strip()
    return None if out == "NONE" else int(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e1", required=True)
    ap.add_argument("--e1w", required=True)
    ap.add_argument("--e2", required=True)
    ap.add_argument("--json")
    a = ap.parse_args()

    checks = []

    def add(cid, desc, ok, detail=""):
        checks.append({"id": cid, "desc": desc, "ok": bool(ok), "detail": detail})

    # A + B + C over draws
    ab_ok = True
    range_ok = True
    detail = ""
    for t in SEEDS:
        d1 = draws(False, a.e1, t, K)
        dw = draws(False, a.e1w, t, K)
        d2 = draws(True, a.e2, t, K)
        if d1 != dw:
            ab_ok = False
            detail = f"E1 != E1w at seed {t}"
            break
        if d1 != d2:
            ab_ok = False
            detail = f"E1 != E2 at seed {t}"
            break
        if any(v > 0x7FFFFFFF or v < 0 for v in d1):
            range_ok = False
            detail = f"range violation at seed {t}"
            break
    add("A", f"draws E1 == E1w ({len(SEEDS)} seeds x {K})", ab_ok, detail)
    add("B", f"draws E2 == E1 (same vectors)", ab_ok, detail)
    add("C", "draws range <= 0x7FFFFFFF", range_ok, detail)

    # D: cand equality + scan semantics (brute-force verified), both engines
    d_ok = True
    d_detail = ""
    n_sub = 0
    for fmt, (per, shift, width) in FORMATS.items():
        for t in T_VALS:
            for k in SUBN:
                nmax = k + 3
                c1 = cand(False, a.e1, t, per, shift, width, k)
                c2 = cand(True, a.e2, t, per, shift, width, k)
                n_sub += 1
                if c1 != c2:
                    d_ok = False
                    d_detail = f"cand mismatch {fmt} t={t} n={k}"
                    break
                s1 = scan(False, a.e1, t, per, shift, width, c1, nmax)
                s2 = scan(True, a.e2, t, per, shift, width, c1, nmax)
                if s1 != k or s2 != k:
                    d_ok = False
                    d_detail = f"scan miss {fmt} t={t} k={k} e1={s1} e2={s2}"
                    break
                # mutated target: brute-force expected result, then compare engines
                mut = ("1" if c1[0] == "0" else "0") + c1[1:]
                exp = None
                for m in range(1, nmax + 1):
                    if cand(False, a.e1, t, per, shift, width, m) == mut:
                        exp = m
                        break
                m1 = scan(False, a.e1, t, per, shift, width, mut, nmax)
                m2 = scan(True, a.e2, t, per, shift, width, mut, nmax)
                n_sub += 1
                if m1 != exp or m2 != exp:
                    d_ok = False
                    d_detail = f"scan mutant {fmt} t={t} k={k} exp={exp} e1={m1} e2={m2}"
                    break
            if not d_ok:
                break
        if not d_ok:
            break
    add("D", f"cand/scan equality + semantics ({n_sub} subchecks)", d_ok, d_detail)

    failed = [c for c in checks if not c["ok"]]
    for c in checks:
        print(f"[{c['id']}] {c['desc']}: {'OK' if c['ok'] else 'FAIL'}" + (f" ({c['detail']})" if c["detail"] else ""))
    if failed:
        print("SELFTEST: FAIL")
    else:
        print("SELFTEST: ALL OK")

    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as f:
            json.dump(
                {"checks": checks, "all_ok": not failed, "seeds": SEEDS, "k": K, "formats": FORMATS},
                f,
                indent=2,
                sort_keys=True,
            )
            f.write("\n")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
