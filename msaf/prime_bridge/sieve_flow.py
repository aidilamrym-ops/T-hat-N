"""Fast segmented sieve for prime counting up to N.
Exports:
- segmented_sieve(N) -> list[int] (primes ≤ N)
- prime_pi(N) -> int (π(N))
"""
import math

def _simple_sieve(limit: int) -> list[int]:
    """Classic Eratosthenes up to limit (≈ √N)."""
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[:2] = b"\x00\x00"
    for p in range(2, int(math.isqrt(limit)) + 1):
        if sieve[p]:
            step = p
            start = p * p
            sieve[start:limit+1:step] = b"\x00" * ((limit - start) // step + 1)
    return [i for i, is_prime in enumerate(sieve) if is_prime]

def segmented_sieve(N: int) -> list[int]:
    """Return list of all primes ≤ N using segment size ≈ √N.
    Memory O(√N). Works for N up to ~10^12 on modest RAM.
    """
    if N < 2:
        return []
    limit = int(math.isqrt(N))
    small_primes = _simple_sieve(limit)
    segment_size = max(limit, 32768)
    primes = []
    low = 2
    while low <= N:
        high = min(low + segment_size - 1, N)
        segment = bytearray(b"\x01") * (high - low + 1)
        for p in small_primes:
            start = ((low + p - 1) // p) * p
            if start < p * p:
                start = p * p
            for multiple in range(start, high + 1, p):
                segment[multiple - low] = 0
        for i, is_prime in enumerate(segment):
            if is_prime:
                primes.append(low + i)
        low = high + 1
    return primes

def prime_pi(N: int) -> int:
    """Return π(N) – number of primes ≤ N."""
    return len(segmented_sieve(N))
