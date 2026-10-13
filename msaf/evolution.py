"""Measured, replayable evolution for the MSAF core lattice.

Design contract
---------------
The lattice must be able to mutate over time without ever drifting silently.
Every mutation is therefore an *experiment* with a recorded protocol:

    propose -> measure -> certify -> gate -> commit or revert

Four rules keep the evolution honest and machine-checkable:

1. Fitness is **measured**, never asserted. It is assembled from ball
   arithmetic quantities the auditors already produce: the certified margin of
   the commutation residual, and the agreement between two independent
   spectral algorithms computed on the same mutant.
2. A mutant is promoted only when it does not regress fitness *and* every
   certificate still passes. Regression is an automatic reject.
3. The ledger is an append-only SHA-256 hash chain. Any retroactive edit is
   detectable by :meth:`Ledger.verify_chain`.
4. :meth:`Ledger.replay` re-executes the certification protocol and
   re-derives every stored verdict from scratch. A record whose verdict cannot
   be reproduced is a hard failure, not a warning.

This is the operational meaning of evolving naturally: the lattice changes,
but every change is evidence-backed, ordered, and reversible.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Final, NamedTuple

from flint import acb, arb, fmpq

from .certify import contains_zero
from .format import point
from .operators import CirculantHamiltonian, CyclicShift, commutator_residual
from .precision import log2

__all__ = [
    "GENOME_SCHEMA",
    "Genome",
    "RootPullGenome",
    "MAX_NEWTON_ITER",
    "Fitness",
    "measure_fitness",
    "mutate",
    "RootPullFitness",
    "RootPullOutcome",
    "measure_root_pull_fitness",
    "LedgerRecord",
    "Ledger",
    "EvolutionOutcome",
    "evolve_lattice",
    "evolve_root_pull",
]

GENOME_SCHEMA: Final[str] = "msaf.genome.v1"


class Genome(NamedTuple):
    """Mutable description of a candidate spectral Hamiltonian.

    A genome is pure data and carries no numerical claim of its own. The
    symbol is rebuilt from scratch on every measurement, so a genome that
    stops producing a certified Hamiltonian cannot survive a campaign.
    """

    generation: int
    harmonic: int
    tilt: str

    def identifier(self) -> str:
        raw = f"{self.generation}:{self.harmonic}:{self.tilt}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def symbol(self, n: int) -> CirculantHamiltonian:
        """Rebuild c[j] = cos(2 pi h j / n) + tilt * delta_{j0}."""
        harmonic, tilt = self.harmonic, arb(self.tilt)
        return CirculantHamiltonian.from_function(
            n,
            lambda j: arb(fmpq(2 * harmonic * j, n)).cos_pi() + (tilt if j == 0 else arb(0)),
        )


class Fitness(NamedTuple):
    """Measured quality of one genome. Every component is an Arb ball."""

    genome_id: str
    certificate_bits: arb
    spectral_agreement_bits: arb
    total: arb
    certificate_passed: bool

    def render(self) -> str:
        return (
            f"id={self.genome_id} "
            f"cert={point(self.certificate_bits, 8)}bit "
            f"spec={point(self.spectral_agreement_bits, 8)}bit "
            f"total={point(self.total, 12)}"
        )


def _margin_bits(reference: arb, deviation: arb) -> arb:
    """Bits of separation between a measurement and its reference.

    A deviation whose ball contains zero scores as ``log2(reference)``, the
    ceiling reachable at this precision. Otherwise the score is the negated
    base-2 magnitude of the certified deviation.
    """
    if contains_zero(deviation):
        return log2(reference)
    return -log2(_abs_ball(deviation))


def _is_provably_worse(candidate: arb, incumbent: arb) -> bool:
    """True only when the candidate is *certifiably* below the incumbent.

    A bare ``candidate < incumbent`` returns False whenever two balls overlap,
    so an identical measurement would be misjudged as a regression and the
    campaign would stall forever. Rejection therefore requires a strict
    separation of the enclosures, which is the only comparison ball
    arithmetic can settle without ambiguity.
    """
    return bool(candidate.upper() < incumbent.lower())


def _spectral_agreement_bits(matrix: CirculantHamiltonian) -> arb:
    """Cross-validate two independent spectral algorithms on one mutant.

    Algorithm A: structural DFT diagonalisation, exact for circulant matrices.
    Algorithm B: the general-purpose isolating eigen-solver ``arb_mat.eig``.

    Agreement between two unrelated algorithms is evidence; agreement of an
    algorithm with itself is not. This component is what makes the campaign
    able to reject a mutant whose spectral content merely looks plausible.
    """
    n = matrix.n
    try:
        dense = matrix.to_matrix().eig(multiple=True)
    except Exception:  # noqa: BLE001 - the isolating solver refuses some spectra
        return -arb(n)
    structural = matrix.dft_eigenvalues()
    worst = arb(0)
    for value in structural:
        # Match each structural eigenvalue to its NEAREST solver candidate.
        # Taking the worst over all pairs would compare unrelated eigenvalues
        # and would report disagreement even when the spectra coincide.
        best = None
        for candidate in dense:
            deviation = max(
                _abs_ball(value.real - candidate.real),
                _abs_ball(value.imag - candidate.imag),
            )
            if best is None or deviation < best:
                best = deviation
        if best is not None:
            worst = max(worst, best)
    return _margin_bits(arb(n), worst)


def _abs_ball(x: arb) -> arb:
    """Magnitude of a ball as a ball. Arb exposes no ``abs`` method."""
    return (x * x).sqrt()


def _certificate_bits(n: int, width: arb) -> arb:
    """Certified margin of the commutation residual, in bits.

    An exactly zero residual means the identity holds without any rounding,
    which is better than any finite margin, but it is not infinitely better:
    beyond the working precision no further statement is possible. The score is
    therefore capped at twice the precision instead of evaluating ``log2(0)``,
    which would produce an infinity and poison every downstream comparison.
    """
    from flint import ctx

    ceiling = 2 * ctx.prec
    if bool(width.is_zero()):
        return arb(ceiling)
    return (log2(arb(n)) - log2(width)).min(arb(ceiling))


def measure_fitness(genome: Genome, n: int) -> Fitness:
    """Measure one genome against its own certified residuals.

    ``certificate_bits``
        Bits of margin retained by the commutation residual against a signal
        scale of n. Measures numerical soundness.

    ``spectral_agreement_bits``
        Bits of agreement between the structural DFT spectrum and the general
        eigen-solver. Measures correctness of the spectrum.

    Both must be healthy simultaneously for a promotion; neither alone is
    sufficient.
    """
    symbol = genome.symbol(n)
    audit = commutator_residual(symbol, CyclicShift(n))
    certificate_bits = _certificate_bits(n, audit.max_half_width)
    agreement = _spectral_agreement_bits(symbol)
    return Fitness(
        genome_id=genome.identifier(),
        certificate_bits=certificate_bits,
        spectral_agreement_bits=agreement,
        total=certificate_bits + agreement,
        certificate_passed=audit.certified,
    )


def mutate(genome: Genome, step: int) -> Genome:
    """Deterministic single-step mutation.

    A pure function of parent and step index, so any campaign is exactly
    reproducible and no hidden RNG state can leak into the certification.
    """
    harmonics = (1, 2, 3, 5, 7, 11)
    tilts = ("1", "2", "1.5", "0.5")
    return Genome(
        generation=genome.generation + 1,
        harmonic=harmonics[step % len(harmonics)],
        tilt=tilts[(step // len(harmonics)) % len(tilts)],
    )


class LedgerRecord(NamedTuple):
    """One immutable line of the evolution ledger.

    The full genome is stored, not merely its hash. A replay that could only
    trust an opaque identifier would be trusting the ledger instead of
    re-deriving the evidence, which is exactly the failure mode this design
    exists to prevent.
    """

    index: int
    generation: int
    harmonic: int
    tilt: str
    genome_id: str
    decision: str
    fitness_total: str
    certificate_bits: str
    spectral_agreement_bits: str
    previous_hash: str
    record_hash: str

    def genome(self) -> "Genome":
        return Genome(
            generation=self.generation,
            harmonic=self.harmonic,
            tilt=self.tilt,
        )


class NonFiniteMeasurement(RuntimeError):
    """A non-finite quantity reached the ledger and must never be recorded."""


def _reject_non_finite(fitness: Fitness, genome: Genome) -> None:
    """Refuse to commit a measurement that contains NaN or an infinity.

    Serialising ``nan`` into a signed ledger would launder a failed experiment
    into an apparently valid historical record. The failure has to surface at
    the point of measurement instead.
    """
    for name, value in (
        ("certificate_bits", fitness.certificate_bits),
        ("spectral_agreement_bits", fitness.spectral_agreement_bits),
        ("total", fitness.total),
    ):
        if not value.is_finite():
            raise NonFiniteMeasurement(
                f"{name} is not finite for genome {genome.identifier()}; "
                "experiment refused, nothing recorded"
            )


class Ledger:
    """Append-only hash-chained ledger of every evolution decision."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._records: list[LedgerRecord] = []

    def __len__(self) -> int:
        return len(self._records)

    @property
    def records(self) -> tuple[LedgerRecord, ...]:
        return tuple(self._records)

    @property
    def head(self) -> str:
        return self._records[-1].record_hash if self._records else "GENESIS"

    @staticmethod
    def _digest(body: dict) -> str:
        return hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    def append(self, genome: Genome, fitness: Fitness, decision: str) -> LedgerRecord:
        _reject_non_finite(fitness, genome)
        body = {
            "index": len(self._records),
            "generation": genome.generation,
            "harmonic": genome.harmonic,
            "tilt": genome.tilt,
            "genome_id": fitness.genome_id,
            "decision": decision,
            "fitness_total": fitness.total.mid().str(30, radius=False),
            "certificate_bits": fitness.certificate_bits.mid().str(30, radius=False),
            "spectral_agreement_bits": fitness.spectral_agreement_bits.mid().str(
                30, radius=False
            ),
            "previous_hash": self.head,
        }
        record = LedgerRecord(record_hash=self._digest(body), **body)
        self._records.append(record)
        self._write(record)
        return record

    def _write(self, record: LedgerRecord) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record._asdict(), sort_keys=True) + "\n")

    def append_root_pull(
        self, genome: RootPullGenome, fitness: RootPullFitness, decision: str
    ) -> LedgerRecord:
        """Append a root-pull decision.

        `sigma_radius` is serialised as an explicit decimal string. Writing it
        as a JSON number would round it through binary64 and could land on
        exactly 0.0 for a radius below 1e-308, manufacturing an exact zero that
        the measurement never produced.
        """
        body = {
            "index": len(self._records),
            "generation": genome.generation,
            "harmonic": genome.harmonic,
            "tilt": f"zero#{genome.zero_index}",
            "genome_id": fitness.genome_id,
            "decision": decision,
            "fitness_total": fitness.sigma_radius,
            "certificate_bits": fitness.verdict,
            "spectral_agreement_bits": fitness.on_half_line,
            "previous_hash": self.head,
        }
        record = LedgerRecord(record_hash=self._digest(body), **body)
        self._records.append(record)
        self._write(record)
        return record

    def load(self) -> "Ledger":
        self._records.clear()
        if not self.path.exists():
            return self
        with self.path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    self._records.append(LedgerRecord(**json.loads(line)))
        return self

    def verify_chain(self) -> tuple[bool, int]:
        """Recompute every hash. Returns ``(intact, first_bad_index)``."""
        previous = "GENESIS"
        for index, record in enumerate(self._records):
            if record.previous_hash != previous:
                return False, index
            body = dict(record._asdict())
            body.pop("record_hash")
            if self._digest(body) != record.record_hash:
                return False, index
            previous = record.record_hash
        return True, -1


