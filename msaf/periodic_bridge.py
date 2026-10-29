"""Periodic-box axis values of the discrete Green function, exact mode sum.

This is the [B] (bounded) side of a bounded-to-free-space bridge study. The
model is the sealed one (``msaf/navier_stokes/fluid_lattice.py``): the 7-point
periodic Laplacian on T^3_N with spacing ``dx = L/N``. For the zero-mean point
source ``delta_0 - 1/N^3`` the exact solution is

    phi_N(x) = -(1/N^3) * sum_{f != 0} e^{2 pi i f.x/N} / lam_f
    lam_f    = (2/dx^2) * (3 - cos(2 pi f_x/N) - cos(2 pi f_y/N) - cos(2 pi f_z/N))

(the zero mode is pinned, the gauge of the sealed solver). Along the axis
``x = (r,0,0)`` the imaginary part cancels, and the value is the real mode sum
evaluated here term by term in Arb.

Why a direct sum: the sealed separable-DFT solver costs O(N^4) per axis and
stops near N=16-32. This mode sum costs O(N^3) per radius and reaches N=64+,
so the bounded side can be probed at several sizes with identical rigour.
Every term is an Arb ball built from ``cos_pi`` of an exact rational; the sum
is therefore a rigorous enclosure of the exact discrete solution. No float,
no FFT, no interpolation.

Bridge status (do not overread): this module certifies the BOUNDED side only.
The free-space (infinite-lattice) value is NOT evaluated here. The image-sum
identity that would connect the two sides is stated in
``reports/PERIODIC_BRIDGE_STUDY_2026-10-19.md``; its tail bound is OPEN. No
convergence rate and no limit value are claimed.
"""

from __future__ import annotations

from typing import NamedTuple, Sequence

from flint import arb, fmpq

__all__ = ["axis_value", "axis_values", "Probe", "probe"]


def _require_int(name: str, value: object) -> int:
    if isinstance(value, float):
        raise TypeError("%s: float64 leakage refused (got %r); pass int" % (name, value))
    if not isinstance(value, int):
        raise TypeError("%s: expected int, got %s" % (name, type(value).__name__))
    return value


def _require_length(value: str | int | arb) -> arb:
    if isinstance(value, float):
        raise TypeError("length: float64 leakage refused (got %r); pass decimal str" % (value,))
    if isinstance(value, arb):
        ball = value
    elif isinstance(value, int):
        ball = arb(value)
    elif isinstance(value, str):
        ball = arb(value)
    else:
        raise TypeError("length: expected str|int|arb, got %s" % type(value).__name__)
    if not ball.is_finite():
        raise ValueError("length: non-finite input rejected")
    if not bool(arb(0) < ball):
        raise ValueError("length: need provably length > 0")
    return ball


def _cos_table(n: int) -> list[arb]:
    return [arb(fmpq(2 * j, n)).cos_pi() for j in range(n)]


def axis_value(n: int, r: int, length: str | int | arb = "1") -> arb:
    """Exact periodic-box solution at axis cell ``(r,0,0)``, as an Arb ball.

    ``n`` is the box side, ``r`` the axis offset (``0 <= r < n``), ``length``
    the box side length. Caller sets ``ctx.prec`` (256 is the sealed working
    precision); the value is a rigorous enclosure of the exact discrete
    solution, with radius at the working precision.
    """
    n = _require_int("n", n)
    r = _require_int("r", r)
    if n < 2:
        raise ValueError("axis_value: need n >= 2 (zero mode is the only mode)")
    if not 0 <= r < n:
        raise ValueError("axis_value: need 0 <= r < n, got r=%d, n=%d" % (r, n))
    length_ball = _require_length(length)
    dx = length_ball / arb(n)
    scale = arb(2) / (dx * dx)
    cv = _cos_table(n)
    num = [arb(fmpq(2 * j * r, n)).cos_pi() for j in range(n)]
    total = arb(0)
    for fx in range(n):
        nx = num[fx]
        cx = cv[fx]
        for fy in range(n):
            cy = cv[fy]
            for fz in range(n):
                if fx == 0 and fy == 0 and fz == 0:
                    continue
                den = scale * (arb(3) - cx - cy - cv[fz])
                total += nx / den
    return -total / arb(n) ** 3


def axis_values(n: int, rs: Sequence[int], length: str | int | arb = "1") -> dict[int, arb]:
    """Axis values at several offsets, one mode sum per radius."""
    return {int(r): axis_value(n, int(r), length) for r in rs}


class Probe(NamedTuple):
    """Difference-quotient probe on the axis: (v1 - v2) / (v2 - v4)."""

    n: int
    v1: arb
    v2: arb
    v4: arb
    denominator: arb
    q: arb


def probe(n: int, length: str | int | arb = "1") -> Probe:
    """Certified probe statistic at box side ``n`` (shells 1, 2, 4).

    The quotient is rigorous only when the denominator provably excludes
    zero; otherwise a ValueError is raised (fail-closed, never a signed
    float guess).
    """
    v1 = axis_value(n, 1, length)
    v2 = axis_value(n, 2, length)
    v4 = axis_value(n, 4, length)
    denominator = v2 - v4
    if bool(denominator.contains(arb(0))):
        raise ValueError(
            "probe: denominator v2 - v4 contains zero; quotient not certifiable "
            "at this box size"
        )
    return Probe(n, v1, v2, v4, denominator, (v1 - v2) / denominator)


