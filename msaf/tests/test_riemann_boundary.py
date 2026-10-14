"""Boundary zero-free certificates (Turing G1 prerequisite)."""
import pytest

from msaf.riemann.boundary import certify_boundary
from msaf.riemann.counter import count_zeros


def test_boundary_gamma1_all_clear():
    out = certify_boundary("13.9", "14.4")
    assert out["verdict"] == "ALL-CLEAR"
    assert out["stuck"] == []
    assert len(out["certified"]) >= 4


def test_boundary_empty_range_all_clear():
    out = certify_boundary("15.0", "15.5")
    assert out["verdict"] == "ALL-CLEAR"
    assert out["stuck"] == []


def test_boundary_gamma1_interior_plus_edge():
    # G1-a milestone lock: COMPLETE interior count of 1 together
    # with an ALL-CLEAR contour pins "exactly one zero inside,
    # none on the edge" -- the well-posed setup for winding.
    counted = count_zeros("13.9", "14.4")
    edged = certify_boundary("13.9", "14.4")
    assert counted["verdict"] == "COMPLETE" and counted["count"] == 1
    assert edged["verdict"] == "ALL-CLEAR" and edged["stuck"] == []


def test_boundary_flagship_all_clear():
    # Full [0,50] contour (~10k evals, a few seconds): every edge of
    # the flagship rectangle is provably zero-free.
    out = certify_boundary("0.0", "50.0")
    assert out["verdict"] == "ALL-CLEAR"
    assert out["stuck"] == []


def test_boundary_through_zero_never_clears():
    # Bottom edge at sig=0.5 runs at/near gamma_1: segments around
    # the zero can never exclude it -- honest negative path.
    out = certify_boundary("14.1", "14.2", "0.5", "0.51", max_depth=8)
    assert out["verdict"] == "INCONCLUSIVE"
    assert len(out["stuck"]) >= 1
    assert all(leaf["status"] == "CANNOT-EXCLUDE" for leaf in out["stuck"])
    assert any(leaf["edge"] == "bottom" for leaf in out["stuck"])


def test_boundary_float_rejection():
    with pytest.raises(TypeError):
        certify_boundary(13.9, "14.4")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        certify_boundary("13.9", "14.4", max_depth=8.0)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        certify_boundary("14.4", "13.9")
