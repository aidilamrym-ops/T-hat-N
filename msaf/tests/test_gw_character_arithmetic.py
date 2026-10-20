# -*- coding: utf-8 -*-
"""Guard for the exact Dirichlet-character arithmetic certificate.

The guard is deliberately exact: every character value is an integer, every
coprimality test is integer arithmetic, and no tolerance is used.  It also
checks that the certificate refuses to promote a non-real candidate into a
real lift and that the scope flags cannot silently turn the arithmetic result
into an L-function or critical-line claim.
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path

import pytest
from flint import dirichlet_char

from msaf import gw_character_arithmetic as g

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "msaf" / "gw_character_arithmetic.py"
PREREG = ROOT / "reports" / "PREREG_GW_CHARACTER_ARITHMETIC_2026-10-21.md"
RECEIPT = ROOT / "reports" / "gw_character_arithmetic_2026-10-21.json"


def test_locked_configuration() -> None:
    assert g.CUTOFF == 200
    assert len(g.INSTANCES) == 5
    assert [item["modulus"] for item in g.INSTANCES] == [12, 12, 15, 15, 12]
    assert [item["number"] for item in g.INSTANCES] == [7, 5, 4, 11, 1]
    assert g.candidate_numbers(1) == [1]
    assert g.candidate_numbers(12) == [1, 5, 7, 11]


def test_exact_values_and_structural_zero() -> None:
    expected_12_7 = {
        1: 1,
        2: 0,
        3: 0,
        4: 0,
        5: 1,
        6: 0,
        7: -1,
        8: 0,
        9: 0,
        10: 0,
        11: -1,
        12: 0,
    }
    for item in g.INSTANCES:
        modulus = int(item["modulus"])
        number = int(item["number"])
        chi = dirichlet_char(modulus, number)
        for n in range(1, g.CUTOFF + 1):
            value = g.exact_value(chi, n)
            assert value in (-1, 0, 1)
            assert (value == 0) == (math.gcd(n, modulus) > 1)
        if (modulus, number) == (12, 7):
            assert {n: g.exact_value(chi, n) for n in range(1, 13)} == expected_12_7


def test_primitive_lift_and_minimality() -> None:
    expected = {
        (12, 7): (4, 3),
        (12, 5): (3, 2),
        (15, 4): (5, 4),
        (15, 11): (3, 2),
        (12, 1): (1, 1),
    }
    for item in g.INSTANCES:
        modulus = int(item["modulus"])
        number = int(item["number"])
        q_star, n_star, chi_star = g.primitive_lift(modulus, number)
        assert (q_star, n_star) == expected[(modulus, number)]
        assert chi_star.is_primitive() is True
        assert int(chi_star.conductor()) == q_star
        target = {
            unit: g.exact_value(dirichlet_char(modulus, number), unit)
            for unit in g.candidate_numbers(modulus)
        }
        assert g._smaller_matching_modulus(modulus, target, q_star) is None


def test_new_prime_activation() -> None:
    expected_new = {
        (12, 7): (3,),
        (12, 5): (2,),
        (15, 4): (3,),
        (15, 11): (5,),
        (12, 1): (2, 3),
    }
    for item in g.INSTANCES:
        result = g.certify_instance(item)
        key = (int(item["modulus"]), int(item["number"]))
        assert tuple(result["new_primes"]) == expected_new[key]
        assert result["activation_count"] > 0
        assert result["checks"]["C3_activation"] is True
        assert result["status"] == "PASS"

    # Concrete activation witnesses: coefficient zero, primitive parent nonzero.
    assert g.exact_value(dirichlet_char(12, 7), 3) == 0
    assert g.exact_value(dirichlet_char(4, 3), 3) == -1
    assert g.exact_value(dirichlet_char(12, 5), 2) == 0
    assert g.exact_value(dirichlet_char(3, 2), 2) == -1
    assert g.exact_value(dirichlet_char(15, 4), 3) == 0
    assert g.exact_value(dirichlet_char(5, 4), 3) == -1
    assert g.exact_value(dirichlet_char(15, 11), 5) == 0
    assert g.exact_value(dirichlet_char(3, 2), 5) == -1
    assert g.exact_value(dirichlet_char(12, 1), 2) == 0
    assert g.exact_value(dirichlet_char(1, 1), 2) == 1


def test_prime_power_table_is_locked() -> None:
    expected = {
        "chi_12_7": ("f0e23d1be9ed55120a095cf2f43f58e621f0728ef778732d70576d51660d688f", "43eae80f81f4376f1065e3da65a469554bc774aba668b3c2e5066c81772f6008"),
        "chi_12_5": ("e190df42e564d161de08950dbb10e0bf53a6272c84cb2ab49c63b54325307c47", "4fc212ce7ae0c53046b3268e16d74184697cf8083a08ae06583a82cb995cb2d5"),
        "chi_15_4": ("a70f405a39e74ef29dc46322ce8673a53e021f58c223ed231dc63810c7ab89b5", "2002a45ccdecac13c5d1eae3e97814ebb3a32307e119373a6646ea3e7d46636e"),
        "chi_15_11": ("f0f9753fa9997617e5daaa4fb8fc07c3c37f4a755e15668146f51c5a2b21c314", "b4451a0c7f312b4a27d6f292d1c51783c4c535d054a14fb9941760e8470da5c3"),
        "chi_12_1": ("062d62fc2ba0e6753ead94b329efc0d37b5763113d87bc9cf41400b027145e99", "3f86eafafc37e1546c1efd6571153a928b4b378335c089dff8d1c6679464dd93"),
    }
    for item in g.INSTANCES:
        result = g.certify_instance(item)
        identifier = result["identifier"]
        assert result["table_sha256"] == expected[identifier][0]
        assert result["prime_power_table_sha256"] == expected[identifier][1]
        rows = {row["q_k"]: row for row in result["prime_power_rows"]}
        assert rows[2]["prime"] == 2
        assert rows[4]["exponent"] == 2
        assert rows[8]["exponent"] == 3
        assert any(row["new_zero_active"] for row in result["prime_power_rows"])


def test_nonreal_candidate_is_not_accepted_as_real_lift() -> None:
    complex_character = dirichlet_char(5, 2)
    with pytest.raises(g.CharacterArithmeticError):
        g.exact_value(complex_character, 2)
    # The complex character must not match the real chi_15_4 table.
    target = {
        unit: g.exact_value(dirichlet_char(15, 4), unit)
        for unit in g.candidate_numbers(15)
    }
    assert g._matches_real(complex_character, target) is False


def test_failure_is_fail_closed() -> None:
    item = dict(g.INSTANCES[0])
    item["expected_conductor"] = 999
    result = g.certify_instance(item)
    assert result["checks"]["C1_metadata"] is False
    assert result["status"] == "FAILED"


def test_receipt_is_deterministic_and_matches_disk() -> None:
    first = g.build_receipt()
    second = g.build_receipt()
    assert g.canonical_json(first) == g.canonical_json(second)
    assert g.receipt_sha256(first) == g.receipt_sha256(second)
    assert first["verdict"] == "PASS"
    assert all(instance["status"] == "PASS" for instance in first["instances"])
    assert first["prereg_sha256"] == hashlib.sha256(
        PREREG.read_bytes().replace(b"\r\n", b"\n")
    ).hexdigest()
    on_disk = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert on_disk == first


def test_committed_receipt_is_locked() -> None:
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["schema"] == g.SCHEMA
    assert data["cutoff"] == 200
    assert data["verdict"] == "PASS"
    assert g.receipt_sha256(data) == (
        "cfd966c5795d3e0b7e0009ee89f80e9b26592745e0a6b0c08f430b24d4473eb2"
    )
    assert all(item["status"] == "PASS" for item in data["instances"])
    assert all(all(item["checks"].values()) for item in data["instances"])
    assert all(item["smaller_matching_modulus"] is None for item in data["instances"])


def test_tamper_is_detected() -> None:
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    base = g.receipt_sha256(data)
    data["verdict"] = "TAMPERED"
    assert g.receipt_sha256(data) != base


def test_scope_flags_forbid_overclaiming() -> None:
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["scope"] == {
        "character_arithmetic_only": True,
        "guinand_weil_matrix_constructed": False,
        "l_function_object_selected": False,
        "standard_l_function_zero_claim": False,
        "dirichlet_series_zero_claim": False,
        "critical_line_claim": False,
        "rh_claim": False,
        "factorization_claim": False,
        "sealed_campaigns_rerun": False,
    }


def test_core_has_no_float_or_numpy() -> None:
    source = MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    assert "float" not in names
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
            imports.extend(alias.name for alias in node.names)
    assert not any(name == "numpy" or name.startswith("numpy.") for name in imports)
