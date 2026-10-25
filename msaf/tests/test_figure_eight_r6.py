"""Guard for the T2-r6 reduced 8x8 figure‑eight campaign.

Ensures discriminative K6 mutations per PREREG_FIGURE_EIGHT_R6_2026-10-25.md.
"""

import hashlib
import json
from pathlib import Path

import pytest

from msaf import figure_eight_r6 as r6

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "reports" / "PREREG_FIGURE_EIGHT_R6_2026-10-25.md"
BASE_PREREG = ROOT / "reports" / "PREREG_FIGURE_EIGHT_R3_2026-10-23.md"
BASE_RECEIPT = ROOT / "reports" / "figure_eight_r3_2026-10-23.json"
RECEIPT = ROOT / "reports" / "figure_eight_r6_2026-10-25.json"

# Expected hashes (pre‑computed)
EXPECTED_PREREG_SHA = "92b687f5ee6237fd01a0b43374c91cce4ba72898f32bfd3f655925a61e591b6b"
EXPECTED_BASE_MODULE_SHA = "8eddc2bb17647d452e15325397e852e224e1af028f055fa4fe41de94af939ec6"
EXPECTED_BASE_RECEIPT_SHA = "6b0b71e91c9b38a2e8b43e8b2da12dbf2ce273321ffe2c4376e09bbbbdf829c9"

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
]


def test_prereg_hash():
    actual = r6.t1.sha256lf(PREREG)
    assert actual == EXPECTED_PREREG_SHA, f"prereg hash mismatch: {actual}"


def test_base_module_hash():
    actual = r6.t1.sha256lf(Path(r6.r3.__file__))
    assert actual == EXPECTED_BASE_MODULE_SHA, f"base module hash mismatch: {actual}"


def test_base_receipt_hash():
    with open(BASE_RECEIPT, "rb") as f:
        data = f.read()
    assert hashlib.sha256(data).hexdigest() == EXPECTED_BASE_RECEIPT_SHA


def test_campaign():
    payload = r6.run_campaign()
    assert RECEIPT.exists(), "receipt not written"
    with open(RECEIPT, "rb") as f:
        receipt_bytes = f.read()
    assert hashlib.sha256(receipt_bytes).hexdigest() == r6.receipt_sha(payload)
    base = payload["base"]
    for key in ("schema", "receipt", "receipt_sha256lf", "module", "module_sha256lf", "prereg_sha256lf", "all_pass"):
        assert key in base
    rows = payload["k6"]["rows"]
    assert len(rows) == len(EXPECTED_MUTATIONS)
    rows_by_id = {row["id"]: row for row in rows}
    for exp in EXPECTED_MUTATIONS:
        row = rows_by_id.get(exp["id"])
        assert row is not None, f"missing row {exp['id']}"
        assert row["parameter"] == exp["parameter"]
        assert row["expected"] == exp["expected"]
        assert row["passed"] is True


def test_ast_float_forbid():
    source = Path(r6.__file__).read_text(encoding="utf-8")
    hits = r6.r3._ast_hits(source)
    assert hits == []


def test_registry_entry():
    payload = r6.run_campaign()
    if payload["all_pass"]:
        assert payload["registry"] == r6.REGISTRY_ID
    else:
        assert payload["registry"] is None
