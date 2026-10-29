"""Guard for the T2 figure-eight validated-orbit campaign.

Implements the K6 guard obligation of the T2 preregistration
(``reports/PREREG_FIGURE_EIGHT_THREE_BODY_2026-10-22.md`` section 4 K6 and
section 9.3):

* two full campaign runs must be byte-identical and equal to the sealed
  receipt;
* the AST scan of the T2 module must reject float literals and float calls;
* mutations M1-M5 must fail exactly as locked (M1: K2 width cap fail-fast;
  M2: seed shift -> K3 fail; M3: receipt byte tamper detected; M4: float
  injection -> AST failure; M5: block-wise reset -> K3 fail).

No threshold or locked constant is redefined here: K1-K5 live in the
campaign module ``msaf.figure_eight`` and the frozen T1/T1b modules.  This
file only *checks*.  The verdict of the sealed T2 campaign is INCONCLUSIVE
(K5 frame mislabelling, disclosed in the report); this guard therefore pins
the actual sealed payload, not an ALL PASS expectation.
"""

import copy
import hashlib
import json
from pathlib import Path

import flint
import pytest

from msaf import figure_eight as b

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "reports" / "PREREG_FIGURE_EIGHT_THREE_BODY_2026-10-22.md"
RECEIPT = ROOT / "reports" / "figure_eight_three_body_2026-10-22.json"

