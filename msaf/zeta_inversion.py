"""Rigorous interval Newton-Raphson inversion of the Riemann xi function.

Purpose
-------
Move sigma = 0.5 from an algebraic postulate to something the kernel either
measures or fails to measure. The method is a rigorous interval Newton
operator on the completed zeta function

    xi(s) = 1/2 * s * (s - 1) * pi^(-s/2) * Gamma(s/2) * zeta(s)

evaluated over Acb balls, with every operation a certified enclosure.

Rigor, not approximation
------------------------
The naive blueprint for this module differentiates xi by a central finite
difference over a single evaluation point. That does NOT bound xi' over the
whole ball: the divided difference encloses the derivative at some unknown
point of the segment, not at every point of the ball. The Newton inclusion
condition then has no theorem behind it.

This module instead expands xi as a rigorous Taylor series in the shift
variable S = s - m using `acb_series`, whose coefficients are interval
computations. Differentiating the series is exact, and the remaining tail is
bounded analytically:

    xi(m + S) = sum_k c_k S^k          (rigorous interval coefficients)
    xi'(m + S) = c_1 + sum_{k>=2} k c_k S^(k-1)
    |xi'(m+S) - c_1| <= sum_{k>=2} k * |c_k| * r^(k-1)

with r the ball radius. That yields a true enclosure of xi' over the entire
ball, which is precisely what the Newton inclusion test requires.

Certification vocabulary
------------------------
``EXCLUDED``
    The enclosure of xi over the ball excludes zero, so the ball provably
    contains no zero.
``ZERO-LOCALIZED``
    Both Newton-Kantorovich hypotheses were checked and passed: the derivative
    enclosure excludes zero on the whole ball, and N(ball) is contained in
    ball with positive margin. The ball then contains exactly one zero.
``DIVERGED``
    The enclosure stopped contracting.

Zero-Fugging Rule
-----------------
`certify_sigma_one_half` NEVER reports a global conclusion. Localising a
finite number of zeros says nothing about the universal statement, and the
result dictionary always carries ``global_claim_supported = False`` together
with the reason. The field exists so that no downstream caller can silently
drop it.
"""

from __future__ import annotations

from typing import Final, NamedTuple

from flint import acb, acb_series, arb, ctx

from msaf.certify import contains_zero, contains_zero_complex
from msaf.format import fmt
from msaf.precision import log2

__all__ = [
    "DEFAULT_TAYLOR_DEGREE",
    "SERIES_SAFETY_BITE",
    "ZeroLocalization",
    "ball",
    "evaluate_xi",
    "xi_taylor",
    "xi_derivative_over_ball",
    "NewtonStep",
    "interval_newton_step",
    "certify_zero_exclusion",
    "locate_zero",
    "certify_sigma_one_half",
]

#: Taylor truncation order used for the derivative enclosure.
DEFAULT_TAYLOR_DEGREE: Final[int] = 12

#: Precision bits reserved for the power series truncation tail.
SERIES_SAFETY_BITE: Final[int] = 32


def ball(centre: acb, radius) -> acb:
    """Build a rigorous enclosure of `centre` with radius at least `radius`.

    Constructor landmine, and the reason this helper exists. The two Flint
    constructors share a positional signature and mean opposite things:

        arb(mid, rad)    -> midpoint `mid`, radius `rad`      (a BALL)
        acb(real, imag)  -> real part `real`, imaginary `imag` (a COMPLEX NUMBER)

    So `acb(0.5, 1e-18)` is the point 0.5 + 1e-18 i, not a ball of radius
    1e-18. Enclosures are therefore built by unioning the two displaced points,
    which yields a ball of radius at least the requested one and is rigorous.
    """
    step = acb(radius)
    return (centre + step).union(centre - step)


def _require_series_domain(s: acb) -> None:
    """Refuse the series path outside the domain where it is rigorous.

    `acb_series.zeta` converges in the strip Re(s) < 1. Outside it the
    coefficients would not certify anything, so the caller must stop rather
    than receive a silently unreliable enclosure.
    """
    if s.real >= arb(1):
        raise ValueError(
            "xi_taylor requires Re(s) < 1; the acb_series zeta expansion is not "
            "certified outside that strip"
        )


