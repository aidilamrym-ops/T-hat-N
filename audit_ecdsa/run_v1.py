#!/usr/bin/env python3
"""V1 orchestrator: run audit items I2..I6 against the frozen seeds manifest and
write one JSON per item. Engine outputs come ONLY via engine_e1 (compiled C
binary) and engine_e2 (pure Python); comparisons are exact (hex, ci).

Does not modify anything except the --out file.

Usage: run_v1.py {i2|i3|i4|i5|i6} --manifest M [--e1 E1] [--e2 E2] [--out OUT]
"""
import argparse
import datetime
import fractions
import json
import math
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"FAIL: command rc={p.returncode}: {cmd}\n{p.stderr}")
    return p.stdout.strip()


def e1_cand(path, t, per, shift, width, n):
    return run([path, "cand", str(t), str(per), str(shift), str(width), str(n)]).upper()


def e2_cand(path, t, per, shift, width, n):
    return run([sys.executable, path, "cand", str(t), str(per), str(shift), str(width), str(n)]).upper()


def e1_scan(path, t, per, shift, width, target, nmax):
    out = run([path, "scan", str(t), str(per), str(shift), str(width), target, str(nmax)])
    return None if out == "NONE" else int(out)


def e2_scan(path, t, per, shift, width, target, nmax):
    out = run([sys.executable, path, "scan", str(t), str(per), str(shift), str(width), target, str(nmax)])
    return None if out == "NONE" else int(out)


def label3(bools):
    if all(bools):
        return "MATCH"
    if not any(bools):
        return "MISMATCH"
    return "PARTIAL"


def rows_of_kind(man, kind):
    return [r for r in man["rows"] if r["kind"] == kind and r["role"] == "reproduce"]


def do_i2i3(mode, man, a, kind):
    rows_out = []
    for r in rows_of_kind(man, kind):
        t, per, shift, width, n = r["seed_arg"], r["per"], r["shift"], r["width"], r["n"]
        std = r["std_hex"]
        c1 = e1_cand(a.e1, t, per, shift, width, n)
        c2 = e2_cand(a.e2, t, per, shift, width, n)
        s1 = e1_scan(a.e1, t, per, shift, width, std, n)
        s2 = e2_scan(a.e2, t, per, shift, width, std, n)
        match_std = c1 == std and c2 == std
        rows_out.append(
            {
                "id": r["id"],
                "curve": r["curve"],
                "t_utc": r["t_utc"],
                "t_epoch": r["t_epoch"],
                "seed_arg": r["seed_arg"],
                "n": n,
                "per": per,
                "shift": shift,
                "width": width,
                "std_hex": std,
                "std_source": r["std_source"],
                "claim_hex": r["claim_hex"],
                "e1_cand": c1,
                "e2_cand": c2,
                "e1_scan": s1,
                "e2_scan": s2,
                "match_std_e1": c1 == std,
                "match_std_e2": c2 == std,
                "match_claim_e1": (c1 == r["claim_hex"]) if r["claim_hex"] else None,
                "first_at_n": (s1 == n and s2 == n),
                "label": "MATCH" if match_std else "MISMATCH",
            }
        )
    item = "I2" if kind == "prime" else "I3"
    n_match = sum(1 for r in rows_out if r["label"] == "MATCH")
    out = {
        "item": item,
        "kind": kind,
        "rows": rows_out,
        "summary": {
            "n_rows": len(rows_out),
            "n_match": n_match,
            "n_mismatch": len(rows_out) - n_match,
            "all_match_std": n_match == len(rows_out),
            "claim_crosscheck_mismatches": [r["id"] for r in rows_out if r["match_claim_e1"] is False],
            "rows_first_reappearance_not_at_n": [r["id"] for r in rows_out if not r["first_at_n"]],
        },
    }
    return out


def do_i4(man):
    rows = [r for r in man["rows"] if r.get("i4")]
    if len(rows) != 10:
        raise SystemExit(f"I4: expected 10 i4 rows in manifest, got {len(rows)}")
    curves_out = []
    count = 0
    for r in sorted(rows, key=lambda x: x["id"]):
        h = r["std_hex"]
        words = [int(h[i * 8:(i + 1) * 8], 16) for i in range(5)]
        topsy = [w >> 31 for w in words]
        all_zero = all(t == 0 for t in topsy)
        count += 1 if all_zero else 0
        curves_out.append(
            {"id": r["id"], "curve": r["curve"], "words": [f"{w:08X}" for w in words],
             "word_top_bits": topsy, "all_top_bits_zero": all_zero}
        )
    p = fractions.Fraction(1, 32)
    prob = sum(fractions.Fraction(math.comb(10, k)) * p ** k * (1 - p) ** (10 - k) for k in range(4, 11))
    inv = 1 / prob
    one_over_p = float(inv)
    claim_value = 5810
    within_tol = abs(one_over_p - claim_value) <= claim_value * 0.01
    count_ok = count == 4
    sub = {"count_ok": count_ok, "probability_within_tolerance": within_tol}
    return {
        "item": "I4",
        "curves": curves_out,
        "count_all_top_bits_zero": count,
        "expected_count": 4,
        "p_ge_4_exact": f"{prob.numerator}/{prob.denominator}",
        "one_over_p_exact": str(inv),
        "one_over_p": one_over_p,
        "claim_one_over_p": claim_value,
        "tolerance_pct": 1,
        "subchecks": sub,
        "label": label3(list(sub.values())),
    }


