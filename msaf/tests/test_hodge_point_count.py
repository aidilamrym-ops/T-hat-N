"""Picard-program point counting regression (hand-derived oracles)."""
import pytest

from msaf.hodge.point_count import count_fermat_quartic


def test_fermat_quartic_f2_is_seven():
    res = count_fermat_quartic(2)
    assert res["total"] == 7
    assert res["affine"] == 4
    assert res["infinity"] == 3


def test_fermat_quartic_f3_is_16():
    res = count_fermat_quartic(3)
    assert res["total"] == 16
    assert res["affine"] == 12
    assert res["infinity"] == 4


def test_fermat_quartic_f5_is_empty():
    res = count_fermat_quartic(5)
    assert res["total"] == 0


def test_point_count_input_gates():
    with pytest.raises(TypeError):
        count_fermat_quartic(2.0)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        count_fermat_quartic(4)
    with pytest.raises(ValueError):
        count_fermat_quartic(1)
