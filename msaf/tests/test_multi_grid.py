"""Multi-grid pivot-stability regression (R3)."""


def test_multi_grid_stub():
    pass


def test_multi_grid_pivot_n16():
    from msaf.navier_stokes.multi_grid_check import verify_multi_grid_pivot_stability

    res = verify_multi_grid_pivot_stability(16, "0.1")
    assert res["grid"] == 16
    assert res["status"] in ("CERTIFIED_POSITIVE", "SKIPPED")


def test_multi_grid_pivot_n32():
    from msaf.navier_stokes.multi_grid_check import verify_multi_grid_pivot_stability

    res = verify_multi_grid_pivot_stability(32, "0.1")
    assert res["grid"] == 32
    assert res["status"] in ("CERTIFIED_POSITIVE", "SKIPPED")


def test_multi_grid_n64_lock():
    from msaf.navier_stokes.multi_grid_check import verify_multi_grid_pivot_stability

    res = verify_multi_grid_pivot_stability(64, "0.1")
    assert res["status"] == "CERTIFIED_POSITIVE"


def test_pure_rh_scaffolding_gate():
    import pytest

    from msaf.milenium_frontier.pure_rh_strengthen import PureRiemannVerify

    v = PureRiemannVerify(256)
    assert "local enclosures only" in v.SCOPE
    with pytest.raises(TypeError):
        v._guess(0.5, 14.0)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        PureRiemannVerify(256.0)  # type: ignore[arg-type]


def test_hodge_lattice_initialization():
    import pytest

    from msaf.milenium_frontier.hodge_conjecture_lattice import HodgeLattice

    h = HodgeLattice(3, 1)
    assert "finite rational shadow" in h.SCOPE
    k = h.add_cycle(("1/2", "-3", 2))
    assert h.is_rational_hodge_class(k) is True
    assert str(h.pairing_value(k, k)) == "53/4"
    with pytest.raises(TypeError):
        h.add_cycle((0.5, 0.0, 0.0))  # type: ignore[arg-type]
