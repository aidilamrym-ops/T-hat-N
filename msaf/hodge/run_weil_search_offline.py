"""Offline last-trace search for the smooth quartic over F_3 (CH option 2).

Runs the exact Newton-class enumeration + Weil circle test
(`msaf.hodge.weil_search.search_a11`, ~75 min) and writes
reports/weil_search_a11.json. Re-run with:

    python msaf/hodge/run_weil_search_offline.py

(~75 min; progress printed every 50,000 candidates.)
The test suite never runs it -- it locks the artifact (passers,
scanned count, bound, modulus class).
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from msaf.hodge.weil_search import search_a11

ARTIFACT = Path(__file__).resolve().parents[2] / "reports" / (
    "hodge_quartic_f3_traces.json"
)
OUT = Path(__file__).resolve().parents[2] / "reports" / "weil_search_a11.json"


def main() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    traces = {
        k: int(data["counts"][str(k)]) - 1 - 3 ** (2 * k) for k in range(1, 11)
    }
    t0 = time.time()
    state = search_a11(traces, q=3)
    state["elapsed"] = round(time.time() - t0, 1)
    OUT.write_text(json.dumps(state, indent=1), encoding="utf-8")
    print(f"passers={state['passers']} scanned={state['scanned']} "
          f"({state['elapsed']}s) -> {OUT}")


if __name__ == "__main__":
    main()
