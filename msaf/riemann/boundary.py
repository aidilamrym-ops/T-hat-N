"""Boundary zero-free certificates: the G1 prerequisite.

SCOPE (binding): certify that xi has no zero ON the rectangular
contour [sig_lo,sig_hi] x [t_lo,t_hi] itself, by rigorous ball
evaluation over adaptively subdivided edge segments. A segment
clears only when its xi enclosure excludes zero; segments that
cannot clear within budget are reported CANNOT-EXCLUDE (a zero may
sit on or arbitrarily near the contour there).

Why this matters (Turing G1): the argument principle counts zeros
strictly INSIDE a contour, and is undefined when a zero lies on
it. The Newton counter (`counter.py`) counts interior boxes while
saying nothing about zeros straddling the outer rectangle edge.
An ALL-CLEAR boundary plus a COMPLETE interior count of n pins
down "exactly n zeros inside, none on the edge" -- the well-posed
setup on which a future winding-number cross-check can build.

Explicit non-claim: boundary clearance alone is NOT an independent
count. It says nothing about the interior (that is the counter's
job) and nothing about S(T) (gap G2) or the rest of the strip
(gap G3). The winding-number computation itself remains OPEN.
"""
from __future__ import annotations

from flint import acb, arb, ctx

from msaf.certify import contains_zero_complex
from msaf.zeta_inversion import evaluate_xi

__all__ = ["certify_boundary"]


def _reject_float(value, name: str) -> None:
    if isinstance(value, float):
        raise TypeError(f"{name}: float64 leakage refused")


def _split(lo: arb, hi: arb) -> arb:
    mid = ((lo + hi) / arb(2)).mid()
    if not bool(lo <= mid) or not bool(mid <= hi):
        raise ValueError("bisection point escaped its interval")
    return mid


def _certify_horizontal(
    sig_pt: arb,
    lo: arb,
    hi: arb,
    max_depth: int,
    min_width: arb,
    edge: str,
    certified: list[dict],
    stuck: list[dict],
) -> int:
    evaluated = 0
    stack: list[tuple[arb, arb, int]] = [(lo, hi, 0)]
    while stack:
        a, b, depth = stack.pop()
        evaluated += 1
        box = acb(sig_pt, a.union(b))
        if not contains_zero_complex(evaluate_xi(box)):
            certified.append(
                {
                    "edge": edge,
                    "t_lo": a.str(12, radius=False),
                    "t_hi": b.str(12, radius=False),
                    "depth": depth,
                }
            )
        elif depth >= max_depth or not bool(min_width < (b - a)):
            stuck.append(
                {
                    "edge": edge,
                    "t_lo": a.str(12, radius=False),
                    "t_hi": b.str(12, radius=False),
                    "depth": depth,
                    "status": "CANNOT-EXCLUDE",
                }
            )
        else:
            mid = _split(a, b)
            stack.append((mid, b, depth + 1))
            stack.append((a, mid, depth + 1))
    return evaluated


def _certify_vertical(
    t_pt: arb,
    lo: arb,
    hi: arb,
    max_depth: int,
    min_width: arb,
    edge: str,
    certified: list[dict],
    stuck: list[dict],
) -> int:
    evaluated = 0
    stack: list[tuple[arb, arb, int]] = [(lo, hi, 0)]
    while stack:
        a, b, depth = stack.pop()
        evaluated += 1
        box = acb(a.union(b), t_pt)
        if not contains_zero_complex(evaluate_xi(box)):
            certified.append(
                {
                    "edge": edge,
                    "sig_lo": a.str(12, radius=False),
                    "sig_hi": b.str(12, radius=False),
                    "depth": depth,
                }
            )
        elif depth >= max_depth or not bool(min_width < (b - a)):
            stuck.append(
                {
                    "edge": edge,
                    "sig_lo": a.str(12, radius=False),
                    "sig_hi": b.str(12, radius=False),
                    "depth": depth,
                    "status": "CANNOT-EXCLUDE",
                }
            )
        else:
            mid = _split(a, b)
            stack.append((mid, b, depth + 1))
            stack.append((a, mid, depth + 1))
    return evaluated


def certify_boundary(
    t_lo_str: str,
    t_hi_str: str,
    sig_lo_str: str = "0.49",
    sig_hi_str: str = "0.51",
    max_depth: int = 20,
    min_width_str: str = "1e-9",
    prec_bits: int = 256,
) -> dict:
    """Certify the 4-edge contour zero-free, or report INCONCLUSIVE.

    Subdivision is per-edge adaptive (bisect the segment that fails
    to clear). The point coordinates (sig_pt / t_pt) are exact
    ``arb`` decimal enclosures, so each evaluated box rigorously
    covers its contour segment. Verdict ALL-CLEAR only when every
    segment of every edge cleared.
    """
    for name, val in (
        ("t_lo_str", t_lo_str),
        ("t_hi_str", t_hi_str),
        ("sig_lo_str", sig_lo_str),
        ("sig_hi_str", sig_hi_str),
        ("min_width_str", min_width_str),
    ):
        _reject_float(val, name)
    if isinstance(max_depth, float) or isinstance(prec_bits, float):
        raise TypeError("max_depth/prec_bits: float64 leakage refused")
    max_depth = int(max_depth)
    if max_depth < 0:
        raise ValueError("max_depth must be non-negative")
    ctx.prec = int(prec_bits)
    t_lo, t_hi = arb(str(t_lo_str)), arb(str(t_hi_str))
    sig_lo, sig_hi = arb(str(sig_lo_str)), arb(str(sig_hi_str))
    min_width = arb(str(min_width_str))
    if not bool(t_lo <= t_hi) or not bool(sig_lo <= sig_hi):
        raise ValueError("empty or inverted rectangle refused")
    certified: list[dict] = []
    stuck: list[dict] = []
    evaluated = 0
    evaluated += _certify_horizontal(
        sig_lo, t_lo, t_hi, max_depth, min_width, "bottom", certified, stuck
    )
    evaluated += _certify_horizontal(
        sig_hi, t_lo, t_hi, max_depth, min_width, "top", certified, stuck
    )
    evaluated += _certify_vertical(
        t_lo, sig_lo, sig_hi, max_depth, min_width, "left", certified, stuck
    )
    evaluated += _certify_vertical(
        t_hi, sig_lo, sig_hi, max_depth, min_width, "right", certified, stuck
    )
    return {
        "verdict": "ALL-CLEAR" if not stuck else "INCONCLUSIVE",
        "boxes_evaluated": evaluated,
        "certified": certified,
        "stuck": stuck,
    }


