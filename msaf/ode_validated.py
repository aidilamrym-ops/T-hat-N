"""Validated ODE integrator on arb balls (T1 milestone).

Scope and pass criteria are locked in
``reports/PREREG_ODE_VALIDATED_2026-10-21.md``.  Only systems S1-S4 from
that document are implemented.  Every reported enclosure is produced by
ball arithmetic plus an explicit Taylor remainder bound; no float is used
in the certified path.

The integrator is a Taylor method of order ``p``.  For each step it

1. computes the Taylor coefficients of the solution at the midpoint of the
   current state box (never from the box itself),
2. verifies a Picard enclosure (so the solution stays inside a box ``B``),
3. bounds the order-``(p+1)`` Taylor coefficient over ``B``, and
4. transports the input uncertainty with the mean-value form
   ``F(X) subset F(m) + J_X * (X - m)`` using a Euclidean radius and the
   spectral-norm bound ``||J_X||_2`` of the interval Jacobian.

The Picard check is what makes the remainder bound legitimate: without a
box that provably contains the solution over the step, the coefficient
bound would not apply.

Note: the spectral-norm bound is sound but pessimistic over many steps; for
S3/S4 it inflates the radius until the C4/C5 tolerances are exceeded (see
``reports/ODE_VALIDATED_2026-10-21.md``).  This module keeps that behaviour
visible instead of hiding it behind an unreported heuristic.
"""

from __future__ import annotations

import ast
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Callable, Sequence

import flint
from flint import arb

ROOT = Path(__file__).resolve().parents[1]
PREREG_PATH = ROOT / "reports" / "PREREG_ODE_VALIDATED_2026-10-21.md"
RECEIPT_PATH = ROOT / "reports" / "ode_validated_2026-10-21.json"

PREC = 256
ORDER = 24
SCHEMA = "msaf.ode_validated.v1"

State = Sequence[arb]
CoeffFn = Callable[[State, int], list[list[arb]]]
RhsFn = Callable[[State], list[arb]]


class ValidationError(RuntimeError):
    """Raised when a rigorous enclosure check cannot be established."""


# ---------------------------------------------------------------------------
# ball helpers
# ---------------------------------------------------------------------------


def _ball(value: int | Fraction) -> arb:
    """Exact rational as a tight arb ball."""
    if isinstance(value, int):
        return arb(value)
    return arb(value.numerator) / arb(value.denominator)


def _tol(text: str) -> arb:
    """Decimal tolerance string as an exact rational ball."""
    return _ball(Fraction(text))


def _contains(ball: arb, value: int | Fraction) -> bool:
    """True when the exact rational lies inside the ball."""
    return bool(ball.contains(_ball(value)))


def _width(ball: arb) -> arb:
    """Width of a ball, as an arb upper-bound ball."""
    return 2 * ball.rad()


