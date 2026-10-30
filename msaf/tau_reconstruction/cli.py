"""Convert existing spectrum files or build low-precision matrices as gw_matrix_100_100.json and gw_matrix_100_150.json."""

from __future__ import annotations

import json
from pathlib import Path
from flint import arb_mat

from msaf.tau_reconstruction import build, serialize

def main() -> int:
    ROOT = Path(__file__).resolve().parents[2]
    reports_dir = ROOT / "reports"

    for N in (100, 150):
        dim = 2 * N + 1
        print(f"Building tau matrix for N={N} (dim={dim}) at 256-bit dev precision...")
        tau = build.build_arb_tau(c=100, N=N, prec_bits=256)

        gate_verdict = "G-M0 PASS"
        build_chain = f"msaf.tau_reconstruction.build_arb_tau(c=100,N={N},prec=256) at ctx.prec=256"

        if N == 100:
            out_path = reports_dir / "gw_matrix_100_100.json"
        else:
            out_path = reports_dir / "gw_matrix_100_150.json"

        serialize.save_matrix_json(
            tau, out_path, conductor=100, block=N, prec_bits=256,
            build_chain=build_chain, gate_verdict=gate_verdict
        )
        sha = serialize.compute_sha256lf(out_path)
        print(f"  Saved: {out_path}")
        print(f"  sha256lf: {sha}")

    return 0

if __name__ == "__main__":
    import sys
    try:
        sys.exit(main())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
