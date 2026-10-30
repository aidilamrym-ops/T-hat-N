"""Guinand-Weil spectral observables for the two existing artifacts.

Scope discipline:

* only ``dim=201`` and ``dim=301`` are defined; ``dim=401`` is rejected;
* the artifacts contain a spectrum, not a matrix, so no matrix is
  reconstructed (the ``build_chain`` producer is not present in this repo);
* every numeric quantity is an Arb ball;
* a perturbation is synthetic: it shifts imaginary parts of the *recorded
  spectrum*, it does not move a zero of zeta.

The two contentful measurements are the spectral Shannon entropy ``H_S`` and
the imaginary leak ``L_Im``. The circulant pairing test is a necessary
condition for a real symmetric circulant spectrum; it can only refute, never
confirm, and the vocabulary forbids a ``CIRCULANT`` verdict.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence

from flint import acb, arb, ctx, fmpq

__all__ = [
    "SCOPE",
    "ARTIFACTS",
    "PREREG_PATH",
    "Spectrum",
    "Observables",
    "CirculantPairing",
    "PerturbationCheck",
    "load_spectrum",
    "spectral_observables",
    "circulant_pairing",
    "perturb",
    "evaluate_perturbations",
    "build_insights",
    "write_insights",
    "ball_to_dict",
    "ball_from_dict",
    "sha256lf",
]

ROOT = Path(__file__).resolve().parents[2]

ARTIFACTS: dict[int, str] = {
    201: "reports/gw_spectrum_100_100.json",
    301: "reports/gw_spectrum_100_150.json",
}

PREREG_PATH = "reports/PREREG_CHRONO_RUNTIME_2026-10-30.md"

SCOPE: dict[str, bool] = {
    "rh_claim": False,
    "zero_location_claim": False,
    "weil_positivity_claim": False,
}

INSIGHTS_SCHEMA = "msaf.chrono_riemann_insights.v1"
DEFAULT_EPSILONS: tuple[Fraction, ...] = (Fraction(1, 100), Fraction(1, 50))


def sha256lf(path: Path) -> str:
    """SHA-256 with CRLF normalised to LF, matching the registry sensor."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _require_precision(min_bits: int = 200) -> None:
    if ctx.prec < min_bits:
        raise RuntimeError(
            f"Arb precision {ctx.prec} is below the required {min_bits} bits; "
            "call msaf.precision.set_precision() first"
        )


def ball_to_dict(value: arb) -> dict[str, str]:
    """Serialise an Arb ball as midpoint and radius decimal strings.

    The midpoint is printed with 100 significant digits: the radius can be as
    small as ``1e-74`` while the midpoint is order one, so a shorter decimal
    would round the midpoint outside the original ball and the reconstruction
    would no longer overlap it.
    """
    return {
        "mid": value.mid().str(100, radius=False),
        "rad": value.rad().str(40, radius=False),
    }


def ball_from_dict(payload: dict[str, str]) -> arb:
    """Rebuild a ball covering the recorded ``{mid, rad}`` pair."""
    mid = arb(payload["mid"])
    rad = abs(arb(payload["rad"]))
    return (mid - rad).union(mid + rad)


@dataclass(frozen=True)
class Spectrum:
    dim: int
    artifact: str
    conductor: int
    block: int
    prec_bits: int
    eigenvalues: tuple[acb, ...]

    @property
    def n(self) -> int:
        return len(self.eigenvalues)


