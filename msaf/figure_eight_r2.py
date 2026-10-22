"""T2-r2: validated figure-eight periodic orbit on a reduced 8x8 shooting system.

Scope and pass criteria are locked in
``reports/PREREG_FIGURE_EIGHT_R2_2026-10-22.md`` (sections 1-10).  The
certificate targets a periodic orbit of the planar equal-mass three-body
problem with the exact fixed period ``T0``, after quotiening translations
and boosts by an exact centre-of-mass lift.  Phase and orientation are
fixed by two gauges:

    q1y = 1/5,          I_xy = sum_i q_ix q_iy = 0,

and the six return components ``(0,1,3,4,5,6)`` plus the two gauges form
the square map ``G: R^8 -> R^8``.  Krawczyk's theorem on a small exact box
certifies existence and LOCAL uniqueness; no global, stability, spectral,
or spectral-track claim is made.

Reuse is import-only from the frozen modules ``msaf.ode_validated`` (T1)
and ``msaf.ode_validated_block`` (T1b): the validated Taylor step, the
continuous signed block certificate, and the ball/AST helpers are theirs.
The reduced lift, gauges, Newton-Krawczyk map, and criteria are new here.
No float is used in the certified path (AST-scanned by the guard).
"""

from __future__ import annotations

import ast
import json
from fractions import Fraction
from pathlib import Path

import flint
from flint import arb, arb_mat

from msaf import ode_validated as t1
from msaf import ode_validated_block as t1b

ROOT = Path(__file__).resolve().parents[1]
PREREG_PATH = ROOT / "reports" / "PREREG_FIGURE_EIGHT_R2_2026-10-22.md"
RECEIPT_PATH = ROOT / "reports" / "figure_eight_r2_2026-10-22.json"

PREC = t1.PREC
ORDER = t1.ORDER
SCHEMA = "msaf.figure_eight_r2.v1"
T1_MODULE_SHA = "c1d9b5d60036a5f0772f7e3f1b8c78969efaa7146a713c762531ddce346251b9"
T1B_MODULE_SHA = "42d196a51c5ae45e3b87b8c1e36319abfeb93df776b3c2317e812f7c2c0b5b97"
PREREG_SHA = "c6b7d4c7cf253962f7d50b8c6d25f0df5079972d498c63a849cb96f4a226bb39"

# --- locked data (prereg sections 1-4; all exact rationals) ---------------

T0 = Fraction(632600304, 10**8)             # fixed period 6.326003040
C = Fraction(1, 5)                          # phase gauge q1y = 1/5
H_STEPS = 1536
H_GRID = T0 / H_STEPS

SEED_R2 = (
    Fraction("0.1448544459401314"),
    Fraction("0.2"),
    Fraction("-1.04839609289586"),
    Fraction("-0.07773682382648972"),
    Fraction("-0.7922166346262658"),
    Fraction("-0.9821886530957104"),
    Fraction("0.15139114003894605"),
    Fraction("0.5091019520994268"),
)

KEEP = (0, 1, 3, 4, 5, 6)                   # dropped return rows: 2 and 7
IDX8 = (0, 1, 2, 3, 6, 7, 8, 9)            # 12-state indices of the 8 x coords
DEP8 = (4, 5, 4, 5, 10, 11, 10, 11)        # q3x,q3y,v3x,v3y columns tied to x

R_B = Fraction(1, 10**10)                   # Krawczyk box radius
K_MARGIN = Fraction(9, 10)                  # K(B) inclusion budget
KAPPA_MAX = Fraction(1, 2)                  # contraction bound
NEWTON_MAX = 6
NEWTON_TARGET = Fraction(1, 10**24)
ROUND_DEC = 10**25

TUBE_CAP = Fraction(1, 10**7)               # K2 state-tube width cap
GAUSS_DET_MIN = Fraction(1, 10**6)          # K4 determinant lower bound
GAUSS_COND_MAX = Fraction(10**6, 1)         # K4 condition upper bound
CHOREO_TOL = Fraction(1, 10**6)             # K5 choreography defect

REMAINDER_FACTOR = 1                        # mutation M1 sets 1e70
SWEEP_SIGNED = True                         # mutation M5 sets False
BLOCK_STEPS = 96

N_STATE = 12
N_SEC = 8


# --- small helpers --------------------------------------------------------


def _b(fr: Fraction) -> arb:
    """Exact rational as a tight arb ball (frozen T1 primitive)."""
    return t1._ball(fr)


ZERO = arb(0)
ONE = arb(1)


