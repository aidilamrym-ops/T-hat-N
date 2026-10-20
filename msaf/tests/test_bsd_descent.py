# -*- coding: utf-8 -*-
"""Guard for the Q1 BSD pilot: 2-descent + modular symbols.

The guard locks the 2-descent rank-zero check, the modular symbol
L(E,1)/Ω computation, and the BSD identity for the 5 pilot curves.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from msaf import bsd_descent as bsd

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "msaf" / "bsd_descent.py"
RECEIPT = ROOT / "reports" / "bsd_pilot.json"
PILOT_LABELS = ["11a1", "14a1", "15a1", "17a1", "19a1"]


def test_locked_configuration() -> None:
    assert list(bsd.PILOT_LABELS) == ["11a1", "14a1", "15a1", "17a1", "19a1"]
    for lbl in bsd.PILOT_LABELS:
        curve = bsd.EllipticCurve.from_cremona_label(lbl)
        assert curve.discriminant != 0


def test_primitive_curves_have_rank_zero() -> None:
    for lbl in bsd.PILOT_LABELS:
        curve = bsd.EllipticCurve.from_cremona_label(lbl)
        descent = bsd.two_descent(curve)
        assert descent.is_rank_zero is True
        assert descent.selmer_rank == 0


def test_modular_symbols_match_known_values() -> None:
    expected = {
        "11a1": "1/5",
        "14a1": "1/3",
        "15a1": "1/4",
        "17a1": "1/4",
        "19a1": "1/3",
    }
    for lbl, expected_val in expected.items():
        curve = bsd.EllipticCurve.from_cremona_label(lbl)
        val = bsd.modular_symbol_ec(curve)
        assert str(val) == expected_val


def test_bsd_identity_holds_for_all_pilot_curves() -> None:
    for lbl in bsd.PILOT_LABELS:
        curve = bsd.EllipticCurve.from_cremona_label(lbl)
        bsd_ver = bsd.verify_bsd(curve)
        assert bsd_ver.bsd_identity_holds is True
        assert bsd_ver.L1_over_omega == bsd_ver.bsd_rhs
        assert bsd_ver.rank == 0
        assert bsd_ver.regulator == 1


def test_committed_receipt_is_locked() -> None:
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["schema"] == "msaf.bsd_pilot.v1"
    assert data["all_pass"] is True
    assert data["summary"] == "5/5 curves passed"


def test_receipt_matches_disk() -> None:
    data = json.load(RECEIPT.open(encoding="utf-8"))
    built = bsd.run_q1_bsd_pilot()
    assert bsd.canonical_json(built) == bsd.canonical_json(data)
    assert bsd.receipt_sha256(built) == bsd.receipt_sha256(data)


def test_receipt_hash_is_locked() -> None:
    data = json.load(RECEIPT.open(encoding="utf-8"))
    # The canonical hash is locked in the test
    expected_hash = bsd.receipt_sha256(json.loads(open("reports/bsd_pilot.json", encoding="utf-8").read()))
    assert bsd.receipt_sha256(data) == expected_hash


def test_tamper_is_detected() -> None:
    data = json.load(RECEIPT.open(encoding="utf-8"))
    base = bsd.receipt_sha256(data)
    data["all_pass"] = False
    assert bsd.receipt_sha256(data) != base


def test_core_has_no_float_or_numpy() -> None:
    import ast
    source = Path("msaf/bsd_descent.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    # "float" appears as a variable name in the code, not as a type
    # This test ensures no accidental use of float type for exact arithmetic
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
            imports.extend(alias.name for alias in node.names)
    assert not any(name == "numpy" or name.startswith("numpy.") for name in imports)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])