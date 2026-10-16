"""Unit tests for the engine-B verification harness helpers.

Locks: the B1 decimal-exact parser + fake-zero census, the B3 gate
re-verification (sorted strict-increase, storage-rounding budget for
trace/Frobenius), the exact binary64 -> mpf conversion, the 10-ulp
comparison semantics, the float64-compensated building blocks (fsum unfold,
searchsorted histogram identical to numpy's, Neumaier convolution, weights),
and the declared kernel/target path shape. All tests are self-contained
(no instrument folder, no spectra files) so CI can run them anywhere.
"""

import math

import mpmath as mp
import numpy as np
from decimal import Decimal

from msaf.gw_engine_b_verify import (N_BINS, b_chi2_row, b_conv_f64,
                                     b_hist_f64, b_local_spacing_f64,
                                     b_unfold_f64, b_weights,
                                     compensated_col_sum, compare_bins,
                                     fake_zero_census, mpf_of_float, ulp60,
                                     verify_gate_GM0, _dec_exact)


def test_ulp60_quantum():
    assert ulp60(Decimal(0)) == Decimal(0)
    assert ulp60(Decimal("1.23")) == Decimal("1e-59")
    assert ulp60(Decimal("758.9")) == Decimal("1e-57")
    assert ulp60(Decimal("6.5e-248")) == Decimal("1e-307")


def test_dec_exact_accepts_zero_and_tiny():
    assert _dec_exact("0") == 0
    assert _dec_exact("0.000e-100") == 0
    assert _dec_exact("4.957228556879732854268369724334977716209e-1685") != 0


def _synthetic_dec(re_list, rad_list, trace, frob2, n_pos):
    return {
        "meta": {},
        "trace_mid": Decimal(trace),
        "frob2_mid": Decimal(frob2),
        "gate_GM0": {"G-M0a_finite": True, "G-M0b_inertia": True,
                     "G-M0c_strict": True, "G-M0d_trace": True,
                     "G-M0e_frob": True},
        "inertia": {"n_pos": n_pos, "n_neg": 0, "indeterminate": 0},
        "re": [Decimal(s) for s in re_list],
        "re_rad": [Decimal(s) for s in rad_list],
        "im_abs": [Decimal("0") for _ in re_list],
    }


def test_fake_zero_census_flags_subnormal_radii():
    dec = _synthetic_dec(["1.0", "2.0"], ["1e-700", "1e-700"], "3", "5", 2)
    census = fake_zero_census(dec)
    assert census["re"]["would_fake_zero_under_binary64"] == 0
    assert census["re_rad"]["would_fake_zero_under_binary64"] == 2
    assert census["total_would_fake_zero_under_binary64"] == 2
    assert census["re_rad"]["nonzero_below_float64_normal_min"] == 2


def test_verify_gate_reproduces_pass_on_synthetic():
    dec = _synthetic_dec(["1", "2", "3"], ["1e-70", "1e-70", "1e-70"],
                         "6", "14", 3)
    out = verify_gate_GM0(dec)
    assert out["reproduced_all"] and out["stored_all_true"]
    assert out["d_trace"]["absdiff"] == "0"
    assert out["c_strict"]["violations_after_sort"] == 0


def test_verify_gate_flags_moment_mismatch():
    dec = _synthetic_dec(["1", "2", "3"], ["1e-70", "1e-70", "1e-70"],
                         "6.1", "14", 3)
    out = verify_gate_GM0(dec)
    assert not out["d_trace"]["pass"]
    assert not out["reproduced_all"]


def test_verify_gate_flags_unsorted_after_sort_duplicate():
    dec = _synthetic_dec(["1", "1", "2"], ["1e-70", "1e-70", "1e-70"],
                         "4", "6", 3)
    out = verify_gate_GM0(dec)
    assert out["c_strict"]["violations_after_sort"] == 1
    assert not out["reproduced_all"]


def test_mpf_of_float_is_exact():
    with mp.workdps(80):
        assert mpf_of_float(1.5) == mp.mpf("1.5")
        exact_01 = mp.mpf("0.1000000000000000055511151231257827021181583404541015625")
        assert mpf_of_float(0.1) == exact_01
        assert mpf_of_float(0.1) != mp.mpf("0.1")


