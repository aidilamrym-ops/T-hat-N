"""MSAF core lattice: cyclic-shift operator, quantized von Mangoldt map, and
commutation audit.

This module is the executable transcription of the operative axioms:

    Axiom 1  Finite grid            N_steps = D_obs / l_P, discrete arithmetic only.
    Axiom 2  Rigid circulant algebra  T unitary cyclic shift, [H, T] = 0 certified.
    Axiom 3  Tail-error elimination   truncation residual certified to contain zero.
    Axiom 4  Shannon / underflow bound mantissa budget and critical dimension.

Zero-Fudging mandate
--------------------
A ball arithmetic residual is never exactly zero at finite precision. The
only admissible certificate for a zero claim is ``residual.contains(0)``,
never ``residual == 0`` and never ``float(residual) == 0``. Every identity
in this module is reported through :func:`verify_commutation` or
:func:`verify_truncation`, both of which use containment.

Non-triviality gate
-------------------
``[H, T] = 0`` holds for *every* circulant Hamiltonian by an algebraic
identity, independent of any numerical content. A verifier that returns a bare
PASS for it is therefore lying by omission. :func:`verify_commutation`
additionally classifies the residual as TRIVIAL or NON-TRIVIAL so that a
structural tautology can never be laundered into evidence.

Language policy
---------------
Code, identifiers, docstrings and comments are English by standing
instruction. Prose reports to the researcher are Indonesian.
"""

from __future__ import annotations

import sys
from typing import Final, NamedTuple, Sequence

from flint import arb, arb_mat, ctx, fmpz

from msaf.certify import MANDATE, contains_zero, is_exact_zero, matrix_residual_width
from msaf.constants import ELL_P
from msaf.precision import (
    DEFAULT_PRECISION_BITS,
    PrecisionLandmine,
    audit_precision_landmines,
    current_precision,
    set_precision,
)

__all__ = [
    "MANDATE",
    "MAX_MATERIALISED_DIMENSION",
    "PrecisionProfile",
    "initialize_precision",
    "LatticeDimensionViolation",
    "generate_shift_operator",
    "apply_cyclic_shift",
    "is_prime_power",
    "quantized_von_mangoldt",
    "manuscript_log_kernel",
    "von_mangoldt_log_kernel",
    "is_circulant",
    "CommutationAudit",
    "verify_commutation",
    "TruncationAudit",
    "verify_truncation",
    "verify_unitarity",
]


# --------------------------------------------------------------------------
# 1. Initialization of precision
# --------------------------------------------------------------------------

MAX_MATERIALISED_DIMENSION: Final[int] = 4096
"""Hard ceiling for dense matrix materialisation.

N_steps is 5.4e61, so an N x N dense representation is not a performance
problem but a structurally impossible one. Requests beyond this ceiling are
rejected loudly instead of attempting an allocation that will exhaust memory.
"""


class PrecisionProfile(NamedTuple):
    """Immutable record of the precision state at the moment of use."""

    bits: int
    contamination: tuple[str, ...]
    lattice_unit: arb

    def render(self) -> str:
        return (
            f"arb precision   = {self.bits} bit\n"
            f"contamination   = {self.contamination or 'none'}\n"
            f"lattice unit    = {self.lattice_unit.mid().str(24, radius=False)} m"
        )


def initialize_precision(bits: int = DEFAULT_PRECISION_BITS) -> PrecisionProfile:
    """Establish a deterministic, contamination-checked global Arb precision.

    Landmine guarded here: ``mpmath.mp.dps`` is a process-global precision
    mutator. Importing mpmath transitively (via sympy, scipy, matplotlib, or
    any package depending on them) can silently re-scale the numeric
    behaviour of the whole process. Any such module already resident at the
    time of this call is reported in the returned profile so that the caller
    can refuse the analysis.

    The call is idempotent. Re-requesting a *different* precision raises
    ``PrecisionLandmine`` rather than silently renegotiating: global precision
    must never drift mid-analysis.
    """
    contamination = audit_precision_landmines()
    set_precision(bits)
    return PrecisionProfile(
        bits=current_precision(),
        contamination=contamination,
        lattice_unit=ELL_P,
    )


# --------------------------------------------------------------------------
# 2. Unitary cyclic shift matrix generator
# --------------------------------------------------------------------------


class LatticeDimensionViolation(MemoryError):
    """A dense matrix was requested beyond the materialisation ceiling."""


