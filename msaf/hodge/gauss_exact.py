"""Exact Jacobi sums for the Fermat quartic via Davenport-Hasse lifting.

SCOPE (binding): exact INTEGER polynomial arithmetic in the
cyclotomic ring Z[zeta_m], m = lcm(4, p) -- no floats, no balls --
for the projective point count of x^4+y^4+z^4+w^4 = 0 over F_{p^n},
odd p. Character sums of order e = gcd(4, p^n - 1) are computed
ONCE over F_p (O(p) terms) and lifted to F_{p^n} with the
Davenport-Hasse formula

    tau_{n} = (-1)^{n-1} * tau_1^n

so every extension degree costs a handful of integer powers instead
of an O(p^n) sweep. This is what makes the degree-22 Newton
reconstruction (traces a_1..a_11) reachable: the ball sweep costs
~5x per degree and stalls near n = 8, the exact lifted version is
instant at any n.

Ring note (learned the hard way, kept documented). The additive
character is psi(a) = zeta_p^{Tr(a)}, NOT i^{Tr(a)}: the Gauss sums
live in Q(zeta_{4p}), not in Z[i]. An earlier revision summed with
i^{a} (a Z[i] shortcut) and produced non-integral counts, caught by
the divisibility assertion and the n=1 naive cross-check. The ring
is therefore Z[zeta_m] with basis 1, w, ..., w^{d-1}, d = phi(m),
and every reduction is exact integer polynomial arithmetic mod the
cyclotomic polynomial Phi_m.

Cross-validates against `odd_fields.jacobi_trace` (an independent
O(p^n) ball computation) and, over F_p, against naive enumeration.

Explicit non-claim: this module counts points; it says nothing
about Picard rank. The K3 reading lives in `picard_bound`.
"""
from __future__ import annotations

from math import gcd

__all__ = [
    "cyclotomic_polynomial",
    "CyclotomicRing",
    "order_e_gauss_sums",
    "lifted_taus",
    "fermat_quartic_projective_exact",
]


# --- integer polynomial helpers (lowest coefficient first) -------------


def _poly_mul(a: list[int], b: list[int]) -> list[int]:
    out = [0] * (len(a) + len(b) - 1)
    for i, ca in enumerate(a):
        for j, cb in enumerate(b):
            out[i + j] += ca * cb
    return out


def _poly_sub(a: list[int], b: list[int]) -> list[int]:
    n = max(len(a), len(b))
    out = [0] * n
    for i in range(n):
        va = a[i] if i < len(a) else 0
        vb = b[i] if i < len(b) else 0
        out[i] = va - vb
    return _poly_trim(out)


def _poly_trim(a: list[int]) -> list[int]:
    out = list(a)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [0]


def _poly_divmod(a: list[int], b: list[int]) -> tuple[list[int], list[int]]:
    a = _poly_trim(list(a))
    b = _poly_trim(list(b))
    quo = [0] * max(1, len(a) - len(b) + 1)
    while len(a) >= len(b) and not (len(a) == 1 and a[0] == 0):
        coef, rem = divmod(a[-1], b[-1])
        shift = len(a) - len(b)
        quo[shift] += coef
        for i, cb in enumerate(b):
            a[shift + i] -= coef * cb
        a = _poly_trim(a)
    return _poly_trim(quo), a


def cyclotomic_polynomial(m: int) -> list[int]:
    """Phi_m(x) as an integer coefficient list (lowest first)."""
    if isinstance(m, float):
        raise TypeError("m: float64 leakage refused")
    m = int(m)
    if m < 1:
        raise ValueError(f"m must be >= 1, got {m}")
    if m == 1:
        return [-1, 1]
    # x^m - 1 = Phi_m * prod_{d | m, d < m} Phi_d, hence Phi_m is the
    # quotient by the proper divisors, each division exact or loud.
    xm = [-1] + [0] * (m - 1) + [1]  # x^m - 1
    poly = list(xm)
    for d in range(1, m):
        if m % d:
            continue
        poly, rem = _poly_divmod(poly, cyclotomic_polynomial(d))
        if any(rem):
            raise RuntimeError(f"division by Phi_{d} failed: {rem}")
    return poly


