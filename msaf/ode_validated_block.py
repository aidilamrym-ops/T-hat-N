"""T1b: two-pass signed block propagation for the validated ODE integrator.

Scope and pass criteria are locked in
``reports/PREREG_ODE_VALIDATED_T1B_2026-10-21.md`` (sections 2, 10, 11).
This module imports the frozen T1 machinery (``msaf/ode_validated.py``) and
changes only the uncertainty transport:

- forward pass per block: midpoint Taylor step, Picard box (running sound
  bound), Taylor remainder vector, interval Jacobian ``J_k`` over the box;
- backward certificate at every checkpoint: one continuous signed sweep from
  the checkpoint back to step 0,

      c_out_i = sum_j |P[i,j]| * c_in_j
              + sum_k sum_j |P_k[i,j]| * (rem_k,j + quad_k),

  with ``P = J_{t-1} ... J_0`` and ``P_k = J_{t-1} ... J_{k+1}``.

This is the signed column formulation of the preregistration without column
merging (which the section 11 amendment cancels as unsound): the sensitivity
product is carried *continuously across block boundaries* -- a block is only
a reporting checkpoint, never a reset of the product (sections 2.1, 2.4,
11; see section 12).  No scalar norm is applied to ``rho`` per step: the
per-step scalar-norm propagation that failed in T1 is exercised only by the
C7 mutation, which reruns the frozen T1 mechanism itself.
"""

from __future__ import annotations

import ast
import json
from fractions import Fraction
from pathlib import Path

import flint
from flint import arb

from msaf import ode_validated as t1

ROOT = Path(__file__).resolve().parents[1]
PREREG_PATH = ROOT / "reports" / "PREREG_ODE_VALIDATED_T1B_2026-10-21.md"
RECEIPT_PATH = ROOT / "reports" / "ode_validated_t1b_2026-10-21.json"

PREC = t1.PREC
ORDER = t1.ORDER
SCHEMA = "msaf.ode_validated_block.v1"
T1_MODULE_SHA = "c1d9b5d60036a5f0772f7e3f1b8c78969efaa7146a713c762531ddce346251b9"
KAPPA_NL_TEXT = "1e18"
EPS_SLACK = "1e-70"
C7_LIMIT_S3 = 1557
C7_LIMIT_S4 = 42

RhsFn = t1.RhsFn
CoeffFn = t1.CoeffFn


# ---------------------------------------------------------------------------
# linear algebra helpers (n <= 12)
# ---------------------------------------------------------------------------


def _kappa_nl() -> arb:
    """Locked quadratic constant; call inside the 256-bit context."""
    return t1._ball(Fraction(10**18))


def _identity(n: int) -> list[list[arb]]:
    return [[arb(1) if i == j else arb(0) for j in range(n)] for i in range(n)]


def _matmul(a: list[list[arb]], b: list[list[arb]], n: int) -> list[list[arb]]:
    out = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            acc = arb(0)
            for k in range(n):
                acc = acc + a[i][k] * b[k][j]
            out[i][j] = acc
    return out


def _row_abs_sum(mat: list[list[arb]], i: int, n: int) -> arb:
    acc = arb(0)
    for j in range(n):
        acc = acc + mat[i][j].abs_upper()
    return acc


def _max_arb(values: list[arb]) -> arb:
    top = values[0]
    for x in values[1:]:
        if bool(x > top):
            top = x
    return top


def _mr_split(jac: list[list[arb]]) -> tuple[list[list[arb]], list[list[arb]]]:
    """Split an interval matrix into point midpoints and nonnegative radii."""
    n = len(jac)
    mids = [[jac[i][j].mid() for j in range(n)] for i in range(n)]
    rads = [[jac[i][j].rad().abs_upper() for j in range(n)] for i in range(n)]
    return mids, rads


