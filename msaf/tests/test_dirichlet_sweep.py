"""Tests for the exact Dirichlet conductor sweep (Track 3).

The sweep is an arithmetic audit. These tests pin the gates declared in
``reports/PREREG_CHRONO_MULTI_TRACK_2026-11-01.md``:

* only real characters enter the integer path;
* every admitted value is an exact ``fmpz`` in ``{-1, 0, +1}``;
* ``chi(n) == 0`` iff ``gcd(n, q) > 1`` for admitted characters;
* complex characters are rejected, never coerced;
* every admitted block transports into ``LaurentLogicBridgeEngine``;
* a float coefficient is a hard structural failure (negative control).
"""

from __future__ import annotations

import json
from math import gcd
from pathlib import Path

import pytest
from flint import fmpz

from msaf.chrono_runtime.dirichlet_giant_q import (
    ADMISSIBLE_INTEGER_VALUES,
    DEFAULT_MAX_N,
    DEFAULT_SWEEP_MODULI,
    audit_character,
    first_real_character,
    run_dirichlet_sweep,
    sweep_conductors,
    sweep_modulus,
)
from msaf.chrono_runtime.laurent_bridge_operator import (
    LaurentLogicBridgeEngine,
    StructuralIntegrityViolation,
)


def test_default_sweep_is_frozen_and_covers_stress_moduli() -> None:
    assert DEFAULT_MAX_N == 128
    assert DEFAULT_SWEEP_MODULI[:60] == tuple(range(1, 61))
    assert (72, 84, 120, 180, 210, 360, 420, 840, 1000) == DEFAULT_SWEEP_MODULI[60:]
    assert len(set(DEFAULT_SWEEP_MODULI)) == len(DEFAULT_SWEEP_MODULI)


def test_admissible_integer_values_are_exactly_the_three_signs() -> None:
    assert ADMISSIBLE_INTEGER_VALUES == frozenset({-1, 0, 1})


def test_sweep_includes_primitive_and_imprimitive_characters() -> None:
    report = sweep_conductors(moduli=[1, 2, 3, 4, 5, 6, 1000], max_n=16)
    assert report["primitive_total"] > 0
    assert report["imprimitive_total"] > 0
    assert report["primitive_admitted"] > 0
    assert report["imprimitive_admitted"] > 0

    per_modulus = {entry["modulus"]: entry for entry in report["per_modulus"]}
    # q=5 has an imprimitive principal character and a primitive real one.
    q5 = per_modulus[5]
    assert q5["primitive_count"] >= 1
    assert q5["imprimitive_count"] >= 1
    # q=1000 has real characters, but none of them is primitive.
    q1000 = per_modulus[1000]
    assert q1000["real_count"] > 0
    assert q1000["primitive_real_count"] == 0
    assert q1000["imprimitive_real_count"] == q1000["real_count"]
    assert q1000["admitted_count"] > 0


def test_admitted_coefficients_are_exact_fmpz_values_in_signed_unit_set() -> None:
    for modulus, number in ((1, 1), (3, 2), (5, 4), (8, 3), (1000, 249)):
        record = audit_character(modulus, number, max_n=64)
        assert record.admitted is True
        assert record.coefficients is not None
        assert len(record.coefficients) == 64
        for n, value in enumerate(record.coefficients, start=1):
            assert isinstance(value, int)
            assert value in ADMISSIBLE_INTEGER_VALUES
            # The exact extraction path used by the module must agree.
            assert int(fmpz(value)) == value
            assert (value == 0) == (gcd(n, modulus) > 1)


def test_structural_zero_gate_matches_gcd_pattern_exactly() -> None:
    for modulus in (1, 2, 3, 5, 8, 12, 30, 1000):
        for number in sorted({1, first_real_character(modulus, non_principal=False)}):
            record = audit_character(modulus, number, max_n=128)
            assert record.structural_zero_gate is True
            zeros = {n for n, v in enumerate(record.coefficients, 1) if v == 0}
            gcd_zeros = {n for n in range(1, 129) if gcd(n, modulus) > 1}
            assert zeros == gcd_zeros, (modulus, number)


def test_complex_characters_are_rejected_not_coerced() -> None:
    # q=7, number 3 has order 6 in FLINT; it must not enter the integer path.
    record = audit_character(7, 3, max_n=32)
    assert record.real is False
    assert record.admitted is False
    assert record.coefficients is None
    assert record.coefficient_sha256 is None
    assert record.bridge_residue is None
    assert record.rejection_reason is not None
    assert "not coerced" in record.rejection_reason


def test_sweep_marks_complex_characters_as_not_admitted() -> None:
    report = sweep_conductors(moduli=[7, 9, 1000], max_n=24)
    complex_records = [
        record
        for entry in report["per_modulus"]
        for record in entry["characters"]
        if not record["real"]
    ]
    assert complex_records, "expected at least one complex character"
    for record in complex_records:
        assert record["admitted"] is False
        assert record["coefficients"] is None
        assert record["rejection_reason"]
    assert report["gates"]["complex_rejected_not_coerced"] is True


def test_admitted_blocks_transport_into_the_bridge() -> None:
    record = audit_character(4, 3, max_n=16)
    assert record.admitted is True
    assert record.bridge_status == "CERTIFIED"
    assert record.bridge_residue is not None

    engine = LaurentLogicBridgeEngine([int(v) for v in record.coefficients], p=1)
    assert len(engine.coefficients) == 16
    assert engine.enclose_residues()["status"] == "CERTIFIED"


def test_float_coefficient_is_a_structural_failure() -> None:
    with pytest.raises(StructuralIntegrityViolation):
        LaurentLogicBridgeEngine([1.0, 0.0, -1.0], p=1)


def test_sweep_report_is_json_serialisable_and_scoped() -> None:
    report = sweep_conductors(moduli=[2, 3, 5, 8, 1000], max_n=16)
    text = json.dumps(report)
    assert json.loads(text)["status"] == "CERTIFIED"
    assert report["scope_notice"]["rh_claim"] is False
    assert report["scope_notice"]["grh_claim"] is False
    assert report["scope_notice"]["weil_positivity_claim"] is False
    assert report["scope_notice"]["zero_location_claim"] is False
    assert report["gates"] == {
        "exact_integer_gate": True,
        "structural_zero_gate": True,
        "complex_rejected_not_coerced": True,
        "bridge_transport_gate": True,
    }


def test_receipt_writer_is_silent_and_lands_on_requested_path(tmp_path: Path) -> None:
    target = tmp_path / "sweep.json"
    report = run_dirichlet_sweep(moduli=[2, 3, 5], max_n=8, receipt_path=target)
    assert target.is_file()
    stored = json.loads(target.read_text(encoding="utf-8"))
    assert stored["modulus_count"] == 3
    assert stored["status"] == report["status"] == "CERTIFIED"


def test_first_real_character_rejects_moduli_without_real_characters() -> None:
    assert first_real_character(3) == 2
    assert first_real_character(5) == 4
    with pytest.raises(ValueError):
        # q=2 has only the principal character, which is not non-principal.
        first_real_character(2)


def test_repeated_sweep_of_one_modulus_is_deterministic() -> None:
    first = sweep_modulus(8, max_n=32)
    second = sweep_modulus(8, max_n=32)
    assert first == second