def _round25(x: arb) -> Fraction:
    """Round the midpoint of a ball to the nearest 25-decimal grid point.

    The midpoint of an arb is an exact dyadic rational; ``man_exp`` exposes
    it without text formatting.  The old T2-style decimal-string parser
    truncated the mantissa of scientific notation (e.g. ``1.44...e+24`` to
    ``1``); this implementation multiplies the exact dyadic by ``10**25``
    and rounds the resulting rational to the nearest integer, float-free.
    """
    man, exp = x.mid().man_exp()
    man = int(man)
    exp = int(exp)
    if exp >= 0:
        scaled = Fraction(man << exp, 1) * ROUND_DEC
    else:
        scaled = Fraction(man, 1 << (-exp)) * ROUND_DEC
    num, den = scaled.numerator, scaled.denominator
    whole, rem = divmod(num, den)
    if 2 * rem >= den:
        whole += 1
    return Fraction(whole, ROUND_DEC)


def _max_arb(values: list[arb]) -> arb:
    return t1b._max_arb(values)


def _row_abs(mat: list[list[arb]], i: int, n: int) -> arb:
    acc = arb(0)
    for j in range(n):
        acc = acc + mat[i][j].abs_upper()
    return acc


# --- lift / projection ----------------------------------------------------


def _lift(x: list[arb]) -> list[arb]:
    """8 reduced coordinates -> 12-dimensional COM-zero state."""
    return [
        x[0], x[1], x[2], x[3],
        -x[0] - x[2], -x[1] - x[3],
        x[4], x[5], x[6], x[7],
        -x[4] - x[6], -x[5] - x[7],
    ]


def _lift_box(x: list[Fraction], c: list[arb]) -> tuple[list[arb], list[arb]]:
    """Lift a reduced point box to a sound 12-dimensional component box.

    The dependent q3/v3 radii are the sums of the corresponding q1/q2
    radii; this is the exact radius of the linear combination, so every
    lifted point of the 8-dimensional box is contained.
    """
    m = _lift([_b(v) for v in x])
    r = [
        c[0], c[1], c[2], c[3],
        c[0] + c[2], c[1] + c[3],
        c[4], c[5], c[6], c[7],
        c[4] + c[6], c[5] + c[7],
    ]
    return m, r


def _project8(y: list[arb]) -> list[arb]:
    """12-dimensional state -> the eight independent reduced coordinates."""
    return [y[0], y[1], y[2], y[3], y[6], y[7], y[8], y[9]]


def _g2_value(x: list[arb]) -> arb:
    """I_xy = sum_i q_ix q_iy with q3 = -q1 - q2."""
    return x[0] * x[1] + x[2] * x[3] + (x[0] + x[2]) * (x[1] + x[3])


def _g2_grad(x: list[arb]) -> list[arb]:
    """Exact gradient of I_xy in the eight reduced coordinates."""
    a, b, c, d = x[0], x[1], x[2], x[3]
    return [
        2 * b + d,
        2 * a + c,
        b + 2 * d,
        a + 2 * c,
        ZERO,
        ZERO,
        ZERO,
        ZERO,
    ]


# --- checkpoint certificate (signed = frozen T1b; reset = M5 path) --------


def _certificate(jacs, rems, quads, c_in, upto, lo):
    """Checkpoint certificate plus slack weights.

    Honest path (``SWEEP_SIGNED``): the frozen T1b continuous signed sweep.
    Mutation path: the same sweep with the sensitivity product reset to its
    entrywise absolute value at every block boundary (M5) -- a wider but
    still sound enclosure, used only to demonstrate that the K3 gate
    discriminates.
    """
    if SWEEP_SIGNED:
        return t1b.certificate(jacs, rems, quads, c_in, upto, lo, N_STATE)
    n = N_STATE
    p_m = t1b._identity(n)
    p_r = [[arb(0) for _ in range(n)] for _ in range(n)]
    c_out = [arb(0) for _ in range(n)]
    slack_weight = [arb(0) for _ in range(n)]
    for k in range(upto - 1, -1, -1):
        flat = jacs[k]
        jac = [[flat[i * n + j] for j in range(n)] for i in range(n)]
        m_k, r_k = t1b._mr_split(jac)
        for i in range(n):
            acc = c_out[i]
            weight = arb(0)
            for j in range(n):
                w = p_m[i][j].abs_upper() + p_r[i][j]
                acc = acc + w * (rems[k][j] + quads[k])
                weight = weight + w
            c_out[i] = acc
            if k >= lo:
                slack_weight[i] = slack_weight[i] + weight
        p_m, p_r = t1b._mr_mul(p_m, p_r, m_k, r_k)
        if k > 0 and k % BLOCK_STEPS == 0:
            p_m = [[p_m[i][j].abs_upper() for j in range(n)] for i in range(n)]
    for i in range(n):
        acc = c_out[i]
        for j in range(n):
            acc = acc + (p_m[i][j].abs_upper() + p_r[i][j]) * c_in[j]
        c_out[i] = acc
    return c_out, slack_weight


