# -*- coding: utf-8 -*-
"""H1 floor-refinement extractor -- machine-extracts the refined 18-cell
grid and the C4 five-seed robustness table from the run logs, then emits
the machine-readable artifact and the report section. Numbers are NEVER
retyped by hand; everything below is parsed from the logs.

Frozen output format (reports/AMENDMENT_FLOOR_SPEC.md section 3):
  - p values as EXACT COUNTS k/20000 and as decimals with at least 6
    significant digits; the string "0.0000" is retired;
  - k = 0 is reported as a 95% Clopper-Pearson upper bound, never as a
    measured zero;
  - verdict rules UNCHANGED.

Counts provenance:
  - refined runs carry `# exact_counts = [...]` (spy on np.mean of boolean
    arrays in msaf/gw_h1_floor_refine.py) -> exact integers;
  - sealed logs have no spy; their k is recovered from the printed %.4f p,
    which is exact at n = 2000 (p is a multiple of 5e-4).

Usage:
    python msaf/gw_h1_extract.py                 # full extraction (writes artifacts)
    python msaf/gw_h1_extract.py --sealed-only   # print sealed grid, no writes
    python msaf/gw_h1_extract.py --repro-check A B   # compare two logs (rerun vs sealed)
"""

import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys

from scipy.stats import beta
from scipy.stats import chi2 as chi2dist

SEALED = {
    201: "reports/mont_run_100_100.txt",
    301: "reports/mont_run_100_150.txt",
    401: "msaf/mont_run.txt",
}
REFINED_A = {
    201: "reports/mont_run_20000_100_100.txt",
    301: "reports/mont_run_20000_100_150.txt",
    401: "reports/mont_run_20000_100_200.txt",
}
REFINED_B = {
    20261001: "reports/mont_run_20000_s20261001_100_150.txt",
    20261002: "reports/mont_run_20000_s20261002_100_150.txt",
    20261003: "reports/mont_run_20000_s20261003_100_150.txt",
    20261004: "reports/mont_run_20000_s20261004_100_150.txt",
}
S5 = [20260927, 20261001, 20261002, 20261003, 20261004]
C4 = ("T", 0.5)                     # dim 301, chart T, sigma_u 0.5

CELL_ORDER = [("T", "0.3"), ("T", "0.5"), ("T", "1.0"),
              ("L", "0.3"), ("L", "0.5"), ("L", "1.0")]

