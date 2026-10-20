# -*- coding: utf-8 -*-
"""Guard for the finite RBM Anderson S1/S2 diagnostic.

The full campaign is deliberately not rerun in CI.  These tests exercise the
formulas, exact-rational matrix construction, deterministic seed derivation,
the Arb spot-check, the quick campaign path, receipt hashing, and the committed
full receipt.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from msaf import rbm_anderson as r

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "reports" / "PREREG_RBM_ANDERSON_2026-10-20.md"
FULL_RECEIPT = ROOT / "reports" / "rbm_anderson_2026-10-20.json"


def test_seed_and_config_are_locked() -> None:
    assert r.MASTER_SEED == 2430500035454946990
    assert r.derive_seed("rbm:1:0") == 16251301238791598469
    assert r.derive_seed("gue:ref:0") == 651868131420040142
    assert r.derive_seed("pois:cal:3") == 6806020971409150465
    assert r.FULL_CONFIG.dim == 201
    assert r.FULL_CONFIG.bandwidths == (1, 10, 120)
    assert r.FULL_CONFIG.n_matrices == 64
    assert r.FULL_CONFIG.n_reference == 2000
    assert r.FULL_CONFIG.n_calibration == 64
    assert r.FULL_CONFIG.n_bootstrap == 2000
    assert r.SIGMA_U == (0.3, 0.5, 1.0)
    assert r.CHARTS == ("T", "L")


def test_matrix_is_exact_hermitian_and_banded() -> None:
    for b in (1, 5, 15):
        a = r.matrix_from_seed(r.derive_seed(f"rbm:{b}:0"), 31, b)
        assert a.shape == (31, 31)
        assert np.array_equal(a, a.conj().T)
        idx = np.arange(31)
        outside = np.abs(idx[:, None] - idx[None, :]) > b
        assert np.all(a[outside] == 0)
        # Every entry is an integer multiple of 1/65536 (diagonal: 1/32768).
        assert np.allclose(a * 65536.0, np.round(a * 65536.0))


def test_chart_and_s1_formula() -> None:
    ev = np.array([-2.0, 0.0, 1.0, 5.0])
    linear = r.chart_levels(ev, "L")
    logged = r.chart_levels(ev, "T")
    assert np.allclose(linear, [1.0, 3.0, 4.0, 8.0])
    assert np.allclose(logged, np.log([1.0, 3.0, 4.0, 8.0]))
    assert linear[0] == 1.0
    assert logged[0] == 0.0
    assert np.isclose(r.s1([0.0, 1.0, 3.0, 6.0]), 7.0 / 12.0, atol=0.0, rtol=1e-15)


def test_s2_is_finite_and_affine_invariant() -> None:
    x = np.array([-2.0, -0.3, 0.1, 0.7, 1.2, 2.5, 4.0, 7.1])
    a = r.s2(x, 0.5)
    b = r.s2(3.0 * x + 11.0, 0.5)
    assert a.shape == (20,)
    assert np.all(np.isfinite(a))
    assert np.all(a >= 0.0)
    assert np.allclose(a, b, atol=1e-12, rtol=0.0)
    mask = r.kept_bin_mask(31)
    assert mask.shape == (20,)
    assert not mask[0]
    assert r.kept_bin_mask(201).all()


def test_spot_check_matches_float_spectrum() -> None:
    seed = r.derive_seed("rbm:1:0")
    check = r.spot_check(seed, 31, 1)
    assert check["pass"] is True
    assert check["imaginary_parts_contain_zero"] is True
    assert check["max_abs_eigenvalue_diff"] <= 1e-8
    assert len(check["matrix_sha256"]) == 64
    # A tampered matrix hash must not silently equal the locked one.
    assert r.matrix_sha256(seed, 31, 1) == check["matrix_sha256"]


def test_quick_campaign_is_deterministic_and_structured() -> None:
    first = r.run_campaign(r.QUICK_CONFIG, do_spot_check=False)
    second = r.run_campaign(r.QUICK_CONFIG, do_spot_check=False)
    assert r.canonical_json(first) == r.canonical_json(second)
    assert first["schema"] == r.SCHEMA
    assert first["verdict"] in {"PASS", "PARTIAL", "INCONCLUSIVE", "FAILED"}
    assert first["prereg_sha256"] == hashlib.sha256(
        PREREG.read_bytes().replace(b"\r\n", b"\n")
    ).hexdigest()
    assert first["config"]["dim"] == 31
    assert tuple(first["config"]["bandwidths"]) == (1, 5, 15)
    assert len(first["rbm"]) == 3
    assert first["integrity"]["pass"] is True


def test_receipt_hash_changes_on_tamper() -> None:
    receipt = r.run_campaign(r.QUICK_CONFIG, do_spot_check=False)
    base = r.receipt_sha256(receipt)
    receipt["verdict"] = "TAMPERED"
    assert r.receipt_sha256(receipt) != base


def test_committed_full_receipt_is_locked() -> None:
    data = json.loads(FULL_RECEIPT.read_text(encoding="utf-8"))
    assert data["schema"] == r.SCHEMA
    assert data["config"]["dim"] == 201
    assert data["config"]["bandwidths"] == [1, 10, 120]
    assert data["config"]["seed"] == r.MASTER_SEED
    assert data["prereg_sha256"] == hashlib.sha256(
        PREREG.read_bytes().replace(b"\r\n", b"\n")
    ).hexdigest()
    assert data["integrity"]["pass"] is True
    assert data["verdict"] == "PASS"
    assert r.receipt_sha256(data) == (
        "3744cbe92546256f8cb9c25c0dabb16a98921838ebfa026c07c60e5c4892bca3"
    )


def test_full_receipt_has_all_six_s2_cells() -> None:
    data = json.loads(FULL_RECEIPT.read_text(encoding="utf-8"))
    for b in ("1", "10", "120"):
        assert len(data["rbm"][b]["s2"]) == 6
        assert len(data["rbm"][b]["s1"]) == 2
    assert data["s2_extreme"]["b_min"]["n"] == 6
    assert data["s2_extreme"]["b_max"]["n"] == 6