# --- full validated forward pass -----------------------------------------


def _forward_pass(m0: list[arb], c0: list[arb], gate: bool) -> dict:
    """Integrate [m0 +/- c0] over T0 with signed-sweep certificates.

    ``m0`` must be a point (midpoints only); ``c0`` carries the input box
    radii.  Blocks of ``BLOCK_STEPS`` insert the locked quadratic slack and
    compute a certificate at every block end (K2 checkpoints).  When
    ``gate`` is true the run fail-fasts as soon as a checkpoint radius
    exceeds ``TUBE_CAP``.
    """
    n = N_STATE
    m = [x.mid() for x in m0]
    c = list(c0)
    c_in = list(c0)
    jacs: list = []
    rems: list = []
    quads: list = []
    mids: list = [list(m)]
    checkpoints: dict = {}
    pcs: dict = {}
    error = None
    steps_done = 0
    factor = _b(Fraction(REMAINDER_FACTOR, 1))
    for k in range(H_STEPS):
        try:
            m_next, jac, rem, _quad = t1b.forward_step(
                t1.coeffs_three_body,
                t1.rhs_three_body,
                m,
                c,
                _b(H_GRID),
                ORDER,
                True,
            )
        except t1.ValidationError as exc:
            error = "aborted at step %d: %s" % (k + 1, exc)
            steps_done = k
            break
        if REMAINDER_FACTOR != 1:
            rem = [r * factor for r in rem]
        jacs.append([jac[i][j] for i in range(n) for j in range(n)])
        rems.append(rem)
        quads.append(arb(0))
        mids.append([x.mid() for x in m_next])
        c_next = []
        for i in range(n):
            acc = arb(0)
            for j in range(n):
                acc = acc + jac[i][j].abs_upper() * c[j]
            c_next.append(acc + rem[i] + t1._tol(t1b.EPS_SLACK))
        m = [x.mid() for x in m_next]
        c = c_next
        steps_done = k + 1
        upto = k + 1
        if upto % BLOCK_STEPS == 0 or upto == H_STEPS:
            lo = upto - min(BLOCK_STEPS, upto)
            c_pre, slack_weight = _certificate(jacs, rems, quads, c_in, upto, lo)
            kappa = t1b._kappa_nl()
            radius = _max_arb(c_pre)
            slack = kappa * radius * radius
            for kk in range(lo, upto):
                quads[kk] = slack
            c_out = [c_pre[i] + slack_weight[i] * slack for i in range(n)]
            c = list(c_out)
            maxc = _max_arb(c_out)
            width = _b(Fraction(2, 1)) * maxc
            checkpoints[upto] = {
                "step": upto,
                "c_out": list(c_out),
                "max_radius": maxc,
                "width": width,
                "slack": slack,
            }
            if gate and bool(width > _b(TUBE_CAP)):
                error = (
                    "K2 fail-fast: tube width %s exceeds cap %s at step %d"
                    % (width, _b(TUBE_CAP), upto)
                )
                break
    return {
        "mids": mids,
        "jacs": jacs,
        "rems": rems,
        "quads": quads,
        "checkpoints": checkpoints,
        "pcs": pcs,
        "error": error,
        "steps_done": steps_done,
        "c0": list(c_in),
    }


# --- input-radius series (checkpoint certificate + extension) ------------


def _c_series_tight(ps: dict) -> list:
    """Input-radius enclosure at every grid step of the run."""
    if ps.get("cat_series") is not None:
        return ps["cat_series"]
    n = N_STATE
    done = ps["steps_done"]
    series = [None] * (done + 1)
    c = list(ps["c0"])
    for k in range(done):
        if k in ps["checkpoints"]:
            c = list(ps["checkpoints"][k]["c_out"])
        series[k] = list(c)
        flat = ps["jacs"][k]
        c_next = []
        for i in range(n):
            acc = arb(0)
            for j in range(n):
                acc = acc + flat[i * n + j].abs_upper() * c[j]
            c_next.append(acc + ps["rems"][k][i] + ps["quads"][k])
        c = c_next
    series[done] = list(c)
    ps["cat_series"] = series
    return series


# --- reduced sensitivity product -----------------------------------------


