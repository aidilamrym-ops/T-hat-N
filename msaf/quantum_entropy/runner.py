"""Campaign V2 runner (standalone; D7: repo-style CI guard kept separately).

Pipeline (frozen in reports/AUDIT_QUANTUM_PREREG_2026-10-19.md):

1. interval LDL^T (Sylvester) on the model block itself, dual engine
   (K-Q2 / ALL_EXCLUDE_ZERO); any pivot ball touching zero trips the loud
   fence and forces exit 2 (UNDETERMINED);
2. certified spectral coordinates: exact-rational bisection (150 steps)
   with dual-engine Sturm-count decisions (interval inertia; see _decide)
   and exact rational fallback; symmetric Minkowski widening by the frozen
   envelope (L39) and the Weyl bound;
3. interval Newton contraction diagnostics on both engines;
4. surrogate battery: SIMULATED entropy stream drives the S2 statistic;
   chi-square grid per K-Q4; envelope-exceedance diagnostic recorded;
5. ledger records (BLOCK / STATS / VERDICT) with the K-Q6 hash chain;
6. standalone dashboard (K-Q5).

K-Q1: there is no ``--seed`` argument; occurrences are refused with exit 2.
L42: all artifact paths are anchored at the module location or taken from
explicit CLI arguments.
"""

from __future__ import annotations

import argparse
import array
import datetime
import hashlib
import math
import sys
import time
from fractions import Fraction
from pathlib import Path

from . import SIMULATED_LABEL
from . import chispec
from .dashboard import write_report
from .engines import (
    ENGINE_A_BITS,
    ENGINE_B_DPS,
    a_frac,
    a_newton,
    b_point,
    b_newton,
    lock_engine_a,
    pivot_count_a,
    pivot_count_b,
    pivot_sign_counts,
)
from .entropy_source import BATCH_NOTE, EntropySource, refuse_seed
from .ledger import append_record, verify_chain
from .sylvester import sylvester_a, sylvester_b

ROOT = Path(__file__).resolve().parents[2]  # L42 anchor

DIMS = (201, 301, 401)
SAMPLES_PER_DIM = 20000
BATCH_SIZE = 500
BISECTION_STEPS = 150
BISECT_LO = Fraction(0)
BISECT_HI = Fraction(41, 10)
ENVELOPE = Fraction(4, 1000)  # 1/250 = 0.004 exact (L39 envelope)
NOISE_BASE = Fraction(5, 10000)  # 0.0005 exact
ENVELOPE_FACTOR = 4
WIDTH_FLOOR_REL = Fraction(2, 100)  # 0.02 resolution floor
NEWTON_START_HALF = Fraction(5, 10**10)  # 5e-10: the f'-enclosure width scales
# linearly with the Newton ball (chaotic pivot-orbit amplification ~1e10 at the
# worst campaign coordinate, D=401 k=300), so the ball must stay small enough
# that the derivative enclosure keeps a definite sign; 5e-10 leaves >=100x
# margin there and stays far from every leading-minor eigenvalue (>=3e-7 at
# D=401), while still giving visible quadratic contraction from 1e-9 width to
# the 1e-25 target within a few iterations.
NEWTON_ITERS = 60
NEWTON_TARGET = Fraction(1, 10**25)
FALLBACK_MAX_RATIO = Fraction(5, 100)  # 5 % of decision steps
CHI2_MAX = Fraction(60)
WALL_CAP_MIN = 30.0

_SIM = SIMULATED_LABEL


def _log(msg: str) -> None:
    print("[quantum] %s" % msg, flush=True)


def _utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# frozen model block
# ---------------------------------------------------------------------------


def model_block(D: int):
    """Sharp-truncated lattice block (Campaign V2 model operator).

    Symmetric tridiagonal: a_i = 2 + (i+1)^2 * h^4, b = -1, h = 1/(D+1).
    Exact rationals; spectrum in (0, 4.1). Model instance only: nothing
    here claims a relation to the arithmetic Weil form or zeta zeros.
    """
    h = Fraction(1, D + 1)
    diag = [Fraction(2) + Fraction((i + 1) ** 2) * h ** 4 for i in range(D)]
    off2 = [Fraction(1)] * (D - 1)
    return diag, off2


