"""van Luijk Picard upper bound from Frobenius traces (exact integers).

SCOPE (binding): given power-sum traces t_1..t_d for a degree-d
Frobenius polynomial over F_q, this module builds the polynomial by
Newton identities, completes it by the Poincare functional equation

    a_k = sign * q^{dim_x*(k - d/2)} * a_{d-k}

(both signs tried; the max count is taken, which is sound since the
true polynomial carries one of them), and counts eigenvalues of the
form q*zeta by Moebius inversion over exact QQ[x] GCDs (iterated,
so multiplicities are counted, not just distinct roots). No float
at any point; every division is asserted exact.

dim_x (variety dimension, default 2 = surface/K3) is a BINDING
input: it enters the FE through the Poincare-duality pairing
alpha <-> q^{dim_x}/alpha (Tate twist (-dim_x)). Purity puts the
eigenvalues on |alpha| = q^{dim_x/2}. Hardcoding the surface
exponent 2k-d broke curves (off by q^{k-d/2}); the E/F_3 control
test caught it, and the parameter is now explicit.

The bound counts WITH multiplicity, hence dominates the Picard rank
(van Luijk). It says nothing when vacuous (e.g. 22 on a K3).
"""
from __future__ import annotations

from fractions import Fraction
from math import gcd as int_gcd

__all__ = [
    "euler_phi",
    "char_poly_from_traces",
    "poly_gcd_deg",
    "picard_bound",
]


def euler_phi(m: int) -> int:
    if isinstance(m, float):
        raise TypeError("m: float64 leakage refused")
    m = int(m)
    if m < 1:
        raise ValueError("m must be >= 1")
    result, k, n = m, 2, m
    while k * k <= n:
        if n % k == 0:
            while n % k == 0:
                n //= k
            result -= result // k
        k += 1 if k == 2 else 2
    if n > 1:
        result -= result // n
    return result


def _newton_half(traces: dict[int, int], half: int) -> list[Fraction]:
    e: list[Fraction] = [Fraction(1)]
    for k in range(1, half + 1):
        if k not in traces:
            raise ValueError(f"missing trace t_{k}")
        total = Fraction(0)
        for i in range(1, k + 1):
            total += Fraction((-1) ** (i - 1)) * e[k - i] * traces[i]
        ek = total / k
        if ek.denominator != 1:
            raise ValueError(f"non-integral e_{k}: input not a true trace set")
        e.append(ek)
    return e


def _power_sum(e: list[Fraction], k: int) -> Fraction:
    """p_k = sum alpha_i^k from elementary symmetric e (Newton, exact).

    For k <= deg the k*e_k term applies; for k > deg the recurrence
    uses only e_1..e_deg (power sums of the roots of the char poly).
    """
    if k < 0:
        raise ValueError("k must be >= 0")
    d = len(e) - 1
    p: list[Fraction] = [Fraction(0)] * (k + 1)
    p[0] = Fraction(d)
    for m in range(1, k + 1):
        s = Fraction(0)
        for i in range(1, min(m - 1, d) + 1):
            s += Fraction((-1) ** (i - 1)) * e[i] * p[m - i]
        if m <= d:
            s += Fraction((-1) ** (m - 1)) * m * e[m]
        p[m] = s
    return p[k]


def char_poly_from_traces(
    traces: dict[int, int], dim: int, q: int, sign: int, dim_x: int = 2
) -> list[Fraction] | None:
    """Full degree-dim coefficients (lowest-first) via Newton + FE.

    ``sign`` is the functional-equation sign (+1/-1); the caller
    tries both. ``dim_x`` is the DIMENSION OF THE VARIETY: Poincare
    duality with the (-dim_x)-Tate twist pairs Frobenius eigenvalues
    alpha <-> q^{dim_x}/alpha, giving the FE

        a_k = sign * q^{dim_x*(k - dim/2)} * a_{dim-k}.

    (The exponent depends on dim_x, not derivable from dim alone --
    an earlier revision hardcoded 2k-dim, correct for surfaces but
    off by a factor q^{k-d/2} for curves; the E/F_3 control test
    caught it. Purity gives |alpha| = q^{dim_x/2}: self-paired at
    the circle |alpha| = q^{dim_x/2}.)

    Sign admission is a REAL check, not a rubber stamp: any supplied
    trace t_k with half < k (data a point-counting run actually has)
    is recomputed from the completed coefficients via Newton and must
    match exactly, else None (wrong sign, normal control flow). With
    only half traces supplied both signs are admitted and the caller
    takes the max, which is sound (the true polynomial carries one).
    """
    if sign not in (1, -1):
        raise ValueError("sign must be +1 or -1")
    if dim % 2:
        raise ValueError("even dimension required")
    if not isinstance(dim_x, int) or isinstance(dim_x, float) or dim_x < 1:
        raise ValueError(f"dim_x must be a positive int, got {dim_x}")
    half = dim // 2
    e = _newton_half(traces, half)
    full: list[Fraction] = [Fraction(0)] * (dim + 1)
    for k in range(half + 1):
        full[k] = e[k] if k == 0 else ((-1) ** k) * e[k]
    for k in range(half + 1, dim + 1):
        # dim even => dim_x*(2k-dim)/2 is an integer >= dim_x >= 1.
        exp = Fraction(dim_x * (2 * k - dim), 2)
        full[k] = Fraction(sign) * (Fraction(q) ** exp) * full[dim - k]
    # Structural FE tripwire (construction vs independent re-check)...
    for k in range(dim + 1):
        rhs = Fraction(sign) * (Fraction(q) ** Fraction(dim_x * (2 * k - dim), 2)) * full[
            dim - k
        ]
        if full[k] != rhs:
            return None
    # ...and the substantive one: traces above the Newton half must be
    # reproduced by the completed polynomial (kills the wrong sign).
    e_full = [((-1) ** i) * full[i] for i in range(dim + 1)]
    max_extra = max((k for k in traces if k > half), default=0)
    if max_extra > 0:
        for k in sorted(k for k in traces if k > half):
            if k < 1:
                raise ValueError(f"trace index must be >= 1, got {k}")
            if _power_sum(e_full, k) != Fraction(traces[k]):
                return None
    return full


