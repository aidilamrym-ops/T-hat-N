"""Exact discrete lattice for the Chrono-Geometric runtime.

The lattice exponent is the integer floor of the rigid modulus ``T^N = I``
recorded by ``msaf.grid``. The literal below is checked against
``msaf.grid.n_steps_floor()`` at import time: a drift raises immediately
instead of silently producing a different cycle.

No float ever appears here. Tick times are exact :class:`~fractions.Fraction`
values derived from the same Planck-length literal that ``msaf/grid.py`` uses
and the exact SI speed of light.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Final

from msaf.grid import n_steps_floor

__all__ = [
    "N_STEPS",
    "L_PLANCK_M",
    "C_M_PER_S",
    "TICK_SECONDS",
    "HORIZON_SECONDS",
    "phase",
    "wrap",
    "tick_seconds",
    "check_exact_integer",
]

#: floor(8.8e26 / 1.616255e-35), the exponent of the rigid modulus T^N = I.
#: 62 decimal digits, 206 bits. Never an Arb ball: the ball in
#: ``msaf.constants.N_STEPS`` is not an integer and must not be used as an
#: exponent.
N_STEPS: Final[int] = 54446853992717733278474003174004102075476951347404957757284586

#: Planck length in metres as the exact rational 1.616255e-35, matching the
#: literal used by ``msaf.grid.n_steps_exact_rational_parts``.
L_PLANCK_M: Final[Fraction] = Fraction(1616255, 10**41)

#: Speed of light in m/s, exact by SI definition.
C_M_PER_S: Final[Fraction] = Fraction(299792458)

#: Model convention: one lattice step lasts l_P / c seconds. This is not a
#: measurement and no physical claim is attached to it.
TICK_SECONDS: Final[Fraction] = L_PLANCK_M / C_M_PER_S

#: Time to traverse the whole cycle once, as an exact Fraction. Because
#: ``N_STEPS`` is a floor, this is ``D_OBS / c`` only up to the floor.
HORIZON_SECONDS: Final[Fraction] = Fraction(N_STEPS) * TICK_SECONDS

_GRID_FLOOR: Final[int] = int(n_steps_floor())
if N_STEPS != _GRID_FLOOR:  # pragma: no cover - import-time guard
    raise RuntimeError(
        "N_STEPS literal drifted from msaf.grid.n_steps_floor(): "
        f"{N_STEPS} != {_GRID_FLOOR}"
    )


def check_exact_integer() -> bool:
    """Return True when the literal still equals the audited grid floor.

    Kept as a function so a test can call it explicitly even though the same
    check already runs at import time.
    """
    return N_STEPS == int(n_steps_floor())


def phase(tick: int) -> int:
    """Return ``tick mod N_STEPS``.

    Negative ticks are not defined: there is no phase before ``now``.
    """
    if not isinstance(tick, int) or isinstance(tick, bool):
        raise TypeError(f"tick must be an int, got {type(tick).__name__}")
    if tick < 0:
        raise ValueError(f"tick must be non-negative, got {tick}")
    return tick % N_STEPS


def wrap(tick: int) -> int:
    """Alias for :func:`phase`, the only sanctioned wrap point."""
    return phase(tick)


def tick_seconds(tick: int) -> Fraction:
    """Elapsed model time for ``tick`` steps, as an exact Fraction."""
    if not isinstance(tick, int) or isinstance(tick, bool):
        raise TypeError(f"tick must be an int, got {type(tick).__name__}")
    if tick < 0:
        raise ValueError(f"tick must be non-negative, got {tick}")
    return Fraction(tick) * TICK_SECONDS
