# -*- coding: utf-8 -*-
"""C4 seeds10 extension -- machine-extracts the S10 robustness array.

Pre-registration (committed and pushed BEFORE the first new draw; seed
identities and the frozen analysis rules are declared there):
    reports/C4_SEEDS10_PREREG_2026-10-17.md

Scope: EXTENDS the C4 robustness array of the frozen H1 amendment
(reports/AMENDMENT_FLOOR_SPEC.md section 4, five seeds S5) from 5 to 10
seeds. No sealed artifact is modified. The five original k values are
re-parsed from the original logs and HARD cross-checked against the sealed
artifact reports/gw_h1_floor_refine.json (must match exactly); the five new
k values are parsed from the new logs. All arithmetic (Clopper-Pearson,
homogeneity chi-square, frozen decision tree) is imported unchanged from the
sealed extractor msaf/gw_h1_extract.py -- never retyped.

Outputs (new files only; written by --write after all five new logs exist):
    reports/gw_h1_c4_seeds10.json     machine artifact (all numbers parsed)
    reports/h1_c4_seeds10_section.md  markdown section for the dated report

Usage:
    python msaf/gw_h1_c4_seeds10.py           # status + sealed cross-check
    python msaf/gw_h1_c4_seeds10.py --write   # full extraction + write
"""

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

try:
    from msaf.gw_h1_extract import (C4, REFINED_A, REFINED_B, S5, classify_c4,
                                    cp95, fmt_cp, parse_log, p6)
except ImportError:                      # `python msaf/gw_h1_c4_seeds10.py`
    from gw_h1_extract import (C4, REFINED_A, REFINED_B, S5, classify_c4,
                               cp95, fmt_cp, parse_log, p6)

MODULE_PATH = os.path.abspath(__file__)
ROOT = os.path.dirname(_HERE)
REPORTS = os.path.join(ROOT, "reports")

REFINE_JSON = os.path.join(REPORTS, "gw_h1_floor_refine.json")
PREREG_DOC = os.path.join(REPORTS, "C4_SEEDS10_PREREG_2026-10-17.md")
S10_JSON = os.path.join(REPORTS, "gw_h1_c4_seeds10.json")
S10_SECTION = os.path.join(REPORTS, "h1_c4_seeds10_section.md")

NEW_SEEDS = [20261005, 20261006, 20261007, 20261008, 20261009]
S10 = list(S5) + NEW_SEEDS
OLD_SEEDS = [20260927, 20261001, 20261002, 20261003, 20261004]

N_PER_SEED = 20000
C4_KEY = "%s|%.1f" % C4                  # "T|0.5" -- the frozen C4 cell

# Pins for the new logs (must equal the sealed 2026-10-16 batch's values).
INSTRUMENT_SHA256 = ("072910f232b15768ba35e14d7cc6aaf4fe1ee174dc45b65429460f791"
                     "196e1d5")
SPECTRUM_SHA256 = ("8fded8394f0ab4e8ed83f537609d313d0d50eef42f09214c30d1cfcd9"
                   "94d161d")

SEALED_FIELDS = ("seeds", "k", "n_per_seed", "pooled_k", "pooled_n", "p_hat",
                 "pooled_cp95", "per_seed_cp95", "homogeneity_stat",
                 "homogeneity_p", "classification")


def sha256_lf(path):
    with open(path, "rb") as fh:
        data = fh.read()
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


def old_log_path(seed):
    if seed == OLD_SEEDS[0]:
        return os.path.join(ROOT, REFINED_A[301])
    return os.path.join(ROOT, REFINED_B[seed])


def new_log_path(seed):
    return os.path.join(REPORTS, "mont_run_20000_s%d_100_150.txt" % seed)


def load_sealed():
    with open(REFINE_JSON, encoding="utf-8") as fh:
        return json.load(fh)


def _close(a, b, rel_tol=1e-12):
    scale = max(abs(a), abs(b), 1e-300)
    return abs(a - b) <= rel_tol * scale


def crosscheck_old5():
    """Re-parse the five original logs; must equal the sealed artifact."""
    sealed = load_sealed()["c4_array"]
    ks = [parse_log(old_log_path(s))["cells"][C4_KEY]["k_gue"]
          for s in OLD_SEEDS]
    rec = classify_c4(ks)
    cp = [cp95(k, N_PER_SEED) for k in ks]
    checks = {
        "k_match": ks == sealed["k"],
        "pooled_k_match": rec["pooled_k"] == sealed["pooled_k"],
        "pooled_n_match": rec["pooled_n"] == sealed["pooled_n"],
        "p_hat_match": _close(rec["p_hat"], sealed["p_hat"]),
        "homogeneity_stat_match": _close(rec["homogeneity_stat"],
                                         sealed["homogeneity_stat"]),
        "homogeneity_p_match": _close(rec["homogeneity_p"],
                                      sealed["homogeneity_p"], 1e-9),
        "classification_match": (rec["classification"]
                                 == sealed["classification"]),
        "pooled_cp95_match": all(_close(a, b) for a, b in
                                 zip(rec["pooled_cp95"],
                                     sealed["pooled_cp95"])),
        "per_seed_cp95_match": all(_close(a, b) for pair_new, pair_old in
                                   zip(cp, sealed["per_seed_cp95"])
                                   for a, b in zip(pair_new, pair_old)),
    }
    return {"all_match": all(checks.values()), "checks": checks,
            "k_reparsed": ks, "seeds": list(OLD_SEEDS)}


