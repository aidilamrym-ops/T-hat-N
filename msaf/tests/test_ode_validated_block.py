"""Guard for the T1b validated-ODE block campaign.

Implements the C6 guard obligation of the T1b preregistration
(``reports/PREREG_ODE_VALIDATED_T1B_2026-10-21.md`` section 4, mirroring
T1 section 4 lines 118-131):

* rerun the full certified campaign and compare its payload byte for byte
  with the sealed receipt (the receipt itself was produced by two
  consecutive byte-identical runs, sha256
  ``FA2C27F045A299231B45135BD85C1A6DB5AE8CAB5A327AB2454072A65E3DAAF8``);
* mutations M1-M5, each of which must FAIL when the enforcement is
  weakened;
* the AST scan over the T1b module and the frozen T1 module;
* the section 2.3 obligation ``kappa_nl * r_tot^2 <= 1e-30`` gating the
  C4/C5 verdict (preregistration sections 2.3, 5, 12.5).

No system, tolerance, or configuration parameter is redefined here: S1-S4
and C1-C6 live in the frozen ``msaf.ode_validated`` (T1) and the campaign
module ``msaf.ode_validated_block`` (T1b).  This file only *checks*.
"""

import copy
import hashlib
import json
from pathlib import Path

import flint
import pytest
from flint import arb

from msaf import ode_validated as t1
from msaf import ode_validated_block as b

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "reports" / "PREREG_ODE_VALIDATED_T1B_2026-10-21.md"
RECEIPT = ROOT / "reports" / "ode_validated_t1b_2026-10-21.json"

# Receipt sha256 of the two byte-identical certified runs recorded in the
# report (reports/ODE_VALIDATED_T1B_2026-10-21.md, section on determinism).
RECEIPT_SHA256 = (
    "FA2C27F045A299231B45135BD85C1A6DB5AE8CAB5A327AB2454072A65E3DAAF8"
)


