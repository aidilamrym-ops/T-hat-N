"""AD HOC zeta-block perturbation with Dirichlet-character coefficients.

This module deliberately does **not** construct the Guinand-Weil block of a
Dirichlet L-function.  It keeps the zeta pole block ``W02_zeta`` and the zeta
archimedean block ``WR_zeta`` unchanged and replaces only the prime-power
block by

    Wp_chi = sum_{q_k=p^a <= c} log(p) q_k^(-1/2) chi(q_k) * shape(q_k).

The resulting matrix is

    tau_pert = W02_zeta - WR_zeta - Wp_chi,

labelled ``AD HOC PERTURBATION`` everywhere.  Inertia of this finite matrix is
a statement about the finite matrix only.  It is not an explicit formula for
L(s, chi), not a zero-location result, and not a critical-line claim.

The local builder mirrors the published ``source_arb_ldlt_certify.py``
assembly.  When that external module is available it is used as a control:
the local zeta matrix must agree with the external zeta matrix entrywise
within the ball threshold.  The external file itself is never modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Sequence

from flint import acb, arb, arb_mat, ctx, dirichlet_char

from . import gw_character_arithmetic as chars

SCHEMA = "msaf.gw_char_adhoc.v1"

CONFIGS = (
    {"role": "primary", "c": 100, "N": 20, "prec": 600},
    {"role": "replication", "c": 200, "N": 20, "prec": 600},
)

CHARACTERS = ((12, 7), (12, 5), (15, 4), (15, 11))

REPO_ROOT = Path(__file__).resolve().parents[1]
PREREG_PATH = REPO_ROOT / "reports" / "PREREG_GW_CHAR_ADHOC_2026-10-21.md"
RECEIPT_PATH = REPO_ROOT / "reports" / "gw_char_adhoc_2026-10-21.json"
GW_DIR = Path(os.environ.get("GW_DIR", r"C:/Users/usER/oracle-toe/GUINAND_WEIL"))


class AdHocError(RuntimeError):
    """A finite ad hoc matrix invariant failed.

    This is not evidence about an L-function.
    """


def prime_powers_up_to(c: int) -> list[tuple[int, int]]:
    """Return ``(q, p)`` for prime powers ``q = p^a <= c``, sorted."""
    if c < 2:
        return []
    primes: list[int] = []
    for value in range(2, c + 1):
        if all(value % prime for prime in primes):
            primes.append(value)
    out: list[tuple[int, int]] = []
    for prime in primes:
        power = prime
        while power <= c:
            out.append((power, prime))
            if power > c // prime:
                break
            power *= prime
    out.sort()
    return out


def _geom_sums(n: int, L: arb, prec: int):
    """Rigorous geometric sums used by the zeta archimedean closed forms."""
    PI = arb.pi()
    w = 2 * PI * n / L
    w2 = w * w
    gS = arb(0)
    gCC = arb(0)
    gX1 = arb(0)
    gX2 = arb(0)
    threshold = arb(2) ** (-(prec + 24))
    k = 0
    while True:
        c_k = arb(2 * k) + arb("0.5")
        e = (-c_k * L).exp()
        den = c_k * c_k + w2
        gS += e / den
        if n != 0:
            gCC += e * w2 / (c_k * den)
        gX1 += e * c_k / den
        gX2 += e * (c_k * c_k - w2) / (den * den)
        if e < threshold and k > 2:
            break
        k += 1
    c_next = arb(2 * (k + 1)) + arb("0.5")
    one_minus_z = 1 - (-2 * L).exp()
    tail_geo = (-c_next * L).exp() / one_minus_z
    remainder = arb(4) * tail_geo

    def widen(value: arb) -> arb:
        return value + arb(0, remainder)

    return widen(gS), widen(gCC), widen(gX1), widen(gX2)


def _arb_closed_forms(N: int, c: int, prec: int):
    """Zeta archimedean closed forms, mirroring the external builder."""
    ctx.prec = prec
    L = arb(c).log()
    PI = arb.pi()
    quarter = arb("0.25")
    psi_quarter = quarter.digamma()
    S = [arb(0)] * (N + 1)
    CC = [arb(0)] * (N + 1)
    XC = [arb(0)] * (N + 1)
    for n in range(N + 1):
        w = 2 * PI * n / L
        zarg = acb(quarter, PI * n / L)
        psi = zarg.digamma()
        psi1 = zarg.polygamma(acb(1))
        gS, gCC, gX1, gX2 = _geom_sums(n, L, prec)
        if n == 0:
            S[n] = arb(0)
            CC[n] = arb(0)
        else:
            S[n] = arb("0.5") * psi.imag - w * gS
            CC[n] = -arb("0.5") * (psi.real - psi_quarter) + gCC
        XC[n] = arb("0.25") * psi1.real - L * gX1 - gX2
    return S, CC, XC, L


def _arb_J(L: arb) -> arb:
    U = (L / 2).exp()
    return (
        -2 * (U + 1).log()
        + (U * U + 1).log()
        + 2 * U.atan()
        + arb(2).log()
        - arb.pi() / 2
    )


def _arb_kappa(L: arb) -> arb:
    eL = L.exp()
    return (4 * arb.pi() * (eL - 1) / (eL + 1)).log() + arb.const_euler()


@contextmanager
def _precision(bits: int):
    saved = ctx.prec
    try:
        ctx.prec = int(bits)
        yield
    finally:
        ctx.prec = saved


def build_base(c: int, N: int, prec: int) -> dict:
    """Build the zeta blocks and the unperturbed zeta matrix.

    The loop is a local mirror of the published external assembly.  ``W02``,
    ``WR``, and ``Wp_zeta`` are kept separately so the ad hoc replacement can
    be audited.  ``tau_zeta`` is assembled entrywise in the same order as the
    external builder.
    """
    ctx.prec = prec
    S, CC, XC, L = _arb_closed_forms(N, c, prec)
    PI = arb.pi()
    sp2 = 16 * PI * PI
    l2 = L * L
    pref02 = 32 * L * (L / 4).sinh() ** 2
    kappa = _arb_kappa(L)
    J = _arb_J(L)
    pdata = prime_powers_up_to(c)
    weights = [arb(p).log() * (arb(q) ** arb("-0.5")) for q, p in pdata]
    positions = [arb(q).log() for q, p in pdata]
    M = len(weights)

    def S_signed(nn: int) -> arb:
        return S[nn] if nn >= 0 else -S[-nn]

    dim = 2 * N + 1
    W02 = arb_mat(dim, dim)
    WR = arb_mat(dim, dim)
    Wp = arb_mat(dim, dim)
    tau = arb_mat(dim, dim)
    arch_pole = arb_mat(dim, dim)
    for i in range(dim):
        n = i - N
        for j in range(i, dim):
            m = j - N
            num = l2 - sp2 * m * n
            den = (l2 + sp2 * m * m) * (l2 + sp2 * n * n)
            w02 = pref02 * num / den
            if n == m:
                wr = kappa + 2 * CC[abs(n)] + J - (2 / L) * XC[abs(n)]
            else:
                wr = (S_signed(m) - S_signed(n)) / (PI * (n - m))
            wp = arb(0)
            for idx in range(M):
                y = positions[idx]
                if n == m:
                    shape = 2 * (1 - y / L) * (2 * PI * n * y / L).cos()
                else:
                    shape = (
                        (2 * PI * m * y / L).sin()
                        - (2 * PI * n * y / L).sin()
                    ) / (PI * (n - m))
                wp += weights[idx] * shape
            W02[i, j] = W02[j, i] = w02
            WR[i, j] = WR[j, i] = wr
            Wp[i, j] = Wp[j, i] = wp
            arch_pole[i, j] = arch_pole[j, i] = w02 - wr
            tau[i, j] = tau[j, i] = w02 - wr - wp
    return {
        "c": c,
        "N": N,
        "prec": prec,
        "dim": dim,
        "L": L,
        "pdata": pdata,
        "weights": weights,
        "positions": positions,
        "W02": W02,
        "WR": WR,
        "Wp_zeta": Wp,
        "arch_pole": arch_pole,
        "tau_zeta": tau,
    }


def wp_from_values(base: dict, values: dict[int, int]) -> arb_mat:
    """Build ``Wp_chi`` from exact integer character values at prime powers."""
    L = base["L"]
    pdata = base["pdata"]
    weights = base["weights"]
    positions = base["positions"]
    dim = base["dim"]
    N = base["N"]
    PI = arb.pi()
    out = arb_mat(dim, dim)
    for i in range(dim):
        n = i - N
        for j in range(i, dim):
            m = j - N
            wp = arb(0)
            for idx, (q, p) in enumerate(pdata):
                chi = int(values[q])
                if chi == 0:
                    continue
                y = positions[idx]
                if n == m:
                    shape = 2 * (1 - y / L) * (2 * PI * n * y / L).cos()
                else:
                    shape = (
                        (2 * PI * m * y / L).sin()
                        - (2 * PI * n * y / L).sin()
                    ) / (PI * (n - m))
                wp += weights[idx] * shape * chi
            out[i, j] = out[j, i] = wp
    return out


def tau_from_wp(base: dict, wp: arb_mat) -> arb_mat:
    """Assemble ``tau = W02_zeta - WR_zeta - Wp`` entrywise."""
    dim = base["dim"]
    out = arb_mat(dim, dim)
    for i in range(dim):
        for j in range(i, dim):
            value = base["W02"][i, j] - base["WR"][i, j] - wp[i, j]
            out[i, j] = out[j, i] = value
    return out


def certified_inertia(A: arb_mat, dim: int | None = None):
    """Interval LDL^T inertia, mirroring the external routine.

    Returns ``(n_pos, n_neg, undetermined_pivot, transcript)``.  No heartbeats
    are printed; a false or undetermined pivot is returned, never rounded.
    """
    if dim is None:
        dim = A.nrows()
    if A.nrows() != dim or A.ncols() != dim:
        raise ValueError("matrix dimension does not match dim")
    d = [None] * dim
    Lf = [[arb(0)] * dim for _ in range(dim)]
    n_pos = 0
    n_neg = 0
    transcript: list[str] = []
    for i in range(dim):
        s = A[i, i]
        for k in range(i):
            s = s - Lf[i][k] * Lf[i][k] * d[k]
        d[i] = s
        if s > 0:
            n_pos += 1
            sign = "+"
        elif s < 0:
            n_neg += 1
            sign = "-"
        else:
            return n_pos, n_neg, i, transcript
        transcript.append(
            "%d %s %s %s"
            % (
                i,
                sign,
                s.mid().str(40, radius=False),
                s.rad().str(10, radius=False),
            )
        )
        for j in range(i + 1, dim):
            t = A[j, i]
            for k in range(i):
                t = t - Lf[j][k] * Lf[i][k] * d[k]
            Lf[j][i] = t / d[i]
    return n_pos, n_neg, None, transcript


def matrix_is_finite(matrix: arb_mat) -> bool:
    for i in range(matrix.nrows()):
        for j in range(matrix.ncols()):
            if not matrix[i, j].is_finite():
                return False
    return True


def ball_payload(value: arb, digits: int = 30) -> dict:
    return {
        "mid": value.mid().str(digits, radius=False),
        "rad": value.rad().str(10, radius=True),
    }


def max_abs_difference(left: arb_mat, right: arb_mat) -> arb:
    if left.nrows() != right.nrows() or left.ncols() != right.ncols():
        raise ValueError("matrices must have the same shape")
    result = arb(0)
    for i in range(left.nrows()):
        for j in range(left.ncols()):
            difference = (left[i, j] - right[i, j]).abs_upper()
            if bool(difference > result):
                result = difference
    return result


def character_values(modulus: int, number: int, c: int) -> dict[int, int]:
    chi = dirichlet_char(int(modulus), int(number))
    return {
        power: chars.exact_value(chi, power)
        for power, prime in prime_powers_up_to(c)
    }


def activation_terms(
    modulus: int,
    conductor: int,
    values: dict[int, int],
    lift_values: dict[int, int],
) -> list[dict]:
    terms = []
    for power, prime in prime_powers_up_to(max(values)):
        if math.gcd(power, modulus) > 1 and math.gcd(power, conductor) == 1:
            terms.append(
                {
                    "q_k": power,
                    "prime": prime,
                    "value": values[power],
                    "lift_value": lift_values[power],
                }
            )
    return terms


def _load_external():
    """Load the published external builder if it is available.

    This is a control only.  A missing module is reported as unavailable, not
    as a mathematical failure.
    """
    if str(GW_DIR) not in sys.path:
        sys.path.insert(0, str(GW_DIR))
    try:
        import source_arb_ldlt_certify as external  # type: ignore
    except Exception:  # noqa: BLE001 - optional external control
        return None
    return external


def external_control(base: dict) -> dict:
    """Compare the local zeta matrix with the published external builder."""
    external = _load_external()
    if external is None:
        return {
            "available": False,
            "match": False,
            "status": "TOOL NOT RUN",
            "max_abs_difference": None,
        }
    c = int(base["c"])
    N = int(base["N"])
    prec = int(base["prec"])
    ext_matrix, ext_dim = external.build_arb_tau(c, N, prec)
    if int(ext_dim) != int(base["dim"]):
        return {
            "available": True,
            "match": False,
            "status": "DIMENSION MISMATCH",
            "max_abs_difference": None,
        }
    difference = max_abs_difference(base["tau_zeta"], ext_matrix)
    threshold = arb(2) ** (-(prec - 32))
    match = bool(difference <= threshold)
    return {
        "available": True,
        "match": match,
        "status": "MATCH" if match else "MISMATCH",
        "max_abs_difference": ball_payload(difference),
        "threshold": ball_payload(threshold),
    }


def inertia_record(matrix: arb_mat) -> dict:
    dim = matrix.nrows()
    n_pos, n_neg, undetermined, transcript = certified_inertia(matrix, dim)
    finite = matrix_is_finite(matrix)
    if not finite:
        status = "NON-FINITE"
    elif undetermined is not None:
        status = "INCONCLUSIVE"
    elif n_pos == dim and n_neg == 0:
        status = "POSITIVE DEFINITE"
    else:
        status = "NOT POSITIVE DEFINITE"
    transcript_bytes = "\n".join(transcript).encode("utf-8")
    return {
        "n_pos": n_pos,
        "n_neg": n_neg,
        "undetermined_pivot": undetermined,
        "pivots_recorded": len(transcript),
        "entries_finite": finite,
        "status": status,
        "pivot_transcript_sha256": hashlib.sha256(transcript_bytes).hexdigest(),
    }


def _case_record(base: dict, modulus: int, number: int) -> dict:
    c = int(base["c"])
    q_star, n_star, chi_star = chars.primitive_lift(modulus, number)
    values = character_values(modulus, number, c)
    lift_values = character_values(q_star, n_star, c)
    activation = activation_terms(modulus, q_star, values, lift_values)
    wp_nonprimitive = wp_from_values(base, values)
    wp_primitive = wp_from_values(base, lift_values)
    tau_nonprimitive = tau_from_wp(base, wp_nonprimitive)
    tau_primitive = tau_from_wp(base, wp_primitive)
    inertia_nonprimitive = inertia_record(tau_nonprimitive)
    inertia_primitive = inertia_record(tau_primitive)
    difference = max_abs_difference(wp_nonprimitive, wp_primitive)
    checks = {
        "C3_activation_nonempty": bool(activation),
        "C3_activation_values": all(
            row["value"] == 0 and row["lift_value"] != 0 for row in activation
        ),
        "C3_wp_zero_criterion": all(
            (values[q] == 0) == (math.gcd(q, modulus) > 1)
            for q, _ in base["pdata"]
        ),
        "C3_lift_zero_criterion": all(
            (lift_values[q] == 0) == (math.gcd(q, q_star) > 1)
            for q, _ in base["pdata"]
        ),
        "C3_nonprimitive_finite": matrix_is_finite(tau_nonprimitive),
        "C3_primitive_finite": matrix_is_finite(tau_primitive),
    }
    return {
        "identifier": f"chi_{modulus}_{number}",
        "modulus": modulus,
        "number": number,
        "primitive_lift": {
            "modulus": q_star,
            "number": n_star,
            "identifier": f"chi_{q_star}_{n_star}",
            "primitive": bool(chi_star.is_primitive()),
        },
        "new_primes": list(
            prime
            for prime in chars._prime_divisors(modulus)
            if q_star % prime != 0
        ),
        "activation_count": len(activation),
        "activation_terms": activation,
        "wp_nonprimitive_vs_primitive_max_abs": ball_payload(difference),
        "primitive": inertia_primitive,
        "nonprimitive": inertia_nonprimitive,
        "checks": checks,
        "status": (
            "PASS"
            if all(checks.values())
            and inertia_primitive["status"] != "NON-FINITE"
            and inertia_nonprimitive["status"] != "NON-FINITE"
            else "FAILED"
        ),
    }


def run_config(config: dict) -> dict:
    c = int(config["c"])
    N = int(config["N"])
    prec = int(config["prec"])
    with _precision(prec):
        base = build_base(c, N, prec)
        baseline = inertia_record(base["tau_zeta"])
        control = external_control(base)
        cases = [_case_record(base, modulus, number) for modulus, number in CHARACTERS]
    return {
        "role": config["role"],
        "c": c,
        "N": N,
        "dim": 2 * N + 1,
        "prec": prec,
        "baseline_zeta": baseline,
        "external_control": control,
        "cases": cases,
    }


def _sha256_file_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def build_receipt(prereg_sha256: str | None = None) -> dict:
    """Run the locked campaign and return the deterministic receipt."""
    prereg = prereg_sha256 or _sha256_file_lf(PREREG_PATH)
    configs = [run_config(config) for config in CONFIGS]
    cases = [case for config in configs for case in config["cases"]]
    external_available = all(
        config["external_control"]["available"] for config in configs
    )
    external_match = all(
        config["external_control"]["match"] for config in configs
    )
    baseline_positive = all(
        config["baseline_zeta"]["status"] == "POSITIVE DEFINITE"
        for config in configs
    )
    all_finite = all(
        config["baseline_zeta"]["entries_finite"]
        and all(
            case["primitive"]["entries_finite"]
            and case["nonprimitive"]["entries_finite"]
            for case in config["cases"]
        )
        for config in configs
    )
    all_structure = all(
        case["status"] == "PASS" for case in cases
    )
    any_undetermined = any(
        record["undetermined_pivot"] is not None
        for config in configs
        for case in config["cases"]
        for record in (case["primitive"], case["nonprimitive"])
    ) or any(
        config["baseline_zeta"]["undetermined_pivot"] is not None
        for config in configs
    )

    if not all_finite or not all_structure or not baseline_positive:
        execution_status = "FAILED"
    elif not external_available:
        execution_status = "INCONCLUSIVE"
    elif not external_match:
        execution_status = "FAILED"
    elif any_undetermined:
        execution_status = "INCONCLUSIVE"
    else:
        execution_status = "PASS"

    statuses = [
        record["status"]
        for config in configs
        for case in config["cases"]
        for record in (case["primitive"], case["nonprimitive"])
    ] + [config["baseline_zeta"]["status"] for config in configs]
    if any(status == "INCONCLUSIVE" or status == "NON-FINITE" for status in statuses):
        mathematical_verdict = "INCONCLUSIVE"
    elif all(status == "POSITIVE DEFINITE" for status in statuses):
        mathematical_verdict = "AD HOC POSITIVE"
    else:
        mathematical_verdict = "AD HOC NEGATIVE"

    if execution_status == "PASS":
        verdict = mathematical_verdict
    else:
        verdict = execution_status

    return {
        "schema": SCHEMA,
        "prereg_sha256": prereg,
        "config": {
            "configs": [dict(config) for config in CONFIGS],
            "characters": [
                {"modulus": modulus, "number": number}
                for modulus, number in CHARACTERS
            ],
            "definition": "tau_pert = W02_zeta - WR_zeta - Wp_chi",
            "label": "AD HOC PERTURBATION",
        },
        "external_control": {
            "available": external_available,
            "match": external_match,
            "status": (
                "MATCH"
                if external_available and external_match
                else ("MISMATCH" if external_available else "TOOL NOT RUN")
            ),
        },
        "execution_status": execution_status,
        "mathematical_verdict": mathematical_verdict,
        "verdict": verdict,
        "scope": {
            "ad_hoc_perturbation": True,
            "correct_character_weil_block": False,
            "zeta_pole_block_reused": True,
            "zeta_archimedean_block_reused": True,
            "global_claim_supported": False,
            "standard_l_function_claim": False,
            "dirichlet_series_claim": False,
            "critical_line_claim": False,
            "zero_localization_claim": False,
            "rh_claim": False,
            "factorization_claim": False,
            "sealed_campaigns_rerun": False,
        },
        "configs": configs,
    }


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def receipt_sha256(receipt: dict) -> str:
    return hashlib.sha256(canonical_json(receipt).encode("utf-8")).hexdigest()


def write_receipt(path: Path | str = RECEIPT_PATH) -> str:
    receipt = build_receipt()
    text = json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    target = Path(path)
    target.write_text(text, encoding="utf-8", newline="\n")
    return receipt_sha256(receipt)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="AD HOC zeta-block perturbation with Dirichlet characters"
    )
    parser.add_argument("--out", default=str(RECEIPT_PATH), help="receipt output path")
    args = parser.parse_args(argv)
    digest = write_receipt(args.out)
    receipt = json.loads(Path(args.out).read_text(encoding="utf-8"))
    print(f"wrote {args.out}")
    print(f"execution_status: {receipt['execution_status']}")
    print(f"mathematical_verdict: {receipt['mathematical_verdict']}")
    print(f"verdict: {receipt['verdict']}")
    print(f"receipt sha256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


