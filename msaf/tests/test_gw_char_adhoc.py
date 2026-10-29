# -*- coding: utf-8 -*-
"""Guard for the AD HOC zeta-block perturbation experiment.

The experiment is deliberately labelled ad hoc.  The guard locks the local
zeta-builder control, the activation terms, the interval inertia at the
primary configuration, the separation of execution status from mathematical
verdict, and the no-overclaim scope flags.  The optional external control is
skipped when the published builder is not available.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path

import pytest
from flint import arb, arb_mat, ctx

from msaf import gw_char_adhoc as a

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "msaf" / "gw_char_adhoc.py"
PREREG = ROOT / "reports" / "PREREG_GW_CHAR_ADHOC_2026-10-21.md"
RECEIPT = ROOT / "reports" / "gw_char_adhoc_2026-10-21.json"


def test_locked_configuration() -> None:
    assert a.SCHEMA == "msaf.gw_char_adhoc.v1"
    assert a.CONFIGS == (
        {"role": "primary", "c": 100, "N": 20, "prec": 600},
        {"role": "replication", "c": 200, "N": 20, "prec": 600},
    )
    assert a.CHARACTERS == ((12, 7), (12, 5), (15, 4), (15, 11))
    assert a.prime_powers_up_to(10) == [(2, 2), (3, 3), (4, 2), (5, 5), (7, 7), (8, 2), (9, 3)]


def test_local_zeta_builder_self_consistency() -> None:
    with a._precision(200):
        base = a.build_base(50, 5, 200)
        values = {q: 1 for q, _ in base["pdata"]}
        wp = a.wp_from_values(base, values)
        tau = a.tau_from_wp(base, wp)
        assert a.max_abs_difference(wp, base["Wp_zeta"]) <= arb(2) ** (-160)
        assert a.max_abs_difference(tau, base["tau_zeta"]) <= arb(2) ** (-160)
        record = a.inertia_record(base["tau_zeta"])
        assert record["entries_finite"] is True
        assert record["pivots_recorded"] == base["dim"]


def test_activation_terms_are_exact() -> None:
    expected_counts = {
        (12, 7): 4,
        (12, 5): 6,
        (15, 4): 4,
        (15, 11): 2,
    }
    for modulus, number in a.CHARACTERS:
        q_star, n_star, _ = a.chars.primitive_lift(modulus, number)
        values = a.character_values(modulus, number, 100)
        lift_values = a.character_values(q_star, n_star, 100)
        terms = a.activation_terms(modulus, q_star, values, lift_values)
        assert len(terms) == expected_counts[(modulus, number)]
        assert all(term["value"] == 0 and term["lift_value"] != 0 for term in terms)
        assert all((values[q] == 0) == (__import__("math").gcd(q, modulus) > 1) for q in values)
        assert all((lift_values[q] == 0) == (__import__("math").gcd(q, q_star) > 1) for q in lift_values)


def test_primary_configuration_inertia_is_locked() -> None:
    config = a.run_config(a.CONFIGS[0])
    assert config["dim"] == 41
    assert config["baseline_zeta"]["n_pos"] == 41
    assert config["baseline_zeta"]["n_neg"] == 0
    assert config["baseline_zeta"]["status"] == "POSITIVE DEFINITE"
    expected = {
        "chi_12_7": ((17, 24), (20, 21)),
        "chi_12_5": ((16, 25), (21, 20)),
        "chi_15_4": ((19, 22), (20, 21)),
        "chi_15_11": ((16, 25), (19, 22)),
    }
    for case in config["cases"]:
        primitive = (case["primitive"]["n_pos"], case["primitive"]["n_neg"])
        nonprimitive = (case["nonprimitive"]["n_pos"], case["nonprimitive"]["n_neg"])
        assert primitive == expected[case["identifier"]][0]
        assert nonprimitive == expected[case["identifier"]][1]
        assert case["status"] == "PASS"
        assert case["primitive"]["status"] == "NOT POSITIVE DEFINITE"
        assert case["nonprimitive"]["status"] == "NOT POSITIVE DEFINITE"


def test_interval_inertia_signs() -> None:
    with a._precision(200):
        identity = arb_mat(2, 2)
        identity[0, 0] = arb(1)
        identity[1, 1] = arb(1)
        assert a.inertia_record(identity)["status"] == "POSITIVE DEFINITE"
        negative = arb_mat(1, 1)
        negative[0, 0] = arb(-1)
        assert a.inertia_record(negative)["status"] == "NOT POSITIVE DEFINITE"
        zero = arb_mat(1, 1)
        zero[0, 0] = arb(0)
        assert a.inertia_record(zero)["status"] == "INCONCLUSIVE"


def test_external_control_if_available() -> None:
    with a._precision(200):
        base = a.build_base(50, 5, 200)
        control = a.external_control(base)
    if not control["available"]:
        pytest.skip("published external builder is not available")
    assert control["match"] is True
    assert control["status"] == "MATCH"


def test_small_campaign_is_deterministic() -> None:
    first = a.run_config({"role": "test", "c": 50, "N": 5, "prec": 200})
    second = a.run_config({"role": "test", "c": 50, "N": 5, "prec": 200})
    assert a.canonical_json(first) == a.canonical_json(second)


def test_receipt_matches_disk() -> None:
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    # Check if external builder is available in the current environment
    # (not just whether the committed receipt had it available)
    import sys
    from pathlib import Path
    GW_DIR = Path(os.environ.get("GW_DIR", r"C:/Users/usER/oracle-toe/GUINAND_WEIL"))
    if str(GW_DIR) not in sys.path:
        sys.path.insert(0, str(GW_DIR))
    try:
        import source_arb_ldlt_certify  # type: ignore
        external_available = True
    except Exception:
        external_available = False
    
    if not external_available:
        pytest.skip("external builder source_arb_ldlt_certify not available in this environment")
    
    first = a.build_receipt()
    assert a.canonical_json(first) == a.canonical_json(data)
    assert a.receipt_sha256(first) == a.receipt_sha256(data)


def test_committed_receipt_is_locked() -> None:
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["schema"] == a.SCHEMA
    assert data["execution_status"] == "PASS"
    assert data["mathematical_verdict"] == "AD HOC NEGATIVE"
    assert data["verdict"] == "AD HOC NEGATIVE"
    assert data["external_control"] == {
        "available": True,
        "match": True,
        "status": "MATCH",
    }
    assert a.receipt_sha256(data) == (
        "76e43dac29f299cd7ec222bbf5bafce74850d1b6a24a33046f2b3ea9676093c1"
    )
    assert data["prereg_sha256"] == hashlib.sha256(
        PREREG.read_bytes().replace(b"\r\n", b"\n")
    ).hexdigest()
    for config in data["configs"]:
        assert config["baseline_zeta"]["status"] == "POSITIVE DEFINITE"
        assert config["baseline_zeta"]["n_pos"] == 41
        assert config["baseline_zeta"]["n_neg"] == 0
        for case in config["cases"]:
            assert case["status"] == "PASS"
            assert case["activation_count"] > 0
            assert case["primitive"]["undetermined_pivot"] is None
            assert case["nonprimitive"]["undetermined_pivot"] is None
            assert case["primitive"]["status"] == "NOT POSITIVE DEFINITE"
            assert case["nonprimitive"]["status"] == "NOT POSITIVE DEFINITE"


def test_tamper_is_detected() -> None:
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    base = a.receipt_sha256(data)
    data["mathematical_verdict"] = "AD HOC POSITIVE"
    assert a.receipt_sha256(data) != base


def test_scope_flags_forbid_overclaiming() -> None:
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["scope"] == {
        "ad_hoc_perturbation": True,
        "correct_character_weil_block": False,
        "zeta_pole_block_reused": True,
        "zeta_archimedean_block_reused": True,
        "global_claim_supported": False,
        "standard_l_function_claim": False,
        "dirichlet_series_claim": False,
        "critical_line_claim": False,
        "zero_localization_claim": False,
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
    assert not any(name == "mpmath" or name.startswith("mpmath.") for name in imports)


