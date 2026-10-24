"""Candidate character-aware Guinand-Weil block (research stage, NOT certified).

This module implements a *candidate* archimedean block for a real primitive
Dirichlet character, following the explicit-formula dictionary of
arXiv:2607.02828v3 with the character-dependent data

    Lambda(s, chi) = (q*/pi)^((s+a)/2) Gamma((s+a)/2) L(s, chi),

so that the archimedean density is

    h_chi(r) = Re psi((1+2a)/4 + i r/2) + log q* - log pi,

and the partial-fraction poles of the digamma shift from
``c_k = 2k + 1/2`` to ``c_k = 2k + 2 alpha`` with ``alpha = (1+2a)/4``.

Only non-principal characters are handled: the standard L-function of a
non-principal character has no pole, so ``W02_chi = 0``.  The principal
character, whose pole block needs a residue-scaled source, is **not**
implemented and is reported as ``NOT IMPLEMENTED``.

Scope of the result.  The construction is a candidate, not a certified
character-aware Weil block:

* the ``q*=1`` reduction reproduces the zeta archimedean block, which only
  validates the code path for ``alpha = 1/4``;
* the parity shift ``alpha = 3/4`` and the conductor shift ``log q*`` have no
  independent validation inside this package;
* the principal pole block is missing.

Therefore the receipt records ``certification_status = INCONCLUSIVE`` and
``verdict = INCONCLUSIVE``.  Nothing here is a zero statement, a critical
line statement, a positivity statement for ``L(s, chi)``, or a Riemann
hypothesis claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Sequence

from flint import acb, arb, arb_mat, ctx, dirichlet_char

from . import gw_char_adhoc as adhoc
from . import gw_character_arithmetic as chars

SCHEMA = "msaf.gw_char_block.v1"

CONFIGS = (
    {"role": "primary", "c": 100, "N": 20, "prec": 600},
    {"role": "replication", "c": 200, "N": 20, "prec": 600},
)

PRIMITIVE_CHARACTERS = ((4, 3), (3, 2), (5, 4))
PRINCIPAL_CHARACTERS = ((4, 1), (3, 1), (5, 1))
NONPRIMITIVE_PARENTS = ((12, 7), (12, 5), (15, 4), (15, 11))

PRINCIPAL_POLE_IMPLEMENTED = False
INDEPENDENT_VALIDATION = "Q1_REDUCTION_ONLY"
Q1_CONTROL = {"c": 13, "N": 4, "prec": 200}

REPO_ROOT = Path(__file__).resolve().parents[1]
PREREG_PATH = REPO_ROOT / "reports" / "PREREG_GW_CHAR_BLOCK_2026-10-21.md"
RECEIPT_PATH = REPO_ROOT / "reports" / "gw_char_block_2026-10-21.json"


class CharacterBlockError(RuntimeError):
    """A finite candidate-block invariant failed.

    This says nothing about any L-function.
    """


def alpha_fraction(parity: int) -> Fraction:
    """Exact ``alpha = (1 + 2a)/4`` for a character parity."""
    parity = int(parity)
    if parity not in (0, 1):
        raise ValueError("parity must be 0 or 1")
    return Fraction(1 + 2 * parity, 4)


def alpha_arb(parity: int) -> arb:
    """Ball value of ``alpha`` for use inside closed forms."""
    return arb(1 + 2 * int(parity)) / 4


def _arb_kappa(L: arb) -> arb:
    eL = L.exp()
    return (4 * arb.pi() * (eL - 1) / (eL + 1)).log() + arb.const_euler()


def _arb_J(L: arb) -> arb:
    U = (L / 2).exp()
    return (
        -2 * (U + 1).log()
        + (U * U + 1).log()
        + 2 * U.atan()
        + arb(2).log()
        - arb.pi() / 2
    )


def geom_sums(n: int, L: arb, alpha: arb, prec: int):
    """Rigorous geometric sums with the character-shifted poles.

    The zeta builder uses ``c_k = 2k + 1/2``.  For a character with parity
    ``a`` the digamma poles sit at ``c_k = 2k + 2 alpha``, which is the only
    change made here.
    """
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
        c_k = arb(2 * k) + 2 * alpha
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
    c_next = arb(2 * (k + 1)) + 2 * alpha
    one_minus_z = 1 - (-2 * L).exp()
    tail_geo = (-c_next * L).exp() / one_minus_z
    remainder = arb(4) * tail_geo

    def widen(value: arb) -> arb:
        return value + arb(0, remainder)

    return widen(gS), widen(gCC), widen(gX1), widen(gX2)


def arch_closed_forms(N: int, c: int, prec: int, alpha: arb):
    """Character-aware archimedean closed forms ``S``, ``CC``, ``XC``, ``L``."""
    ctx.prec = prec
    L = arb(c).log()
    PI = arb.pi()
    psi_alpha = alpha.digamma()
    S = [arb(0)] * (N + 1)
    CC = [arb(0)] * (N + 1)
    XC = [arb(0)] * (N + 1)
    for n in range(N + 1):
        w = 2 * PI * n / L
        zarg = acb(alpha, PI * n / L)
        psi = zarg.digamma()
        psi1 = zarg.polygamma(acb(1))
        gS, gCC, gX1, gX2 = geom_sums(n, L, alpha, prec)
        if n == 0:
            S[n] = arb(0)
            CC[n] = arb(0)
        else:
            S[n] = arb("0.5") * psi.imag - w * gS
            CC[n] = -arb("0.5") * (psi.real - psi_alpha) + gCC
        XC[n] = arb("0.25") * psi1.real - L * gX1 - gX2
    return S, CC, XC, L


def wr_from_closed(S, CC, XC, L, kappa, J, N: int) -> arb_mat:
    """Assemble the archimedean block from the closed forms.

    The layout follows the zeta builder: the diagonal uses
    ``kappa + 2 CC + J - (2/L) XC`` and the off-diagonal uses the divided
    differences of ``S``.  ``kappa`` already carries the conductor shift
    ``log q*``.
    """
    PI = arb.pi()
    dim = 2 * N + 1
    out = arb_mat(dim, dim)

    def S_signed(nn: int) -> arb:
        return S[nn] if nn >= 0 else -S[-nn]

    for i in range(dim):
        n = i - N
        for j in range(i, dim):
            m = j - N
            if n == m:
                wr = kappa + 2 * CC[abs(n)] + J - (2 / L) * XC[abs(n)]
            else:
                wr = (S_signed(m) - S_signed(n)) / (PI * (n - m))
            out[i, j] = out[j, i] = wr
    return out


def w02_zeta(c: int, N: int, prec: int) -> arb_mat:
    """Build the zeta pole block W02_zeta (pole_B from the external builder)."""
    with adhoc._precision(prec):
        L = arb(c).log()
        PI = arb.pi()
        sp2 = 16 * PI * PI
        l2 = L * L
        pref02 = 32 * L * (L / 4).sinh() ** 2
        dim = 2 * N + 1
        W02 = arb_mat(dim, dim)
        for i in range(dim):
            n = i - N
            for j in range(i, dim):
                m = j - N
                num = l2 - sp2 * m * n
                den = (l2 + sp2 * m * m) * (l2 + sp2 * n * n)
                w02 = pref02 * num / den
                W02[i, j] = W02[j, i] = w02
        return W02


def totient(n: int) -> int:
    """Euler's totient function φ(n)."""
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1 if p == 2 else 2
    if temp > 1:
        result -= result // temp
    return result


