"""Adaptive zero-exclusion sweep over ordinate ranges.

A leaf rectangle clears (CERTIFIED-ABSENT) only when the rigorous xi
enclosure over the whole rectangle excludes zero. Leaves that cannot
clear within budget are reported CANNOT-EXCLUDE with their bounds --
the honest negative path (a zero may live there). The sweep verdict is
ALL-CLEAR only when every leaf cleared.
"""
from __future__ import annotations

from flint import acb, arb, ctx

from msaf.zeta_inversion import contains_zero_complex, evaluate_xi

__all__ = ["exclusion_box", "certify_box_absent", "sweep_exclusion"]


def _reject_float(value, name: str) -> None:
    if isinstance(value, float):
        raise TypeError(f"{name}: float64 leakage refused")


def exclusion_box(
    t_lo_str: str,
    t_hi_str: str,
    sig_lo_str: str = "0.45",
    sig_hi_str: str = "0.55",
    prec_bits: int = 256,
) -> acb:
    """Rigorous rectangle hull [sig_lo,sig_hi] x [t_lo,t_hi] as one ball.

    Hulls via ``arb.union`` cover the closed intervals exactly; no
    float, no sampling, no gaps.
    """
    for name, val in (
        ("t_lo_str", t_lo_str),
        ("t_hi_str", t_hi_str),
        ("sig_lo_str", sig_lo_str),
        ("sig_hi_str", sig_hi_str),
    ):
        _reject_float(val, name)
    if isinstance(prec_bits, float):
        raise TypeError("prec_bits: float64 leakage refused")
    ctx.prec = int(prec_bits)
    t_lo, t_hi = arb(str(t_lo_str)), arb(str(t_hi_str))
    sig_lo, sig_hi = arb(str(sig_lo_str)), arb(str(sig_hi_str))
    if not bool(t_lo <= t_hi) or not bool(sig_lo <= sig_hi):
        raise ValueError("empty or inverted rectangle refused")
    return acb(sig_lo.union(sig_hi), t_lo.union(t_hi))


def certify_box_absent(box: acb) -> dict:
    """Evaluate xi over the whole box; True only on certified exclusion."""
    if isinstance(box, (float, int)):
        raise TypeError("box: scalar leakage refused")
    value = evaluate_xi(box)
    absent = not contains_zero_complex(value)
    return {
        "absent": bool(absent),
        "mid": value.mid().str(12),
        "real_radius": value.real.rad().str(6),
    }


def sweep_exclusion(
    t_lo_str: str,
    t_hi_str: str,
    sig_lo_str: str = "0.45",
    sig_hi_str: str = "0.55",
    max_depth: int = 6,
    prec_bits: int = 256,
) -> dict:
    """Bisect the range until every leaf clears or budget runs out."""
    for name, val in (("t_lo_str", t_lo_str), ("t_hi_str", t_hi_str)):
        _reject_float(val, name)
    if isinstance(max_depth, float):
        raise TypeError("max_depth: float64 leakage refused")
    max_depth = int(max_depth)
    if max_depth < 0:
        raise ValueError("max_depth must be non-negative")
    ctx.prec = int(prec_bits)
    lo, hi = arb(str(t_lo_str)), arb(str(t_hi_str))
    sig_lo, sig_hi = arb(str(sig_lo_str)), arb(str(sig_hi_str))
    certified: list[dict] = []
    stuck: list[dict] = []
    evaluated = 0
    stack: list[tuple[arb, arb, int]] = [(lo, hi, 0)]
    while stack:
        blo, bhi, depth = stack.pop()
        box = acb(sig_lo.union(sig_hi), blo.union(bhi))
        evaluated += 1
        if certify_box_absent(box)["absent"]:
            certified.append(
                {
                    "t_lo": blo.str(12, radius=False),
                    "t_hi": bhi.str(12, radius=False),
                    "depth": depth,
                }
            )
        elif depth >= max_depth:
            stuck.append(
                {
                    "t_lo": blo.str(12, radius=False),
                    "t_hi": bhi.str(12, radius=False),
                    "depth": depth,
                    "status": "CANNOT-EXCLUDE",
                }
            )
        else:
            mid = (blo + bhi) / arb(2)
            stack.append((mid, bhi, depth + 1))
            stack.append((blo, mid, depth + 1))
    return {
        "verdict": "ALL-CLEAR" if not stuck else "INCONCLUSIVE",
        "boxes_evaluated": evaluated,
        "certified": certified,
        "stuck": stuck,
    }


