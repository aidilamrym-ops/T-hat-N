"""The Guinand-Weil test matrix family and its spectral audit.

The Weil matrix of size n is defined as
    W[i][j] = cos(2 pi i j / n) - delta_{ij}

Decisive structural property: W is normal and symmetric, hence its eigenvalues
are real and can be read directly from the DFT of the first column, with no
general eigenvalue algorithm and no complex arithmetic at all.

Verified landmine in this module: the smallest magnitude eigenvalue of this
family does NOT decay exponentially. The first column is [0, 1, 1, ..., 1],
whose DFT evaluates in closed form:
    lambda_0 = n - 1,   and   lambda_k = -1 for k = 1..n-1.
Therefore min |lambda| = 1 exactly, for every n.
"""

from __future__ import annotations

from typing import NamedTuple

from flint import acb_mat, arb, arb_mat, fmpq

from .precision import log2

__all__ = [
    "weil_matrix",
    "WeilSpectrum",
    "weil_spectrum",
    "spectral_entropy_from_magnitudes",
    "SpectralProfile",
    "spectral_profile",
]


def weil_matrix(n: int) -> arb_mat:
    """The n x n Weil matrix with every entry an Arb ball.

    `cos(pi * x)` is evaluated through `arb.cos_pi` so that no `math.cos`
    float ever enters the numeric path.
    """
    if n < 1:
        raise ValueError(f"n must be positive, got {n}")
    w = arb_mat(n, n)
    for i in range(n):
        for j in range(n):
            w[i, j] = arb(fmpq(2 * i * j, n)).cos_pi() - (1 if i == j else 0)
    return w


class WeilSpectrum(NamedTuple):
    n: int
    eigenvalues: tuple

    @property
    def min_magnitude(self) -> arb:
        return min(_abs_ball(e) for e in self.eigenvalues)

    @property
    def total_magnitude(self) -> arb:
        return sum((_abs_ball(e) for e in self.eigenvalues), arb(0))

    def probabilities(self) -> list[arb]:
        """Normalised spectral density p_k = |lambda_k| / sum_j |lambda_j|."""
        denom = self.total_magnitude
        return [_abs_ball(e) / denom for e in self.eigenvalues]


def _abs_ball(x):
    """Magnitude of a complex ball as a real ball."""
    return (x.real * x.real + x.imag * x.imag).sqrt()


def weil_spectrum(n: int) -> WeilSpectrum:
    """Spectrum of W_n via the DFT of its first column.

    The first column is [0, 1, ..., 1], whose DFT is evaluable analytically.
    The numerical path is still executed so that the result can be compared
    against the closed form as a regression fixture.
    """
    w = weil_matrix(n)
    first_column = arb_mat(n, 1, [w[i, 0] for i in range(n)])
    # `acb_mat.dft` already carries 1/sqrt(n); multiply back so that the
    # eigenvalues of W are read directly rather than a rescaled version.
    diagonalised = acb_mat.dft(n) * arb(n).sqrt() * first_column
    return WeilSpectrum(n=n, eigenvalues=tuple(diagonalised[k, 0] for k in range(n)))


def spectral_entropy_from_magnitudes(magnitudes: list[arb]) -> arb:
    """Spectral Shannon entropy in bits: -sum p log2 p, p_k = |lam_k| / sum|lam|."""
    total = sum(magnitudes, arb(0))
    entropy = arb(0)
    for magnitude in magnitudes:
        probability = magnitude / total
        if probability.is_zero():
            continue
        entropy -= probability * log2(probability)
    return entropy


class SpectralProfile(NamedTuple):
    n: int
    entropy_bits: arb
    min_magnitude: arb


def spectral_profile(n: int) -> SpectralProfile:
    spec = weil_spectrum(n)
    return SpectralProfile(
        n=n,
        entropy_bits=spectral_entropy_from_magnitudes(
            [_abs_ball(e) for e in spec.eigenvalues]
        ),
        min_magnitude=spec.min_magnitude,
    )

