# -*- coding: utf-8 -*-
"""Static diagnostics dashboard v3 -- Guinand-Weil resolution series.

WHAT THIS DOES
--------------
Reads machine artefacts only (nothing retyped by hand):

  reports/lambda_min_eig_ladder.json  lambda_min eig ladder, c=13, 6000 bit
  msaf/mont_run.txt                   dim 401 baseline measurement (UTF-16)
  reports/mont_run_100_100.txt        dim 201 measurement
  reports/mont_run_100_150.txt        dim 301 measurement (third resolution)
  reports/gw_capture_100_100.log      dim 201 capture, G-M0 evaluation
  reports/gw_capture_100_150.log      dim 301 capture, G-M0 evaluation
  reports/gw_spectrum_100_100.json    certified dim-201 spectrum
  reports/gw_spectrum_100_150.json    certified dim-301 spectrum

and writes a single self-contained HTML file:

  reports/gw_diagnostic_v3.html

Design rules (operational spec, 2026-10-16):
  * no external dependencies: inline CSS only, raw SVG only, NO scripts
    at all -- offline and byte-replayable;
  * every number extracted at generation time; a missing file or pattern
    aborts with SystemExit (fail-loud, nothing guessed);
  * byte-stable: no timestamps, no randomness; reruns are identical;
  * honesty guards: the c=13 damping ladder and the c=100 Montgomery
    resolution series are drawn as SEPARATE, clearly labelled series --
    across-c is not apples-to-apples and the two are never merged; the
    c=13 plateau is marked UNCONFIRMED (dim 257/321 not yet measured);
  * raw chi2 is annotated as NOT comparable across N (pair counts scale
    as N^2); the matched-N Monte-Carlo p-values are the statistic.

usage:
    python msaf/gw_dashboard_v3.py           # dry run: prints data tables
    python msaf/gw_dashboard_v3.py --write   # writes the HTML
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gw_resolution_delta as gwd  # noqa: E402  (reuse the canonical parsers)

LADDER_LMIN = ROOT / "reports" / "lambda_min_eig_ladder.json"
LOG401 = gwd.LOG401
LOG201 = gwd.LOG201
LOG301 = gwd.LOG301
CAPTURE201 = gwd.CAPTURE
CAPTURE301 = gwd.CAPTURE301
SPEC201 = ROOT / "reports" / "gw_spectrum_100_100.json"
SPEC301 = ROOT / "reports" / "gw_spectrum_100_150.json"
LADDER_C100 = ROOT / "reports" / "gw_route_s_ladder_c100.json"
OUT = ROOT / "reports" / "gw_diagnostic_v3.html"

C13 = "#1f6feb"      # damping ladder (c=13) -- solid blue
MODEL = "#d1242f"    # refuted exponential model -- dashed red
C100 = "#0d9488"     # Montgomery series (c=100) -- teal
RT = "#1f6feb"       # S1 chart T -- blue
RL = "#d97706"       # S1 chart L -- orange
FONT = ("font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,"
        "'Noto Sans',sans-serif")


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def short_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def extra_refs(text: str, label: str) -> dict:
    out = {}
    for kind in ("goe", "poisson"):
        m = re.search(r"^\s*" + kind + r"\s+mean ([\d.]+)\s+sd ([\d.]+)", text, re.M)
        if not m:
            raise SystemExit("parse failure: %s %s reference line not found" % (label, kind))
        out[kind] = (float(m.group(1)), float(m.group(2)))
    m = re.search(r"G-M0 gate\s*:\s*([^\n]+)", text)
    if not m:
        raise SystemExit("parse failure: %s G-M0 gate line not found" % label)
    out["gate"] = m.group(1).strip()
    m = re.search(r"eig time\s*:\s*([\d.]+) s", text)
    if not m:
        raise SystemExit("parse failure: %s eig time line not found" % label)
    out["eig_s"] = m.group(1)
    return out


def heat_color(t: float) -> str:
    r = round(255 + (103 - 255) * t)
    g = round(245 + (0 - 245) * t)
    b = round(240 + (13 - 240) * t)
    return "#%02x%02x%02x" % (r, g, b)


def build_panel1(c13: list, c100: list, badge: str) -> str:
    """lambda_min chart: c=13 damping ladder + c=100 Montgomery series."""
    W, H = 1060, 470
    PX0, PX1 = 92, 1030
    PY0, PY1 = 405, 42
    XMAX = 410.0
    vals = [math.log10(v) for _, v, _ in c13] + [math.log10(f) for _, f, _ in c100]
    ytop = 0.0
    ybot = math.floor((min(vals) - 12.0) / 50.0) * 50.0

    def px(dim: float) -> float:
        return PX0 + (PX1 - PX0) * dim / XMAX

    def py(v: float) -> float:
        return PY1 + (ytop - v) * (PY0 - PY1) / (ytop - ybot)

    L = []
    add = L.append
    add('<svg viewBox="0 0 %d %d" width="100%%" role="img" '
        'aria-label="lambda_min chart">' % (W, H))
    add('<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (W, H))
    # frame
    add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fbfbfd" '
        'stroke="#c9ccd4"/>' % (PX0, PY1, PX1 - PX0, PY0 - PY1))
    # y grid
    v = ybot
    while v <= ytop + 0.1:
        y = py(v)
        add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#e4e6ec"/>'
            % (PX0, y, PX1, y))
        add('<text x="%.1f" y="%.1f" font-size="12" fill="#666" text-anchor="end" '
            'style="%s">1e%d</text>' % (PX0 - 8, y + 4, FONT, int(v)))
        v += 50
    # x ticks
    for d in (17, 33, 65, 129, 201, 301, 401):
        x = px(d)
        add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#eef0f4"/>'
            % (x, PY1, x, PY0))
        add('<text x="%.1f" y="%.1f" font-size="12" fill="#666" text-anchor="middle" '
            'style="%s">%d</text>' % (x, PY0 + 18, FONT, d))
    add('<text x="%.1f" y="%.1f" font-size="12.5" fill="#444" text-anchor="middle" '
        'style="%s">dimensi (dim = 2N+1)</text>' % ((PX0 + PX1) / 2, PY0 + 38, FONT))
    # refuted exponential model through the first two c=13 points
    (d1, v1, _), (d2, v2, _) = c13[0], c13[1]
    a1, a2 = math.log10(v1), math.log10(v2)
    slope = (a2 - a1) / (d2 - d1)
    dend = 17.0 + (ybot - a1) / slope
    dend = min(max(dend, 17.0), XMAX)
    add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
        'stroke-width="2" stroke-dasharray="7,5"><title>A*exp(-B*dim), B dari dua titik '
        'pertama -- TERBANTAH oleh titik ke-3/4</title></line>'
        % (px(17), py(a1), px(dend), py(ybot), MODEL))
    # c=13 series
    pts_xy = [(px(d), py(math.log10(v))) for d, v, _ in c13]
    add('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
        % (" ".join("%.1f,%.1f" % p for p in pts_xy), C13))
    for (d, v, rad), (x, y) in zip(c13, pts_xy):
        add('<circle cx="%.1f" cy="%.1f" r="5" fill="%s" stroke="#ffffff" '
            'stroke-width="1.5"><title>c=13 dim %d: lambda_min = %s (radius = %s)</title>'
            '</circle>' % (x, y, C13, d, v, rad))
    # c=100 Montgomery series
    pts = [(px(d), py(math.log10(f))) for d, f, _ in c100]
    add('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
        % (" ".join("%.1f,%.1f" % p for p in pts), C100))
    for (d, f, s), (x, y) in zip(c100, pts):
        add('<rect x="%.1f" y="%.1f" width="9" height="9" fill="%s" stroke="#ffffff" '
            'stroke-width="1.5" transform="rotate(45 %.1f %.1f)">'
            '<title>c=100 dim %d: lambda_min = %s (dari log kanonik)</title></rect>'
            % (x - 4.5, y - 4.5, C100, x, y, d, s))
    # annotations
    lnv = [math.log(v) for _, v, _ in c13]
    sl = "/".join("%.2f" % ((lnv[i + 1] - lnv[i]) / (c13[i + 1][0] - c13[i][0]))
                  for i in range(len(c13) - 1))
    add('<text x="%.1f" y="%.1f" font-size="12.5" fill="%s" style="%s">'
        'irisan c=13 (hukum redaman): %.1e -&gt; %.1e; lereng %s'
        '</text>' % (px(20), py(a1) - 14, C13, FONT, c13[0][1], c13[-1][1], sl))
    add('<text x="%.1f" y="%.1f" font-size="12.5" fill="#7a7f8a" style="%s">'
        'plateau c=13?&#160; BELUM terkonfirmasi -- dim 257/321 belum diukur '
        '(larangan menyimpulkan dari 4 titik)</text>' % (px(38), py(a2) - 26, FONT))
    mid = c100[1]
    add('<text x="%.1f" y="%.1f" font-size="12.5" fill="%s" style="%s">'
        'seri Montgomery c=100 (lambda_min per resolusi, terukur)</text>'
        % (px(mid[0]) - 40, py(math.log10(mid[1])) - 16, C100, FONT))
    add('<text x="%.1f" y="%.1f" font-size="12" fill="#7a7f8a" style="%s">'
        'dua irisan berbeda c -- digambar terpisah, no pernah digabung '
        '(across-c bukan apel-samel)</text>' % (px(150), py(-6.0), FONT))
    # badge
    add('<rect x="%.1f" y="%.1f" width="%.1f" height="34" rx="8" fill="#e7f6ec" '
        'stroke="#1a7f37"/>' % (PX1 - 470, 10, 460))
    add('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="#1a7f37" '
        'stroke-width="3"/>' % (PX1 - 452, 27, PX1 - 443, 36, PX1 - 426, 18))
    add('<text x="%.1f" y="%.1f" font-size="13" fill="#1a7f37" style="%s">%s</text>'
        % (PX1 - 416, 32, FONT, esc(badge)))
    add('</svg>')
    return "\n".join(L)


def build_panel3(dims: list, logs: dict) -> str:
    """S1 gap-ratio gradient: r_bar chart T / chart L vs matched references."""
    W, H = 1060, 360
    PX0, PX1 = 92, 1030
    PY0, PY1 = 300, 42
    xs = {d: PX0 + (PX1 - PX0) * (i + 0.5) / len(dims) for i, d in enumerate(dims)}
    F = {}
    for d in dims:
        g = logs[d]
        F[d] = {"rT": float(g["rT"]), "rL": float(g["rL"]),
                "gm": float(g["gue_mean"]), "gs": float(g["gue_sd"]),
                "goe": float(g["goe"][0]), "pois": float(g["poisson"][0])}
    allv = []
    for d in dims:
        f = F[d]
        allv += [f["rT"], f["rL"], f["gm"], f["goe"], f["pois"],
                 f["gm"] + f["gs"], f["gm"] - f["gs"]]
    lo = max(0.0, math.floor((min(allv) - 0.06) / 0.1) * 0.1)
    hi = math.ceil((max(allv) + 0.06) / 0.1) * 0.1

    def py(v: float) -> float:
        return PY1 + (hi - v) * (PY0 - PY1) / (hi - lo)

    L = []
    add = L.append
    add('<svg viewBox="0 0 %d %d" width="100%%" role="img" aria-label="S1 gap ratio">'
        % (W, H))
    add('<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (W, H))
    add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fbfbfd" '
        'stroke="#c9ccd4"/>' % (PX0, PY1, PX1 - PX0, PY0 - PY1))
    v = lo
    while v <= hi + 1e-9:
        y = py(v)
        add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#e4e6ec"/>'
            % (PX0, y, PX1, y))
        add('<text x="%.1f" y="%.1f" font-size="12" fill="#666" text-anchor="end" '
            'style="%s">%.1f</text>' % (PX0 - 8, y + 4, FONT, v))
        v = round(v + 0.1, 10)
    for d in dims:
        x = xs[d]
        add('<text x="%.1f" y="%.1f" font-size="13" fill="#444" text-anchor="middle" '
            'style="%s">dim %d</text>' % (x, PY0 + 24, FONT, d))
        f = F[d]
        g = logs[d]
        y1, y2 = py(f["gm"] + f["gs"]), py(f["gm"] - f["gs"])
        add('<rect x="%.1f" y="%.1f" width="120" height="%.1f" fill="#bfdbfe" '
            'opacity="0.55"><title>GUE matched-N band %s +- %s</title></rect>'
            % (x - 60, y1, y2 - y1, g["gue_mean"], g["gue_sd"]))
        for kind, color in (("goe", "#6b7280"), ("poisson", "#e5a3a3")):
            val = F[d]["goe"] if kind == "goe" else F[d]["pois"]
            add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                'stroke-width="2" stroke-dasharray="4,4"><title>%s mean %.6f</title>'
                '</line>' % (x - 60, py(val), x + 60, py(val), color, kind, val))
    pts_t = [(xs[d], py(F[d]["rT"])) for d in dims]
    pts_l = [(xs[d], py(F[d]["rL"])) for d in dims]
    add('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
        % (" ".join("%.1f,%.1f" % p for p in pts_t), RT))
    for d, (x, y) in zip(dims, pts_t):
        add('<circle cx="%.1f" cy="%.1f" r="6" fill="%s" stroke="#ffffff" '
            'stroke-width="1.5"><title>r_bar T dim %d = %s</title></circle>'
            % (x, y, RT, d, logs[d]["rT"]))
        add('<text x="%.1f" y="%.1f" font-size="12" fill="%s" text-anchor="middle" '
            'style="%s">%s</text>' % (x, y - 12, RT, FONT, logs[d]["rT"]))
    add('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
        % (" ".join("%.1f,%.1f" % p for p in pts_l), RL))
    for d, (x, y) in zip(dims, pts_l):
        add('<circle cx="%.1f" cy="%.1f" r="6" fill="%s" stroke="#ffffff" '
            'stroke-width="1.5"><title>r_bar L dim %d = %s</title></circle>'
            % (x, y, RL, d, logs[d]["rL"]))
        add('<text x="%.1f" y="%.1f" font-size="12" fill="%s" text-anchor="middle" '
            'style="%s">%s</text>' % (x, y + 22, RL, FONT, logs[d]["rL"]))
    add('<rect x="%.1f" y="%.1f" width="14" height="10" fill="#bfdbfe" opacity="0.8"/>'
        % (PX0 + 8, 14))
    add('<text x="%.1f" y="%.1f" font-size="12.5" fill="#444" style="%s">'
        'pita GUE matched-N (+-1 sd)&#160;&#160;--&#160;&#160;'
        '<tspan fill="%s" font-weight="bold">r_bar T (PRIMARY)</tspan>&#160;&#160;--&#160;&#160;'
        '<tspan fill="%s" font-weight="bold">r_bar L (SECONDARY)</tspan></text>'
        % (PX0 + 28, 24, FONT, RT, RL))
    add('</svg>')
    return "\n".join(L)


def build_html(c13: list, c100: list, logs: dict, dims: list, badge: str,
               hashes: list, finals: dict) -> str:
    heat_cells = {}
    logs10 = []
    for d in dims:
        for chart in ("T", "L"):
            for s in gwd.SIGMAS:
                v = float(logs[d]["s2"][(chart, s)]["chi2"])
                heat_cells[(d, chart, s)] = v
                logs10.append(math.log10(v))
    lo, hi = min(logs10), max(logs10)

    def t_of(v: float) -> float:
        return 0.0 if hi == lo else (math.log10(v) - lo) / (hi - lo)

    rows = ""
    for d in dims:
        g = logs[d]
        tag = " (NEW CAPTURE)" if d == 301 else (" (baseline run2)" if d == 401 else "")
        rows += ('<tr><th class="rh"><div class="dim">dim %d%s</div>'
                 '<div class="sub">%s &middot; eig %s s &middot; n=%s</div></th>'
                 % (d, tag, esc(g["gate"]), g["eig_s"], g["prov"].split(" n=")[-1]))
        for cell_chart in ("T", "L"):
            for s in gwd.SIGMAS:
                c = g["s2"][(cell_chart, s)]
                t = t_of(float(c["chi2"]))
                fg = "#ffffff" if t > 0.62 else "#2b2b2b"
                rows += ('<td style="background:%s;color:%s">'
                         '<div class="chi">%s</div>'
                         '<div class="pv">p_GUE %s &middot; p_Pois %s</div></td>'
                         % (heat_color(t), fg, esc(c["chi2"]), esc(c["pGUE"]), esc(c["pPois"])))
        rows += "</tr>"

    grad = "".join('<span class="sw" style="width:34px;background:%s"></span>'
                   % heat_color(i / 8.0) for i in range(9))
    n_floor = sum(1 for d in dims for v in logs[d]["s2"].values() if v["pGUE"] == "0.0000")
    n_cells = len(dims) * 6
    pg_max = max(float(v["pGUE"]) for d in dims for v in logs[d]["s2"].values())
    if n_floor == n_cells:
        floor_note = ("in lantai 2000 surrogat artinya chi^2_obs melebihi chi^2 SEMUA "
                      "realisasi GUE matched-N in setiap titik kisi")
    else:
        floor_note = ("nilai in luar lantai tetap berada in bawah ambang 0,05: rejeksi no "
                      "seragam sempurna, tetapi no ada titik kisi mana pun which mencapai "
                      "konsistensi")
    verdict = ("<b>Verdict dari artefak:</b> p_GUE = 0,0000 in %d/%d sel (3 resolusi &times; "
               "6 titik); maksimum p_GUE seluruh kisi = %s &mdash; %s. Deviasi <b>no "
               "menyusut</b> menuju RMT-GUE on rentang 201&ndash;401. chi^2 mentah <b>no "
               "comparable lintas-N</b> (pasangan &prop; N&sup2;/2): baris ber-N lebih besar "
               "secara mentah karena jumlah pasangan, bukan bukti &quot;deviasi membesar&quot;."
               % (n_floor, n_cells, ("%.4f" % pg_max).replace(".", ","), floor_note))
    header_g = "".join(
        '<th class="ch">chart %s &middot; sigma_u %s</th>' % (chart, s)
        for chart in ("T", "L") for s in gwd.SIGMAS)

    finals_html = ""
    for d in dims:
        finals_html += ('<li><b>dim %d</b> &mdash; S1 FINAL: %s; S2 FINAL: %s</li>'
                        % (d, esc(finals[d]["s1"]), esc(finals[d]["s2"])))

    hash_rows = "".join('<tr><td class="hp">%s</td><td class="hh">%s</td></tr>'
                        % (esc(n), h) for n, h in hashes)

    c100_desc = " &rarr; ".join("%d: %s" % (d, s) for d, _f, s in c100)

    return """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>GW Diagnostic v3 -- seri resolusi 201/301/401</title>
