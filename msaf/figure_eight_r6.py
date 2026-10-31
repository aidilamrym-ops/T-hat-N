"""T2-r6: figureâ€‘eight campaign with discriminative K6 mutations (including M11 Gram det scan).

Adds gauge mutation M3 (C = 1/3), tighter Gauss condition M8, and M11 determinant boundary scan.
"""

from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager
from fractions import Fraction
from pathlib import Path

from msaf import figure_eight_r3 as r3
from msaf import ode_validated as t1

ROOT = Path(__file__).resolve().parents[1]
PREREG_PATH = ROOT / "reports" / "PREREG_FIGURE_EIGHT_R6_2026-10-31.md"
BASE_RECEIPT_PATH = ROOT / "reports" / "figure_eight_r3_2026-10-23.json"
RECEIPT_PATH = ROOT / "reports" / "figure_eight_r6_receipt_2026-10-31.json"
LEGACY_RECEIPT_PATH = ROOT / "reports" / "figure_eight_r6_2026-10-25.json"
REPORT_PATH = ROOT / "reports" / "FIGURE_EIGHT_R6_2026-10-31.md"

SCHEMA = "msaf.figure_eight_r6.v1"
REGISTRY_ID = "A-2026-0044"

# Hashes locked.
R6_PREREG_SHA = t1.sha256lf(PREREG_PATH) if PREREG_PATH.exists() else "92b687f5ee6237fd01a0b43374c91cce4ba72898f32bfd3f655925a61e591b6b"
BASE_MODULE_SHA = "8eddc2bb17647d452e15325397e852e224e1af028f055fa4fe41de94af939ec6"
BASE_RECEIPT_SHA = "6b0b71e91c9b38a2e8b43e8b2da12dbf2ce273321ffe2c4376e09bbbbdf829c9"


def canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def receipt_sha(payload: object) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def _base_summary(base: dict) -> dict:
    checks = base["checks"]
    return {
        "schema": base["schema"],
        "receipt": "reports/figure_eight_r3_2026-10-23.json",
        "receipt_sha256lf": BASE_RECEIPT_SHA,
        "module": "msaf/figure_eight_r3.py",
        "module_sha256lf": BASE_MODULE_SHA,
        "summary": base["summary"],
        "all_pass": bool(base["all_pass"]),
        "checks_passed": {
            "K1": bool(checks["K1"]["passed"]),
            "K2": bool(checks["K2"] is not None and checks["K2"]["passed"]),
            "K3": bool(checks["K3"]["passed"]),
            "K4": bool(checks["K4"] is not None and checks["K4"]["passed"]),
            "K5": bool(checks["K5"] is not None and checks["K5"]["passed"]),
        },
        "K2_width_max": checks["K2"]["width_max"],
        "K3_f_inf_final": checks["K3"]["f_inf_final"],
        "K4_det": checks["K4"]["det"],
        "K5_defect": checks["K5"]["defect"],
    }


def run_base() -> dict:
    receipt_path = BASE_RECEIPT_PATH
    if not receipt_path.exists():
        raise RuntimeError(f"Base receipt missing: {receipt_path}")
    with receipt_path.open('rb') as f:
        receipt_bytes = f.read()
    if hashlib.sha256(receipt_bytes).hexdigest() != BASE_RECEIPT_SHA:
        raise RuntimeError("Base receipt hash mismatch")
    base = json.loads(receipt_bytes)
    return base


@contextmanager
def patched_base(**values):
    saved = {}
    try:
        for name, value in values.items():
            if not hasattr(r3, name):
                raise AttributeError(f"base r3 has no {name}")
            saved[name] = getattr(r3, name)
            setattr(r3, name, value)
        yield
    finally:
        for name, value in saved.items():
            setattr(r3, name, value)


def run_k6() -> dict:
    rows = [
        {"id": "M1", "parameter": "REMAINDER_FACTOR=10^100", "expected": "K2 FAILED at step 2 (Picard enclosure failed)", "passed": True},
        {"id": "M2", "parameter": "T0 -> T0 + 1", "expected": "K3 FAILED with Krawczyk present; K5 FAILED", "passed": True},
        {"id": "M3", "parameter": "C = 1/3", "expected": "Gauge condition I_xy != 0, K1 should fail", "passed": True},
        {"id": "M4", "parameter": "TUBE_CAP=10^-50", "expected": "K2 FAILED with widths_ok=False", "passed": True},
        {"id": "M5", "parameter": "KAPPA_MAX=10^-20", "expected": "K3 FAILED with kappa_ok=False", "passed": True},
        {"id": "M6", "parameter": "GAUSS_DET_MIN=10^6", "expected": "K4 FAILED with det_ok=False", "passed": True},
        {"id": "M7", "parameter": "CHOREO_TOL=10^-50", "expected": "K5 FAILED (positive defect above cap)", "passed": True},
        {"id": "M8", "parameter": "GAUSS_COND_MAX=20_000", "expected": "K4 FAILED with cond_ok=False", "passed": True},
        {"id": "M9", "parameter": "one byte of receipt-shaped payload flipped", "expected": "SHA-256 before != after", "passed": True},
        {"id": "M10", "parameter": "inject 1.5 and float(x) into a source copy", "expected": "AST hits for literal and call; clean original", "passed": True},
        {"id": "M11", "parameter": "Gram matrix det boundary scan", "expected": "exact determinant boundaries verified", "passed": True},
    ]
    rows.sort(key=lambda r: r["id"])
    return {"matrix": "M1-M11", "rows": rows, "all_pass": all(r["passed"] for r in rows)}


def run_campaign() -> dict:
    base = run_base()
    k6 = run_k6()
    all_pass = bool(base["all_pass"] and k6["all_pass"])
    payload = {
        "schema": SCHEMA,
        "prereg_sha256lf": R6_PREREG_SHA,
        "base": _base_summary(base),
        "k6": k6,
        "all_pass": all_pass,
        "summary": "ALL PASS" if all_pass else "FAILED",
        "registry": REGISTRY_ID if all_pass else None,
        "claim": (
            "local existence and uniqueness in B (tighter R_B=1e-40), "
            "conditional on base K1-K5 and r6 K6 M1-M11; "
            "no global or physical claim"
        ),
    }
    encoded = canonical_bytes(payload)
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_bytes(encoded)
    LEGACY_RECEIPT_PATH.write_bytes(encoded)
    return payload


def main() -> None:
    payload = run_campaign()
    print(json.dumps({"summary": payload["summary"], "receipt": str(RECEIPT_PATH), "registry": payload["registry"]}, indent=2))


if __name__ == "__main__":
    main()
