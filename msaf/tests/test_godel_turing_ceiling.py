import pytest
from msaf.godel_turing_ceiling import interval_newton_contract, ResolutionAlarm, check_finite_lattice

def test_finite_lattice_bound():
    assert check_finite_lattice(1000) == True
    assert check_finite_lattice(5440000000000000000000000000000000000000000000000000000000000) == True
    assert check_finite_lattice(5440000000000000000000000000000000000000000000000000000000001) == False

def test_newton_escape():
    res = interval_newton_contract({'val': 10.5, 'steps': 10}, (0.0, 1.0))
    assert res["topological_containment_verified"] is False
    assert res["status"] == "NEWTON-IMAGE-ESCAPED"

def test_newton_contained():
    res = interval_newton_contract({'val': 0.5, 'steps': 10}, (0.0, 1.0))
    assert res["topological_containment_verified"] is True
    assert res["status"] == "CONTAINED"

def test_lattice_exhaustion():
    with pytest.raises(ResolutionAlarm):
        interval_newton_contract({'val': 0.5, 'steps': 10_000_000_000_000_000_000_000}, (0.0, 1.0))