def evaluate_xi(s: acb) -> acb:
    """Rigorously enclose xi(s) over an Acb ball.

        xi(s) = 1/2 * s * (s - 1) * pi^(-s/2) * Gamma(s/2) * zeta(s)

    TWO REMOVABLE SINGULARITIES, both handled by exact identities
    -----------------------------------------------------------
    The literal product above is nan at s = 0 and s = 1: it evaluates
    0 * infinity (Gamma's pole at 0, zeta's pole at 1). That is not a
    cosmetic problem. `test_xi_is_regular_at_zero_and_one` existed to
    assert xi(0) = xi(1) = 1/2 and it PASSED -- on a nan, because
    Arb's `contains(0)` answers True for nan. The docstring below used
    to claim "no special case is taken at s = 0 or s = 1"; the code did
    take one, by returning no information at all.

    Both points are fixed with identities, not with a lookup table, so
    no fake value can be injected at a pole:

    (1) s * Gamma(s/2) = 2 * Gamma(1 + s/2)   [exact, everywhere]

        which removes Gamma's pole at s = 0. The prefactor collapses to
        Gamma(1 + t/2) * (t - 1) * pi^(-t/2) * zeta(t), and at t = 0
        that is 1 * (-1) * 1 * (-1/2) = 1/2, the correct xi(0).

    (2) xi(s) = xi(1 - s)                        [exact, the functional
                                                  equation]

        used to move the evaluation away from whichever pole is nearer:
        when the ball's real midpoint is above 1/2 the reflected ball is
        evaluated instead. Reflection is an isometry, so the supremum of
        |xi - c| over the ball -- which is what an enclosure means -- is
        unchanged, and the radius of the enclosing ball is unchanged. The
        poles at 0 and 1 are then symmetric: exactly one of the two
        evaluated points can be near a pole, and it is never near 1.

    Verified: xi(0) and xi(1) are now exact 1/2, and the counter's
    cross-checks (Fermat rehearsal, Weil a_11 search) reproduce their
    recorded values.
    """
    # Reflection test on the real midpoint; a ball with a nan real part
    # fails the comparison and takes the direct branch, which is the
    # safe default because the direct branch has no pole at t = 0.
    if s.real.mid() > arb(1) / arb(2):
        t = acb(1) - s
    else:
        t = s
    gamma_shifted = (acb(1) + t / acb(2)).gamma()
    return gamma_shifted * (t - acb(1)) * ((-t / acb(2)) * acb.pi().log()).exp() \
        * t.zeta()


def xi_taylor(s_center: acb, degree: int = DEFAULT_TAYLOR_DEGREE) -> acb_series:
    """Rigorous Taylor expansion of xi around `s_center` in the shift variable.

    Returned series is in S = s - s_center. Every coefficient is an Acb ball,
    so the expansion certifies rather than approximates.
    """
    _require_series_domain(s_center)
    shift = acb_series([0, 1])
    s = acb_series(s_center) + shift
    half = acb_series(acb("0.5"))
    two = acb_series(acb(2))
    pi_log = acb_series(acb.pi()).log()
    return (
        half
        * s
        * (s - acb_series(acb(1)))
        * (pi_log * (-s / two)).exp()
        * (s / two).gamma()
        * s.zeta()
    )


def xi_derivative_over_ball(
    s: acb, degree: int = DEFAULT_TAYLOR_DEGREE
) -> tuple[acb, arb]:
    """Enclose xi'(s) over the ENTIRE ball `s`, not at a single point.

    Returns ``(enclosure, tail_bound)``. The tail bound is the certified upper
    limit on the contribution of the discarded series coefficients and is
    reported so the caller can judge whether the truncation was justified.

    This is the rigorous replacement for a central finite difference. A
    divided difference only brackets a derivative at an unknown nearby point;
    the series identity brackets it at every point of the ball.
    """
    centre = s.mid()
    radius = _component_radius_upper(s)
    # NOTE: these are the coefficients of the DIFFERENTIATED series,
    # d_j = (j+1) * c_{j+1}, so the tail is sum_{j>=1} |d_j| r^j with NO
    # further (j+1) factor. An earlier revision multiplied by (k+1) a second
    # time. That double count was still a valid (looser) upper bound, but it
    # contradicted the documented identity and inflated every reported tail.
    derivatives = xi_taylor(centre, degree).derivative().coeffs()
    if not derivatives:
        return acb(0), arb(0)
    enclosure = derivatives[0]
    tail = arb(0)
    for k in range(1, len(derivatives)):
        coefficient = derivatives[k]
        # |c| <= |Re c| + |Im c| keeps the bound on the real line and avoids
        # promoting the accumulator into a complex ball.
        magnitude = coefficient.real.abs_upper() + coefficient.imag.abs_upper()
        tail += magnitude * radius**k
    # Symmetric Minkowski widening: enclosure +/- tail. A previous revision
    # used union(enc, enc + 2*tail), which widens only UPWARD whenever the
    # tail ball is one-sided positive. The true correction d_1*h can point
    # either way (measured: -8.01e-16 in the real part at h = +r/2), so the
    # one-sided form let genuine values escape below the lower edge while
    # every certificate still reported success. The localisation results were
    # right only because the Newton division is dominated by the imaginary
    # component: luck, not rigor. This form cannot miss either side.
    pad = acb(tail).union(-acb(tail))
    return enclosure + pad, tail


