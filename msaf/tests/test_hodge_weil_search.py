"""Weil circle test + a_11 lock regression (exact integer arithmetic)."""
import json
from fractions import Fraction
from math import comb
from pathlib import Path

import pytest

from msaf.hodge.picard_bound import char_poly_from_traces, euler_phi, picard_bound
from msaf.hodge.weil_search import (
    _moebius,
    _ramanujan,
    circle_test,
    ramanujan_power_sums,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "reports"
    / "hodge_quartic_f3_traces.json"
)
SEARCH_ARTIFACT = (
    Path(__file__).resolve().parents[2] / "reports" / "weil_search_a11.json"
)
REHEARSE_ARTIFACT = (
    Path(__file__).resolve().parents[2] / "reports" / "weil_rehearse_fermat.json"
)


def _conv(a, b):
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, ca in enumerate(a):
        for j, cb in enumerate(b):
            out[i + j] += ca * cb
    return out


def _binom(n, a):
    return [Fraction(comb(n, k) * a**k) for k in range(n + 1)]


def _smooth_traces():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    return {k: int(data["counts"][str(k)]) - 1 - 3 ** (2 * k) for k in range(1, 11)}


def test_circle_accepts_genuine_weil_polys():
    # (1-3T)^12 (1+3T)^10: the Fermat F_3 truth (eigenvalues +-3).
    assert circle_test(_conv(_binom(12, -3), _binom(10, 3)), 3) is True
    # (1-3T)^22 and (1+3T)^22: all eigenvalues 3 / -3.
    assert circle_test(_binom(22, -3), 3) is True
    assert circle_test(_binom(22, 3), 3) is True


def test_circle_rejects_non_weil_polys():
    # Reciprocal pair 1 <-> 9 (truth-scale coefficients): off-circle.
    bad = _conv(
        _conv([Fraction(1), Fraction(-1)], [Fraction(1), Fraction(-9)]),
        _conv(_binom(10, -3), _binom(10, -3)),
    )
    assert circle_test(bad, 3) is False
    # Breaks the FE: reciprocity gate must refuse, not Sturm.
    broken = list(_binom(22, -3))
    broken[11] += 1
    assert circle_test(broken, 3) is False


def test_circle_end_to_end_on_fermat_f5():
    # Real data path: exact traces -> Newton+FE -> circle (q = 5).
    from msaf.hodge.fermat_k3 import fermat_k3_traces

    traces = fermat_k3_traces(5, 11)
    poly = char_poly_from_traces(traces, 22, 5, 1, dim_x=2)
    assert poly is not None
    assert circle_test(poly, 5) is True


def test_search_artifact_integrity():
    data = json.loads(SEARCH_ARTIFACT.read_text(encoding="utf-8"))
    assert data["scanned"] == 708588
    assert data["B"] == 22 * 3**11
    assert data["Umod11"] == 6
    assert data["distinct"] == [354294]
    assert sorted(tuple(p) for p in data["passers"]) == [(354294, -1), (354294, 1)]


def test_rehearsal_artifact_integrity():
    # Same machinery, independently known truth (Fermat e_11 != 0 path).
    data = json.loads(REHEARSE_ARTIFACT.read_text(encoding="utf-8"))
    assert data["truth"] == 354294
    assert data["distinct"] == [354294]
    assert data["passers"] == [[354294, 1]]


def test_a11_locked_poly_and_bound():
    traces = _smooth_traces()
    traces[11] = 354294
    out = picard_bound(traces, 22, 3, dim_x=2)
    assert out["bound"] == 22
    assert out["sign"] == 1
    assert out["char_poly"][-1] == str(3**22)
    orders = out["exact_orders"]
    assert orders == {1: 2, 2: 2, 6: 2, 7: 6, 10: 4, 14: 6}
    # Galois-orbit completeness: every order count is a union of full
    # primitive-root orbits (a fake completion essentially never shows
    # exact phi-multiples at every order simultaneously).
    assert sum(orders.values()) == 22
    for m, cnt in orders.items():
        assert cnt % euler_phi(m) == 0


def test_ramanujan_units():
    assert _moebius(1) == 1 and _moebius(7) == -1 and _moebius(10) == 1
    assert _moebius(4) == 0 and _moebius(12) == 0
    assert _ramanujan(7, 1) == -1
    assert _ramanujan(6, 1) == 1
    assert _ramanujan(10, 2) == -1
    assert _ramanujan(7, 7) == 6


def test_orbit_structure_reproduces_measured_traces():
    # Independent path (number theory, not linear algebra): the orbit
    # data {m: count} predicts a_1 = 6, a_2 = 0, a_3 = -27 by hand-
    # checkable Ramanujan sums; the locked counts say the same.
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    locked = {k: int(data["counts"][str(k)]) - 1 - 3 ** (2 * k) for k in (1, 2, 3)}
    assert (locked[1], locked[2], locked[3]) == (6, 0, -27)
    got = ramanujan_power_sums({1: 2, 2: 2, 6: 2, 7: 6, 10: 4, 14: 6}, 3, [1, 2, 3])
    assert (got[1], got[2], got[3]) == (6, 0, -27)


def test_a11_input_gates():
    with pytest.raises(TypeError):
        circle_test([Fraction(1)], 3.0)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        ramanujan_power_sums({1: 2}, 3.0, [1])  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        ramanujan_power_sums({6: 3}, 3, [1])  # 3 is not a union of order-6 orbits
