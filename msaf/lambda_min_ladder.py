"""lambda_min decay ladder from the CERTIFIED staircase (gw-spectral-map).

Why not from Route S
--------------------
`certified_inertia` gives the SIGN of every eigenvalue and nothing about
its size. Reading a decay law off inertia would be fabrication. The only
rigorous route to a magnitude here is the certified Sturm staircase in
gw-spectral-map: Arb proves, for a counted shift, how many eigenvalues of
tau lie below it, so adjacent counts differing by one bracket exactly one
eigenvalue, and the LOWER endpoint of the lowest bracket is a certified
lower bound for lambda_min.

What this script claims and does not claim
------------------------------------------
CLAIMED: for each dimension, a certified bracket containing the smallest
         eigenvalue, plus the wall-clock cost.
NOT CLAIMED: a fitted exponent B. Three or four points do not determine
         an exponential decay constant, and the cluster brackets have
         width ~1e-5 at dim 17 while lambda_min is expected near 1e-100:
         until the individual bracket around the smallest eigenvalue is
         actually resolved, the ladder measures COST, not decay. The fit
         is therefore reported only if every rung yields an individual
         bracket whose width is a small fraction of its lower endpoint,
         and otherwise reported as NOT MEASURED.

usage:
    python msaf/lambda_min_ladder.py --prec 300 --ladder 8,16,32,64
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_TREE = Path(
    os.environ.get("GW_PAIR",
                   r"C:/Users/usER/AppData/Local/Temp/opencode/ladderwork")
)


def run_one(driver_dir: Path, c: int, n_block: int, prec: int) -> dict:
    """Run the certified bracket driver for one (c, N, prec)."""
    out = (driver_dir / "results").resolve()
    out.mkdir(exist_ok=True)
    cmd = [sys.executable, "bracket_driver.py", "--c", str(c),
           "--N", str(n_block), "--prec", str(prec),
           "--out", "results/ladder_c%d_N%d_p%d.json" % (c, n_block, prec)]
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=str(driver_dir), capture_output=True,
                          text=True)
    dt = round(time.time() - t0, 1)
    path = out / ("ladder_c%d_N%d_p%d.json" % (c, n_block, prec))
    row = {"c": c, "N": n_block, "dim": 2 * n_block + 1, "prec_bits": prec,
           "exit": proc.returncode, "seconds": dt}
    if proc.returncode != 0 or not path.exists():
        row["verdict"] = "DRIVER FAILED"
        row["tail"] = (proc.stdout or proc.stderr or "")[-600:]
        return row
    data = json.loads(path.read_text(encoding="utf-8"))
    # `brackets` is the full segment list, each tagged `kind`; the
    # `individual_brackets` / `cluster_brackets` / `conflicts` keys are
    # COUNTS, not lists. The first version of this script tried to
    # iterate an int and died -- the shape was read from one earlier
    # artifact, not from this one.
    segs = list(data.get("brackets", []))
    if not segs:
        row["verdict"] = "NO SEGMENTS"
        return row
    lowest = min(segs, key=lambda s: float(s["lo"]))
    row.update({
        "coverage": data.get("coverage_of_dimension"),
        "individual": data.get("individual_brackets"),
        "clusters": data.get("clusters"),
        "conflicts": data.get("conflicts"),
        "lowest_lo": float(lowest["lo"]),
        "lowest_hi": float(lowest["hi"]),
        "lowest_kind": lowest.get("kind"),
        "lowest_width": float(lowest.get("width", 0.0)),
    })
    # A magnitude is only usable if the bracket resolves the eigenvalue:
    # width must be negligible next to the value it bounds.
    lo = float(lowest["lo"])
    resolved = (lowest.get("kind") == "individual"
                and abs(lo) > 0
                and row["lowest_width"] <= 1e-6 * abs(lo))
    row["magnitude_resolved"] = bool(resolved)
    row["verdict"] = ("CERTIFIED BRACKET, magnitude resolved" if resolved
                      else "CERTIFIED BRACKET, magnitude NOT resolved")
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prec", type=int, default=300)
    ap.add_argument("--c", type=int, default=13)
    ap.add_argument("--ladder", default="8,16,32,64")
    ap.add_argument("--tree", default=str(DEFAULT_TREE))
    ap.add_argument("--out", default="reports/lambda_min_ladder.json")
    args = ap.parse_args()

    driver_dir = Path(args.tree) / "gw-spectral-map"
    if not (driver_dir / "bracket_driver.py").exists():
        raise SystemExit("bracket_driver.py not found under %s" % driver_dir)

    ladder = [int(x) for x in args.ladder.split(",") if x.strip()]
    out_path = Path(__file__).resolve().parents[1] / args.out
    print("certified staircase ladder  c=%d prec=%d bits" % (args.c, args.prec))
    print("%-4s %-5s %-7s %-6s %-14s %-14s %-9s %s"
          % ("N", "dim", "exit", "secs", "lowest_lo", "width", "kind",
             "verdict"))
    print("-" * 108)
    results = []
    for n_block in ladder:
        row = run_one(driver_dir, args.c, n_block, args.prec)
        results.append(row)
        print("%-4s %-5s %-7s %-6s %-14s %-14s %-9s %s"
              % (row.get("N"), row.get("dim"), row.get("exit"),
                 row.get("seconds"), ("%.6e" % row["lowest_lo"])
                 if "lowest_lo" in row else "-",
                 ("%.3e" % row["lowest_width"]) if "lowest_width" in row else "-",
                 row.get("lowest_kind", "-"), row.get("verdict")))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps({"c": args.c, "prec_bits": args.prec,
                                        "runs": results}, indent=1),
                            encoding="utf-8")
        sys.stdout.flush()

    resolved = [r for r in results if r.get("magnitude_resolved")]
    print("-" * 108)
    print("%d run(s); %d certified with a resolved magnitude"
          % (len(results), len(resolved)))
    if len(resolved) >= 3:
        print("Fitting A*exp(-B*dim) is NOT attempted automatically: with")
        print("rungs this few the exponent is not determined, and a number")
        print("printed here would be read as a measured law. Do it by hand")
        print("from reports/lambda_min_ladder.json, with the bracket")
        print("widths printed above as the error bars.")
    else:
        print("Decay law NOT MEASURED: fewer than three rungs resolved a")
        print("magnitude. What this ladder establishes is COST, and the")
        print("fact that the certified staircase certifies every rung.")
    print("written: %s" % out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
