# -*- coding: utf-8 -*-
"""Guard for the committed engine-B full-run artefact (H1 stage C).

The full 20000-sample independent S2 verification (2026-10-17, exit 0,
9062 s) is sealed in reports/gw_engine_b_verify.json + .log. This test
machine-checks the committed artefact against the frozen expectations:

  * verdict block -- PASS-WITH-ENUMERATED-EXCEPTIONS, 0 failing cells,
    9 clean + 9 enumerated-edge-cluster cells (the pre-declared verdict);
  * module/instrument sha256 recorded in the artefact match the sealed
    values (module 485ab652..., instrument 072910f2... before AND after);
  * declared manifest -- mode full, seed 20260927, dps 50, 20000 samples
    per dimension (201/301/401);
  * counts -- all 18 cells reproduce engine A exactly: k_GUE and k_Pois
    equal in the artefact, in the artefact's own A capture, and in the
    A-side reference reports/gw_h1_floor_refine.json; all exact_* flags
    true; the informational chi2 print check stays within 1e-3;
  * the log carries the frozen verdict lines verbatim.

No raw file hashes here: line-ending normalisation differs across
checkouts (see the stable_bytes note in msaf/gw_dashboard_v4.py).
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
VERIFY = os.path.join(ROOT, "reports", "gw_engine_b_verify.json")
REFINE = os.path.join(ROOT, "reports", "gw_h1_floor_refine.json")
LOG = os.path.join(ROOT, "reports", "gw_engine_b_verify.log")

SCRIPT_SHA = "485ab6525531aa8ef9b5e499736331b600fdb205bb2a9b93cfa438ffa261fcea"
INSTRUMENT_SHA = ("072910f232b15768ba35e14d7cc6aaf4fe1ee174dc45b65429460f791"
                  "196e1d5")


def _load():
    with open(VERIFY, encoding="utf-8") as fh:
        return json.load(fh)


def test_verdict_block():
    v = _load()["verdict"]
    assert v["b1"] == "PASS"
    assert v["b3"] == "PASS"
    assert v["b2_observed_grid"] == "PASS-WITH-ENUMERATED-EXCEPTIONS"
    assert v["counts"] == "PASS"
    assert v["overall"] == "PASS-WITH-ENUMERATED-EXCEPTIONS"
    assert v["cells_pass"] == 9
    assert v["cells_pass_enumerated_edge_cluster"] == 9
    assert v["cells_fail"] == 0


def test_manifest_sealed_hashes_and_declared_scope():
    a = _load()
    assert a["mode"] == "full"
    assert a["manifest"]["instrument"]["sha256_before"] == INSTRUMENT_SHA
    assert a["manifest"]["instrument"]["sha256_after"] == INSTRUMENT_SHA
    assert a["script"]["sha256"] == SCRIPT_SHA
    dec = a["manifest"]["declared_before_run"]
    assert dec["seed"] == 20260927
    assert dec["mpmath_dps"] == 50
    assert dec["samples"] == {"201": 20000, "301": 20000, "401": 20000}


def test_counts_exact_against_engine_a_reference():
    a = _load()
    with open(REFINE, encoding="utf-8") as fh:
        grid = json.load(fh)["grid"]
    ref = {(int(g["dim"]), str(g["chart"]), round(float(g["sigma_u"]), 1)): g
           for g in grid}
    cells = a["counts"]["cells"]
    assert len(cells) == 18
    assert a["counts"]["summary"] == {"cells": 18, "exact_k_gue": 18,
                                      "exact_k_pois": 18, "exact_all_four": 18}
    for c in cells:
        key = (int(c["dim"]), str(c["chart"]), round(float(c["sigma_u"]), 1))
        g = ref[key]
        assert c["k_gue"] == g["k_gue"] == c["A_k_gue"], key
        assert c["k_pois"] == g["k_pois"] == c["A_k_pois"], key
        assert c["exact_k_gue"] and c["exact_k_pois"]
        assert c["exact_k_gue_lower"] and c["exact_k_pois_upper"]
        assert c["chi2_absdiff_vs_printed"] <= 1e-3, key


def test_log_carries_frozen_verdict_lines():
    with open(LOG, encoding="utf-8") as fh:
        text = fh.read()
    assert "ENGINE B VERDICT (full)" in text
    assert ("counts vs engine A: k_GUE 18/18 exact, k_Pois 18/18 exact, "
            "all four tails 18/18") in text
    assert "PASS-WITH-ENUMERATED-EXCEPTIONS" in text
    assert ("observed grid: 720 bins compared; frozen OR 666/720; "
            "tighter 10-ulp branch 8/720") in text
    assert "script sha256 = " + SCRIPT_SHA in text
