"""CRT combiner + oracle gate regression (exact integer arithmetic)."""
import pytest

from msaf.hodge.crt_combine import crt, oracle_check, recover_integer

# locked exact integers used as rehearsal targets
A8_SMOOTH_QUARTIC = 0  # #X(F_{3^8}) - 1 - 3^16, locked by two counters
A5_FERMAT_F5 = -12026  # locked by Davenport-Hasse + ball sweep
B8 = 22 * 3**8  # 144342
B5_F5 = 22 * 5**5  # 68750


def _residues(value: int, moduli: list[int]) -> list[int]:
    return [value % m for m in moduli]


def test_garner_matches_direct_congruences():
    moduli = [5, 7, 11, 13]
    residues = [3, 2, 9, 5]
    x = crt(residues, moduli)
    for r, m in zip(residues, moduli):
        assert x % m == r


def test_rehearsal_recovers_zero_trace():
    # a_8 = 0 of the smooth quartic: the combiner must return exactly
    # 0 (symmetric representative), not 0 mod M as a guess.
    moduli = [5, 7, 11, 13, 17, 19]
    out = recover_integer(
        _residues(A8_SMOOTH_QUARTIC, moduli), moduli, B8
    )
    assert out["verdict"] == "RECOVERED"
    assert out["value"] == 0


def test_rehearsal_recovers_negative_trace():
    # a_5 = -12026 (Fermat F_5): exercises the symmetric branch.
    moduli = [7, 11, 13, 17, 19, 23]
    out = recover_integer(
        _residues(A5_FERMAT_F5, moduli), moduli, B5_F5
    )
    assert out["verdict"] == "RECOVERED"
    assert out["value"] == A5_FERMAT_F5


def test_insufficient_moduli_refuse():
    # M = 5 <= 2B: suggestive residues, no number. Ever.
    out = recover_integer([0], [5], B8)
    assert out["verdict"] == "INCONCLUSIVE"
    assert out["value"] is None


def test_oracle_holds_on_correct_engine():
    assert oracle_check({8: 0, 5: -12026}, {8: 0, 5: -12026}) == {
        "verdict": "ORACLE-HOLD",
        "mismatches": [],
    }


def test_oracle_fails_corrupted_engine():
    out = oracle_check({8: 1, 5: -12026}, {8: 0, 5: -12026})
    assert out["verdict"] == "ORACLE-FAIL"
    assert out["mismatches"] == [(8, 1, 0)]
    out2 = oracle_check({5: -12026}, {8: 0, 5: -12026})
    assert out2["verdict"] == "ORACLE-FAIL"


def test_input_gates():
    with pytest.raises(ValueError):
        crt([1, 2], [6, 10])  # not coprime
    with pytest.raises(ValueError):
        crt([7], [5])  # residue out of range
    with pytest.raises(ValueError):
        crt([], [])
    with pytest.raises(ValueError):
        recover_integer([0], [5], -1)
    with pytest.raises(TypeError):
        crt([1.0], [5])  # type: ignore[list-item]
    with pytest.raises(TypeError):
        recover_integer([0], [5], 2.0)  # type: ignore[arg-type]
