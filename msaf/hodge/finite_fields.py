"""Finite-field extension machinery for Picard bounds (F_{2^n}).

SCOPE (binding): exact F_{2^n} arithmetic (bitmask polynomials),
verified irreducibles, and NAIVE projective enumeration giving
Frobenius traces t_n = #X(F_{2^n}) - 1 - 2^{2n} for the Fermat
quartic. Measured exactly: t_1..t_6 = 2,4,8,16,32,64 (note t_n =
2^n throughout -- an observation, not a theorem).

HARD WALL (measured): naive enumeration costs O(2^{3n}) -- 34 s at
n = 6; n = 11 (needed for the full degree-22 Frobenius polynomial)
is infeasible this way (centuries). The mapped upgrade is Jacobi
character sums: O(2^n) per trace, exact for diagonal hypersurfaces.
van Luijk upper bounds are explicitly NOT claimed until that
upgrade lands and its counts cross-validate against these naive
values on n <= 6.
"""
from __future__ import annotations

from itertools import product

__all__ = ["MODULI", "is_irreducible", "frobenius_traces"]


def _deg(p: int) -> int:
    return p.bit_length() - 1


def _modmul(a: int, b: int, mod: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    while r.bit_length() >= mod.bit_length():
        r ^= mod << (r.bit_length() - mod.bit_length())
    return r


def _modrem(p: int, q: int) -> int:
    r = p
    while r.bit_length() >= q.bit_length() and r:
        r ^= q << (r.bit_length() - q.bit_length())
    return r


def _monic_irreds(deg: int) -> list[int]:
    out: list[int] = []
    for c in range(1 << deg):
        p = (1 << deg) | c
        ok = True
        d = 1
        while d * 2 <= deg:
            for q in _monic_irreds(d):
                if _modrem(p, q) == 0:
                    ok = False
                    break
            if not ok:
                break
            d += 1
        if ok:
            out.append(p)
    return out


def is_irreducible(p: int) -> bool:
    """Trial-division primality for GF(2)[x]; exact, no float."""
    if isinstance(p, float):
        raise TypeError("p: float64 leakage refused")
    p = int(p)
    n = _deg(p)
    if n < 1:
        return False
    d = 1
    while d * 2 <= n:
        for q in _monic_irreds(d):
            if _modrem(p, q) == 0:
                return False
        d += 1
    return True


#: Verified degree-n moduli for F_{2^n} (checked by test, not trusted).
MODULI: dict[int, int] = {
    1: 0b11,
    2: 0b111,
    3: 0b1011,
    4: 0b10011,
    5: 0b100101,
    6: 0b1000011,
}


def _pw4(a: int, mod: int) -> int:
    a2 = _modmul(a, a, mod)
    return _modmul(a2, a2, mod)


def _count_fermat_quartic_f2n(n: int) -> int:
    mod = MODULI[n]
    field = range(1 << n)
    total = 0
    for x, y, z, w in product(field, repeat=4):
        if x == 0 and y == 0 and z == 0 and w == 0:
            continue
        first = x or y or z or w
        if first != 1:
            continue
        if _pw4(x, mod) ^ _pw4(y, mod) ^ _pw4(z, mod) ^ _pw4(w, mod) == 0:
            total += 1
    return total


def frobenius_traces(ns: list[int]) -> dict[int, int]:
    """Exact traces t_n = #X(F_{2^n}) - 1 - 2^{2n} for given n."""
    out: dict[int, int] = {}
    for n in ns:
        if isinstance(n, float):
            raise TypeError("n: float64 leakage refused")
        n = int(n)
        if n not in MODULI:
            raise ValueError(f"no verified modulus for n={n}")
        count = _count_fermat_quartic_f2n(n)
        out[n] = count - 1 - (2**n) ** 2
    return out
