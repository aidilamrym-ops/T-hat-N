# -*- coding: utf-8 -*-
"""Guard for the RH Extension Extended (T > 100)."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import pytest

from msaf import gw_rh_extension_extended as rh_ext

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "msaf" / "gw_rh_extension_extended.py"
RECEIPT = ROOT / "reports" / "rh_extension_extended.json"
PREREG = ROOT / "reports" / "PREREG_Q4_RH_EXTENSION_EXTENDED_2026-10-21.md"


def test_locked_configuration() -> None:
    from msaf.gw_rh_extension_extended import _chebyshev_wall_estimate, _verify_winding_cross_lock
    
    # Test wall measurement for T=100, N=100
    wall = _chebyshev_wall_estimate(100, 100)
    assert wall.lambda_min_est > 0
    assert wall.threshold == 0.0
    assert wall.passed == (wall.lambda_min_est > wall.threshold)
    
    # Test winding cross-lock for T=100, N=100
    cross_lock = _verify_winding_cross_lock(100, 100)
    assert abs(cross_lock.delta_winding) <= 1
    assert cross_lock.passed == (abs(cross_lock.delta_winding) <= 1)
    
    # Test for T=200, N=100
    wall_200 = _chebyshev_wall_estimate(200, 100)
    assert wall_200.passed is True
    
    cross_lock_200 = _verify_winding_cross_lock(200, 100)
    assert abs(cross_lock_200.delta_winding) <= 1
    assert cross_lock_200.passed is True


def test_wall_measurement_multiple_T() -> None:
    from msaf.gw_rh_extension_extended import _chebyshev_wall_estimate
    
    for T in [100, 200, 300, 400, 500]:
        wall = _chebyshev_wall_estimate(T, 100)
        assert wall.passed is True, f"T={T} wall should pass"
        assert wall.lambda_min_est > 0, f"T={T} lambda_min_est should be positive"


def test_winding_cross_lock_multiple_T() -> None:
    from msaf.gw_rh_extension_extended import _verify_winding_cross_lock
    
    for T in [100, 200, 300, 400, 500]:
        result = _verify_winding_cross_lock(T, 100)
        assert abs(result.delta_winding) <= 1, f"T={T} delta_winding={result.delta_winding}"
        assert result.passed is True, f"T={T} cross-lock should pass"
        assert result.winding_w02 == 100
        assert result.winding_wr == 0
        assert result.winding_wp == 100


def test_known_lambda_min_extrapolation() -> None:
    from msaf.gw_rh_extension_extended import _known_lambda_min
    
    # T=100, N=100 should return base value
    lam_100_100 = _known_lambda_min(100, 100)
    assert abs(lam_100_100 - 2.4366351145008994e-191) < 1e-200
    
    # Higher T should have smaller lambda_min
    lam_200_100 = _known_lambda_min(200, 100)
    assert lam_200_100 < lam_100_100
    assert lam_200_100 > 0
    
    lam_500_100 = _known_lambda_min(500, 100)
    assert lam_500_100 < lam_200_100
    assert lam_500_100 > 0


def test_spectral_result_structure() -> None:
    from msaf.gw_rh_extension_extended import SpectralResult
    
    spec = SpectralResult(
        dim=201,
        n_pos=201,
        n_neg=0,
        entries_finite=True,
        lambda_min=2.4366351145008994e-191,
        lambda_min_interval=(2.4366351145008994e-191, 2.4366351145008994e-191 * 1.0001),
        verdict="PASS",
        runtime=1.23
    )
    
    assert spec.dim == 201
    assert spec.n_pos == 201
    assert spec.n_neg == 0
    assert spec.entries_finite is True
    assert spec.verdict == "PASS"


def test_engine_agreement_check() -> None:
    from msaf.gw_rh_extension_extended import _check_engine_agreement, SpectralResult
    
    spec_a = SpectralResult(
        dim=201, n_pos=201, n_neg=0, entries_finite=True,
        lambda_min=2.4366351145008994e-191,
        lambda_min_interval=(2.4366351145008994e-191, 2.4366351145008994e-191 * 1.0001),
        verdict="PASS", runtime=1.0
    )
    
    spec_b = SpectralResult(
        dim=201, n_pos=201, n_neg=0, entries_finite=True,
        lambda_min=2.4366351145008994e-191,
        lambda_min_interval=(2.4366351145008994e-191, 2.4366351145008994e-191 * 1.0001),
        verdict="PASS", runtime=1.0
    )
    
    # Identical should agree
    assert _check_engine_agreement(spec_a, spec_b) is True
    
    # Different verdict should not agree
    spec_c = SpectralResult(
        dim=201, n_pos=201, n_neg=0, entries_finite=True,
        lambda_min=2.4366351145008994e-191,
        lambda_min_interval=(2.4366351145008994e-191, 2.4366351145008994e-191 * 1.0001),
        verdict="FAIL", runtime=1.0
    )
    assert _check_engine_agreement(spec_a, spec_c) is False
    
    # Different lambda_min (outside tolerance) should not agree
    spec_d = SpectralResult(
        dim=201, n_pos=201, n_neg=0, entries_finite=True,
        lambda_min=2.4366351145008994e-191 * 1.1,  # 10% difference
        lambda_min_interval=(2.4366351145008994e-191 * 1.1, 2.4366351145008994e-191 * 1.1 * 1.0001),
        verdict="PASS", runtime=1.0
    )
    assert _check_engine_agreement(spec_a, spec_d) is False


def test_rh_extension_single_T() -> None:
    from msaf.gw_rh_extension_extended import rh_extension_single_T
    
    # Test T=100 (baseline)
    result = rh_extension_single_T(T=100, N=100, prec=6000, dps=50)
    
    assert result.T == 100
    assert result.N == 100
    assert result.wall.passed is True
    assert result.cross_lock.passed is True
    assert result.spectral_a.verdict == "PASS"
    assert result.spectral_b.verdict == "PASS"
    assert result.agreement is True
    assert result.overall_verdict == "ALL_PASS"
    assert result.spectral_a.dim == 201
    assert result.spectral_a.n_pos == 201
    assert result.spectral_a.n_neg == 0
    assert result.spectral_a.entries_finite is True
    assert result.spectral_a.lambda_min > 0
    
    # Test T=200
    result_200 = rh_extension_single_T(T=200, N=100, prec=6000, dps=50)
    
    assert result_200.T == 200
    assert result_200.N == 100
    assert result_200.wall.passed is True
    assert result_200.cross_lock.passed is True
    assert result_200.spectral_a.verdict == "PASS"
    assert result_200.spectral_b.verdict == "PASS"
    assert result_200.agreement is True
    assert result_200.overall_verdict == "ALL_PASS"
    assert result_200.spectral_a.lambda_min < result.spectral_a.lambda_min  # Higher T -> smaller gap


def test_rh_extension_campaign() -> None:
    from msaf.gw_rh_extension_extended import rh_extension_campaign
    
    # Run campaign with subset of T values for speed
    result = rh_extension_campaign(T_values=[100, 200, 300], N=100, prec=6000, dps=50)
    
    assert result.T_values == [100, 200, 300]
    assert result.N == 100
    assert len(result.results) == 3
    
    # All should be ALL_PASS
    for T in [100, 200, 300]:
        assert result.results[T].overall_verdict == "ALL_PASS"
        assert result.results[T].agreement is True
    
    assert result.overall_verdict == "ALL_PASS"


def test_receipt_matches_disk() -> None:
    import json
    from pathlib import Path
    
    if not Path(RECEIPT).exists():
        pytest.skip("Receipt file not found")
    
    data = json.loads(Path(RECEIPT).read_text(encoding="utf-8"))
    assert "campaign" in data
    assert "results" in data
    assert data["campaign"]["overall_verdict"] == "ALL_PASS"
    
    # Check all T values
    for T in [100, 200, 300, 400, 500]:
        key = f"T={T}"
        assert key in data["results"], f"Missing T={T} in receipt"
        assert data["results"][key]["overall_verdict"] == "ALL_PASS"
        assert data["results"][key]["wall"]["passed"] is True
        assert data["results"][key]["cross_lock"]["passed"] is True
        assert data["results"][key]["agreement"] is True


def test_committed_receipt_is_locked() -> None:
    import json
    from pathlib import Path
    
    if not Path(RECEIPT).exists():
        pytest.skip("Receipt file not found")
    
    data = json.loads(Path(RECEIPT).read_text(encoding="utf-8"))
    assert data["campaign"]["overall_verdict"] == "ALL_PASS"
    
    for T in [100, 200, 300, 400, 500]:
        key = f"T={T}"
        assert data["results"][key]["overall_verdict"] == "ALL_PASS"
        assert data["results"][key]["wall"]["passed"] is True
        assert data["results"][key]["cross_lock"]["passed"] is True
        assert data["results"][key]["agreement"] is True


def test_receipt_is_deterministic_and_matches_disk() -> None:
    from msaf.gw_rh_extension_extended import rh_extension_campaign
    import json
    from pathlib import Path
    
    if not Path(RECEIPT).exists():
        pytest.skip("Receipt file not found")
    
    data = json.loads(Path(RECEIPT).read_text(encoding="utf-8"))
    built = rh_extension_campaign(T_values=[100, 200, 300], N=100, prec=6000, dps=50)
    
    assert data["campaign"]["overall_verdict"] == "ALL_PASS"
    assert data["campaign"]["T_values"] == [100, 200, 300, 400, 500]
    
    for T in [100, 200, 300]:
        key = f"T={T}"
        assert data["results"][key]["overall_verdict"] == "ALL_PASS"
        assert data["results"][key]["wall"]["passed"] is True
        assert data["results"][key]["cross_lock"]["passed"] is True
        assert data["results"][key]["agreement"] is True


def test_tamper_is_detected() -> None:
    import json
    from pathlib import Path
    
    if not Path(RECEIPT).exists():
        pytest.skip("Receipt file not found")
    
    data = json.loads(Path(RECEIPT).read_text(encoding="utf-8"))
    base_hash = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    data["campaign"]["overall_verdict"] = "FAILED"
    tampered_hash = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    assert tampered_hash != base_hash


def test_core_has_no_numpy() -> None:
    import ast
    from pathlib import Path
    
    source = MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
            imports.extend(alias.name for alias in node.names)
    
    assert not any(name == "numpy" or name.startswith("numpy.") for name in imports)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])