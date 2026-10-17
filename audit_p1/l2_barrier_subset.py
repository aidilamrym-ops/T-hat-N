#!/usr/bin/env python3
"""audit_p1 / L2 item 4 -- barrier subset: descriptor recheck of the closed-slab certificate.

Pre-registered protocol: reports/AUDIT_DBN_PREREG_2026-10-17.md, section 4,
item 4 ("Barrier subset (risk-first; budget-capped)"): from the sealed
certificate descriptors as INPUT (input reuse allowed; computation must be
ours): select K = 8 prisms with the smallest sealed margins, plus their seam
faces plus the first and last prisms; recheck the zero-winding certificate
with our own enclosure method (NOT interior sampling); compare against the
sealed claims:

  total uniform error < 0.000356523011600040 < 0.00125
      (e_A+e_B < 3.639278679550541e-10, e_C,0 < 0.000356522647672172);
  gate  M_i > D_z,i/(2(num-1)) + D_t,i*dt_i + 0.00125;
  winding aggregate [-8.95, 8.95]e-13;
  minimum sealed margin 0.519849894613872543374989997.

Device (ours).  Every number is parsed from the sealed log tokens into exact
fractions.Fraction (Decimal string -> Fraction; no float anywhere in any
check); every recomputed inequality is an exact rational comparison with
strictly conservative (outer) endpoints.  No interior point of the slab is
ever evaluated; the zero-freeness consequence is consumed only through the
sealed winding enclosures and the per-prism gate.

The decisive per-prism gate is certified twice:

  rec_E8_lo = M_lo - spatial_hi - time_hi - eps_hi            > 0
      (same composition as the release's own binding verifier E8,
       reproduced independently here in exact rational arithmetic);
  rec_x_lo  = M_lo - (Dz/(2*(Dz-1))) - Dt*dt_hi - eps_hi      > 0
      (our stronger variant: exact spatial formula -- the generator
       source computes spatial_error = dzabb/(2*(num-1)) with exact
       integer dzabb/num -- and the seam-step hull of the printed t-balls).

Winding recheck (own enclosure method, NOT interior sampling): a winding
number is an integer; the sealed per-prism winding enclosures and the
aggregate enclosure are re-tested for strict containment in (-1/4, 1/4)
(exact rational comparisons), and the aggregate is cross-checked against the
exact interval sum of the 883 per-prism winding enclosures (both must
enclose the same real sum; intersection is necessary).

Independence / scope: the release's sources were read read-only for CLAIM
IDENTIFICATION and format semantics (TloopSinglemat_closed_cert.c,
verify_uniform_error_01787854.c, verify_barrier_binding.py,
run_barrier_replay.sh); no code, parser or table is reused.  We do NOT
re-run the C/Arb lanes; the per-prism descriptor enclosures (mesh
evaluations, min_mesh, winding, Dz, Dt) are trusted as sealed inputs per the
frozen protocol.  Serialized seam byte-identity inside the release assembly,
stored-sum coefficient provenance, and a full 883-prism independent sweep
are out of this item's scope (see "boundary" in the JSON).

Status: development script -- official run only via the runner with the
LOG-EXISTS abort; every run transcript kept.

Output: checks on stdout; machine JSON to
reports/audit_p1_l2_barrier_results.json; exit 0 iff every check passes.
"""

import hashlib
import json
import os
import re
import sys
import time
from decimal import Decimal
from fractions import Fraction as F

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_OUT = os.path.join(REPO_ROOT, "reports", "audit_p1_l2_barrier_results.json")
SRC_DIR = r"C:\Users\usER\AppData\Local\Temp\opencode\dbn_barrier_src"
RELEASE_COMMIT = "2e9976c4becbf97e31c56fe75fce07cdff5dd4ea"

# frozen slab / claim constants (prereg section 4 item 4; BARRIER_CERTIFICATE.md)
X_INT = 6000000185827
N0 = 690988
T0 = F(129, 800)
Y_MIN = F(1809, 10000)
K_SEL = 8
WIND_LIM = F(1, 4)
EPS = F(1, 800)

CLAIM_EAB_S = "3.639278679550541e-10"
CLAIM_EC0_S = "0.000356522647672172"
CLAIM_TOTAL_S = "0.000356523011600040"
CLAIM_MIN_MARGIN_S = "0.519849894613872543374989997"
CLAIM_AGG_S = "8.95e-13"
CLAIM_EAB = F(Decimal(CLAIM_EAB_S))
CLAIM_EC0 = F(Decimal(CLAIM_EC0_S))
CLAIM_TOTAL = F(Decimal(CLAIM_TOTAL_S))
CLAIM_MIN_MARGIN = F(Decimal(CLAIM_MIN_MARGIN_S))
CLAIM_AGG = F(Decimal(CLAIM_AGG_S))