def channel_scale(D: int):
    """v_i = (i+1)/D; w_i = NOISE_BASE * (1 + (i+1)/D)."""
    v = [Fraction(i + 1, D) for i in range(D)]
    w = [NOISE_BASE * (1 + Fraction(i + 1, D)) for i in range(D)]
    return v, w


def sigma0_float(D: int) -> float:
    v, w = channel_scale(D)
    s = 0.0
    for vi, wi in zip(v, w):
        t = float(vi) * float(wi)
        s += t * t
    return math.sqrt(s)


def _f(x: Fraction) -> str:
    d = 34
    return format(float(x), ".17g") if abs(x) < Fraction(10) ** 30 else str(x)[: d + 8]


# ---------------------------------------------------------------------------
# decisions and bisection
# ---------------------------------------------------------------------------


def _build_matrices(D: int):
    """Exact-rational model data and its per-engine ball mirrors.

    Design freeze (documented in the preregistration): control decisions,
    endpoint certificates and Newton diagnostics run on the model instance
    itself (exact rational diagonal). The eps-envelope enters only through
    the Weyl bound on eigenvalue location (L39); an interval LDL over the
    full eps-box would fence at D >= ~80 because lambda_min(A0) ~
    (pi/(D+1))^2 < eps = 1/250 (structural note, prereg section).
    """
    from .engines import assert_engine_a  # local import keeps L41 order explicit

    assert_engine_a()
    diag_fr, off2_fr = model_block(D)
    diag_a = [a_frac(d) for d in diag_fr]
    off2_a = [a_frac(b) for b in off2_fr]
    diag_b = [b_point(d) for d in diag_fr]
    off2_b = [b_point(b) for b in off2_fr]
    return {
        "diag_fr": diag_fr,
        "off2_fr": off2_fr,
        "diag_a": diag_a,
        "off2_a": off2_a,
        "diag_b": diag_b,
        "off2_b": off2_b,
    }


def _decide(mid_fr: Fraction, mat, k: int) -> dict:
    """Dual-engine Sturm-count decision at a rational point (K-Q3).

    The decision variable is the number of model eigenvalues strictly below
    ``mid`` (Sylvester inertia: positive LDL pivots of ``mid*I - A``). Engine A
    (Arb, 6000 bits) and Engine B (directed mpf, dps 50) each return an
    interval count; a definite count requires every pivot ball to exclude
    zero. Equal counts = agreement; disagreements are counted (must be 0)
    and resolved by the exact rational count; any ambiguity (or exact-zero
    entry) falls back to the exact rational p-recurrence.
    """
    ca = pivot_count_a(mid_fr, mat["diag_a"], mat["off2_a"])
    cb = pivot_count_b(mid_fr, mat["diag_b"], mat["off2_b"])
    if ca is not None and cb is not None:
        if ca != cb:
            ex = pivot_sign_counts(mid_fr, mat["diag_fr"], mat["off2_fr"])
            if ex is None:
                raise RuntimeError("exact decomposition failed after disagreement")
            lt, le = ex
            return {"lt": lt, "le": le, "method": "exact", "disagree": True}
        return {"lt": ca, "le": ca, "method": "dual", "disagree": False}
    ex = pivot_sign_counts(mid_fr, mat["diag_fr"], mat["off2_fr"])
    if ex is None:
        raise RuntimeError("degenerate exact pivot decomposition")
    lt, le = ex
    method = "exact_zero" if (lt < k <= le) else "exact"
    return {"lt": lt, "le": le, "method": method, "disagree": False}


def certified_bracket(k: int, mat) -> dict:
    """Certified [lo, hi] containing the k-th eigenvalue (1-based).

    Invariants: count(lo) < k (so lo <= lambda_k) and count(hi) >= k (so
    lambda_k < hi); the width is <= (BISECT_HI-BISECT_LO)/2^steps unless an
    exact rational eigenvalue hit resolves to a point.
    """
    lo, hi = BISECT_LO, BISECT_HI
    stats = {"steps": 0, "dual": 0, "exact": 0, "exact_zero": 0, "disagree": 0}
    for _ in range(BISECTION_STEPS):
        mid = (lo + hi) / 2
        d = _decide(mid, mat, k)
        stats["steps"] += 1
        stats[d["method"]] += 1
        if d["disagree"]:
            stats["disagree"] += 1
        lt, le = d["lt"], d["le"]
        if lt < k <= le:
            lo = hi = mid  # exact eigenvalue hit: resolved to a point
            break
        if le < k:
            lo = mid
        else:
            hi = mid
    return {"lo": lo, "hi": hi, "stats": stats}


