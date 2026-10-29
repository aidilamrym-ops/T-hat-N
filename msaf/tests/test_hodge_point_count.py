"""Picard-program point counting regression (hand-derived oracles)."""
import pytest

from msaf.hodge.point_count import count_fermat_quartic, is_frobenius_degenerate


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


def test_char2_degeneracy():
    """Over F_2, x^4+y^4+z^4+w^4 IS (x+y+z+w)^4: quadruple plane.

    Pointwise witness on all of F_2^4 (decisive for counting: every
    counted point lies on the fattened hyperplane, so no K3
    interpretation may be attached to F_2 counts).
    """
    for x in (0, 1):
        for y in (0, 1):
            for z in (0, 1):
                for w in (0, 1):
                    assert (x + y + z + w) ** 4 % 2 == (x + y + z + w) % 2
                    assert (x**4 + y**4 + z**4 + w**4) % 2 == (x + y + z + w) % 2


def test_frobenius_degeneracy_gate():
    fermat4 = [[4, 0, 0, 0], [0, 4, 0, 0], [0, 0, 4, 0], [0, 0, 0, 4]]
    assert is_frobenius_degenerate(fermat4, 2) is True
    assert is_frobenius_degenerate(fermat4, 3) is False
    assert is_frobenius_degenerate(fermat4, 5) is False
    assert is_frobenius_degenerate([[2, 0], [0, 2]], 2) is True
    assert is_frobenius_degenerate([[3, 0, 0], [0, 3, 0], [0, 0, 3]], 2) is False