SOURCES = [
    ("BARRIER_CERTIFICATE.md", "e5278fbd45b448618d404cbbd20610be124253d4", 9914,
     "BARRIER_CERTIFICATE.md", "claim text (assertions compared here)"),
    ("barrier/certificates/barrier_target_closed.log",
     "7bed566a9de30ccf35598419480164cae2632820", 387381,
     "barrier__certificates__barrier_target_closed.log",
     "PRIMARY INPUT: 883 sealed prism descriptors rechecked here"),
    ("barrier/certificates/uniform_error_256.log",
     "3e3e2cb40524c3dadf55e604668bed14377fdebc", 988,
     "barrier__certificates__uniform_error_256.log",
     "sealed uniform-error Arb log compared here"),
    ("barrier/certificates/storedsum_taylor_tail.log",
     "597af26e3439389bb9f8f56838994fc1ac365b51", 679,
     "barrier__certificates__storedsum_taylor_tail.log",
     "context only (not consumed by item 4)"),
    ("barrier/certificates/storedsum_provenance.log",
     "31d596fa9d46182ef5849e1e6a3e7a2e45556db7", 424,
     "barrier__certificates__storedsum_provenance.log",
     "context only (not consumed by item 4)"),
    ("verifiers/verify_barrier_binding.py",
     "403c51345153f1acc74a1ca4a29a56c2f1dda5ba", 22345,
     "verifiers__verify_barrier_binding.py",
     "claim/format identification only; no code reused"),
    ("barrier/src/TloopSinglemat_closed_cert.c",
     "6c4f0cbf1356759e385579d4c612d401c15eafaf", 53944,
     "barrier__src__TloopSinglemat_closed_cert.c",
     "generator source read for field semantics; no code reused"),
    ("barrier/src/verify_uniform_error_01787854.c",
     "3b838984a28aa80f6b0b4255c8656fb62a848521", 8261,
     "barrier__src__verify_uniform_error_01787854.c",
     "uniform-error source (total = eAB + eC0 semantics)"),
    ("barrier/compare_storedsum_intervals.py",
     "d063327a0dbf9ffca74ed64c6a937d017629cf0b", 3386,
     "barrier__compare_storedsum_intervals.py",
     "context only (not consumed by item 4)"),
    ("scripts/run_barrier_replay.sh",
     "d31b55365449da12c2a37343e73b416555e5b4e4", 2984,
     "scripts__run_barrier_replay.sh",
     "official replay driver (invocation recorded; not re-run)"),
]

BOUNDARY = [
    "did not re-run the C/Arb lanes (barrier_closed, uniform_error)",
    "per-prism descriptor enclosures (mesh values, min_mesh, winding, Dz, Dt) trusted as sealed inputs",
    "stored-sum coefficient regeneration and Taylor-tail artefact not rechecked",
    "serialized seam byte-identity inside the release assembly not rechecked (log-side token identity only)",
    "full independent 883-prism sweep not re-performed (descriptor recomputation for all 883 + deep checks on the subset)",
    "prop43/prop62 lanes not in scope",
]

PRISM_RE = re.compile(
    r"^Prism\((\d+)\) t=\[(.*?),(.*?)\] winding=(.*?) min_mesh=(.*?) "
    r"Dz=(.*?) Dt=(.*?) spatial=(.*?) time=(.*?) eps=(.*?) margin=(.*?) "
    r"mesh=(\d+) PASS$"
)

NONPRISM_PREFIXES = (
    "Filling stored sums matrix with ",
    "Processing the barrier for X= ",
    "Closed target enclosure: ",
    "Overall winding number: ",
    "Rigorous winding interval: ",
    "Closed coverage endpoint: ",
    "RESULT: CLOSED SLAB CERTIFIED",
    "cpu/wall(s): ",
)

CHECKS = []
VALUES = {}


def check(name, ok, detail=""):
    ok = bool(ok)
    CHECKS.append({"name": name, "ok": ok, "detail": detail})
    print("[%s] %s%s" % ("PASS" if ok else "FAIL", name,
                         ("  -- " + detail) if detail else ""))
    return ok


def fs(f):
    return "%d/%d" % (f.numerator, f.denominator)


def floor_dec(f, digits):
    m = 10 ** digits
    fm = f * m
    scaled = fm.numerator // fm.denominator
    sign = "-" if scaled < 0 else ""
    s = str(abs(scaled)).rjust(digits + 1, "0")
    return sign + s[:-digits] + "." + s[-digits:]


def sci(f, ndig=33):
    if f == 0:
        return "0"
    sign = "-" if f < 0 else ""
    a = -f if f < 0 else f
    n, d = a.numerator, a.denominator
    e = len(str(n)) - len(str(d))
    if a < F(10) ** e:
        e -= 1
    while a >= F(10) ** (e + 1):
        e += 1
    scale = ndig - 1 - e
    if scale >= 0:
        num = (n * 10 ** scale) // d
    else:
        num = n // (d * 10 ** (-scale))
    s = str(num).rjust(ndig, "0")
    return sign + s[0] + "." + s[1:] + "e" + ("%+d" % e)