def generate_shift_operator(n: int) -> arb_mat:
    """Build the genuine n x n unitary cyclic shift operator T as ``arb_mat``.

    Convention: ``T e_j = e_{(j+1) mod n}``, so that the matrix has ones on the
    sub-diagonal with a wrap-around one in the bottom-left corner. Under this
    convention:

        T @ T.dag = I        (unitarity, exact zero residual)
        T**n      = I        (periodicity, exact zero residual)
        T**a @ T**b = T**(a+b)  (single generator => T and every circulant H commute)

    The entries are the exact rationals 0 and 1, so both certificates above
    have *exactly* zero residuals at any precision. That is a genuine
    difference from generic floating-point shift matrices and must be
    preserved: never route these entries through ``float``.

    Raises ``LatticeDimensionViolation`` when n exceeds
    ``MAX_MATERIALISED_DIMENSION``.
    """
    n = int(n)
    if n < 1:
        raise ValueError(f"n must be positive, got {n}")
    if n > MAX_MATERIALISED_DIMENSION:
        raise LatticeDimensionViolation(
            f"dimension {n} exceeds the materialisation ceiling "
            f"{MAX_MATERIALISED_DIMENSION}; use apply_cyclic_shift instead"
        )
    t = arb_mat(n, n)
    for i in range(n):
        t[(i + 1) % n, i] = arb(1)
    return t


def apply_cyclic_shift(vector: Sequence[arb], steps: int = 1) -> list[arb]:
    """Apply the shift operator to a vector in O(n) time and O(n) memory.

    This is the structural alternative to a dense N x N operator and is the
    only representation that scales towards N_steps. ``steps`` may be any
    integer; it is reduced modulo n so the result is periodic.
    """
    v = list(vector)
    n = len(v)
    if n < 1:
        raise ValueError("vector must be non-empty")
    shift = int(steps) % n
    return [v[(i - shift) % n] for i in range(n)]


# --------------------------------------------------------------------------
# 3. Discrete von Mangoldt lattice mapping
# --------------------------------------------------------------------------


def is_prime_power(k: int) -> bool:
    """True iff the integer k is p^m with p prime and m >= 1.

    Exact integer test via FLINT factorisation. ``k <= 1`` is rejected because
    0 and 1 are perfect powers in the algebraic sense but are not prime
    powers in the number-theoretic sense.
    """
    z = fmpz(int(k))
    if z <= 1:
        return False
    factors = z.factor()
    if len(factors) != 1:
        return False
    prime, _exponent = factors[0]
    return bool(prime.is_prime())


def quantized_von_mangoldt(k: int) -> arb:
    """Evaluate the quantized von Mangoldt function Lambda_d(k).

    Definition implemented (Manuscript Section 2.2):

        Lambda_d(k) = ln(p)   if the pixel index k is an exact prime power p^m
                    = 0      for every other pixel index

    Dimensional normalisation, stated explicitly because the manuscript does
    not. The manuscript condition ``k * l_P == p^m`` compares a *length* with
    a *dimensionless* integer, which is a category error. The only reading
    that is operationally computable inside MSAF is that ``l_P`` is the *unit*
    of the pixel: then ``k * l_P`` is a length whose integer measure is k,
    and the admissible test is whether that integer measure is a prime power.
    This function therefore tests the integer index.

    Guarantees that matter for zero-fudging:

    * the non-prime-power branch returns an **exact** ``arb(0)``, never NaN;
    * the prime-power branch returns ``ln(p)`` as a ball whose radius is the
      honest transcendental rounding error, not a rounded float;
    * no intermediate ever passes through ``float`` or ``math.log``.

    Landmine fixed here: the manuscript kernel ``log(Lambda_d(k) + delta)``
    evaluates ``log(0)`` on every non-prime-power pixel and therefore returns
    NaN across the bulk of the grid. :func:`manuscript_log_kernel` reproduces
    that defect on purpose; :func:`von_mangoldt_log_kernel` is the repair.
    """
    if is_prime_power(k):
        factors = fmpz(int(k)).factor()
        prime = factors[0][0]
        return arb(prime).log()
    return arb(0)


def manuscript_log_kernel(k: int) -> arb:
    """Reproduce the manuscript kernel ``log(Lambda_d(k) + delta_{k,1})``.

    Retained only as a regression fixture. For every pixel index that is not
    a prime power the argument is zero and FLINT returns NaN, which then
    propagates through the whole discrete Fourier transform. Calling this in
    a spectral pipeline is a defect, not a computation.
    """
    shifted = quantized_von_mangoldt(k) + (arb(1) if k == 1 else arb(0))
    return shifted.log()


