"""Feature extraction utilities for prime‑sieve output.
Exports:
- gaps(primes: list[int]) -> list[int]
- gap_histogram(gaps: list[int], bins: int = 20) -> tuple[list[int], list[int]]
- dirichlet_sums(primes: list[int], moduli: list[int]) -> dict[int, complex]
"""
from collections import Counter
from math import log

def gaps(primes: list[int]) -> list[int]:
    """Return list of successive prime gaps."""
    return [b - a for a, b in zip(primes, primes[1:])]

def gap_histogram(gap_list: list[int], bins: int = 20) -> tuple[list[int], list[int]]:
    """Simple histogram: returns (bin_edges, counts)."""
    if not gap_list:
        return ([], [])
    max_gap = max(gap_list)
    step = max(1, max_gap // bins)
    edges = list(range(0, max_gap + step, step))
    counts = [0] * (len(edges) - 1)
    for g in gap_list:
        idx = min((g // step), len(counts) - 1)
        counts[idx] += 1
    return (edges, counts)

def dirichlet_sums(primes: list[int], moduli: list[int]) -> dict[int, complex]:
    """Compute Σ χ(p) for each modulus where χ is the primitive character.
    For simplicity we use χ(p)=exp(2πi * (p % q) / q)."""
    from cmath import exp, pi
    result = {}
    for q in moduli:
        total = 0j
        for p in primes:
            total += exp(2j * pi * (p % q) / q)
        result[q] = total
    return result