def extract_new():
    """Parse the five new logs; None while any of them is still missing."""
    ks = []
    metas = {}
    for seed in NEW_SEEDS:
        path = new_log_path(seed)
        if not os.path.exists(path):
            return None
        log = parse_log(path)
        bad = []
        if log.get("samples") != N_PER_SEED:
            bad.append("samples")
        if log.get("seed") != seed:
            bad.append("seed")
        if log.get("instrument_sha256") != INSTRUMENT_SHA256:
            bad.append("instrument_sha256")
        if log.get("spectrum_sha256") != SPECTRUM_SHA256:
            bad.append("spectrum_sha256")
        if log.get("exit") != "0":
            bad.append("exit")
        if log.get("exact_capture_count") != 36:
            bad.append("spy captures")
        if log.get("cells_parsed") != 6:
            bad.append("cells_parsed")
        if C4_KEY not in log.get("cells", {}):
            bad.append("C4 cell")
        if not all(n == N_PER_SEED for n, _ in log.get("exact_counts", [])):
            bad.append("capture sizes")
        if bad:
            raise SystemExit("new log failed guards (%s): %s"
                             % (", ".join(bad), rel(path)))
        ks.append(log["cells"][C4_KEY]["k_gue"])
        metas[str(seed)] = {
            "log": rel(path), "sha256_lf": sha256_lf(path),
            "tag": log.get("tag"), "start": log.get("start"),
            "end": log.get("end"), "elapsed_s": log.get("elapsed_s"),
            "exact_capture_count": log.get("exact_capture_count"),
        }
    return ks, metas


def prereg_commit():
    """First commit that ADDED the pre-registration doc (hash, committer ISO)."""
    try:
        out = subprocess.run(
            ["git", "-C", ROOT, "log", "--diff-filter=A", "-1",
             "--format=%H %cI", "--", rel(PREREG_DOC)],
            capture_output=True, text=True, timeout=60)
        text = out.stdout.strip()
        if not text:
            return None, None
        commit, stamp = text.split()
        return commit, stamp
    except Exception:
        return None, None


def prereg_order_check(metas, stamp):
    if stamp is None:
        return {"status": "SKIPPED (no pre-registration commit time available)"}
    commit_time = datetime.datetime.fromisoformat(
        stamp).astimezone().replace(tzinfo=None)
    starts = {s: datetime.datetime.fromisoformat(m["start"])
              for s, m in metas.items()}
    first = min(starts.values())
    ok = all(t >= commit_time for t in starts.values())
    return {"status": "PASS" if ok else "FAIL",
            "prereg_commit_time_local": commit_time.isoformat(
                timespec="seconds"),
            "first_new_run_start": first.isoformat(timespec="seconds"),
            "note": "all new runs must start AFTER the pre-registration "
                    "commit (anti-cocoklogi ordering)"}


def build():
    sealed = load_sealed()
    cc = crosscheck_old5()
    if not cc["all_match"]:
        raise SystemExit("SEALED CROSS-CHECK FAILED: %s"
                         % json.dumps(cc["checks"], indent=2))
    new = extract_new()
    commit, stamp = prereg_commit()
    out = {
        "preregistration": {
            "doc": rel(PREREG_DOC),
            "sha256_lf": (sha256_lf(PREREG_DOC)
                          if os.path.exists(PREREG_DOC) else None),
            "commit": commit,
        },
        "base": {
            "artifact": rel(REFINE_JSON),
            "sha256_lf": sha256_lf(REFINE_JSON),
            "sealed_c4_array": {f: sealed["c4_array"][f]
                                for f in SEALED_FIELDS},
            "reparse_crosscheck": cc,
        },
        "extension": None,
        "manifest": {
            "generated": datetime.datetime.now().isoformat(timespec="seconds"),
            "repo_head": subprocess.run(
                ["git", "-C", ROOT, "rev-parse", "HEAD"],
                capture_output=True, text=True).stdout.strip(),
            "tool": rel(MODULE_PATH),
            "tool_sha256_lf": sha256_lf(MODULE_PATH),
            "instrument_sha256": INSTRUMENT_SHA256,
            "spectrum_sha256": SPECTRUM_SHA256,
            "n_per_seed": N_PER_SEED,
            "new_logs": None,
            "prereg_order_check": None,
        },
    }
    if new is not None:
        new_ks, metas = new
        ks10 = cc["k_reparsed"] + new_ks
        rec = classify_c4(ks10)
        out["extension"] = {
            "seeds": S10,
            "new_seeds": list(NEW_SEEDS),
            "k": ks10,
            "n_per_seed": N_PER_SEED,
            "per_seed_p": [k / N_PER_SEED for k in ks10],
            "per_seed_cp95": [list(cp95(k, N_PER_SEED)) for k in ks10],
            "pooled_k": rec["pooled_k"],
            "pooled_n": rec["pooled_n"],
            "p_hat": rec["p_hat"],
            "pooled_cp95": list(rec["pooled_cp95"]),
            "homogeneity_stat": rec["homogeneity_stat"],
            "homogeneity_df": len(ks10) - 1,
            "homogeneity_p": rec["homogeneity_p"],
            "classification": rec["classification"],
            "number_of_record": {
                "k": ks10[0], "n": N_PER_SEED,
                "p": p6(ks10[0], N_PER_SEED),
                "note": "UNCHANGED: canonical seed 20260927; the S10 pooled "
                        "result is the enlarged robustness statement only",
            },
        }
        out["manifest"]["new_logs"] = metas
        out["manifest"]["prereg_order_check"] = prereg_order_check(metas,
                                                                   stamp)
    return out


