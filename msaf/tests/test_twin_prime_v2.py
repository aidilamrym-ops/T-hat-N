from __future__ import annotations

from msaf import twin_prime_v2 as q2


def test_census_100k_matches_known_values() -> None:
    pairs_a = q2.sieve_a(100_000)
    pairs_b = q2.sieve_b(100_000)
    assert len(pairs_a) == len(pairs_b) == 1224
    assert q2.max_gap(pairs_a) == q2.max_gap(pairs_b) == 630
    assert pairs_a == pairs_b
    assert pairs_a[0] == (3, 5)
    assert pairs_a[-1] == (99989, 99991)


def test_payload_is_deterministic() -> None:
    first = q2.build_payload(100_000)
    second = q2.build_payload(100_000)
    assert first == second
    assert first["all_pass"] is True
    assert first["count_a"] == first["count_b"] == 1224
