"""Weil root-location test + last-trace search for K3 surfaces.

SCOPE (binding): given a completed degree-22 Frobenius char poly over
F_q (surface, dim_x = 2), decide EXACTLY (all Fractions, no floats)
whether all roots satisfy |alpha| = q, via Poincare-reciprocity +
Chebyshev reduction to a real polynomial + Sturm root location; and
given the first ten power-sum traces, enumerate the mod-11 Newton
class for the eleventh and keep every candidate passing the test.

Method status (measured, not assumed):
  - 3 genuine Weil polys accepted, 2 genuine non-Weil rejected;
  - end-to-end Newton+FE+circle passes on real F_5 Fermat data;
  - 708,587 of 708,588 class members rejected on the smooth quartic
    (unique passer a_11 = 354294), and the identical machinery
    uniquely recovers the independently known Fermat truth.
  - a scare resolved by regime analysis: random SMALL-coefficient
    reciprocal polys pass often (Lakatos-type bias, verified
    numerically) -- but truth-scale candidates are rejected at
    708587/708588, and a truth-scale non-Weil control (reciprocal
    pair 1 <-> 9) is correctly rejected. Discriminating power lives
    in the coefficient regime, and the enumeration regime has teeth.

The search is offline-heavy (~75 min for the full class); the test
suite exercises `circle_test` (milliseconds) plus locked artifacts,
never the search itself.

Explicit non-claim: passing the test means "all roots have the Weil
magnitude", not "this is the true polynomial" -- uniqueness over the
exhausted class plus the rehearsal is what identifies the trace.
"""
from __future__ import annotations

from fractions import Fraction
from math import gcd

from msaf.hodge.picard_bound import (
    _newton_half,
    _poly_gcd,
    char_poly_from_traces,
    euler_phi,
)

__all__ = ["circle_test", "search_a11", "ramanujan_power_sums"]


# --- exact univariate polynomial helpers (lowest coefficient first) --


def _trim(poly: list[Fraction]) -> list[Fraction]:
    out = list(poly)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def _divmod_exact(
    a: list[Fraction], b: list[Fraction]
) -> tuple[list[Fraction], list[Fraction]]:
    a = _trim(list(a))
    b = _trim(list(b))
    quo: list[Fraction] = [Fraction(0)] * max(1, len(a) - len(b) + 1)
    while len(a) >= len(b) and not (len(a) == 1 and a[0] == 0):
        coef = a[-1] / b[-1]
        shift = len(a) - len(b)
        quo[shift] += coef
        for i, cb in enumerate(b):
            a[shift + i] -= coef * cb
        a = _trim(a)
    return _trim(quo), a


def _mul(a: list[Fraction], b: list[Fraction]) -> list[Fraction]:
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, ca in enumerate(a):
        for j, cb in enumerate(b):
            out[i + j] += ca * cb
    return _trim(out)


def _add(a: list[Fraction], b: list[Fraction]) -> list[Fraction]:
    n = max(len(a), len(b))
    return _trim(
        [
            (a[i] if i < len(a) else Fraction(0))
            + (b[i] if i < len(b) else Fraction(0))
            for i in range(n)
        ]
    )


def _deriv(poly: list[Fraction]) -> list[Fraction]:
    return _trim([i * poly[i] for i in range(1, len(poly))]) or [Fraction(0)]


def _eval(poly: list[Fraction], x: Fraction) -> Fraction:
    v = Fraction(0)
    for coef in reversed(poly):
        v = v * x + coef
    return v


# --- Sturm root location (exact) --------------------------------------


def _sturm_seq(poly: list[Fraction]) -> list[list[Fraction]]:
    seq = [_trim(list(poly)), _trim(_deriv(poly))]
    while not (len(seq[-1]) == 1 and seq[-1][0] == 0):
        _, rem = _divmod_exact(seq[-2], seq[-1])
        seq.append([-c for c in rem])
        if len(seq) > 40:
            raise RuntimeError("sturm recursion runaway")
    return seq[:-1]


def _variations(seq: list[list[Fraction]], x: Fraction) -> int:
    signs = []
    for p in seq:
        v = _eval(p, x)
        if v > 0:
            signs.append(1)
        elif v < 0:
            signs.append(-1)
    return sum(
        1 for i in range(1, len(signs)) if signs[i] != signs[i - 1]
    )


