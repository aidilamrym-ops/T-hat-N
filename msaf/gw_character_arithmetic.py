"""Exact Dirichlet-character arithmetic and structural-zero certificate.

This module is the finite arithmetic prerequisite for the non-primitive
Guinand-Weil scope audit.  It works only with integer character values and
integer coprimality.  It does not build a Guinand-Weil matrix, does not
evaluate an L-function, and makes no statement about zeros, the critical
line, or the Riemann hypothesis.

For a character ``chi`` modulo ``q`` the structural-zero statement is

    chi(n) = 0  iff  gcd(n, q) > 1.

That statement concerns the Dirichlet coefficients.  In particular, if
``chi`` is non-primitive with primitive parent ``chi*`` modulo ``q*``, a new
prime ``p | q`` with ``p`` not dividing ``q*`` gives ``chi(p) = 0`` while
``chi*(p) != 0``.  This is an arithmetic fact about the coefficients, not a
zero of the standard L-function ``L(s, chi) = L(s, chi*)`` and not a zero of
the finite-Euler-factor Dirichlet series either.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable, Sequence

from flint import arb, dirichlet_char

SCHEMA = "msaf.gw_character_arithmetic.v1"
CUTOFF = 200

INSTANCES = (
    {
        "role": "primary",
        "modulus": 12,
        "number": 7,
        "expected_conductor": 4,
        "expected_primitive": False,
        "expected_parity": 1,
        "expected_order": 2,
        "expected_lift": (4, 3),
        "expected_new_primes": (3,),
    },
    {
        "role": "primary",
        "modulus": 12,
        "number": 5,
        "expected_conductor": 3,
        "expected_primitive": False,
        "expected_parity": 1,
        "expected_order": 2,
        "expected_lift": (3, 2),
        "expected_new_primes": (2,),
    },
    {
        "role": "primary",
        "modulus": 15,
        "number": 4,
        "expected_conductor": 5,
        "expected_primitive": False,
        "expected_parity": 0,
        "expected_order": 2,
        "expected_lift": (5, 4),
        "expected_new_primes": (3,),
    },
    {
        "role": "primary",
        "modulus": 15,
        "number": 11,
        "expected_conductor": 3,
        "expected_primitive": False,
        "expected_parity": 1,
        "expected_order": 2,
        "expected_lift": (3, 2),
        "expected_new_primes": (5,),
    },
    {
        "role": "control",
        "modulus": 12,
        "number": 1,
        "expected_conductor": 1,
        "expected_primitive": False,
        "expected_parity": 0,
        "expected_order": 1,
        "expected_lift": (1, 1),
        "expected_new_primes": (2, 3),
    },
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PREREG_PATH = REPO_ROOT / "reports" / "PREREG_GW_CHARACTER_ARITHMETIC_2026-10-21.md"
RECEIPT_PATH = REPO_ROOT / "reports" / "gw_character_arithmetic_2026-10-21.json"


class CharacterArithmeticError(RuntimeError):
    """An exact character-table invariant failed.

    This is a fail-closed error for a finite arithmetic certificate.  It is
    not evidence about any analytic object.
    """


def _coprime(a: int, b: int) -> bool:
    """Exact coprimality test with Python integers."""
    return math.gcd(int(a), int(b)) == 1


def candidate_numbers(modulus: int) -> list[int]:
    """Valid character numbers modulo ``modulus``.

    For modulus 1 the trivial character uses number 1.  For every modulus
    greater than 1, valid numbers are the units in ``1..modulus-1``.
    """
    modulus = int(modulus)
    if modulus < 1:
        raise ValueError("modulus must be positive")
    if modulus == 1:
        return [1]
    return [number for number in range(1, modulus) if _coprime(number, modulus)]


def exact_value(chi, n: int) -> int:
    """Evaluate a real character at an integer as exactly -1, 0, or +1.

    FLINT evaluates Dirichlet characters in Acb arithmetic.  For a real
    character the result is exact, but this function still checks exactness
    and rejects any non-real or non-integral enclosure rather than reading a
    midpoint.
    """
    value = chi(int(n))
    if not value.imag.is_zero() or not value.real.is_exact():
        raise CharacterArithmeticError(
            f"character value at {n} is not an exact real integer"
        )
    real = value.real
    for candidate in (1, -1, 0):
        if real == arb(candidate):
            return candidate
    raise CharacterArithmeticError(
        f"character value at {n} is exact but not -1, 0, or +1"
    )


def _metadata(chi) -> dict:
    return {
        "conductor": int(chi.conductor()),
        "primitive": bool(chi.is_primitive()),
        "parity": int(chi.parity()),
        "order": int(chi.order()),
    }


def _matches_real(candidate, target: dict[int, int]) -> bool:
    """Return whether a candidate matches a real table on every unit.

    A complex candidate is not an error in the lift search: it simply is not
    the real primitive parent.  Non-real values are treated as a mismatch,
    while a malformed real value still raises through ``exact_value``.
    """
    for unit, value in target.items():
        try:
            candidate_value = exact_value(candidate, unit)
        except CharacterArithmeticError:
            return False
        if candidate_value != value:
            return False
    return True


def _divisors(n: int) -> list[int]:
    """Positive divisors of ``n`` in increasing order."""
    small: list[int] = []
    large: list[int] = []
    root = math.isqrt(int(n))
    for divisor in range(1, root + 1):
        if n % divisor == 0:
            small.append(divisor)
            if divisor * divisor != n:
                large.append(n // divisor)
    return small + list(reversed(large))


def _prime_divisors(n: int) -> tuple[int, ...]:
    """Distinct prime divisors of ``n``."""
    n = int(n)
    if n < 2:
        return ()
    primes: list[int] = []
    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            primes.append(divisor)
            while n % divisor == 0:
                n //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if n > 1:
        primes.append(n)
    return tuple(primes)


def _prime_powers(cutoff: int) -> list[tuple[int, int, int]]:
    """Prime powers ``(q_k, p, exponent)`` up to ``cutoff``, sorted by q_k."""
    if cutoff < 2:
        return []
    sieve = bytearray(b"\x01") * (cutoff + 1)
    sieve[0:2] = b"\x00\x00"
    for value in range(2, math.isqrt(cutoff) + 1):
        if sieve[value]:
            sieve[value * value : cutoff + 1 : value] = b"\x00" * (
                ((cutoff - value * value) // value) + 1
            )
    rows: list[tuple[int, int, int]] = []
    for prime in range(2, cutoff + 1):
        if not sieve[prime]:
            continue
        power = prime
        exponent = 1
        while power <= cutoff:
            rows.append((power, prime, exponent))
            if power > cutoff // prime:
                break
            power *= prime
            exponent += 1
    rows.sort()
    return rows


def primitive_lift(modulus: int, number: int):
    """Return ``(q_star, n_star, chi_star)`` for the primitive parent.

    The search is exact: candidates modulo the FLINT-reported conductor are
    compared with the original character on every unit modulo ``modulus``.
    Exactly one candidate must match.  The returned candidate is checked for
    primitivity and conductor agreement by the caller.
    """
    chi = dirichlet_char(int(modulus), int(number))
    q_star = int(chi.conductor())
    target = {
        unit: exact_value(chi, unit) for unit in candidate_numbers(int(modulus))
    }
    matches = []
    for candidate_number in candidate_numbers(q_star):
        candidate = dirichlet_char(q_star, candidate_number)
        if _matches_real(candidate, target):
            matches.append((candidate_number, candidate))
    if len(matches) != 1:
        raise CharacterArithmeticError(
            f"expected one primitive lift for chi_{modulus}_{number} modulo "
            f"{q_star}, found {len(matches)}"
        )
    candidate_number, candidate = matches[0]
    return q_star, candidate_number, candidate


def _smaller_matching_modulus(
    modulus: int, target: dict[int, int], conductor: int
) -> dict | None:
    """Find a character modulo a proper divisor that matches on all units.

    A match would contradict the claimed conductor.  Only divisors of the
    modulus can be conductors of a character modulo that modulus.
    """
    for divisor in _divisors(int(modulus)):
        if divisor >= conductor:
            continue
        for candidate_number in candidate_numbers(divisor):
            candidate = dirichlet_char(divisor, candidate_number)
            if _matches_real(candidate, target):
                return {
                    "modulus": divisor,
                    "number": candidate_number,
                }
    return None


def _table_sha256(rows: Iterable[tuple]) -> str:
    payload = "\n".join("|".join(str(part) for part in row) for row in rows)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def certify_instance(item: dict, cutoff: int = CUTOFF) -> dict:
    """Certify one locked character instance with exact integer checks."""
    modulus = int(item["modulus"])
    number = int(item["number"])
    chi = dirichlet_char(modulus, number)
    metadata = _metadata(chi)
    q_star, n_star, chi_star = primitive_lift(modulus, number)
    lift_metadata = _metadata(chi_star)

    values = {n: exact_value(chi, n) for n in range(1, cutoff + 1)}
    lift_values = {n: exact_value(chi_star, n) for n in range(1, cutoff + 1)}
    units = candidate_numbers(modulus)
    target = {unit: values[unit] for unit in units if unit <= cutoff}

    metadata_ok = (
        metadata["conductor"] == int(item["expected_conductor"])
        and metadata["primitive"] == bool(item["expected_primitive"])
        and metadata["parity"] == int(item["expected_parity"])
        and metadata["order"] == int(item["expected_order"])
        and (q_star, n_star) == tuple(item["expected_lift"])
    )

    periodic_ok = all(
        exact_value(chi, n + modulus) == values[n] for n in range(1, cutoff + 1)
    )
    multiplicative_ok = True
    for a in range(1, cutoff + 1):
        for b in range(a, cutoff + 1):
            if not _coprime(a, b):
                continue
            if exact_value(chi, a * b) != values[a] * values[b]:
                multiplicative_ok = False
                break
        if not multiplicative_ok:
            break

    parity_ok = exact_value(chi, -1) == (-1) ** metadata["parity"]
    order_ok = metadata["order"] in (1, 2) and all(
        pow(values[unit], metadata["order"]) == 1
        for unit in units
        if unit <= cutoff
    )
    if metadata["order"] == 2:
        order_ok = order_ok and any(
            values[unit] == -1 for unit in units if unit <= cutoff
        )
    if metadata["order"] == 1:
        order_ok = order_ok and all(
            values[unit] == 1 for unit in units if unit <= cutoff
        )

    structural_zero_ok = all(
        (values[n] == 0) == (math.gcd(n, modulus) > 1)
        for n in range(1, cutoff + 1)
    )
    lift_zero_ok = all(
        (lift_values[n] == 0) == (math.gcd(n, q_star) > 1)
        for n in range(1, cutoff + 1)
    )
    lift_agreement_ok = all(
        values[unit] == lift_values[unit] for unit in units if unit <= cutoff
    )
    lift_metadata_ok = (
        lift_metadata["primitive"]
        and lift_metadata["conductor"] == q_star
        and lift_metadata["parity"] == metadata["parity"]
        and lift_metadata["order"] == metadata["order"]
    )
    smaller = _smaller_matching_modulus(modulus, target, q_star)
    minimality_ok = smaller is None

    new_primes = tuple(
        prime
        for prime in _prime_divisors(modulus)
        if q_star % prime != 0
    )
    activation = [
        n
        for n in range(1, cutoff + 1)
        if math.gcd(n, modulus) > 1 and math.gcd(n, q_star) == 1
    ]
    activation_ok = True
    activation_rows = []
    for n in activation:
        active = values[n] == 0 and lift_values[n] != 0
        activation_ok = activation_ok and active
        if len(activation_rows) < 12:
            activation_rows.append(
                {
                    "n": n,
                    "value": values[n],
                    "lift_value": lift_values[n],
                }
            )
    if not metadata["primitive"]:
        activation_ok = activation_ok and bool(activation)

    prime_power_rows = []
    prime_power_ok = True
    for power, prime, exponent in _prime_powers(cutoff):
        structural_zero = values[power] == 0
        lift_zero = lift_values[power] == 0
        expected_structural_zero = math.gcd(power, modulus) > 1
        expected_lift_zero = math.gcd(power, q_star) > 1
        row_ok = (
            structural_zero == expected_structural_zero
            and lift_zero == expected_lift_zero
        )
        prime_power_ok = prime_power_ok and row_ok
        prime_power_rows.append(
            {
                "q_k": power,
                "prime": prime,
                "exponent": exponent,
                "value": values[power],
                "lift_value": lift_values[power],
                "gcd_modulus": math.gcd(power, modulus),
                "gcd_conductor": math.gcd(power, q_star),
                "structural_zero": structural_zero,
                "lift_zero": lift_zero,
                "new_zero_active": structural_zero and not lift_zero,
            }
        )

    table_rows = [
        (
            n,
            values[n],
            lift_values[n],
            math.gcd(n, modulus),
            math.gcd(n, q_star),
        )
        for n in range(1, cutoff + 1)
    ]
    table_sha = _table_sha256(table_rows)
    pp_sha = _table_sha256(
        (
            row["q_k"],
            row["prime"],
            row["exponent"],
            row["value"],
            row["lift_value"],
            row["gcd_modulus"],
            row["gcd_conductor"],
        )
        for row in prime_power_rows
    )

    checks = {
        "C1_metadata": metadata_ok,
        "C1_periodic": periodic_ok,
        "C1_multiplicative": multiplicative_ok,
        "C1_parity": parity_ok,
        "C1_order": order_ok,
        "C2_structural_zero": structural_zero_ok,
        "C2_prime_power_table": prime_power_ok,
        "C3_lift_metadata": lift_metadata_ok,
        "C3_lift_agreement": lift_agreement_ok,
        "C3_lift_zero": lift_zero_ok,
        "C3_minimality": minimality_ok,
        "C3_activation": activation_ok,
    }
    status = "PASS" if all(checks.values()) else "FAILED"

    return {
        "role": item["role"],
        "modulus": modulus,
        "number": number,
        "identifier": f"chi_{modulus}_{number}",
        "metadata": metadata,
        "primitive_lift": {
            "modulus": q_star,
            "number": n_star,
            "identifier": f"chi_{q_star}_{n_star}",
            "metadata": lift_metadata,
        },
        "new_primes": list(new_primes),
        "activation_count": len(activation),
        "activation_examples": activation_rows,
        "zero_count": sum(1 for value in values.values() if value == 0),
        "unit_count": len(units),
        "table_sha256": table_sha,
        "prime_power_table_sha256": pp_sha,
        "prime_power_rows": prime_power_rows,
        "smaller_matching_modulus": smaller,
        "checks": checks,
        "status": status,
    }


def _sha256_file_lf(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def build_receipt(prereg_sha256: str | None = None) -> dict:
    """Build the deterministic receipt for the five locked instances."""
    prereg = prereg_sha256 or _sha256_file_lf(PREREG_PATH)
    instances = [certify_instance(item) for item in INSTANCES]
    if any(instance["status"] == "FAILED" for instance in instances):
        verdict = "FAILED"
    else:
        verdict = "PASS"
    return {
        "schema": SCHEMA,
        "prereg_sha256": prereg,
        "cutoff": CUTOFF,
        "config": {
            "cutoff": CUTOFF,
            "instances": [
                {
                    **item,
                    "expected_lift": list(item["expected_lift"]),
                    "expected_new_primes": list(item["expected_new_primes"]),
                }
                for item in INSTANCES
            ],
            "definitions": {
                "structural_zero": "chi(n)=0 iff gcd(n,modulus)>1",
                "new_prime": "p divides modulus and p does not divide conductor",
                "activation": (
                    "n<=cutoff with gcd(n,modulus)>1 and gcd(n,conductor)=1"
                ),
            },
        },
        "scope": {
            "character_arithmetic_only": True,
            "guinand_weil_matrix_constructed": False,
            "l_function_object_selected": False,
            "standard_l_function_zero_claim": False,
            "dirichlet_series_zero_claim": False,
            "critical_line_claim": False,
            "rh_claim": False,
            "factorization_claim": False,
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
    """Write the receipt as UTF-8 with LF endings; return its canonical hash."""
    receipt = build_receipt()
    text = json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    target = Path(path)
    target.write_text(text, encoding="utf-8", newline="\n")
    return receipt_sha256(receipt)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Exact Dirichlet-character arithmetic certificate"
    )
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
