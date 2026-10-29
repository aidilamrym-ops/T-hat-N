# -*- coding: utf-8 -*-
"""Guard for the finite Ulam spectral-closure certificate.

The full campaign is small enough to rerun once in CI.  The guard locks the
exact matrix hashes, the 128-bit first-pass rung, the resolution-alarm
semantics, the scope flags, and the committed receipt.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import pytest
from flint import ctx

from msaf import ulam_spectral as u

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "reports" / "PREREG_ULAM_SPECTRAL_2026-10-21.md"
RECEIPT = ROOT / "reports" / "ulam_spectral_2026-10-21.json"


def test_locked_configuration() -> None:
    assert u.TARGET_WIDTH == Fraction(1, 10**25)
    assert u.TARGET_WIDTH_STR == "1e-25"
    assert u.MAX_RESOLUTION_ATTEMPTS == 60
    assert u.MAX_PRECISION_BITS == 1024
    assert u.RESOLUTION_LADDER == (64, 128, 256, 512, 1024)
    assert u.ALGORITHM == "rump"
    assert len(u.INSTANCES) == 2
    for item in u.INSTANCES:
        n = int(item["n"])
        p = Fraction(int(item["p_num"]), int(item["p_den"]))
        assert p == Fraction(n, 2 * (n + 1))


def test_exact_matrix_is_stochastic_and_nonsymmetric() -> None:
    expected = {
        16: "16ba75523f3a5ee0351dc226325342ea5e9b24753fd09b2e89a617b5bc28ade8",
        32: "96236555230c87bab8c951d002a8ed20931cb884b355508c17ac8242be8ab396",
    }
    for item in u.INSTANCES:
        n = int(item["n"])
        p = Fraction(int(item["p_num"]), int(item["p_den"]))
        matrix = u.ulam_matrix(n, p)
        assert all(isinstance(value, Fraction) for row in matrix for value in row)
        assert all(value >= 0 for row in matrix for value in row)
        assert all(sum(row, Fraction(0)) == 1 for row in matrix)
        assert any(
            matrix[i][j] != matrix[j][i]
            for i in range(n)
            for j in range(i + 1, n)
        )
        assert u.matrix_sha256(matrix) == expected[n]


def test_exact_rank_and_simple_spectrum() -> None:
    expected_det = {
        16: "203212800/2862423051509815793",
        32: "425479634944000000/1843706170846276747857062870605259735097",
    }
    for item in u.INSTANCES:
        n = int(item["n"])
        p = Fraction(int(item["p_num"]), int(item["p_den"]))
        exact = u.exact_checks(n, p)
        assert exact["status"] == "PASS"
        assert exact["checks"]["C1_full_rank"] is True
        assert exact["checks"]["C1_perron_simple"] is True
        assert exact["checks"]["C1_squarefree"] is True
        assert exact["rank"] == n
        assert exact["rank_minus_identity"] == n - 1
        assert exact["discriminant_nonzero"] is True
        assert exact["determinant"] == expected_det[n]


def test_128_bit_enclosure_meets_target_and_restores_precision() -> None:
    before = ctx.prec
    item = u.INSTANCES[0]
    n = int(item["n"])
    p = Fraction(int(item["p_num"]), int(item["p_den"]))
    matrix = u.matrix_to_fmpq(u.ulam_matrix(n, p))
    result = u.measure_ladder(matrix, ladder=(128,))
    assert ctx.prec == before
    assert result["all_rungs_ok"] is True
    assert result["target_met"] is True
    assert result["first_pass_bits"] == 128
    rung = result["rungs"][0]
    assert rung["n_eigenvalues"] == n
    assert len(rung["perron_indices"]) == 1
    assert rung["all_other_modulus_below_one"] is True
    assert rung["width_float"] <= 1e-25


def test_resolution_alarm_is_fail_closed() -> None:
    with pytest.raises(u.ResolutionAlarm):
        u.assert_resolution(
            {"all_rungs_ok": False, "target_met": True, "contraction": True}
        )
    with pytest.raises(u.ResolutionAlarm):
        u.assert_resolution(
            {"all_rungs_ok": True, "target_met": False, "contraction": True}
        )
    with pytest.raises(u.ResolutionAlarm):
        u.assert_resolution(
            {"all_rungs_ok": True, "target_met": True, "contraction": False}
        )
    u.assert_resolution(
        {"all_rungs_ok": True, "target_met": True, "contraction": True}
    )


def test_full_campaign_is_deterministic_and_matches_disk() -> None:
    first = u.build_receipt()
    second = u.build_receipt()
    assert u.canonical_json(first) == u.canonical_json(second)
    assert u.receipt_sha256(first) == u.receipt_sha256(second)
    assert first["verdict"] == "PASS"
    assert first["prereg_sha256"] == hashlib.sha256(
        PREREG.read_bytes().replace(b"\r\n", b"\n")
    ).hexdigest()
    on_disk = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert on_disk == first


def test_receipt_hash_changes_on_tamper() -> None:
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    base = u.receipt_sha256(data)
    data["verdict"] = "TAMPERED"
    assert u.receipt_sha256(data) != base


def test_committed_receipt_is_locked() -> None:
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["schema"] == u.SCHEMA
    assert data["verdict"] == "PASS"
    assert u.receipt_sha256(data) == (
        "4a850532be255fd0f68a55d529c12d3406696b50e281997daba20528dcb883ac"
    )
    assert data["config"]["resolution_ladder"] == [64, 128, 256, 512, 1024]
    assert data["config"]["target_width"] == "1e-25"
    for instance in data["instances"]:
        assert instance["status"] == "PASS"
        assert instance["spectral"]["first_pass_bits"] == 128
        assert instance["spectral"]["attempts_used"] == 5
        assert instance["spectral"]["alarm_triggered"] is False
        assert instance["spectral"]["contraction"] is True
        assert instance["newton_contraction_tested"] is False
        assert all(instance["checks"].values())


def test_scope_flags_forbid_overclaiming() -> None:
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["scope"] == {
        "newton_contraction_tested": False,
        "continuous_operator_claim": False,
        "ergodicity_claim": False,
        "mixing_claim": False,
        "logistic_spectrum_claim": False,
        "sealed_campaigns_rerun": False,
    }


