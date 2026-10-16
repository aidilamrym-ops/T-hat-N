# -*- coding: utf-8 -*-
"""Capture the FULL certified spectrum of the Guinand-Weil matrix at
(c, N) = (100, 100) -> dim 201, at 6000-bit precision, in the canonical
schema of gw_spectrum_arb.py (so gw_montgomery.py can read it).

CHAIN (documented deviation from the dim-401 capture):
  dim-401 chain : mpmath dps=400 matrix -> decimal strings (gw_matrix_100_200_dps400.json)
                  -> arb parse at prec=2048 -> eig(algorithm=vdhoeven_mourrain)
  THIS chain    : source_arb_ldlt_certify.build_arb_tau(100, 100, 6000)  [pure arb,
                  no decimal serialization] -> eig(algorithm=vdhoeven_mourrain)
                  at ctx.prec=6000.
  The `dps` field records int(6000*log10(2)) = 1806 (decimal-digit equivalent of the
  6000-bit arb precision). No mpmath decimal round trip was used in this chain.

GATE G-M0 (same logic as the canonical gw_spectrum_arb.py):
  G-M0a  all eigenvalues finite
  G-M0b  all rigorously POSITIVE -> must reproduce certified inertia 201/0
  G-M0c  strictly increasing after sorting (60-digit mids)
  G-M0d  |sum(lam) - trace(M)| / |trace(M)| < 1e-300
  G-M0e  |sum(lam^2) - ||M||_F^2| / ||M||_F^2 < 1e-300
Failure -> ABORT: no statistics are computed from this file.

Honesty rules honoured: arb ball arithmetic only in the measurement; ctx.prec
and mpmath's `mp.dps` are set inside and restored in `finally`; any failure
prints as-is, never rounded into a verdict. Output -> reports/gw_spectrum_100_100.json.

usage:
    python msaf/capture_spectrum_201.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

GW = Path(os.environ.get("GW_DIR", r"C:/Users/usER/oracle-toe/GUINAND_WEIL"))
if str(GW) not in sys.path:
    sys.path.insert(0, str(GW))

OUT_PATH = Path(__file__).resolve().parents[1] / "reports" / "gw_spectrum_100_100.json"


def ckpt(msg):
    print(msg, flush=True)


def arb_mid_str(ball, digits):
    return ball.mid().str(digits, radius=False)


def arb_rad_str(ball):
    try:
        return ball.rad().mid().str(40, radius=False)
    except Exception:
        return "0"


def main() -> int:
    import mpmath as mp
    from flint import ctx

    c, n_block, prec = 100, 100, 6000
    dim = 2 * n_block + 1
    dps_field = int(prec * 0.3010299956639812)  # log10(2) * 6000 = 1806.18

    import source_arb_ldlt_certify as gw

    saved = ctx.prec
    saved_dps = mp.mp.dps
    ok = True
    results = {}
    try:
        ctx.prec = prec
        ckpt("#" * 96)
        ckpt("# FULL SPECTRUM CAPTURE (c, N, prec) = (%d, %d, %d)  dim = %d" % (c, n_block, prec, dim))
        ckpt("# chain: build_arb_tau -> arb_mat.eig(algorithm=vdhoeven_mourrain), NO decimal round trip")
        ckpt("#" * 96)

        # ---- stage 1: build matrix in pure arb ---------------------------------
        t0 = time.time()
        A, dim_returned = gw.build_arb_tau(c, n_block, prec)
        assert dim_returned == dim, "builder returned dim %s, expected %s" % (dim_returned, dim)
        t_build = time.time() - t0
        ckpt("STAGE 1 -- build_arb_tau: %.1f s" % t_build)

        # ---- stage 2: matrix moments (arb, same precision) ----------------------
        t1 = time.time()
        from flint import arb

        tr = arb(0)
        frob = arb(0)
        for i in range(dim):
            tr += A[i, i]
            for j in range(dim):
                frob += A[i, j] * A[i, j]
        t_moments = time.time() - t1
        ckpt("STAGE 2 -- matrix moments: %.1f s" % t_moments)
        ckpt("  trace(M)  = %s" % arb_mid_str(tr, 30))
        ckpt("  ||M||_F^2 = %s" % arb_mid_str(frob, 30))

        # ---- stage 3: full eig --------------------------------------------------
        t2 = time.time()
        ev = A.eig(algorithm="vdhoeven_mourrain")
        t_eig = time.time() - t2
        if isinstance(ev, tuple):
            ckpt("  (eig returned a tuple of length %d; using element 0)" % len(ev))
            ev = ev[0]
        n_ev = len(ev)
        ckpt("STAGE 3 -- eig: %.1f s   %d eigenvalues returned" % (t_eig, n_ev))
        ckpt("")

        # ---- gate G-M0 ----------------------------------------------------------
        ckpt("GATE G-M0 -- EVALUATION")

        # G-M0a finite
        bad = 0
        for w in ev:
            try:
                if not (w.real.mid().is_finite() and w.imag.mid().is_finite()):
                    bad += 1
            except Exception:
                bad += 1
        results["G-M0a_finite"] = (bad == 0)
        ckpt("  G-M0a finite : %s (non-finite = %d)" % ("PASS" if bad == 0 else "FAIL", bad))
        ok = ok and bad == 0

        # G-M0b rigorous positivity / inertia
        n_pos = sum(1 for w in ev if w.real > 0)
        n_neg = sum(1 for w in ev if w.real < 0)
        n_ind = n_ev - n_pos - n_neg
        im_max = max(abs(w.imag) for w in ev)
        results["G-M0b_inertia"] = (n_pos == dim and n_neg == 0 and n_ind == 0)
        ckpt("  G-M0b inertia: n+ = %d, n- = %d, indeterminate = %d -> %s"
             % (n_pos, n_neg, n_ind, "PASS" if results["G-M0b_inertia"] else "FAIL"))
        ckpt("           max |Im| (float): %r" % float(im_max))
        ok = ok and results["G-M0b_inertia"]

        # G-M0c strictly increasing after sort
        re_mid = [w.real.mid().str(60, radius=False) for w in ev]
        mp.mp.dps = 100
        vals = sorted(mp.mpf(s) for s in re_mid)
        n_dup = sum(1 for k in range(len(vals) - 1) if vals[k + 1] <= vals[k])
        results["G-M0c_strict"] = (n_dup == 0 and len(vals) == dim)
        ckpt("  G-M0c strictly increasing: %s (violations = %d, count = %d)"
             % ("PASS" if results["G-M0c_strict"] else "FAIL", n_dup, len(vals)))
        ok = ok and results["G-M0c_strict"]

        # G-M0d / G-M0e moments
        lam_sum = arb(0)
        lam_sq = arb(0)
        for w in ev:
            r = w.real
            lam_sum += r
            lam_sq += r * r
        d_tr = abs(lam_sum - tr) / abs(tr)
        d_fr = abs(lam_sq - frob) / abs(frob)
        log_d_tr = mp.log10(mp.mpf(d_tr.mid().str(30, radius=False))) if d_tr != 0 else mp.mpf("-inf")
        log_d_fr = mp.log10(mp.mpf(d_fr.mid().str(30, radius=False))) if d_fr != 0 else mp.mpf("-inf")
        results["G-M0d_trace"] = (log_d_tr < -300)
        results["G-M0e_frob"] = (log_d_fr < -300)
        ckpt("  G-M0d |sum(lam)-trace|/|trace| : 1e%s -> %s"
             % (mp.nstr(log_d_tr, 8), "PASS" if results["G-M0d_trace"] else "FAIL"))
        ckpt("  G-M0e |sum(lam^2)-||M||F^2|/..: 1e%s -> %s"
             % (mp.nstr(log_d_fr, 8), "PASS" if results["G-M0e_frob"] else "FAIL"))
        ok = ok and results["G-M0d_trace"] and results["G-M0e_frob"]

        # radius quality
        worst_rel = mp.mpf(0)
        worst_idx = -1
        for k, w in enumerate(ev):
            r = w.real
            rad = mp.mpf(r.rad().mid().str(30, radius=False))
            mid = mp.mpf(r.mid().str(60, radius=False))
            if mid != 0:
                rel = rad / abs(mid)
                if rel > worst_rel:
                    worst_rel = rel
                    worst_idx = k
        ckpt("  radius worst |rad|/|mid| : 1e%s (level index %d)"
             % (mp.nstr(mp.log10(worst_rel), 8) if worst_rel > 0 else "-inf", worst_idx))

        verdict_g0 = "G-M0 PASS" if ok else "G-M0 FAIL -- ABORT, NO STATISTICS"
        ckpt("")
        ckpt("  >>> %s <<<" % verdict_g0)
        ckpt("")

        # ---- summary ------------------------------------------------------------
        if len(vals) == dim:
            lo, hi = vals[0], vals[-1]
            ckpt("SPECTRUM SUMMARY")
            ckpt("  lambda_min = %s" % mp.nstr(lo, 30))
            ckpt("  lambda_max = %s" % mp.nstr(hi, 30))
            ckpt("  spread     = %s orders" % mp.nstr(mp.log10(hi / lo), 12))

        # ---- save ---------------------------------------------------------------
        digits = 60
        payload = {
            "c": c, "N": n_block, "dps": dps_field, "prec": prec,
            "algo": "vdhoeven_mourrain",
            "n": dim, "eig_seconds": round(t_eig, 3),
            "gate_GM0": {k: bool(v) for k, v in results.items()},
            "gate_verdict": verdict_g0,
            "inertia": {"n_pos": n_pos, "n_neg": n_neg, "indeterminate": n_ind},
            "im_max_float": float(im_max),
            "trace_mid": arb_mid_str(tr, 60),
            "frob2_mid": arb_mid_str(frob, 60),
            "eig": [{"re": arb_mid_str(w.real, digits),
                     "re_rad": arb_rad_str(w.real),
                     "im_abs": abs(w.imag).mid().str(20, radius=False)}
                    for w in ev],
            "build_chain": ("source_arb_ldlt_certify.build_arb_tau(c=%d,N=%d,prec=%d) -> "
                            "flint.arb_mat.eig(algorithm=vdhoeven_mourrain) at ctx.prec=%d; "
                            "no decimal serialization; dps field = int(prec*log10(2)) = %d"
                            % (c, n_block, prec, prec, dps_field)),
            "build_seconds": round(t_build, 2),
            "moments_seconds": round(t_moments, 2),
        }
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUT_PATH, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)
        ckpt("saved -> %s (%.2f MB, %d eigenvalues)"
             % (OUT_PATH, OUT_PATH.stat().st_size / 1048576.0, len(ev)))
        return 0 if ok else 1
    finally:
        ctx.prec = saved
        mp.mp.dps = saved_dps


if __name__ == "__main__":
    sys.exit(main())
