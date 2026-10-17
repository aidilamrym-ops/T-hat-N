#!/usr/bin/env python3
"""audit_p1 / L2 item 2 -- Prop 4.10 finite-lane effective-error budget & binding.

Pre-registered protocol: reports/AUDIT_DBN_PREREG_2026-10-17.md, section 4,
item 2. Independence: our own implementation; no reuse of the package source
(code, parser, partitions, tables). Formula statements transcribed by us from
the pinned release documents, read-only (git blob sha1 re-verified below):

  PROOF_NOTE.md                            git blob sha1 323e2144e9d1624c81002be5997b0901147ce166
  ERROR_CONSTANT_WELD.md                   git blob sha1 9fd635b59831316b73c1052dd4f6ec71ce70f1e1
  vendor/.../ERROR_TERMS_AUDIT.md          git blob sha1 542c1ce0e9909bbb2556e6debf3ce25ed0ec34a3
  CANDIDATE_PARAMETERS.md                  git blob sha1 bdad0402562f5ea077a9ab380558cb19f74ffb82
  logs/finite_and_binding.log              git blob sha1 c84e2b3404b966c00477a3040c303a0a1ff809b6
  verifiers/verify_finite_and_binding.py   git blob sha1 17c33ac18f4e03ab75f5f6f82c745e4a430408b2
                                           (claim identified from; no code used)
  verifiers/verify_error_constant_weld.py  git blob sha1 891f3b017d8699b86e11494bb28526fb9480f5d8
                                           (weld statement identified from; no code used)

Formulas ((20)-(23) from the vendored audit of arXiv:1904.12438v2 Theorem 1.3
as transcribed there; e_C,0 in the welded form of ERROR_CONSTANT_WELD.md,
10.50 = 3.58 + 6.92):

  (20) |gamma| <= e^{0.02 y} (x/4pi)^{-y/2}
  (21) Re s_* >= (1+y)/2 + (t/4) log(x/4pi) - (t/(2 x^2)) (1-3y+4y(1+y)/x^2)_+
  (22) |kappa| <= t y / (2 (x-6))
  (23) e_A+e_B <= sum_{n<=N} (1 + |gamma| N^{|kappa|} n^y) (b_n^t / n^{Re s_*})
                  (exp(((t^2/16) log^2(x/(4 pi n^2)) + 0.626)/(x - 6.66)) - 1),
       b_n^t = exp((t/4) log^2 n),  N = floor(sqrt(x/4pi + t/16))
  (24) e_C,0 <= (x/4pi)^{-(1+y)/4} exp(-(t/16) log^2(x/4pi)
                + 1.24 (3^y + 3^{-y})/(N - 0.125)
                + (3 |log(x/4pi) + i pi/2| + 10.50)/(x - 12))

Region = the release's evaluation configuration for the finite lane (the
E_max claim of PROOF_NOTE (4.15)/(4.16), consumed over (4.5) and (4.12)):
  t in [129/800, 161250001/10^9]  (t-box containing the exact row t0 = 129/800),
  y in [y0, sqrt(1-2 t0)],  y0 = sqrt(87677/2500000),
  x at the N-th window's left edge x0(N) = 4 pi (N^2 - t/16),
for N in {690988 (main; the release's own evaluation point), 690989,
1000000, 3840000 (= the release's cutoff N_*, equation (5.1); the closed
finite/tail overlap window)}.

Method (ours; structure differs from the release's head+cap+max-product
evaluator): for every n the three factor groups are bounded independently,
evaluated in mpmath.iv (240-bit outward-rounded intervals):
  * f_n = b_n^t n^{-Re s_*} <= exp((t/4) log^2 n - sigma1 log n), where
    sigma1 is the (21) lower bound evaluated at x = x0(t), y = y0; for x > x0
    the log-term only grows and the correction only shrinks, so sigma1 is a
    uniform lower bound on the window [x0(N), x0(N+1));
  * (1 + |gamma| N^{|kappa|} n^y) <= 1 + exp(mc_n), where
    mc_n = max of the four corner products of the rectangle
    [c_lo, c_hi] x [y0_lo, ymax_ub] with
    c = 0.02 + log n + t log N/(2 (x0 - 6)) - (1/2) log(x0/(4pi))
    (c is decreasing in x, increasing in t; sup of c*y over the rectangle is
    attained at a corner; y endpoints taken outward: y0 lower, sqrt(1-2t0)
    upper); no sign branch is needed since all four corners are compared;
  * (exp(theta_n) - 1) <= exp(u_n) - 1, u_n = ((t^2/16) w_n^2 + 0.626)/(x0-6.66),
    w_n = log(x0/(4pi)) - 2 log n (theta_n is decreasing in x: the numerator
    grows like (t^2/8)w/x but 2w - w^2 <= 1 gives d/dx < 0 uniformly).
Exact per-term enumeration for n = 1..m0 (m0 = 20000, our choice); the tail
n = m0+1..N is enclosed via convexity of h(u) = (t/4)u^2 - sigma1 u + u:
with f decreasing on [m0, N] (machine check (t_hi/2) log N < sigma1_lo),
sum f(n) <= int_{m0}^{N} f <= (log N - log m0) max(E(log m0), E(log N)),
E(u) = exp(h(u)); h is convex (t > 0), so E's maximum is at an endpoint.
The tail's (1+|gamma|) factor uses the corner supremum at n = N (c increasing
in n), the (exp(theta)-1) factor its value at n = m0 (theta decreasing in n).

All final numbers are EXACT rationals: every ivmpf endpoint is extracted via
mpmath.libmp.to_rational (binary expansion) and the per-term products and the
whole sum are accumulated in fractions.Fraction. Comparisons against the
sealed decimal constants are exact Fraction comparisons.

Sealed constants (recomputed against; strings as printed):
  0.000000000002057023688667     e_A+e_B   (log line 5; PROOF_NOTE (4.15))
  0.000000233492848188649183     e_C,0     (log line 5; PROOF_NOTE (4.15))
  0.000000233494905212337849     E_max     (log line 5; PROOF_NOTE (4.15))
  0.000000557871094787           margin    (log line 7; PROOF_NOTE (4.16))
  0.000000791366                 T_floor   (stored 4-leg floor, INPUT reuse)

Output: checks on stdout; machine JSON to reports/audit_p1_l2_prop410_results.json;
exit 0 iff every check passes.
"""