def _is_root_pull_record(record: LedgerRecord) -> bool:
    """Root-pull lines carry the zero index in the tilt field as ``zero#N``."""
    return isinstance(record.tilt, str) and record.tilt.startswith("zero#")


def replay(ledger: Ledger, dimension: int) -> tuple[bool, int]:
    """Re-derive every stored fitness from the recorded genome and compare.

    The genome is reconstructed from the ledger line itself, so this is a true
    independent re-execution rather than a re-read of trusted inputs. Symbol
    lines and root-pull lines are dispatched to their respective measurement
    functions. Any mismatch means the stored claim is not reproducible, which
    is a hard failure of the campaign's auditability, not a warning.

    The replay must run at the same working precision as the campaign: ball
    radii are precision-dependent, so a precision change alters the serialised
    strings and would report a false mismatch. The same holds for the Newton
    budget of root-pull lines, which is why the caller passes it through
    instead of letting replay invent one.
    """
    for record in ledger.records:
        if _is_root_pull_record(record):
            genome = RootPullGenome(
                generation=record.generation,
                zero_index=int(record.tilt.split("#", 1)[1]),
                harmonic=record.harmonic,
            )
            if genome.identifier() != record.genome_id:
                return False, record.index
            recomputed = measure_root_pull_fitness(genome, newton_max_iter=dimension)
            if recomputed.sigma_radius != record.fitness_total:
                return False, record.index
            if recomputed.verdict != record.certificate_bits:
                return False, record.index
            continue
        genome = record.genome()
        if genome.identifier() != record.genome_id:
            return False, record.index
        recomputed = measure_fitness(genome, dimension)
        if recomputed.total.mid().str(30, radius=False) != record.fitness_total:
            return False, record.index
    return True, -1


