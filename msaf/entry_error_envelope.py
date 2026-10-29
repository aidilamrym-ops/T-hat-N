#!/usr/bin/env python3
"""Entry-error envelope for the c=13, N=160 Guinand-Weil block.

The matrix is built by `build_arb_tau` from the external
`oracle-toe/GUINAND_WEIL` checkout.  Every entry is an Arb ball.  This tool
records an upper bound for the radius of every entry, serialises the radii as
decimal strings (never through float64), and checks the pre-registered
envelope

    epsilon = 10^-100
    delta   = 321 * epsilon = 3.21 * 10^-98
    delta   < lambda_min = 3.123458832662237e-59

The output is a provenance record, not a proof that the matrix is positive
definite.  The eigenvalue certificate remains the external `arb_mat.eig` run;
the Lean theorem in `lean/Stage_5_EntryError_Perturbation.lean` is conditional
on the matrix satisfying the quadratic lower bound.

Usage:
    python -m msaf.entry_error_envelope            # rebuild, write JSON
    python -m msaf.entry_error_envelope --check    # verify existing JSON
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
OUT = ROOT / "reports" / "entry_error_envelope_c13_n160.json"

C = 13
N = 160
PREC_BITS = 6000
DIM = 2 * N + 1

# Locked by reports/PREREG_ENTRY_ERROR_ENVELOPE_2026-10-26.md before code.
EPSILON = "1e-100"
DELTA = "3.21e-98"
LAMBDA_MIN = "3.123458832662237e-59"
SERIALIZATION_SLACK = "1e-120"
DIGITS = 140


class EnvelopeError(RuntimeError):
    pass


def _canonical_line(i: int, j: int, mid: str, rad: str) -> str:
    return f"{i} {j} {mid} {rad}\n"


def build_envelope() -> dict:
    """Build the Arb matrix and return the envelope record."""
    if GW_DIR not in sys.path:
        sys.path.insert(0, GW_DIR)
    from flint import arb, ctx

    import source_arb_ldlt_certify as gw

    saved = ctx.prec
    try:
        ctx.prec = PREC_BITS
        A, dim = gw.build_arb_tau(C, N, PREC_BITS)
        if dim != DIM:
            raise EnvelopeError(f"builder returned dim {dim}, expected {DIM}")

        epsilon = arb(EPSILON)
        slack = arb(SERIALIZATION_SLACK)
        max_rad = arb(0)
        max_plus = arb(0)
        digest = hashlib.sha256()
        n_entries = 0

        for i in range(dim):
            for j in range(dim):
                ball = A[i, j]
                if not ball.is_finite():
                    raise EnvelopeError(f"non-finite entry at ({i},{j})")
                rad = ball.rad()
                rad_str = rad.str(DIGITS, radius=False)
                mid_str = ball.mid().str(DIGITS, radius=False)
                # The printed decimal must not understate the true radius.
                reparsed = arb(rad_str)
                upper = reparsed + slack
                if not bool(upper >= rad):
                    raise EnvelopeError(
                        f"decimal radius understates entry ({i},{j}): "
                        f"{rad_str}"
                    )
                if bool(upper > max_plus):
                    max_plus = upper
                if bool(rad > max_rad):
                    max_rad = rad
                digest.update(
                    _canonical_line(i, j, mid_str, rad_str).encode("utf-8")
                )
                n_entries += 1

        expected_entries = DIM * DIM
        if n_entries != expected_entries:
            raise EnvelopeError(
                f"scanned {n_entries} entries, expected {expected_entries}"
            )
        if not bool(max_plus <= epsilon):
            raise EnvelopeError(
                "entry radius exceeds preregistered epsilon: "
                f"{max_plus.str(30)} > {EPSILON}"
            )

        delta = Fraction(DIM) * Fraction(EPSILON)
        lam = Fraction(LAMBDA_MIN)
        if not delta < lam:
            raise EnvelopeError(
                f"delta {float(delta):.6e} is not below lambda {LAMBDA_MIN}"
            )

        return {
            "schema": "msaf.entry_error_envelope.v1",
            "c": C,
            "N": N,
            "dim": DIM,
            "prec_bits": PREC_BITS,
            "epsilon": EPSILON,
            "delta": DELTA,
            "lambda_min": LAMBDA_MIN,
            "max_entry_radius_upper": max_rad.upper().str(
                DIGITS, radius=False
            ),
            "max_entry_radius_plus_slack": max_plus.upper().str(
                DIGITS, radius=False
            ),
            "serialization_slack": SERIALIZATION_SLACK,
            "n_entries": n_entries,
            "digest_sha256": digest.hexdigest(),
            "digest_convention": (
                "sha256 of LF-joined 'i j mid rad' lines; mid/rad are "
                f"arb.str({DIGITS}, radius=False)"
            ),
            "verdict": "PASS",
            "scope": (
                "entry-radius envelope only; not a proof of matrix positive "
                "definiteness, not a zeta-spectrum or RH claim"
            ),
        }
    finally:
        ctx.prec = saved


def check_envelope(path: Path = OUT) -> dict:
    """Verify an existing envelope record without rebuilding the matrix."""
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema",
        "c",
        "N",
        "dim",
        "prec_bits",
        "epsilon",
        "delta",
        "lambda_min",
        "max_entry_radius_upper",
        "max_entry_radius_plus_slack",
        "n_entries",
        "digest_sha256",
        "verdict",
    }
    missing = required - set(data)
    if missing:
        raise EnvelopeError(f"missing fields: {sorted(missing)}")
    if data["schema"] != "msaf.entry_error_envelope.v1":
        raise EnvelopeError("unexpected schema")
    if (data["c"], data["N"], data["dim"], data["prec_bits"]) != (
        C,
        N,
        DIM,
        PREC_BITS,
    ):
        raise EnvelopeError("matrix parameters do not match preregistration")
    if data["verdict"] != "PASS":
        raise EnvelopeError(f"recorded verdict is {data['verdict']!r}")
    if data["n_entries"] != DIM * DIM:
        raise EnvelopeError("entry count mismatch")
    if len(data["digest_sha256"]) != 64:
        raise EnvelopeError("malformed digest")
    try:
        int(data["digest_sha256"], 16)
    except ValueError as exc:
        raise EnvelopeError("digest is not hexadecimal") from exc

    epsilon = Fraction(data["epsilon"])
    delta = Fraction(data["delta"])
    lam = Fraction(data["lambda_min"])
    upper = Fraction(data["max_entry_radius_plus_slack"])
    if not upper <= epsilon:
        raise EnvelopeError(
            f"recorded radius {data['max_entry_radius_plus_slack']} > epsilon"
        )
    if not delta < lam:
        raise EnvelopeError("recorded delta is not below lambda")
    if delta != DIM * epsilon:
        raise EnvelopeError("recorded delta != dim * epsilon")
    return data


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--check",
        action="store_true",
        help="verify the existing JSON instead of rebuilding the matrix",
    )
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args(argv)

    try:
        if args.check:
            data = check_envelope(Path(args.out))
            print(
                "PASS entry-error envelope: "
                f"max_plus={data['max_entry_radius_plus_slack']} "
                f"<= epsilon={data['epsilon']}; "
                f"delta={data['delta']} < lambda={data['lambda_min']}"
            )
            return 0

        data = build_envelope()
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(
            "wrote %s; max_plus=%s verdict=%s"
            % (out, data["max_entry_radius_plus_slack"], data["verdict"])
        )
        return 0
    except EnvelopeError as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())