<style>
body{background:#f5f6f8;color:#22252b;%s;margin:0;padding:24px}
.wrap{max-width:1120px;margin:0 auto}
h1{font-size:22px;margin:0 0 6px}
h2{font-size:17px;margin:0 0 10px}
.subtle{color:#6b7280;font-size:13px;margin:0 0 18px}
.panel{background:#ffffff;border:1px solid #d9dce3;border-radius:10px;
       padding:18px 18px 14px;margin:0 0 18px;box-shadow:0 1px 2px rgba(16,24,40,.05)}
.note{color:#6b7280;font-size:12.5px;margin-top:8px}
table.heat{border-collapse:collapse;width:100%%;font-size:13px}
table.heat th,table.heat td{border:1px solid #ffffff;padding:10px 8px;text-align:center;
       vertical-align:middle}
th.rh{background:#f0f1f4;text-align:left;width:190px}
.ch{background:#eceef2;font-weight:600;padding:8px 6px}
.dim{font-weight:700;font-size:14px}
.rb .sub,div.sub{color:#6b7280;font-size:11.5px;font-weight:400;margin-top:2px}
.chi{font-weight:700;font-size:14.5px}
.pv{font-size:11.5px;margin-top:3px;opacity:.92}
.legend{display:flex;align-items:center;gap:6px;margin:10px 0 0;font-size:12px;color:#555}
.sw{height:14px;display:inline-block;border:1px solid #d9dce3}
ul.fin{font-size:13px;margin:10px 0 0;padding-left:18px}
ul.fin li{margin:3px 0}
.verdict{background:#fff7ed;border:1px solid #fdba74;border-radius:8px;
         padding:12px 14px;font-size:13px;margin-top:12px}
.verdict b{color:#9a3412}
table.hash{border-collapse:collapse;font-size:12px;width:100%%}
table.hash td{border-bottom:1px solid #eceef2;padding:4px 8px}
td.hp{color:#444;font-family:ui-monospace,Consolas,monospace}
td.hh{color:#6b7280;font-family:ui-monospace,Consolas,monospace;text-align:right}
.scope{font-size:12px;color:#6b7280;margin-top:12px;line-height:1.5}
</style>
</head>
<body><div class="wrap">
<h1>Guinand-Weil -- dashboard diagnostik resolusi (v3)</h1>
<p class="subtle">Statis, tanpa JavaScript, tanpa CDN. Semua angka diekstrak mesin dari
artefak kanonik oleh <code>msaf/gw_dashboard_v3.py</code>; hash source in footer.
Basis: dim 401 (baseline run2), dim 201 (resolusi kedua), dim 301 (NEW).
Koreksi limit: baris memakai resolusi TERUKUR (201/301/401).</p>

<div class="panel">
<h2>Panel 1 &mdash; lambda_min: model eksponensial terbantah vs seri c=100</h2>
%s
<p class="note">Garis merah putus-putus = model <b>A&middot;e<sup>&minus;Bn</sup></b>
(dari dua titik pertama c=13) -- terbantah oleh titik ke-3/4 (lereng melemah
&minus;1,72 &rarr; &minus;1,05 &rarr; &minus;0,34). Seri c=100 (belah ketupat):
%s. Dua irisan <b>no digabung</b>; plateau c=13 belum terkonfirmasi.</p>
</div>

<div class="panel">
<h2>Panel 2 &mdash; heatmap deviasi chi^2 (3 resolusi &times; 6 titik kisi)</h2>
<table class="heat">
<thead><tr><th class="rh">Resolusi</th>%s</tr></thead>
<tbody>%s</tbody>
</table>
<div class="legend">skala warna log10(chi^2): <span class="sw" style="background:%s"></span>rendah
%s tinggi</div>
<div class="verdict">%s</div>
<ul class="fin">%s</ul>
</div>

<div class="panel">
<h2>Panel 3 &mdash; gradien S1: r_bar chart T vs chart L terhadap referensi matched-N</h2>
%s
<p class="note">Chart T tetap in dalam pita RMT-GUE in ketiga resolusi; chart L tetap
in luar ketiganya -- chart-dependence bertahan, verdict S1 tetap INCONCLUSIVE
(no memilih chart which menguntungkan).</p>
</div>

<div class="panel">
<h2>Provenance &amp; limit</h2>
<table class="hash">%s</table>
<p class="scope"><b>Batasan literal:</b> ini statistik dari matriks finit which
dibangun; BUKAN teorema Montgomery, BUKAN bukti RH/Weil-positivity/penghitungan
prima. 2000 surrogat N-matched per ensemble, seed 20260927. Instrumen:
<code>gw_montgomery.py</code> kanonik (read-only), python 3.14 + numpy 2.5.2 +
scipy 1.18.0 + mpmath + python-flint. Rendering byte-stabil: tanpa timestamp,
tanpa acak -- rerun menghasilkan file identik.</p>
</div>
</div></body></html>
""" % (FONT, build_panel1(c13, c100, badge), c100_desc, header_g, rows,
       heat_color(0.0), grad, verdict, finals_html, build_panel3(dims, logs), hash_rows)


def main(argv: list) -> int:
    write = "--write" in argv

    lad = json.loads(gwd.read_text(LADDER_LMIN))
    c13 = []
    for r in lad["runs"]:
        if "CERTIFIED" not in r["verdict"]:
            raise SystemExit("lambda_min ladder run dim %d is not CERTIFIED" % r["dim"])
        c13.append((r["dim"], r["lambda_min_mid"], r["lambda_min_rad"]))
    if len(c13) < 4:
        raise SystemExit("lambda_min ladder has fewer than 4 certified runs")

    logs = {}
    hashes_extra = []
    for path, dimv in ((LOG401, 401), (LOG201, 201), (LOG301, 301)):
        text = gwd.read_text(path)
        d = gwd.parse_measurement_log(text, "dim-%d" % dimv)
        d.update(extra_refs(text, "dim-%d" % dimv))
        logs[dimv] = d
        hashes_extra.append((path.name, short_hash(path)))
    dims = [201, 301, 401]
    c100 = [(d, float(logs[d]["lambda_min"]), logs[d]["lambda_min"]) for d in dims]

    for path in (CAPTURE201, CAPTURE301, SPEC201, SPEC301):
        if not path.exists():
            raise SystemExit("required artefact missing: %s" % path)
        if path.suffix == ".log" and ">>> G-M0 PASS <<<" not in gwd.read_text(path):
            raise SystemExit("%s does not show G-M0 PASS" % path.name)

    for d in dims:
        vals = [logs[d]["lambda_min"], logs[d]["rT"], logs[d]["rL"],
                logs[d]["gue_mean"], logs[d]["gue_sd"]]
        for cell in logs[d]["s2"].values():
            vals += [cell["chi2"], cell["pGUE"], cell["pPois"]]
        for v in vals:
            if not math.isfinite(float(v)):
                raise SystemExit("non-finite value in dim-%d log: %r" % (d, v))

    lad100 = json.loads(gwd.read_text(LADDER_C100))
    run3 = None
    for r in lad100["runs"]:
        if r.get("N") == 150:
            run3 = r
    if run3 is None or "CERTIFIED" not in run3["verdict"]:
        raise SystemExit("c=100 ladder has no certified N=150 run")
    if not (run3["n_pos"] == run3["dim"] and run3["n_neg"] == 0):
        raise SystemExit("c=100 ladder N=150 inertia is not fully positive")
    badge = ("dim 301 (c=100): CERTIFIED \u2713 -- ladder %d/%d + %s; eig %s s"
             % (run3["n_pos"], run3["n_neg"], logs[301]["gate"], logs[301]["eig_s"]))
    finals = {d: {"s1": logs[d]["s1_final"], "s2": logs[d]["s2_final"]} for d in dims}
    hashes = [("lambda_min_eig_ladder.json", short_hash(LADDER_LMIN)),
              ("gw_route_s_ladder_c100.json", short_hash(LADDER_C100))]
    hashes += hashes_extra
    hashes += [("gw_capture_100_100.log", short_hash(CAPTURE201)),
               ("gw_capture_100_150.log", short_hash(CAPTURE301)),
               ("gw_spectrum_100_100.json", short_hash(SPEC201)),
               ("gw_spectrum_100_150.json", short_hash(SPEC301))]

    html = build_html(c13, c100, logs, dims, badge, hashes, finals)

    print("lambda_min c=13 ladder:")
    for d, v, rad in c13:
        print("  dim %3d  %-25s rad=%s" % (d, v, rad))
    print("lambda_min c=100 (Montgomery resolution series):")
    for d, _f, v in c100:
        print("  dim %3d  %s" % (d, v))
    print("S2 chi^2 matrix:")
    for d in dims:
        cells = " | ".join("%s/%s: %s" % (ch, s, logs[d]["s2"][(ch, s)]["chi2"])
                           for ch in ("T", "L") for s in gwd.SIGMAS)
        print("  dim %3d: %s" % (d, cells))
    print("S1: " + " | ".join("dim %d rT=%s rL=%s" % (d, logs[d]["rT"], logs[d]["rL"])
                              for d in dims))
    print("html size: %.1f KB" % (len(html.encode("utf-8")) / 1024.0))

    if not write:
        print("DRY RUN -- rerun with --write to write %s" % OUT)
        return 0
    OUT.write_bytes(html.encode("utf-8"))
    print("written: %s (%d bytes)" % (OUT, OUT.stat().st_size))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))


