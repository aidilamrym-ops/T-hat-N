"""Bridges between bounded and unbounded mathematics (the two-space doctrine).

A claim about an unbounded object -- an infinite series, an integral over an
unbounded domain -- is assembled from three blocks, and never from a silent
space swap:

    [B]  bounded certificate: a rigorous enclosure of the finite part
         (a partial sum, an integral over a compact interval, a closed form);
    [J]  bridge: a named classical lemma that bounds the tail, instantiated
         with explicit parameters and carried as a conservative enclosure;
    [U]  unbounded statement: the final enclosure = [B] + [J], with the swap
         made explicit (label, cutoff, budget, verdict).

Direction matters. An upper bound must *contain* a true upper bound of the
tail; a lower bound must be *contained in* a true lower bound. Every decision
(``tail <= eps``) uses the rigorous Arb comparisons, which return True only
when the relation is provable for every member of both balls -- never a
midpoint or float comparison. A non-finite input is neither a confirmation
nor a refutation and is rejected at every public entry, matching the landmine
rule of ``msaf/certify.py``.

Lemmas instantiated here (all classical; proofs by elementary calculus,
cited, not re-derived):

    L1  geometric tail (exact, both directions):
            sum_{n>N} r**n = r**(N+1) / (1 - r),        0 <= r < 1
    L2  p-series tail (two-sided, integral comparison):
            1 / ((p-1) * (N+1)**(p-1))  <=  sum_{n>N} n**(-p)
                                        <=  1 / ((p-1) * N**(p-1)),  p > 1
    L3  exponential envelope (upper bound):
            f(x) <= C * exp(-lam * x) on [M, inf)
              =>  int_M^inf f  <=  (C / lam) * exp(-lam * M),  C >= 0, lam > 0
    L4  Gaussian tail (upper bound):
            int_M^inf exp(-x**2) dx  <=  exp(-M**2) / (2 * M),  M > 0
    L5  integral comparison (the mechanism behind L2):
            f positive decreasing:  int_{N+1}^inf f  <=  sum_{n>N} f(n)
                                                    <=  int_N^inf f

Search versus certificate: cutoffs are found by a plain search (doubling and
bisection over integers, bisection over floats for a continuous variable).
The search is a heuristic; nothing is accepted unless a rigorous comparison
certifies it -- ``assemble`` re-checks every promotion.

Non-goals: this module proves no external claim. It certifies mechanics:
given a bounded enclosure and a named tail lemma, the promoted statement is
as rigorous as the inputs, and the swap is on record.
"""

from __future__ import annotations

from typing import Callable, NamedTuple

from flint import arb

__all__ = [
    "MANDATE",
    "Budget",
    "BridgeCertificate",
    "split_budget",
    "geometric_tail",
    "pseries_tail_bounds",
    "exp_envelope_tail",
    "gaussian_tail_ub",
    "choose_cutoff",
    "choose_cutoff_real",
    "assemble",
]

MANDATE = (
    "No claim crosses from a bounded space to an unbounded one without a "
    "named bridge and a conservative tail certificate."
)

_NON_FINITE = (
    "non-finite input rejected: a NaN or inf is neither a confirmation nor "
    "a refutation (msaf/certify.py landmine rule)"
)


def _require_finite(name: str, *values: arb) -> None:
    for value in values:
        if not value.is_finite():
            raise ValueError("%s: %s" % (name, _NON_FINITE))


def _provably_leq(x: arb, y: arb) -> bool:
    """Rigorous: True only if x <= y for every member of both balls."""
    return bool(x <= y)


def _within(bound: arb, eps: arb) -> bool:
    """Rigorous budget check; a non-finite bound never counts as accepted."""
    return bound.is_finite() and bool(bound <= eps)


class Budget(NamedTuple):
    """Error-budget split: eps_bounded + eps_tail = eps (up to ball rounding)."""

    eps: arb
    frac: arb
    eps_bounded: arb
    eps_tail: arb


