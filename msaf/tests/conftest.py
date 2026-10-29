# -*- coding: utf-8 -*-
"""Suite-wide test fixtures (added by the 2026-10-27 D6 housekeeping package).

``flint.ctx.prec`` is process-global state.  A test that writes it and
never restores it leaks that precision into every later test in the same
session; ``reports/NONFINITE_DEFECT.md`` section 3 documents the class.

The autouse fixture below saves the precision at test start and restores
the exact same value afterwards, so a stray write inside any test can no
longer change what later tests observe.  It does not set or lower
precision itself, so a test that needs its own precision still declares
it (the six known function-level writes in test_convergence_order,
test_moore_premises, test_sbp_correspondence, test_tail_decay and
test_periodic_bridge keep working exactly as before while their leakage
is neutralised at the suite boundary).
"""

from __future__ import annotations

import pytest
import flint


@pytest.fixture(autouse=True)
def arb_ctx_prec_guard():
    saved = int(flint.ctx.prec)
    yield
    flint.ctx.prec = saved


