"""Frontier depth regression: Z3 double-entry on the first zeta zero.

Skips honestly where the zeta layer is absent (isolated workspace):
``importorskip`` keeps T-hat-N green without faking a PASS.
"""
import pytest

msaf_zeta = pytest.importorskip("msaf.zeta_inversion")


def test_z3_containment_first_zero():
    from msaf.milenium_frontier.pure_rh_strengthen import PureRiemannVerify

    v = PureRiemannVerify(256)
    res = v.z3_confirm_containment("0.5", "14.134725")
    assert res["z3_verdict"] == "sat"
    assert res["contains_half"] is True
    assert "local enclosures only" in res["scope"]


