# -*- coding: utf-8 -*-
"""README generator: sealed-status block + workflow / verification diagrams.

WHAT THIS DOES
--------------
Regenerates, from the sealed machine artefacts only (no number retyped):

  docs/math/readme_workflow.svg     project overview & measurement workflow
  docs/math/readme_trustchain.svg   the verification chain: why a number
                                    cannot be silently edited
  README.md                         the block between the markers
        <!-- BEGIN GENERATED BLOCK: sealed-status (msaf/gw_readme.py) -->
        ...
        <!-- END GENERATED BLOCK: sealed-status -->

SOURCES (committed, machine-produced)
-------------------------------------
  reports/gw_engine_b_verify.json   independent engine-B re-verification (C)
  reports/gw_engine_b_verify.log    console transcript of the same run
  reports/gw_h1_floor_refine.json   refined 20000-surrogate grid + C4 array
  reports/AMENDMENT_FLOOR_SPEC.md   frozen pre-registration (hash pinned)
  reports/gw_diagnostic_v3.html     sealed dashboard (read-only here)
  reports/gw_diagnostic_v4.html     intermediate rebuild (preserved, pinned)
  reports/gw_diagnostic_v5.html     preserved predecessor (pinned)
  reports/gw_diagnostic_v6.html     current dashboard (hash pinned)
  reports/gw_h1_c4_seeds10.json     C4 S10 robustness extension (section 7)
  msaf/gw_engine_b_verify.py        stage-C harness (hash cross-checked
                                    against its own run manifest)

USAGE
-----
  python msaf/gw_readme.py            dry run: ASCII summary, no writes
  python msaf/gw_readme.py --write    rewrite the SVGs and the README block
  python msaf/gw_readme.py --check    exit 1 on any drift (CI-equivalent)

Provenance hashes are SHA-256 over newline-normalised bytes ("stable_bytes",
same convention as msaf/gw_dashboard_v6.py): identical on Windows and Linux
checkouts with core.autocrlf=true.

GUARD
-----
  msaf/tests/test_readme_guard.py recomputes everything here and fails CI
  on any drift between README.md / the SVGs and the sealed artefacts.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ENGINE_B_JSON = ROOT / "reports" / "gw_engine_b_verify.json"
ENGINE_B_LOG = ROOT / "reports" / "gw_engine_b_verify.log"
REFINE_JSON = ROOT / "reports" / "gw_h1_floor_refine.json"
SPEC_MD = ROOT / "reports" / "AMENDMENT_FLOOR_SPEC.md"
DASH_V3 = ROOT / "reports" / "gw_diagnostic_v3.html"
DASH_V4 = ROOT / "reports" / "gw_diagnostic_v4.html"
DASH_V5 = ROOT / "reports" / "gw_diagnostic_v5.html"
DASH_V6 = ROOT / "reports" / "gw_diagnostic_v6.html"
S10_JSON = ROOT / "reports" / "gw_h1_c4_seeds10.json"
ENGINE_B_SCRIPT = ROOT / "msaf" / "gw_engine_b_verify.py"

README = ROOT / "README.md"
SVG_WORKFLOW = ROOT / "docs" / "math" / "readme_workflow.svg"
SVG_TRUSTCHAIN = ROOT / "docs" / "math" / "readme_trustchain.svg"

BEGIN = "<!-- BEGIN GENERATED BLOCK: sealed-status (msaf/gw_readme.py) -->"
END = "<!-- END GENERATED BLOCK: sealed-status -->"

FONT = ("font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,"
        "sans-serif")


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def stable_bytes(path: Path) -> bytes:
    """File bytes with CRLF normalised to LF (checkout-stable hashing)."""
    return path.read_bytes().replace(b"\r\n", b"\n")


def sha256_stable(path: Path) -> str:
    return hashlib.sha256(stable_bytes(path)).hexdigest()


def esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def e5(x) -> str:
    """5-significant-figure scientific notation (machine formatting)."""
    return "%.5e" % float(x)


def req(d, key, where):
    if key not in d:
        raise SystemExit("%s: missing key %r (present keys: %s)"
                         % (where, key, sorted(d)))
    return d[key]


# --------------------------------------------------------------------------
# data collection (fail-loud on any disagreement between artefacts)
# --------------------------------------------------------------------------
def collect() -> dict:
    ctx: dict = {}

    eb = json.loads(ENGINE_B_JSON.read_text(encoding="utf-8"))
    log = ENGINE_B_LOG.read_text(encoding="utf-8", errors="replace")

    # ---- engine-B verdict: JSON and log must agree ----------------------
    v = eb["verdict"]
    for needle in ("#   B1 parsing      : %s" % v["b1"],
                   "#   B3 gate G-M0    : %s" % v["b3"],
                   "#   B2 observed grid: %s" % v["b2_observed_grid"],
                   "#   counts          : %s" % v["counts"],
                   "#   OVERALL         : %s" % v["overall"]):
        if needle not in log:
            raise SystemExit("engine-B log misses verdict line: %r" % needle)
    if v["cells_fail"] != 0:
        raise SystemExit("engine-B verdict reports failing cells")
    ctx["verdict"] = v

    m = re.search(r"observed grid: (\d+) bins compared; frozen OR "
                  r"(\d+)/(\d+); tighter 10-ulp branch (\d+)/(\d+)", log)
    if not m:
        raise SystemExit("engine-B log: grid summary line not found")
    ctx["grid"] = dict(bins=int(m.group(1)), or_pass=int(m.group(2)),
                       or_total=int(m.group(3)), tight=int(m.group(4)),
                       tight_total=int(m.group(5)))

    m = re.search(r"counts vs engine A: k_GUE (\d+)/(\d+) exact, "
                  r"k_Pois (\d+)/(\d+) exact, all four tails (\d+)/(\d+)",
                  log)
    if not m:
        raise SystemExit("engine-B log: counts summary line not found")
    ctx["counts_line"] = dict(
        gue=int(m.group(1)), gue_n=int(m.group(2)),
        pois=int(m.group(3)), pois_n=int(m.group(4)),
        four=int(m.group(5)), four_n=int(m.group(6)))

    # ---- engine-B counts table (18 cells, B values) ----------------------
    s = eb["counts"]["summary"]
    if not (s["cells"] == 18 and s["exact_k_gue"] == 18
            and s["exact_k_pois"] == 18 and s["exact_all_four"] == 18):
        raise SystemExit("engine-B counts summary is not 18/18/18/18")
    rows = []
    for c in eb["counts"]["cells"]:
        for flag in ("exact_k_gue", "exact_k_gue_lower", "exact_k_pois",
                     "exact_k_pois_upper"):
            if not c[flag]:
                raise SystemExit("engine-B cell %s/%s not exact on %s"
                                 % (c["dim"], c["cell"], flag))
        rows.append((c["dim"], c["chart"], c["sigma_u"], c["k_gue"],
                     c["k_gue_lower"], c["k_pois"], c["k_pois_upper"]))
    if len(rows) != 18:
        raise SystemExit("engine-B counts table is not 18 rows")
    ctx["counts_rows"] = rows

    # ---- enumerated edge cluster: the pre-declared pattern --------------
    lcells = [c for c in eb["b2_observed_grid"] if c["chart"] == "L"]
    others = [c for c in eb["b2_observed_grid"] if c["chart"] != "L"]
    if len(lcells) != 9 or len(others) != 9:
        raise SystemExit("expected 9 chart-L and 9 other grid cells")
    members = []
    worst = 0.0
    for c in lcells:
        if c["cell_status"] != "PASS_ENUMERATED_EDGE_CLUSTER":
            raise SystemExit("chart-L cell not enumerated: %s" % c["dim"])
        if len(c["or_fail_bins_cv"]) != 6 or c["or_fail_bins_tgt"]:
            raise SystemExit("chart-L OR-fail pattern changed (dim %d)"
                             % c["dim"])
        if c["hist_flips"] != 2 or c["flips_via_A_edges"] != 0:
            raise SystemExit("chart-L flip pattern changed (dim %d)"
                             % c["dim"])
        md = c["membership_disagreements"]
        if not md["all_adjacent_within_1e-9"] or md["boundary_skips"]:
            raise SystemExit("chart-L membership pattern changed (dim %d)"
                             % c["dim"])
        members.append(md["count"])
        worst = max(worst, c["max_or_fail_absdiff"])
    for c in others:
        if c["cell_status"] != "PASS":
            raise SystemExit("non-L grid cell not clean: dim %d" % c["dim"])
    ctx["edge"] = dict(members_min=min(members), members_max=max(members),
                       worst_absdiff=worst)

    # ---- engine-B run manifest ------------------------------------------
    man = eb["manifest"]
    declared = req(man, "declared_before_run", "engine-B manifest")
    inst = req(man, "instrument", "engine-B manifest")
    script = req(eb, "script", "engine-B top level")
    if inst["sha256_before"] != inst["sha256_after"]:
        raise SystemExit("interval instrument changed during the run")
    raw = hashlib.sha256(ENGINE_B_SCRIPT.read_bytes()).hexdigest()
    if raw != script["sha256"] \
            and sha256_stable(ENGINE_B_SCRIPT) != script["sha256"]:
        raise SystemExit("msaf/gw_engine_b_verify.py does not match the "
                         "sha256 recorded in its own run manifest "
                         "(module edited after the run?)")
    samples = declared["samples"]
    if not all(samples[d] == 20000 for d in ("201", "301", "401")):
        raise SystemExit("engine-B declared samples are not 20000 per dim")
    ctx["eb"] = dict(
        seed=declared["seed"], dps=declared["mpmath_dps"],
        samples=samples["201"], generated=eb["generated"],
        elapsed_s=eb["elapsed_s"], repo_head=eb["repo_head"],
        mode=eb["mode"], instrument_sha=inst["sha256_before"],
        script_sha=script["sha256"], versions=man["versions"])

    # ---- H1 refined grid + robustness array ------------------------------
    rf = json.loads(REFINE_JSON.read_text(encoding="utf-8"))
    cells = rf["grid"]
    zero = [c for c in cells if c["k_gue"] == 0]
    above = [c for c in cells if c["k_gue"] > 0]
    if len(cells) != 18 or len(above) != 1:
        raise SystemExit("refine grid: expected 18 cells, exactly 1 above "
                         "the k_GUE floor")
    for c in cells:
        if c["verdict_printed"] != c["verdict_recomputed"]:
            raise SystemExit("refine verdict recomputation mismatch at "
                             "dim %d/%s" % (c["dim"], c["chart"]))
    bounds = {c["cp95_gue"][1] for c in zero}
    if len(bounds) != 1:
        raise SystemExit("floor cells disagree on the 95% upper bound")
    ctx["floor"] = dict(n_zero=len(zero), n=zero[0]["n"],
                        bound=sorted(bounds)[0], cell=above[0])

    c4 = rf["c4_array"]
    if not (len(c4["seeds"]) == len(c4["k"]) == len(c4["per_seed_p"]) == 5):
        raise SystemExit("C4 array is not a five-seed array")
    if c4["k"][0] != above[0]["k_gue"]:
        raise SystemExit("C4 canonical k != grid cell k")
    if abs(c4["canonical_chi2"] - above[0]["chi2_obs"]) > 1e-9:
        raise SystemExit("C4 canonical chi2 != grid cell chi2")
    ctx["c4"] = c4

    # ---- C4 S10 extension (ten-seed robustness array) --------------------
    s10 = json.loads(S10_JSON.read_text(encoding="utf-8-sig"))
    sx = s10["extension"]
    if sx["seeds"][:5] != list(c4["seeds"]) or sx["k"][:5] != list(c4["k"]):
        raise SystemExit("S10: sealed S5 base drift")
    if len(sx["seeds"]) != 10 or sx["pooled_k"] != sum(sx["k"]):
        raise SystemExit("S10: extension arrays inconsistent")
    if not sx["classification"].startswith("NOT STABLE"):
        raise SystemExit("S10: classification changed")
    if sx["number_of_record"]["k"] != c4["k"][0]:
        raise SystemExit("S10: number of record != sealed C4 canonical k")
    if s10["manifest"]["prereg_order_check"]["status"] != "PASS":
        raise SystemExit("S10: pre-registration ordering check not PASS")
    ctx["s10"] = sx
    ctx["s10_order"] = s10["manifest"]["prereg_order_check"]["status"]

    rfman = rf["manifest"]
    ctx["rf"] = dict(n_sealed=len(req(rfman, "sealed_logs",
                                      "refine manifest")),
                     n_refined=len(req(rfman, "refined_logs",
                                       "refine manifest")))

    # ---- provenance table -------------------------------------------------
    # Byte counts AND hashes are taken over LF-normalised bytes only: raw
    # st_size() is checkout-dependent (CRLF worktree vs LF on CI) and would
    # make the block non-reproducible -- this exact defect failed CI run
    # 38975016984 on its first appearance.
    prov = [
        ("reports/AMENDMENT_FLOOR_SPEC.md", SPEC_MD,
         "frozen pre-registration (authority)"),
        ("reports/gw_h1_floor_refine.json", REFINE_JSON,
         "stage A + B artefact"),
        ("reports/gw_engine_b_verify.json", ENGINE_B_JSON,
         "stage C artefact"),
        ("reports/gw_engine_b_verify.log", ENGINE_B_LOG,
         "stage C transcript"),
        ("reports/gw_diagnostic_v3.html", DASH_V3,
         "sealed dashboard (read-only)"),
        ("reports/gw_diagnostic_v4.html", DASH_V4,
         "intermediate rebuild (preserved)"),
        ("reports/gw_diagnostic_v5.html", DASH_V5,
         "preserved predecessor (pinned)"),
        ("reports/gw_diagnostic_v6.html", DASH_V6,
         "current dashboard"),
        ("reports/gw_h1_c4_seeds10.json", S10_JSON,
         "C4 S10 extension (robustness)"),
        ("msaf/gw_engine_b_verify.py", ENGINE_B_SCRIPT,
         "stage C harness (frozen)"),
    ]
    prov_rows = []
    for name, path, note in prov:
        st = stable_bytes(path)
        prov_rows.append((name, len(st),
                          hashlib.sha256(st).hexdigest(), note))
    ctx["prov"] = prov_rows

    return ctx


# --------------------------------------------------------------------------
# README block (ASCII markdown; every figure parsed from the artefacts)
# --------------------------------------------------------------------------
def render_block(ctx: dict) -> str:
    v = ctx["verdict"]
    g = ctx["grid"]
    cl = ctx["counts_line"]
    eb = ctx["eb"]
    fl = ctx["floor"]
    c4 = ctx["c4"]
    s10 = ctx["s10"]
    ed = ctx["edge"]
    cell = fl["cell"]
    out: list = []
    add = out.append

    add("_Machine-generated from the sealed artefacts in this repository; "
        "no number below is typed by hand._")
    add("_Rebuild with `python msaf/gw_readme.py --write`; "
        "`msaf/tests/test_readme_guard.py` fails CI on any drift._")
    add("")
    add("**Stage A - refined grid (18 pre-registered cells, %d surrogates "
        "each).**" % eb["samples"])
    add("Dims 201/301/401 x charts T/L x sigma_u 0.3/0.5/1.0, seed %d."
        % eb["seed"])
    add("")
    add("| quantity | value |")
    add("|---|---|")
    add("| cells at the k_GUE floor | %d / %d (k_GUE = 0/%d; one-sided 95%% "
        "upper bound < %s) |" % (fl["n_zero"], len(ctx["counts_rows"]),
                                 fl["n"], e5(fl["bound"])))
    add("| first cell above the floor | dim %d, chart %s, sigma_u %s: "
        "k_GUE = %d/%d = %s (chi2_obs = %s) |"
        % (cell["dim"], cell["chart"], cell["sigma_u"], cell["k_gue"],
           cell["n"], cell["p_gue"], cell["chi2_obs"]))
    add("| at the sealed 2000-surrogate resolution | k_GUE = %d/%d "
        "(re-measured by this grid) |"
        % (cell["sealed_k_gue"], cell["sealed_n"]))
    add("| its recomputed verdict | %s |" % cell["verdict_recomputed"])
    add("| verdict recomputation, all cells | %d / %d printed == recomputed |"
        % (len(ctx["counts_rows"]), len(ctx["counts_rows"])))
    add("")
    add("**Stage B - five-seed robustness array on that cell** "
        "(seeds %s)." % ", ".join(str(x) for x in c4["seeds"]))
    add("")
    add("| seed | k_GUE / %d | p_hat |" % c4["n_per_seed"])
    add("|---|---|---|")
    for seed, k, p in zip(c4["seeds"], c4["k"], c4["per_seed_p"]):
        add("| %d | %d | %s |" % (seed, k, p))
    add("| **pooled** | **%d / %d** | **%s** (95%% CI %s to %s) |"
        % (c4["pooled_k"], c4["pooled_n"], c4["p_hat"],
           e5(c4["pooled_cp95"][0]), e5(c4["pooled_cp95"][1])))
    add("")
    add("Homogeneity across the five seeds: chi2 = %.4f (df %d), p = %s "
        "-> classification: **%s**."
        % (c4["homogeneity_stat"], len(c4["seeds"]) - 1,
           e5(c4["homogeneity_p"]), c4["classification"]))
    add("")
    add("**Stage B extension - C4 S10 (ten-seed robustness array).** The "
        "sealed five-seed array was extended with five fresh seeds under a "
        "pre-registration committed before the first new draw (ordering "
        "check %s)."
        % ctx["s10_order"])
    add("")
    add("| quantity | value |")
    add("|---|---|")
    add("| pooled (10 x %d) | %d / %d = %s (95%% CI %s to %s) |"
        % (s10["n_per_seed"], s10["pooled_k"], s10["pooled_n"],
           e5(s10["p_hat"]), e5(s10["pooled_cp95"][0]),
           e5(s10["pooled_cp95"][1])))
    add("| homogeneity | chi2 = %.4f (df %d), p = %s |"
        % (s10["homogeneity_stat"], s10["homogeneity_df"],
           e5(s10["homogeneity_p"])))
    add("| classification | %s |" % s10["classification"])
    add("| number of record | %d / %d = %s (unchanged; canonical seed %d) |"
        % (s10["number_of_record"]["k"], s10["number_of_record"]["n"],
           s10["number_of_record"]["p"], s10["seeds"][0]))
    add("")
    add("**Stage C - independent engine-B re-verification** (spec Section 5; "
        "decimal-exact parse, mpmath dps %d, seed %d, %d samples per dim; "
        "run %s, %.1f s; artefact written)."
        % (eb["dps"], eb["seed"], eb["samples"], eb["generated"],
           eb["elapsed_s"]))
    add("")
    add("| check | verdict |")
    add("|---|---|")
    add("| B1 - decimal-exact parsing census (dims 201/301/401) | %s |"
        % v["b1"])
    add("| B3 - gate G-M0 re-verification | %s |" % v["b3"])
    add("| B2a - observed grid (%d bins, dps %d vs float64) | %s (frozen OR "
        "%d/%d; tighter 10-ulp branch %d/%d) |"
        % (g["bins"], eb["dps"], v["b2_observed_grid"], g["or_pass"],
           g["or_total"], g["tight"], g["tight_total"]))
    add("| B2b - counts (18 cells x %d samples) | %s |"
        % (eb["samples"], v["counts"]))
    add("| **overall** | **%s** |" % v["overall"])
    add("")
    add("Cell census: %d clean + %d enumerated edge-cluster + %d failing. "
        "Enumeration of the 9 chart-L cells (pre-declared rules, applied "
        "uniformly): 6/20 cv bins outside the frozen OR (0/20 tgt bins); "
        "2 histogram flips across one adjacent edge (0 via-A flips); %d-%d "
        "membership disagreements, all between adjacent bins within 1e-9 "
        "(0 boundary skips); worst |B - A| inside the enumerated bins %s. "
        "The cluster is enumerated bin-by-bin; nothing is excused."
        % (v["cells_pass"], v["cells_pass_enumerated_edge_cluster"],
           v["cells_fail"], ed["members_min"], ed["members_max"],
           e5(ed["worst_absdiff"])))
    add("")
    add("**Engine-B counts vs engine A - the reproduction table.** B values "
        "shown; A equals B in every entry (k_GUE, k_GUE lower tail, k_Pois, "
        "k_Pois upper tail: %d/%d cells, all four tails exact)."
        % (cl["four"], cl["four_n"]))
    add("")
    add("| dim | chart | sigma_u | k_GUE | k_GUE low | k_Pois | k_Pois up |")
    add("|---|---|---|---|---|---|---|")
    for dim, chart, sigma, kg, kl, kp, ku in ctx["counts_rows"]:
        add("| %d | %s | %s | %d | %d | %d | %d |"
            % (dim, chart, sigma, kg, kl, kp, ku))
    add("")
    add("**Sealed artefact provenance** (SHA-256 and byte counts over "
        "LF-normalised bytes - identical on Windows and CI checkouts).")
    add("")
    add("| artefact | bytes | sha256 |")
    add("|---|---|---|")
    for name, size, sha, _note in ctx["prov"]:
        add("| `%s` | %d | `%s` |" % (name, size, sha))
    add("")
    add("**Engine-B run manifest.** mode `%s`; %d samples per dim; seed %d; "
        "mpmath dps %d; generated %s; elapsed %.1f s; repository head `%s`; "
        "interval instrument sha256 before = after = `%s...` (first 16 hex; "
        "full hash in the run manifest); python %s, numpy %s, scipy %s, "
        "mpmath %s."
        % (eb["mode"], eb["samples"], eb["seed"], eb["dps"], eb["generated"],
           eb["elapsed_s"], eb["repo_head"][:7], eb["instrument_sha"][:16],
           eb["versions"]["python"], eb["versions"]["numpy"],
           eb["versions"]["scipy"], eb["versions"]["mpmath"]))
    return "\n".join(out)


def render_segment(ctx: dict) -> str:
    return BEGIN + "\n" + render_block(ctx) + "\n" + END


def block_pattern() -> "re.Pattern[str]":
    return re.compile(re.escape(BEGIN) + r".*?" + re.escape(END),
                      re.DOTALL)


def splice_readme(text: str, segment: str) -> str:
    """Replace the generated segment in README text (LF form)."""
    pat = block_pattern()
    if not pat.search(text):
        raise SystemExit("README.md: generated-block markers not found")
    return pat.sub(lambda _m: segment, text, count=1)


# --------------------------------------------------------------------------
# diagram 1: project overview & measurement workflow
# --------------------------------------------------------------------------
def render_workflow_svg(ctx: dict) -> str:
    W, H = 1100, 530
    eb, g, fl = ctx["eb"], ctx["grid"], ctx["floor"]
    s10, v, ed = ctx["s10"], ctx["verdict"], ctx["edge"]
    cell = fl["cell"]
    n_cells = len(ctx["counts_rows"])
    L: list = []
    add = L.append
    add('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
        'width="100%%" role="img" '
        'aria-label="project overview and measurement workflow">' % (W, H))
    add('<defs><marker id="arw" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M 0 1 L 9 5 L 0 9 z" fill="#94a3b8"/></marker></defs>')

    def stage(y: float, text: str) -> None:
        add('<text x="16" y="%.1f" font-size="11" fill="#8a94a8" '
            'letter-spacing="1.4" style="%s">%s</text>'
            % (y, FONT, esc(text)))

    def box(x: float, y: float, w: float, h: float, title: str,
            lines: list) -> None:
        add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="9" '
            'fill="#f8fafd" stroke="#c9d4e4"/>' % (x, y, w, h))
        add('<text x="%.1f" y="%.1f" font-size="13" font-weight="600" '
            'fill="#101828" style="%s">%s</text>'
            % (x + 14, y + 24, FONT, esc(title)))
        ty = y + 43
        for ln in lines:
            add('<text x="%.1f" y="%.1f" font-size="11.5" fill="#475569" '
                'style="%s">%s</text>' % (x + 14, ty, FONT, esc(ln)))
            ty += 16

    def harrow(x1: float, y: float, x2: float) -> None:
        add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
            'stroke="#94a3b8" stroke-width="1.6" '
            'marker-end="url(#arw)"/>' % (x1, y, x2, y))

    stage(20, "STAGE 1 \u00b7 INSTRUMENT & CAPTURE "
              "(COMPANION CHECKOUT + REPORTS/)")
    box(20, 30, 320, 88, "Interval instrument",
        ["gw_montgomery.py \u00b7 arb / acb \u00b7 6000-bit",
         "no float64 in the numeric path",
         "frozen: sha256 %s\u2026 (before = after)"
         % eb["instrument_sha"][:8]])
    harrow(344, 74, 376)
    box(380, 30, 330, 88, "Certified spectra",
        ["dims 201 / 301 / 401 (c = 100)",
         "G-M0 gate: PASS on every run",
         "sha256 pinned in the run manifest"])
    harrow(714, 74, 746)
    box(750, 30, 330, 88, "Measurement logs",
        ["%d sealed (2000) + %d refined (20000)"
         % (ctx["rf"]["n_sealed"], ctx["rf"]["n_refined"]),
         "machine-written, committed as-is",
         "reports/mont_run_20000_*.txt"])

    stage(150, "STAGE 2 \u00b7 H1 CAMPAIGN \u2014 REFINED GRID (A) + "
               "ROBUSTNESS ARRAY (B)")
    box(20, 160, 320, 88, "Refined grid \u2014 stage A",
        ["%d surrogates per cell \u00b7 %d cells"
         % (eb["samples"], n_cells),
         "seed %d \u00b7 printed == recomputed" % eb["seed"],
         "%d/%d cells at the k_GUE floor"
         % (fl["n_zero"], n_cells)])
    harrow(344, 204, 376)
    box(380, 160, 330, 88, "Robustness array \u2014 stage B",
        ["10 seeds (S5 + S10) on the off-floor cell",
         "pooled %d/%d \u2014 %s"
         % (s10["pooled_k"], s10["pooled_n"],
            s10["classification"].split(" (")[0]),
         "homogeneity p = %s (rejected)" % e5(s10["homogeneity_p"])])
    harrow(714, 204, 746)
    box(750, 160, 330, 88, "Sealed verdicts",
        ["single off-floor cell: %d/%d"
         % (cell["k_gue"], cell["n"]),
         "verdicts recomputed from the logs",
         "spec frozen before the run"])

    stage(280, "STAGE 3 \u00b7 INDEPENDENT RE-VERIFICATION (C) \u2014 "
               "ENGINE B")
    box(20, 290, 320, 88, "Engine-B harness \u2014 stage C",
        ["decimal-exact parsing of the spectra",
         "mpmath dps %d \u00b7 seed %d" % (eb["dps"], eb["seed"]),
         "separate code path from engine A"])
    harrow(344, 334, 376)
    box(380, 290, 330, 88, "Cross-checks vs engine A",
        ["counts %d/%d exact \u00b7 all four tails"
         % (ctx["counts_line"]["four"], ctx["counts_line"]["four_n"]),
         "%d-bin grid: frozen OR %d/%d"
         % (g["bins"], g["or_pass"], g["or_total"]),
         "edge cluster enumerated \u00b7 0 failures"])
    harrow(714, 334, 746)
    box(750, 290, 330, 88, "Verdict",
        ["%s" % v["overall"],
         "%d clean + %d enumerated + %d failing"
         % (v["cells_pass"], v["cells_pass_enumerated_edge_cluster"],
            v["cells_fail"]),
         "log + JSON committed as artefacts"])

    stage(410, "STAGE 4 \u00b7 PUBLICATION & PROOF \u2014 DASHBOARDS, "
               "MANUSCRIPT, DOI")
    box(20, 420, 320, 88, "Dashboards",
        ["v6 \u2014 H1 + S10 + dim-501 (current)",
         "v5 \u00b7 v4 \u00b7 v3 \u2014 preserved byte-identical",
         "all standalone offline HTML"])
    harrow(344, 464, 376)
    box(380, 420, 330, 88, "Manuscript & release",
        ["research_paper.tex \u00b7 results appendix",
         "AMENDMENT_FLOOR_RESULTS.md Section 8",
         "green public CI on every commit"])
    harrow(714, 464, 746)
    box(750, 420, 330, 88, "Permanent archive",
        ["Zenodo DOI 10.5281/zenodo.23445149",
         "concept DOI 10.5281/zenodo.23338271",
         "all versions pinned forever"])
    add("</svg>")
    return "\n".join(L)


# --------------------------------------------------------------------------
# diagram 2: the verification chain
# --------------------------------------------------------------------------
def render_trustchain_svg(ctx: dict) -> str:
    W, H = 1100, 306
    inst8 = ctx["eb"]["instrument_sha"][:8]
    L: list = []
    add = L.append
    add('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
        'width="100%%" role="img" '
        'aria-label="verification chain: artefacts to permanent archive">'
        % (W, H))
    add('<defs><marker id="arw2" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M 0 1 L 9 5 L 0 9 z" fill="#94a3b8"/></marker></defs>')
    add('<text x="16" y="20" font-size="11" fill="#8a94a8" '
        'letter-spacing="1.4" style="%s">VERIFICATION CHAIN \u00b7 EVERY '
        'FIGURE TRACEABLE TO COMMITTED BYTES</text>' % FONT)

    nodes = [
        ("Raw artefacts", ["spectra \u00b7 logs \u00b7", "dashboards \u00b7 git"]),
        ("Stable hash", ["sha256 over", "CRLF\u2192LF bytes"]),
        ("Pinned in README", ["full hashes pinned,", "plus guard tests"]),
        ("Recompute in CI", ["test_readme_guard.py", "fails on any drift"]),
        ("Public CI run", ["pytest + guards", "per commit \u00b7 archived"]),
        ("Permanent archive", ["Zenodo DOI +", "release tag \u00b7 pinned"]),
    ]
    for i, (title, lines) in enumerate(nodes):
        x = 20 + i * 180.0
        add('<rect x="%.1f" y="30" width="155" height="112" rx="9" '
            'fill="#f8fafd" stroke="#c9d4e4"/>' % x)
        add('<text x="%.1f" y="56" font-size="12.5" font-weight="600" '
            'fill="#101828" style="%s">%s</text>'
            % (x + 12, FONT, esc(title)))
        ty = 78
        for ln in lines:
            add('<text x="%.1f" y="%.1f" font-size="10.5" fill="#475569" '
                'style="%s">%s</text>' % (x + 12, ty, FONT, esc(ln)))
            ty += 15
        if i < len(nodes) - 1:
            add('<line x1="%.1f" y1="86" x2="%.1f" y2="86" '
                'stroke="#94a3b8" stroke-width="1.6" '
                'marker-end="url(#arw2)"/>' % (x + 157, x + 178))

    add('<rect x="20" y="162" width="1060" height="126" rx="9" '
        'fill="#ffffff" stroke="#d9e0ec"/>')
    add('<text x="34" y="186" font-size="13" font-weight="600" '
        'fill="#101828" style="%s">Why a number cannot be silently '
        'edited</text>' % FONT)
    notes = [
        "1. The sealed block in this section is parsed from the artefacts "
        "at build time; hand-editing README.md breaks it against the "
        "generator (CI red).",
        "2. Editing an artefact changes its LF-normalised sha256, which no "
        "longer matches the hash pinned in this block (CI red on the drift "
        "tests).",
        "3. The test suite re-verifies the artefacts themselves (engine-B "
        "artifact guard, dashboard guard, amendment-floor tests) on every "
        "commit.",
        "4. The interval instrument is hashed before and after the "
        "engine-B run; both hashes must be equal (sha256 %s\u2026)." % inst8,
    ]
    ty = 208
    for ln in notes:
        add('<text x="34" y="%.1f" font-size="11.5" fill="#475569" '
            'style="%s">%s</text>' % (ty, FONT, esc(ln)))
        ty += 19
    add("</svg>")
    return "\n".join(L)


# --------------------------------------------------------------------------
# entry points
# --------------------------------------------------------------------------
def dry_run() -> int:
    ctx = collect()
    v = ctx["verdict"]
    g = ctx["grid"]
    cl = ctx["counts_line"]
    fl = ctx["floor"]
    cell = fl["cell"]
    seg = render_segment(ctx)
    wf = render_workflow_svg(ctx)
    tc = render_trustchain_svg(ctx)
    text = README.read_text(encoding="utf-8")
    pat = block_pattern()
    m = pat.search(text)
    readme_state = "DRIFT" if (not m or m.group(0) != seg) else "match"
    print("gw_readme dry run (no files written)")
    print("  engine B: %s (%d clean + %d enumerated + %d failing)"
          % (v["overall"], v["cells_pass"],
             v["cells_pass_enumerated_edge_cluster"], v["cells_fail"]))
    print("  grid: %d bins, frozen OR %d/%d, 10-ulp %d/%d"
          % (g["bins"], g["or_pass"], g["or_total"], g["tight"],
             g["tight_total"]))
    print("  counts: %d/%d exact (k_GUE, k_Pois, all four tails)"
          % (cl["four"], cl["four_n"]))
    print("  refine: %d/%d cells at the floor; above-floor cell: dim %d "
          "chart %s sigma_u %s k=%d/%d"
          % (fl["n_zero"], len(ctx["counts_rows"]), cell["dim"],
             cell["chart"], cell["sigma_u"], cell["k_gue"], cell["n"]))
    print("  S10 extension: pooled %d/%d = %s; %s (number of record %d/"
          "%d unchanged)"
          % (ctx["s10"]["pooled_k"], ctx["s10"]["pooled_n"],
             e5(ctx["s10"]["p_hat"]),
             ctx["s10"]["classification"].split(" (")[0],
             ctx["s10"]["number_of_record"]["k"],
             ctx["s10"]["number_of_record"]["n"]))
    print("  block: %d lines, %d bytes"
          % (seg.count("\n") + 1, len(seg.encode("utf-8"))))
    print("  workflow svg: %d bytes; trustchain svg: %d bytes"
          % (len(wf.encode("utf-8")), len(tc.encode("utf-8"))))
    print("  README block on disk: %s" % readme_state)
    return 0


def write_all() -> int:
    ctx = collect()
    SVG_WORKFLOW.write_bytes(render_workflow_svg(ctx).encode("utf-8"))
    SVG_TRUSTCHAIN.write_bytes(render_trustchain_svg(ctx).encode("utf-8"))
    raw = README.read_bytes()
    text = raw.decode("utf-8")
    crlf = "\r\n" in text
    out = splice_readme(text.replace("\r\n", "\n"), render_segment(ctx))
    if crlf:
        out = out.replace("\n", "\r\n")
    README.write_bytes(out.encode("utf-8"))
    print("wrote docs/math/readme_workflow.svg")
    print("wrote docs/math/readme_trustchain.svg")
    print("wrote README.md sealed-status block")
    return 0


def check() -> int:
    ctx = collect()
    seg = render_segment(ctx)
    ok = True
    m = block_pattern().search(README.read_text(encoding="utf-8"))
    if not m or m.group(0) != seg:
        print("DRIFT: README.md sealed-status block")
        ok = False
    for path, fresh in ((SVG_WORKFLOW, render_workflow_svg(ctx)),
                        (SVG_TRUSTCHAIN, render_trustchain_svg(ctx))):
        if path.read_text(encoding="utf-8") != fresh:
            print("DRIFT: %s" % path.name)
            ok = False
    if ok:
        print("PASS: README block and both diagrams match the sealed "
              "artefacts")
        return 0
    print("FAIL: re-run: python msaf/gw_readme.py --write")
    return 1


def main(argv: list) -> int:
    mode = argv[1] if len(argv) > 1 else ""
    if mode == "--write":
        return write_all()
    if mode == "--check":
        return check()
    if mode:
        print("usage: python msaf/gw_readme.py [--write | --check]")
        return 2
    return dry_run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
