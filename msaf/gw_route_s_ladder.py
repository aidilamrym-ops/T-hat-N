"""Route S ladder: rigorous interval LDL^T inertia at rising dimension.

What this measures
------------------
For the Guinand-Weil block tau = W02 - WR - Wp of dimension
DIM = 2N+1, `certified_inertia` performs an interval LDL^T factorisation
and counts the strictly signed pivots. That count is a RIGOROUS statement
about the whole spectrum: every pivot strictly positive means every
eigenvalue is strictly positive. It is NOT a magnitude: inertia says
sign, not size. Any lambda_min curve derived from this file alone would be
a fabrication, so this file reports none -- see the certified staircase
for that.

Cost model, measured rather than assumed: entries cost O(M) trig calls at
`prec` bits (M = number of prime powers up to c), the factorisation costs
O(DIM^3), so the ladder is dominated by precision first and dimension
second.

Honesty rules honoured here:
  * exact ball arithmetic only, no float anywhere in the measurement;
  * `ctx.prec` is set inside each run and restored after it, so a sweep
    in this file cannot change the precision another test module sees;
  * a NaN or an inconclusive inertia is printed as-is and counted, never
    rounded into a verdict.

usage:
    python msaf/gw_route_s_ladder.py --prec 6000 --ladder 10,20,40,80
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

GW = Path(os.environ.get("GW_DIR", r"C:/Users/usER/oracle-toe/GUINAND_WEIL"))
if str(GW) not in sys.path:
    sys.path.insert(0, str(GW))


def run_one(c: int, n_block: int, prec: int) -> dict:
    from flint import ctx

    import source_arb_ldlt_certify as gw

    dim = 2 * n_block + 1
    saved = ctx.prec
    t0 = time.time()
    try:
        ctx.prec = prec
        # build_arb_tau returns (matrix, dimension); taking the matrix alone
        # was the first version's bug and it surfaced as a TypeError from
        # deep inside the factorisation rather than at the call site.
        A, dim_returned = gw.build_arb_tau(c, n_block, prec)
        assert dim_returned == dim, (
            "builder returned dim %s, expected %s" % (dim_returned, dim))
        t_build = time.time() - t0
        t1 = time.time()
        res = gw.certified_inertia(A, dim)
        t_ldlt = time.time() - t1
        # certified_inertia returns (n_pos, n_neg, undetermined_index, transcript).
        # The third element is None when every pivot was strictly signed, and
        # otherwise the index of the first pivot that could not be decided --
        # a real outcome that must be reported, never rounded into a verdict.
        n_pos, n_neg, undetermined, transcript = res
        finite = True
        for i in range(dim):
            for j in range(dim):
                if not A[i, j].is_finite():
                    finite = False
                    break
            if not finite:
                break
        return {
            "c": c, "N": n_block, "dim": dim, "prec_bits": prec,
            "n_pos": n_pos, "n_neg": n_neg,
            "undetermined_pivot": undetermined,
            "pivots_recorded": len(transcript),
            "entries_finite": finite,
            "verdict": ("CERTIFIED POSITIVE DEFINITE"
                        if (undetermined is None and n_pos == dim
                            and n_neg == 0 and finite)
                        else ("UNDETERMINED at pivot %s" % undetermined
                              if undetermined is not None
                              else "NOT POSITIVE DEFINITE")),
            "build_s": round(t_build, 2),
            "ldlt_s": round(t_ldlt, 2),
            "total_s": round(time.time() - t0, 2),
        }
    except Exception as exc:  # never let a sweep crash: record it
        return {
            "c": c, "N": n_block, "dim": dim, "prec_bits": prec,
            "verdict": "ERROR: %r" % (exc,),
            "total_s": round(time.time() - t0, 2),
        }
    finally:
        ctx.prec = saved


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prec", type=int, default=6000)
    ap.add_argument("--c", type=int, default=13)
    ap.add_argument("--ladder", default="10,20,40,80",
                    help="comma separated block indices N; dim = 2N+1")
    ap.add_argument("--out", default="reports/gw_route_s_ladder.json")
    args = ap.parse_args()

    ladder = [int(x) for x in args.ladder.split(",") if x.strip()]
    out_path = Path(__file__).resolve().parents[1] / args.out
    results = []
    if out_path.exists():
        results = json.loads(out_path.read_text(encoding="utf-8")).get("runs", [])

    print("Route S ladder  c=%d  prec=%d bits" % (args.c, args.prec))
    print("dim = 2N+1; inertia is SIGN only, not magnitude")
    print("%-4s %-5s %-8s %-6s %-6s %-9s %-8s %-8s %s"
          % ("N", "dim", "prec", "n_pos", "n_neg", "finite", "build_s",
             "ldlt_s", "verdict"))
    print("-" * 92)
    for n_block in ladder:
        row = run_one(args.c, n_block, args.prec)
        results.append(row)
        print("%-4s %-5s %-8s %-6s %-6s %-9s %-8s %-8s %s"
              % (row.get("N"), row.get("dim"), row.get("prec_bits"),
                 row.get("n_pos"), row.get("n_neg"),
                 row.get("entries_finite"), row.get("build_s"),
                 row.get("ldlt_s"), row.get("verdict")))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps({"c": args.c, "runs": results}, indent=1),
            encoding="utf-8")
        sys.stdout.flush()

    bad = [r for r in results if r["verdict"] != "CERTIFIED POSITIVE DEFINITE"]
    print("-" * 92)
    print("%d run(s); %d certified, %d not certified"
          % (len(results), len(results) - len(bad), len(bad)))
    print("written: %s" % out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())


