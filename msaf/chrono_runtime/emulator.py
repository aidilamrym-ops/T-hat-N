"""Discrete Chronon emulator.

Every transition mirrors a Lean declaration in
``ChronoGeometric_Framework/lean/ChronoNat.lean``:

* ``ChronoState.advance_shape`` -- the new shape is ``line old point``;
* ``ChronoState.advance_time``  -- the chronon advances by one;
* ``ChronoState.collapse_to_harmony_eq`` -- a ``space`` at a successor time
  collapses to ``point``.

The emulator never reads the system clock. A tick is an integer carried by the
state, and its lattice phase is ``tick mod N_STEPS``. Each transition emits a
certificate; exact discrete transitions carry radius zero and are labelled
``EXACT-DISCRETE`` rather than presented as a hard numerical enclosure.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from msaf.chrono_runtime import lattice
from msaf.chrono_runtime.shape_ops import (
    Shape,
    leaf_count,
    line,
    point,
    shape_to_obj,
)

__all__ = [
    "ChronoState",
    "Certificate",
    "SimulationResult",
    "state_hash",
    "step",
    "collapse",
    "simulate",
]

CERTIFICATE_SCHEMA = "msaf.chrono_runtime.certificate.v1"


def _canonical(payload: object) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _sha256(payload: object) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


@dataclass(frozen=True)
class ChronoState:
    value: int
    shape: Shape
    tick: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int) or isinstance(self.value, bool):
            raise TypeError("value must be an int")
        if self.value < 0:
            raise ValueError(f"value must be non-negative, got {self.value}")
        if not isinstance(self.shape, Shape):
            raise TypeError("shape must be a Shape")
        if not isinstance(self.tick, int) or isinstance(self.tick, bool):
            raise TypeError("tick must be an int")
        if self.tick < 0:
            raise ValueError(f"tick must be non-negative, got {self.tick}")


def state_hash(state: ChronoState) -> str:
    """Deterministic hash of a state, including the full shape tree."""
    return _sha256(
        {
            "value": state.value,
            "shape": shape_to_obj(state.shape),
            "tick": state.tick,
        }
    )


@dataclass(frozen=True)
class Certificate:
    rule_id: str
    tick: int
    phase: int
    value: int
    leaf_count: int
    prev_state_hash: str
    state_hash: str
    observable_name: str
    observable_mid: str
    observable_rad: str
    kind: str
    lean_decl: str | None
    anchor_status: str
    anchor_reason: str | None = None
    run_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema": CERTIFICATE_SCHEMA,
            "rule_id": self.rule_id,
            "tick": self.tick,
            "phase": self.phase,
            "value": self.value,
            "leaf_count": self.leaf_count,
            "prev_state_hash": self.prev_state_hash,
            "state_hash": self.state_hash,
            "observable": {
                "name": self.observable_name,
                "mid": self.observable_mid,
                "rad": self.observable_rad,
            },
            "kind": self.kind,
            "lean_decl": self.lean_decl,
            "anchor_status": self.anchor_status,
            "run_id": self.run_id,
        }
        if self.anchor_reason is not None:
            payload["anchor_reason"] = self.anchor_reason
        return payload


def step(state: ChronoState, run_id: str = "") -> tuple[ChronoState, Certificate]:
    """One ``ChronoState.advance``: value fixed, shape grows, tick advances."""
    before = leaf_count(state.shape)
    new_state = ChronoState(
        value=state.value,
        shape=line(state.shape, point()),
        tick=state.tick + 1,
    )
    after = leaf_count(new_state.shape)
    if after != before + 1:  # pragma: no cover - structural invariant
        raise RuntimeError(
            f"advance invariant violated: {after} != {before} + 1"
        )
    certificate = Certificate(
        rule_id="CHRONO-ADVANCE",
        tick=new_state.tick,
        phase=lattice.phase(new_state.tick),
        value=new_state.value,
        leaf_count=after,
        prev_state_hash=state_hash(state),
        state_hash=state_hash(new_state),
        observable_name="leaf_count",
        observable_mid=str(after),
        observable_rad="0",
        kind="EXACT-DISCRETE",
        lean_decl="ChronoState.advance_shape",
        anchor_status="ANCHORED",
        run_id=run_id,
    )
    return new_state, certificate


def collapse(state: ChronoState, run_id: str = "") -> tuple[ChronoState, Certificate]:
    """Mirror ``ChronoState.collapse_to_harmony``.

    A ``space`` shape at a successor time becomes a ``point``; everything else
    is left unchanged. The rule is structural, not numerical.
    """
    applies = state.shape.tag == "space" and state.tick >= 1
    new_state = (
        ChronoState(value=state.value, shape=point(), tick=state.tick)
        if applies
        else state
    )
    certificate = Certificate(
        rule_id="CHRONO-COLLAPSE",
        tick=new_state.tick,
        phase=lattice.phase(new_state.tick),
        value=new_state.value,
        leaf_count=leaf_count(new_state.shape),
        prev_state_hash=state_hash(state),
        state_hash=state_hash(new_state),
        observable_name="leaf_count",
        observable_mid=str(leaf_count(new_state.shape)),
        observable_rad="0",
        kind="EXACT-DISCRETE",
        lean_decl="ChronoState.collapse_to_harmony_eq",
        anchor_status="ANCHORED",
        run_id=run_id,
    )
    return new_state, certificate


@dataclass(frozen=True)
class SimulationResult:
    initial: ChronoState
    final: ChronoState
    certificates: tuple[Certificate, ...]

    @property
    def invariants_hold(self) -> bool:
        delta = self.final.tick - self.initial.tick
        return (
            self.final.value == self.initial.value
            and leaf_count(self.final.shape) - leaf_count(self.initial.shape) == delta
            and self.final.tick == self.initial.tick + len(self.certificates)
        )


def simulate(
    initial: ChronoState, steps: int, run_id: str = ""
) -> SimulationResult:
    """Run ``steps`` advances and fail closed if any invariant breaks."""
    if not isinstance(steps, int) or isinstance(steps, bool):
        raise TypeError("steps must be an int")
    if steps < 0:
        raise ValueError(f"steps must be non-negative, got {steps}")

    state = initial
    certificates: list[Certificate] = []
    for _ in range(steps):
        state, certificate = step(state, run_id=run_id)
        certificates.append(certificate)

    result = SimulationResult(
        initial=initial,
        final=state,
        certificates=tuple(certificates),
    )
    if not result.invariants_hold:  # pragma: no cover - structural invariant
        raise RuntimeError("simulation invariants violated")
    return result
