# -*- coding: utf-8 -*-
"""CI guard: Campaign V2 quantum-entropy sub-kernel must pass its frozen
selftest run with ZERO FAILURE.

The selftest is the single executable contract of the freeze (see
reports/REPLAY_CERT_SPEC_V0.2_QUANTUM.md): K-Q1 seed refusal, dual-engine
protocol checks, L39/L41/L42 landmines, K-Q2/K-Q4/K-Q5/K-Q6 checks, and an
end-to-end mini campaign on dims 8/9/10 against temp ledger/outdir. Any
drift in the frozen package must fail here; CI never passes silently.

SIMULATED: nothing in this campaign measures physical quantum entropy.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_quantum_entropy_selftest_zero_failure() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "msaf.quantum_entropy.selftest"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=1800,
    )
    tail = (proc.stdout or "")[-4000:] + (proc.stderr or "")[-4000:]
    assert proc.returncode == 0, "selftest exit %d:\n%s" % (proc.returncode, tail)
    assert "ZERO FAILURE" in proc.stdout, tail


