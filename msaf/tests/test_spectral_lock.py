"""Test suite for Stage 3 Spectral Lock and Matrice-Tau Projection."""

from __future__ import annotations

import pytest
from flint import fmpq

from msaf.chrono_runtime.stage3_spectral_lock import (
    Stage3SpectralLockEngine,
    run_stage3_spectral_locking,
)


def test_stage3_tau_assembly() -> None:
    engine = Stage3SpectralLockEngine([fmpq(1, 2), fmpq(1, 6)], dim=5)
    tau = engine.assemble_tau_matrix()
    assert tau.nrows() == 5
    assert tau.ncols() == 5


def test_stage3_spectral_certification() -> None:
    engine = Stage3SpectralLockEngine([fmpq(1, 2), fmpq(1, 6)], dim=12)
    tau = engine.assemble_tau_matrix()
    cert = engine.certify_spectrum_and_leak(tau)
    assert cert["status"] == "CERTIFIED"
    assert cert["imag_leak_certified"] is True
    assert cert["gm0_passed"] is True


def test_stage3_receipt_generation() -> None:
    report = run_stage3_spectral_locking()
    assert report["status"] == "CERTIFIED"
    assert report["certificate"]["imag_leak_certified"] is True
