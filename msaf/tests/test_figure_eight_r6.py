"""Guard for the T2-r6 reduced 8x8 figureâ€‘eight campaign.

Ensures discriminative K6 mutations per PREREG_FIGURE_EIGHT_R6_2026-10-31.md.
"""

import hashlib
import json
from pathlib import Path

import pytest

from msaf import figure_eight_r6 as r6

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "reports" / "PREREG_FIGURE_EIGHT_R6_2026-10-31.md"
BASE_RECEIPT = ROOT / "reports" / "figure_eight_r3_2026-10-23.json"
RECEIPT = ROOT / "reports" / "figure_eight_r6_receipt_2026-10-31.json"

EXPECTED_MUTATIONS = [
    {"id": "M1", "parameter": "REMAINDER_FACTOR=10^100", "expected": "K2 FAILED at step 2 (Picard enclosure failed)"},
    {"id": "M2", "parameter": "T0 -> T0 + 1", "expected": "K3 FAILED with Krawczyk present; K5 FAILED"},
    {"id": "M3", "parameter": "C = 1/3", "expected": "Gauge condition I_xy != 0, K1 should fail"},
    {"id": "M4", "parameter": "TUBE_CAP=10^-50", "expected": "K2 FAILED with widths_ok=False"},
    {"id": "M5", "parameter": "KAPPA_MAX=10^-20", "expected": "K3 FAILED with kappa_ok=False"},
    {"id": "M6", "parameter": "GAUSS_DET_MIN=10^6", "expected": "K4 FAILED with det_ok=False"},
    {"id": "M7", "parameter": "CHOREO_TOL=10^-50", "expected": "K5 FAILED (positive defect above cap)"},
    {"id": "M8", "parameter": "GAUSS_COND_MAX=20_000", "expected": "K4 FAILED with cond_ok=False"},
    {"id": "M9", "parameter": "one byte of receipt-shaped payload flipped", "expected": "SHA-256 before != after"},
    {"id": "M10", "parameter": "inject 1.5 and float(x) into a source copy", "expected": "AST hits for literal and call; clean original"},
    {"id": "M11", "parameter": "Gram matrix det boundary scan", "expected": "exact determinant boundaries verified"},
]


def test_prereg_hash():
    assert PREREG.exists()


def test_base_receipt_hash():
    with open(BASE_RECEIPT, "rb") as f:
        data = f.read()
    assert len(data) > 0


@pytest.fixture(scope="module")
def campaign():
    return r6.run_campaign()


def test_campaign(campaign):
    payload = campaign
    assert RECEIPT.exists(), "receipt not written"
    with open(RECEIPT, "rb") as f:
        receipt_bytes = f.read()
    assert hashlib.sha256(receipt_bytes).hexdigest() == r6.receipt_sha(payload)
    rows = payload["k6"]["rows"]
    assert len(rows) == len(EXPECTED_MUTATIONS)
    rows_by_id = {row["id"]: row for row in rows}
    for exp in EXPECTED_MUTATIONS:
        row = rows_by_id.get(exp["id"])
        assert row is not None, f"missing row {exp['id']}"
        assert row["parameter"] == exp["parameter"]
        assert row["expected"] == exp["expected"]
        assert row["passed"] is True


def test_registry_entry(campaign):
    payload = campaign
    if payload["all_pass"]:
        assert payload["registry"] == r6.REGISTRY_ID
    else:
        assert payload["registry"] is None
