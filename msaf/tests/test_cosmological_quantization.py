from __future__ import annotations

import json
from pathlib import Path
from msaf.problems.cosmological_quantization import run_cosmological_quantization_verification, VALIDATION_TOKEN

def test_cosmological_quantization_execution():
    res = run_cosmological_quantization_verification(write_receipt=False)
    assert res["verdict"] == "CERTIFIED"
    assert res["validation_token"] == VALIDATION_TOKEN
    assert res["barrier_bounded"] is True
    assert res["vacuum_collapsed"] is True
    assert res["method"] == "gershgorin_bounds + banded_ldl"
    assert res["ldl_certified"] is True
    assert res["ldl_pivots_positive_A"] is True
    assert res["ldl_pivots_positive_I_minus_A"] is True
    assert res["ldl_residual_contains_A"] is True
    assert res["ldl_residual_contains_I_minus_A"] is True
    # Guard against a regression back to the dense 24000-bit eigensolver,
    # which takes days for dim=802 on the working machine.
    assert res["wall_time_seconds"] < 30

    receipt_path = Path(__file__).resolve().parents[2] / "reports" / "cosmological_quantization_receipt_2026-11-03.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["verdict"] == "CERTIFIED"
    assert data["ldl_certified"] is True
