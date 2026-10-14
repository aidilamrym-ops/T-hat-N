"""Finite-field machinery regression (verified moduli + traces)."""
import pytest

from msaf.hodge.finite_fields import MODULI, frobenius_traces, is_irreducible


def test_moduli_verified_irreducible():
    for n, mod in sorted(MODULI.items()):
        assert mod.bit_length() - 1 == n
        assert is_irreducible(mod) is True
    assert is_irreducible(0b101) is False  # (x+1)^2
    assert is_irreducible(0b1001) is False  # (x+1)(x^2+x+1)
    with pytest.raises(TypeError):
        is_irreducible(3.0)  # type: ignore[arg-type]


def test_frobenius_traces_small():
    assert frobenius_traces([1, 2, 3]) == {1: 2, 2: 4, 3: 8}


def test_finite_field_input_gates():
    with pytest.raises(TypeError):
        frobenius_traces([1.0])  # type: ignore[list-item]
    with pytest.raises(ValueError):
        frobenius_traces([7])
