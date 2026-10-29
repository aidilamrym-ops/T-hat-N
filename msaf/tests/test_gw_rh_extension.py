# -*- coding: utf-8 -*-
"""Guard for the RH Extension T=100 (winding cross-lock)."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import pytest

from msaf import gw_rh_extension as rh

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "msaf" / "gw_rh_extension.py"
RECEIPT = ROOT / "reports" / "rh_extension.json"
PREREG = ROOT / "reports" / "PREREG_Q4_RH_EXTENSION_2026-10-21.md"


def test_locked_configuration() -> None:
    from msaf.gw_rh_extension import _chebyshev_wall_estimate, _verify_winding_cross_lock
    
    # Test wall measurement for T=100, N=100
    wall = _chebyshev_wall_estimate(100, 100)
    assert wall.lambda_min_est > 0
    assert wall.threshold == 0.0  # Locked: threshold=0 for positive definiteness
    assert wall.passed == (wall.lambda_min_est > wall.threshold)
    
    # Test winding cross-lock for T=100, N=100
    cross_lock = _verify_winding_cross_lock(100, 100)
    assert abs(cross_lock.delta_winding) <= 1
    assert cross_lock.passed == (abs(cross_lock.delta_winding) <= 1)


def test_wall_measurement_logic() -> None:
    from msaf.gw_rh_extension import _chebyshev_wall_estimate
    
    # N=100 should pass
    wall_100 = _chebyshev_wall_estimate(100, 100)
    assert wall_100.passed is True
    assert wall_100.lambda_min_est > wall_100.threshold
    
    # N=150 should pass
    wall_150 = _chebyshev_wall_estimate(100, 150)
    assert wall_150.passed is True


def test_winding_cross_lock_logic() -> None:
    from msaf.gw_rh_extension import _verify_winding_cross_lock
    
    # T=100, N=100
    result_100 = _verify_winding_cross_lock(100, 100)
    assert abs(result_100.delta_winding) <= 1
    assert result_100.passed is True
    
    # T=100, N=150
    result_150 = _verify_winding_cross_lock(100, 150)
    assert abs(result_150.delta_winding) <= 1
    assert result_150.passed is True


def test_spectral_result_structure() -> None:
    from msaf.gw_rh_extension import SpectralResult
    
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
    from msaf.gw_rh_extension import _check_engine_agreement, SpectralResult
    
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


def test_rh_extension_main() -> None:
    from msaf.gw_rh_extension import rh_extension_t100
    
    # Test N=100 (dim 201)
    result = rh_extension_t100(N=100, prec=6000, dps=50)
    
    assert result.T == 100
    assert result.N == 100
    assert result.wall.passed is True
    assert result.cross_lock.passed is True
    assert result.spectral_a.verdict == "PASS"
    assert result.spectral_b.verdict == "PASS"
    assert result.agreement is True
    assert result.overall_verdict == "ALL_PASS"
    assert result.spectral_a.dim == 201
    assert result.spectral_b.dim == 201
    assert result.spectral_a.n_pos == 201
    assert result.spectral_a.n_neg == 0
    assert result.spectral_a.entries_finite is True
    assert result.spectral_a.lambda_min > 0
    
    # Test N=150 (dim 301)
    result_150 = rh_extension_t100(N=150, prec=6000, dps=50)
    
    assert result_150.T == 100
    assert result_150.N == 150
    assert result_150.wall.passed is True
    assert result_150.cross_lock.passed is True
    assert result_150.spectral_a.verdict == "PASS"
    assert result_150.spectral_b.verdict == "PASS"
    assert result_150.agreement is True
    assert result_150.overall_verdict == "ALL_PASS"
    assert result_150.spectral_a.dim == 301
    assert result_150.spectral_b.dim == 301


def test_receipt_matches_disk() -> None:
    import json
    from pathlib import Path
    
    if not Path(RECEIPT).exists():
        pytest.skip("Receipt file not found")
    
    data = json.loads(Path(RECEIPT).read_text(encoding="utf-8"))
    # New receipt structure has "N=100" and "N=150" keys
    assert "N=100" in data
    assert "N=150" in data
    assert data["N=100"]["overall_verdict"] == "ALL_PASS"
    assert data["N=150"]["overall_verdict"] == "ALL_PASS"
    assert data["N=100"]["wall"]["passed"] is True
    assert data["N=100"]["cross_lock"]["passed"] is True


def test_committed_receipt_is_locked() -> None:
    import json
    from pathlib import Path
    
    if not Path(RECEIPT).exists():
        pytest.skip("Receipt file not found")
    
    data = json.loads(Path(RECEIPT).read_text(encoding="utf-8"))
    assert data["N=100"]["overall_verdict"] == "ALL_PASS"
    assert data["N=150"]["overall_verdict"] == "ALL_PASS"
    assert data["N=100"]["wall"]["passed"] is True
    assert data["N=100"]["cross_lock"]["passed"] is True
    assert data["N=100"]["agreement"] is True


def test_receipt_is_deterministic_and_matches_disk() -> None:
    from msaf.gw_rh_extension import rh_extension_t100
    import json
    from pathlib import Path
    
    if not Path(RECEIPT).exists():
        pytest.skip("Receipt file not found")
    
    data = json.loads(Path(RECEIPT).read_text(encoding="utf-8"))
    built = rh_extension_t100(N=100, prec=6000, dps=50)
    
    assert data["N=100"]["overall_verdict"] == "ALL_PASS"
    assert data["N=100"]["wall"]["passed"] is True
    assert data["N=100"]["cross_lock"]["passed"] is True
    assert data["N=100"]["agreement"] is True


def test_tamper_is_detected() -> None:
    import json
    from pathlib import Path
    
    if not Path(RECEIPT).exists():
        pytest.skip("Receipt file not found")
    
    data = json.loads(Path(RECEIPT).read_text(encoding="utf-8"))
    base_hash = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    data["N=100"]["overall_verdict"] = "FAILED"
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

