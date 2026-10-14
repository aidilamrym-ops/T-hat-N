"""Certified winding number: the G1-b independent count (Turing G1).

SCOPE (binding): count zeros of xi strictly inside the rectangle
[sig_lo,sig_hi] x [t_lo,t_hi] by the argument principle,
N = (total continuous arg change along the contour) / 2pi,
with every operation a certified enclosure. This is INDEPENDENT of
the Newton counter (`counter.py`): Newton isolates boxes from the
inside; winding integrates the boundary from the outside. Their
agreement guards against a zero missed by BOTH Newton and exclusion
(e.g. two close zeros defeating isolation) -- the gap G1 was opened
for. xi is entire (no poles), so N is exactly the interior count.

Method (endpoint unwrapping, homotopy-exact steps). The contour is
traversed counter-clockwise (bottom t=t_lo sigma lo->hi, right
sigma=sig_hi t lo->hi, top t=t_hi sigma hi->lo, left sigma=sig_lo
t hi->lo) through adaptively subdivided segments.
Per step i from corner c_i to c_{i+1}:

- point values W_i = xi(corner_i) are thin balls; per step a rotation
  u (among 8 exact-ball octant rotations, identity tried first) is
  chosen so that BOTH rotated args arg(W_i*u) are thin (radius < 0.1:
  below pi/2 this cannot straddle the branch cut, since a straddle
  forces radius >= ~pi/2). Rotation is angle-preserving, so the true
  change is invariant and the rotation angle cancels in the
  difference: J_i = b_{i+1} - b_i. (An earlier revision used raw
  principal args, which blow up to radius ~pi at cut-crossing
  corners -- caught as INCONCLUSIVE by the machine, never a wrong
  number. Blind spot fixed at the root, not papered over.);
- the segment enclosure B'_i = seg-box U W_i U W_{i+1} must BOTH
  exclude zero (rectangular) AND fit a closed quadrant after some
  k*pi/4 rotation (8 exact-ball rotations tried). Quadrant fit
  gives true |change| <= pi/2 RIGOROUSLY (angles of a quadrant
  minus the origin span at most pi/2);
- the true arc and the chord live in convex B' not containing 0,
  hence are homotopic rel endpoints in C\\{0}: EQUAL arg change,
  exactly, contributing ZERO interval width. The enclosure only
  selects the branch k in J_i + 2pi*k (unique hit asserted) with
  margin pi/2 >> endpoint error ~1e-74; a wrong k would need
  D >= pi - w, impossible under quadrant fit, and is additionally
  blocked by a |delta| <= pi/2 + 0.01 sanity bound.

Hence total error = sum of corner-arg radii only (~1e-70 over ten
thousand steps, << pi). The integer is certified by containing
EXACTLY ONE integer in total/2pi of width < 1.

Subdivision terminates because |xi| attains a positive minimum on
the zero-free contour while enclosures shrink to points (angular
diameter <= pi/4 always passes some rotation -- proven in the
G1-b work notes). Anything unresolved within budget is STUCK
(CANNOT-EXCLUDE on the contour, CANNOT-RESOLVE on branch/integer
ambiguity, NEEDS-SPLIT-BEYOND-BUDGET on refinement): verdict
INCONCLUSIVE with winding None. A number is returned ONLY on
COMPUTED. No float at any point.

Explicit non-claims: counts THIS rectangle's interior only (G3:
rest of strip out of scope); no S(T) bound (G2 still OPEN).
"""
from __future__ import annotations

from flint import acb, arb, ctx

from msaf.certify import contains_zero_complex
from msaf.zeta_inversion import evaluate_xi

__all__ = ["winding_number"]


def _reject_float(value, name: str) -> None:
    if isinstance(value, float):
        raise TypeError(f"{name}: float64 leakage refused")


def _split(a: arb, b: arb) -> arb:
    mid = ((a + b) / arb(2)).mid()
    inside = (bool(a <= mid) and bool(mid <= b)) or (
        bool(b <= mid) and bool(mid <= a)
    )
    if not inside:
        raise ValueError("bisection point escaped its interval")
    return mid


def _unit_octants() -> list[acb]:
    """Rigorous balls around e^{ik pi/4}, k = 0..7 (rotation probes)."""
    sqrt2 = arb(2).sqrt()
    u1 = acb(sqrt2 / arb(2), sqrt2 / arb(2))
    units = [acb(1)]
    for _ in range(7):
        units.append(units[-1] * u1)
    return units


def _rect_bounds(ev: acb) -> tuple[arb, arb, arb, arb]:
    re, im = ev.real, ev.imag
    return (
        re.mid() - re.rad(),
        re.mid() + re.rad(),
        im.mid() - im.rad(),
        im.mid() + im.rad(),
    )


def _in_quadrant(ev: acb) -> bool:
    """True only if the rectangle CERTAINLY fits a closed quadrant."""
    x1, x2, y1, y2 = _rect_bounds(ev)
    return (
        (bool(x1 >= 0) and bool(y1 >= 0))
        or (bool(x1 >= 0) and bool(y2 <= 0))
        or (bool(x2 <= 0) and bool(y1 >= 0))
        or (bool(x2 <= 0) and bool(y2 <= 0))
    )


