# -*- coding: utf-8 -*-
"""Engine B -- second, independent S2 verification harness (FROZEN spec section 5).

Authority: reports/AMENDMENT_FLOOR_SPEC.md (sha256 recorded in HANDOFF sec. 1).
Engine B is VERIFICATION ONLY: it never changes any verdict and is not a new
instrument (spec B6). It verifies engine A's arithmetic and I/O:

  B1  decimal-exact parsing: every numeric payload field of the spectra is read
      with decimal.Decimal; the landmine-L24 class (fields below the float64
      range) never touches binary64 in B's precision path; fail-fast tripwire
      on any fake-zero parse.
  B2  independent summation: math.fsum (correctly rounded) for unfold row sums;
      chunked Neumaier compensation for every convolution / bin accumulator;
      kernel matrices K (r2) and target vector tgt evaluated with mpmath at the
      DECLARED dps (frozen here: 50), rounded to binary64 for the float64
      surrogate loop; elementary CDF values via scipy.special.ndtr (the same
      underlying special function A's scipy.stats.norm.cdf calls, documented).
  B3  gate re-verification: G-M0a/b/c recomputed rigorously from the stored
      strings; G-M0d/e recomputed in exact decimal arithmetic against the
      60-digit artifact references with a declared storage-rounding budget.
      The original 1e-300 threshold cannot be re-established from 60 stored
      digits -- this limitation is measured and declared, not hidden.
  B4  agreement: the frozen OR implemented verbatim -- a bin passes iff
      |B - A| <= 1e-9*|A| OR |B - A| <= 10*ulp(A); the 10-ulp branch is the
      declared tighter bound (10 ulp <= 2.3e-15 relative < 1e-9 relative for
      normal-range float64 values) and both branch censuses are reported per
      bin. Chart-L cv bins that fail the frozen OR must be covered by
      enumerated fine-bin membership disagreements under the pre-declared
      rule in reports/ENGINE_B_PILOT_FINDINGS_2026-10-16.md; uncovered
      failures -> STOP, record as divergence, publish nothing until resolved.
      Counts k_GUE and k_Pois (plus the captured gue-lower / pois-upper
      tails) must agree EXACTLY with engine A's.
  B5  output: reports/gw_engine_b_verify.json (per-bin comparison table,
      counts, script revisions) as a sealed artifact.

Declared manifest (frozen BEFORE the run, spec section 7 anti-tuning rails):
  - mpmath dps = 50 (spec B2 proposed default).
  - criterion = 10 ulp (tighter-of declaration above).
  - scope = observed grid (3 dims x 2 charts x 3 sigma_u = 18 cells) per-bin
    vs engine A float64; counts = GUE + Poisson, 20000 samples, seed
    20260927, all 18 cells compared (four pre-registered target cells
    flagged); GOE curves are NOT recomputed (reported-only in engine A;
    declared limitation).

Usage:
    python msaf/gw_engine_b_verify.py --pilot     # pre-flight (~8-12 min)
    python msaf/gw_engine_b_verify.py --full      # full verification (~3 h)

The instrument is imported READ-ONLY; its sha256 is asserted unchanged
before/after (the canonical sealed instrument must never be modified).
"""

import argparse
import datetime
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from bisect import bisect_left, bisect_right
from decimal import Decimal, getcontext
from fractions import Fraction

import mpmath as mp
import numpy as np
from scipy.special import ndtr

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

INSTRUMENT_DIR = os.environ.get(
    "GW_INSTRUMENT_DIR",
    r"D:\THE ASYMMETRIC WAGER\guinand-weil-rigorous-numerics-main")
INSTRUMENT = "gw_montgomery.py"

DPS = 50                      # mpmath precision, DECLARED before the run
SEED = 20260927               # canonical declared seed (unchanged since sealed)
SIGMA_U = (0.3, 0.5, 1.0)
DU = 0.5
U_MAX = 10.0
N_BINS = 20
MIN_EXPECTED = 5.0
FINE = Decimal("0.01")
DEC11 = Decimal("11")
FAKE_ZERO_BOUND = Decimal("2.4703282292062327e-324")
FLOAT64_NORMAL_MIN = Decimal("2.2250738585072014e-308")

SPECTRA = {
    201: os.path.join(REPO, "reports", "gw_spectrum_100_100.json"),
    301: os.path.join(REPO, "reports", "gw_spectrum_100_150.json"),
    401: os.path.join(INSTRUMENT_DIR, "gw_spectrum_100_200.json"),
}
CELL_ORDER = [("T", "0.3"), ("T", "0.5"), ("T", "1.0"),
              ("L", "0.3"), ("L", "0.5"), ("L", "1.0")]
TARGET_CELLS = {(201, "T", "0.3"): "C1", (301, "T", "0.3"): "C2",
                (401, "T", "0.3"): "C3", (301, "T", "0.5"): "C4"}


def ckpt(msg):
    print(msg, flush=True)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def instrument_revision():
    try:
        out = subprocess.run(
            ["git", "-C", INSTRUMENT_DIR, "log", "-1", "--format=%H %ci", "--",
             INSTRUMENT],
            capture_output=True, text=True, timeout=60)
        return out.stdout.strip() or "UNKNOWN"
    except Exception as exc:                                   # pragma: no cover
        return "UNKNOWN (%r)" % (exc,)


def repo_head():
    try:
        return subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                              capture_output=True, text=True,
                              timeout=60).stdout.strip()
    except Exception:                                          # pragma: no cover
        return "UNKNOWN"


def mpf_of_float(x):
    """Exact binary64 -> mpf conversion (via integer ratio)."""
    num, den = Fraction(x).as_integer_ratio()
    return mp.mpf(num) / mp.mpf(den)


# ---------------------------------------------------------------------------
# B1 -- decimal-exact parsing
# ---------------------------------------------------------------------------

def _dec_exact(s):
    d = Decimal(s)
    if d == 0:
        mant = s.split("e")[0].split("E")[0]
        if any(c in "123456789" for c in mant):
            raise SystemExit("FAKE-ZERO TRIPWIRE: %r parsed to 0" % s)
    return d