def render_section(out):
    ext = out["extension"]
    base = out["base"]
    order = out["manifest"]["prereg_order_check"]["status"]
    lines = ["## C4 robustness array extension (S10) -- dim 301, chart T, "
             "sigma_u 0.5", ""]
    lines.append("Pre-registration: `reports/C4_SEEDS10_PREREG_2026-10-17.md` "
                 "(commit %s; ordering check: %s)."
                 % (out["preregistration"]["commit"], order))
    lines.append("")
    lines.append("| seed | k/20000 | p_hat_i | CP95 | segment |")
    lines.append("|---|---|---|---|---|")
    for i, (seed, k, cp) in enumerate(zip(ext["seeds"], ext["k"],
                                          ext["per_seed_cp95"])):
        seg = "S5 (sealed)" if i < len(OLD_SEEDS) else "S10 (new)"
        lines.append("| %d | %d/20000 | %.5e | %s | %s |"
                     % (seed, k, k / 20000, fmt_cp(*cp), seg))
    lines.append("")
    lines.append("Pooled (S10, 10 seeds): %d/%d (p_hat = %.5e), CP95 %s"
                 % (ext["pooled_k"], ext["pooled_n"], ext["p_hat"],
                    fmt_cp(*ext["pooled_cp95"])))
    lines.append("")
    lines.append("Homogeneity: Pearson chi2 = %.4f, df = %d, p = %.5e"
                 % (ext["homogeneity_stat"], ext["homogeneity_df"],
                    ext["homogeneity_p"]))
    lines.append("")
    lines.append("Frozen decision tree classification: **%s**"
                 % ext["classification"])
    lines.append("")
    if not ext["classification"].startswith("STABLE"):
        lines.append("C4 stays flagged resolution-sensitive per frozen spec "
                     "section 4; the verdict grid recomputation still uses "
                     "the canonical 20000 value (number of record).")
        lines.append("")
    lines.append("Number of record (UNCHANGED): %d/20000 = %s (canonical seed "
                 "20260927)." % (ext["number_of_record"]["k"],
                                  ext["number_of_record"]["p"]))
    lines.append("")
    lines.append("Old five seeds: re-parsed from the original logs and "
                 "cross-checked against the sealed artifact "
                 "(`reports/gw_h1_floor_refine.json`, sha256_lf %s); "
                 "cross-check %s." % (base["sha256_lf"], "PASS"
                                      if base["reparse_crosscheck"]["all_match"]
                                      else "FAIL"))
    return "\n".join(lines) + "\n"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="write the S10 artifacts (needs all five new logs)")
    args = ap.parse_args(argv[1:])
    out = build()
    cc = out["base"]["reparse_crosscheck"]
    print("sealed cross-check (old 5 re-parsed vs artifact):",
          "PASS" if cc["all_match"] else "FAIL")
    if not cc["all_match"]:
        print(json.dumps(cc["checks"], indent=2))
    present = [s for s in NEW_SEEDS if os.path.exists(new_log_path(s))]
    print("new logs present: %d/5 %s" % (len(present), present))
    if out["extension"] is None:
        print("extension: INCOMPLETE (artifacts not written)")
        return 0
    ext = out["extension"]
    print("S10 pooled: %d/%d (p_hat = %.5e), CP95 %s"
          % (ext["pooled_k"], ext["pooled_n"], ext["p_hat"],
             fmt_cp(*ext["pooled_cp95"])))
    print("homogeneity: chi2 = %.4f, df = %d, p = %.5e"
          % (ext["homogeneity_stat"], ext["homogeneity_df"],
             ext["homogeneity_p"]))
    print("classification:", ext["classification"])
    print("prereg order:", out["manifest"]["prereg_order_check"]["status"])
    if args.write:
        if out["manifest"]["prereg_order_check"]["status"] == "FAIL":
            raise SystemExit("PREREG ORDER CHECK FAILED -- refusing to write")
        with open(S10_JSON, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=2)
            fh.write("\n")
        with open(S10_SECTION, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(render_section(out))
        print("wrote", rel(S10_JSON))
        print("wrote", rel(S10_SECTION))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
