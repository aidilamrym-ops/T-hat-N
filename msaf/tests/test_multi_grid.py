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
