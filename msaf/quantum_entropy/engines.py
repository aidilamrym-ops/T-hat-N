"""Dual-precision engines for Campaign V2 (SIMULATED entropy).

Engine A: python-flint / Arb ball arithmetic at 6000 bits (ENGINE_A_BITS).
Engine B: mpmath at dps 50 with directed rounding on raw mpf pairs.

Landmine L41 discipline:

* ``lock_engine_a()`` must run before any Engine-A computation; every
  Engine-A entry point re-asserts ``ctx.prec`` and raises ``EngineDrift``
  on any drift.
* mpmath is imported lazily and its ``dps`` is (re)set inside every
  Engine-B entry call; no mpmath state survives between calls.

Control decisions are dual-engine: sign evaluations from Engine A and
Engine B must agree; when either engine is inconclusive the exact rational
recurrence (``det_sign_exact``) decides and the fallback is counted
(allowance frozen in the preregistration).
"""

from __future__ import annotations

import decimal
from fractions import Fraction

from flint import arb, ctx

from .intervals import parse_decimal

__all__ = [
    "ENGINE_A_BITS",
    "ENGINE_B_DPS",
    "EngineDrift",
    "MPBall",
    "a_ball",
    "a_det",
    "a_det_d",
    "a_frac",
    "a_newton",
    "assert_engine_a",
    "b_ball",
    "b_det",
    "b_det_d",
    "b_fmt",
    "b_newton",
    "b_point",
    "b_sign",
    "det_sign_a",
    "det_sign_b",
    "det_sign_exact",
    "lock_engine_a",
    "mpf_to_fraction",
    "a_fmt",
]

ENGINE_A_BITS = 6000
ENGINE_B_DPS = 50

_LOCKED = False


class EngineDrift(RuntimeError):
    """Engine A global precision drifted from the locked campaign value."""


def lock_engine_a(bits: int = ENGINE_A_BITS) -> int:
    """Lock ``flint.ctx.prec`` (L41: run before any dependent computation)."""
    global _LOCKED
    ctx.prec = int(bits)
    _LOCKED = True
    return ctx.prec


def assert_engine_a() -> None:
    if not _LOCKED:
        raise EngineDrift("engine A not locked: call lock_engine_a() first (L41)")
    if ctx.prec != ENGINE_A_BITS:
        raise EngineDrift(
            "engine A precision drifted: %s != %s" % (ctx.prec, ENGINE_A_BITS)
        )


# ---------------------------------------------------------------------------
# Engine A (Arb)
# ---------------------------------------------------------------------------


def a_frac(fr: Fraction) -> arb:
    """Exact rational -> tight Arb ball containing the exact value."""
    assert_engine_a()
    return arb(fr.numerator) / arb(fr.denominator)


def _frac_to_dec_str(fr: Fraction, digits: int = 120) -> str:
    """Correctly rounded decimal string (nearest) at ``digits`` precision."""
    dctx = decimal.Context(prec=digits, rounding=decimal.ROUND_HALF_EVEN)
    with decimal.localcontext(dctx):
        return str(
            dctx.divide(decimal.Decimal(fr.numerator), decimal.Decimal(fr.denominator))
        )


def a_ball(lo_fr: Fraction, hi_fr: Fraction) -> arb:
    """Arb ball guaranteed to contain the exact rational interval [lo, hi].

    Built through the string form ``[mid +/- rad]`` with outward-padded
    radius; the containment property is checked in the selftest.
    """
    assert_engine_a()
    if hi_fr < lo_fr:
        raise ValueError("hi < lo")
    if lo_fr == hi_fr:
        return a_frac(lo_fr)
    mid_fr = (lo_fr + hi_fr) / 2
    rad_fr = (hi_fr - lo_fr) / 2
    mid_str = _frac_to_dec_str(mid_fr)
    mid_err = abs(parse_decimal(mid_str) - mid_fr)
    rad_eff = rad_fr + mid_err + parse_decimal("1e-110")
    rad_str = _frac_to_dec_str(rad_eff)
    return arb("[%s +/- %s]" % (mid_str, rad_str))


