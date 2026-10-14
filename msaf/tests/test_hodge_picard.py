"""Picard-bound machinery regression (exact integer arithmetic)."""
from fractions import Fraction

import pytest

from msaf.hodge.odd_fields import jacobi_trace
from msaf.hodge.picard_bound import (
    char_poly_from_traces,
    euler_phi,
    picard_bound,
    poly_gcd_deg,
)


def test_newton_fe_roundtrip_curve():
    # P(T) = (1-9T^2)(1-T^2) = 1 - 10T^2 + 9T^4: eigenvalues
    # {+-3, +-1}; pairs alpha <-> q/alpha hold (3<->1, -3<->-1),
    # so this is a dim_x=1 (curve) polynomial. Newton needs
    # t_1..t_2 = p_1..p_2 = 0, 20.
    traces = {1: 0, 2: 20}
    got = char_poly_from_traces(traces, 4, 3, 1, dim_x=1)
    assert got == [
        Fraction(1),
        Fraction(0),
        Fraction(-10),
        Fraction(0),
        Fraction(9),
    ]
    out = picard_bound(traces, 4, 3, dim_x=1)
    # roots +-1/3 are zeta/3; roots +-1 are not (zeta = +-3).
    assert out["bound"] == 2


def test_multiplicity_lock():
    # P = (1-3T)^4 (1-T)^4 (pairs 1/3 <-> 1 under q/alpha, so
    # dim_x=1): root 1/3 carries multiplicity 4. A single squarefree
    # gcd counts it once -- the bound must be 4, locking
    # multiplicity-weighted counting.
    traces = {k: 4 * 3**k + 4 for k in range(1, 5)}
    out = picard_bound(traces, 8, 3, dim_x=1)
    assert out["bound"] == 4


def test_gcd_degrees():
    x2m1 = [Fraction(-1), Fraction(0), Fraction(1)]
    x3mx = [Fraction(0), Fraction(-1), Fraction(0), Fraction(1)]
    assert poly_gcd_deg(x2m1, x3mx) == 2
    assert poly_gcd_deg([Fraction(1), Fraction(1)], [Fraction(2)]) == 0
    assert euler_phi(1) == 1 and euler_phi(6) == 2 and euler_phi(22) == 10


def test_picard_bound_curve_zero():
    # E/F_3, y^2 = x^3+x+1: #E(F_3)=4, #E(F_9)=16 by two independent
    # enumerations, hence the Frobenius traces a_n = q^n+1-#E(F_q^n)
    # are a_1 = 0, a_2 = -6 and the char poly is 1 + 3T^2 (this locks
    # the dim_x=1 FE: a_2 = q*a_0). Supplied t_2 also exercises the
    # real sign check: only sign +1 reproduces it via Newton.
    out = picard_bound({1: 0, 2: -6}, 2, 3, dim_x=1)
    assert out["bound"] == 0
    assert out["sign"] == 1


def test_sign_admission_real():
    # Same traces, wrong sign alone must be refused (power-sum check).
    assert char_poly_from_traces({1: 0, 2: -6}, 2, 3, -1, dim_x=1) is None
    assert char_poly_from_traces({1: 0, 2: -6}, 2, 3, 1, dim_x=1) is not None


def test_fermat_k3_pipeline():
    # F_3 Fermat quartic SURFACE (K3, dim_x=2): traces a_n =
    # #X(F_3^n) - 1 - 9^n from certified counts. Expected structure:
    # eigenvalues {3 x 12, -3 x 10} (self-paired under alpha <->
    # q^2/alpha), char poly (1-3T)^12 (1+3T)^10, bound 22 = b_2
    # (vacuous for Picard, but the whole pipeline is pinned
    # end-to-end on real counts).
    q = 3
    traces = {}
    for k in range(1, 11):
        # live Jacobi: every count is a ball-certified integer.
        traces[k] = jacobi_trace(k, 3)["projective"] - 1 - q ** (2 * k)
    # k = 11 via the locked e=2 closed form N = (q+1)^2 (verified
    # live at n = 5, 7, 9 and cross-checked at n = 11 =
    # 31381413904; a live n=11 run costs ~20 s).
    traces[11] = (q**11 + 1) ** 2 - 1 - q**22
    assert traces[1] == 6 and traces[2] == 198 and traces[10] == 1299078
    # surface FE: a_22 = q^22 * a_0 (dim_x=2 exponent 2k-22).
    got = char_poly_from_traces(traces, 22, 3, 1, dim_x=2)
    assert got is not None
    assert got[-1] == Fraction(3**22)
    out = picard_bound(traces, 22, 3)
    assert out["bound"] == 22
    assert out["sign"] == 1
    assert out["exact_orders"] == {1: 12, 2: 10}


def test_picard_input_gates():
    with pytest.raises(ValueError):
        char_poly_from_traces({1: 0}, 2, 3, 0)
    with pytest.raises(ValueError):
        picard_bound({1: 0}, 3, 3)
    with pytest.raises(ValueError):
        # t_2 = 1 makes e_2 non-integral: not a true trace set.
        char_poly_from_traces({1: 0, 2: 1}, 4, 3, 1, dim_x=1)
    with pytest.raises(ValueError):
        char_poly_from_traces({1: 0}, 2, 3, 1, dim_x=0)