def _sproduct8(ps: dict, upto: int):
    """Incremental 8x8 reduced sensitivity chain in midpoint-radius form.

    The 8x8 one-step matrix is the derivative of the constrained reduced
    map: for independent coordinate ``j`` the lift changes both the
    independent state column ``IDX8[j]`` and its dependent partner
    ``DEP8[j]`` (q3 or v3), so the step entry is
    ``J[row_i, IDX8[j]] - J[row_i, DEP8[j]]``.  This is exactly the
    row/column projection of the full step derivative onto the COM-zero
    subspace (the old T2 pattern used the independent block only, which
    ignored the dependent columns and produced a wrong Newton direction).
    """
    n = N_SEC
    chain = ps.get("sprod8")
    if chain is None:
        chain = [(t1b._identity(n), [[arb(0) for _ in range(n)] for _ in range(n)])]
        ps["sprod8"] = chain
    while len(chain) <= upto:
        k = len(chain) - 1
        flat = ps["jacs"][k]
        jac = [
            [
                flat[IDX8[i] * N_STATE + IDX8[j]]
                - flat[IDX8[i] * N_STATE + DEP8[j]]
                for j in range(n)
            ]
            for i in range(n)
        ]
        m_k, r_k = t1b._mr_split(jac)
        p_m, p_r = t1b._mr_mul(m_k, r_k, chain[k][0], chain[k][1])
        chain.append((p_m, p_r))
    return chain[upto]


def _flow_deriv8(ps: dict) -> list[list[arb]]:
    """8x8 interval enclosure of d proj(Phi_T)/dx over the input box."""
    p_m, p_r = _sproduct8(ps, H_STEPS)
    return [
        [p_m[i][j] + arb(0, p_r[i][j]) for j in range(N_SEC)]
        for i in range(N_SEC)
    ]


# --- one certified run: G, DG, final state ---------------------------------


def _evaluate(
    x: list[Fraction], c8: list[arb], gate: bool, box_gauges: bool
) -> dict:
    """Certified run from the reduced point ``x`` with input box ``c8``.

    Returns ``G`` (six return components plus the two gauges), the 8x8
    derivative ``DG``, and the final 12-dimensional state enclosure.  The
    flow derivative is the reduced 8x8 sensitivity product; the gauge
    gradients are exact interval formulas.  ``box_gauges`` evaluates the
    I_xy gradient over the input box (for DG(B)); otherwise at the point.
    """
    x_arb = [_b(v) for v in x]
    m0, c0 = _lift_box(x, c8)
    ps = _forward_pass(m0, c0, gate)
    out = {"ps": ps}
    if ps["error"] is not None:
        out["ok"] = False
        out["error"] = ps["error"]
        return out
    if H_STEPS not in ps["checkpoints"]:
        out["ok"] = False
        out["error"] = "missing final checkpoint"
        return out
    ck = ps["checkpoints"][H_STEPS]
    c_out = ck["c_out"]
    y = [ps["mids"][H_STEPS][i] + arb(0, c_out[i]) for i in range(N_STATE)]
    proj = _project8(y)
    p8 = [proj[i] - x_arb[i] for i in range(N_SEC)]
    G = [p8[KEEP[i]] for i in range(6)] + [
        x_arb[1] - _b(C),
        _g2_value(x_arb),
    ]
    S8 = _flow_deriv8(ps)
    DP = [
        [S8[i][j] - (ONE if i == j else ZERO) for j in range(N_SEC)]
        for i in range(N_SEC)
    ]
    if box_gauges:
        xg = [x_arb[i] + arb(0, c8[i]) for i in range(N_SEC)]
    else:
        xg = x_arb
    DG = [[DP[KEEP[i]][j] for j in range(N_SEC)] for i in range(6)]
    DG.append([ONE if j == 1 else ZERO for j in range(N_SEC)])
    DG.append(_g2_grad(xg))
    out.update(
        {
            "ok": True,
            "G": G,
            "DG": DG,
            "y_final": y,
            "f_inf": _max_arb([fi.abs_upper() for fi in G]),
            "c_final": c_out,
            "S8": S8,
        }
    )
    return out


# --- inverse / determinant helpers ---------------------------------------


def _inverse_mid(df: list[list[arb]]) -> arb_mat | None:
    """Midpoint inverse of an interval 8x8 matrix, or None if singular."""
    n = N_SEC
    mat = arb_mat([[df[i][j].mid() for j in range(n)] for i in range(n)])
    try:
        return mat.inv()
    except ZeroDivisionError:
        return None


def _det_interval(mat: list[list[arb]]) -> arb:
    """Interval determinant via pivoted Gaussian elimination (mid pivots)."""
    n = len(mat)
    a = [list(row) for row in mat]
    sign = 1
    for p in range(n):
        best = p
        best_val = a[p][p].mid().abs_upper()
        for i in range(p + 1, n):
            val = a[i][p].mid().abs_upper()
            if bool(val > best_val):
                best = i
                best_val = val
        if best != p:
            a[p], a[best] = a[best], a[p]
            sign = -sign
        piv = a[p][p]
        for i in range(p + 1, n):
            fac = a[i][p] / piv
            for j in range(p, n):
                a[i][j] = a[i][j] - fac * a[p][j]
    det = _b(Fraction(sign, 1))
    for p in range(n):
        det = det * a[p][p]
    return det