def load_spectrum(dim: int) -> Spectrum:
    """Load one of the two locked spectra.

    ``dim=401`` has no artifact in this repository and is rejected before any
    file lookup, so the failure is explicit rather than a missing-file error.
    """
    _require_precision()
    if dim not in ARTIFACTS:
        raise ValueError(
            f"dim {dim} is not in the locked scope; available: {sorted(ARTIFACTS)}"
        )
    path = ROOT / ARTIFACTS[dim]
    if not path.is_file():
        raise FileNotFoundError(f"missing spectrum artifact: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))

    entries = data["eig"]
    if int(data["n"]) != dim or len(entries) != dim:
        raise ValueError(
            f"artifact {path} reports n={data['n']} with {len(entries)} entries; "
            f"expected {dim}"
        )

    eigenvalues: list[acb] = []
    for entry in entries:
        mid = arb(entry["re"])
        radius = abs(arb(entry["re_rad"]))
        real = (mid - radius).union(mid + radius)
        imag = abs(arb(entry["im_abs"]))
        eigenvalues.append(acb(real, imag))

    return Spectrum(
        dim=dim,
        artifact=ARTIFACTS[dim],
        conductor=int(data["c"]),
        block=int(data["N"]),
        prec_bits=int(data["prec"]),
        eigenvalues=tuple(eigenvalues),
    )


@dataclass(frozen=True)
class Observables:
    count: int
    sigma_abs_sum: arb
    entropy: arb
    leak: arb


def spectral_observables(values: Sequence[acb]) -> Observables:
    """Compute ``sum |lambda|``, ``H_S`` and ``L_Im`` with Arb enclosures.

    ``p_i = |lambda_i| / sum |lambda_j|`` and ``H_S = -sum p_i log p_i`` with
    the convention ``0 log 0 = 0``. ``L_Im`` is the ratio of the imaginary
    mass to the modulus mass.
    """
    _require_precision()
    if not values:
        raise ValueError("at least one eigenvalue is required")

    moduli = [abs(value) for value in values]
    total = sum(moduli, arb(0))
    if total.lower() <= 0:
        raise ZeroDivisionError("sum |lambda| is not certified positive")

    entropy = arb(0)
    for modulus in moduli:
        share = modulus / total
        if share == 0:
            continue
        entropy -= share * share.log()

    imaginary_mass = sum((abs(value.imag) for value in values), arb(0))
    leak = imaginary_mass / total

    return Observables(
        count=len(values),
        sigma_abs_sum=total,
        entropy=entropy,
        leak=leak,
    )


@dataclass(frozen=True)
class CirculantPairing:
    verdict: str
    defect: arb
    witness_index: int | None
    witness_lower: arb
    ordering_certified: bool
    real_spectrum: bool


def _sorted_by_midpoint(values: Iterable[acb]) -> list[acb]:
    """Insertion-sort by real part (``acb`` has no ordering)."""
    ordered = list(values)
    for i in range(1, len(ordered)):
        key = ordered[i]
        j = i - 1
        while j >= 0 and key.real < ordered[j].real:
            ordered[j + 1] = ordered[j]
            j -= 1
        ordered[j + 1] = key
    return ordered


def circulant_pairing(values: Sequence[acb]) -> CirculantPairing:
    """Test the necessary palindrome condition of a real symmetric circulant.

    A real symmetric circulant has a real spectrum invariant under the
    frequency involution, so after sorting descending the multiset must pair
    ``lambda_(j)`` with ``lambda_(n-1-j)``. A disjoint pair refutes circulant
    structure; a compatible result is necessary-only and never a proof.
    """
    _require_precision()
    n = len(values)
    if n == 0:
        raise ValueError("at least one eigenvalue is required")

    ordered = _sorted_by_midpoint(values)
    ordering_certified = all(
        not ordered[i].real.overlaps(ordered[i + 1].real) for i in range(n - 1)
    )

    defect: arb | None = None
    witness_index: int | None = None
    witness_lower = arb(0)
    for j in range(n):
        delta = abs(ordered[j].real - ordered[n - 1 - j].real)
        if defect is None or delta.upper() > defect.upper():
            defect = delta
        lower = delta.lower()
        if lower > 0 and (witness_index is None or lower > witness_lower):
            witness_index = j
            witness_lower = lower

    non_real = next((i for i, value in enumerate(values) if value.imag != 0), None)
    real_spectrum = non_real is None

    if defect is None:  # pragma: no cover - n >= 1 guarantees one iteration
        defect = arb(0)

    if non_real is not None:
        # A real symmetric circulant has a real spectrum; a certified non-zero
        # imaginary component refutes that structure outright.
        verdict = "NOT-SYMMETRIC-CIRCULANT"
        witness_index = non_real
        witness_lower = abs(values[non_real].imag).lower()
    elif not ordering_certified:
        verdict = "UNAVAILABLE"
    elif witness_index is not None:
        verdict = "NOT-SYMMETRIC-CIRCULANT"
    else:
        verdict = "COMPATIBLE-NECESSARY-ONLY"

    return CirculantPairing(
        verdict=verdict,
        defect=defect,
        witness_index=witness_index,
        witness_lower=witness_lower,
        ordering_certified=ordering_certified,
        real_spectrum=real_spectrum,
    )


def perturb(values: Sequence[acb], epsilon: Fraction) -> tuple[acb, ...]:
    """Add ``i*epsilon`` to every eigenvalue.

    ``epsilon`` is an exact Fraction converted through ``fmpq``. This is a
    synthetic displacement of the recorded spectrum, not a movement of a zeta
    zero.
    """
    if epsilon < 0:
        raise ValueError(f"epsilon must be non-negative, got {epsilon}")
    eps = arb(fmpq(epsilon.numerator, epsilon.denominator))
    return tuple(acb(value.real, eps) for value in values)


@dataclass(frozen=True)
class PerturbationCheck:
    epsilon: Fraction
    observables: Observables
    checks: dict[str, bool]

    @property
    def status(self) -> str:
        return "PASS" if all(self.checks.values()) else "FAILED"


def evaluate_perturbations(
    values: Sequence[acb],
    baseline: Observables,
    epsilons: Sequence[Fraction] = DEFAULT_EPSILONS,
) -> tuple[tuple[PerturbationCheck, ...], dict[str, bool]]:
    """Run P1-P4 and return the per-epsilon checks plus the P4 verdict."""
    ordered_epsilons = sorted(epsilons)
    checks: list[PerturbationCheck] = []
    for epsilon in ordered_epsilons:
        observables = spectral_observables(perturb(values, epsilon))
        delta = observables.entropy - baseline.entropy
        per_epsilon = {
            "P2_leak_positive": observables.leak.lower() > 0,
            "P3_entropy_increases": delta.lower() > 0,
            "P3_entropy_gain_at_least_1e-3": delta.lower() >= arb(fmpq(1, 1000)),
        }
        checks.append(
            PerturbationCheck(
                epsilon=epsilon,
                observables=observables,
                checks=per_epsilon,
            )
        )

    p4 = False
    if len(checks) >= 2:
        difference = checks[-1].observables.leak - checks[0].observables.leak
        p4 = difference.lower() > 0

    return tuple(checks), {"P4_leak_monotone": p4}


def _record_for_dim(spec: Spectrum) -> dict[str, Any]:
    baseline = spectral_observables(spec.eigenvalues)
    pairing = circulant_pairing(spec.eigenvalues)
    perturbations, family_checks = evaluate_perturbations(
        spec.eigenvalues, baseline
    )

    p1 = baseline.leak == 0
    all_checks = {
        "P1_baseline_leak_zero": p1,
        "ordering_certified": pairing.ordering_certified,
        "circulant_verdict_recorded": pairing.verdict != "UNAVAILABLE",
        **family_checks,
    }
    for item in perturbations:
        all_checks.update(
            {f"eps={item.epsilon}:{name}": ok for name, ok in item.checks.items()}
        )

    record: dict[str, Any] = {
        "dim": spec.dim,
        "artifact": spec.artifact,
        "artifact_sha256lf": sha256lf(ROOT / spec.artifact),
        "eigenvalue_count": spec.n,
        "conductor": spec.conductor,
        "block": spec.block,
        "source_prec_bits": spec.prec_bits,
        "prec_bits": ctx.prec,
        "sigma_abs_sum": ball_to_dict(baseline.sigma_abs_sum),
        "spectral_entropy": ball_to_dict(baseline.entropy),
        "imaginary_leak": ball_to_dict(baseline.leak),
        "circulant_pairing": {
            "verdict": pairing.verdict,
            "witness_index": pairing.witness_index,
            "defect_lower_bound": pairing.witness_lower.mid().str(40, radius=False),
            "defect_lower_ball": ball_to_dict(pairing.witness_lower),
            "defect": ball_to_dict(pairing.defect),
            "ordering_certified": pairing.ordering_certified,
            "real_spectrum": pairing.real_spectrum,
        },
        "perturbations": [
            {
                "epsilon": f"{item.epsilon.numerator}/{item.epsilon.denominator}",
                "synthetic_only": True,
                "zero_location_claim": False,
                "spectral_entropy": ball_to_dict(item.observables.entropy),
                "imaginary_leak": ball_to_dict(item.observables.leak),
                "checks": item.checks,
                "execution_status": item.status,
            }
            for item in perturbations
        ],
        "checks": all_checks,
        "numerical_verdict": (
            f"dim {spec.dim}: L_Im = {baseline.leak.str(8)}; "
            f"H_S = {baseline.entropy.str(12)}; "
            f"circulant pairing {pairing.verdict} "
            f"(witness {pairing.witness_index}, "
            f"lower bound {pairing.witness_lower.str(8)})"
        ),
        "execution_status": "PASS" if all(all_checks.values()) else "FAILED",
    }
    return record


def run_id_for(dims: Sequence[int], prec_bits: int) -> str:
    payload = {
        "schema": INSIGHTS_SCHEMA,
        "dims": sorted(int(dim) for dim in dims),
        "prec_bits": int(prec_bits),
        "epsilons": [
            f"{epsilon.numerator}/{epsilon.denominator}"
            for epsilon in DEFAULT_EPSILONS
        ],
    }
    canonical = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def build_insights(
    dims: Sequence[int] = (201, 301),
    generated_utc: str = "",
) -> dict[str, Any]:
    """Build the locked insights JSON.

    A per-dimension runtime failure is recorded as ``execution_status``
    ``FAILED`` with a deviation entry; it is not raised, because a failed
    measurement must stay observable instead of killing the caller. A missing
    pre-registration is a setup error and does raise.
    """
    _require_precision()
    prereg = ROOT / PREREG_PATH
    if not prereg.is_file():
        raise FileNotFoundError(f"pre-registration is missing: {prereg}")

    records: list[dict[str, Any]] = []
    deviations: list[dict[str, Any]] = []

    for dim in dims:
        try:
            spec = load_spectrum(dim)
            record = _record_for_dim(spec)
            records.append(record)
        except Exception as exc:  # noqa: BLE001 - recorded, never swallowed
            deviations.append(
                {
                    "dim": int(dim),
                    "stage": "spectrum",
                    "exception": type(exc).__name__,
                    "message": str(exc),
                    "execution_status": "FAILED",
                }
            )
            records.append(
                {
                    "dim": int(dim),
                    "artifact": ARTIFACTS.get(int(dim)),
                    "execution_status": "FAILED",
                    "deviation": f"{type(exc).__name__}: {exc}",
                }
            )

    payload: dict[str, Any] = {
        "schema": INSIGHTS_SCHEMA,
        "run_id": run_id_for(dims, ctx.prec),
        "prereg": PREREG_PATH,
        "prereg_sha256lf": sha256lf(prereg),
        "generated_utc": generated_utc,
        "prec_bits": ctx.prec,
        "scope": dict(SCOPE),
        "records": records,
        "deviations": deviations,
    }
    return payload


def write_insights(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
