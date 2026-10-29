"""Guard for the two-space bridge kit (msaf/bridge.py).

The kit's correctness rules are pinned here:

  * the lemmas are instantiated sound: bounds bracket the true value where
    an independent closed form is available (zeta(2), e^-1, Gaussian tail
    against an mpmath spot value), and direction is never flipped;
  * a non-finite input never enters a bridge (the msaf/certify.py landmine
    rule applies to the two-space kit as well);
  * search results are accepted only after a rigorous comparison; an
    unreachable budget raises, never passes;
  * assemble() re-checks every promotion: width <= eps is PROVEN, or the
    certificate says NOT CERTIFIED;
  * the end-to-end zeta(2) pipeline contains pi^2/6.

All decisions use Arb comparisons, which are True only when the relation is
provable for every member of both balls. Floats appear only in heuristic
search coordinates, never in a verdict.
"""

from __future__ import annotations

import pytest
from flint import arb, ctx

from msaf.bridge import (
    MANDATE,
    assemble,
    choose_cutoff,
    choose_cutoff_real,
    exp_envelope_tail,
    gaussian_tail_ub,
    geometric_tail,
    pseries_tail_bounds,
    split_budget,
)


@pytest.fixture(autouse=True)
def _precision():
    old = ctx.prec
    ctx.prec = 128
    yield
    ctx.prec = old


def _close(x: arb, y: arb, tol: str = "1e-30") -> bool:
    """|x - y| <= tol at both ends (both balls tight around the same value)."""
    d = x - y
    t = arb(tol)
    return bool(d <= t) and bool(-d <= t)


def test_mandate_nonempty() -> None:
    assert MANDATE and "bridge" in MANDATE.lower()


def test_geometric_tail_matches_closed_form() -> None:
    r = arb("0.5")
    for n in (0, 1, 10, 64):
        assert _close(geometric_tail(r, n), arb("2") ** (-n))


def test_geometric_tail_rejects() -> None:
    for bad in ("1", "nan", "inf", "-0.25"):
        with pytest.raises(ValueError):
            geometric_tail(arb(bad), 3)
    with pytest.raises(ValueError):
        geometric_tail(arb("0.5"), -1)


def test_pseries_bounds_bracket_true_tail() -> None:
    p = arb(2)
    lo, hi = pseries_tail_bounds(p, 5)
    assert bool(lo <= hi)
    partial = sum(1 / arb(k) ** 2 for k in range(1, 6))
    tail5 = arb.pi() ** 2 / 6 - partial
    assert bool(lo <= tail5)
    assert bool(tail5 <= hi)
    assert bool(lo <= arb("0.181"))
    assert bool(arb("0.182") <= hi)


def test_pseries_rejects() -> None:
    with pytest.raises(ValueError):
        pseries_tail_bounds(arb(1), 5)
    with pytest.raises(ValueError):
        pseries_tail_bounds(arb("nan"), 5)
    with pytest.raises(ValueError):
        pseries_tail_bounds(arb("1.5"), 0)


def test_exp_envelope_monotone_and_sound() -> None:
    f2, f3 = exp_envelope_tail(arb(2)), exp_envelope_tail(arb(3))
    assert bool(f3 <= f2)
    assert bool(f2 <= arb("0.136"))
    assert bool(arb("0.135") <= f2)
    c2 = exp_envelope_tail(arb(2), C=arb(2), lam=arb(1))
    assert bool(c2 <= arb("0.271"))
    assert bool(arb("0.270") <= c2)


def test_exp_envelope_rejects() -> None:
    with pytest.raises(ValueError):
        exp_envelope_tail(arb(1), lam=arb(0))
    with pytest.raises(ValueError):
        exp_envelope_tail(arb(1), C=arb(-1))
    with pytest.raises(ValueError):
        exp_envelope_tail(arb("nan"))


def test_gaussian_ub_sound_and_ordered() -> None:
    u2, u3 = gaussian_tail_ub(arb(2)), gaussian_tail_ub(arb(3))
    assert bool(u3 <= u2)
    assert bool(u2 <= arb("0.005"))
    mp = pytest.importorskip("mpmath")
    mp.mp.dps = 40
    spot = mp.quad(lambda x: mp.e ** (-x * x), [2, mp.inf])
    # Spot-check only (1e-12 slack): the lemma itself is analytic (L4).
    assert mp.mpf(float(u2.mid())) + mp.mpf("1e-12") >= spot


