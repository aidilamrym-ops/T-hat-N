"""The Planck shift operator T and the circulant Hamiltonian H, as structural
algebra rather than as an N x N dense matrix.

Most expensive architectural landmine in MSAF: N = N_steps ~ 5.44e61. A single
matrix cell already needs N^2 elements. Materialising T or H at the working
dimension is not slow, it is structurally impossible, so BOTH operators must be
carried as compact data:

    T  -> a permutation function (index rotation), O(1) state
    H  -> a generator symbol c[0..N-1], O(N) state

The identity `[H, T] = 0` requires no numerical computation at all. Since
`H = sum_j c_j T^j` and all powers of a single operator commute, the
commutator vanishes as an algebraic tautology for any symbol `c` and any `n`.
Numerical verification is therefore admissible only as a regression test at a
small dimension, and the audit layer explicitly downgrades that verdict to
TRIVIAL so a tautology can never be presented as evidence.
"""

from __future__ import annotations

from typing import Callable, Sequence

from flint import acb_mat, arb, arb_mat

from .certify import ZeroCertificate, certify_matrix, contains_zero
from .precision import current_precision

__all__ = [
    "MATERIALISATION_CAP",
    "MatrixDimensionViolation",
    "CyclicShift",
    "CirculantHamiltonian",
    "PlanckClock",
    "PLANCK_TIME_SECONDS",
    "identity",
    "commutator_residual",
    "structural_commutation",
]

#: Hard ceiling on dense matrix materialisation inside the kernel. Above this
#: value the numeric path is automatically routed to structural algebra.
MATERIALISATION_CAP = 4096


class MatrixDimensionViolation(MemoryError):
    """Dense matrix materialisation was attempted beyond the hard ceiling."""


def _guard(n: int) -> None:
    if n > MATERIALISATION_CAP:
        raise MatrixDimensionViolation(
            f"dimension {n} exceeds the materialisation ceiling "
            f"{MATERIALISATION_CAP}; use structural algebra instead"
        )


def identity(n: int) -> arb_mat:
    _guard(n)
    m = arb_mat(n, n)
    for i in range(n):
        m[i, i] = arb(1)
    return m


#: One Planck tick in seconds, from the manuscript value 5.39e-44 s.
#: Constructed live from the decimal string on every call below, never frozen
#: at import precision (landmine L31) and never routed through float.
def PLANCK_TIME_SECONDS() -> arb:  # noqa: N802 - constant-like factory, see docstring
    return arb("5.39e-44")


class PlanckClock:
    """Discrete time bookkeeping on the shift-operator execution path.

    The operator `CyclicShift` itself stays pure and stateless. This clock
    wraps it and records every executed lattice shift (k -> k+1 mod n) as one
    accumulated Planck tick. The counter is a Python integer: exact,
    unbounded, with no rounding at any magnitude. The physical elapsed time
    is derived only on demand as `ticks * t_P` in Arb balls built from exact
    decimal strings. No float64 participates at any point.
    """

    __slots__ = ("shift", "ticks")

    def __init__(self, n: int) -> None:
        self.shift = CyclicShift(n)
        self.ticks = 0

    @property
    def dimension(self) -> int:
        return self.shift.n

    def tick(self, vector: Sequence[arb]) -> list[arb]:
        """Execute one shift and record one Planck tick. Returns the vector."""
        self.ticks += 1
        return self.shift.apply(vector)

    def advance(self, vector: Sequence[arb], steps: int) -> list[arb]:
        """Execute `steps` shifts, recording each. Negative steps refused."""
        if int(steps) < 0:
            raise ValueError(f"steps must be non-negative, got {steps}")
        state = list(vector)
        for _ in range(int(steps)):
            state = self.tick(state)
        return state

    def elapsed_ticks(self) -> int:
        """Accumulated discrete time in Planck ticks. Exact integer."""
        return self.ticks

    def elapsed_time(self) -> arb:
        """Accumulated physical time in seconds, as an Arb ball.

        `arb(int)` is exact, so the only enclosure width comes from the
        three-significant-figure manuscript value of t_P itself.
        """
        return arb(self.ticks) * PLANCK_TIME_SECONDS()


