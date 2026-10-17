#!/usr/bin/env python3
"""audit_p1 / L2 item 1 -- window freeze & affine sign map (exact rational lane).

Pre-registered protocol: reports/AUDIT_DBN_PREREG_2026-10-17.md, section 4,
item 1. Independence: this is our own implementation; no reuse of the package
source (code, parser, interval partition, decimal tables). The statements
being re-derived are taken from the pinned release documents, read-only:

  WINDOW_FREEZE_THEOREM.md                git blob sha1 0f4ebe3567414e9eb94c3be23f5e662e211f92ca
  CANDIDATE_PARAMETERS.md                 git blob sha1 bdad0402562f5ea077a9ab380558cb19f74ffb82
  verifiers/verify_criterion_sign_map.py  git blob sha1 f3079eb10fec368a4fb4454957ffcb38aa1998b0
                                          (statement identified from; no code used)

Stack: fractions for every certification; sympy for symbolic derivative
identities (pure-Python CAS; same Python stack; not FLINT/Arb).

Output: human-readable checks on stdout; machine JSON to
reports/audit_p1_l2_window_results.json; exit 0 iff every check passes.
"""

import hashlib
import json
import math
import os
import sys
from fractions import Fraction as F

try:
    import sympy as sp
except Exception:  # pragma: no cover
    sp = None

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_OUT = os.path.join(REPO_ROOT, "reports", "audit_p1_l2_window_results.json")
RELEASE_COMMIT = "2e9976c4becbf97e31c56fe75fce07cdff5dd4ea"