def von_mangoldt_log_kernel(k: int) -> arb:
    """NaN-free replacement kernel ``log(1 + Lambda_d(k))``.

    The additive unit inside the logarithm keeps the argument strictly
    positive on every pixel, so the transform over the whole grid is
    well defined and every entry is a finite ball.
    """
    return (arb(1) + quantized_von_mangoldt(k)).log()


# --------------------------------------------------------------------------
# 4. Commutative constraint audit
# --------------------------------------------------------------------------


class CommutationAudit(NamedTuple):
    """Full, non-launderable verdict on the constraint [H, T] = 0."""

    label: str
    dimension: int
    precision_bits: int
    residual: arb_mat
    contains_zero: bool
    max_half_width: arb
    exact_zero_entries: int
    total_entries: int
    structurally_guaranteed: bool
    verdict: str
    mandate: str

    @property
    def passes(self) -> bool:
        return self.contains_zero

    @property
    def carries_information(self) -> bool:
        """False when the vanishing follows from circulant algebra alone."""
        return self.passes and not self.structurally_guaranteed

    def render(self) -> str:
        return (
            f"{self.label}\n"
            f"  dimension            = {self.dimension}\n"
            f"  precision            = {self.precision_bits} bit\n"
            f"  residual contains 0  = {self.contains_zero}\n"
            f"  max half width       = {self.max_half_width.mid().str(12, radius=False)}\n"
            f"  exact zero entries   = {self.exact_zero_entries}/{self.total_entries}\n"
            f"  structurally trivial = {self.structurally_guaranteed}\n"
            f"  verdict              = {self.verdict}\n"
            f"  mandate              = {self.mandate}"
        )


def is_circulant(matrix: arb_mat) -> bool:
    """Structural circulant test: ``M[i][j] == M[0][(j - i) mod n]``.

    Verified on exact entry identities where available, and by certified
    containment otherwise. Used to detect tautological commutation before a
    PASS is allowed to count as evidence.
    """
    rows, cols = matrix.nrows(), matrix.ncols()
    if rows != cols:
        return False
    n = rows
    for i in range(n):
        for j in range(n):
            if not contains_zero(matrix[i, j] - matrix[0, (j - i) % n]):
                return False
    return True


def _entry_zero_stats(m: arb_mat) -> tuple[int, int]:
    total = m.nrows() * m.ncols()
    exact = sum(
        1
        for i in range(m.nrows())
        for j in range(m.ncols())
        if is_exact_zero(m[i, j])
    )
    return exact, total


def verify_commutation(h_matrix: arb_mat, t_matrix: arb_mat) -> CommutationAudit:
    """Rigid zero-fudging audit of the constraint [H, T] = 0.

    Computes the commutator ``H @ T - T @ H`` as ball arithmetic and certifies
    the result by containment of zero, never by equality. A residual that
    happens to be a pure radius still passes, and that is the correct
    outcome: the identity is satisfied in exact arithmetic and the residual
    width is the honest accumulated rounding error at the working precision.

    Additionally classifies the result. When ``h_matrix`` is circulant the
    commutation is an algebraic tautology, so ``carries_information`` is
    False and the verdict is downgraded to TRIVIAL. This is deliberate: the
    constraint cannot be used as evidence for anything about zeta zeros.
    """
    if h_matrix.nrows() != h_matrix.ncols():
        raise ValueError("h_matrix must be square")
    if h_matrix.nrows() != t_matrix.nrows():
        raise ValueError(
            f"dimension mismatch: H is {h_matrix.nrows()}, T is {t_matrix.nrows()}"
        )
    residual = h_matrix * t_matrix - t_matrix * h_matrix
    contains = all(
        contains_zero(residual[i, j])
        for i in range(residual.nrows())
        for j in range(residual.ncols())
    )
    exact_entries, total = _entry_zero_stats(residual)
    trivial = is_circulant(h_matrix)
    if not contains:
        verdict = "FAIL: residual does not contain zero"
    elif trivial:
        verdict = "TRIVIAL: vanishes by circulant algebra, carries no information"
    elif exact_entries == total:
        verdict = "PASS-EXACT: residual is exact zero at every entry"
    else:
        verdict = "PASS-BY-ENCLOSURE: zero lies inside the residual ball"
    return CommutationAudit(
        label="[H,T] commutation audit",
        dimension=h_matrix.nrows(),
        precision_bits=current_precision(),
        residual=residual,
        contains_zero=contains,
        max_half_width=matrix_residual_width(residual),
        exact_zero_entries=exact_entries,
        total_entries=total,
        structurally_guaranteed=trivial,
        verdict=verdict,
        mandate=MANDATE,
    )


