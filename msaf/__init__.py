"""MSAF - Matrix-constraint Spectral Analysis Framework.

Rigid computation kernel built on ball arithmetic (python-flint / Arb).
No `float` ever touches the numeric path. Every quantity entering the system
is an Arb ball initialised from an exact decimal string.

Import discipline (deterministic, non-transitive):

    from msaf import precision, constants, grid, certify, operators
    from msaf import guinand, budget, evolution

Never import any module after `precision.set_precision()` has run: the global
Arb precision must be fixed exactly once, before any dependent numeric import.

Standing policy: all code, identifiers, docstrings and comments are English.
Prose reports to the researcher are Indonesian.
"""

from __future__ import annotations

__all__ = ["__version__"]

__version__ = "0.2.0"