import hashlib
import json
import math
import os
import sys
import time
from fractions import Fraction as F

from mpmath import iv, mp, mpf
from mpmath.libmp import to_rational

iv.prec = 240
mp.prec = 240

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_OUT = os.path.join(REPO_ROOT, "reports", "audit_p1_l2_prop410_results.json")
RELEASE_COMMIT = "2e9976c4becbf97e31c56fe75fce07cdff5dd4ea"
DOC_DIR = r"C:\Users\usER\AppData\Local\Temp\opencode\dbn_release_docs"

T0 = F(129, 800)
THI = F(161250001, 10 ** 9)
Y2 = F(87677, 2500000)
YMAX2 = 1 - 2 * T0
X_INT = 6000000185827
N0 = 690988
M0 = 20000
N_LIST = [690988, 690989, 1000000, 3840000]

SEALED_EAB = F("0.000000000002057023688667")
SEALED_EC0 = F("0.000000233492848188649183")
SEALED_EMAX = F("0.000000233494905212337849")
SEALED_MARGIN = F("0.000000557871094787")
T_FLOOR = F("0.000000791366")

SOURCES = [
    ("PROOF_NOTE.md", "323e2144e9d1624c81002be5997b0901147ce166",
     "PROOF_NOTE.md", "statement source ((4.15)/(4.16), region)"),
    ("ERROR_CONSTANT_WELD.md", "9fd635b59831316b73c1052dd4f6ec71ce70f1e1",
     "ERROR_CONSTANT_WELD.md", "welded 10.50 corollary (statement source)"),
    ("vendor/dbn21a/certificates/record/error_terms_audit/ERROR_TERMS_AUDIT.md",
     "542c1ce0e9909bbb2556e6debf3ce25ed0ec34a3",
     "vendor__dbn21a__certificates__record__error_terms_audit__ERROR_TERMS_AUDIT.md",
     "formula transcription (20)-(24) source"),
    ("CANDIDATE_PARAMETERS.md", "bdad0402562f5ea077a9ab380558cb19f74ffb82",
     "CANDIDATE_PARAMETERS.md", "constants source (t0, y0, margin target)"),
    ("logs/finite_and_binding.log", "c84e2b3404b966c00477a3040c303a0a1ff809b6",
     "logs__finite_and_binding.log", "sealed numbers source"),
    ("verifiers/verify_finite_and_binding.py", "17c33ac18f4e03ab75f5f6f82c745e4a430408b2",
     "verifiers__verify_finite_and_binding.py", "claim identified from; no code reused"),
    ("verifiers/verify_error_constant_weld.py", "891f3b017d8699b86e11494bb28526fb9480f5d8",
     "verifiers__verify_error_constant_weld.py", "claim identified from; no code reused"),
]

