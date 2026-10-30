"""Tests for the Guinand-Weil spectral observables and the insights artifact."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest
from flint import arb, fmpq

from msaf.precision import DEFAULT_PRECISION_BITS, set_precision

set_precision(DEFAULT_PRECISION_BITS)

from msaf.chrono_runtime import riemann_operator as ro  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
INSIGHTS = ROOT / "reports" / "CHRONO_RIEMANN_INSIGHTS.json"
PREREG = ROOT / ro.PREREG_PATH


def _all_keys(value: object) -> list[str]:
    if isinstance(value, dict):
        keys = list(value.keys())
        for item in value.values():
            keys.extend(_all_keys(item))
        return keys
    if isinstance(value, list):
        keys: list[str] = []
        for item in value:
            keys.extend(_all_keys(item))
        return keys
    return []


@pytest.mark.parametrize("dim", [201, 301])
def test_locked_spectrum_loads(dim: int) -> None:
    spectrum = ro.load_spectrum(dim)
    assert spectrum.dim == dim
    assert spectrum.n == dim
    assert spectrum.artifact in ro.ARTIFACTS.values()
    assert spectrum.conductor == 100
    assert spectrum.block in {100, 150}
    assert all(value.imag == 0 for value in spectrum.eigenvalues)


def test_dim_401_and_other_dimensions_are_rejected() -> None:
    for dim in (401, 400, 200):
        with pytest.raises(ValueError):
            ro.load_spectrum(dim)


@pytest.mark.parametrize("dim", [201, 301])
def test_observables_are_arb_enclosed(dim: int) -> None:
    spectrum = ro.load_spectrum(dim)
    observables = ro.spectral_observables(spectrum.eigenvalues)

    assert observables.count == dim
    assert observables.sigma_abs_sum.lower() > 0
    assert observables.entropy.lower() > 0
    assert observables.entropy.rad() < arb("1e-9")
    assert observables.leak == 0


@pytest.mark.parametrize("dim", [201, 301])
def test_circulant_pairing_refutes_a_symmetric_circulant(dim: int) -> None:
    spectrum = ro.load_spectrum(dim)
    pairing = ro.circulant_pairing(spectrum.eigenvalues)

    assert pairing.real_spectrum
    assert pairing.ordering_certified
    assert pairing.verdict == "NOT-SYMMETRIC-CIRCULANT"
    assert pairing.verdict != "CIRCULANT"
    assert pairing.witness_index is not None
    assert pairing.witness_lower > 0
    assert pairing.defect.lower() > 0


@pytest.mark.parametrize("dim", [201, 301])
def test_synthetic_perturbation_is_detected(dim: int) -> None:
    spectrum = ro.load_spectrum(dim)
    baseline = ro.spectral_observables(spectrum.eigenvalues)
    checks, family = ro.evaluate_perturbations(spectrum.eigenvalues, baseline)

    assert len(checks) == 2
    assert [str(item.epsilon) for item in checks] == ["1/100", "1/50"]
    assert family == {"P4_leak_monotone": True}
    for item in checks:
        assert item.status == "PASS"
        assert all(item.checks.values())
        assert item.observables.leak.lower() > 0
        assert item.observables.entropy.lower() > baseline.entropy.upper()

    small, large = checks
    assert large.observables.leak.lower() > small.observables.leak.upper()


def test_perturbation_uses_exact_fractions_not_decimals() -> None:
    spectrum = ro.load_spectrum(201)
    values = ro.perturb(spectrum.eigenvalues, Fraction(1, 100))
    assert len(values) == spectrum.n
    # The imaginary part is the exact fmpq 1/100, checked via overlap.
    assert values[0].imag.overlaps(arb(fmpq(1, 100)))


def test_build_insights_records_a_failed_dimension_without_raising() -> None:
    payload = ro.build_insights(dims=(401,), generated_utc="1970-01-01T00:00:00Z")
    assert payload["records"][0]["execution_status"] == "FAILED"
    assert payload["deviations"][0]["dim"] == 401
    assert payload["scope"] == ro.SCOPE


def test_insights_artifact_is_bound_to_prereg_and_sources() -> None:
    assert INSIGHTS.is_file(), "reports/CHRONO_RIEMANN_INSIGHTS.json is missing"
    payload = json.loads(INSIGHTS.read_text(encoding="utf-8"))

    assert payload["schema"] == ro.INSIGHTS_SCHEMA
    assert payload["scope"] == {
        "rh_claim": False,
        "zero_location_claim": False,
        "weil_positivity_claim": False,
    }
    assert "mathematical_verdict" not in _all_keys(payload)
    assert payload["prereg_sha256lf"] == ro.sha256lf(PREREG)
    assert payload["run_id"] == ro.run_id_for([201, 301], payload["prec_bits"])
    assert payload["deviations"] == []

    records = {record["dim"]: record for record in payload["records"]}
    assert set(records) == {201, 301}

    for dim, record in records.items():
        assert record["artifact"] == ro.ARTIFACTS[dim]
        assert record["artifact_sha256lf"] == ro.sha256lf(ROOT / record["artifact"])
        assert record["eigenvalue_count"] == dim
        assert record["execution_status"] == "PASS"
        assert record["circulant_pairing"]["verdict"] == "NOT-SYMMETRIC-CIRCULANT"
        assert record["circulant_pairing"]["real_spectrum"] is True
        assert record["imaginary_leak"] == {"mid": "0", "rad": "0"}

        for item in record["perturbations"]:
            assert item["synthetic_only"] is True
            assert item["zero_location_claim"] is False
            assert item["execution_status"] == "PASS"
            assert item["epsilon"] in {"1/100", "1/50"}


@pytest.mark.parametrize("dim", [201, 301])
def test_insights_values_overlap_a_fresh_recomputation(dim: int) -> None:
    payload = json.loads(INSIGHTS.read_text(encoding="utf-8"))
    record = next(item for item in payload["records"] if item["dim"] == dim)

    spectrum = ro.load_spectrum(dim)
    observables = ro.spectral_observables(spectrum.eigenvalues)
    pairing = ro.circulant_pairing(spectrum.eigenvalues)

    assert observables.entropy.overlaps(
        ro.ball_from_dict(record["spectral_entropy"])
    )
    assert observables.sigma_abs_sum.overlaps(
        ro.ball_from_dict(record["sigma_abs_sum"])
    )
    assert observables.leak.overlaps(ro.ball_from_dict(record["imaginary_leak"]))

    lower_ball = ro.ball_from_dict(record["circulant_pairing"]["defect_lower_ball"])
    assert lower_ball.lower() > 0
    assert pairing.witness_lower.overlaps(lower_ball)

    for item in record["perturbations"]:
        epsilon = Fraction(item["epsilon"])
        recomputed = ro.spectral_observables(
            ro.perturb(spectrum.eigenvalues, epsilon)
        )
        assert recomputed.entropy.overlaps(
            ro.ball_from_dict(item["spectral_entropy"])
        )
        assert recomputed.leak.overlaps(
            ro.ball_from_dict(item["imaginary_leak"])
        )
