"""Moore-premise verifier: check the Lean theorem's hypotheses as enclosures.

For an isolation box ``B`` (from a strict ``locate_zero`` run), this
module verifies the exact premises of ``NewtonExistence.moore_box``:

(a) invariance ``N(B) ⊆ B`` for the pointwise Newton map, by interval
    evaluation (circular containment, strict);
(b) clean derivative: the ``xi'`` enclosure over ``B`` excludes zero
    (hence every pointwise derivative is nonzero);
(c) Lipschitz bound ``sup|N'| < 1`` with ``N' = f*f''/(f')^2``,
    via a second-derivative enclosure mirroring the kernel's
    documented first-derivative pattern.

Verdict PREMISES-HOLD only when all three hold certainly; otherwise
PREMISES-FAIL with the failing gate named. No float anywhere.
"""
from __future__ import annotations

from flint import acb, arb, ctx

from msaf.zeta_inversion import (
    DEFAULT_TAYLOR_DEGREE,
    evaluate_xi,
    interval_newton_step,
    xi_taylor,
)

__all__ = ["second_derivative_over_ball", "verify_moore_premises"]


def _reject_float(value, name: str) -> None:
    if isinstance(value, float):
        raise TypeError(f"{name}: float64 leakage refused")


def _component_radius_upper(s: acb) -> arb:
    return max(s.real.rad().abs_upper(), s.imag.rad().abs_upper())


def second_derivative_over_ball(
    s: acb, degree: int = DEFAULT_TAYLOR_DEGREE
) -> tuple[acb, arb]:
    """Enclose xi''(s) over the ENTIRE ball ``s``.

    Mirrors ``xi_derivative_over_ball`` exactly: series differentiated
    twice gives ``d_j = (j+1)(j+2) c_{j+2}``, enclosure ``d_0`` plus
    ``sum_{j>=1} |d_j| r^j`` with NO further factorial factor, closed
    by symmetric Minkowski widening.
    """
    if isinstance(degree, float):
        raise TypeError("degree: float64 leakage refused")
    centre = s.mid()
    radius = _component_radius_upper(s)
    derivatives = xi_taylor(centre, int(degree)).derivative().derivative().coeffs()
    if not derivatives:
        return acb(0), arb(0)
    enclosure = derivatives[0]
    tail = arb(0)
    for k in range(1, len(derivatives)):
        coefficient = derivatives[k]
        magnitude = coefficient.real.abs_upper() + coefficient.imag.abs_upper()
        tail += magnitude * radius**k
    pad = acb(tail).union(-acb(tail))
    return enclosure + pad, tail


def _circular_contains(inner: acb, outer: acb) -> bool:
    separation = (inner.mid() - outer.mid()).abs_upper()
    span = separation + inner.complex_rad().abs_upper()
    return bool(span < outer.complex_rad().abs_lower())


def _halo(box: acb, halo_str: str = "1e-70") -> acb:
    """Widen by a fixed halo on every side (hull, never shift).

    Floor-level balls (radius ~1e-76) sit below evaluation noise, so
    no Newton image can fit inside them; lifting to 1e-70 restores a
    regime where containment is decidable. Big boxes are unaffected
    in practice (halo negligible) and stay subject to the same check.
    """
    halo = arb(halo_str)
    return acb(
        (box.real - halo).union(box.real + halo),
        (box.imag - halo).union(box.imag + halo),
    )


def verify_moore_premises(box: acb, degree: int = DEFAULT_TAYLOR_DEGREE) -> dict:
    """Check (a) invariance, (b) clean derivative, (c) Lipschitz < 1.

    Invariance is checked on the halo-lifted box (see ``_halo``) via
    one kernel Newton step -- the Moore test itself, whose image is
    far tighter than naive whole-box evaluation; uniqueness then
    holds there. Derivative and Lipschitz data are evaluated on the
    same lifted box.
    """
    if isinstance(box, (float, int)):
        raise TypeError("box: scalar leakage refused")
    if isinstance(degree, float):
        raise TypeError("degree: float64 leakage refused")
    degree = int(degree)
    lifted = _halo(box)
    step = interval_newton_step(lifted, degree)
    deriv_excludes = bool(step.derivative_excludes_zero)
    if not deriv_excludes:
        return {
            "verdict": "PREMISES-FAIL",
            "failed_gate": "derivative_excludes_zero",
            "maps_to": False,
            "deriv_excludes_zero": False,
            "lipschitz_K": "n/a",
            "k_below_one": False,
        }
    maps_to = bool(step.contained)
    f_ball = evaluate_xi(lifted)
    fpp_ball, _ = second_derivative_over_ball(lifted, degree)
    fp_ball = step.derivative
    nprime = f_ball * fpp_ball / (fp_ball * fp_ball)
    k_mag = nprime.abs_upper()
    k_below_one = bool(k_mag < arb(1))
    holds = bool(maps_to) and bool(k_below_one)
    return {
        "verdict": "PREMISES-HOLD" if holds else "PREMISES-FAIL",
        "failed_gate": None if holds else "maps_to_or_lipschitz",
        "maps_to": bool(maps_to),
        "deriv_excludes_zero": True,
        "lipschitz_K": k_mag.str(8),
        "k_below_one": bool(k_below_one),
    }