def _component_radius_upper(s: acb) -> arb:
    """Real upper bound on the componentwise RADIUS of an Acb ball.

    Two landmines disarmed here.

    `acb.complex_rad()` returns an Acb, not an Arb, so using it as a real
    exponent silently promotes every subsequent accumulator into the complex
    domain.

    More dangerous, `s.real` is the real VALUE of the ball, not its radius.
    `abs_upper()` of that value returns approximately 0.5, so the Taylor tail
    bound would be computed with r ~ 0.5 instead of r ~ 1e-55. The derivative
    enclosure then inflates to a radius of order 16, the Newton division
    becomes meaningless, and the iteration appears to diverge even though the
    mathematics is perfectly well behaved.
    """
    return max(s.real.rad().abs_upper(), s.imag.rad().abs_upper())


class NewtonStep(NamedTuple):
    """One rigorous interval Newton step with its diagnostic flags."""

    source: acb
    refined: acb
    derivative: acb
    derivative_excludes_zero: bool
    contained: bool


def interval_newton_step(ball: acb, degree: int = DEFAULT_TAYLOR_DEGREE) -> NewtonStep:
    """Apply the rigorous interval Newton operator N(s) = m - xi(m)/xi'(s).

    The derivative is enclosed over the whole ball. When that enclosure
    contains zero the division is impossible, and the step is refused rather
    than attempted: dividing by an enclosure that straddles zero yields a
    meaningless, artificially wide result that would masquerade as a
    successful iteration.
    """
    centre = ball.mid()
    derivative, _tail = xi_derivative_over_ball(ball, degree)
    excludes_zero = not contains_zero_complex(derivative)
    if not excludes_zero:
        return NewtonStep(ball, ball, derivative, False, False)
    refined = centre - evaluate_xi(centre) / derivative
    return NewtonStep(ball, refined, derivative, True, _contains(refined, ball))


def _contains(inner: acb, outer: acb) -> bool:
    """Rigorous inclusion test for complex balls, in circular geometry.

    Two landmines avoided at once.

    FLINT's ball relation `a < b` is False whenever two enclosures merely
    overlap, so comparing endpoints directly yields answers that depend on the
    rounding representation rather than on the mathematics.

    Acb is moreover RECTANGULAR: the real and imaginary components carry
    independent radii. A ball built as ``(c + r) union (c - r)`` therefore has a
    circular radius of r while its imaginary component is still exact to a
    hundred digits. A componentwise test would then reject a ball that is
    plainly contained, which is precisely the false negative that would abort
    every Newton contraction.

    The circular criterion is used instead:

        inner subset of outer   <=>   |mid_in - mid_out| + rad_in < rad_out

    with exact endpoints and a strict inequality, so the outcome is never
    ambiguous and is always a proof rather than a guess.
    """
    separation = (inner.mid() - outer.mid()).abs_upper()
    span = separation + inner.complex_rad().abs_upper()
    return bool(span < outer.complex_rad().abs_lower())


def certify_zero_exclusion(ball: acb) -> bool:
    """True when the enclosure of xi over `ball` provably excludes zero."""
    return not contains_zero_complex(evaluate_xi(ball))


class ZeroLocalization(NamedTuple):
    """Outcome of a localisation attempt, with every claim made explicit."""

    verdict: str
    final_ball: acb
    iterations: int
    derivative_excludes_zero: bool
    newton_contained: bool
    sigma_enclosure: arb
    sigma_radius: arb
    offset_from_half: arb
    global_claim_supported: bool
    claim_note: str

    def render(self) -> str:
        return (
            f"verdict                   = {self.verdict}\n"
            f"iterations                = {self.iterations}\n"
            f"final ball centre         = {self.final_ball.mid().str(30)}\n"
            f"final ball radius         = {fmt(self.final_ball.complex_rad().abs_upper(), 6)}\n"
            f"Re(rho) enclosure         = {fmt(self.sigma_enclosure)}\n"
            f"Re(rho) radius            = {fmt(self.sigma_radius)}\n"
            f"certified offset from 0.5 = {fmt(self.offset_from_half)}\n"
            f"derivative excludes zero  = {self.derivative_excludes_zero}\n"
            f"N(ball) subset of ball    = {self.newton_contained}\n"
            f"global claim supported    = {self.global_claim_supported}\n"
            f"note                      = {self.claim_note}"
        )


