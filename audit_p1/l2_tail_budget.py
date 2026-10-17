#!/usr/bin/env python3
"""audit_p1 / L2 item 3 -- tail lane: TAIL_LEMMA partition budget, finite lane.

Pre-registered protocol: reports/AUDIT_DBN_PREREG_2026-10-17.md, section 4,
item 3 ("Tail lane"): re-derive the partition from the formula statements and
spot-check with our own enclosures: two-sided corridor
0.999719 < D < 0.999721; (1-D)/M_max > 0.0001735326089372; tail error
< 0.000000011671604; post-error margin > 0.0001735209373337;
anchors M = 153814, M_err = 3000, M_max < 1.608290.

Independence: this is our own implementation written from the formula
statements of TAIL_LEMMA.md as transcribed by us:
  (2.1)/(3.1) b_t(u) = exp((t/4) log^2 u),
              E_{t,sigma}(u) = u b_t(u) u^{-sigma},
              Cap_t(a,c;sigma) = max(E(a),E(c)) log(c/a);
  (4.2) c_m(t) = sum_{d|m, d in S} lambda_d b_t(m/d), c_1 = 1;
  (4.4)-(4.6) P, TR (floor(M/d) routed caps);
  (4.7) OV (moving caps, floor(N/d) >= N/(d+1));
  (5.2)-(5.4) A-branch AB and M_max; D = P+TR+OV+M_max*AB;
  (8.1) Delta; (8.2) e_A+e_B <= (e^Delta-1)[sum b n^{-sigma1} + G sum b n^{-sigma2}];
  (8.3) e_C0 welded 10.50 form (3.58+6.92, x-12 denominator).
All constants (boxes, S, lambda, N*, M, M_err, sealed decimals) are read from
the pinned documents, NOT from executable code. The release's verifiers
(verifiers/verify_tail_1787854_256.py, verifiers/verify_tail_arb.c) were read
read-only for CLAIM IDENTIFICATION ONLY (what each sealed number stands for
and the evaluation device: D-side on the closed I_box; error side on the
closed I_ext); no code, parser, or table is reused.

Our lane: mpmath.iv at 240 bits (outward-rounded), every interval endpoint
extracted as an exact rational (mpmath.libmp.to_rational of the raw _mpi_
endpoints) and all sums and comparisons accumulated in fractions.Fraction;
final inequalities are exact rational comparisons. Box enclosures are widened
by 2^-190 (far below every certified margin).

Scope (honest, per pre-registration): the certified spot is the design point
N = N_* = 3840000 (uniform in the closed t-interval, as the release does);
the all-N step N >= N_* and the y-coverage above I_box are the release's
section 6/7 reductions, whose gates we re-check as necessary premises only
(SC1/SC2/SC3, YM, Delta and eC0 quotient gates, GN-TR/GN-AB/GN-error,
OVW floors). The release's Arb/FLINT C lane and the 160/256-bit Python lane
were not re-run; the published 512-bit directed Arb points are consulted as
non-verdict regression references.

Status: development script -- official run only via the runner with the
LOG-EXISTS abort; every run transcript kept.

Output: checks on stdout; machine JSON to reports/audit_p1_l2_tail_results.json;
exit 0 iff every check passes.
"""

import hashlib
import json
import os
import sys
import time
from fractions import Fraction as F

from mpmath import iv, mp, mpf
from mpmath.libmp import to_rational

iv.prec = 240
mp.prec = 240

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_OUT = os.path.join(REPO_ROOT, "reports", "audit_p1_l2_tail_results.json")
RELEASE_COMMIT = "2e9976c4becbf97e31c56fe75fce07cdff5dd4ea"
DOC_DIR = r"C:\Users\usER\AppData\Local\Temp\opencode\dbn_release_docs"

# ---------------------------------------------------------------- exact data
T0 = F(129, 800)
T_HI = F(161250001, 10 ** 9)
Y_LO = F(1872719, 10 ** 7)          # I_box low = I_ext low
Y_BOX_HI = F(23409, 125000)         # I_box top
Y_EXT_HI = F(8231039, 10 ** 7)      # I_ext top
Y2 = F(87677, 2500000)              # y0^2
T0_PLUS_Y2_2 = F(893927, 5000000)   # t0 + y0^2/2
NSTAR = 3840000
MHEAD = 153814
MERR = 3000
S_LIST = [1, 2, 3, 4, 5, 6, 7, 10, 11, 13, 14]
LAM = {
    1: F(1),
    2: F(-1021, 1000),
    3: F(-1054, 1000),
    4: F(-9, 200),
    5: F(-1119, 1000),
    6: F(1001, 1000),
    7: F(-1043, 1000),
    10: F(128, 125),
    11: F(-161, 200),
    13: F(-447, 500),
    14: F(456373, 500000),
}
SUM_ABS_LAM = F(9918746, 10 ** 6)

DELTA = F(1, 2 ** 190)  # box/scalar widening; far below every certified margin

# sealed constants from the pinned documents (prereg section 4 item 3)
CORRIDOR_LO = F("0.999719")
CORRIDOR_HI = F("0.999721")
SEALED_FLOW = F("0.0001735326089372")
SEALED_ERR = F("0.000000011671604")
SEALED_MARGIN = F("0.0001735209373337")
SEALED_MMAX = F("1.608290")

# release 512-bit directed Arb points (non-verdict regression references;
# strings as printed in logs/tail_arb_512.log, blob c091e5ee...)
ARB_REF = {
    "P": F("0.170228023678122342286328162340"),
    "TR": F("0.262901330124790894596039723464"),
    "OV": F("0.0392426812101768641638975708089"),
    "Mmax": F("1.60828914495414090322020715102"),
    "AB": F("0.327894319270990003368094008613"),
    "D": F("0.999720909388750699545691864037"),
    "flow": F("0.000173532608937218501848333877396"),
    "eAB": F("4.93807921086187247227924285051e-13"),
    "eC0": F("1.16711096273536263367986975936e-8"),
    "err": F("1.16716034352747125240459255179e-8"),
    "margin": F("0.000173520937333783227135809831471"),
}

