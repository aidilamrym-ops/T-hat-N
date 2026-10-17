# -*- coding: utf-8 -*-
"""Re-measure the enclosure-radius semantics of the Route A2 ladder.

WHY THIS EXISTS (2026-10-17)
----------------------------
reports/lambda_min_eig_ladder*.json record `lambda_min_rad` as
`float(lo.rad().abs_upper())`. That float conversion collapses every
radius below ~4.9e-324 (the float64 subnormal floor) to exactly 0.0 --
the same trap the kernel already documents in `msaf/evolution.py`
("Writing it as a JSON number would round it through binary64 and could
land on exactly 0.0 for a radius below 1e-308, manufacturing an exact
zero that the measurement never produced").

Earlier prose (THREE_TASKS 2026-10-15, HANDOFF, dashboard v5) read that
field as "radius exactly zero / isolated to a point". This script
re-measures the same arb objects at small dims and prints what is
actually true, ASCII only:

  * the true enclosure radii are nonzero (~1e-1790 at dims 17/33);
  * `is_exact()` is False -- no enclosure is a point;
  * no enclosure contains zero -- that is the certified content.

The script asserts nothing about larger dims it does not re-run; the
registry value 0.0 there is explained by the same underflow mechanism.

Run:  python msaf/gw_radius_registry_check.py
"""
from __future__ import annotations

import os
import re
import sys

GW_DIR = os.environ.get("GW_DIR", r"C:/Users/usER/oracle-toe/GUINAND_WEIL")
if GW_DIR not in sys.path:
    sys.path.insert(0, GW_DIR)


def rad_tail(z) -> str:
    """The '+/- X' radius shown by repr(), extracted verbatim."""
    m = re.search(r"\+/-\s*([0-9.e+-]+)\]", repr(z))
    return m.group(1) if m else "?"


def head(z) -> str:
    """The leading number of repr(z), extracted verbatim."""
    m = re.match(r"\[([0-9.e+-]+)", repr(z))
    return m.group(1) if m else "?"


def main() -> int:
    from flint import ctx, arb

    import source_arb_ldlt_certify as gw

    # Tooling semantics first: python-flint '==' tests EXACT equality only.
    # For an inexact ball x, x == x is False -- comparing inexact balls with
    # '==' is a trap (it nearly read as "the matrix is not symmetric").
    x = arb(1) / 3
    print("semantics: (arb(1)/3) == (arb(1)/3) -> %s   "
          "(exact-equality-only semantics; use mid/rad tests instead)"
          % (x == x))
    print("semantics: x.mid() == x.mid() -> %s ; arb(2) == 2 -> %s"
          % (x.mid() == x.mid(), arb(2) == 2))

    for n_block in (8, 16):
        ctx.prec = 6000
        A, dim = gw.build_arb_tau(13, n_block, 6000)
        out = A.eig()
        vals = sorted(out, key=lambda z: z.real.mid())
        lo = vals[0].real
        hi = vals[-1].real
        n_exact = sum(1 for z in out if z.real.is_exact())
        n_imag_zero = sum(1 for z in out if z.imag == 0)
        leak = max(z.imag.abs_upper() for z in out)
        n_mid = sum(1 for i in range(dim) for j in range(dim)
                    if A[i, j].mid() != A[j, i].mid())
        n_rad = sum(1 for i in range(dim) for j in range(dim)
                    if A[i, j].rad().mid() != A[j, i].rad().mid())
        print("dim %d: n=%d  float(rad)=%.1f  is_exact(lo)=%s  "
              "contains0(lo)=%s" % (
                  dim, len(out), float(lo.rad().abs_upper()),
                  lo.is_exact(), bool(lo.contains(arb(0)))))
        print("  ball-symmetry (exact-dyadic mid/rad test): "
              "mid-diff entries %d/%d, rad-diff entries %d/%d -> %s"
              % (n_mid, dim * dim, n_rad, dim * dim,
                 "EXACTLY SYMMETRIC as a ball matrix"
                 if n_mid == 0 and n_rad == 0 else "asymmetric"))
        print("  radius lo   = +/- %s (repr tail, verbatim)" % rad_tail(lo))
        print("  radius hi   = +/- %s (repr tail, verbatim)" % rad_tail(hi))
        print("  exact real parts in the whole spectrum: %d/%d"
              % (n_exact, len(out)))
        print("  imag parts exactly zero: %d/%d  max leak = %s "
              "(float registry = %r)" % (
                  n_imag_zero, len(out), head(leak), float(leak)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