def a_det(lam: arb, diag: list, off2: list) -> arb:
    """det(lam*I - A) for symmetric tridiagonal A, interval-safe recurrence."""
    assert_engine_a()
    pp2 = arb(0)
    pp1 = arb(1)
    for i, d in enumerate(diag):
        t = (lam - d) * pp1
        if i:
            t = t - off2[i - 1] * pp2
        pp2, pp1 = pp1, t
    return pp1


def a_det_d(lam: arb, diag: list, off2: list) -> arb:
    """d/dlam det(lam*I - A) via LDL pivots, never dividing by the last pivot.

    Mirrors the engine-B formulation in Arb arithmetic: with pivots
    v_1..v_n (v_i = det(leading i)/det(leading i-1)) and S = sum_{i<n}
    (v_i'/v_i):

        f' = (v_1 * ... * v_{n-1}) * (v_n * S + v_n')

    so a Newton ball containing the root (v_n straddles zero) is fine;
    only intermediate pivots v_1..v_{n-1} are inverted. The side-by-side
    naive derivative recurrence is NOT used: its interval widths grow like
    r_+^n of the recurrence (r_+ ~ 1.94 away from the oscillatory band),
    which was measured to straddle zero at campaign depths (probe 11).
    """
    assert_engine_a()
    if not diag:
        return arb(0)
    one = arb(1)
    v_prev = lam - diag[0]
    if len(diag) == 1:
        return one  # f = v_1, f' = 1
    q_prev = one / v_prev  # q_1 = v_1'/v_1
    s = q_prev
    prodprev = v_prev
    n = len(diag)
    for j2 in range(1, n):  # computes v_{j2+1}
        v_new = (lam - diag[j2]) - off2[j2 - 1] / v_prev
        vder_new = one + off2[j2 - 1] * q_prev / v_prev
        if j2 < n - 1:
            prodprev = prodprev * v_new
            q_new = vder_new / v_new
            s = s + q_new
            q_prev = q_new
        else:
            v_last = v_new
            vder_last = vder_new
        v_prev = v_new
    return prodprev * (vder_last + v_last * s)  # f' = prodprev*(v_n' + v_n*S)


def a_newton(
    lo_fr: Fraction,
    hi_fr: Fraction,
    diag: list,
    off2: list,
    iters: int,
    target_fr: Fraction,
) -> dict:
    """Interval Newton image iteration (contraction diagnostic, Engine A).

    x_{n+1} = mid(x_n) - f(mid)/f'(x_n); the image contains any root of f
    lying in x_n whenever f'(x_n) excludes zero. Widths are recorded.
    """
    assert_engine_a()
    x = a_ball(lo_fr, hi_fr)
    if not (x.contains(a_frac(lo_fr)) and x.contains(a_frac(hi_fr))):
        raise RuntimeError("a_ball containment precheck failed")
    target = a_frac(target_fr)
    widths = []
    status = "CONTRACTED"
    for _ in range(iters):
        w = 2 * x.rad()
        widths.append(w)
        if (w - target) <= 0:
            break
        m = x.mid()
        fx = a_det(m, diag, off2)
        dfx = a_det_d(x, diag, off2)
        if not (dfx > 0) and not (dfx < 0):
            status = "DERIVATIVE_AMBIGUOUS"
            break
        x = m - fx / dfx
    else:
        if (2 * x.rad() - target) > 0:
            status = "CAP_REACHED"
    return {"ball": x, "widths": widths, "status": status}


def det_sign_a(lam_fr: Fraction, diag: list, off2: list) -> int:
    """+1 / -1 when the Arb det ball is one-sided; 0 = inconclusive."""
    assert_engine_a()
    d = a_det(a_frac(lam_fr), diag, off2)
    if d > 0:
        return 1
    if d < 0:
        return -1
    return 0


