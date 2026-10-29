"""Q2 twin-prime census v2: two independent exact sieves.

This module implements a finit census of twin primes ``(p, p + 2)`` up to a
locked ``N``.  It uses only integer arithmetic in the census path and writes a
deterministic receipt.  It makes no claim about the twin-prime conjecture.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREREG_PATH = ROOT / "reports" / "PREREG_Q2_TWIN_PRIME_V2_2026-10-25.md"
RECEIPT_PATH = ROOT / "reports" / "twin_prime_v2_2026-10-25.json"
REPORT_PATH = ROOT / "reports" / "TWIN_PRIME_V2_2026-10-25.md"
SCHEMA = "msaf.twin_prime_v2.v1"
DEFAULT_N = 10_000_000
BLOCK = 1 << 20


def sha256lf(path: Path) -> str:
    """SHA-256 of a file with CRLF normalised to LF."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def _base_primes(limit: int) -> list[int]:
    """Independent simple prime list for the segmented sieve."""
    if limit < 2:
        return []
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0:2] = b"\x00\x00"
    for value in range(2, math.isqrt(limit) + 1):
        if flags[value]:
            for multiple in range(value * value, limit + 1, value):
                flags[multiple] = 0
    return [value for value in range(2, limit + 1) if flags[value]]


def sieve_a(n: int) -> list[tuple[int, int]]:
    """Full bytearray Eratosthenes; independent implementation A."""
    limit = n + 2
    prime = bytearray(b"\x01") * (limit + 1)
    prime[0:2] = b"\x00\x00"
    for value in range(2, math.isqrt(limit) + 1):
        if prime[value]:
            start = value * value
            prime[start : limit + 1 : value] = b"\x00" * (
                ((limit - start) // value) + 1
            )
    return [
        (value, value + 2)
        for value in range(3, n + 1, 2)
        if prime[value] and prime[value + 2]
    ]


def sieve_b(n: int) -> list[tuple[int, int]]:
    """Segmented sieve with a precomputed prime set; independent implementation B."""
    limit = n + 2
    base = _base_primes(math.isqrt(limit))
    primes: set[int] = set()
    for low in range(2, limit + 1, BLOCK):
        high = min(low + BLOCK - 1, limit)
        segment = bytearray(b"\x01") * (high - low + 1)
        for value in base:
            start = max(value * value, ((low + value - 1) // value) * value)
            for multiple in range(start, high + 1, value):
                segment[multiple - low] = 0
        for offset, flag in enumerate(segment):
            if flag:
                primes.add(low + offset)
    ordered = sorted(primes)
    return [
        (value, value + 2)
        for value in ordered
        if value >= 3 and value <= n and value + 2 in primes
    ]


def max_gap(pairs: list[tuple[int, int]]) -> int:
    return max(
        (pairs[index + 1][0] - pairs[index][0] for index in range(len(pairs) - 1)),
        default=0,
    )


def _pairs_digest(pairs: list[tuple[int, int]]) -> str:
    blob = json.dumps(pairs, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(blob).hexdigest()


def build_payload(n: int = DEFAULT_N) -> dict:
    pairs_a = sieve_a(n)
    pairs_b = sieve_b(n)
    count_a = len(pairs_a)
    count_b = len(pairs_b)
    gap_a = max_gap(pairs_a)
    gap_b = max_gap(pairs_b)
    pairs_equal = pairs_a == pairs_b
    payload = {
        "schema": SCHEMA,
        "N": n,
        "prereg_sha256lf": sha256lf(PREREG_PATH),
        "count": count_a,
        "count_a": count_a,
        "count_b": count_b,
        "max_gap": gap_a,
        "max_gap_a": gap_a,
        "max_gap_b": gap_b,
        "pairs": [list(pair) for pair in pairs_a],
        "pairs_sha256": _pairs_digest(pairs_a),
        "pairs_equal": pairs_equal,
        "first_pair": list(pairs_a[0]) if pairs_a else None,
        "last_pair": list(pairs_a[-1]) if pairs_a else None,
        "all_pass": bool(
            count_a == count_b
            and pairs_equal
            and gap_a == gap_b
            and count_a > 0
        ),
    }
    payload["summary"] = "ALL PASS" if payload["all_pass"] else "FAILED"
    return payload


def write_receipt(payload: dict) -> str:
    raw = canonical_bytes(payload)
    RECEIPT_PATH.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    payload = build_payload()
    digest = write_receipt(payload)
    print(json.dumps({
        "N": payload["N"],
        "count": payload["count"],
        "max_gap": payload["max_gap"],
        "all_pass": payload["all_pass"],
        "receipt_sha256": digest,
    }, indent=2))


if __name__ == "__main__":
    main()


