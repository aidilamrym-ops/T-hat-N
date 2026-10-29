"""Fermat-quartic K3 over F_5: exact pipeline and Picard bound."""
import pytest

from msaf.hodge.fermat_k3 import fermat_k3_picard, fermat_k3_report
from msaf.hodge.gauss_exact import fermat_quartic_projective_exact as exact
from msaf.hodge.odd_fields import jacobi_trace

EXACT_COUNTS = {
    1: 0,
    2: 1112,
    3: 15360,
    4: 402072,
    5: 9753600,
    6: 244476632,
    7: 6103050240,
}
TRACES = {
    1: -26,
    2: 486,
    3: -266,
    4: 11446,
    5: -12026,
    6: 336006,
    7: -465386,
    8: 8142166,
    9: -5968346,
    10: 176005926,
    11: -125576906,
}


def test_exact_matches_ball_sweep():
    # Two independent implementations of the same counts: exact
    # Z[zeta_20] + Davenport-Hasse vs the O(p^n) ball sweep.
    for n in range(1, 6):
        assert exact(n, 5)["projective"] == jacobi_trace(n, 5)["projective"]


def test_exact_matches_locked_counts():
    for n, value in EXACT_COUNTS.items():
        assert exact(n, 5)["projective"] == value


def test_exact_beyond_ball_reach():
    # The ball sweep stalls near n = 8 (~5 min per degree); the exact
    # lifted version reaches n = 10, 11 in milliseconds.
    assert exact(10, 5)["projective"] == 95367607646552
    assert exact(11, 5)["projective"] == 2384185665438720


def test_lift_refused_where_invalid():
    # p = 3, even n: characters of order 4 over F_{3^n} have no lift
    # from F_3 and the naive lift is the WRONG sum. The module refuses
    # loudly with NotImplementedError, naming the F_{p^2} remedy,
    # instead of returning a plausible-looking integer.
    with pytest.raises(NotImplementedError, match="not yet implemented"):
        exact(2, 3)
    assert exact(1, 3)["projective"] == 16  # odd n: e = 2 lifts fine
    # Distinct motivation, distinct branch: for p = 3 mod 4 with even n
    # (p here = 7) Davenport-Hasse genuinely does not cover the order-4
    # case -> the generic RuntimeError must stay in place and covered.
    with pytest.raises(RuntimeError, match="Davenport-Hasse"):
        exact(2, 7)


def test_exact_input_gates():
    with pytest.raises(TypeError):
        exact(1.0, 5)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        exact(1, 2)
    with pytest.raises(ValueError):
        exact(0, 5)


def test_k3_f5_picard_bound():
    out = fermat_k3_picard(5, 11)
    assert out["traces"] == TRACES
    # surface FE closes: leading coefficient q^22 with sign +1.
    assert out["leading_coeff"] == str(5**22)
    # Structure: 20 Picard-type eigenvalues (8 of +5, 12 of -5) plus
    # the pair -3 +- 4i; the bound is 20, non-vacuous vs the F_3
    # value 22 (which no K3 can reach: rho <= b_2 - 2 = 20).
    assert out["picard_upper_bound"] == 20
    assert out["sign"] == 1
    assert out["exact_orders"] == {1: 8, 2: 12}
    assert out["vacuous"] is False


def test_k3_f5_structure_cross_check():
    # If the eigenvalue structure 8*(5) + 12*(-5) + (-3 +- 4i) is the
    # truth then a_2 = 8*25 + 12*25 + [(-3+4i)^2 + (-3-4i)^2] = 486.
    out = fermat_k3_picard(5, 11)
    assert out["traces"][2] == 8 * 25 + 12 * 25 + (-7 - 24) + (-7 + 24)


def test_report_is_honest():
    text = fermat_k3_report(5)["text"]
    assert "no statement about" in text
    assert "Picard rank upper bound (van Luijk): 20" in text

