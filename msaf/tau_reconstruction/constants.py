"""Constants and parameters for Guinand-Weil tau matrix reconstruction."""

from __future__ import annotations

from typing import Final

from flint import arb, acb, ctx, fmpq

__all__ = [
    "CONDUCTOR",
    "BLOCK_100",
    "BLOCK_150",
    "DIM_201",
    "DIM_301",
    "DEV_PREC_BITS",
    "PROD_PREC_BITS",
    "LOG_N_OVER_2PI_100",
    "LOG_N_OVER_2PI_150",
    "get_zeros",
    "get_primes_up_to",
    "PRIMES_UP_TO_100",
    "PRIMES_UP_TO_150",
]

CONDUCTOR: Final[int] = 100
BLOCK_100: Final[int] = 100
BLOCK_150: Final[int] = 150
DIM_201: Final[int] = 2 * BLOCK_100 + 1
DIM_301: Final[int] = 2 * BLOCK_150 + 1

DEV_PREC_BITS: Final[int] = 256
PROD_PREC_BITS: Final[int] = 6000

def _log_n_over_2pi(N: int) -> arb:
    return arb(fmpq(N, 1)).log() - arb(2).log() - arb.pi().log()

LOG_N_OVER_2PI_100: Final[arb] = _log_n_over_2pi(BLOCK_100)
LOG_N_OVER_2PI_150: Final[arb] = _log_n_over_2pi(BLOCK_150)

PRIMES_UP_TO_100: Final[list[int]] = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97
]

PRIMES_UP_TO_150: Final[list[int]] = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
    101, 103, 107, 109, 113, 127, 131, 137, 139, 149
]

def get_zeros(n_zeros: int, prec_bits: int) -> list[arb]:
    old_prec = ctx.prec
    ctx.prec = prec_bits
    try:
        zeros = []
        for k in range(1, n_zeros + 1):
            zero = acb.zeta_zero(k)
            gamma = zero.imag
            zeros.append(arb(gamma))
        return zeros
    finally:
        ctx.prec = old_prec

def get_primes_up_to(N: int) -> list[int]:
    if N <= 100:
        return PRIMES_UP_TO_100
    return PRIMES_UP_TO_150