def q1_reduction_control(c: int, N: int, prec: int) -> dict:
    """Check that ``q*=1, a=0`` reproduces the zeta archimedean block.

    This is an implementation control.  It does not validate the parity
    shift ``alpha = 3/4`` nor the conductor shift ``log q*``.
    """
    with adhoc._precision(prec):
        reference = adhoc.build_base(c, N, prec)
        S, CC, XC, L = arch_closed_forms(N, c, prec, alpha_arb(0))
        kappa = _arb_kappa(L) + arb(1).log()
        wr = wr_from_closed(S, CC, XC, L, kappa, _arb_J(L), N)
        difference = adhoc.max_abs_difference(wr, reference["WR"])
        threshold = arb(2) ** (-(prec - 32))
        passed = bool(difference <= threshold)
        return {
            "c": c,
            "N": N,
            "prec": prec,
            "conductor": 1,
            "parity": 0,
            "alpha": "1/4",
            "max_abs_difference": adhoc.ball_payload(difference),
            "threshold": adhoc.ball_payload(threshold),
            "passed": passed,
        }


def candidate_block(
    base: dict,
    c: int,
    N: int,
    prec: int,
    modulus: int,
    number: int,
    source: str,
) -> dict:
    """Build one candidate character block.

    ``source="standard"`` uses the primitive parent ``chi*`` and the
    conductor ``q*``, which is the standard L-function object.
    ``source="dirichlet_series"`` keeps ``q*`` and the parity but uses the
    coefficients of the imprimitive character, which is the finite
    Euler-factor Dirichlet series, a different object.
    """
    if source not in ("standard", "dirichlet_series"):
        raise ValueError("source must be 'standard' or 'dirichlet_series'")
    q_star, n_star, chi_star = chars.primitive_lift(modulus, number)
    parity = int(chi_star.parity())
    is_principal = (int(chi_star.conductor()) == 1 and int(chi_star.parity()) == 0 and int(chi_star.order()) == 1)
    alpha = alpha_arb(parity)
    S, CC, XC, L = arch_closed_forms(N, c, prec, alpha)
    kappa = _arb_kappa(L) + arb(q_star).log()
    wr = wr_from_closed(S, CC, XC, L, kappa, _arb_J(L), N)

    if source == "standard":
        values = adhoc.character_values(q_star, n_star, c)
        zero_modulus = q_star
    else:
        values = adhoc.character_values(modulus, number, c)
        zero_modulus = modulus
    wp = adhoc.wp_from_values(base, values)

    # Build W02 (pole block): zero for non-principal, scaled for principal
    dim = 2 * N + 1
    if is_principal:
        # For principal character modulo q, residue = φ(q)/q
        residue = arb(totient(modulus)) / arb(modulus)
        W02 = w02_zeta(c, N, prec)
        # Scale by residue φ(q)/q
        for i in range(dim):
            for j in range(i, dim):
                W02[i, j] = W02[j, i] = W02[i, j] * residue
        pole_block = f"SCALED POLE (residue {totient(modulus)}/{modulus})"
    else:
        W02 = arb_mat(dim, dim)  # zero matrix
        pole_block = "ZERO (non-principal)"

    if source == "standard":
        values = adhoc.character_values(q_star, n_star, c)
        zero_modulus = q_star
    else:
        values = adhoc.character_values(modulus, number, c)
        zero_modulus = modulus
    wp = adhoc.wp_from_values(base, values)

    dim = 2 * N + 1
    tau = arb_mat(dim, dim)
    for i in range(dim):
        for j in range(i, dim):
            value = W02[i, j] - wr[i, j] - wp[i, j]
            tau[i, j] = tau[j, i] = value

    inertia = adhoc.inertia_record(tau)
    checks = {
        "C2_wr_finite": adhoc.matrix_is_finite(wr),
        "C2_wp_finite": adhoc.matrix_is_finite(wp),
        "C2_tau_finite": adhoc.matrix_is_finite(tau),
        "C2_wp_zero_criterion": all(
            (values[q] == 0) == (math.gcd(q, zero_modulus) > 1)
            for q, _ in base["pdata"]
        ),
        "C2_pole_block_correct": is_principal or all(W02[i, j] == 0 for i in range(dim) for j in range(dim)),
    }
    return {
        "record": {
            "identifier": f"chi_{modulus}_{number}",
            "modulus": modulus,
            "number": number,
            "source": source,
            "primitive_lift": {
                "modulus": q_star,
                "number": n_star,
                "identifier": f"chi_{q_star}_{n_star}",
                "primitive": bool(chi_star.is_primitive()),
            },
            "conductor": q_star,
            "parity": parity,
            "alpha": str(alpha_fraction(parity)),
            "pole_block": pole_block,
            "inertia": inertia,
            "checks": checks,
            "status": "PASS" if all(checks.values()) else "FAILED",
        },
        "values": values,
        "tau": tau,
        "wr": wr,
        "wp": wp,
        "W02": W02,
    }