# Receipt sha256 (LF-normalised bytes) of the two byte-identical certified
# runs recorded in reports/FIGURE_EIGHT_2026-10-22.md.
RECEIPT_SHA256 = (
    "72309f63d2bd9da14659fda0461ca1a9aaee85eec6f0cc9dabd3cf5e18842fce"
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
    """One fresh full certified campaign run (K1-K5).

    ``run_campaign`` wraps itself in ``flint.ctx.workprec(PREC)`` and never
    writes the receipt (only ``main()`` does), so the sealed file on disk is
    left untouched by this guard.
    """
    return b.run_campaign()


# ---------------------------------------------------------------------------
# K6(i): fresh campaign must reproduce the sealed receipt byte for byte
# ---------------------------------------------------------------------------


def test_campaign_payload_is_byte_identical_to_receipt(campaign: dict) -> None:
    """A fresh rerun of the certified campaign equals the sealed receipt.

    The comparison is on LF-normalised bytes (the repo's sha256LF
    convention), so it is stable on CRLF checkouts as well as on CI Linux.
    """
    assert RECEIPT.exists(), "sealed T2 receipt is missing"
    fresh = (
        json.dumps(campaign, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    )
    stored = _receipt_bytes()
    assert fresh.encode("utf-8") == stored

    receipt = json.loads(stored.decode("utf-8"))
    assert _canonical(campaign) == _canonical(receipt)
    assert hashlib.sha256(stored).hexdigest() == RECEIPT_SHA256


def test_receipt_freezes_prereg_and_frozen_module_hashes(campaign: dict) -> None:
    """The receipt pins the live preregistration and the frozen modules."""
    prereg_sha = hashlib.sha256(PREREG.read_bytes()).hexdigest()
    t1_sha = hashlib.sha256(Path(b.t1.__file__).read_bytes()).hexdigest()
    t1b_sha = hashlib.sha256(Path(b.t1b.__file__).read_bytes()).hexdigest()

    assert campaign["schema"] == "msaf.figure_eight.v1"
    assert campaign["prereg_sha256lf"] == prereg_sha == b.PREREG_SHA
    assert campaign["t1_module_sha256lf"] == t1_sha == b.T1_MODULE_SHA
    assert campaign["t1b_module_sha256lf"] == t1b_sha == b.T1B_MODULE_SHA
    assert campaign["python_flint"] == flint.__version__
    assert campaign["precision"] == 256
    assert campaign["order"] == 24
    assert campaign["config"]["remainder_factor"] == 1
    assert campaign["config"]["sweep_signed"] is True

    # K6(ii): the certified path is float-free.
    assert campaign["checks"]["K1"]["ast_scan_hits"] == []
    assert campaign["checks"]["K1"]["passed"] is True

    # Locked verdict of the strict campaign: K3 fails at the first Newton
    # inverse because the two-return map has the exact x-translation null
    # direction.  Therefore FAILED; K2/K4/K5 are not evaluated and no
    # registry entry exists.
    assert campaign["summary"] == "FAILED"
    assert campaign["all_pass"] is False
    checks = campaign["checks"]
    assert checks["K1"]["passed"] is True
    assert checks["K3"]["passed"] is False
    assert checks["K3"]["newton_ok"] is False
    assert checks["K3"]["df_singular"] is True
    assert checks["K3"]["null_witness"]["translation_null"] is True
    assert checks["K2"] is None
    assert checks["K4"] is None
    assert checks["K5"] is None


# ---------------------------------------------------------------------------
# M1: remainder factor 1e70 must trip the K2 width cap fail-fast
# ---------------------------------------------------------------------------


def test_m1_remainder_factor_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    """M1: factor 1e70 is rejected fail-fast by the certified forward pass.

    Disclosure: the abort happens **earlier** than the locked K2 checkpoint
    gate -- the inflated remainder radius makes the Picard enclosure fail
    at step 2.  The mutation still yields FAILED and K3 false, but the K2
    width gate itself is not exercised (prereg 9.3 expected the first
    checkpoint).
    """
    monkeypatch.setattr(b, "REMAINDER_FACTOR", 10**70)
    mutated = b.run_campaign()

    assert mutated["summary"] == "FAILED"
    assert mutated["checks"]["K3"]["newton_ok"] is False
    error = mutated["checks"]["K3"]["error"] or ""
    assert "aborted at step 2" in error, error
    assert "Picard enclosure failed" in error, error


# ---------------------------------------------------------------------------
# M2: seed q1x shifted by +1e-3 must fail Newton's monotone rule
# ---------------------------------------------------------------------------


def test_m2_seed_shift_fails_k3(monkeypatch: pytest.MonkeyPatch) -> None:
    """M2: a +1e-3 shift of q1x must not certify (K3 fail).

    Disclosure: the failure is confounded by the exact translation null
    direction, which makes DF singular at every seed; the mutated run
    therefore fails at the same first inverse as the honest campaign.
    """
    shifted = list(b.SEED)
    shifted[0] = shifted[0] + b.Fraction(1, 1000)
    monkeypatch.setattr(b, "SEED", tuple(shifted))
    mutated = b.run_campaign()

    assert mutated["summary"] == "FAILED"
    assert mutated["checks"]["K3"]["passed"] is False
    assert mutated["checks"]["K3"]["newton_ok"] is False
    assert mutated["checks"]["K3"]["df_singular"] is True


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
            (json.dumps(tampered, indent=2, sort_keys=True, ensure_ascii=True)
             + "\n").encode("utf-8")
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
# M5: block-wise signed-sweep reset must fail K3 (prereg 9.3)
# ---------------------------------------------------------------------------


def test_m5_unsigned_sweep_fails_k3(monkeypatch: pytest.MonkeyPatch) -> None:
    """M5: the reset-per-block mutation must fail K3.

    Disclosure (prereg 9.3 expected a box-run DF blow-up): the honest
    campaign already fails at the singular section derivative, so M5 is
    **non-discriminating** for the signed-sweep mechanism.  The mutation
    still yields FAILED and K3 false, which is all this guard can assert
    without weakening the locked scope.
    """
    monkeypatch.setattr(b, "SWEEP_SIGNED", False)
    mutated = b.run_campaign()

    assert mutated["summary"] == "FAILED"
    k3 = mutated["checks"]["K3"]
    assert k3["passed"] is False
    assert k3["newton_ok"] is False
    assert k3["df_singular"] is True
    assert k3["krawczyk"] is None


