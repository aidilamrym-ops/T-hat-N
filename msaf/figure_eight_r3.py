"""T2-r3: validated figure-eight periodic orbit on a reduced 8x8 shooting system.

Scope and pass criteria are locked in
``reports/PREREG_FIGURE_EIGHT_R3_2026-10-23.md`` sections 1-9.  This is a
new track, not an amendment of T2 or T2-r2.  The r2 Newton point is used
only as a point seed; the r3 campaign re-evaluates ``G(xh)`` and builds a
new local state tube with a per-step Hessian bound and a Taylor-remainder
derivative bound.  The frozen T1/T1b modules are imported, never modified.
The local helper ``_step_with_box`` is a line-for-line copy of the frozen
T1b step whose only extension is returning the validated Picard path box;
it exists because the local Hessian/remainder bounds must be evaluated over
the actual solution path, not just a start-centered ball.

The target is a periodic orbit of the planar equal-mass three-body problem
at the exact fixed period ``T0`` after an exact centre-of-mass lift.  Two
gauges fix phase and orientation:

    q1y = 1/5,          I_xy = sum_i q_ix q_iy = 0.

The six return components ``(0,1,3,4,5,6)`` plus the two gauges form
``G: R^8 -> R^8``.  Krawczyk's theorem on a small exact box certifies
existence and LOCAL uniqueness; no global, stability, spectral, PDE, RH,
chaos, ergodicity, or priority claim is made.  No float is used in the
certified path (AST-scanned by the guard).
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
PREREG_PATH = ROOT / "reports" / "PREREG_FIGURE_EIGHT_R3_2026-10-23.md"
RECEIPT_PATH = ROOT / "reports" / "figure_eight_r3_2026-10-23.json"

PREC = t1.PREC
ORDER = t1.ORDER
SCHEMA = "msaf.figure_eight_r3.v1"
T1_MODULE_SHA = "c1d9b5d60036a5f0772f7e3f1b8c78969efaa7146a713c762531ddce346251b9"
T1B_MODULE_SHA = "42d196a51c5ae45e3b87b8c1e36319abfeb93df776b3c2317e812f7c2c0b5b97"
PREREG_SHA = "23ab24254f13539dddf1bd3cccd87dbbcef01b3398dab1ccf5fb2d75099a6b93"

# --- locked data (prereg sections 1, 5; all exact rationals) --------------

T0 = Fraction(632600304, 10**8)             # fixed period 6.326003040
C = Fraction(1, 5)                          # phase gauge q1y = 1/5
H_STEPS = 1536
H_GRID = T0 / H_STEPS

# Exact r2 Newton point, used only as a point seed.  It is not an r2
# certificate claim; the r3 point residual check below is independent.
XHAT_R2 = (
    Fraction(362136114856268068257747, 2500000000000000000000000),
    Fraction(1, 5),
    Fraction(-10483960928968566266000323, 10000000000000000000000000),
    Fraction(-777368238261201944637859, 10000000000000000000000000),
    Fraction(-15844332692571749887599, 20000000000000000000000),
    Fraction(-4910943265462970329809137, 5000000000000000000000000),
    Fraction(15139114003751568438393, 100000000000000000000000),
    Fraction(5091019520969526187485373, 10000000000000000000000000),
)

KEEP = (0, 1, 3, 4, 5, 6)
IDX8 = (0, 1, 2, 3, 6, 7, 8, 9)
DEP8 = (4, 5, 4, 5, 10, 11, 10, 11)

R_B = Fraction(1, 10**18)
K_MARGIN = Fraction(9, 10)
KAPPA_MAX = Fraction(1, 2)
POINT_TARGET = Fraction(1, 10**24)

HESS_BOX = Fraction(1, 10**12)
QUAD_SAFETY = 4
QUAD_CAP = Fraction(1, 10**18)
DR_CAP = Fraction(1, 10**18)
TUBE_CAP = Fraction(1, 10**10)

GAUSS_DET_MIN = Fraction(1, 10**6)
GAUSS_COND_MAX = Fraction(10**6, 1)
CHOREO_TOL = Fraction(1, 10**6)

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


def _max_arb(values: list[arb]) -> arb:
    return t1b._max_arb(values)


def _row_abs(mat: list[list[arb]], i: int, n: int) -> arb:
    acc = arb(0)
    for j in range(n):
        acc = acc + mat[i][j].abs_upper()
    return acc


# --- exact lift / projection ---------------------------------------------


def _lift(x: list[arb]) -> list[arb]:
    """8 reduced coordinates -> 12-dimensional COM-zero state."""
    return [
        x[0], x[1], x[2], x[3],
        -x[0] - x[2], -x[1] - x[3],
        x[4], x[5], x[6], x[7],
        -x[4] - x[6], -x[5] - x[7],
    ]


def _lift_box(x: list[Fraction], c: list[arb]) -> tuple[list[arb], list[arb]]:
    """Lift a reduced point box to a sound 12-dimensional component box."""
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


# --- second-order jet (local Hessian bound only) -------------------------


class Dual2:
    """A second-order jet: value, gradient, and full Hessian.

    ``v`` is an arb enclosure, ``g[i]`` the first derivative, and
    ``h[i][j]`` the second derivative.  The Hessian is kept full (not
    symmetrised) so the interval operations remain inclusion-isotonic.
    """

    __slots__ = ("v", "g", "h")

    def __init__(self, v: arb, g: list[arb], h: list[list[arb]]):
        self.v = v
        self.g = g
        self.h = h

    @staticmethod
    def const(ref: "Dual2", value) -> "Dual2":
        n = len(ref.g)
        z = ref.v - ref.v
        val = value if isinstance(value, arb) else arb(value)
        return Dual2(
            val,
            [z for _ in range(n)],
            [[z for _ in range(n)] for _ in range(n)],
        )

    @staticmethod
    def var(v: arb, i: int, n: int) -> "Dual2":
        z = v - v
        g = [z for _ in range(n)]
        g[i] = arb(1)
        h = [[z for _ in range(n)] for _ in range(n)]
        return Dual2(v, g, h)

    @staticmethod
    def _coerce(ref: "Dual2", other) -> "Dual2":
        if isinstance(other, Dual2):
            return other
        return Dual2.const(ref, other)

    def __add__(self, other):
        o = self._coerce(self, other)
        n = len(self.g)
        return Dual2(
            self.v + o.v,
            [a + b for a, b in zip(self.g, o.g)],
            [[self.h[i][j] + o.h[i][j] for j in range(n)] for i in range(n)],
        )

    __radd__ = __add__

    def __sub__(self, other):
        o = self._coerce(self, other)
        n = len(self.g)
        return Dual2(
            self.v - o.v,
            [a - b for a, b in zip(self.g, o.g)],
            [[self.h[i][j] - o.h[i][j] for j in range(n)] for i in range(n)],
        )

    def __rsub__(self, other):
        return self._coerce(self, other) - self

    def __neg__(self):
        return Dual2(
            -self.v,
            [-a for a in self.g],
            [[-x for x in row] for row in self.h],
        )

    def __mul__(self, other):
        o = self._coerce(self, other)
        n = len(self.g)
        g = [self.g[i] * o.v + self.v * o.g[i] for i in range(n)]
        h = [
            [
                self.h[i][j] * o.v
                + self.g[i] * o.g[j]
                + self.g[j] * o.g[i]
                + self.v * o.h[i][j]
                for j in range(n)
            ]
            for i in range(n)
        ]
        return Dual2(self.v * o.v, g, h)

    __rmul__ = __mul__

    def __truediv__(self, other):
        o = self._coerce(self, other)
        n = len(self.g)
        inv = arb(1) / o.v
        binv = Dual2(
            inv,
            [-o.g[i] * inv * inv for i in range(n)],
            [
                [
                    2 * o.g[i] * o.g[j] * inv * inv * inv
                    - o.h[i][j] * inv * inv
                    for j in range(n)
                ]
                for i in range(n)
            ],
        )
        return self * binv

    def __rtruediv__(self, other):
        return self._coerce(self, other) / self

    def sqrt(self) -> "Dual2":
        n = len(self.g)
        root = self.v.sqrt()
        inv2 = arb(1) / (2 * root)
        coef = arb(1) / (4 * self.v * root)
        g = [a * inv2 for a in self.g]
        h = [
            [
                self.h[i][j] * inv2 - self.g[i] * self.g[j] * coef
                for j in range(n)
            ]
            for i in range(n)
        ]
        return Dual2(root, g, h)


def _rhs2(state: list[Dual2]) -> list[Dual2]:
    """Three-body RHS over a second-order jet (same formula as T1)."""
    xs = state[0:6:2]
    ys = state[1:6:2]
    vxs = state[6:12:2]
    vys = state[7:12:2]
    zero = state[0] - state[0]
    ax = [zero, zero, zero]
    ay = [zero, zero, zero]
    one = zero + 1
    for i, j in ((0, 1), (0, 2), (1, 2)):
        dx = xs[i] - xs[j]
        dy = ys[i] - ys[j]
        r2 = dx * dx + dy * dy
        inv = one / (r2 * r2.sqrt())
        fx = dx * inv
        fy = dy * inv
        ax[i] = ax[i] - fx
        ay[i] = ay[i] - fy
        ax[j] = ax[j] + fx
        ay[j] = ay[j] + fy
    return [
        vxs[0], vys[0], vxs[1], vys[1], vxs[2], vys[2],
        ax[0], ay[0], ax[1], ay[1], ax[2], ay[2],
    ]


def _norm1_d2(out: list[Dual2]) -> tuple[arb, arb]:
    """Bounds ``max_i sum_j |df_i/dy_j|`` and ``max_i sum_jk |d2f_i|``."""
    n = len(out)
    best_a = arb(0)
    best_b = arb(0)
    for d in out:
        a = arb(0)
        for j in range(n):
            a = a + d.g[j].abs_upper()
        b = arb(0)
        for j in range(n):
            for k in range(n):
                b = b + d.h[j][k].abs_upper()
        if bool(a > best_a):
            best_a = a
        if bool(b > best_b):
            best_b = b
    return best_a, best_b


def _dnorm_dual(box: list[arb]) -> arb:
    """First-derivative bound of the RHS over a box, via T1 Dual."""
    n = len(box)
    dstate = [
        t1.Dual(box[i], [arb(1) if j == i else arb(0) for j in range(n)])
        for i in range(n)
    ]
    out = t1.rhs_three_body(dstate)
    best = arb(0)
    for d in out:
        acc = arb(0)
        for j in range(n):
            acc = acc + d.g[j].abs_upper()
        if bool(acc > best):
            best = acc
    return best


# --- checkpoint certificate (signed = frozen T1b; reset = M5 path) --------


def _certificate(jacs, rems, quads, c_in, upto, lo):
    """Checkpoint certificate; honest signed sweep or M5 reset sweep."""
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


# --- point trajectory -----------------------------------------------------


def _step_with_box(
    coeff_fn,
    rhs_fn,
    m: list[arb],
    c: list[arb],
    h: arb,
    order: int,
    include_remainder: bool = True,
):
    """Local copy of the frozen T1b step, exposing the validated Picard box.

    The Taylor recurrence, Picard containment check, remainder bound, and
    input-box Jacobian are exactly the frozen T1b logic; only the return
    value is extended with the validated ``box``.  The frozen module is
    not modified.  Exposing ``box`` is necessary because the one-step
    Hessian and remainder-derivative bounds must be evaluated over the
    actual solution path, not just a tiny box around the initial point.
    """
    n = len(m)
    kappa_nl = t1b._kappa_nl()
    midpoint = [m[i].mid() for i in range(n)]
    pc = coeff_fn(midpoint, order)
    m_next = [t1._horner(comp, h) for comp in pc]

    r_tot = c[0]
    for x in c[1:]:
        if bool(x > r_tot):
            r_tot = x

    t = t1._time_ball(h)
    prange = [t1._horner(comp, t) for comp in pc]
    span = 2 * prange[0].rad()
    for b in prange[1:]:
        w = 2 * b.rad()
        if bool(w > span):
            span = w
    eps = t1._tol("1e-12")
    factor = 1
    box = prange
    for _ in range(16):
        delta = (span * (arb(1) / 16) + r_tot + eps) * factor
        box = [b + arb(0, delta.abs_upper()) for b in prange]
        image = rhs_fn(box)
        ok = True
        for i in range(n):
            if not box[i].contains(m[i] + arb(0, c[i]) + h * image[i]):
                ok = False
                break
        if ok:
            break
        factor *= 2
    else:
        raise t1.ValidationError("Picard enclosure failed")

    rem: list[arb]
    if include_remainder:
        tail = coeff_fn(box, order + 1)
        h_pow = h ** (order + 1)
        rem = [
            (tail[i][order + 1].abs_upper() * h_pow).abs_upper()
            for i in range(n)
        ]
    else:
        rem = [arb(0) for _ in range(n)]

    xbox = [midpoint[i] + arb(0, c[i]) for i in range(n)]
    dual = t1._dual_coeffs(coeff_fn, xbox, order)
    jac = [
        [
            t1._horner([dual[i][k].g[j] for k in range(order + 1)], h)
            for j in range(n)
        ]
        for i in range(n)
    ]
    quad = kappa_nl * r_tot * r_tot
    return m_next, jac, rem, quad, box


def _point_pass(x: list[Fraction]) -> dict:
    """Point Taylor propagation at ``x`` with zero state radius.

    Returns the point midpoints, step Jacobians, Taylor remainders,
    validated Picard path boxes, and the final point-endpoint error
    enclosure.  No local quadratic slack is inserted; the point pass only
    supplies the seed trajectory and the one-step data for the local-bound
    prepass.  The path boxes are used by ``_local_bounds`` so that the
    Hessian/remainder bounds see the actual solution path over each step.
    """
    n = N_STATE
    m0, _ = _lift_box(x, [ZERO] * N_SEC)
    m = [v.mid() for v in m0]
    c = [ZERO] * n
    jacs: list = []
    rems: list = []
    boxes: list = []
    mids: list = [list(m)]
    factor = _b(Fraction(REMAINDER_FACTOR, 1))
    for k in range(H_STEPS):
        try:
            m_next, jac, rem, _, box = _step_with_box(
                t1.coeffs_three_body,
                t1.rhs_three_body,
                m,
                c,
                _b(H_GRID),
                ORDER,
                True,
            )
        except t1.ValidationError as exc:
            return {
                "mids": mids,
                "jacs": jacs,
                "rems": rems,
                "boxes": boxes,
                "error": "point aborted at step %d: %s" % (k + 1, exc),
                "steps_done": k,
            }
        if REMAINDER_FACTOR != 1:
            rem = [r * factor for r in rem]
        jacs.append([jac[i][j] for i in range(n) for j in range(n)])
        rems.append(rem)
        boxes.append(box)
        mids.append([v.mid() for v in m_next])
        m = mids[-1]
        c = [ZERO] * n
    c_out, _ = _certificate(
        jacs,
        rems,
        [ZERO] * H_STEPS,
        [ZERO] * n,
        H_STEPS,
        max(0, H_STEPS - BLOCK_STEPS),
    )
    return {
        "mids": mids,
        "jacs": jacs,
        "rems": rems,
        "boxes": boxes,
        "c_out": c_out,
        "error": None,
        "steps_done": H_STEPS,
    }


def _local_bounds(ps: dict) -> dict:
    """Compute the prereregistered local Hessian and remainder-derivative bounds.

    The base box for each step is the validated T1b Picard path box exposed
    by ``_step_with_box``.  It contains the true solution path on that step,
    not merely a tiny ball around the initial point.  It is then expanded by
    ``2 * HESS_BOX`` so that it also contains the box-pass path, whose state
    tube is at most ``HESS_BOX`` wide.  The caller must still verify that the
    certified state tube respects ``HESS_BOX``; otherwise the second-order
    remainder is not applicable.
    """
    mids = ps["mids"]
    jacs = ps["jacs"]
    boxes = ps["boxes"]
    pad = _b(Fraction(2, 1) * HESS_BOX)
    hball = _b(H_GRID)
    h_pow = hball ** (ORDER + 1)
    dr_list: list[arb] = []
    grad_tail_max = arb(0)
    lf_max = arb(0)
    for k in range(H_STEPS):
        base_box = boxes[k]
        box = [base_box[i] + arb(0, pad) for i in range(N_STATE)]
        lf = _dnorm_dual(box)
        if bool(lf > lf_max):
            lf_max = lf
        lam = (lf * hball).exp() * 2
        dual_tail = t1._dual_coeffs(t1.coeffs_three_body, box, ORDER + 1)
        grad_tail = arb(0)
        for i in range(N_STATE):
            for j in range(N_STATE):
                val = dual_tail[i][ORDER + 1].g[j].abs_upper()
                if bool(val > grad_tail):
                    grad_tail = val
        if bool(grad_tail > grad_tail_max):
            grad_tail_max = grad_tail
        dr = 2 * lam * grad_tail * h_pow
        dr_list.append(dr)
    dr_max = arb(0)
    for dr in dr_list:
        if bool(dr > dr_max):
            dr_max = dr

    p_m = t1b._identity(N_STATE)
    p_r = [[arb(0) for _ in range(N_STATE)] for _ in range(N_STATE)]
    max_a = arb(0)
    max_b = arb(0)
    max_s = arb(0)
    max_hstep = arb(0)
    for k in range(H_STEPS):
        base_box = boxes[k]
        box = [base_box[i] + arb(0, pad) for i in range(N_STATE)]
        dstate = [Dual2.var(box[i], i, N_STATE) for i in range(N_STATE)]
        out = _rhs2(dstate)
        a, b = _norm1_d2(out)
        if bool(a > max_a):
            max_a = a
        if bool(b > max_b):
            max_b = b
        smax = arb(0)
        for i in range(N_STATE):
            acc = arb(0)
            for j in range(N_STATE):
                acc = acc + p_m[i][j].abs_upper() + p_r[i][j]
            if bool(acc > smax):
                smax = acc
        if bool(smax < ONE):
            smax = ONE
        if bool(smax > max_s):
            max_s = smax
        ah = a * hball
        ea = ah.exp()
        hstep = (b * smax * smax / a) * ea * (ea - 1)
        if bool(hstep > max_hstep):
            max_hstep = hstep
        flat = jacs[k]
        jac_eff = [
            [
                flat[i * N_STATE + j] + arb(0, dr_max)
                for j in range(N_STATE)
            ]
            for i in range(N_STATE)
        ]
        m_k, r_k = t1b._mr_split(jac_eff)
        p_m, p_r = t1b._mr_mul(m_k, r_k, p_m, p_r)
    quad_step = _b(Fraction(QUAD_SAFETY, 1)) * max_hstep * _b(HESS_BOX) * _b(HESS_BOX)
    return {
        "a_max": max_a,
        "b_max": max_b,
        "s_max": max_s,
        "hstep_max": max_hstep,
        "quad_step": quad_step,
        "dr_max": dr_max,
        "dr_list": dr_list,
        "lf_max": lf_max,
        "grad_tail_max": grad_tail_max,
    }


# --- reduced sensitivity product -----------------------------------------


def _sproduct8_jacs(jacs: list, upto: int):
    """Incremental 8x8 reduced sensitivity chain in midpoint-radius form."""
    n = N_SEC
    chain = [(t1b._identity(n), [[arb(0) for _ in range(n)] for _ in range(n)])]
    for k in range(upto):
        flat = jacs[k]
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


def _flow_deriv8_jacs(jacs: list, upto: int) -> list[list[arb]]:
    """8x8 interval enclosure of the reduced flow derivative."""
    p_m, p_r = _sproduct8_jacs(jacs, upto)
    return [
        [p_m[i][j] + arb(0, p_r[i][j]) for j in range(N_SEC)]
        for i in range(N_SEC)
    ]


def _point_dg(x_arb: list[arb], jacs_point: list, dr_max: arb) -> list[list[arb]]:
    """Point DG enclosure: flow derivative plus exact gauge gradients."""
    n = N_STATE
    jacs_eff = [
        [
            jacs_point[k][i * n + j] + arb(0, dr_max)
            for i in range(n)
            for j in range(n)
        ]
        for k in range(H_STEPS)
    ]
    S8 = _flow_deriv8_jacs(jacs_eff, H_STEPS)
    DP = [
        [S8[i][j] - (ONE if i == j else ZERO) for j in range(N_SEC)]
        for i in range(N_SEC)
    ]
    DG = [[DP[KEEP[i]][j] for j in range(N_SEC)] for i in range(6)]
    DG.append([ONE if j == 1 else ZERO for j in range(N_SEC)])
    DG.append(_g2_grad(x_arb))
    return DG


def _g_point(x_arb: list[arb], ps: dict) -> list[arb]:
    """Point G enclosure: six return rows plus the two exact gauges."""
    c_out = ps["c_out"]
    y = [
        ps["mids"][H_STEPS][i] + arb(0, c_out[i])
        for i in range(N_STATE)
    ]
    proj = _project8(y)
    p8 = [proj[i] - x_arb[i] for i in range(N_SEC)]
    return [p8[KEEP[i]] for i in range(6)] + [
        x_arb[1] - _b(C),
        _g2_value(x_arb),
    ]


def _evaluate_point(x: list[Fraction], ps: dict, dr_max: arb) -> dict:
    """Assemble the point G/DG data from the point pass."""
    x_arb = [_b(v) for v in x]
    if ps.get("error") is not None:
        return {"ok": False, "error": ps["error"], "ps": ps}
    G = _g_point(x_arb, ps)
    DG = _point_dg(x_arb, ps["jacs"], dr_max)
    return {
        "ok": True,
        "G": G,
        "DG": DG,
        "y_final": [
            ps["mids"][H_STEPS][i] + arb(0, ps["c_out"][i])
            for i in range(N_STATE)
        ],
        "f_inf": _max_arb([fi.abs_upper() for fi in G]),
        "c_final": ps["c_out"],
        "ps": ps,
    }


# --- box pass -------------------------------------------------------------


def _box_pass(
    x: list[Fraction],
    c8: list[arb],
    quad_step: arb,
    dr_max: arb,
    gate: bool,
) -> dict:
    """Integrate the reduced input box with local quadratic/derivative bounds.

    The local copy of the frozen T1b step supplies the Taylor polynomial,
    its interval Jacobian, the Taylor remainder, and the validated Picard
    path box.  ``J_eff = J + [-DR_MAX, DR_MAX]`` widens the derivative to
    the full step map.  ``QUAD_STEP`` is the per-step second-order radius;
    it is constant, so there is no ``KAPPA_NL`` feedback loop.
    """
    n = N_STATE
    m0, c0 = _lift_box(x, c8)
    m = [v.mid() for v in m0]
    c = list(c0)
    c_in = list(c0)
    jacs: list = []
    rems: list = []
    quads: list = []
    mids: list = [list(m)]
    checkpoints: dict = {}
    c_series: list = [list(c)]
    error = None
    steps_done = 0
    factor = _b(Fraction(REMAINDER_FACTOR, 1))
    for k in range(H_STEPS):
        try:
            m_next, jac, rem, _, _path_box = _step_with_box(
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
        jac_eff = [
            [
                jac[i][j] + arb(0, dr_max)
                for j in range(n)
            ]
            for i in range(n)
        ]
        jacs.append([jac_eff[i][j] for i in range(n) for j in range(n)])
        rems.append(rem)
        quads.append(quad_step)
        mids.append([v.mid() for v in m_next])
        c_next = []
        for i in range(n):
            acc = arb(0)
            for j in range(n):
                acc = acc + jac_eff[i][j].abs_upper() * c[j]
            c_next.append(acc + rem[i] + quad_step + t1._tol(t1b.EPS_SLACK))
        m = [v.mid() for v in m_next]
        c = c_next
        steps_done = k + 1
        c_series.append(list(c))
        upto = k + 1
        if upto % BLOCK_STEPS == 0 or upto == H_STEPS:
            lo = upto - min(BLOCK_STEPS, upto)
            c_pre, _weights = _certificate(
                jacs, rems, quads, c_in, upto, lo
            )
            c = list(c_pre)
            c_series[-1] = list(c_pre)
            maxc = _max_arb(c_pre)
            width = _b(Fraction(2, 1)) * maxc
            checkpoints[upto] = {
                "step": upto,
                "c_out": list(c_pre),
                "max_radius": maxc,
                "width": width,
                "slack": quad_step,
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
        "c0": list(c_in),
        "error": error,
        "steps_done": steps_done,
        "cat_series": c_series,
        "quad_step": quad_step,
        "dr_max": dr_max,
    }


def _evaluate_box(
    x: list[Fraction],
    c8: list[arb],
    quad_step: arb,
    dr_max: arb,
    gate: bool,
) -> dict:
    """Assemble the box DG enclosure and final tube data."""
    ps = _box_pass(x, c8, quad_step, dr_max, gate)
    out = {"ps": ps}
    if ps["error"] is not None:
        out["ok"] = False
        out["error"] = ps["error"]
        return out
    if H_STEPS not in ps["checkpoints"]:
        out["ok"] = False
        out["error"] = "missing final checkpoint"
        return out
    S8 = _flow_deriv8_jacs(ps["jacs"], H_STEPS)
    DP = [
        [S8[i][j] - (ONE if i == j else ZERO) for j in range(N_SEC)]
        for i in range(N_SEC)
    ]
    x_arb = [_b(v) for v in x]
    xg = [x_arb[i] + arb(0, c8[i]) for i in range(N_SEC)]
    DG = [[DP[KEEP[i]][j] for j in range(N_SEC)] for i in range(6)]
    DG.append([ONE if j == 1 else ZERO for j in range(N_SEC)])
    DG.append(_g2_grad(xg))
    ck = ps["checkpoints"][H_STEPS]
    out.update(
        {
            "ok": True,
            "DG": DG,
            "c_final": ck["c_out"],
            "width": ck["width"],
            "max_radius": ck["max_radius"],
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
        if t1._contains(piv, 0):
            # A zero-containing pivot makes the elimination non-enclosing.
            # Return a deliberately wide ball containing any determinant of
            # the small matrices used here; K4 then fails instead of passing.
            return arb(0, _b(Fraction(10**60, 1)))
        for i in range(p + 1, n):
            fac = a[i][p] / piv
            for j in range(p, n):
                a[i][j] = a[i][j] - fac * a[p][j]
    det = _b(Fraction(sign, 1))
    for p in range(n):
        det = det * a[p][p]
    return det


# --- K3: Krawczyk inclusion ------------------------------------------------


def _krawczyk(ev_point: dict, dg_box: list[list[arb]]) -> dict:
    """K3 box test with the point G and box derivative enclosure."""
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
            "point_ok": False,
            "passed": False,
            "error": "singular midpoint DG(xh)",
        }
    G = ev_point["G"]
    point_ok = bool(ev_point["f_inf"] <= _b(POINT_TARGET))
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
        "point_ok": point_ok,
        "passed": bool(included and kappa_ok and point_ok),
        "error": None,
    }


# --- K4: Gauss matrix determinant / conditioning --------------------------


def _k4_check(ev_point: dict, ev_box: dict) -> dict:
    """K4: interval determinant and condition estimate (no spectrum)."""
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
    """K5: phase-independent choreography defects over the box tube."""
    ps = ev_box["ps"]
    series = ps["cat_series"]
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
    series = ps["cat_series"]
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


def _k2_check(ev_box: dict, local: dict) -> dict:
    """K2: validated local tube, derivative/quadratic caps, Hessian box."""
    if not ev_box.get("ok", False):
        return {
            "checkpoints": [],
            "width_max": None,
            "running_radius_max": None,
            "quad_step": str(local["quad_step"]),
            "quad_ok": bool(local["quad_step"] <= _b(QUAD_CAP)),
            "dr_max": str(local["dr_max"]),
            "dr_ok": bool(local["dr_max"] <= _b(DR_CAP)),
            "widths_ok": False,
            "running_ok": False,
            "passed": False,
            "error": ev_box.get("error"),
        }
    ps = ev_box["ps"]
    rows = []
    max_width = ZERO
    max_radius_ck = ZERO
    widths_ok = True
    for upto in sorted(ps["checkpoints"]):
        ck = ps["checkpoints"][upto]
        width = ck["width"]
        rad = ck["max_radius"]
        ok = bool(width <= _b(TUBE_CAP) and rad <= _b(HESS_BOX))
        widths_ok = widths_ok and ok
        if bool(width > max_width):
            max_width = width
        if bool(rad > max_radius_ck):
            max_radius_ck = rad
        rows.append(
            {
                "step": upto,
                "time": str(_b(H_GRID * upto)),
                "max_radius": str(rad),
                "width": str(width),
                "width_ok": ok,
                "slack": str(ck["slack"]),
            }
        )
    running_max = ZERO
    for cvec in ps["cat_series"]:
        val = _max_arb(cvec)
        if bool(val > running_max):
            running_max = val
    running_ok = bool(running_max <= _b(HESS_BOX))
    quad_ok = bool(local["quad_step"] <= _b(QUAD_CAP))
    dr_ok = bool(local["dr_max"] <= _b(DR_CAP))
    passed = bool(
        widths_ok
        and running_ok
        and quad_ok
        and dr_ok
        and ps["error"] is None
    )
    return {
        "checkpoints": rows,
        "width_max": str(max_width),
        "checkpoint_radius_max": str(max_radius_ck),
        "running_radius_max": str(running_max),
        "quad_step": str(local["quad_step"]),
        "quad_ok": quad_ok,
        "dr_max": str(local["dr_max"]),
        "dr_ok": dr_ok,
        "widths_ok": widths_ok,
        "running_ok": running_ok,
        "passed": passed,
        "error": ps["error"],
    }


# --- campaign -------------------------------------------------------------


def run_campaign() -> dict:
    """Full certified T2-r3 campaign (K1-K5); deterministic; writes nothing."""
    with flint.ctx.workprec(PREC):
        k1 = _k1_check()
        point_ps = _point_pass(list(XHAT_R2))
        local = None
        ev_point = None
        k2 = None
        k3 = {"x_hat": [str(v) for v in XHAT_R2], "krawczyk": None}
        k4 = None
        k5 = None
        collision = None
        if point_ps.get("error") is None:
            local = _local_bounds(point_ps)
            ev_point = _evaluate_point(list(XHAT_R2), point_ps, local["dr_max"])
        if ev_point is not None and ev_point.get("ok", False):
            c8_box = [_b(R_B)] * N_SEC
            ev_box = _evaluate_box(
                list(XHAT_R2),
                c8_box,
                local["quad_step"],
                local["dr_max"],
                True,
            )
            k2 = _k2_check(ev_box, local)
            k3["f_inf_final"] = str(ev_point["f_inf"])
            k3["point_ok"] = bool(ev_point["f_inf"] <= _b(POINT_TARGET))
            if ev_box.get("ok", False):
                k3["box_error"] = None
                kraw = _krawczyk(ev_point, ev_box["DG"])
                k3["krawczyk"] = kraw
                k3["passed"] = kraw["passed"]
                k4 = _k4_check(ev_point, ev_box)
                k5 = _k5_check(ev_box)
                collision = _collision_note(ev_box["ps"])
            else:
                k3["box_error"] = ev_box.get("error")
                k3["passed"] = False
        else:
            k3["f_inf_final"] = None
            k3["point_ok"] = False
            k3["box_error"] = (
                point_ps.get("error")
                if point_ps.get("error") is not None
                else ev_point.get("error")
            )
            k3["passed"] = False
        k1_pass = bool(k1["passed"])
        k2_pass = bool(k2 is not None and k2["passed"])
        k3_pass = bool(k3["passed"])
        k4_pass = bool(k4 is not None and k4["passed"])
        k5_pass = bool(k5 is not None and k5["passed"])
        # K6 is exercised by the guard; the campaign records the locked
        # mutation catalogue but does not claim it here.
        all_pass = k1_pass and k2_pass and k3_pass and k4_pass and k5_pass
        if all_pass:
            summary = "ALL PASS"
        elif k3_pass:
            summary = "INCONCLUSIVE"
        else:
            summary = "FAILED"
        checks = {"K1": k1, "K2": k2, "K3": k3, "K4": k4, "K5": k5}
        local_payload = None
        if local is not None:
            local_payload = {
                "a_max": str(local["a_max"]),
                "b_max": str(local["b_max"]),
                "s_max": str(local["s_max"]),
                "hstep_max": str(local["hstep_max"]),
                "quad_step": str(local["quad_step"]),
                "dr_max": str(local["dr_max"]),
                "lf_max": str(local["lf_max"]),
                "grad_tail_max": str(local["grad_tail_max"]),
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
                "section": "{q1y = 1/5, I_xy = 0}",
                "T0": str(T0),
                "C": str(C),
                "h": str(H_GRID),
                "steps": H_STEPS,
                "block_steps": BLOCK_STEPS,
                "seed": [str(v) for v in XHAT_R2],
                "rows_keep": list(KEEP),
                "rows_drop": [2, 7],
                "r_B": str(R_B),
                "point_target": str(POINT_TARGET),
                "hess_box": str(HESS_BOX),
                "quad_safety": QUAD_SAFETY,
                "remainder_factor": REMAINDER_FACTOR,
                "sweep_signed": SWEEP_SIGNED,
            },
            "thresholds": {
                "K2_tube_width": str(TUBE_CAP),
                "K2_quad_cap": str(QUAD_CAP),
                "K2_dr_cap": str(DR_CAP),
                "K3_point_target": str(POINT_TARGET),
                "K3_krawczyk_margin": str(K_MARGIN),
                "K3_kappa_max": str(KAPPA_MAX),
                "K4_det_min": str(GAUSS_DET_MIN),
                "K4_cond_max": str(GAUSS_COND_MAX),
                "K5_choreo": str(CHOREO_TOL),
                "K6_mutations": [
                    "M1 remainder_factor 1e70 -> FAILED",
                    "M2 T0 + 1/10 -> K3 fail",
                    "M3 receipt byte tamper -> guard hash mismatch",
                    "M4 float injection -> AST scan fail",
                    "M5 sweep_signed False -> K2/K3 fail",
                ],
            },
            "local_bounds": local_payload,
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