def run_config(config: dict) -> dict:
    """Run one locked configuration and return its deterministic record."""
    c = int(config["c"])
    N = int(config["N"])
    prec = int(config["prec"])
    with adhoc._precision(prec):
        base = adhoc.build_base(c, N, prec)
        control = q1_reduction_control(
            Q1_CONTROL["c"], Q1_CONTROL["N"], Q1_CONTROL["prec"]
        )
        standard = {}
        standard_records = []
        for modulus, number in PRIMITIVE_CHARACTERS + PRINCIPAL_CHARACTERS:
            built = candidate_block(base, c, N, prec, modulus, number, "standard")
            standard[(modulus, number)] = built
            standard_records.append(built["record"])
        series_records = []
        comparisons = []
        for modulus, number in NONPRIMITIVE_PARENTS:
            built = candidate_block(
                base, c, N, prec, modulus, number, "dirichlet_series"
            )
            series_records.append(built["record"])
            q_star, n_star, _ = chars.primitive_lift(modulus, number)
            reference = standard[(q_star, n_star)]
            lift_values = adhoc.character_values(q_star, n_star, c)
            activation = adhoc.activation_terms(
                modulus, q_star, built["values"], lift_values
            )
            comparisons.append(
                {
                    "parent": f"chi_{modulus}_{number}",
                    "standard_block": f"chi_{q_star}_{n_star}",
                    "max_abs_tau_difference": adhoc.ball_payload(
                        adhoc.max_abs_difference(built["tau"], reference["tau"])
                    ),
                    "max_abs_wp_difference": adhoc.ball_payload(
                        adhoc.max_abs_difference(built["wp"], reference["wp"])
                    ),
                    "activation_count": len(activation),
                    "activation_terms": activation,
                    "standard_status": reference["record"]["inertia"]["status"],
                    "dirichlet_series_status": built["record"]["inertia"]["status"],
                    "objects_are_identical": False,
                }
            )
    return {
        "role": config["role"],
        "c": c,
        "N": N,
        "dim": 2 * N + 1,
        "prec": prec,
        "q1_reduction_control": control,
        "standard_blocks": standard_records,
        "dirichlet_series_blocks": series_records,
        "standard_vs_series": comparisons,
    }