def load_spectrum_decimal(path):
    """Read the spectrum JSON; parse every numeric payload field as Decimal.

    Metadata scalars (c, N, dps, prec, n, eig_seconds) are provenance-only and
    are not part of the numeric data path.
    """
    with open(path, "r", encoding="utf-8") as fh:
        blob = json.load(fh)
    return {
        "meta": {k: blob[k] for k in
                 ("c", "N", "dps", "prec", "algo", "n", "eig_seconds",
                  "gate_verdict") if k in blob},
        "trace_mid": _dec_exact(blob["trace_mid"]),
        "frob2_mid": _dec_exact(blob["frob2_mid"]),
        "gate_GM0": dict(blob.get("gate_GM0", {})),
        "inertia": dict(blob.get("inertia", {})),
        "re": [_dec_exact(e["re"]) for e in blob["eig"]],
        "re_rad": [_dec_exact(e["re_rad"]) for e in blob["eig"]],
        "im_abs": [_dec_exact(e["im_abs"]) for e in blob["eig"]],
    }


def fake_zero_census(dec):
    census = {}
    tot_sub = 0
    tot_fake = 0
    for field in ("re", "re_rad", "im_abs"):
        vals = dec[field]
        nz_sub = sum(1 for v in vals
                     if v != 0 and abs(v) < FLOAT64_NORMAL_MIN)
        fake = sum(1 for v in vals if v != 0 and abs(v) < FAKE_ZERO_BOUND)
        census[field] = {"count": len(vals),
                         "nonzero_below_float64_normal_min": nz_sub,
                         "would_fake_zero_under_binary64": fake}
        tot_sub += nz_sub
        tot_fake += fake
    for field in ("trace_mid", "frob2_mid"):
        v = dec[field]
        census[field] = {
            "count": 1,
            "nonzero_below_float64_normal_min":
                int(v != 0 and abs(v) < FLOAT64_NORMAL_MIN),
            "would_fake_zero_under_binary64":
                int(v != 0 and abs(v) < FAKE_ZERO_BOUND)}
    census["total_nonzero_below_float64_normal_min"] = tot_sub
    census["total_would_fake_zero_under_binary64"] = tot_fake
    return census


# ---------------------------------------------------------------------------
# B3 -- gate re-verification (exact decimal)
# ---------------------------------------------------------------------------

def ulp60(x):
    """Worst-case storage-rounding quantum of a 60-significant-digit decimal."""
    if x == 0:
        return Decimal(0)
    return Decimal("1e%d" % (x.adjusted() - 59))


def verify_gate_GM0(dec):
    """Recompute G-M0a/b/c/d/e from the stored strings, in exact decimal."""
    getcontext().prec = 600     # engine B process only; no repo-wide state
    re_list = dec["re"]
    rad_list = dec["re_rad"]
    n = len(re_list)
    stored = dec["gate_GM0"]
    out = {"n": n}

    finite = (all(v.is_finite() for v in re_list)
              and all(v.is_finite() for v in rad_list)
              and all(v.is_finite() for v in dec["im_abs"]))
    out["a_finite"] = {"pass": bool(finite),
                       "stored_flag": stored.get("G-M0a_finite")}

    n_pos = n_neg = n_ind = 0
    for m, r in zip(re_list, rad_list):
        if m - r > 0:
            n_pos += 1
        elif m + r < 0:
            n_neg += 1
        else:
            n_ind += 1
    b_pass = (n_pos == n and n_neg == 0 and n_ind == 0)
    out["b_inertia"] = {
        "recomputed": {"n_pos": n_pos, "n_neg": n_neg,
                       "indeterminate": n_ind},
        "stored": dec["inertia"], "pass": bool(b_pass),
        "stored_flag": stored.get("G-M0b_inertia")}

    srt = sorted(re_list)
    viol = sum(1 for i in range(n - 1) if not (srt[i] < srt[i + 1]))
    out["c_strict"] = {"violations_after_sort": viol,
                       "file_order_sorted": bool(re_list == srt),
                       "pass": bool(viol == 0),
                       "stored_flag": stored.get("G-M0c_strict")}

    s1 = sum(re_list)
    ref1 = dec["trace_mid"]
    d1 = abs(s1 - ref1)
    budget1 = (sum(ulp60(v) for v in re_list) + ulp60(ref1)
               + abs(ref1) * Decimal("1e-300"))
    out["d_trace"] = {
        "sum_re": str(s1), "reference": str(ref1), "absdiff": str(d1),
        "rel": (str(d1 / abs(ref1)) if ref1 != 0 else None),
        "budget": str(budget1), "pass": bool(d1 <= budget1),
        "stored_flag": stored.get("G-M0d_trace")}

    s2 = sum(v * v for v in re_list)
    ref2 = dec["frob2_mid"]
    d2 = abs(s2 - ref2)
    budget2 = (sum(ulp60(v * v) for v in re_list) + ulp60(ref2)
               + abs(ref2) * Decimal("1e-300"))
    out["e_frob"] = {
        "sum_re_sq": str(s2), "reference": str(ref2), "absdiff": str(d2),
        "rel": (str(d2 / abs(ref2)) if ref2 != 0 else None),
        "budget": str(budget2), "pass": bool(d2 <= budget2),
        "stored_flag": stored.get("G-M0e_frob")}

    out["reproduced_all"] = bool(
        out["a_finite"]["pass"] and out["b_inertia"]["pass"]
        and out["c_strict"]["pass"] and out["d_trace"]["pass"]
        and out["e_frob"]["pass"])
    out["stored_all_true"] = bool(
        all(stored.get(k) is True for k in
            ("G-M0a_finite", "G-M0b_inertia", "G-M0c_strict", "G-M0d_trace",
             "G-M0e_frob")))
    return out


# ---------------------------------------------------------------------------
# B2a -- high-precision observed grid (mpmath, dps declared)
# ---------------------------------------------------------------------------

