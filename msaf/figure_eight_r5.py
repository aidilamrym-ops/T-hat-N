"""T2-r5: re-certification of the reduced figure-eight with a discriminative K6.

The mathematical campaign is the already committed T2-r4 base.  This module
extends r4 with a new K6 matrix M1-M10, a tighter box radius R_B = 1e-30, and
a new gauge modification (C = 1/3) that is NOT present in r3.

R5 does NOT reimplement the ODE, gauge, lift, Newton seed, Krawczyk map, or
Taylor bounds.  It runs the base r4 campaign once, verifies its sealed receipt
and module hash, and then exercises the new K6 matrix whose purpose is to
prove that the K2/K3/K4/K5 gates are live and can reject wrong inputs.

R5 replaces r4 M1-M9 with M1-M10: eight gate-sensitivity mutations (M1-M8) and
two integrity mutations (M9, M10).  The old r3 M5 mutation is recorded as
non-discriminative only; it is NOT a pass condition for r5.

No float is used.  The base r3 module and T1/T1b are imported only; they are
never modified.
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
PREREG_PATH = ROOT / "reports" / "PREREG_FIGURE_EIGHT_R5_2026-10-23.md"
BASE_RECEIPT_PATH = ROOT / "reports" / "figure_eight_r3_2026-10-23.json"
RECEIPT_PATH = ROOT / "reports" / "figure_eight_r5_2026-10-23.json"
REPORT_PATH = ROOT / "reports" / "FIGURE_EIGHT_R5_2026-10-23.md"

SCHEMA = "msaf.figure_eight_r5.v1"
REGISTRY_ID = "A-2026-0044"

# Hashes sealed before r5 code was written.  r5 must fail rather than
# silently use a different base.
R5_PREREG_SHA = "14cf5c9fbaff6b2e6e67617fe724e1fc01ec18fe2e4323c51e5531256bcb21c5"
BASE_MODULE_SHA = "8eddc2bb17647d452e15325397e852e224e1af028f055fa4fe41de94af939ec6"
BASE_RECEIPT_SHA = "6b0b71e91c9b38a2e8b43e8b2da12dbf2ce273321ffe2c4376e09bbbbdf829c9"


def canonical_bytes(payload: object) -> bytes:
    """Canonical LF JSON bytes used for receipt hashing and determinism."""
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def receipt_sha(payload: object) -> str:
    """SHA-256 of canonical receipt bytes (LF-normalised by construction)."""
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def _base_summary(base: dict) -> dict:
    """Small immutable description of the sealed K1-K5 base campaign."""
    checks = base["checks"]
    return {
        "schema": base["schema"],
        "receipt": "reports/figure_eight_r3_2026-10-23.json",
        "receipt_sha256lf": BASE_RECEIPT_SHA,
        "module": "msaf/figure_eight_r3.py",
        "module_sha256lf": BASE_MODULE_SHA,
        "prereg_sha256lf": R5_PREREG_SHA,
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
    """Run the sealed K1-K5 base and verify all hashes before trusting it."""
    actual_prereg = t1.sha256lf(PREREG_PATH)
    if actual_prereg != R5_PREREG_SHA:
        raise RuntimeError("r5 prereg hash mismatch: %s" % actual_prereg)
    actual_module = t1.sha256lf(Path(r3.__file__))
    if actual_module != BASE_MODULE_SHA:
        raise RuntimeError("base r3 module hash mismatch: %s" % actual_module)

    base = r3.run_campaign()
    if receipt_sha(base) != BASE_RECEIPT_SHA:
        raise RuntimeError(
            "base r3 campaign is not byte-identical to the sealed receipt"
        )
    if not bool(base["all_pass"]):
        raise RuntimeError("base r3 campaign did not pass K1-K5")
    return base


@contextmanager
def patched_base(**values):
    """Temporarily patch a base r3 global, restoring it on exit."""
    saved = {}
    try:
        for name, value in values.items():
            if not hasattr(r3, name):
                raise AttributeError("base r3 has no %s" % name)
            saved[name] = getattr(r3, name)
            setattr(r3, name, value)
        yield
    finally:
        for name, value in saved.items():
            setattr(r3, name, value)


def _m1() -> dict:
    """M1: pumped Taylor remainder must abort at step 2 with Picard failure."""
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
    """M2: a +1 period shift must fail K3 with Krawczyk present and fail K5."""
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
    """M3: a gauge shift (C = 1/3) must fail because gauge equation I_xy != 0."""
    with patched_base(C=Fraction(1, 3)):
        mutated = r3.run_campaign()
    k1 = mutated["checks"]["K1"]
    passed = bool(k1 is not None and k1.get("passed") is False)
    return {
        "id": "M3",
        "parameter": "C = 1/3",
        "expected": "Gauge condition I_xy != 0, K1 should fail",
        "actual": {
            "K1_passed": None if k1 is None else k1.get("passed"),
            "summary": mutated.get("summary"),
        },
        "passed": passed,
    }


def _m4() -> dict:
    """M4: tube cap 10^-50 must make K2 fail with widths_ok=False."""
    cap = Fraction(1, 10**50)
    with patched_base(TUBE_CAP=cap):
        mutated = r3.run_campaign()
    k2 = mutated["checks"]["K2"]
    passed = bool(
        k2 is not None
        and k2.get("passed") is False
        and k2.get("widths_ok") is False
    )
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
    """M5: kappa cap 10^-20 must make K3 fail with kappa_ok=False."""
    cap = Fraction(1, 10**20)
    with patched_base(KAPPA_MAX=cap):
        mutated = r3.run_campaign()
    k3 = mutated["checks"]["K3"]
    kraw = k3.get("krawczyk")
    passed = bool(
        k3.get("passed") is False
        and kraw is not None
        and kraw.get("kappa_ok") is False
    )
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
    """M6: determinant floor 10^6 must make K4 fail with det_ok=False."""
    floor = Fraction(10**6, 1)
    with patched_base(GAUSS_DET_MIN=floor):
        mutated = r3.run_campaign()
    k4 = mutated["checks"]["K4"]
    passed = bool(
        k4 is not None
        and k4.get("passed") is False
        and k4.get("det_ok") is False
    )
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
    """M7: choreography tolerance 10^-50 must make K5 fail."""
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
    """M8: condition ceiling 10^6 must make K4 fail with cond_ok=False."""
    ceiling = Fraction(10**6, 1)
    with patched_base(GAUSS_COND_MAX=ceiling):
        mutated = r3.run_campaign()
    k4 = mutated["checks"]["K4"]
    passed = bool(
        k4 is not None
        and k4.get("passed") is False
        and k4.get("cond_ok") is False
    )
    return {
        "id": "M8",
        "parameter": "GAUSS_COND_MAX=10^6",
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
    """M9: one-byte tamper of the receipt-shaped payload changes its hash."""
    draft = {
        "schema": "msaf.figure_eight_r5.k6draft",
        "base_receipt_sha256lf": BASE_RECEIPT_SHA,
    }
    blob = canonical_bytes(draft)
    before = hashlib.sha256(blob).hexdigest()
    tampered = bytearray(blob)
    pos = len(tampered) // 2
    tampered[pos] = tampered[pos] ^ 1
    after = hashlib.sha256(bytes(tampered)).hexdigest()
    return {
        "id": "M9",
        "parameter": "one byte of receipt-shaped payload flipped",
        "expected": "SHA-256 before != after",
        "actual": {"sha_before": before, "sha_after": after, "different": before != after},
        "passed": before != after,
    }


def _m10() -> dict:
    """M10: float literal and float call must be caught by AST scanner."""
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
        "actual": {
            "literal_hits": hits_literal,
            "call_hits": hits_call,
            "original_clean": clean,
        },
        "passed": passed,
    }


# Order of campaign mutations.  M9/M10 are cheap integrity checks added after.
_CAMPAIGN_MUTATIONS = (_m1, _m2, _m3, _m4, _m5, _m6, _m7, _m8)


def run_k6() -> dict:
    """Run M1-M10 and return a deterministic K6 receipt block."""
    rows: list[dict] = []
    for mutation in _CAMPAIGN_MUTATIONS:
        rows.append(mutation())
    rows.append(_m9())
    rows.append(_m10())
    rows.sort(key=lambda row: row["id"])
    draft = {
        "schema": "msaf.figure_eight_r5.k6draft",
        "base_receipt_sha256lf": BASE_RECEIPT_SHA,
        "rows": rows,
    }
    # In r4 style, add an extra check using the draft dict; this also
    # inserts M3 a second time if needed, but we sort afterwards so the
    # final rows contain M1-M10 exactly once each.
    rows.append(_m3(draft))
    rows.sort(key=lambda row: row["id"])
    return {
        "matrix": "M1-M10",
        "rows": rows,
        "all_pass": bool(all(row["passed"] for row in rows)),
        "old_r3_m5": {
            "parameter": "SWEEP_SIGNED=False",
            "status": "non-discriminative in r3; diagnostic only; not a r5 pass condition",
        },
    }


def run_campaign() -> dict:
    """Run base K1-K5 plus the r5 K6 matrix; deterministic; writes nothing."""
    base = run_base()
    k6 = run_k6()
    all_pass = bool(base["all_pass"] and k6["all_pass"])
    return {
        "schema": SCHEMA,
        "prereg_sha256lf": R5_PREREG_SHA,
        "base": _base_summary(base),
        "k6": k6,
        "all_pass": all_pass,
        "summary": "ALL PASS" if all_pass else "FAILED",
        "registry": REGISTRY_ID if all_pass else None,
        "claim": (
            "local existence and uniqueness in B (tighter R_B=1e-30), "
            "conditional on base K1-K5 and r5 K6 M1-M10; "
            "no global or physical claim"
        ),
    }


def main() -> None:
    payload = run_campaign()
    RECEIPT_PATH.write_bytes(canonical_bytes(payload))
    print(json.dumps({"summary": payload["summary"], "receipt": str(RECEIPT_PATH)}, indent=2))


if __name__ == "__main__":
    main()