# --- Newton ---------------------------------------------------------------


def _grid_floor_ceil(x: arb) -> tuple[int, int]:
    """Floor and ceil of ``10**25 * midpoint(x)`` as exact integers."""
    man, exp = x.mid().man_exp()
    man = int(man)
    exp = int(exp)
    if exp >= 0:
        scaled = Fraction(man << exp, 1) * ROUND_DEC
    else:
        scaled = Fraction(man, 1 << (-exp)) * ROUND_DEC
    lo = scaled.numerator // scaled.denominator
    hi = lo if scaled.denominator * lo == scaled.numerator else lo + 1
    return lo, hi


def _newton_step(
    x: list[Fraction], wmat: arb_mat, G: list[arb], dg: list[list[arb]]
) -> list[Fraction]:
    """One Newton iterate on the locked 25-decimal grid.

    The exact correction ``x - W G`` is generally off-grid.  Rather than
    always taking the nearest grid point (which stalled at |G| ~ 1.6e-24
    because the 25-decimal grid itself limits the attainable residual), the
    step chooses among the floor/ceil grid points of the eight coordinates
    the one minimizing the linearized residual ``|G + DG (x_c - x)|_inf``.
    This is a deterministic grid-rounding rule; no threshold or constant is
    changed.
    """
    n = N_SEC
    gvec = arb_mat([[G[i]] for i in range(n)])
    delta = wmat * gvec
    lo: list[int] = []
    hi: list[int] = []
    for i in range(n):
        a, b = _grid_floor_ceil(_b(x[i]) - delta[i, 0])
        lo.append(a)
        hi.append(b)
    gmid = [G[i].mid() for i in range(n)]
    dmid = [[dg[i][j].mid() for j in range(n)] for i in range(n)]
    best: tuple[arb, tuple[int, ...]] | None = None
    for mask in range(1 << n):
        ks = tuple(hi[i] if (mask >> i) & 1 else lo[i] for i in range(n))
        worst = ZERO
        for i in range(n):
            acc = gmid[i]
            for j in range(n):
                acc = acc + dmid[i][j] * (_b(Fraction(ks[j], ROUND_DEC)) - _b(x[j]))
            val = acc.abs_upper()
            if bool(val > worst):
                worst = val
        key = (worst, ks)
        if best is None:
            best = key
        elif bool(worst < best[0]):
            best = key
        elif not bool(worst > best[0]) and ks < best[1]:
            best = key
    assert best is not None
    return [Fraction(k, ROUND_DEC) for k in best[1]]


def _newton() -> dict:
    """Certified Newton on G with the locked rules (prereg section 3 K3)."""
    x = list(SEED_R2)
    c0 = [ZERO] * N_SEC
    history = []
    increases = 0
    prev = None
    for it in range(1, NEWTON_MAX + 1):
        ev = _evaluate(x, c0, True, False)
        if not ev["ok"]:
            return {
                "ok": False,
                "history": history,
                "iterations": it - 1,
                "error": "iteration %d: %s" % (it, ev.get("error")),
                "x_fracs": x,
            }
        finf = ev["f_inf"]
        entry = {"iter": it, "f_inf": str(finf)}
        if prev is not None:
            rose = bool(finf > prev)
            entry["rose"] = rose
            increases = increases + 1 if rose else 0
            if increases >= 2:
                history.append(entry)
                return {
                    "ok": False,
                    "history": history,
                    "iterations": it,
                    "error": (
                        "monotone rule: |G|_inf rose at iterations %d and %d"
                        % (it - 1, it)
                    ),
                    "x_fracs": x,
                }
        history.append(entry)
        prev = finf
        if bool(finf <= _b(NEWTON_TARGET)):
            return {
                "ok": True,
                "history": history,
                "iterations": it,
                "error": None,
                "x_fracs": list(x),
                "eval": ev,
            }
        wmat = _inverse_mid(ev["DG"])
        if wmat is None:
            history.append({"iter": it, "f_inf": str(finf), "singular_dg": True})
            return {
                "ok": False,
                "history": history,
                "iterations": it,
                "error": "iteration %d: singular Gauss derivative DG" % it,
                "x_fracs": x,
                "dg_singular": True,
            }
        prev_x = list(x)
        x = _newton_step(x, wmat, ev["G"], ev["DG"])
        if x == prev_x:
            history.append({"iter": it, "f_inf": str(finf), "grid_stagnation": True})
            return {
                "ok": False,
                "history": history,
                "iterations": it,
                "error": "grid stagnation at iteration %d" % it,
                "x_fracs": x,
            }
    return {
        "ok": False,
        "history": history,
        "iterations": NEWTON_MAX,
        "error": "no convergence within %d iterations" % NEWTON_MAX,
        "x_fracs": x,
    }


