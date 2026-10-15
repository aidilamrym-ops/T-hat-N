"""lambda_min decay ladder via the interval eigen-solver (Route A2).

The Sturm staircase in `gw-spectral-map` certifies the whole spectrum
but deliberately does not resolve the near-zero cluster: at 300 bits and
again at 3000 bits it returns the SAME cluster bracket for the smallest
eigenvalues (measured, bit-identical), because the shift positions come
from a float64 dual engine and no amount of Arb precision moves them.
So that tool measures cost, not decay.

The tool that does produce certified magnitudes is `arb_mat.eig`
(Arb's Rump / van der Hoeven-Mourrain interval eigensolver), which is
what the Guinand-Weil README calls route A2: "81/81 eigenvalues
isolated, ENCLOSED STRICTLY POSITIVE". This script uses it directly and
records, per dimension:

  * the certified lower bound for the smallest eigenvalue;
  * whether every eigenvalue's enclosure excludes zero;
  * the imaginary leakage, which must be zero for a symmetric real
    matrix and is reported rather than assumed;
  * wall-clock cost.

WHAT IS NOT CLAIMED HERE: a fitted exponent B. The script prints the
lower bounds and their dimensions and stops. A decay constant fitted
from four or five points is not a measurement, and printing one would be
the exact failure mode this program exists to prevent. Fit it by hand
from the JSON, with the printed radii as error bars, and only if the
radii are negligible against the values.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

GW_DIR = os.environ.get("GW_DIR", r"C:/Users/usER/oracle-toe/GUINAND_WEIL")
if GW_DIR not in sys.path:
    sys.path.insert(0, GW_DIR)


def run_one(c: int, n_block: int, prec: int) -> dict:
    from flint import ctx

    import source_arb_ldlt_certify as gw

    dim = 2 * n_block + 1
    saved = ctx.prec
    t0 = time.time()
    try:
        ctx.prec = prec
        A, dim_built = gw.build_arb_tau(c, n_block, prec)
        assert dim_built == dim, "builder returned dim %s" % dim_built
        t_build = time.time() - t0
        t1 = time.time()
        out = A.eig()
        t_eig = time.time() - t1
        # A non-finite enclosure is reported as such, never as a value.
        finite = all(z.is_finite() for z in out)
        im_leak = max((z.imag.abs_upper() for z in out), default=None)
        vals = sorted(out, key=lambda z: z.real.mid())
        lo = vals[0].real
        hi = vals[-1].real
        excludes_zero = all(
            not bool(z.real.contains(_zero())) for z in out)
        return {
            "c": c, "N": n_block, "dim": dim, "prec_bits": prec,
            "n_eigenvalues": len(out),
            "all_finite": bool(finite),
            "imag_leak_upper": None if im_leak is None else float(im_leak),
            "lambda_min_lo": float(lo.lower()),
            "lambda_min_mid": float(lo.mid()),
            "lambda_min_rad": float(lo.rad().abs_upper()),
            "lambda_max_hi": float(hi.upper()),
            "all_exclude_zero": bool(excludes_zero),
            "build_s": round(t_build, 2),
            "eig_s": round(t_eig, 2),
            "verdict": ("CERTIFIED, all eigenvalues strictly positive"
                        if (finite and excludes_zero and dim == len(out))
                        else "NOT CERTIFIED -- see fields"),
        }
    except Exception as exc:
        return {"c": c, "N": n_block, "dim": dim, "prec_bits": prec,
                "verdict": "ERROR: %r" % (exc,),
                "total_s": round(time.time() - t0, 2)}
    finally:
        ctx.prec = saved


def _zero():
    from flint import arb
    return arb(0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prec", type=int, default=6000)
    ap.add_argument("--c", type=int, default=13)
    ap.add_argument("--ladder", default="8,16,32,64")
    ap.add_argument("--out", default="reports/lambda_min_eig_ladder.json")
    args = ap.parse_args()

    ladder = [int(x) for x in args.ladder.split(",") if x.strip()]
    out_path = Path(__file__).resolve().parents[1] / args.out
    print("lambda_min ladder via arb_mat.eig   c=%d prec=%d bits" % (
        args.c, args.prec))
    print("%-4s %-5s %-6s %-15s %-10s %-8s %-7s %s"
          % ("N", "dim", "eig_s", "lambda_min_lo", "rad", "Im_leak",
             "n_excl0", "verdict"))
    print("-" * 112)
    results = []
    for n_block in ladder:
        row = run_one(args.c, n_block, args.prec)
        results.append(row)
        print("%-4s %-5s %-6s %-15s %-10s %-8s %-7s %s" % (
            row.get("N"), row.get("dim"), row.get("eig_s"),
            ("%.6e" % row["lambda_min_lo"]) if "lambda_min_lo" in row else "-",
            ("%.1e" % row["lambda_min_rad"]) if "lambda_min_rad" in row else "-",
            ("%.1e" % row["imag_leak_upper"])
            if row.get("imag_leak_upper") is not None else "-",
            row.get("all_exclude_zero"),
            row.get("verdict")))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(
            {"c": args.c, "prec_bits": args.prec, "runs": results}, indent=1),
            encoding="utf-8")
        sys.stdout.flush()

    ok = [r for r in results if str(r.get("verdict", "")).startswith("CERTIFIED")]
    print("-" * 112)
    print("%d run(s); %d certified magnitudes" % (len(results), len(ok)))
    print("No exponent is fitted here. The lower bounds above are the")
    print("measurement; a decay constant needs the radii to be negligible")
    print("against the values AND enough rungs to constrain it, and")
    print("neither is asserted by this script.")
    print("written: %s" % out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
