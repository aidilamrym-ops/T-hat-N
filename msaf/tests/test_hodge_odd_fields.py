"""Odd-characteristic extension fields regression."""
import pytest

from msaf.hodge.odd_fields import (
    count_fermat_quartic_fpn,
    fermat_quartic_smooth,
    find_modulus,
    is_irreducible_mod,
)


def test_odd_moduli_verified():
    for n in (1, 2, 3):
        mod = find_modulus(n, 3)
        assert len(mod) - 1 == n
        if n > 1:
            assert is_irreducible_mod(mod, 3) is True
    assert is_irreducible_mod([0, 0, 1], 3) is False  # x^2, repeated root
    assert is_irreducible_mod([2, 0, 1], 3) is False  # x^2-1, split roots
    assert is_irreducible_mod([0, 1], 3) is True  # linear is irreducible


def test_fermat_smooth_odd():
    assert fermat_quartic_smooth(3) is True
    assert fermat_quartic_smooth(5) is True
    with pytest.raises(ValueError):
        fermat_quartic_smooth(2)


def test_fermat_counts_f3n():
    # n = 1 reproduces the independent F_3 count (16): cross-validation
    # of the extension machinery against point_count.py.
    r1 = count_fermat_quartic_fpn(1, 3)
    assert (r1["total"], r1["affine"], r1["infinity"]) == (16, 12, 4)
    r2 = count_fermat_quartic_fpn(2, 3)
    assert (r2["total"], r2["affine"], r2["infinity"]) == (280, 252, 28)
    r3 = count_fermat_quartic_fpn(3, 3)
    assert (r3["total"], r3["affine"], r3["infinity"]) == (784, 756, 28)


def test_odd_field_input_gates():
    with pytest.raises(TypeError):
        count_fermat_quartic_fpn(1.0, 3)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        count_fermat_quartic_fpn(1, 2)
    with pytest.raises(ValueError):
        count_fermat_quartic_fpn(0, 3)
