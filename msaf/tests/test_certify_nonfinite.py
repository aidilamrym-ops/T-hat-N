"""A non-finite residual must never be certified as a zero.

Regression test for a silent pass found while planning the next track
(2026-10-15). Arb answers True to `arb('nan').contains(0)`, so
`certify('r', arb('nan'))` returned

    PASS-BY-ENCLOSURE: 0 lies in the residual ball

A NaN is a computation that FAILED. Reporting it as a certified zero is
the most damaging defect this program could ship: `evaluate_xi`'s own
docstring calls a fake root "the most damaging possible defect in a
zero-finding kernel", and this is exactly how one gets in.

The rule these tests pin: a non-finite residual is neither a
confirmation nor a refutation, and no entry point may answer a
containment question about it.
"""
import pytest
from flint import acb, arb, arb_mat

from msaf.certify import (
    NOT_FINITE_VERDICT,
    certify,
    certify_matrix,
    contains_zero,
    contains_zero_complex,
    contains_zero_matrix,
    is_finite,
)

NON_FINITE = ["nan", "inf", "-inf"]


@pytest.mark.parametrize("text", NON_FINITE)
def test_non_finite_is_not_finite(text):
    assert is_finite(arb(text)) is False


@pytest.mark.parametrize("text", NON_FINITE)
def test_non_finite_never_certified(text):
    assert contains_zero(arb(text)) is False


@pytest.mark.parametrize("text", NON_FINITE)
def test_non_finite_never_yields_a_pass_verdict(text):
    cert = certify("residual", arb(text))
    assert cert.finite is False
    assert cert.certified is False
    assert cert.exact is False
    assert not cert.verdict.startswith("PASS")
    assert cert.verdict == NOT_FINITE_VERDICT


def test_nan_verdict_names_the_failure():
    # The verdict must say the evaluation failed, not merely that zero was
    # not found: a reader who sees "does not contain zero" will record a
    # refutation that never happened.
    assert "not a refutation" in NOT_FINITE_VERDICT.lower()
    assert "nan" in NOT_FINITE_VERDICT.lower()


def test_matrix_path_has_the_same_guard():
    m = arb_mat(1, 1)
    m[0, 0] = arb("nan")
    assert contains_zero_matrix(m) is False
    cert = certify_matrix("M", m)
    assert cert.finite is False
    assert not cert.verdict.startswith("PASS")


def test_complex_path_has_the_same_guard():
    assert contains_zero_complex(acb("nan")) is False
    assert contains_zero_complex(acb("inf")) is False


def test_finite_results_are_unchanged():
    # The guard must not have broken the ordinary paths: an exact zero
    # still certifies, and a ball that misses zero still refutes.
    exact = certify("r", arb(0))
    assert exact.certified and exact.exact
    assert exact.verdict.startswith("PASS")
    miss = certify("r", arb("1e-40"))
    assert miss.certified is False
    assert miss.verdict == "FAIL: residual does not contain zero"
    miss2 = certify("r", arb("-1e-40"))
    assert miss2.certified is False


def test_a_nan_wide_ball_cannot_impersonate_a_containment():
    # The shape of the original bug, stated as a property: a ball whose
    # radius is nan cannot be inside any ball, so no enclosure question
    # about it may answer yes.
    wide = arb("1e10") + arb("nan")
    assert contains_zero(wide) is False
    assert certify("wide", wide).finite is False


