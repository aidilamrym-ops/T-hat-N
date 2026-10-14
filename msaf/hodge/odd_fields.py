"""Odd-characteristic extension fields for the K3 Picard program.

SCOPE (binding): exact GF(p)[x] arithmetic (integer coefficient
lists, p an odd prime), verified irreducible moduli, naive Fermat
quartic counts over F_{3^n} for small n, and an explicit Jacobian
smoothness gate. The F_2 machinery lives separately in
``finite_fields.py`` (kept: its counts are valid integers, but the
surface is degenerate there -- see the Frobenius gate).
Cross-check: n = 1 must reproduce the independent F_3 count (16).
``jacobi_trace`` extends traces far beyond naive reach (certified
integer enclosures); for e = 2 (n odd) the closed form
N_proj = (q+1)^2 holds by the same derivation and is locked by test.
"""
from __future__ import annotations

from itertools import product

from flint import acb, arb, ctx, fmpq

__all__ = [
    "find_modulus",
    "is_irreducible_mod",
    "count_fermat_quartic_fpn",
    "fermat_quartic_smooth",
    "jacobi_trace",
]


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


def _strip(poly: list[int]) -> list[int]:
    out = list(poly)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [0]


def _pad(a: list[int], n: int) -> tuple[int, ...]:
    """Canonical fixed-length key: stripped values pad identically."""
    a = _strip(list(a))
    return tuple(a + [0] * (n - len(a)))


