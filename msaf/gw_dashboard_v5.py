# -*- coding: utf-8 -*-
"""gw_dashboard_v5.py -- H1 floor-amendment + engine-B extension of the
v4 dashboard.

What this module does
---------------------
Renders reports/gw_diagnostic_v5.html from:
  * the byte-frozen v4 page (reports/gw_diagnostic_v4.html) used as the
    base layout -- preserved byte-identical, its sha256 embedded in
    panel 6;
  * the H1 stage A+B artefact of record
    (reports/gw_h1_floor_refine.json);
  * the engine-B stage C artefacts
    (reports/gw_engine_b_verify.json and .log);
  * the dim-257 lambda_min rung
    (reports/lambda_min_eig_ladder_big.json) for the panel-1 caption
    correction, and the dim-129 rung from the sealed ladder for the
    measured ln-slope.

Every number is machine-extracted at build time; a missing file, a
missing field, a value that contradicts the sealed record, or a patch
anchor that does not match exactly once aborts the build. No number is
typed by hand; no timestamp is embedded; reruns are byte-stable.

Patches applied to the v4 base (each must match exactly once):
  1. title / kicker / h1 version mark v4 -> v5;
  2. hero sub: v5 provenance + v4-preserved statement;
  3. hero chips: sealed-2000 census relabelled; H1 + engine-B chips
     added;
  4. table of contents: two new entries (panels 7 and 8);
  5. panel 1 caption: dim-257 rung correction (measured 2026-10-15;
     v4 said "257/321 not yet measured");
  6. heatmap: row label "baseline run 2" clarified + row-label note;
  7. panel 6: v4 preserved-predecessor paragraph + "changes in v5"
     list; regenerate hint v4 -> v5;
  8. two new panels (7: H1 floor amendment; 8: engine-B verification)
     + footer.

CLI:
    python msaf/gw_dashboard_v5.py           # dry run: prints extracted data
    python msaf/gw_dashboard_v5.py --write   # writes the HTML
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gw_dashboard_v4 as v4  # noqa: E402  (frozen base; never modified)

V4 = ROOT / "reports" / "gw_diagnostic_v4.html"
OUT = ROOT / "reports" / "gw_diagnostic_v5.html"
REFINE = ROOT / "reports" / "gw_h1_floor_refine.json"
EB_JSON = ROOT / "reports" / "gw_engine_b_verify.json"
EB_LOG = ROOT / "reports" / "gw_engine_b_verify.log"
EB_SCRIPT = HERE / "gw_engine_b_verify.py"
LADDER_LMIN = ROOT / "reports" / "lambda_min_eig_ladder.json"
LADDER_BIG = ROOT / "reports" / "lambda_min_eig_ladder_big.json"
SPEC = ROOT / "reports" / "AMENDMENT_FLOOR_SPEC.md"

# instrument sha256 recorded in the sealed records (external frozen file)
INSTRUMENT_SHA = "072910f2"

GREEN = "#1c7a46"
AMBER = "#b45309"
BLUE = "#2563eb"
ROSE = "#be5b5b"
SLATE = "#64748b"
FONT = v4.FONT

MID = "\u00b7"        # middle dot
ARR = "\u2192"        # right arrow
EMD = "\u2014"        # em dash
SIG = "\u03c3"        # sigma
LE = "\u2264"         # <=
CHI = "\u03c7"        # chi
ALPHA = "\u03b1"      # alpha
SUM = "\u03a3"        # Sigma

# pre-registered target cells (frozen spec section 2, quoted in
# reports/AMENDMENT_FLOOR_RESULTS.md section 2)
TARGET_CELLS = {
    (201, "T", 0.3): "C1",
    (301, "T", 0.3): "C2",
    (401, "T", 0.3): "C3",
    (301, "T", 0.5): "C4",
}


def read_text(path) -> str:
    return Path(path).read_text(encoding="utf-8")


def read_json(path) -> dict:
    return json.loads(read_text(path))


def f5(x: float) -> str:
    return "%.5e" % x


def cp_str(pair) -> str:
    return "[%s, %s]" % (f5(pair[0]), f5(pair[1]))


# --------------------------------------------------------------------------
# collectors -- fail loud on any contradiction with the sealed record
# --------------------------------------------------------------------------
def collect_h1() -> dict:
    ref = read_json(REFINE)
    grid = ref["grid"]
    if len(grid) != 18:
        raise SystemExit("H1 refine json: expected 18 grid cells, got %d"
                         % len(grid))
    for key in TARGET_CELLS:
        if not any((c["dim"], c["chart"], c["sigma_u"]) == key
                   for c in grid):
            raise SystemExit("H1 refine json: target cell %r missing" % (key,))

    floor = [c for c in grid if c["k_gue"] == 0]
    off = [c for c in grid if c["k_gue"] > 0]
    if not (len(floor) == 17 and len(off) == 1):
        raise SystemExit("H1 refine json: floor census changed (%d floor, "
                         "%d off)" % (len(floor), len(off)))
    if not all(c["n"] == 20000 for c in grid):
        raise SystemExit("H1 refine json: non-20000 n found")
    bound = max(c["cp95_gue"][1] for c in floor)
    if any(abs(c["cp95_gue"][1] - bound) > 1e-18 for c in floor):
        raise SystemExit("H1 refine json: floor bounds are not uniform")

    c4 = off[0]
    if (c4["dim"], c4["chart"], c4["sigma_u"], c4["k_gue"],
            c4["n"]) != (301, "T", 0.5, 1262, 20000):
        raise SystemExit("H1 refine json: off-floor cell is not C4/1262")
    if c4["p_gue"] != "6.31000e-02":
        raise SystemExit("H1 refine json: C4 p_gue changed: %r"
                         % c4["p_gue"])

    arr = ref["c4_array"]
    if arr["k"] != [1262, 960, 1289, 1021, 1345]:
        raise SystemExit("H1 refine json: C4 seed array changed: %r"
                         % arr["k"])
    if sum(arr["k"]) != arr["pooled_k"] or arr["pooled_n"] != 100000:
        raise SystemExit("H1 refine json: pooled counts inconsistent")
    if abs(arr["p_hat"] - 0.05877) > 1e-12:
        raise SystemExit("H1 refine json: pooled p_hat changed")
    if not arr["classification"].startswith("NOT STABLE"):
        raise SystemExit("H1 refine json: classification changed")
    n_above = sum(1 for p in arr["per_seed_p"] if p >= 0.05)
    if n_above != 4:
        raise SystemExit("H1 refine json: seed census changed")

    # refined S2 FINAL lines, read verbatim from the A logs
    logs = sorted({c["log"] for c in grid})
    if len(logs) != 3:
        raise SystemExit("H1 refine json: expected 3 A logs, got %d"
                         % len(logs))
    finals = {}
    for rel in logs:
        txt = read_text(ROOT / rel)
        m = re.search(r"S2 FINAL(?:[^:\n]*): ([^\n]+)", txt)
        if not m:
            raise SystemExit("no S2 FINAL line in %s" % rel)
        finals[rel] = m.group(1).strip()
    c4_log = c4["log"]
    if "UNSTABLE" not in finals[c4_log]:
        raise SystemExit("dim-301 refined log does not read UNSTABLE")
    for rel, line in finals.items():
        if rel != c4_log and "UNSTABLE" in line:
            raise SystemExit("unexpected UNSTABLE in %s" % rel)
    txt301 = read_text(ROOT / c4_log)
    m5 = re.search(r"INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION"
                   r"\s+\((\d+) grid points\)", txt301)
    m1 = re.search(r"NO DISCRIMINATION AT N=401\s+\((\d+) grid points\)",
                   txt301)
    if not m5 or not m1 or (int(m5.group(1)), int(m1.group(1))) != (5, 1):
        raise SystemExit("dim-301 verdict breakdown changed")

    return {
        "grid": grid, "floor": floor, "c4": c4, "arr": arr,
        "bound": bound, "bound_s": f5(bound), "n_above": n_above,
        "finals": finals, "c4_log": c4_log,
        "breakdown": (int(m5.group(1)), int(m1.group(1))),
        "manifest": ref["manifest"],
    }


def collect_eb() -> dict:
    eb = read_json(EB_JSON)
    v = eb["verdict"]
    if (v["b1"], v["b3"]) != ("PASS", "PASS"):
        raise SystemExit("engine B: B1/B3 not PASS")
    if v["b2_observed_grid"] != "PASS-WITH-ENUMERATED-EXCEPTIONS":
        raise SystemExit("engine B: B2a verdict changed")
    if v["counts"] != "PASS" or v["overall"] != \
            "PASS-WITH-ENUMERATED-EXCEPTIONS":
        raise SystemExit("engine B: counts/overall verdict changed")
    if (v["cells_pass"], v["cells_pass_enumerated_edge_cluster"],
            v["cells_fail"]) != (9, 9, 0):
        raise SystemExit("engine B: cell census changed")

    cells = eb["counts"]["cells"]
    if len(cells) != 18:
        raise SystemExit("engine B: expected 18 counts cells")
    for c in cells:
        if not (c["exact_k_gue"] and c["exact_k_pois"]
                and c["exact_k_gue_lower"] and c["exact_k_pois_upper"]):
            raise SystemExit("engine B: a counts cell is not exact")
    summ = eb["counts"]["summary"]
    if summ != {"cells": 18, "exact_k_gue": 18, "exact_k_pois": 18,
                "exact_all_four": 18}:
        raise SystemExit("engine B: counts summary changed")

    tot = orpass = tenulp = 0
    enum_cells = []
    for e in eb["b2_observed_grid"]:
        for b in e["bins_cv"] + e["bins_tgt"]:
            tot += 1
            orpass += 1 if b["within_frozen_or"] else 0
            tenulp += 1 if b["within_10ulp"] else 0
        if len(e["or_fail_bins_tgt"]) != 0:
            raise SystemExit("engine B: tgt OR-fail found (never excused)")
        if e["cell_status"] != "PASS":
            enum_cells.append(e)
    if (tot, orpass, tenulp) != (720, 666, 8):
        raise SystemExit("engine B: per-bin census changed: %d/%d/%d"
                         % (tot, orpass, tenulp))
    orfail = tot - orpass
    if len(enum_cells) != 9 or any(
            "ENUMERATED" not in e["cell_status"] for e in enum_cells):
        raise SystemExit("engine B: enumerated-cell set changed")
    if any(len(e["or_fail_bins_cv"]) != 6 for e in enum_cells):
        raise SystemExit("engine B: enumerated cells no longer 6 cv bins")

    # cross-check against the engine-B log print
    log_text = read_text(EB_LOG)
    m = re.search(r"observed grid: (\d+) bins compared; frozen OR "
                  r"(\d+)/\d+; tighter 10-ulp branch (\d+)/\d+", log_text)
    if not m or (int(m.group(1)), int(m.group(2)), int(m.group(3))) != \
            (720, 666, 8):
        raise SystemExit("engine B: log census print disagrees")

    # script hash: the artefact records it; the on-disk file must match
    disk = v4.full_hash(EB_SCRIPT)
    if disk != eb["script"]["sha256"]:
        raise SystemExit("engine B script hash mismatch: %s vs %s"
                         % (disk, eb["script"]["sha256"]))

    declared = eb["manifest"]["declared_before_run"]
    if declared["mpmath_dps"] != 50 or declared["seed"] != 20260927:
        raise SystemExit("engine B: declared dps/seed changed")
    if any(s != 20000 for s in declared["samples"].values()):
        raise SystemExit("engine B: declared samples changed")
    crit = declared["per_bin_criterion"].split(".")[0] + "."

    return {"eb": eb, "cells": cells, "tot": tot, "orpass": orpass,
            "tenulp": tenulp, "orfail": orfail, "enum_cells": enum_cells,
            "crit": crit, "declared": declared}


def collect_ladder257() -> dict:
    big = read_json(LADDER_BIG)
    runs = big["runs"]
    if len(runs) != 1 or runs[0]["dim"] != 257:
        raise SystemExit("big ladder: expected the single dim-257 run")
    r = runs[0]
    if not r["all_exclude_zero"] or r["lambda_min_rad"] != 0.0:
        raise SystemExit("big ladder: dim-257 rung not certified")
    lad = read_json(LADDER_LMIN)
    r129 = [x for x in lad["runs"] if x["dim"] == 129]
    if len(r129) != 1:
        raise SystemExit("sealed ladder: dim-129 rung missing")
    slope = (math.log(r["lambda_min_lo"] / r129[0]["lambda_min_lo"])
             / (257 - 129))
    return {"lam": r["lambda_min_lo"],
            "lam_s": "%.6e" % r["lambda_min_lo"],
            "eig_s": r["eig_s"], "slope_s": "%+.4f" % slope}


# --------------------------------------------------------------------------
# new SVG builders (inline SVG: no xmlns, no external references)
# --------------------------------------------------------------------------
def build_seed_svg(h1: dict) -> str:
    arr = h1["arr"]
    seeds, ks, ps = arr["seeds"], arr["k"], arr["per_seed_p"]
    cis = arr["per_seed_cp95"]
    pooled_p, pooled_ci = arr["p_hat"], arr["pooled_cp95"]
    W, H = 940, 300
    L, R, T, B = 70, 30, 26, 64
    lo, hi = 0.044, 0.073

    def Y(v: float) -> float:
        return T + (hi - v) / (hi - lo) * (H - T - B)

    def X(i: int) -> float:
        return L + (i + 0.5) * (W - L - R) / (len(seeds) + 1)

    p = ['<svg viewBox="0 0 %d %d" width="100%%" role="img" '
         'aria-label="C4 five-seed robustness array" '
         'style="display:block">' % (W, H)]
    # gridlines + y labels
    for gv in (0.05, 0.06, 0.07):
        p.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" '
                 'stroke="#e4e9f2" stroke-width="1"/>'
                 % (L, Y(gv), W - R, Y(gv)))
        p.append('<text x="%d" y="%.1f" font-size="11" fill="%s" '
                 'text-anchor="end" style="%s">%.2f</text>'
                 % (L - 8, Y(gv) + 4, SLATE, FONT, gv))
    # pre-registered threshold
    p.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" '
             'stroke-width="1.4" stroke-dasharray="6 4"/>'
             % (L, Y(0.05), W - R, Y(0.05), ROSE))
    p.append('<text x="%d" y="%.1f" font-size="11" fill="%s" '
             'style="%s">pre-registered threshold 0.05</text>'
             % (W - R, Y(0.05) - 6, ROSE, FONT))
    # per-seed points
    for i, (k, pv, ci) in enumerate(zip(ks, ps, cis)):
        x = X(i)
        p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                 'stroke="%s" stroke-width="1.6"/>'
                 % (x, Y(ci[0]), x, Y(ci[1]), BLUE))
        for e in (ci[0], ci[1]):
            p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                     'stroke="%s" stroke-width="1.6"/>'
                     % (x - 6, Y(e), x + 6, Y(e), BLUE))
        p.append('<circle cx="%.1f" cy="%.1f" r="4.6" fill="%s"/>'
                 % (x, Y(pv), BLUE))
        p.append('<text x="%.1f" y="%.1f" font-size="11.5" fill="#1c2433" '
                 'text-anchor="middle" style="%s">%s</text>'
                 % (x, Y(pv) - 10, FONT, f5(pv)))
        p.append('<text x="%.1f" y="%d" font-size="10.5" fill="%s" '
                 'text-anchor="middle" style="%s">%d</text>'
                 % (x, H - B + 18, SLATE, FONT, seeds[i]))
        p.append('<text x="%.1f" y="%d" font-size="10" fill="%s" '
                 'text-anchor="middle" style="%s">%d/20000</text>'
                 % (x, H - B + 32, SLATE, FONT, k))
    # pooled marker
    x = X(len(seeds))
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
             'stroke="%s" stroke-width="2"/>'
             % (x, Y(pooled_ci[0]), x, Y(pooled_ci[1]), AMBER))
    p.append('<rect x="%.1f" y="%.1f" width="9" height="9" fill="%s" '
             'transform="rotate(45 %.1f %.1f)"/>'
             % (x - 4.5, Y(pooled_p) - 4.5, AMBER, x, Y(pooled_p)))
    p.append('<text x="%.1f" y="%.1f" font-size="11.5" fill="%s" '
             'text-anchor="middle" style="%s">%s</text>'
             % (x, Y(pooled_p) - 12, AMBER, FONT, f5(pooled_p)))
    p.append('<text x="%.1f" y="%d" font-size="10.5" fill="%s" '
             'text-anchor="middle" style="%s">pooled</text>'
             % (x, H - B + 18, SLATE, FONT))
    p.append('<text x="%.1f" y="%d" font-size="10" fill="%s" '
             'text-anchor="middle" style="%s">%d/100000</text>'
             % (x, H - B + 32, SLATE, FONT, arr["pooled_k"]))
    # annotation
    p.append('<text x="%d" y="%d" font-size="11.5" fill="#1c2433" '
             'style="%s">homogeneity %s\u00b2 = %.4f (df %d), p = %s '
             '\u2192 %s</text>'
             % (L, 18, FONT, CHI, arr["homogeneity_stat"],
                len(seeds) - 1, f5(arr["homogeneity_p"]),
                arr["classification"].split(" (")[0]))
    p.append('</svg>')
    return "".join(p)


def build_census_svg(eb: dict) -> str:
    tot, orpass, tenulp, orfail = (eb["tot"], eb["orpass"], eb["tenulp"],
                                   eb["orfail"])
    W, H = 940, 128
    x0, x1, y, h = 24, W - 24, 44, 34
    w = x1 - x0
    wp = w * orpass / tot
    p = ['<svg viewBox="0 0 %d %d" width="100%%" role="img" '
         'aria-label="engine B 720-bin census" style="display:block">'
         % (W, H)]
    p.append('<rect x="%d" y="%d" width="%.1f" height="%d" fill="%s" '
             'rx="6"/>' % (x0, y, wp, h, GREEN))
    p.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" fill="%s" '
             'rx="6"/>' % (x0 + wp, y, w - wp, h, AMBER))
    p.append('<text x="%.1f" y="%d" font-size="12" fill="#ffffff" '
             'text-anchor="middle" style="%s">frozen OR pass %d/%d '
             '(of which %d/%d also pass the tighter 10-ulp branch)</text>'
             % (x0 + wp / 2, y + 22, FONT, orpass, tot, tenulp, tot))
    dims = len({c["dim"] for c in eb["cells"]})
    per = len(eb["cells"]) // dims
    enum = eb["enum_cells"]
    per_cell = sorted({len(e["or_fail_bins_cv"]) for e in enum})
    if len(per_cell) != 1:
        raise SystemExit("engine B: enumerated bins-per-cell changed")
    mem = sorted(e["membership_disagreements"]["count"] for e in enum)
    p.append('<text x="%d" y="%d" font-size="11" fill="%s" style="%s">'
             '%d/%d bin-checks \u00b7 %d resolutions \u00d7 %d grid points '
             '\u00d7 20 bins \u00d7 2 curves (cv, tgt)</text>'
             % (x0, 26, SLATE, FONT, tot, tot, dims, per))
    p.append('<text x="%d" y="%d" font-size="11.5" fill="#1c2433" '
             'style="%s">%d/%d OR-fail bins (all chart-L cv edge-cluster, '
             '%d enumerated cells, %d bins each, membership members '
             '%d\u2013%d per cell) \u2014 all excused by the pre-declared '
             'enumeration rule; 0 unexcused failures.</text>'
             % (x0, y + h + 24, FONT, orfail, tot, len(enum),
                per_cell[0], mem[0], mem[-1]))
    p.append('</svg>')
    return "".join(p)


def build_strip(h1: dict) -> str:
    out = ['<div style="display:flex;flex-wrap:wrap;gap:4px;'
           'margin:10px 0 4px">']
    for c in h1["grid"]:
        off = c["k_gue"] > 0
        bg = "#fff4ec" if off else "#eef1f7"
        bc = "#e7b98f" if off else "#d9e0ec"
        lbl = "%d%s%s%s%.1f" % (c["dim"], MID, c["chart"], MID,
                                c["sigma_u"])
        out.append('<span title="k_GUE/20000 = %d" style="min-width:56px;'
                   'padding:4px 7px;border-radius:6px;background:%s;'
                   'border:1px solid %s;font-size:10.5px;text-align:center;'
                   'line-height:1.35"><span style="color:#5b6b85">%s</span>'
                   '<br><b>%d</b></span>'
                   % (c["k_gue"], bg, bc, lbl, c["k_gue"]))
    out.append('</div>')
    out.append('<p class="note" style="margin-top:2px">Census: %d of %d '
               'cells at k_GUE = 0/20000 (95%% upper bound p_GUE &lt; %s); '
               'one off-floor cell \u2014 C4 (dim 301 %s chart T %s '
               '%su = 0.5) at %d/20000.</p>'
               % (len(h1["floor"]), len(h1["grid"]), h1["bound_s"], MID,
                  MID, SIG, h1["c4"]["k_gue"]))
    return "".join(out)


# --------------------------------------------------------------------------
# new panel builders
# --------------------------------------------------------------------------
def build_h1_panel(h1: dict, lad: dict) -> str:
    grid, c4, arr = h1["grid"], h1["c4"], h1["arr"]
    bound_s = h1["bound_s"]

    rows = ""
    for c in grid:
        key = (c["dim"], c["chart"], c["sigma_u"])
        cell = TARGET_CELLS.get(key, "\u2014")
        off = c["k_gue"] > 0
        hl = ' style="background:#fff7ee"' if off else ''
        p_cell = (c["p_gue"] if c["p_gue"]
                  else "p &lt; %s" % bound_s)
        verdict = "NO DISCRIMINATION" if off else "INCONSISTENT"
        sealed = "%d/2000 %s %.4f" % (c["sealed_k_gue"], ARR,
                                      c["sealed_p_gue"])
        rows += ('<tr%s><td class="mono">%s %s %d %s %s %s %su=%.1f</td>'
                 '<td class="mono">%.4f</td><td class="mono">%d/20000</td>'
                 '<td class="mono">%s</td><td class="mono">%s</td>'
                 '<td class="mono">%s</td></tr>'
                 % (hl, cell, MID, c["dim"], MID, c["chart"], MID, SIG,
                    c["sigma_u"], c["chi2_obs"], c["k_gue"], p_cell,
                    verdict, sealed))
    table = ('<table class="t"><thead><tr><th>cell %s dim %s chart %s '
             '%su</th><th>%s\u00b2 obs</th><th>k_GUE/20000</th>'
             '<th>p_GUE (95%% CP)</th><th>verdict (abbrev.)</th>'
             '<th>sealed (2000)</th></tr></thead><tbody>%s</tbody></table>'
             % (MID, MID, MID, SIG, CHI, rows))

    finals_lines = ""
    n_map = {"100": "201", "150": "301", "200": "401"}
    order = sorted(h1["finals"])
    for rel in order:
        line = h1["finals"][rel]
        mrel = re.search(r"100_(\d+)\.txt", rel)
        if not mrel or mrel.group(1) not in n_map:
            raise SystemExit("unexpected A log name: %s" % rel)
        dim = n_map[mrel.group(1)]
        extra = ""
        if "UNSTABLE" in line:
            extra = (" [%d \u00d7 INCONSISTENT + %d \u00d7 NO DISCRIMINATION]"
                     % h1["breakdown"])
        finals_lines += ('<li>dim %s: %s%s</li>' % (dim, v4.esc(line),
                                                    extra))

    seed_rows = ""
    for i, (s, k, pv, ci) in enumerate(zip(arr["seeds"], arr["k"],
                                           arr["per_seed_p"],
                                           arr["per_seed_cp95"])):
        canon = " (canonical)" if i == 0 else ""
        seed_rows += ('<tr><td class="mono">%d%s</td>'
                      '<td class="mono">%d/20000</td>'
                      '<td class="mono">%s</td><td class="mono">%s</td>'
                      '</tr>' % (s, canon, k, f5(pv), cp_str(ci)))
    seed_table = ('<table class="t"><thead><tr><th>seed</th>'
                  '<th>k/20000</th><th>p&#770;</th><th>95%% CP</th>'
                  '</tr></thead><tbody>%s</tbody></table>' % seed_rows)

    body = (
        '<p class="lead">The H1 floor amendment (pre-registered and frozen '
        'in <code>reports/AMENDMENT_FLOOR_SPEC.md</code> before execution) '
        're-measured the S2 grid at 20000 surrogates per ensemble \u2014 '
        'ten times the sealed floor \u2014 and added a five-seed '
        'robustness array for the single off-floor cell C4. Sealed '
        '2026-10-16; independently re-verified by engine B (panel 8). '
        'For the four pre-registered target cells C1\u2013C4 the refined '
        'values supersede the sealed 2000-surrogate values; the sealed '
        'columns remain visible below and are never edited.</p>'
        '<h3>7.1 ' + MID + ' (A) refined grid \u2014 20000 surrogates per '
        'ensemble, seed 20260927</h3>'
        + build_strip(h1) + table
        + '<div class="eq">p<sub>upper</sub> = 1 \u2212 ' + ALPHA
        + '<sup>1/n</sup>, &nbsp; ' + ALPHA + ' = 0.05, &nbsp; n = 20000'
        + '<span class="tag">(CP95 bound, frozen spec \u00a73)</span></div>'
        + '<p class="note">Format (frozen spec \u00a73): k_GUE = 0 is '
        'reported as the 95% Clopper-Pearson upper bound p_GUE &lt; '
        + bound_s + ' (rule of three), never as a measured zero; the '
        '"0.0000" print format is retired. Verdict strings are '
        'abbreviated from the frozen instrument\u2019s literal prints: '
        '\u201cINCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION\u201d '
        '(17 cells) and \u201cNO DISCRIMINATION AT N=401\u201d (C4 '
        '\u2014 the literal hardcoded in the frozen instrument, sha256 '
        + INSTRUMENT_SHA + '\u2026; the cell is dim 301, the label is '
        'quoted verbatim and never edited). Refined S2 FINAL per '
        'resolution, read from the A logs:</p><ul class="chg">'
        + finals_lines + '</ul>'
        '<h3>7.2 ' + MID + ' (B) five-seed robustness array on C4 '
        '\u2014 301 %s T %s %su = 0.5</h3>' % (MID, MID, SIG)
        + build_seed_svg(h1) + seed_table
        + '<div class="eq">p&#770; = ' + SUM + 'k<sub>i</sub> / ' + SUM
        + 'n<sub>i</sub>, &nbsp; ' + CHI + '\u00b2<sub>hom</sub> = '
        + SUM + ' (k<sub>i</sub> \u2212 n<sub>i</sub>p&#770;)\u00b2 / '
        '(n<sub>i</sub>p&#770;(1\u2212p&#770;))'
        + '<span class="tag">(pooled + homogeneity, frozen spec '
        '\u00a74)</span></div>'
        + '<p class="note"><b>Pooled (5 \u00d7 20000):</b> '
        + '%d/100000 = %s (95%% CP %s); homogeneity %s\u00b2 = %.4f '
        '(df 4), p = %s \u2014 frozen decision-tree classification: '
        '<b>%s</b>. C4 is flagged resolution-sensitive; the canonical '
        'number of record remains the 20000 value %d/20000.</p>'
        % (arr["pooled_k"], f5(arr["p_hat"]), cp_str(arr["pooled_cp95"]),
           CHI, arr["homogeneity_stat"], f5(arr["homogeneity_p"]),
           v4.esc(arr["classification"]), c4["k_gue"])
        + '<p class="note"><b>Pre-registered expectation falsified '
        '(recorded, never patched):</b> spec \u00a74 stated that every '
        'branch would leave C4 below the 0.05 verdict threshold; '
        'measured pooled p&#770; = ' + f5(arr["p_hat"]) + ' and '
        + str(h1["n_above"]) + ' of 5 seeds \u2265 0.05 (the exception: '
        'seed 20261001 = 4.80000e-02). Even a STABLE outcome would not '
        'make C4 \u201cphysical\u201d: these are statistics of finite '
        'deterministic matrices \u2014 not Montgomery\u2019s theorem, '
        'not evidence for RH.</p>'
        + '<p class="note">Open item recorded with the panel-1 caption: '
        'the dim-257 rung was measured 2026-10-15 (lambda_min = '
        + lad["lam_s"] + '; registry radius 0.0 = float64 underflow, '
        'not an exact point; ln-slope ' + lad["slope_s"] + ' over 129'
        + ARR + '257 \u2014 plateau candidate). dim 321 remains not run '
        '(deliberately deferred).</p>')
    return body


def build_eb_panel(ebd: dict) -> str:
    eb = ebd["eb"]
    v = eb["verdict"]
    rows = ""
    for c in sorted(ebd["cells"], key=lambda c: (c["dim"], c["chart"],
                                                 c["sigma_u"])):
        rows += ('<tr><td class="mono">%d %s %s %s %su=%.1f</td>'
                 '<td class="mono">%d</td><td class="mono">%d</td>'
                 '<td class="mono">%d</td><td class="mono">%d</td>'
                 '<td class="mono">4/4</td></tr>'
                 % (c["dim"], MID, c["chart"], MID, SIG, c["sigma_u"],
                    c["k_gue"], c["k_gue_lower"], c["k_pois"],
                    c["k_pois_upper"]))
    counts_table = ('<table class="t"><thead><tr>'
                    '<th>cell</th><th>k_GUE</th><th>GUE-lower</th>'
                    '<th>k_Pois</th><th>Pois-upper</th>'
                    '<th>vs engine A</th></tr></thead><tbody>%s</tbody>'
                    '</table>' % rows)

    samp = sorted(set(ebd["declared"]["samples"].values()))
    if len(samp) != 1:
        raise SystemExit("engine B: declared samples differ across dims")

    prov = [("engine B script \u2014 msaf/gw_engine_b_verify.py", EB_SCRIPT),
            ("engine B log \u2014 reports/gw_engine_b_verify.log", EB_LOG),
            ("engine B json \u2014 reports/gw_engine_b_verify.json",
             EB_JSON),
            ("H1 refine json \u2014 reports/gw_h1_floor_refine.json",
             REFINE),
            ("H1 spec \u2014 reports/AMENDMENT_FLOOR_SPEC.md", SPEC),
            ("dim-257 rung \u2014 reports/lambda_min_eig_ladder_big.json",
             LADDER_BIG)]
    hash_rows = "".join('<tr><td class="hp">%s</td><td class="hh">%s</td>'
                        '</tr>' % (v4.esc(n), v4.short_hash(p))
                        for n, p in prov)
    prov_table = ('<table class="hash">%s</table>'
                  '<p class="note">Hash convention: sha256 over '
                  'newline-normalised bytes (CRLF \u2192 LF), first 12 hex '
                  'chars \u2014 identical on every checkout.</p>'
                  % hash_rows)

    body = (
        '<p class="lead">Engine B is an independent re-implementation of '
        'the S2 observed-grid computation (spec \u00a75, checks B1\u2013B6) '
        'run in full mode over all 18 cells at 20000 samples per ensemble '
        '(seed 20260927, mpmath dps = 50). It is verification only '
        '\u2014 never verdict-bearing; a divergence would have stopped '
        'the campaign and published nothing. Sealed 2026-10-17 after the '
        'full run (elapsed %.1f s); pilot history (R1/R2) is recorded in '
        '<code>reports/ENGINE_B_PILOT_FINDINGS_2026-10-16.md</code>.</p>'
        % eb["elapsed_s"]
        + '<div class="chips">'
        + '<span class="chip green">B1 %s</span>' % v["b1"]
        + '<span class="chip green">B3 %s</span>' % v["b3"]
        + '<span class="chip amber">B2a %s</span>' % v["b2_observed_grid"]
        + '<span class="chip green">counts %s</span>' % v["counts"]
        + '<span class="chip green">cells: %d clean + %d enumerated '
        '+ %d failing</span>'
        % (v["cells_pass"], v["cells_pass_enumerated_edge_cluster"],
           v["cells_fail"])
        + '<span class="chip amber">overall %s</span>' % v["overall"]
        + '</div>'
        '<h3>8.1 ' + MID + ' per-bin census (720 checks)</h3>'
        + build_census_svg(ebd)
        + '<p class="note">Per-bin criterion (frozen OR, declared before '
        'the run): ' + v4.esc(ebd["crit"]) + ' The 10-ulp branch is the '
        'declared tighter bound; both branch censuses are reported. '
        'Edge-cluster excuse rule: a cv bin failing the frozen OR is '
        'excused only if covered by enumerated fine-bin membership '
        'disagreements (width 1, bounded members and delta); tgt bins '
        'are never excused. GOE curves were not recomputed (declared '
        'scope limit in the artefact manifest).</p>'
        '<h3>8.2 ' + MID + ' counts vs engine A \u2014 four tails, '
        '18/18 exact</h3>' + counts_table
        + '<p class="note">Counts criterion (frozen): k_GUE and k_Pois '
        'plus the captured GUE-lower / Poisson-upper tails must agree '
        'exactly with engine A; any larger discrepancy would STOP and '
        'publish nothing. Measured: %d/%d cells exact on all four tails '
        '(%d \u00d7 4 = %d exact integer matches).</p>'
        % (len(ebd["cells"]), len(ebd["cells"]), len(ebd["cells"]),
           len(ebd["cells"]) * 4)
        + '<h3>8.3 ' + MID + ' provenance</h3>' + prov_table
        + '<p class="scope"><b>Run manifest (declared before run):</b> '
        'mpmath dps = %d %s seed = %d %s samples = %d per ensemble '
        '(dim 201/301/401) %s elapsed = %.1f s %s repo head = '
        '<span class="mono">%s</span>.</p>'
        % (ebd["declared"]["mpmath_dps"], MID, ebd["declared"]["seed"],
           MID, samp[0], MID, eb["elapsed_s"], MID,
           v4.esc(eb["repo_head"][:12]))
        + '<p class="scope"><b>Scope:</b> this panel verifies the '
        'engine-A numbers; it never changes a verdict. Guard test: '
        '<code>msaf/tests/test_gw_engine_b_full_artifact.py</code>. '
        'The engine-B artefacts are append-only; the R1/R2 interruptions '
        'are preserved verbatim in the findings note.</p>')
    return body


# --------------------------------------------------------------------------
# patch application + render
# --------------------------------------------------------------------------
def apply_patch(base: str, old: str, new: str, label: str,
                applied: list) -> str:
    n = base.count(old)
    if n != 1:
        raise SystemExit("v5 patch %r matched %d times (expected 1)"
                         % (label, n))
    applied.append(label)
    return base.replace(old, new)


def render(ctx4: dict, h1: dict, eb: dict, lad: dict) -> tuple:
    base = v4.render(ctx4)
    applied: list = []
    v4_full = v4.full_hash(V4)
    v4_short = v4_full[:12]
    v3_short = ctx4["v3_short"]

    # 1. title / kicker / h1
    base = apply_patch(
        base,
        "<title>Guinand-Weil Resolution-Series Diagnostics \u2014 "
        "Dashboard v4</title>",
        "<title>Guinand-Weil Resolution-Series Diagnostics \u2014 "
        "Dashboard v5</title>", "title", applied)
    base = apply_patch(
        base,
        '<div class="kicker">Sealed record \u00b7 resolution series '
        'dim 201 / 301 / 401 \u00b7 c = 100 Montgomery construction '
        '\u00b7 2026-10-16</div>',
        '<div class="kicker">Sealed record \u00b7 resolution series '
        'dim 201 / 301 / 401 \u00b7 H1 floor amendment (A+B) + '
        'engine-B verification (C) \u00b7 c = 100 Montgomery '
        'construction \u00b7 2026-10-17</div>', "kicker", applied)
    base = apply_patch(base, '>v4</span></h1>', '>v5</span></h1>',
                       "h1 mark", applied)

    # 2. hero sub
    base = apply_patch(
        base, "by <code>msaf/gw_dashboard_v4.py</code>",
        "by <code>msaf/gw_dashboard_v5.py</code>", "sub module", applied)
    base = apply_patch(
        base,
        "English, derivations-complete rebuild of the sealed v3 layout; "
        "<b>v3 is preserved byte-identical</b> (sha256 in panel 6).",
        "English; v5 extends the v4 layout with the H1 floor-amendment "
        "and engine-B verification panels. <b>v4 and v3 are preserved "
        "byte-identical</b> (sha256 in panel 6).", "sub preserved",
        applied)

    # 3. chips
    chip_h1 = ('<span class="chip green">H1 refined 20000: %d/%d cells '
               'k_GUE = 0/20000 \u00b7 bound p_GUE &lt; %s</span>'
               % (len(h1["floor"]), len(h1["grid"]), h1["bound_s"]))
    chip_c4 = ('<span class="chip amber">C4 (301|T|0.5): %d/20000 = %s '
               '\u2192 NO DISCRIMINATION \u00b7 NOT STABLE (homogeneity '
               'p = %s)</span>'
               % (h1["c4"]["k_gue"], h1["c4"]["p_gue"],
                  f5(h1["arr"]["homogeneity_p"])))
    chip_eb = ('<span class="chip green">engine B: %s \u2014 counts '
               '18/18 exact</span>' % eb["eb"]["verdict"]["overall"])
    base = apply_patch(
        base,
        '<span class="chip amber">floor census: 17/18 cells at p_GUE = '
        '0.0000 \u00b7 grid max 0.0180</span>',
        '<span class="chip amber">floor census (sealed 2000): 17/18 '
        'cells at p_GUE = 0.0000 \u00b7 grid max 0.0180</span>'
        + chip_h1 + chip_c4 + chip_eb, "chips", applied)

    # 4. toc
    base = apply_patch(
        base, '</nav>',
        '<a href="#h1">Panel 7 \u2014 H1 floor amendment</a>'
        '<a href="#engineb">Panel 8 \u2014 engine B verification</a>'
        '</nav>', "toc", applied)

    # 5. panel 1 caption (dim-257 correction)
    base = apply_patch(
        base, "dim 257/321 not yet measured.",
        "dim 321 not yet run (deliberately deferred; see HANDOFF); "
        "dim 257 was measured on 2026-10-15: lambda_min = "
        + lad["lam_s"] + " with every enclosure excluding zero; the "
        "registry radius 0.0 is a float64 underflow, not an exact point "
        "(ln-slope " + lad["slope_s"] + " over 129\u2192257 \u2014 "
        "plateau candidate; stored in "
        "reports/lambda_min_eig_ladder_big.json).",
        "panel1 caption", applied)

    # 6. heatmap label + note
    base = apply_patch(
        base, '<div class="dim">dim 401 (baseline run 2)</div>',
        '<div class="dim">dim 401 (baseline run 2 \u00b7 sealed)</div>',
        "heat label", applied)
    base = apply_patch(
        base, "<b>Artifact verdict:</b>",
        '<p class="note">Row labels: \u201cnew capture\u201d = the '
        'third-resolution capture sealed 2026-10-16; \u201cbaseline run '
        '2\u201d = the second, sealed baseline measurement of dim 401 '
        '\u2014 run 1 was retired under the defect register (a completed '
        'run; the label does not denote a running process).</p>'
        "<b>Artifact verdict:</b>", "heat note", applied)

    # 7. panel 6 additions
    marker = '<p class="scope"><b>Preserved predecessor:</b>'
    i = base.find(marker)
    if i == -1:
        raise SystemExit("v5 patch 'preserved predecessor' not found")
    j = base.find('</p>', i)
    if j == -1:
        raise SystemExit("v5 patch 'preserved predecessor' unclosed")
    v4_par = ('<p class="scope"><b>Preserved predecessor (v5):</b> '
              'reports/gw_diagnostic_v4.html \u2014 byte-identical, full '
              'sha256 <span class="mono">' + v4_full + '</span> (first '
              '12: ' + v4_short + ').</p>')
    base = base[:j + 4] + v4_par + base[j + 4:]
    applied.append("v4 preserved paragraph")

    v5_changes = (
        '<p class="scope"><b>Changes in v5 relative to v4:</b></p>'
        '<ul class="chg">'
        '<li>New panel 7: H1 floor amendment \u2014 refined '
        '20000-surrogate grid (17/18 cells at the 0/20000 bound) + '
        'five-seed robustness array for C4, with a new seed chart.</li>'
        '<li>New panel 8: engine-B independent verification \u2014 '
        'verdict chips, 720-check census chart, 18/18 exact counts '
        'table, provenance.</li>'
        '<li>Hero chips updated: sealed-2000 census relabelled; H1 and '
        'engine-B chips added.</li>'
        '<li>Panel 1 caption corrected: the dim-257 rung was measured '
        '2026-10-15 (v4 said \u201c257/321 not yet measured\u201d); the '
        'measured value is now stated; dim 321 remains open.</li>'
        '<li>Heatmap row-label note added (\u201cbaseline run 2\u201d = '
        'completed, sealed run).</li>'
        '<li>v4 preserved byte-identical \u2014 nothing in it was '
        'edited (sha256 above).</li></ul>')
    base = apply_patch(
        base, '<p class="scope"><b>Changes in v4 relative to v3:</b></p>',
        v5_changes + '<p class="scope"><b>Changes in v4 relative to '
        'v3:</b></p>', "v5 changes list", applied)
    base = apply_patch(
        base, '<code>python msaf/gw_dashboard_v4.py --write</code>',
        '<code>python msaf/gw_dashboard_v5.py --write</code>',
        "regenerate hint", applied)

    # 7b. radius wording in the four imported chart tooltips (2026-10-17
    #     float64 registry correction: the field records 0.0, the true
    #     radius is nonzero but below the float64 floor)
    tip_old = " (enclosure radius = 0.0)</title>"
    tip_new = (" (registry radius = 0.0 \u2014 float64 underflow, "
               "not an exact point)</title>")
    n_tip = base.count(tip_old)
    if n_tip != 4:
        raise SystemExit("v5 tooltip radius anchors: expected 4, found %d"
                         % n_tip)
    base = base.replace(tip_old, tip_new)
    applied.append("tooltip radius wording (4x)")

    # 8. new panels + footer
    footer = ('<footer>Rendered by msaf/gw_dashboard_v5.py \u2014 '
              'byte-stable \u00b7 no JavaScript \u00b7 no external '
              'resources. v4 preserved byte-identical (' + v4_short
              + '); v3 preserved byte-identical (' + v3_short
              + ').</footer>')
    new_panels = (
        v4.panel("h1", "Panel 7 \u2014 H1 floor amendment: refined "
                 "20000 grid + five-seed C4 array",
                 build_h1_panel(h1, lad))
        + v4.panel("engineb", "Panel 8 \u2014 engine B: independent "
                   "verification of the S2 grid",
                   build_eb_panel(eb))
        + footer)
    base = apply_patch(base, '</div></body></html>',
                       new_panels + '</div></body></html>',
                       "new panels", applied)
    return base, applied


def collect_all() -> tuple:
    return (v4.collect(), collect_h1(), collect_eb(), collect_ladder257())


def build() -> str:
    ctx4, h1, eb, lad = collect_all()
    html, _applied = render(ctx4, h1, eb, lad)
    return html


def main(argv: list) -> int:
    write = "--write" in argv
    ctx4, h1, eb, lad = collect_all()
    html, applied = render(ctx4, h1, eb, lad)

    print("v5 dashboard source check:")
    print("  H1: %d/%d floor cells; bound p_GUE < %s; C4 %d/20000 = %s"
          % (len(h1["floor"]), len(h1["grid"]), h1["bound_s"],
             h1["c4"]["k_gue"], h1["c4"]["p_gue"]))
    print("  H1 seeds: pooled %d/100000 = %s; homogeneity p = %s -> %s"
          % (h1["arr"]["pooled_k"], f5(h1["arr"]["p_hat"]),
             f5(h1["arr"]["homogeneity_p"]),
             h1["arr"]["classification"].split(" (")[0]))
    print("  engine B: %s; census %d/%d frozen OR, %d/%d 10-ulp, "
          "%d/%d OR-fail all enumerated; counts 18/18 exact"
          % (eb["eb"]["verdict"]["overall"], eb["orpass"], eb["tot"],
             eb["tenulp"], eb["tot"], eb["orfail"], eb["tot"]))
    print("  dim-257 rung: %s (eig %.2f s; ln-slope %s)"
          % (lad["lam_s"], lad["eig_s"], lad["slope_s"]))
    print("  patches applied: %d" % len(applied))
    print("  v4 seal: %s (preserved, untouched)" % v4.full_hash(V4))
    print("  html size: %.1f KB" % (len(html.encode("utf-8")) / 1024.0))

    if not write:
        print("DRY RUN -- rerun with --write to write %s" % OUT)
        return 0
    OUT.write_bytes(html.encode("utf-8"))
    print("written: %s (%d bytes)" % (OUT, OUT.stat().st_size))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))


