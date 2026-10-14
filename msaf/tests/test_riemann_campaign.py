"""Riemann exclusion campaign regression (bounded certificates)."""
import pytest

from msaf.riemann.exclusion import (
    certify_box_absent,
    exclusion_box,
    sweep_exclusion,
)


def test_exclusion_single_friendly_box():
    box = exclusion_box("15.0", "15.01", "0.495", "0.505")
    res = certify_box_absent(box)
    assert res["absent"] is True


def test_exclusion_zero_box_never_clears():
    box = exclusion_box("14.1", "14.2", "0.4", "0.6")
    res = certify_box_absent(box)
    assert res["absent"] is False
    out = sweep_exclusion("14.1", "14.2", "0.4", "0.6", max_depth=2)
    assert out["verdict"] == "INCONCLUSIVE"
    assert len(out["stuck"]) >= 1
    assert all(leaf["status"] == "CANNOT-EXCLUDE" for leaf in out["stuck"])


def test_sweep_small_range_all_clear():
    out = sweep_exclusion("15.0", "15.06", "0.49", "0.51", max_depth=6)
    assert out["verdict"] == "ALL-CLEAR"
    assert out["stuck"] == []
    assert len(out["certified"]) >= 1


def test_exclusion_float_rejection():
    with pytest.raises(TypeError):
        exclusion_box(15.0, "15.1")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        sweep_exclusion("15.0", "15.1", max_depth=2.0)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        exclusion_box("16.0", "15.0")