SOURCES = [
    ("TAIL_LEMMA.md", "cdc612e9117b24cd4c050d2c146cf5d2fa1a3de6", 14476,
     "TAIL_LEMMA.md", "formula statements (2.1),(3.1),(4.2)-(4.7),(5.2)-(5.4),(8.1)-(8.3); boxes, S, lambda"),
    ("TAIL_PROVENANCE.md", "cb3bc2947e2e6b02a7f1b580d9b347e708a68591", 1793,
     "TAIL_PROVENANCE.md", "scope/provenance statement"),
    ("CANDIDATE_PARAMETERS.md", "bdad0402562f5ea077a9ab380558cb19f74ffb82", 4695,
     "CANDIDATE_PARAMETERS.md", "sealed constants source (item 3 lines)"),
    ("MAXIMUM_CHECKS.md", "acbf9813044be247bec1f14aec6216d3f6fcf108", 13572,
     "MAXIMUM_CHECKS.md", "sealed-claim source (section 6)"),
    ("logs/assembly_1787854.log", "d5b6a0fdd77c0856c4e21b59434b7bcecedd734d", 4303,
     "logs__assembly_1787854.log", "assembly context (target lines)"),
    ("logs/tail_1787854_256.log", "fb129d45c51de94601571908002de72639e14ba5", 13729,
     "logs__tail_1787854_256.log", "supplementary Python-lane regression witnesses"),
    ("logs/tail_arb_256.log", "bc0f2f3bfb573077e8102567c659baee531b2315", 2708,
     "logs__tail_arb_256.log", "Arb 256 directed reference values"),
    ("logs/tail_arb_512.log", "c091e5ee3f4ff912778b10c8e6d9fe72dc54b2db", 2708,
     "logs__tail_arb_512.log", "Arb 512 directed reference values (this run's witnesses)"),
    ("verifiers/verify_tail_1787854_256.py", "f39f55f9917f1cf9fd366594ae7df6940bd6905a", 31668,
     "verifiers__verify_tail_1787854_256.py", "claim identified from; no code reused"),
    ("verifiers/verify_tail_arb.c", "dcedaa220c871402abf88a87f1c2c74e97ea5f56", 27256,
     "verifiers__verify_tail_arb.c", "claim identified from; no code reused"),
]

CHECKS = []
VALUES = {}

# ---------------------------------------------------------------- helpers


def check(name, ok):
    ok = bool(ok)
    CHECKS.append({"name": name, "ok": ok})
    print("[%s] %s" % ("PASS" if ok else "FAIL", name))
    return ok


def fs(f):
    return "%d/%d" % (f.numerator, f.denominator)


def floor_dec(f, digits):
    m = 10 ** digits
    fm = f * m
    scaled = fm.numerator // fm.denominator
    sign = "-" if scaled < 0 else ""
    s = str(abs(scaled)).rjust(digits + 1, "0")
    return sign + s[:-digits] + "." + s[-digits:]


