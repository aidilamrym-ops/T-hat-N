"""T2: validated figure-eight periodic orbit for the planar three-body problem.

Scope and pass criteria are locked in
``reports/PREREG_FIGURE_EIGHT_THREE_BODY_2026-10-22.md`` (sections 1-9,
amendments 1-2).  This module certifies, for the exact-rational IVP of
preregistration section 2d, the existence and LOCAL uniqueness of a
periodic orbit near the disclosed seed via a Krawczyk test on the
two-return Poincare map of the codimension-one section

    Sigma = { q3y = 0, orientation v3y < 0 },

plus a validated state tube (K2), a monodromy-matrix enclosure (K4,
artifact for track T2b -- NO spectrum claims here), and a validated shape
descriptor (K5).

Reuse is import-only from the frozen modules ``msaf.ode_validated`` (T1)
and ``msaf.ode_validated_block`` (T1b): the validated Taylor step, the
continuous signed block certificate, and the ball/AST helpers are theirs;
the section, crossing, Newton-Krawczyk, and criterion logic are new here.
No float is used in the certified path (AST-scanned by the guard).  The
stability spectrum of the multipliers is explicitly OUT OF SCOPE (T2b).
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
PREREG_PATH = ROOT / "reports" / "PREREG_FIGURE_EIGHT_THREE_BODY_2026-10-22.md"
RECEIPT_PATH = ROOT / "reports" / "figure_eight_three_body_2026-10-22.json"

PREC = t1.PREC
ORDER = t1.ORDER
SCHEMA = "msaf.figure_eight.v1"
T1_MODULE_SHA = "c1d9b5d60036a5f0772f7e3f1b8c78969efaa7146a713c762531ddce346251b9"
T1B_MODULE_SHA = "42d196a51c5ae45e3b87b8c1e36319abfeb93df776b3c2317e812f7c2c0b5b97"
PREREG_SHA = "6cc2ef2a613ae9ed5f9d1917624c57e3b1a0cbe915d2a0052dcf8a7f99f27ddf"

# --- locked data (prereg 2d, 3.3, 3.4, 9.2; all exact rationals) ----------

TILDE = Fraction(632600304, 10**8)          # T~ = 6.326003040
H_STEPS = 1536                              # h = T~/1536
H_GRID = TILDE / H_STEPS                    # 0.0041184915625 exactly
N_STEPS = 1554                              # H = N*h >= 6.4 > w2 upper
W1C = Fraction(3163014927, 10**9)           # w1 centre 3.163014927
W2C = Fraction(6326003040, 10**9)           # w2 centre 6.326003040
W_HALF = Fraction(1, 100)                   # window half-width 0.01

SEED = (
    Fraction(881825885905, 10**12),
    Fraction(471573247799, 10**12),
    Fraction(-881817147851, 10**12),
    Fraction(-471630773362, 10**12),
    Fraction(-48006190, 10**12),
    Fraction(-557287392981, 10**12),
    Fraction(306081711672, 10**12),
    Fraction(-557356449974, 10**12),
    Fraction(306044779690, 10**12),
    Fraction(1114643842954, 10**12),
    Fraction(-612126491362, 10**12),
)

R_B = Fraction(2, 10**13)                   # Krawczyk box radius (amend 1)
K_MARGIN = Fraction(9, 10)                  # K(B) subset box(xh, 0.9*r_B)
NEWTON_MAX = 6
NEWTON_TARGET = Fraction(1, 10**22)         # |F|_inf stopping threshold
ROUND_DEC = 10**25                          # Newton iterates: 25 decimals

TUBE_CAP = Fraction(1, 10**22)              # K2 state-tube cap
CROSS_CAP = Fraction(1, 10**19)             # K2 crossing-time width cap
MONO_CAP = Fraction(1, 10**16)              # K4 monodromy entry width cap
CHOREO_TOL = Fraction(1, 10**6)             # K5 choreography defect
PERIOD_TOL = Fraction(1, 10**9)             # K5 |T~ - (t1+t2)(xh)|

REMAINDER_FACTOR = 1                        # mutation M1 sets 1e70
SWEEP_SIGNED = True                         # mutation M5 sets False
BLOCK_STEPS = 96                            # checkpoints at 96k (768, 1536
                                            # land inside w1, w2)
JTAU_BOUND = 2                              # coarse |J_tau|_inf bound (9.4)
BISECT_MAX = 200                            # rational bisection guard

# K5 locked descriptor data (prereg 4 K5)
PROBE1 = Fraction(2108735283, 10**9)        # up-crossing probe 2.108735283
PROBE3 = Fraction(4217376381, 10**9)        # up-crossing probe 4.217376381
PROBE_HALF = Fraction(1, 10**6)
V3Y_UP = Fraction(1, 4)
Q3X_C1 = (Fraction(-100001, 10**5), Fraction(-99999, 10**5))
Q3X_C3 = (Fraction(99999, 10**5), Fraction(100001, 10**5))
Q3X_W1 = (Fraction(-6, 10**5), Fraction(-3, 10**5))
Q3X_W2 = (Fraction(-1, 10**6), Fraction(1, 10**6))

N_STATE = 12
N_SEC = 11
IDX_Q3Y = 5
IDX_V3Y = 11
IDX_Q3X = 4


# --- small helpers --------------------------------------------------------


def _b(fr: Fraction) -> arb:
    """Exact rational as a tight arb ball (frozen T1 primitive)."""
    return t1._ball(fr)


ZERO = arb(0)


def _embed(x: list[arb]) -> list[arb]:
    """Section coordinates -> 12-dim state with q3y = 0 exactly."""
    return [x[0], x[1], x[2], x[3], x[4], ZERO] + [x[5 + i] for i in range(6)]


def _project(y: list[arb]) -> list[arb]:
    """12-dim state -> section coordinates (drops q3y)."""
    return [y[0], y[1], y[2], y[3], y[4]] + [y[6 + i] for i in range(6)]


def _round25(x: arb) -> Fraction:
    """Round a ball to its 25-decimal rational grid point (exact result).

    The scaled midpoint is an exact ball around an integer far from any
    rounding boundary at 256 bits; the decimal string of its lower part is
    parsed without floats.
    """
    scaled = (x.mid() * _b(ROUND_DEC)).lower()
    text = str(scaled).lstrip("[ ")
    token = text.split("+/-")[0].strip()
    whole = token.split(".")[0]
    return Fraction(int(whole), ROUND_DEC)


def _max_arb(values: list[arb]) -> arb:
    return t1b._max_arb(values)


def _row_abs(mat: list[list[arb]], i: int, n: int) -> arb:
    acc = arb(0)
    for j in range(n):
        acc = acc + mat[i][j].abs_upper()
    return acc


# --- certificate (signed = frozen T1b; reset = mutation M5 path) ----------


def _certificate(jacs, rems, quads, c_in, upto, lo):
    """Checkpoint certificate plus slack weights.

    Honest path (``SWEEP_SIGNED``): the frozen T1b continuous signed sweep.
    Mutation path: the same sweep with the sensitivity product reset to its
    entrywise absolute value at every block boundary (prereg 9.3, M5) --
    a wider but still sound enclosure, used only to demonstrate that the
    K3 gate discriminates.
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
    """Integrate [m0 +/- c0] over N_STEPS with signed-sweep certificates.

    ``m0`` must be a point (midpoints only); ``c0`` carries the input box
    radii.  Blocks of BLOCK_STEPS insert the locked quadratic slack and
    compute a certificate at every block end (K2 checkpoints).  When
    ``gate`` is true (point runs of the honest configuration) the run
    fail-fasts as soon as a checkpoint radius exceeds TUBE_CAP (prereg
    4 K2, 9.3 M1).
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
    for k in range(N_STEPS):
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
        # sound forward running bound, sizes the next Picard boxes only
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
        if upto % BLOCK_STEPS == 0 or upto == N_STEPS:
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
                "slack_ok": bool(slack <= t1._tol("1e-30")),
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


# --- tube at an arbitrary time inside a step ------------------------------


def _tube_at(ps: dict, k: int, tau: Fraction, coarse: bool) -> list[arb]:
    """Enclosure of the state at t = k*h + tau (tau in [0, h]).

    Sound extension: certificate radii at the last block checkpoint <= k,
    forward |J| extension through the steps up to k (sign loss bounded by
    the few steps involved), then the step polynomial at ``tau`` with the
    mean-value radius over the step input box.  ``coarse`` replaces the
    interval partial Jacobian by the locked bound |J_tau|_inf <= JTAU_BOUND
    (prereg 9.4; valid because certified pair distances stay >= 1/2 over
    the horizon); tight mode differentiates the step polynomial exactly as
    the frozen ``forward_step`` does.
    """
    n = N_STATE
    c = _c_at(ps, k)
    pc = ps["pcs"].get(k)
    if pc is None:
        pc = t1.coeffs_three_body(ps["mids"][k], ORDER)
        ps["pcs"][k] = pc
    taub = _b(tau)
    mid = [t1._horner(comp, taub) for comp in pc]
    remk = ps["rems"][k]
    quadk = ps["quads"][k]
    if coarse:
        cmax = _max_arb(c)
        rad = [_b(JTAU_BOUND) * cmax + remk[i] + quadk for i in range(n)]
    else:
        xbox = [ps["mids"][k][i] + arb(0, c[i]) for i in range(n)]
        dual = t1._dual_coeffs(t1.coeffs_three_body, xbox, ORDER)
        rad = []
        for i in range(n):
            acc = arb(0)
            for j in range(n):
                jt = t1._horner(
                    [dual[i][ord_k].g[j] for ord_k in range(ORDER + 1)], taub
                )
                acc = acc + jt.abs_upper() * c[j]
            rad.append(acc + remk[i] + quadk)
    return [mid[i] + arb(0, rad[i].abs_upper()) for i in range(n)]


def _tau_range_enclosure(
    ps: dict, k: int, tau_lo: Fraction, tau_hi: Fraction
) -> tuple[arb, arb]:
    """(q3y, v3y) enclosures over the whole tau sub-range of step k."""
    taum = (tau_lo + tau_hi) / 2
    taur = (tau_hi - tau_lo) / 2
    taub = _b(taum) + arb(0, _b(taur))
    pc = ps["pcs"].get(k)
    if pc is None:
        pc = t1.coeffs_three_body(ps["mids"][k], ORDER)
        ps["pcs"][k] = pc
    g = t1._horner(pc[IDX_Q3Y], taub)
    v = t1._horner(pc[IDX_V3Y], taub)
    # coarse input-uncertainty radius on top (sound, sign decisions below
    # have huge margins relative to it)
    cmax = _max_arb(_c_at(ps, k))
    w = arb(0, (_b(JTAU_BOUND) * cmax + ps["rems"][k][IDX_Q3Y]).abs_upper())
    wv = arb(0, (_b(JTAU_BOUND) * cmax + ps["rems"][k][IDX_V3Y]).abs_upper())
    return g + w, v + wv


def _v3y_window_ok(
    ps: dict, ka: int, ta: Fraction, kb: int, tb: Fraction, down: bool
) -> bool:
    """Certified monotonicity of v3y over the window (crossing gate).

    ``down``: the q3y crossing is downwards, the gate is v3y <= -1/2 over
    the whole window; up-crossings (K5 probes) require v3y >= +1/4.
    """
    limit = _b(Fraction(-1, 2)) if down else _b(V3Y_UP)
    kk = ka
    while kk <= kb:
        lo = ta if kk == ka else Fraction(0)
        hi = tb if kk == kb else H_GRID
        _g, v = _tau_range_enclosure(ps, kk, lo, hi)
        if down:
            if not bool(v.upper() <= limit):
                return False
        else:
            if not bool(v.lower() >= limit):
                return False
        kk = kk + 1
    return True


# --- certified crossing search -------------------------------------------


def _find_crossing(
    ps: dict, w_lo: Fraction, w_hi: Fraction, down: bool, coarse: bool
) -> dict:
    """Unique q3y crossing inside [w_lo, w_hi] (prereg 3.3, amendment 2).

    Gate: strict sign pattern at the window ends (down-crossing:
    q3y(w_lo) > 0 > q3y(w_hi); up-crossing: the reverse) and certified
    monotonicity of v3y (down: v3y <= -1/2; up: v3y >= +1/4) over the
    whole window.  Then rational bisection on the certified step
    polynomials down to the tube floor; the bracket (a, b) is a rigorous
    enclosure of the unique crossing time.  ``coarse`` selects the locked
    coarse |J_tau| bound in the tube evaluations (prereg 9.4).
    """
    ka = int(w_lo / H_GRID)
    kb = int(w_hi / H_GRID)
    ta = w_lo - ka * H_GRID
    tb = w_hi - kb * H_GRID
    g_lo = _tube_at(ps, ka, ta, coarse)[IDX_Q3Y]
    g_hi = _tube_at(ps, kb, tb, coarse)[IDX_Q3Y]
    if down:
        sign_ok = bool(g_lo.lower() > ZERO) and bool(g_hi.upper() < ZERO)
    else:
        sign_ok = bool(g_lo.upper() < ZERO) and bool(g_hi.lower() > ZERO)
    mono_ok = _v3y_window_ok(ps, ka, ta, kb, tb, down)
    a = w_lo
    b = w_hi
    if sign_ok:
        for _ in range(BISECT_MAX):
            if b - a <= Fraction(1, 10**30):
                break
            t_m = (a + b) / 2
            k_m = int(t_m / H_GRID)
            tau_m = t_m - k_m * H_GRID
            g = _tube_at(ps, k_m, tau_m, coarse)[IDX_Q3Y]
            if down:
                if bool(g.upper() < ZERO):
                    b = t_m
                elif bool(g.lower() > ZERO):
                    a = t_m
                else:
                    break
            else:
                if bool(g.lower() > ZERO):
                    b = t_m
                elif bool(g.upper() < ZERO):
                    a = t_m
                else:
                    break
    return {
        "ok": bool(sign_ok and mono_ok),
        "sign_ok": sign_ok,
        "mono_ok": mono_ok,
        "g_lo": g_lo,
        "g_hi": g_hi,
        "bracket": (a, b),
        "width": b - a,
        "window": (w_lo, w_hi),
    }




# ---------------------------------------------------------------------------
# PART B: sensitivity, section derivative, Newton-Krawczyk, criteria
# ---------------------------------------------------------------------------

_SEC_IDX = (0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11)


# --- input-radius bookkeeping (checkpoint certificate + extension) --------


def _c_series_tight(ps: dict) -> list:
    """Input-radius enclosure at every grid step of the run.

    At each block checkpoint the signed-sweep certificate radius replaces
    the running bound; through the partial block the bound is forward
    extended with the one-step |J| recurrence.  Computed once per run and
    cached; every mid-step tube evaluation reads the radius from here.
    """
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


def _c_at(ps: dict, k: int) -> list:
    """Input-radius enclosure at grid step k."""
    return _c_series_tight(ps)[k]


# --- hull / interval-time tube -------------------------------------------


def _hull(a: arb, b: arb) -> arb:
    """Smallest ball containing both a and b."""
    ma = a.mid()
    mb = b.mid()
    mid = (ma + mb) / 2
    rad = ((ma - mb).abs_upper() + a.rad().abs_upper() + b.rad().abs_upper()) / 2
    return mid + arb(0, rad.abs_upper())


def _tube_interval(
    ps: dict, k: int, tau_lo: Fraction, tau_hi: Fraction
) -> list[arb]:
    """State enclosure for every tau in [tau_lo, tau_hi] of step k.

    The step polynomial is evaluated over the whole tau interval at once
    (interval arithmetic), so no monotonicity of the trajectory is needed.
    The input-uncertainty radius uses the locked coarse bound
    |J_tau|_inf <= JTAU_BOUND (prereg 9.4).
    """
    n = N_STATE
    c = _c_at(ps, k)
    pc = ps["pcs"].get(k)
    if pc is None:
        pc = t1.coeffs_three_body(ps["mids"][k], ORDER)
        ps["pcs"][k] = pc
    tm = (tau_lo + tau_hi) / 2
    tr = (tau_hi - tau_lo) / 2
    taub = _b(tm) + arb(0, _b(tr))
    cmax = _max_arb(c)
    out = []
    for i in range(n):
        mid = t1._horner(pc[i], taub)
        rad = _b(JTAU_BOUND) * cmax + ps["rems"][k][i] + ps["quads"][k]
        out.append(mid + arb(0, rad.abs_upper()))
    return out


def _state_span(ps: dict, t_lo: Fraction, t_hi: Fraction) -> list[arb]:
    """State enclosure for every t in [t_lo, t_hi] (hull over the steps)."""
    k_lo = int(t_lo / H_GRID)
    k_hi = int(t_hi / H_GRID)
    if k_lo == k_hi:
        return _tube_interval(ps, k_lo, t_lo - k_lo * H_GRID, t_hi - k_lo * H_GRID)
    left = _tube_interval(ps, k_lo, t_lo - k_lo * H_GRID, H_GRID)
    right = _tube_interval(ps, k_hi, Fraction(0), t_hi - k_hi * H_GRID)
    return [_hull(left[i], right[i]) for i in range(N_STATE)]


# --- sensitivity product and section derivative ---------------------------


def _sproduct(ps: dict, upto: int):
    """Incremental sensitivity chain; chain[i] = J_{i-1}...J_0 (mid/rad).

    The one-step Jacobians are the certified mean-value boxes of the
    frozen ``forward_step``; the product is carried in midpoint-radius
    form with the frozen T1b multiplication (no sign reset here either).
    """
    n = N_STATE
    chain = ps.get("sprod")
    if chain is None:
        chain = [(t1b._identity(n), [[arb(0) for _ in range(n)] for _ in range(n)])]
        ps["sprod"] = chain
    while len(chain) <= upto:
        k = len(chain) - 1
        flat = ps["jacs"][k]
        jac = [[flat[i * n + j] for j in range(n)] for i in range(n)]
        m_k, r_k = t1b._mr_split(jac)
        p_m, p_r = t1b._mr_mul(chain[k][0], chain[k][1], m_k, r_k)
        chain.append((p_m, p_r))
    return chain[upto]


def _partial_jac(ps: dict, k: int, taub: arb) -> list[list[arb]]:
    """Interval Jacobian of the step-k Taylor map at tau (an arb interval).

    Same differentiation as the frozen ``forward_step`` dual recurrence,
    over the step input box ``[m_k +/- _c_at(ps, k)]``.
    """
    n = N_STATE
    c = _c_at(ps, k)
    xbox = [ps["mids"][k][i] + arb(0, c[i]) for i in range(n)]
    dual = t1._dual_coeffs(t1.coeffs_three_body, xbox, ORDER)
    return [
        [
            t1._horner([dual[i][o].g[j] for o in range(ORDER + 1)], taub)
            for j in range(n)
        ]
        for i in range(n)
    ]


def _S_at(ps: dict, k: int, tau_lo: Fraction, tau_hi: Fraction) -> list[list[arb]]:
    """d y(t)/d y(0) for every t in [k*h + tau_lo, k*h + tau_hi]."""
    n = N_STATE
    tm = (tau_lo + tau_hi) / 2
    tr = (tau_hi - tau_lo) / 2
    taub = _b(tm) + arb(0, _b(tr))
    jtau = _partial_jac(ps, k, taub)
    p_m, p_r = _sproduct(ps, k)
    out = []
    for i in range(n):
        row = []
        for j in range(n):
            acc = arb(0)
            for kk in range(n):
                acc = acc + jtau[i][kk] * (p_m[kk][j] + arb(0, p_r[kk][j]))
            row.append(acc)
        out.append(row)
    return out


def _S_span(ps: dict, t_lo: Fraction, t_hi: Fraction) -> list[list[arb]]:
    """d y(t)/d y(0) enclosure for every t in [t_lo, t_hi] (hull by step)."""
    k_lo = int(t_lo / H_GRID)
    k_hi = int(t_hi / H_GRID)
    if k_lo == k_hi:
        return _S_at(ps, k_lo, t_lo - k_lo * H_GRID, t_hi - k_lo * H_GRID)
    left = _S_at(ps, k_lo, t_lo - k_lo * H_GRID, H_GRID)
    right = _S_at(ps, k_hi, Fraction(0), t_hi - k_hi * H_GRID)
    return [
        [_hull(left[i][j], right[i][j]) for j in range(N_STATE)]
        for i in range(N_STATE)
    ]


def _df_section(S12: list, f: list, f5: arb) -> list[list[arb]]:
    """Section derivative of the two-return map (prereg 3.6, 9.4).

        dF/dx = Pi[ S E - f (row5(S E))/f5 ] - I,

    with E the 11->12 embedding (q3y row zero), Pi the 12->11 projection,
    row5(S E) the section gradient composed with the flow sensitivity
    (d q3y/d t at the crossing) and f5 = v3y < 0 the orientation gate of
    the section.  All entries are interval balls.
    """
    n = N_SEC
    row5 = [S12[5][c] for c in _SEC_IDX]
    df = []
    for i in range(n):
        row = []
        fi = f[_SEC_IDX[i]]
        for j in range(n):
            entry = S12[_SEC_IDX[i]][_SEC_IDX[j]] - fi * (row5[j] / f5)
            if i == j:
                entry = entry - arb(1)
            row.append(entry)
        df.append(row)
    return df


# --- collision guard (internal note, prereg 9.4) --------------------------


def _collision_guard(ps: dict) -> dict:
    """Internal soundness note for the coarse |J_tau| bound (prereg 9.4).

    Not a pass criterion.  Records a lower bound for every body-pair
    distance along the run: the minimum squared distance of the midpoint
    trajectory over the grid, square-rooted, minus the half-step motion
    bound 2*v_max*h and twice the tube radius.  A certified pair distance
    >= 1/2 at all times justifies |J_tau|_inf <= JTAU_BOUND in the
    interval-time tube evaluations.
    """
    n = N_STATE
    max_speed = ZERO
    for st in ps["mids"]:
        for i in range(6, n):
            v = st[i].abs_upper()
            if bool(v > max_speed):
                max_speed = v
    series = _c_series_tight(ps)
    cmax = ZERO
    for k in range(ps["steps_done"] + 1):
        c_k = _max_arb(series[k])
        if bool(c_k > cmax):
            cmax = c_k
    motion = 2 * max_speed * _b(H_GRID)
    min_d2 = None
    for st in ps["mids"]:
        for (a, bpair) in ((0, 2), (0, 4), (2, 4)):
            dx = st[a] - st[bpair]
            dy = st[a + 1] - st[bpair + 1]
            d2 = (dx * dx + dy * dy).lower()
            if min_d2 is None or bool(d2 < min_d2):
                min_d2 = d2
    d_lb = min_d2.sqrt() - motion - 2 * cmax
    return {
        "min_pair_distance_lower": str(d_lb),
        "half_step_motion": str(motion),
        "radius_max": str(cmax),
        "strictly_above_half": bool(d_lb.lower() > _b(Fraction(1, 2))),
    }


# --- one certified run: crossings, F, section derivative -----------------


def _evaluate(
    x: list[Fraction], c0: list[arb], coarse_cross: bool, gate: bool
) -> dict:
    """Certified run from the section point ``x`` with input box ``c0``.

    Integrates [x +/- c0] over the horizon, certifies both window
    down-crossings, and returns the two-return map value
    ``F(x) = Pi(y(t2)) - x`` (t2 = absolute w2 crossing time) together
    with its section derivative dF/dx.  ``coarse_cross`` selects the
    locked coarse |J_tau| bound inside the crossing searches (point
    runs); the box run uses the tight partial Jacobian (prereg 9.4).
    """
    x_arb = [_b(v) for v in x]
    m0 = _embed(x_arb)
    ps = _forward_pass(m0, list(c0), gate)
    out = {"ps": ps}
    if ps["error"] is not None:
        out["ok"] = False
        out["error"] = ps["error"]
        return out
    cross1 = _find_crossing(ps, W1C - W_HALF, W1C + W_HALF, True, coarse_cross)
    cross2 = _find_crossing(ps, W2C - W_HALF, W2C + W_HALF, True, coarse_cross)
    out["cross1"] = cross1
    out["cross2"] = cross2
    if not (cross1["ok"] and cross2["ok"]):
        out["ok"] = False
        out["error"] = "window crossing gate failed (sign pattern or monotone v3y)"
        return out
    t2a, t2b = cross2["bracket"]
    ybox = _state_span(ps, t2a, t2b)
    S12 = _S_span(ps, t2a, t2b)
    f = t1.rhs_three_body(ybox)
    f5 = f[IDX_V3Y]
    if bool(f5.upper() >= ZERO):
        out["ok"] = False
        out["error"] = "orientation gate failed: v3y at the w2 crossing is not < 0"
        return out
    F = [ybox[_SEC_IDX[i]] - x_arb[i] for i in range(N_SEC)]
    out["y_cross2"] = ybox
    out["f"] = f
    out["f5"] = f5
    out["S"] = S12
    out["F"] = F
    out["f_inf"] = _max_arb([fi.abs_upper() for fi in F])
    out["DF"] = _df_section(S12, f, f5)
    out["ok"] = True
    return out


# --- certified Newton on F (prereg 3.6, amendment 1) ----------------------


def _inverse_mid(df: list[list[arb]]) -> arb_mat | None:
    """Midpoint inverse of an interval 11x11 matrix, or None if singular.

    A singular midpoint is an honest K3 failure, not a numerical accident:
    the locked two-return map is invariant under uniform x-translation, so
    its derivative has the exact null vector (1,0,1,0,1,0,0,0,0,0,0) in
    section coordinates.  The caller records the witness and returns FAILED.
    """
    n = N_SEC
    mat = arb_mat([[df[i][j].mid() for j in range(n)] for i in range(n)])
    try:
        return mat.inv()
    except ZeroDivisionError:
        return None


def _df_null_witness(df: list[list[arb]]) -> dict:
    """Rigorous witness that the section derivative has a translation null.

    ``F`` is invariant under x-translation, hence ``DF @ e = 0`` for
    ``e = (1,0,1,0,1,0,0,0,0,0,0)``.  The interval sums are evaluated in
    the certified enclosure; ``translation_null`` is true only when every
    component interval contains zero.
    """
    n = N_SEC
    e = [0] * n
    e[0] = e[2] = e[4] = 1
    rows = []
    residual = ZERO
    null_ok = True
    for i in range(n):
        acc = arb(0)
        for j in range(n):
            acc = acc + df[i][j] * e[j]
        rows.append(str(acc))
        null_ok = null_ok and bool(t1._contains(acc, 0))
        residual = max(residual, acc.abs_upper())
    return {
        "translation_null": bool(null_ok),
        "residual_inf": str(residual),
        "row_sums": rows,
    }


def _newton_step(x: list[Fraction], wmat: arb_mat, F: list[arb]) -> list[Fraction]:
    """One Newton iterate: x - W F(x), rounded to 25 exact decimals."""
    n = N_SEC
    fvec = arb_mat([[F[i]] for i in range(n)])
    delta = wmat * fvec
    return [_round25(_b(x[i]) - delta[i, 0]) for i in range(n)]


def _newton() -> dict:
    """Certified Newton on F with the locked rules (prereg 3.6, amend 1).

    At most NEWTON_MAX iterations; the |F|_inf upper bound must fall
    strictly at every iteration, two consecutive rises abort; iterates are
    rounded to the 25-decimal exact-rational grid; convergence is
    |F|_inf <= NEWTON_TARGET.  Honesty note: with a badly conditioned
    section derivative the loop may diverge -- that is an honest FAILED
    verdict, never a silent tolerance change.
    """
    x = list(SEED)
    c0 = [ZERO] * N_STATE
    history = []
    increases = 0
    prev = None
    for it in range(1, NEWTON_MAX + 1):
        ev = _evaluate(x, c0, True, True)
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
                        "monotone rule: |F|_inf rose at iterations %d and %d"
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
        wmat = _inverse_mid(ev["DF"])
        if wmat is None:
            witness = _df_null_witness(ev["DF"])
            history.append({"iter": it, "f_inf": str(finf), "singular_df": True})
            return {
                "ok": False,
                "history": history,
                "iterations": it,
                "error": (
                    "iteration %d: singular section derivative DF "
                    "(exact x-translation null direction); K3 cannot "
                    "certify a locally unique fixed point" % it
                ),
                "x_fracs": x,
                "df_singular": True,
                "null_witness": witness,
            }
        x = _newton_step(x, wmat, ev["F"])
    return {
        "ok": False,
        "history": history,
        "iterations": NEWTON_MAX,
        "error": "no convergence within %d iterations" % NEWTON_MAX,
        "x_fracs": x,
    }


# --- K4: monodromy enclosure and interval determinant --------------------


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


def _monodromy_check(S12: list) -> dict:
    """K4: entry widths of the 12x12 flow sensitivity at the w2 crossing.

    det dPhi/dy0 = exp(integral div f) = 1 EXACTLY (Newtonian acceleration
    has zero divergence), so the interval determinant must contain 1.
    NO eigenvalue, multiplier, or stability claim is made here (T2b).
    """
    n = N_STATE
    max_width = ZERO
    widths_ok = True
    for i in range(n):
        for j in range(n):
            w = t1._width(S12[i][j])
            if bool(w > max_width):
                max_width = w
            if not bool(w <= _b(MONO_CAP)):
                widths_ok = False
    det = _det_interval(S12)
    det_ok = t1._contains(det, 1)
    return {
        "entry_width_max": str(max_width),
        "widths_ok": widths_ok,
        "det": str(det),
        "det_contains_one": det_ok,
        "passed": bool(widths_ok and det_ok),
    }


# --- K3: Krawczyk inclusion on the two-return map ------------------------


def _krawczyk(ev_point: dict, df_box: list) -> dict:
    """K3 box test: K(B) subset box(xh, K_MARGIN*r_B) (prereg 3.6, amend 1).

        K(B) = xh - W F(xh) + (I - W DF(B)) (B - xh),

    W the rigorous inverse of the MIDPOINT matrix of the final point-run
    dF/dx, F(xh) and the point derivative from that run, DF(B) the
    derivative enclosure over the box from the signed-sweep box run
    (r_B radii on the eleven section coordinates, q3y exact).
    """
    n = N_SEC
    wmat = _inverse_mid(ev_point["DF"])
    F = ev_point["F"]
    wlist = [[wmat[i, j] for j in range(n)] for i in range(n)]
    budget = _b(K_MARGIN * R_B)
    r_b = _b(R_B)
    w_max = ZERO
    for i in range(n):
        for j in range(n):
            if bool(wlist[i][j].abs_upper() > w_max):
                w_max = wlist[i][j].abs_upper()
    rows = []
    included = True
    for i in range(n):
        wfi = arb(0)
        for j in range(n):
            wfi = wfi + wlist[i][j] * F[j]
        rad = arb(0)
        for j in range(n):
            acc = arb(0)
            for kk in range(n):
                acc = acc + wlist[i][kk] * df_box[kk][j]
            resid = (arb(1) if i == j else arb(0)) - acc
            rad = rad + resid.abs_upper() * r_b
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
    return {
        "w_max": str(w_max),
        "budget": str(budget),
        "rows": rows,
        "included": included,
    }


# --- K5: validated shape descriptor --------------------------------------


def _k5_checks(ps: dict, cross1: dict, cross2: dict) -> dict:
    """K5: the locked shape descriptor of the periodic orbit (prereg 4 K5).

    (a) unique up-crossings at the two locked probe windows with v3y
        >= +1/4 and the q3x ranges of choreography branches 2 and 3;
    (b) q3x ranges at the w1 and w2 down-crossings;
    (c) period difference |T~ - (t1 + t2)(xh)| = |T~ - t2_abs| <= 1e-9
        (t2 measured from the w1 crossing to the w2 crossing);
    (d) choreography defects q1(t + T/3) = q2(t) and q1(t + 2T/3) = q3(t)
        at the exact grid gaps 512h and 1024h, over every grid pair.
    """
    up1 = _find_crossing(ps, PROBE1 - PROBE_HALF, PROBE1 + PROBE_HALF, False, True)
    up3 = _find_crossing(ps, PROBE3 - PROBE_HALF, PROBE3 + PROBE_HALF, False, True)
    y_up1 = _state_span(ps, up1["bracket"][0], up1["bracket"][1]) if up1["ok"] else None
    y_up3 = _state_span(ps, up3["bracket"][0], up3["bracket"][1]) if up3["ok"] else None

    def _in_range(v: arb, bounds: tuple) -> bool:
        return bool(v.lower() >= _b(bounds[0]) and v.upper() <= _b(bounds[1]))

    up1_q3x_ok = y_up1 is not None and _in_range(y_up1[IDX_Q3X], Q3X_C1)
    up3_q3x_ok = y_up3 is not None and _in_range(y_up3[IDX_Q3X], Q3X_C3)
    y_w1 = _state_span(ps, cross1["bracket"][0], cross1["bracket"][1])
    y_w2 = _state_span(ps, cross2["bracket"][0], cross2["bracket"][1])
    w1_q3x_ok = _in_range(y_w1[IDX_Q3X], Q3X_W1)
    w2_q3x_ok = _in_range(y_w2[IDX_Q3X], Q3X_W2)
    t2a, t2b = cross2["bracket"]
    period_diff = max(abs(TILDE - t2a), abs(TILDE - t2b))
    period_ok = period_diff <= PERIOD_TOL
    series = _c_series_tight(ps)
    mids = ps["mids"]
    max512 = ZERO
    for k in range(0, N_STEPS - 512 + 1):
        c_a = series[k]
        c_b = series[k + 512]
        for (ia, ib) in ((0, 2), (1, 3)):
            d = (mids[k + 512][ia] - mids[k][ib]).abs_upper() + c_b[ia] + c_a[ib]
            if bool(d > max512):
                max512 = d
    max1024 = ZERO
    for k in range(0, N_STEPS - 1024 + 1):
        c_a = series[k]
        c_b = series[k + 1024]
        for (ia, ib) in ((0, 4), (1, 5)):
            d = (mids[k + 1024][ia] - mids[k][ib]).abs_upper() + c_b[ia] + c_a[ib]
            if bool(d > max1024):
                max1024 = d
    choreo_ok = bool(max512 <= _b(CHOREO_TOL) and max1024 <= _b(CHOREO_TOL))
    passed = bool(
        up1["ok"]
        and up3["ok"]
        and up1_q3x_ok
        and up3_q3x_ok
        and w1_q3x_ok
        and w2_q3x_ok
        and period_ok
        and choreo_ok
    )
    return {
        "up_crossings_ok": bool(up1["ok"] and up3["ok"]),
        "up1_q3x": str(y_up1[IDX_Q3X]) if y_up1 is not None else None,
        "up3_q3x": str(y_up3[IDX_Q3X]) if y_up3 is not None else None,
        "up1_q3x_ok": up1_q3x_ok,
        "up3_q3x_ok": up3_q3x_ok,
        "w1_q3x": str(y_w1[IDX_Q3X]),
        "w2_q3x": str(y_w2[IDX_Q3X]),
        "w1_q3x_ok": w1_q3x_ok,
        "w2_q3x_ok": w2_q3x_ok,
        "period_diff": str(_b(period_diff)),
        "period_ok": period_ok,
        "choreo_512_max": str(max512),
        "choreo_1024_max": str(max1024),
        "choreo_ok": choreo_ok,
        "passed": passed,
    }


# --- K1/K2 ----------------------------------------------------------------


def _ast_hits(source: str) -> list[str]:
    """K1 scan: frozen T1 name/import scan plus float literals.

    ``t1.ast_scan`` rejects ``float``/``math``/``numpy``/``scipy``/``random``
    and time names or imports; the prereg additionally forbids float
    *literals*, which the frozen scanner does not inspect.  Hits are
    returned as ``kind:detail:line`` strings in deterministic order.
    """
    hits = t1.ast_scan(source)
    tree = ast.parse(source)
    for node in ast.walk(tree):
        # The builtin name itself is forbidden by t1.ast_scan; classify by
        # type name so this scanner does not introduce a forbidden Name.
        if isinstance(node, ast.Constant) and type(node.value).__name__ == "float":
            hits.append("literal:float:%d" % node.lineno)
    return hits


def _k1_check() -> dict:
    """K1: AST scan of the certified path (no float literal or call)."""
    source = Path(__file__).read_text(encoding="utf-8")
    hits = _ast_hits(source)
    return {"ast_scan_hits": hits, "ast_scan_passed": hits == [], "passed": hits == []}


def _k2_check(ps: dict, cross1: dict, cross2: dict) -> dict:
    """K2: validated state tube and crossing gates (prereg 4 K2)."""
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
                "slack_ok": ck["slack_ok"],
            }
        )
    cw1 = cross1["bracket"][1] - cross1["bracket"][0]
    cw2 = cross2["bracket"][1] - cross2["bracket"][0]
    cross_ok = bool(_b(cw1) <= _b(CROSS_CAP) and _b(cw2) <= _b(CROSS_CAP))
    signs_ok = bool(cross1["sign_ok"] and cross2["sign_ok"])
    mono_ok = bool(cross1["mono_ok"] and cross2["mono_ok"])
    passed = bool(widths_ok and cross_ok and signs_ok and mono_ok)
    return {
        "checkpoints": rows,
        "width_max": str(max_width),
        "widths_ok": widths_ok,
        "crossing_width_w1": str(_b(cw1)),
        "crossing_width_w2": str(_b(cw2)),
        "crossing_widths_ok": cross_ok,
        "signs_ok": signs_ok,
        "mono_ok": mono_ok,
        "passed": passed,
    }


# --- campaign -------------------------------------------------------------


def run_campaign() -> dict:
    """Full certified T2 campaign (K1-K5); deterministic; writes nothing.

    Verdict per prereg section 5: ALL PASS only when K1..K5 all pass (K6
    determinism and mutations are enforced by the guard on top of this
    payload); FAILED when K1, K2, or K3 fail; INCONCLUSIVE when K3 passes
    but K4 or K5 fail.
    """
    with flint.ctx.workprec(PREC):
        k1 = _k1_check()
        newton = _newton()
        k3 = {
            "newton": newton["history"],
            "iterations": newton["iterations"],
            "newton_ok": newton["ok"],
            "error": newton.get("error"),
            "df_singular": newton.get("df_singular", False),
            "null_witness": newton.get("null_witness"),
            "krawczyk": None,
        }
        k2 = None
        k4 = None
        k5 = None
        collision = None
        if newton["ok"]:
            x_hat = newton["x_fracs"]
            ev = newton["eval"]
            ps = ev["ps"]
            k2 = _k2_check(ps, ev["cross1"], ev["cross2"])
            k4 = _monodromy_check(ev["S"])
            k5 = _k5_checks(ps, ev["cross1"], ev["cross2"])
            collision = _collision_guard(ps)
            c0_box = [ZERO] * N_STATE
            for i in _SEC_IDX:
                c0_box[i] = _b(R_B)
            ev_box = _evaluate(x_hat, c0_box, False, False)
            k3["x_hat"] = [str(v) for v in x_hat]
            k3["f_inf_final"] = str(ev["f_inf"])
            if ev_box["ok"]:
                kraw = _krawczyk(ev, ev_box["DF"])
                k3["krawczyk"] = kraw
                k3["box_error"] = None
                k3["passed"] = kraw["included"]
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
        checks = {
            "K1": k1,
            "K2": k2,
            "K3": k3,
            "K4": k4,
            "K5": k5,
        }
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
                "section": "{q3y = 0, v3y < 0}",
                "T_tilde": str(TILDE),
                "h": str(H_GRID),
                "steps": N_STEPS,
                "block_steps": BLOCK_STEPS,
                "window_w1": [str(W1C - W_HALF), str(W1C + W_HALF)],
                "window_w2": [str(W2C - W_HALF), str(W2C + W_HALF)],
                "seed": [str(v) for v in SEED],
                "r_B": str(R_B),
                "newton_target": str(NEWTON_TARGET),
                "remainder_factor": REMAINDER_FACTOR,
                "sweep_signed": SWEEP_SIGNED,
            },
            "thresholds": {
                "K2_tube_width": str(TUBE_CAP),
                "K2_crossing_width": str(CROSS_CAP),
                "K3_newton_max_iter": NEWTON_MAX,
                "K3_newton_target": str(NEWTON_TARGET),
                "K3_krawczyk_margin": str(K_MARGIN),
                "K4_entry_width": str(MONO_CAP),
                "K5_choreo": str(CHOREO_TOL),
                "K5_period_diff": str(PERIOD_TOL),
                "K6_mutations": [
                    "M1 remainder_factor 1e70 -> K2 fail-fast",
                    "M2 seed q1x +1e-3 -> K3 fail",
                    "M3 receipt byte tamper -> guard hash mismatch",
                    "M4 float injection -> AST scan fail",
                    "M5 sweep_signed False -> K3 fail",
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


