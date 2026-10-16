"""Unit tests for the H1 floor-refinement extractor helpers.

Locks the frozen-format arithmetic (Clopper-Pearson bound for k = 0 with the
spec formula 1 - 0.05^(1/n), two-sided interval for k > 0, 6-significant-
digit decimal rendering), the unchanged verdict rule, and the frozen C4
classification tree. Also round-trips the capped-thread sanity rerun log
(reports/mont_run_rerun_2000_100_100.txt) through parse_log: it must carry
36 exact-count captures and reproduce the sealed dim-201 values exactly
(chi2 14621.8788 / 2146.3923, k_GUE = 0).
"""

import os

from msaf.gw_h1_extract import (CELL_RE, classify_c4, cp95, p6, p_field,
                                parse_log, verdict_from_k)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
RERUN = os.path.join(ROOT, "reports", "mont_run_rerun_2000_100_100.txt")


def test_cp95_zero_uses_frozen_bound():
    lo, hi = cp95(0, 20000)
    assert lo == 0.0
    assert hi == 1 - 0.05 ** (1.0 / 20000)
    assert hi < 1.50e-4          # the spec's stated bound


def test_cp95_two_sided_for_positive_k():
    lo, hi = cp95(360, 20000)
    assert 0.0 < lo < 360 / 20000 < hi < 0.021


def test_p_field_zero_states_a_bound():
    hi = 1 - 0.05 ** (1.0 / 20000)
    assert p_field(0, 20000) == "0/20000 (p < %.5e, 95%% CP upper bound)" % hi
    assert p_field(360, 20000) == "360/20000 (1.80000e-02)"


def test_p6_six_significant_digits():
    assert p6(0, 20000) is None
    assert p6(360, 20000) == "1.80000e-02"
    assert p6(1, 20000) == "5.00000e-05"


def test_verdict_rule_unchanged():
    assert verdict_from_k(360, 500, 20000) == (
        "INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION")
    assert verdict_from_k(2000, 200, 20000) == (
        "CONSISTENT WITH MONTGOMERY/GUE, DISTINGUISHABLE FROM POISSON")
    assert verdict_from_k(2000, 2000, 20000) == (
        "NO DISCRIMINATION AT N=401")


def test_classify_c4_tree():
    # homogeneity rejected (one seed far off) -> branch 1
    assert classify_c4([0, 0, 0, 0, 3000])["classification"].startswith(
        "NOT STABLE (homogeneity")
    # pooled below the 0.010 floor -> branch 2
    assert classify_c4([0, 0, 0, 0, 0])["classification"] == (
        "NOT STABLE (pooled p_hat < 0.010)")
    # persistent off-floor signal, homogeneous -> branch 3
    stable = classify_c4([360] * 5)
    assert stable["classification"] == "STABLE OFF-FLOOR"
    assert stable["pooled_k"] == 1800 and stable["pooled_n"] == 100000
    # pooled above the 0.045 ceiling -> branch 4
    assert classify_c4([1000] * 5)["classification"] == "MIXED"


def test_cell_regex_on_frozen_block():
    block = (
        "  chart T (ln lambda, PRIMARY)   sigma_u 0.3 : chi2 = 14621.8788\n"
        "      p_GUE   = P(chi2_GUE   >= chi2_obs) = 0.0000\n"
        "      p_GOE   = P(chi2_GOE   >= chi2_obs) = 0.0000  [reported only]\n"
        "      p_Pois  = P(chi2_Pois  <= chi2_obs) = 0.9910  [lower tail, #1001631]\n"
        "      -> CONSISTENT WITH MONTGOMERY/GUE, DISTINGUISHABLE FROM POISSON\n")
    hits = CELL_RE.findall(block)
    assert len(hits) == 1
    chart, su, chi2, _pg, _pgoe, ppois, verdict = hits[0]
    assert (chart, su) == ("T", "0.3")
    assert float(chi2) == 14621.8788
    assert float(ppois) == 0.9910
    assert verdict.startswith("CONSISTENT")


def test_parse_log_rerun_roundtrip():
    log = parse_log(RERUN)
    assert log["samples"] == 2000 and log["seed"] == 20260927
    assert log["cells_parsed"] == 6
    assert log["exact_capture_count"] == 36
    assert all(n == 2000 for n, _ in log["exact_counts"])
    assert log["cells"]["T|0.3"]["chi2_obs"] == 14621.8788
    assert log["cells"]["T|0.3"]["k_gue"] == 0
    assert log["cells"]["T|0.5"]["chi2_obs"] == 2146.3923
