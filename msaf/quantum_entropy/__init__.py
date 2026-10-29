"""MSAF Campaign V2 -- quantum-entropy certification sub-kernel (SIMULATED).

Campaign V2 replaces the deterministic PRNG paths *inside this sub-kernel only*
with a non-deterministic entropy stream. In this workspace no quantum hardware
is attached: the stream is a SIMULATED surrogate drawn from the operating
system CSPRNG (`secrets`), and every artifact of this campaign carries the
``SIMULATED`` label. Nothing here measures or claims physical quantum
entropy.

Freeze discipline (see reports/REPLAY_CERT_SPEC_V0.2_QUANTUM.md and
reports/AUDIT_QUANTUM_PREREG_2026-10-19.md):

* K-Q1: no ``--seed`` argument exists anywhere in this package; a ``--seed``
  occurrence on a command line is refused with exit code 2.
* K-Q7: ``global_claim_supported`` is hardcoded ``False`` below. MSAF
  measures one finite model instance at a stated precision; it does not
  claim absolute truth, physical quantum measurement, or any statement
  about the Riemann zeta zeros.

Existing sealed pipelines are untouched by this package (additive scope, D4).
"""

from __future__ import annotations

__all__ = ["__version__", "SIMULATED_LABEL", "global_claim_supported"]

__version__ = "0.2.0-quantum"

#: K-Q7 hardcoded at module root: no global (absolute) claim is supported.
global_claim_supported = False

#: Every record, dashboard and log line produced by this package must carry
#: this label: the entropy source is simulated, not a physical measurement.
SIMULATED_LABEL = "SIMULATED"


