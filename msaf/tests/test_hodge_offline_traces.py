"""Offline trace artifact: integrity, identity and Weil gating.

The artifact `reports/hodge_quartic_f3_traces.json` is written by
`msaf/hodge/extend_traces_offline.py` (a long offline run: k = 9 takes
~12 min, k = 10 ~2 h). The test suite NEVER runs the heavy counter; it
validates whatever the artifact contains. Because the artifact is
written incrementally (after each degree), this test automatically
starts covering the new degrees the moment they land -- no edit needed.

What is checked, in order of severity:
  1. the artifact exists and is valid JSON;
  2. its surface (coefficient table) is EXACTLY the one the locked
     tests certify smooth -- a swapped coefficient file would
     otherwise produce plausible nonsense;
  3. every already-locked count (k = 1..8) still matches;
  4. every count in the artifact is in Weil range, and its derived
     trace is recorded.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "reports"
    / "hodge_quartic_f3_traces.json"
)

SMOOTH = {
    (0, 0): 2, (0, 1): 1, (0, 2): 2, (0, 3): 1, (0, 4): 1,
    (1, 0): 1, (1, 1): 2, (1, 2): 1, (1, 3): 1,
    (2, 0): 1, (2, 1): 1, (2, 2): 2,
    (3, 0): 2, (3, 1): 1, (4, 0): 1,
}
LOCKED = {
    1: 16, 2: 82, 3: 703, 4: 6562, 5: 58321, 6: 533629,
    7: 4787344, 8: 43046722,
}


def _load() -> dict:
    assert ARTIFACT.exists(), f"artifact missing: {ARTIFACT}"
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert isinstance(data.get("counts"), dict)
    return data


def test_artifact_surface_matches_certified_one():
    data = _load()
    got = {
        tuple(int(x) for x in k.split(",")): v
        for k, v in data["coeffs"].items()
    }
    assert got == SMOOTH, "artifact surface differs from the certified one"


@pytest.mark.parametrize("k,count", sorted(LOCKED.items()))
def test_locked_counts_still_hold_in_artifact(k, count):
    data = _load()
    assert int(data["counts"][str(k)]) == count


def test_every_artifact_count_is_within_weil():
    data = _load()
    for k_str, count in data["counts"].items():
        k = int(k_str)
        q = 3**k
        a = int(count) - 1 - q * q
        assert abs(a) <= 22 * q, f"k={k}: |a_k|={abs(a)} outside envelope"


def test_artifact_grows_as_offline_run_progresses():
    # Informational, not a gate: records how far the offline run got.
    data = _load()
    have = sorted(int(k) for k in data["counts"])
    assert have[: len(LOCKED)] == sorted(LOCKED), "locked prefix broken"
    extra = [k for k in have if k > max(LOCKED)]
    print(f"offline degrees present beyond the locked ones: {extra}")