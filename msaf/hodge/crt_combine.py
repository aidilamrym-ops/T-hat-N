"""Exact CRT combiner + oracle gate for the Couveignes-Henocq last trace.

SCOPE (binding): recover ONE integer (the missing trace a_11) from
residues modulo distinct primes, with a uniqueness certificate from
the Weil envelope. Every operation is exact integer arithmetic; there
is no rounding anywhere, hence no rounding error to bound.

Rules (all asserted loudly):
  - moduli must be pairwise coprime (gcd check), residues in range;
  - the combined modulus M must satisfy M > 2*B (B = envelope bound)
    or the verdict is INCONCLUSIVE -- a small modulus set never
    yields a number, no matter how suggestive;
  - the oracle gate (`oracle_check`) compares engine-produced
    recoveries of the KNOWN traces against locked integers; any
    mismatch refuses the engine for the unknown trace.

Explicit non-claim: this module manufactures no residues. A residue
source (the CH engine, still open per reports/HODGE_CH_SPEC.md) that
emits a corrupted residue yields a wrong integer inside the envelope
that this layer cannot detect -- that is precisely what the oracle
gate is for, and why the engine must reproduce a_1..a_10 first.
"""
from __future__ import annotations

from math import gcd

__all__ = ["crt", "recover_integer", "oracle_check"]


def _reject_float(value, name: str) -> None:
    if isinstance(value, (float, bool)):
        raise TypeError(f"{name}: float64 leakage refused")


def _as_int(value, name: str) -> int:
    _reject_float(value, name)
    if isinstance(value, bool):
        raise TypeError(f"{name}: bool leakage refused")
    return int(value)


def crt(residues: list[int], moduli: list[int]) -> int:
    """Exact Garner CRT: x with x = r_i (mod m_i) for all i.

    Moduli must be pairwise coprime and each residue in [0, m_i);
    both asserted. Returns the least non-negative solution.
    """
    if len(residues) != len(moduli) or not moduli:
        raise ValueError("residues and moduli must be non-empty and paired")
    rs = [_as_int(r, "residue") for r in residues]
    ms = [_as_int(m, "modulus") for m in moduli]
    for m in ms:
        if m < 2:
            raise ValueError(f"modulus must be >= 2, got {m}")
    for i in range(len(ms)):
        if not 0 <= rs[i] < ms[i]:
            raise ValueError(f"residue {rs[i]} out of range for modulus {ms[i]}")
        for j in range(i + 1, len(ms)):
            if gcd(ms[i], ms[j]) != 1:
                raise ValueError(
                    f"moduli not coprime: {ms[i]} and {ms[j]}"
                )
    x, m = 0, 1
    for r, mod in zip(rs, ms):
        inv = pow(m, -1, mod)
        x = x + m * (((r - x) * inv) % mod)
        m *= mod
    return x % m


def recover_integer(
    residues: list[int], moduli: list[int], bound: int
) -> dict:
    """Recover the integer in [-bound, bound] or refuse (INCONCLUSIVE).

    Uniqueness certificate: with M the product of the moduli, any two
    distinct candidates differ by a multiple of M; if M > 2*bound the
    symmetric representative is THE integer. Otherwise no number is
    returned, however suggestive the residues look.
    """
    b = _as_int(bound, "bound")
    if b < 0:
        raise ValueError(f"bound must be >= 0, got {b}")
    x = crt(residues, moduli)
    mods = [_as_int(m, "modulus") for m in moduli]
    m_prod = 1
    for m in mods:
        m_prod *= m
    if not m_prod > 2 * b:
        return {
            "verdict": "INCONCLUSIVE",
            "value": None,
            "modulus": m_prod,
            "reason": f"M={m_prod} <= 2B={2*b}: budget insufficient",
        }
    value = x if x <= m_prod // 2 else x - m_prod
    if abs(value) > b:
        return {
            "verdict": "INCONCLUSIVE",
            "value": None,
            "modulus": m_prod,
            "reason": "symmetric representative outside envelope",
        }
    return {"verdict": "RECOVERED", "value": value, "modulus": m_prod,
            "reason": "M > 2B: uniqueness certified"}


def oracle_check(recovered: dict[int, int], known: dict[int, int]) -> dict:
    """The engine reproduces every locked known trace, or is refused.

    `recovered` maps trace index -> combiner-recovered integer from
    engine residues; `known` maps index -> locked exact integer. Any
    missing index or any mismatch fails the engine LOUDLY: a residue
    source that cannot reproduce the known cannot be trusted on the
    unknown, and a corrupted residue otherwise yields a wrong integer
    that nothing downstream would catch.
    """
    mismatches = []
    for k, want in known.items():
        if k not in recovered:
            mismatches.append((k, "missing", want))
        elif recovered[k] != want:
            mismatches.append((k, recovered[k], want))
    if mismatches:
        return {"verdict": "ORACLE-FAIL", "mismatches": mismatches}
    return {"verdict": "ORACLE-HOLD", "mismatches": []}


