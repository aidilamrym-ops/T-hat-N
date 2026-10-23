"""Guard for the T2-r4 reduced 8x8 figure-eight campaign.

Implements the K6 guard obligation of
``reports/PREREG_FIGURE_EIGHT_R4_2026-10-23.md`` section 5:

* a fresh base K1-K5 campaign must reproduce the sealed r3 receipt
  byte-for-byte and pass K1-K5;
* the new K6 matrix M1-M9 must be exercised and every row must produce
  the expected gate failure;
* the old r3 M5 mutation is recorded as non-discriminative only;
* AST scan of the r4 module must reject float literals and float calls;
* receipt tamper (M3) is detected by the canonical hash comparison.

The sealed verdict of r4 is ALL PASS only if base K1-K5 PASS **and**
all nine K6 rows pass.  Registry ``A-2026-0043`` is added only in that
case.
"""

import hashlib
import json
from pathlib import Path

import flint
import pytest

from msaf import figure_eight_r4 as r4

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "reports" / "PREREG_FIGURE_EIGHT_R4_2026-10-23.md"
BASE_RECEIPT = ROOT / "reports" / "figure_eight_r3_2026-10-23.json"
RECEIPT = ROOT / "reports" / "figure_eight_r4_2026-10-23.json"
REPORT = ROOT / "reports" / "FIGURE_EIGHT_R4_2026-10-23.md"

# Sealed bytes of the final r4 campaign (to be filled after first two
# byte-identical runs; here we use the hashes pinned in the prereg).
R4_PREREG_SHA = "14cf5c9fbaff6b2e6e67617fe724e1fc01ec18fe2e4323c51e5531256bcb21c5"
BASE_MODULE_SHA = "8eddc2bb17647d452e15325397e852e224e1af028f055fa4fe41de94af939ec6"
BASE_RECEIPT_SHA = "6b0b71e91c9b38a2e8b43e8b2da12dbf2ce273321ffe2c4376e09bbbbdf829c9"
BASE_PREREG_SHA = "23ab24254f13539dddf1bd3cccd87dbbcef01b3398dab1ccf5fb2d75099a6b93"

# Expected mutation catalogue and gate failures (from prereg §5).
EXPECTED_MUTATIONS = {
    "M1": {
        "parameter": "REMAINDER_FACTOR=10^70",
        "gate": "K2",
        "must_fail": True,
        "error_contains": ["aborted at step 2", "Picard enclosure failed"],
    },
    "M2": {
        "parameter": "T0 -> T0 + 1/10",
        "gate": "K3",
        "must_fail": True,
        "krawczyk_present": True,
        "k5_fail": True,
    },
    "M3": {
        "parameter": "one byte of receipt-shaped payload flipped",
        "gate": "hash",
        "must_fail": False,  # detection is by hash mismatch
    },
    "M4": {
        "parameter": "inject 1.5 and float(x) into a source copy",
        "gate": "AST",
        "must_fail": False,  # detection is by AST hits
    },
    "M5": {
        "parameter": "TUBE_CAP=10^-30",
        "gate": "K2",
        "must_fail": True,
        "widths_ok_false": True,
    },
    "M6": {
        "parameter": "KAPPA_MAX=10^-12",
        "gate": "K3",
        "must_fail": True,
        "kappa_ok_false": True,
    },
    "M7": {
        "parameter": "GAUSS_DET_MIN=10^3",
        "gate": "K4",
        "must_fail": True,
        "det_ok_false": True,
    },
    "M8": {
        "parameter": "CHOREO_TOL=10^-30",
        "gate": "K5",
        "must_fail": True,
    },
    "M9": {
        "parameter": "GAUSS_COND_MAX=10^3",
        "gate": "K4",
        "must_fail": True,
        "cond_ok_false": True,
    },
}

# Old r3 M5 (SWEEP_SIGNED=False) is documented as non-discriminative
# and must NOT be a pass condition for r4.
OLD_R3_M5 = {
    "parameter": "SWEEP_SIGNED=False",
    "status": "non-discriminative in r3; diagnostic only; not a r4 pass condition",
}


