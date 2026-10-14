"""Jacobi character-sum traces regression (cross-locked, certified)."""
import pytest

from msaf.hodge.odd_fields import jacobi_trace


def test_jacobi_traces_match_naive():
    # Exact agreement with independent naive enumeration.
    assert jacobi_trace(1, 3)["projective"] == 16
    assert jacobi_trace(2, 3)["projective"] == 280
    assert jacobi_trace(3, 3)["projective"] == 784
    assert jacobi_trace(4, 3)["projective"] == 8344


def test_jacobi_closed_form_odd():
    # e = 2 forces N_proj = (q+1)^2 exactly; Jacobi must reproduce it
    # far beyond naive reach (q = 243 here).
    r = jacobi_trace(5, 3)
    assert r["e"] == 2
    assert r["projective"] == (243 + 1) ** 2


def test_jacobi_input_gates():
    with pytest.raises(TypeError):
        jacobi_trace(1.0, 3)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        jacobi_trace(1, 2)
