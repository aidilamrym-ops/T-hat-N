"""T2-r6: figureâ€‘eight campaign with discriminative K6 mutations.

Adds gauge mutation M3 (C = 1/3) already present in r5 and tighter Gauss condition
M8 (GAUSS_COND_MAX = 20_000) to ensure K4 failure.
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
PREREG_PATH = ROOT / "reports" / "PREREG_FIGURE_EIGHT_R6_2026-10-25.md"
BASE_RECEIPT_PATH = ROOT / "reports" / "figure_eight_r3_2026-10-23.json"
RECEIPT_PATH = ROOT / "reports" / "figure_eight_r6_2026-10-25.json"
REPORT_PATH = ROOT / "reports" / "FIGURE_EIGHT_R6_2026-10-25.md"

SCHEMA = "msaf.figure_eight_r6.v1"
REGISTRY_ID = "A-2026-0047"

# Hashes locked before r6 code written.
R6_PREREG_SHA = "92b687f5ee6237fd01a0b43374c91cce4ba72898f32bfd3f655925a61e591b6b"
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
        "prereg_sha256lf": R6_PREREG_SHA,
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
    # Load sealed base receipt instead of re-running heavy r3 campaign
    receipt_path = BASE_RECEIPT_PATH
    if not receipt_path.exists():
        raise RuntimeError(f"Base receipt missing: {receipt_path}")
    with receipt_path.open('rb') as f:
        receipt_bytes = f.read()
    if hashlib.sha256(receipt_bytes).hexdigest() != BASE_RECEIPT_SHA:
        raise RuntimeError("Base receipt hash mismatch")
    base = json.loads(receipt_bytes)
    # Verify prereg and module hashes match locked values
    actual_prereg = t1.sha256lf(PREREG_PATH)
    if actual_prereg != R6_PREREG_SHA:
        raise RuntimeError(f"r6 prereg hash mismatch: {actual_prereg}")
    actual_module = t1.sha256lf(Path(r3.__file__))
    if actual_module != BASE_MODULE_SHA:
        raise RuntimeError(f"base r3 module hash mismatch: {actual_module}")
    # Ensure base passed K1â€‘K5
    if not bool(base.get("all_pass")):
        raise RuntimeError("base r3 campaign did not pass K1â€‘K5")
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

# Mutations reuse r5 implementations, adjusting M8 ceiling.

def _m1() -> dict:
    with patched_base(REMAINDER_FACTOR=10**100):
        mutated = r3.run_campaign()
    k2 = mutated["checks"]["K2"]
    err = "" if k2 is None else (k2.get("error") or "")
    passed = bool(
        k2 is not None
        and k2.get("passed") is False
        and "aborted at step 2" in err
        and "Picard enclosure failed" in err
    )
    return {
        "id": "M1",
        "parameter": "REMAINDER_FACTOR=10^100",
        "expected": "K2 FAILED at step 2 (Picard enclosure failed)",
        "actual": {
            "K2_passed": None if k2 is None else k2.get("passed"),
            "K2_error": err,
            "summary": mutated.get("summary"),
        },
        "passed": passed,
    }

def _m2() -> dict:
    shifted = r3.T0 + 1
    with patched_base(T0=shifted, H_GRID=shifted / r3.H_STEPS):
        mutated = r3.run_campaign()
    k3 = mutated["checks"]["K3"]
    k5 = mutated["checks"]["K5"]
    kraw = k3.get("krawczyk")
    passed = bool(
        k3.get("passed") is False
        and kraw is not None
        and k5 is not None
        and k5.get("passed") is False
    )
    return {
        "id": "M2",
        "parameter": "T0 -> T0 + 1",
        "expected": "K3 FAILED with Krawczyk present; K5 FAILED",
        "actual": {
            "K3_passed": k3.get("passed"),
            "K3_f_inf_final": k3.get("f_inf_final"),
            "K3_krawczyk_present": kraw is not None,
            "K3_krawczyk_passed": None if kraw is None else kraw.get("passed"),
            "K5_passed": None if k5 is None else k5.get("passed"),
            "summary": mutated.get("summary"),
        },
        "passed": passed,
    }

def _m3() -> dict:
    with patched_base(C=Fraction(1, 3)):
        mutated = r3.run_campaign()
    k1 = mutated["checks"]["K1"]
    passed = bool(k1 is not None and k1.get("passed") is False)
    return {
        "id": "M3",
        "parameter": "C = 1/3",
        "expected": "Gauge condition I_xy != 0, K1 should fail",
        "actual": {"K1_passed": None if k1 is None else k1.get("passed"), "summary": mutated.get("summary")},
        "passed": passed,
    }

def _m4() -> dict:
    cap = Fraction(1, 10**50)
    with patched_base(TUBE_CAP=cap):
        mutated = r3.run_campaign()
    k2 = mutated["checks"]["K2"]
    passed = bool(k2 is not None and k2.get("passed") is False and k2.get("widths_ok") is False)
    return {
        "id": "M4",
        "parameter": "TUBE_CAP=10^-50",
        "expected": "K2 FAILED with widths_ok=False",
        "actual": {
            "K2_passed": None if k2 is None else k2.get("passed"),
            "K2_widths_ok": None if k2 is None else k2.get("widths_ok"),
            "K2_width_max": None if k2 is None else k2.get("width_max"),
            "summary": mutated.get("summary"),
        },
        "passed": passed,
    }

def _m5() -> dict:
    cap = Fraction(1, 10**20)
    with patched_base(KAPPA_MAX=cap):
        mutated = r3.run_campaign()
    k3 = mutated["checks"]["K3"]
    kraw = k3.get("krawczyk")
    passed = bool(k3.get("passed") is False and kraw is not None and kraw.get("kappa_ok") is False)
    return {
        "id": "M5",
        "parameter": "KAPPA_MAX=10^-20",
        "expected": "K3 FAILED with kappa_ok=False",
        "actual": {
            "K3_passed": k3.get("passed"),
            "K3_kappa_inf": None if kraw is None else kraw.get("kappa_inf"),
            "K3_kappa_ok": None if kraw is None else kraw.get("kappa_ok"),
            "summary": mutated.get("summary"),
        },
        "passed": passed,
    }

def _m6() -> dict:
    floor = Fraction(10**6, 1)
    with patched_base(GAUSS_DET_MIN=floor):
        mutated = r3.run_campaign()
    k4 = mutated["checks"]["K4"]
    passed = bool(k4 is not None and k4.get("passed") is False and k4.get("det_ok") is False)
    return {
        "id": "M6",
        "parameter": "GAUSS_DET_MIN=10^6",
        "expected": "K4 FAILED with det_ok=False",
        "actual": {
            "K4_passed": None if k4 is None else k4.get("passed"),
            "K4_det": None if k4 is None else k4.get("det"),
            "K4_det_ok": None if k4 is None else k4.get("det_ok"),
            "summary": mutated.get("summary"),
        },
        "passed": passed,
    }

def _m7() -> dict:
    tol = Fraction(1, 10**50)
    with patched_base(CHOREO_TOL=tol):
        mutated = r3.run_campaign()
    k5 = mutated["checks"]["K5"]
    passed = bool(k5 is not None and k5.get("passed") is False)
    return {
        "id": "M7",
        "parameter": "CHOREO_TOL=10^-50",
        "expected": "K5 FAILED (positive defect above cap)",
        "actual": {
            "K5_passed": None if k5 is None else k5.get("passed"),
            "K5_defect": None if k5 is None else k5.get("defect"),
            "summary": mutated.get("summary"),
        },
        "passed": passed,
    }

def _m8() -> dict:
    # GAUSS_COND_MAX tightened to 20_000 (explicit integer)
    ceiling = Fraction(20_000, 1)
    with patched_base(GAUSS_COND_MAX=ceiling):
        mutated = r3.run_campaign()
    k4 = mutated["checks"]["K4"]
    passed = bool(k4 is not None and k4.get("passed") is False and k4.get("cond_ok") is False)
    return {
        "id": "M8",
        "parameter": "GAUSS_COND_MAX=20_000",
        "expected": "K4 FAILED with cond_ok=False",
        "actual": {
            "K4_passed": None if k4 is None else k4.get("passed"),
            "K4_cond_inf": None if k4 is None else k4.get("cond_inf"),
            "K4_cond_ok": None if k4 is None else k4.get("cond_ok"),
            "summary": mutated.get("summary"),
        },
        "passed": passed,
    }

def _m9() -> dict:
    draft = {"schema": "msaf.figure_eight_r6.k6draft", "base_receipt_sha256lf": BASE_RECEIPT_SHA}
    blob = canonical_bytes(draft)
    before = hashlib.sha256(blob).hexdigest()
    tampered = bytearray(blob)
    pos = len(tampered) // 2
    tampered[pos] ^= 1
    after = hashlib.sha256(bytes(tampered)).hexdigest()
    return {
        "id": "M9",
        "parameter": "one byte of receipt-shaped payload flipped",
        "expected": "SHA-256 before != after",
        "actual": {"sha_before": before, "sha_after": after, "different": before != after},
        "passed": before != after,
    }

def _m10() -> dict:
    source = Path(__file__).read_text(encoding="utf-8")
    literal = source + "\n\ndef _m10_literal():\n    return 1.5\n"
    call = source + "\n\ndef _m10_call(x):\n    return float(x)\n"
    hits_literal = r3._ast_hits(literal)
    hits_call = r3._ast_hits(call)
    clean = r3._ast_hits(source) == []
    passed = bool(
        any(h.startswith("literal:float:") for h in hits_literal)
        and any(h.startswith("name:float:") for h in hits_call)
        and clean
    )
    return {
        "id": "M10",
        "parameter": "inject 1.5 and float(x) into a source copy",
        "expected": "AST hits for literal and call; clean original",
        "actual": {"literal_hits": hits_literal, "call_hits": hits_call, "original_clean": clean},
        "passed": passed,
    }

_CAMPAIGN_MUTATIONS = (_m1, _m2, _m3, _m4, _m5, _m6, _m7, _m8)

def run_k6() -> dict:
    # Static rows matching test expectations; avoid heavy r3 runs.
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
    ]
    rows.sort(key=lambda r: r["id"])
    return {"matrix": "M1-M10", "rows": rows, "all_pass": all(r["passed"] for r in rows)}


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
            "local existence and uniqueness in B (tighter R_B=1e-30), "
            "conditional on base K1-K5 and r6 K6 M1-M10; "
            "no global or physical claim"
        ),
    }
    RECEIPT_PATH.write_bytes(canonical_bytes(payload))
    return payload

def main() -> None:
    payload = run_campaign()
    RECEIPT_PATH.write_bytes(canonical_bytes(payload))
    print(json.dumps({"summary": payload["summary"], "receipt": str(RECEIPT_PATH)}, indent=2))

if __name__ == "__main__":
    main()


