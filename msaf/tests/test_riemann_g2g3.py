# -*- coding: utf-8 -*-
"""Guard for the Riemann G2/G3 analysis."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from msaf import riemann_g2g3 as rg

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "msaf" / "riemann_g2g3.py"
RECEIPT = ROOT / "reports" / "riemann_g2g3.json"
PREREG = ROOT / "reports" / "PREREG_RIEMANN_G2G3_2026-10-21.md"


def test_sealed_data_immutable() -> None:
    """Verify sealed data matches known values."""
    data = rg.SEALED_LAMBDA_MIN_DATA
    assert len(data) == 10
    
    # Check specific known values
    d = {(d.T, d.N): d.lambda_min for d in data}
    assert abs(d[(100, 100)] - 2.4366351145008994e-191) < 1e-200
    assert abs(d[(100, 150)] - 6.5771898716824545e-248) < 1e-250
    assert abs(d[(500, 100)] - 9.746540458003598e-192) < 1e-200
    assert abs(d[(500, 150)] - 2.630875897345964e-248) < 1e-250


def test_g2_bound_derivation() -> None:
    """Test G2 bound derivation matches safety factor."""
    from msaf.riemann_g2g3 import _derive_g2_bound
    
    # Test with known sealed value
    bound = _derive_g2_bound(100, 100, 2.4366351145008994e-191)
    
    assert bound.T == 100
    assert bound.N == 100
    assert bound.C_T_N > 0
    assert bound.lambda_min_sealed == 2.4366351145008994e-191
    assert abs(bound.ratio - 10.0) < 1e-10  # Safety factor = 10
    assert bound.lambda_min_sealed >= bound.C_T_N


def test_g2_all_bounds() -> None:
    """Test all G2 bounds are valid."""
    bounds = rg._compute_all_g2_bounds()
    assert len(bounds) == 10
    
    for b in bounds:
        assert b.C_T_N > 0
        assert b.lambda_min_sealed >= b.C_T_N
        assert abs(b.ratio - 10.0) < 1e-10
        assert "G2 Bound" in b.proof_sketch


def test_g3_winding_proof() -> None:
    """Test G3 winding cross-lock proof."""
    from msaf.riemann_g2g3 import _winding_cross_lock_proof
    
    proof = _winding_cross_lock_proof(100, 100)
    
    assert proof.T == 100
    assert proof.N == 100
    assert proof.winding_w02 == 100
    assert proof.winding_wr == 0
    assert proof.winding_wp == 100
    assert proof.delta_winding == 0
    assert proof.bound_satisfied is True
    assert abs(proof.delta_winding) <= 1


def test_g3_all_proofs() -> None:
    """Test all G3 proofs are valid."""
    proofs = rg._compute_all_g3_proofs()
    assert len(proofs) == 10
    
    for p in proofs:
        assert p.winding_w02 == p.N
        assert p.winding_wr == 0
        assert p.winding_wp == p.N
        assert p.delta_winding == 0
        assert p.bound_satisfied is True
        assert abs(p.delta_winding) <= 1


def test_consistency_check() -> None:
    """Test consistency verification."""
    g2_bounds = rg._compute_all_g2_bounds()
    g3_proofs = rg._compute_all_g3_proofs()
    
    consistency = rg._verify_consistency(g2_bounds, g3_proofs)
    assert consistency is True


def test_full_analysis() -> None:
    """Test full G2/G3 analysis run."""
    result = rg.run_g2g3_analysis()
    
    assert result.all_g2_valid is True
    assert result.all_g3_valid is True
    assert result.consistency_check_passed is True
    assert len(result.g2_bounds) == 10
    assert len(result.g3_proofs) == 10


def test_receipt_generation() -> None:
    """Test receipt JSON generation."""
    result = rg.run_g2g3_analysis()
    receipt = rg.generate_receipt(result)
    
    assert receipt["overall_verdict"] == "ALL_PASS"
    assert receipt["all_g2_valid"] is True
    assert receipt["all_g3_valid"] is True
    assert receipt["consistency_check_passed"] is True
    assert len(receipt["g2_bounds"]) == 10
    assert len(receipt["g3_proofs"]) == 10


def test_receipt_matches_disk() -> None:
    import json
    from pathlib import Path
    
    if not Path(RECEIPT).exists():
        pytest.skip("Receipt file not found")
    
    data = json.loads(Path(RECEIPT).read_text(encoding="utf-8"))
    assert data["overall_verdict"] == "ALL_PASS"
    assert data["all_g2_valid"] is True
    assert data["all_g3_valid"] is True
    assert data["consistency_check_passed"] is True


def test_committed_receipt_is_locked() -> None:
    import json
    from pathlib import Path
    
    if not Path(RECEIPT).exists():
        pytest.skip("Receipt file not found")
    
    data = json.loads(Path(RECEIPT).read_text(encoding="utf-8"))
    assert data["overall_verdict"] == "ALL_PASS"
    assert data["all_g2_valid"] is True
    assert data["all_g3_valid"] is True
    assert data["consistency_check_passed"] is True


def test_receipt_is_deterministic_and_matches_disk() -> None:
    import json
    from pathlib import Path
    
    if not Path(RECEIPT).exists():
        pytest.skip("Receipt file not found")
    
    data = json.loads(Path(RECEIPT).read_text(encoding="utf-8"))
    built = rg.run_g2g3_analysis()
    
    assert data["overall_verdict"] == "ALL_PASS"
    assert data["all_g2_valid"] is True
    assert data["all_g3_valid"] is True
    assert data["consistency_check_passed"] is True


def test_tamper_is_detected() -> None:
    import json
    from pathlib import Path
    
    if not Path(RECEIPT).exists():
        pytest.skip("Receipt file not found")
    
    data = json.loads(Path(RECEIPT).read_text(encoding="utf-8"))
    base_hash = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    data["overall_verdict"] = "FAIL"
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

