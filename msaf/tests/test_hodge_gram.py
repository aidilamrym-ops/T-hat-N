"""Hodge Gram exactness + Sylvester definiteness regression.

Pure-stdlib rational path (``fractions.Fraction``): runs in both the
full repository and the Navier-Stokes-only isolated workspace.
"""
from fractions import Fraction

import pytest

from msaf.milenium_frontier.hodge_conjecture_lattice import HodgeLattice


def test_hodge_gram_pairing_exactness():
    h = HodgeLattice(2, 1)
    gram = h.compute_exact_gram_matrix([[1, 0], [0, 1]])
    assert gram == [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    assert all(type(x) is Fraction for row in gram for x in row)
    h.add_cycle([1, 0])
    h.add_cycle([0, 1])
    pos = h.verify_hodge_cycle_definiteness()
    assert pos["status"] == "POSITIVE_DEFINITE"
    assert pos["leading_minors"] == ["1", "1"]

    d = HodgeLattice(2, 1)
    d.add_cycle([1, 1])
    d.add_cycle([1, 1])
    undet = d.verify_hodge_cycle_definiteness()
    assert undet["status"] == "UNDETERMINED"
    assert undet["leading_minors"] == ["2", "0"]

    n = HodgeLattice(2, 1)
    n.pairing = [[Fraction(-1), Fraction(0)], [Fraction(0), Fraction(-1)]]
    n.add_cycle([1, 0])
    n.add_cycle([0, 1])
    neg = n.verify_hodge_cycle_definiteness()
    assert neg["status"] == "NEGATIVE_DEFINITE"
    assert neg["leading_minors"] == ["-1", "1"]

    assert HodgeLattice._exact_det(
        [[Fraction(x) for x in r] for r in [[1, 1, 0], [1, 1, 1], [0, 1, 1]]]
    ) == Fraction(-1)

    with pytest.raises(ValueError):
        HodgeLattice(2, 1).verify_hodge_cycle_definiteness()
    with pytest.raises(TypeError):
        h.compute_exact_gram_matrix([[0.5, 0]])  # type: ignore[list-item]
    with pytest.raises(TypeError):
        h.add_cycle([1.0, 0])  # type: ignore[list-item]


