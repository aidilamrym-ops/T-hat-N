"""Build the Guinand-Weil tau matrix using source_arb_ldlt_certify directly."""

from __future__ import annotations

import sys
import os
from pathlib import Path
from flint import arb_mat

GW = Path(os.environ.get("GW_DIR", r"C:/Users/usER/oracle-toe/GUINAND_WEIL"))
if str(GW) not in sys.path:
    sys.path.insert(0, str(GW))

import source_arb_ldlt_certify as gw

__all__ = [
    "build_arb_tau",
]

def build_arb_tau(c: int = 100, N: int = 100, prec_bits: int = 256) -> arb_mat:
    # source_arb_ldlt_certify.build_arb_tau returns (matrix, dim)
    mat, dim = gw.build_arb_tau(c, N, prec_bits)
    return mat