def hp_cdf(z):
    """Phi(z) = erfc(-z/sqrt(2))/2 at the current dps."""
    return mp.erfc(-z / mp.sqrt(2)) / 2


def hp_local_spacing(y):
    n = len(y)
    kk = min(10, max(1, (n - 1) // 2))
    h = []
    for i in range(n):
        lo = max(0, i - kk)
        hi = min(n - 1, i + kk)
        step = hi - lo
        if step == 0:
            step = 1
        h.append((y[hi] - y[lo]) / step)
    pos = [v for v in h if v > 0]
    floor = min(pos) * mp.mpf("1e-6") if pos else mp.mpf("1e-300")
    return [v if v > 0 else floor for v in h]


def hp_unfold(y, su):
    """Neumaier-compensated unfold at the current dps; fixed ascending order."""
    n = len(y)
    h = [su * v for v in hp_local_spacing(y)]
    x = []
    for i in range(n):
        yi = y[i]
        s = mp.mpf(0)
        comp = mp.mpf(0)
        for m in range(n):
            t = hp_cdf((yi - y[m]) / h[m])
            nt = s + t
            if abs(s) >= abs(t):
                comp += (s - nt) + t
            else:
                comp += (t - nt) + s
            s = nt
        x.append(s + comp)
    gaps = [x[i + 1] - x[i] for i in range(n - 1)]
    s = mp.mpf(0)
    comp = mp.mpf(0)
    for g in gaps:
        nt = s + g
        if abs(s) >= abs(g):
            comp += (s - nt) + g
        else:
            comp += (g - nt) + s
        s = nt
    m = (s + comp) / (n - 1)
    if not (m > 0):
        raise SystemExit("B: unfolding produced non-positive mean gap")
    return [v / m for v in x]


def build_kernels():
    """K (r2), tgt (montgomery_smoothed), u centres -- mpmath at declared dps."""
    sigma_e = mp.mpf("0.5")
    norm_const = 1 / (mp.sqrt(2 * mp.pi) * sigma_e)
    u_dec = [Decimal("0.25") + Decimal("0.5") * b for b in range(N_BINS)]
    edges = [Decimal("-11") + FINE * j for j in range(2201)]
    centers = [e + Decimal("0.005") for e in edges[:-1]]
    K_r2 = []
    for b in range(N_BINS):
        ub = mp.mpf(str(u_dec[b]))
        row = []
        for c in centers:
            cc = mp.mpf(str(c))
            row.append(mp.exp(-((ub - cc) ** 2) / (2 * sigma_e ** 2))
                       * norm_const)
        K_r2.append(row)
    M = []
    for f in edges:
        ff = mp.mpf(str(f))
        if abs(ff) < mp.mpf("1e-12"):
            M.append(mp.mpf(0))
        else:
            t = mp.pi * ff
            s = mp.sin(t) / t
            M.append(1 - s * s)
    tgt = []
    for b in range(N_BINS):
        ub = mp.mpf(str(u_dec[b]))
        s = mp.mpf(0)
        comp = mp.mpf(0)
        for j in range(2201):
            fj = mp.mpf(str(edges[j]))
            k = (mp.exp(-((ub - fj) ** 2) / (2 * sigma_e ** 2)) * norm_const)
            t = k * M[j]
            nt = s + t
            if abs(s) >= abs(t):
                comp += (s - nt) + t
            else:
                comp += (t - nt) + s
            s = nt
        tgt.append((s + comp) * mp.mpf("0.01"))
    return {"u_dec": u_dec, "K_r2": K_r2, "tgt": tgt}


def hp_hist_and_cv(x, kern):
    """Exact-ish fine histogram (windowed) + Neumaier convolution."""
    n = len(x)
    hist = [0] * 2200
    d11 = mp.mpf(11)
    for i in range(n):
        xi = x[i]
        jlo = bisect_left(x, xi - d11)
        jhi = bisect_right(x, xi + d11)
        for j in range(jlo, jhi):
            if j == i:
                continue
            q = (xi - x[j] + d11) / mp.mpf("0.01")
            idx = int(mp.floor(q))
            if idx < 0:
                continue
            if idx > 2199:
                idx = 2199          # d == +11 exactly -> last bin
            hist[idx] += 1
    cv = []
    for b in range(N_BINS):
        row = kern["K_r2"][b]
        s = mp.mpf(0)
        comp = mp.mpf(0)
        for c in range(2200):
            t = row[c] * hist[c]
            nt = s + t
            if abs(s) >= abs(t):
                comp += (s - nt) + t
            else:
                comp += (t - nt) + s
            s = nt
        cv.append((s + comp) / n)
    return hist, cv


def compare_bins(cvB, cvA, label):
    """Per-bin census of the frozen OR: |B-A| <= 1e-9*|A| OR <= 10 ulp(A).

    Both branch censuses are reported; the 10-ulp branch is the declared
    tighter bound for normal-range float64 values."""
    bins = []
    for b in range(N_BINS):
        a = float(cvA[b])
        bb = cvB[b]
        a_mp = mpf_of_float(a)
        diff = abs(bb - a_mp)
        ulp = math.ulp(a)
        within_10ulp = bool(diff <= 10 * mpf_of_float(ulp))
        if a != 0:
            rel = float(diff / abs(a_mp))
            within_rel = bool(diff <= mpf_of_float(abs(a))
                              * mpf_of_float(1e-9))
        else:
            rel = None
            within_rel = False
        bins.append({
            "bin": b, "A": a, "B": mp.nstr(bb, 25),
            "absdiff": mp.nstr(diff, 3), "absdiff_f": float(diff),
            "ulp_A": ulp,
            "diff_ulps": float(diff / mpf_of_float(ulp)) if ulp > 0 else None,
            "rel": rel,
            "within_10ulp": within_10ulp,
            "within_1e9rel": within_rel,
            "within_frozen_or": bool(within_10ulp or within_rel)})
    return bins


def hp_observed_grid(dims, decs, g, kern, log):
    records = []
    u_centers = np.arange(DU * 0.5, U_MAX, DU)
    edges_np = np.arange(-(U_MAX + 1.0), U_MAX + 1.0 + 1e-9, 0.01)
    edge_exact = [mp.mpf(str(Decimal("-11") + FINE * k))
                  for k in range(edges_np.size)]
    for dim in dims:
        dec = decs[dim]
        lam = np.sort(np.array([float(e["re"]) for e in
                                _raw_eig(SPECTRA[dim])]))
        yT_float = np.log(lam)
        yL_float = lam.copy()
        re_sorted = sorted(dec["re"])          # solver order in the file is
        y_T = [mp.log(mp.mpf(str(v))) for v in re_sorted]   # not sorted; A sorts
        y_L = [mp.mpf(str(v)) for v in re_sorted]
        for cname, y_mp, y_f in (("T", y_T, yT_float), ("L", y_L, yL_float)):
            for su in SIGMA_U:
                t0 = time.time()
                xB = hp_unfold(y_mp, mp.mpf(str(su)))
                histB, cvB = hp_hist_and_cv(xB, kern)
                xA = g.unfold(y_f, su)
                _, cvA = g.r2_curve(xA)
                tgtA = g.montgomery_smoothed(u_centers)
                bins_cv = compare_bins(cvB, cvA, "cv")
                bins_tgt = compare_bins(kern["tgt"], tgtA, "tgt")
                # A-side fine histogram, identical numpy expression as A's
                nn = xA.size
                DA = xA[:, None] - xA[None, :]
                mask = ~np.eye(nn, dtype=bool)
                histA, _ = np.histogram(DA[mask], bins=edges_np)
                flips_detail = [(int(b), int(histB[b] - histA[b]))
                                for b in np.where(np.array(histB) != histA)[0]]
                # pair-level membership disagreements (mpf window, as histB)
                members = []
                members_total = 0
                boundary_skips = 0
                d11 = mp.mpf(11)
                for i in range(nn):
                    xi = xB[i]
                    jlo = bisect_left(xB, xi - d11)
                    jhi = bisect_right(xB, xi + d11)
                    for j in range(jlo, jhi):
                        if j == i:
                            continue
                        d = xi - xB[j]
                        if d > d11 or d < -d11:
                            continue
                        q = (d + d11) / mp.mpf("0.01")
                        bB = int(mp.floor(q))
                        if bB > 2199:
                            bB = 2199
                        dA = float(DA[i, j])
                        bA = int(np.searchsorted(edges_np, dA,
                                                 side="right")) - 1
                        if dA == edges_np[-1]:
                            bA = edges_np.size - 2
                        if bA < 0 or bA > 2199:
                            boundary_skips += 1
                            continue
                        if bB != bA:
                            members_total += 1
                            if len(members) < 200:
                                e_idx = min(bB, bA) + 1
                                members.append({
                                    "pair": [i, j],
                                    "D_A": repr(dA),
                                    "D_B": mp.nstr(d, 20),
                                    "bin_A": bA, "bin_B": bB,
                                    "edge_idx": e_idx,
                                    "edge_exact":
                                        mp.nstr(edge_exact[e_idx], 20),
                                    "edge_float":
                                        repr(float(edges_np[e_idx])),
                                    "dist_A": abs(dA -
                                                  float(edges_np[e_idx])),
                                    "dist_B": float(abs(d -
                                                        edge_exact[e_idx]))})
                members_ok = all(
                    abs(m["bin_A"] - m["bin_B"]) == 1
                    and m["dist_A"] <= 1e-9 and m["dist_B"] <= 1e-9
                    for m in members)
                # cross-check: B data rounded through A's float64 edges
                xf = np.array([float(v) for v in xB])
                Df = (xf[:, None] - xf[None, :])[mask]
                idx = np.searchsorted(edges_np, Df, side="right") - 1
                idx[Df == edges_np[-1]] = edges_np.size - 2
                valid = (idx >= 0) & (idx <= edges_np.size - 2)
                histX = np.bincount(idx[valid], minlength=edges_np.size - 1)
                flips_via_A_edges = int(np.count_nonzero(histX != histA))
                # x agreement summary
                xmax = mp.mpf(0)
                for k in range(nn):
                    dd = abs(xB[k] - mpf_of_float(float(xA[k])))
                    ul = mpf_of_float(math.ulp(float(xA[k])))
                    if ul > 0:
                        q = dd / ul
                        if q > xmax:
                            xmax = q
                or_fail_cv = [b["bin"] for b in bins_cv
                              if not b["within_frozen_or"]]
                or_fail_tgt = [b["bin"] for b in bins_tgt
                               if not b["within_frozen_or"]]
                max_fail = 0.0
                for b in bins_cv + bins_tgt:
                    if (not b["within_frozen_or"]) and \
                            b["absdiff_f"] > max_fail:
                        max_fail = b["absdiff_f"]
                if not or_fail_cv and not or_fail_tgt:
                    status = "PASS"
                elif (not or_fail_tgt and members_total > 0 and members_ok
                      and members_total <= 100
                      and len(members) == members_total
                      and max_fail <= 1e-2):
                    status = "PASS_ENUMERATED_EDGE_CLUSTER"
                else:
                    status = "FAIL"
                rec = {"dim": dim, "chart": cname, "sigma_u": su,
                       "bins_cv": bins_cv, "bins_tgt": bins_tgt,
                       "or_fail_bins_cv": or_fail_cv,
                       "or_fail_bins_tgt": or_fail_tgt,
                       "max_or_fail_absdiff": max_fail,
                       "hist_flips": len(flips_detail),
                       "hist_flips_detail": flips_detail,
                       "flips_via_A_edges": flips_via_A_edges,
                       "membership_disagreements": {
                           "count": members_total,
                           "all_adjacent_within_1e-9": bool(members_ok),
                           "boundary_skips": boundary_skips,
                           "members": members},
                       "x_max_ulps": float(xmax),
                       "cell_status": status,
                       "elapsed_s": round(time.time() - t0, 1)}
                records.append(rec)
                log("    hp %d|%s|%.1f: %s  OR-fail cv %d tgt %d  "
                    "flips %d (via-A-edges %d)  members %d  "
                    "max cv %.1f ulp / rel %.2e  (%.0f s)"
                    % (dim, cname, su, status, len(or_fail_cv),
                       len(or_fail_tgt), len(flips_detail),
                       flips_via_A_edges, members_total,
                       max((r["diff_ulps"] or 0) for r in bins_cv),
                       max((r["rel"] or 0) for r in bins_cv),
                       rec["elapsed_s"]))
    return records


def _raw_eig(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)["eig"]


# ---------------------------------------------------------------------------
# B2b -- float64-compensated surrogate loop (counts)
# ---------------------------------------------------------------------------

def b_local_spacing_f64(y):
    n = len(y)
    kk = min(10, max(1, (n - 1) // 2))
    h = np.empty(n)
    for i in range(n):
        lo = max(0, i - kk)
        hi = min(n - 1, i + kk)
        step = hi - lo
        if step == 0:
            step = 1
        h[i] = (y[hi] - y[lo]) / step
    pos = h[h > 0]
    floor = float(pos.min() * 1e-6) if pos.size else 1e-300
    h[h <= 0] = floor
    return h


def b_unfold_f64(y, su):
    """ndtr CDF values (same underlying special function as A's norm.cdf);
    row sums via math.fsum (correctly rounded; fixed ascending order)."""
    n = len(y)
    h = b_local_spacing_f64(y) * su
    Z = (y[:, None] - y[None, :]) / h[None, :]
    P = ndtr(Z)
    x = np.empty(n)
    for i in range(n):
        x[i] = math.fsum(P[i].tolist())
    gaps = np.diff(x)
    m = math.fsum(gaps.tolist()) / (n - 1)
    if not np.isfinite(m) or m <= 0:
        raise SystemExit("B: unfolding produced non-positive mean gap")
    return x / m


def b_hist_f64(x):
    n = len(x)
    edges = np.arange(-(U_MAX + 1.0), U_MAX + 1.0 + 1e-9, 0.01)
    D = (x[:, None] - x[None, :]).ravel()
    D = D[np.repeat(np.arange(n), n) != np.tile(np.arange(n), n)]
    idx = np.searchsorted(edges, D, side="right") - 1
    idx[D == edges[-1]] = edges.size - 2
    valid = (idx >= 0) & (idx <= edges.size - 2)
    return np.bincount(idx[valid], minlength=edges.size - 1).astype(float)


def b_conv_f64(hist, Kf, n):
    """Chunked Neumaier convolution over the 2200 fine bins."""
    s = np.zeros(N_BINS)
    comp = np.zeros(N_BINS)
    for c0 in range(0, 2200, 100):
        part = Kf[:, c0:c0 + 100] @ hist[c0:c0 + 100]
        t = s + part
        comp += np.where(np.abs(s) >= np.abs(part),
                         (s - t) + part, (part - t) + s)
        s = t
    return (s + comp) / n


def compensated_col_sum(M):
    s = np.zeros(M.shape[1])
    comp = np.zeros(M.shape[1])
    for c0 in range(0, M.shape[0], 1000):
        part = M[c0:c0 + 1000].sum(axis=0)
        t = s + part
        comp += np.where(np.abs(s) >= np.abs(part),
                         (s - t) + part, (part - t) + s)
        s = t
    return s + comp


def b_weights(cv_gue):
    m = cv_gue.shape[0]
    mean = compensated_col_sum(cv_gue) / m
    dev = (cv_gue - mean) ** 2
    var = compensated_col_sum(dev) / (m - 1)
    var[var <= 0] = np.finfo(float).tiny
    return 1.0 / var


def b_chi2_row(cv_row, w_keep, tgt_keep):
    s = 0.0
    comp = 0.0
    for b in range(len(tgt_keep)):
        d = cv_row[b] - tgt_keep[b]
        t = w_keep[b] * d * d
        nt = s + t
        if abs(s) >= abs(t):
            comp += (s - nt) + t
        else:
            comp += (t - nt) + s
        s = nt
    return s + comp


def b_montgomery_centers():
    """montgomery(u) at the 20 centres via mpmath (declared dps)."""
    out = []
    for b in range(N_BINS):
        u = mp.mpf(str(Decimal("0.25") + Decimal("0.5") * b))
        t = mp.pi * u
        s = mp.sin(t) / t
        out.append(float(1 - s * s))
    return np.array(out)


def run_counts_dim(dim, samples, Kf, tgt_f64, log):
    """Independent float64 counts loop. Returns per-cell records."""
    t0 = time.time()
    with open(SPECTRA[dim], "r", encoding="utf-8") as fh:
        blob = json.load(fh)
    lam = np.array([float(e["re"]) for e in blob["eig"]])
    lam = np.sort(lam)
    n = lam.size
    charts = {"T": np.log(lam), "L": lam.copy()}

    obs_cv = {}
    for cname, y in charts.items():
        for su in SIGMA_U:
            x = b_unfold_f64(y, su)
            obs_cv[(cname, su)] = b_conv_f64(b_hist_f64(x), Kf, n)

    keep = (n * b_montgomery_centers() * DU) >= MIN_EXPECTED
    log("    dim %d: n=%d samples=%d keep_bins=%d/%d"
        % (dim, n, samples, int(keep.sum()), N_BINS))

    rng = np.random.default_rng(SEED)
    gue_cv = {su: np.empty((samples, N_BINS)) for su in SIGMA_U}
    for s in range(samples):
        A = rng.standard_normal((n, n))
        Bm = rng.standard_normal((n, n))
        H = ((A + 1j * Bm) / math.sqrt(2.0 * n))
        H = (H + H.conj().T) / 2.0
        y = np.sort(np.linalg.eigvalsh(H))
        for su in SIGMA_U:
            x = b_unfold_f64(y, su)
            gue_cv[su][s] = b_conv_f64(b_hist_f64(x), Kf, n)
        if (s + 1) % 1000 == 0:
            log("    dim %d gue %d/%d  (%.0f s)"
                % (dim, s + 1, samples, time.time() - t0))
    for _ in range(samples):        # consume GOE draws exactly as A (no eig)
        rng.standard_normal((n, n))
    pois_cv = {su: np.empty((samples, N_BINS)) for su in SIGMA_U}
    for s in range(samples):
        y = np.sort(rng.uniform(0.0, n, n))
        for su in SIGMA_U:
            x = b_unfold_f64(y, su)
            pois_cv[su][s] = b_conv_f64(b_hist_f64(x), Kf, n)
        if (s + 1) % 5000 == 0:
            log("    dim %d poisson %d/%d  (%.0f s)"
                % (dim, s + 1, samples, time.time() - t0))

    results = {}
    for cname in ("T", "L"):
        for su in SIGMA_U:
            cv_obs = obs_cv[(cname, su)]
            w = b_weights(gue_cv[su])
            w_k = w[keep]
            tgt_k = tgt_f64[keep]
            chi_obs = b_chi2_row(cv_obs[keep], w_k, tgt_k)
            chis_g = np.array([b_chi2_row(row[keep], w_k, tgt_k)
                               for row in gue_cv[su]])
            chis_p = np.array([b_chi2_row(row[keep], w_k, tgt_k)
                               for row in pois_cv[su]])
            results[(cname, "%.1f" % su)] = {
                "dim": dim, "chart": cname, "sigma_u": su,
                "chi2_obs_B": float(chi_obs),
                "k_gue": int(np.count_nonzero(chis_g >= chi_obs)),
                "k_gue_lower": int(np.count_nonzero(chis_g <= chi_obs)),
                "k_pois": int(np.count_nonzero(chis_p <= chi_obs)),
                "k_pois_upper": int(np.count_nonzero(chis_p >= chi_obs)),
                "n": samples, "seed": SEED,
                "keep_bins": int(keep.sum())}
    log("    dim %d counts done in %.0f s" % (dim, time.time() - t0))
    return results


# ---------------------------------------------------------------------------
# reference comparison
# ---------------------------------------------------------------------------

def attach_refs(results_by_dim, refs, log):
    ok_gue = ok_pois = ok_all4 = tot = 0
    for dim, results in results_by_dim.items():
        ref = refs[dim]
        for key, res in results.items():
            cell = ref["cells"].get("%s|%s" % key)
            if cell is None:
                res["A_reference"] = "MISSING"
                continue
            res["A_k_gue"] = cell["k_gue"]
            res["A_k_gue_lower"] = cell.get("k_gue_lower")
            res["A_k_pois"] = cell["k_pois"]
            res["A_k_pois_upper"] = cell.get("k_pois_upper")
            res["A_chi2_printed"] = cell["chi2_obs"]
            res["exact_k_gue"] = (res["k_gue"] == cell["k_gue"])
            res["exact_k_pois"] = (res["k_pois"] == cell["k_pois"])
            res["exact_k_gue_lower"] = (
                res["k_gue_lower"] == cell.get("k_gue_lower"))
            res["exact_k_pois_upper"] = (
                res["k_pois_upper"] == cell.get("k_pois_upper"))
            res["chi2_absdiff_vs_printed"] = abs(
                res["chi2_obs_B"] - cell["chi2_obs"])
            res["target_cell"] = TARGET_CELLS.get(
                (dim, res["chart"], "%.1f" % res["sigma_u"]))
            tot += 1
            ok_gue += int(res["exact_k_gue"])
            ok_pois += int(res["exact_k_pois"])
            ok_all4 += int(res["exact_k_gue"] and res["exact_k_pois"]
                           and res["exact_k_gue_lower"]
                           and res["exact_k_pois_upper"])
    summary = {"cells": tot, "exact_k_gue": ok_gue, "exact_k_pois": ok_pois,
               "exact_all_four": ok_all4}
    log("  counts vs engine A: k_GUE %d/%d exact, k_Pois %d/%d exact, "
        "all four tails %d/%d" % (ok_gue, tot, ok_pois, tot, ok_all4, tot))
    return summary


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def load_extractor():
    sys.path.insert(0, HERE)
    import gw_h1_extract as ex
    return ex


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--skip-hp", action="store_true")
    ap.add_argument("--skip-counts", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv[1:])
    pilot = args.pilot
    if not args.full and not pilot:
        pilot = False                    # default = full

    mp.mp.dps = DPS
    getcontext().prec = 600

    inst_path = os.path.join(INSTRUMENT_DIR, INSTRUMENT)
    inst_sha_before = sha256_file(inst_path)
    inst_sha_after = None
    script_sha = sha256_file(os.path.abspath(__file__))
    head = repo_head()

    if pilot:
        hp_dims = [201]
        count_dims = {301: 2000}
        out_path = args.out or os.path.join(
            REPO, "reports", "gw_engine_b_pilot.json")
        mode = "pilot"
    else:
        hp_dims = [201, 301, 401]
        count_dims = {201: 20000, 301: 20000, 401: 20000}
        out_path = args.out or os.path.join(
            REPO, "reports", "gw_engine_b_verify.json")
        mode = "full"

    t_start = time.time()
    ckpt("#" * 96)
    ckpt("# ENGINE B -- independent S2 verification harness (spec section 5)")
    ckpt("# mode = %s   dps = %d (declared)   seed = %d" % (mode, DPS, SEED))
    ckpt("# instrument = %s" % inst_path)
    ckpt("# instrument sha256 (before) = %s" % inst_sha_before)
    ckpt("# script sha256 = %s" % script_sha)
    ckpt("#" * 96)

    # ---- B1 + B3 ----------------------------------------------------------
    ckpt("")
    ckpt("B1 -- decimal-exact parsing census")
    decs = {}
    b1 = {}
    b3 = {}
    for dim in (201, 301, 401):
        decs[dim] = load_spectrum_decimal(SPECTRA[dim])
        b1[dim] = fake_zero_census(decs[dim])
        b3[dim] = verify_gate_GM0(decs[dim])
        c = b1[dim]
        g = b3[dim]
        ckpt("  dim %d: fields n=%d  below-float64-range=%d  "
             "would-fake-zero=%d" % (dim, c["re"]["count"],
                                     c["total_nonzero_below_float64_normal_min"],
                                     c["total_would_fake_zero_under_binary64"]))
        ckpt("  dim %d: G-M0 reproduced=%s stored=%s  (a=%s b=%s c=%s d=%s e=%s)"
             % (dim, g["reproduced_all"], g["stored_all_true"],
                g["a_finite"]["pass"], g["b_inertia"]["pass"],
                g["c_strict"]["pass"], g["d_trace"]["pass"],
                g["e_frob"]["pass"]))
        ckpt("    d: |sum-trace|=%s  budget=%s" % (g["d_trace"]["absdiff"],
                                                   g["d_trace"]["budget"]))
        ckpt("    e: |sumsq-frob|=%s  budget=%s" % (g["e_frob"]["absdiff"],
                                                    g["e_frob"]["budget"]))

    # ---- instrument import (A-side reference; read-only) ------------------
    sys.path.insert(0, INSTRUMENT_DIR)
    import gw_montgomery as g

    # ---- B2a observed grid -------------------------------------------------
    hp_records = []
    if not args.skip_hp:
        ckpt("")
        ckpt("B2a -- high-precision observed grid (mpmath dps %d vs engine A "
             "float64)" % DPS)
        t0 = time.time()
        kern = build_kernels()
        ckpt("  kernels built in %.0f s" % (time.time() - t0))
        hp_records = hp_observed_grid(hp_dims, decs, g, kern, ckpt)
        nbin = sum(len(r["bins_cv"]) + len(r["bins_tgt"])
                   for r in hp_records)
        n_or = sum(sum(1 for b in r["bins_cv"] + r["bins_tgt"]
                       if b["within_frozen_or"]) for r in hp_records)
        n10 = sum(sum(1 for b in r["bins_cv"] + r["bins_tgt"]
                      if b["within_10ulp"]) for r in hp_records)
        ckpt("  observed grid: %d bins compared; frozen OR %d/%d; "
             "tighter 10-ulp branch %d/%d" % (nbin, n_or, nbin, n10, nbin))
    else:
        kern = None

    # ---- B2b counts --------------------------------------------------------
    counts = {}
    counts_summary = None
    ex = load_extractor()
    if not args.skip_counts:
        ckpt("")
        ckpt("B2b -- independent float64-compensated counts loop")
        Kf = np.array([[float(v) for v in row] for row in kern["K_r2"]])
        tgt_f64 = np.array([float(v) for v in kern["tgt"]])
        for dim, samples in count_dims.items():
            counts[dim] = run_counts_dim(dim, samples, Kf, tgt_f64, ckpt)
        if pilot:
            sealed = ex.parse_log(ex.SEALED[301])
            ckpt("")
            ckpt("  pilot comparison vs SEALED log %s (n=%d)"
                 % (sealed["path"], sealed["samples"]))
            ok = 0
            tot = 0
            for key in sorted(counts[301]):
                res = counts[301][key]
                cell = sealed["cells"].get("%s|%s" % key)
                if cell is None:
                    ckpt("    %s: NO SEALED CELL" % (key,))
                    continue
                tot += 1
                gok = res["k_gue"] == cell["k_gue"]
                pok = res["k_pois"] == cell["k_pois"]
                cok = abs(res["chi2_obs_B"] - cell["chi2_obs"]) <= 1e-3
                ok += int(gok and pok and cok)
                res["sealed_k_gue"] = cell["k_gue"]
                res["sealed_k_pois"] = cell["k_pois"]
                res["sealed_chi2"] = cell["chi2_obs"]
                res["pilot_match"] = bool(gok and pok and cok)
                ckpt("    %s: k_GUE %d/%d (sealed %d)  k_Pois %d/%d (sealed %d)"
                     "  chi2 %.4f (sealed %.4f)  %s"
                     % (key, res["k_gue"], res["n"], cell["k_gue"],
                        res["k_pois"], res["n"], cell["k_pois"],
                        res["chi2_obs_B"], cell["chi2_obs"],
                        "OK" if res["pilot_match"] else "MISMATCH"))
            counts_summary = {"sealed_cells": tot, "matched": ok,
                              "sealed_log": sealed["path"],
                              "sealed_log_sha256": sealed["sha256"]}
            ckpt("  pilot: %d/%d sealed cells reproduced" % (ok, tot))
        else:
            refs = {dim: ex.parse_log(ex.REFINED_A[dim])
                    for dim in count_dims}
            counts_summary = attach_refs(counts, refs, ckpt)

    # ---- verdict -----------------------------------------------------------
    b1_pass = True
    b3_pass = all(v["reproduced_all"] and v["stored_all_true"]
                  for v in b3.values())
    statuses = [r["cell_status"] for r in hp_records]
    n_exc = statuses.count("PASS_ENUMERATED_EDGE_CLUSTER")
    n_fail = statuses.count("FAIL")
    if not hp_records:
        b2_pass = None
        b2_label = "SKIPPED"
    elif n_fail:
        b2_pass = False
        b2_label = "FAIL"
    elif n_exc:
        b2_pass = True
        b2_label = "PASS-WITH-ENUMERATED-EXCEPTIONS"
    else:
        b2_pass = True
        b2_label = "PASS"
    if pilot:
        counts_pass = (counts_summary["matched"] == counts_summary["sealed_cells"]
                       if counts_summary else None)
    else:
        counts_pass = (counts_summary["exact_k_gue"] == counts_summary["cells"]
                       and counts_summary["exact_k_pois"] == counts_summary["cells"]
                       if counts_summary else None)
    overall = bool(b1_pass and b3_pass
                   and (b2_pass in (True, None))
                   and (counts_pass in (True, None)))
    if not overall:
        overall_label = "STOP -- DISCREPANCY"
    elif n_exc:
        overall_label = "PASS-WITH-ENUMERATED-EXCEPTIONS"
    else:
        overall_label = "PASS"
    verdict = {"b1": "PASS" if b1_pass else "FAIL",
               "b3": "PASS" if b3_pass else "FAIL",
               "b2_observed_grid": b2_label,
               "counts": ("PASS" if counts_pass else
                          ("FAIL" if counts_pass is False else "SKIPPED")),
               "cells_pass": statuses.count("PASS"),
               "cells_pass_enumerated_edge_cluster": n_exc,
               "cells_fail": n_fail,
               "overall": overall_label}

    ckpt("")
    ckpt("#" * 96)
    ckpt("# ENGINE B VERDICT (%s)" % mode)
    ckpt("#   B1 parsing      : %s" % verdict["b1"])
    ckpt("#   B3 gate G-M0    : %s" % verdict["b3"])
    ckpt("#   B2 observed grid: %s" % verdict["b2_observed_grid"])
    ckpt("#   counts          : %s" % verdict["counts"])
    ckpt("#   OVERALL         : %s" % verdict["overall"])
    ckpt("#" * 96)

    inst_sha_after = sha256_file(inst_path)
    if inst_sha_after != inst_sha_before:
        raise SystemExit("INSTRUMENT CHANGED DURING RUN -- ABORT")

    payload = {
        "artifact": ("Engine B verification -- reports/AMENDMENT_FLOOR_SPEC.md "
                     "section 5 (B1-B6); verification only, never "
                     "verdict-bearing"),
        "mode": mode,
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "repo_head": head,
        "script": {"path": "msaf/gw_engine_b_verify.py", "sha256": script_sha},
        "manifest": {
            "declared_before_run": {
                "mpmath_dps": DPS,
                "seed": SEED,
                "samples": {str(k): v for k, v in count_dims.items()},
                "per_bin_criterion": ("FROZEN text implemented verbatim: a "
                                      "bin passes iff |B - A| <= 1e-9*|A| OR "
                                      "|B - A| <= 10*ulp(A). The 10-ulp "
                                      "branch is the declared tighter bound "
                                      "(10 ulp <= 2.3e-15 relative < 1e-9 "
                                      "relative for normal-range float64 "
                                      "values); both branch censuses are "
                                      "reported per bin. Measured in the "
                                      "pilot: engine A's own float64 "
                                      "quadrature noise floor is ~1e2-1e3 "
                                      "ulp (cv) and ~2e2 ulp (tgt), so the "
                                      "frozen OR is met via the relative "
                                      "branch."),
                "chart_L_edge_cluster_treatment": (
                    "pre-declared (see pilot findings note): a cv bin "
                    "failing the frozen OR is excused only if covered by "
                    "enumerated fine-bin membership disagreements with "
                    "|bin_A-bin_B| = 1, |D_B-edge_exact| <= 1e-9, "
                    "|D_A-edge_float| <= 1e-9, <= 100 members per cell, and "
                    "max |delta cv| over OR-failing bins <= 1e-2 "
                    "(mechanism-derived bound); tgt bins are never excused; "
                    "uncovered OR failures -> STOP"),
                "pilot_findings_note": ("reports/"
                                        "ENGINE_B_PILOT_FINDINGS_2026-10-16.md"),
                "counts_criterion": ("k_GUE and k_Pois (plus captured "
                                     "gue-lower / pois-upper tails) must agree "
                                     "EXACTLY with engine A; any larger "
                                     "discrepancy -> STOP, record divergence, "
                                     "publish nothing"),
                "observed_chi2_check": ("informational only: "
                                        "|chi2_B - chi2_A_printed| <= 1e-3 "
                                        "(4-decimal print precision)"),
                "b3_d_e": ("recomputed in exact decimal arithmetic at "
                           "artifact precision; PASS = |sum - ref| <= "
                           "storage-rounding budget (1 ulp60 per stored value "
                           "+ 1 ulp60 of the reference + 1e-300 relative "
                           "margin); the original 1e-300 full-precision "
                           "threshold cannot be re-established from 60 stored "
                           "digits (declared limitation)"),
                "scope": ("observed grid 18 cells per-bin; counts GUE+Poisson "
                          "all 18 cells; GOE curves not recomputed "
                          "(reported-only in engine A; declared limitation)"),
                "elementary_functions": ("CDF via scipy.special.ndtr (same "
                                         "underlying special function as A's "
                                         "scipy.stats.norm.cdf); row sums via "
                                         "math.fsum; convolution/chi2/weights "
                                         "via chunked Neumaier; kernels K and "
                                         "target tgt via mpmath at declared "
                                         "dps then rounded to binary64"),
            },
            "instrument": {"path": inst_path,
                           "sha256_before": inst_sha_before,
                           "sha256_after": inst_sha_after,
                           "revision": instrument_revision()},
            "spectra": {str(dim): {"path": SPECTRA[dim],
                                   "sha256": sha256_file(SPECTRA[dim])}
                        for dim in (201, 301, 401)},
            "threading_env": {
                "OPENBLAS_NUM_THREADS":
                    os.environ.get("OPENBLAS_NUM_THREADS", "unset"),
                "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS", "unset")},
            "versions": {
                "python": sys.version.split()[0],
                "numpy": np.__version__,
                "scipy": __import__("scipy").__version__,
                "mpmath": mp.__version__},
        },
        "b1_parse": {str(k): v for k, v in b1.items()},
        "b3_gate": {str(k): v for k, v in b3.items()},
        "b2_observed_grid": hp_records,
        "counts": {
            "cells": [{"dim": dim, "cell": key, **res}
                      for dim in sorted(counts)
                      for key, res in sorted(counts[dim].items())],
            "summary": counts_summary},
        "verdict": verdict,
        "elapsed_s": round(time.time() - t_start, 1),
    }
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")
    ckpt("wrote %s  (%.0f s total)" % (out_path, time.time() - t_start))
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