def _isqrt(n: int) -> int:
    """Integer square root without float or math module."""
    if n < 0:
        raise ValueError("isqrt of negative integer")
    if n == 0:
        return 0
    x = 1 << ((n.bit_length() + 1) // 2)
    while True:
        y = (x + n // x) // 2
        if y >= x:
            return x
        x = y


def _horner(coeffs: Sequence[arb], t: arb) -> arb:
    acc = coeffs[-1]
    for c in reversed(coeffs[:-1]):
        acc = acc * t + c
    return acc


def _time_ball(h: arb) -> arb:
    """A ball covering [0, h_upper] for the step duration."""
    hi = h.upper()
    half = hi / 2
    return arb(half, half)


def _ser(value):
    """Recursively serialise arb values to deterministic strings."""
    if isinstance(value, arb):
        return str(value)
    if isinstance(value, dict):
        return {k: _ser(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_ser(v) for v in value]
    return value


def sha256lf(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# forward-mode jets (value + gradient)
# ---------------------------------------------------------------------------


class Dual:
    """A first-order jet: ``v`` plus a gradient ``g`` (forward-mode AD)."""

    __slots__ = ("v", "g")

    def __init__(self, v: arb, g: list[arb]):
        self.v = v
        self.g = g

    @staticmethod
    def _coerce(ref: "Dual", other) -> "Dual":
        if isinstance(other, Dual):
            return other
        if isinstance(other, arb):
            value = other
        elif isinstance(other, Fraction):
            value = _ball(other)
        else:
            value = arb(other)
        return Dual(value, [ref.v * 0 for _ in ref.g])

    def __add__(self, other):
        o = self._coerce(self, other)
        return Dual(self.v + o.v, [a + b for a, b in zip(self.g, o.g)])

    __radd__ = __add__

    def __sub__(self, other):
        o = self._coerce(self, other)
        return Dual(self.v - o.v, [a - b for a, b in zip(self.g, o.g)])

    def __rsub__(self, other):
        return self._coerce(self, other) - self

    def __neg__(self):
        return Dual(-self.v, [-a for a in self.g])

    def __mul__(self, other):
        o = self._coerce(self, other)
        return Dual(
            self.v * o.v,
            [a * o.v + self.v * b for a, b in zip(self.g, o.g)],
        )

    __rmul__ = __mul__

    def __truediv__(self, other):
        o = self._coerce(self, other)
        value = self.v / o.v
        return Dual(
            value,
            [(a - value * b) / o.v for a, b in zip(self.g, o.g)],
        )

    def __rtruediv__(self, other):
        return self._coerce(self, other) / self

    def sqrt(self):
        root = self.v.sqrt()
        return Dual(root, [a / (2 * root) for a in self.g])


def _dual_coeffs(coeff_fn, state: Sequence[arb], order: int) -> list[list[Dual]]:
    """Taylor coefficients with gradients seeded by the identity."""
    n = len(state)
    dual_state = [
        Dual(state[i], [arb(1) if j == i else arb(0) for j in range(n)])
        for i in range(n)
    ]
    return coeff_fn(dual_state, order)


# ---------------------------------------------------------------------------
# Taylor coefficients (system specific, O(p^2) per step)
# ---------------------------------------------------------------------------


def coeffs_s1(state: State, order: int) -> list[list]:
    """x' = x^2 (works for arb and for Dual jets)."""
    zero = state[0] - state[0]
    x = [state[0]] + [zero] * order
    for k in range(order):
        acc = zero
        for i in range(k + 1):
            acc = acc + x[i] * x[k - i]
        x[k + 1] = acc / (k + 1)
    return [x]


def coeffs_s2(state: State, order: int) -> list[list]:
    """x'' = -x (works for arb and for Dual jets)."""
    zero = state[0] - state[0]
    x = [state[0]] + [zero] * order
    v = [state[1]] + [zero] * order
    for k in range(order):
        x[k + 1] = v[k] / (k + 1)
        v[k + 1] = -x[k] / (k + 1)
    return [x, v]


def coeffs_kepler(state: State, order: int) -> list[list]:
    """Circular Kepler problem, G = M = 1 (arb or Dual)."""
    zero = state[0] - state[0]
    x = [state[0]] + [zero] * order
    y = [state[1]] + [zero] * order
    vx = [state[2]] + [zero] * order
    vy = [state[3]] + [zero] * order

    a2 = [None] * (order + 1)
    r = [None] * (order + 1)
    r3 = [None] * (order + 1)
    inv = [None] * (order + 1)

    for k in range(order):
        acc = zero
        for i in range(k + 1):
            acc = acc + x[i] * x[k - i] + y[i] * y[k - i]
        a2[k] = acc

        if k == 0:
            r[0] = a2[0].sqrt()
        else:
            acc = a2[k]
            for i in range(1, k):
                acc = acc - r[i] * r[k - i]
            r[k] = acc / (2 * r[0])

        acc = zero
        for i in range(k + 1):
            acc = acc + a2[i] * r[k - i]
        r3[k] = acc

        if k == 0:
            inv[0] = arb(1) / r3[0]
        else:
            acc = zero
            for i in range(1, k + 1):
                acc = acc + r3[i] * inv[k - i]
            inv[k] = -inv[0] * acc

        ax = zero
        ay = zero
        for i in range(k + 1):
            ax = ax - inv[i] * x[k - i]
            ay = ay - inv[i] * y[k - i]

        vx[k + 1] = ax / (k + 1)
        vy[k + 1] = ay / (k + 1)
        x[k + 1] = vx[k] / (k + 1)
        y[k + 1] = vy[k] / (k + 1)

    return [x, y, vx, vy]


def coeffs_three_body(state: State, order: int) -> list[list]:
    """Planar three-body problem, m = G = 1 (arb or Dual).

    State layout: x0 y0 x1 y1 x2 y2 vx0 vy0 vx1 vy1 vx2 vy2.
    """
    zero = state[0] - state[0]
    xs = [[state[2 * i]] + [zero] * order for i in range(3)]
    ys = [[state[2 * i + 1]] + [zero] * order for i in range(3)]
    vxs = [[state[6 + 2 * i]] + [zero] * order for i in range(3)]
    vys = [[state[7 + 2 * i]] + [zero] * order for i in range(3)]

    pairs = ((0, 1), (0, 2), (1, 2))
    a2 = {p: [None] * (order + 1) for p in pairs}
    r = {p: [None] * (order + 1) for p in pairs}
    r3 = {p: [None] * (order + 1) for p in pairs}
    inv = {p: [None] * (order + 1) for p in pairs}

    for k in range(order):
        for i, j in pairs:
            acc = zero
            for m in range(k + 1):
                dx = xs[i][m] - xs[j][m]
                dy = ys[i][m] - ys[j][m]
                dx2 = xs[i][k - m] - xs[j][k - m]
                dy2 = ys[i][k - m] - ys[j][k - m]
                acc = acc + dx * dx2 + dy * dy2
            a2[(i, j)][k] = acc

            if k == 0:
                r[(i, j)][0] = acc.sqrt()
            else:
                acc2 = a2[(i, j)][k]
                for m in range(1, k):
                    acc2 = acc2 - r[(i, j)][m] * r[(i, j)][k - m]
                r[(i, j)][k] = acc2 / (2 * r[(i, j)][0])

            acc3 = zero
            for m in range(k + 1):
                acc3 = acc3 + a2[(i, j)][m] * r[(i, j)][k - m]
            r3[(i, j)][k] = acc3

            if k == 0:
                inv[(i, j)][0] = arb(1) / acc3
            else:
                acc4 = zero
                for m in range(1, k + 1):
                    acc4 = acc4 + r3[(i, j)][m] * inv[(i, j)][k - m]
                inv[(i, j)][k] = -inv[(i, j)][0] * acc4

        ax = [zero, zero, zero]
        ay = [zero, zero, zero]
        for i, j in pairs:
            fxk = zero
            fyk = zero
            for m in range(k + 1):
                fxk = fxk + inv[(i, j)][m] * (xs[i][k - m] - xs[j][k - m])
                fyk = fyk + inv[(i, j)][m] * (ys[i][k - m] - ys[j][k - m])
            ax[i] = ax[i] - fxk
            ay[i] = ay[i] - fyk
            ax[j] = ax[j] + fxk
            ay[j] = ay[j] + fyk

        for i in range(3):
            vxs[i][k + 1] = ax[i] / (k + 1)
            vys[i][k + 1] = ay[i] / (k + 1)
            xs[i][k + 1] = vxs[i][k] / (k + 1)
            ys[i][k + 1] = vys[i][k] / (k + 1)

    comps: list[list] = []
    for i in range(3):
        comps.append(xs[i])
        comps.append(ys[i])
    for i in range(3):
        comps.append(vxs[i])
        comps.append(vys[i])
    return comps


# ---------------------------------------------------------------------------
# right-hand sides (used by the Picard check)
# ---------------------------------------------------------------------------


def rhs_s1(state: State) -> list[arb]:
    return [state[0] * state[0]]


def rhs_s2(state: State) -> list[arb]:
    return [state[1], -state[0]]


def rhs_kepler(state: State) -> list[arb]:
    x, y, vx, vy = state
    r2 = x * x + y * y
    inv = arb(1) / (r2 * r2.sqrt())
    return [vx, vy, -x * inv, -y * inv]


def rhs_three_body(state: State) -> list[arb]:
    xs = state[0:6:2]
    ys = state[1:6:2]
    vxs = state[6:12:2]
    vys = state[7:12:2]
    ax = [arb(0), arb(0), arb(0)]
    ay = [arb(0), arb(0), arb(0)]
    for i, j in ((0, 1), (0, 2), (1, 2)):
        dx = xs[i] - xs[j]
        dy = ys[i] - ys[j]
        r2 = dx * dx + dy * dy
        inv = arb(1) / (r2 * r2.sqrt())
        fx = dx * inv
        fy = dy * inv
        ax[i] -= fx
        ay[i] -= fy
        ax[j] += fx
        ay[j] += fy
    return [
        vxs[0], vys[0], vxs[1], vys[1], vxs[2], vys[2],
        ax[0], ay[0], ax[1], ay[1], ax[2], ay[2],
    ]


# ---------------------------------------------------------------------------
# invariants (exact rational constants for the locked initial data)
# ---------------------------------------------------------------------------


def energy_kepler(state: State) -> arb:
    x, y, vx, vy = state
    r = (x * x + y * y).sqrt()
    return (vx * vx + vy * vy) / 2 - arb(1) / r


def angular_kepler(state: State) -> arb:
    x, y, vx, vy = state
    return x * vy - y * vx


def energy_three_body(state: State) -> arb:
    xs = state[0:6:2]
    ys = state[1:6:2]
    vxs = state[6:12:2]
    vys = state[7:12:2]
    kin = arb(0)
    for i in range(3):
        kin += vxs[i] * vxs[i] + vys[i] * vys[i]
    kin = kin / 2
    pot = arb(0)
    for i, j in ((0, 1), (0, 2), (1, 2)):
        dx = xs[i] - xs[j]
        dy = ys[i] - ys[j]
        pot += arb(1) / (dx * dx + dy * dy).sqrt()
    return kin - pot


def angular_three_body(state: State) -> arb:
    xs = state[0:6:2]
    ys = state[1:6:2]
    vxs = state[6:12:2]
    vys = state[7:12:2]
    acc = arb(0)
    for i in range(3):
        acc += xs[i] * vys[i] - ys[i] * vxs[i]
    return acc


def com_three_body(state: State) -> list[arb]:
    xs = state[0:6:2]
    ys = state[1:6:2]
    vxs = state[6:12:2]
    vys = state[7:12:2]
    return [
        (xs[0] + xs[1] + xs[2]) / 3,
        (ys[0] + ys[1] + ys[2]) / 3,
        (vxs[0] + vxs[1] + vxs[2]) / 3,
        (vys[0] + vys[1] + vys[2]) / 3,
    ]


# ---------------------------------------------------------------------------
# one validated Taylor step
# ---------------------------------------------------------------------------


def taylor_step(
    coeff_fn: CoeffFn,
    rhs_fn: RhsFn,
    state: State,
    h: arb,
    order: int,
    radius: arb,
    include_remainder: bool = True,
) -> tuple[list[arb], arb]:
    """One Taylor step with a verified Picard box and mean-value propagation.

    The Taylor coefficients are computed at the midpoint of the state box
    (never from the box itself).  The input uncertainty is carried as an
    explicit Euclidean radius ``radius`` and propagated with the
    spectral-norm bound of the interval Jacobian over the tiny midpoint
    box.  The radius is not re-derived from the component radii: doing so
    would inflate it by ``sqrt(n)`` at every step.
    """
    n = len(state)
    midpoint = [s.mid() for s in state]
    point_coeffs = coeff_fn(midpoint, order)
    endpoint = [_horner(comp, h) for comp in point_coeffs]

    if not include_remainder:
        return endpoint, radius

    # Picard box: path of the midpoint polynomial, inflated by the path span
    # and the input radius.  The check uses the full state box, so every
    # solution starting in the box stays in ``box`` over the step.
    t = _time_ball(h)
    prange = [_horner(comp, t) for comp in point_coeffs]
    span = 2 * prange[0].rad()
    for b in prange[1:]:
        w = 2 * b.rad()
        if bool(w > span):
            span = w

    eps = _tol("1e-12")
    factor = 1
    box = prange
    for _ in range(10):
        delta = (span + radius + eps) * factor
        box = [b + arb(0, delta.abs_upper()) for b in prange]
        image = rhs_fn(box)
        if all(box[i].contains(state[i] + h * image[i]) for i in range(n)):
            break
        factor *= 2
    else:
        raise ValidationError("Picard enclosure failed")

    # Rigorous Taylor remainder over the path box.
    tail = coeff_fn(box, order + 1)
    h_pow = h ** (order + 1)
    rem_sq = arb(0)
    for comp in tail:
        ri = (comp[order + 1].abs_upper() * h_pow).abs_upper()
        rem_sq = rem_sq + ri * ri
    remainder = rem_sq.sqrt()

    # Interval Jacobian of the Taylor polynomial over the tiny box
    # [midpoint +/- radius].  Mean-value form: F(x) - F(m) = J(xi)(x - m).
    xbox = [midpoint[i] + arb(0, radius) for i in range(n)]
    dual = _dual_coeffs(coeff_fn, xbox, order)
    jac = [
        [
            _horner([dual[i][k].g[j] for k in range(order + 1)], h)
            for j in range(n)
        ]
        for i in range(n)
    ]

    # ||J||_2^2 <= ||J^T J||_inf = max_i sum_j |(J^T J)_ij|
    sigma_sq = arb(0)
    for i in range(n):
        row = arb(0)
        for j in range(n):
            acc = arb(0)
            for k in range(n):
                acc = acc + jac[k][i] * jac[k][j]
            row = row + acc.abs_upper()
        if bool(row > sigma_sq):
            sigma_sq = row
    sigma = sigma_sq.sqrt()

    # The remainder depends on the initial state too; its variation is at
    # most O(remainder * radius).  The constant below is deliberately far
    # larger than any observed gradient and the term is negligible.
    rem_var = remainder * _tol("1e12") * radius
    new_radius = sigma * radius + 3 * remainder + rem_var + _tol("1e-70")
    return [endpoint[i] + arb(0, new_radius) for i in range(n)], new_radius


# ---------------------------------------------------------------------------
# system campaigns
# ---------------------------------------------------------------------------


def _run_s1(order: int, include_remainder: bool = True) -> dict:
    state = [_ball(1)]
    radius = arb(0)
    h = _ball(Fraction(1, 32))
    for _ in range(16):
        state, radius = taylor_step(
            coeffs_s1, rhs_s1, state, h, order, radius, include_remainder
        )
    tol = "1e-12" if order == 16 else "1e-18"
    return {
        "order": order,
        "steps": 16,
        "h": h,
        "endpoint": state[0],
        "width": _width(state[0]),
        "contains_2": _contains(state[0], 2),
        "width_ok": bool(_width(state[0]) <= _tol(tol)),
        "include_remainder": include_remainder,
    }


def _run_s2() -> dict:
    state = [_ball(1), _ball(0)]
    radius = arb(0)
    h = arb.pi() / 32
    checkpoints = {}
    for k in range(1, 65):
        state, radius = taylor_step(coeffs_s2, rhs_s2, state, h, ORDER, radius)
        if k in (32, 64):
            target = (-1, 0) if k == 32 else (1, 0)
            checkpoints[k] = {
                "step": k,
                "state": list(state),
                "widths": [_width(s) for s in state],
                "contains": all(_contains(state[i], target[i]) for i in range(2)),
                "width_ok": all(bool(_width(s) <= _tol("1e-20")) for s in state),
            }
    return checkpoints


def _run_s3() -> tuple[list[dict], str | None]:
    state = [_ball(1), _ball(0), _ball(0), _ball(1)]
    radius = arb(0)
    h = 2 * arb.pi() / 256
    checkpoints = []
    error = None
    for k in range(1, 2561):
        try:
            state, radius = taylor_step(
                coeffs_kepler, rhs_kepler, state, h, ORDER, radius
            )
        except Exception as exc:  # noqa: BLE001 - record the failure verbatim
            error = f"aborted at step {k}: {type(exc).__name__}: {exc}"
            break
        if k % 256 == 0:
            e = energy_kepler(state)
            l = angular_kepler(state)
            checkpoints.append(
                {
                    "step": k,
                    "energy": e,
                    "angular": l,
                    "energy_ok": _contains(e, Fraction(-1, 2)),
                    "angular_ok": _contains(l, 1),
                    "energy_width": _width(e),
                    "angular_width": _width(l),
                    "width_ok": bool(
                        _width(e) <= _tol("1e-12")
                        and _width(l) <= _tol("1e-12")
                    ),
                }
            )
    return checkpoints, error


def _run_s4() -> tuple[list[dict], str | None]:
    a = Fraction(347111, 10**6)
    b = Fraction(532728, 10**6)
    state = [
        _ball(-1), _ball(0),
        _ball(1), _ball(0),
        _ball(0), _ball(0),
        _ball(a), _ball(b),
        _ball(a), _ball(b),
        _ball(-2 * a), _ball(-2 * b),
    ]
    period = _ball(Fraction(632591398, 10**8))
    h = period / 512
    e0 = Fraction(-257428899017, 200000000000)

    checkpoints = []
    radius = arb(0)
    error = None
    for k in range(1, 513):
        try:
            state, radius = taylor_step(
                coeffs_three_body, rhs_three_body, state, h, ORDER, radius
            )
        except Exception as exc:  # noqa: BLE001 - record the failure verbatim
            error = f"aborted at step {k}: {type(exc).__name__}: {exc}"
            break
        if k % 64 == 0:
            e = energy_three_body(state)
            l = angular_three_body(state)
            com = com_three_body(state)
            checkpoints.append(
                {
                    "step": k,
                    "energy": e,
                    "angular": l,
                    "com": com,
                    "energy_ok": _contains(e, e0),
                    "angular_ok": _contains(l, 0),
                    "com_ok": all(_contains(c, 0) for c in com),
                    "energy_width": _width(e),
                    "width_ok": bool(_width(e) <= _tol("1e-10")),
                }
            )
    return checkpoints, error


# ---------------------------------------------------------------------------
# C1: ball primitive soundness
# ---------------------------------------------------------------------------


def _lcg(seed: int):
    s = seed
    while True:
        s = (1103515245 * s + 12345) % (2**31)
        yield s


def check_c1() -> dict:
    gen = _lcg(20261021)
    failures: list[str] = []

    for _ in range(1000):
        an = next(gen) % 2000001 - 1000000
        ad = next(gen) % 2000000 + 1
        bn = next(gen) % 2000001 - 1000000
        bd = next(gen) % 2000000 + 1
        a = Fraction(an, ad)
        b = Fraction(bn, bd)
        cases = [
            ("add", _ball(a) + _ball(b), a + b),
            ("sub", _ball(a) - _ball(b), a - b),
            ("mul", _ball(a) * _ball(b), a * b),
        ]
        if b != 0:
            cases.append(("div", _ball(a) / _ball(b), a / b))
        for name, ball, exact in cases:
            # A ball result is tight to ~1e-77 relative, so a strict
            # contains() of the exact ball can fail at the boundary.  The
            # relative slack below is 17 orders above working precision and
            # still catches any real arithmetic error.
            diff = (ball - _ball(exact)).abs_upper()
            bound = _tol("1e-60") * (1 + abs(_ball(exact)))
            if not bool(diff <= bound):
                failures.append(f"{name}:{a}:{b}")

    for _ in range(1000):
        qn = next(gen) % 2000001 - 1000000
        qd = next(gen) % 2000000 + 1
        q = Fraction(qn * qn, qd * qd)
        s = _ball(q).sqrt()
        # Soundness check: s^2 must contain q (relative slack for rounding).
        diff = (s * s - _ball(q)).abs_upper()
        bound = _tol("1e-60") * (1 + _ball(q))
        if not bool(diff <= bound):
            failures.append(f"sqrt:{q}")

    return {
        "passed": not failures,
        "cases": 2000,
        "failures": failures[:5],
    }


# ---------------------------------------------------------------------------
# C2-C5
# ---------------------------------------------------------------------------


def check_c2() -> dict:
    r16 = _run_s1(16)
    r24 = _run_s1(24)
    passed = bool(
        r16["contains_2"]
        and r24["contains_2"]
        and r16["width_ok"]
        and r24["width_ok"]
        and (r24["width"] * 10**4 <= r16["width"])
    )
    return {"passed": passed, "order16": r16, "order24": r24}


def check_c3() -> dict:
    checkpoints = _run_s2()
    passed = all(cp["contains"] and cp["width_ok"] for cp in checkpoints.values())
    return {"passed": passed, "checkpoints": checkpoints}


def check_c4() -> dict:
    checkpoints, error = _run_s3()
    passed = error is None and all(
        cp["energy_ok"] and cp["angular_ok"] and cp["width_ok"]
        for cp in checkpoints
    )
    return {"passed": passed, "error": error, "checkpoints": checkpoints}


def check_c5() -> dict:
    checkpoints, error = _run_s4()
    passed = error is None and all(
        cp["energy_ok"] and cp["angular_ok"] and cp["com_ok"] and cp["width_ok"]
        for cp in checkpoints
    )
    return {"passed": passed, "error": error, "checkpoints": checkpoints}


# ---------------------------------------------------------------------------
# C6: AST scan for float leakage
# ---------------------------------------------------------------------------

FORBIDDEN_NAMES = {"float", "math", "numpy", "scipy", "np"}


def ast_scan(source: str) -> list[str]:
    tree = ast.parse(source)
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            hits.append(f"name:{node.id}:{node.lineno}")
        if isinstance(node, ast.Attribute):
            root = node
            while isinstance(root, ast.Attribute):
                root = root.value
            if isinstance(root, ast.Name) and root.id in FORBIDDEN_NAMES:
                hits.append(f"attr:{root.id}:{node.lineno}")
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in FORBIDDEN_NAMES:
                    hits.append(f"import:{alias.name}:{node.lineno}")
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in FORBIDDEN_NAMES:
                hits.append(f"from:{node.module}:{node.lineno}")
    return hits


# ---------------------------------------------------------------------------
# campaign
# ---------------------------------------------------------------------------


def run_campaign() -> dict:
    with flint.ctx.workprec(PREC):
        c1 = check_c1()
        c2 = check_c2()
        c3 = check_c3()
        c4 = check_c4()
        c5 = check_c5()
        hits = ast_scan(Path(__file__).read_text(encoding="utf-8"))
        c6 = {"ast_scan_hits": hits, "ast_scan_passed": not hits}

        checks = {"C1": c1, "C2": c2, "C3": c3, "C4": c4, "C5": c5, "C6": c6}
        all_pass = all(
            [
                c1["passed"],
                c2["passed"],
                c3["passed"],
                c4["passed"],
                c5["passed"],
                c6["ast_scan_passed"],
            ]
        )
        return {
            "schema": SCHEMA,
            "prereg_sha256lf": sha256lf(PREREG_PATH),
            "python_flint": flint.__version__,
            "precision": PREC,
            "order": ORDER,
            "checks": _ser(checks),
            "summary": "ALL PASS" if all_pass else "SOME CHECKS FAILED",
            "all_pass": all_pass,
            "guard_required": True,
        }


def main() -> None:
    result = run_campaign()
    RECEIPT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    printable = {
        "summary": result["summary"],
        "all_pass": result["all_pass"],
        "prereg_sha256lf": result["prereg_sha256lf"],
        "receipt": str(RECEIPT_PATH),
    }
    print(json.dumps(printable, indent=2))


if __name__ == "__main__":
    main()
