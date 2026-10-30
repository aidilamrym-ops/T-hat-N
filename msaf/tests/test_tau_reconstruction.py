"""Test suite for tau reconstruction."""

from __future__ import annotations

import pytest
from pathlib import Path
from flint import arb_mat

from msaf.tau_reconstruction import build, serialize, constants

def test_constants():
    assert constants.CONDUCTOR == 100
    assert constants.DIM_201 == 201
    assert constants.DIM_301 == 301

def test_build_dim_201():
    mat = build.build_arb_tau(c=100, N=100, prec_bits=256)
    assert isinstance(mat, arb_mat)
    assert mat.nrows() == 201
    assert mat.ncols() == 201

def test_serialize_and_hash():
    mat = build.build_arb_tau(c=100, N=100, prec_bits=256)
    ROOT = Path(__file__).resolve().parents[2]
    out_path = ROOT / "reports" / "test_gw_matrix.json"
    serialize.save_matrix_json(
        mat, out_path, conductor=100, block=100, prec_bits=256,
        build_chain="test chain", gate_verdict="G-M0 PASS"
    )
    assert out_path.is_file()
    sha = serialize.compute_sha256lf(out_path)
    assert len(sha) == 64
    out_path.unlink()
