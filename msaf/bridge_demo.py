"""Reproducible demo of the two-space bridge kit (``msaf/bridge.py``).

Run:

    python -m msaf.bridge_demo

D1  zeta(2) = sum_{n>=1} 1/n**2     (two-sided rational bridge; L2)
D2  int_1^inf exp(-x) dx           (closed form + exponential envelope; L3)
D3  int_2^inf exp(-x**2) dx        (Gaussian tail bound; L4)

Every block prints [B] bounded part, [J] tail interval and [U] total
interval with the rigorous budget verdict. Deterministic at fixed precision
(Arb, prec = 128); no float ever decides anything.
"""

from __future__ import annotations

from flint import arb, ctx

from msaf.bridge import (
    assemble,
    choose_cutoff,
    choose_cutoff_real,
    exp_envelope_tail,
    gaussian_tail_ub,
    pseries_tail_bounds,
    split_budget,
)

PREC = 128


def _zeta2() -> bool:
    eps = arb("1e-8")
    budget = split_budget(eps)
    p = arb(2)

    def width(n: int) -> arb:
        lo, hi = pseries_tail_bounds(p, n)
        return hi - lo

    n = choose_cutoff(width, budget.eps_tail)
    partial = sum(1 / arb(k) ** 2 for k in range(1, n + 1))
    lo, hi = pseries_tail_bounds(p, n)
    cert = assemble("zeta(2) via partial sum + p-series tail", partial, hi, eps, tail_lo=lo)
    pi2_6 = arb.pi() ** 2 / 6
    total_lo, total_hi = cert.total()
    contains = bool(total_lo <= pi2_6) and bool(pi2_6 <= total_hi)
    print("D1  zeta(2) = sum_{n>=1} 1/n^2   (L2, two-sided)")
    print("    cutoff N = %d (partial-sum terms: %d)" % (n, n))
    for line in cert.lines():
        print("   ", line)
    print("    contains pi^2/6  :", contains)
    print()
    return cert.certified and contains


def _exp_integral() -> bool:
    eps = arb("1e-18")
    budget = split_budget(eps)
    m = choose_cutoff_real(lambda x: exp_envelope_tail(x), budget.eps_tail, lo=1.0, hi=100.0)
    e_minus_m = (-m).exp()
    bounded = (-arb(1)).exp() - e_minus_m  # int_1^M exp(-x) dx, closed form
    cert = assemble("int_1^inf exp(-x) dx (closed form + envelope)", bounded, e_minus_m, eps)
    total_lo, total_hi = cert.total()
    bracket = bool(arb("0.36") <= total_lo) and bool(total_hi <= arb("0.38"))
    print("D2  int_1^inf exp(-x) dx   (L3, envelope C=1 lam=1)")
    print("    cutoff M = %s" % m)
    for line in cert.lines():
        print("   ", line)
    print("    bracket [0.36, 0.38] :", bracket)
    print()
    return cert.certified and bracket


def _gaussian_tail() -> bool:
    eps = arb("0.005")
    ub = gaussian_tail_ub(arb(2))
    cert = assemble("gaussian tail bound at M=2 (L4)", arb(0), ub, eps)
    print("D3  int_2^inf exp(-x^2) dx   (L4, Gaussian tail)")
    for line in cert.lines():
        print("   ", line)
    print()
    return cert.certified


def main() -> int:
    ctx.prec = PREC
    print("BRIDGE KIT DEMO -- bounded [B] + bridge [J] + unbounded [U]")
    print("arb precision: %d" % ctx.prec)
    print()
    ok = _zeta2() and _exp_integral() and _gaussian_tail()
    print("ALL DEMOS CERTIFIED:", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
