from __future__ import annotations

import ast
import hashlib
from pathlib import Path

from msaf import twin_prime_v2 as v2
from msaf import twin_prime_v3 as v3

PREREG_SHA256LF = (
    "5c46e9e0b0a9d82fd58b451b1e83af65f42352fdde81bfeb1a9901d200cebf3d"
)


def test_small_census_matches_v2_and_known_values() -> None:
    pairs_a = list(v3.iter_pairs_a(100_000))
    pairs_b = list(v3.iter_pairs_b(100_000))
    reference = v2.sieve_a(100_000)
    assert pairs_a == pairs_b == reference
    assert len(pairs_a) == 1224
    assert pairs_a[0] == (3, 5)
    assert pairs_a[-1] == (99989, 99991)
    gaps = [pairs_a[i + 1][0] - pairs_a[i][0] for i in range(len(pairs_a) - 1)]
    assert max(gaps) == 630


def test_checkpoint_1e6_matches_reference() -> None:
    payload = v3.build_payload(10**6)
    assert payload["count_a"] == payload["count_b"] == 8_169
    assert payload["elementwise_mismatches"] == 0
    assert payload["checkpoints"] == [
        {"x": 10**6, "reference": 8_169, "count_a": 8_169, "count_b": 8_169}
    ]
    assert payload["all_pass"] is True
    assert payload["summary"] == "ALL PASS"


def test_payload_is_deterministic_and_canonical() -> None:
    first = v3.build_payload(10**6)
    second = v3.build_payload(10**6)
    raw_first = v3.canonical_bytes(first)
    raw_second = v3.canonical_bytes(second)
    assert raw_first == raw_second
    assert v3.canonical_bytes(v3.json.loads(raw_first)) == raw_first
    assert first["prereg_sha256lf"] == PREREG_SHA256LF
    assert first["module_sha256lf"] == v3.sha256lf(Path(v3.__file__))
    assert first["volatile_fields"] == []


def test_c1_static_guard_rejects_float_and_numpy() -> None:
    assert v3._c1_static_ok() is True
    source = Path(v3.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    assert "numpy" not in imported
    assert "twin_prime_v2" not in imported


def test_scan_helper_matches_naive_reference() -> None:
    limit = 2000
    flags = bytearray(
        1 if _is_prime(2 * k + 1) else 0 for k in range((limit + 1) // 2 + 1)
    )
    stop = (limit + 1) // 2
    naive = [k for k in range(stop) if flags[k] and flags[k + 1]]
    assert list(v3._positions_both_set(flags, stop, chunk=37)) == naive


def test_stream_summary_checkpoint_semantics() -> None:
    summary = v3.StreamSummary([5, 10])
    for pair in [(3, 5), (5, 7), (11, 13)]:
        summary.add(pair)
    summary.finish()
    assert summary.count == 3
    assert summary.checkpoint_counts == {5: 2, 10: 2}
    assert summary.first == (3, 5)
    assert summary.last == (11, 13)
    assert summary.max_gap == 6


def test_digest_is_over_16_byte_big_endian_records() -> None:
    pairs = list(v3.iter_pairs_a(10**6))
    blob = b"".join(
        p.to_bytes(8, "big") + q.to_bytes(8, "big") for p, q in pairs
    )
    digest = hashlib.sha256(blob).hexdigest()
    assert digest == (
        "b82914c370785009e13f9d37632431693998a5b9cf61a2bdcca0773ef0e560f2"
    )
    payload = v3.build_payload(10**6)
    assert payload["pairs_sha256_a"] == digest


def test_all_pairs_are_plain_ints() -> None:
    for p, q in v3.iter_pairs_a(10_000):
        assert type(p) is int and type(q) is int
        assert q == p + 2
        assert _is_prime(p) and _is_prime(q)


def _is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True
