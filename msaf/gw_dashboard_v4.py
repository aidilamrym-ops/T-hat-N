# -*- coding: utf-8 -*-
"""Static diagnostics dashboard v4 (English) -- Guinand-Weil resolution series.

WHAT THIS DOES
--------------
English, derivations-complete rebuild of the sealed v3 layout
(reports/gw_diagnostic_v3.html -- preserved byte-identical, never written
by this script). Reads the same machine artefacts as v3 (nothing retyped
by hand):

  reports/lambda_min_eig_ladder.json  lambda_min eig ladder, c=13, 6000 bit
  reports/gw_route_s_ladder_c100.json Route S ladder c=100 (N=100, N=150)
  msaf/mont_run.txt                   dim 401 baseline measurement (UTF-16)
  reports/mont_run_100_100.txt        dim 201 measurement
  reports/mont_run_100_150.txt        dim 301 measurement (third resolution)
  reports/gw_capture_100_100.log      dim 201 capture, G-M0 evaluation
  reports/gw_capture_100_150.log      dim 301 capture, G-M0 evaluation
  reports/gw_spectrum_100_100.json    certified dim-201 spectrum
  reports/gw_spectrum_100_150.json    certified dim-301 spectrum

and writes a single self-contained HTML file:

  reports/gw_diagnostic_v4.html

Design rules (operational spec, 2026-10-16; carried over from v3):
  * no external dependencies: inline CSS only, raw SVG only, NO scripts
    at all -- offline and byte-replayable;
  * every number extracted at generation time; a missing file or pattern
    aborts with SystemExit (fail-loud, nothing guessed);
  * byte-stable: no timestamps, no randomness; reruns are identical,
    and provenance hashes are taken over newline-normalised bytes
    (CRLF -> LF) so the rendered table is identical on every checkout;
  * honesty guards: the c=13 damping ladder and the c=100 Montgomery
    resolution series are drawn as SEPARATE, clearly labelled series --
    across-c is not apples-to-apples and the two are never merged; the
    c=13 plateau is marked UNCONFIRMED (dim 257/321 not yet measured);
    raw chi2 is annotated as NOT comparable across N (pair counts scale
    as N^2); the matched-N Monte-Carlo p-values are the statistic.

v4 additions over v3:
  * English throughout; professional restyle;
  * definitions & derivations panel: the exact S1/S2 formulas, the
    pre-registered verdict rules, and the refuted constant-B decay model;
  * pipeline panel: the measurement chain from certified capture to the
    two statistics;
  * measured matched-N reference table (GUE/GOE/Poisson mean+-sd, sample
    counts, seed, GOE-vs-GUE separation yardstick, resolution ceiling);
  * honesty fix: the GUE band drawn in panel 3 is mean +- 1 sd (visual
    guide only); v4 states the measured SD distances and the LOGGED
    verdicts separately instead of equating the band with the verdict.

usage:
    python msaf/gw_dashboard_v4.py           # dry run: prints data tables
    python msaf/gw_dashboard_v4.py --write   # writes the HTML
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
LADDER_C100 = ROOT / "reports" / "gw_route_s_ladder_c100.json"
LOG401 = gwd.LOG401
LOG201 = gwd.LOG201
LOG301 = gwd.LOG301
CAPTURE201 = gwd.CAPTURE
CAPTURE301 = gwd.CAPTURE301
SPEC201 = ROOT / "reports" / "gw_spectrum_100_100.json"
SPEC301 = ROOT / "reports" / "gw_spectrum_100_150.json"
V3 = ROOT / "reports" / "gw_diagnostic_v3.html"
OUT = ROOT / "reports" / "gw_diagnostic_v4.html"

DIMS = (201, 301, 401)

C13 = "#2563eb"      # damping ladder (c=13) -- solid blue
MODEL = "#dc2626"    # refuted exponential model -- dashed red
C100 = "#0d9488"     # Montgomery series (c=100) -- teal
RT = "#2563eb"       # S1 chart T -- blue
RL = "#d97706"       # S1 chart L -- amber
GOE = "#64748b"      # GOE reference -- slate dashed
POIS = "#be5b5b"     # Poisson reference -- rose dashed
GRID = "#e4e9f2"
MUTED = "#64748b"
FONT = ("font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,"
        "'Noto Sans',sans-serif")
RB = "r\u0304"       # r-bar (r + combining macron)

CSS = """
:root{color-scheme:light}
*{box-sizing:border-box}
body{background:#eef1f6;color:#1c2433;font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,'Noto Sans',sans-serif;margin:0;padding:26px 18px 34px;line-height:1.55}
.wrap{max-width:1180px;margin:0 auto}
code,.mono{font-family:ui-monospace,Consolas,'Cascadia Mono',monospace}
code{font-size:12px;background:#f1f4f9;border:1px solid #e2e8f0;border-radius:5px;padding:1px 5px}
.hero{background:linear-gradient(135deg,#0f172a 0%,#1e293b 60%,#243b5e 100%);color:#e8eef9;border-radius:16px;padding:28px 30px 24px;margin:0 0 16px;box-shadow:0 2px 10px rgba(15,23,42,.18)}
.hero .kicker{font-size:11.5px;letter-spacing:1.6px;text-transform:uppercase;color:#8fa3c8;margin:0 0 10px}
.hero h1{font-size:25px;margin:0 0 10px;font-weight:650;letter-spacing:.2px}
.hero .sub{color:#b9c6de;font-size:13.5px;margin:0;max-width:1000px}
.hero .sub code{background:#1c2b45;border-color:#2c4166;color:#cfe0ff}
.chips{margin-top:16px;display:flex;flex-wrap:wrap;gap:8px}
.chip{font-size:12px;padding:5px 11px;border-radius:999px;border:1px solid transparent;white-space:nowrap}
.chip.red{background:#31131a;color:#ffa8a8;border-color:#6b2530}
.chip.amber{background:#332711;color:#ffd28a;border-color:#6b4d1a}
.chip.green{background:#10281a;color:#90e2ab;border-color:#205434}
.chip.blue{background:#122340;color:#a8c8ff;border-color:#2a4a7d}
.toc{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:12.5px;color:#5b6b85;margin:2px 0 18px}
.toc a{color:#2f5bd7;text-decoration:none}
.toc a:hover{text-decoration:underline}
.panel{background:#ffffff;border:1px solid #d9e0ec;border-radius:14px;padding:22px 24px 18px;margin:0 0 18px;box-shadow:0 1px 3px rgba(15,23,42,.05)}
.panel h2{font-size:17px;margin:0 0 8px;color:#0f172a;font-weight:650}
.panel h3{font-size:14px;margin:18px 0 6px;color:#22304a}
.panel .lead{color:#5b6b85;font-size:13px;margin:0 0 12px}
.note{color:#5b6b85;font-size:12.5px;margin:12px 0 0}
table.t{width:100%;border-collapse:collapse;font-size:12.5px}
table.t th,table.t td{border-bottom:1px solid #e7ecf4;padding:7px 9px;text-align:left;vertical-align:top}
table.t th{color:#5b6b85;font-weight:600;background:#f7fafd}
table.t td.mono,table.t .mono{font-family:ui-monospace,Consolas,'Cascadia Mono',monospace;font-size:11.5px;word-break:break-all}
table.heat{border-collapse:collapse;width:100%;font-size:12.5px}
table.heat th,table.heat td{border:1px solid #ffffff;padding:9px 7px;text-align:center;vertical-align:middle}
th.rh{background:#eef1f7;text-align:left;width:210px}
th.rh .dim{font-weight:700;font-size:13.5px;color:#0f172a}
th.rh .sub{color:#5b6b85;font-size:11px;font-weight:400;margin-top:3px}
.ch{background:#e7ecf4;font-weight:600;padding:8px 5px;font-size:12px;color:#22304a}
.chi{font-weight:700;font-size:14px;font-family:ui-monospace,Consolas,monospace}
.pv{font-size:11px;margin-top:3px;opacity:.92}
.legend{display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin:10px 0 0;font-size:12px;color:#556}
.sw{height:14px;display:inline-block;border:1px solid #d9e0ec}
.verdict{border-radius:10px;padding:12px 15px;font-size:13px;margin-top:12px}
.verdict.warn{background:#fff8ec;border:1px solid #f0c479}
.verdict b{color:#7c2d12}
ul.fin{font-size:13px;margin:10px 0 0;padding-left:18px}
ul.fin li{margin:3px 0}
.eq{font-family:'Cambria Math',Cambria,Georgia,'Times New Roman',serif;font-size:16.5px;text-align:center;margin:12px 0;padding:12px 96px 12px 14px;background:#f8fafd;border:1px solid #e7ecf4;border-radius:10px;position:relative;color:#101828}
.eq .tag{position:absolute;right:14px;top:50%;transform:translateY(-50%);font-size:12px;color:#8a94a8;font-family:ui-monospace,Consolas,monospace}
.eq i{font-family:Georgia,'Times New Roman',serif}
.frac{display:inline-block;vertical-align:-0.55em;text-align:center;margin:0 3px}
.frac .num{display:block;padding:0 5px 1px;border-bottom:1.2px solid #2a3345}
.frac .den{display:block;padding:1px 5px 0}
.rules{font-size:13px;margin:8px 0 0;padding-left:18px}
.rules li{margin:4px 0}
.eqnote{font-size:12px;color:#5b6b85;text-align:center;margin:-4px 0 12px}
table.hash{border-collapse:collapse;font-size:12px;width:100%}
table.hash td{border-bottom:1px solid #eef1f7;padding:5px 8px}
td.hp{color:#33415c;font-family:ui-monospace,Consolas,monospace}
td.hh{color:#5b6b85;font-family:ui-monospace,Consolas,monospace;text-align:right}
.scope{font-size:12.5px;color:#5b6b85;margin-top:12px;line-height:1.65}
.scope b{color:#33415c}
ul.chg{font-size:12.5px;color:#33415c;margin:10px 0 0;padding-left:18px}
ul.chg li{margin:3px 0}
footer{color:#8a94a8;font-size:12px;margin:4px 0 26px;text-align:center}
@media (max-width:820px){table.heat .pv{display:none}}
"""


def esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def stable_bytes(path: Path) -> bytes:
    """File bytes with CRLF normalised to LF (checkout-stable hashing).

    core.autocrlf checkouts differ between Windows and Linux; the
    provenance table must not. UTF-16 line endings (0D 00 0A 00) do not
    contain the byte pair 0D 0A, so this is a no-op for the UTF-16 logs.
    """
    return path.read_bytes().replace(b"\r\n", b"\n")


def short_hash(path: Path) -> str:
    return hashlib.sha256(stable_bytes(path)).hexdigest()[:12]


def full_hash(path: Path) -> str:
    return hashlib.sha256(stable_bytes(path)).hexdigest()


def minus(s) -> str:
    """ASCII hyphen -> typographic minus (display only)."""
    return str(s).replace("-", "\u2212")


def arrowed(s) -> str:
    return str(s).replace("->", "\u2192")


def extra_refs(text: str, label: str) -> dict:
    """v3-compatible reference parsing plus the v4 additions."""
    out = {}
    for kind in ("goe", "poisson"):
        m = re.search(r"^\s*" + kind + r"\s+mean ([\d.]+)\s+sd ([\d.]+)",
                      text, re.M)
        if not m:
            raise SystemExit("parse failure: %s %s reference line not found"
                             % (label, kind))
        out[kind] = (m.group(1), m.group(2))
    for key, pat, grp in (
        ("gate", r"G-M0 gate\s*:\s*([^\n]+)", 1),
        ("eig_s", r"eig time\s*:\s*([\d.]+) s", 1),
        ("samples",
         r"surrogate samples per ensemble = (\d+)\s+seed = (\d+)", 1),
        ("seed",
         r"surrogate samples per ensemble = (\d+)\s+seed = (\d+)", 2),
        ("goe_gue",
         r"GOE-vs-GUE separation needs \|Delta r_bar\| ~ ([\d.]+) against "
         r"SE ~ ([\d.]+)", 1),
        ("goe_gue_se",
         r"GOE-vs-GUE separation needs \|Delta r_bar\| ~ ([\d.]+) against "
         r"SE ~ ([\d.]+)", 2),
        ("rT_verdict",
         r"S1 chart T \(ln lambda, PRIMARY\)\s+r_bar = ([\d.]+)\s*->\s*"
         r"([^\n]+)", 2),
        ("rL_verdict",
         r"S1 chart L \(lambda, SECONDARY\)\s+r_bar = ([\d.]+)\s*->\s*"
         r"([^\n]+)", 2),
        ("ceiling", r"RESOLUTION CEILING:\s*([^\n]+)", 1),
    ):
        m = re.search(pat, text)
        if not m:
            raise SystemExit("parse failure: %s line for %r not found"
                             % (label, key))
        out[key] = m.group(grp).strip()
    m = re.search(r"TOOL STATUS:\s*([^\n]+)\n\s*([^\n]+)", text)
    if not m:
        raise SystemExit("parse failure: %s TOOL STATUS block not found"
                         % label)
    out["tools"] = m.group(1).strip() + " " + m.group(2).strip()
    return out


def heat_color(t: float) -> str:
    """Light cream -> deep red ramp (same family as v3)."""
    r = round(255 + (107 - 255) * t)
    g = round(244 + (18 - 244) * t)
    b = round(236 + (32 - 236) * t)
    return "#%02x%02x%02x" % (r, g, b)


def ladder_run(lad: dict, n_block: int) -> dict:
    for r in lad["runs"]:
        if r.get("N") == n_block:
            return r
    raise SystemExit("ladder JSON has no run with N=%d" % n_block)


# --------------------------------------------------------------------------
# data collection (fail-loud; nothing guessed)
# --------------------------------------------------------------------------
def collect() -> dict:
    ctx: dict = {}

    lad = json.loads(gwd.read_text(LADDER_LMIN))
    c13 = []
    for r in lad["runs"]:
        if "CERTIFIED" not in r["verdict"]:
            raise SystemExit("lambda_min ladder run dim %d is not CERTIFIED"
                             % r["dim"])
        c13.append((r["dim"], r["lambda_min_mid"], r["lambda_min_rad"]))
    if len(c13) < 4:
        raise SystemExit("lambda_min ladder has fewer than 4 certified runs")
    ctx["c13"] = c13

    logs = {}
    for path, dimv in ((LOG401, 401), (LOG201, 201), (LOG301, 301)):
        text = gwd.read_text(path)
        d = gwd.parse_measurement_log(text, "dim-%d" % dimv)
        d.update(extra_refs(text, "dim-%d" % dimv))
        # integrity cross-check: the chart-verdict lines must quote the
        # same r_bar values as the measurement blocks (fail-loud)
        m = re.search(r"S1 chart T \(ln lambda, PRIMARY\)\s+r_bar = "
                      r"([\d.]+)", text)
        if not m or m.group(1) != d["rT"]:
            raise SystemExit("dim-%d: chart-T verdict line r_bar mismatch"
                             % dimv)
        m = re.search(r"S1 chart L \(lambda, SECONDARY\)\s+r_bar = "
                      r"([\d.]+)", text)
        if not m or m.group(1) != d["rL"]:
            raise SystemExit("dim-%d: chart-L verdict line r_bar mismatch"
                             % dimv)
        logs[dimv] = d
    ctx["logs"] = logs

    ss = {(logs[d]["samples"], logs[d]["seed"]) for d in DIMS}
    if len(ss) != 1:
        raise SystemExit("samples/seed differ across canonical logs: %r" % ss)
    ctx["samples"], ctx["seed"] = ss.pop()

    lad100 = json.loads(gwd.read_text(LADDER_C100))
    run100 = ladder_run(lad100, 100)
    run150 = ladder_run(lad100, 150)
    for run, tag in ((run100, "N=100"), (run150, "N=150")):
        if "CERTIFIED" not in run["verdict"]:
            raise SystemExit("c=100 ladder %s run is not CERTIFIED" % tag)
        if not (run["n_pos"] == run["dim"] and run["n_neg"] == 0):
            raise SystemExit("c=100 ladder %s inertia is not fully positive"
                             % tag)
    ctx["run100"], ctx["run150"] = run100, run150

    for path in (CAPTURE201, CAPTURE301, SPEC201, SPEC301):
        if not path.exists():
            raise SystemExit("required artefact missing: %s" % path)
        if path.suffix == ".log" and ">>> G-M0 PASS <<<" not in \
                gwd.read_text(path):
            raise SystemExit("%s does not show G-M0 PASS" % path.name)
    ctx["cap201"] = gwd.parse_capture(gwd.read_text(CAPTURE201),
                                      "capture-201")
    ctx["cap301"] = gwd.parse_capture(gwd.read_text(CAPTURE301),
                                      "capture-301")

    ctx["c100"] = [(d, logs[d]["lambda_min"], logs[d]["prov"]) for d in DIMS]
    ctx["dims"] = list(DIMS)

    for d in DIMS:
        vals = [logs[d]["lambda_min"], logs[d]["lambda_max"],
                logs[d]["rT"], logs[d]["rL"], logs[d]["gue_mean"],
                logs[d]["gue_sd"], logs[d]["goe"][0], logs[d]["poisson"][0]]
        for cell in logs[d]["s2"].values():
            vals += [cell["chi2"], cell["pGUE"], cell["pPois"]]
        for v in vals:
            if not math.isfinite(float(v)):
                raise SystemExit("non-finite value in dim-%d log: %r"
                                 % (d, v))

    ctx["badge"] = ("dim 301 (c = 100): CERTIFIED \u2014 ladder n+ = %d / "
                    "n\u2212 = %d; %s; eig %s s"
                    % (run150["n_pos"], run150["n_neg"],
                       logs[301]["gate"], logs[301]["eig_s"]))

    hashes = [("lambda_min_eig_ladder.json", short_hash(LADDER_LMIN)),
              ("gw_route_s_ladder_c100.json", short_hash(LADDER_C100))]
    for path in (LOG401, LOG201, LOG301):
        hashes.append((path.name, short_hash(path)))
    hashes += [("gw_capture_100_100.log", short_hash(CAPTURE201)),
               ("gw_capture_100_150.log", short_hash(CAPTURE301)),
               ("gw_spectrum_100_100.json", short_hash(SPEC201)),
               ("gw_spectrum_100_150.json", short_hash(SPEC301))]
    ctx["hashes"] = hashes
    if not V3.exists():
        raise SystemExit("v3 layout missing: %s" % V3)
    ctx["v3_short"] = short_hash(V3)
    ctx["v3_full"] = full_hash(V3)

    lnv = [math.log(v) for _, v, _ in c13]
    slopes = [(lnv[i + 1] - lnv[i]) / (c13[i + 1][0] - c13[i][0])
              for i in range(len(c13) - 1)]
    ctx["slopes"] = " \u2192 ".join("%.2f" % s for s in slopes)
    ctx["sd"] = {d: (float(logs[d]["rT"]) - float(logs[d]["gue_mean"]))
                 / float(logs[d]["gue_sd"]) for d in DIMS}
    floor = [logs[d]["s2"][(c, s)]["pGUE"] for d in DIMS
             for c in ("T", "L") for s in gwd.SIGMAS]
    ctx["n_floor"] = sum(1 for v in floor if v == "0.0000")
    ctx["n_cells"] = len(floor)
    ctx["pg_max"] = max(float(v) for v in floor)
    ctx["finals"] = {d: {"s1": logs[d]["s1_final"],
                         "s2": logs[d]["s2_final"]} for d in DIMS}
    return ctx


# --------------------------------------------------------------------------
# SVG builders
# --------------------------------------------------------------------------
def build_lmin_svg(c13: list, c100: list, badge: str, slopes: str) -> str:
    W, H = 1060, 486
    PX0, PX1 = 96, 1024
    PY0, PY1 = 416, 62
    XMAX = 410.0
    vals = ([math.log10(v) for _, v, _ in c13]
            + [math.log10(float(f)) for _, f, _ in c100])
    ytop = 0.0
    ybot = math.floor((min(vals) - 12.0) / 50.0) * 50.0

    def px(dim: float) -> float:
        return PX0 + (PX1 - PX0) * dim / XMAX

    def py(v: float) -> float:
        return PY1 + (ytop - v) * (PY0 - PY1) / (ytop - ybot)

    L = []
    add = L.append
    add('<svg viewBox="0 0 %d %d" width="100%%" role="img" '
        'aria-label="lambda_min ladder chart">' % (W, H))
    add('<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>'
        % (W, H))
    add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" '
        'fill="#fbfdff" stroke="#dbe3ee"/>'
        % (PX0, PY1, PX1 - PX0, PY0 - PY1))
    v = ybot
    while v <= ytop + 0.1:
        y = py(v)
        add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>'
            % (PX0, y, PX1, y, GRID))
        add('<text x="%.1f" y="%.1f" font-size="11.5" fill="%s" '
            'text-anchor="end" style="%s">1e%d</text>'
            % (PX0 - 10, y + 4, MUTED, FONT, int(v)))
        v += 50
    for d in (17, 33, 65, 129, 201, 301, 401):
        x = px(d)
        add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>'
            % (x, PY1, x, PY0, GRID))
        add('<text x="%.1f" y="%.1f" font-size="11.5" fill="%s" '
            'text-anchor="middle" style="%s">%d</text>'
            % (x, PY0 + 20, MUTED, FONT, d))
    add('<text x="%.1f" y="%.1f" font-size="12" fill="#475569" '
        'text-anchor="middle" style="%s">dimension (dim = 2N + 1)</text>'
        % ((PX0 + PX1) / 2, PY0 + 42, FONT))
    add('<text x="30" y="%.1f" font-size="12" fill="#475569" '
        'text-anchor="middle" style="%s" '
        'transform="rotate(-90 30 %.1f)">lambda_min (log scale)</text>'
        % ((PY0 + PY1) / 2, FONT, (PY0 + PY1) / 2))

    (d1, v1, _), (d2, v2, _) = c13[0], c13[1]
    a1, a2 = math.log10(v1), math.log10(v2)
    slope = (a2 - a1) / (d2 - d1)
    dend = 17.0 + (ybot - a1) / slope
    dend = min(max(dend, 17.0), XMAX)
    add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
        'stroke-width="2" stroke-dasharray="7,5"><title>constant-B model '
        'A*exp(-B*dim) through the first two c=13 points -- refuted by '
        'points 3-4</title></line>'
        % (px(17), py(a1), px(dend), py(ybot), MODEL))

    pts13 = [(px(d), py(math.log10(v))) for d, v, _ in c13]
    add('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
        % (" ".join("%.1f,%.1f" % p for p in pts13), C13))
    for (d, v, rad), (x, y) in zip(c13, pts13):
        add('<circle cx="%.1f" cy="%.1f" r="5" fill="%s" stroke="#ffffff" '
            'stroke-width="1.5"><title>c = 13 &#183; dim %d: lambda_min = '
            '%s (enclosure radius = %s)</title></circle>'
            % (x, y, C13, d, v, rad))
    pts100 = [(px(d), py(math.log10(float(f)))) for d, f, _ in c100]
    add('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
        % (" ".join("%.1f,%.1f" % p for p in pts100), C100))
    for (d, f, _s), (x, y) in zip(c100, pts100):
        add('<rect x="%.1f" y="%.1f" width="9" height="9" fill="%s" '
            'stroke="#ffffff" stroke-width="1.5" '
            'transform="rotate(45 %.1f %.1f)"><title>c = 100 &#183; dim %d: '
            'lambda_min = %s (measured)</title></rect>'
            % (x - 4.5, y - 4.5, C100, x, y, d, f))

    # c=13 info card (bottom-left; empty region, model line never passes)
    cx, cy, cw, ch = 100.0, 288.0, 404.0, 112.0
    add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="9" '
        'fill="#ffffff" fill-opacity="0.94" stroke="#dbe3ee"/>'
        % (cx, cy, cw, ch))
    add('<text x="%.1f" y="%.1f" font-size="12.5" font-weight="600" '
        'fill="%s" style="%s">c = 13 damping ladder</text>'
        % (cx + 14, cy + 22, C13, FONT))
    add('<text x="%.1f" y="%.1f" font-size="12" fill="#334155" style="%s">'
        '%.1e \u2192 %.1e over dim %d\u2192%d</text>'
        % (cx + 14, cy + 40, FONT, c13[0][1], c13[-1][1],
           c13[0][0], c13[-1][0]))
    add('<text x="%.1f" y="%.1f" font-size="12" fill="%s" style="%s">'
        'ln-slopes %s \u2014 constant-B form refuted</text>'
        % (cx + 14, cy + 58, MODEL, FONT, minus(slopes)))
    add('<text x="%.1f" y="%.1f" font-size="12" fill="%s" style="%s">'
        'plateau UNCONFIRMED \u2014 dim 257/321 not yet measured</text>'
        % (cx + 14, cy + 76, MUTED, FONT))
    add('<text x="%.1f" y="%.1f" font-size="12" fill="%s" style="%s">'
        'c-slices drawn separately, never merged (across-c)</text>'
        % (cx + 14, cy + 94, MUTED, FONT))

    mid = c100[1]
    add('<text x="%.1f" y="%.1f" font-size="12.5" fill="%s" style="%s">'
        'c = 100 Montgomery series (measured)</text>'
        % (px(mid[0]) - 140, py(math.log10(float(mid[1]))) - 18, C100, FONT))

    # legend (top-right, inside the plot)
    lx, ly = PX1 - 262, PY1 + 14
    add('<rect x="%.1f" y="%.1f" width="252" height="76" rx="8" '
        'fill="#ffffff" fill-opacity="0.92" stroke="#dbe3ee"/>'
        % (lx - 12, ly - 8))
    add('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s"/>'
        % (lx + 4, ly + 6, C13))
    add('<text x="%.1f" y="%.1f" font-size="11.5" fill="#334155" '
        'style="%s">c = 13 damping ladder</text>'
        % (lx + 16, ly + 10, FONT))
    add('<rect x="%.1f" y="%.1f" width="9" height="9" fill="%s" '
        'transform="rotate(45 %.1f %.1f)"/>'
        % (lx, ly + 16, C100, lx + 4.5, ly + 20.5))
    add('<text x="%.1f" y="%.1f" font-size="11.5" fill="#334155" '
        'style="%s">c = 100 Montgomery series</text>'
        % (lx + 16, ly + 28, FONT))
    add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
        'stroke-width="2" stroke-dasharray="6,4"/>'
        % (lx - 2, ly + 38, lx + 14, ly + 38, MODEL))
    add('<text x="%.1f" y="%.1f" font-size="11.5" fill="#334155" '
        'style="%s">constant-B model (refuted)</text>'
        % (lx + 16, ly + 42, FONT))
    add('<text x="%.1f" y="%.1f" font-size="11" fill="%s" style="%s">'
        'log10 axis \u00b7 points carry native tooltips</text>'
        % (lx + 4, ly + 60, MUTED, FONT))

    bw = 30 + len(badge) * 6.8
    bx = PX1 - bw
    add('<rect x="%.1f" y="8" width="%.1f" height="36" rx="9" '
        'fill="#eaf7ef" stroke="#2f9e5f"/>' % (bx, bw))
    add('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" '
        'stroke="#2f9e5f" stroke-width="3"/>'
        % (bx + 16, 26, bx + 25, 35, bx + 41, 17))
    add('<text x="%.1f" y="%.1f" font-size="12.5" fill="#1c7a46" '
        'style="%s">%s</text>' % (bx + 50, 31, FONT, esc(badge)))
    add('</svg>')
    return "\n".join(L)


def build_rbar_svg(dims: list, logs: dict, sd: dict) -> str:
    W, H = 1060, 372
    PX0, PX1 = 96, 1024
    PY0, PY1 = 300, 66
    xs = {d: PX0 + (PX1 - PX0) * (i + 0.5) / len(dims)
          for i, d in enumerate(dims)}
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
    add('<svg viewBox="0 0 %d %d" width="100%%" role="img" '
        'aria-label="S1 gap-ratio gradient chart">' % (W, H))
    add('<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>'
        % (W, H))
    add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" '
        'fill="#fbfdff" stroke="#dbe3ee"/>'
        % (PX0, PY1, PX1 - PX0, PY0 - PY1))
    v = lo
    while v <= hi + 1e-9:
        y = py(v)
        add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>'
            % (PX0, y, PX1, y, GRID))
        add('<text x="%.1f" y="%.1f" font-size="11.5" fill="%s" '
            'text-anchor="end" style="%s">%.1f</text>'
            % (PX0 - 10, y + 4, MUTED, FONT, v))
        v = round(v + 0.1, 10)
    for d in dims:
        x = xs[d]
        add('<text x="%.1f" y="%.1f" font-size="13" fill="#334155" '
            'text-anchor="middle" style="%s">dim %d</text>'
            % (x, PY0 + 26, FONT, d))
        f = F[d]
        g = logs[d]
        y1, y2 = py(f["gm"] + f["gs"]), py(f["gm"] - f["gs"])
        add('<rect x="%.1f" y="%.1f" width="128" height="%.1f" '
            'fill="#bfdbfe" opacity="0.5"><title>GUE matched-N band: '
            '%s \u00b1 %s (mean \u00b1 1 sd)</title></rect>'
            % (x - 64, y1, y2 - y1, g["gue_mean"], g["gue_sd"]))
        for val, color, kind in ((f["goe"], GOE, "GOE"),
                                 (f["pois"], POIS, "Poisson")):
            add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                'stroke="%s" stroke-width="2" stroke-dasharray="4,4">'
                '<title>%s matched-N mean %.6f</title></line>'
                % (x - 64, py(val), x + 64, py(val), color, kind, val))
    pts_t = [(xs[d], py(F[d]["rT"])) for d in dims]
    pts_l = [(xs[d], py(F[d]["rL"])) for d in dims]
    add('<polyline points="%s" fill="none" stroke="%s" '
        'stroke-width="2.5"/>'
        % (" ".join("%.1f,%.1f" % p for p in pts_t), RT))
    for d, (x, y) in zip(dims, pts_t):
        add('<circle cx="%.1f" cy="%.1f" r="6" fill="%s" '
            'stroke="#ffffff" stroke-width="1.5"><title>%s T dim %d = %s '
            '(logged: %s)</title></circle>'
            % (x, y, RT, RB, d, logs[d]["rT"],
               esc(logs[d]["rT_verdict"])))
        add('<text x="%.1f" y="%.1f" font-size="11.5" fill="%s" '
            'text-anchor="middle" style="%s">%s (%s SD)</text>'
            % (x, y - 12, RT, FONT, logs[d]["rT"],
               minus("%+.2f" % sd[d])))
    add('<polyline points="%s" fill="none" stroke="%s" '
        'stroke-width="2.5"/>'
        % (" ".join("%.1f,%.1f" % p for p in pts_l), RL))
    for d, (x, y) in zip(dims, pts_l):
        add('<circle cx="%.1f" cy="%.1f" r="6" fill="%s" '
            'stroke="#ffffff" stroke-width="1.5"><title>%s L dim %d = %s '
            '(logged: %s)</title></circle>'
            % (x, y, RL, RB, d, logs[d]["rL"],
               esc(logs[d]["rL_verdict"])))
        add('<text x="%.1f" y="%.1f" font-size="11.5" fill="%s" '
            'text-anchor="middle" style="%s">%s</text>'
            % (x, y + 22, RL, FONT, logs[d]["rL"]))
    add('<rect x="%.1f" y="%.1f" width="16" height="11" '
        'fill="#bfdbfe" opacity="0.8"/>' % (PX0 + 8, 16))
    add('<text x="%.1f" y="%.1f" font-size="12.5" fill="#334155" '
        'style="%s">GUE matched-N band (\u00b11 sd, visual guide) &#160;'
        '\u00b7&#160; <tspan fill="%s" font-weight="bold">%s T '
        '(PRIMARY)</tspan> &#160;\u00b7&#160; <tspan fill="%s" '
        'font-weight="bold">%s L (SECONDARY)</tspan> &#160;\u00b7&#160; '
        '<tspan fill="%s">GOE mean</tspan>&#160;\u00b7&#160; '
        '<tspan fill="%s">Poisson mean</tspan></text>'
        % (PX0 + 30, 26, FONT, RT, RB, RL, RB, GOE, POIS))
    add('</svg>')
    return "\n".join(L)


def build_flow_svg(samples: str, seed: str) -> str:
    W, H = 1100, 412
    L = []
    add = L.append
    add('<svg viewBox="0 0 %d %d" width="100%%" role="img" '
        'aria-label="measurement pipeline">' % (W, H))
    add('<defs><marker id="arw" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M 0 1 L 9 5 L 0 9 z" fill="#94a3b8"/></marker></defs>')

    def stage(y: float, text: str) -> None:
        add('<text x="16" y="%.1f" font-size="11" fill="#8a94a8" '
            'letter-spacing="1.4" style="%s">%s</text>'
            % (y, FONT, text))

    def box(x: float, y: float, w: float, h: float, title: str,
            lines: list) -> None:
        add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="9" '
            'fill="#f8fafd" stroke="#c9d4e4"/>' % (x, y, w, h))
        add('<text x="%.1f" y="%.1f" font-size="13" font-weight="600" '
            'fill="#101828" style="%s">%s</text>'
            % (x + 14, y + 24, FONT, title))
        ty = y + 43
        for ln in lines:
            add('<text x="%.1f" y="%.1f" font-size="11.5" fill="#475569" '
                'style="%s">%s</text>' % (x + 14, ty, FONT, ln))
            ty += 16

    def harrow(x1: float, y: float, x2: float) -> None:
        add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
            'stroke="#94a3b8" stroke-width="1.6" '
            'marker-end="url(#arw)"/>' % (x1, y, x2, y))

    stage(20, "STAGE 1 \u00b7 CERTIFIED SPECTRA")
    box(20, 30, 320, 88, "Certified capture (interval arithmetic)",
        ["arb / vdhoeven_mourrain eigensolver",
         "no decimal serialisation in the chain",
         "G-M0 gate: PASS (all runs)"])
    harrow(344, 74, 376)
    box(380, 30, 330, 88, "Certified spectra",
        ["dim 201 \u00b7 dim 301 \u00b7 dim 401 (c = 100)",
         "ladder inertias fully positive",
         "(N = 100 and N = 150, 6000-bit)"])
    harrow(714, 74, 746)
    box(750, 30, 330, 88, "Two monotone charts",
        ["T: x = ln \u03bb (primary)",
         "L: x = \u03bb (secondary)",
         "\u2014 both always reported"])

    stage(150, "STAGE 2 \u00b7 S1 \u2014 MEAN ADJACENT GAP RATIO "
               "(UNFOLDING-FREE)")
    box(20, 160, 320, 72, "Gaps & ratios",
        ["adjacent gaps \u2192 ratio r = min/max",
         "mean over all ratios: %s (unfolding-free)" % RB])
    harrow(344, 196, 376)
    box(380, 160, 330, 72, "S1 verdict per chart",
        ["pre-registered membership rules",
         "chart disagreement \u2192 CHART-DEPENDENT"])
    harrow(714, 196, 746)
    box(750, 160, 330, 72, "S1 FINAL (as logged)",
        ["INCONCLUSIVE \u2014 the flattering chart",
         "is never chosen"])

    stage(266, "STAGE 3 \u00b7 S2 \u2014 PAIR CORRELATION VS THE "
               "MONTGOMERY KERNEL")
    box(20, 276, 320, 88, "Unfolding",
        ["Gaussian-kernel smoothing of the counting",
         "function (adaptive bandwidth; \u00b110 neighbours)",
         "rescaled: mean gap \u2192 exactly 1"])
    harrow(344, 320, 376)
    box(380, 276, 330, 88, "Estimator & statistic",
        ["estimator R\u2082 (\u03c3 = 0.5 fixed; u \u2208 [0,10), "
         "20 bins)",
         "observed \u03c7\u00b2: bins E \u2265 5, GUE-variance weights",
         "raw \u03c7\u00b2 is not cross-N comparable "
         "(pairs \u221d N\u00b2/2)"])
    harrow(714, 320, 746)
    box(750, 276, 330, 88, "Matched-N references \u2192 p-values",
        ["GUE / GOE / Poisson \u00b7 %s draws each \u00b7 seed %s"
         % (samples, seed),
         "GUE upper tail \u00b7 Poisson lower tail (#1001631)",
         "never memorised constants \u2014 simulations at matched N"])
    add('</svg>')
    return "\n".join(L)


# --------------------------------------------------------------------------
# HTML panel builders
# --------------------------------------------------------------------------
def eq(tag: str, inner: str) -> str:
    return ('<div class="eq">' + inner
            + '<span class="tag">(%s)</span></div>' % tag)


def panel(pid: str, title: str, body: str) -> str:
    return ('<section class="panel" id="%s"><h2>%s</h2>%s</section>'
            % (pid, title, body))


def build_math_panel(logs: dict, dims: list, samples: str, seed: str,
                     slopes: str) -> str:
    frac = ('<span class="frac"><span class="num">%s</span>'
            '<span class="den">%s</span></span>')

    e1 = eq("1",
            '<i>s</i><sub><i>i</i></sub> = '
            '<i>x</i><sub><i>i</i>+1</sub> \u2212 '
            '<i>x</i><sub><i>i</i></sub>, &nbsp;&nbsp; '
            '<i>r</i><sub><i>i</i></sub> = '
            + frac % ("min(<i>s</i><sub><i>i</i></sub>, "
                      "<i>s</i><sub><i>i</i>+1</sub>)",
                      "max(<i>s</i><sub><i>i</i></sub>, "
                      "<i>s</i><sub><i>i</i>+1</sub>)")
            + ', &nbsp;&nbsp; ' + RB + ' = mean<sub><i>i</i></sub> '
            '<i>r</i><sub><i>i</i></sub>')
    e2 = eq("2",
            '<i>T</i>: <i>x</i><sub><i>i</i></sub> = ln '
            '<i>\u03bb</i><sub><i>i</i></sub> (primary) '
            '&nbsp;\u00b7&nbsp; <i>L</i>: <i>x</i><sub><i>i</i></sub> = '
            '<i>\u03bb</i><sub><i>i</i></sub> (secondary)')
    e3 = eq("3",
            '<i>R</i><sub>2</sub>(<i>u</i>) = 1 \u2212 ('
            + frac % ("sin(\u03c0<i>u</i>)", "\u03c0<i>u</i>")
            + ')<sup>2</sup>, &nbsp;&nbsp; <i>R</i><sub>2</sub>(0) = 0')
    e4 = eq("4",
            '<i>x</i><sub><i>k</i></sub> = \u03a3<sub><i>m</i></sub> '
            '\u03a6( '
            + frac % ("<i>y</i><sub><i>k</i></sub> \u2212 "
                      "<i>y</i><sub><i>m</i></sub>",
                      "<i>\u03c3</i><sub><i>u</i></sub> "
                      "<i>h</i><sub><i>m</i></sub>")
            + ' )')
    e5 = eq("5",
            '<i>R</i><sub>2</sub><sup>est</sup>(<i>u</i>) = '
            + frac % ("1", "<i>D</i>")
            + ' \u03a3<sub><i>i</i>\u2260<i>j</i></sub> '
            'Gauss<sub><i>\u03c3</i><sub>e</sub></sub>('
            '<i>u</i> \u2212 (<i>x</i><sub><i>i</i></sub> \u2212 '
            '<i>x</i><sub><i>j</i></sub>))')
    e6 = eq("6",
            '\u03c7\u00b2<sub>obs</sub> = \u03a3<sub>bins '
            '<i>E</i> \u2265 5</sub> '
            + frac % ("(<i>c</i><sub><i>b</i></sub> \u2212 "
                      "<i>T</i><sub><i>\u03c3</i>e</sub>"
                      "(<i>u</i><sub><i>b</i></sub>))\u00b2",
                      "Var<sub>GUE</sub>(<i>b</i>)")
            + ' &nbsp;&nbsp; <i>p</i><sub>GUE</sub> = '
            'P[\u03c7\u00b2<sub>GUE</sub> \u2265 '
            '\u03c7\u00b2<sub>obs</sub>] &nbsp;&nbsp; '
            '<i>p</i><sub>Pois</sub> = P[\u03c7\u00b2<sub>Pois</sub> '
            '\u2264 \u03c7\u00b2<sub>obs</sub>]')
    e7 = eq("7",
            '<i>\u03bb</i><sub>min</sub>(<i>n</i>) \u2248 <i>A</i> '
            'e<sup>\u2212<i>B n</i></sup> &nbsp;&nbsp;'
            '(constant-<i>B</i> exponential form)')

    rules_s1 = (
        "<li>inside the Poisson reference only \u2192 "
        "<b>CONSISTENT WITH POISSON</b></li>"
        "<li>inside the RMT reference only \u2192 "
        "<b>CONSISTENT WITH RMT</b></li>"
        "<li>inside both \u2192 <b>NO DISCRIMINATION</b></li>"
        "<li>inside neither \u2192 <b>INCONSISTENT WITH ALL THREE "
        "REFERENCES</b></li>"
        "<li>the two charts disagree \u2192 <b>CHART-DEPENDENT</b>, "
        "hence <b>INCONCLUSIVE</b></li>")
    rules_s2 = (
        "<li><i>p</i><sub>GUE</sub> \u2265 0.05 and "
        "<i>p</i><sub>Pois</sub> &lt; 0.05 \u2192 "
        "<b>CONSISTENT WITH MONTGOMERY/GUE</b>, distinguishable from "
        "Poisson</li>"
        "<li>both \u2265 0.05 \u2192 <b>NO DISCRIMINATION</b></li>"
        "<li><i>p</i><sub>GUE</sub> &lt; 0.05 \u2192 "
        "<b>INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION</b></li>"
        "<li>the verdict must hold on <b>all 6 grid points</b>, "
        "otherwise <b>UNSTABLE</b>, hence INCONCLUSIVE \u2014 the "
        "instability is reported and the favourable cell is never "
        "picked</li>")

    ref_rows = (
        ("levels (n)", [str(logs[d]["n"]) for d in dims]),
        ("ratios (n_ratios)", [str(logs[d]["rT_n"]) for d in dims]),
        ("GUE matched-N (mean \u00b1 sd)",
         ["%s \u00b1 %s" % (logs[d]["gue_mean"], logs[d]["gue_sd"])
          for d in dims]),
        ("GOE matched-N (mean \u00b1 sd)",
         ["%s \u00b1 %s" % (logs[d]["goe"][0], logs[d]["goe"][1])
          for d in dims]),
        ("Poisson matched-N (mean \u00b1 sd)",
         ["%s \u00b1 %s" % (logs[d]["poisson"][0], logs[d]["poisson"][1])
          for d in dims]),
        ("GOE-vs-GUE separation yardstick (|Delta r_bar| / SE)",
         ["%s / %s" % (logs[d]["goe_gue"], logs[d]["goe_gue_se"])
          for d in dims]),
        ("resolution ceiling (as printed in the log)",
         [esc(logs[d]["ceiling"]) for d in dims]),
    )
    ref_html = ('<table class="t"><thead><tr><th>Quantity</th>'
                + "".join("<th>dim %d</th>" % d for d in dims)
                + "</tr></thead><tbody>")
    for name, cells in ref_rows:
        ref_html += ("<tr><th>%s</th>" % name
                     + "".join('<td class="mono">%s</td>' % c
                               for c in cells) + "</tr>")
    ref_html += "</tbody></table>"

    body = (
        '<p class="lead">The exact definitions behind panels 1\u20133, as '
        'implemented by the canonical instrument and pre-registered '
        'before execution. Nothing on this dashboard changes these '
        'rules.</p>'
        '<h3>4.1 \u00b7 S1 \u2014 mean adjacent gap ratio '
        '(unfolding-free)</h3>'
        '<p>For levels <i>x</i><sub>1</sub> &lt; \u22ef &lt; '
        '<i>x</i><sub><i>D</i></sub>:</p>' + e1
        + '<p>Charts:</p>' + e2
        + '<p>The statistic is applied to both charts unconditionally; '
        'the flattering chart is never chosen afterwards. Chart L is '
        'non-uniform across tens\u2013hundreds of orders in \u03bb; the '
        'preregistration explains its role as the secondary reading.</p>'
        '<h3>4.2 \u00b7 S2 \u2014 pair correlation versus the Montgomery '
        'kernel</h3>'
        + e3
        + '<p>Target kernel (<i>u</i> = unfolded separation); '
        '<i>R</i><sub>2</sub>(0) = 0 (level repulsion).</p>'
        + e4
        + '<p>Unfolding: Gaussian-kernel smoothing of the counting '
        'function with adaptive bandwidth \u03c3<sub><i>u</i></sub> '
        'times the local mean spacing <i>h</i><sub><i>m</i></sub> '
        '(from \u00b110 neighbours), then rescaled so the mean gap is '
        'exactly 1.</p>'
        + e5
        + '<p>Estimator, compared against the target pushed through the '
        'estimator\u2019s own smoothing (the apples-to-apples fix; no '
        'threshold was moved). Grid: \u03c3<sub><i>u</i></sub> \u2208 '
        '{0.3, 0.5, 1.0} \u00d7 {T, L}; \u03c3<sub>e</sub> = 0.5 '
        'fixed; <i>u</i> \u2208 [0, 10) in 20 bins of width 0.5; bin '
        'weight = 1 / (matched-N GUE per-bin variance); bins with '
        'expected pair count below 5 are dropped and reported.</p>'
        + e6
        + '<p>Statistic and p-values. Poisson is tested on the lower '
        'tail (pre-registration #1001631, registered before any real '
        'spectrum was read; the S1/S2 rules are pre-registration '
        '#1001630).</p>'
        '<h3>4.3 \u00b7 Verdict rules (pre-registered)</h3>'
        '<p><b>S1:</b></p><ul class="rules">' + rules_s1 + '</ul>'
        '<p><b>S2:</b></p><ul class="rules">' + rules_s2 + '</ul>'
        '<p>References are matched-N simulations (GUE / GOE / Poisson, '
        + samples + ' samples each, seed ' + seed + '), never memorised '
        'constants. The same rules and the same seed are used in every '
        'run behind this dashboard.</p>'
        '<h3>4.4 \u00b7 The lambda_min decay model, tested and '
        'refuted</h3>'
        + e7
        + '<p class="eqnote">constant-<i>B</i> exponential form fitted '
        'through the first two c = 13 points; refuted by points '
        '3\u20134 \u2014 measured ln-slopes ' + minus(slopes)
        + '. The c = 13 plateau is UNCONFIRMED (dim 257/321 not yet '
        'measured).</p>'
        '<h3>4.5 \u00b7 Measured matched-N reference data '
        '(machine-extracted)</h3>'
        + ref_html
        + '<p class="note">Sources: the three canonical measurement '
        'logs. The GOE-vs-GUE separation entry is the S1 rule\u2019s '
        'own printed yardstick (|Delta r_bar| needed vs the standard '
        'error). Raw \u03c7\u00b2 is not cross-N comparable by '
        'construction; the comparable statistic is the matched-N '
        'Monte-Carlo p-value.</p>')
    return body


def render(ctx: dict) -> str:
    c13, c100, logs, dims = (ctx["c13"], ctx["c100"], ctx["logs"],
                             ctx["dims"])
    samples, seed = ctx["samples"], ctx["seed"]

    s1_set = sorted({ctx["finals"][d]["s1"] for d in dims})
    s2_set = sorted({ctx["finals"][d]["s2"] for d in dims})
    s1_chip = (arrowed(s1_set[0]) if len(s1_set) == 1
               else " \u00b7 ".join(arrowed(s) for s in s1_set))
    s2_chip = (arrowed(s2_set[0]) if len(s2_set) == 1
               else " \u00b7 ".join(arrowed(s) for s in s2_set))

    chips = (
        '<span class="chip red">S1 FINAL: ' + esc(s1_chip) + '</span>'
        '<span class="chip red">S2 FINAL: ' + esc(s2_chip) + '</span>'
        '<span class="chip amber">floor census: %d/%d cells at '
        'p_GUE = 0.0000 \u00b7 grid max %.4f</span>'
        % (ctx["n_floor"], ctx["n_cells"], ctx["pg_max"])
        + '<span class="chip green">dim 301 ladder: '
        + esc(ctx["run150"]["verdict"]) + ' \u2014 n+ = %d / n\u2212 = %d'
        '</span>' % (ctx["run150"]["n_pos"], ctx["run150"]["n_neg"])
        + '<span class="chip blue">lambda_min record: '
        + esc(logs[401]["lambda_min"]) + ' (dim 401)</span>')

    hero = (
        '<header class="hero">'
        '<div class="kicker">Sealed record \u00b7 resolution series '
        'dim 201 / 301 / 401 \u00b7 c = 100 Montgomery construction '
        '\u00b7 2026-10-16</div>'
        '<h1>Guinand-Weil \u2014 Resolution-Series Diagnostics '
        '<span style="font-size:14px;color:#8fa3c8">v4</span></h1>'
        '<p class="sub">Static, self-contained dashboard \u2014 no '
        'JavaScript, no CDN, byte-replayable. Every number is '
        'machine-extracted at generation time from the canonical '
        'artefacts by <code>msaf/gw_dashboard_v4.py</code> (a missing '
        'file or pattern aborts the build \u2014 nothing is guessed). '
        'English, derivations-complete rebuild of the sealed v3 layout; '
        '<b>v3 is preserved byte-identical</b> (sha256 in panel 6).</p>'
        '<div class="chips">' + chips + '</div></header>')

    toc = ('<nav class="toc">'
           '<a href="#summary">Executive summary</a>'
           '<a href="#lmin">Panel 1 \u2014 lambda_min ladder</a>'
           '<a href="#heat">Panel 2 \u2014 \u03c7\u00b2 heatmap</a>'
           '<a href="#rbar">Panel 3 \u2014 ' + RB + ' gradient</a>'
           '<a href="#math">Panel 4 \u2014 definitions &amp; '
           'derivations</a>'
           '<a href="#flow">Panel 5 \u2014 measurement pipeline</a>'
           '<a href="#prov">Panel 6 \u2014 provenance &amp; '
           'limits</a></nav>')

    summary_rows = (
        ("provenance", [logs[d]["prov"] for d in dims]),
        ("lambda_min (float)", [logs[d]["lambda_min"] for d in dims]),
        ("lambda_max", [logs[d]["lambda_max"] for d in dims]),
        ("spread (orders)", [logs[d]["spread"] for d in dims]),
        ("G-M0 gate", [logs[d]["gate"] for d in dims]),
        ("eig time (s)", [logs[d]["eig_s"] for d in dims]),
    )
    summary = ('<table class="t"><thead><tr><th>Quantity</th>'
               + "".join("<th>dim %d</th>" % d for d in dims)
               + "</tr></thead><tbody>")
    for name, cells in summary_rows:
        summary += ("<tr><th>%s</th>" % name
                    + "".join('<td class="mono">%s</td>' % esc(c)
                              for c in cells) + "</tr>")
    summary += "</tbody></table>"
    summary_body = (
        '<p class="lead">This dashboard reports the resolution series '
        'dim 201 / 301 / 401 of the c = 100 Montgomery construction: '
        'the S1 gap-ratio statistic, the S2 pair-correlation statistic '
        'against the Montgomery kernel, and their pre-registered '
        'verdicts. Panels 1\u20133 are the measurements; panel 4 '
        'documents the exact formulas and verdict rules; panel 5 '
        'traces the measurement chain; panel 6 lists provenance and '
        'the literal scope limit. No cell was selected, moved or '
        'averaged.</p>' + summary
        + '<p class="note">All rows machine-extracted from the three '
        'canonical measurement logs; the c = 100 ladder entries '
        '(N = 100, N = 150 \u2014 both CERTIFIED, inertia fully '
        'positive) come from the Route S ladder JSON.</p>')

    panel1_body = (
        build_lmin_svg(c13, c100, ctx["badge"], ctx["slopes"])
        + '<p class="note">Red dashed line: the constant-B exponential '
        'model A\u00b7e<sup>\u2212Bn</sup> fitted through the first two '
        'c = 13 points \u2014 refuted by points 3\u20134 (measured '
        'ln-slopes ' + minus(ctx["slopes"]) + '). Teal diamonds: the '
        'c = 100 Montgomery series (lambda_min per resolution, '
        'measured). The two c-slices are drawn separately and never '
        'merged (across-c is not apples-to-apples); the c = 13 plateau '
        'is UNCONFIRMED \u2014 dim 257/321 not yet measured.</p>')

    heat_cells = {}
    logs10 = []
    for d in dims:
        for chart in ("T", "L"):
            for s in gwd.SIGMAS:
                v = float(logs[d]["s2"][(chart, s)]["chi2"])
                heat_cells[(d, chart, s)] = v
                logs10.append(math.log10(v))
    lo10, hi10 = min(logs10), max(logs10)

    def t_of(v: float) -> float:
        return 0.0 if hi10 == lo10 else (math.log10(v) - lo10) / (hi10 - lo10)

    tags = {201: "", 301: " (new capture)", 401: " (baseline run 2)"}
    rows = ""
    for d in dims:
        g = logs[d]
        rows += ('<tr><th class="rh"><div class="dim">dim %d%s</div>'
                 '<div class="sub">%s \u00b7 eig %s s \u00b7 n = %s</div>'
                 '</th>' % (d, tags[d], esc(g["gate"]), g["eig_s"],
                            g["n"]))
        for chart in ("T", "L"):
            for s in gwd.SIGMAS:
                c = g["s2"][(chart, s)]
                t = t_of(float(c["chi2"]))
                fg = "#ffffff" if t > 0.62 else "#2b2b2b"
                rows += ('<td style="background:%s;color:%s">'
                         '<div class="chi">%s</div>'
                         '<div class="pv">p_GUE %s \u00b7 p_Pois %s</div>'
                         '</td>'
                         % (heat_color(t), fg, esc(c["chi2"]),
                            esc(c["pGUE"]), esc(c["pPois"])))
        rows += "</tr>"
    header_g = "".join('<th class="ch">chart %s \u00b7 sigma_u %s</th>'
                       % (chart, s)
                       for chart in ("T", "L") for s in gwd.SIGMAS)
    grad = "".join('<span class="sw" style="width:34px;background:%s">'
                   '</span>' % heat_color(i / 8.0) for i in range(9))
    cells_per = len(gwd.SIGMAS) * 2
    if ctx["n_floor"] == ctx["n_cells"]:
        floor_note = ("at the " + samples + "-surrogate floor this "
                      "means the observed \u03c7\u00b2 exceeds the "
                      "\u03c7\u00b2 of ALL " + samples + " matched GUE "
                      "realisations at every grid point")
    else:
        floor_note = ("off-floor values remain below the 0.05 "
                      "threshold: rejection is not perfectly uniform, "
                      "but no grid point reaches consistency")
    verdict = ('<b>Artifact verdict:</b> p_GUE = 0.0000 at %d/%d cells '
               '(%d resolutions \u00d7 %d grid points); the grid '
               'maximum is p_GUE = %.4f \u2014 %s. The deviation '
               '<b>does not shrink</b> toward RMT-GUE over dim '
               '201\u2192401. Raw \u03c7\u00b2 is <b>not cross-N '
               'comparable</b> by construction (pair counts '
               '\u221d N\u00b2/2): larger-N rows read larger raw '
               'values because of pair counts, not because the '
               'deviation grows.'
               % (ctx["n_floor"], ctx["n_cells"], len(dims), cells_per,
                  ctx["pg_max"], floor_note))
    finals_html = "".join(
        '<li><b>dim %d</b> \u2014 S1 FINAL: %s; S2 FINAL: %s</li>'
        % (d, esc(ctx["finals"][d]["s1"]),
           esc(ctx["finals"][d]["s2"])) for d in dims)
    panel2_body = (
        '<table class="heat"><thead><tr><th class="rh">Resolution</th>'
        + header_g + '</tr></thead><tbody>' + rows
        + '</tbody></table>'
        '<div class="legend">colour scale \u2014 log10(\u03c7\u00b2) '
        'from ' + ("%.2f" % lo10) + ' (low) ' + grad + ' to '
        + ("%.2f" % hi10) + ' (high)</div>'
        '<div class="verdict warn">' + verdict + '</div>'
        '<ul class="fin">' + finals_html + '</ul>')

    verdict_rows = ""
    for d in dims:
        g = logs[d]
        verdict_rows += (
            '<tr><th>dim %d</th><td class="mono">%s \u2014 %s</td>'
            '<td class="mono">%s \u2014 %s</td>'
            '<td class="mono">%s</td></tr>'
            % (d, esc(g["rT"]), esc(g["rT_verdict"]),
               esc(g["rL"]), esc(g["rL_verdict"]),
               minus("%+.2f" % ctx["sd"][d])))
    panel3_body = (
        build_rbar_svg(dims, logs, ctx["sd"])
        + '<table class="t"><thead><tr><th>Resolution</th>'
        '<th>' + RB + ' T \u2014 logged verdict</th>'
        '<th>' + RB + ' L \u2014 logged verdict</th>'
        '<th>' + RB + ' T distance from GUE mean (ensemble SD)</th>'
        '</tr></thead><tbody>' + verdict_rows + '</tbody></table>'
        '<p class="note">Shaded band: GUE matched-N mean \u00b1 1 sd '
        '\u2014 a visual guide only; the logged verdicts are read from '
        'the pre-registered rules, not from this band. Measured '
        'distances of ' + RB + ' T from the GUE mean: '
        + " / ".join(minus("%+.2f" % ctx["sd"][d]) for d in dims)
        + ' ensemble SD \u2014 reported as-is. Chart T reads '
        'CONSISTENT WITH RMT and chart L reads INCONSISTENT WITH ALL '
        'THREE REFERENCES at all three resolutions (per the canonical '
        'logs); the disagreement keeps S1 FINAL at CHART-DEPENDENT '
        '\u2192 INCONCLUSIVE, and the flattering chart is never '
        'chosen.</p>')

    panel4_body = build_math_panel(logs, dims, samples, seed,
                                   ctx["slopes"])

    panel5_body = (
        build_flow_svg(samples, seed)
        + '<p class="note">How each number on this dashboard is '
        'produced \u2014 from the certified capture to the two '
        'statistics and their verdicts. All rules pre-registered; all '
        'artefacts machine-generated; the same seed is used in every '
        'run.</p>')

    hash_rows = "".join('<tr><td class="hp">%s</td>'
                        '<td class="hh">%s</td></tr>' % (esc(n), h)
                        for n, h in ctx["hashes"])
    panel6_body = (
        '<table class="hash">' + hash_rows + '</table>'
        '<p class="note">Hash convention: sha256 over '
        'newline-normalised bytes (CRLF \u2192 LF), first 12 hex '
        'chars shown \u2014 identical on every checkout (Windows or '
        'Linux).</p>'
        '<p class="scope"><b>Preserved predecessor:</b> '
        'reports/gw_diagnostic_v3.html \u2014 byte-identical, full '
        'sha256 <span class="mono">' + ctx["v3_full"] + '</span> '
        '(first 12: ' + ctx["v3_short"] + ').</p>'
        '<p class="scope"><b>Literal scope limit:</b> these are '
        'statistics of finite constructed matrices. They are NOT '
        'Montgomery\u2019s theorem, NOT evidence for RH, NOT Weil '
        'positivity, NOT prime counting, NOT factorisation. References '
        'are matched-N simulations (never memorised constants). '
        'Rendering is byte-stable: no timestamps, no randomness '
        '\u2014 reruns produce identical bytes. Regenerate with '
        '<code>python msaf/gw_dashboard_v4.py --write</code>.</p>'
        '<p class="scope"><b>Tool status (from the canonical logs):'
        '</b> ' + esc(logs[201]["tools"]) + '</p>'
        '<p class="scope"><b>Changes in v4 relative to v3:</b></p>'
        '<ul class="chg">'
        '<li>English throughout; professional restyle (same canonical '
        'sources, same numbers).</li>'
        '<li>New panel 4: definitions, derivations and the '
        'pre-registered verdict rules.</li>'
        '<li>New panel 5: the measurement pipeline.</li>'
        '<li>New measured reference table: GUE / GOE / Poisson '
        'mean \u00b1 sd, sample counts, seed, GOE-vs-GUE separation '
        'yardstick, resolution ceiling.</li>'
        '<li>Honesty fix: v3\u2019s caption equated the \u00b11 sd '
        'band with the verdict; v4 states the measured SD distances '
        'and the logged verdicts separately (dim 201 T sits at '
        + minus("%+.2f" % ctx["sd"][201]) + ' SD).</li>'
        '<li>v3 layout preserved byte-identical \u2014 nothing in it '
        'was edited.</li></ul>')

    footer = ('<footer>Rendered by msaf/gw_dashboard_v4.py '
              '\u2014 byte-stable \u00b7 no JavaScript \u00b7 no '
              'external resources. v3 preserved byte-identical ('
              + ctx["v3_short"] + ').</footer>')

    html = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n'
            '<meta charset="utf-8"/>\n'
            '<meta name="viewport" content="width=device-width, '
            'initial-scale=1"/>\n'
            '<title>Guinand-Weil Resolution-Series Diagnostics '
            '\u2014 Dashboard v4</title>\n'
            '<style>' + CSS + '</style>\n</head>\n<body><div '
            'class="wrap">'
            + hero + toc
            + panel("summary", "Executive summary", summary_body)
            + panel("lmin", "Panel 1 \u2014 lambda_min ladder: "
                            "damping slice (c = 13) vs the Montgomery "
                            "series (c = 100)", panel1_body)
            + panel("heat", "Panel 2 \u2014 \u03c7\u00b2 deviation "
                            "heatmap (3 resolutions \u00d7 6 grid "
                            "points)", panel2_body)
            + panel("rbar", "Panel 3 \u2014 S1 gap-ratio gradient: "
                            + RB + " (T) and " + RB + " (L) vs "
                            "matched-N references", panel3_body)
            + panel("math", "Panel 4 \u2014 definitions, derivations "
                            "and pre-registered verdict rules",
                    panel4_body)
            + panel("flow", "Panel 5 \u2014 measurement pipeline",
                    panel5_body)
            + panel("prov", "Panel 6 \u2014 provenance &amp; limits",
                    panel6_body)
            + '</div></body></html>\n')
    return html


def main(argv: list) -> int:
    write = "--write" in argv
    ctx = collect()
    html = render(ctx)

    print("v4 dashboard source check (same canonical sources as v3):")
    print("lambda_min c=13 ladder:")
    for d, v, rad in ctx["c13"]:
        print("  dim %3d  %-25s rad=%s" % (d, v, rad))
    print("lambda_min c=100 (Montgomery resolution series):")
    for d, f, _p in ctx["c100"]:
        print("  dim %3d  %s" % (d, f))
    print("S2 chi^2 matrix:")
    for d in ctx["dims"]:
        cells = " | ".join(
            "%s/%s: %s" % (ch, s, ctx["logs"][d]["s2"][(ch, s)]["chi2"])
            for ch in ("T", "L") for s in gwd.SIGMAS)
        print("  dim %3d: %s" % (d, cells))
    print("S1: " + " | ".join(
        "dim %d rT=%s rL=%s" % (d, ctx["logs"][d]["rT"],
                                ctx["logs"][d]["rL"])
        for d in ctx["dims"]))
    tv = sorted({ctx["logs"][d]["rT_verdict"] for d in ctx["dims"]})
    lv = sorted({ctx["logs"][d]["rL_verdict"] for d in ctx["dims"]})
    print("S1 chart verdicts: T = %s ; L = %s" % (" | ".join(tv),
                                                  " | ".join(lv)))
    print("SD distances: " + " | ".join(
        "dim %d %+.2f" % (d, ctx["sd"][d]) for d in ctx["dims"]))
    print("ln-slopes c=13: %s" % ctx["slopes"].replace("\u2192", "->"))
    print("floor census: %d/%d cells at 0.0000; grid max p_GUE = %.4f"
          % (ctx["n_floor"], ctx["n_cells"], ctx["pg_max"]))
    print("samples/seed: %s / %s (identical in all three logs)"
          % (ctx["samples"], ctx["seed"]))
    print("v3 seal: %s (preserved, untouched)" % ctx["v3_full"])
    print("html size: %.1f KB" % (len(html.encode("utf-8")) / 1024.0))

    if not write:
        print("DRY RUN -- rerun with --write to write %s" % OUT)
        return 0
    OUT.write_bytes(html.encode("utf-8"))
    print("written: %s (%d bytes)" % (OUT, OUT.stat().st_size))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))


