"""Final audit and ledger replay: the Terminus Phase 3 kernel.

The ledger verification identity is

    V(L) = AND_j Replay(Block_j)

evaluated over every historical block. If V(L) is true, every recorded root
was generated deterministically, carries no hidden float bias, and was checked
against the causal pixel bounds.

Blueprint deviations, all measured. The Phase 3 blueprint
(`msaf_terminus_phase3.md`) recomputes the hash chain by hand with a
`"0" * 64` genesis, evaluates entropy with `float()` and `numpy.log2`, and
stores `root_string` fields that this ledger never wrote. Recomputing hashes
with a different genesis would invalidate every existing ledger, and float
entropy on 206-bit quantities is exactly the saturation artefact the project
exists to prevent. This kernel therefore reuses `Ledger.verify_chain` and
`evolution.replay` (genesis `GENESIS`, SHA-256 over the full canonical body)
and evaluates the holographic load in Arb:

    load(n) = H(n) * b(n) <= N_steps

on BOTH entropy paths, manuscript and measured. A dimension is safe only when
both paths agree it is safe; when they disagree the disagreement itself is
the finding.
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

from flint import arb

from .budget import (
    _budget_product,
    manuscript_critical_dimension,
    manuscript_entropy,
    mantissa_bits,
    measured_critical_dimension,
)
from .constants import N_STEPS
from .evolution import Ledger, replay
from .format import fmt

__all__ = [
    "CapacityVerdict",
    "holographic_capacity_check",
    "LedgerVerdict",
    "verify_ledger",
    "FinalAudit",
    "run_final_audit",
]


class CapacityVerdict(NamedTuple):
    dimension: int
    manuscript_load: arb
    measured_load: arb
    capacity: arb
    manuscript_safe: bool
    measured_safe: bool
    verdict: str

    def render(self) -> str:
        return (
            f"dimension                = {self.dimension}\n"
            f"manuscript load H*n*b    = {fmt(self.manuscript_load)}\n"
            f"measured load H*b        = {fmt(self.measured_load)}\n"
            f"universal capacity       = {fmt(self.capacity, 3)}\n"
            f"manuscript path safe     = {self.manuscript_safe}\n"
            f"measured path safe       = {self.measured_safe}\n"
            f"verdict                  = {self.verdict}"
        )


def holographic_capacity_check(dimension: int) -> CapacityVerdict:
    """Check the Shannon entropy load of dimension `n` against N_steps, in Arb.

    No float, no numpy. `dimension` is a Python int; it enters Arb through the
    exact integer constructor, never through a binary64 rounding.
    """
    n = arb(int(dimension))
    manuscript_load = manuscript_entropy(n) * mantissa_bits(n)
    measured_load = _budget_product(n)
    manuscript_safe = bool(manuscript_load < N_STEPS)
    measured_safe = bool(measured_load < N_STEPS)
    if manuscript_safe and measured_safe:
        verdict = "SAFE-COMPUTATION"
    elif not manuscript_safe and not measured_safe:
        verdict = "HOLOGRAPHIC-OVERFLOW-COLLAPSE"
    else:
        verdict = "PATH-DISAGREEMENT: manuscript and measured entropies disagree"
    return CapacityVerdict(
        dimension=int(dimension),
        manuscript_load=manuscript_load,
        measured_load=measured_load,
        capacity=N_STEPS,
        manuscript_safe=manuscript_safe,
        measured_safe=measured_safe,
        verdict=verdict,
    )


class LedgerVerdict(NamedTuple):
    path: Path
    blocks: int
    chain_intact: bool
    first_bad_chain_index: int
    reproduced: bool
    first_bad_replay_index: int
    identity_holds: bool

    def render(self) -> str:
        return (
            f"ledger                   = {self.path}\n"
            f"blocks                   = {self.blocks}\n"
            f"hash chain intact        = {self.chain_intact} "
            f"(first bad index {self.first_bad_chain_index})\n"
            f"blocks reproduced        = {self.reproduced} "
            f"(first bad index {self.first_bad_replay_index})\n"
            f"V(L)                     = {self.identity_holds}"
        )


def verify_ledger(path: Path, dimension: int) -> LedgerVerdict:
    """Evaluate V(L) for one ledger file without trusting runtime memory."""
    ledger = Ledger(Path(path)).load()
    intact, first_bad = ledger.verify_chain()
    reproduced, bad_index = replay(ledger, dimension) if intact else (False, -1)
    return LedgerVerdict(
        path=Path(path),
        blocks=len(ledger),
        chain_intact=intact,
        first_bad_chain_index=first_bad,
        reproduced=reproduced,
        first_bad_replay_index=bad_index,
        identity_holds=bool(intact and reproduced),
    )


class FinalAudit(NamedTuple):
    ledgers: tuple[LedgerVerdict, ...]
    capacities: tuple[CapacityVerdict, ...]
    sealed: bool

    def render(self) -> str:
        parts = [v.render() for v in self.ledgers] + [c.render() for c in self.capacities]
        parts.append(f"sealed = {self.sealed}")
        return "\n--\n".join(parts)


def run_final_audit(
    ledger_paths: list[Path], dimensions: list[int], replay_dimension: int
) -> FinalAudit:
    """Run the full Phase 3 audit: every ledger replayed, every dimension checked.

    The seal is granted only when every ledger identity holds AND every
    capacity check agrees on SAFE-COMPUTATION across both entropy paths.
    """
    ledger_verdicts = tuple(verify_ledger(p, replay_dimension) for p in ledger_paths)
    capacity_verdicts = tuple(holographic_capacity_check(d) for d in dimensions)
    sealed = all(v.identity_holds for v in ledger_verdicts) and all(
        c.verdict == "SAFE-COMPUTATION" for c in capacity_verdicts
    )
    return FinalAudit(
        ledgers=ledger_verdicts, capacities=capacity_verdicts, sealed=sealed
    )