CHECKS = []
VALUES = {}


def check(name, ok):
    ok = bool(ok)
    CHECKS.append({"name": name, "ok": ok})
    print("[%s] %s" % ("PASS" if ok else "FAIL", name))
    return ok


def check_skip(name, why):
    CHECKS.append({"name": name, "ok": True, "skipped": why})
    print("[SKIP] %s (%s)" % (name, why))


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


def git_blob_sha1(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def ivq(num, den=1):
    return iv.mpf(num) / iv.mpf(den)


def f_from_tuple(t):
    p, q = to_rational(t)
    return F(p, q)


def lo_f(x):
    """Exact Fraction of the lower endpoint of an ivmpf."""
    return f_from_tuple(x._mpi_[0])


def hi_f(x):
    """Exact Fraction of the upper endpoint of an ivmpf."""
    return f_from_tuple(x._mpi_[1])


def frac_of(v):
    """Exact Fraction of an mpf value."""
    return f_from_tuple(mpf(v)._mpf_)


def fr_to_iv(f):
    return iv.mpf(f.numerator) / iv.mpf(f.denominator)


def part_sources():
    print("== statement sources (pinned release, read-only) ==")
    for name, expected, fname, note in SOURCES:
        path = os.path.join(DOC_DIR, fname)
        print("  file: %s  (%s)" % (name, note))
        print("    expected git_blob_sha1: %s" % expected)
        if os.path.exists(path):
            with open(path, "rb") as fh:
                data = fh.read()
            got = git_blob_sha1(data)
            sha256 = hashlib.sha256(data).hexdigest()
            print("    fetched copy: size %d  sha256 %s" % (len(data), sha256))
            print("    fetched copy git_blob_sha1: %s  match: %s" % (got, got == expected))
            check("source blob match: %s" % name, got == expected)
        else:
            check_skip("source blob match: %s" % name, "fetched copy absent on this machine")
    print()


def part_selftests():
    print("== arithmetic helper self-tests ==")
    check("frac_of(3/2) exact", frac_of(mpf(1.5)) == F(3, 2))
    check("frac_of(-1/4) exact", frac_of(mpf(-0.25)) == F(-1, 4))
    check("frac_of(3) exact", frac_of(mpf(3)) == F(3))
    check("iv.pi interval inside (314159/100000, 31416/10000)",
          F(314159, 10 ** 5) < lo_f(iv.pi) and hi_f(iv.pi) < F(31416, 10 ** 4))
    check("fr_to_iv round-trip brackets 1/3",
          lo_f(fr_to_iv(F(1, 3))) <= F(1, 3) <= hi_f(fr_to_iv(F(1, 3))))
    print()


def build_config_iv():
    t0_iv = ivq(T0.numerator, T0.denominator)
    thi_iv = ivq(THI.numerator, THI.denominator)
    # affine hull: t0 + u * (t_hi - t0), u in [0, 1] -> contains [t0, t_hi]
    t_box = t0_iv + iv.mpf([0, 1]) * (thi_iv - t0_iv)
    y0_iv = iv.sqrt(ivq(Y2.numerator, Y2.denominator))
    ymax_iv = iv.sqrt(1 - 2 * t0_iv)
    return {
        "t_box": t_box,
        "y0": y0_iv,
        "ymax": ymax_iv,
        "Y0_LO": lo_f(y0_iv),
        "YMAX_UB": hi_f(ymax_iv),
        "K626": ivq(313, 500),
        "K666": ivq(333, 50),
        "K02": ivq(1, 50),
        "K124": ivq(31, 25),
        "K1050": ivq(21, 2),
        "K12": ivq(12),
        "K125": ivq(1, 8),
    }


def part_region(ctx):
    print("== region and configuration checks (exact rational lane) ==")
    print("  t0 = %s ; t_hi = %s ; y0^2 = %s ; 1-2t0 = %s" % (fs(T0), fs(THI), fs(Y2), fs(YMAX2)))
    check("t0 > 0", T0 > 0)
    check("t0 < t_hi", T0 < THI)
    check("t_hi <= 1/4", THI <= F(1, 4))
    check("t_hi - t0 = 1/10^9 exactly", THI - T0 == F(1, 10 ** 9))
    check("0 < y0^2 < 1-2t0 <= 1", 0 < Y2 < YMAX2 <= 1)
    check("N0^2 = 477464416144", N0 * N0 == 477464416144)
    check("N0 > m0", N0 > M0)

    # item-1 style brackets: y0 and sqrt(1-2t0) via exact squaring
    check("(1872719/10^7)^2 < y0^2", F(1872719, 10 ** 7) ** 2 < Y2)
    check("y0^2 < (23409/125000)^2", Y2 < F(23409, 125000) ** 2)
    check("(8231038/10^7)^2 < 1-2t0", F(8231038, 10 ** 7) ** 2 < YMAX2)
    check("1-2t0 < (8231039/10^7)^2 (implies stated <=)", YMAX2 < F(8231039, 10 ** 7) ** 2)

    # x_* (criterion start) bracket, item-1 method: X + sqrt(1 - y0^2)
    s2 = 1 - Y2
    scale = 10 ** 18
    dd = s2.numerator * s2.denominator * scale * scale
    n_isq = math.isqrt(dd)
    sqrt_lo = F(n_isq, s2.denominator * scale)
    x_star_lo = F(X_INT) + sqrt_lo
    check("s2 = 1 - y0^2 = 2412323/2500000", s2 == F(2412323, 2500000))
    check("isqrt square check for x_* lower bracket", n_isq * n_isq <= dd < (n_isq + 1) ** 2)
    print("  x_star lower bracket (scale 10^18): %s" % fs(x_star_lo))

    x0_main_iv = 4 * iv.pi * (iv.mpf(N0) ** 2 - ctx["t_box"] / 16)
    x0_ub = hi_f(x0_main_iv)
    x0_lb = lo_f(x0_main_iv)
    check("x0(690988) upper < x_* lower (evaluation below criterion start)", x0_ub < x_star_lo)
    print("  x0(690988) interval: [%s, %s] (6 dp floor/ceil)"
          % (floor_dec(x0_lb, 6), ceil_dec(x0_ub, 6)))
    print("  x_* - x0(690988) lower margin > %s" % floor_dec(x_star_lo - x0_ub, 6))
    check("(h)_+ <= 1 lemma: 4(1 + ymax_ub) < 3 x0^2",
          4 * (1 + ctx["YMAX_UB"]) < 3 * x0_lb ** 2)
    check("sealed arithmetic replay: T_floor - sealed E_max >= sealed margin",
          T_FLOOR - SEALED_EMAX >= SEALED_MARGIN)
    print()


def corner_ysup(ctx, c_iv):
    """Exact Fraction sup of exp(c*y) over c in c_iv and y in [y0, sqrt(1-2t0)]."""
    c_lo = lo_f(c_iv)
    c_hi = hi_f(c_iv)
    y0_lo = ctx["Y0_LO"]
    ymax_ub = ctx["YMAX_UB"]
    mc = max(c_lo * y0_lo, c_lo * ymax_ub, c_hi * y0_lo, c_hi * ymax_ub)
    return hi_f(iv.exp(fr_to_iv(mc)))


def window_budget(ctx, N, lnn):
    t_box = ctx["t_box"]
    y0_iv = ctx["y0"]
    ymax_iv = ctx["ymax"]
    Nv = iv.mpf(N)
    x0_iv = 4 * iv.pi * (Nv ** 2 - t_box / 16)
    log0_iv = iv.log(Nv ** 2 - t_box / 16)
    lnN_iv = iv.log(Nv)
    delta1_iv = (t_box / 4) * (-iv.log(1 - t_box / (16 * Nv ** 2))) + t_box / (2 * x0_iv ** 2)
    sigma1_iv = (1 + y0_iv) / 2 + (t_box / 2) * lnN_iv - delta1_iv
    cbase_iv = ctx["K02"] + t_box * lnN_iv / (2 * (x0_iv - ivq(6))) - log0_iv / 2

    # direct per-term section n = 1..m0 (exact Fraction accumulation)
    s = F(0)
    for n in range(1, M0 + 1):
        lg = lnn[n]
        f_iv = iv.exp((t_box / 4) * lg ** 2 - sigma1_iv * lg)
        g_ub = corner_ysup(ctx, cbase_iv + lg)
        w_iv = log0_iv - 2 * lg
        u_iv = ((t_box ** 2) / 16 * w_iv ** 2 + ctx["K626"]) / (x0_iv - ctx["K666"])
        th_ub = hi_f(iv.exp(u_iv) - 1)
        s += hi_f(f_iv) * (1 + g_ub) * th_ub
    eab_direct = s

    # tail by convexity: h(u) = (t/4)u^2 - sigma1 u + u, E(u) = exp(h(u))
    lnm0 = lnn[M0]
    dec_ok = hi_f((t_box / 2) * lnN_iv) < lo_f(sigma1_iv)
    E_m0_ub = hi_f(iv.exp((1 - sigma1_iv) * lnm0 + (t_box / 4) * lnm0 ** 2))
    E_N_ub = hi_f(iv.exp((1 - sigma1_iv) * lnN_iv + (t_box / 4) * lnN_iv ** 2))
    maxE = max(E_m0_ub, E_N_ub)
    cap = maxE * hi_f(lnN_iv - lnm0)
    u_m0 = ((t_box ** 2) / 16 * (log0_iv - 2 * lnm0) ** 2 + ctx["K626"]) / (x0_iv - ctx["K666"])
    theta_m0_ub = hi_f(iv.exp(u_m0) - 1)
    g_tail_ub = corner_ysup(ctx, cbase_iv + lnN_iv)
    tail = (1 + g_tail_ub) * theta_m0_ub * cap
    eab = eab_direct + tail

    # e_C,0 (welded 10.50 form)
    ln3_iv = iv.log(ivq(3))
    term_a = -(1 + y0_iv) / 4 * log0_iv
    term_b = -(t_box / 16) * log0_iv ** 2
    term_c = ctx["K124"] * (iv.exp(ymax_iv * ln3_iv) + iv.exp(-ymax_iv * ln3_iv)) / (Nv - ctx["K125"])
    term_d = (3 * iv.sqrt(log0_iv ** 2 + (iv.pi / 2) ** 2) + ctx["K1050"]) / (x0_iv - ctx["K12"])
    ec0 = hi_f(iv.exp(term_a + term_b + term_c + term_d))

    emax = eab + ec0
    margin = T_FLOOR - emax
    return {
        "N": N,
        "x0_lo": lo_f(x0_iv),
        "x0_hi": hi_f(x0_iv),
        "sigma1_lo": lo_f(sigma1_iv),
        "sigma1_hi": hi_f(sigma1_iv),
        "dec_ok": dec_ok,
        "eab_direct": eab_direct,
        "cap": cap,
        "theta_m0_ub": theta_m0_ub,
        "g_tail_ub": g_tail_ub,
        "tail": tail,
        "eab": eab,
        "ec0": ec0,
        "emax": emax,
        "margin": margin,
    }


def main():
    t_start = time.time()
    print("audit_p1 L2 item 2 - Prop 4.10 finite-lane effective-error budget & binding")
    print("release commit: %s" % RELEASE_COMMIT)
    print("prereg: reports/AUDIT_DBN_PREREG_2026-10-17.md section 4 item 2")
    print("stack: mpmath.iv prec=%d; fractions for all final numbers" % iv.prec)
    print()

    part_sources()
    part_selftests()
    ctx = build_config_iv()
    part_region(ctx)

    print("== precompute log(n) for n = 1..%d ==" % M0)
    lnn = [None] * (M0 + 1)
    for n in range(1, M0 + 1):
        lnn[n] = iv.log(iv.mpf(n))
    print("  done")
    print()

    per_N = []
    print("== window budgets (our bounds; per-term enumeration + convexity tail) ==")
    for N in N_LIST:
        r = window_budget(ctx, N, lnn)
        per_N.append(r)
        print("-- N = %d" % N)
        print("   x0 = [%s, %s] (6 dp floor/ceil)" % (floor_dec(r["x0_lo"], 6), ceil_dec(r["x0_hi"], 6)))
        print("   sigma1 interval = [%s, %s] (24 dp)"
              % (floor_dec(r["sigma1_lo"], 24), ceil_dec(r["sigma1_hi"], 24)))
        print("   direct sum n=1..%d  <= %s" % (M0, ceil_dec(r["eab_direct"], 24)))
        print("   tail cap <= %s ; theta_m0 <= %s ; (1+gamma_tail) <= %s"
              % (ceil_dec(r["cap"], 24), ceil_dec(r["theta_m0_ub"], 24), ceil_dec(r["g_tail_ub"] + 1, 24)))
        print("   tail <= %s" % ceil_dec(r["tail"], 24))
        print("   e_A+e_B <= %s" % ceil_dec(r["eab"], 24))
        print("   e_C,0   <= %s" % ceil_dec(r["ec0"], 24))
        print("   E_max   <= %s" % ceil_dec(r["emax"], 24))
        print("   margin  >= %s (18 dp floor)" % floor_dec(r["margin"], 18))
        print("   cert gap floors: sealed-eAB >= %s ; sealed-eC0 >= %s ; margin-sealed >= %s"
              % (floor_dec(SEALED_EAB - r["eab"], 24),
                 floor_dec(SEALED_EC0 - r["ec0"], 30),
                 floor_dec(r["margin"] - SEALED_MARGIN, 18)))
        if N == N0:
            print("   sealed: e_A+e_B <= 0.000000000002057023688667 ; e_C,0 <= 0.000000233492848188649183")
            print("   sealed: E_max <= 0.000000233494905212337849 ; margin >= 0.000000557871094787")
        check("N=%d f decreasing on [m0,N] ((t_hi/2) log N < sigma1_lo)" % N, r["dec_ok"])
        check("N=%d e_A+e_B <= sealed 2.057023688667e-12" % N, r["eab"] <= SEALED_EAB)
        check("N=%d e_C,0 <= sealed 2.33492848188649183e-7" % N, r["ec0"] <= SEALED_EC0)
        check("N=%d E_max <= sealed 2.33494905212337849e-7" % N, r["emax"] <= SEALED_EMAX)
        check("N=%d margin >= sealed 5.57871094787e-7" % N, r["margin"] >= SEALED_MARGIN)
        print()

    failed = [c for c in CHECKS if not c["ok"]]
    total = len(CHECKS)
    print("== summary ==")
    print("checks_total: %d  checks_failed: %d" % (total, len(failed)))
    verdict = "PASS" if not failed else "FAIL"
    print("item2 machine verdict: %s" % verdict)
    print("runtime_seconds: %.1f" % (time.time() - t_start))

    VALUES.update({
        "release_commit": RELEASE_COMMIT,
        "region": {
            "t_box": [fs(T0), fs(THI)],
            "y0_sq": fs(Y2),
            "one_minus_2t0": fs(YMAX2),
            "x0_definition": "4*pi*(N^2 - t/16)",
            "N_list": N_LIST,
            "direct_terms_m0": M0,
            "tail_method": "convexity cap (log N - log m0) * max(E endpoints); f decreasing checked",
        },
        "sealed": {
            "eab": "0.000000000002057023688667",
            "ec0": "0.000000233492848188649183",
            "emax": "0.000000233494905212337849",
            "margin": "0.000000557871094787",
            "t_floor_input": "0.000000791366",
        },
        "per_N": [
            {
                "N": r["N"],
                "x0_floor6": floor_dec(r["x0_lo"], 6),
                "x0_ceil6": ceil_dec(r["x0_hi"], 6),
                "sigma1_lo": fs(r["sigma1_lo"]),
                "sigma1_hi": fs(r["sigma1_hi"]),
                "dec_ok": r["dec_ok"],
                "eab_direct_ceil24": ceil_dec(r["eab_direct"], 24),
                "cap_ceil24": ceil_dec(r["cap"], 24),
                "theta_m0_ceil24": ceil_dec(r["theta_m0_ub"], 24),
                "tail_ceil24": ceil_dec(r["tail"], 24),
                "eab_ceil24": ceil_dec(r["eab"], 24),
                "ec0_ceil24": ceil_dec(r["ec0"], 24),
                "emax_ceil24": ceil_dec(r["emax"], 24),
                "margin_floor18": floor_dec(r["margin"], 18),
                "sealed_minus_eab_floor24": floor_dec(SEALED_EAB - r["eab"], 24),
                "sealed_minus_ec0_floor30": floor_dec(SEALED_EC0 - r["ec0"], 30),
                "sealed_minus_ec0_ceil30": ceil_dec(SEALED_EC0 - r["ec0"], 30),
                "sealed_minus_emax_floor24": floor_dec(SEALED_EMAX - r["emax"], 24),
                "margin_minus_sealed_floor18": floor_dec(r["margin"] - SEALED_MARGIN, 18),
                "eab_le_sealed": r["eab"] <= SEALED_EAB,
                "ec0_le_sealed": r["ec0"] <= SEALED_EC0,
                "emax_le_sealed": r["emax"] <= SEALED_EMAX,
                "margin_ge_sealed": r["margin"] >= SEALED_MARGIN,
            }
            for r in per_N
        ],
    })

    payload = {
        "item": "L2-2 Prop 4.10 finite-lane effective-error budget & binding",
        "prereg": "reports/AUDIT_DBN_PREREG_2026-10-17.md section 4 item 2",
        "release_commit": RELEASE_COMMIT,
        "stack": {"mpmath_iv_prec_bits": iv.prec,
                  "exact_rational_extraction": "mpmath.libmp.to_rational + fractions"},
        "sources": [
            {"path": name, "git_blob_sha1_expected": sha,
             "fetched_as": fname, "role": role}
            for name, sha, fname, role in SOURCES
        ],
        "checks_total": total,
        "checks_failed": len(failed),
        "machine_verdict": verdict,
        "checks": CHECKS,
        "values": VALUES,
    }
    os.makedirs(os.path.dirname(JSON_OUT), exist_ok=True)
    with open(JSON_OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2, sort_keys=False)
        fh.write("\n")
    print("json written: %s" % JSON_OUT)
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
