"""Tests for python/moore_premises.py.

The verifier depends on ``msaf.zeta_inversion`` (T-hat-N package). When that
package is not importable (standalone framework checkout), the tests are
skipped rather than failed, so the suite stays green in both layouts.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

# Allow running from repo root or python/ directory.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# When the framework is checked out inside the T-hat-N tree (sibling of
# msaf/), add that root so the optional dependency resolves. On standalone
# CI checkouts this does nothing and the tests skip.
_PARENT = _HERE.parent.parent
if (_PARENT / "msaf").is_dir() and str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))

_msaF_available = importlib.util.find_spec("msaf") is not None

requires_msaf = pytest.mark.skipif(
    not _msaF_available,
    reason="msaf.zeta_inversion not importable (T-hat-N dependency)",
)


def test_moore_premises_module_imports():
    """moore_premises should be importable when its deps are present."""
    if not _msaF_available:
        pytest.skip("msaf.zeta_inversion not importable")
    import moore_premises  # noqa: F401
    assert hasattr(moore_premises, "verify_moore_premises")
    assert hasattr(moore_premises, "second_derivative_over_ball")


@requires_msaf
def test_reject_float_leakage():
    import moore_premises

    with pytest.raises(TypeError, match="leakage"):
        moore_premises.verify_moore_premises(0.5)


@requires_msaf
def test_second_derivative_returns_tuple():
    from flint import acb

    import moore_premises

    ball = acb("0.5", "0")
    result = moore_premises.second_derivative_over_ball(ball, degree=16)
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_reject_float_degree():
    """degree must not be a Python float."""
    if not _msaF_available:
        pytest.skip("msaf.zeta_inversion not importable")
    import moore_premises
    from flint import acb

    with pytest.raises(TypeError, match="degree"):
        moore_premises.second_derivative_over_ball(acb("0.5", "0"), degree=16.0)

