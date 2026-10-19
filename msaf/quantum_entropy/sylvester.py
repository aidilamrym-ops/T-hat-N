"""Interval LDL^T (Sylvester criterion) for tridiagonal model blocks (K-Q2).

Statuses:

* ``CERTIFIED_PD``  -- every pivot ball excludes zero and is strictly
  positive in its own engine's arithmetic (the ALL_EXCLUDE_ZERO principle);
* ``FENCE_ZERO``    -- some pivot ball straddles zero; the runner trips the
  loud non-PD fence and exits 2 (UNDETERMINED);
* ``NEGATIVE_PIVOT`` -- some pivot ball is strictly negative: definite
  non-positive-definiteness (deterministic failure, exit 1).

Pivot records keep the first five and last two pivot strings plus counts
(compact, searchable); the full pivot list is recomputable.
"""

from __future__ import annotations

from .engines import _b_div, _b_env, _b_sub, a_fmt, assert_engine_a, b_fmt, b_sign

__all__ = ["sylvester_a", "sylvester_b"]

_FENCE = "FENCE_ZERO"
_PD = "CERTIFIED_PD"
_NEG = "NEGATIVE_PIVOT"


def _compact(items, render) -> dict:
    n = len(items)
    head = [render(x) for x in items[:5]]
    tail = [render(x) for x in items[-2:]] if n > 5 else []
    return {"n": n, "head": head, "tail": tail}


def sylvester_a(diag: list, off2: list) -> dict:
    """Engine A interval LDL^T; diag/off2 are Arb balls."""
    assert_engine_a()
    pivots = [diag[0]]
    p = diag[0]
    for i in range(1, len(diag)):
        if not (p > 0) and not (p < 0):
            return {
                "status": _FENCE,
                "index": i - 1,
                "pivots": _compact(pivots, a_fmt),
            }
        p = diag[i] - off2[i - 1] / p
        pivots.append(p)
    if all(x > 0 for x in pivots):
        status = _PD
    elif any(x < 0 for x in pivots):
        status = _NEG
    else:
        status = _FENCE
    return {"status": status, "index": None, "pivots": _compact(pivots, a_fmt)}


def sylvester_b(diag: list, off2: list) -> dict:
    """Engine B interval LDL^T; diag/off2 are MPBall instances."""
    p = _b_env()
    pivots = [diag[0]]
    cur = diag[0]
    for i in range(1, len(diag)):
        if b_sign(cur) == 0:
            return {
                "status": _FENCE,
                "index": i - 1,
                "pivots": _compact(pivots, b_fmt),
            }
        try:
            cur = _b_sub(diag[i], _b_div(off2[i - 1], cur, p), p)
        except ZeroDivisionError:
            return {
                "status": _FENCE,
                "index": i - 1,
                "pivots": _compact(pivots, b_fmt),
            }
        pivots.append(cur)
    signs = [b_sign(x) for x in pivots]
    if all(s == 1 for s in signs):
        status = _PD
    elif any(s == -1 for s in signs):
        status = _NEG
    else:
        status = _FENCE
    return {"status": status, "index": None, "pivots": _compact(pivots, b_fmt)}
