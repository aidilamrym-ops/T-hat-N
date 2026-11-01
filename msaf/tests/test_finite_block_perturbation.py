from __future__ import annotations

import pytest
from msaf.finite_block_perturbation import verify_block_bound

def test_block_bound():
    assert verify_block_bound(64)
