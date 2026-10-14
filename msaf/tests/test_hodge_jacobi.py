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


def test_trace_form_linear_lock():
    # Tr is F_p-linear: the fast dot-product form (used in the Jacobi
    # hot loop) must agree with the reference Frobenius iteration.
    import random

    from msaf.hodge.odd_fields import (
        _field_elements,
        _trace_form,
        _trace_lin,
        _trace_to_fp,
        find_modulus,
    )

    for n, p in ((3, 3), (4, 3), (5, 3), (6, 5)):
        mod = find_modulus(n, p)
        tvec = _trace_form(n, p, mod)
        assert tvec[0] == n % p  # Tr(1) = n mod p
        elems = _field_elements(n, p)
        random.seed(0)
        for a in random.sample(elems, min(100, len(elems))):
            assert _trace_to_fp(a, mod, p, n) == _trace_lin(a, tvec, p)
