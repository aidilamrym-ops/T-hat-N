"""Moore-premise verifier regression (Lean-Banach correspondence)."""
from flint import acb, arb, ctx

from msaf.riemann.moore_premises import verify_moore_premises
from msaf.zeta_inversion import locate_zero


def _wide(c: str, r: str) -> arb:
    return (arb(c) - arb(r)).union(arb(c) + arb(r))


def test_moore_premises_gamma1_hold():
    ctx.prec = 256
    box = acb(_wide("0.5", "1e-6"), _wide("14.1347251417", "1e-6"))
    res = locate_zero(box, 20)
    assert res.verdict == "ZERO-LOCALIZED"
    assert bool(res.newton_contained) is True
    out = verify_moore_premises(res.final_ball)
    assert out["verdict"] == "PREMISES-HOLD"
    assert out["maps_to"] is True
    assert out["deriv_excludes_zero"] is True
    assert out["k_below_one"] is True
    assert "analogue" in out["scope"] and "unformalized" in out["scope"]


def test_moore_premises_zero_free_fail():
    ctx.prec = 256
    box = acb(_wide("0.5", "1e-6"), _wide("10.0", "1e-6"))
    out = verify_moore_premises(box)
    assert out["verdict"] == "PREMISES-FAIL"


