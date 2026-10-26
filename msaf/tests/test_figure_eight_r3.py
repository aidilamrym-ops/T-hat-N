"""Guard for the T2-r3 reduced 8x8 figure-eight campaign.

Implements the K6 guard obligations of
``reports/PREREG_FIGURE_EIGHT_R3_2026-10-23.md`` section 4:

* a fresh full campaign must reproduce the sealed K1-K5 receipt byte for
  byte;
* the AST scan must reject float literals and float calls;
* M1 (remainder factor), M2 (period shift), M3 (receipt tamper), and M4
  (float injection) are exercised;
* M5 (unsigned reset sweep) is exercised and is recorded as
  **non-discriminative**: it still passes K2/K3 on the tight r3 tube.
  Therefore K6 is not claimed as fully PASS, the formal r3 verdict is
  INCONCLUSIVE, and no registry entry is created.

The mathematical K1-K5 certificate is independent of K6.  This guard pins
only the campaign payload and the actual mutation effects; it does not
redefine thresholds, does not amend the prereg, and makes no global
uniqueness, stability, spectral, or physical claim.
"""

import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import flint
import pytest

from msaf import figure_eight_r3 as b

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "reports" / "PREREG_FIGURE_EIGHT_R3_2026-10-23.md"
RECEIPT = ROOT / "reports" / "figure_eight_r3_2026-10-23.json"
REPORT = ROOT / "reports" / "FIGURE_EIGHT_R3_2026-10-23.md"

# Sealed bytes of the final K1-K5 campaign, produced by two byte-identical
# runs after the path-box soundness correction.
RECEIPT_SHA256 = (
    "6b0b71e91c9b38a2e8b43e8b2da12dbf2ce273321ffe2c4376e09bbbbdf829c9"
)
MODULE_SHA256 = (
    "8eddc2bb17647d452e15325397e852e224e1af028f055fa4fe41de94af939ec6"
)


