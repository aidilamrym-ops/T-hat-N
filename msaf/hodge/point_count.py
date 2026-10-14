"""Finite-field point counting for explicit surfaces (Picard program).

SCOPE (binding): this module counts F_p-points of the Fermat quartic
by exact integer arithmetic, cross-checked by chart decomposition.
It does NOT compute Picard ranks yet (that needs F_{p^n} traces +
van Luijk bounds: mapped next increment, explicitly not claimed).
Hand-derived oracles (each re-verified after the machine corrected
two human slips: scalar-multiple double counting, and confusing
nonzero-counts with fourth-power sums):
- #X(F_2) = 7: a^4 = a over F_2, so x+y+z+w = 0; 8 affine
  solutions minus the origin = 7 (4 affine + 3 at infinity).
- #X(F_3) = 16: fourth powers lie in {0,1}, so the projective sum
  vanishes iff exactly 3 coordinates are nonzero; modulo scalar
  multiples (F_3* = {1,2} pairs them) that is 4 supports x 4 = 16
  (12 affine + 4 at infinity). The naive C(4,3)*2^3 = 32 double
  counts every point with its scalar double.
- #X(F_5) = 0: fourth powers lie in {0,1}; the affine chart needs
  x^4+y^4+z^4 = 4 mod 5 from three {0,1} summands (impossible),
  and infinity needs all-zero (excluded).
"""
from __future__ import annotations

__all__ = ["count_fermat_quartic"]


def _reject_float(value, name: str) -> None:
    if isinstance(value, float):
        raise TypeError(f"{name}: float64 leakage refused")


def _is_prime(p: int) -> bool:
    if p < 2:
        return False
    if p % 2 == 0:
        return p == 2
    k = 3
    while k * k <= p:
        if p % k == 0:
            return False
        k += 2
    return True


def count_fermat_quartic(p: int) -> dict:
    """Count P^3(F_p)-points of x^4+y^4+z^4+w^4 = 0, with chart gate.

    Canonical representatives (first nonzero coordinate is 1) make
    double-counting impossible by construction. The total must equal
    the affine chart (w = 1) plus the line at infinity (w = 0),
    computed on independent code paths; mismatch raises loudly.
    """
    _reject_float(p, "p")
    if isinstance(p, bool):
        raise TypeError("p: bool is not a prime")
    p = int(p)
    if not _is_prime(p):
        raise ValueError(f"p must be prime, got {p}")

    def pw4(a: int) -> int:
        return pow(a, 4, p)

    total = 0
    for x in range(p):
        for y in range(p):
            for z in range(p):
                for w in range(p):
                    if x == 0 and y == 0 and z == 0 and w == 0:
                        continue
                    first = x if x else (y if y else (z if z else w))
                    if first != 1:
                        continue
                    if (pw4(x) + pw4(y) + pw4(z) + pw4(w)) % p == 0:
                        total += 1
    affine = 0
    for x in range(p):
        for y in range(p):
            for z in range(p):
                if (pw4(x) + pw4(y) + pw4(z) + 1) % p == 0:
                    affine += 1
    infinity = 0
    for x in range(p):
        for y in range(p):
            for z in range(p):
                if x == 0 and y == 0 and z == 0:
                    continue
                first = x if x else (y if y else z)
                if first != 1:
                    continue
                if (pw4(x) + pw4(y) + pw4(z)) % p == 0:
                    infinity += 1
    if total != affine + infinity:
        raise RuntimeError(
            f"chart decomposition failed: {total} != {affine} + {infinity}"
        )
    return {"p": p, "total": total, "affine": affine, "infinity": infinity}