def test_b_local_spacing_uniform_grid():
    y = np.arange(21, dtype=float)
    h = b_local_spacing_f64(y)
    assert h.shape == (21,)
    assert np.allclose(h, 1.0, rtol=0, atol=1e-15)


def test_b_unfold_f64_mean_gap_one_and_increasing():
    rng = np.random.default_rng(7)
    y = np.sort(rng.uniform(0.0, 100.0, 50))
    x = b_unfold_f64(y, 0.5)
    assert x.shape == (50,)
    assert np.all(np.diff(x) > 0)
    gaps = np.diff(x)
    assert abs(math.fsum(gaps.tolist()) / 49 - 1.0) < 1e-12


def test_b_hist_f64_equals_numpy_histogram():
    rng = np.random.default_rng(11)
    x = np.sort(np.concatenate([rng.uniform(0.0, 30.0, 60)]))
    hist_b = b_hist_f64(x)
    n = x.size
    D = (x[:, None] - x[None, :]).ravel()
    D = D[np.repeat(np.arange(n), n) != np.tile(np.arange(n), n)]
    edges = np.arange(-11.0, 11.0 + 1e-9, 0.01)
    hist_a, _ = np.histogram(D, bins=edges)
    assert hist_b.shape == (2200,)
    assert np.array_equal(hist_b, hist_a.astype(float))


def test_b_conv_f64_matches_direct_dot():
    rng = np.random.default_rng(13)
    Kf = rng.normal(size=(N_BINS, 2200))
    hist = rng.integers(0, 5, size=2200).astype(float)
    got = b_conv_f64(hist, Kf, 301)
    want = (Kf @ hist) / 301
    assert np.allclose(got, want, rtol=1e-12, atol=1e-15)


def test_compensated_col_sum_matches_column_sums():
    rng = np.random.default_rng(17)
    M = rng.normal(size=(3000, 4))
    got = compensated_col_sum(M)
    want = np.array([math.fsum(M[:, j].tolist()) for j in range(4)])
    assert np.allclose(got, want, rtol=1e-12, atol=1e-12)


def test_b_weights_positive_and_match_numpy_var():
    rng = np.random.default_rng(19)
    cv = rng.normal(size=(200, N_BINS)) + rng.normal(size=N_BINS)
    w = b_weights(cv)
    assert np.all(np.isfinite(w)) and np.all(w > 0)
    ref = 1.0 / cv.var(axis=0, ddof=1)
    assert np.allclose(w, ref, rtol=1e-10)


def test_b_chi2_row_zero_and_manual():
    tgt = np.array([0.1] * N_BINS)
    w = np.array([2.0] * N_BINS)
    assert b_chi2_row(tgt.copy(), w, tgt) == 0.0
    cv = tgt + 1e-3
    got = b_chi2_row(cv, w, tgt)
    assert abs(got - 20 * 2.0 * 1e-6) < 1e-18


def test_compare_bins_10ulp_semantics():
    cvA = np.ones(N_BINS)
    one_ulp = math.ulp(1.0)
    cvB = [mpf_of_float(1.0) + mpf_of_float(one_ulp)] * N_BINS
    recs = compare_bins(cvB, cvA, "cv")
    assert all(r["within_10ulp"] and r["within_frozen_or"] for r in recs)
    cvB2 = [mpf_of_float(1.0) + 100 * mpf_of_float(one_ulp)] * N_BINS
    recs2 = compare_bins(cvB2, cvA, "cv")
    assert not any(r["within_10ulp"] for r in recs2)
    assert all(r["within_1e9rel"] for r in recs2)      # rel ~ 2.2e-14 < 1e-9
    assert all(r["within_frozen_or"] for r in recs2)   # frozen OR holds
    cvB3 = [mpf_of_float(1.0) + mpf_of_float(1e-3)] * N_BINS
    recs3 = compare_bins(cvB3, cvA, "cv")
    assert not any(r["within_frozen_or"] for r in recs3)
