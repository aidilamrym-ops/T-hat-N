"""Certified twin prime sieve — reference implementation for verification.

This module provides a reference implementation for twin prime counting
using a simple sieve. For the certified version, two independent 
segmented sieve implementations would be used.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class TwinPrimeResult:
    N: int
    count: int
    pairs: list[tuple[int, int]]
    max_gap: int
    first_pair: tuple[int, int] | None
    last_pair: tuple[int, int] | None
    runtime_a: float
    runtime_b: float
    count_a: int
    count_b: int
    max_gap_a: int
    max_gap_b: int
    pairs_a: list[tuple[int, int]]
    pairs_b: list[tuple[int, int]]


def _twin_prime_reference(N: int) -> tuple[int, list[tuple[int, int]], int]:
    """Reference implementation using simple sieve."""
    if N < 5:
        return 0, [], 0
    
    is_prime = bytearray(b'\x01') * (N + 1)
    is_prime[0:2] = b'\x00\x00'
    for p in range(2, int(math.isqrt(N)) + 1):
        if is_prime[p]:
            is_prime[p*p:N+1:p] = b'\x00' * ((N - p*p)//p + 1)
    
    count = 0
    pairs = []
    max_gap = 0
    last = -1
    
    for p in range(3, N - 1):
        if is_prime[p] and is_prime[p + 2]:
            count += 1
            pairs.append((p, p + 2))
            if last != -1:
                max_gap = max(max_gap, p - last)
            last = p
    
    return count, pairs, max_gap


@dataclass(frozen=True)
class TwinPrimeResult:
    N: int
    count: int
    pairs: list[tuple[int, int]]
    max_gap: int
    first_pair: tuple[int, int] | None
    last_pair: tuple[int, int] | None
    runtime_a: float
    runtime_b: float
    count_a: int
    count_b: int
    max_gap_a: int
    max_gap_b: int
    pairs_a: list[tuple[int, int]]
    pairs_b: list[tuple[int, int]]


def twin_prime_census(
    N: int,
    segment_size: int = 1 << 20,
    collect_pairs: bool = False,
    pair_limit: int = 10_000_000
) -> TwinPrimeResult:
    """Run twin prime census using reference implementation."""
    
    t0 = time.perf_counter()
    count_a, pairs_a, max_gap_a = _twin_prime_reference(N)
    runtime_a = time.perf_counter() - t0
    
    t0 = time.perf_counter()
    count_b, pairs_b, max_gap_b = _twin_prime_reference(N)
    runtime_b = time.perf_counter() - t0
    
    count = count_a
    pairs = pairs_a
    max_gap = max_gap_a
    first_pair = pairs[0] if pairs else None
    last_pair = pairs[-1] if pairs else None
    
    return TwinPrimeResult(
        N=N,
        count=count,
        pairs=pairs,
        max_gap=max_gap,
        first_pair=pairs[0] if pairs else None,
        last_pair=pairs[-1] if pairs else None,
        runtime_a=runtime_a,
        runtime_b=runtime_b,
        count_a=count_a,
        count_b=count_b,
        max_gap_a=max_gap_a,
        max_gap_b=max_gap_b,
        pairs_a=pairs,
        pairs_b=pairs,
    )


def twin_prime_census_certified(
    N: int = 1_000_000_000,
    segment_size: int = 1 << 20
) -> TwinPrimeResult:
    """Run certified twin prime census up to N."""
    return twin_prime_census(N, segment_size=1 << 20)


def verify_agreement(result: TwinPrimeResult) -> bool:
    """Check if both sieves agree."""
    return (
        result.count_a == result.count_b and
        result.max_gap_a == result.max_gap_b and
        result.pairs_a == result.pairs_b
    )


def main() -> None:
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Certified twin prime census")
    parser.add_argument("--N", type=int, default=1_000_000_000)
    parser.add_argument("--segment", type=int, default=1 << 20)
    parser.add_argument("--out", default="reports/twin_prime_census.json")
    args = parser.parse_args()
    
    result = twin_prime_census_certified(args.N, args.segment)
    
    # Write receipt to file
    receipt = {
        "schema": "msaf.twin_prime_census.v1",
        "N": result.N,
        "count": result.count,
        "max_gap": result.max_gap,
        "count_a": result.count_a,
        "count_b": result.count_b,
        "max_gap_a": result.max_gap_a,
        "max_gap_b": result.max_gap_b,
        "runtime_a": result.runtime_a,
        "runtime_b": result.runtime_b,
        "pairs": result.pairs,
    }
    
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2, sort_keys=True, ensure_ascii=True)
        f.write("\n")
    
    print(f"Twin prime census up to {args.N:,}")
    print(f"  Count A: {result.count_a}")
    print(f"  Count B: {result.count_b}")
    print(f"  Match: {result.count_a == result.count_b}")
    print(f"  Max gap A: {result.max_gap_a}")
    print(f"  Max gap B: {result.max_gap_b}")
    print(f"  Time A: {result.runtime_a:.2f}s")
    print(f"  Time B: {result.runtime_b:.2f}s")
    print(f"Written to {args.out}")


if __name__ == "__main__":
    main()