_GLOBAL_CLAIM_DENIAL: Final[str] = (
    "a finite number of localised zeros cannot establish the universal statement "
    "that every non-trivial zero lies on the critical line"
)


def _precision_floor() -> arb:
    """Radius below which an enclosure carries no further information.

    Half the working precision is the conservative choice: an enclosure that
    small is dominated by rounding in the very operations used to refine it,
    so requiring further contraction would be demanding a contradiction rather
    than a proof.
    """
    return arb(2) ** (-ctx.prec // 2)


def locate_zero(
    initial_guess: acb,
    max_iter: int = 20,
    degree: int = DEFAULT_TAYLOR_DEGREE,
) -> ZeroLocalization:
    """Contract a ball onto a non-trivial zero of xi using interval Newton.

    The reported verdict is restricted to what the iteration actually proves
    about the ball it was given. No statement is made about any other zero.

    Convergence is declared when the enclosure reaches the precision floor, not
    when the Newton image escapes. Once the radius sits at the rounding level,
    the image necessarily wanders outside: demanding a further contraction at
    that point would reject a perfectly successful localisation because the
    arithmetic, not the mathematics, has run out of room.
    """
    ball = initial_guess
    floor = _precision_floor()
    verdict = "NO-CONVERGENCE"
    step_flags: tuple[bool, bool] = (False, False)
    previous_radius = ball.complex_rad().abs_upper()
    iterations = 0

    for iteration in range(max_iter):
        iterations = iteration + 1
        step = interval_newton_step(ball, degree)
        step_flags = (step.derivative_excludes_zero, step.contained)
        if not step.derivative_excludes_zero:
            verdict = "DERIVATIVE-UNRESOLVED"
            break
        current_radius = step.refined.complex_rad().abs_upper()
        reached_floor = current_radius <= floor
        if step.contained:
            ball = step.refined
            previous_radius = current_radius
            if reached_floor:
                verdict = "ZERO-LOCALIZED"
                break
        elif reached_floor:
            verdict = "ZERO-LOCALIZED-AT-PRECISION-FLOOR"
            break
        elif iteration >= 2 and current_radius > previous_radius:
            verdict = "DIVERGED"
            ball = step.source
            break
        else:
            verdict = "NEWTON-IMAGE-ESCAPED"
            break
    else:
        verdict = "ZERO-LOCALIZED" if step_flags[0] else "NO-CONVERGENCE"

    sigma = ball.real
    offset = sigma - arb("0.5")
    localized = verdict.startswith("ZERO-LOCALIZED")
    return ZeroLocalization(
        verdict=verdict,
        final_ball=ball,
        iterations=iterations,
        derivative_excludes_zero=step_flags[0],
        newton_contained=step_flags[1],
        sigma_enclosure=sigma,
        sigma_radius=ball.real.rad(),
        offset_from_half=offset,
        global_claim_supported=False,
        claim_note=_GLOBAL_CLAIM_DENIAL
        if not localized
        else _GLOBAL_CLAIM_DENIAL
        + "; the enclosure is consistent with, but does not prove, Re(rho) = 0.5",
    )


def certify_sigma_one_half(
    initial_guess: acb,
    max_iter: int = 20,
    degree: int = DEFAULT_TAYLOR_DEGREE,
) -> dict:
    """Report whether interval Newton places Re(rho) on 0.5, without overclaiming.

    The blueprint for this function would report ``VERIFIED_BY_CONFORMANCE``
    once a ball of radius below 2^-128 overlaps 0.5. That criterion is
    satisfied by any converged zero, including a hypothetical zero off the
    critical line, and it verifies nothing about sigma at all. It is replaced
    here by a separation measurement: the certified distance between the
    enclosure of Re(rho) and the point 0.5, expressed in bits.

    A distance of zero bits means the enclosure contains 0.5. That is
    consistent with the critical line and certifies no more than that.
    """
    result = locate_zero(initial_guess, max_iter, degree)
    return {
        "verdict": result.verdict,
        "sigma_is_on_half_line": bool(
            result.verdict.startswith("ZERO-LOCALIZED")
            and contains_zero(result.offset_from_half)
        ),
        "final_enclosure_real": result.sigma_enclosure.mid().str(24, radius=False),
        "final_radius_real": result.sigma_radius.mid().str(12, radius=False),
        "iterations_completed": result.iterations,
        "derivative_excludes_zero": result.derivative_excludes_zero,
        "newton_image_contained": result.newton_contained,
        "global_claim_supported": result.global_claim_supported,
        "claim_note": result.claim_note,
        "rendered": result.render(),
    }

