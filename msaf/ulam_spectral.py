"""Finite Ulam spectral-closure certificate for a chaotic skew tent map.

The exact layer is rational: the map has full branches with rational
breakpoints, the partition is uniform, and every Ulam entry is an exact
``Fraction``.  The spectral layer converts the exact matrix to an ``arb_mat``
and asks ``arb_mat.eig`` for interval enclosures on a pre-registered precision
ladder.

This is a finite matrix certificate.  It does not certify the continuous
Frobenius-Perron operator, ergodicity, mixing, or a Newton contraction.  The
logistic map is not used: its symmetric two-to-one Ulam discretisation is
rank-deficient and cannot be isolated by ``arb_mat.eig`` at the locked sizes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Sequence

from flint import arb, arb_mat, fmpq, fmpq_mat

from .precision import ball_precision

SCHEMA = "msaf.ulam_spectral.v1"
TARGET_WIDTH_STR = "1e-25"
TARGET_WIDTH = Fraction(1, 10**25)
MAX_RESOLUTION_ATTEMPTS = 60
MAX_PRECISION_BITS = 1024
RESOLUTION_LADDER = (64, 128, 256, 512, 1024)
ALGORITHM = "rump"

INSTANCES = (
    {"role": "primary", "n": 16, "p_num": 8, "p_den": 17},
    {"role": "replication", "n": 32, "p_num": 16, "p_den": 33},
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PREREG_PATH = REPO_ROOT / "reports" / "PREREG_ULAM_SPECTRAL_2026-10-21.md"
RECEIPT_PATH = REPO_ROOT / "reports" / "ulam_spectral_2026-10-21.json"


class ResolutionAlarm(RuntimeError):
    """Finite precision budget exhausted before the spectral target was met.

    This is a capacity alarm, not evidence of a chaotic singularity.  Catch it
    and record ``INCONCLUSIVE``/``PARTIAL``; never relabel it as a proof of
    blow-up or as a successful enclosure.
    """


def skew_tent(x: Fraction, p: Fraction) -> Fraction:
    """Evaluate the full-branched skew tent map ``T_p`` exactly."""
    if not (Fraction(0) < p < Fraction(1)):
        raise ValueError("p must lie strictly between 0 and 1")
    if not (Fraction(0) <= x <= Fraction(1)):
        raise ValueError("x must lie in [0, 1]")
    if x <= p:
        return x / p
    return (Fraction(1) - x) / (Fraction(1) - p)


def preimages(n: int, p: Fraction, j: int) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
    """Return the two exact preimage intervals of ``I_j`` under ``T_p``."""
    if not (0 <= j < n):
        raise ValueError("j must be a partition index")
    left = (p * Fraction(j, n), p * Fraction(j + 1, n))
    right = (
        Fraction(1) - (Fraction(1) - p) * Fraction(j + 1, n),
        Fraction(1) - (Fraction(1) - p) * Fraction(j, n),
    )
    return left, right


def ulam_matrix(n: int, p: Fraction) -> list[list[Fraction]]:
    """Build the exact row-stochastic Ulam matrix on a uniform partition.

    Row ``i`` is the source interval ``I_i``; column ``j`` is the target
    interval ``I_j``.  Endpoint overlaps have measure zero and contribute
    nothing, so the exact overlap formula is unaffected by closed endpoints.
    """
    if n < 2:
        raise ValueError("n must be at least 2")
    if not (Fraction(0) < p < Fraction(1)):
        raise ValueError("p must lie strictly between 0 and 1")
    matrix: list[list[Fraction]] = []
    for i in range(n):
        lo = Fraction(i, n)
        hi = Fraction(i + 1, n)
        row: list[Fraction] = []
        for j in range(n):
            left, right = preimages(n, p, j)
            overlap = Fraction(0)
            for a, b in (left, right):
                width = min(hi, b) - max(lo, a)
                if width > 0:
                    overlap += width
            row.append(overlap * n)
        matrix.append(row)
    return matrix


def matrix_to_fmpq(matrix: Sequence[Sequence[Fraction]]) -> fmpq_mat:
    """Convert an exact rational matrix to ``fmpq_mat`` without floats."""
    n = len(matrix)
    if n == 0 or any(len(row) != n for row in matrix):
        raise ValueError("matrix must be non-empty and square")
    out = fmpq_mat(n, n)
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            if not isinstance(value, Fraction):
                raise TypeError("matrix entries must be Fraction")
            out[i, j] = fmpq(value.numerator, value.denominator)
    return out


def matrix_sha256(matrix: Sequence[Sequence[Fraction]]) -> str:
    """Canonical SHA-256 of an exact rational matrix."""
    rows = [
        ",".join(f"{value.numerator}/{value.denominator}" for value in row)
        for row in matrix
    ]
    payload = f"{len(matrix)}x{len(matrix[0])}\n" + "\n".join(rows)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _fmpq_str(value: fmpq) -> str:
    return f"{int(value.p)}/{int(value.q)}"


def _poly_sha256(poly) -> str:
    payload = f"{poly.degree()}\n" + ",".join(_fmpq_str(c) for c in poly.coeffs())
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _identity(n: int) -> fmpq_mat:
    out = fmpq_mat(n, n)
    for i in range(n):
        out[i, i] = fmpq(1)
    return out


def exact_checks(n: int, p: Fraction) -> dict:
    """Run the exact construction and simple-spectrum checks for one instance."""
    matrix = ulam_matrix(n, p)
    exact = matrix_to_fmpq(matrix)
    row_sums = [sum(row, Fraction(0)) for row in matrix]
    nonnegative = all(value >= 0 for row in matrix for value in row)
    row_stochastic = all(value == 1 for value in row_sums)
    asymmetric_pairs = sum(
        1 for i in range(n) for j in range(i + 1, n) if matrix[i][j] != matrix[j][i]
    )
    rank = exact.rank()
    rank_minus_identity = (exact - _identity(n)).rank()
    charpoly = exact.charpoly()
    discriminant = charpoly.discriminant()
    determinant = exact.det()
    nonzero = sum(1 for row in matrix for value in row if value != 0)
    positive = [value for row in matrix for value in row if value > 0]

    checks = {
        "C1_nonnegative": nonnegative,
        "C1_row_stochastic": row_stochastic,
        "C1_nonsymmetric": asymmetric_pairs > 0,
        "C1_full_rank": rank == n,
        "C1_perron_simple": rank_minus_identity == n - 1,
        "C1_squarefree": discriminant != 0,
    }
    return {
        "n": n,
        "p": str(p),
        "matrix_sha256": matrix_sha256(matrix),
        "nonzero_entries": nonzero,
        "asymmetric_pairs": asymmetric_pairs,
        "rank": rank,
        "rank_minus_identity": rank_minus_identity,
        "determinant": _fmpq_str(determinant),
        "charpoly_degree": charpoly.degree(),
        "charpoly_sha256": _poly_sha256(charpoly),
        "discriminant_nonzero": discriminant != 0,
        "discriminant_sign": 1 if int(discriminant.p) > 0 else -1,
        "min_positive_entry": str(min(positive)),
        "max_entry": str(max(positive)),
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAILED",
    }


def _ball_payload(value: arb, digits: int = 30) -> dict:
    """Serialise an Arb ball without pretending its midpoint is exact."""
    return {
        "mid": value.mid().str(digits, radius=False),
        "rad": value.rad().str(10, radius=True),
    }


def _eigenvalue_payload(value) -> dict:
    return {
        "real": _ball_payload(value.real),
        "imag": _ball_payload(value.imag),
        "abs_upper": _ball_payload(value.abs_upper()),
    }


def _measure_rung(matrix: fmpq_mat, bits: int) -> tuple[dict, arb | None]:
    """Measure one precision rung and return ``(payload, max_width_ball)``.

    Every comparison is performed inside the ``ball_precision`` context.  This
    matters: constructing a target ball after the context exits would silently
    evaluate it at the process default precision.
    """
    n = matrix.nrows()
    with ball_precision(bits):
        target = arb(fmpq(TARGET_WIDTH.numerator, TARGET_WIDTH.denominator))
        try:
            eigenvalues = arb_mat(matrix).eig(
                multiple=True, algorithm=ALGORITHM
            )
        except Exception as exc:  # noqa: BLE001 - the solver refuses some spectra
            return (
                {
                    "bits": bits,
                    "algorithm": ALGORITHM,
                    "ok": False,
                    "error": f"{type(exc).__name__}: {exc}",
                    "n_eigenvalues": 0,
                    "target_met": False,
                },
                None,
            )

        width = arb(0)
        for value in eigenvalues:
            real_width = value.real.rad()
            imag_width = value.imag.rad()
            local = (
                real_width
                if bool(real_width.upper() >= imag_width.upper())
                else imag_width
            )
            if bool(local.upper() > width.upper()):
                width = local

        perron_indices = [
            index
            for index, value in enumerate(eigenvalues)
            if bool(value.real.contains(arb(1))) and bool(value.imag.contains(arb(0)))
        ]
        other_abs = []
        for index, value in enumerate(eigenvalues):
            if index in perron_indices:
                continue
            other_abs.append(value.abs_upper().upper())

        max_other = arb(0)
        for value in other_abs:
            if bool(value.upper() > max_other.upper()):
                max_other = value
        all_other_inside = all(bool(value < arb(1)) for value in other_abs)
        perron_ok = len(perron_indices) == 1
        target_met = bool(width.upper() <= target)
        spectral_gap = arb(1) - max_other
        payload = {
            "bits": bits,
            "algorithm": ALGORITHM,
            "ok": len(eigenvalues) == n and perron_ok and all_other_inside,
            "n_eigenvalues": len(eigenvalues),
            "perron_indices": perron_indices,
            "perron_unique": perron_ok,
            "all_other_modulus_below_one": all_other_inside,
            "width": _ball_payload(width),
            "width_float": float(width),
            "target_met": target_met,
            "max_other_abs_upper": _ball_payload(max_other),
            "spectral_gap_lower": _ball_payload(spectral_gap),
            "eigenvalues": [_eigenvalue_payload(value) for value in eigenvalues],
        }
        return payload, width


def measure_ladder(
    matrix: fmpq_mat, ladder: Sequence[int] = RESOLUTION_LADDER
) -> dict:
    """Measure every rung of the pre-registered precision ladder."""
    if len(ladder) > MAX_RESOLUTION_ATTEMPTS:
        raise ValueError("resolution ladder exceeds the 60-attempt budget")
    if any(bits < 1 or bits > MAX_PRECISION_BITS for bits in ladder):
        raise ValueError("precision rung outside the 1024-bit cap")
    if not ladder:
        raise ValueError("resolution ladder must not be empty")

    payloads: list[dict] = []
    widths: list[tuple[int, arb]] = []
    for bits in ladder:
        payload, width = _measure_rung(matrix, bits)
        payloads.append(payload)
        if width is not None:
            widths.append((bits, width))

    all_rungs_ok = all(payload["ok"] for payload in payloads)
    target_met = any(payload["target_met"] for payload in payloads)
    contraction = len(widths) == len(ladder)
    if contraction:
        for index in range(1, len(widths)):
            previous = widths[index - 1][1]
            current = widths[index][1]
            if not bool(current.upper() < previous.lower()):
                contraction = False
                break
    first_pass_bits = next(
        (payload["bits"] for payload in payloads if payload["target_met"]), None
    )
    alarm_reasons: list[str] = []
    if not all_rungs_ok:
        alarm_reasons.append("EIGENSOLVER-FAILED")
    if not target_met:
        alarm_reasons.append("TARGET-NOT-MET")
    return {
        "ladder": [int(bits) for bits in ladder],
        "target_width": TARGET_WIDTH_STR,
        "attempts_used": len(ladder),
        "max_attempts": MAX_RESOLUTION_ATTEMPTS,
        "max_precision_bits": MAX_PRECISION_BITS,
        "all_rungs_ok": all_rungs_ok,
        "target_met": target_met,
        "first_pass_bits": first_pass_bits,
        "contraction": contraction,
        "alarm_triggered": bool(alarm_reasons),
        "alarm_reasons": alarm_reasons,
        "rungs": payloads,
    }


def assert_resolution(result: dict) -> None:
    """Raise ``ResolutionAlarm`` unless the locked resolution gates pass."""
    if not result["all_rungs_ok"]:
        raise ResolutionAlarm(
            "arb_mat.eig failed to isolate the locked spectrum at one or more rungs"
        )
    if not result["target_met"]:
        raise ResolutionAlarm(
            f"no rung reached the width target {TARGET_WIDTH_STR} before the "
            f"{MAX_PRECISION_BITS}-bit cap"
        )
    if not result["contraction"]:
        raise ResolutionAlarm("interval widths did not contract strictly between rungs")


def certify_instance(role: str, n: int, p: Fraction) -> dict:
    """Certify one locked instance and return a JSON-safe record."""
    exact = exact_checks(n, p)
    spectral = measure_ladder(matrix_to_fmpq(ulam_matrix(n, p)))
    alarm_message = None
    try:
        assert_resolution(spectral)
    except ResolutionAlarm as exc:
        alarm_message = str(exc)

    checks = {
        "C1_exact": exact["status"] == "PASS",
        "C2_all_rungs": spectral["all_rungs_ok"],
        "C2_target": spectral["target_met"],
        "C2_contraction": spectral["contraction"],
        "C3_no_alarm": alarm_message is None,
    }
    if not checks["C1_exact"]:
        status = "FAILED"
    elif all(checks.values()):
        status = "PASS"
    else:
        status = "PARTIAL"
    return {
        "role": role,
        "n": n,
        "p": str(p),
        "exact": exact,
        "spectral": spectral,
        "alarm_message": alarm_message,
        "newton_contraction_tested": False,
        "checks": checks,
        "status": status,
    }


def _sha256_file_lf(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def build_receipt(prereg_sha256: str | None = None) -> dict:
    """Build the deterministic receipt for the two locked instances."""
    prereg = prereg_sha256 or _sha256_file_lf(PREREG_PATH)
    instances = []
    for item in INSTANCES:
        p = Fraction(int(item["p_num"]), int(item["p_den"]))
        instances.append(certify_instance(item["role"], int(item["n"]), p))
    if any(instance["status"] == "FAILED" for instance in instances):
        verdict = "FAILED"
    elif all(instance["status"] == "PASS" for instance in instances):
        verdict = "PASS"
    else:
        verdict = "PARTIAL"
    return {
        "schema": SCHEMA,
        "prereg_sha256": prereg,
        "config": {
            "target_width": TARGET_WIDTH_STR,
            "resolution_ladder": [int(bits) for bits in RESOLUTION_LADDER],
            "max_resolution_attempts": MAX_RESOLUTION_ATTEMPTS,
            "max_precision_bits": MAX_PRECISION_BITS,
            "algorithm": ALGORITHM,
            "instances": [dict(item) for item in INSTANCES],
        },
        "scope": {
            "newton_contraction_tested": False,
            "continuous_operator_claim": False,
            "ergodicity_claim": False,
            "mixing_claim": False,
            "logistic_spectrum_claim": False,
            "sealed_campaigns_rerun": False,
        },
        "instances": instances,
        "verdict": verdict,
    }


def canonical_json(value: object) -> str:
    """Canonical JSON used for the receipt hash."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def receipt_sha256(receipt: dict) -> str:
    """SHA-256 of the canonical receipt payload."""
    return hashlib.sha256(canonical_json(receipt).encode("utf-8")).hexdigest()


def write_receipt(path: Path | str = RECEIPT_PATH) -> str:
    """Write the receipt as UTF-8 with LF endings; return its hash."""
    receipt = build_receipt()
    text = json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    target = Path(path)
    target.write_text(text, encoding="utf-8", newline="\n")
    return receipt_sha256(receipt)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Finite Ulam spectral-closure certificate")
    parser.add_argument("--out", default=str(RECEIPT_PATH), help="receipt output path")
    args = parser.parse_args(argv)
    digest = write_receipt(args.out)
    receipt = json.loads(Path(args.out).read_text(encoding="utf-8"))
    print(f"wrote {args.out}")
    print(f"verdict: {receipt['verdict']}")
    print(f"receipt sha256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