def pivot_count_a(lam_fr: Fraction, diag: list, off2: list):
    """Interval Sturm count via Arb LDL pivots: #{lambda_j < lam}.

    For ``lam*I - A`` the count of strictly positive LDL pivots equals
    #{lambda_j < lam} (Sylvester inertia at a rational point). Returns None
    (ambiguous) if any pivot ball touches zero.
    """
    assert_engine_a()
    lam_a = a_frac(lam_fr)
    cur = lam_a - diag[0]
    cnt = 0
    if cur > 0:
        cnt = 1
    elif cur < 0:
        pass
    else:
        return None
    for i in range(1, len(diag)):
        cur = (lam_a - diag[i]) - off2[i - 1] / cur
        if cur > 0:
            cnt += 1
        elif cur < 0:
            continue
        else:
            return None
    return cnt


def a_fmt(x: arb, cap: int = 120) -> str:
    s = str(x)
    return s if len(s) <= cap else s[:cap] + "...<cut>"


# ---------------------------------------------------------------------------
# Exact rational control path (no rounding anywhere)
# ---------------------------------------------------------------------------


def det_sign_exact(lam_fr: Fraction, diag_fr: list, off2_fr: list) -> int:
    """Exact sign of det(lam*I - A) for rational lam; 0 = exact eigenvalue."""
    pp2 = Fraction(0)
    pp1 = Fraction(1)
    for i, d in enumerate(diag_fr):
        t = (lam_fr - d) * pp1
        if i:
            t = t - off2_fr[i - 1] * pp2
        pp2, pp1 = pp1, t
    if pp1 > 0:
        return 1
    if pp1 < 0:
        return -1
    return 0


def pivot_sign_counts(lam_fr: Fraction, diag_fr: list, off2_fr: list):
    """Exact (lt, le) eigenvalue counts vs lam via LDL pivots of lam*I - A.

    Positive pivots count eigenvalues strictly below lam (Sylvester
    inertia); zero pivots (leading-minor eigenvalue hit) widen to le.
    Returns None on a zero pivot mid-sequence (caller treats as fatal or
    shifts; the campaign never expects this case).
    """
    n = len(diag_fr)
    d = lam_fr - diag_fr[0]
    lt = 1 if d > 0 else 0
    zeros = 1 if d == 0 else 0
    prev = d
    for i in range(1, n):
        if prev == 0:
            return None
        prev = (lam_fr - diag_fr[i]) - off2_fr[i - 1] / prev
        if prev > 0:
            lt += 1
        elif prev == 0:
            zeros += 1
    return lt, lt + zeros


# ---------------------------------------------------------------------------
# Engine B (mpmath, directed rounding on raw mpf pairs)
# ---------------------------------------------------------------------------


class MPBall:
    """Directed-rounding interval over mpmath raw mpf endpoints."""

    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi):
        self.lo = lo
        self.hi = hi


def _b_env() -> int:
    import mpmath as mp

    mp.mp.dps = ENGINE_B_DPS
    return mp.mp.prec


def b_point(fr: Fraction) -> MPBall:
    p = _b_env()
    from mpmath.libmp import from_rational, round_ceiling, round_floor

    return MPBall(
        from_rational(fr.numerator, fr.denominator, p, round_floor),
        from_rational(fr.numerator, fr.denominator, p, round_ceiling),
    )


def b_ball(lo_fr: Fraction, hi_fr: Fraction) -> MPBall:
    p = _b_env()
    from mpmath.libmp import from_rational, round_ceiling, round_floor

    return MPBall(
        from_rational(lo_fr.numerator, lo_fr.denominator, p, round_floor),
        from_rational(hi_fr.numerator, hi_fr.denominator, p, round_ceiling),
    )


def _b_add(a: MPBall, b: MPBall, p: int) -> MPBall:
    from mpmath.libmp import mpf_add, round_ceiling, round_floor

    return MPBall(
        mpf_add(a.lo, b.lo, p, round_floor), mpf_add(a.hi, b.hi, p, round_ceiling)
    )


def _b_sub(a: MPBall, b: MPBall, p: int) -> MPBall:
    from mpmath.libmp import mpf_sub, round_ceiling, round_floor

    return MPBall(
        mpf_sub(a.lo, b.hi, p, round_floor), mpf_sub(a.hi, b.lo, p, round_ceiling)
    )


