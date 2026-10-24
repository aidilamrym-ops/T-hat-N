# -*- coding: utf-8 -*-
"""t2n_science -- interval/precision calculator role entry (F0 skeleton)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.skeleton import serve_generic

DESCRIPTION = ("T-hat-N science kernel: mpmath.iv interval arithmetic with "
               "AST-whitelist evaluation, exact Fraction comparisons, "
               "float-free AST scanning, precision discipline.")

if __name__ == "__main__":
    serve_generic("t2n_science", DESCRIPTION)