def do_i5(man):
    rows = {r["curve"]: r for r in man["rows"]}
    bin_rows = [rows[c] for c in ["B-233", "B-283", "B-409", "B-571"]]
    out_bin = []
    ok_halved = True
    ok_doubled = True
    for r in bin_rows:
        halved_date = datetime.datetime.fromtimestamp(r["seed_arg"], datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        doubled_date = datetime.datetime.fromtimestamp(r["t_epoch"], datetime.timezone.utc).strftime("%Y-%m-%d")
        hf = halved_date.startswith("1984-02-")
        dd = doubled_date == "1998-04-17"
        ok_halved &= hf
        ok_doubled &= dd
        out_bin.append(
            {"id": r["id"], "curve": r["curve"], "t_utc": r["t_utc"], "t_epoch": r["t_epoch"],
             "seed_arg": r["seed_arg"], "halved_date_utc": halved_date, "halved_in_feb1984": hf,
             "doubled_date_utc": doubled_date, "doubled_is_1998_04_17": dd}
        )
    diff = rows["B-233"]["t_epoch"] - rows["P-224"]["t_epoch"]
    days_floor = diff // 86400
    ok_interval = days_floor == 14
    prime = [r for r in man["rows"] if r["kind"] == "prime"]
    mn = min(r["t_epoch"] for r in prime)
    mx = max(r["t_epoch"] for r in prime)
    mn_d = datetime.datetime.fromtimestamp(mn, datetime.timezone.utc).strftime("%Y-%m-%d")
    mx_d = datetime.datetime.fromtimestamp(mx, datetime.timezone.utc).strftime("%Y-%m-%d")
    ok_prime = mn_d >= "1997-05-01" and mx_d <= "1998-04-30"
    sub = {
        "halved_dates_feb1984": ok_halved,
        "doubled_dates_1998_04_17": ok_doubled,
        "interval_b233_p224_floor_days_14": ok_interval,
        "prime_range_may1997_apr1998": ok_prime,
    }
    return {
        "item": "I5",
        "binary": out_bin,
        "interval": {"from": "P-224", "to": "B-233", "from_t_utc": rows["P-224"]["t_utc"],
                     "to_t_utc": rows["B-233"]["t_utc"], "exact_seconds": diff,
                     "floor_days": days_floor},
        "prime_range": {"min_utc": mn_d, "max_utc": mx_d},
        "subchecks": sub,
        "label": label3(list(sub.values())),
    }


def do_i6(man, a):
    rows_out = []
    min_sources = None
    all_agree = True
    for r in man["rows"]:
        srcs = r["sources"]
        hexes = {s["hex"] for s in srcs}
        agree = len(hexes) == 1 and (not r.get("std_hex") or next(iter(hexes)) == r["std_hex"])
        all_agree &= agree
        min_sources = len(srcs) if min_sources is None else min(min_sources, len(srcs))
        rows_out.append({"id": r["id"], "curve": r["curve"], "n_sources": len(srcs),
                         "sources": [s["id"] for s in srcs], "all_agree": agree})
    # rebuild the manifest from frozen captures and compare bytes
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td) / "manifest_rebuilt.json"
        run([sys.executable, str(HERE / "build_manifest.py"), "--quiet",
             "--rows", str(HERE / "v1_rows.tsv"), "--captures", str(HERE / "captures"),
             "--out", str(tmp)])
        rebuilt = tmp.read_bytes()
    frozen = pathlib.Path(a.manifest).read_bytes()
    rebuilt_identical = rebuilt == frozen
    sub = {
        "min_sources_ge_2": (min_sources or 0) >= 2,
        "sources_all_agree_with_manifest": all_agree,
        "rebuild_from_captures_identical": rebuilt_identical,
    }
    return {
        "item": "I6",
        "rows": rows_out,
        "min_sources": min_sources,
        "subchecks": sub,
        "label": label3(list(sub.values())),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["i2", "i3", "i4", "i5", "i6"])
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--e1")
    ap.add_argument("--e2")
    ap.add_argument("--out")
    a = ap.parse_args()
    man = json.loads(pathlib.Path(a.manifest).read_text(encoding="utf-8"))
    if a.mode in ("i2", "i3") and (not a.e1 or not a.e2):
        raise SystemExit(f"{a.mode} requires --e1 and --e2")
    if a.mode == "i2":
        out = do_i2i3("i2", man, a, "prime")
    elif a.mode == "i3":
        out = do_i2i3("i3", man, a, "binary")
    elif a.mode == "i4":
        out = do_i4(man)
    elif a.mode == "i5":
        out = do_i5(man)
    else:
        out = do_i6(man, a)
    text = json.dumps(out, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if a.out:
        pathlib.Path(a.out).write_text(text, encoding="utf-8", newline="\n")
    summary = {k: v for k, v in out.items() if k in ("item", "label", "summary", "subchecks", "count_all_top_bits_zero")}
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
