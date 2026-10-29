"""Fermat quartic K3 over other primes: the bound is always 20.

NEGATIVE RESULT (machine-verified, intentional): for the Fermat
quartic the van Luijk bound equals 20 = b_2 - 2 for every prime
tried, because the surface's geometric Picard rank IS 20. The
family can never give a bound below 20 -- the method is
structurally saturated here. These locks exist so the family is
proven exhausted as a source of informative bounds, rather than
merely untried.

An informative bound needs a K3 of LOW geometric Picard rank. The
char-2 Artin-Schreier attempt (msaf/hodge/char2_k3.py draft) is
recorded as mapped-open in the register: in characteristic 2 the
naive form w^2 + w = F(x,y,z) is singular at z = 0 (W^2 + x^6 =
(W + x^3)^2, inseparable), and the separable replacement w^2 + wH
+ G needs a different counting scheme. Not shipped half-verified.
"""
import pytest

from msaf.hodge.fermat_k3 import fermat_k3_picard

TRACES_13 = {
    1: -42,
    2: 3142,
    3: -12858,
    4: 570742,
    5: -802122,
    6: 103447462,
    7: -297316698,
    8: 14683381462,
    9: -50901802602,
    10: 2948010155782,
    11: -3826475324538,
}
TRACES_17 = {
    1: 310,
    2: 6102,
    3: 97270,
    4: 1607062,
    5: 30583990,
    6: 435456342,
    7: 8993624950,
    8: 129577870102,
    9: 2442475810870,
    10: 41070203130582,
    11: 642490589315830,
}


@pytest.mark.parametrize("p,traces", [(13, TRACES_13), (17, TRACES_17)])
def test_fermat_bound_saturated_at_twenty(p, traces):
    out = fermat_k3_picard(p, 11)
    assert out["traces"] == traces
    assert out["leading_coeff"] == str(p**22)
    assert out["picard_upper_bound"] == 20
    assert out["vacuous"] is False


def test_fermat_bound_is_structural_not_accidental():
    # 20 of the 22 eigenvalues are of the form p * zeta (orders 1
    # and 2 in these primes), i.e. the surface is "20-algebraic":
    # the bound equals its geometric Picard rank by construction.
    for p in (13, 17):
        out = fermat_k3_picard(p, 11)
        assert sum(out["exact_orders"].values()) == 20

