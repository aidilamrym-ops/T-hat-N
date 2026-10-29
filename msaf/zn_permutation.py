"""Exact finite certificate for modular multiplication on the unit group.

The core path is exact integer/rational arithmetic only:

* ``fmpq_mat`` for the permutation matrix and its powers;
* ``fmpq_poly`` for characteristic/minimal polynomials and cyclotomic
  factorisation.

No floating-point value, ``numpy`` array, or Arb ball participates in the
certificate.  The package certifies two pre-registered toy instances; it is
not a factorisation algorithm and makes no cryptographic claim.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Iterable, Sequence

from flint import fmpq, fmpq_mat, fmpq_poly

SCHEMA = "msaf.zn_permutation.v1"
REPO_ROOT = Path(__file__).resolve().parents[1]
PREREG_PATH = REPO_ROOT / "reports" / "PREREG_ZN_PERMUTATION_2026-10-20.md"
RECEIPT_PATH = REPO_ROOT / "reports" / "zn_permutation_2026-10-20.json"

# Locked instances from the pre-registration.  The cycles are written as
# tuples so accidental mutation in a caller cannot alter the expected value.
CASES = (
    {
        "n": 15,
        "a": 2,
        "m": 4,
        "cycles": ((1, 2, 4, 8), (7, 14, 13, 11)),
    },
    {
        "n": 21,
        "a": 2,
        "m": 6,
        "cycles": ((1, 2, 4, 8, 16, 11), (5, 10, 20, 19, 17, 13)),
    },
)


def units_mod(n: int) -> list[int]:
    """Return the units of ``Z/nZ`` in ascending order."""
    if n < 2:
        raise ValueError("n must be at least 2")
    return [x for x in range(1, n) if math.gcd(x, n) == 1]


def multiplicative_order(n: int, a: int) -> int:
    """Return the least ``m >= 1`` with ``a**m == 1 (mod n)``."""
    if n < 2:
        raise ValueError("n must be at least 2")
    if math.gcd(a, n) != 1:
        raise ValueError("a must be a unit modulo n")
    value = a % n
    m = 1
    while value != 1:
        value = (value * a) % n
        m += 1
        if m > n:
            raise ArithmeticError("no multiplicative order found")
    return m


def zero_matrix(n: int) -> fmpq_mat:
    """Return the exact ``n x n`` zero matrix."""
    return fmpq_mat(n, n)


def identity_matrix(n: int) -> fmpq_mat:
    """Return the exact ``n x n`` identity matrix."""
    m = fmpq_mat(n, n)
    for i in range(n):
        m[i, i] = fmpq(1)
    return m


def _entry_int(value: fmpq) -> int:
    """Convert an integral ``fmpq`` to a Python ``int``."""
    if int(value.q) != 1:
        raise ValueError(f"non-integral entry: {value}")
    return int(value.p)


def permutation_matrix(n: int, a: int) -> fmpq_mat:
    """Build ``U |x> = |a*x mod n>`` on the sorted units of ``Z/nZ``."""
    units = units_mod(n)
    index = {x: i for i, x in enumerate(units)}
    if math.gcd(a, n) != 1:
        raise ValueError("a must be a unit modulo n")
    m = fmpq_mat(len(units), len(units))
    for x in units:
        m[index[(a * x) % n], index[x]] = fmpq(1)
    return m


def matrix_is_zero(m: fmpq_mat) -> bool:
    """Exact zero test for an ``fmpq_mat``."""
    return m == zero_matrix(m.nrows())


def matrix_is_identity(m: fmpq_mat) -> bool:
    """Exact identity test for a square ``fmpq_mat``."""
    if m.nrows() != m.ncols():
        return False
    return m == identity_matrix(m.nrows())


def is_permutation_matrix(m: fmpq_mat) -> bool:
    """Exact check that ``m`` is a square 0/1 matrix with unit row/col sums."""
    if m.nrows() != m.ncols() or m.nrows() == 0:
        return False
    n = m.nrows()
    for i in range(n):
        row_sum = 0
        for j in range(n):
            value = _entry_int(m[i, j])
            if value not in (0, 1):
                return False
            row_sum += value
        if row_sum != 1:
            return False
    for j in range(n):
        col_sum = sum(_entry_int(m[i, j]) for i in range(n))
        if col_sum != 1:
            return False
    return True


def matrix_sha256(m: fmpq_mat) -> str:
    """Canonical SHA-256 of a small integral matrix."""
    rows = []
    for i in range(m.nrows()):
        rows.append(",".join(str(_entry_int(m[i, j])) for j in range(m.ncols())))
    payload = f"{m.nrows()}x{m.ncols()}\n" + "\n".join(rows)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def cycle_decomposition(n: int, a: int) -> list[list[int]]:
    """Return the cycles of ``x -> a*x mod n`` on the sorted units."""
    units = units_mod(n)
    unit_set = set(units)
    if math.gcd(a, n) != 1:
        raise ValueError("a must be a unit modulo n")
    seen: set[int] = set()
    cycles: list[list[int]] = []
    for start in units:
        if start in seen:
            continue
        cycle: list[int] = []
        x = start
        while x not in seen:
            if x not in unit_set:
                raise ArithmeticError("orbit left the unit group")
            seen.add(x)
            cycle.append(x)
            x = (a * x) % n
        if x != start:
            raise ArithmeticError("permutation orbit did not close at start")
        cycles.append(cycle)
    return cycles


def _x_poly() -> fmpq_poly:
    return fmpq_poly([0, 1])


def expected_charpoly(m: int, multiplicity: int) -> fmpq_poly:
    """Return ``(x**m - 1)**multiplicity`` exactly."""
    return (_x_poly() ** m - 1) ** multiplicity


def expected_minpoly(m: int) -> fmpq_poly:
    """Return ``x**m - 1`` exactly."""
    return _x_poly() ** m - 1


def poly_coeffs(p: fmpq_poly) -> list[int]:
    """Return low-to-high integral coefficients, rejecting non-integers."""
    return [_entry_int(c) for c in p.coeffs()]


def poly_matches(p: fmpq_poly, q: fmpq_poly) -> bool:
    """Exact polynomial equality."""
    return p == q


def divisors(m: int) -> list[int]:
    """Return the positive divisors of ``m`` in ascending order."""
    if m < 1:
        raise ValueError("m must be positive")
    return [d for d in range(1, m + 1) if m % d == 0]


_CYCLOTOMIC_CACHE: dict[int, fmpq_poly] = {}


def cyclotomic(m: int) -> fmpq_poly:
    """Return the ``m``-th cyclotomic polynomial by exact recursion."""
    if m < 1:
        raise ValueError("m must be positive")
    if m in _CYCLOTOMIC_CACHE:
        return _CYCLOTOMIC_CACHE[m]
    p = _x_poly() ** m - 1
    for d in divisors(m):
        if d < m:
            q = cyclotomic(d)
            remainder = p % q
            if not remainder.is_zero():
                raise ArithmeticError(f"non-exact cyclotomic division at d={d}")
            p = p / q
    _CYCLOTOMIC_CACHE[m] = p
    return p


def cyclotomic_product(m: int) -> fmpq_poly:
    """Return ``product_{d|m} Phi_d(x)`` exactly."""
    product = fmpq_poly([1])
    for d in divisors(m):
        product *= cyclotomic(d)
    return product


def cyclotomic_check(charpoly: fmpq_poly, m: int, multiplicity: int) -> bool:
    """Check charpoly against the exact cyclotomic factorisation."""
    base = cyclotomic_product(m)
    if base != _x_poly() ** m - 1:
        return False
    return charpoly == base ** multiplicity


def factor_consistency(charpoly: fmpq_poly, m: int) -> bool:
    """Check ``fmpq_poly.factor()`` multiplies back to ``charpoly``.

    Every irreducible factor is also checked against the pre-computed
    cyclotomic set.  This is an exact algebraic check, not a numerical one.
    """
    content, factors = charpoly.factor()
    product = fmpq_poly([content])
    allowed = [cyclotomic(d) for d in divisors(m)]
    for factor, exponent in factors:
        if not any(factor == candidate for candidate in allowed):
            return False
        product *= factor ** exponent
    return product == charpoly


def commutator_status(n: int, a: int) -> dict:
    """Return the exact ``[CyclicShift, U]`` observation and a control.

    The result is recorded independently.  A nonzero commutator is a valid
    finite observation and does not change the core certificate.
    """
    u = permutation_matrix(n, a)
    n_states = u.nrows()
    shift = zero_matrix(n_states)
    for i in range(n_states):
        shift[(i + 1) % n_states, i] = fmpq(1)
    commutator = shift * u - u * shift
    nonzero_entries = []
    max_abs = 0
    for i in range(n_states):
        for j in range(n_states):
            value = _entry_int(commutator[i, j])
            if value != 0:
                nonzero_entries.append((i, j, value))
                max_abs = max(max_abs, abs(value))
    if nonzero_entries:
        status = "NONZERO"
        witness = {
            "row": nonzero_entries[0][0],
            "col": nonzero_entries[0][1],
            "value": nonzero_entries[0][2],
            "nonzero_entries": len(nonzero_entries),
            "max_abs": max_abs,
        }
    else:
        status = "ZERO"
        witness = {
            "row": None,
            "col": None,
            "value": 0,
            "nonzero_entries": 0,
            "max_abs": 0,
        }

    control = u + u.transpose()
    control_commutator = control * u - u * control
    return {
        "H": "CyclicShift (same sorted unit list)",
        "status": status,
        "witness": witness,
        "control": {
            "H": "U + U^T",
            "status": "ZERO" if matrix_is_zero(control_commutator) else "NONZERO",
            "tautological": True,
        },
    }


def certify_instance(
    n: int,
    a: int,
    expected_m: int | None = None,
    expected_cycles: Sequence[Sequence[int]] | None = None,
) -> dict:
    """Run the exact checks for one instance and return a JSON-safe record."""
    units = units_mod(n)
    u = permutation_matrix(n, a)
    m_computed = multiplicative_order(n, a)
    cycles = cycle_decomposition(n, a)
    dimension = len(units)
    multiplicity = dimension // m_computed
    charpoly = u.charpoly()
    minpoly = u.minpoly()

    expected_cycles_list = (
        [list(cycle) for cycle in expected_cycles]
        if expected_cycles is not None
        else None
    )
    cycle_structure_ok = (
        len(cycles) == multiplicity
        and all(len(cycle) == m_computed for cycle in cycles)
    )
    if expected_cycles_list is not None:
        cycle_structure_ok = cycle_structure_ok and cycles == expected_cycles_list

    checks = {
        "C1_permutation": is_permutation_matrix(u),
        "C1_unitarity": (
            matrix_is_identity(u.transpose() * u)
            and matrix_is_identity(u * u.transpose())
        ),
        "C2_order": matrix_is_identity(u ** m_computed),
        "C2_minimal": all(
            not matrix_is_identity(u ** k) for k in range(1, m_computed)
        ),
        "C2_expected_m": expected_m is None or m_computed == expected_m,
        "C3_cycles": cycle_structure_ok,
        "C4_charpoly": poly_matches(
            charpoly, expected_charpoly(m_computed, multiplicity)
        ),
        "C4_minpoly": poly_matches(minpoly, expected_minpoly(m_computed)),
        "C5_cyclotomic": cyclotomic_check(
            charpoly, m_computed, multiplicity
        ),
        "C5_factor": factor_consistency(charpoly, m_computed),
    }
    status = "PASS" if all(checks.values()) else "FAILED"

    return {
        "n": n,
        "a": a,
        "units": units,
        "dimension": dimension,
        "m_expected": expected_m,
        "m_computed": m_computed,
        "cycles": cycles,
        "matrix_sha256": matrix_sha256(u),
        "determinant": _entry_int(u.det()),
        "charpoly_coeffs": poly_coeffs(charpoly),
        "minpoly_coeffs": poly_coeffs(minpoly),
        "cyclotomic": {
            str(d): poly_coeffs(cyclotomic(d)) for d in divisors(m_computed)
        },
        "checks": checks,
        "status": status,
        "commutator": commutator_status(n, a),
    }


def _sha256_file_lf(path: Path) -> str:
    """SHA-256 of a file after LF normalisation."""
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def build_receipt(prereg_sha256: str | None = None) -> dict:
    """Build the deterministic receipt for both locked instances."""
    prereg = prereg_sha256 or _sha256_file_lf(PREREG_PATH)
    instances = [
        certify_instance(
            case["n"],
            case["a"],
            expected_m=case["m"],
            expected_cycles=case["cycles"],
        )
        for case in CASES
    ]
    verdict = "PASS" if all(item["status"] == "PASS" for item in instances) else "FAILED"
    return {
        "schema": SCHEMA,
        "prereg_sha256": prereg,
        "instances": instances,
        "verdict": verdict,
    }


def canonical_json(value: object) -> str:
    """Canonical JSON used for the receipt hash."""
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


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


def main() -> int:
    """Generate the receipt and print its hash."""
    digest = write_receipt()
    receipt = build_receipt()
    print(f"wrote {RECEIPT_PATH}")
    print(f"verdict: {receipt['verdict']}")
    print(f"receipt sha256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


