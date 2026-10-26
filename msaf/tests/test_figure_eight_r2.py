"""Guard for the T2-r2 reduced 8x8 figure-eight campaign.

Implements the K6 guard obligation of
``reports/PREREG_FIGURE_EIGHT_R2_2026-10-22.md`` section 4 K6:

* two full campaign runs must be byte-identical and equal to the sealed
  receipt;
* the AST scan of the r2 module must reject float literals and float calls;
* mutations M1-M5 are exercised, with the disclosure that the honest
  campaign already fails K2 at the first checkpoint, so M1/M2/M5 cannot
  discriminate the K2 width gate cleanly.

The sealed verdict of T2-r2 is FAILED at K2 (frozen T1b quadratic slack
versus ``R_B = 1e-10``); this guard pins that payload.  It does not
redefine thresholds and makes no local-uniqueness claim.
"""

import copy
import hashlib
import json
from pathlib import Path

import flint
import pytest

from msaf import figure_eight_r2 as b

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "reports" / "PREREG_FIGURE_EIGHT_R2_2026-10-22.md"
RECEIPT = ROOT / "reports" / "figure_eight_r2_2026-10-22.json"

# Receipt sha256 (LF-normalised bytes) of the two byte-identical failed runs
# recorded in reports/FIGURE_EIGHT_R2_2026-10-22.md.
RECEIPT_SHA256 = (
    "b25c7692e0bf3236e5b1d8945b8a0159c6f1f9a93a962ee19583b36a46866aa4"
)
MODULE_SHA256 = (
    "22fcc6ecdd63fccb9caf7c0ddab3ae55e888dfdd74600a1d3a30dc1f5aa34f04"
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
    """One fresh full campaign run (K1-K5); writes nothing to disk."""
    return b.run_campaign()


# ---------------------------------------------------------------------------
# K6(i): fresh campaign must reproduce the sealed failed receipt byte for byte
# ---------------------------------------------------------------------------


def test_campaign_payload_is_byte_identical_to_receipt(campaign: dict) -> None:
    """A fresh rerun equals the sealed receipt on LF-normalised bytes."""
    assert RECEIPT.exists(), "sealed T2-r2 receipt is missing"
    fresh = (
        json.dumps(campaign, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    )
    stored = _receipt_bytes()
    assert fresh.encode("utf-8") == stored

    receipt = json.loads(stored.decode("utf-8"))
    assert _canonical(campaign) == _canonical(receipt)
    assert hashlib.sha256(stored).hexdigest() == RECEIPT_SHA256


def test_receipt_freezes_hashes_and_failed_verdict(campaign: dict) -> None:
    """The receipt pins the prereg/frozen modules and the honest failure."""
    prereg_sha = hashlib.sha256(PREREG.read_bytes()).hexdigest()
    t1_sha = hashlib.sha256(Path(b.t1.__file__).read_bytes()).hexdigest()
    t1b_sha = hashlib.sha256(Path(b.t1b.__file__).read_bytes()).hexdigest()
    module_sha = hashlib.sha256(
        Path(b.__file__).read_bytes().replace(b"\r\n", b"\n")
    ).hexdigest()

    assert campaign["schema"] == "msaf.figure_eight_r2.v1"
    assert campaign["prereg_sha256lf"] == prereg_sha == b.PREREG_SHA
    assert campaign["t1_module_sha256lf"] == t1_sha == b.T1_MODULE_SHA
    assert campaign["t1b_module_sha256lf"] == t1b_sha == b.T1B_MODULE_SHA
    assert campaign["python_flint"] == flint.__version__
    assert campaign["precision"] == 256
    assert campaign["order"] == 24
    assert campaign["config"]["r_B"] == str(b.R_B)
    assert campaign["config"]["remainder_factor"] == 1
    assert campaign["config"]["sweep_signed"] is True
    assert campaign["checks"]["K1"]["ast_scan_hits"] == []
    assert campaign["checks"]["K1"]["passed"] is True

    # The locked verdict is FAILED: K1 and Newton pass, K2 fails at step 96,
    # and K3/K4/K5 are not reached.  No registry entry is implied.
    assert module_sha == MODULE_SHA256
    assert campaign["summary"] == "FAILED"
    assert campaign["all_pass"] is False
    checks = campaign["checks"]
    assert checks["K1"]["passed"] is True
    assert checks["K2"]["passed"] is False
    assert checks["K2"]["width_max"] is None
    assert checks["K2"]["widths_ok"] is False
    assert "K2 fail-fast" in (checks["K2"]["error"] or "")
    assert "at step 96" in (checks["K2"]["error"] or "")
    assert checks["K3"]["newton_ok"] is True
    assert checks["K3"]["iterations"] == 3
    assert checks["K3"]["f_inf_final"].startswith(
        "[4.222845715357847910637323998643523507567862899636295014679650259478241866838e-25"
    )
    assert checks["K3"]["passed"] is False
    assert checks["K3"]["krawczyk"] is None
    assert checks["K3"]["box_error"] == checks["K2"]["error"]
    assert checks["K4"] is None
    assert checks["K5"] is None
    assert campaign["collision_guard"] is None


def test_k2_failure_is_locked_t1b_slack_not_collision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Diagnostic: one first checkpoint already exceeds the cap via slack.

    This is a root-cause guard, not a certification.  It reproduces the
    first checkpoint with ``R_B = 1e-10`` and asserts that the slack term
    (``KAPPA_NL * radius**2`` with the frozen T1b ``KAPPA_NL = 1e18``) is
    above ``TUBE_CAP`` before any collision or Picard failure.
    """
    monkeypatch.setattr(b, "H_STEPS", 1)
    monkeypatch.setattr(b, "H_GRID", b.T0 / 1536)
    with flint.ctx.workprec(b.PREC):
        m0, c0 = b._lift_box(
            list(b.SEED_R2), [b._b(b.R_B)] * b.N_SEC
        )
        ps = b._forward_pass(m0, c0, False)
        assert ps["error"] is None
        ck = ps["checkpoints"][1]
        assert bool(ck["slack"] > b._b(b.TUBE_CAP))
        assert bool(ck["width"] > b._b(b.TUBE_CAP))


def test_reduced_derivative_matches_short_horizon_finite_difference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression for the q3/v3 dependent columns and product order.

    The old independent-block/forward-order product had a finite-difference
    mismatch of about 2.7e-7 on this four-step horizon; the fixed constrained
    derivative agrees to about 2.2e-17.
    """
    monkeypatch.setattr(b, "H_STEPS", 4)
    monkeypatch.setattr(b, "H_GRID", b.Fraction(1, 1000))
    with flint.ctx.workprec(b.PREC):
        x = list(b.SEED_R2)
        z = [b.ZERO] * b.N_SEC
        base = b._evaluate(x, z, False, False)
        assert base["ok"] is True, base.get("error")
        eps = b.Fraction(1, 10**8)
        worst = b.ZERO
        for j in range(b.N_SEC):
            xp = list(x)
            xm = list(x)
            xp[j] = xp[j] + eps
            xm[j] = xm[j] - eps
            ep = b._evaluate(xp, z, False, False)
            em = b._evaluate(xm, z, False, False)
            assert ep["ok"] and em["ok"], (j, ep.get("error"), em.get("error"))
            for i in range(b.N_SEC):
                fd = (ep["G"][i] - em["G"][i]) / (2 * b._b(eps))
                diff = (fd - base["DG"][i][j]).abs_upper()
                if bool(diff > worst):
                    worst = diff
        assert bool(worst < b._b(b.Fraction(1, 10**15))), worst


def test_inverse_mid_reports_singular_matrix() -> None:
    """The crash handler must turn a singular midpoint into ``None``."""
    n = b.N_SEC
    zero = [[b.arb(0) for _ in range(n)] for _ in range(n)]
    assert b._inverse_mid(zero) is None

    eye = [
        [b.arb(1) if i == j else b.arb(0) for j in range(n)]
        for i in range(n)
    ]
    assert b._inverse_mid(eye) is not None


# ---------------------------------------------------------------------------
# M1: remainder factor 1e70 must fail the campaign honestly
# ---------------------------------------------------------------------------


def test_m1_remainder_factor_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    """M1: factor 1e70 is rejected; on r2 this aborts before K2.

    Disclosure: the inflated remainder makes the Picard enclosure fail at
    step 2, so the K2 width gate is not exercised.  The mutation still
    yields FAILED and K3 false.
    """
    monkeypatch.setattr(b, "REMAINDER_FACTOR", 10**70)
    mutated = b.run_campaign()

    assert mutated["summary"] == "FAILED"
    assert mutated["all_pass"] is False
    assert mutated["checks"]["K3"]["newton_ok"] is False
    assert mutated["checks"]["K3"]["passed"] is False
    error = mutated["checks"]["K3"]["error"] or ""
    assert "aborted at step" in error, error
    assert "Picard enclosure failed" in error, error
    assert mutated["checks"]["K2"] is None


# ---------------------------------------------------------------------------
# M2: period shift +1/10 must still fail K3
# ---------------------------------------------------------------------------


def test_m2_period_shift_fails_k3(monkeypatch: pytest.MonkeyPatch) -> None:
    """M2: a +1/10 period shift must not certify (K3 false).

    Disclosure: the honest campaign already fails K2; this mutation also
    perturbs the Newton target, so it is not a clean isolated test of the
    period gate.  It still asserts that no PASS verdict is produced.
    """
    shifted = b.T0 + b.Fraction(1, 10)
    monkeypatch.setattr(b, "T0", shifted)
    monkeypatch.setattr(b, "H_GRID", shifted / b.H_STEPS)
    mutated = b.run_campaign()

    assert mutated["summary"] == "FAILED"
    assert mutated["all_pass"] is False
    assert mutated["checks"]["K3"]["passed"] is False


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
# M5: block-wise signed-sweep reset must not certify
# ---------------------------------------------------------------------------


def test_m5_unsigned_sweep_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """M5: the reset-per-block mutation must not produce a PASS verdict.

    Disclosure: the honest campaign already fails K2 at step 96, so this
    mutation is non-discriminating for the signed-sweep mechanism.  It still
    asserts FAILED and no Krawczyk result.
    """
    monkeypatch.setattr(b, "SWEEP_SIGNED", False)
    mutated = b.run_campaign()

    assert mutated["summary"] == "FAILED"
    assert mutated["all_pass"] is False
    assert mutated["checks"]["K2"]["passed"] is False
    assert mutated["checks"]["K3"]["passed"] is False
    assert mutated["checks"]["K3"]["krawczyk"] is None


def test_no_r2_registry_entry() -> None:
    """The failed r2 track must not create registry entry A-2026-0041."""
    registry = (ROOT / "reports" / "FENCE_REGISTRY.md").read_text(
        encoding="utf-8"
    )
    # A historical note may mention the id; only a real entry heading counts.
    assert "### A-2026-0041" not in registry
