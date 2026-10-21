# -*- coding: utf-8 -*-
"""Guard for the certified twin prime sieve."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from msaf import twin_prime_sieve as tps

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "msaf" / "twin_prime_sieve.py"
RECEIPT = ROOT / "reports" / "twin_prime_census.json"
PREREG = ROOT / "reports" / "PREREG_Q2_TWIN_PRIME_2026-10-21.md"


def test_locked_configuration() -> None:
    assert tps.twin_prime_census(100, 1 << 15).count == 8  # Known value for N=100


def test_known_values() -> None:
    # Known twin prime counts for various N
    known = {
        10: 2,      # (3,5), (5,7)
        100: 8,     # 8 pairs up to 100
        1000: 35,
        10000: 205,
        100000: 1224,
    }
    for N, expected in known.items():
        result = tps.twin_prime_census(N)
        assert result.count == expected, f"N={N}: expected {expected}, got {result.count}"


def test_twin_pairs_correct() -> None:
    result = tps.twin_prime_census(100)
    pairs = result.pairs
    assert pairs == [(3, 5), (5, 7), (11, 13), (17, 19), (29, 31), (41, 43), (59, 61), (71, 73)]


def test_max_gap() -> None:
    result = tps.twin_prime_census(100)
    # Gaps: (5,7)->(11,13): gap=6, (17,19)->(29,31): gap=12, (41,43)->(59,61): gap=18, (71,73): gap=0? No
    # Actual gaps: 6, 6, 12, 12, 12, 18, 10
    # Max = 18
    assert result.max_gap == 18


def test_deterministic() -> None:
    result1 = tps.twin_prime_census_certified(1000)
    result2 = tps.twin_prime_census_certified(1000)
    assert result1.count_a == result2.count_a
    assert result1.count_b == result2.count_b


def test_receipt_matches_disk() -> None:
    import json
    data = json.loads(open("reports/twin_prime_census.json", encoding="utf-8").read())
    built = tps.twin_prime_census_certified(100000)
    assert data["count"] == built.count
    assert data["max_gap"] == built.max_gap
    assert data["count_a"] == built.count_a
    assert data["count_b"] == built.count_b


if __name__ == "__main__":
    pytest.main([__file__, "-v"])