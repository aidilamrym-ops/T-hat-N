# -*- coding: utf-8 -*-
"""Guard for the exact Z_N unit-permutation certificate.

The guard is deliberately exact: no float tolerance is allowed.  Tamper tests
exercise the same predicates used by the certificate builder, so a broken
check cannot pass silently.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from flint import fmpq

from msaf import zn_permutation as z

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "msaf" / "zn_permutation.py"
PREREG = ROOT / "reports" / "PREREG_ZN_PERMUTATION_2026-10-20.md"
RECEIPT = ROOT / "reports" / "zn_permutation_2026-10-20.json"


def test_locked_units_orders_and_cycles() -> None:
    assert z.units_mod(15) == [1, 2, 4, 7, 8, 11, 13, 14]
    assert z.units_mod(21) == [1, 2, 4, 5, 8, 10, 11, 13, 16, 17, 19, 20]
    assert z.multiplicative_order(15, 2) == 4
    assert z.multiplicative_order(21, 2) == 6
    assert z.cycle_decomposition(15, 2) == [[1, 2, 4, 8], [7, 14, 13, 11]]
    assert z.cycle_decomposition(21, 2) == [
        [1, 2, 4, 8, 16, 11],
        [5, 10, 20, 19, 17, 13],
    ]


def test_permutation_and_unitarity_are_exact() -> None:
    for case in z.CASES:
        n, a = case["n"], case["a"]
        units = z.units_mod(n)
        index = {x: i for i, x in enumerate(units)}
        u = z.permutation_matrix(n, a)
        assert z.is_permutation_matrix(u)
        assert z.matrix_is_identity(u.transpose() * u)
        assert z.matrix_is_identity(u * u.transpose())
        assert u.nrows() == len(units)
        assert u.ncols() == len(units)
        for x in units:
            assert z._entry_int(u[index[(a * x) % n], index[x]]) == 1


def test_order_and_minimality() -> None:
    for case in z.CASES:
        u = z.permutation_matrix(case["n"], case["a"])
        m = z.multiplicative_order(case["n"], case["a"])
        assert m == case["m"]
        assert z.matrix_is_identity(u ** m)
        for k in range(1, m):
            assert not z.matrix_is_identity(u ** k)


def test_charpoly_and_minpoly_are_locked() -> None:
    expected = {
        15: (
            [1, 0, 0, 0, -2, 0, 0, 0, 1],
            [-1, 0, 0, 0, 1],
        ),
        21: (
            [1, 0, 0, 0, 0, 0, -2, 0, 0, 0, 0, 0, 1],
            [-1, 0, 0, 0, 0, 0, 1],
        ),
    }
    for case in z.CASES:
        u = z.permutation_matrix(case["n"], case["a"])
        m = case["m"]
        multiplicity = len(z.units_mod(case["n"])) // m
        assert z.poly_coeffs(u.charpoly()) == expected[case["n"]][0]
        assert z.poly_coeffs(u.minpoly()) == expected[case["n"]][1]
        assert u.charpoly() == z.expected_charpoly(m, multiplicity)
        assert u.minpoly() == z.expected_minpoly(m)


def test_cyclotomic_factorisation_is_exact() -> None:
    for case in z.CASES:
        m = case["m"]
        multiplicity = len(z.units_mod(case["n"])) // m
        base = z.cyclotomic_product(m)
        assert base == z._x_poly() ** m - 1
        u = z.permutation_matrix(case["n"], case["a"])
        assert z.cyclotomic_check(u.charpoly(), m, multiplicity)
        assert z.factor_consistency(u.charpoly(), m)


def test_commutator_observation_and_control() -> None:
    for case in z.CASES:
        result = z.commutator_status(case["n"], case["a"])
        assert result["status"] in {"ZERO", "NONZERO"}
        assert result["control"]["status"] == "ZERO"
        assert result["control"]["tautological"] is True

        u = z.permutation_matrix(case["n"], case["a"])
        n_states = u.nrows()
        shift = z.zero_matrix(n_states)
        for i in range(n_states):
            shift[(i + 1) % n_states, i] = fmpq(1)
        commutator = shift * u - u * shift
        if result["status"] == "ZERO":
            assert z.matrix_is_zero(commutator)
        else:
            witness = result["witness"]
            assert witness["nonzero_entries"] > 0
            assert z._entry_int(commutator[witness["row"], witness["col"]]) != 0


def test_receipt_is_deterministic_and_matches_prereg() -> None:
    first = z.build_receipt()
    second = z.build_receipt()
    assert first == second
    assert z.canonical_json(first) == z.canonical_json(second)
    assert z.receipt_sha256(first) == z.receipt_sha256(second)
    assert first["verdict"] == "PASS"
    assert all(item["status"] == "PASS" for item in first["instances"])

    prereg_hash = hashlib.sha256(
        PREREG.read_bytes().replace(b"\r\n", b"\n")
    ).hexdigest()
    assert first["prereg_sha256"] == prereg_hash

    on_disk = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert on_disk == first
    assert z.receipt_sha256(on_disk) == z.receipt_sha256(first)


def test_tamper_is_detected() -> None:
    u = z.permutation_matrix(15, 2)
    assert z.is_permutation_matrix(u)
    clean_hash = z.matrix_sha256(u)

    u[0, 0] = fmpq(1)  # a zero entry; rows now sum to two
    assert not z.is_permutation_matrix(u)
    assert z.matrix_sha256(u) != clean_hash

    assert not z.poly_matches(
        z.expected_charpoly(4, 2), z.expected_charpoly(4, 1)
    )
    assert not z.poly_matches(z.expected_minpoly(6), z.expected_minpoly(4))
    assert not z.cyclotomic_check(z.expected_charpoly(4, 1), 4, 2)
    assert not z.matrix_is_identity(u ** 4)


def test_core_has_no_float_or_numpy_or_arb() -> None:
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
    assert "arb" not in imports