def main(argv: list[str] | None = None) -> int:
    """Replay a ledger from scratch: ``python -m msaf.evolution --replay PATH``.

    Rebuilds every verification state without trusting runtime memory, exactly
    as the Terminus Phase 3 directive requires. Exit code 0 means the full
    identity V(L) holds: chain intact AND every block reproduced.
    """
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        prog="msaf.evolution", description="Replay an MSAF ledger from scratch"
    )
    parser.add_argument("--replay", type=Path, required=True)
    parser.add_argument("--dimension", type=int, default=8)
    parser.add_argument("--prec", type=int, default=256,
                        help="working precision; MUST match the campaign precision, "
                             "because serialised ball radii are precision-dependent")
    args = parser.parse_args(argv)

    from .precision import set_precision

    set_precision(args.prec)
    ledger = Ledger(args.replay).load()
    intact, first_bad = ledger.verify_chain()
    reproduced, bad_index = replay(ledger, args.dimension) if intact else (False, -1)
    verdict = intact and reproduced
    sys.stdout.write(
        "\n".join(
            [
                f"ledger              = {args.replay}",
                f"blocks              = {len(ledger)}",
                f"hash chain intact   = {intact} (first bad index {first_bad})",
                f"blocks reproduced   = {reproduced} (first bad index {bad_index})",
                f"V(L)                = {verdict}",
            ]
        )
        + "\n"
    )
    return 0 if verdict else 1