def _mpf_min4(x1, x2, x3, x4):
    """Numeric minimum of four raw mpf tuples (NOT lexicographic)."""
    from mpmath.libmp import mpf_lt

    m = x1
    if mpf_lt(x2, m):
        m = x2
    if mpf_lt(x3, m):
        m = x3
    if mpf_lt(x4, m):
        m = x4
    return m


def _mpf_max4(x1, x2, x3, x4):
    """Numeric maximum of four raw mpf tuples (NOT lexicographic)."""
    from mpmath.libmp import mpf_lt

    m = x1
    if mpf_lt(m, x2):
        m = x2
    if mpf_lt(m, x3):
        m = x3
    if mpf_lt(m, x4):
        m = x4
    return m


def _b_mul(a: MPBall, b: MPBall, p: int) -> MPBall:
    from mpmath.libmp import mpf_mul, round_ceiling, round_floor

    lo = _mpf_min4(
        mpf_mul(a.lo, b.lo, p, round_floor),
        mpf_mul(a.lo, b.hi, p, round_floor),
        mpf_mul(a.hi, b.lo, p, round_floor),
        mpf_mul(a.hi, b.hi, p, round_floor),
    )
    hi = _mpf_max4(
        mpf_mul(a.lo, b.lo, p, round_ceiling),
        mpf_mul(a.lo, b.hi, p, round_ceiling),
        mpf_mul(a.hi, b.lo, p, round_ceiling),
        mpf_mul(a.hi, b.hi, p, round_ceiling),
    )
    return MPBall(lo, hi)


def _b_recip(a: MPBall, p: int) -> MPBall:
    from mpmath.libmp import fone, fzero, mpf_div, mpf_lt, round_ceiling, round_floor

    if mpf_lt(fzero, a.lo) or mpf_lt(a.hi, fzero):
        return MPBall(
            mpf_div(fone, a.hi, p, round_floor), mpf_div(fone, a.lo, p, round_ceiling)
        )
    raise ZeroDivisionError("engine B interval straddles zero")


def _b_div(a: MPBall, b: MPBall, p: int) -> MPBall:
    return _b_mul(a, _b_recip(b, p), p)


def b_sign(x: MPBall) -> int:
    from mpmath.libmp import fzero, mpf_lt

    if mpf_lt(fzero, x.lo):
        return 1
    if mpf_lt(x.hi, fzero):
        return -1
    return 0


def b_det(lam: MPBall, diag: list, off2: list) -> MPBall:
    """det(lam*I - A) as the LDL pivot product (stable relative enclosure).

    The naive recurrence has widths that grow like r_+^(2D) (r_+ >= 1); the
    pivot product p_1 * ... * p_D keeps pivot widths relatively bounded, so
    the enclosure stays usable at dps 50 for all campaign dimensions.
    """
    p = _b_env()
    if not diag:
        return b_point(Fraction(1))
    cur = _b_sub(lam, diag[0], p)  # p_1 = lam - a_1
    prod = cur
    for i in range(1, len(diag)):
        cur = _b_sub(_b_sub(lam, diag[i], p), _b_div(off2[i - 1], cur, p), p)
        prod = _b_mul(prod, cur, p)
    return prod


def b_det_d(lam: MPBall, diag: list, off2: list) -> MPBall:
    """d/dlam det(lam*I - A) via pivots, never dividing by the last pivot.

    With pivots v_1..v_n and S = sum_{i<n} (v_i'/v_i):

        f' = (v_1 * ... * v_{n-1}) * (v_n * S + v_n')

    so an isolation ball containing the root (v_n straddles zero) is fine;
    only intermediate pivots v_1..v_{n-1} are ever inverted.
    """
    p = _b_env()
    if not diag:
        return b_point(Fraction(0))
    one_b = b_point(Fraction(1))
    v_prev = _b_sub(lam, diag[0], p)  # v_1
    if len(diag) == 1:
        return one_b  # f = v_1, f' = 1
    q_prev = _b_div(one_b, v_prev, p)  # q_1 = v_1'/v_1 = 1/v_1
    s = q_prev
    prodprev = v_prev  # product of v_1..v_{j-1}
    n = len(diag)
    for j2 in range(1, n):  # computes v_{j2+1}
        v_new = _b_sub(
            _b_sub(lam, diag[j2], p), _b_div(off2[j2 - 1], v_prev, p), p
        )
        vder_new = _b_add(
            one_b, _b_div(_b_mul(off2[j2 - 1], q_prev, p), v_prev, p), p
        )  # v_j' = 1 + b^2 * q_{j-1} / v_{j-1}
        if j2 < n - 1:
            prodprev = _b_mul(prodprev, v_new, p)
            q_new = _b_div(vder_new, v_new, p)
            s = _b_add(s, q_new, p)
            q_prev = q_new
        else:
            v_last = v_new
            vder_last = vder_new
        v_prev = v_new
    return _b_mul(
        prodprev, _b_add(vder_last, _b_mul(v_last, s, p), p), p
    )  # f' = prodprev * (v_n' + v_n * S)


