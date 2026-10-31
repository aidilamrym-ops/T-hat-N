"""Test suite for Stage 4 Containment Proof and Topological Enclosures."""

from __future__ import annotations

import pytest

from msaf.chrono_runtime.stage4_containment_proof import (
    Stage4ContainmentEngine,
    run_stage4_containment_extraction,
)


def test_stage4_containment_engine() -> None:
    engine = Stage4ContainmentEngine(t_values=[14.134725])
    cert = engine.certify_containment()
    assert cert["status"] == "CERTIFIED"
    assert cert["topological_containment_verified"] is True
    assert cert["banach_contraction_verified"] is True


def test_stage4_receipt_generation() -> None:
    report = run_stage4_containment_extraction()
    assert report["status"] == "CERTIFIED"
    assert report["containment_certificate"]["status"] == "CERTIFIED"