def split_budget(eps: arb, frac: arb | None = None) -> Budget:
    """Split a total budget eps into bounded-part and tail parts.

    Default split: half for the bounded enclosure, half for the tail.
    """
    frac = arb("0.5") if frac is None else frac
    _require_finite("split_budget.eps", eps)
    _require_finite("split_budget.frac", frac)
    if not bool(arb(0) < eps):
        raise ValueError("split_budget: need provably eps > 0")
    if not (bool(arb(0) < frac) and bool(frac < arb(1))):
        raise ValueError("split_budget: need provably 0 < frac < 1")
    return Budget(eps, frac, (1 - frac) * eps, frac * eps)


def geometric_tail(r: arb, N: int) -> arb:
    """L1, exact: enclosure of sum_{n=N+1}^inf r**n = r**(N+1) / (1 - r)."""
    _require_finite("geometric_tail.r", r)
    if not (bool(arb(0) <= r) and bool(r < arb(1))):
        raise ValueError("geometric_tail: need provably 0 <= r < 1")
    if N < 0:
        raise ValueError("geometric_tail: need N >= 0")
    return r ** (N + 1) / (1 - r)


def pseries_tail_bounds(p: arb, N: int) -> tuple[arb, arb]:
    """L2, two-sided: (lo, hi) with lo <= sum_{n>N} n**(-p) <= hi."""
    _require_finite("pseries_tail_bounds.p", p)
    if not bool(arb(1) < p):
        raise ValueError("pseries_tail_bounds: need provably p > 1")
    if N < 1:
        raise ValueError("pseries_tail_bounds: need N >= 1")
    q = p - 1
    hi = 1 / (q * arb(N) ** q)
    lo = 1 / (q * arb(N + 1) ** q)
    return lo, hi


def exp_envelope_tail(M: arb, C: arb | None = None, lam: arb | None = None) -> arb:
    """L3, upper bound: (C / lam) * exp(-lam * M).

    Applies to any f with f(x) <= C * exp(-lam * x) on [M, inf).
    """
    C = arb(1) if C is None else C
    lam = arb(1) if lam is None else lam
    _require_finite("exp_envelope_tail.M", M)
    _require_finite("exp_envelope_tail.C", C)
    _require_finite("exp_envelope_tail.lam", lam)
    if not bool(arb(0) <= C):
        raise ValueError("exp_envelope_tail: need provably C >= 0")
    if not bool(arb(0) < lam):
        raise ValueError("exp_envelope_tail: need provably lam > 0")
    return (C / lam) * (-lam * M).exp()


def gaussian_tail_ub(M: arb) -> arb:
    """L4, upper bound: exp(-M**2) / (2 * M) for int_M^inf exp(-x**2) dx."""
    _require_finite("gaussian_tail_ub.M", M)
    if not bool(arb(0) < M):
        raise ValueError("gaussian_tail_ub: need provably M > 0")
    return (-(M * M)).exp() / (2 * M)