def _octant_ok(ev: acb, units: list[acb]) -> bool:
    return any(_in_quadrant(ev * u) for u in units)


def _eval_corner(sig: arb, t: arb) -> acb:
    return evaluate_xi(acb(sig, t))


def _thin_args(
    wa: acb, wb: acb, units: list[acb]
) -> tuple[arb, arb] | None:
    """Branch-cut-dodging endpoint args (rotation-invariant change).

    Returns (b_a, b_b) = arg(W u) at both corners for a rotation u
    under which BOTH arg balls are thin (radius < 0.1). A ball
    straddling the negative-real cut has arg radius >= ~pi/2, so
    thinness certifies single-branch containment; the rigid rotation
    preserves the true arg change while its angle cancels in J.
    None when every rotation sees a fat ball (e.g. corner at a
    zero) -- the caller reports CANNOT-RESOLVE, never a guess.
    """
    cap = arb("0.1")
    for idx, u in enumerate(units):
        if idx == 0:
            ba, bb = wa.arg(), wb.arg()
        else:
            ba, bb = (wa * u).arg(), (wb * u).arg()
        if bool(ba.rad() < cap) and bool(bb.rad() < cap):
            return ba, bb
    return None


def _refine_edge(
    box_of,
    corner_of,
    a: arb,
    b: arb,
    max_depth: int,
    min_width: arb,
    edge: str,
    units: list[acb],
    segs: list[dict],
    stuck: list[dict],
) -> int:
    """Subdivide one directed edge until every segment is step-safe.

    A segment is accepted only when B' = seg-box U corners BOTH
    excludes zero AND passes the octant test. Shared corners are
    passed down the recursion (each evaluated once, no float keys).
    Segments append in traversal order (right pushed before left).
    """
    evaluated = 0
    wa = corner_of(a)
    wb = corner_of(b)
    evaluated += 2
    stack: list[tuple[arb, acb, arb, acb, int]] = [(a, wa, b, wb, 0)]
    while stack:
        ca, cwa, cb, cwb, depth = stack.pop()
        sev = evaluate_xi(box_of(ca, cb))
        evaluated += 1
        wide = sev.union(cwa).union(cwb)
        if not contains_zero_complex(wide) and _octant_ok(wide, units):
            segs.append(
                {
                    "edge": edge,
                    "wa": cwa,
                    "wb": cwb,
                    "depth": depth,
                }
            )
        else:
            span = cb - ca
            if bool(span < arb(0)):
                span = -span
            if depth >= max_depth or not bool(min_width < span):
                stuck.append(
                    {
                        "edge": edge,
                        "status": "CANNOT-EXCLUDE"
                        if contains_zero_complex(wide)
                        else "NEEDS-SPLIT-BEYOND-BUDGET",
                    }
                )
            else:
                m = _split(ca, cb)
                wm = corner_of(m)
                evaluated += 1
                stack.append((m, wm, cb, cwb, depth + 1))
                stack.append((ca, cwa, m, wm, depth + 1))
    return evaluated


def _select_branch(j: arb, two_pi: arb, pi: arb) -> int | None:
    """Unique k with (J + 2pi k) meeting [-pi, pi]; None if not unique."""
    jlo = j.mid() - j.rad()
    jhi = j.mid() + j.rad()
    hits = []
    for k in (-1, 0, 1):
        lo = jlo + two_pi * k
        hi = jhi + two_pi * k
        if bool(lo <= pi) and bool(hi >= -pi):
            hits.append(k)
    if len(hits) != 1:
        return None
    return hits[0]


def _round_ball_to_int(q: arb, what: str) -> int | None:
    """Unique integer in the ball; None unless width < 1 and unique.

    The midpoint string is parsed float-free, including scientific
    notation (a bare "1" head with e-70 exponent once rounded a ~0
    quotient to 1 -- caught by the empty-contour test, fixed here).
    """
    qlo = q.mid() - q.rad()
    qhi = q.mid() + q.rad()
    if not bool((qhi - qlo) < arb(1)):
        return None
    s = q.mid().str(20, radius=False).strip().lstrip("[").rstrip("]")
    neg = s.startswith("-")
    core = s.lstrip("+-")
    if "e" in core or "E" in core:
        mant, _, exp = core.replace("E", "e").partition("e")
        try:
            e = int(exp)
        except ValueError:
            return None
        intpart, _, fracpart = mant.partition(".")
        intpart = intpart or "0"
        if e < 0:
            m0 = 0
        elif e >= len(fracpart):
            try:
                m0 = int(intpart + fracpart + "0" * (e - len(fracpart)))
            except ValueError:
                return None
        else:
            try:
                m0 = int((intpart + fracpart[:e]) or "0")
            except ValueError:
                return None
    else:
        try:
            m0 = int(core.split(".")[0] or "0")
        except ValueError:
            return None
    if neg:
        m0 = -m0
    found = []
    for m in range(m0 - 2, m0 + 3):
        if bool(arb(m) >= qlo) and bool(arb(m) <= qhi):
            found.append(m)
    if len(found) != 1:
        return None
    return found[0]


