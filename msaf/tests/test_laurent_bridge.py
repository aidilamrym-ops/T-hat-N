"""Test suite for the Laurent-Logic Bridge Operator.

Verifies exact FLINT rational structures, structural integrity rejection of floats,
and residue enclosure bounds below 1e-12.
"""

from __future__ import annotations

import pytest
from flint import arb, fmpq

from msaf.chrono_runtime.laurent_bridge_operator import (
    LaurentLogicBridgeEngine,
    StructuralIntegrityViolation,
    run_laurent_bridge_analysis,
)


def test_structural_integrity_rejects_floats() -> None:
    with pytest.raises(StructuralIntegrityViolation):
        LaurentLogicBridgeEngine([1.5, 2.0], p=1)


def test_exact_rational_coefficients() -> None:
    engine = LaurentLogicBridgeEngine([fmpq(1, 2), fmpq(3, 4)], p=1)
    assert engine.coefficients[0] == fmpq(1, 2)


def test_residue_enclosure_bounds() -> None:
    engine = LaurentLogicBridgeEngine([1, 0, 5], p=1)
    res = engine.enclose_residues()
    assert res["bounded_below_threshold"] is True
    assert res["status"] == "CERTIFIED"


def test_receipt_generation() -> None:
    report = run_laurent_bridge_analysis()
    assert report["status"] == "CERTIFIED"
    assert report["residue_analysis"]["bounded_below_threshold"] is True
