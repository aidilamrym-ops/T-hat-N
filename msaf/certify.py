"""Zero certificates: the only admissible way to assert that an identity vanishes.

Central MSAF landmine. Statements such as `[H, T] = 0`, `T^dag T = I` or
`E_trunc = 0` are exact identities only in symbolic algebra. Under ball
arithmetic, multiplication and addition introduce rounding, so the residual is
a WIDE BALL THAT CONTAINS ZERO, not the number zero.

Consequences, in order of subtlety:

    residual == 0                 -> WRONG (almost always False)
    arb(0).contains(residual)     -> WRONG (a point ball cannot hold a wide ball)
    residual.contains(arb(0))     -> CORRECT (this is the only admissible form)

The direction matters. FLINT defines `a.contains(b)` as "b is a subset of a",
so the residual must be the receiver.

Every zero claim in MSAF must pass through `contains_zero`. Mixing it with
equality comparison or with a float conversion is prohibited.
"""

from __future__ import annotations

from typing import NamedTuple

from flint import acb, arb, arb_mat, ctx

__all__ = [
    "MANDATE",
    "ZeroCertificate",
    "CertificateReport",
    "zero_ball",
    "contains_zero",
    "contains_zero_complex",
    "contains_zero_matrix",
    "is_exact_zero",
    "matrix_residual_width",
    "certify",
    "certify_matrix",
    "report",
]

#: The non-negotiable rule: zero claims are certified by enclosure, not equality.
MANDATE = "zero-claim must be certified by containment, never by equality"


def zero_ball() -> arb:
    """The exact zero ball at the active precision."""
    return arb(0)


class ZeroCertificate(NamedTuple):
    """Certification result for a zero residual, with its enclosure width."""

    label: str
    certified: bool
    exact: bool
    max_half_width: arb
    verdict: str


class CertificateReport(NamedTuple):
    precision_bits: int
    certificates: tuple[ZeroCertificate, ...]

    @property
    def all_certified(self) -> bool:
        return all(c.certified for c in self.certificates)

    @property
    def all_exact(self) -> bool:
        return all(c.exact for c in self.certificates)

    def render(self) -> str:
        lines = [f"arb precision = {self.precision_bits} bit", MANDATE]
        lines += [f"  [{c.label}] {c.verdict}" for c in self.certificates]
        lines.append(f"  ALL CERTIFIED = {self.all_certified}")
        lines.append(f"  ALL EXACT     = {self.all_exact}")
        return "\n".join(lines)


def contains_zero(x: arb) -> bool:
    """Does the ball `x` contain the exact point zero?

    The containment direction must be `x.contains(0)`, never `0.contains(x)`:
    a point ball is contained in a wider ball, not the other way round.
    """
    return bool(x.contains(zero_ball()))


def is_exact_zero(x: arb) -> bool:
    """Exact zero with no rounding at all; a far stricter condition."""
    return bool(x.is_exact()) and bool(x.is_zero())


def contains_zero_complex(z) -> bool:
    """Does a complex ball contain the exact complex zero?

    Kept separate from `contains_zero` on purpose. Arb and Acb have different
    containment semantics, different constructor conventions, and in fact
    different `contains` implementations: `arb.contains(acb(...))` raises
    TypeError rather than coercing. A single helper silently applied to both
    domains would therefore fail at runtime, or worse, coerce and mislead.
    """
    return bool(z.contains(acb(0)))


def contains_zero_matrix(m: arb_mat) -> bool:
    """Certify zero for every matrix entry, one at a time."""
    return all(
        contains_zero(m[i, j]) for i in range(m.nrows()) for j in range(m.ncols())
    )


def matrix_residual_width(m: arb_mat) -> arb:
    """Largest ball radius inside a matrix residual: the tightness of a zero claim."""
    widest = zero_ball()
    for i in range(m.nrows()):
        for j in range(m.ncols()):
            widest = max(widest, m[i, j].rad())
    return widest


def _classify(certified: bool, exact: bool, width: arb) -> str:
    if not certified:
        return "FAIL: residual does not contain zero"
    if exact:
        return "PASS: residual is exact zero"
    return "PASS-BY-ENCLOSURE: 0 lies in the residual ball"


def certify(label: str, x: arb) -> ZeroCertificate:
    return ZeroCertificate(
        label=label,
        certified=contains_zero(x),
        exact=is_exact_zero(x),
        max_half_width=x.rad(),
        verdict=_classify(contains_zero(x), is_exact_zero(x), x.rad()),
    )


def certify_matrix(label: str, m: arb_mat) -> ZeroCertificate:
    ok = contains_zero_matrix(m)
    exact = ok and all(
        is_exact_zero(m[i, j]) for i in range(m.nrows()) for j in range(m.ncols())
    )
    width = matrix_residual_width(m)
    return ZeroCertificate(
        label=label,
        certified=ok,
        exact=exact,
        max_half_width=width,
        verdict=_classify(ok, exact, width),
    )


def report(certificates: list[ZeroCertificate]) -> CertificateReport:
    return CertificateReport(precision_bits=ctx.prec, certificates=tuple(certificates))