"""Certified zero-counter regression (bounded completeness)."""
import pytest

from msaf.riemann.counter import count_zeros


def test_counter_gamma1_complete():
    out = count_zeros("13.9", "14.4")
    assert out["verdict"] == "COMPLETE"
    assert out["count"] == 1
    assert out["stuck"] == []


def test_counter_range_complete_two():
    out = count_zeros("10.0", "24.5")
    assert out["verdict"] == "COMPLETE"
    assert out["count"] == 2
    assert out["stuck"] == []


def test_counter_empty_range_complete_zero():
    out = count_zeros("15.0", "15.5")
    assert out["verdict"] == "COMPLETE"
    assert out["count"] == 0


def test_counter_boundary_range_complete():
    # [10,25] abuts gamma_3 = 25.01 yet completes: fine subdivision
    # clears the edge region (single-step soundness needs no luck).
    out = count_zeros("10.0", "25.0")
    assert out["verdict"] == "COMPLETE"
    assert out["count"] == 2
    assert out["stuck"] == []


def test_counter_range_zero_fifty_complete_ten():
    # Flagship bounded result: exactly the ten known zeros live in
    # [0.49,0.51] x [0,50]; nothing else, nothing stuck. (~14 s.)
    out = count_zeros("0.0", "50.0")
    assert out["verdict"] == "COMPLETE"
    assert out["count"] == 10
    assert out["stuck"] == []


def test_counter_no_false_existence():
    # Locks the inherited verdict boundary: a point seed far from any
    # zero must NEVER satisfy the strict existence criteria, even
    # though the loose verdict string claims localization on a ball
    # that provably contains no zero at all.
    from flint import acb, arb

    from msaf.zeta_inversion import (
        contains_zero_complex,
        evaluate_xi,
        locate_zero,
    )

    res = locate_zero(acb(arb("0.5"), arb("10.0")), 20)
    strict = (
        res.verdict == "ZERO-LOCALIZED"
        and bool(res.newton_contained)
        and bool(res.derivative_excludes_zero)
    )
    assert strict is False
    assert not contains_zero_complex(evaluate_xi(res.final_ball))


def test_counter_float_rejection():
    with pytest.raises(TypeError):
        count_zeros(10.0, "25.0")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        count_zeros("25.0", "10.0")