def endpoint_certificate(mat, e_lo: Fraction, e_hi: Fraction, k: int) -> dict:
    """Count certificate: lambda_k lies inside [e_lo, e_hi].

    Each engine must return definite Sturm counts with cnt(e_lo) <= k-1 and
    cnt(e_hi) >= k. Other eigenvalues may also lie inside the envelope
    (frozen gaps can be smaller than 1/250), so equality of the two counts
    is NOT required -- only the two inequalities (they pin the index k).
    """
    c = {
        "a_lo": pivot_count_a(e_lo, mat["diag_a"], mat["off2_a"]),
        "a_hi": pivot_count_a(e_hi, mat["diag_a"], mat["off2_a"]),
        "b_lo": pivot_count_b(e_lo, mat["diag_b"], mat["off2_b"]),
        "b_hi": pivot_count_b(e_hi, mat["diag_b"], mat["off2_b"]),
    }

    def _ok(lo_c, hi_c):
        return lo_c is not None and hi_c is not None and lo_c <= k - 1 and hi_c >= k

    ok = _ok(c["a_lo"], c["a_hi"]) and _ok(c["b_lo"], c["b_hi"])
    return {"ok": ok, "counts": c}


def certified_coordinates(D: int, mat) -> list:
    coords = []
    ks = sorted({D // 4, D // 2, (3 * D) // 4, D})
    for k in ks:
        br = certified_bracket(k, mat)
        lo, hi = br["lo"], br["hi"]
        e_lo, e_hi = lo - ENVELOPE, hi + ENVELOPE
        rel = (e_hi - e_lo) / ((e_lo + e_hi) / 2)
        cert = endpoint_certificate(mat, e_lo, e_hi, k)
        mid = (lo + hi) / 2
        na = a_newton(
            mid - NEWTON_START_HALF,
            mid + NEWTON_START_HALF,
            mat["diag_a"],
            mat["off2_a"],
            NEWTON_ITERS,
            NEWTON_TARGET,
        )
        nb = b_newton(
            mid - NEWTON_START_HALF,
            mid + NEWTON_START_HALF,
            mat["diag_b"],
            mat["off2_b"],
            NEWTON_ITERS,
            NEWTON_TARGET,
        )
        coords.append(
            {
                "k": k,
                "lo": e_lo,
                "hi": e_hi,
                "rel_width": rel,
                "contracted": rel <= WIDTH_FLOOR_REL,
                "cert": cert,
                "newton_a": na,
                "newton_b": nb,
                "decisions": br["stats"],
            }
        )
    return coords


# ---------------------------------------------------------------------------
# surrogate battery
# ---------------------------------------------------------------------------


def _sampling_pass(D, samples, batch, src, ledger_path, time_cap_min, t0):
    v, w = channel_scale(D)
    weights = [float(vi) * float(wi) for vi, wi in zip(v, w)]
    sigma0 = math.sqrt(sum(t * t for t in weights))
    zs = []
    counts = [0] * chispec.BINS
    exceed = 0
    env_exceed = 0
    budget_exceeded = False
    b = 0
    done = 0
    while done < samples:
        n = min(batch, samples - done)
        src.begin_batch()
        for _ in range(n):
            xs = src.normals(D)
            if max(abs(x) for x in xs) > float(ENVELOPE_FACTOR):
                env_exceed += 1
            s = 0.0
            for wt, x in zip(weights, xs):
                s += wt * x
            z = s / sigma0
            zs.append(z)
            counts[chispec.bin_index(z)] += 1
            if z >= float(chispec.Z_STAR):
                exceed += 1
        meta = src.end_batch()
        append_record(
            ledger_path,
            {
                "type": "BLOCK",
                "campaign": "quantum-v2",
                "dim": D,
                "batch": b,
                "samples": n,
                "bytes": meta["bytes"],
                "digest": meta["digest"],
                "entropy_label": _SIM,
                "retention": BATCH_NOTE,
            },
        )
        b += 1
        done += n
        elapsed_min = (time.monotonic() - t0) / 60.0
        if elapsed_min > time_cap_min:
            budget_exceeded = True
            break
    return {
        "zs": zs,
        "counts": counts,
        "exceedances": exceed,
        "envelope_exceeded": env_exceed,
        "budget_exceeded": budget_exceeded,
    }


def _write_stats(outdir: Path, D: int, zs) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / ("stats_d%d.bin" % D)
    buf = array.array("d", zs)
    data = buf.tobytes()  # native float64 (x86-64: little-endian; spec-recorded)
    path.write_bytes(data)
    return {
        "path": str(path),
        "rel": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "sha256": hashlib.sha256(data).hexdigest(),
        "samples": len(zs),
    }


# ---------------------------------------------------------------------------
# per-dimension pipeline
# ---------------------------------------------------------------------------


def run_dim(D, samples, batch, src, ledger_path, outdir, time_cap_min, t0):
    mat = _build_matrices(D)
    syl_a = sylvester_a(mat["diag_a"], mat["off2_a"])
    syl_b = sylvester_b(mat["diag_b"], mat["off2_b"])
    reasons = []
    status = "RESOLVED"
    undetermined = False
    if syl_a["status"] == "FENCE_ZERO" or syl_b["status"] == "FENCE_ZERO":
        undetermined = True
        reasons.append("ALL_EXCLUDE_ZERO fence: pivot ball touches zero (K-Q2)")
    elif syl_a["status"] == "NEGATIVE_PIVOT" or syl_b["status"] == "NEGATIVE_PIVOT":
        status = "NOT_RESOLVED"
        reasons.append("negative pivot: block not positive definite")
    coords = []
    try:
        coords = certified_coordinates(D, mat)
    except RuntimeError as e:
        undetermined = True
        reasons.append("degenerate decision path: %s" % e)
    for c in coords:
        if not c["contracted"]:
            status = "NOT_RESOLVED"
            reasons.append("k=%d: enclosure wider than resolution floor" % c["k"])
        if not c["cert"]["ok"]:
            status = "NOT_RESOLVED"
            reasons.append("k=%d: endpoint certificate not definite" % c["k"])
        for eng in ("newton_a", "newton_b"):
            st = c[eng]["status"]
            if st == "DERIVATIVE_AMBIGUOUS":
                undetermined = True
                reasons.append("k=%d: %s derivative ambiguous" % (c["k"], eng))
            elif st != "CONTRACTED":
                status = "NOT_RESOLVED"
                reasons.append("k=%d: %s status %s" % (c["k"], eng, st))
        dc = c["decisions"]
        if dc["disagree"] > 0:
            status = "NOT_RESOLVED"
            reasons.append("k=%d: engine disagreements=%d" % (c["k"], dc["disagree"]))
        if dc["steps"] > 0 and Fraction(dc["exact"] + dc["exact_zero"], dc["steps"]) > FALLBACK_MAX_RATIO:
            undetermined = True
            reasons.append("k=%d: exact fallback rate above allowance" % c["k"])
    sampling = _sampling_pass(D, samples, batch, src, ledger_path, time_cap_min, t0)
    zs = sampling["zs"]
    stats = _write_stats(outdir, D, zs)
    append_record(
        ledger_path,
        {
            "type": "STATS",
            "campaign": "quantum-v2",
            "dim": D,
            "samples": len(zs),
            "file": stats["rel"],
            "sha256": stats["sha256"],
            "format": "float64-native",
            "note": "z values as sampled (statistical layer, float64)",
        },
    )
    expected = chispec.expected_counts(len(zs))
    kept, dropped = chispec.floor_rule(expected)
    chi2 = chispec.chi2_exact(sampling["counts"], expected, kept)
    chi2_ok = chi2 is not None and Fraction(0) <= chi2 <= CHI2_MAX
    if chi2 is None:
        status = "NOT_RESOLVED"
        reasons.append("chi2 undefined (no cell kept by the frozen floor rule)")
    elif not chi2_ok:
        status = "NOT_RESOLVED"
        reasons.append("chi2 outside frozen window [0, 60]")
    if sampling["budget_exceeded"]:
        status = "NOT_RESOLVED"
        reasons.append("wall-clock cap exceeded")
    final = "UNDETERMINED" if undetermined else status
    return {
        "dim": D,
        "status": final,
        "reasons": reasons,
        "samples": len(zs),
        "counts": sampling["counts"],
        "expected": expected,
        "kept": kept,
        "dropped": dropped,
        "chi2": chi2,
        "chi2_ok": chi2_ok,
        "exceedances": sampling["exceedances"],
        "envelope_exceeded": sampling["envelope_exceeded"],
        "budget_exceeded": sampling["budget_exceeded"],
        "pivots_a": syl_a,
        "pivots_b": syl_b,
        "coords": coords,
        "stats_file": stats,
    }


def _coord_compact(c: dict) -> dict:
    return {
        "k": c["k"],
        "lo_exact": "%d/%d" % (c["lo"].numerator, c["lo"].denominator),
        "hi_exact": "%d/%d" % (c["hi"].numerator, c["hi"].denominator),
        "rel_width": format(float(c["rel_width"]), ".6g"),
        "floor_rel": format(float(WIDTH_FLOOR_REL), ".6g"),
        "contracted": c["contracted"],
        "endpoint_cert": c["cert"]["ok"],
        "newton_a": {
            "status": c["newton_a"]["status"],
            "iters": len(c["newton_a"]["widths"]),
            "final_width": format(float(2 * c["newton_a"]["ball"].rad()), ".3e"),
        },
        "newton_b": {
            "status": c["newton_b"]["status"],
            "iters": len(c["newton_b"]["widths"]),
            "final_width": format(float(c["newton_b"]["widths"][-1]), ".3e") if c["newton_b"]["widths"] else None,
        },
        "decisions": c["decisions"],
    }


def run_campaign(
    dims=DIMS,
    samples=SAMPLES_PER_DIM,
    batch=BATCH_SIZE,
    outdir=None,
    ledger_path=None,
    html_path=None,
    time_cap_min=WALL_CAP_MIN,
    quiet=False,
):
    outdir = Path(outdir) if outdir is not None else ROOT / "audit_quantum" / ("exec_" + datetime.date.today().isoformat())
    ledger_path = Path(ledger_path) if ledger_path is not None else ROOT / "ledger" / "quantum_evolution.jsonl"
    html_path = Path(html_path) if html_path is not None else ROOT / "reports" / "gw_quantum_diagnostic_v1.html"
    chain = verify_chain(ledger_path)
    if not chain["ok"]:
        raise SystemExit("ledger check failed: %s" % chain["error"])
    t0 = time.monotonic()
    src = EntropySource()
    results = []
    for D in dims:
        if not quiet:
            _log("dim=%d: start (%s entropy, %d samples)" % (D, _SIM, samples))
        r = run_dim(D, samples, batch, src, ledger_path, outdir, time_cap_min, t0)
        results.append(r)
        append_record(
            ledger_path,
            {
                "type": "VERDICT",
                "scope": "dim",
                "campaign": "quantum-v2",
                "dim": D,
                "status": r["status"],
                "reasons": r["reasons"],
                "samples": r["samples"],
                "chi2": None if r["chi2"] is None else format(float(r["chi2"]), ".12g"),
                "chi2_kept": len(r["kept"]),
                "chi2_dropped": r["dropped"],
                "exceedances": r["exceedances"],
                "envelope_exceeded": r["envelope_exceeded"],
                "pivots": {"a": r["pivots_a"]["status"], "b": r["pivots_b"]["status"]},
                "coords": [_coord_compact(c) for c in r["coords"]],
                "entropy_label": _SIM,
                "created_utc": _utc(),
            },
        )
        if not quiet:
            _log("dim=%d: %s" % (D, r["status"]))
    statuses = [r["status"] for r in results]
    if "UNDETERMINED" in statuses:
        campaign_status, exit_code = "UNDETERMINED", 2
    elif "NOT_RESOLVED" in statuses:
        campaign_status, exit_code = "NOT_RESOLVED", 1
    else:
        campaign_status, exit_code = "RESOLVED", 0
    payload = {
        "campaign": "quantum-v2",
        "created_utc": _utc(),
        "entropy": src.descriptor(),
        "verdict": {
            "status": campaign_status,
            "exit_code": exit_code,
            "reasons": sorted({x for r in results for x in r["reasons"]}),
        },
        "dims": [
            {
                "dim": r["dim"],
                "status": r["status"],
                "samples": r["samples"],
                "counts": r["counts"],
                "expected_float": float(r["expected"][0]) if r["expected"] else 0.0,
                "chi2": None if r["chi2"] is None else format(float(r["chi2"]), ".12g"),
                "chi2_kept": len(r["kept"]),
                "chi2_dropped": r["dropped"],
                "exceedances": r["exceedances"],
                "envelope_exceeded": r["envelope_exceeded"],
                "floor_rel": float(WIDTH_FLOOR_REL),
                "coords": [
                    {
                        "k": c["k"],
                        "lo_float": float(c["lo"]),
                        "hi_float": float(c["hi"]),
                        "rel_width_float": float(c["rel_width"]),
                        "contracted": c["contracted"],
                        "cert": "A/B definite counts pinning k"
                        if c["cert"]["ok"]
                        else "NOT definite",
                    }
                    for c in r["coords"]
                ],
                "pivots": {"a": r["pivots_a"]["status"], "b": r["pivots_b"]["status"]},
                "newton": {
                    "a_status": r["coords"][0]["newton_a"]["status"] if r["coords"] else None,
                    "a_final": float(2 * r["coords"][0]["newton_a"]["ball"].rad()) if r["coords"] else None,
                    "b_status": r["coords"][0]["newton_b"]["status"] if r["coords"] else None,
                    "b_final": float(r["coords"][0]["newton_b"]["widths"][-1]) if r["coords"] and r["coords"][0]["newton_b"]["widths"] else None,
                },
                "decisions": r["coords"][0]["decisions"] if r["coords"] else {},
            }
            for r in results
        ],
    }
    rep = write_report(html_path, payload)
    res = verify_chain(ledger_path)
    append_record(
        ledger_path,
        {
            "type": "VERDICT",
            "scope": "campaign",
            "campaign": "quantum-v2",
            "status": campaign_status,
            "exit_code": exit_code,
            "global_claim_supported": False,
            "entropy_label": _SIM,
            "entropy": src.descriptor(),
            "parameters": {
                "dims": list(dims),
                "samples": samples,
                "batch": batch,
                "bisection_steps": BISECTION_STEPS,
                "envelope": "1/250",
                "width_floor_rel": "0.02",
                "newton_target": "1e-25",
                "chi2_window": [0, "60"],
            },
            "engine": {"a_bits": ENGINE_A_BITS, "b_dps": ENGINE_B_DPS},
            "artifacts": {
                "html": {"path": rep["path"], "bytes": rep["bytes"]},
                "stats": {
                    str(r["dim"]): r["stats_file"]["sha256"] for r in results
                },
            },
            "ledger_head": res["head"],
            "created_utc": _utc(),
        },
    )
    if not quiet:
        _log("campaign: %s (exit %d)" % (campaign_status, exit_code))
    return {"status": campaign_status, "exit_code": exit_code, "dims": results, "html": rep}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="msaf.quantum_entropy.runner",
        description="Campaign V2 quantum entropy kernel runner (SIMULATED entropy; no --seed exists, K-Q1)",
    )
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--dims", default=",".join(str(d) for d in DIMS))
    ap.add_argument("--samples", type=int, default=SAMPLES_PER_DIM)
    ap.add_argument("--batch", type=int, default=BATCH_SIZE)
    ap.add_argument("--ledger", default=None)
    ap.add_argument("--html", default=None)
    ap.add_argument("--time-cap-min", type=float, default=WALL_CAP_MIN)
    return ap


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    refuse_seed(argv)  # K-Q1, before any computation
    ap = _build_parser()
    args = ap.parse_args(argv)
    lock_engine_a()  # L41: flint precision locked first, once
    dims = tuple(int(x) for x in str(args.dims).split(",") if x.strip())
    _log("Campaign V2 start: %s entropy label; dims=%s samples=%d" % (_SIM, dims, args.samples))
    res = run_campaign(
        dims=dims,
        samples=args.samples,
        batch=args.batch,
        outdir=args.outdir,
        ledger_path=args.ledger,
        html_path=args.html,
        time_cap_min=args.time_cap_min,
    )
    return res["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
