"""Chi-square specification for the S2 surrogate statistic (K-Q4).

Frozen at 2026-10-19 (values computed offline with mpmath at dps 70 and
literals frozen here; roundtrip check |Phi(q_k) - k/16| <= 1e-70):

* 16 bins delimited by the 15 quantile knots q_1..q_15 of N(0,1); the
  interior knots are symmetric about q_8 = 0;
* expected count E_b = samples/16 exactly (rational);
* the frozen floor rule drops every cell with expected count < 5 (cells
  dropped are recorded; the threshold 5 is frozen);
* exceedance diagnostic: z >= Z_STAR = 3.5, reference probability
  P_STAR (frozen literal).

The statistical layer is float64 by design (scope note in the spec); the
certified layer never consumes these values.
"""

from __future__ import annotations

from fractions import Fraction

__all__ = [
    "BINS",
    "KNOTS",
    "Z_STAR",
    "P_STAR",
    "EXPECTED_FLOOR_MIN",
    "bin_index",
    "counts_from",
    "expected_counts",
    "floor_rule",
    "chi2_exact",
    "exceedances",
]

BINS = 16

# q_k = Phi^{-1}(k/16), k = 1..15 (ascending, symmetric; q_8 = 0 exact).
KNOTS = (
    "-1.53412054435254631170839905903716552576425115",
    "-1.15034938037600817829676531083058533654439507",
    "-0.887146559018876056685664259810216476611600454",
    "-0.674489750196081743202227014541307185386904415",
    "-0.488776411114669498910885782949055276352904866",
    "-0.31863936396437516302194846367007464334964034",
    "-0.157310684610170695522370718076290313620386998",
    "0",
    "0.157310684610170695522370718076290313620386998",
    "0.31863936396437516302194846367007464334964034",
    "0.488776411114669498910885782949055276352904866",
    "0.674489750196081743202227014541307185386904415",
    "0.887146559018876056685664259810216476611600454",
    "1.15034938037600817829676531083058533654439507",
    "1.53412054435254631170839905903716552576425115",
)

Z_STAR = "3.5"

#: P(z >= 3.5) for standard normal, frozen literal.
P_STAR = "0.000232629079035525036349925886727984773548749336"

#: K-Q4 frozen floor: drop cells with expected count below this value.
EXPECTED_FLOOR_MIN = 5


def bin_index(z: float) -> int:
    """Bin of z in {0..15}: index = number of knots <= z."""
    c = 0
    for s in KNOTS:
        if z < float(s):
            break
        c += 1
    return c


def counts_from(zs) -> list:
    counts = [0] * BINS
    for z in zs:
        counts[bin_index(z)] += 1
    return counts


def expected_counts(samples: int) -> list:
    return [Fraction(samples, BINS)] * BINS


def floor_rule(expected: list, floor: int = EXPECTED_FLOOR_MIN):
    """K-Q4: kept/dropped cell indices by the frozen expected-count floor."""
    kept = [i for i, e in enumerate(expected) if e >= floor]
    dropped = [i for i, e in enumerate(expected) if e < floor]
    return kept, dropped


def chi2_exact(counts: list, expected: list, kept: list):
    """Exact rational chi-square over kept cells; None if no cell is kept."""
    if not kept:
        return None
    t = Fraction(0)
    for i in kept:
        t += (Fraction(counts[i]) - expected[i]) ** 2 / expected[i]
    return t


def exceedances(zs, z_star: str = Z_STAR) -> int:
    zt = float(z_star)
    return sum(1 for z in zs if z >= zt)
