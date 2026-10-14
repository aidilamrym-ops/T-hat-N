"""Certified winding-number regression (Turing G1-b independent count)."""
import pytest

from msaf.riemann.counter import count_zeros
from msaf.riemann.winding import winding_number


def test_winding_gamma1_one():
    out = winding_number("13.9", "14.4")
    assert out["verdict"] == "COMPUTED"
    assert out["winding"] == 1
    assert out["stuck"] == []


def test_winding_empty_zero():
    out = winding_number("15.0", "15.5")
    assert out["verdict"] == "COMPUTED"
    assert out["winding"] == 0
    assert out["stuck"] == []


def test_winding_cross_lock():
    # Two independent algorithms, same rectangles: Newton isolation
    # from the inside vs arg winding from the outside must agree.
    for a, b, n in (("13.9", "14.4", 1), ("10.0", "24.5", 2)):
        counted = count_zeros(a, b)
        wound = winding_number(a, b)
        assert counted["verdict"] == "COMPLETE"
        assert wound["verdict"] == "COMPUTED"
        assert wound["winding"] == n == counted["count"]


def test_winding_flagship_ten():
    # Full [0,50]: winding 10 by contour integration alone.
    out = winding_number("0.0", "50.0")
    assert out["verdict"] == "COMPUTED"
    assert out["winding"] == 10
    assert out["stuck"] == []


def test_winding_through_zero_inconclusive():
    # Contour runs at/near gamma_1: no number is ever returned.
    out = winding_number("14.1", "14.2", "0.5", "0.51", max_depth=8)
    assert out["verdict"] == "INCONCLUSIVE"
    assert out["winding"] is None
    assert len(out["stuck"]) >= 1


def test_winding_float_rejection():
    with pytest.raises(TypeError):
        winding_number(13.9, "14.4")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        winding_number("13.9", "14.4", max_depth=8.0)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        winding_number("14.4", "13.9")