class TruncationAudit(NamedTuple):
    """Audit of a claimed analytic truncation residual."""

    label: str
    tail_bound: arb
    contains_zero: bool
    is_identically_zero: bool
    underdetermined: bool
    verdict: str

    def render(self) -> str:
        return f"{self.label}\n  verdict = {self.verdict}"


def verify_truncation(
    tail_bound: arb,
    positive_evidence: arb | None = None,
    label: str = "truncation residual",
) -> TruncationAudit:
    """Audit a claimed analytic truncation residual such as ``l_P * exp(-N_steps)``.

    The manuscript asserts ``E_trunc == 0``. In ball arithmetic this is an
    *imposition*, not a derivation: ``l_P * exp(-N_steps)`` is a strictly
    positive real number that simply is not representable.

    Measured finding: ``l_P * exp(-N_steps)`` is NOT unrepresentable in Arb. The
    Arb exponent is an arbitrary-precision integer, so the value survives with a
    strictly positive lower endpoint and about 21 bits of relative accuracy at a
    256-bit working precision. A ``float64`` would underflow to zero here, which
    is precisely why a naive implementation can mistake a representable
    positive bound for a vanishing one.

    Four outcomes are distinguished and must never be conflated:

    ``IDENTICAL-ZERO``
        The quantity is the exact rational zero; nothing is lost.
    ``NOT-ZERO``
        The ball has a strictly positive lower endpoint, so it certifies
        non-vanishing and a claim of exact vanishing is an imposition.
    ``UNDERDETERMINED``
        The ball contains zero without being the exact zero. Such an enclosure
        can certify NEITHER vanishing nor non-vanishing, and any reported zero
        from it is a formatting artefact.
    ``NOT-ZERO (external evidence)``
        An underdetermined ball, but ``positive_evidence`` independently proves
        strict positivity. Used for quantities such as exponentials whose
        logarithm stays representable while the value does not.

    Pass ``positive_evidence=log(tail_bound)`` for any exponential quantity so
    that the audit can never mistake a precision artefact for a proof.
    """
    identical = bool(tail_bound.is_exact()) and bool(tail_bound.is_zero())
    certifies_nonzero = tail_bound.lower() > 0
    underdetermined = (not identical) and contains_zero(tail_bound)
    evidence_positive = (
        positive_evidence is not None
        and positive_evidence.is_finite()
        and positive_evidence.lower() > 0
    )

    if identical:
        verdict = "IDENTICAL-ZERO: residual is the exact rational zero"
    elif certifies_nonzero:
        verdict = (
            "NOT-ZERO: lower endpoint is strictly positive; a claim of exact "
            "vanishing is an imposition, not a derivation"
        )
    elif evidence_positive:
        verdict = (
            "NOT-ZERO (external evidence): the enclosure cannot certify non-vanishing, "
            "but the logarithm independently proves strict positivity"
        )
    else:
        verdict = (
            "UNDERDETERMINED: the enclosure contains zero without being the exact "
            "zero; neither vanishing nor non-vanishing can be certified"
        )
    return TruncationAudit(
        label=label,
        tail_bound=tail_bound,
        contains_zero=contains_zero(tail_bound),
        is_identically_zero=identical,
        underdetermined=underdetermined,
        verdict=verdict,
    )


def verify_unitarity(t_matrix: arb_mat) -> CommutationAudit:
    """Audit ``T^dag T = I`` for the shift operator.

    Wrapped in the same report type so that unit-level and identity-level
    claims share one presentation and one verdict vocabulary.
    """
    rows = t_matrix.nrows()
    residual = t_matrix.transpose() * t_matrix
    for i in range(rows):
        residual[i, i] -= arb(1)
    contains = all(
        contains_zero(residual[i, j]) for i in range(rows) for j in range(residual.ncols())
    )
    exact_entries, total = _entry_zero_stats(residual)
    return CommutationAudit(
        label="T^dag T = I unitarity audit",
        dimension=rows,
        precision_bits=current_precision(),
        residual=residual,
        contains_zero=contains,
        max_half_width=matrix_residual_width(residual),
        exact_zero_entries=exact_entries,
        total_entries=total,
        structurally_guaranteed=True,
        verdict="PASS-EXACT: shift entries are exact 0 and 1"
        if contains and exact_entries == total
        else "FAIL: residual does not contain zero",
        mandate=MANDATE,
    )