def winding_number(
    t_lo_str: str,
    t_hi_str: str,
    sig_lo_str: str = "0.49",
    sig_hi_str: str = "0.51",
    max_depth: int = 24,
    min_width_str: str = "1e-9",
    prec_bits: int = 256,
) -> dict:
    """Certified zero count inside the rectangle via the argument principle.

    Traversal is counter-clockwise. Verdict COMPUTED carries the
    integer winding (exactly the interior zero count, xi entire);
    anything else is INCONCLUSIVE with winding None -- never a guess.
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
    units = _unit_octants()
    pi = arb.pi()
    two_pi = pi * 2
    tol = arb("0.01")
    segs: list[dict] = []
    stuck: list[dict] = []
    evaluated = 0

    def h_edge(sig_pt: arb):
        return lambda a, b: acb(sig_pt, a.union(b))

    def v_edge(t_pt: arb):
        return lambda a, b: acb(a.union(b), t_pt)

    # Counter-clockwise in the (sigma, t) plane (x = sigma real,
    # y = t imag): bottom t=t_lo sigma lo->hi, right sigma=sig_hi
    # t lo->hi, top t=t_hi sigma hi->lo, left sigma=sig_lo t hi->lo.
    # Interior stays on the left of travel: positive orientation,
    # so the winding is +N for N interior zeros. (An earlier
    # revision traversed bottom = sigma_lo first, i.e. clockwise,
    # returning -N -- caught by the flagship sign check.)
    evaluated += _refine_edge(
        v_edge(t_lo),
        lambda p: _eval_corner(p, t_lo),
        sig_lo,
        sig_hi,
        max_depth,
        min_width,
        "bottom",
        units,
        segs,
        stuck,
    )
    evaluated += _refine_edge(
        h_edge(sig_hi),
        lambda p: _eval_corner(sig_hi, p),
        t_lo,
        t_hi,
        max_depth,
        min_width,
        "right",
        units,
        segs,
        stuck,
    )
    evaluated += _refine_edge(
        v_edge(t_hi),
        lambda p: _eval_corner(p, t_hi),
        sig_hi,
        sig_lo,
        max_depth,
        min_width,
        "top",
        units,
        segs,
        stuck,
    )
    evaluated += _refine_edge(
        h_edge(sig_lo),
        lambda p: _eval_corner(sig_lo, p),
        t_hi,
        t_lo,
        max_depth,
        min_width,
        "left",
        units,
        segs,
        stuck,
    )
    if stuck:
        return {
            "verdict": "INCONCLUSIVE",
            "winding": None,
            "error_radius": None,
            "segments": len(segs),
            "boxes_evaluated": evaluated,
            "stuck": stuck,
        }
    total = arb(0)
    # Every step (edge segments plus the closing corner-to-corner
    # step) is validated independently: rotations may differ per
    # step since each true change is rotation-invariant and each
    # branch selection carries its own pi/2 margin.
    steps: list[tuple[acb, acb, str]] = [
        (seg["wa"], seg["wb"], seg["edge"]) for seg in segs
    ]
    steps.append((segs[-1]["wb"], segs[0]["wa"], "closing"))
    for wa, wb, edge in steps:
        pair = _thin_args(wa, wb, units)
        if pair is None:
            stuck.append({"edge": edge, "status": "CANNOT-RESOLVE"})
            break
        beta_a, beta_b = pair
        j = beta_b - beta_a
        k = _select_branch(j, two_pi, pi)
        if k is None:
            stuck.append({"edge": edge, "status": "CANNOT-RESOLVE"})
            break
        delta = j + two_pi * k
        dlo = delta.mid() - delta.rad()
        dhi = delta.mid() + delta.rad()
        if not bool(dlo >= -pi / 2 - tol) or not bool(dhi <= pi / 2 + tol):
            stuck.append({"edge": edge, "status": "CANNOT-RESOLVE"})
            break
        total = total + delta
    if stuck:
        return {
            "verdict": "INCONCLUSIVE",
            "winding": None,
            "error_radius": None,
            "segments": len(segs),
            "boxes_evaluated": evaluated,
            "stuck": stuck,
        }
    quotient = total / two_pi
    m = _round_ball_to_int(quotient, "winding quotient")
    if m is None:
        return {
            "verdict": "INCONCLUSIVE",
            "winding": None,
            "error_radius": None,
            "segments": len(segs),
            "boxes_evaluated": evaluated,
            "stuck": [{"edge": "quotient", "status": "CANNOT-RESOLVE"}],
        }
    return {
        "verdict": "COMPUTED",
        "winding": m,
        "error_radius": total.rad().str(4),
        "segments": len(segs),
        "boxes_evaluated": evaluated,
        "stuck": [],
    }
