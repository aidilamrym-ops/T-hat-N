# -*- coding: utf-8 -*-
"""gw_dashboard_v6.py -- C4 S10 robustness extension + dim-501 outcome
panel over the byte-frozen v5 dashboard.

What this module does
---------------------
Renders reports/gw_diagnostic_v6.html from:
  * the byte-frozen v5 page rendered by msaf/gw_dashboard_v5.py -- its
    sha256 is hard-asserted before any patch is applied and embedded in
    panel 6 (v5 layout preserved byte-identical);
  * the C4 S10 extension artefact (reports/gw_h1_c4_seeds10.json);
  * the dim-321 lambda_min rung (reports/lambda_min_eig_ladder_dim321.json
    + .log) for the panel-1 caption and panel-7 open-item corrections;
  * the fourth-resolution-point artefacts
    (reports/gw_route_s_ladder_c100_n250.json + .log, the launch log).

Every number is machine-extracted at build time; a missing file, a
missing field, a value that contradicts the sealed record, or a patch
anchor that does not match exactly once aborts the build. No number is
typed by hand; no timestamp is embedded; reruns are byte-stable.

Scope notes recorded in v6 (owner decision 2026-10-18):
  * release scope note "analytic justification at t=0 remains external"
    (quoted verbatim; surfaced by the audit-P1 lane, registry
    A-2026-0001) -- recorded in panel 6 per owner decision;
  * S10 scope note -- panel 9;
  * dim-501 outcome scope note -- panel 10.

Patches applied to the v5 base (each must match exactly once):
  1. title / kicker / h1 version mark v5 -> v6;
  2. hero sub: v6 provenance + preserved statement;
  3. hero chips: S10 + dim-501 outcome chips added;
  4. table of contents: two new entries (panels 9 and 10);
  5. panel 1 caption: dim-321 rung correction (measured 2026-10-17;
     v5 said "dim 321 not yet run");
  6. panel 7 open item: dim-321 measured (v5 said "remains not run");
  7. panel 6: v5 preserved-predecessor paragraph + "changes in v6"
     list + the recorded scope-notes block; regenerate hint v5 -> v6;
  8. two new panels (9: C4 S10 extension; 10: dim-501 outcome)
     + footer.

CLI:
    python msaf/gw_dashboard_v6.py           # dry run: prints extracted data
    python msaf/gw_dashboard_v6.py --write   # writes the HTML
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gw_dashboard_v5 as v5  # noqa: E402  (frozen base; never modified)
import gw_dashboard_v4 as v4  # noqa: E402  (helpers; frozen)

V5 = ROOT / "reports" / "gw_diagnostic_v5.html"
OUT = ROOT / "reports" / "gw_diagnostic_v6.html"
S10_JSON = ROOT / "reports" / "gw_h1_c4_seeds10.json"
S10_PREREG = ROOT / "reports" / "C4_SEEDS10_PREREG_2026-10-17.md"
S10_SECTION = ROOT / "reports" / "h1_c4_seeds10_section.md"
S10_TOOL = HERE / "gw_h1_c4_seeds10.py"
LADDER321 = ROOT / "reports" / "lambda_min_eig_ladder_dim321.json"
LADDER321_LOG = ROOT / "reports" / "lambda_min_eig_ladder_dim321.log"
RES4_JSON = ROOT / "reports" / "gw_route_s_ladder_c100_n250.json"
RES4_LOG = ROOT / "reports" / "gw_route_s_ladder_c100_n250.log"
RES4_LAUNCH = ROOT / "reports" / "res4_dim501_launch_2026-10-17.log"
RES4_TOOL = HERE / "gw_route_s_ladder.py"
RES4_PREREG = ROOT / "reports" / "RESOLUTION4_DIM501_PREREG_2026-10-17.md"

# the v5 page this module freezes as its base (sha256LF, README-pinned)
V5_SHA = "0e99571b887f17b95180edc478af7bf887cce861edfbc9fd2ac3b1a2798d4259"
# instrument / spectrum hashes sealed in the S10 artefact manifest
INSTRUMENT_SHA = "072910f232b15768ba35e14d7cc6aaf4fe1ee174dc45b65429460f791196e1d5"
SPECTRUM_SHA = "8fded8394f0ab4e8ed83f537609d313d0d50eef42f09214c30d1cfcd994d161d"
S10_PREREG_SHA = "d8dd65cd614f5457a5fe12f7aa24556dc97a4dcda57fed0d01b69f8fb34a0b95"
RES4_TOOL_SHA = "cc09ed5a35ac90b581cf2ef5660f3db903704843909b8a80b7fb21bf036a5b20"

MID = v5.MID
ARR = v5.ARR
EMD = v5.EMD
SIG = v5.SIG
CHI = v5.CHI
SUM = v5.SUM
GREEN = v5.GREEN
AMBER = v5.AMBER
BLUE = v5.BLUE
ROSE = v5.ROSE
SLATE = v5.SLATE
FONT = v5.FONT
f5 = v5.f5
cp_str = v5.cp_str


def read_text(path) -> str:
    return Path(path).read_text(encoding="utf-8-sig")


def read_json(path) -> dict:
    return v5.read_json(path)


# --------------------------------------------------------------------------
# collectors -- fail loud on any contradiction with the sealed records
# --------------------------------------------------------------------------
def collect_s10() -> dict:
    s10 = read_json(S10_JSON)
    pre, base = s10["preregistration"], s10["base"]
    ext = s10["extension"]
    man = s10["manifest"]

    # pre-registration seal + ordering (anti-cocoklogi)
    if pre["sha256_lf"] != S10_PREREG_SHA or \
            not pre["commit"].startswith("657352c"):
        raise SystemExit("S10: preregistration seal changed")
    order = man["prereg_order_check"]
    if order["status"] != "PASS" or \
            not (order["prereg_commit_time_local"]
                 < order["first_new_run_start"]):
        raise SystemExit("S10: pre-registration ordering check failed")

    # sealed S5 base must match the frozen refine artefact
    arr = base["sealed_c4_array"]
    if arr["k"] != [1262, 960, 1289, 1021, 1345] or \
            arr["pooled_k"] != 5877 or arr["pooled_n"] != 100000 or \
            not arr["classification"].startswith("NOT STABLE"):
        raise SystemExit("S10: sealed S5 array changed")
    if v4.full_hash(v5.REFINE) != base["sha256_lf"]:
        raise SystemExit("S10: sealed refine artefact hash mismatch")
    if not base["reparse_crosscheck"]["all_match"] or \
            not all(base["reparse_crosscheck"]["checks"].values()):
        raise SystemExit("S10: reparse cross-check not clean")

    # extension arrays
    seeds = [20260927, 20261001, 20261002, 20261003, 20261004,
             20261005, 20261006, 20261007, 20261008, 20261009]
    ks = [1262, 960, 1289, 1021, 1345, 1164, 1115, 1114, 1022, 1166]
    if ext["seeds"] != seeds or ext["k"] != ks or \
            ext["new_seeds"] != seeds[5:]:
        raise SystemExit("S10: extension seed array changed")
    if ext["pooled_k"] != sum(ks) or ext["pooled_k"] != 11458 or \
            ext["pooled_n"] != 200000 or ext["n_per_seed"] != 20000:
        raise SystemExit("S10: pooled counts changed")
    if abs(ext["p_hat"] - ext["pooled_k"] / ext["pooled_n"]) > 1e-12:
        raise SystemExit("S10: pooled p_hat inconsistent")
    for k, p in zip(ks, ext["per_seed_p"]):
        if abs(p - k / 20000.0) > 5e-9:
            raise SystemExit("S10: per-seed p inconsistent with k")
    if ext["homogeneity_df"] != 9 or \
            not ext["classification"].startswith("NOT STABLE"):
        raise SystemExit("S10: homogeneity classification changed")
    nor = ext["number_of_record"]
    if nor["k"] != 1262 or nor["n"] != 20000 or \
            nor["p"] != "6.31000e-02":
        raise SystemExit("S10: number of record changed")

    # run manifest: instrument/spectrum identical, five runs, exact caps
    if man["instrument_sha256"] != INSTRUMENT_SHA or \
            man["spectrum_sha256"] != SPECTRUM_SHA:
        raise SystemExit("S10: instrument/spectrum hash changed")
    logs = man["new_logs"]
    if sorted(logs) != [str(s) for s in seeds[5:]] or \
            any(e["exact_capture_count"] != 36 for e in logs.values()):
        raise SystemExit("S10: new-run manifest changed")
    elapsed = [logs[str(s)]["elapsed_s"] for s in seeds[5:]]

    n_above = sum(1 for p in ext["per_seed_p"] if p >= 0.05)
    if n_above != 9:
        raise SystemExit("S10: seed census changed (>= 0.05)")
    return {"s10": s10, "ext": ext, "arr": arr, "n_above": n_above,
            "elapsed": elapsed, "man": man, "pre": pre}


def collect_ladder321() -> dict:
    big257 = v5.collect_ladder257()          # validates the dim-257 rung
    lad = read_json(LADDER321)
    runs = lad["runs"]
    if len(runs) != 1:
        raise SystemExit("dim-321 ladder: expected a single run")
    r = runs[0]
    if (r["dim"], r["N"], r["c"], r["prec_bits"]) != (321, 160, 13, 6000):
        raise SystemExit("dim-321 ladder: run parameters changed")
    if r["n_eigenvalues"] != 321 or not r["all_finite"] or \
            not r["all_exclude_zero"] or r["lambda_min_rad"] != 0.0 or \
            not r["verdict"].startswith("CERTIFIED"):
        raise SystemExit("dim-321 ladder: rung not certified")
    if v4.full_hash(LADDER321) != "e92e05ef8d37b10bb3e39c65e7537e23c8e" \
            "3a426da548028a0a560126b60b696" or \
            v4.full_hash(LADDER321_LOG) != "8f3a41074718278927b350fc92" \
            "68600108322aefe7e8dc091245a4d620e1ebbc":
        raise SystemExit("dim-321 ladder: artefact hash drifted from report")
    lam = r["lambda_min_lo"]
    lam_s = "%.6e" % lam
    slope_s = "%+.6f" % (math.log(lam / big257["lam"]) / (321 - 257))
    if lam_s != "3.123459e-59" or slope_s != "-0.000854":
        raise SystemExit("dim-321 ladder: formatted values changed")
    if abs(lam / big257["lam"] - 0.9467838255140328) > 1e-12:
        raise SystemExit("dim-321 ladder: ratio disagrees with report")
    if lam_s not in read_text(LADDER321_LOG):
        raise SystemExit("dim-321 ladder: log disagrees")
    return {"lam": lam, "lam_s": lam_s, "slope_s": slope_s,
            "eig_s": r["eig_s"], "r": r}


def collect_res4() -> dict:
    j = read_json(RES4_JSON)
    runs = j["runs"]
    if len(runs) != 1:
        raise SystemExit("res4: expected a single run")
    r = runs[0]
    if (r["dim"], r["N"], r["c"], r["prec_bits"]) != (501, 250, 100, 6000):
        raise SystemExit("res4: run parameters changed")
    if (r["n_pos"], r["n_neg"], r["undetermined_pivot"],
            r["pivots_recorded"], r["entries_finite"]) != \
            (446, 0, 446, 446, True):
        raise SystemExit("res4: pivot census changed")
    if r["verdict"] != "UNDETERMINED at pivot 446":
        raise SystemExit("res4: verdict changed")
    if (r["build_s"], r["ldlt_s"], r["total_s"]) != \
            (1612.96, 177.07, 1790.13):
        raise SystemExit("res4: timings changed")
    for path, pref in ((RES4_JSON, "3d210490"), (RES4_LOG, "3d896377"),
                       (RES4_LAUNCH, "48074b5d")):
        if not v4.full_hash(path).startswith(pref):
            raise SystemExit("res4: artefact hash drifted: %s" % path.name)
    if v4.full_hash(RES4_TOOL) != RES4_TOOL_SHA:
        raise SystemExit("res4: ladder tool hash changed")
    log = read_text(RES4_LOG)
    if not re.search(r"250\s+501\s+6000\s+446\s+0\s+True\s+1612\.96\s+"
                     r"177\.07\s+UNDETERMINED at pivot 446", log) or \
            "1 run(s); 0 certified, 1 not certified" not in log:
        raise SystemExit("res4: run log disagrees")
    launch = read_text(RES4_LAUNCH)
    if "orchestrator start" not in launch or \
            "stage L finished exit= elapsed=1791s" not in launch or \
            "ABORT: stage L nonzero exit" not in launch:
        raise SystemExit("res4: launcher log changed")
    return {"j": j, "r": r, "log": log, "launch": launch}


# --------------------------------------------------------------------------
# new SVG builders (inline SVG: no xmlns, no external references)
# --------------------------------------------------------------------------
def build_s10_svg(s10: dict) -> str:
    ext = s10["ext"]
    seeds, ks, ps = ext["seeds"], ext["k"], ext["per_seed_p"]
    cis = ext["per_seed_cp95"]
    pooled_p, pooled_ci = ext["p_hat"], ext["pooled_cp95"]
    W, H = 940, 300
    L, R, T, B = 70, 30, 26, 64
    lo, hi = 0.044, 0.073

    def Y(v: float) -> float:
        return T + (hi - v) / (hi - lo) * (H - T - B)

    def X(i: int) -> float:
        return L + (i + 0.5) * (W - L - R) / (len(seeds) + 1)

    p = ['<svg viewBox="0 0 %d %d" width="100%%" role="img" '
         'aria-label="C4 S10 ten-seed robustness array" '
         'style="display:block">' % (W, H)]
    for gv in (0.05, 0.06, 0.07):
        p.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" '
                 'stroke="#e4e9f2" stroke-width="1"/>'
                 % (L, Y(gv), W - R, Y(gv)))
        p.append('<text x="%d" y="%.1f" font-size="11" fill="%s" '
                 'text-anchor="end" style="%s">%.2f</text>'
                 % (L - 8, Y(gv) + 4, SLATE, FONT, gv))
    p.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" '
             'stroke-width="1.4" stroke-dasharray="6 4"/>'
             % (L, Y(0.05), W - R, Y(0.05), ROSE))
    p.append('<text x="%d" y="%.1f" font-size="11" fill="%s" '
             'style="%s">pre-registered threshold 0.05</text>'
             % (W - R, Y(0.05) - 6, ROSE, FONT))
    for i, (k, pv, ci) in enumerate(zip(ks, ps, cis)):
        x = X(i)
        col = BLUE if i < 5 else AMBER
        p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                 'stroke="%s" stroke-width="1.6"/>'
                 % (x, Y(ci[0]), x, Y(ci[1]), col))
        for e in (ci[0], ci[1]):
            p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                     'stroke="%s" stroke-width="1.6"/>'
                     % (x - 6, Y(e), x + 6, Y(e), col))
        p.append('<circle cx="%.1f" cy="%.1f" r="4.6" fill="%s"/>'
                 % (x, Y(pv), col))
        p.append('<text x="%.1f" y="%.1f" font-size="11" fill="#1c2433" '
                 'text-anchor="middle" style="%s">%s</text>'
                 % (x, Y(pv) - 10, FONT, f5(pv)))
        p.append('<text x="%.1f" y="%d" font-size="9.5" fill="%s" '
                 'text-anchor="middle" style="%s">%d</text>'
                 % (x, H - B + 18, SLATE, FONT, seeds[i]))
        p.append('<text x="%.1f" y="%d" font-size="9.5" fill="%s" '
                 'text-anchor="middle" style="%s">%d/20000</text>'
                 % (x, H - B + 32, SLATE, FONT, k))
    x = X(len(seeds))
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
             'stroke="%s" stroke-width="2"/>'
             % (x, Y(pooled_ci[0]), x, Y(pooled_ci[1]), ROSE))
    p.append('<rect x="%.1f" y="%.1f" width="9" height="9" fill="%s" '
             'transform="rotate(45 %.1f %.1f)"/>'
             % (x - 4.5, Y(pooled_p) - 4.5, ROSE, x, Y(pooled_p)))
    p.append('<text x="%.1f" y="%.1f" font-size="11" fill="%s" '
             'text-anchor="middle" style="%s">%s</text>'
             % (x, Y(pooled_p) - 12, ROSE, FONT, f5(pooled_p)))
    p.append('<text x="%.1f" y="%d" font-size="9.5" fill="%s" '
             'text-anchor="middle" style="%s">pooled</text>'
             % (x, H - B + 18, SLATE, FONT))
    p.append('<text x="%.1f" y="%d" font-size="9.5" fill="%s" '
             'text-anchor="middle" style="%s">%d/%d</text>'
             % (x, H - B + 32, SLATE, FONT, ext["pooled_k"],
                ext["pooled_n"]))
    p.append('<text x="%d" y="14" font-size="11" fill="#1c2433" '
             'style="%s">homogeneity %sÂ² = %.4f (df %d), p = %s â†’ %s'
             '</text>'
             % (L, FONT, CHI, ext["homogeneity_stat"],
                ext["homogeneity_df"], f5(ext["homogeneity_p"]),
                ext["classification"].split(" (")[0]))
    p.append('<text x="%d" y="14" font-size="11" fill="%s" '
             'text-anchor="end" style="%s">S5 sealed (blue) Â· S10 new '
             '(amber) Â· pooled (rose)</text>' % (W - R, SLATE, FONT))
    p.append('</svg>')
    return "".join(p)


def build_res4_svg(res4: dict) -> str:
    r = res4["r"]
    dim, n_pos = r["dim"], r["n_pos"]
    W, H = 940, 128
    x0, x1, y, h = 24, W - 24, 44, 34
    w = x1 - x0
    wp = w * n_pos / dim
    p = ['<svg viewBox="0 0 %d %d" width="100%%" role="img" '
         'aria-label="dim-501 LDL^T pivot census" style="display:block">'
         % (W, H)]
    p.append('<rect x="%d" y="%d" width="%.1f" height="%d" fill="%s" '
             'rx="6"/>' % (x0, y, wp, h, GREEN))
    p.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" '
             'fill="#e2e8f0" rx="6"/>' % (x0 + wp, y, w - wp, h))
    p.append('<text x="%.1f" y="%d" font-size="12" fill="#ffffff" '
             'text-anchor="middle" style="%s">%d / %d pivots decided '
             'positive (interval sign)</text>'
             % (x0 + wp / 2, y + 22, FONT, n_pos, dim))
    p.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" '
             'stroke-width="2"/>'
             % (x0 + wp, y - 6, x0 + wp, y + h + 6, ROSE))
    p.append('<text x="%d" y="%d" font-size="11" fill="%s" '
             'style="%s">LDL^T pivot census â€” dim %d Â· Route S ladder Â· '
             'c = %d, N = %d, 6000 bit</text>'
             % (x0, 26, SLATE, FONT, dim, r["c"], r["N"]))
    p.append('<text x="%.1f" y="%d" font-size="10.5" fill="%s" '
             'style="%s">pivot %d</text>'
             % (x0 + wp + 4, y - 8, ROSE, FONT, r["undetermined_pivot"]))
    p.append('<text x="%d" y="%d" font-size="11.5" fill="#1c2433" '
             'style="%s">n_neg = %d Â· entries finite = %s Â· first '
             'undetermined pivot: %d â†’ UNDETERMINED at pivot %d '
             '(non-PD outcome; the statistics of this point end here)'
             '</text>'
             % (x0, y + h + 24, FONT, r["n_neg"],
                str(r["entries_finite"]).lower(),
                r["undetermined_pivot"], r["undetermined_pivot"]))
    p.append('<text x="%d" y="%d" font-size="11" fill="%s" '
             'style="%s">build %.2f s Â· LDL^T %.2f s Â· total %.2f s '
             '(launcher elapsed 1791 s)</text>'
             % (x0, y + h + 40, SLATE, FONT, r["build_s"], r["ldlt_s"],
                r["total_s"]))
    p.append('</svg>')
    return "".join(p)


# --------------------------------------------------------------------------
# new panel builders
# --------------------------------------------------------------------------
def _hash_table(pairs) -> str:
    rows = "".join('<tr><td class="hp">%s</td><td class="hh">%s</td>'
                   '</tr>' % (v4.esc(n), v4.short_hash(p))
                   for n, p in pairs)
    note = ('<p class="note">Hash convention: sha256 over '
            'newline-normalised bytes (CRLF \u2192 LF), first 12 hex '
            'chars \u2014 identical on every checkout.</p>')
    return '<table class="hash">%s</table>' % rows + note


def build_s10_panel(s10: dict) -> str:
    ext = s10["ext"]
    rows = ""
    for i, (s, k, pv, ci) in enumerate(zip(ext["seeds"], ext["k"],
                                           ext["per_seed_p"],
                                           ext["per_seed_cp95"])):
        seg = "S5 (sealed)" if i < 5 else "S10 (new)"
        rows += ('<tr><td class="mono">%d</td><td class="mono">%d/20000'
                 '</td><td class="mono">%s</td><td class="mono">%s</td>'
                 '<td class="mono">%s</td></tr>'
                 % (s, k, f5(pv), cp_str(ci), seg))
    table = ('<table class="t"><thead><tr><th>seed</th><th>k/20000</th>'
             '<th>p&#770;</th><th>95%% CP</th><th>segment</th>'
             '</tr></thead><tbody>%s</tbody></table>' % rows)

    prov_table = _hash_table([
        ("preregistration \u2014 reports/C4_SEEDS10_PREREG_2026-10-17.md",
         S10_PREREG),
        ("S10 artefact \u2014 reports/gw_h1_c4_seeds10.json", S10_JSON),
        ("S10 section \u2014 reports/h1_c4_seeds10_section.md", S10_SECTION),
        ("extractor \u2014 msaf/gw_h1_c4_seeds10.py", S10_TOOL),
        ("sealed refine \u2014 reports/gw_h1_floor_refine.json", v5.REFINE)])

    elapsed_s = "/".join("%.1f" % e for e in s10["elapsed"])
    nor = ext["number_of_record"]
    body = (
        '<p class="lead">The five-seed C4 robustness array (panel 7.2) '
        'was extended to ten seeds on 2026-10-17 with five fresh seeds, '
        'pre-registered in <code>reports/C4_SEEDS10_PREREG_2026-10-17.md'
        '</code> and committed before the first new draw (ordering check '
        'PASS). Same instrument (sha256 ' + INSTRUMENT_SHA[:8]
        + '\u2026, identical across all five new run headers), same '
        'cell: dim 301 ' + MID + ' chart T ' + MID + ' ' + SIG
        + 'u = 0.5. Every number below is machine-extracted from '
        '<code>reports/gw_h1_c4_seeds10.json</code>.</p>'
        + '<div class="chips">'
        + '<span class="chip amber">pooled (10 \u00d7 20000): '
        + f5(ext["p_hat"]) + ' \u2014 NOT STABLE</span>'
        + '<span class="chip green">number of record unchanged: '
        + '1262/20000 = 6.31000e-02</span>'
        + '<span class="chip green">ordering PASS \u00b7 5 new runs, '
        + '36/36 exact captures each</span>'
        + '</div>'
        '<h3>9.1 ' + MID + ' (B+) S5 \u2192 S10 \u2014 seeds, chart, '
        'pooled statistics</h3>'
        + build_s10_svg(s10) + table
        + '<div class="eq">p&#770; = ' + SUM + 'k<sub>i</sub> / ' + SUM
        + 'n<sub>i</sub>, &nbsp; ' + CHI + '\u00b2<sub>hom</sub> = '
        + SUM + ' (k<sub>i</sub> \u2212 n<sub>i</sub>p&#770;)\u00b2 / '
        '(n<sub>i</sub>p&#770;(1\u2212p&#770;))'
        + '<span class="tag">(pooled + homogeneity, frozen spec '
        '\u00a74)</span></div>'
        + '<p class="note"><b>Pooled (10 \u00d7 20000):</b> '
        + '%d/%d = %s (95%% CP %s); homogeneity %s\u00b2 = %.4f '
        '(df %d), p = %s \u2014 frozen decision-tree classification: '
        '<b>%s</b>. %d of 10 seeds \u2265 0.05 (the exception: seed '
        '20261001 = 4.80000e-02). C4 remains resolution-sensitive; the '
        'number of record is <b>unchanged</b> (canonical seed 20260927: '
        '%d/20000 = %s).</p>'
        % (ext["pooled_k"], ext["pooled_n"], f5(ext["p_hat"]),
           cp_str(ext["pooled_cp95"]), CHI, ext["homogeneity_stat"],
           ext["homogeneity_df"], f5(ext["homogeneity_p"]),
           v4.esc(ext["classification"]), s10["n_above"], nor["k"],
           nor["p"])
        + '<p class="note"><b>Pre-registered question, answered as '
        'measured:</b> does the S5 dispersion persist at n = 10? '
        '\u2014 it persists (NOT STABLE; dispersion-dominated). The '
        'extension enlarges the robustness statement only: it never '
        'changes the canonical number and is never evidence about '
        'Montgomery\u2019s theorem or RH.</p>'
        + '<h3>9.2 ' + MID + ' provenance and run manifest</h3>'
        + prov_table
        + '<p class="scope"><b>Run manifest (pre-declared):</b> 5 new '
        'seeds ' + str(ext["new_seeds"][0]) + '\u2013'
        + str(ext["new_seeds"][-1]) + ', 20000 surrogates per seed; '
        'elapsed ' + elapsed_s + ' s; instrument and spectrum sha256 '
        'identical across all new run headers (manifest cross-check); '
        'the S5 array inside the artefact was hard cross-checked '
        'against <code>reports/gw_h1_floor_refine.json</code> (hash '
        'pinned above).</p>'
        + '<p class="scope"><b>Scope (S10 record):</b> the extension is '
        'a robustness statement about finite deterministic matrices at '
        'one resolution \u2014 not Montgomery\u2019s result, not '
        'evidence for RH, never \u201cphysical\u201d. The '
        'pre-registration ordered the draws after the commit '
        '(anti-cocoklogi); logs are append-only; nothing sealed was '
        'modified.</p>')
    return body


def build_res4_panel(res4: dict) -> str:
    r = res4["r"]
    metrics = [("verdict", r["verdict"]), ("n_pos", str(r["n_pos"])),
               ("n_neg", str(r["n_neg"])),
               ("undetermined pivot", str(r["undetermined_pivot"])),
               ("pivots recorded", str(r["pivots_recorded"])),
               ("entries finite", str(r["entries_finite"]).lower()),
               ("build_s", "%.2f" % r["build_s"]),
               ("ldlt_s", "%.2f" % r["ldlt_s"]),
               ("total_s", "%.2f" % r["total_s"]),
               ("launcher elapsed_s", "1791")]
    rows = "".join('<tr><td class="mono">%s</td><td class="mono">%s</td>'
                   '</tr>' % (k, v) for k, v in metrics)
    metrics_table = ('<table class="t"><thead><tr><th>field</th>'
                     '<th>value</th></tr></thead><tbody>%s</tbody>'
                     '</table>' % rows)
    prov_table = _hash_table([
        ("preregistration \u2014 "
         "reports/RESOLUTION4_DIM501_PREREG_2026-10-17.md", RES4_PREREG),
        ("ladder artefact \u2014 "
         "reports/gw_route_s_ladder_c100_n250.json", RES4_JSON),
        ("ladder log \u2014 reports/gw_route_s_ladder_c100_n250.log",
         RES4_LOG),
        ("launcher log \u2014 reports/res4_dim501_launch_2026-10-17.log",
         RES4_LAUNCH),
        ("ladder tool \u2014 msaf/gw_route_s_ladder.py", RES4_TOOL)])
    body = (
        '<p class="lead">The wider-N lever (Section 6.7 item 2) was '
        'executed as the pre-registered fourth resolution point: dim 501 '
        '(Route S ladder, c = 100, N = 250, 6000 bit). The '
        'pre-registration '
        '(<code>reports/RESOLUTION4_DIM501_PREREG_2026-10-17.md</code>) '
        'was pushed with green CI before launch. The ladder printed '
        '<b>UNDETERMINED at pivot 446</b> \u2014 not a positive-definite '
        'certificate. Per pre-registration \u00a74 a non-PD ladder is '
        'the outcome, not an infrastructure failure: it ends the '
        'statistics of this point. Stages C and M were not launched; '
        'there are no S1/S2 numbers for dim 501 and no fourth GW-DELTA '
        'block; no parameter was changed and there was no rerun.</p>'
        + '<div class="chips">'
        + '<span class="chip amber">UNDETERMINED at pivot '
        + str(r["undetermined_pivot"]) + ' \u2014 non-PD outcome</span>'
        + '<span class="chip green">n_pos 446 \u00b7 n_neg 0 \u00b7 '
        'entries finite</span>'
        + '<span class="chip blue">statistics ended per '
        'pre-registration \u00a74 \u2014 no rerun</span>'
        + '</div>'
        '<h3>10.1 ' + MID + ' outcome record \u2014 dim 501, Route S '
        'ladder (c = 100, N = 250, 6000 bit)</h3>'
        + build_res4_svg(res4) + metrics_table
        + '<p class="note"><b>Per pre-registration \u00a74 (verbatim):'
        '</b> \u201cA G-M0 FAIL or a non-PD ladder is NOT an '
        'infrastructure failure: it is the outcome, reported as-is, and '
        'it ends the statistics of this point.\u201d</p>'
        + '<p class="note"><b>What does not exist (because the outcome '
        'ended the point):</b> <code>reports/gw_capture_100_250.log'
        '</code>, <code>reports/gw_spectrum_100_250.json</code>, '
        '<code>reports/mont_run_100_250.txt</code> and the stage-M '
        'stdout/stderr logs were never created. Their absence is part '
        'of the record.</p>'
        + '<p class="note"><b>Launcher wrapper incident (recorded, not '
        'hidden):</b> the PowerShell 5.1 launcher mis-read an empty '
        'ExitCode from <span class="mono">Start-Process</span> + '
        '<span class="mono">WaitForExit()</span> and mis-labelled the '
        'stop as \u201cinfrastructure failure\u201d; the computation '
        'itself finished normally (complete log and JSON, empty '
        'err.log, the tool always exits 0). End state identical; the '
        'launcher log is kept verbatim and never edited; the official '
        'classification is the OUTCOME branch of pre-registration '
        '\u00a74 (dated report '
        '<code>reports/GW_RESOLUTION4_DIM501_2026-10-17.md</code>).</p>'
        + '<h3>10.2 ' + MID + ' provenance</h3>' + prov_table
        + '<p class="scope"><b>Scope (dim-501 outcome):</b> a statement '
        'about one finite 6000-bit matrix \u2014 an interval sign '
        'census of LDL^T pivots: not Montgomery\u2019s theorem, not a '
        'proof of RH, not Weil positivity, not a statement about the '
        'actual spectrum, not prime counting, not factorisation, not a '
        'trend. The verdict is a certificate statement (UNDETERMINED), '
        'not an error: nothing failed.</p>')
    return body


# --------------------------------------------------------------------------
# patch application + render
# --------------------------------------------------------------------------
def apply_patch(base: str, old: str, new: str, label: str,
                applied: list) -> str:
    n = base.count(old)
    if n != 1:
        raise SystemExit("v6 patch %r matched %d times (expected 1)"
                         % (label, n))
    applied.append(label)
    return base.replace(old, new)


def render(ctx4: dict, h1: dict, eb: dict, lad: dict, s10: dict,
           lad321: dict, res4: dict) -> tuple:
    base, _ = v5.render(ctx4, h1, eb, lad)
    applied: list = []
    v5_full = v4.full_hash(V5)
    if v5_full != V5_SHA:
        raise SystemExit("v5 seal drifted: %s" % v5_full)
    v5_short = v5_full[:12]
    v4_short = v4.full_hash(v5.V4)[:12]
    v3_short = ctx4["v3_short"]

    # 1. title / kicker / h1
    base = apply_patch(
        base,
        "<title>Guinand-Weil Resolution-Series Diagnostics \u2014 "
        "Dashboard v5</title>",
        "<title>Guinand-Weil Resolution-Series Diagnostics \u2014 "
        "Dashboard v6</title>", "title", applied)
    base = apply_patch(
        base,
        "H1 floor amendment (A+B) + engine-B verification (C) \u00b7 "
        "c = 100 Montgomery construction \u00b7 2026-10-17</div>",
        "H1 floor amendment (A+B) + engine-B verification (C) + C4 S10 "
        "extension + dim-501 outcome \u00b7 c = 100 Montgomery "
        "construction \u00b7 2026-10-17</div>", "kicker", applied)
    base = apply_patch(base, ">v5</span></h1>", ">v6</span></h1>",
                       "h1 mark", applied)

    # 2. hero sub
    base = apply_patch(
        base, "by <code>msaf/gw_dashboard_v5.py</code>",
        "by <code>msaf/gw_dashboard_v6.py</code>", "sub module", applied)
    base = apply_patch(
        base,
        "English; v5 extends the v4 layout with the H1 floor-amendment "
        "and engine-B verification panels. <b>v4 and v3 are preserved "
        "byte-identical</b> (sha256 in panel 6).",
        "English; v6 extends the v5 layout with the C4 S10 robustness "
        "extension and the dim-501 outcome panel. <b>v5, v4 and v3 are "
        "preserved byte-identical</b> (sha256 in panel 6).",
        "sub preserved", applied)

    # 3. chips
    chip_eb = ('<span class="chip green">engine B: %s \u2014 counts '
               '18/18 exact</span>' % eb["eb"]["verdict"]["overall"])
    chip_s10 = ('<span class="chip amber">C4 S10 (10 seeds): %d/%d = %s '
                '\u00b7 NOT STABLE (\u03c7\u00b2 p = %s)</span>'
                % (s10["ext"]["pooled_k"], s10["ext"]["pooled_n"],
                   f5(s10["ext"]["p_hat"]),
                   f5(s10["ext"]["homogeneity_p"])))
    chip_r4 = ('<span class="chip red">dim 501 (Route S, N=250): '
               'UNDETERMINED at pivot %d \u2014 non-PD outcome; '
               'statistics ended</span>'
               % res4["r"]["undetermined_pivot"])
    base = apply_patch(base, chip_eb, chip_eb + chip_s10 + chip_r4,
                       "chips", applied)

    # 4. toc
    base = apply_patch(
        base, "</nav>",
        '<a href="#s10">Panel 9 \u2014 C4 S10 extension</a>'
        '<a href="#res4">Panel 10 \u2014 dim-501 outcome</a>'
        "</nav>", "toc", applied)

    # 5. panel 1 caption (dim-321 correction)
    base = apply_patch(
        base,
        "dim 321 not yet run (deliberately deferred; see HANDOFF); ",
        "dim 321 was measured on 2026-10-17: lambda_min = "
        + lad321["lam_s"] + " with every one of the 321 enclosures "
        "excluding zero (all_finite; ln-slope " + lad321["slope_s"]
        + " over 257\u2192321; stored in "
        "reports/lambda_min_eig_ladder_dim321.json); ",
        "panel1 caption 321", applied)

    # 6. panel 7 open item (dim-321 measured)
    base = apply_patch(
        base,
        "dim 321 remains not run (deliberately deferred).",
        "dim 321 was measured on 2026-10-17 (lambda_min = "
        + lad321["lam_s"] + "; every one of the 321 enclosures excludes "
        "zero; ln-slope " + lad321["slope_s"] + " over 257\u2192321 "
        "\u2014 still decreasing, no upturn; stored in "
        "reports/lambda_min_eig_ladder_dim321.json).",
        "panel7 open item", applied)

    # 7. panel 6 additions
    base = apply_patch(
        base,
        '<p class="scope"><b>Preserved predecessor (v5):</b>',
        '<p class="scope"><b>Preserved predecessor (v6):</b> '
        'reports/gw_diagnostic_v5.html \u2014 byte-identical, full '
        'sha256 <span class="mono">' + v5_full + '</span> (first 12: '
        + v5_short + ').</p>'
        '<p class="scope"><b>Preserved predecessor (v5):</b>',
        "v5 preserved paragraph", applied)

    v6_changes = (
        '<p class="scope"><b>Changes in v6 relative to v5:</b></p>'
        '<ul class="chg">'
        '<li>New panel 9: C4 robustness array extended S5 \u2192 S10 '
        '(+5 fresh seeds; pooled %d/%d = %s; NOT STABLE persists; the '
        'number of record is unchanged).</li>'
        '<li>New panel 10: fourth resolution point (dim 501) \u2014 '
        'non-PD outcome (UNDETERMINED at pivot %d); the statistics of '
        'the point ended per pre-registration.</li>'
        '<li>Panel 1 caption + panel 7 open item updated: the dim-321 '
        'lambda_min rung was measured 2026-10-17 (v5 said \u201cnot yet '
        'run\u201d / \u201cremains open\u201d); the measured value '
        '(%s, all enclosures excluding zero) is now stated.</li>'
        '<li>Hero chips updated: S10 and dim-501 outcome chips '
        'added.</li>'
        '<li>Scope notes recorded (release t=0; S10; dim 501) \u2014 '
        'see the block below.</li>'
        '<li>v5 preserved byte-identical \u2014 nothing in it was '
        'edited (sha256 above).</li></ul>'
        % (s10["ext"]["pooled_k"], s10["ext"]["pooled_n"],
           f5(s10["ext"]["p_hat"]), res4["r"]["undetermined_pivot"],
           lad321["lam_s"]))
    scope_notes = (
        '<p class="scope"><b>Scope notes recorded in v6 (owner '
        'decision 2026-10-18):</b></p>'
        '<ul class="chg">'
        '<li><b>Release scope note</b> (DBN release barrier '
        'certificates; surfaced by the audit-P1 lane, registry '
        'A-2026-0001): \u201canalytic justification at t=0 remains '
        'external\u201d \u2014 the release\u2019s own binding scope '
        'statement, quoted verbatim.</li>'
        '<li><b>S10 scope note</b> \u2014 panel 9: the extension is a '
        'robustness statement only; the number of record is unchanged; '
        'never Montgomery\u2019s result, never evidence for RH.</li>'
        '<li><b>dim-501 scope note</b> \u2014 panel 10: an interval '
        'sign certificate statement on one finite matrix at one '
        'precision; statistics ended by pre-registration; no rerun; '
        'no trend.</li></ul>')
    base = apply_patch(
        base,
        '<p class="scope"><b>Changes in v5 relative to v4:</b></p>',
        v6_changes + scope_notes
        + '<p class="scope"><b>Changes in v5 relative to v4:</b></p>',
        "v6 changes + scope notes", applied)
    base = apply_patch(
        base, "<code>python msaf/gw_dashboard_v5.py --write</code>",
        "<code>python msaf/gw_dashboard_v6.py --write</code>",
        "regenerate hint", applied)

    # 8. new panels + footer
    if base.count("<footer>") != 1:
        raise SystemExit("v6: footer anchor not found exactly once")
    fi = base.find("<footer>")
    fc = base.find("</footer>", fi)
    if fc == -1:
        raise SystemExit("v6: footer unclosed")
    old_footer = base[fi:fc + len("</footer>")]
    if not old_footer.startswith(
            "<footer>Rendered by msaf/gw_dashboard_v5.py"):
        raise SystemExit("v6: unexpected footer content")
    new_footer = (
        '<footer>Rendered by msaf/gw_dashboard_v6.py \u2014 '
        'byte-stable \u00b7 no JavaScript \u00b7 no external resources. '
        'v5 preserved byte-identical (' + v5_short + '); v4 preserved '
        'byte-identical (' + v4_short + '); v3 preserved '
        'byte-identical (' + v3_short + ').</footer>')
    new_panels = (
        v4.panel("s10", "Panel 9 \u2014 C4 S10 extension: ten-seed "
                 "robustness array", build_s10_panel(s10))
        + v4.panel("res4", "Panel 10 \u2014 Fourth resolution point "
                   "(dim 501): non-PD outcome", build_res4_panel(res4))
        + new_footer)
    base = base[:fi] + new_panels + base[fc + len("</footer>"):]
    applied.append("new panels + footer")
    return base, applied


def collect_all() -> tuple:
    ctx4, h1, eb, lad = v5.collect_all()
    return (ctx4, h1, eb, lad, collect_s10(), collect_ladder321(),
            collect_res4())


def build() -> str:
    ctx4, h1, eb, lad, s10, lad321, res4 = collect_all()
    html, _applied = render(ctx4, h1, eb, lad, s10, lad321, res4)
    return html


def main(argv: list) -> int:
    write = "--write" in argv
    ctx4, h1, eb, lad, s10, lad321, res4 = collect_all()
    html, applied = render(ctx4, h1, eb, lad, s10, lad321, res4)

    print("v6 dashboard source check:")
    print("  S10: %d seeds; pooled %d/%d = %s; homogeneity p = %s -> %s"
          % (len(s10["ext"]["seeds"]), s10["ext"]["pooled_k"],
             s10["ext"]["pooled_n"], f5(s10["ext"]["p_hat"]),
             f5(s10["ext"]["homogeneity_p"]),
             s10["ext"]["classification"].split(" (")[0]))
    print("  dim-321 rung: %s (eig %.2f s; ln-slope %s)"
          % (lad321["lam_s"], lad321["eig_s"], lad321["slope_s"]))
    print("  res4: %s; n_pos %d n_neg %d; total %.2f s"
          % (res4["r"]["verdict"], res4["r"]["n_pos"],
             res4["r"]["n_neg"], res4["r"]["total_s"]))
    print("  patches applied: %d" % len(applied))
    print("  v5 seal: %s (preserved, untouched)" % v4.full_hash(V5))
    print("  html size: %.1f KB" % (len(html.encode("utf-8")) / 1024.0))

    if not write:
        print("DRY RUN -- rerun with --write to write %s" % OUT)
        return 0
    OUT.write_bytes(html.encode("utf-8"))
    print("written: %s (%d bytes)" % (OUT, OUT.stat().st_size))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))