def choose_cutoff(
    tail_ub: Callable[[int], arb],
    eps: arb,
    start: int = 1,
    max_doublings: int = 64,
) -> int:
    """Cutoff N (doubling then bisection) with tail_ub(N) <= eps *proven*.

    The search order is heuristic; the returned N is accepted only after a
    rigorous comparison. If no N within max_doublings satisfies the budget,
    a RuntimeError is raised -- fail-closed, never a silent pass.
    """
    _require_finite("choose_cutoff.eps", eps)
    if not bool(arb(0) < eps):
        raise ValueError("choose_cutoff: need provably eps > 0")
    if start < 1:
        raise ValueError("choose_cutoff: need start >= 1")
    n = start
    for _ in range(max_doublings):
        if _within(tail_ub(n), eps):
            break
        n *= 2
    else:
        raise RuntimeError(
            "choose_cutoff: no cutoff within %d doublings satisfies the "
            "budget (unreachable or undecidable at this precision)"
            % max_doublings
        )
    lo, hi = max(start, n // 2), n
    while lo < hi:
        mid = (lo + hi) // 2
        if _within(tail_ub(mid), eps):
            hi = mid
        else:
            lo = mid + 1
    if not _within(tail_ub(lo), eps):
        raise RuntimeError("choose_cutoff: final check failed (undecidable)")
    return lo


def choose_cutoff_real(
    tail_ub: Callable[[arb], arb],
    eps: arb,
    lo: float = 0.0,
    hi: float = 1.0,
    tol: float = 1e-12,
    growth: int = 64,
    steps: int = 200,
) -> arb:
    """Cutoff on a continuous variable: float-midpoint bisection, heuristic.

    The returned value was the last point at which the budget check passed a
    rigorous arb comparison, but the caller must re-check -- never trust a
    search (``assemble`` performs the re-check).
    """
    _require_finite("choose_cutoff_real.eps", eps)
    if not bool(arb(0) < eps):
        raise ValueError("choose_cutoff_real: need provably eps > 0")
    if not (0.0 < lo < hi):
        raise ValueError("choose_cutoff_real: need 0 < lo < hi")
    x_hi = hi
    for _ in range(growth):
        if _within(tail_ub(arb(repr(x_hi))), eps):
            break
        x_hi *= 2.0
    else:
        raise RuntimeError("choose_cutoff_real: no cutoff within growth range")
    x_lo = lo
    for _ in range(steps):
        if x_hi - x_lo <= tol * max(1.0, x_hi):
            break
        mid = 0.5 * (x_lo + x_hi)
        if _within(tail_ub(arb(repr(mid))), eps):
            x_hi = mid
        else:
            x_lo = mid
    return arb(repr(x_hi))


class BridgeCertificate(NamedTuple):
    """[B]/[J]/[U] blocks for one bounded-to-unbounded promotion."""

    label: str
    bounded: arb
    tail_lo: arb
    tail_hi: arb
    eps: arb
    certified: bool
    verdict: str

    def total(self) -> tuple[arb, arb]:
        """(lo, hi): enclosure of [B] + [J] -- the [U] statement."""
        return self.bounded + self.tail_lo, self.bounded + self.tail_hi

    def lines(self) -> list[str]:
        lo, hi = self.total()
        return [
            "[B] bounded part : %s" % self.bounded,
            "[J] tail in      : [%s, %s]" % (self.tail_lo, self.tail_hi),
            "[U] total in     : [%s, %s]" % (lo, hi),
            "    budget eps   : %s   (width <= eps: %s)" % (self.eps, self.certified),
            "    verdict      : %s" % self.verdict,
            "    label        : %s" % self.label,
        ]


def assemble(
    label: str,
    bounded: arb,
    tail_hi: arb,
    eps: arb,
    tail_lo: arb | None = None,
) -> BridgeCertificate:
    """Assemble and (re-)certify a bridge: total width <= eps must be proven.

    tail_lo defaults to exact 0, valid when the tail is known non-negative
    (a positive series or a non-negative integrand). A non-finite argument
    raises; a width that cannot be proven within budget returns a certificate
    with ``certified=False`` -- it never passes silently.
    """
    tail_lo = arb(0) if tail_lo is None else tail_lo
    _require_finite("assemble.bounded", bounded)
    _require_finite("assemble.tail_lo", tail_lo)
    _require_finite("assemble.tail_hi", tail_hi)
    _require_finite("assemble.eps", eps)
    if not bool(arb(0) < eps):
        raise ValueError("assemble: need provably eps > 0")
    if not bool(arb(0) <= tail_lo):
        raise ValueError("assemble: need provably tail_lo >= 0")
    if not _provably_leq(tail_lo, tail_hi):
        raise ValueError("assemble: need provably tail_lo <= tail_hi")
    width = (bounded + tail_hi) - (bounded + tail_lo)
    certified = _provably_leq(width, eps)
    verdict = (
        "CERTIFIED: bounded + bridge within budget"
        if certified
        else "NOT CERTIFIED: tail width exceeds budget (increase cutoff or relax eps)"
    )
    return BridgeCertificate(label, bounded, tail_lo, tail_hi, eps, certified, verdict)
