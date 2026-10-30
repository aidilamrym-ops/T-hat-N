"""Tests for the exact lattice, the discrete emulator, and the Shape bridge."""

from __future__ import annotations

import ast
import json
from fractions import Fraction
from pathlib import Path

import pytest

from msaf.precision import DEFAULT_PRECISION_BITS, set_precision

set_precision(DEFAULT_PRECISION_BITS)

from msaf.chrono_runtime import emulator, lattice  # noqa: E402
from msaf.chrono_runtime import shape_ops as so  # noqa: E402
from msaf.bridge.chrono_bridge import (  # noqa: E402
    OFF_DIAGONAL_GUARD,
    build_operators,
    verify_commutation,
)

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_SOURCES = (
    ROOT / "msaf" / "chrono_runtime" / "lattice.py",
    ROOT / "msaf" / "chrono_runtime" / "shape_ops.py",
    ROOT / "msaf" / "chrono_runtime" / "emulator.py",
    ROOT / "msaf" / "chrono_runtime" / "riemann_operator.py",
    ROOT / "msaf" / "chrono_runtime" / "ledger.py",
    ROOT / "msaf" / "bridge" / "chrono_bridge.py",
)


def _shape_with_leaves(count: int) -> so.Shape:
    shape = so.point()
    for _ in range(count - 1):
        shape = so.line(shape, so.point())
    return shape


def test_n_steps_is_the_exact_grid_floor() -> None:
    assert lattice.N_STEPS == 54446853992717733278474003174004102075476951347404957757284586
    assert lattice.check_exact_integer()
    assert len(str(lattice.N_STEPS)) == 62
    assert lattice.N_STEPS.bit_length() == 206


def test_tick_seconds_is_an_exact_fraction() -> None:
    expected = Fraction(1616255, 10**41 * 299792458)
    assert lattice.TICK_SECONDS == expected
    assert isinstance(lattice.TICK_SECONDS, Fraction)
    assert lattice.HORIZON_SECONDS == Fraction(lattice.N_STEPS) * expected
    assert isinstance(lattice.HORIZON_SECONDS, Fraction)


def test_phase_wraps_and_rejects_negative_ticks() -> None:
    assert lattice.phase(0) == 0
    assert lattice.phase(3) == 3
    assert lattice.phase(lattice.N_STEPS + 3) == 3
    assert lattice.wrap(2 * lattice.N_STEPS + 7) == 7
    with pytest.raises(ValueError):
        lattice.phase(-1)
    with pytest.raises(TypeError):
        lattice.phase("1")  # type: ignore[arg-type]


def test_no_float_and_no_system_clock_in_runtime_sources() -> None:
    issues: list[str] = []
    for path in RUNTIME_SOURCES:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, float):
                issues.append(f"{path.name}:{node.lineno}: float literal")
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "float"
            ):
                issues.append(f"{path.name}:{node.lineno}: float() call")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in {"time", "datetime"}:
                        issues.append(
                            f"{path.name}:{node.lineno}: import {alias.name}"
                        )
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module.split(".")[0] in {"time", "datetime"}:
                    issues.append(
                        f"{path.name}:{node.lineno}: from {node.module}"
                    )
    assert not issues, "\n".join(issues)


def test_flatten_mirrors_the_four_lean_equations() -> None:
    p = so.point()
    assert so.flatten(p) == (1,)
    assert so.flatten(so.line(p, p)) == (1, 1)
    assert so.flatten(so.plane(p, p, p)) == (1, 1, 1)
    nested = so.space(so.line(p, so.plane(p, p, p)), p)
    assert so.flatten(nested) == (1, 1, 1, 1, 1)
    assert so.leaf_count(nested) == 5
    assert json.loads(json.dumps(so.shape_to_obj(nested))) is not None


def test_empty_space_is_rejected() -> None:
    with pytest.raises(ValueError):
        build_operators(so.space())


def test_emulator_invariants_and_certificate_chain() -> None:
    initial = emulator.ChronoState(value=7, shape=so.point(), tick=0)
    result = emulator.simulate(initial, steps=17, run_id="unit-test")

    assert result.invariants_hold
    assert result.final.value == 7
    assert result.final.tick == 17
    assert so.leaf_count(result.final.shape) == 18

    previous_hash = emulator.state_hash(initial)
    for index, certificate in enumerate(result.certificates, start=1):
        assert certificate.tick == index
        assert certificate.phase == index % lattice.N_STEPS
        assert certificate.leaf_count == index + 1
        assert certificate.kind == "EXACT-DISCRETE"
        assert certificate.anchor_status == "ANCHORED"
        assert certificate.lean_decl == "ChronoState.advance_shape"
        assert certificate.prev_state_hash == previous_hash
        assert certificate.to_dict()["schema"] == "msaf.chrono_runtime.certificate.v1"
        previous_hash = certificate.state_hash

    assert result.certificates[-1].state_hash == emulator.state_hash(result.final)


def test_collapse_rule_matches_lean() -> None:
    empty_space = so.space()
    state = emulator.ChronoState(value=3, shape=empty_space, tick=1)
    collapsed, certificate = emulator.collapse(state)
    assert collapsed.shape.tag == "point"
    assert collapsed.value == 3
    assert collapsed.tick == 1
    assert certificate.rule_id == "CHRONO-COLLAPSE"


def test_collapse_is_identity_when_guard_does_not_apply() -> None:
    at_zero = emulator.ChronoState(value=3, shape=so.space(), tick=0)
    unchanged, _ = emulator.collapse(at_zero)
    assert unchanged == at_zero

    point_state = emulator.ChronoState(value=3, shape=so.point(), tick=5)
    unchanged, _ = emulator.collapse(point_state)
    assert unchanged == point_state


def test_bridge_builds_exact_circulants_and_a_tautological_guard() -> None:
    shape = _shape_with_leaves(17)
    operators = build_operators(shape)
    assert operators.dim == 17
    assert operators.h_is_symmetric
    assert operators.t_is_permutation
    assert operators.commutes_exactly
    assert so.is_circulant(operators.h_hat)
    assert so.is_circulant(operators.t_hat)

    certificate = verify_commutation(shape)
    assert certificate.commutes_exactly
    assert certificate.commutation_residual_is_zero
    assert certificate.kind == "CONSTRUCTION-GUARD"
    assert certificate.tautological_by_construction is True
    assert certificate.lean_decl is None
    assert certificate.anchor_status == "UNANCHORED"
    assert certificate.h_off_diagonal_upper.upper() < OFF_DIAGONAL_GUARD
    assert certificate.t_off_diagonal_upper.upper() < OFF_DIAGONAL_GUARD
    assert certificate.h_diagonal_deviation.upper() < OFF_DIAGONAL_GUARD
    assert certificate.t_unit_modulus_deviation.upper() < OFF_DIAGONAL_GUARD
    assert certificate.dft_guard_passed

    payload = certificate.to_dict()
    assert payload["tautological_by_construction"] is True
    assert "CONSTRUCTION-GUARD" in payload["kind"]