CELL_RE = re.compile(
    r"chart (T|L) \([^)]*\)\s+sigma_u (0\.3|0\.5|1\.0) : chi2 = ([0-9.]+)"
    r"\n\s+p_GUE\s+= P\(chi2_GUE\s+>= chi2_obs\) = ([0-9.]+)"
    r"\n\s+p_GOE\s+= P\(chi2_GOE\s+>= chi2_obs\) = ([0-9.]+)[^\n]*"
    r"\n\s+p_Pois\s+= P\(chi2_Pois\s+<= chi2_obs\) = ([0-9.]+)[^\n]*"
    r"\n\s+-> ([A-Z][^\n]*)")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_log(path):
    raw = open(path, "rb").read()
    text = None
    for enc in ("utf-8", "utf-16"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        raise SystemExit("cannot decode %s" % path)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    out = {"path": path, "sha256": sha256_file(path)}

    m = re.search(r"surrogate samples per ensemble = (\d+)\s+seed = (\d+)",
                  text)
    if m:
        out["samples"], out["seed"] = int(m.group(1)), int(m.group(2))
    else:
        m = re.search(r"# samples = (\d+)\s+seed = (\d+)", text)
        out["samples"], out["seed"] = int(m.group(1)), int(m.group(2))

    for key, pat in (
            ("spectrum", r"# spectrum = ([^\n]+)"),
            ("spectrum_sha256", r"# spectrum sha256 = ([0-9a-f]+)"),
            ("instrument", r"# instrument = ([^\n]+)"),
            ("instrument_sha256", r"# instrument sha256 = ([0-9a-f]+)"),
            ("instrument_rev", r"# instrument git revision = ([^\n]+)"),
            ("tag", r"# tag = ([^\n]+)"),
            ("start", r"# start = ([^\n]+)"),
    ):
        m = re.search(pat, text)
        if m:
            out[key] = m.group(1).strip()

    m = re.search(r"# end = ([^\n]+)   elapsed = ([0-9.]+) s   exit = (\S+)",
                  text)
    if m:
        out["end"], out["elapsed_s"], out["exit"] = (
            m.group(1).strip(), float(m.group(2)), m.group(3))

    m = re.search(r"# exact_counts = (\[.*\])\n", text)
    exact = json.loads(m.group(1)) if m else None
    if exact is not None:
        out["exact_counts"] = exact
        out["exact_capture_count"] = len(exact)

    cells = {}
    for i, (chart, su, chi2, pg, pgoe, ppois, verdict) in enumerate(
            CELL_RE.findall(text)):
        key = "%s|%s" % (chart, su)
        rec = {
            "chart": chart,
            "sigma_u": float(su),
            "chi2_obs": float(chi2),
            "p_gue_printed": float(pg),
            "p_goe_printed": float(pgoe),
            "p_pois_printed": float(ppois),
            "verdict_printed": verdict.strip(),
        }
        if exact is not None:
            if len(exact) != 36:
                rec["spy_capture_count"] = len(exact)
            base = 6 * i
            rec["k_gue"] = exact[base + 0][1]
            rec["k_gue_lower"] = exact[base + 1][1]
            rec["k_goe"] = exact[base + 2][1]
            rec["k_pois_upper"] = exact[base + 4][1]
            rec["k_pois"] = exact[base + 5][1]
        else:
            n = out["samples"]
            rec["k_gue"] = int(round(float(pg) * n))
            rec["k_goe"] = int(round(float(pgoe) * n))
            rec["k_pois"] = int(round(float(ppois) * n))
        cells[key] = rec
    out["cells"] = cells
    out["cells_parsed"] = len(cells)

    m = re.search(r"  S1 FINAL(?: \(charts agree\))?: ([^\n]+)", text)
    if m:
        out["s1_final"] = m.group(1).strip()
    m = re.search(r"  S2 FINAL(?: \(all \d+ grid points agree\))?: ([^\n]+)",
                  text)
    if m:
        out["s2_final"] = m.group(1).strip()
    out["r_bar"] = {}
    for chart, rb in re.findall(
            r"S1 chart (T|L) \([^)]*\)\s+r_bar = ([0-9.]+)", text):
        out["r_bar"].setdefault(chart, float(rb))
    return out


def cp95(k, n):
    """95% Clopper-Pearson interval.

    0 < k < n: standard two-sided interval. k = 0: the frozen spec
    (section 3) requires the one-sided 95% upper bound 1 - 0.05^(1/n)
    (rule of three), labelled as a bound, never as a measured zero.
    k = n: upper bound is exactly 1.0.
    """
    if k == 0:
        return 0.0, 1.0 - 0.05 ** (1.0 / n)
    if k == n:
        return float(beta.ppf(0.025, n, 1)), 1.0
    lo = float(beta.ppf(0.025, k, n - k + 1))
    hi = float(beta.ppf(0.975, k + 1, n - k))
    return lo, hi


def p6(k, n):
    """Decimal string with 6 significant digits; None for k = 0 (bound)."""
    return None if k == 0 else "%.5e" % (k / n)


def verdict_from_k(k_gue, k_pois, n):
    p_g = k_gue / n
    p_p = k_pois / n
    if p_g >= 0.05 and p_p < 0.05:
        return "CONSISTENT WITH MONTGOMERY/GUE, DISTINGUISHABLE FROM POISSON"
    if p_g >= 0.05 and p_p >= 0.05:
        return "NO DISCRIMINATION AT N=401"
    return "INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION"


def classify_c4(ks, n=20000):
    total = sum(ks)
    N = n * len(ks)
    p_hat = total / N
    per = [k / n for k in ks]
    e = n * p_hat
    stat = 0.0
    # degenerate e = 0 or e = n: every count identical; stat = 0 by convention
    if 0.0 < e < n:
        for k in ks:
            stat += (k - e) ** 2 / e + ((n - k) - (n - e)) ** 2 / (n - e)
    p_hom = float(chi2dist.sf(stat, len(ks) - 1))
    if p_hom < 0.01:
        cls = ("NOT STABLE (homogeneity rejected at alpha = 0.01; "
               "dispersion-dominated)")
    elif p_hat < 0.010:
        cls = "NOT STABLE (pooled p_hat < 0.010)"
    elif 0.010 <= p_hat <= 0.045 and all(0.002 <= p <= 0.060 for p in per):
        cls = "STABLE OFF-FLOOR"
    else:
        cls = "MIXED"
    return {"k": ks, "n_per_seed": n, "pooled_k": total, "pooled_n": N,
            "p_hat": p_hat, "per_seed_p": per,
            "pooled_cp95": cp95(total, N), "homogeneity_stat": stat,
            "homogeneity_p": p_hom, "classification": cls}


def fmt_cp(lo, hi):
    return "[%.5e, %.5e]" % (lo, hi)


def p_field(k, n):
    if k == 0:
        _, hi = cp95(0, n)
        return "0/%d (p < %.5e, 95%% CP upper bound)" % (n, hi)
    return "%d/%d (%.5e)" % (k, n, k / n)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sealed-only", action="store_true")
    ap.add_argument("--repro-check", nargs=2, metavar=("LOG_A", "LOG_B"))
    args = ap.parse_args(argv[1:])

    if args.repro_check:
        a = parse_log(args.repro_check[0])
        b = parse_log(args.repro_check[1])
        print("A:", a["path"], "samples", a["samples"], "seed", a["seed"])
        print("B:", b["path"], "samples", b["samples"], "seed", b["seed"])
        fails = 0
        for key in sorted(a["cells"]):
            ca, cb = a["cells"][key], b["cells"][key]
            for field in ("chi2_obs", "p_gue_printed", "p_goe_printed",
                          "p_pois_printed", "verdict_printed"):
                if ca[field] != cb[field]:
                    fails += 1
                    print("MISMATCH %s %s: %r vs %r"
                          % (key, field, ca[field], cb[field]))
            if "k_gue" in b and ca["k_gue"] != cb["k_gue"]:
                fails += 1
                print("MISMATCH %s k_gue: %r vs %r"
                      % (key, ca["k_gue"], cb["k_gue"]))
        for field in ("s1_final", "s2_final"):
            if a.get(field) != b.get(field):
                fails += 1
                print("MISMATCH %s: %r vs %r" % (field, a.get(field),
                                                 b.get(field)))
        if a.get("r_bar") != b.get("r_bar"):
            fails += 1
            print("MISMATCH r_bar: %r vs %r" % (a.get("r_bar"), b.get("r_bar")))
        print("REPRO CHECK:", "PASS" if fails == 0 else "FAIL (%d)" % fails)
        return 0 if fails == 0 else 1

    sealed = {dim: parse_log(p) for dim, p in SEALED.items()}
    if args.sealed_only:
        for dim, log in sealed.items():
            print("== sealed dim %d (%s), n=%d ==" % (dim, log["path"],
                                                      log["samples"]))
            for key in sorted(log["cells"]):
                c = log["cells"][key]
                print("  %s chi2 %.4f  k_GUE %d/%d  k_Pois %d/%d  %s"
                      % (key, c["chi2_obs"], c["k_gue"], log["samples"],
                         c["k_pois"], log["samples"],
                         c["verdict_printed"][:40]))
        return 0

    refined = {}
    for dim, path in REFINED_A.items():
        import os
        if os.path.exists(path):
            refined[("A", dim)] = parse_log(path)
    for seed, path in REFINED_B.items():
        import os
        if os.path.exists(path):
            refined[("B", seed)] = parse_log(path)

    grid = []
    for dim in (201, 301, 401):
        log = refined.get(("A", dim))
        sl = sealed[dim]
        for chart, su in CELL_ORDER:
            key = "%s|%s" % (chart, su)
            if log is None or key not in log.get("cells", {}):
                grid.append({"dim": dim, "chart": chart,
                             "sigma_u": float(su), "status": "missing"})
                continue
            c = log["cells"][key]
            s = sl["cells"][key]
            n = log["samples"]
            lo, hi = cp95(c["k_gue"], n)
            lo_p, hi_p = cp95(c["k_pois"], n)
            rec = {
                "dim": dim, "chart": chart, "sigma_u": float(su),
                "chi2_obs": c["chi2_obs"],
                "k_gue": c["k_gue"], "n": n,
                "p_gue": p6(c["k_gue"], n), "cp95_gue": [lo, hi],
                "k_pois": c["k_pois"],
                "p_pois": p6(c["k_pois"], n), "cp95_pois": [lo_p, hi_p],
                "verdict_printed": c["verdict_printed"],
                "verdict_recomputed": verdict_from_k(c["k_gue"], c["k_pois"],
                                                     n),
                "sealed_k_gue": s["k_gue"], "sealed_n": sl["samples"],
                "sealed_p_gue": s["p_gue_printed"],
                "sealed_chi2": s["chi2_obs"],
                "log": log["path"], "seed": log["seed"],
            }
            grid.append(rec)

    c4 = None
    log301 = refined.get(("A", 301))
    if log301 is not None and "T|0.5" in log301.get("cells", {}):
        ks = [log301["cells"]["T|0.5"]["k_gue"]]
        seeds_present = [20260927]
        for seed in (20261001, 20261002, 20261003, 20261004):
            blog = refined.get(("B", seed))
            if blog is None or "T|0.5" not in blog.get("cells", {}):
                continue  # missing or still-running: array stays INCOMPLETE
            ks.append(blog["cells"]["T|0.5"]["k_gue"])
            seeds_present.append(seed)
        if len(ks) == 5:
            c4 = classify_c4(ks)
            c4["seeds"] = seeds_present
            c4["per_seed_cp95"] = [cp95(k, 20000) for k in ks]
            c4["canonical_chi2"] = log301["cells"]["T|0.5"]["chi2_obs"]
            c4["canonical_p_gue"] = p6(ks[0], 20000)

    manifest = {
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "repo_head": subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip(),
        "extractor_sha256": sha256_file(__file__),
        "sealed_logs": {str(k): v["sha256"] for k, v in sealed.items()},
        "refined_logs": {("%s_%s" % k): v["sha256"]
                         for k, v in refined.items()},
    }

    out = {"spec": "reports/AMENDMENT_FLOOR_SPEC.md",
           "grid": grid, "c4_array": c4, "manifest": manifest}
    with open("reports/gw_h1_floor_refine.json", "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")

    target_map = {(201, "T", "0.3"): "C1", (301, "T", "0.3"): "C2",
                  (401, "T", "0.3"): "C3", (301, "T", "0.5"): "C4"}
    lines = []
    lines.append("## Refined grid (A) -- 20000 surrogates per ensemble, "
                 "seed 20260927")
    lines.append("")
    lines.append("Target cells (pre-registered, spec section 2): C1 = "
                 "201|T|0.3, C2 = 301|T|0.3, C3 = 401|T|0.3, C4 = 301|T|0.5. "
                 "For these four cells the refined values SUPERSEDE the "
                 "sealed values; sealed columns remain visible, never edited.")
    lines.append("")
    lines.append("| cell | dim | chart | sigma_u | chi2_obs | k_GUE/20000 | "
                 "p_GUE | CP95 GUE | k_Pois/20000 | CP95 Pois | verdict | "
                 "sealed k/2000 | sealed p_GUE |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for rec in grid:
        cell_id = target_map.get(
            (rec["dim"], rec["chart"], "%.1f" % rec["sigma_u"]), "")
        if rec.get("status") == "missing":
            lines.append("| %s | %d | %s | %.1f | MISSING"
                         % (cell_id, rec["dim"], rec["chart"],
                            rec["sigma_u"]) + " |" * 9)
            continue
        lines.append("| %s | %d | %s | %.1f | %.4f | %d/20000 | %s | %s | "
                     "%d/20000 | %s | %s | %d/2000 | %.4f |"
                     % (cell_id, rec["dim"], rec["chart"], rec["sigma_u"],
                        rec["chi2_obs"], rec["k_gue"],
                        p_field(rec["k_gue"], rec["n"]),
                        fmt_cp(*rec["cp95_gue"]), rec["k_pois"],
                        fmt_cp(*rec["cp95_pois"]),
                        rec["verdict_printed"], rec["sealed_k_gue"],
                        rec["sealed_p_gue"]))
    lines.append("")
    if c4 is not None:
        lines.append("## Robustness array (B) -- C4 (dim 301, chart T, "
                     "sigma_u 0.5), 5 seeds")
        lines.append("")
        lines.append("| seed | k/20000 | p_hat_i | CP95 |")
        lines.append("|---|---|---|---|")
        for seed, k, cp in zip(c4["seeds"], c4["k"], c4["per_seed_cp95"]):
            lines.append("| %d | %d/20000 | %.5e | %s |"
                         % (seed, k, k / 20000, fmt_cp(*cp)))
        lines.append("")
        lines.append("Pooled: %d/100000 (p_hat = %.5e), CP95 %s; "
                     "homogeneity chi2 = %.4f, p = %.5e"
                     % (c4["pooled_k"], c4["p_hat"],
                        fmt_cp(*c4["pooled_cp95"]),
                        c4["homogeneity_stat"], c4["homogeneity_p"]))
        lines.append("")
        lines.append("Frozen decision tree classification: **%s**"
                     % c4["classification"])
        lines.append("")
        if not c4["classification"].startswith("STABLE"):
            lines.append("C4 flagged resolution-sensitive per frozen spec "
                         "section 4; the verdict grid recomputation still uses "
                         "the canonical 20000 value (number of record).")
            lines.append("")
    else:
        lines.append("## Robustness array (B) -- INCOMPLETE")
        lines.append("")
    with open("reports/h1_floor_refine_section.md", "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")

    print("wrote reports/gw_h1_floor_refine.json")
    print("wrote reports/h1_floor_refine_section.md")
    print("grid cells:", len(grid), " C4 array complete:",
          c4 is not None)
    for rec in grid:
        if rec.get("status") != "missing":
            if rec["verdict_printed"] != rec["verdict_recomputed"]:
                print("VERDICT DISAGREEMENT (k-based vs printed):",
                      rec["dim"], rec["chart"], rec["sigma_u"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))


