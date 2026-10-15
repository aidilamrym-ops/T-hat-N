"""General quartic surfaces: Groebner smoothness certificate + counts."""
import pytest

from msaf.hodge.groebner import Poly, groebner_contains_one
from msaf.hodge.quartic_surface import (
    count_quartic_brute,
    is_smooth_branch,
    quartic_traces,
)

FERMAT_SURFACE = {(4, 0): 2, (0, 4): 2, (0, 0): 2}  # {w^2 = -(x^4+y^4+z^4)}
FERMAT_TWIST = {(4, 0): 1, (0, 4): 1, (0, 0): 1}  # the quadratic twist
SMOOTH_RANDOM = {
    (0, 0): 2, (0, 1): 1, (0, 2): 2, (0, 3): 1, (0, 4): 1,
    (1, 0): 1, (1, 1): 2, (1, 2): 1, (1, 3): 1,
    (2, 0): 1, (2, 1): 1, (2, 2): 2,
    (3, 0): 2, (3, 1): 1, (4, 0): 1,
}
DOUBLED_CONIC = {
    (4, 0): 1, (0, 4): 1, (0, 0): 1,
    (2, 2): 2, (0, 2): 2, (2, 0): 2,
}


def test_groebner_unit_ideal_controls():
    # (y-1, x, x-1) has no common zero -> unit ideal -> True
    p = 3
    ym1 = Poly(p, [((0, 1), 1), ((0, 0), 2)])
    x = Poly(p, [((1, 0), 1)])
    xm1 = Poly(p, [((1, 0), 1), ((0, 0), 2)])
    assert groebner_contains_one([ym1, x, xm1], p) is True
    # (y-1, x) has the zero (0, 1) -> not the unit ideal
    assert groebner_contains_one([ym1, x], p) is False


def test_fermat_surface_is_smooth():
    assert is_smooth_branch(FERMAT_SURFACE, 3) is True
    assert is_smooth_branch(FERMAT_TWIST, 3) is True


def test_doubled_conic_is_singular():
    # (x^2+y^2+z^2)^2 is a doubled smooth conic: singular by hand.
    assert is_smooth_branch(DOUBLED_CONIC, 3) is False


def test_count_matches_independently_locked_fermat():
    # The Jacobi/naive pipeline locked #X(F_3) = 16 for the Fermat
    # quartic; here the same surface is written as a double cover and
    # counted from scratch. Two unrelated implementations agree.
    assert count_quartic_brute(FERMAT_SURFACE, 1, 3) == 16
    assert count_quartic_brute(FERMAT_SURFACE, 2, 3) == 154


def test_twist_and_surface_differ():
    # The quadratic twist is a different surface; conflating the two
    # sign conventions is exactly the error this locks.
    assert count_quartic_brute(FERMAT_TWIST, 1, 3) == 10


def test_smooth_random_counts_within_weil():
    for k, expect_n in ((1, 16), (2, 82)):
        q = 3**k
        n = count_quartic_brute(SMOOTH_RANDOM, k, 3)
        assert n == expect_n
        a = n - 1 - q * q
        assert abs(a) <= 22 * q
    # k = 3 measured once and locked: #X(F_27) = 703, a_3 = -27
    # (recomputed here only in the offline probe: 7.7 s)


def test_weil_gate_is_a_count_check_not_a_smoothness_check():
    from msaf.hodge.quartic_surface import assert_weil

    assert_weil(5, 1, 3)  # a small trace passes
    with pytest.raises(RuntimeError, match="Weil"):
        assert_weil(835, 2, 9)  # exactly what the q-1 overcount produced
    # Documented limitation (measured, not assumed): a certified
    # SINGULAR quartic over F_3 produced |a_2| = 27 < 198, inside the
    # envelope. The gate therefore never certifies smoothness --
    # is_smooth_branch is the separate witness.


def test_input_gates():
    with pytest.raises(ValueError):
        count_quartic_brute(FERMAT_SURFACE, 1, 2)
    with pytest.raises(ValueError):
        count_quartic_brute(FERMAT_SURFACE, 0, 3)
    with pytest.raises(TypeError):
        count_quartic_brute(FERMAT_SURFACE, 1.0, 3)  # type: ignore[arg-type]