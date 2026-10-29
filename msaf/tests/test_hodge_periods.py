"""Hodge periods regression (AGM measurement + triple validation)."""
import pytest

from msaf.hodge.periods import algebraic_j, elliptic_periods


def test_square_lattice_tau_contains_i():
    from flint import acb, arb

    res = elliptic_periods("2", "1", "0")
    assert bool(res["tau"].contains(acb(arb(0), arb(1)))) is True


def test_lambda4_j_match():
    res = elliptic_periods("4", "1", "0")
    assert bool(res["j_of_tau"].contains(algebraic_j("4"))) is True


def test_lambda4_orbit_locks_convention():
    # Canonical basis gives lambda = 1/4; the swapped basis would
    # give 3/4. This test pins the convention against silent swaps.
    from flint import arb

    res = elliptic_periods("4", "1", "0")
    assert bool(res["lambda_of_tau"].contains(arb("0.25"))) is True
    assert bool(res["tau"].imag.mid() > arb("1")) is True


def test_periods_input_gates():
    with pytest.raises(TypeError):
        elliptic_periods(4.0, "1", "0")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        elliptic_periods("1", "1", "0")
    with pytest.raises(ValueError):
        elliptic_periods("0", "1", "2")