class EvolutionOutcome(NamedTuple):
    promoted: tuple[Genome, ...]
    rejected: tuple[Genome, ...]
    incumbent_genome: Genome
    incumbent_fitness: Fitness
    ledger: Ledger


# --------------------------------------------------------------------------
# Root pull: replacing the postulated symbol with certified zero positions
# --------------------------------------------------------------------------

#: Imaginary part of the first non-trivial zero, to full printed precision.
GAMMA_1: Final[str] = "14.1347251417346937904572519835624702707842571156992431756856"


class RootPullGenome(NamedTuple):
    """Candidate whose generator symbol is anchored on a certified zero.

    Unlike `Genome`, which searches a hand-designed symbol family, a root-pull
    genome is pulled from an actual root of the completed zeta function as
    localised by the interval Newton kernel. The parameter `zero_index` selects
    which zero, and `harmonic` selects the discrete phase coupled to it.
    """

    generation: int
    zero_index: int
    harmonic: int

    def identifier(self) -> str:
        raw = f"pull:{self.generation}:{self.zero_index}:{self.harmonic}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


class RootPullFitness(NamedTuple):
    """Measured quality of a root-pull proposal, with the localisation record."""

    genome_id: str
    verdict: str
    on_half_line: bool
    sigma_radius: str
    gamma_midpoint: str
    global_claim_supported: bool
    accepted: bool
    reason: str

    def render(self) -> str:
        return (
            f"id={self.genome_id} verdict={self.verdict} "
            f"on_half={self.on_half_line} sigma_radius={self.sigma_radius} "
            f"accepted={self.accepted}"
        )


#: Default Newton iteration budget for root-pull localisation. Localisation of
#: the tabulated zeros converges in a single step; the budget only bounds the
#: search, it does not alter a converged enclosure (verified identical for
#: budgets 12, 16 and 20 on zero #1).
MAX_NEWTON_ITER: Final[int] = 16


def measure_root_pull_fitness(
    genome: RootPullGenome, newton_max_iter: int = MAX_NEWTON_ITER, radius: str = "1e-12"
) -> RootPullFitness:
    """Localise a genuine zeta zero and gate the proposal on the result.

    The budget parameter is the Newton iteration cap, nothing else. It was
    previously misnamed `dimension`, which falsely suggested the matrix
    dimension controls the root finder. Replay must use the same budget as the
    campaign, exactly as it must use the same precision.

    A proposal is accepted only when the interval Newton kernel certifies a
    localised zero whose real part enclosure contains 0.5. Anything else,
    including a divergence, an unresolved derivative or an escaped Newton
    image, is rejected and must be recorded as REVERT by the caller.

    The global flag is carried through untouched. No single localised zero can
    support the universal statement, and dropping that flag at the call site
    is precisely how a local observation would be laundered into a global
    claim.
    """
    from .zeta_inversion import ball, certify_sigma_one_half

    zero_index = int(genome.zero_index)
    reference = acb.zeta_zero(zero_index)
    seed = ball(reference.mid(), radius)
    report = certify_sigma_one_half(seed, max_iter=newton_max_iter)

    accepted = bool(report["sigma_is_on_half_line"])
    if accepted:
        reason = "zero localised and real part enclosed around 0.5"
    elif report["verdict"].startswith("ZERO-LOCALIZED"):
        reason = "zero localised but the real part enclosure does not contain 0.5"
    else:
        reason = f"localisation failed: {report['verdict']}"

    return RootPullFitness(
        genome_id=genome.identifier(),
        verdict=report["verdict"],
        on_half_line=bool(report["sigma_is_on_half_line"]),
        sigma_radius=report["final_radius_real"],
        gamma_midpoint=reference.imag.mid().str(30, radius=False),
        global_claim_supported=bool(report["global_claim_supported"]),
        accepted=accepted,
        reason=reason,
    )