def _canonical(data: object) -> str:
    """Canonical JSON payload used for tamper comparisons (repo pattern)."""
    return json.dumps(
        data, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def _receipt_bytes() -> bytes:
    """Sealed receipt bytes normalised to LF (repo sha256LF convention)."""
    return RECEIPT.read_bytes().replace(b"\r\n", b"\n")


@pytest.fixture(scope="module")
def campaign() -> dict:
    """One fresh full K1-K5 campaign run; writes nothing to disk."""
    return b.run_campaign()


# ---------------------------------------------------------------------------
# K6(i): fresh campaign must reproduce the sealed K1-K5 receipt byte for byte
# ---------------------------------------------------------------------------


def test_campaign_payload_is_byte_identical_to_receipt(campaign: dict) -> None:
    """A fresh rerun equals the sealed receipt on LF-normalised bytes."""
    assert RECEIPT.exists(), "sealed T2-r3 receipt is missing"
    fresh = (
        json.dumps(campaign, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    )
    stored = _receipt_bytes()
    assert fresh.encode("utf-8") == stored

    receipt = json.loads(stored.decode("utf-8"))
    assert _canonical(campaign) == _canonical(receipt)
    assert hashlib.sha256(stored).hexdigest() == RECEIPT_SHA256


def test_receipt_freezes_hashes_and_k1_k5_certificate(campaign: dict) -> None:
    """The receipt pins the prereg/frozen modules and the K1-K5 result.

    ``summary == "ALL PASS"`` here is the campaign's K1-K5 scope.  It is
    **not** a registry eligibility claim: M5 is non-discriminative, so the
    formal r3 verdict in the report is INCONCLUSIVE.
    """
    assert campaign["schema"] == "msaf.figure_eight_r3.v1"
    assert campaign["prereg_sha256lf"] == b.PREREG_SHA
    assert campaign["t1_module_sha256lf"] == b.T1_MODULE_SHA
    assert campaign["t1b_module_sha256lf"] == b.T1B_MODULE_SHA
    assert campaign["python_flint"] == flint.__version__
    assert campaign["precision"] == 256
    assert campaign["order"] == 24
    assert campaign["config"]["r_B"] == str(b.R_B)
    assert campaign["config"]["remainder_factor"] == 1
    assert campaign["config"]["sweep_signed"] is True
    assert b.t1.sha256lf(Path(b.__file__)) == MODULE_SHA256
    assert b.t1.sha256lf(PREREG) == b.PREREG_SHA

    checks = campaign["checks"]
    assert checks["K1"]["ast_scan_hits"] == []
    assert checks["K1"]["passed"] is True
    assert checks["K2"]["passed"] is True
    assert checks["K2"]["widths_ok"] is True
    assert checks["K2"]["running_ok"] is True
    assert checks["K2"]["quad_ok"] is True
    assert checks["K2"]["dr_ok"] is True
    assert checks["K2"]["width_max"].startswith(
        "[4.375764330275093479072173756299383027704756423307118008194399677529249856e-14"
    )
    assert checks["K2"]["running_radius_max"].startswith(
        "[8.164954245581349658454018570980975810530326533270745959377329243217152681e-14"
    )
    assert checks["K2"]["quad_step"].startswith(
        "[1.89472898237386694193432847013056621902513394442303910879984932024175902466e-19"
    )
    assert checks["K2"]["dr_max"].startswith(
        "[1.114186167976259912261111347941188803136125740982181566395971920697744154081e-42"
    )
    assert checks["K3"]["point_ok"] is True
    assert checks["K3"]["f_inf_final"].startswith(
        "[4.222845715357847910637323998643523507567862899636295014679650259478241866838e-25"
    )
    assert checks["K3"]["box_error"] is None
    assert checks["K3"]["passed"] is True
    assert checks["K3"]["krawczyk"]["passed"] is True
    assert checks["K3"]["krawczyk"]["kappa_ok"] is True
    assert checks["K3"]["krawczyk"]["included"] is True
    assert checks["K3"]["krawczyk"]["kappa_inf"].startswith(
        "[0.0003376789173614763082806101085567345829527377267338976536845222223977244780842"
    )
    assert checks["K3"]["krawczyk"]["w_max"].startswith(
        "[51.92421404453306048520794615189042988529949171436103110337159103612738783770"
    )
    assert checks["K4"]["passed"] is True
    assert checks["K4"]["det_contains_zero"] is False
    assert checks["K4"]["det"].startswith(
        "[-7.62340755583888116663998805"
    )
    assert checks["K4"]["cond_inf"].startswith(
        "[29649.63760391575706697521057457355981231035243000495552906011464528223181393"
    )
    assert checks["K5"]["passed"] is True
    assert checks["K5"]["defect"].startswith(
        "[1.212132602582212128642850918829943957140899920031779056126538927385849407e-14"
    )
    assert campaign["collision_guard"]["strictly_above_half"] is True
    assert campaign["collision_guard"]["min_pair_distance_lower"].startswith(
        "[0.6808134400065059275698514449553289341771577342545415021508429937759583634781"
    )


def test_path_box_is_the_validated_t1b_enclosure() -> None:
    """``_step_with_box`` matches T1b and exposes a path-containing box.

    This is the regression for the withdrawn start-centered Hessian box:
    the local bounds must be evaluated over the validated Picard path box,
    which contains both the step start and the step endpoint.
    """
    with flint.ctx.workprec(b.PREC):
        m0, _ = b._lift_box(b.XHAT_R2, [b.ZERO] * b.N_SEC)
        m = [v.mid() for v in m0]
        c = [b._b(Fraction(1, 10**14))] * b.N_STATE
        frozen = b.t1b.forward_step(
            b.t1.coeffs_three_body,
            b.t1.rhs_three_body,
            m,
            c,
            b._b(b.H_GRID),
            b.ORDER,
            True,
        )
        local = b._step_with_box(
            b.t1.coeffs_three_body,
            b.t1.rhs_three_body,
            m,
            c,
            b._b(b.H_GRID),
            b.ORDER,
            True,
        )
        for i in range(b.N_STATE):
            assert frozen[0][i].mid() == local[0][i].mid()
            assert frozen[0][i].rad() == local[0][i].rad()
            assert frozen[2][i].mid() == local[2][i].mid()
            assert frozen[2][i].rad() == local[2][i].rad()
            for j in range(b.N_STATE):
                assert frozen[1][i][j].mid() == local[1][i][j].mid()
                assert frozen[1][i][j].rad() == local[1][i][j].rad()
            assert local[4][i].contains(m[i])
            assert local[4][i].contains(local[0][i])
        # The path box is much wider than the old 1e-12 start ball; a
        # mutation back to a start-centered box would fail this test's
        # containment premise, not silently tighten the bound.
        assert bool(local[4][0].rad() > b._b(Fraction(1, 10**6)))


# ---------------------------------------------------------------------------
# M1: remainder factor 1e70 must fail the campaign honestly
# ---------------------------------------------------------------------------


def test_m1_remainder_factor_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """M1: factor 1e70 is rejected at the Picard/box gate."""
    monkeypatch.setattr(b, "REMAINDER_FACTOR", 10**70)
    mutated = b.run_campaign()

    assert mutated["summary"] == "FAILED"
    assert mutated["all_pass"] is False
    assert mutated["checks"]["K2"]["passed"] is False
    error = mutated["checks"]["K2"]["error"] or ""
    assert "aborted at step 2" in error, error
    assert "Picard enclosure failed" in error, error
    assert mutated["checks"]["K3"]["passed"] is False
    assert mutated["checks"]["K3"]["krawczyk"] is None
    assert mutated["checks"]["K4"] is None
    assert mutated["checks"]["K5"] is None


# ---------------------------------------------------------------------------
# M2: period shift +1/10 must still fail K3
# ---------------------------------------------------------------------------


def test_m2_period_shift_fails_k3(monkeypatch: pytest.MonkeyPatch) -> None:
    """M2: a +1/10 period shift must not certify (K3 false)."""
    shifted = b.T0 + Fraction(1, 10)
    monkeypatch.setattr(b, "T0", shifted)
    monkeypatch.setattr(b, "H_GRID", shifted / b.H_STEPS)
    mutated = b.run_campaign()

    assert mutated["summary"] == "FAILED"
    assert mutated["all_pass"] is False
    assert mutated["checks"]["K3"]["passed"] is False
    assert mutated["checks"]["K3"]["krawczyk"] is not None
    assert mutated["checks"]["K3"]["krawczyk"]["passed"] is False
    assert mutated["checks"]["K5"]["passed"] is False


# ---------------------------------------------------------------------------
# M3: one-byte receipt tamper must be detected by the payload comparison
# ---------------------------------------------------------------------------


def test_m3_receipt_tamper_detected(campaign: dict) -> None:
    """M3: altering one character of the sealed receipt is detected."""
    receipt = json.loads(_receipt_bytes().decode("utf-8"))
    assert _canonical(receipt) == _canonical(campaign)

    tampered = copy.deepcopy(receipt)
    seed0 = tampered["config"]["seed"][0]
    assert isinstance(seed0, str) and seed0
    last = seed0[-1]
    tampered["config"]["seed"][0] = seed0[:-1] + ("0" if last != "0" else "1")
    assert tampered["config"]["seed"][0] != seed0

    assert _canonical(tampered) != _canonical(campaign)
    assert (
        hashlib.sha256(
            (
                json.dumps(tampered, indent=2, sort_keys=True, ensure_ascii=True)
                + "\n"
            ).encode("utf-8")
        ).hexdigest()
        != RECEIPT_SHA256
    )


# ---------------------------------------------------------------------------
# M4: float injection must be rejected by the K1 AST scan
# ---------------------------------------------------------------------------


def test_m4_ast_scanner_rejects_float_literal_and_call() -> None:
    """M4: injected float literal / float call must produce AST hits."""
    source = Path(b.__file__).read_text(encoding="utf-8")

    literal_probe = source + "\n\ndef _m4_literal():\n    return 1.5\n"
    hits = b._ast_hits(literal_probe)
    assert any(h.startswith("literal:float:") for h in hits), hits

    call_probe = source + "\n\ndef _m4_call(x):\n    return float(x)\n"
    hits = b._ast_hits(call_probe)
    assert any(h.startswith("name:float:") for h in hits), hits

    assert b._ast_hits(source) == []


# ---------------------------------------------------------------------------
# M5: the unsigned reset sweep is non-discriminative on the tight r3 tube
# ---------------------------------------------------------------------------


def test_m5_unsigned_sweep_is_non_discriminative(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """M5 does **not** fail K2/K3; K6 is therefore not claimed as PASS.

    This is an honest limitation of the locked r3 mutation suite, not a
    certificate pass claim.  The formal verdict in the report is
    INCONCLUSIVE and no registry entry is created.
    """
    monkeypatch.setattr(b, "SWEEP_SIGNED", False)
    mutated = b.run_campaign()

    assert mutated["summary"] == "ALL PASS"
    assert mutated["all_pass"] is True
    assert mutated["checks"]["K2"]["passed"] is True
    assert mutated["checks"]["K3"]["passed"] is True
    assert mutated["checks"]["K3"]["krawczyk"]["passed"] is True


def test_no_r3_registry_entry() -> None:
    """The r3 track must not create A-2026-0042; A-2026-0041 stays absent."""
    registry = (ROOT / "reports" / "FENCE_REGISTRY.md").read_text(
        encoding="utf-8"
    )
    # A historical note may mention the id; only a real entry heading counts.
    assert "### A-2026-0041" not in registry
    assert "### A-2026-0042" not in registry


def test_report_records_inconclusive_verdict() -> None:
    """The narrative report must carry the formal INCONCLUSIVE verdict."""
    assert REPORT.exists(), "r3 report is missing"
    text = REPORT.read_text(encoding="utf-8")
    assert "INCONCLUSIVE" in text
    assert "non-diskriminatif" in text or "non-discriminative" in text