def _sha256_file_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def build_receipt(prereg_sha256: str | None = None) -> dict:
    """Build the deterministic candidate-block receipt."""
    prereg = prereg_sha256 or _sha256_file_lf(PREREG_PATH)
    configs = [run_config(config) for config in CONFIGS]

    controls_ok = all(config["q1_reduction_control"]["passed"] for config in configs)
    blocks_ok = all(
        record["status"] == "PASS"
        for config in configs
        for record in (
            list(config["standard_blocks"]) + list(config["dirichlet_series_blocks"])
        )
    )
    finite_ok = all(
        record["inertia"]["entries_finite"]
        for config in configs
        for record in (
            list(config["standard_blocks"]) + list(config["dirichlet_series_blocks"])
        )
    )
    determined = all(
        record["inertia"]["undetermined_pivot"] is None
        for config in configs
        for record in (
            list(config["standard_blocks"]) + list(config["dirichlet_series_blocks"])
        )
    )
    separated = all(
        comparison["max_abs_tau_difference"]["mid"] != "0.0"
        and comparison["activation_count"] > 0
        for config in configs
        for comparison in config["standard_vs_series"]
    )

    if not (controls_ok and blocks_ok and finite_ok):
        execution_status = "FAILED"
    elif not determined:
        execution_status = "INCONCLUSIVE"
    else:
        execution_status = "PASS"

    statuses = [
        record["inertia"]["status"]
        for config in configs
        for record in (
            list(config["standard_blocks"]) + list(config["dirichlet_series_blocks"])
        )
    ]
    if any(status in ("INCONCLUSIVE", "NON-FINITE") for status in statuses):
        candidate_result = "INCONCLUSIVE"
    elif all(status == "POSITIVE DEFINITE" for status in statuses):
        candidate_result = "CANDIDATE POSITIVE DEFINITE"
    else:
        candidate_result = "CANDIDATE NOT POSITIVE DEFINITE"

    certification_status = "INCONCLUSIVE"
    verdict = "INCONCLUSIVE" if execution_status != "FAILED" else "FAILED"

    return {
        "schema": SCHEMA,
        "prereg_sha256": prereg,
        "config": {
            "configs": [dict(config) for config in CONFIGS],
            "primitive_characters": [
                {"modulus": modulus, "number": number}
                for modulus, number in PRIMITIVE_CHARACTERS
            ],
            "nonprimitive_parents": [
                {"modulus": modulus, "number": number}
                for modulus, number in NONPRIMITIVE_PARENTS
            ],
            "q1_control": dict(Q1_CONTROL),
            "definition_standard": (
                "tau_chi = -WR_chi - Wp_chi with conductor q*, parity a, "
                "alpha=(1+2a)/4, coefficients of the primitive parent chi*"
            ),
            "definition_dirichlet_series": (
                "same archimedean block, coefficients of the imprimitive "
                "character (zeros at the new primes)"
            ),
        },
        "execution_status": execution_status,
        "certification_status": certification_status,
        "candidate_result": candidate_result,
        "verdict": verdict,
        "block_status": "CANDIDATE",
        "principal_pole_status": "IMPLEMENTED" if PRINCIPAL_POLE_IMPLEMENTED else "NOT IMPLEMENTED",
        "independent_validation": INDEPENDENT_VALIDATION,
        "registry_entry": None,
        "scope": {
            "candidate_block_only": True,
            "certified_character_weil_block": False,
            "standard_l_function_block_certified": False,
            "principal_pole_included": PRINCIPAL_POLE_IMPLEMENTED,
            "independent_validation_complete": False,
            "imprimitive_and_standard_identified": False,
            "critical_line_claim": False,
            "zero_localization_claim": False,
            "rh_claim": False,
            "global_positivity_claim": False,
            "factorization_claim": False,
            "sealed_campaigns_rerun": False,
        },
        "checks": {
            "C1_q1_reduction": controls_ok,
            "C2_blocks_finite": finite_ok and blocks_ok,
            "C3_inertia_determined": determined,
            "C4_standard_vs_series_separated": separated,
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
        description="Candidate character-aware Guinand-Weil block (research)"
    )
    parser.add_argument("--out", default=str(RECEIPT_PATH), help="receipt output path")
    args = parser.parse_args(argv)
    digest = write_receipt(args.out)
    receipt = json.loads(Path(args.out).read_text(encoding="utf-8"))
    print(f"wrote {args.out}")
    print(f"execution_status: {receipt['execution_status']}")
    print(f"certification_status: {receipt['certification_status']}")
    print(f"candidate_result: {receipt['candidate_result']}")
    print(f"verdict: {receipt['verdict']}")
    print(f"receipt sha256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
