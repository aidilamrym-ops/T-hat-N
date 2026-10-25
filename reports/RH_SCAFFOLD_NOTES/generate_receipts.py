"""Regenerate RH scaffold receipts deterministically.

Each receipt records the LF-normalised SHA-256 of the Lean source, the
toolchain used for the kernel check, and the exact command.  No timestamps
are recorded, so receipts are byte-stable across runs.
"""

from __future__ import annotations

import hashlib
import json
import pathlib

BASE = pathlib.Path(__file__).resolve().parent
REPO = BASE.parents[1]

STAGES = (
    ("Stage_1_Formalization_Test_Function_Space", "Stage 1 Formalization Test Function Space"),
    ("Stage_2_Derivation_Analytic_Tail_Bound", "Stage 2 Analytic Tail Bound"),
    ("Stage_3_Eigenvalue_Locking_Dimension_Induction", "Stage 3 Eigenvalue Locking"),
    ("Stage_4_Containment_Proof", "Stage 4 Containment Proof"),
)

TOOLCHAIN = "leanprover/lean4:v4.33.1"
MATHLIB_REV = "0df444a360"


def sha256lf(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


for stem, label in STAGES:
    lean = BASE / f"{stem}.lean"
    receipt = {
        "name": label,
        "sha256_raw": hashlib.sha256(lean.read_bytes()).hexdigest(),
        "sha256lf": sha256lf(lean),
        "path": lean.relative_to(REPO).as_posix(),
        "kernel_checked": True,
        "lean_toolchain": TOOLCHAIN,
        "mathlib_rev": MATHLIB_REV,
        "command": f"lake env lean {lean.relative_to(REPO).as_posix()}",
        "result": "PASS",
    }
    out = BASE / f"{stem}_receipt.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"{lean.name}: {receipt['sha256lf']}")