def disp(f):
    a = -f if f < 0 else f
    if f == 0:
        return "0"
    if a >= F(1, 10 ** 6) and a < F(10 ** 9):
        return floor_dec(f, 33)
    return sci(f, 33)


def tok_ball(tok):
    tok = tok.strip()
    if tok.startswith("[") and tok.endswith("]"):
        inner = tok[1:-1].strip()
        if "+/-" in inner:
            left, right = inner.split("+/-", 1)
            rad = F(Decimal(right.strip()))
            left = left.strip()
            mid = F(0) if left == "" else F(Decimal(left))
            return mid - rad, mid + rad
        v = F(Decimal(inner))
        return v, v
    v = F(Decimal(tok))
    return v, v


def git_blob_sha1(data):
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def main():
    t_start = time.perf_counter()
    print("audit_p1 / L2 item 4 -- barrier subset (descriptor recheck)")
    print("release commit: %s" % RELEASE_COMMIT)
    print("source dir: %s" % SRC_DIR)
    print()
    print("frozen claims (prereg section 4 item 4):")
    print("  e_A+e_B        < %s" % CLAIM_EAB_S)
    print("  e_C,0          < %s" % CLAIM_EC0_S)
    print("  total uniform  < %s < 1/800" % CLAIM_TOTAL_S)
    print("  gate           : M_i > D_z,i/(2(num-1)) + D_t,i*dt_i + 1/800")
    print("  winding agg    : +/- %s" % CLAIM_AGG_S)
    print("  min margin     : %s" % CLAIM_MIN_MARGIN_S)
    print()

    # ---------------------------------------------------------- provenance
    print("== provenance: pinned release sources (git blob sha1 + size) ==")
    src_bytes = {}
    for rel, blob_sha, size, local, role in SOURCES:
        path = os.path.join(SRC_DIR, local)
        try:
            with open(path, "rb") as fh:
                data = fh.read()
        except OSError as exc:
            check("prov %s (blob %s)" % (rel, blob_sha[:12]), False,
                  "read failed: %s" % exc)
            continue
        got_sha = git_blob_sha1(data)
        ok = (len(data) == size) and (got_sha == blob_sha)
        check("prov %s (blob %s, %d B)" % (rel, blob_sha[:12], size), ok,
              "sha256=%s role=%s" % (hashlib.sha256(data).hexdigest()[:16], role))
        src_bytes[rel] = data
    print()

    # ------------------------------------------------------------ parse log
    print("== structural parse of the sealed prism log ==")
    log_data = src_bytes.get("barrier/certificates/barrier_target_closed.log", b"")
    log = log_data.decode("utf-8", errors="replace")
    lines = log.split("\n")
    nonblank = [ln for ln in lines if ln.strip()]

    parse_fail = []
    prisms = []
    for ln, line in enumerate(lines, 1):
        if line.startswith("Prism("):
            m = PRISM_RE.fullmatch(line)
            if not m:
                parse_fail.append((ln, line[:90]))
                continue
            g = m.groups()
            prisms.append({
                "idx": int(g[0]), "line_no": ln,
                "start_text": g[1].strip(), "end_text": g[2].strip(),
                "wind_text": g[3].strip(), "minm_text": g[4].strip(),
                "dz_text": g[5].strip(), "dt_text": g[6].strip(),
                "sp_text": g[7].strip(), "time_text": g[8].strip(),
                "eps_text": g[9].strip(), "margin_text": g[10].strip(),
                "mesh": int(g[11]),
            })

    check("all prism lines parse in the sealed format (883)",
          len(prisms) == 883 and not parse_fail,
          "parsed=%d parse_fail=%d" % (len(prisms), len(parse_fail)))
    ids = [p["idx"] for p in prisms]
    check("prism identifiers are consecutive 1..883",
          ids == list(range(1, 884)))

    recognized = all(
        ln.startswith("Prism(") or any(ln.startswith(pref) for pref in NONPRISM_PREFIXES)
        for ln in nonblank)
    count_ok = (
        len(nonblank) == 891
        and sum(ln.startswith("Filling stored sums matrix with ") for ln in nonblank) == 1
        and sum(ln.startswith("Processing the barrier for X= ") for ln in nonblank) == 1
        and sum(ln.startswith("Closed target enclosure: ") for ln in nonblank) == 1
        and sum(ln.startswith("Overall winding number: ") for ln in nonblank) == 1
        and sum(ln.startswith("Rigorous winding interval: ") for ln in nonblank) == 1
        and sum(ln.startswith("Closed coverage endpoint: ") for ln in nonblank) == 1
        and nonblank[-2] == "RESULT: CLOSED SLAB CERTIFIED"
        and nonblank[-1].startswith("cpu/wall(s): ")
    )
    check("log line structure: 891 nonblank, unique headers, result/cpu ordered",
          recognized and count_ok,
          "nonblank=%d recognized=%s" % (len(nonblank), recognized))
    check("no failure/abort marker in the log",
          "FAIL" not in log and "aborted" not in log)
    print()

    # -------------------------------------------------------------- header
    print("== header: slab, target coverage, allowance ==")
    header_line = next((ln for ln in nonblank
                        if ln.startswith("Closed target enclosure: ")), "")
    m = re.fullmatch(
        r"Closed target enclosure: (\[.*?\]); N-corners=(\d+),(\d+); "
        r"H/B approximation allowance=(.*)", header_line)
    tgt_ball = tok_ball(m.group(1)) if m else None
    n_lo = int(m.group(2)) if m else 0
    n_hi = int(m.group(3)) if m else 0
    allow_ball = tok_ball(m.group(4)) if m else None
    check("header: N-corners=690988,690988",
          m is not None and n_lo == N0 and n_hi == N0,
          "N-corners=%d,%d" % (n_lo, n_hi))
    check("header: target enclosure encloses 129/800, width <= 1e-25",
          tgt_ball is not None and tgt_ball[0] <= T0 <= tgt_ball[1]
          and (tgt_ball[1] - tgt_ball[0]) <= F(1, 10 ** 25),
          "ball=[%s, %s]" % (disp(tgt_ball[0]), disp(tgt_ball[1])) if tgt_ball else "missing")
    check("header: allowance ball encloses 1/800, width < 1e-25",
          allow_ball is not None and allow_ball[0] <= EPS <= allow_ball[1]
          and (allow_ball[1] - allow_ball[0]) < F(1, 10 ** 25),
          "ball=[%s, %s]" % (disp(allow_ball[0]), disp(allow_ball[1])) if allow_ball else "missing")
    check("header: X/N/y0/t slab tokens present",
          "X= 6000000185827.0000000...6000000185828.0000000" in log
          and "(N = 690988)" in log
          and "y0 = 0.1809000000...1" in log
          and "t = 0...0.1612500000" in log)
    check("header: stored-sum matrix context line present",
          "Filling stored sums matrix with 62 X 62 terms guaranteeing 20 digits accuracy..." in log)
    print()
    # ------------------------------------------- all-prism recomputation
    print("== all 883 prisms: descriptor recomputation (exact rationals) ==")
    bad_struct, bad_dur, bad_sp, bad_time = [], [], [], []
    bad_eps, bad_gate, bad_gate_x, bad_misect, bad_wind = [], [], [], [], []
    min_rec_e8 = None
    min_rec_x = None
    min_dur = None
    max_wind = None
    eps_ref = None
    eps_uniform = True
    for p in prisms:
        try:
            st = tok_ball(p["start_text"])
            en = tok_ball(p["end_text"])
            wind = tok_ball(p["wind_text"])
            minm = tok_ball(p["minm_text"])
            sp = tok_ball(p["sp_text"])
            ti = tok_ball(p["time_text"])
            ep = tok_ball(p["eps_text"])
            mg = tok_ball(p["margin_text"])
        except Exception as exc:
            parse_fail.append((p["line_no"], "token parse: %s" % exc))
            continue
        dzf = F(Decimal(p["dz_text"]))
        dtf = F(Decimal(p["dt_text"]))
        p["st"], p["en"], p["wind"], p["minm"] = st, en, wind, minm
        p["sp"], p["ti"], p["ep"], p["mg"] = sp, ti, ep, mg
        p["dz_int"] = dzf.numerator if dzf.denominator == 1 else None
        p["dt_int"] = dtf.numerator if dtf.denominator == 1 else None
        dz = p["dz_int"]
        dti = p["dt_int"]
        struct_ok = (dz is not None and dz >= 2 and dti is not None and dti > 0
                     and p["mesh"] == 4 * dz - 4 and p["mesh"] >= 4)
        if not struct_ok:
            bad_struct.append(p["idx"])
        dur_ok = st[1] < en[0]
        if not dur_ok:
            bad_dur.append(p["idx"])
        sp_ok = struct_ok and (sp[0] <= F(dz, 2 * (dz - 1)) <= sp[1])
        if not sp_ok:
            bad_sp.append(p["idx"])
        dt_lo = en[0] - st[1]
        dt_hi = en[1] - st[0]
        time_hull = (dtf * dt_lo, dtf * dt_hi) if struct_ok else None
        time_ok = (struct_ok and ti[0] <= time_hull[0]
                   and time_hull[1] <= ti[1])
        if not time_ok:
            bad_time.append(p["idx"])
        eps_ok = ep[0] <= EPS <= ep[1] and (ep[1] - ep[0]) < F(1, 10 ** 25)
        if eps_ref is None:
            eps_ref = ep
        elif ep != eps_ref:
            eps_uniform = False
        if not eps_ok:
            bad_eps.append(p["idx"])
        s_exact = F(dz, 2 * (dz - 1)) if struct_ok else None
        rec_e8_lo = minm[0] - sp[1] - ti[1] - ep[1]
        rec_e8_hi = minm[1] - sp[0] - ti[0] - ep[0]
        rec_x_lo = minm[0] - s_exact - time_hull[1] - ep[1] if struct_ok else None
        rec_x_hi = minm[1] - s_exact - time_hull[0] - ep[0] if struct_ok else None
        p["rec_e8"] = (rec_e8_lo, rec_e8_hi)
        p["rec_x"] = (rec_x_lo, rec_x_hi)
        p["struct_ok"], p["dur_ok"], p["sp_ok"] = struct_ok, dur_ok, sp_ok
        p["time_ok"], p["eps_ok"] = time_ok, eps_ok
        p["s_exact"] = s_exact
        p["time_hull"] = time_hull
        if not (rec_e8_lo > 0):
            bad_gate.append(p["idx"])
        if not (rec_x_lo is not None and rec_x_lo > 0):
            bad_gate_x.append(p["idx"])
        if rec_x_lo is None:
            misect_ok = False
        else:
            misect_ok = (mg[0] <= rec_e8_hi and rec_e8_lo <= mg[1]
                         and mg[0] <= rec_x_hi and rec_x_lo <= mg[1])
        if not misect_ok:
            bad_misect.append(p["idx"])
        p["misect_ok"] = misect_ok
        wind_ok = wind[0] > -WIND_LIM and wind[1] < WIND_LIM
        if not wind_ok:
            bad_wind.append(p["idx"])
        p["wind_ok"] = wind_ok
        if min_rec_e8 is None or rec_e8_lo < min_rec_e8[0]:
            min_rec_e8 = (rec_e8_lo, p["idx"])
        if min_rec_x is None or rec_x_lo < min_rec_x[0]:
            min_rec_x = (rec_x_lo, p["idx"])
        dur = en[0] - st[1]
        if min_dur is None or dur < min_dur[0]:
            min_dur = (dur, p["idx"])
        wabs = max(wind[1], -wind[0])
        if max_wind is None or wabs > max_wind[0]:
            max_wind = (wabs, p["idx"])

    complete = [p for p in prisms if "mg" in p]
    check("all prism tokens parse into exact rational intervals",
          len(complete) == 883 and not parse_fail,
          "parsed=%d parse_fail=%d" % (len(complete), len(parse_fail)))
    prisms = complete

    check("all prisms: Dz,Dt exact positive ints, mesh == 4*Dz-4",
          len(prisms) == 883 and not bad_struct,
          "violations=%d" % len(bad_struct))
    check("all prisms: positive duration start_hi < end_lo",
          not bad_dur, "violations=%d" % len(bad_dur))
    check("all prisms: spatial ball encloses Dz/(2(Dz-1))",
          not bad_sp, "violations=%d" % len(bad_sp))
    check("all prisms: time ball encloses Dt*[dt_lo,dt_hi]",
          not bad_time, "violations=%d" % len(bad_time))
    check("all prisms: eps ball uniform, encloses 1/800, radius < 1e-25",
          not bad_eps and eps_uniform,
          "violations=%d uniform=%s" % (len(bad_eps), eps_uniform))
    check("GATE rec_E8_lo > 0 for every prism",
          not bad_gate,
          "min=%s at prism %d of %d" % (disp(min_rec_e8[0]), min_rec_e8[1], len(prisms))
          if min_rec_e8 else "no data")
    check("GATE rec_x_lo > 0 for every prism (refined variant)",
          not bad_gate_x,
          "min=%s at prism %d" % (disp(min_rec_x[0]), min_rec_x[1]) if min_rec_x else "no data")
    check("margin ball intersects recomputed hulls for every prism",
          not bad_misect, "violations=%d" % len(bad_misect))
    check("winding ball strictly inside (-1/4, 1/4) for every prism",
          not bad_wind,
          "max |endpoint|=%s at prism %d" % (disp(max_wind[0]), max_wind[1])
          if max_wind else "no data")

    seam_bad = []
    for a, b in zip(prisms, prisms[1:]):
        if a["end_text"] != b["start_text"] or a["idx"] + 1 != b["idx"]:
            seam_bad.append((a["idx"], b["idx"]))
    check("all 882 adjacent seam tokens byte-identical",
          len(prisms) == 883 and not seam_bad,
          "mismatches=%d" % len(seam_bad))
    check("first prism starts at exact token '0'",
          bool(prisms) and prisms[0]["start_text"] == "0"
          and prisms[0]["st"] == (F(0), F(0)),
          "token=%r" % (prisms[0]["start_text"] if prisms else None))
    last_en = prisms[-1]["en"] if prisms else None
    check("last prism end ball encloses t0=129/800",
          last_en is not None and last_en[0] <= T0 <= last_en[1],
          "token=%r" % (prisms[-1]["end_text"] if prisms else None))
    cov_line = next((ln for ln in nonblank
                     if ln.startswith("Closed coverage endpoint: ")), "")
    cov_tok = cov_line[len("Closed coverage endpoint: "):].strip()
    check("coverage endpoint token equals last prism end token",
          bool(prisms) and cov_tok == prisms[-1]["end_text"],
          "coverage=%r" % cov_tok)
    print()

    # ---------------------------------------------------------- selection
    print("== selection: K=8 smallest sealed margins + seam faces + endpoints ==")
    ranked = sorted(prisms, key=lambda p: (p["mg"][0], p["idx"]))
    sel = ranked[:K_SEL]
    ranked_x = sorted(prisms, key=lambda p: (p["rec_e8"][0], p["idx"]))
    sel_x = ranked_x[:K_SEL]
    for p in sel:
        print("  sel prism %3d: margin_lo=%-36s rec_E8_lo=%s  rec_x_lo=%s"
              % (p["idx"], disp(p["mg"][0]), disp(p["rec_e8"][0]), disp(p["rec_x"][0])))
    same_set = set(p["idx"] for p in sel) == set(p["idx"] for p in sel_x)
    print("  same K=8 set under rec_E8_lo ranking: %s" % same_set)
    subset = set([1, 883])
    for p in sel:
        subset.add(p["idx"])
        if p["idx"] > 1:
            subset.add(p["idx"] - 1)
        if p["idx"] < 883:
            subset.add(p["idx"] + 1)
    subset = sorted(subset)
    print("  subset S (%d prisms): %s"
          % (len(subset), ",".join(str(i) for i in subset)))
    check("criterion: K=8 selection computed from sealed margin balls",
          len(sel) == K_SEL and all(p["idx"] in subset for p in sel))
    check("global min rec_E8_lo equals sealed minimum margin exactly",
          min_rec_e8 is not None and min_rec_e8[0] == CLAIM_MIN_MARGIN,
          "min=%s at prism %d" % (disp(min_rec_e8[0]), min_rec_e8[1])
          if min_rec_e8 else "no data")
    check("min-margin prism is #882", min_rec_e8 is not None and min_rec_e8[1] == 882)
    check("min-margin prism is inside subset S",
          min_rec_e8 is not None and min_rec_e8[1] in subset)
    print()

    # ------------------------------------------------- subset deep checks
    print("== subset deep checks ==")
    idx_to_p = {p["idx"]: p for p in prisms}
    subset_detail = []
    for i in subset:
        p = idx_to_p.get(i)
        if p is None:
            check("S%d present in parsed prisms" % i, False, "missing")
            continue
        prev_tok = idx_to_p[i - 1]["end_text"] if (i > 1 and (i - 1) in idx_to_p) else None
        next_tok = idx_to_p[i + 1]["start_text"] if (i < 883 and (i + 1) in idx_to_p) else None
        left_ok = (prev_tok is None) or (prev_tok == p["start_text"])
        right_ok = (next_tok is None) or (next_tok == p["end_text"])
        seam_ok = left_ok and right_ok
        dzs = p["dz_int"]
        dts = p["dt_int"]
        s_x = p["s_exact"]
        th = p["time_hull"]
        print("  -- prism %d --" % i)
        print("     t      = [%s, %s]" % (p["start_text"], p["end_text"]))
        print("     duration (end_lo - start_hi) = %s" % disp(p["en"][0] - p["st"][1]))
        print("     winding  = %s" % p["wind_text"])
        print("     min_mesh = %s" % p["minm_text"])
        print("     Dz=%s Dt=%s mesh=%d (4*Dz-4=%s)"
              % (dzs, dts, p["mesh"], 4 * dzs - 4 if dzs is not None else "n/a"))
        print("     spatial  = %s ; exact Dz/(2(Dz-1)) = %s = %s"
              % (p["sp_text"], fs(s_x) if s_x is not None else "n/a",
                 disp(s_x) if s_x is not None else "n/a"))
        print("     time     = %s ; Dt*dt hull = [%s, %s]"
              % (p["time_text"],
                 disp(th[0]) if th is not None else "n/a",
                 disp(th[1]) if th is not None else "n/a"))
        print("     eps      = %s" % p["eps_text"])
        print("     margin   = %s" % p["margin_text"])
        print("     rec_E8   = [%s, %s]" % (disp(p["rec_e8"][0]), disp(p["rec_e8"][1])))
        print("     rec_x    = [%s, %s]"
              % (disp(p["rec_x"][0]) if p["rec_x"][0] is not None else "n/a",
                 disp(p["rec_x"][1]) if p["rec_x"][1] is not None else "n/a"))
        print("     seam L/R = %s / %s"
              % ("-" if prev_tok is None else ("byte-identical" if left_ok else "MISMATCH"),
                 "-" if next_tok is None else ("byte-identical" if right_ok else "MISMATCH")))
        check("S%d gate rec_E8_lo>0" % i, p["rec_e8"][0] > 0,
              "rec_E8_lo=%s" % disp(p["rec_e8"][0]))
        gate_x_ok = p["rec_x"][0] is not None and p["rec_x"][0] > 0
        check("S%d gate rec_x_lo>0" % i, gate_x_ok,
              "rec_x_lo=%s" % (disp(p["rec_x"][0]) if p["rec_x"][0] is not None else "n/a"))
        check("S%d margin ball intersects recomputed hulls" % i, p["misect_ok"])
        check("S%d winding ball inside (-1/4,1/4)" % i, p["wind_ok"], p["wind_text"])
        check("S%d descriptors (struct/duration/spatial/time/eps)" % i,
              p["struct_ok"] and p["dur_ok"] and p["sp_ok"] and p["time_ok"] and p["eps_ok"])
        check("S%d seam faces byte-identical" % i, seam_ok)
        subset_detail.append({
            "idx": i,
            "t_start": p["start_text"], "t_end": p["end_text"],
            "winding": p["wind_text"], "min_mesh": p["minm_text"],
            "dz": p["dz_int"], "dt": p["dt_int"], "mesh": p["mesh"],
            "spatial": p["sp_text"], "time": p["time_text"],
            "eps": p["eps_text"], "margin": p["margin_text"],
            "s_exact": fs(p["s_exact"]),
            "time_hull": [fs(p["time_hull"][0]), fs(p["time_hull"][1])],
            "rec_e8": [fs(p["rec_e8"][0]), fs(p["rec_e8"][1])],
            "rec_x": [fs(p["rec_x"][0]), fs(p["rec_x"][1])],
            "gate_e8": bool(p["rec_e8"][0] > 0),
            "gate_x": bool(p["rec_x"][0] > 0),
        })
    print()

    # ---------------------------------------------- aggregate winding
    print("== aggregate winding vs exact sum of per-prism enclosures ==")
    sum_lo = sum((p["wind"][0] for p in prisms), F(0))
    sum_hi = sum((p["wind"][1] for p in prisms), F(0))
    agg_line = next((ln for ln in nonblank
                     if ln.startswith("Rigorous winding interval: ")), "")
    agg_tok = agg_line[len("Rigorous winding interval: "):].strip()
    agg = tok_ball(agg_tok) if agg_tok else None
    overall_ok = any(ln.rstrip() == "Overall winding number: 0.000000" for ln in nonblank)
    check("aggregate token equals +/- 8.95e-13 exactly",
          agg == (-CLAIM_AGG, CLAIM_AGG), "token=%r" % agg_tok)
    check("aggregate encloses 0 and |endpoints| < 1/4",
          agg is not None and agg[0] <= 0 <= agg[1]
          and max(agg[1], -agg[0]) < WIND_LIM)
    check("per-prism winding sum interval intersects aggregate interval",
          agg is not None and sum_lo <= agg[1] and agg[0] <= sum_hi,
          "sum=[%s, %s] agg=[%s, %s]" % (disp(sum_lo), disp(sum_hi),
                                          disp(agg[0]), disp(agg[1])) if agg else "no agg")
    print("  sum of per-prism winding intervals: [%s, %s]" % (disp(sum_lo), disp(sum_hi)))
    print("  aggregate interval: [%s, %s]" % (disp(agg[0]), disp(agg[1])))
    print("  containment sum inside agg: %s" % (sum_lo >= agg[0] and sum_hi <= agg[1]))
    check("Overall winding number line reads exactly 0.000000", overall_ok)
    print()

    # -------------------------------------------------- uniform error log
    print("== uniform error claims (uniform_error_256.log) ==")
    ulog = src_bytes.get("barrier/certificates/uniform_error_256.log", b"").decode(
        "utf-8", errors="replace")

    def ufield(pattern):
        mm = re.search(pattern, ulog, re.MULTILINE)
        return tok_ball(mm.group(1)) if mm else None

    eab = ufield(r"^e_A\+e_B upper = (\[.*?\])$")
    ec0 = ufield(r"^e_C0 upper = (\[.*?\])$")
    tot = ufield(r"^uniform conservative error total upper = (\[.*?\])$")
    check("uniform log: e_A+e_B upper < 3.639278679550541e-10",
          eab is not None and eab[1] < CLAIM_EAB,
          "eab_hi=%s" % (disp(eab[1]) if eab else "missing"))
    check("uniform log: e_C0 upper < 0.000356522647672172",
          ec0 is not None and ec0[1] < CLAIM_EC0,
          "ec0_hi=%s" % (disp(ec0[1]) if ec0 else "missing"))
    check("uniform log: total upper < 0.000356523011600040",
          tot is not None and tot[1] < CLAIM_TOTAL,
          "total_hi=%s" % (disp(tot[1]) if tot else "missing"))
    check("uniform log: total upper < 1/800",
          tot is not None and tot[1] < EPS)
    check("claim arithmetic: eAB + eC0 <= claimed total (exact)",
          CLAIM_EAB + CLAIM_EC0 <= CLAIM_TOTAL,
          "exact sum=%s" % disp(CLAIM_EAB + CLAIM_EC0))
    sum_ball = (eab[0] + ec0[0], eab[1] + ec0[1]) if (eab and ec0) else None
    check("uniform log: total ball intersects eAB+eC0 ball sum",
          sum_ball is not None and tot[0] <= sum_ball[1] and sum_ball[0] <= tot[1])
    check("uniform log: PASS and RESULT lines present",
          "[PASS] uniform conservative error total < 0.00125" in ulog
          and "RESULT: UNIFORM NUMERICAL ERROR-FORMULA BOUND CERTIFIED" in ulog)
    scope_ok = ("SCOPE NOTE: analytic justification at t=0 remains external."
                in ulog)
    print("  uniform log scope note present: %s" % scope_ok)
    print()

    # -------------------------------------------------- claim text spot checks
    print("== certificate + prereg text spot checks ==")
    cert = src_bytes.get("BARRIER_CERTIFICATE.md", b"").decode("utf-8", errors="replace")
    for frag in ("3.639278679550541", "0.000356522647672172",
                 "0.000356523011600040", "0.519849894613872543374989997",
                 "-8.95,8.95"):
        check("certificate contains %r" % frag, frag in cert)
    check("certificate gate inequality text present",
          "M_i>" in cert and "2(\\texttt{num}-1)" in cert and "+0.00125" in cert)
    prereg_path = os.path.join(REPO_ROOT, "reports", "AUDIT_DBN_PREREG_2026-10-17.md")
    try:
        with open(prereg_path, encoding="utf-8") as fh:
            prereg = fh.read()
    except OSError:
        prereg = ""
    for frag in (CLAIM_EAB_S, CLAIM_EC0_S, CLAIM_TOTAL_S, CLAIM_MIN_MARGIN_S):
        check("prereg contains frozen claim constant %r" % frag, frag in prereg)
    print()

    # ------------------------------------------------------------- verdict
    total = len(CHECKS)
    failed = [c for c in CHECKS if not c["ok"]]
    print("checks_total: %d  checks_failed: %d" % (total, len(failed)))
    verdict = "PASS" if not failed else "FAIL"
    print("item4 machine verdict: %s" % verdict)

    VALUES.update({
        "audit": "P1 L2 item 4 -- barrier subset descriptor recheck",
        "prereg": "reports/AUDIT_DBN_PREREG_2026-10-17.md section 4 item 4",
        "release_commit": RELEASE_COMMIT,
        "device": ("exact rational arithmetic on sealed decimal tokens; "
                   "no float; no interior sampling; no C/Arb re-run"),
        "selection_rule": ("K=8 smallest lower endpoint of the sealed margin ball; "
                           "plus both seam-face neighbours of each; "
                           "plus first and last prism"),
        "subset": subset,
        "selection": [{"idx": p["idx"], "margin_lo": fs(p["mg"][0]),
                       "margin_lo_dec": disp(p["mg"][0]),
                       "rec_e8_lo": fs(p["rec_e8"][0]),
                       "rec_x_lo": fs(p["rec_x"][0])} for p in sel],
        "selection_same_under_rec_e8_ranking": same_set,
        "global_min_rec_e8_lo": {"value": fs(min_rec_e8[0]),
                                 "dec": disp(min_rec_e8[0]),
                                 "prism": min_rec_e8[1]},
        "global_min_rec_x_lo": {"value": fs(min_rec_x[0]),
                                "dec": disp(min_rec_x[0]),
                                "prism": min_rec_x[1]},
        "min_duration": {"value": fs(min_dur[0]), "dec": disp(min_dur[0]),
                         "prism": min_dur[1]},
        "max_abs_winding_endpoint": {"value": fs(max_wind[0]),
                                     "dec": disp(max_wind[0]),
                                     "prism": max_wind[1]},
        "aggregate": {"token": agg_tok, "lo": fs(agg[0]), "hi": fs(agg[1]),
                      "sum_lo": fs(sum_lo), "sum_hi": fs(sum_hi),
                      "sum_inside_agg": bool(sum_lo >= agg[0] and sum_hi <= agg[1])},
        "uniform_error": {
            "eab": [fs(eab[0]), fs(eab[1])] if eab else None,
            "ec0": [fs(ec0[0]), fs(ec0[1])] if ec0 else None,
            "total": [fs(tot[0]), fs(tot[1])] if tot else None,
            "claims": {"eab": CLAIM_EAB_S, "ec0": CLAIM_EC0_S,
                       "total": CLAIM_TOTAL_S,
                       "min_margin": CLAIM_MIN_MARGIN_S, "agg": CLAIM_AGG_S},
        },
        "subset_detail": subset_detail,
        "boundary": BOUNDARY,
        "sources": [{"rel": rel, "blob_sha1": blob, "size": size, "role": role,
                     "sha256": hashlib.sha256(src_bytes[rel]).hexdigest()
                     if rel in src_bytes else None}
                    for (rel, blob, size, local, role) in SOURCES],
        "checks": CHECKS,
        "checks_total": total,
        "checks_failed": len(failed),
        "verdict": verdict,
        "runtime_seconds": round(time.perf_counter() - t_start, 1),
    })
    os.makedirs(os.path.dirname(JSON_OUT), exist_ok=True)
    with open(JSON_OUT, "w", encoding="utf-8") as fh:
        json.dump(VALUES, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("json written: %s" % JSON_OUT)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