def _mr_mul(
    m1: list[list[arb]],
    r1: list[list[arb]],
    m2: list[list[arb]],
    r2: list[list[arb]],
) -> tuple[list[list[arb]], list[list[arb]]]:
    """Midpoint-radius product of interval matrices.

    Encloses ``(M1 +- R1) * (M2 +- R2)`` as ``M1*M2 +- (R1*|M2| + |M1|*R2
    + R1*R2)``.  Plain interval multiplication would inflate the width of a
    long backward product like ``prod |J|`` (wrapping), which is not a
    property of the signed product; this form keeps the width proportional
    to the accumulated Jacobian widths (see prereg section 12).
    """
    n = len(m1)
    mm = _matmul(m1, m2, n)
    rr = [[arb(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            acc = arb(0)
            for k in range(n):
                acc = acc + r1[i][k] * m2[k][j].abs_upper()
                acc = acc + m1[i][k].abs_upper() * r2[k][j]
                acc = acc + r1[i][k] * r2[k][j]
            rr[i][j] = acc
    return mm, rr


# ---------------------------------------------------------------------------
# one forward step
# ---------------------------------------------------------------------------


def forward_step(
    coeff_fn: CoeffFn,
    rhs_fn: RhsFn,
    m: list[arb],
    c: list[arb],
    h: arb,
    order: int,
    include_remainder: bool = True,
) -> tuple[list[arb], list[list[arb]], list[arb], arb]:
    """One Taylor step from the box ``[m_i +/- c_i]``.

    Returns ``(m_next, jac, rem, quad)``.  ``jac`` encloses the one-step
    Jacobian over the input box, ``rem`` is the componentwise Taylor
    remainder bound, ``quad`` is the locked quadratic slack.
    """
    n = len(m)
    kappa_nl = _kappa_nl()
    # Taylor coefficients are computed at the point midpoint (as in T1);
    # the ball radius of ``m`` itself must not be pumped through the
    # recurrence, or the midpoint picks up dependency inflation.
    midpoint = [m[i].mid() for i in range(n)]
    pc = coeff_fn(midpoint, order)
    m_next = [t1._horner(comp, h) for comp in pc]

    r_tot = c[0]
    for x in c[1:]:
        if bool(x > r_tot):
            r_tot = x

    # Picard box: every solution starting in [m +/- c] must stay in ``box``.
    t = t1._time_ball(h)
    prange = [t1._horner(comp, t) for comp in pc]
    span = 2 * prange[0].rad()
    for b in prange[1:]:
        w = 2 * b.rad()
        if bool(w > span):
            span = w
    eps = t1._tol("1e-12")
    # Box inflation is started small and grown (doubling) until the *same*
    # rigorous Picard containment passes; the containment check below is the
    # sole soundness gate and is unchanged.  A smaller passing box is strictly
    # better: the (p+1)-th coefficient bound (and hence the Taylor remainder)
    # is inclusion-monotone in the box radius, so over-inflating by a full
    # ``span`` inflates the remainder by many orders of magnitude near a close
    # approach (prereg section 12; measured 19 orders at S4 step 40).
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

    # Rigorous Taylor remainder: the (p+1)-th derivative is bounded over the
    # *validated Picard box*, which is what contains the true solution path on
    # the step.  Bounding it on the input box alone is unsound -- the Lagrange
    # remainder involves the derivative along the path, not at the initial
    # point (the frozen T1 module bounds it over the path box for the same
    # reason).  See prereg section 12.
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

    # Interval Jacobian of the Taylor polynomial over the tiny input box
    # (mean-value form, as in the frozen T1 module): the sensitivity of the
    # step map to the initial state, evaluated at the point midpoint.
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
    return m_next, jac, rem, quad


# ---------------------------------------------------------------------------
# forward block pass
# ---------------------------------------------------------------------------


def forward_block(
    coeff_fn: CoeffFn,
    rhs_fn: RhsFn,
    m0: list[arb],
    c0: list[arb],
    h: arb,
    steps: int,
    order: int,
    step_offset: int = 0,
    include_remainder: bool = True,
) -> tuple[list[arb], list[arb], list, list[arb], arb, arb]:
    """Advance one block forward, collecting the per-step data.

    Returns ``(m, c_run, jacs, rems, max_rem, max_run)`` where ``jacs`` are
    flattened ``n*n`` interval Jacobians ``J_k`` of the step maps, ``rems``
    the rigorous Taylor remainder vectors, and ``c_run`` the sound (possibly
    loose, section 11.3) forward running bound -- used only to size the next
    Picard boxes.  The checkpoint certificate is *not* computed here; it is
    the continuous signed backward sweep of :func:`certificate`.
    """
    n = len(m0)
    m = list(m0)
    c = list(c0)
    jacs: list[list[arb]] = []
    rems: list[list[arb]] = []
    max_rem = arb(0)
    max_run = arb(0)
    for x in c:
        if bool(x > max_run):
            max_run = x

    for k in range(steps):
        try:
            m_next, jac, rem, _quad = forward_step(
                coeff_fn, rhs_fn, m, c, h, order, include_remainder
            )
        except t1.ValidationError as exc:
            raise t1.ValidationError(
                f"aborted at step {step_offset + k + 1}: {exc}"
            ) from exc
        jacs.append([jac[i][j] for i in range(n) for j in range(n)])
        rems.append(rem)
        for r in rem:
            if bool(r > max_rem):
                max_rem = r
        # Sound (possibly loose) running bound for the next Picard box.
        # The self-referential kappa_nl*r_tot^2 slack is NOT added here:
        # with the interval Jacobian the mean-value form is exact for the
        # polynomial part, and the feedback would destroy the enclosure
        # (see prereg section 12).
        c_next = [arb(0) for _ in range(n)]
        for i in range(n):
            acc = arb(0)
            for j in range(n):
                acc = acc + jac[i][j].abs_upper() * c[j]
            c_next[i] = acc + rem[i] + t1._tol(EPS_SLACK)
            if bool(c_next[i] > max_run):
                max_run = c_next[i]
        m = m_next
        c = c_next

    return m, c, jacs, rems, max_rem, max_run


# ---------------------------------------------------------------------------
# continuous signed backward certificate
# ---------------------------------------------------------------------------


def certificate(
    jacs: list,
    rems: list[list[arb]],
    quads: list[arb],
    c_in: list[arb],
    upto: int,
    lo: int,
    n: int,
) -> tuple[list[arb], list[arb]]:
    """Checkpoint certificate at step ``upto`` via one continuous sweep.

    Sweeps ``k = upto-1 ... 0`` carrying the signed sensitivity product
    ``P = J_{upto-1} ... J_{k+1}`` in midpoint-radius form **across block
    boundaries**: a block is only a reporting checkpoint, never a reset of
    the product.  Resetting the product at each block boundary would compose
    per-block absolute-value bounds (``|P_B| * ... * |P_1|``), which discard
    the sign correlations between blocks and over-estimate the sensitivity of
    the periodic figure-eight flow by orders of magnitude -- the very scalar-
    norm pathology section 1 forbids, reappearing at the block interface
    (preregistration sections 2.1, 2.4, 11, 12).

    Returns ``(c_out, slack_weight)`` with

        c_out_i = sum_j |P[i,j]| * c_in_j
                + sum_k |P_k[i,j]| * (rems[k][j] + quads[k]),

    and ``slack_weight_i`` the backward weights of the current block's steps
    ``[lo, upto)`` only (used to insert the locked quadratic slack of section
    2.3 through this block's steps).
    """
    p_m = _identity(n)
    p_r = [[arb(0) for _ in range(n)] for _ in range(n)]
    c_out = [arb(0) for _ in range(n)]
    slack_weight = [arb(0) for _ in range(n)]
    for k in range(upto - 1, -1, -1):
        flat = jacs[k]
        jac = [[flat[i * n + j] for j in range(n)] for i in range(n)]
        m_k, r_k = _mr_split(jac)
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
        p_m, p_r = _mr_mul(p_m, p_r, m_k, r_k)

    # Incoming uncertainty at the global initial time (exact for S1-S4, kept
    # general so the identity of section 11 holds for inexact starts too).
    for i in range(n):
        acc = c_out[i]
        for j in range(n):
            acc = acc + (p_m[i][j].abs_upper() + p_r[i][j]) * c_in[j]
        c_out[i] = acc
    return c_out, slack_weight


# ---------------------------------------------------------------------------
# block integrator
# ---------------------------------------------------------------------------


def integrate_blocks(
    coeff_fn: CoeffFn,
    rhs_fn: RhsFn,
    m0: list[arb],
    h: arb,
    n_blocks: int,
    steps_per_block: int,
    order: int,
    include_remainder: bool = True,
    checkpoint_fn=None,
) -> dict:
    n = len(m0)
    m = list(m0)
    c = [arb(0) for _ in range(n)]  # forward seed: exact start for S1-S4
    c_in = list(c)
    jacs: list = []
    rems: list[list[arb]] = []
    quads: list[arb] = []
    checkpoints = []
    diags = []
    error = None
    for b in range(n_blocks):
        lo = b * steps_per_block
        try:
            m, c_run, j_new, r_new, max_rem, max_run = forward_block(
                coeff_fn,
                rhs_fn,
                m,
                c,
                h,
                steps_per_block,
                order,
                step_offset=lo,
                include_remainder=include_remainder,
            )
        except Exception as exc:  # noqa: BLE001 - record the failure verbatim
            error = str(exc)
            break
        jacs.extend(j_new)
        rems.extend(r_new)
        upto = lo + steps_per_block
        quads.extend([arb(0)] * steps_per_block)

        # Section 2.3 quadratic slack: computed once per block from the
        # *pre-slack* certificate radius of this checkpoint (no self-
        # reference; section 12), then inserted as a per-step noise radius
        # over this block's steps (section 10.3), so later checkpoints
        # propagate it like any other local error.
        c_pre, slack_weight = certificate(jacs, rems, quads, c_in, upto, lo, n)
        kappa_nl = _kappa_nl()
        radius = _max_arb(c_pre)
        slack = kappa_nl * radius * radius
        for k in range(lo, upto):
            quads[k] = slack
        c_out = [c_pre[i] + slack_weight[i] * slack for i in range(n)]

        diags.append(
            {
                "max_rem": max_rem,
                "max_run": max_run,
                "slack": slack,
                "slack_ok": bool(slack <= t1._tol("1e-30")),
                "block": b + 1,
            }
        )
        c = list(c_out)  # tight certificate seeds the next block's boxes
        if checkpoint_fn is not None:
            checkpoints.append(checkpoint_fn(m, c_out, b + 1))
    return {
        "m": m,
        "c": c,
        "checkpoints": checkpoints,
        "diags": diags,
        "error": error,
    }


def _state_box(m: list[arb], c: list[arb]) -> list[arb]:
    return [m[i] + arb(0, c[i]) for i in range(len(m))]


# ---------------------------------------------------------------------------
# systems S1-S4 (configs locked in the T1/T1b preregs)
# ---------------------------------------------------------------------------


def _run_s1(order: int, include_remainder: bool = True) -> dict:
    m0 = [t1._ball(1)]
    h = t1._ball(Fraction(1, 32))
    res = integrate_blocks(
        t1.coeffs_s1,
        t1.rhs_s1,
        m0,
        h,
        1,
        16,
        order,
        include_remainder=include_remainder,
    )
    m, c = res["m"], res["c"]
    endpoint = m[0] + arb(0, c[0])
    tol = "1e-12" if order == 16 else "1e-18"
    return {
        "order": order,
        "steps": 16,
        "h": h,
        "endpoint": endpoint,
        "width": t1._width(endpoint),
        "contains_2": t1._contains(endpoint, 2),
        "width_ok": bool(t1._width(endpoint) <= t1._tol(tol)),
        "include_remainder": include_remainder,
        "error": res["error"],
    }


def _run_s2() -> dict:
    m0 = [t1._ball(1), t1._ball(0)]
    h = arb.pi() / 32

    def checkpoint(m, c, block):
        state = _state_box(m, c)
        target = (-1, 0) if block == 1 else (1, 0)
        return {
            "step": block * 32,
            "state": state,
            "widths": [t1._width(s) for s in state],
            "contains": all(
                t1._contains(state[i], target[i]) for i in range(2)
            ),
            "width_ok": all(
                bool(t1._width(s) <= t1._tol("1e-20")) for s in state
            ),
        }

    res = integrate_blocks(
        t1.coeffs_s2, t1.rhs_s2, m0, h, 2, 32, ORDER, checkpoint_fn=checkpoint
    )
    return {"checkpoints": res["checkpoints"], "error": res["error"]}


def _run_s3() -> dict:
    m0 = [t1._ball(1), t1._ball(0), t1._ball(0), t1._ball(1)]
    h = 2 * arb.pi() / 256

    def checkpoint(m, c, block):
        state = _state_box(m, c)
        e = t1.energy_kepler(state)
        l = t1.angular_kepler(state)
        return {
            "step": block * 256,
            "energy": e,
            "angular": l,
            "energy_ok": t1._contains(e, Fraction(-1, 2)),
            "angular_ok": t1._contains(l, 1),
            "energy_width": t1._width(e),
            "angular_width": t1._width(l),
            "width_ok": bool(
                t1._width(e) <= t1._tol("1e-12")
                and t1._width(l) <= t1._tol("1e-12")
            ),
        }

    res = integrate_blocks(
        t1.coeffs_kepler,
        t1.rhs_kepler,
        m0,
        h,
        10,
        256,
        ORDER,
        checkpoint_fn=checkpoint,
    )
    return res


def _run_s4() -> dict:
    a = Fraction(347111, 10**6)
    b = Fraction(532728, 10**6)
    m0 = [
        t1._ball(-1),
        t1._ball(0),
        t1._ball(1),
        t1._ball(0),
        t1._ball(0),
        t1._ball(0),
        t1._ball(a),
        t1._ball(b),
        t1._ball(a),
        t1._ball(b),
        t1._ball(-2 * a),
        t1._ball(-2 * b),
    ]
    period = t1._ball(Fraction(632591398, 10**8))
    h = period / 512
    e0 = Fraction(-257428899017, 200000000000)

    def checkpoint(m, c, block):
        state = _state_box(m, c)
        e = t1.energy_three_body(state)
        l = t1.angular_three_body(state)
        com = t1.com_three_body(state)
        return {
            "step": block * 64,
            "energy": e,
            "angular": l,
            "com": com,
            "energy_ok": t1._contains(e, e0),
            "angular_ok": t1._contains(l, 0),
            "com_ok": all(t1._contains(x, 0) for x in com),
            "energy_width": t1._width(e),
            "width_ok": bool(t1._width(e) <= t1._tol("1e-10")),
        }

    res = integrate_blocks(
        t1.coeffs_three_body,
        t1.rhs_three_body,
        m0,
        h,
        8,
        64,
        ORDER,
        checkpoint_fn=checkpoint,
    )
    return res


# ---------------------------------------------------------------------------
# criteria C1-C7
# ---------------------------------------------------------------------------


def check_c1() -> dict:
    """C1 is the frozen T1 ball-primitive check (same generator, same data)."""
    return t1.check_c1()


def check_c2() -> dict:
    r16 = _run_s1(16)
    r24 = _run_s1(24)
    passed = bool(
        r16["error"] is None
        and r24["error"] is None
        and r16["contains_2"]
        and r24["contains_2"]
        and r16["width_ok"]
        and r24["width_ok"]
        and (r24["width"] * 10**4 <= r16["width"])
    )
    return {"passed": passed, "order16": r16, "order24": r24}


def check_c3() -> dict:
    res = _run_s2()
    checkpoints = {str(cp["step"]): cp for cp in res["checkpoints"]}
    passed = res["error"] is None and all(
        cp["contains"] and cp["width_ok"] for cp in checkpoints.values()
    )
    return {"passed": passed, "error": res["error"], "checkpoints": checkpoints}


def check_c4() -> dict:
    res = _run_s3()
    checkpoints = res["checkpoints"]
    # Section 2.3 obligation: kappa_nl * r_tot^2 <= 1e-30 for every block.
    # This gates the verdict; it is not a diagnostic that can be reported
    # alongside a PASS (preregistration sections 2.3, 5, 12.5).
    slack_ok = all(d["slack_ok"] for d in res["diags"])
    passed = (
        res["error"] is None
        and slack_ok
        and all(
            cp["energy_ok"] and cp["angular_ok"] and cp["width_ok"]
            for cp in checkpoints
        )
    )
    return {
        "passed": passed,
        "error": res["error"],
        "checkpoints": checkpoints,
        "diags": res["diags"],
        "section2_3_slack_ok": slack_ok,
    }


def check_c5() -> dict:
    res = _run_s4()
    checkpoints = res["checkpoints"]
    # Section 2.3 obligation gates the verdict here too (see check_c4).
    slack_ok = all(d["slack_ok"] for d in res["diags"])
    passed = (
        res["error"] is None
        and slack_ok
        and all(
            cp["energy_ok"] and cp["angular_ok"] and cp["com_ok"] and cp["width_ok"]
            for cp in checkpoints
        )
    )
    return {
        "passed": passed,
        "error": res["error"],
        "checkpoints": checkpoints,
        "diags": res["diags"],
        "section2_3_slack_ok": slack_ok,
    }


def check_c6() -> dict:
    """AST scan over the T1b module and the frozen T1 module."""
    hits = t1.ast_scan(Path(__file__).read_text(encoding="utf-8"))
    hits = hits + t1.ast_scan(Path(t1.__file__).read_text(encoding="utf-8"))
    return {
        "ast_scan_hits": hits,
        "ast_scan_passed": not hits,
        "t1_module_sha256lf": T1_MODULE_SHA,
    }


def _abort_step(text: str | None) -> int | None:
    if not text:
        return None
    parts = text.split()
    for i, part in enumerate(parts):
        if part == "step" and i + 1 < len(parts):
            token = parts[i + 1].rstrip(":")
            try:
                return int(token)
            except ValueError:
                return None
    return None


def check_c7() -> dict:
    """C7/M5: the frozen T1 scalar mechanism must reproduce its failure."""
    cps3, err3 = t1._run_s3()
    cps4, err4 = t1._run_s4()
    abort3 = _abort_step(err3)
    abort4 = _abort_step(err4)
    cp1024 = [cp for cp in cps3 if cp["step"] == 1024]
    cp1024_bad = bool(cp1024) and not cp1024[0]["width_ok"]
    c4_reproduced = bool(
        (abort3 is not None and abort3 <= C7_LIMIT_S3) or cp1024_bad
    )
    c5_reproduced = bool(abort4 is not None and abort4 <= C7_LIMIT_S4)
    return {
        "passed": bool(c4_reproduced and c5_reproduced),
        "c4_reproduced": c4_reproduced,
        "c5_reproduced": c5_reproduced,
        "s3_abort_step": abort3,
        "s4_abort_step": abort4,
        "s3_error": err3,
        "s4_error": err4,
        "limit_s3": C7_LIMIT_S3,
        "limit_s4": C7_LIMIT_S4,
        "mechanism": "frozen T1 scalar propagation via t1._run_s3/_run_s4",
    }


# ---------------------------------------------------------------------------
# campaign
# ---------------------------------------------------------------------------


def run_campaign() -> dict:
    with flint.ctx.workprec(PREC):
        c1 = check_c1()
        c2 = check_c2()
        c3 = check_c3()
        c4 = check_c4()
        c5 = check_c5()
        c6 = check_c6()
        c7 = check_c7()

        checks = {
            "C1": c1,
            "C2": c2,
            "C3": c3,
            "C4": c4,
            "C5": c5,
            "C6": c6,
            "C7": c7,
        }
        all_pass = all(
            [
                c1["passed"],
                c2["passed"],
                c3["passed"],
                c4["passed"],
                c5["passed"],
                c6["ast_scan_passed"],
                c7["passed"],
            ]
        )
        return {
            "schema": SCHEMA,
            "prereg_sha256lf": t1.sha256lf(PREREG_PATH),
            "t1_module_sha256lf": t1.sha256lf(Path(t1.__file__)),
            "python_flint": flint.__version__,
            "precision": PREC,
            "order": ORDER,
            "kappa_nl": KAPPA_NL_TEXT,
            "c7_limits": {"s3": C7_LIMIT_S3, "s4": C7_LIMIT_S4},
            "checks": t1._ser(checks),
            "summary": "ALL PASS" if all_pass else "SOME CHECKS FAILED",
            "all_pass": all_pass,
        }


def main() -> None:
    result = run_campaign()
    RECEIPT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    printable = {
        "summary": result["summary"],
        "all_pass": result["all_pass"],
        "prereg_sha256lf": result["prereg_sha256lf"],
        "receipt": str(RECEIPT_PATH),
    }
    print(json.dumps(printable, indent=2))


if __name__ == "__main__":
    main()