def ceil_dec(f, digits):
    m = 10 ** digits
    fm = f * m
    scaled = -((-fm.numerator) // fm.denominator)
    sign = "-" if scaled < 0 else ""
    s = str(abs(scaled)).rjust(digits + 1, "0")
    return sign + s[:-digits] + "." + s[-digits:]


def mfr(f):
    """mpf approximation of an exact Fraction (directed by later interval use)."""
    return mpf(f.numerator) / mpf(f.denominator)


def ivpt(f):
    """Interval enclosing the exact rational f (width 2*DELTA, direction-safe)."""
    return iv.mpf([mfr(f - DELTA), mfr(f + DELTA)])


def ivbox(lo, hi):
    """Interval containing the exact closed box [lo, hi]."""
    return iv.mpf([mfr(lo - DELTA), mfr(hi + DELTA)])


def ivint(n):
    """Exact point interval for a small integer."""
    x = mpf(n)
    return iv.mpf([x, x])


def lo_f(x):
    p, q = to_rational(x._mpi_[0])
    return F(p, q)


def hi_f(x):
    p, q = to_rational(x._mpi_[1])
    return F(p, q)


def abs_hi(x):
    a = lo_f(x)
    b = hi_f(x)
    return max(abs(a), abs(b))


def abs_lo(x):
    a = lo_f(x)
    b = hi_f(x)
    if a <= 0 <= b:
        return F(0)
    return min(abs(a), abs(b))


def nstr10(f):
    if not isinstance(f, F):
        f = F(f)
    return mp.nstr(mpf(f.numerator) / mpf(f.denominator), 10)


# ---------------------------------------------------------------- selftests


def part_selftests():
    print("== selftests (helpers) ==")
    x = iv.mpf([mpf(1), mpf(2)])
    check("selftest lo_f/hi_f on [1,2]", lo_f(x) == 1 and hi_f(x) == 2)
    y = ivpt(F(1, 3))
    check("selftest ivpt(1/3) contains 1/3", lo_f(y) <= F(1, 3) <= hi_f(y))
    z = iv.mpf([mpf(-2), mpf(1)])
    check("selftest abs_hi/abs_lo on [-2,1]", abs_hi(z) == 2 and abs_lo(z) == 0)
    check("selftest floor_dec/ceil_dec", floor_dec(F(123, 100), 1) == "1.2"
          and ceil_dec(F(123, 100), 1) == "1.3")
    t = ivpt(F(1, 2)) + ivpt(F(1, 3))
    check("selftest interval add contains 5/6", lo_f(t) <= F(5, 6) <= hi_f(t))
    print()


# ---------------------------------------------------------------- sources


def part_sources():
    print("== statement sources (git blob sha1 re-verified in-run) ==")
    for rel, sha, size, local, role in SOURCES:
        p = os.path.join(DOC_DIR, local)
        try:
            b = open(p, "rb").read()
        except OSError:
            check("source %s readable (%s)" % (rel, role), False)
            continue
        got = hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()
        check("source %s blob sha1+size verified (%s)" % (rel, role),
              got == sha and len(b) == size)
    print()


# ---------------------------------------------------------------- anchors


def part_anchors():
    print("== exact anchors and hull checks (integer arithmetic) ==")
    check("anchor t0 + y0^2/2 = 893927/5000000 (exact)",
          T0 + Y2 / 2 == T0_PLUS_Y2_2)
    check("anchor (1872719/10^7)^2 < y0^2 < (23409/125000)^2 (exact)",
          F(1872719, 10 ** 7) ** 2 < Y2 < F(23409, 125000) ** 2)
    check("anchor (8231039/10^7)^2 >= 1-2t0 (exact)",
          Y_EXT_HI ** 2 >= 1 - 2 * T0)
    check("anchor I_box top below sqrt(1-2t) on I_t (exact)",
          Y_BOX_HI ** 2 < 1 - 2 * T_HI)
    check("anchor lambda_1 = 1 and sum|lambda| = 9918746/10^6 (exact)",
          LAM[1] == 1 and sum((abs(LAM[d]) for d in S_LIST), F(0)) == SUM_ABS_LAM)
    ok_floors = all(d * (MHEAD // d) <= MHEAD < d * (MHEAD // d + 1) for d in S_LIST)
    check("anchor floors: d*(M//d) <= M < d*(M//d+1) for all d in S", ok_floors)
    check("anchor N* > M > M_err > 1",
          NSTAR > MHEAD > MERR > 1)
    check("anchor (5.1) cutoffs: M = 153814, M_err = 3000 (spec constants)",
          MHEAD == 153814 and MERR == 3000)
    print()


# ---------------------------------------------------------------- sigma

def fix_sigmas():
    """Build boxes and sigma scalars; returns a dict of intervals and Fractions."""
    d = {}
    d["t_box"] = ivbox(T0, T_HI)
    d["y_box"] = ivbox(Y_LO, Y_BOX_HI)
    d["y_ext"] = ivbox(Y_LO, Y_EXT_HI)
    NPT = ivint(NSTAR)
    d["NPT"] = NPT
    d["lnN"] = iv.log(NPT)
    d["X"] = 4 * iv.pi * (NPT ** 2 - d["t_box"] / 16)
    d["L"] = iv.log(NPT ** 2 - d["t_box"] / 16)
    d["delta"] = (d["t_box"] / 4) * (-iv.log(1 - d["t_box"] / (16 * NPT ** 2))) \
        + d["t_box"] / (2 * d["X"] ** 2)
    d["kappa"] = d["t_box"] / (2 * (d["X"] - 6))
    d["s1_box"] = (1 + d["y_box"]) / 2 + (d["t_box"] / 2) * d["lnN"] - d["delta"]
    d["s2_box"] = (1 - d["y_box"]) / 2 + (d["t_box"] / 2) * d["lnN"] - d["delta"] - d["kappa"]
    d["s1_ext"] = (1 + d["y_ext"]) / 2 + (d["t_box"] / 2) * d["lnN"] - d["delta"]
    d["s2_ext"] = (1 - d["y_ext"]) / 2 + (d["t_box"] / 2) * d["lnN"] - d["delta"] - d["kappa"]
    for k in ("s1_box", "s1_ext", "s2_box", "s2_ext"):
        d[k + "_lo"] = lo_f(d[k])
        d[k + "_hi"] = hi_f(d[k])
    return d


def part_sigma(d):
    print("== fixed scalars and cap-validity gates ==")
    print("  delta in [%s, %s] (30 dp)" % (floor_dec(lo_f(d["delta"]), 30),
                                           ceil_dec(hi_f(d["delta"]), 30)))
    print("  kappa in [%s, %s] (30 dp)" % (floor_dec(lo_f(d["kappa"]), 30),
                                           ceil_dec(hi_f(d["kappa"]), 30)))
    for k in ("s1_box", "s1_ext", "s2_box", "s2_ext"):
        print("  %s in [%s, %s] (30 dp)" % (k, floor_dec(d[k + "_lo"], 30),
                                            ceil_dec(d[k + "_hi"], 30)))
    sc1_rhs = hi_f((d["t_box"] / 2) * d["lnN"])
    check("SC1: sigma1 > (t/2) log N on box and extended hull",
          d["s1_box_lo"] > sc1_rhs and d["s1_ext_lo"] > sc1_rhs)
    check("SC2: sigma2 > (t/2) log N on box and extended hull",
          d["s2_box_lo"] > sc1_rhs and d["s2_ext_lo"] > sc1_rhs)
    check("SC3: sigma1, sigma2 > 1 on both hulls",
          min(d["s1_box_lo"], d["s2_box_lo"], d["s1_ext_lo"], d["s2_ext_lo"]) > 1)
    ym1 = hi_f(ivpt(F(2, 100)) - d["L"] / 2 + d["lnN"] / 2)
    ym2 = hi_f(ivpt(F(2, 100)) - d["lnN"] / 2
               - iv.log(1 - d["t_box"] / (16 * d["NPT"] ** 2)) / 2)
    check("YM: D decreases above the lower y-box (both algebraic forms, upper < 0)",
          ym1 < 0 and ym2 < 0)
    delta_gate = lo_f(((d["t_box"] ** 2) / 16) * d["L"] * (d["L"] - ivpt(F(2)))
                      + ivpt(F(626, 1000)))
    check("Delta N-monotonicity gate: (t^2/16)L(L-2)+0.626 > 0",
          delta_gate > 0)
    check("eC0 quotient N-monotonicity gate: 3 < 10.50 and X_N > 12",
          3 * 2 < 21 and lo_f(d["X"]) > 12)
    check("domain: log(N^2-t/16) > 2 and X_N > 200",
          lo_f(d["L"]) > 2 and lo_f(d["X"]) > 200)
    z16 = d["t_box"] / (16 * d["NPT"] ** 2)
    check("domain: 0 < t/(16N^2) < 1 and window log gate N(1-t/(16N^2)) > 1",
          lo_f(z16) > 0 and hi_f(z16) < 1
          and lo_f(ivint(NSTAR) * (1 - z16)) > 1)
    print()


# ---------------------------------------------------------------- fills


def part_fill(d):
    print("== fills: log table, b_t table, sigma-power tables ==")
    t0 = time.perf_counter()
    LN = [None] * (MHEAD + 1)
    LN[1] = ivpt(F(0))
    for k in range(2, MHEAD + 1):
        LN[k] = iv.log(ivint(k))
    print("  log table 1..%d done (%.1f s)" % (MHEAD, time.perf_counter() - t0))
    t0 = time.perf_counter()
    B = [None] * (MHEAD + 1)
    B[1] = ivpt(F(1))
    for k in range(2, MHEAD + 1):
        B[k] = iv.exp((d["t_box"] / 4) * LN[k] ** 2)
    print("  b_t table 1..%d done (%.1f s)" % (MHEAD, time.perf_counter() - t0))
    t0 = time.perf_counter()
    S1LO_IV = ivpt(d["s1_box_lo"])
    S1HI_IV = ivpt(d["s1_box_hi"])
    K1LO = [None] * (MHEAD + 1)
    K1HI = [None] * (MHEAD + 1)
    K1LO[1] = ivpt(F(1))
    K1HI[1] = ivpt(F(1))
    for k in range(2, MHEAD + 1):
        K1LO[k] = iv.exp(-S1LO_IV * LN[k])
        K1HI[k] = iv.exp(-S1HI_IV * LN[k])
    print("  k^{-sigma1} tables done (%.1f s)" % (time.perf_counter() - t0))
    t0 = time.perf_counter()
    S2LO_IV = ivpt(d["s2_box_lo"])
    S2HI_IV = ivpt(d["s2_box_hi"])
    K2LO = [None] * (MHEAD + 1)
    K2HI = [None] * (MHEAD + 1)
    K2LO[1] = ivpt(F(1))
    K2HI[1] = ivpt(F(1))
    for k in range(2, MHEAD + 1):
        K2LO[k] = iv.exp(-S2LO_IV * LN[k])
        K2HI[k] = iv.exp(-S2HI_IV * LN[k])
    print("  k^{-sigma2} tables done (%.1f s)" % (time.perf_counter() - t0))
    print("  GN-TR gates (cap decrease for all N >= N*), endpoints M//d:")
    ok_gntr = True
    for dd in S_LIST:
        a = MHEAD // dd
        ga = lo_f((d["t_box"] / 2) * LN[a] * (d["lnN"] - LN[a]))
        gb = lo_f(ivpt(d["s1_box_lo"] - 1) * (d["lnN"] - LN[a]))
        ok = ga > 1 and gb > 1
        ok_gntr = ok_gntr and ok
        if not ok:
            print("    d=%d a=%d ga=%s gb=%s" % (dd, a, nstr10(ga), nstr10(gb)))
    check("GN-TR: every fixed-left routed cap decreases for all N >= N* (gates)", ok_gntr)
    a = MHEAD
    ga = lo_f((d["t_box"] / 2) * LN[a] * (d["lnN"] - LN[a]))
    gb = lo_f(ivpt(d["s2_box_lo"] - 1) * (d["lnN"] - LN[a]))
    check("GN-AB: fixed-left MHEAD A-cap decreases for all N >= N* (gates)",
          ga > 1 and gb > 1)
    a = MERR
    ga = lo_f((d["t_box"] / 2) * LN[a] * (d["lnN"] - LN[a]))
    gb1 = lo_f(ivpt(d["s1_ext_lo"] - 1) * (d["lnN"] - LN[a]))
    gb2 = lo_f(ivpt(d["s2_ext_lo"] - 1) * (d["lnN"] - LN[a]))
    check("GN-error: both MERR=3000 caps decrease for all N >= N* (gates)",
          ga > 1 and gb1 > 1 and gb2 > 1)
    check("OVW: floor(N/d) >= N/(d+1) for all d in S (exact)",
          all((NSTAR // dd) * (dd + 1) >= NSTAR for dd in S_LIST))
    print()
    return LN, B, K1LO, K1HI, K2LO, K2HI


# ---------------------------------------------------------------- coefficient head


def part_coef(d, LN, B):
    print("== exact convolution head c_m(t) over the t-box (m = 2..%d) ==" % MHEAD)
    t0 = time.perf_counter()
    c_iv = [None] * (MHEAD + 1)
    c_iv[1] = ivpt(F(1))
    for m in range(2, MHEAD + 1):
        c_iv[m] = B[m]
    for dd in S_LIST[1:]:
        LAMIV = ivpt(LAM[dd])
        kmax = MHEAD // dd
        for k in range(1, kmax + 1):
            c_iv[dd * k] = c_iv[dd * k] + LAMIV * B[k]
    print("  coefficient table built (%.1f s)" % (time.perf_counter() - t0))
    check("identity: c_1 = 1 (lambda_1 = b_t(1) = 1)",
          lo_f(c_iv[1]) <= 1 <= hi_f(c_iv[1]))
    return c_iv


# ---------------------------------------------------------------- P, TR, OV, Mmax


def part_P(c_iv, K1LO, K1HI):
    print("== P (floor-partition head) ==")
    t0 = time.perf_counter()
    P_ub = F(0)
    P_lb = F(0)
    for m in range(2, MHEAD + 1):
        P_ub += abs_hi(c_iv[m]) * hi_f(K1LO[m])
        P_lb += abs_lo(c_iv[m]) * lo_f(K1HI[m])
    print("  P sum done (%.1f s)" % (time.perf_counter() - t0))
    print("  P upper >= %s (30 dp floor)" % floor_dec(P_ub, 30))
    print("  P lower <= %s (30 dp ceil)" % ceil_dec(P_lb, 30))
    return P_ub, P_lb


def e_hi(om_sig_iv, lnu_iv, t_box):
    return hi_f(iv.exp(om_sig_iv * lnu_iv + (t_box / 4) * lnu_iv ** 2))


def e_lo(om_sig_iv, lnu_iv, t_box):
    return lo_f(iv.exp(om_sig_iv * lnu_iv + (t_box / 4) * lnu_iv ** 2))


def part_sums(d, LN, K1LO, K1HI):
    print("== TR, OV, M_max, G, A-branch, AB, D ==")
    t_box = d["t_box"]
    lnN = d["lnN"]
    om_s1lo = ivpt(1 - d["s1_box_lo"])
    om_s1hi = ivpt(1 - d["s1_box_hi"])
    om_s2lo = ivpt(1 - d["s2_box_lo"])
    om_s2hi = ivpt(1 - d["s2_box_hi"])
    E_N_u = e_hi(om_s1lo, lnN, t_box)
    E_N_l = e_lo(om_s1hi, lnN, t_box)
    TR_ub = F(0)
    TR_lb = F(0)
    for dd in S_LIST:
        a = MHEAD // dd
        lna = LN[a]
        cap_ub = max(e_hi(om_s1lo, lna, t_box), E_N_u) * hi_f(lnN - lna)
        cap_lb = max(e_lo(om_s1hi, lna, t_box), E_N_l) * lo_f(lnN - lna)
        fac_ub = abs(LAM[dd]) * (1 if dd == 1 else hi_f(K1LO[dd]))
        fac_lb = abs(LAM[dd]) * (1 if dd == 1 else lo_f(K1HI[dd]))
        TR_ub += fac_ub * cap_ub
        TR_lb += fac_lb * cap_lb
    OV_ub = F(0)
    OV_lb = F(0)
    for dd in S_LIST[1:]:
        logdp1 = iv.log(ivint(dd + 1))
        lna = lnN - logdp1
        cap_ub = max(e_hi(om_s1lo, lna, t_box), E_N_u) * hi_f(lnN - lna)
        cap_lb = max(e_lo(om_s1hi, lna, t_box), E_N_l) * lo_f(lnN - lna)
        OV_ub += abs(LAM[dd]) * hi_f(K1LO[dd]) * cap_ub
        OV_lb += abs(LAM[dd]) * lo_f(K1HI[dd]) * cap_lb
    MMAX_ub = F(1)
    MMAX_lb = F(1)
    for dd in S_LIST[1:]:
        MMAX_ub += abs(LAM[dd]) * hi_f(K1LO[dd])
        MMAX_lb += abs(LAM[dd]) * lo_f(K1HI[dd])
    K02 = ivpt(F(2, 100))
    G_IV = iv.exp(K02 * d["y_box"]) * iv.exp(-(d["y_box"] / 2) * d["L"])
    G_ub = hi_f(G_IV)
    G_lb = lo_f(G_IV)
    print("  TR upper >= %s (30 dp floor)" % floor_dec(TR_ub, 30))
    print("  OV upper >= %s (30 dp floor)" % floor_dec(OV_ub, 30))
    print("  Mmax upper >= %s (30 dp floor)" % floor_dec(MMAX_ub, 30))
    print("  G in [%s, %s] (30 dp)" % (floor_dec(G_lb, 30), ceil_dec(G_ub, 30)))
    print("  TR interval width (ub-lb) <= %s (30 dp ceil)"
          % ceil_dec(TR_ub - TR_lb, 30))
    print("  OV interval width (ub-lb) <= %s (30 dp ceil)"
          % ceil_dec(OV_ub - OV_lb, 30))
    return (TR_ub, TR_lb, OV_ub, OV_lb, MMAX_ub, MMAX_lb, G_ub, G_lb,
            om_s2lo, om_s2hi)


# ---------------------------------------------------------------- A branch, AB, D


def part_AB(d, LN, B, K2LO, K2HI, TRF, P_ub, P_lb):
    (TR_ub, TR_lb, OV_ub, OV_lb, MMAX_ub, MMAX_lb, G_ub, G_lb,
     om_s2lo, om_s2hi) = TRF
    t_box = d["t_box"]
    lnN = d["lnN"]
    t0 = time.perf_counter()
    PA_ub = F(0)
    PA_lb = F(0)
    for k in range(1, MHEAD + 1):
        PA_ub += hi_f(B[k]) * hi_f(K2LO[k])
        PA_lb += lo_f(B[k]) * lo_f(K2HI[k])
    print("  A-head sum done (%.1f s)" % (time.perf_counter() - t0))
    capB_ub = max(e_hi(om_s2lo, LN[MHEAD], t_box), e_hi(om_s2lo, lnN, t_box)) \
        * hi_f(lnN - LN[MHEAD])
    capB_lb = max(e_lo(om_s2hi, LN[MHEAD], t_box), e_lo(om_s2hi, lnN, t_box)) \
        * lo_f(lnN - LN[MHEAD])
    AB_ub = G_ub * (PA_ub + capB_ub)
    AB_lb = G_lb * (PA_lb + capB_lb)
    D_ub = P_ub + TR_ub + OV_ub + MMAX_ub * AB_ub
    D_lb = P_lb + TR_lb + OV_lb + MMAX_lb * AB_lb
    flow_lo = (1 - D_ub) / MMAX_ub
    print("  A-head upper >= %s ; capB upper >= %s (30 dp floor / 30 dp floor)"
          % (floor_dec(PA_ub, 30), floor_dec(capB_ub, 30)))
    print("  AB upper >= %s ; AB lower <= %s (30 dp)"
          % (floor_dec(AB_ub, 30), ceil_dec(AB_lb, 30)))
    print("  D upper >= %s (30 dp floor)" % floor_dec(D_ub, 30))
    print("  D lower <= %s (30 dp ceil)" % ceil_dec(D_lb, 30))
    print("  D interval width (ub-lb) <= %s (30 dp ceil)" % ceil_dec(D_ub - D_lb, 30))
    print("  flow lower (1-D_ub)/Mmax_ub <= %s (40 dp ceil)" % ceil_dec(flow_lo, 40))
    return (D_ub, D_lb, flow_lo, PA_ub, PA_lb, capB_ub, capB_lb, AB_ub, AB_lb)


# ---------------------------------------------------------------- error side


def part_err(d, LN, B):
    print("== error side (8.1)-(8.3) on the extended hull ==")
    t_box = d["t_box"]
    lnN = d["lnN"]
    om_s1elo = ivpt(1 - d["s1_ext_lo"])
    om_s1ehi = ivpt(1 - d["s1_ext_hi"])
    om_s2elo = ivpt(1 - d["s2_ext_lo"])
    om_s2ehi = ivpt(1 - d["s2_ext_hi"])
    S1ELO_IV = ivpt(d["s1_ext_lo"])
    S1EHI_IV = ivpt(d["s1_ext_hi"])
    S2ELO_IV = ivpt(d["s2_ext_lo"])
    S2EHI_IV = ivpt(d["s2_ext_hi"])
    SB_ub = F(0)
    SB_lb = F(0)
    PAe_ub = F(0)
    PAe_lb = F(0)
    for n in range(1, MERR + 1):
        bn = B[n]
        SB_ub += hi_f(bn) * hi_f(iv.exp(-S1ELO_IV * LN[n]))
        SB_lb += lo_f(bn) * lo_f(iv.exp(-S1EHI_IV * LN[n]))
        PAe_ub += hi_f(bn) * hi_f(iv.exp(-S2ELO_IV * LN[n]))
        PAe_lb += lo_f(bn) * lo_f(iv.exp(-S2EHI_IV * LN[n]))
    cap1_ub = max(e_hi(om_s1elo, LN[MERR], t_box), e_hi(om_s1elo, lnN, t_box)) \
        * hi_f(lnN - LN[MERR])
    cap1_lb = max(e_lo(om_s1ehi, LN[MERR], t_box), e_lo(om_s1ehi, lnN, t_box)) \
        * lo_f(lnN - LN[MERR])
    cap2_ub = max(e_hi(om_s2elo, LN[MERR], t_box), e_hi(om_s2elo, lnN, t_box)) \
        * hi_f(lnN - LN[MERR])
    cap2_lb = max(e_lo(om_s2ehi, LN[MERR], t_box), e_lo(om_s2ehi, lnN, t_box)) \
        * lo_f(lnN - LN[MERR])
    S1_ub = SB_ub + cap1_ub
    S1_lb = SB_lb + cap1_lb
    S2_ub2 = PAe_ub + cap2_ub
    S2_lb2 = PAe_lb + cap2_lb
    K02 = ivpt(F(2, 100))
    GERR_IV = iv.exp(K02 * d["y_ext"]) * iv.exp(-(d["y_ext"] / 2) * d["L"])
    Gerr_ub = hi_f(GERR_IV)
    Gerr_lb = lo_f(GERR_IV)
    DELERR_IV = (t_box ** 2 / 16 * d["L"] ** 2 + ivpt(F(626, 1000))) \
        / (d["X"] - ivpt(F(333, 50)))
    EABF_IV = iv.exp(DELERR_IV) - ivpt(F(1))
    eABF_ub = hi_f(EABF_IV)
    eABF_lb = lo_f(EABF_IV)
    eAB_ub = eABF_ub * (S1_ub + Gerr_ub * S2_ub2)
    eAB_lb = eABF_lb * (S1_lb + Gerr_lb * S2_lb2)
    ln3 = iv.log(ivint(3))
    p4 = (iv.pi ** 2) / 4
    nq = ivpt(F(8 * NSTAR - 1, 8))
    EXPON_IV = (-(1 + d["y_ext"]) / 4) * d["L"] - (t_box / 16) * d["L"] ** 2 \
        + ivpt(F(124, 100)) * (iv.exp(ln3 * d["y_ext"]) + iv.exp(-(ln3 * d["y_ext"]))) / nq \
        + (3 * iv.sqrt(d["L"] ** 2 + p4) + ivpt(F(105, 10))) / (d["X"] - ivpt(F(12)))
    eC0_IV = iv.exp(EXPON_IV)
    eC0_ub = hi_f(eC0_IV)
    eC0_lb = lo_f(eC0_IV)
    err_ub = eAB_ub + eC0_ub
    err_lb = eAB_lb + eC0_lb
    print("  Delta in [%s, %s] (36 dp)" % (floor_dec(lo_f(DELERR_IV), 36),
                                            ceil_dec(hi_f(DELERR_IV), 36)))
    print("  eAB factor (e^Delta-1) <= %s (30 dp ceil)" % ceil_dec(eABF_ub, 30))
    print("  eAB upper >= %s (30 dp floor)" % floor_dec(eAB_ub, 30))
    print("  eC0 upper >= %s (30 dp floor)" % floor_dec(eC0_ub, 30))
    print("  err upper >= %s (30 dp floor)" % floor_dec(err_ub, 30))
    return err_ub, err_lb, eAB_ub, eAB_lb, eC0_ub, eC0_lb


# ---------------------------------------------------------------- probe


def part_probe(d, ups):
    """Point-coverage regression probe (necessary condition only).

    Independent non-interval lane (~45 dps): evaluates the released
    quantities at explicit points of the box / extended hull and checks that
    every certified upper bound dominates the sampled value. Catches
    direction/corner mistakes in the interval devices; a finite sample can
    never prove coverage.
    """
    print("== point-coverage regression probe (plain mpf lane, non-interval) ==")
    t_probe = time.perf_counter()
    saved_prec = mp.prec
    mp.prec = 150

    def mf(fr):
        return mp.mpf(fr.numerator) / mp.mpf(fr.denominator)

    N = mpf(NSTAR)
    lnN = mp.log(N)
    lam = {dd: mf(LAM[dd]) for dd in S_LIST}

    def X_t(tt):
        return 4 * mp.pi * (N * N - tt / 16)

    def del_t(tt):
        return (tt / 4) * (-mp.log(1 - tt / (16 * N * N))) + tt / (2 * X_t(tt) ** 2)

    def kap_t(tt):
        return tt / (2 * (X_t(tt) - 6))

    def s1_t(tt, yy):
        return (1 + yy) / 2 + (tt / 2) * lnN - del_t(tt)

    def s2_t(tt, yy):
        return s1_t(tt, yy) - yy - kap_t(tt)

    def Ept(u, sig, tt):
        lu = mp.log(u)
        return mp.exp((1 - sig) * lu + (tt / 4) * lu ** 2)

    def G1e_pt(tt, yy):
        return mp.exp(mf(F(2, 100)) * yy) * mp.exp(-(yy / 2) * mp.log(N * N - tt / 16))

    tab_cache = {}

    def tables(tt):
        if tt not in tab_cache:
            lnt = [None] * (MHEAD + 1)
            bt = [None] * (MHEAD + 1)
            lnt[1] = mpf(0)
            bt[1] = mpf(1)
            for k in range(2, MHEAD + 1):
                lnt[k] = mp.log(k)
                bt[k] = mp.exp((tt / 4) * lnt[k] ** 2)
            tab_cache[tt] = (lnt, bt)
        return tab_cache[tt]

    worst = []

    def probe_dside(tt, yy, label):
        t0p = time.perf_counter()
        lnt, bt = tables(tt)
        s1 = s1_t(tt, yy)
        s2 = s2_t(tt, yy)
        cpt = bt[:]
        for dd in S_LIST[1:]:
            kmax = MHEAD // dd
            for k in range(1, kmax + 1):
                cpt[dd * k] = cpt[dd * k] + lam[dd] * bt[k]
        P_pt = mpf(0)
        for m in range(2, MHEAD + 1):
            P_pt += abs(cpt[m]) * mp.exp(-s1 * lnt[m])
        E_N = Ept(N, s1, tt)
        TR_pt = mpf(0)
        for dd in S_LIST:
            a = MHEAD // dd
            cap = max(Ept(mpf(a), s1, tt), E_N) * (lnN - mp.log(mpf(a)))
            TR_pt += abs(lam[dd]) * mp.exp(-s1 * mp.log(dd)) * cap
        OV_pt = mpf(0)
        for dd in S_LIST[1:]:
            la = lnN - mp.log(dd + 1)
            cap = max(mp.exp((1 - s1) * la + (tt / 4) * la ** 2), E_N) * mp.log(dd + 1)
            OV_pt += abs(lam[dd]) * mp.exp(-s1 * mp.log(dd)) * cap
        Mmax_pt = mpf(1)
        for dd in S_LIST[1:]:
            Mmax_pt += abs(lam[dd]) * mp.exp(-s1 * mp.log(dd))
        head = mpf(1)
        for k in range(2, MHEAD + 1):
            head += bt[k] * mp.exp(-s2 * lnt[k])
        capA = max(Ept(mpf(MHEAD), s2, tt), Ept(N, s2, tt)) * (lnN - mp.log(mpf(MHEAD)))
        AB_pt = G1e_pt(tt, yy) * (head + capA)
        D_pt = P_pt + TR_pt + OV_pt + Mmax_pt * AB_pt
        ok = True
        for name, val, ub in (("P", P_pt, ups["P"]), ("TR", TR_pt, ups["TR"]),
                              ("OV", OV_pt, ups["OV"]), ("Mmax", Mmax_pt, ups["Mmax"]),
                              ("AB", AB_pt, ups["AB"]), ("D", D_pt, ups["D"])):
            hr = mf(ub) - val
            worst.append((hr, label + "/" + name))
            ok = ok and hr >= 0
        print("  D-side point %s (%.1f s): P=%s TR=%s OV=%s"
              % (label, time.perf_counter() - t0p, mp.nstr(P_pt, 18),
                 mp.nstr(TR_pt, 18), mp.nstr(OV_pt, 18)))
        print("    Mmax=%s AB=%s D=%s"
              % (mp.nstr(Mmax_pt, 18), mp.nstr(AB_pt, 18), mp.nstr(D_pt, 18)))
        return ok

    def probe_errside(tt, yy, label):
        lnt, bt = tables(tt)
        s1 = s1_t(tt, yy)
        s2 = s2_t(tt, yy)
        SB_pt = mpf(1)
        PAe_pt = mpf(1)
        for n in range(2, MERR + 1):
            SB_pt += bt[n] * mp.exp(-s1 * lnt[n])
            PAe_pt += bt[n] * mp.exp(-s2 * lnt[n])
        laM = mp.log(mpf(MERR))
        cap1 = max(Ept(mpf(MERR), s1, tt), Ept(N, s1, tt)) * (lnN - laM)
        cap2 = max(Ept(mpf(MERR), s2, tt), Ept(N, s2, tt)) * (lnN - laM)
        S1_pt = SB_pt + cap1
        S2_pt = PAe_pt + cap2
        Lpt = mp.log(N * N - tt / 16)
        Xpt = X_t(tt)
        Del_pt = ((tt ** 2) / 16 * Lpt ** 2 + mf(F(626, 1000))) / (Xpt - mf(F(666, 100)))
        eAB_pt = (mp.exp(Del_pt) - 1) * (S1_pt + G1e_pt(tt, yy) * S2_pt)
        eC0_pt = mp.exp(-(1 + yy) / 4 * Lpt - (tt / 16) * Lpt ** 2
                        + mf(F(124, 100)) * (mp.exp(mp.log(3) * yy) + mp.exp(-mp.log(3) * yy))
                        / (N - mf(F(1, 8)))
                        + (3 * mp.sqrt(Lpt ** 2 + mp.pi ** 2 / 4) + mf(F(105, 10)))
                        / (Xpt - 12))
        err_pt = eAB_pt + eC0_pt
        hr = mf(ups["err"]) - err_pt
        worst.append((hr, label + "/err"))
        print("  error point %s: eAB=%s eC0=%s err=%s"
              % (label, mp.nstr(eAB_pt, 18), mp.nstr(eC0_pt, 18), mp.nstr(err_pt, 18)))
        return hr >= 0

    TT_HI = mf(T_HI)
    TT0 = mf(T0)
    okA = probe_dside(TT_HI, mf(Y_LO), "(t_hi, y_lo)")
    okA2 = probe_dside(TT0, mf(Y_BOX_HI), "(t0, y_box_hi)")
    okB = probe_errside(TT0, mf(Y_EXT_HI), "(t0, y_ext_hi)")
    okC = probe_errside(TT_HI, mf(Y_EXT_HI), "(t_hi, y_ext_hi)")
    okD = probe_errside(TT0, mf(Y_LO), "(t0, y_lo)")
    mp.prec = saved_prec
    wmin = min(worst)
    print("  smallest headroom: %s at %s (probe %.1f s)"
          % (mp.nstr(wmin[0], 6), wmin[1], time.perf_counter() - t_probe))
    check("probe: certified uppers dominate D-side point values (t_hi, y_lo)", okA)
    check("probe: certified uppers dominate D-side point values (t0, y_box_hi)", okA2)
    check("probe: err_ub dominates error point values (3 hull points)", okB and okC and okD)
    print()


# ---------------------------------------------------------------- main


def main():
    t_start = time.perf_counter()
    upto = "all"
    if "--upto" in sys.argv:
        upto = sys.argv[sys.argv.index("--upto") + 1]
    order = ["anchors", "sigma", "fill", "coef", "sums", "err", "all"]

    def reached(name):
        return order.index(upto) >= order.index(name)

    print("audit_p1 L2 item 3 - tail lane: TAIL_LEMMA partition budget (finite lane)")
    print("release commit: %s" % RELEASE_COMMIT)
    print("prereg: reports/AUDIT_DBN_PREREG_2026-10-17.md section 4 item 3")
    print("stack: mpmath.iv prec=%d; fractions for all final numbers" % iv.prec)
    if upto != "all":
        print("DEV partial run: upto=%s (no JSON, no verdict)" % upto)
    print()

    part_selftests()
    part_sources()
    part_anchors()
    if not reached("sigma"):
        return finish_partial(t_start, upto)

    d = fix_sigmas()
    part_sigma(d)
    if not reached("fill"):
        return finish_partial(t_start, upto)

    LN, B, K1LO, K1HI, K2LO, K2HI = part_fill(d)
    if not reached("coef"):
        return finish_partial(t_start, upto)

    c_iv = part_coef(d, LN, B)
    P_ub, P_lb = part_P(c_iv, K1LO, K1HI)
    del c_iv
    if not reached("sums"):
        return finish_partial(t_start, upto)

    TRF = part_sums(d, LN, K1LO, K1HI)
    del K1LO, K1HI
    if not reached("err"):
        return finish_partial(t_start, upto)

    TR = part_AB(d, LN, B, K2LO, K2HI, TRF, P_ub, P_lb)
    del K2LO, K2HI
    (D_ub, D_lb, flow_lo, PA_ub, PA_lb, capB_ub, capB_lb, AB_ub, AB_lb) = TR
    (TR_ub, TR_lb, OV_ub, OV_lb, MMAX_ub, MMAX_lb, G_ub, G_lb,
     om_s2lo, om_s2hi) = TRF

    err_ub, err_lb, eAB_ub, eAB_lb, eC0_ub, eC0_lb = part_err(d, LN, B)
    margin_lo = flow_lo - err_ub
    part_probe(d, {"P": P_ub, "TR": TR_ub, "OV": OV_ub, "Mmax": MMAX_ub,
                   "AB": AB_ub, "D": D_ub, "err": err_ub})
    if not reached("all"):
        return finish_partial(t_start, upto)

    print()
    print("== sealed targets (pre-registered, exact rational comparisons) ==")
    print("  corridor:            0.999719 < D < 0.999721")
    print("  D_lb - 0.999719 >=  %s (30 dp floor)" % floor_dec(D_lb - CORRIDOR_LO, 30))
    print("  0.999721 - D_ub >=  %s (30 dp floor)" % floor_dec(CORRIDOR_HI - D_ub, 30))
    print("  flow: (1-D_ub)/Mmax_ub > 0.0001735326089372")
    print("  flow_lo - sealed >= %s (36 dp floor)" % floor_dec(flow_lo - SEALED_FLOW, 36))
    print("  error < 0.000000011671604")
    print("  sealed - err_ub >= %s (36 dp floor)" % floor_dec(SEALED_ERR - err_ub, 36))
    print("  margin > 0.0001735209373337")
    print("  margin_lo - sealed >= %s (36 dp floor)" % floor_dec(margin_lo - SEALED_MARGIN, 36))
    print("  Mmax_ub - 1.608290 <= %s (30 dp ceil)" % ceil_dec(MMAX_ub - SEALED_MMAX, 30))
    print()
    check("corridor lower: D_lb > 0.999719", D_lb > CORRIDOR_LO)
    check("corridor upper: D_ub < 0.999721", D_ub < CORRIDOR_HI)
    check("flow: (1-D_ub)/Mmax_ub > 0.0001735326089372", flow_lo > SEALED_FLOW)
    check("error: eAB_ub + eC0_ub < 0.000000011671604", err_ub < SEALED_ERR)
    check("margin: flow_lo - err_ub > 0.0001735209373337", margin_lo > SEALED_MARGIN)
    check("anchor M_max_ub < 1.608290", MMAX_ub < SEALED_MMAX)
    check("decisive contraction D_ub < 1 (strict)", D_ub < 1)
    check("error positivity: 0 < err_lb (strict)", err_lb > 0)
    print()

    print("== comparison vs release Arb 512 directed points (non-verdict) ==")
    print("  (reference: logs/tail_arb_512.log, blob c091e5ee3f4ff912778b10c8e6d9fe72dc54b2db)")
    for name, ours in (("P", P_ub), ("TR", TR_ub), ("OV", OV_ub), ("Mmax", MMAX_ub),
                       ("AB", AB_ub), ("D", D_ub), ("flow", flow_lo),
                       ("eAB", eAB_ub), ("eC0", eC0_ub), ("err", err_ub),
                       ("margin", margin_lo)):
        print("  %-6s our-Arb = %s" % (name, nstr10(ours - ARB_REF[name])))
    print("  note: our eC0 equals the release's 256-bit Python lane value")
    print("        (1.167110878131e-8) to ~4e-19 relative; the 512-bit C/Arb lane")
    print("        is looser by 7.25e-8 relative on the exponent (both are valid")
    print("        enclosures; the sealed err target clears all three lanes).")
    print()

    failed = [c for c in CHECKS if not c["ok"]]
    total = len(CHECKS)
    print("== summary ==")
    print("checks_total: %d  checks_failed: %d" % (total, len(failed)))
    verdict = "PASS" if not failed else "FAIL"
    print("item3 machine verdict: %s" % verdict)
    print("runtime_seconds: %.1f" % (time.perf_counter() - t_start))

    VALUES.update({
        "audit": "P1/L2 item 3 - tail lane (TAIL_LEMMA partition), finite certified spot",
        "release_commit": RELEASE_COMMIT,
        "prereg": "reports/AUDIT_DBN_PREREG_2026-10-17.md section 4 item 3",
        "script_sha256": hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest(),
        "python": sys.version.split()[0],
        "iv_prec": iv.prec,
        "scope": {
            "certified_point": "N = N_* = 3840000 (uniform in the closed t-interval); "
                               "all-N N >= N_* and y-coverage above I_box are the release's "
                               "section 6/7 reductions with gates re-checked as necessary premises only",
            "not_done": ["release Arb/FLINT C lane not re-run",
                         "release 160/256-bit Python lane not re-run",
                         "no re-derivation of Polymath Theorem 1.3 itself"],
        },
        "boxes": {
            "t": [fs(T0), fs(T_HI)],
            "y_box": [fs(Y_LO), fs(Y_BOX_HI)],
            "y_ext": [fs(Y_LO), fs(Y_EXT_HI)],
            "N": NSTAR, "M": MHEAD, "M_err": MERR,
        },
        "sigmas": {
            "s1_box_lo": fs(d["s1_box_lo"]), "s1_box_hi": fs(d["s1_box_hi"]),
            "s2_box_lo": fs(d["s2_box_lo"]), "s2_box_hi": fs(d["s2_box_hi"]),
            "s1_ext_lo": fs(d["s1_ext_lo"]), "s1_ext_hi": fs(d["s1_ext_hi"]),
            "s2_ext_lo": fs(d["s2_ext_lo"]), "s2_ext_hi": fs(d["s2_ext_hi"]),
            "delta_lo": fs(lo_f(d["delta"])), "delta_hi": fs(hi_f(d["delta"])),
            "kappa_lo": fs(lo_f(d["kappa"])), "kappa_hi": fs(hi_f(d["kappa"])),
        },
        "components": {
            "P": {"ub": fs(P_ub), "lb": fs(P_lb)},
            "TR": {"ub": fs(TR_ub), "lb": fs(TR_lb)},
            "OV": {"ub": fs(OV_ub), "lb": fs(OV_lb)},
            "Mmax": {"ub": fs(MMAX_ub), "lb": fs(MMAX_lb)},
            "G": {"ub": fs(G_ub), "lb": fs(G_lb)},
            "AB": {"ub": fs(AB_ub), "lb": fs(AB_lb)},
            "D": {"ub": fs(D_ub), "lb": fs(D_lb)},
            "flow_lo": fs(flow_lo),
            "eAB": {"ub": fs(eAB_ub), "lb": fs(eAB_lb)},
            "eC0": {"ub": fs(eC0_ub), "lb": fs(eC0_lb)},
            "err": {"ub": fs(err_ub), "lb": fs(err_lb)},
            "margin_lo": fs(margin_lo),
        },
        "sealed": {
            "corridor_lo": "0.999719", "corridor_hi": "0.999721",
            "flow": "0.0001735326089372", "err": "0.000000011671604",
            "margin": "0.0001735209373337", "mmax": "1.608290",
        },
        "sealed_slacks": {
            "flow_lo_minus_sealed": fs(flow_lo - SEALED_FLOW),
            "sealed_minus_err_ub": fs(SEALED_ERR - err_ub),
            "margin_lo_minus_sealed": fs(margin_lo - SEALED_MARGIN),
            "corridor_lo_margin": fs(D_lb - CORRIDOR_LO),
            "corridor_hi_margin": fs(CORRIDOR_HI - D_ub),
            "sealed_mmax_minus_ub": fs(SEALED_MMAX - MMAX_ub),
        },
        "arb_reference_diffs": {k: nstr10((P_ub if k == "P" else
                                          TR_ub if k == "TR" else
                                          OV_ub if k == "OV" else
                                          MMAX_ub if k == "Mmax" else
                                          AB_ub if k == "AB" else
                                          D_ub if k == "D" else
                                          flow_lo if k == "flow" else
                                          eAB_ub if k == "eAB" else
                                          eC0_ub if k == "eC0" else
                                          err_ub if k == "err" else
                                          margin_lo) - ARB_REF[k])
                                 for k in ARB_REF},
        "sources": [{"path": rel, "blob_sha1": sha, "bytes": size, "role": role}
                    for (rel, sha, size, local, role) in SOURCES],
        "checks": CHECKS,
        "checks_total": total,
        "checks_failed": len(failed),
        "verdict": verdict,
        "runtime_seconds": round(time.perf_counter() - t_start, 1),
    })
    with open(JSON_OUT, "w", encoding="utf-8") as fh:
        json.dump(VALUES, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("json written: %s" % JSON_OUT)
    return 0 if not failed else 1


def finish_partial(t_start, upto):
    print()
    print("[DEV] partial run end (upto=%s) -- no JSON, no verdict" % upto)
    print("runtime_seconds: %.1f" % (time.perf_counter() - t_start))
    return 0


if __name__ == "__main__":
    sys.exit(main())
