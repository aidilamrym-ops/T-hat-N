"""Anatomy test for tau matrices: Toeplitz and Hankel residual analysis using Flint arb."""

from __future__ import annotations

import json
from pathlib import Path
from flint import arb, arb_mat

def load_matrix(path: Path) -> arb_mat:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data["matrix"]
    n = len(rows)
    mat = arb_mat(n, n)
    for i in range(n):
        for j in range(n):
            val = rows[i][j]
            if isinstance(val, dict):
                mat[i, j] = arb(val["mid"], val["rad"])
            else:
                mat[i, j] = arb(str(val))
    return mat

def compute_residuals(mat: arb_mat) -> dict:
    n = mat.nrows()
    toep_res = arb(0)
    for i in range(n - 1):
        for j in range(n - 1):
            diff = mat[i, j] - mat[i+1, j+1]
            if diff < 0:
                diff = -diff
            if diff > toep_res:
                toep_res = diff

    hank_res = arb(0)
    for i in range(n - 1):
        for j in range(1, n):
            diff = mat[i, j] - mat[i+1, j-1]
            if diff < 0:
                diff = -diff
            if diff > hank_res:
                hank_res = diff

    return {
        "toeplitz_max_abs_diff": str(toep_res),
        "hankel_max_abs_diff": str(hank_res),
        "is_toeplitz_approximate": bool(toep_res < arb("1e-10")),
        "is_hankel_approximate": bool(hank_res < arb("1e-10")),
    }

def main():
    root = Path(__file__).resolve().parents[2]
    reports_dir = root / "reports"

    res_100 = reports_dir / "gw_matrix_100_100.json"
    res_150 = reports_dir / "gw_matrix_100_150.json"

    results = {}
    if res_100.is_file():
        m100 = load_matrix(res_100)
        results["gw_matrix_100_100"] = compute_residuals(m100)

    if res_150.is_file():
        m150 = load_matrix(res_150)
        results["gw_matrix_150"] = compute_residuals(m150)

    out_path = reports_dir / "TAU_ANATOMY_RESULTS_2026-10-30.md"
    content = (
        "# TAU MATRIX ANATOMY RESULTS (Toeplitz & Hankel Residuals)\n\n"
        "Date: 2026-10-30\n"
        "Scope: {rh_claim: false, zero_location_claim: false, weil_positivity_claim: false}\n\n"
        "## Summary of Residuals\n"
        "```json\n"
        f"{json.dumps(results, indent=2)}\n"
        "```\n"
    )
    out_path.write_text(content, encoding="utf-8")
    print(f"Wrote anatomy results to {out_path}")

if __name__ == "__main__":
    main()