def test_gaussian_rejects() -> None:
    with pytest.raises(ValueError):
        gaussian_tail_ub(arb(0))
    with pytest.raises(ValueError):
        gaussian_tail_ub(arb("-1"))
    with pytest.raises(ValueError):
        gaussian_tail_ub(arb("inf"))


def test_split_budget_totals() -> None:
    b = split_budget(arb("1e-6"))
    assert bool(b.eps_bounded <= b.eps)
    assert bool(b.eps_tail <= b.eps)
    assert _close(b.eps_bounded + b.eps_tail, b.eps)
    q = split_budget(arb("1e-6"), frac=arb("0.25"))
    assert _close(q.eps_tail, arb("2.5e-7"))
    assert _close(q.eps_bounded, arb("7.5e-7"))


def test_split_budget_rejects() -> None:
    with pytest.raises(ValueError):
        split_budget(arb(0))
    with pytest.raises(ValueError):
        split_budget(arb("-1e-6"))
    with pytest.raises(ValueError):
        split_budget(arb("nan"))
    with pytest.raises(ValueError):
        split_budget(arb("1e-6"), frac=arb(1))
    with pytest.raises(ValueError):
        split_budget(arb("1e-6"), frac=arb(0))


def test_choose_cutoff_two_sided_width() -> None:
    eps = arb("1e-6")
    p = arb(2)

    def width(n: int) -> arb:
        lo, hi = pseries_tail_bounds(p, n)
        return hi - lo

    n = choose_cutoff(width, eps)
    assert bool(width(n) <= eps)
    assert 500 <= n <= 4096


def test_choose_cutoff_hi_only_scales() -> None:
    eps = arb("1e-6")
    n = choose_cutoff(lambda k: pseries_tail_bounds(arb(2), k)[1], eps)
    assert bool(pseries_tail_bounds(arb(2), n)[1] <= eps)
    assert n <= 2 ** 21


def test_choose_cutoff_fail_closed() -> None:
    with pytest.raises(ValueError):
        choose_cutoff(lambda k: arb("1e-9"), arb(0))
    with pytest.raises(RuntimeError):
        choose_cutoff(lambda k: arb("1e-3"), arb("1e-6"), max_doublings=4)


def test_choose_cutoff_real_exp() -> None:
    eps = arb("1e-18")
    m = choose_cutoff_real(lambda x: exp_envelope_tail(x), eps, lo=1.0, hi=100.0)
    assert bool(exp_envelope_tail(m) <= eps)
    assert 40.0 <= float(m.mid()) <= 60.0


def test_assemble_certified_and_unverified() -> None:
    ok = assemble("t", arb(1), arb("1e-12"), arb("1e-9"))
    assert ok.certified
    assert "CERTIFIED" in ok.verdict
    text = "\n".join(ok.lines())
    for tag in ("[B]", "[J]", "[U]"):
        assert tag in text
    bad = assemble("t", arb(1), arb("1e-3"), arb("1e-9"))
    assert not bad.certified
    assert "NOT CERTIFIED" in bad.verdict


def test_assemble_two_sided_and_rejects() -> None:
    cert = assemble("t", arb(1), arb("9e-10"), arb("1e-9"), tail_lo=arb("1e-10"))
    assert cert.certified
    with pytest.raises(ValueError):
        assemble("t", arb(1), arb("1e-12"), arb("1e-9"), tail_lo=arb("1e-6"))
    with pytest.raises(ValueError):
        assemble("t", arb("nan"), arb("1e-12"), arb("1e-9"))
    with pytest.raises(ValueError):
        assemble("t", arb(1), arb("1e-12"), arb(0))


def test_zeta2_bridge_end_to_end() -> None:
    eps = arb("1e-6")
    p = arb(2)
    budget = split_budget(eps)

    def width(n: int) -> arb:
        lo, hi = pseries_tail_bounds(p, n)
        return hi - lo

    n = choose_cutoff(width, budget.eps_tail)
    partial = sum(1 / arb(k) ** 2 for k in range(1, n + 1))
    lo, hi = pseries_tail_bounds(p, n)
    cert = assemble("zeta(2)", partial, hi, eps, tail_lo=lo)
    assert cert.certified
    total_lo, total_hi = cert.total()
    pi2_6 = arb.pi() ** 2 / 6
    assert bool(total_lo <= pi2_6)
    assert bool(pi2_6 <= total_hi)


def test_non_finite_never_bridges() -> None:
    for bad in ("nan", "inf", "-inf"):
        with pytest.raises(ValueError):
            assemble("t", arb(1), arb(bad), arb("1e-9"))


