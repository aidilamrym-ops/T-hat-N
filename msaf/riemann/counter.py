"""Certified zero counter over bounded rectangles.

SOUNDNESS CONTRACT (binding): a zero is counted if and only if a
SINGLE interval Newton step on that exact box returns contained with
a derivative excluding zero -- the Moore test, which yields existence
AND uniqueness in that box. Boxes come from a disjoint partition
tree, so counted zeros are provably distinct. The multi-step
``locate_zero`` verdicts (including the uncontained
``ZERO-LOCALIZED-AT-PRECISION-FLOOR`` branch, which fires on balls
that can provably contain no zero at all) NEVER count here.
Excluded boxes contribute zero by rigorous xi evaluation. Anything
else is reported stuck (CANNOT-ISOLATE); the verdict is then PARTIAL
with a certified lower bound, never a silent COMPLETE.

Note: the Lean kernel (`NewtonExistence.moore_box`) currently covers
the Banach-iteration form; the Moore-test form used here is its
documented next formalization target.
"""
from __future__ import annotations

from flint import acb, arb, ctx

from msaf.riemann.exclusion import certify_box_absent
from msaf.zeta_inversion import interval_newton_step

__all__ = ["count_zeros"]


def _reject_float(value, name: str) -> None:
    if isinstance(value, float):
        raise TypeError(f"{name}: float64 leakage refused")


def _split(lo: arb, hi: arb) -> arb:
    mid = ((lo + hi) / arb(2)).mid()
    if not bool(lo <= mid) or not bool(mid <= hi):
        raise ValueError("bisection point escaped its interval")
    return mid


def count_zeros(
    t_lo_str: str,
    t_hi_str: str,
    sig_lo_str: str = "0.49",
    sig_hi_str: str = "0.51",
    max_depth: int = 24,
    min_width_str: str = "1e-4",
    prec_bits: int = 256,
) -> dict:
    """Count zeros in the rectangle, with a completeness verdict.

    The default sigma strip [0.49, 0.51] scopes the count to a line
    neighbourhood; zeros outside the stated rectangle are out of
    scope by construction, and COMPLETE means complete within it.
    Subdivision bisects whichever dimension is wider (2D adaptive),
    since sigma-driven enclosure width can otherwise block exclusion
    no matter how finely t is split.
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
    ctx.prec = int(prec_bits)
    t_lo, t_hi = arb(str(t_lo_str)), arb(str(t_hi_str))
    sig_lo, sig_hi = arb(str(sig_lo_str)), arb(str(sig_hi_str))
    min_width = arb(str(min_width_str))
    if not bool(t_lo < t_hi):
        raise ValueError("empty or inverted t-range refused")
    isolated: list[dict] = []
    stuck: list[dict] = []
    evaluated = 0
    stack: list[tuple[arb, arb, arb, arb, int]] = [
        (sig_lo, sig_hi, t_lo, t_hi, 0)
    ]
    while stack:
        slo, shi, tlo, thi, depth = stack.pop()
        box = acb(slo.union(shi), tlo.union(thi))
        evaluated += 1
        if certify_box_absent(box)["absent"]:
            continue
        step = interval_newton_step(box, 12)
        if bool(step.contained) and bool(step.derivative_excludes_zero):
            isolated.append(
                {
                    "mid": step.refined.mid().str(14),
                    "t_lo": tlo.str(12, radius=False),
                    "t_hi": thi.str(12, radius=False),
                    "sig_lo": slo.str(12, radius=False),
                    "sig_hi": shi.str(12, radius=False),
                }
            )
        elif depth >= max_depth or (
            not bool(min_width < (thi - tlo))
            and not bool(min_width < (shi - slo))
        ):
            stuck.append(
                {
                    "sig_lo": slo.str(12, radius=False),
                    "sig_hi": shi.str(12, radius=False),
                    "t_lo": tlo.str(12, radius=False),
                    "t_hi": thi.str(12, radius=False),
                    "depth": depth,
                    "status": "CANNOT-ISOLATE",
                }
            )
        elif bool((thi - tlo) > (shi - slo)):
            mid = _split(tlo, thi)
            stack.append((slo, shi, mid, thi, depth + 1))
            stack.append((slo, shi, tlo, mid, depth + 1))
        else:
            mid = _split(slo, shi)
            stack.append((mid, shi, tlo, thi, depth + 1))
            stack.append((slo, mid, tlo, thi, depth + 1))
    return {
        "verdict": "COMPLETE" if not stuck else "PARTIAL",
        "count": len(isolated),
        "isolated": isolated,
        "stuck": stuck,
        "boxes_evaluated": evaluated,
    }