# --- K3: Krawczyk inclusion ------------------------------------------------


def _krawczyk(ev_point: dict, dg_box: list[list[arb]]) -> dict:
    """K3 box test: K(B) subset box(xh, K_MARGIN*r_B), plus contraction.

        K(B) = xh - W G(xh) + (I - W DG(B)) (B - xh),

    W the rigorous inverse of the midpoint matrix of the final point-run
    DG(xh); G(xh) and DG(xh) from that run; DG(B) the derivative enclosure
    over the signed-sweep box run with R_B radii on the eight coordinates.
    """
    n = N_SEC
    wmat = _inverse_mid(ev_point["DG"])
    if wmat is None:
        return {
            "w_max": None,
            "kappa_inf": None,
            "budget": str(_b(K_MARGIN * R_B)),
            "rows": [],
            "included": False,
            "kappa_ok": False,
            "passed": False,
            "error": "singular midpoint DG(xh)",
        }
    G = ev_point["G"]
    wlist = [[wmat[i, j] for j in range(n)] for i in range(n)]
    budget = _b(K_MARGIN * R_B)
    r_b = _b(R_B)
    w_max = ZERO
    for i in range(n):
        for j in range(n):
            if bool(wlist[i][j].abs_upper() > w_max):
                w_max = wlist[i][j].abs_upper()
    resid = [[arb(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            acc = arb(0)
            for kk in range(n):
                acc = acc + wlist[i][kk] * dg_box[kk][j]
            resid[i][j] = (ONE if i == j else ZERO) - acc
    kappa = ZERO
    for i in range(n):
        row = ZERO
        for j in range(n):
            row = row + resid[i][j].abs_upper()
        if bool(row > kappa):
            kappa = row
    rows = []
    included = True
    for i in range(n):
        wfi = arb(0)
        for j in range(n):
            wfi = wfi + wlist[i][j] * G[j]
        rad = arb(0)
        for j in range(n):
            rad = rad + resid[i][j].abs_upper() * r_b
        total = wfi.abs_upper() + rad
        ok = bool(total <= budget)
        included = included and ok
        rows.append(
            {
                "index": i,
                "wf": str(wfi),
                "box_radius": str(rad),
                "total": str(total),
                "ok": ok,
            }
        )
    kappa_ok = bool(kappa <= _b(KAPPA_MAX))
    return {
        "w_max": str(w_max),
        "kappa_inf": str(kappa),
        "budget": str(budget),
        "rows": rows,
        "included": included,
        "kappa_ok": kappa_ok,
        "passed": bool(included and kappa_ok),
        "error": None,
    }


# --- K4: Gauss matrix determinant / conditioning --------------------------


def _k4_check(ev_point: dict, ev_box: dict) -> dict:
    """K4: interval determinant and condition estimate of DG (no spectrum)."""
    n = N_SEC
    dg_point = ev_point["DG"]
    det = _det_interval(dg_point)
    if bool(det.lower() > ZERO):
        det_abs_lower = det.lower()
    elif bool(det.upper() < ZERO):
        det_abs_lower = -det.upper()
    else:
        det_abs_lower = ZERO
    contains_zero = t1._contains(det, 0)
    wmat = _inverse_mid(dg_point)
    if wmat is None:
        return {
            "det": str(det),
            "det_abs_lower": str(det_abs_lower),
            "det_contains_zero": contains_zero,
            "cond_inf": None,
            "det_ok": False,
            "cond_ok": False,
            "passed": False,
        }
    w_inf = ZERO
    for i in range(n):
        row = ZERO
        for j in range(n):
            row = row + wmat[i, j].abs_upper()
        if bool(row > w_inf):
            w_inf = row
    dg_inf = ZERO
    for i in range(n):
        row = _row_abs(ev_box["DG"], i, n)
        if bool(row > dg_inf):
            dg_inf = row
    cond = w_inf * dg_inf
    det_ok = bool((not contains_zero) and det_abs_lower >= _b(GAUSS_DET_MIN))
    cond_ok = bool(cond <= _b(GAUSS_COND_MAX))
    return {
        "det": str(det),
        "det_abs_lower": str(det_abs_lower),
        "det_contains_zero": contains_zero,
        "cond_inf": str(cond),
        "det_ok": det_ok,
        "cond_ok": cond_ok,
        "passed": bool(det_ok and cond_ok),
    }


# --- K5: choreography descriptor ------------------------------------------


def _k5_check(ev_box: dict) -> dict:
    """K5: phase-independent figure-eight choreography defects.

    Six relations at the exact grid gaps T0/3 = 512 h and 2T0/3 = 1024 h
    are bounded over the certified box tube; no absolute window is used.
    """
    ps = ev_box["ps"]
    series = _c_series_tight(ps)
    mids = ps["mids"]
    pairs = (
        ("q1(T/3)=q2(0)", 0, 2, 512, 0),
        ("q2(T/3)=q3(0)", 2, 4, 512, 0),
        ("q3(T/3)=q1(0)", 4, 0, 512, 0),
        ("q1(2T/3)=q3(0)", 0, 4, 1024, 0),
        ("q2(2T/3)=q1(0)", 2, 0, 1024, 0),
        ("q3(2T/3)=q2(0)", 4, 2, 1024, 0),
    )
    rows = []
    defect = ZERO
    for label, a, b, ka, kb in pairs:
        dx = (
            (mids[ka][a] - mids[kb][b]).abs_upper()
            + series[ka][a]
            + series[kb][b]
        )
        dy = (
            (mids[ka][a + 1] - mids[kb][b + 1]).abs_upper()
            + series[ka][a + 1]
            + series[kb][b + 1]
        )
        d = (dx * dx + dy * dy).sqrt()
        if bool(d > defect):
            defect = d
        rows.append({"relation": label, "defect": str(d)})
    passed = bool(defect <= _b(CHOREO_TOL))
    return {"relations": rows, "defect": str(defect), "passed": passed}


# --- collision note (internal, not a pass criterion) ----------------------


def _collision_note(ps: dict) -> dict:
    """Internal lower bound for body-pair distances along the run."""
    max_speed = ZERO
    for st in ps["mids"]:
        for i in range(6, N_STATE):
            v = st[i].abs_upper()
            if bool(v > max_speed):
                max_speed = v
    series = _c_series_tight(ps)
    cmax = ZERO
    for k in range(ps["steps_done"] + 1):
        c_k = _max_arb(series[k])
        if bool(c_k > cmax):
            cmax = c_k
    motion = _b(Fraction(2, 1)) * max_speed * _b(H_GRID)
    min_d2 = None
    for st in ps["mids"]:
        for (a, bp) in ((0, 2), (0, 4), (2, 4)):
            dx = st[a] - st[bp]
            dy = st[a + 1] - st[bp + 1]
            d2 = (dx * dx + dy * dy).lower()
            if min_d2 is None or bool(d2 < min_d2):
                min_d2 = d2
    d_lb = min_d2.sqrt() - motion - _b(Fraction(2, 1)) * cmax
    return {
        "min_pair_distance_lower": str(d_lb),
        "half_step_motion": str(motion),
        "radius_max": str(cmax),
        "strictly_above_half": bool(d_lb.lower() > _b(Fraction(1, 2))),
    }


# --- K1 / K2 --------------------------------------------------------------


def _ast_hits(source: str) -> list[str]:
    """K1 scan: frozen T1 name/import scan plus float literals."""
    hits = t1.ast_scan(source)
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and type(node.value).__name__ == "float":
            hits.append("literal:float:%d" % node.lineno)
    return hits


def _k1_check() -> dict:
    """K1: AST scan, prereg hash, and frozen-module hash pins."""
    source = Path(__file__).read_text(encoding="utf-8")
    hits = _ast_hits(source)
    prereg_sha_ok = t1.sha256lf(PREREG_PATH) == PREREG_SHA
    t1_sha_ok = t1.sha256lf(Path(t1.__file__)) == T1_MODULE_SHA
    t1b_sha_ok = t1.sha256lf(Path(t1b.__file__)) == T1B_MODULE_SHA
    passed = bool(hits == [] and prereg_sha_ok and t1_sha_ok and t1b_sha_ok)
    return {
        "ast_scan_hits": hits,
        "ast_scan_passed": hits == [],
        "prereg_sha_ok": prereg_sha_ok,
        "t1_sha_ok": t1_sha_ok,
        "t1b_sha_ok": t1b_sha_ok,
        "passed": passed,
    }


def _k2_check(ev_box: dict) -> dict:
    """K2: validated state tube at the block checkpoints."""
    if not ev_box.get("ok", False):
        return {
            "checkpoints": [],
            "width_max": None,
            "widths_ok": False,
            "passed": False,
            "error": ev_box.get("error"),
        }
    ps = ev_box["ps"]
    rows = []
    max_width = ZERO
    widths_ok = True
    for upto in sorted(ps["checkpoints"]):
        ck = ps["checkpoints"][upto]
        width = ck["width"]
        ok = bool(width <= _b(TUBE_CAP))
        widths_ok = widths_ok and ok
        if bool(width > max_width):
            max_width = width
        rows.append(
            {
                "step": upto,
                "time": str(_b(H_GRID * upto)),
                "max_radius": str(ck["max_radius"]),
                "width": str(width),
                "width_ok": ok,
                "slack": str(ck["slack"]),
            }
        )
    passed = bool(widths_ok and ps["error"] is None)
    return {
        "checkpoints": rows,
        "width_max": str(max_width),
        "widths_ok": widths_ok,
        "passed": passed,
        "error": ps["error"],
    }


# --- campaign -------------------------------------------------------------


def run_campaign() -> dict:
    """Full certified T2-r2 campaign (K1-K5); deterministic; writes nothing."""
    with flint.ctx.workprec(PREC):
        k1 = _k1_check()
        newton = _newton()
        k3 = {
            "newton": newton["history"],
            "iterations": newton["iterations"],
            "newton_ok": newton["ok"],
            "error": newton.get("error"),
            "dg_singular": newton.get("dg_singular", False),
            "krawczyk": None,
        }
        k2 = None
        k4 = None
        k5 = None
        collision = None
        if newton["ok"]:
            x_hat = newton["x_fracs"]
            ev_point = newton["eval"]
            c8_box = [_b(R_B)] * N_SEC
            ev_box = _evaluate(x_hat, c8_box, True, True)
            k2 = _k2_check(ev_box)
            k3["x_hat"] = [str(v) for v in x_hat]
            k3["f_inf_final"] = str(ev_point["f_inf"])
            if ev_box["ok"]:
                k4 = _k4_check(ev_point, ev_box)
                k5 = _k5_check(ev_box)
                collision = _collision_note(ev_box["ps"])
                kraw = _krawczyk(ev_point, ev_box["DG"])
                k3["krawczyk"] = kraw
                k3["box_error"] = None
                k3["passed"] = kraw["passed"]
            else:
                k3["box_error"] = ev_box.get("error")
                k3["passed"] = False
        else:
            k3["x_hat"] = None
            k3["f_inf_final"] = None
            k3["passed"] = False
        k1_pass = bool(k1["passed"])
        k2_pass = bool(k2 is not None and k2["passed"])
        k3_pass = bool(k3["passed"])
        k4_pass = bool(k4 is not None and k4["passed"])
        k5_pass = bool(k5 is not None and k5["passed"])
        all_pass = k1_pass and k2_pass and k3_pass and k4_pass and k5_pass
        if all_pass:
            summary = "ALL PASS"
        elif k3_pass:
            summary = "INCONCLUSIVE"
        else:
            summary = "FAILED"
        checks = {"K1": k1, "K2": k2, "K3": k3, "K4": k4, "K5": k5}
        return {
            "schema": SCHEMA,
            "summary": summary,
            "all_pass": all_pass,
            "precision": PREC,
            "order": ORDER,
            "python_flint": flint.__version__,
            "prereg_sha256lf": t1.sha256lf(PREREG_PATH),
            "t1_module_sha256lf": t1.sha256lf(Path(t1.__file__)),
            "t1b_module_sha256lf": t1.sha256lf(Path(t1b.__file__)),
            "config": {
                "section": "{q1y = 1/5, I_xy = 0}",
                "T0": str(T0),
                "C": str(C),
                "h": str(H_GRID),
                "steps": H_STEPS,
                "block_steps": BLOCK_STEPS,
                "seed": [str(v) for v in SEED_R2],
                "rows_keep": list(KEEP),
                "rows_drop": [2, 7],
                "r_B": str(R_B),
                "newton_target": str(NEWTON_TARGET),
                "remainder_factor": REMAINDER_FACTOR,
                "sweep_signed": SWEEP_SIGNED,
            },
            "thresholds": {
                "K2_tube_width": str(TUBE_CAP),
                "K3_newton_max_iter": NEWTON_MAX,
                "K3_newton_target": str(NEWTON_TARGET),
                "K3_krawczyk_margin": str(K_MARGIN),
                "K3_kappa_max": str(KAPPA_MAX),
                "K4_det_min": str(GAUSS_DET_MIN),
                "K4_cond_max": str(GAUSS_COND_MAX),
                "K5_choreo": str(CHOREO_TOL),
                "K6_mutations": [
                    "M1 remainder_factor 1e70 -> K2 fail-fast",
                    "M2 T0 + 1/10 -> K3 fail",
                    "M3 receipt byte tamper -> guard hash mismatch",
                    "M4 float injection -> AST scan fail",
                    "M5 sweep_signed False -> K2/K3 fail",
                ],
            },
            "collision_guard": collision,
            "checks": checks,
        }


def main() -> None:
    payload = run_campaign()
    RECEIPT_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    printable = {
        "summary": payload["summary"],
        "all_pass": payload["all_pass"],
        "prereg_sha256lf": payload["prereg_sha256lf"],
        "receipt": str(RECEIPT_PATH),
    }
    print(json.dumps(printable, indent=2))


if __name__ == "__main__":
    main()
