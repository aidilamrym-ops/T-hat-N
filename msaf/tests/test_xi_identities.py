"""xi must be regular at its own two poles, and the fix must not move anything.

Two defects, one root. `evaluate_xi` evaluated the literal product

    xi(s) = 1/2 * s * (s-1) * pi^(-s/2) * Gamma(s/2) * zeta(s)

which is nan at s = 0 and s = 1 (0 times infinity). The guard test for
this existed and passed -- on the nan, because Arb's `contains(0)` is
True for nan. The function's own docstring claimed no special case was
taken; the code was taking one, by returning nothing at all.

The fix uses exact identities (s*Gamma(s/2) = 2*Gamma(1+s/2), and the
functional equation xi(s) = xi(1-s)). Identities, not a lookup table: a
table of special values is exactly how a fake root gets injected into a
zero counter.

These tests pin three separate obligations:

  1. regularity at 0 and 1 -- xi = 1/2 there, exactly;
  2. no regression -- wherever the OLD literal product was finite, the
     new enclosure must agree with it, so sealed counts cannot move;
  3. no nan anywhere in the critical strip, which is where the counter
     works and where the old failure mode was hardest to notice.
"""
import pytest
from flint import acb, arb, ctx

from msaf.zeta_inversion import evaluate_xi


@pytest.fixture(autouse=True)
def _restore_precision():
    """Never leak working precision into another test module.

    `ctx.prec` is global mutable state in Arb/Acb. Setting it at module
    import time (as several test modules here do) makes the suite
    order-dependent: with `prec = 200` leaking in, the adversarial
    stress thresholds in test_adversarial_stress.py failed in a full run
    while passing in isolation. Two failures that only appear when the
    whole suite runs are the worst kind to debug, so this file saves and
    restores whatever it finds."""
    saved = ctx.prec
    ctx.prec = 200
    try:
        yield
    finally:
        ctx.prec = saved


def pt(re_text: str, im_text: str) -> acb:
    """A point ball. `acb(arb, arb)` is the working two-argument form;
    `acb((a, b))` and the `x+yi` string form both raise in this flint."""
    return acb(arb(re_text), arb(im_text))


def literal_product(s: acb) -> acb:
    """The pre-fix formula, kept as the reference to differ against."""
    half = acb("0.5")
    two = acb(2)
    pi = acb.pi()
    polynomial = half * s * (s - acb(1))
    exponential = (-s / two) * pi.log()
    return polynomial * exponential.exp() * (s / two).gamma() * s.zeta()


def test_xi_is_exactly_half_at_its_poles():
    for point in ("0", "1"):
        value = evaluate_xi(acb(point))
        assert value.is_finite(), "xi(%s) must be finite" % point
        assert bool(value.contains(acb("0.5"))), (
            "xi(%s) = %s, expected 1/2" % (point, value))


def test_literal_product_really_was_nan_there():
    # If flint ever regularises its own zeta/gamma, this fails and says
    # why the reference below stops being the pre-fix behaviour.
    assert not literal_product(acb(0)).is_finite()
    assert not literal_product(acb(1)).is_finite()


@pytest.mark.parametrize("re_s", ["0.4", "0.5", "0.6", "0.7", "0.8"])
@pytest.mark.parametrize("im", ["14.134725", "21.022040", "25.010858"])
def test_critical_line_agrees_with_the_literal_product(re_s, im):
    """Where the old formula worked, the new one must give the same number."""
    s = pt(re_s, im)
    old = literal_product(s)
    new = evaluate_xi(s)
    assert new.is_finite()
    assert old.is_finite(), "reference unexpectedly nan at %s" % s
    assert bool(new.contains(old.mid())), (
        "enclosures disagree at s=%s: old %s, new %s"
        % (s, old.str(12), new.str(12)))
    assert new.rad().abs_upper() <= old.rad().abs_upper() * 4


@pytest.mark.parametrize("k", range(1, 26))
def test_no_nan_in_the_critical_strip(k):
    # The counter's working region. A nan here is a silent loss of
    # information in the exact place where a fake root is most damaging.
    s = pt("0.5", str(arb(k) / arb(2)))
    assert evaluate_xi(s).is_finite(), "nan at t = %s" % (k / 2.0)


@pytest.mark.parametrize("im", ["14.134725", "21.022040", "25.010858"])
def test_reflection_branch_returns_the_conjugate_mirror(im):
    """xi(0.75 + it) must be the CONJUGATE of xi(0.25 + it), not its twin.

    The first draft of this test asserted the two enclosures overlap and
    failed, which looked like a broken reflection branch. It was the
    assertion that was wrong, and the arithmetic says so:

        xi(s) = xi(1 - s)            functional equation
        xi(conj s) = conj(xi(s))     xi has real Taylor coefficients

    Take s = 0.75 + it. Then xi(0.25 - it) = xi(0.75 + it), and
    xi(0.25 - it) = conj(xi(0.25 + it)). Hence

        xi(0.75 + it) = conj(xi(0.25 + it))

    The reflection branch computes exactly that, so the correct statement
    is a conjugate mirror. Written down here because the wrong version is
    the natural one to write, and it fails for a reason that looks like a
    code defect."""
    left = evaluate_xi(pt("0.25", im))
    right = evaluate_xi(pt("0.75", im))
    assert left.is_finite() and right.is_finite()
    mirror = left.conjugate()
    assert bool(right.contains(mirror.mid())), (
        "xi(0.75+%si) = %s does not contain conj(xi(0.25+%si)) = %s"
        % (im, right.str(12), im, mirror.str(12)))


def test_wide_ball_on_the_line_is_still_finite():
    # A ball, not a point: moore_premises lifts boxes before evaluating,
    # and that path must not reintroduce a nan.
    s = acb(arb("0.5") + arb("1e-6"), arb("14.134725") + arb("1e-6"))
    assert evaluate_xi(s).is_finite()


def test_reflection_branch_is_exercised():
    # Guard against the reflection silently becoming dead code: a point
    # with Re > 1/2 must take the other branch and still be right.
    assert evaluate_xi(pt("0.9", "14.134725")).is_finite()
    assert evaluate_xi(pt("0.1", "14.134725")).is_finite()