class CyclicShift:
    """The Planck time-shift operator as a permutation, never as a matrix.

    `T e_j = e_{(j+1) mod n}`, with `T^n = I` and `T^dag T = I`.
    """

    __slots__ = ("n",)

    def __init__(self, n: int) -> None:
        if n < 1:
            raise ValueError(f"n must be positive, got {n}")
        self.n = int(n)

    def apply(self, v: Sequence[arb]) -> list[arb]:
        """Apply T to a vector in O(n) time and O(n) space, forming no matrix."""
        n = self.n
        if len(v) != n:
            raise ValueError(f"vector length {len(v)} does not match n {n}")
        return [v[(i - 1) % n] for i in range(n)]

    def period(self) -> int:
        return self.n

    def to_matrix(self) -> arb_mat:
        """Materialisation; small-dimension regression use only."""
        _guard(self.n)
        t = arb_mat(self.n, self.n)
        for i in range(self.n):
            t[(i + 1) % self.n, i] = arb(1)
        return t


class CirculantHamiltonian:
    """Hermitian Hamiltonian determined entirely by its generator symbol c.

    Index convention follows the shift direction:
        H[i][j] = c[(j - i) mod n]

    Hermiticity over the reals requires `c[(n - k) mod n] == c[k]`, i.e. the
    symbol is symmetric under index reversal. That is checked on the data
    itself, never through an eigenvalue algorithm.
    """

    __slots__ = ("n", "c")

    def __init__(self, c: Sequence[arb]) -> None:
        self.c = list(c)
        self.n = len(self.c)

    @classmethod
    def from_function(cls, n: int, f: Callable[[int], arb]) -> "CirculantHamiltonian":
        """Build the symbol c[j] = f(j) without ever forming a matrix."""
        return cls([f(j) for j in range(n)])

    @property
    def is_structurally_hermitian(self) -> bool:
        """Check c[(n-k) mod n] == c[k] on the data itself."""
        n = self.n
        for j in range(n):
            delta = self.c[j] - self.c[(n - j) % n]
            if not (delta.is_zero() or contains_zero(delta)):
                return False
        return True

    def entry(self, i: int, j: int) -> arb:
        return self.c[(j - i) % self.n]

    def row(self, i: int) -> list[arb]:
        n = self.n
        return [self.c[(j - i) % n] for j in range(n)]

    def to_matrix(self) -> arb_mat:
        """Materialisation; small-dimension regression use only."""
        _guard(self.n)
        m = arb_mat(self.n, self.n)
        for i in range(self.n):
            for j in range(self.n):
                m[i, j] = self.entry(i, j)
        return m

    def dft_eigenvalues(self) -> list:
        """Spectrum of H by structural DFT diagonalisation.

        Because H is circulant, the DFT matrix diagonalises it exactly in
        algebra, so no general eigenvalue algorithm is required.

        `acb_mat.dft` already carries the 1/sqrt(n) factor required by the
        unitary definition, so its output is directly the manuscript's gamma_m.
        """
        diagonalised = acb_mat.dft(self.n) * self.to_matrix()
        return [diagonalised[k, 0] for k in range(self.n)]


def commutator_residual(h: CirculantHamiltonian, t: CyclicShift) -> ZeroCertificate:
    """Numerical residual of [H, T] at the working dimension.

    RULE: this residual is always a ball, never an exact zero at finite
    precision. The only admissible claim is "zero lies inside the residual".
    """
    if h.n != t.n:
        raise ValueError(f"dimension mismatch: H={h.n}, T={t.n}")
    hm, tm = h.to_matrix(), t.to_matrix()
    return certify_matrix(
        f"[H,T] n={h.n} prec={current_precision()}b", hm * tm - tm * hm
    )


def structural_commutation() -> str:
    """The theoretical reason why [H, T] = 0 needs no computation.

    `H = sum_j c_j T^j`. Every power `T^a` and `T^b` commutes because both are
    powers of the same operator, so `H T = T H` holds as an algebraic identity
    for any symbol `c` and any `n`, independent of any numerical content.
    """
    return (
        "H = sum_j c_j T^j and T^a T^b = T^(a+b), therefore [H,T] = 0 "
        "as an algebraic identity, for any symbol c and any n"
    )