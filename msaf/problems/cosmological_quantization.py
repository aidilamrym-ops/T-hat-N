"""PLAN-10: Cosmological Quantisation and Spectral Refutation of Infinite Dark Energy.

Certifies the spectral bounds of the Theta_cosmo operator without a full
eigendecomposition.  The 802 x 802 matrix is symmetric and banded (bandwidth 2):

    A[i, i]   = (1 / N_steps) * ((i + 1)^2 + coupling)
    A[i, i+1] = -coupling / 2
    A[i, i+2] = -coupling / 8

Two independent rigorous checks are performed at 24000-bit Arb precision:

1. Gershgorin discs give lambda_min >= lower and lambda_max <= upper.
2. A banded LDL^T factorization of A and of I - A certifies that both are
   positive definite (all pivots strictly positive).  A positive definite
   I - A is equivalent to lambda_max(A) < 1.

The previous implementation called arb_mat.eig() on the dense 802 x 802
matrix.  At 24000 bits that is not feasible on the working machine (measured
scaling: n=64 took ~325 s; extrapolated n=802 ~7-10 days).  See the dated
amendment in reports/PREREG_COSMOLOGY_2026-11-03.md.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from flint import arb, ctx

PLAN = "PLAN-10"
CAMPAIGN = "Q-COSMOLOGICAL-QUANTIZATION"
PREREG_PATH = "reports/PREREG_COSMOLOGY_2026-11-03.md"
RECEIPT_PATH = "reports/cosmological_quantization_receipt_2026-11-03.json"
VALIDATION_TOKEN = "COSMOLOGICAL-CONTINUUM-SHATTERED"
PRECISION_BITS = 24000
BANDWIDTH = 2


@dataclass(frozen=True)
class BandedSymmetricMatrix:
    """Symmetric banded matrix with bandwidth 2.

    ``off1[i]`` is A[i, i+1] and ``off2[i]`` is A[i, i+2]; the lower triangle
    is implied by symmetry.
    """

    n: int
    diag: list
    off1: list
    off2: list


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_cosmological_tensor(dim: int) -> BandedSymmetricMatrix:
    """Construct the Theta_cosmo spectral tensor for cosmological vacuum energy.

    The operator is stored in its native banded form; materializing the dense
    802 x 802 matrix is unnecessary for the certified bounds.
    """
    ctx.prec = PRECISION_BITS

    # Physical constants in Arb
    N_steps = arb("5.44e61")  # D_obs / l_P
    planck_density = arb("1.0") / N_steps  # Holographic bound
    coupling = arb("1e-120")  # Cosmological constant suppression

    diag = [planck_density * (arb(i + 1) ** 2 + coupling) for i in range(dim)]
    off1 = [-coupling * arb("0.5") for _ in range(dim - 1)]
    off2 = [-coupling * arb("0.125") for _ in range(dim - 2)]
    return BandedSymmetricMatrix(dim, diag, off1, off2)


def gershgorin_bounds(mat: BandedSymmetricMatrix) -> tuple:
    """Rigorous real eigenvalue bounds for a symmetric banded matrix.

    For a symmetric matrix every eigenvalue lies in the union of the intervals
    [A[i,i] - R[i], A[i,i] + R[i]], where R[i] is the sum of absolute values of
    the off-diagonal entries in row i.  The returned lower bound is a rigorous
    lower bound for lambda_min and the upper bound is a rigorous upper bound
    for lambda_max.
    """
    lower = None
    upper = None

    for i in range(mat.n):
        radius = arb(0)
        if i >= 1:
            radius += abs(mat.off1[i - 1])
        if i + 1 < mat.n:
            radius += abs(mat.off1[i])
        if i >= 2:
            radius += abs(mat.off2[i - 2])
        if i + 2 < mat.n:
            radius += abs(mat.off2[i])

        row_lower = mat.diag[i] - radius
        row_upper = mat.diag[i] + radius
        if lower is None or row_lower < lower:
            lower = row_lower
        if upper is None or row_upper > upper:
            upper = row_upper

    return lower, upper


def banded_ldl(mat: BandedSymmetricMatrix) -> tuple:
    """Banded LDL^T factorization without pivoting.

    Returns (D, L1, L2), where D[i] is the i-th pivot and L1[i] = L[i+1, i],
    L2[i] = L[i+2, i].  For a symmetric positive definite matrix all D[i] are
    strictly positive.  Interval arithmetic makes the check rigorous: a pivot
    interval that is strictly positive certifies the true pivot is positive.
    """
    n = mat.n
    D = [None] * n
    L1 = [None] * (n - 1)
    L2 = [None] * (n - 2)

    for j in range(n):
        pivot = mat.diag[j]
        if j >= 1:
            pivot -= L1[j - 1] * L1[j - 1] * D[j - 1]
        if j >= 2:
            pivot -= L2[j - 2] * L2[j - 2] * D[j - 2]
        D[j] = pivot

        if j + 1 < n:
            value = mat.off1[j]
            if j >= 1:
                value -= L2[j - 1] * L1[j - 1] * D[j - 1]
            L1[j] = value / D[j]

        if j + 2 < n:
            L2[j] = mat.off2[j] / D[j]

    return D, L1, L2


def ldl_residual_contains(mat: BandedSymmetricMatrix, D: list, L1: list, L2: list) -> bool:
    """Check that the reconstructed L D L^T contains every entry of mat."""
    n = mat.n

    for i in range(n):
        reconstructed = D[i]
        if i >= 1:
            reconstructed += L1[i - 1] * L1[i - 1] * D[i - 1]
        if i >= 2:
            reconstructed += L2[i - 2] * L2[i - 2] * D[i - 2]
        if not reconstructed.contains(mat.diag[i]):
            return False

    for i in range(n - 1):
        reconstructed = L1[i] * D[i]
        if i >= 1:
            reconstructed += L2[i - 1] * L1[i - 1] * D[i - 1]
        if not reconstructed.contains(mat.off1[i]):
            return False

    for i in range(n - 2):
        if not (L2[i] * D[i]).contains(mat.off2[i]):
            return False

    return True


def identity_minus(mat: BandedSymmetricMatrix) -> BandedSymmetricMatrix:
    """Return the banded representation of I - mat."""
    return BandedSymmetricMatrix(
        mat.n,
        [arb(1) - d for d in mat.diag],
        [-x for x in mat.off1],
        [-x for x in mat.off2],
    )


def _max_radius(values: list) -> arb:
    worst = values[0].rad()
    for value in values[1:]:
        radius = value.rad()
        if radius > worst:
            worst = radius
    return worst


def run_cosmological_quantization_verification(write_receipt: bool = True) -> dict:
    """Run the certified verification.

    ``write_receipt=False`` is used by the test suite so that running the
    guard does not rewrite the pinned receipt (which carries run-specific
    timing fields and is hash-checked by reports/FENCE_REGISTRY.md).
    """
    start_time = time.time()
    start_clock = time.process_time()

    ctx.prec = PRECISION_BITS

    N = 401
    dim = 2 * N

    # Build the genuine cosmological spectral tensor in banded form.
    mat = build_cosmological_tensor(dim)

    # Rigorous spectral bounds via Gershgorin.
    lower, upper = gershgorin_bounds(mat)

    # Positive definiteness of A and I - A via banded LDL^T.
    D_A, L1_A, L2_A = banded_ldl(mat)
    pivots_A_positive = all(bool(d > 0) for d in D_A)
    residual_A = ldl_residual_contains(mat, D_A, L1_A, L2_A)

    mat_I_minus_A = identity_minus(mat)
    D_B, L1_B, L2_B = banded_ldl(mat_I_minus_A)
    pivots_B_positive = all(bool(d > 0) for d in D_B)
    residual_B = ldl_residual_contains(mat_I_minus_A, D_B, L1_B, L2_B)
    ldl_certified = pivots_A_positive and residual_A and pivots_B_positive and residual_B

    # Entropy gap from Pillar II
    entropy_gap = arb("0.5614")
    entropy_rad = arb("3.36e-74")
    delta_s = arb(entropy_gap, entropy_rad)

    barrier_bounded = bool(lower > 0) and bool(delta_s > 0)
    vacuum_collapsed = barrier_bounded and bool(upper < 1)

    verdict = "CERTIFIED" if (barrier_bounded and vacuum_collapsed and ldl_certified) else "FAILED"
    token = VALIDATION_TOKEN if verdict == "CERTIFIED" else "REJECTED"

    elapsed = time.time() - start_time
    end_clock = time.process_time()
    cpu_ticks = int((end_clock - start_clock) * 1e9)

    nonzero_entries = 3 * dim - 3  # diagonal, first off-diagonal, second off-diagonal
    bytes_per_arb = 2 * (PRECISION_BITS // 8)  # midpoint + radius, approximate
    matrix_bytes = nonzero_entries * bytes_per_arb

    result = {
        "plan": PLAN,
        "campaign": CAMPAIGN,
        "method": "gershgorin_bounds + banded_ldl",
        "matrix_layout": "symmetric banded (bandwidth 2)",
        "n_parameter": N,
        "dimension": dim,
        "precision_bits": PRECISION_BITS,
        "entropy_gap": str(delta_s),
        "lambda_min_lower_bound": str(lower),
        "lambda_max_upper_bound": str(upper),
        "lambda_min_midpoint": str(lower.mid()),
        "lambda_max_midpoint": str(upper.mid()),
        "lambda_min_radius": str(lower.rad()),
        "lambda_max_radius": str(upper.rad()),
        "matrix_nonzero_entries": nonzero_entries,
        "matrix_allocation_bytes": matrix_bytes,
        "worst_case_pivot_radius": str(_max_radius(D_A)),
        "ldl_pivots_positive_A": pivots_A_positive,
        "ldl_pivots_positive_I_minus_A": pivots_B_positive,
        "ldl_residual_contains_A": residual_A,
        "ldl_residual_contains_I_minus_A": residual_B,
        "ldl_certified": ldl_certified,
        "cpu_clock_ticks": cpu_ticks,
        "barrier_bounded": barrier_bounded,
        "vacuum_collapsed": vacuum_collapsed,
        "validation_token": token,
        "verdict": verdict,
        "wall_time_seconds": elapsed,
    }

    if write_receipt:
        receipt_file = repo_root() / RECEIPT_PATH
        receipt_file.parent.mkdir(parents=True, exist_ok=True)
        with open(receipt_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

    return result


if __name__ == "__main__":
    res = run_cosmological_quantization_verification()
    print(json.dumps(res, indent=2))
    print(f"Token: {res['validation_token']}")
    print(f"Wall time: {res['wall_time_seconds']:.2f}s")
