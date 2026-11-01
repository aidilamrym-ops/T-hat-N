"""Test suite for Stage 4 Containment Proof and Topological Enclosures.

The engine must report *exactly* what it measured. On the scaffold inputs the
interval-Newton image escapes the ball, so the topological containment gate is
NOT certified even though the Banach contraction bound holds. These tests pin
that honesty rule: a failed localisation may never inherit a CERTIFIED status.
"""

from __future__ import annotations

from msaf.chrono_runtime.stage4_containment_proof import (
    Stage4ContainmentEngine,
    run_stage4_containment_extraction,
)


def test_stage4_banach_gate_and_honest_status() -> None:
    engine = Stage4ContainmentEngine(t_values=[14.134725])
    cert = engine.certify_containment()

    # The contraction bound is what this engine can actually certify.
    assert cert["banach_contraction_verified"] is True
    assert cert["localized_zeros_count"] <= cert["tested_zeros_count"]

    # If no zero was localized, containment must not be reported as verified.
    if cert["localized_zeros_count"] < cert["tested_zeros_count"]:
        assert cert["topological_containment_verified"] is False
        assert cert["status"] == "NOT_VERIFIED"
    else:
        assert cert["status"] == "CERTIFIED"


def test_stage4_receipt_status_matches_certificate() -> None:
    report = run_stage4_containment_extraction()
    cert = report["containment_certificate"]
    assert report["status"] == cert["status"]
    assert cert["scope_notice"]["rh_global_analytic_proof_claim"] is False
    assert cert["scope_notice"]["absolute_infinite_continuum_derivation"] is False


def test_stage4_radius_stays_under_threshold() -> None:
    engine = Stage4ContainmentEngine(t_values=[14.134725])
    cert = engine.certify_containment()
    assert cert["max_radius"] <= cert["threshold"]