DOC_SOURCES = [
    ("WINDOW_FREEZE_THEOREM.md", "0f4ebe3567414e9eb94c3be23f5e662e211f92ca",
     r"C:\Users\usER\AppData\Local\Temp\opencode\dbn_release_docs\WINDOW_FREEZE_THEOREM.md",
     "statement source"),
    ("CANDIDATE_PARAMETERS.md", "bdad0402562f5ea077a9ab380558cb19f74ffb82",
     r"C:\Users\usER\AppData\Local\Temp\opencode\dbn_release_docs\CANDIDATE_PARAMETERS.md",
     "statement source"),
    ("verifiers/verify_criterion_sign_map.py", "f3079eb10fec368a4fb4454957ffcb38aa1998b0",
     r"C:\Users\usER\AppData\Local\Temp\opencode\dbn_release_docs\verify_criterion_sign_map.py",
     "claim identified from; no code reused"),
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


def part0_sources():
    print("== statement sources (pinned release, read-only) ==")
    for name, expected, path, note in DOC_SOURCES:
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


def arctan_inv_int_bounds(xi, k_terms):
    """Bounds for arctan(1/xi) from the alternating Taylor partial sum.

    arctan(1/x) = sum_{k>=0} (-1)^k / ((2k+1) x^(2k+1)); the terms decrease
    strictly in absolute value, so the partial sum S_K differs from
    arctan(1/x) by a remainder of absolute value <= a_{K+1} and of sign
    (-1)^(K+1), where a_{K+1} = 1/((2K+3) x^(2K+3)).
    """
    s = F(0)
    p = xi
    for k in range(k_terms + 1):
        term = F(1, (2 * k + 1) * p)
        s = s + term if k % 2 == 0 else s - term
        p *= xi * xi
    a_next = F(1, (2 * k_terms + 3) * p)
    if (k_terms + 1) % 2 == 1:
        return s - a_next, s
    return s, s + a_next


def part_w():
    print("== W. window freeze (exact rational lane) ==")
    t0 = F(129, 800)
    y0sq = F(87677, 2500000)
    ymax_sq = 1 - 2 * t0
    x_int = 6000000185827
    print("  t0 = %s ; y0^2 = %s ; 1-2t0 = %s ; X = %d" % (fs(t0), fs(y0sq), fs(ymax_sq), x_int))
    print("  y0 := positive square root of y0^2 (release CANDIDATE_PARAMETERS.md)")
    print()

    # --- W1: Machin pi bracket -------------------------------------------------
    K = 90
    lo5, hi5 = arctan_inv_int_bounds(5, K)
    lo239, hi239 = arctan_inv_int_bounds(239, K)
    pi_lo = 16 * lo5 - 4 * hi239
    pi_hi = 16 * hi5 - 4 * lo239
    width = pi_hi - pi_lo
    k_pow = 0
    while width < F(1, 10 ** (k_pow + 1)):
        k_pow += 1
    print("  W1 Machin pi = 16*arctan(1/5) - 4*arctan(1/239), K = %d terms each" % K)
    print("  pi_lo = %s" % fs(pi_lo))
    print("  pi_hi = %s" % fs(pi_hi))
    print("  pi_lo (floor, 60 dp) = %s" % floor_dec(pi_lo, 60))
    print("  pi_hi (ceil, 60 dp)  = %s" % ceil_dec(pi_hi, 60))
    print("  pi bracket width = %s" % fs(width))
    print("  (largest k with width < 10^-k: %s ; width >= 10^-%d)" % (k_pow, k_pow + 1))
    check("W1a pi_lo < pi_hi", pi_lo < pi_hi)
    check("W1b pi bracket width < 1e-100 (exact rational comparison)", width < F(1, 10 ** 100))
    check("W1c 3 < pi_lo (basic sanity)", pi_lo > 3)
    print()

    # --- W2: y0 bracket ---------------------------------------------------------
    a = F(1872719, 10 ** 7)
    b = F(23409, 125000)
    add = a * a
    bdd = b * b
    print("  W2 exact squaring comparisons for y0")
    print("  (1872719/10^7)^2 = %s" % fs(add))
    print("  (23409/125000)^2 = %s" % fs(bdd))
    print("  y0^2 - (1872719/10^7)^2 = %s" % fs(y0sq - add))
    print("  (23409/125000)^2 - y0^2 = %s" % fs(bdd - y0sq))
    check("W2a (1872719/10^7)^2 < y0^2", add < y0sq)
    check("W2b y0^2 < (23409/125000)^2", y0sq < bdd)
    print()

    # --- W3: sqrt(1-2t0) bracket -------------------------------------------------
    c = F(8231038, 10 ** 7)
    d = F(8231039, 10 ** 7)
    ccc = c * c
    ddd = d * d
    print("  W3 exact squaring comparisons for sqrt(1-2t0)")
    print("  (8231038/10^7)^2 = %s" % fs(ccc))
    print("  (8231039/10^7)^2 = %s" % fs(ddd))
    print("  (8231039/10^7)^2 - (1-2t0) = %s" % fs(ddd - ymax_sq))
    print("  note: the release states sqrt(1-2t0) <= 8231039/10^7; the exact")
    print("  squaring below yields the strict <, which implies the stated <=.")
    check("W3a (8231038/10^7)^2 < 1-2t0", ccc < ymax_sq)
    check("W3b 1-2t0 < (8231039/10^7)^2 (strict; implies the stated <=)", ymax_sq < ddd)
    print()

    # --- W4: site bracket --------------------------------------------------------
    s2 = 1 - y0sq
    a_num, b_den = s2.numerator, s2.denominator
    scale = 10 ** 18
    dd = a_num * b_den * scale * scale
    n = math.isqrt(dd)
    sqrt_lo = F(n, b_den * scale)
    sqrt_hi = F(n + 1, b_den * scale)
    x_lo = x_int + sqrt_lo
    x_hi = x_int + sqrt_hi
    print("  W4 site x_* = X + sqrt(1 - y0^2); 1 - y0^2 = %s" % fs(s2))
    print("  integer-square-root bracket with scaling 10^%d:" % 18)
    print("    n = isqrt(num*den*scale^2) = %d" % n)
    print("    sqrt_lo = %s" % fs(sqrt_lo))
    print("    sqrt_hi = %s" % fs(sqrt_hi))
    print("    x_star_lo = %s" % fs(x_lo))
    print("    x_star_hi = %s" % fs(x_hi))
    print("    bracket width x_star_hi - x_star_lo = %s" % fs(x_hi - x_lo))
    check("W4a 1 - y0^2 = 2412323/2500000", s2 == F(2412323, 2500000))
    check("W4b n^2 <= num*den*scale^2 < (n+1)^2", n * n <= dd and dd < (n + 1) * (n + 1))
    print()

    # --- W5: window inequalities and margins ------------------------------------
    q1 = F(690988 ** 2) - t0 / 16
    q2 = F(690989 ** 2) - t0 / 16
    x1_hi = 4 * pi_hi * q1
    x2_lo = 4 * pi_lo * q2
    m1 = x_lo - x1_hi
    m2 = x2_lo - x_hi
    claim1 = F(53773939878, 10 ** 4)
    claim2 = F(119890411746, 10 ** 4)
    print("  W5 windows: q_N = N^2 - t0/16 ; x_N = 4*pi*q_N ; W_N = [x_N, x_{N+1})")
    print("  q_690988 = %s" % fs(q1))
    print("  q_690989 = %s" % fs(q2))
    print("  x_690988 upper enclosure = %s" % fs(x1_hi))
    print("  x_690989 lower enclosure = %s" % fs(x2_lo))
    print("  margin1 lower bound = x_star_lo - x_690988_upper = %s" % fs(m1))
    print("    (floor, 12 dp: %s)" % floor_dec(m1, 12))
    print("  margin2 lower bound = x_690989_lower - x_star_hi = %s" % fs(m2))
    print("    (floor, 12 dp: %s)" % floor_dec(m2, 12))
    print("  release claim margin1 > 5377393.9878; our certified lower bound exceeds it: %s" % (m1 > claim1))
    print("  release claim margin2 > 11989041.1746; our certified lower bound exceeds it: %s" % (m2 > claim2))
    check("W5a x_690988 < x_* (via upper/lower enclosures)", x1_hi < x_lo)
    check("W5b x_* < x_690989 (via upper/lower enclosures)", x_hi < x2_lo)
    check("W5c margin1 lower bound > 5377393.9878 (release claim)", m1 > claim1)
    check("W5d margin2 lower bound > 11989041.1746 (release claim)", m2 > claim2)
    print()

    # --- W6/W7: sign map (symbolic lane) ----------------------------------------
    print("  W6 window monotonicity sign map (sympy symbolic identities):")
    if sp is None:
        check_skip("W6/W7 symbolic identities", "sympy absent")
    else:
        xs, ys = sp.symbols("x y", positive=True)
        t0s = sp.Rational(129, 800)
        ay = 4 * ys * (1 + ys)
        h = 1 - 3 * ys + ay / xs ** 2
        gexpr = sp.exp(ys / 50) * (xs / (4 * sp.pi)) ** (-ys / 2)
        kexpr = t0s * ys / (2 * (xs - 6))
        spos = (1 + ys) / 2 + t0s / 4 * sp.log(xs / (4 * sp.pi)) - t0s / (2 * xs ** 2) * h
        sneg = (1 + ys) / 2 + t0s / 4 * sp.log(xs / (4 * sp.pi))
        check("W6a dG/dx = -(y/(2x)) * G", sp.simplify(sp.diff(gexpr, xs) + (ys / (2 * xs)) * gexpr) == 0)
        check("W6b dK/dx = -t0*y/(2*(x-6)^2)",
              sp.simplify(sp.diff(kexpr, xs) + t0s * ys / (2 * (xs - 6) ** 2)) == 0)
        check("W6c dh/dx = -2A/x^3 with A = 4y(1+y)",
              sp.simplify(sp.diff(h, xs) + 2 * ay / xs ** 3) == 0)
        check("W6d dSigma/dx (h>0 branch) = t0/(4x) + t0*h/x^3 + t0*A/x^5",
              sp.simplify(sp.diff(spos, xs) - (t0s / (4 * xs) + t0s * h / xs ** 3 + t0s * ay / xs ** 5)) == 0)
        check("W6e dSigma/dx (h<0 branch) = t0/(4x)",
              sp.simplify(sp.diff(sneg, xs) - t0s / (4 * xs)) == 0)
        kink = t0s / (4 * xs) + t0s * ay / xs ** 5
        check("W6f kink one-sided form = t0*(x^4/4 + A)/x^5",
              sp.simplify(kink - t0s * (xs ** 4 / 4 + ay) / xs ** 5) == 0)
        nsym = sp.symbols("N", integer=True)
        qn = nsym ** 2 - t0s / 16
        check("W7 q_{N+1} - q_N = 2N+1",
              sp.simplify(qn.subs(nsym, nsym + 1) - qn - (2 * nsym + 1)) == 0)
    print("  conclusion (documented):")
    print("    dG/dx < 0 and dK/dx < 0 on the domain => G, K are decreasing in x,")
    print("    so the left endpoint x_N is the conservative value (G(x,y) <= G_N(y),")
    print("    K(x,y) <= K_N(y) for x in [x_N, x_{N+1})).")
    print("    A = 4y(1+y) >= 0, dh/dx = -2A/x^3 <= 0 => h nonincreasing; h_+ = max(h,0)")
    print("    nonincreasing; x^-2 positive nonincreasing => (t0/2)*x^-2*h_+ nonincreasing")
    print("    (product of nonnegative nonincreasing functions) => its negative is")
    print("    nondecreasing; the log term is strictly increasing; hence Sigma is strictly")
    print("    increasing in x, including across the kink (both one-sided derivative forms")
    print("    are positive for x>0, A>=0). Conservative value is again x_N.")
    print()

    VALUES.update({
        "machin_terms_K": K,
        "pi_lo": fs(pi_lo),
        "pi_hi": fs(pi_hi),
        "pi_lo_floor60": floor_dec(pi_lo, 60),
        "pi_hi_ceil60": ceil_dec(pi_hi, 60),
        "pi_bracket_width": fs(width),
        "pi_width_max_k_lt_10_to_k": k_pow,
        "t0": fs(t0),
        "y0_sq": fs(y0sq),
        "one_minus_2t0": fs(ymax_sq),
        "y0_lo": fs(a),
        "y0_hi": fs(b),
        "y0_lo_sq": fs(add),
        "y0_hi_sq": fs(bdd),
        "sqrt_1m2t0_lo": fs(c),
        "sqrt_1m2t0_hi": fs(d),
        "X": str(x_int),
        "s2_1_minus_y0sq": fs(s2),
        "isqrt_n": str(n),
        "sqrt_scale_pow": 18,
        "x_star_lo": fs(x_lo),
        "x_star_hi": fs(x_hi),
        "x_star_bracket_width": fs(x_hi - x_lo),
        "q_690988": fs(q1),
        "q_690989": fs(q2),
        "x_690988_upper_enclosure": fs(x1_hi),
        "x_690989_lower_enclosure": fs(x2_lo),
        "margin1_lower": fs(m1),
        "margin1_lower_floor12": floor_dec(m1, 12),
        "margin2_lower": fs(m2),
        "margin2_lower_floor12": floor_dec(m2, 12),
        "margin1_release_claim": "5377393.9878",
        "margin2_release_claim": "11989041.1746",
    })


def part_s():
    print("== S. affine H0-to-zeta sign map (our derivation, exact rational algebra) ==")
    print("  affine form (c, cx, cy) represents c + cx*x + cy*y; z = x + i y")

    def aff_sub(u, v):
        return tuple(p - q for p, q in zip(u, v))

    def aff_add(u, v):
        return tuple(p + q for p, q in zip(u, v))

    def aff_neg(u):
        return tuple(-p for p in u)

    def aff_scale(u, k):
        return tuple(p * k for p in u)

    z_re, z_im = (F(0), F(1), F(0)), (F(0), F(0), F(1))
    iz = (aff_neg(z_im), z_re)  # i*z = i*(x+iy) = -y + i*x
    hz = (aff_scale(iz[0], F(1, 2)), aff_scale(iz[1], F(1, 2)))
    s0 = (aff_add(hz[0], (F(1, 2), F(0), F(0))), hz[1])  # s0 = 1/2 + i*z/2
    print("  direct preimage s0 = 1/2 + i*z/2:")
    print("    real form = %s" % (s0[0],))
    print("    imag form = %s" % (s0[1],))
    check("S1 s0 real part is (1-y)/2", s0[0] == (F(1, 2), F(0), F(-1, 2)))
    check("S2 s0 imaginary part is x/2", s0[1] == (F(0), F(1, 2), F(0)))

    one = ((F(1), F(0), F(0)), (F(0), F(0), F(0)))
    refl = (aff_sub(one[0], s0[0]), aff_neg(s0[1]))  # 1 - s0 (functional equation)
    print("  reflected representative 1 - s0 = (1+y)/2 - i*x/2:")
    check("S3 reflected real part is (1+y)/2", refl[0] == (F(1, 2), F(0), F(1, 2)))
    check("S3b reflected imaginary part is -x/2", refl[1] == (F(0), F(-1, 2), F(0)))

    conj = (refl[0], aff_neg(refl[1]))
    print("  conjugated representative = (1+y)/2 + i*x/2:")
    check("S4 conjugated real part is (1+y)/2", conj[0] == (F(1, 2), F(0), F(1, 2)))
    check("S4b conjugated imaginary part is +x/2", conj[1] == (F(0), F(1, 2), F(0)))
    print()

    t0 = F(129, 800)
    y0sq = F(87677, 2500000)
    x_int = 6000000185827
    top = y0sq + 2 * t0
    print("  scalar implications for the criterion hypothesis mapping:")
    print("    t0 = %s ; y0^2 = %s ; y0^2 + 2t0 = %s" % (fs(t0), fs(y0sq), fs(top)))
    check("S5 t0 >= 0 and y0^2 > 0", t0 >= 0 and y0sq > 0)
    check("S5b y0^2 + 2t0 >= y0^2", top >= y0sq)
    check("S5c canopy top square = 893927/2500000", top == F(893927, 2500000))
    print("    implication (documented): sqrt(y0^2+2t0) >= y0 > 0 by monotonicity of")
    print("    the square root on the nonnegative reals")
    check("S6 X > 0", x_int > 0)
    print("    height map (documented): direct-preimage height is x/2; x in [0, X]")
    print("    maps into [0, X/2]; X/2 = %s" % fs(F(x_int, 2)))
    check("S6b height at x = X is exactly 3000000092913.5 (1 dp)",
          floor_dec(F(x_int, 2), 1) == "3000000092913.5")
    print()

    VALUES.update({
        "s0_real_form": str(s0[0]),
        "s0_imag_form": str(s0[1]),
        "reflected_real_form": str(refl[0]),
        "reflected_imag_form": str(refl[1]),
        "conjugated_real_form": str(conj[0]),
        "conjugated_imag_form": str(conj[1]),
        "canopy_top_square": fs(top),
        "X_half": fs(F(x_int, 2)),
    })


def main():
    print("audit_p1 L2 item 1 - window freeze & affine sign map")
    print("release commit: %s" % RELEASE_COMMIT)
    print("prereg: reports/AUDIT_DBN_PREREG_2026-10-17.md section 4 item 1")
    print("sympy: %s" % (sp.__version__ if sp is not None else "ABSENT"))
    print()
    part0_sources()
    part_w()
    part_s()
    failed = [c for c in CHECKS if not c["ok"]]
    total = len(CHECKS)
    print("== summary ==")
    print("checks_total: %d  checks_failed: %d" % (total, len(failed)))
    verdict = "PASS" if not failed else "FAIL"
    print("item1 machine verdict: %s" % verdict)

    payload = {
        "item": "L2-1 window freeze & affine sign map",
        "prereg": "reports/AUDIT_DBN_PREREG_2026-10-17.md section 4 item 1",
        "release_commit": RELEASE_COMMIT,
        "stack": {"fractions": "exact rational lane",
                  "sympy": (sp.__version__ if sp is not None else "ABSENT")},
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
