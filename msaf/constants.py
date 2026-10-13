"""MSAF constants as Arb balls initialised from exact decimal strings.

Landmine: the cosmological constants `D_obs` and `l_P` are known to only one
or two significant figures. Each ball here therefore carries the measurement
uncertainty as an explicit interval width rather than being collapsed into a
single forced number.
"""

from __future__ import annotations

from typing import Final

from flint import arb

__all__ = [
    "ELL_P",
    "D_OBS",
    "N_STEPS",
    "DECAY_B",
    "DECAY_A",
    "ZETA_SIGMA",
    "T_SPECTRAL",
    "one_sigma",
    "relative_width",
]


def one_sigma(centre: str, half_width: str) -> arb:
    """Ball interval [centre - half, centre + half] from two decimal strings.

    API landmine: in python-flint 0.9.0 the signature is ``arb(x, y)`` where
    `y` is a RADIUS, not a digit count. `arb("1.616255", 60)` produces a ball
    of radius 60. The decimal constructor must be called with a single
    argument and left to the global working precision.
    """
    centre_ball, half_ball = arb(centre), arb(half_width)
    return (centre_ball - half_ball).union(centre_ball + half_ball)


#: Planck length, CODATA 2018: l_P = 1.616255e-35 m, uncertainty 0.5e-41 m.
ELL_P: Final[arb] = one_sigma("1.616255e-35", "0.0000005e-35")

#: Observable universe diameter: 8.8e26 m with roughly 2 percent uncertainty.
D_OBS: Final[arb] = one_sigma("8.8e26", "0.2e26")

#: Total information pixels: N_steps = D_obs / l_P.
N_STEPS: Final[arb] = D_OBS / ELL_P

#: Decay rate of the smallest eigenvalue, B ~ 0.115.
DECAY_B: Final[arb] = arb("0.115")

#: Amplitude factor A in lambda_min(n) ~ A exp(-B n).
DECAY_A: Final[arb] = arb("1")

#: The critical line sigma = 0.5. POSTULATED, not derived; see AUDIT.md L11.
ZETA_SIGMA: Final[arb] = arb("0.5")

#: Extreme spectral scale quoted in the manuscript.
T_SPECTRAL: Final[arb] = arb("8e62")


def relative_width(x: arb) -> arb:
    """Relative interval width of a ball, i.e. its relative uncertainty."""
    return (x.upper() - x.lower()) / x.mid()