def det_sign_b(lam_fr: Fraction, diag: list, off2: list) -> int:
    """+1 / -1 when the directed mpf det ball is one-sided; 0 = inconclusive
    (pivot straddle or ball containing zero)."""
    try:
        d = b_det(b_point(lam_fr), diag, off2)
    except ZeroDivisionError:
        return 0
    return b_sign(d)


def pivot_count_b(lam_fr: Fraction, diag: list, off2: list):
    """Interval Sturm count via directed-rounding mpf LDL pivots.

    Mirrors :func:`pivot_count_a` at dps 50 (counts strictly positive
    pivots of ``lam*I - A``); returns None on any pivot straddle or
    division failure (ambiguous step -> exact fallback).
    """
    p = _b_env()
    lam_b = b_point(lam_fr)
    cur = _b_sub(lam_b, diag[0], p)
    sgn = b_sign(cur)
    if sgn == 0:
        return None
    cnt = 1 if sgn > 0 else 0
    for i in range(1, len(diag)):
        try:
            cur = _b_sub(_b_sub(lam_b, diag[i], p), _b_div(off2[i - 1], cur, p), p)
        except ZeroDivisionError:
            return None
        sgn = b_sign(cur)
        if sgn == 0:
            return None
        if sgn > 0:
            cnt += 1
    return cnt


def mpf_to_fraction(x) -> Fraction:
    """Raw mpf tuple -> exact Fraction (libmp sign convention: 1 = negative)."""
    sign, man, exp, bc = x
    if not man:
        return Fraction(0)
    mag = Fraction(man) * Fraction(2) ** int(exp)
    return -mag if sign else mag


def b_newton(
    lo_fr: Fraction,
    hi_fr: Fraction,
    diag: list,
    off2: list,
    iters: int,
    target_fr: Fraction,
) -> dict:
    """Directed-rounding Newton image iteration (Engine B mirror)."""
    p = _b_env()
    from mpmath.libmp import mpf_lt

    x = b_ball(lo_fr, hi_fr)
    widths = []
    status = "CONTRACTED"
    for _ in range(iters):
        w_fr = mpf_to_fraction(x.hi) - mpf_to_fraction(x.lo)
        widths.append(w_fr)
        if w_fr <= target_fr:
            break
        mid_fr = (mpf_to_fraction(x.lo) + mpf_to_fraction(x.hi)) / 2
        m = b_point(mid_fr)
        try:
            fx = b_det(m, diag, off2)
            dfx = b_det_d(x, diag, off2)
        except ZeroDivisionError:
            status = "VALUE_AMBIGUOUS"
            break
        if b_sign(dfx) == 0:
            status = "DERIVATIVE_AMBIGUOUS"
            break
        x = _b_sub(m, _b_div(fx, dfx, p), p)
        if mpf_lt(x.hi, x.lo):
            status = "BROKEN_IMAGE"
            break
    else:
        w_fr = mpf_to_fraction(x.hi) - mpf_to_fraction(x.lo)
        if w_fr > target_fr:
            status = "CAP_REACHED"
    return {"ball": x, "widths": widths, "status": status}


def b_fmt(x: MPBall, digits: int = 30) -> str:
    from mpmath.libmp import to_str

    return "[%s, %s]" % (to_str(x.lo, digits), to_str(x.hi, digits))
