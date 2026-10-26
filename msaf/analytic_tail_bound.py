#!/usr/bin/env python3
"""Analytic diagonal tail bound for the c=13 Guinand-Weil ``XC`` term.

The external implementation in ``oracle-toe/GUINAND_WEIL`` defines

    XC(n) = (1/4) Re psi'(1/4 + i*pi*n/L) - L*gX1(n) - gX2(n)

with ``L = log c``, ``w = 2*pi*n/L`` and

    gX1(n) = sum_k exp(-c_k L) c_k / (c_k^2 + w^2)
    gX2(n) = sum_k exp(-c_k L) (c_k^2 - w^2) / (c_k^2 + w^2)^2

for ``c_k = 2k + 1/2``.  This tool records a numerical check of the
pre-registered analytic claim

    |XC(n)| < 1/n^2        (c = 13, n >= 1)

on the finite grid ``n = 1..N_CHECK``.  The analytic proof is in
``reports/ANALYTIC_TAIL_BOUND_2026-10-26.md``: it uses the standard
trigamma integral representation (DLMF 5.15.1), a two-fold integration by
parts, and the geometric majorants Q0, Q1.  This script does **not** prove
the analytic estimate; it verifies the implementation on a grid and checks
the rational constants.

The resulting ``epsilon_XC(N)`` is only the diagonal ``XC`` tail.  It is not
a bound on the full matrix, not a positive-definiteness certificate, and not
a Riemann Hypothesis claim.

Usage:
    python -m msaf.analytic_tail_bound            # rebuild, write JSON
    python -m msaf.analytic_tail_bound --check    # verify existing JSON
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GW_DIR = os.environ.get("GW_DIR", r"C:/Users/usER/oracle-toe/GUINAND_WEIL")
OUT = ROOT / "reports" / "analytic_tail_bound_c13.json"

C = 13
N_CHECK = 4096
PREC_BITS = 512
DIGITS = 80

# Locked by reports/PREREG_ANALYTIC_TAIL_2026-10-26.md before code.
L_UPPER = "2.6"
PI_LOWER = "3"
CPSI_UPPER = "4"
Q0_UPPER = "0.28"
Q1_UPPER = "0.143"
A_UPPER = "0.93036"
RATIO_UPPER = "1"


class TailBoundError(RuntimeError):
    pass


def _canonical_line(n: int, mid: str, rad: str) -> str:
    return f"{n} {mid} {rad}\n"


def _arb_constants() -> dict:
    """Compute the rational-enclosure constants with Arb."""
    if GW_DIR not in sys.path:
        sys.path.insert(0, GW_DIR)
    from flint import arb

    L = arb(C).log()
    r = (-2 * L).exp()
    q0 = (-L / 2).exp() / (1 - r)
    q1 = (-L / 2).exp() * (2 * r / (1 - r) ** 2 + 1 / (2 * (1 - r)))
    pi = arb.pi()

    if not bool(L.upper() < arb(L_UPPER)):
        raise TailBoundError(f"L upper bound is not below {L_UPPER}")
    if not bool(pi.lower() > arb(PI_LOWER)):
        raise TailBoundError(f"pi lower bound is not above {PI_LOWER}")
    if not bool(q0.upper() < arb(Q0_UPPER)):
        raise TailBoundError(f"Q0 upper bound is not below {Q0_UPPER}")
    if not bool(q1.upper() < arb(Q1_UPPER)):
        raise TailBoundError(f"Q1 upper bound is not below {Q1_UPPER}")

    a_upper = (
        Fraction(1, 5)
        * (
            Fraction(4)
            + Fraction(Q0_UPPER)
            + Fraction(L_UPPER) * Fraction(Q1_UPPER)
        )
    )
    if not a_upper < Fraction(RATIO_UPPER):
        raise TailBoundError(f"A upper bound {float(a_upper):.8f} is not below 1")
    if a_upper != Fraction(A_UPPER):
        raise TailBoundError(
            f"A upper bound {a_upper} does not match locked {A_UPPER}"
        )

    return {
        "L_mid": L.mid().str(DIGITS, radius=False),
        "L_upper_arb": L.upper().str(DIGITS, radius=False),
        "pi_lower_arb": pi.lower().str(DIGITS, radius=False),
        "Q0_mid": q0.mid().str(DIGITS, radius=False),
        "Q0_upper_arb": q0.upper().str(DIGITS, radius=False),
        "Q1_mid": q1.mid().str(DIGITS, radius=False),
        "Q1_upper_arb": q1.upper().str(DIGITS, radius=False),
        "A_upper": A_UPPER,
        "A_upper_exact": f"{a_upper.numerator}/{a_upper.denominator}",
    }


def build_record() -> dict:
    """Build the grid record and return the JSON payload."""
    if GW_DIR not in sys.path:
        sys.path.insert(0, GW_DIR)
    from flint import arb, ctx

    import source_arb_ldlt_certify as gw

    saved = ctx.prec
    try:
        ctx.prec = PREC_BITS
        S, CC, XC, L = gw.arb_closed_forms(N_CHECK, C, PREC_BITS)
        if len(XC) != N_CHECK + 1:
            raise TailBoundError(
                f"arb_closed_forms returned {len(XC)} entries, expected {N_CHECK + 1}"
            )

        digest = hashlib.sha256()
        max_ratio = arb(0)
        max_n = 0
        threshold = arb(RATIO_UPPER)

        for n in range(1, N_CHECK + 1):
            ball = XC[n]
            if not ball.is_finite():
                raise TailBoundError(f"non-finite XC at n={n}")
            # n^2 * |XC(n)|: abs() of an arb ball is a ball containing
            # |x| for every x in the input ball, so upper() is rigorous.
            ratio = arb(n * n) * abs(ball)
            if not bool(ratio.upper() < threshold):
                raise TailBoundError(
                    f"n^2|XC(n)| exceeds 1 at n={n}: {ratio.upper().str(30)}"
                )
            if bool(ratio.upper() > max_ratio):
                max_ratio = ratio.upper()
                max_n = n
            digest.update(
                _canonical_line(
                    n,
                    ball.mid().str(DIGITS, radius=False),
                    ball.rad().str(DIGITS, radius=False),
                ).encode("utf-8")
            )

        constants = _arb_constants()
        return {
            "schema": "msaf.analytic_tail_bound.v1",
            "c": C,
            "L": "log(13)",
            "n_check": N_CHECK,
            "prec_bits": PREC_BITS,
            "claim": "|XC(n)| < 1/n^2 for 1 <= n <= n_check; "
            "analytic proof covers all n >= 1",
            "ratio_upper": RATIO_UPPER,
            "max_ratio_upper": max_ratio.str(DIGITS, radius=False),
            "n_at_max_ratio": max_n,
            "L_upper": L_UPPER,
            "pi_lower": PI_LOWER,
            "Cpsi_upper": CPSI_UPPER,
            "Q0_upper": Q0_UPPER,
            "Q1_upper": Q1_UPPER,
            "A_upper_bound": A_UPPER,
            **constants,
            "digest_sha256": digest.hexdigest(),
            "digest_convention": (
                "sha256 of LF-joined 'n mid rad' lines; mid/rad are "
                f"arb.str({DIGITS}, radius=False)"
            ),
            "verdict": "PASS",
            "scope": (
                "diagonal XC tail only; not a proof of matrix positive "
                "definiteness, not a full matrix tail, not zeta spectrum, "
                "not RH"
            ),
        }
    finally:
        ctx.prec = saved


def check_record(path: Path = OUT) -> dict:
    """Verify an existing record without rebuilding the Arb grid."""
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema",
        "c",
        "n_check",
        "prec_bits",
        "ratio_upper",
        "max_ratio_upper",
        "n_at_max_ratio",
        "L_upper",
        "pi_lower",
        "Cpsi_upper",
        "Q0_upper",
        "Q1_upper",
        "A_upper_bound",
        "digest_sha256",
        "verdict",
    }
    missing = required - set(data)
    if missing:
        raise TailBoundError(f"missing fields: {sorted(missing)}")
    if data["schema"] != "msaf.analytic_tail_bound.v1":
        raise TailBoundError("unexpected schema")
    if data["c"] != C or data["n_check"] != N_CHECK or data["prec_bits"] != PREC_BITS:
        raise TailBoundError("parameters do not match preregistration")
    if data["verdict"] != "PASS":
        raise TailBoundError(f"recorded verdict is {data['verdict']!r}")
    if data["L_upper"] != L_UPPER or data["pi_lower"] != PI_LOWER:
        raise TailBoundError("L/pi bounds drifted from preregistration")
    if data["Cpsi_upper"] != CPSI_UPPER:
        raise TailBoundError("Cpsi bound drifted from preregistration")
    if data["Q0_upper"] != Q0_UPPER or data["Q1_upper"] != Q1_UPPER:
        raise TailBoundError("Q0/Q1 bounds drifted from preregistration")
    if data["A_upper_bound"] != A_UPPER:
        raise TailBoundError("A_upper drifted from preregistration")
    if Fraction(data["max_ratio_upper"]) >= Fraction(data["ratio_upper"]):
        raise TailBoundError("recorded max ratio is not below 1")
    if not Fraction(data["A_upper_bound"]) < 1:
        raise TailBoundError("recorded A_upper is not below 1")

    a_upper = (
        Fraction(1, 5)
        * (
            Fraction(4)
            + Fraction(Q0_UPPER)
            + Fraction(L_UPPER) * Fraction(Q1_UPPER)
        )
    )
    if not a_upper < 1:
        raise TailBoundError("recomputed A_upper is not below 1")

    digest = data["digest_sha256"]
    if len(digest) != 64:
        raise TailBoundError("malformed digest")
    try:
        int(digest, 16)
    except ValueError as exc:
        raise TailBoundError("digest is not hexadecimal") from exc

    return data


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--check",
        action="store_true",
        help="verify the existing JSON instead of rebuilding the grid",
    )
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args(argv)

    try:
        if args.check:
            data = check_record(Path(args.out))
            print(
                "PASS analytic XC tail: "
                f"max n^2|XC(n)|={data['max_ratio_upper']} "
                f"(n={data['n_at_max_ratio']}) < {data['ratio_upper']}; "
                f"A_upper={data['A_upper_bound']} < 1"
            )
            return 0

        data = build_record()
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(
            "wrote %s; max_ratio=%s n=%s verdict=%s"
            % (
                out,
                data["max_ratio_upper"],
                data["n_at_max_ratio"],
                data["verdict"],
            )
        )
        return 0
    except TailBoundError as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
