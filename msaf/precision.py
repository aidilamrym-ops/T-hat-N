"""Deterministic precision kernel.

Landmines handled here:

1. `flint.ctx.prec` is process-global state, not thread or object state. Any
   transitively imported module that touches `ctx.prec` shifts the precision of
   the entire process. Precision is therefore set exactly once, at a single
   entry point (`set_precision`), and is never renegotiated mid-analysis.

2. `mpmath.mp.dps` is a global precision mutator of the same kind. Importing
   mpmath transitively, through sympy, scipy, matplotlib or any package that
   depends on them, can execute code that writes `mp.dps`. This module probes
   `sys.modules` and raises `PrecisionLandmine` when an analysis is launched
   inside an already contaminated process.

3. `arb.log(base)`, `arb.exp(x)` and `arb.sqrt(x)` accept NO arguments in
   python-flint 0.9.0. Base conversion must go through `log_base` or division
   by `log()`. The wrappers below are the only sanctioned spelling.
"""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Final

from flint import arb, ctx

__all__ = [
    "PrecisionLandmine",
    "DEFAULT_PRECISION_BITS",
    "audit_precision_landmines",
    "set_precision",
    "current_precision",
    "require_pure_precision_environment",
    "ball_precision",
    "log2",
    "exp2",
    "log_base",
    "log2_e",
]

#: Working precision. Comfortably above the worst-case demand reported by
#: `msaf.budget`, which stays under 200 bits for every dimension of interest.
DEFAULT_PRECISION_BITS: Final[int] = 256

#: Known third-party global precision mutators.
KNOWN_PRECISION_MUTATORS: Final[frozenset[str]] = frozenset({"mpmath", "gmpy2"})

_LOCKED: bool = False
_LOCKED_AT: int = 0


class PrecisionLandmine(RuntimeError):
    """Raised when the process is contaminated by a global precision mutator."""


def audit_precision_landmines(modules: ModuleType | None = None) -> tuple[str, ...]:
    """Return the names of global precision mutators already resident.

    A pure read of `sys.modules`; nothing is modified.
    """
    namespace = sys.modules if modules is None else vars(modules)
    return tuple(sorted(name for name in KNOWN_PRECISION_MUTATORS if name in namespace))


def require_pure_precision_environment() -> None:
    """Raise `PrecisionLandmine` if the process environment is impure.

    Called once at the entry point, before precision is locked.
    """
    tainted = audit_precision_landmines()
    if tainted:
        raise PrecisionLandmine(
            "global precision mutator already imported: "
            + ", ".join(tainted)
            + " - process contaminated, analysis aborted"
        )


def set_precision(bits: int = DEFAULT_PRECISION_BITS) -> int:
    """Lock the Arb precision idempotently and deterministically.

    A second call with a different value is an architectural error, not a
    renegotiation. Global precision must never drift during an analysis.
    """
    global _LOCKED, _LOCKED_AT
    bits = int(bits)
    if bits <= 0:
        raise ValueError(f"precision must be positive, got {bits}")
    if _LOCKED and bits != _LOCKED_AT:
        raise PrecisionLandmine(
            f"precision already locked at {_LOCKED_AT} bits; request for {bits} refused"
        )
    ctx.prec = bits
    _LOCKED, _LOCKED_AT = True, bits
    return ctx.prec


def current_precision() -> int:
    return ctx.prec


class ball_precision:  # noqa: N801 - used as a context manager
    """Temporary precision for sensitivity probing, restored on exit.

    For sensitivity studies only. The primary analysis path must use
    `set_precision` so that the order of precision changes stays deterministic.
    """

    __slots__ = ("_bits", "_previous")

    def __init__(self, bits: int) -> None:
        self._bits = int(bits)
        self._previous = 0

    def __enter__(self) -> int:
        self._previous = ctx.prec
        ctx.prec = self._bits
        return ctx.prec

    def __exit__(self, *_exc: object) -> bool:
        ctx.prec = self._previous
        return False


def log_base(x: arb, base: arb) -> arb:
    """Logarithm to an arbitrary base, with no hand-off to float."""
    return x.log() / base.log()


def log2(x: arb) -> arb:
    return x.log() / arb(2).log()


def exp2(x: arb) -> arb:
    return (arb(2).log() * x).exp()


def log2_e() -> arb:
    """log2(e) = 1/ln 2, evaluated at the ACTIVE precision on every call.

    Landmine fixed here: this was previously a module-level constant
    ``LOG2_E = 1 / arb(2).log()``, evaluated once at import time under the
    53-bit default precision. Every downstream quantity then carried a
    53-bit-wide ball while the kernel ran at 256 bit, and the report printed
    those widths as if they were 256-bit results. A function cannot freeze;
    callers always observe the precision they actually locked.
    """
    return 1 / arb(2).log()