def _add(a: list[int], b: list[int], p: int) -> list[int]:
    n = max(len(a), len(b))
    return _strip(
        [((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % p
         for i in range(n)]
    )


def _mul(a: list[int], b: list[int], p: int) -> list[int]:
    if a == [0] or b == [0]:
        return [0]
    out = [0] * (len(a) + len(b) - 1)
    for i, ca in enumerate(a):
        for j, cb in enumerate(b):
            out[i + j] = (out[i + j] + ca * cb) % p
    return _strip(out)


def _modrem(a: list[int], mod: list[int], p: int) -> list[int]:
    a = _strip(list(a))
    inv_lead = pow(mod[-1], -1, p)
    while len(a) >= len(mod) and a != [0]:
        coef = (a[-1] * inv_lead) % p
        shift = len(a) - len(mod)
        for i, cm in enumerate(mod):
            a[shift + i] = (a[shift + i] - coef * cm) % p
        a = _strip(a)
    return a


def _monic_of_degree(deg: int, p: int) -> list[list[int]]:
    if deg == 0:
        return [[1]]
    out: list[list[int]] = []
    for coeffs in product(range(p), repeat=deg):
        out.append([c for c in coeffs] + [1])
    return out


def is_irreducible_mod(poly: list[int], p: int) -> bool:
    """Trial-division primality for GF(p)[x]; exact integer arithmetic."""
    if isinstance(p, float):
        raise TypeError("p: float64 leakage refused")
    p = int(p)
    if not _is_prime(p):
        raise ValueError(f"p must be prime, got {p}")
    poly = _strip([int(c) % p for c in poly])
    n = len(poly) - 1
    if n < 1 or poly[-1] == 0:
        return False
    d = 1
    while d * 2 <= n:
        for q in _monic_of_degree(d, p):
            if _modrem(poly, q, p) == [0]:
                return False
        d += 1
    return True


def find_modulus(n: int, p: int) -> list[int]:
    """First monic irreducible of degree n (lexicographic), verified."""
    if isinstance(n, float) or isinstance(p, float):
        raise TypeError("n/p: float64 leakage refused")
    n, p = int(n), int(p)
    if n == 1:
        return [0, 1]
    for cand in _monic_of_degree(n, p):
        if is_irreducible_mod(cand, p):
            return cand
    raise ValueError(f"no degree-{n} irreducible over F_{p}")


def _fadd(a: list[int], b: list[int], p: int) -> list[int]:
    return _add(a, b, p)


def _fmul(a: list[int], b: list[int], mod: list[int], p: int) -> list[int]:
    return _modrem(_mul(a, b, p), mod, p)


def _fpow4(a: list[int], mod: list[int], p: int) -> list[int]:
    a2 = _fmul(a, a, mod, p)
    return _fmul(a2, a2, mod, p)


def _field_elements(n: int, p: int) -> list[list[int]]:
    if n == 1:
        return [[c] for c in range(p)]
    return [[c for c in coeffs] for coeffs in product(range(p), repeat=n)]


def count_fermat_quartic_fpn(n: int, p: int = 3) -> dict:
    """Naive P^3(F_{p^n}) count of the Fermat quartic, chart-gated.

    Same canonical-representative discipline as the F_p counter
    (first nonzero coordinate is exactly 1). Total must equal the
    affine chart plus infinity, else RuntimeError. Cost is O(p^{3n}):
    viable only for tiny (n, p); larger reaches need character sums.
    """
    if isinstance(n, float) or isinstance(p, float):
        raise TypeError("n/p: float64 leakage refused")
    n, p = int(n), int(p)
    if not _is_prime(p) or p == 2:
        raise ValueError(f"p must be an odd prime, got {p}")
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    mod = find_modulus(n, p)
    elems = _field_elements(n, p)
    one = [1] + [0] * (n - 1)
    zero = [0] * n

    def is_zero(v: list[int]) -> bool:
        return all(c == 0 for c in v)

    def is_one(v: list[int]) -> bool:
        return len(v) >= 1 and v[0] == 1 and all(c == 0 for c in v[1:])

    total = 0
    for xyzw in product(elems, repeat=4):
        if all(is_zero(v) for v in xyzw):
            continue
        first = next(v for v in xyzw if not is_zero(v))
        if not is_one(first):
            continue
        s = zero
        for v in xyzw:
            s = _fadd(s, _fpow4(v, mod, p), p)
        if is_zero(s):
            total += 1
    affine = 0
    for xyz in product(elems, repeat=3):
        s = _fadd(one, _fpow4(xyz[0], mod, p), p)
        s = _fadd(s, _fpow4(xyz[1], mod, p), p)
        s = _fadd(s, _fpow4(xyz[2], mod, p), p)
        if is_zero(s):
            affine += 1
    infinity = 0
    for xyz in product(elems, repeat=3):
        if all(is_zero(v) for v in xyz):
            continue
        first = next(v for v in xyz if not is_zero(v))
        if not is_one(first):
            continue
        s = zero
        for v in xyz:
            s = _fadd(s, _fpow4(v, mod, p), p)
        if is_zero(s):
            infinity += 1
    if total != affine + infinity:
        raise RuntimeError(
            f"chart decomposition failed: {total} != {affine} + {infinity}"
        )
    return {"p": p, "n": n, "total": total, "affine": affine, "infinity": infinity}


def fermat_quartic_smooth(p: int) -> bool:
    """Jacobian gate: True iff no projective common zero of partials.

    Partials are 4x^3, ... (4 != 0 mod odd p, so only the origin is
    a common zero -- excluded from projective space). Checked by
    exhaustive enumeration over F_p (exact); refuses p = 2, where
    the gate is meaningless (identically singular).
    """
    if isinstance(p, float):
        raise TypeError("p: float64 leakage refused")
    p = int(p)
    if not _is_prime(p) or p == 2:
        raise ValueError(f"p must be an odd prime, got {p}")
    for xyzw in product(range(p), repeat=4):
        if all(v == 0 for v in xyzw):
            continue
        if all(pow(v, 3, p) == 0 for v in xyzw):
            return False
    return True


def _prime_factors(m: int) -> list[int]:
    out: list[int] = []
    d = 2
    while d * d <= m:
        if m % d == 0:
            out.append(d)
            while m % d == 0:
                m //= d
        d += 1 if d == 2 else 2
    if m > 1:
        out.append(m)
    return out


def _field_pow(a: list[int], e: int, mod: list[int], p: int) -> list[int]:
    r = [1]
    while e:
        if e & 1:
            r = _modrem(_mul(r, a, p), mod, p)
        a = _modrem(_mul(a, a, p), mod, p)
        e >>= 1
    return r


def _primitive_element(
    elems: list[list[int]], mod: list[int], p: int, q: int, n: int
) -> list[int]:
    one = _pad([1], n)
    for g in elems:
        if all(v == 0 for v in g):
            continue
        if all(
            _pad(_field_pow(g, (q - 1) // f, mod, p), n) != one
            for f in _prime_factors(q - 1)
        ):
            return g
    raise ValueError("no primitive element found")


def _trace_to_fp(a: list[int], mod: list[int], p: int, n: int) -> int:
    t = [0]
    cur = list(a)
    for _ in range(n):
        t = _add(t, cur, p)
        cur = _field_pow(cur, p, mod, p)
    return t[0] % p if t else 0


def _round_ball_to_int(v: acb, what: str) -> int:
    if not bool(v.real.rad() < arb("0.25")) or not bool(
        v.imag.rad() < arb("0.25")
    ):
        raise RuntimeError(f"{what}: enclosure too wide to certify")
    m = v.mid().real.str(20, radius=False)
    head = m.strip().lstrip("+-").split(".")[0] or "0"
    k0 = int(head)
    if m.strip().startswith("-"):
        k0 = -k0
    for k in (k0 - 2, k0 - 1, k0, k0 + 1, k0 + 2):
        if bool(v.real.contains(arb(k))) and bool(v.imag.contains(arb(0))):
            return k
    raise RuntimeError(f"{what}: no integer in enclosure")


def jacobi_trace(n: int, p: int = 3, prec_bits: int = 256) -> dict:
    """Fermat-quartic affine count over F_{p^n} via character sums.

    Gauss sums over the order-e character (e = gcd(4, p^n - 1)),
    grouped by root-of-unity class. The ball result must certify a
    unique integer (radius < 0.25), else RuntimeError -- never a
    silent round. Cross-validated against naive enumeration for
    small n; for e = 2 the closed form N_proj = (q+1)^2 holds by
    the same derivation.
    """
    if isinstance(n, float) or isinstance(p, float):
        raise TypeError("n/p: float64 leakage refused")
    if isinstance(prec_bits, float):
        raise TypeError("prec_bits: float64 leakage refused")
    n, p = int(n), int(p)
    if not _is_prime(p) or p == 2:
        raise ValueError(f"p must be an odd prime, got {p}")
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    ctx.prec = int(prec_bits)
    from math import gcd

    q = p**n
    e = gcd(4, q - 1)
    mod = find_modulus(n, p)
    elems = _field_elements(n, p)
    gen = _primitive_element(elems, mod, p, q, n)
    dlog: dict[tuple[int, ...], int] = {}
    cur = [1]
    for k in range(q - 1):
        dlog[_pad(cur, n)] = k
        cur = _modrem(_mul(cur, gen, p), mod, p)

    def zeta(k: int, m: int) -> acb:
        return acb(
            arb(fmpq(2 * k, m)).cos_pi(), arb(fmpq(2 * k, m)).sin_pi()
        )

    omega = zeta(1, p)

    def chi_pow(a: list[int], j: int) -> acb:
        if all(v == 0 for v in a):
            return acb(0)
        return zeta((j * dlog[_pad(a, n)]) % e, e)

    def psi(a: list[int]) -> acb:
        return omega ** _trace_to_fp(a, mod, p, n)

    taus = []
    for j in range(e):
        s = acb(0)
        for a in elems:
            s += chi_pow(a, j) * psi(a)
        taus.append(s)
    total = acb(0)
    for c in range(e):
        sc = acb(1) + sum(
            (zeta((-j * c) % e, e) * taus[j] for j in range(e)), acb(0)
        )
        total += sc * sc * sc * sc
    n_aff = acb(q**3) + total * acb(q - 1) / acb(e) / acb(q)
    n_aff_int = _round_ball_to_int(n_aff, f"affine count q={q}")
    if (n_aff_int - 1) % (q - 1) != 0:
        raise RuntimeError("projective descent failed")
    return {
        "p": p,
        "n": n,
        "q": q,
        "e": e,
        "affine": n_aff_int,
        "projective": (n_aff_int - 1) // (q - 1),
        "radius": n_aff.real.rad().str(4),
    }