def _div_by_root(
    poly: list[Fraction], r: Fraction
) -> tuple[list[Fraction], int]:
    """Divide out (y - r) repeatedly; return (quotient, multiplicity)."""
    mult = 0
    cur = _trim(list(poly))
    while True:
        if _eval(cur, r) != 0:
            return cur, mult
        n = len(cur) - 1
        quo = [Fraction(0)] * n
        carry = Fraction(0)
        for i in range(n - 1, -1, -1):
            quo[i] = cur[i + 1] + carry
            carry = quo[i] * r
        if cur[0] + carry != 0:
            return cur, mult
        cur, mult = _trim(quo), mult + 1


# --- Chebyshev reduction ----------------------------------------------


def _chebyshev_basis(m: int) -> list[list[Fraction]]:
    """V_j(y) with S^j + S^-j = V_j(S + 1/S); V_0 = 2, V_1 = y."""
    V: list[list[Fraction]] = [[Fraction(2)], [Fraction(0), Fraction(1)]]
    for _ in range(2, m + 1):
        V.append(
            _trim(
                _add(
                    _mul([Fraction(0), Fraction(1)], V[-1]),
                    [-c for c in V[-2]],
                )
            )
        )
    return V


def circle_test(poly: list, q: int = 3) -> bool:
    """True iff every root alpha of P satisfies |alpha| = q (exact).

    R(S) = P(S/q) has roots  q/alpha; the FE gives S^d R(1/S) = +-R(S).
    Strip (S^2-1) while anti-reciprocal, Chebyshev-reduce the symmetric
    part to real W(y) with y = S + 1/S, then count W-roots in [-2, 2]
    with multiplicity (exact endpoint division + Sturm interior on the
    squarefree kernel). True iff the total equals deg W.
    """
    if isinstance(q, float):
        raise TypeError("q: float64 leakage refused")
    q = int(q)
    c = [Fraction(x) for x in poly]
    if len(c) != 23 or c[0] != 1:
        return False
    qq = Fraction(q)
    r = [c[k] / qq**k for k in range(23)]
    lhs = [r[22 - k] for k in range(23)]
    if r[0] == 0:
        return False
    eps = lhs[0] / r[0]
    if eps not in (1, -1):
        return False
    if any(lhs[k] != eps * r[k] for k in range(23)):
        return False
    cur = r
    while True:
        n = len(cur) - 1
        rev = [cur[n - k] for k in range(n + 1)]
        e = rev[0] / cur[0] if cur[0] != 0 else None
        if e not in (1, -1):
            return False
        if e == 1:
            break
        quo, rem = _divmod_exact(cur, [Fraction(-1), Fraction(0), Fraction(1)])
        if any(rem):
            return False
        cur = quo
    n = len(cur) - 1
    if n % 2:
        return False
    m = n // 2
    if any(cur[k] != cur[n - k] for k in range(n + 1)):
        return False
    V = _chebyshev_basis(m)
    W: list[Fraction] = [Fraction(0)]
    for k in range(m + 1):
        # middle term contributes c'_m * 1, NOT c'_m * V_0 (= 2 c'_m):
        # V_0 = S^0 + S^-0 counts the middle monomial twice.
        piece = [Fraction(1)] if k == m else V[m - k]
        W = _add(W, [x * cur[k] for x in piece])
    W, r_lo = _div_by_root(W, Fraction(-2))
    W, r_hi = _div_by_root(W, Fraction(2))
    if len(W) == 1 and W[0] == 0:
        return (r_lo + r_hi) == m
    g = _poly_gcd(W, _deriv(W))
    K, rem = _divmod_exact(W, g)
    if any(rem):
        K = W
    interior = _variations(_sturm_seq(K), Fraction(-2)) - _variations(
        _sturm_seq(K), Fraction(2)
    )
    return interior + r_lo + r_hi == m and interior == (len(K) - 1)


# --- Ramanujan-sum verification of orbit data --------------------------


def _moebius(n: int) -> int:
    if n < 1:
        raise ValueError("n must be >= 1")
    p, count, m = 2, 0, n
    while p * p <= m:
        if m % p == 0:
            count += 1
            m //= p
            if m % p == 0:
                return 0
        p += 1 if p == 2 else 2
    if m > 1:
        count += 1
    return -1 if count % 2 else 1


