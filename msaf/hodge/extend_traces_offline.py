"""Offline trace extension for the certified smooth quartic over F_3.

Runs the validated vectorised counter for k = 9 and k = 10 (measured
costs: ~12 min and ~2 h), gates each trace on the Weil envelope, and
writes a JSON artifact. Re-run with:

    python msaf/hodge/extend_traces_offline.py

The artifact is the ONLY thing the test suite reads; the heavy run
never happens inside a test.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from msaf.hodge.quartic_surface import assert_weil, count_quartic_vector

ARTIFACT = Path(__file__).resolve().parents[2] / "reports" / (
    "hodge_quartic_f3_traces.json"
)

SMOOTH = {
    (0, 0): 2, (0, 1): 1, (0, 2): 2, (0, 3): 1, (0, 4): 1,
    (1, 0): 1, (1, 1): 2, (1, 2): 1, (1, 3): 1,
    (2, 0): 1, (2, 1): 1, (2, 2): 2,
    (3, 0): 2, (3, 1): 1, (4, 0): 1,
}

KNOWN = {
    1: 16, 2: 82, 3: 703, 4: 6562, 5: 58321, 6: 533629,
    7: 4787344, 8: 43046722,
}


def main(degrees=(9, 10)) -> None:
    payload = {
        "surface": "general quartic over F_3 (certified smooth)",
        "coeffs": {f"{i},{j}": c for (i, j), c in sorted(SMOOTH.items())},
        "counts": {str(k): v for k, v in KNOWN.items()},
    }
    for k in degrees:
        t0 = time.time()
        n = count_quartic_vector(SMOOTH, k, 3)
        q = 3**k
        a = n - 1 - q * q
        assert_weil(a, k, q)
        dt = time.time() - t0
        payload["counts"][str(k)] = n
        print(
            f"k={k} #X(F_{q})={n} a={a} Weil<={22*q} OK ({dt:.1f}s)",
            flush=True,
        )
        ARTIFACT.write_text(json.dumps(payload, indent=2))
    print(f"artifact written: {ARTIFACT}")


if __name__ == "__main__":
    main()