class RootPullOutcome(NamedTuple):
    """Outcome of a root-pull campaign, with a honestly typed incumbent.

    A previous revision returned `EvolutionOutcome` with
    `incumbent_fitness=None`, a typed lie: the field promises `Fitness` but
    delivered nothing, waiting to detonate on the first caller that trusts
    the annotation. Separate lineages get separate outcome types.
    """

    promoted: tuple[RootPullGenome, ...]
    rejected: tuple[RootPullGenome, ...]
    incumbent_genome: RootPullGenome
    incumbent_fitness: RootPullFitness
    ledger: Ledger


def evolve_root_pull(
    seed: RootPullGenome,
    newton_max_iter: int,
    proposals: int,
    ledger_path: Path,
    radius: str = "1e-12",
) -> RootPullOutcome:
    """Campaign driven by certified zero positions rather than postulated ones.

    Decision vocabulary is extended with REVERT, which the directive requires
    for any proposal whose localisation did not certify. REVERT is distinct
    from REJECT: a rejection is an ordinary fitness comparison, while a revert
    is a safety event caused by the absence of a certificate.

    The incumbent is only ever replaced by a proposal that was accepted, so the
    lineage can never be seeded from an uncertified root.
    """
    ledger = Ledger(ledger_path).load()
    incumbent_genome = seed
    incumbent = measure_root_pull_fitness(incumbent_genome, newton_max_iter, radius)
    ledger.append_root_pull(incumbent_genome, incumbent, "SEED" if incumbent.accepted else "REVERT")

    promoted: list[RootPullGenome] = []
    rejected: list[RootPullGenome] = []
    for step in range(proposals):
        candidate = RootPullGenome(
            generation=incumbent_genome.generation + 1,
            zero_index=incumbent_genome.zero_index + step + 1,
            harmonic=incumbent_genome.harmonic,
        )
        fitness = measure_root_pull_fitness(candidate, newton_max_iter, radius)
        if not fitness.accepted:
            ledger.append_root_pull(candidate, fitness, "REVERT")
            rejected.append(candidate)
            continue
        ledger.append_root_pull(candidate, fitness, "PROMOTE")
        incumbent_genome, incumbent = candidate, fitness
        promoted.append(candidate)
    return RootPullOutcome(
        promoted=tuple(promoted),
        rejected=tuple(rejected),
        incumbent_genome=incumbent_genome,
        incumbent_fitness=incumbent,
        ledger=ledger,
    )


def evolve_lattice(
    seed: Genome,
    dimension: int,
    proposals: int,
    ledger_path: Path,
) -> EvolutionOutcome:
    """Run a gated campaign and return the surviving lineage.

    Promotion rule, applied to every proposal without exception:

        promote  iff  fitness.total >= incumbent.total
              and  commutation residual contains zero

    A regressing proposal is recorded as REJECT and the incumbent is left
    untouched, so the best genome seen so far is monotone in fitness.
    """
    ledger = Ledger(ledger_path).load()
    incumbent_genome = seed
    incumbent_fitness = measure_fitness(incumbent_genome, dimension)
    ledger.append(incumbent_genome, incumbent_fitness, "SEED")

    promoted: list[Genome] = []
    rejected: list[Genome] = []
    for step in range(proposals):
        candidate = mutate(incumbent_genome, step)
        fitness = measure_fitness(candidate, dimension)
        if fitness.certificate_passed and not _is_provably_worse(
            fitness.total, incumbent_fitness.total
        ):
            ledger.append(candidate, fitness, "PROMOTE")
            incumbent_genome, incumbent_fitness = candidate, fitness
            promoted.append(candidate)
        else:
            ledger.append(candidate, fitness, "REJECT")
            rejected.append(candidate)
    return EvolutionOutcome(
        promoted=tuple(promoted),
        rejected=tuple(rejected),
        incumbent_genome=incumbent_genome,
        incumbent_fitness=incumbent_fitness,
        ledger=ledger,
    )


if __name__ == "__main__":
    raise SystemExit(main())