def _ramanujan(m: int, k: int) -> int:
    """Sum of zeta^k over primitive m-th roots (exact integer).

    c_m(k) = mu(m/(m,k)) * phi(m)/phi(m/(m,k)). Vanishes unless the
    quotient is squarefree -- which is why most power sums of a
    root-of-unity multiset are small.
    """
    d = gcd(m, k)
    t = m // d
    mu = _moebius(t)
    if mu == 0:
        return 0
    return mu * euler_phi(m) // euler_phi(t)


def ramanujan_power_sums(
    exact_orders: dict[int, int], q: int, ks: list[int]
) -> dict[int, int]:
    """Power sums a_k = sum (q*zeta)^k from orbit-count data (exact).

    Each order m contributes count_m eigenvalues q*zeta with zeta
    primitive m-th roots; one full Galois orbit sums to
    q^k * c_m(k) with c_m the Ramanujan sum. Independent path from
    the Newton identities: number theory instead of linear algebra.
    """
    if isinstance(q, float):
        raise TypeError("q: float64 leakage refused")
    q = int(q)
    out: dict[int, int] = {}
    for k in ks:
        if k < 1:
            raise ValueError("k must be >= 1")
        total = 0
        for m, cnt in exact_orders.items():
            if cnt % euler_phi(m) != 0:
                raise ValueError(
                    f"order {m}: count {cnt} is not a union of Galois orbits"
                )
            # cnt = (number of full orbits) * phi(m): each orbit sums
            # to q^k * c_m(k). Dividing by phi(m) here (not multiplying
            # by cnt directly) was caught by the a_1 lock (18 vs 6).
            total += (cnt // euler_phi(m)) * (q**k) * _ramanujan(m, k)
        out[k] = total
    return out


# --- the last-trace search (offline-heavy) -------------------------------


def search_a11(
    traces10: dict[int, int], q: int = 3, progress: int = 50000
) -> dict:
    """Enumerate the Newton mod-11 class for a_11; keep circle passers.

    e_11 = (p_11 - U)/11 must be integral with U fixed by p_1..p_10
    (verified against _newton_half on three class members -- the gate
    that caught a sign flip before any enumeration ran). Each
    candidate is completed by Newton+FE (both signs; sign -1 is
    structurally admissible only at e_11 = 0) and kept iff the exact
    circle test passes. Returns ALL passers: uniqueness is the
    verdict, first-hit is not a result. Takes ~75 min for q = 3.
    """
    if isinstance(q, float):
        raise TypeError("q: float64 leakage refused")
    q = int(q)
    if sorted(traces10) != list(range(1, 11)):
        raise ValueError("need exactly traces 1..10")
    bound = 22 * q**11
    e10 = _newton_half(dict(traces10), 10)
    if any(v.denominator != 1 for v in e10):
        raise ValueError("input traces give non-integral Newton coefficients")
    e10 = [int(v) for v in e10]
    U = sum(((1 if i % 2 else -1) * e10[i] * traces10[11 - i]) for i in range(1, 11))
    for p_test in (U % 11, U % 11 + 11, U - 11):
        t = dict(traces10)
        t[11] = int(p_test)
        e = _newton_half(t, 11)
        assert 11 * int(e[11]) == int(p_test) - U, (p_test, e[11])
    cands = [v for v in range(-bound, bound + 1) if v % 11 == U % 11]
    passers: list[list[int]] = []
    base = dict(traces10)
    total = len(cands)
    for idx, p11 in enumerate(cands):
        base[11] = p11
        e11 = (p11 - U) // 11
        for sign in (1, -1):
            if sign == -1 and e11 != 0:
                continue
            try:
                poly = char_poly_from_traces(base, 22, q, sign, dim_x=2)
            except ValueError:
                continue
            if poly is None:
                continue
            if circle_test(poly, q):
                passers.append([p11, sign])
        if progress and (idx + 1) % progress == 0:
            print(f"... {idx + 1}/{total}", flush=True)
    return {
        "passers": passers,
        "scanned": len(cands),
        "bound": bound,
        "Umod11": U % 11,
        "distinct": sorted({p for p, _ in passers}),
    }