class CyclotomicRing:
    """Exact Z[zeta_m] as degree-phi(m) integer coefficient vectors."""

    def __init__(self, m: int) -> None:
        self.m = int(m)
        self.phi = _poly_trim(cyclotomic_polynomial(self.m))
        self.degree = len(self.phi) - 1
        self.one = (1,) + (0,) * (self.degree - 1) if self.degree else (1,)
        self.zero = (0,) * max(1, self.degree)

    def _mod(self, coeffs: list[int]) -> tuple[int, ...]:
        # For a MONIC divisor the long-division remainder IS the
        # canonical representative; a nonzero remainder is the
        # answer, not an error (an earlier revision rejected it and
        # rejected correct reductions such as x^8 mod Phi_20).
        t = _poly_trim(list(coeffs))
        if len(t) <= self.degree:
            return tuple(t)
        _, rem = _poly_divmod(t, self.phi)
        return tuple(rem)

    def mul(self, a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
        return self._mod(_poly_mul(list(a), list(b)))

    def add(self, a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
        n = max(len(a), len(b))
        return tuple(
            (a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
            for i in range(n)
        )

    def neg(self, a: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(-x for x in a)

    def pow(self, a: tuple[int, ...], n: int) -> tuple[int, ...]:
        if n < 0:
            raise ValueError("n must be non-negative")
        result = self.one
        base = a
        while n:
            if n & 1:
                result = self.mul(result, base)
            base = self.mul(base, base)
            n >>= 1
        return result

    def power_of_zeta(self, k: int) -> tuple[int, ...]:
        """zeta_m^k reduced exactly (k taken mod m)."""
        k = k % self.m
        return self._mod([0] * k + [1])

    def is_integer(self, a: tuple[int, ...]) -> bool:
        return all(x == 0 for x in a[1:])

    def as_int(self, a: tuple[int, ...], what: str) -> int:
        if not self.is_integer(a):
            raise RuntimeError(f"{what}: not a rational integer: {a}")
        return a[0]


def _require_odd_prime(p: int) -> None:
    if isinstance(p, bool) or isinstance(p, float):
        raise TypeError("p: float64 leakage refused")
    p = int(p)
    if p < 3 or p % 2 == 0:
        raise ValueError(f"p must be an odd prime, got {p}")
    d = 3
    while d * d <= p:
        if p % d == 0:
            raise ValueError(f"p must be prime, got {p}")
        d += 2


def order_e_gauss_sums(p: int) -> dict:
    """Order-e Gauss sums over F_p, exact in Z[zeta_{4p}].

    tau_j = sum_{a != 0} chi_j(a) psi(a) with chi_j the j-th power
    character (values zeta_4^{j*dlog(a)}) and psi(a) = zeta_p^a.
    """
    _require_odd_prime(p)
    e = gcd(4, p - 1)
    ring = CyclotomicRing(4 * p)
    # generator of F_p^*
    factors = set()
    m = p - 1
    d = 2
    while d * d <= m:
        if m % d == 0:
            factors.add(d)
            while m % d == 0:
                m //= d
        d += 1
    if m > 1:
        factors.add(m)
    gen = None
    for candidate in range(2, p):
        if all(pow(candidate, (p - 1) // f, p) != 1 for f in factors):
            gen = candidate
            break
    if gen is None:
        raise RuntimeError("no generator found")
    dlog: dict[int, int] = {}
    cur = 1
    for k in range(p - 1):
        dlog[cur] = k
        cur = (cur * gen) % p
    taus: list[tuple[int, ...]] = []
    for j in range(e):
        s = ring.zero
        for a in range(1, p):
            # character values are e-th roots of unity, NOT always
            # 4th: for p = 3 (e = 2) chi(2) must be -1 = zeta_2, and
            # using zeta_4 gave the complex conjugate sum (caught by
            # the p = 3 count mismatch).
            chi = ring.power_of_zeta((ring.m // e) * (j * dlog[a] % e))
            psi = ring.power_of_zeta((ring.m // p) * a)
            s = ring.add(s, ring.mul(chi, psi))
        taus.append(s)
    return {"p": p, "e": e, "gen": gen, "ring": ring, "taus": taus}


def lifted_taus(n: int, p: int) -> dict:
    """Gauss sums over F_{p^n} by Davenport-Hasse lifting (exact).

    tau_n = (-1)^{n-1} tau_1^n, elementwise in Z[zeta_{4p}].
    """
    if isinstance(n, float):
        raise TypeError("n: float64 leakage refused")
    n = int(n)
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    base = order_e_gauss_sums(p)
    ring = base["ring"]
    sign = -1 if (n - 1) % 2 else 1
    lifted = []
    for t in base["taus"]:
        w = ring.pow(t, n)
        lifted.append(ring.neg(w) if sign < 0 else w)
    return {"p": p, "n": n, "e": base["e"], "ring": ring, "taus": lifted}


def fermat_quartic_projective_exact(n: int, p: int) -> dict:
    """Projective count of x^4+y^4+z^4+w^4=0 over F_{p^n}, exact int.

    Mirrors the ball aggregation of `odd_fields.jacobi_trace`:
    S_c = 1 + sum_j zeta_e(-jc) tau_j; total = sum_c S_c^4;
    affine = q^3 + total*(q-1)/(e*q). Every operation is exact in
    Z[zeta_{4p}]; rational-integrality and divisibility are
    asserted loudly rather than rounded.
    """
    lifted = lifted_taus(n, p)
    ring = lifted["ring"]
    e = lifted["e"]
    taus = lifted["taus"]
    q = p**n
    # Davenport-Hasse lifts characters of F_p to F_{p^n} of the SAME
    # order. For p = 3 and even n the order-e characters over F_{p^n}
    # have order 4 while over F_p only order 2 exists: the naive lift
    # is then the WRONG sum (caught: non-rational counts over F_3).
    # Refuse loudly instead of returning a plausible-looking number;
    # the correct fix is a base field F_{p^2} extension (not implemented).
    if p == 3 and n % 2 == 0:
        raise NotImplementedError(
            "Base-field F_{p^2} extension not yet implemented for p=3, even n."
        )
    if gcd(4, q - 1) != e:
        raise RuntimeError(
            f"Davenport-Hasse lift does not cover p={p}, n={n}: "
            f"gcd(4, p^n-1)={gcd(4, q - 1)} != gcd(4, p-1)={e}; "
            "use the ball sweep or a base-field F_{p^2} extension"
        )
    total = ring.zero
    for c in range(e):
        sc = ring.one
        for j in range(e):
            zj = ring.power_of_zeta(-((ring.m // e) * j * c) % ring.m)
            sc = ring.add(sc, ring.mul(zj, taus[j]))
        sc2 = ring.mul(sc, sc)
        total = ring.add(total, ring.mul(sc2, sc2))
    total_int = ring.as_int(total, "sum S_c^4")
    denom = e * q
    numer = total_int * (q - 1)
    if numer % denom != 0:
        raise RuntimeError(f"non-integral affine count: {numer}/{denom}")
    affine = q**3 + numer // denom
    if (affine - 1) % (q - 1) != 0:
        raise RuntimeError("projective descent failed")
    return {
        "p": p,
        "n": n,
        "q": q,
        "e": e,
        "affine": affine,
        "projective": (affine - 1) // (q - 1),
    }