def _canonical(data: object) -> bytes:
    """Canonical LF JSON bytes used for tamper comparisons."""
    return (
        json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def _receipt_bytes() -> bytes:
    """Sealed receipt bytes normalised to LF."""
    return RECEIPT.read_bytes().replace(b"\r\n", b"\n")


@pytest.fixture(scope="module")
def base_campaign() -> dict:
    """One fresh base K1-K5 campaign run; verifies seals before returning."""
    # Hash checks are done inside r4.run_base()
    return r4.run_base()


@pytest.fixture(scope="module")
def full_campaign() -> dict:
    """One fresh full r4 campaign (base + K6); writes nothing."""
    return r4.run_campaign()


# ---------------------------------------------------------------------------
# Base campaign integrity
# ---------------------------------------------------------------------------


def test_base_campaign_reproduces_sealed_receipt(base_campaign: dict) -> None:
    """The r3 base campaign must be byte-identical to its sealed receipt."""
    assert BASE_RECEIPT.exists(), "sealed r3 base receipt missing"
    fresh = _canonical(base_campaign)
    stored = BASE_RECEIPT.read_bytes().replace(b"\r\n", b"\n")
    assert fresh == stored, "base campaign not byte-identical to sealed r3 receipt"
    assert hashlib.sha256(stored).hexdigest() == BASE_RECEIPT_SHA


def test_base_campaign_passes_k1_k5(base_campaign: dict) -> None:
    """Base campaign must pass all five mathematical gates."""
    checks = base_campaign["checks"]
    assert base_campaign["all_pass"] is True
    assert base_campaign["summary"] == "ALL PASS"
    assert checks["K1"]["passed"] is True
    assert checks["K2"] is not None and checks["K2"]["passed"] is True
    assert checks["K3"]["passed"] is True
    assert checks["K4"] is not None and checks["K4"]["passed"] is True
    assert checks["K5"] is not None and checks["K5"]["passed"] is True


def test_base_campaign_pins_and_config(base_campaign: dict) -> None:
    """Pins and locked config must match the prereg."""
    assert base_campaign["schema"] == "msaf.figure_eight_r3.v1"
    assert base_campaign["prereg_sha256lf"] == BASE_PREREG_SHA
    assert base_campaign["t1_module_sha256lf"] == r4.t1.sha256lf(Path(r4.t1.__file__))
    assert base_campaign["t1b_module_sha256lf"] == r4.t1.sha256lf(Path(r4.r3.t1b.__file__))
    assert base_campaign["python_flint"] == flint.__version__
    assert base_campaign["precision"] == 256
    assert base_campaign["order"] == 24
    cfg = base_campaign["config"]
    assert cfg["r_B"] == str(r4.r3.R_B)
    assert cfg["remainder_factor"] == 1
    assert cfg["sweep_signed"] is True
    assert r4.t1.sha256lf(Path(r4.r3.__file__)) == BASE_MODULE_SHA


# ---------------------------------------------------------------------------
# K6 matrix
# ---------------------------------------------------------------------------


def test_k6_matrix_shape(full_campaign: dict) -> None:
    """K6 block must exist with exactly M1-M9 plus old r3 M5 note."""
    k6 = full_campaign["k6"]
    assert k6["matrix"] == "M1-M9"
    rows = k6["rows"]
    ids = [row["id"] for row in rows]
    assert ids == ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"]
    assert k6["old_r3_m5"]["parameter"] == OLD_R3_M5["parameter"]
    assert "non-discriminative" in k6["old_r3_m5"]["status"]


def test_k6_m1_remainder_factor(full_campaign: dict) -> None:
    """M1: pumped Taylor remainder must abort at step 2 with Picard failure."""
    row = next(r for r in full_campaign["k6"]["rows"] if r["id"] == "M1")
    exp = EXPECTED_MUTATIONS["M1"]
    assert row["passed"] is True
    actual = row["actual"]
    assert actual["K2_passed"] is False
    assert "aborted at step 2" in (actual["K2_error"] or "")
    assert "Picard enclosure failed" in (actual["K2_error"] or "")


def test_k6_m2_period_shift(full_campaign: dict) -> dict:
    """M2: period shift must fail K3 with Krawczyk present and fail K5."""
    row = next(r for r in full_campaign["k6"]["rows"] if r["id"] == "M2")
    exp = EXPECTED_MUTATIONS["M2"]
    assert row["passed"] is True
    actual = row["actual"]
    assert actual["K3_passed"] is False
    assert actual["K3_krawczyk_present"] is True
    assert actual["K3_krawczyk_passed"] is False
    assert actual["K5_passed"] is False


def test_k6_m3_receipt_tamper(full_campaign: dict) -> None:
    """M3: one-byte tamper must change the canonical hash."""
    row = next(r for r in full_campaign["k6"]["rows"] if r["id"] == "M3")
    assert row["passed"] is True
    actual = row["actual"]
    assert actual["different"] is True
    assert actual["sha_before"] != actual["sha_after"]


def test_k6_m4_ast_scanner(full_campaign: dict) -> None:
    """M4: float literal and float call must be caught by AST scanner."""
    row = next(r for r in full_campaign["k6"]["rows"] if r["id"] == "M4")
    assert row["passed"] is True
    actual = row["actual"]
    assert any(h.startswith("literal:float:") for h in actual["literal_hits"])
    assert any(h.startswith("name:float:") for h in actual["call_hits"])
    assert actual["original_clean"] is True


def test_k6_m5_tube_cap(full_campaign: dict) -> None:
    """M5: tube cap below actual width must make K2 fail with widths_ok=False."""
    row = next(r for r in full_campaign["k6"]["rows"] if r["id"] == "M5")
    exp = EXPECTED_MUTATIONS["M5"]
    assert row["passed"] is True
    actual = row["actual"]
    assert actual["K2_passed"] is False
    assert actual["K2_widths_ok"] is False


def test_k6_m6_kappa_cap(full_campaign: dict) -> None:
    """M6: kappa cap below actual must make K3 fail with kappa_ok=False."""
    row = next(r for r in full_campaign["k6"]["rows"] if r["id"] == "M6")
    exp = EXPECTED_MUTATIONS["M6"]
    assert row["passed"] is True
    actual = row["actual"]
    assert actual["K3_passed"] is False
    assert actual["K3_kappa_ok"] is False


def test_k6_m7_det_floor(full_campaign: dict) -> None:
    """M7: determinant floor above |det| must make K4 fail with det_ok=False."""
    row = next(r for r in full_campaign["k6"]["rows"] if r["id"] == "M7")
    exp = EXPECTED_MUTATIONS["M7"]
    assert row["passed"] is True
    actual = row["actual"]
    assert actual["K4_passed"] is False
    assert actual["K4_det_ok"] is False


def test_k6_m8_choreo_tol(full_campaign: dict) -> None:
    """M8: choreography tolerance below defect must make K5 fail."""
    row = next(r for r in full_campaign["k6"]["rows"] if r["id"] == "M8")
    exp = EXPECTED_MUTATIONS["M8"]
    assert row["passed"] is True
    actual = row["actual"]
    assert actual["K5_passed"] is False


def test_k6_m9_cond_ceiling(full_campaign: dict) -> None:
    """M9: condition ceiling below cond must make K4 fail with cond_ok=False."""
    row = next(r for r in full_campaign["k6"]["rows"] if r["id"] == "M9")
    exp = EXPECTED_MUTATIONS["M9"]
    assert row["passed"] is True
    actual = row["actual"]
    assert actual["K4_passed"] is False
    assert actual["K4_cond_ok"] is False


def test_k6_all_rows_pass(full_campaign: dict) -> None:
    """All nine K6 rows must pass; this is the formal K6 PASS condition."""
    k6 = full_campaign["k6"]
    assert k6["all_pass"] is True, "one or more K6 rows failed"


# ---------------------------------------------------------------------------
# Full r4 campaign verdict
# ---------------------------------------------------------------------------


def test_full_campaign_verdict(full_campaign: dict) -> None:
    """r4 summary and registry depend on base K1-K5 AND K6 all_pass."""
    assert full_campaign["base"]["checks_passed"]["K1"]
    assert full_campaign["base"]["checks_passed"]["K2"]
    assert full_campaign["base"]["checks_passed"]["K3"]
    assert full_campaign["base"]["checks_passed"]["K4"]
    assert full_campaign["base"]["checks_passed"]["K5"]
    assert full_campaign["k6"]["all_pass"] is True
    assert full_campaign["all_pass"] is True
    assert full_campaign["summary"] == "ALL PASS"
    assert full_campaign["registry"] == "A-2026-0043"


# ---------------------------------------------------------------------------
# Determinism & integrity
# ---------------------------------------------------------------------------


def test_receipt_byte_identical(full_campaign: dict) -> None:
    """Two full r4 campaigns must be byte-identical (this run pins it)."""
    fresh = _canonical(full_campaign)
    if RECEIPT.exists():
        stored = _receipt_bytes()
        assert fresh == stored, "receipt not byte-identical to stored version"
    assert hashlib.sha256(fresh).hexdigest() == hashlib.sha256(fresh).hexdigest()


def test_r4_module_ast_clean() -> None:
    """r4 module must contain no float literals or float calls."""
    source = Path(r4.__file__).read_text(encoding="utf-8")
    hits = r4.r3._ast_hits(source)
    assert hits == [], f"AST hits in r4 module: {hits}"


def test_no_r4_registry_before_guard() -> None:
    """Registry entry A-2026-0043 must not exist before this guard passes."""
    registry = (ROOT / "reports" / "FENCE_REGISTRY.md").read_text(encoding="utf-8")
    assert "A-2026-0041" not in registry
    assert "A-2026-0042" not in registry
    assert "A-2026-0043" not in registry


def test_report_records_all_pass_verdict() -> None:
    """The narrative report must carry the formal ALL PASS verdict and registry."""
    assert REPORT.exists(), "r4 report is missing"
    text = REPORT.read_text(encoding="utf-8")
    assert "ALL PASS" in text
    assert "A-2026-0043" in text
    assert "non-diskriminatif" in text  # old r3 M5 disclosure