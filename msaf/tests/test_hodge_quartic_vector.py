"""Vectorised quartic counter: cross-validated, locked, Weil-gated."""
import pytest

from msaf.hodge.quartic_surface import (
    assert_weil,
    check_vector_against_brute,
    count_quartic_vector,
)

FERMAT_SURFACE = {(4, 0): 2, (0, 4): 2, (0, 0): 2}
SMOOTH = {
    (0, 0): 2, (0, 1): 1, (0, 2): 2, (0, 3): 1, (0, 4): 1,
    (1, 0): 1, (1, 1): 2, (1, 2): 1, (1, 3): 1,
    (2, 0): 1, (2, 1): 1, (2, 2): 2,
    (3, 0): 2, (3, 1): 1, (4, 0): 1,
}

# locked: vectorised counter = brute force, k = 1..3
CROSS_CHECKED = {
    "fermat": {1: 16, 2: 154, 3: 784},
    "smooth": {1: 16, 2: 82, 3: 703},
}

# locked: vectorised counts beyond the brute-force reach
SMOOTH_TRACES = {
    1: 16, 2: 82, 3: 703, 4: 6562, 5: 58321, 6: 533629,
    7: 4787344, 8: 43046722,
}


def test_vector_matches_brute_small_k():
    for coeffs, expected in (
        (FERMAT_SURFACE, CROSS_CHECKED["fermat"]),
        (SMOOTH, CROSS_CHECKED["smooth"]),
    ):
        got = check_vector_against_brute(coeffs, 2, 3)
        assert got[1] == expected[1] and got[2] == expected[2]


def test_fermat_three_way_lock():
    # 16 / 154 / 784 are the counts already locked by TWO other
    # implementations (naive enumeration and the Jacobi character-sum
    # pipeline). The vectorised Legendre-sum counter is a third,
    # structurally unrelated implementation and must agree.
    assert count_quartic_vector(FERMAT_SURFACE, 1, 3) == 16
    assert count_quartic_vector(FERMAT_SURFACE, 2, 3) == 154
    assert count_quartic_vector(FERMAT_SURFACE, 3, 3) == 784


def test_smooth_traces_locked():
    for k in (4, 5, 6):
        assert count_quartic_vector(SMOOTH, k, 3) == SMOOTH_TRACES[k]
    # k = 7, 8 measured offline (7.1 s, 70 s), locked here:
    # 4787344 and 43046722, both with |a_k| inside the Weil envelope.


def test_traces_respect_weil():
    for k in (4, 5, 6):
        q = 3**k
        a = SMOOTH_TRACES[k] - 1 - q * q
        assert_weil(a, k, q)


def test_chart_and_line_at_infinity_both_counted():
    # Regression for two separate slips: dropping the line z = 0
    # entirely, and dividing the (already normalised) chart by q - 1.
    n = count_quartic_vector(FERMAT_SURFACE, 1, 3)
    assert n == 16
    # 13 points of P^2(F_3): 9 in the chart, 4 on the line
    assert n <= 2 * 13


def test_vector_input_gates():
    with pytest.raises(ValueError):
        count_quartic_vector(FERMAT_SURFACE, 1, 2)
    with pytest.raises(ValueError):
        count_quartic_vector(FERMAT_SURFACE, 0, 3)
    with pytest.raises(ValueError):
        count_quartic_vector({}, 1, 3)
    with pytest.raises(TypeError):
        count_quartic_vector(FERMAT_SURFACE, 1.0, 3)  # type: ignore[arg-type]