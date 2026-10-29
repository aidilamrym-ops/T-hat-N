"""Finite RBM Anderson diagnostic for the S1/S2 estimators.

The matrix layer is exact-rational: every entry is an integer divided by a
power of two, so the float64 matrix is exactly representable.  The spectral
statistics are a float64 diagnostic layer; a small Arb spot-check verifies
that the float spectra agree with exact-rational matrix input.

This is a finite benchmark, not a claim about the thermodynamic Anderson
transition, universal RMT, or any physical system.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from flint import acb, acb_mat, arb, ctx, fmpq
from scipy.special import ndtr

SCHEMA = "msaf.rbm_anderson.v1"
MASTER_SEED = 2430500035454946990  # 0x21badee7a7ddceae, recorded in the prereg
DIM = 201
BANDWIDTHS = (1, 10, 120)
N_MATRICES = 64
N_REFERENCE = 2000
N_CALIBRATION = 64
N_BOOTSTRAP = 2000
SIGMA_U = (0.3, 0.5, 1.0)
CHARTS = ("T", "L")
SIGMA_E = 0.5
U_CENTERS = tuple(0.25 + 0.5 * i for i in range(20))
FINE_WIDTH = 0.02
FINE_EDGES = tuple(FINE_WIDTH * i for i in range(501))
FINE_CENTERS = np.array(
    [(FINE_EDGES[i] + FINE_EDGES[i + 1]) / 2.0 for i in range(len(FINE_EDGES) - 1)]
)
KERNEL = np.exp(
    -0.5
    * ((np.array(U_CENTERS)[:, None] - FINE_CENTERS[None, :]) / SIGMA_E) ** 2
) / (SIGMA_E * math.sqrt(2.0 * math.pi))

REPO_ROOT = Path(__file__).resolve().parents[1]
PREREG_PATH = REPO_ROOT / "reports" / "PREREG_RBM_ANDERSON_2026-10-20.md"
RECEIPT_PATH = REPO_ROOT / "reports" / "rbm_anderson_2026-10-20.json"


@dataclass(frozen=True)
class Config:
    """Campaign parameters.  The full values are frozen in the prereg."""

    dim: int = DIM
    bandwidths: tuple[int, ...] = BANDWIDTHS
    n_matrices: int = N_MATRICES
    n_reference: int = N_REFERENCE
    n_calibration: int = N_CALIBRATION
    n_bootstrap: int = N_BOOTSTRAP
    seed: int = MASTER_SEED


FULL_CONFIG = Config()
QUICK_CONFIG = Config(
    dim=31,
    bandwidths=(1, 5, 15),
    n_matrices=4,
    n_reference=40,
    n_calibration=4,
    n_bootstrap=80,
)


def derive_seed(label: str, master: int = MASTER_SEED) -> int:
    """Deterministic 64-bit stream seed from the recorded master seed."""
    digest = hashlib.sha256(f"{master}:{label}".encode("ascii")).digest()
    return int.from_bytes(digest[:8], "big")


def _raw_ints(seed: int, dim: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    re = rng.integers(-32768, 32768, size=(dim, dim), dtype=np.int64)
    im = rng.integers(-32768, 32768, size=(dim, dim), dtype=np.int64)
    return re, im


def _band_mask(dim: int, b: int) -> np.ndarray:
    idx = np.arange(dim)
    return np.abs(idx[:, None] - idx[None, :]) <= b


def _matrix_from_ints(re: np.ndarray, im: np.ndarray, b: int) -> np.ndarray:
    dim = re.shape[0]
    a = (re.astype(np.complex128) + 1j * im.astype(np.complex128)) / 32768.0
    a = np.where(_band_mask(dim, b), a, 0.0)
    return (a + a.conj().T) / 2.0


def matrix_from_seed(seed: int, dim: int, b: int) -> np.ndarray:
    """Build one Hermitian banded matrix from exact 16-bit integer entries."""
    if not (0 <= b < dim):
        raise ValueError("bandwidth must satisfy 0 <= b < dim")
    re, im = _raw_ints(seed, dim)
    return _matrix_from_ints(re, im, b)


def rbm_levels(seed: int, dim: int, b: int) -> np.ndarray:
    """Eigenvalues of one RBM matrix, sorted ascending."""
    return np.linalg.eigvalsh(matrix_from_seed(seed, dim, b))


def gue_levels(seed: int, dim: int) -> np.ndarray:
    """Eigenvalues of one full-band complex Hermitian GUE matrix."""
    return rbm_levels(seed, dim, dim - 1)


def poisson_levels(seed: int, dim: int) -> np.ndarray:
    """Ordered cumulative exponential levels (unit-rate Poisson process)."""
    rng = np.random.default_rng(seed)
    return np.cumsum(rng.exponential(size=dim))


def shifted_levels(ev: Iterable[float]) -> np.ndarray:
    """Shift a real spectrum so its minimum is exactly 1."""
    x = np.sort(np.asarray(ev, dtype=np.float64))
    if x.size < 3:
        raise ValueError("spectrum too short")
    return x + (1.0 - x[0])


def chart_levels(ev: Iterable[float], chart: str) -> np.ndarray:
    """Apply the pre-registered chart transform."""
    x = shifted_levels(ev)
    if chart == "L":
        return x
    if chart == "T":
        return np.log(x)
    raise ValueError(f"unknown chart: {chart}")


def s1(ev: Iterable[float]) -> float:
    """Mean adjacent gap ratio (S1), exact formula, float64 input."""
    x = np.sort(np.asarray(ev, dtype=np.float64))
    gaps = np.diff(x)
    if gaps.size < 2:
        raise ValueError("S1 needs at least three levels")
    numer = np.minimum(gaps[:-1], gaps[1:])
    denom = np.maximum(gaps[:-1], gaps[1:])
    return float(np.mean(numer / denom))


def _unfold(y: np.ndarray, sigma_u: float) -> np.ndarray:
    y = np.sort(np.asarray(y, dtype=np.float64))
    dim = y.size
    idx = np.arange(dim)
    lo = np.maximum(idx - 10, 0)
    hi = np.minimum(idx + 10, dim - 1)
    h = (y[hi] - y[lo]) / (hi - lo)
    fallback = float(np.mean(np.diff(y)))
    if fallback <= 0:
        fallback = 1.0
    h = np.where(h > 0, h, fallback)
    z = (y[:, None] - y[None, :]) / (sigma_u * h[None, :])
    x = ndtr(z).sum(axis=1)
    x = np.sort(x)
    span = x[-1] - x[0]
    if span <= 0:
        raise ValueError("degenerate unfolding")
    return (x - x[0]) * (dim - 1) / span


def s2(ev: Iterable[float], sigma_u: float) -> np.ndarray:
    """Binned S2 pair-correlation estimator on the 20 pre-registered centers."""
    x = _unfold(np.asarray(ev, dtype=np.float64), sigma_u)
    iu = np.triu_indices(x.size, 1)
    dist = np.abs(x[:, None] - x[None, :])[iu]
    hist, _ = np.histogram(dist, bins=FINE_EDGES)
    return (2.0 / x.size) * (hist @ KERNEL.T)


def gue_target(u: float) -> float:
    """Montgomery/GUE pair correlation target, with the u=0 limit."""
    if u == 0:
        return 0.0
    return 1.0 - (math.sin(math.pi * u) / (math.pi * u)) ** 2


def kept_bin_mask(dim: int) -> np.ndarray:
    """Bins with expected GUE pair count >= 5."""
    expected = np.array([dim * gue_target(u) * 0.5 for u in U_CENTERS])
    return expected >= 5.0


def matrix_sha256(seed: int, dim: int, b: int) -> str:
    """Canonical hash of the exact upper-triangle integer data."""
    re, im = _raw_ints(seed, dim)
    lines = [f"{dim}:{b}"]
    for i in range(dim):
        for j in range(i, min(dim, i + b + 1)):
            if i == j:
                lines.append(f"{i},{j},{int(re[i, j])}")
            else:
                lines.append(
                    f"{i},{j},{int(re[i, j])},{int(im[i, j])},"
                    f"{int(re[j, i])},{int(im[j, i])}"
                )
    payload = "\n".join(lines)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def spot_check(seed: int, dim: int, b: int, bits: int = 128) -> dict:
    """Arb interval check of one exact-rational RBM matrix."""
    re, im = _raw_ints(seed, dim)
    a_np = _matrix_from_ints(re, im, b)
    ev_np = np.sort(np.linalg.eigvalsh(a_np))
    with ctx.workprec(bits):
        m = acb_mat(dim, dim)
        for i in range(dim):
            for j in range(max(0, i - b), min(dim, i + b + 1)):
                if i == j:
                    m[i, j] = acb(arb(fmpq(int(re[i, j]), 32768)), arb(0))
                elif i < j:
                    real = arb(
                        fmpq(int(re[i, j]) + int(re[j, i]), 65536)
                    )
                    imag = arb(
                        fmpq(int(im[i, j]) - int(im[j, i]), 65536)
                    )
                    m[i, j] = acb(real, imag)
                    m[j, i] = acb(real, -imag)
        ev_arb = m.eig()
    imag_ok = all(e.imag.contains(arb(0)) for e in ev_arb)
    mids = np.array(sorted(float(e.real.mid()) for e in ev_arb), dtype=np.float64)
    max_diff = float(np.max(np.abs(mids - ev_np)))
    return {
        "b": b,
        "bits": bits,
        "dim": dim,
        "matrix_sha256": matrix_sha256(seed, dim, b),
        "imaginary_parts_contain_zero": bool(imag_ok),
        "max_abs_eigenvalue_diff": max_diff,
        "tolerance": 1e-8,
        "pass": bool(imag_ok and max_diff <= 1e-8),
    }


def _spectrum_stats(
    kind: str,
    role: str,
    count: int,
    config: Config,
) -> dict:
    """Collect S1 and S2 arrays for one ensemble."""
    n_bins = len(U_CENTERS)
    s1_arr = {chart: np.empty(count, dtype=np.float64) for chart in CHARTS}
    s2_arr = {
        (sigma_u, chart): np.empty((count, n_bins), dtype=np.float64)
        for sigma_u in SIGMA_U
        for chart in CHARTS
    }
    for i in range(count):
        label = f"{kind}:{role}:{i}"
        seed = derive_seed(label, config.seed)
        ev = (
            gue_levels(seed, config.dim)
            if kind == "gue"
            else poisson_levels(seed, config.dim)
        )
        for chart in CHARTS:
            levels = chart_levels(ev, chart)
            s1_arr[chart][i] = s1(levels)
            for sigma_u in SIGMA_U:
                s2_arr[(sigma_u, chart)][i] = s2(levels, sigma_u)
    return {"s1": s1_arr, "s2": s2_arr}


def _rbm_stats(config: Config) -> dict[str, dict]:
    n_bins = len(U_CENTERS)
    out: dict[str, dict] = {}
    for b in config.bandwidths:
        s1_arr = {chart: np.empty(config.n_matrices) for chart in CHARTS}
        s2_arr = {
            (sigma_u, chart): np.empty((config.n_matrices, n_bins))
            for sigma_u in SIGMA_U
            for chart in CHARTS
        }
        for i in range(config.n_matrices):
            seed = derive_seed(f"rbm:{b}:{i}", config.seed)
            ev = rbm_levels(seed, config.dim, b)
            for chart in CHARTS:
                levels = chart_levels(ev, chart)
                s1_arr[chart][i] = s1(levels)
                for sigma_u in SIGMA_U:
                    s2_arr[(sigma_u, chart)][i] = s2(levels, sigma_u)
        out[str(b)] = {"s1": s1_arr, "s2": s2_arr}
    return out


def _bootstrap_rbar(
    ref: np.ndarray,
    n_obs: int,
    config: Config,
    label: str,
) -> np.ndarray:
    rng = np.random.default_rng(derive_seed(label, config.seed))
    idx = rng.integers(0, ref.size, size=(config.n_bootstrap, n_obs))
    return ref[idx].mean(axis=1)


def _rbar_test(
    obs: np.ndarray,
    ref: np.ndarray,
    config: Config,
    label: str,
) -> dict:
    obs_mean = float(np.mean(obs))
    ref_mean = float(np.mean(ref))
    ref_sd = float(np.std(ref, ddof=1))
    boot = _bootstrap_rbar(ref, obs.size, config, label)
    hits = int(np.count_nonzero(np.abs(boot - ref_mean) >= abs(obs_mean - ref_mean)))
    p_two = hits / config.n_bootstrap
    z = 0.0 if ref_sd == 0 else (obs_mean - ref_mean) / ref_sd
    return {
        "obs_mean": obs_mean,
        "obs_sd": float(np.std(obs, ddof=1)),
        "ref_mean": ref_mean,
        "ref_sd": ref_sd,
        "z": float(z),
        "p_two_sided": p_two,
        "p_count": hits,
        "p_n": config.n_bootstrap,
    }


def _bootstrap_chi2(
    ref: np.ndarray,
    n_obs: int,
    config: Config,
    label: str,
) -> np.ndarray:
    """Bootstrap chi-square null distribution for mean rows of size n_obs."""
    ref = np.asarray(ref, dtype=np.float64)
    mean = ref.mean(axis=0)
    var = ref.var(axis=0, ddof=1)
    var = np.maximum(var, 1e-300)
    rng = np.random.default_rng(derive_seed(label, config.seed))
    idx = rng.integers(0, ref.shape[0], size=(config.n_bootstrap, n_obs))
    boot = ref[idx].mean(axis=1)
    return np.sum((boot - mean) ** 2 / (var / n_obs), axis=1)


def _chi2_obs(
    obs: np.ndarray,
    ref: np.ndarray,
    n_obs: int,
) -> float:
    mean = ref.mean(axis=0)
    var = np.maximum(ref.var(axis=0, ddof=1), 1e-300)
    return float(np.sum((obs.mean(axis=0) - mean) ** 2 / (var / n_obs)))


def _s2_test(
    obs: np.ndarray,
    ref_gue: np.ndarray,
    ref_pois: np.ndarray,
    config: Config,
    label: str,
    mask: np.ndarray,
) -> dict:
    obs = obs[:, mask]
    ref_gue = ref_gue[:, mask]
    ref_pois = ref_pois[:, mask]
    chi_gue = _chi2_obs(obs, ref_gue, obs.shape[0])
    chi_pois = _chi2_obs(obs, ref_pois, obs.shape[0])
    boot_gue = _bootstrap_chi2(ref_gue, obs.shape[0], config, label + ":gue")
    boot_pois = _bootstrap_chi2(ref_pois, obs.shape[0], config, label + ":pois")
    gue_hits = int(np.count_nonzero(boot_gue >= chi_gue))
    pois_hits = int(np.count_nonzero(boot_pois <= chi_pois))
    p_gue = gue_hits / config.n_bootstrap
    p_pois = pois_hits / config.n_bootstrap
    norm_gue = chi_gue / float(np.mean(boot_gue))
    norm_pois = chi_pois / float(np.mean(boot_pois))
    label_phase = "GUE" if norm_gue < norm_pois else "POISSON"
    return {
        "n_bins": int(np.count_nonzero(mask)),
        "chi2_gue": float(chi_gue),
        "chi2_pois": float(chi_pois),
        "p_gue": p_gue,
        "p_pois": p_pois,
        "p_gue_count": gue_hits,
        "p_pois_count": pois_hits,
        "p_n": config.n_bootstrap,
        "norm_gue": float(norm_gue),
        "norm_pois": float(norm_pois),
        "label": label_phase,
    }


def _round(value):
    """JSON-safe, stable float rendering."""
    if isinstance(value, float):
        return float(round(value, 12))
    if isinstance(value, np.floating):
        return float(round(float(value), 12))
    if isinstance(value, np.integer):
        return int(value)
    raise TypeError(f"not JSON-safe: {type(value)}")


def run_campaign(config: Config = FULL_CONFIG, do_spot_check: bool = True) -> dict:
    """Run the full pre-registered campaign and return a JSON-safe receipt."""
    if config.dim < 5:
        raise ValueError("dim must be at least 5")
    if not config.bandwidths:
        raise ValueError("at least one bandwidth is required")
    if any(not (0 <= b < config.dim) for b in config.bandwidths):
        raise ValueError("each bandwidth must satisfy 0 <= b < dim")

    mask = kept_bin_mask(config.dim)
    reference = {
        "gue": _spectrum_stats("gue", "ref", config.n_reference, config),
        "pois": _spectrum_stats("pois", "ref", config.n_reference, config),
    }
    calibration = {
        "gue": _spectrum_stats("gue", "cal", config.n_calibration, config),
        "pois": _spectrum_stats("pois", "cal", config.n_calibration, config),
    }
    rbm = _rbm_stats(config)

    # Null calibration: S1 and S2.
    calibration_s1 = {"gue": {}, "pois": {}}
    calibration_s2 = {"gue": {}, "pois": {}}
    for kind in ("gue", "pois"):
        for chart in CHARTS:
            test = _rbar_test(
                calibration[kind]["s1"][chart],
                reference[kind]["s1"][chart],
                config,
                f"cal:{kind}:s1:{chart}",
            )
            other_kind = "pois" if kind == "gue" else "gue"
            other = _rbar_test(
                calibration[kind]["s1"][chart],
                reference[other_kind]["s1"][chart],
                config,
                f"cal:{kind}:s1:{chart}:other",
            )
            z_gue = test["z"] if kind == "gue" else other["z"]
            z_pois = test["z"] if kind == "pois" else other["z"]
            label = "GUE" if abs(z_gue) < abs(z_pois) else "POISSON"
            calibration_s1[kind][chart] = {
                "own": test,
                "other": other,
                "label": label,
                "correct": label == ("GUE" if kind == "gue" else "POISSON"),
            }
        for sigma_u in SIGMA_U:
            for chart in CHARTS:
                test = _s2_test(
                    calibration[kind]["s2"][(sigma_u, chart)],
                    reference["gue"]["s2"][(sigma_u, chart)],
                    reference["pois"]["s2"][(sigma_u, chart)],
                    config,
                    f"cal:{kind}:s2:{sigma_u}:{chart}",
                    mask,
                )
                own_p = test["p_gue"] if kind == "gue" else test["p_pois"]
                calibration_s2[kind][(sigma_u, chart)] = {
                    **test,
                    "own_p": own_p,
                    "correct": test["label"] == ("GUE" if kind == "gue" else "POISSON"),
                    "own_p_ok": own_p >= 0.05,
                }

    # RBM tests.
    rbm_out: dict[str, dict] = {}
    for b in config.bandwidths:
        key = str(b)
        s1_out = {}
        for chart in CHARTS:
            test = _rbar_test(
                rbm[key]["s1"][chart],
                reference["gue"]["s1"][chart],
                config,
                f"rbm:{b}:s1:{chart}:gue",
            )
            other = _rbar_test(
                rbm[key]["s1"][chart],
                reference["pois"]["s1"][chart],
                config,
                f"rbm:{b}:s1:{chart}:pois",
            )
            label = "GUE" if abs(test["z"]) < abs(other["z"]) else "POISSON"
            s1_out[chart] = {
                "obs_mean": test["obs_mean"],
                "obs_sd": test["obs_sd"],
                "gue": test,
                "pois": other,
                "label": label,
            }
        s2_out = {}
        for sigma_u in SIGMA_U:
            for chart in CHARTS:
                s2_out[(sigma_u, chart)] = _s2_test(
                    rbm[key]["s2"][(sigma_u, chart)],
                    reference["gue"]["s2"][(sigma_u, chart)],
                    reference["pois"]["s2"][(sigma_u, chart)],
                    config,
                    f"rbm:{b}:s2:{sigma_u}:{chart}",
                    mask,
                )
        rbm_out[key] = {"s1": s1_out, "s2": s2_out}

    s1_correct = sum(
        1
        for kind in ("gue", "pois")
        for chart in CHARTS
        if calibration_s1[kind][chart]["correct"]
    )
    s2_correct = sum(
        1
        for kind in ("gue", "pois")
        for sigma_u in SIGMA_U
        for chart in CHARTS
        if calibration_s2[kind][(sigma_u, chart)]["correct"]
        and calibration_s2[kind][(sigma_u, chart)]["own_p_ok"]
    )
    calibration_s1_pass = s1_correct == 4
    calibration_s2_pass = s2_correct >= 10

    # RBM S1: monotone and extreme labels.
    s1_trend = {}
    for chart in CHARTS:
        vals = [rbm_out[str(b)]["s1"][chart]["obs_mean"] for b in config.bandwidths]
        s1_trend[chart] = bool(
            all(vals[i + 1] - vals[i] > 0.01 for i in range(len(vals) - 1))
        )
    s1_extreme = {
        "b_min": all(
            rbm_out[str(config.bandwidths[0])]["s1"][chart]["label"] == "POISSON"
            for chart in CHARTS
        ),
        "b_max": all(
            rbm_out[str(config.bandwidths[-1])]["s1"][chart]["label"] == "GUE"
            for chart in CHARTS
        ),
    }
    s1_pass = bool(all(s1_trend.values()) and all(s1_extreme.values()))

    # RBM S2: extreme labels at b_min and b_max.
    s2_extreme = {}
    for which, b in (("b_min", config.bandwidths[0]), ("b_max", config.bandwidths[-1])):
        labels = [
            rbm_out[str(b)]["s2"][(sigma_u, chart)]["label"]
            for sigma_u in SIGMA_U
            for chart in CHARTS
        ]
        target = "POISSON" if which == "b_min" else "GUE"
        s2_extreme[which] = {
            "target": target,
            "count": int(sum(label == target for label in labels)),
            "n": len(labels),
            "pass": sum(label == target for label in labels) >= 5,
        }
    s2_pass = bool(
        s2_extreme["b_min"]["pass"] and s2_extreme["b_max"]["pass"]
    )

    integrity = {"spot_checks": [], "pass": True}
    if do_spot_check:
        for b in config.bandwidths:
            seed = derive_seed(f"rbm:{b}:0", config.seed)
            check = spot_check(seed, config.dim, b)
            integrity["spot_checks"].append(check)
            integrity["pass"] = bool(integrity["pass"] and check["pass"])

    if not (calibration_s1_pass and calibration_s2_pass):
        verdict = "FAILED"
    elif not integrity["pass"]:
        verdict = "FAILED"
    elif s1_pass and s2_pass:
        verdict = "PASS"
    elif s1_pass or s2_pass:
        verdict = "PARTIAL"
    else:
        verdict = "INCONCLUSIVE"

    return {
        "schema": SCHEMA,
        "prereg_sha256": _sha256_file_lf(PREREG_PATH),
        "config": {
            **asdict(config),
            "sigma_u": list(SIGMA_U),
            "charts": list(CHARTS),
            "sigma_e": SIGMA_E,
            "u_centers": list(U_CENTERS),
            "fine_width": FINE_WIDTH,
        },
        "bin_mask": [bool(x) for x in mask],
        "calibration": {
            "s1": {
                kind: {
                    chart: {
                        "own": calibration_s1[kind][chart]["own"],
                        "other": calibration_s1[kind][chart]["other"],
                        "label": calibration_s1[kind][chart]["label"],
                        "correct": calibration_s1[kind][chart]["correct"],
                    }
                    for chart in CHARTS
                }
                for kind in ("gue", "pois")
            },
            "s2": {
                kind: {
                    f"{sigma_u}|{chart}": calibration_s2[kind][(sigma_u, chart)]
                    for sigma_u in SIGMA_U
                    for chart in CHARTS
                }
                for kind in ("gue", "pois")
            },
            "s1_correct": s1_correct,
            "s2_correct": s2_correct,
            "s1_pass": calibration_s1_pass,
            "s2_pass": calibration_s2_pass,
        },
        "rbm": {
            b: {
                "s1": {
                    chart: {
                        "obs_mean": rbm_out[b]["s1"][chart]["obs_mean"],
                        "obs_sd": rbm_out[b]["s1"][chart]["obs_sd"],
                        "gue": rbm_out[b]["s1"][chart]["gue"],
                        "pois": rbm_out[b]["s1"][chart]["pois"],
                        "label": rbm_out[b]["s1"][chart]["label"],
                    }
                    for chart in CHARTS
                },
                "s2": {
                    f"{sigma_u}|{chart}": rbm_out[b]["s2"][(sigma_u, chart)]
                    for sigma_u in SIGMA_U
                    for chart in CHARTS
                },
            }
            for b in map(str, config.bandwidths)
        },
        "s1_trend": s1_trend,
        "s1_extreme": s1_extreme,
        "s2_extreme": s2_extreme,
        "s1_pass": s1_pass,
        "s2_pass": s2_pass,
        "integrity": integrity,
        "verdict": verdict,
    }


def _sha256_file_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def receipt_sha256(receipt: dict) -> str:
    return hashlib.sha256(canonical_json(receipt).encode("utf-8")).hexdigest()


def write_receipt(
    path: Path | str = RECEIPT_PATH,
    config: Config = FULL_CONFIG,
    do_spot_check: bool = True,
) -> str:
    receipt = run_campaign(config=config, do_spot_check=do_spot_check)
    text = json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    Path(path).write_text(text, encoding="utf-8", newline="\n")
    return receipt_sha256(receipt)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RBM Anderson S1/S2 benchmark")
    parser.add_argument("--quick", action="store_true", help="small guard configuration")
    parser.add_argument("--no-spot-check", action="store_true", help="skip Arb spot-check")
    parser.add_argument("--out", default=str(RECEIPT_PATH), help="receipt output path")
    args = parser.parse_args(argv)
    config = QUICK_CONFIG if args.quick else FULL_CONFIG
    digest = write_receipt(
        path=args.out,
        config=config,
        do_spot_check=not args.no_spot_check,
    )
    receipt = json.loads(Path(args.out).read_text(encoding="utf-8"))
    print(f"wrote {args.out}")
    print(f"verdict: {receipt['verdict']}")
    print(f"receipt sha256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