def _poly_strip(p: list[Fraction]) -> list[Fraction]:
    out = list(p)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def _poly_modrem(a: list[Fraction], b: list[Fraction]) -> list[Fraction]:
    a = _poly_strip(list(a))
    while len(a) >= len(b) and not (len(a) == 1 and a[0] == 0):
        coef = a[-1] / b[-1]
        shift = len(a) - len(b)
        for i, cb in enumerate(b):
            a[shift + i] -= coef * cb
        a = _poly_strip(a)
    return a


def poly_gcd_deg(a: list[Fraction], b: list[Fraction]) -> int:
    """Degree of the exact QQ[x] GCD (Euclid, Fractions only)."""
    return len(_poly_gcd(a, b)) - 1


def _poly_gcd(a: list[Fraction], b: list[Fraction]) -> list[Fraction]:
    a, b = _poly_strip(list(a)), _poly_strip(list(b))
    while not (len(b) == 1 and b[0] == 0):
        a, b = b, _poly_modrem(a, b)
    lead = a[-1]
    return [c / lead for c in a] if lead != 1 else a


def _poly_exact_div(a: list[Fraction], b: list[Fraction]) -> list[Fraction]:
    """Quotient a/b with b | a asserted, else RuntimeError (loud)."""
    a = _poly_strip(list(a))
    b = _poly_strip(list(b))
    rem = list(a)
    quo: list[Fraction] = [Fraction(0)] * max(1, len(a) - len(b) + 1)
    while len(rem) >= len(b) and not (len(rem) == 1 and rem[0] == 0):
        coef = rem[-1] / b[-1]
        shift = len(rem) - len(b)
        quo[shift] += coef
        for i, cb in enumerate(b):
            rem[shift + i] -= coef * cb
        rem = _poly_strip(rem)
    if not (len(rem) == 1 and rem[0] == 0):
        raise RuntimeError("exact division failed (divisor must divide)")
    return _poly_strip(quo)


def _count_multiplicity(
    poly: list[Fraction], g_m: list[Fraction]
) -> int:
    """Roots of poly lying in the root set of g_m, WITH multiplicity.

    g_m = q^m x^m - 1 is squarefree, so a single gcd counts only the
    DISTINCT shared roots (an earlier revision returned 1 where the
    truth is 11 -- caught by the synthetic lock test). Divide the
    shared roots out and repeat until the gcd is constant; the sum of
    degrees is the multiplicity-weighted count. All exact Fractions.
    """
    total = 0
    cur = _poly_strip(list(poly))
    while True:
        g = _poly_gcd(cur, g_m)
        if len(g) == 1 and g[0] == 0:
            raise RuntimeError("gcd degenerate (zero polynomial)")
        dg = len(g) - 1
        if dg == 0:
            return total
        total += dg
        cur = _poly_exact_div(cur, g)


def _candidate_orders(dim: int) -> list[int]:
    out = []
    m = 1
    while True:
        if euler_phi(m) <= dim:
            out.append(m)
        # phi(m) -> infinity, so beyond some point all fail; stop
        # once m exceeds a safe multiple of dim with phi growing.
        if m > max(66, 4 * dim) and euler_phi(m) > dim:
            # confirm tail stays out: phi is eventually increasing
            # past this point for our dim range; verify a window.
            if all(euler_phi(m + k) > dim for k in range(1, 48)):
                break
        m += 1
    return out


def picard_bound(
    traces: dict[int, int], dim: int, q: int, dim_x: int = 2
) -> dict:
    """Upper bound on Picard-relevant eigenvalues, both FE signs.

    Counts roots of the form zeta/q (T-side of eigenvalues q*zeta,
    with multiplicity) by Moebius inversion over exact GCD degrees.
    ``dim_x`` is the variety dimension (see char_poly_from_traces:
    it fixes the FE exponent via the pairing alpha <->
    q^{dim_x}/alpha; default 2 = surface/K3). Returns the max over
    both functional-equation signs (sound: the true polynomial
    carries one).
    """
    if dim % 2:
        raise ValueError("even dimension required")
    best: dict = {"bound": -1}
    for sign in (1, -1):
        poly = char_poly_from_traces(traces, dim, q, sign, dim_x)
        if poly is None:
            continue
        cands = _candidate_orders(dim)
        exact: dict[int, int] = {}
        for m in cands:
            # q^m * x^m - 1 (lowest-first): roots mu with mu^m = q^-m,
            # i.e. mu = zeta/q for a root of unity zeta. (An earlier
            # revision used x^m - q^m, testing the reciprocal
            # condition; caught by the synthetic bound test.)
            xm_q = [Fraction(0)] * (m + 1)
            xm_q[m] = Fraction(q**m)
            xm_q[0] = Fraction(-1)
            g = _count_multiplicity(poly, xm_q)
            sub = sum(
                exact[d] for d in cands if d < m and m % d == 0
            )
            exact[m] = g - sub
        total = sum(exact.values())
        if total > best["bound"]:
            best = {
                "bound": total,
                "sign": sign,
                "char_poly": [str(c) for c in poly],
                "exact_orders": {m: v for m, v in exact.items() if v},
            }
    if best["bound"] < 0:
        raise RuntimeError("no functional-equation sign admitted the traces")
    return best


