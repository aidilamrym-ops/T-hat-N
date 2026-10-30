"""Serialization of Arb matrices to JSON with {mid, rad} format."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Any

from flint import arb, arb_mat

__all__ = [
    "arb_to_dict",
    "arb_mat_to_json",
    "save_matrix_json",
    "compute_sha256lf",
]


def arb_to_dict(val: arb) -> dict[str, str]:
    """Serialize an arb ball as {mid, rad} strings."""
    return {
        "mid": val.mid().str(50, radius=False),
        "rad": val.rad().str(30, radius=False),
    }


def arb_mat_to_json(mat: arb_mat) -> dict[str, Any]:
    """Convert arb_mat to JSON-serializable dict."""
    n = mat.nrows()
    m = mat.ncols()

    matrix_data = []
    for i in range(n):
        row = []
        for j in range(m):
            row.append(arb_to_dict(mat[i, j]))
        matrix_data.append(row)

    return {
        "matrix": matrix_data,
        "dim": n,
    }


def compute_sha256lf(path: Path) -> str:
    """Compute SHA-256 with LF normalization."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def save_matrix_json(
    mat: arb_mat,
    path: Path,
    conductor: int,
    block: int,
    prec_bits: int,
    build_chain: str,
    gate_verdict: str,
) -> None:
    """Save matrix with full metadata to JSON file."""
    n = mat.nrows()
    dps = int(prec_bits * 0.3010299956639812)  # log10(2)

    data = {
        "schema": "msaf.gw_matrix.v1",
        "dim": n,
        "conductor": conductor,
        "block": block,
        "prec_bits": prec_bits,
        "dps": dps,
        "matrix": arb_mat_to_json(mat)["matrix"],
        "build_chain": build_chain,
        "gate_verdict": gate_verdict,
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )