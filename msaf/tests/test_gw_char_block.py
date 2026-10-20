# -*- coding: utf-8 -*-
"""Guard for the candidate character-aware Guinand-Weil block.

The guard is deliberately fail-closed on overclaiming.  It locks the locked
configuration, the parity map, the ``q*=1`` reduction control, the candidate
inertia numbers, the separation of the standard L-function block from the
imprimitive Dirichlet-series block, and the ``INCONCLUSIVE`` verdict.  A
future promotion to ``PASS`` must fail this guard until an independent
validation and the principal pole block exist.
"""

from __future__ import annotations

import ast
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import pytest
from flint import arb

from msaf import gw_char_block as cb

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "msaf" / "gw_char_block.py"
PREREG = ROOT / "reports" / "PREREG_GW_CHAR_BLOCK_2026-10-21.md"
RECEIPT = ROOT / "reports" / "gw_char_block_2026-10-21.json"


def test_locked_configuration() -> None:
    assert cb.SCHEMA == "msaf.gw_char_block.v1"
    assert cb.CONFIGS == (
        {"role": "primary", "c": 100, "N": 20, "prec": 600},
        {"role": "replication", "c": 200, "N": 20, "prec": 600},
    )
    assert cb.PRIMITIVE_CHARACTERS == ((4, 3), (3, 2), (5, 4))
    assert cb.NONPRIMITIVE_PARENTS == ((12, 7), (12, 5), (15, 4), (15, 11))
    assert cb.PRINCIPAL_POLE_IMPLEMENTED is False
    assert cb.INDEPENDENT_VALIDATION == "Q1_REDUCTION_ONLY"
    assert cb.Q1_CONTROL == {"c": 13, "N": 4, "prec": 200}


def test_alpha_parity_map() -> None:
    assert cb.alpha_fraction(0) == Fraction(1, 4)
    assert cb.alpha_fraction(1) == Fraction(3, 4)
    assert cb.alpha_arb(0).is_exact()
    assert cb.alpha_arb(1).is_exact()
    with pytest.raises(ValueError):
        cb.alpha_fraction(2)


def test_q1_reduction_control_reproduces_zeta_block() -> None:
    control = cb.q1_reduction_control(13, 4, 200)
    assert control["passed"] is True
    assert control["conductor"] == 1
    assert control["parity"] == 0
    assert control["alpha"] == "1/4"


def test_primary_candidate_blocks_are_finite_with_locked_inertia() -> None:
    config = cb.run_config(cb.CONFIGS[0])
    assert config["q1_reduction_control"]["passed"] is True
    standard = {
        record["identifier"]: (record["inertia"]["n_pos"], record["inertia"]["n_neg"])
        for record in config["standard_blocks"]
    }
    assert standard == {
        "chi_4_3": (4, 37),
        "chi_3_2": (6, 35),
        "chi_5_4": (16, 25),
    }
    series = {
        record["identifier"]: (record["inertia"]["n_pos"], record["inertia"]["n_neg"])
        for record in config["dirichlet_series_blocks"]
    }
    assert series == {
        "chi_12_7": (4, 37),
        "chi_12_5": (3, 38),
        "chi_15_4": (16, 25),
        "chi_15_11": (2, 39),
    }
    for record in config["standard_blocks"] + config["dirichlet_series_blocks"]:
        assert record["status"] == "PASS"
        assert record["inertia"]["entries_finite"] is True
        assert record["inertia"]["undetermined_pivot"] is None
        assert record["pole_block"] == "ZERO (non-principal)"


def test_standard_block_of_a_parent_equals_its_primitive_parent() -> None:
    with cb.adhoc._precision(600):
        base = cb.adhoc.build_base(100, 20, 600)
        parent = cb.candidate_block(base, 100, 20, 600, 12, 7, "standard")
        primitive = cb.candidate_block(base, 100, 20, 600, 4, 3, "standard")
        difference = cb.adhoc.max_abs_difference(parent["tau"], primitive["tau"])
        tolerance = arb(2) ** (-(600 - 64))
    # The standard L-function object of an imprimitive character is the
    # primitive one, so the two candidate blocks must agree to ball
    # tolerance (Arb transcendental balls are not bit-reproducible).
    assert difference <= tolerance
    assert parent["record"]["conductor"] == primitive["record"]["conductor"] == 4
    assert parent["record"]["alpha"] == primitive["record"]["alpha"] == "3/4"
    assert parent["values"] == primitive["values"]


def test_standard_and_dirichlet_series_blocks_are_separated() -> None:
    config = cb.run_config(cb.CONFIGS[0])
    for comparison in config["standard_vs_series"]:
        assert comparison["activation_count"] > 0
        assert comparison["max_abs_tau_difference"]["mid"] != "0.0"
        assert comparison["objects_are_identical"] is False
        assert comparison["standard_block"] in {"chi_4_3", "chi_3_2", "chi_5_4"}


def test_committed_receipt_is_locked() -> None:
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["schema"] == cb.SCHEMA
    assert data["execution_status"] == "PASS"
    assert data["certification_status"] == "INCONCLUSIVE"
    assert data["verdict"] == "INCONCLUSIVE"
    assert data["block_status"] == "CANDIDATE"
    assert data["candidate_result"] == "CANDIDATE NOT POSITIVE DEFINITE"
    assert data["principal_pole_status"] == "NOT IMPLEMENTED"
    assert data["independent_validation"] == "Q1_REDUCTION_ONLY"
    assert data["registry_entry"] is None
    assert all(data["checks"].values())
    assert cb.receipt_sha256(data) == (
        "25e61d7dc3e3d818b0c6978f34c4c6e123c922d0fd733cb33b86707372efa9ba"
    )
    assert data["prereg_sha256"] == hashlib.sha256(
        PREREG.read_bytes().replace(b"\r\n", b"\n")
    ).hexdigest()


def test_receipt_is_deterministic_and_matches_disk() -> None:
    built = cb.build_receipt()
    on_disk = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert cb.canonical_json(built) == cb.canonical_json(on_disk)
    assert cb.receipt_sha256(built) == cb.receipt_sha256(on_disk)


def test_tamper_is_detected() -> None:
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    base = cb.receipt_sha256(data)
    data["verdict"] = "PASS"
    assert cb.receipt_sha256(data) != base


def test_scope_flags_forbid_overclaiming() -> None:
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["scope"] == {
        "candidate_block_only": True,
        "certified_character_weil_block": False,
        "standard_l_function_block_certified": False,
        "principal_pole_included": False,
        "independent_validation_complete": False,
        "imprimitive_and_standard_identified": False,
        "critical_line_claim": False,
        "zero_localization_claim": False,
        "rh_claim": False,
        "global_positivity_claim": False,
        "factorization_claim": False,
        "sealed_campaigns_rerun": False,
    }


def test_no_promotion_without_principal_pole_and_validation() -> None:
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    # A PASS verdict would require the principal pole block and an independent
    # validation; while either is missing the verdict must stay INCONCLUSIVE.
    if not cb.PRINCIPAL_POLE_IMPLEMENTED:
        assert data["verdict"] != "PASS"
        assert data["certification_status"] == "INCONCLUSIVE"
    if cb.INDEPENDENT_VALIDATION != "COMPLETE":
        assert data["scope"]["certified_character_weil_block"] is False


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