def _canonical(data: object) -> str:
    """Canonical JSON payload used for tamper comparisons (repo pattern)."""
    return json.dumps(
        data, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


@pytest.fixture(scope="module")
def campaign() -> dict:
    """One fresh full certified campaign run (C1-C7, ~4 minutes).

    ``run_campaign`` wraps itself in ``flint.ctx.workprec(PREC)``; it never
    writes the receipt (only ``main()`` does), so the sealed file on disk
    is left untouched by this guard.
    """
    return b.run_campaign()


# ---------------------------------------------------------------------------
# M1: replace one endpoint of an interval so the exact value falls outside
# ---------------------------------------------------------------------------


def test_m1_one_endpoint_mutation_rejected() -> None:
    """M1: an interval whose exact value 2 lies outside must not certify.

    Replaces one endpoint of the certified C2 endpoint interval so that the
    exact solution value 2 is no longer contained; the containment
    enforcement used by every criterion (``t1._contains``) must reject it.
    """
    with flint.ctx.workprec(256):
        good = b._run_s1(24)["endpoint"]
        # Positive control: the certified interval really contains 2.
        assert t1._contains(good, 2) is True

        mid = good.mid()
        rad = good.rad()
        lo = mid - rad
        hi = mid + rad
        if bool(hi > 2):
            # Keep the upper endpoint, raise the lower endpoint above 2.
            new_lo = (hi + 2) / 2
            mutated = arb((new_lo + hi) / 2, (hi - new_lo) / 2)
        else:
            # Keep the lower endpoint, drop the upper endpoint below 2.
            new_hi = (lo + 2) / 2
            mutated = arb((lo + new_hi) / 2, (new_hi - lo) / 2)

        assert t1._contains(mutated, 2) is False


# ---------------------------------------------------------------------------
# M2: set the remainder to 0 in the C2 check
# ---------------------------------------------------------------------------


def test_m2_zero_remainder_fails_c2_check(monkeypatch: pytest.MonkeyPatch) -> None:
    """M2: C2 with remainder = 0 must fail containment.

    With the Taylor remainder dropped, the certificate carries only
    rounding/eps width, so the exact value 2 escapes the interval and the
    C2 gate (``contains_2``) must flip to False.
    """
    real = b._run_s1

    def _no_remainder(order: int, include_remainder: bool = True) -> dict:
        return real(order, include_remainder=False)

    with flint.ctx.workprec(256):
        # Positive control: the honest C2 check passes.
        control = b.check_c2()
        assert control["passed"] is True

        monkeypatch.setattr(b, "_run_s1", _no_remainder)
        mutated = b.check_c2()

    assert mutated["passed"] is False
    assert mutated["order16"]["contains_2"] is False
    assert mutated["order24"]["contains_2"] is False


# ---------------------------------------------------------------------------
# M4: inject float(/math. into a copy of the module; the AST scan must reject
# ---------------------------------------------------------------------------


def test_m4_ast_scanner_rejects_float_and_math() -> None:
    """M4: the AST scanner must reject injected ``float(`` and ``math.``."""
    source = Path(b.__file__).read_text(encoding="utf-8")
    t1_source = Path(t1.__file__).read_text(encoding="utf-8")

    probe_float = source + "\n\ndef _m4_probe(x):\n    return float(x)\n"
    hits_float = t1.ast_scan(probe_float)
    assert any(h.startswith("name:float:") for h in hits_float), hits_float

    probe_math = source + "\nimport math\n"
    hits_math = t1.ast_scan(probe_math)
    assert any(h.startswith("import:math:") for h in hits_math), hits_math

    # C6: the real modules are clean.
    assert t1.ast_scan(source) == []
    assert t1.ast_scan(t1_source) == []


# ---------------------------------------------------------------------------
# C6 core: fresh campaign must reproduce the sealed receipt byte for byte
# ---------------------------------------------------------------------------


def test_campaign_payload_is_byte_identical_to_receipt(campaign: dict) -> None:
    """A fresh rerun of the certified campaign equals the sealed receipt.

    The comparison is on LF-normalised bytes (the repo's sha256LF
    convention), so it is stable on CRLF checkouts (Windows with
    core.autocrlf) as well as on CI Linux.  Together with the recorded
    run1==run2 byte identity (receipt sha256 ``FA2C27F0...``) this
    transitively establishes the preregistration requirement that two
    consecutive runs produce identical bytes.
    """
    assert RECEIPT.exists(), "sealed T1b receipt is missing"
    fresh = (
        json.dumps(campaign, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    )
    stored = RECEIPT.read_bytes().replace(b"\r\n", b"\n")
    assert fresh.encode("utf-8") == stored

    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert _canonical(campaign) == _canonical(receipt)

    fresh_hash = hashlib.sha256(_canonical(campaign).encode("utf-8")).hexdigest()
    stored_hash = hashlib.sha256(_canonical(receipt).encode("utf-8")).hexdigest()
    assert fresh_hash == stored_hash


def test_receipt_freezes_prereg_and_frozen_t1_hashes(campaign: dict) -> None:
    """The receipt pins the live preregistration and frozen T1 module.

    It also restates the locked configuration identity: precision 256,
    order 24, kappa_nl 1e18, C7 limits equal to T1's abort steps.
    """
    prereg_sha = hashlib.sha256(PREREG.read_bytes()).hexdigest()
    t1_sha = hashlib.sha256(Path(t1.__file__).read_bytes()).hexdigest()

    assert campaign["schema"] == "msaf.ode_validated_block.v1"
    assert campaign["prereg_sha256lf"] == prereg_sha
    assert campaign["t1_module_sha256lf"] == t1_sha == b.T1_MODULE_SHA
    assert campaign["python_flint"] == flint.__version__
    assert campaign["precision"] == 256
    assert campaign["order"] == 24
    assert campaign["kappa_nl"] == "1e18"
    assert campaign["c7_limits"] == {"s3": 1557, "s4": 42}

    assert campaign["summary"] == "ALL PASS"
    assert campaign["all_pass"] is True

    checks = campaign["checks"]
    for key in ("C1", "C2", "C3", "C4", "C5", "C7"):
        assert checks[key]["passed"] is True, key
    assert checks["C1"]["cases"] == 2000
    assert checks["C1"]["failures"] == []
    assert checks["C6"]["ast_scan_passed"] is True
    assert checks["C6"]["ast_scan_hits"] == []


# ---------------------------------------------------------------------------
# M3: change E0 in the receipt; the payload comparison must detect it
# ---------------------------------------------------------------------------


def test_m3_e0_tamper_in_receipt_detected(campaign: dict) -> None:
    """M3: altering the certified E0 enclosure in the receipt is detected.

    ``E0 = -257428899017/200000000000`` is carried by the C5 checkpoint
    energy enclosures; a tampered value must no longer match the fresh
    campaign payload.
    """
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    # Pristine receipt matches the fresh run (sanity of the comparison).
    assert _canonical(receipt) == _canonical(campaign)

    tampered = copy.deepcopy(receipt)
    ckpt = tampered["checks"]["C5"]["checkpoints"][0]
    e0_carrier = ckpt["energy"]
    assert "-1.287144495085" in e0_carrier, e0_carrier
    ckpt["energy"] = e0_carrier.replace("-1.287144495085", "-1.287144495086", 1)
    assert ckpt["energy"] != e0_carrier

    # The guard's payload comparison must flag the change.
    assert _canonical(tampered) != _canonical(campaign)


# ---------------------------------------------------------------------------
# M5/C7: the frozen T1 scalar mechanism must reproduce its own failure
# ---------------------------------------------------------------------------


def test_m5_c7_reproduces_frozen_t1_failure(campaign: dict) -> None:
    """M5 = C7: frozen T1 must abort verbatim at its recorded steps."""
    c7 = campaign["checks"]["C7"]
    assert c7["passed"] is True
    assert c7["c4_reproduced"] is True
    assert c7["c5_reproduced"] is True
    assert c7["s3_abort_step"] == 1557
    assert c7["limit_s3"] == 1557
    assert c7["s4_abort_step"] == 42
    assert c7["limit_s4"] == 42
    assert c7["s3_error"] == (
        "aborted at step 1557: ValidationError: Picard enclosure failed"
    )
    assert c7["s4_error"] == (
        "aborted at step 42: ValidationError: Picard enclosure failed"
    )


# ---------------------------------------------------------------------------
# Section 2.3 obligation gates the C4/C5 verdict (prereg 2.3, 5, 12.5)
# ---------------------------------------------------------------------------


def test_section2_3_slack_obligation_gates_c4_c5_verdict(
    campaign: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``kappa_nl * r_tot^2 <= 1e-30`` must be part of the pass condition.

    First: the sealed campaign really records the obligation as satisfied.
    Then: a synthetic per-block violation, with every conservation check
    still passing, must flip ``check_c4``/``check_c5`` to False -- i.e. the
    obligation cannot be silently dropped from the verdict.
    """
    for key in ("C4", "C5"):
        chk = campaign["checks"][key]
        assert chk["section2_3_slack_ok"] is True, key
        assert all(d["slack_ok"] for d in chk["diags"]), key
        assert chk["passed"] is True, key

    fake_c4 = {
        "error": None,
        "checkpoints": [
            {"step": 256, "energy_ok": True, "angular_ok": True, "width_ok": True}
        ],
        "diags": [{"block": 1, "slack_ok": False}],
    }
    monkeypatch.setattr(b, "_run_s3", lambda: fake_c4)
    res = b.check_c4()
    assert res["section2_3_slack_ok"] is False
    assert res["passed"] is False

    fake_c4["diags"] = [{"block": 1, "slack_ok": True}]
    res = b.check_c4()
    assert res["section2_3_slack_ok"] is True
    assert res["passed"] is True

    fake_c5 = {
        "error": None,
        "checkpoints": [
            {
                "step": 64,
                "energy_ok": True,
                "angular_ok": True,
                "com_ok": True,
                "width_ok": True,
            }
        ],
        "diags": [{"block": 1, "slack_ok": False}],
    }
    monkeypatch.setattr(b, "_run_s4", lambda: fake_c5)
    res = b.check_c5()
    assert res["section2_3_slack_ok"] is False
    assert res["passed"] is False

    fake_c5["diags"] = [{"block": 1, "slack_ok": True}]
    res = b.check_c5()
    assert res["section2_3_slack_ok"] is True
    assert res["passed"] is True
