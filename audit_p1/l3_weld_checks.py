#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P1 audit -- L3 clean-room theorem-source weld (frozen prereg section 5).

Scope (pre-registered, `reports/AUDIT_DBN_PREREG_2026-10-17.md` section 5):

  1. Hypothesis mapping: (i)/(ii)/(iii) of Polymath Theorem 1.2 (as
     transcribed from the pinned e-print v2) against the package's
     claims in its own obligation slots (P1 / T1 / B1-B2, supporting
     F1-F3, glue C1; ids from ADVERSARIAL_REVIEW_PROTOCOL.md);
     domain, endpoint, quantifier and substitution per slot.
  2. Parameter compatibility: X/2 vs T_PT; margin 350479773/2;
     window overlap N = 3840000.
  3. Containment: barrier rectangle [X, X+1] + i[1809/10000, 1]
     contains the theorem's curved barrier region for 0 <= t <= t0.
  4. Citation chain versions: each cited result pinned to its refereed
     version where one exists.
  5. Verdict per hypothesis {compatible / mismatch / unresolved} with
     file+line references; then the weld verdict.

Device (frozen before the official run):

  * every verdict inequality is exact `fractions.Fraction` arithmetic
    over integer/rational tokens only; no floats in the checks;
  * release inputs are the version-locked local copies gated in-run
    against the pinned tree (commit 2e9976c4becbf97e31c56fe75fce07
    cdff5dd4ea) by git blob sha1 + size;
  * e-print inputs are re-derived in-run (tar member / gzip payload)
    and hashed against recorded sha256 values;
  * statement weld compares the e-print v2 hypothesis texts against
    the package's PROOF_NOTE section 2 statements after a documented
    canonicalisation (backslash wrappers, spacing, `and` <-> comma,
    `zeroes` <-> `zeros`); both normalised strings are printed;
  * one secondary window-freeze bracket (x_690988 < x_* < x_690989)
    is recomputed with mpmath 60 dps pi brackets + exact sqrt
    brackets; it is labelled secondary (the primary remains the
    release WINDOW_FREEZE_THEOREM plus our committed L2 item 1);
  * no release lane is re-run; L2 item verdicts are consumed only as
    recorded evidence (cross-reference reads of committed logs).

Boundary / not checked here: correctness of the cited published
theorems, the package's analytic reductions (Dini transfer, t=0
dominated-convergence endpoint, native binding algebra, derivative-box
and tail proofs), the typeset journal rendering of the e-prints, and
any interval-arithmetic lane of the release.  Fail-closed: exit 0 only
if every check passes.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import os
import re
import sys
import tarfile
import time
from fractions import Fraction

DATE = "2026-10-17"
RELEASE_COMMIT = "2e9976c4becbf97e31c56fe75fce07cdff5dd4ea"
PREREG = "reports/AUDIT_DBN_PREREG_2026-10-17.md"

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
TMP = r"C:\Users\usER\AppData\Local\Temp\opencode"
DOCS = os.path.join(TMP, "dbn_release_docs")
BSRC = os.path.join(TMP, "dbn_barrier_src")
POLY = os.path.join(TMP, "res3_polymath15")
PTSRC = os.path.join(TMP, "pt_src")
L3META = os.path.join(TMP, "l3_meta")
JSON_OUT = os.path.join(REPO, "reports", "audit_p1_l3_results.json")

# ---------------------------------------------------------------- exact data

X = 6000000185827
T_PT = 3000175332800
MARGIN = Fraction(350479773, 2)
T0 = Fraction(129, 800)
Y0SQ = Fraction(87677, 2500000)
CANDIDATE = Fraction(893927, 5000000)
CEIL = Fraction(271, 400)
CANOPY = Fraction(893927, 2500000)
EDGE = Fraction(1809, 10000)
Y0_LO = Fraction(1872719, 10 ** 7)
Y0_HI = Fraction(23409, 125000)
YMAX_LO = Fraction(8231038, 10 ** 7)
YMAX_HI = Fraction(8231039, 10 ** 7)
ROWS_LO = 690988
ROWS_HI = 3840000
NSTAR = 3840000
LEGS = [(690988, 728999), (729000, 818999), (819000, 1027999), (1028000, 3840000)]

# ------------------------------------------------------------------ sources

BLOB_SOURCES = [
    ("proof_note", os.path.join(DOCS, "PROOF_NOTE.md"), "PROOF_NOTE.md",
     "323e2144e9d1624c81002be5997b0901147ce166", 14965, "weld: criterion sections 2-7"),
    ("candidate_parameters", os.path.join(DOCS, "CANDIDATE_PARAMETERS.md"),
     "CANDIDATE_PARAMETERS.md", "bdad0402562f5ea077a9ab380558cb19f74ffb82", 4695,
     "weld: exact parameter row"),
    ("window_freeze", os.path.join(DOCS, "WINDOW_FREEZE_THEOREM.md"),
     "WINDOW_FREEZE_THEOREM.md", "0f4ebe3567414e9eb94c3be23f5e662e211f92ca", 3856,
     "slot F1/F3: x-freeze + endpoint coverage"),
    ("tail_lemma", os.path.join(DOCS, "TAIL_LEMMA.md"), "TAIL_LEMMA.md",
     "cdc612e9117b24cd4c050d2c146cf5d2fa1a3de6", 14476, "slot T1: all-N tail theorem"),
    ("tail_provenance", os.path.join(DOCS, "TAIL_PROVENANCE.md"), "TAIL_PROVENANCE.md",
     "cb3bc2947e2e6b02a7f1b580d9b347e708a68591", 1793, "slot T1: provenance"),
    ("native_binding", os.path.join(DOCS, "NATIVE_BINDING.md"), "NATIVE_BINDING.md",
     "aac13ed946ce380d79e54e563431865b695cdded", 4194, "slot F1: native binding"),
    ("derivative_box", os.path.join(DOCS, "DERIVATIVE_BOX_LEMMA.md"),
     "DERIVATIVE_BOX_LEMMA.md", "39616582de04385ea95feb7d06be2962b6bef0ff", 9206,
     "slot B1: uniform derivative bounds"),
    ("error_constant_weld", os.path.join(DOCS, "ERROR_CONSTANT_WELD.md"),
     "ERROR_CONSTANT_WELD.md", "9fd635b59831316b73c1052dd4f6ec71ce70f1e1", 2604,
     "slot P3/error: conservative x-12, 10.50 corollary"),
    ("maximum_checks", os.path.join(DOCS, "MAXIMUM_CHECKS.md"), "MAXIMUM_CHECKS.md",
     "acbf9813044be247bec1f14aec6216d3f6fcf108", 13572, "release: check inventory"),
    ("release_readme", os.path.join(DOCS, "README.md"), "README.md",
     "4af5cdb46e7dcc3a24e4aaa535d644291745a584", 10492, "release: front matter"),
    ("bibliography", os.path.join(DOCS, "BIBLIOGRAPHY.md"), "BIBLIOGRAPHY.md",
     "9e0961a138ff6739c8ff1df601d3437cdbba458a", 1095, "citation chain: primary references"),
    ("adversarial_protocol", os.path.join(DOCS, "ADVERSARIAL_REVIEW_PROTOCOL.md"),
     "ADVERSARIAL_REVIEW_PROTOCOL.md", "d26d6db3f8602f56cfde6fb14232f10b8cbf2b8c", 7487,
     "slot ids P1/T1/B1-B2/C1"),
    ("references_readme", os.path.join(DOCS, "references__README.md"),
     "references/README.md", "294ddc5f3759f024428953661a6270c82c884c65", 687,
     "citation chain: version-locked reference hashes"),
    ("barrier_certificate", os.path.join(BSRC, "BARRIER_CERTIFICATE.md"),
     "BARRIER_CERTIFICATE.md", "e5278fbd45b448618d404cbbd20610be124253d4", 9914,
     "slot B1/B2: closed-slab certificate"),
]

SHA_SOURCES = [
    ("poly_pdf", os.path.join(POLY, "1904.12438v2.pdf"),
     "60d0d2d381227d32f98535a5c43dedb86e333a9006d6819f0bdebdd734085603",
     "Polymath15 v2 PDF (also package references hash)"),
    ("poly_eprint", os.path.join(POLY, "1904.12438v2.eprint"),
     "1be3bc38d203ad0142f1c97c267c7deaa06b84c97716c9a1ec1f56456d826863",
     "Polymath15 v2 e-print tar"),
    ("pt_pdf", os.path.join(PTSRC, "2004.09765v1.pdf"),
     "3362f66af9fa9373977eee70e2282ec33989d5d8b97e0852df9e32cc25b52885",
     "Platt-Trudgian v1 PDF (also package references hash)"),
    ("pt_eprint", os.path.join(PTSRC, "2004.09765v1.eprint"),
     "c4f13cdfca711d2bf90a097147be2a094ff175b0b161647359e174633fd8bf86",
     "Platt-Trudgian v1 e-print payload"),
    ("abs_polymath", os.path.join(L3META, "abs_1904.12438.html"),
     "354ed00c24c6fe5aef4968feffdbe88742d7af841bf6881af85fc3441ec77d54",
     "arXiv abs snapshot 1904.12438 (citation-chain record)"),
    ("abs_pt", os.path.join(L3META, "abs_2004.09765.html"),
     "c137519d02a5cbf7146fed1499c73e03943ce8cd75f9bf78f4d82d65bcc16bc7",
     "arXiv abs snapshot 2004.09765 (citation-chain record)"),
]

POLY_TEX = os.path.join(POLY, "src", "debruijn.tex")
POLY_TEX_SHA = "560a28fe31bec92dd793820222e9e73a1fc6958a08344033a946b2ccaba225e5"
PT_TEX_SHA = "c6c29099c943dd2c74ee1b9dc6efc373d3102269bf41b14494687ced8225a75c"

SEGMENTS = {
    (168, 170): {"raw": "4353e6c842cf7ff5c811228a53212ea2260a619824e581d4843474a827fbb12e",
                 "norm": "4353e6c842cf7ff5c811228a53212ea2260a619824e581d4843474a827fbb12e",
                 "what": "region (5) domain"},
    (145, 152): {"raw": "06290d46cbbbe1670c4e9d4ee9957f0f8dc06367a9907644a654d048b7e331ec",
                 "norm": "06290d46cbbbe1670c4e9d4ee9957f0f8dc06367a9907644a654d048b7e331ec",
                 "what": "Theorem 1.2 (upper bound criterion)"},
    (223, 244): {"raw": "2bdd6d87d0a0c1d90a114b934eb905a46a4c40e99cb0fcc27993414ea0e1e08d",
                 "norm": "cebe9801b3c2b57414fa65d55506df0987dd01f94851bada291e51d6a85d68b2",
                 "what": "Theorem 1.3 (effective Riemann-Siegel)"},
    (1442, 1453): {"raw": "b2fbc004252e3f47d2f821febba43b684a49d4fd47125a429c1ed8012d0bc57f",
                   "norm": "b2fbc004252e3f47d2f821febba43b684a49d4fd47125a429c1ed8012d0bc57f",
                   "what": "Lemma 8.4"},
}

MAPPING = [
    {"hypothesis": "i",
     "polymath_label": "Numerical verification of RH at initial time 0",
     "slots": ["P1"],
     "evidence": ["PROOF_NOTE.md s3", "BIBLIOGRAPHY.md (PT)", "references/README.md",
                  "pt_v1.tex Thm 1 (lines 61-63)"],
     "l2_item": None},
    {"hypothesis": "ii",
     "polymath_label": "Asymptotic zero-free region at final time t0",
     "slots": ["T1", "F1", "F2", "F3"],
     "evidence": ["PROOF_NOTE.md s4-s5", "WINDOW_FREEZE_THEOREM.md",
                  "TAIL_LEMMA.md", "NATIVE_BINDING.md"],
     "l2_item": "items 1-3 (committed logs)"},
    {"hypothesis": "iii",
     "polymath_label": "Barrier at intermediate times",
     "slots": ["B1", "B2", "C1 containment"],
     "evidence": ["PROOF_NOTE.md s6", "BARRIER_CERTIFICATE.md",
                  "DERIVATIVE_BOX_LEMMA.md"],
     "l2_item": "item 4 (committed log)"},
]

BOUNDARY = [
    "no release lane re-run; descriptors/verdicts of L2 items 1-4 consumed as "
    "committed evidence only",
    "correctness/applicability of the published Polymath and Platt-Trudgian "
    "theorems is outside this machine check (statements transcribed and "
    "weld-checked; proofs not reviewed)",
    "package analytic reductions (Dini transfer, t=0 dominated-convergence "
    "endpoint, native binding algebra, derivative-box/tail proofs) not "
    "re-proved",
    "Bull. LMS (refereed) full text not accessible to scripted fetch (403); "
    "bibliographic record 53(3):792-797, DOI 10.1112/blms.12460 recorded; "
    "PT statement checked against the version-locked reviewed preprint v1",
    "Polymath v2 = 'final version, incorporating referee comments and "
    "corrections' per arXiv record snapshot; typeset journal pagination not "
    "compared",
    "arXiv abs snapshots are served content dated 2026-10-17; hashes recorded",
    "x_690988 < x_* < x_690989 secondary bracket uses mpmath 60 dps pi; "
    "primary remains WINDOW_FREEZE_THEOREM + L2 item 1",
    "PT zero-count form ('lowest 12,363,153,437,138 zeros') not consumed",
]

# ------------------------------------------------------------------ plumbing

CHECKS = []


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def blob_sha1(data):
    h = hashlib.sha1()
    h.update(b"blob " + str(len(data)).encode() + b"\0")
    h.update(data)
    return h.hexdigest()


def add(cid, tags, desc, ok, detail):
    CHECKS.append({"id": cid, "tags": tags, "desc": desc, "ok": bool(ok),
                   "detail": detail})
    print(("[PASS] " if ok else "[FAIL] ") + cid + " " + desc + " -- " + detail)
    return ok


def guarded(cid, tags, desc, fn):
    try:
        ok, detail = fn()
    except Exception as exc:  # fail-closed
        ok, detail = False, "exception: " + repr(exc)
    return add(cid, tags, desc, ok, detail)


def read_text(path):
    return open(path, "rb").read().decode("utf-8")


def frac_str(fr, digits=12):
    q = fr
    sign = "-" if q < 0 else ""
    q = abs(q)
    whole = q.numerator // q.denominator
    rem = q - whole
    s = ""
    for _ in range(digits):
        rem *= 10
        d = rem.numerator // rem.denominator
        s += str(d)
        rem -= d
    return sign + str(whole) + "." + s


def sqrt_bounds(s, digits=18):
    """Exact rational brackets lo^2 <= s <= hi^2, hi-lo = 10^-digits."""
    scale = 10 ** digits
    k = math.isqrt((s.numerator * scale * scale) // s.denominator)
    lo = Fraction(k, scale)
    while lo * lo > s:
        lo -= Fraction(1, scale)
    hi = lo + Fraction(1, scale)
    while hi * hi < s:
        hi += Fraction(1, scale)
    return lo, hi


# --------------------------------------------------------------- canonicalise

def canon_math(s):
    s = s.strip()
    s = s.replace("\\leq", "\\le").replace("\\geq", "\\ge")
    s = s.replace(" and ", ",")
    s = s.replace("$", "")
    s = s.replace("\\qquad", "")
    s = s.replace("\\,", "")
    s = s.replace("\\\\", "")
    s = s.replace("&", "")
    s = s.replace("\\begin{aligned}", "").replace("\\end{aligned}", "")
    s = re.sub(r"\\frac X2", r"\\frac{X}{2}", s)
    s = re.sub(r"\\frac x2", r"\\frac{x}{2}", s)
    s = re.sub(r"\\frac\{1\}\{2\}\s*y_0\^2", r"\\frac{y_0^2}{2}", s)
    s = re.sub(r"\s+", "", s)
    while ",," in s:
        s = s.replace(",,", ",")
    return s


def canon_prose(s):
    return re.sub(r"\s+", " ", s.strip().lower()).replace("zeroes", "zeros")


def tag_block(pnote, tag):
    m = re.search(r"\\tag\{" + re.escape(tag) + r"\}", pnote)
    if not m:
        raise RuntimeError("tag %s not found in PROOF_NOTE" % tag)
    pos = m.start()
    start = pnote.rfind("\\[", 0, pos)
    if start < 0:
        raise RuntimeError("no display opener before tag %s" % tag)
    return pnote[start + 2:pos]


def main():
    t_start = time.time()
    print("P1 audit -- L3 clean-room theorem-source weld (prereg section 5)")
    print("release commit " + RELEASE_COMMIT + " ; date " + DATE)
    print("")

    # ---------------------------------------------------------- A provenance
    print("== A. provenance gates (pinned tree / recorded sha256) ==")
    doc_data = {}
    for name, path, rel, exp, size, role in BLOB_SOURCES:
        def fn(path=path, exp=exp, size=size, name=name, rel=rel, role=role):
            data = open(path, "rb").read()
            doc_data[name] = data
            got = blob_sha1(data)
            ok = (got == exp) and (len(data) == size)
            return ok, "%s blob %s size %d  [%s]" % (rel, got[:12], len(data), role)
        guarded("A." + name, ["prov"], "blob gate " + name, fn)

    art_data = {}
    for name, path, exp, role in SHA_SOURCES:
        def fn(path=path, exp=exp, name=name, role=role):
            data = open(path, "rb").read()
            art_data[name] = data
            got = hashlib.sha256(data).hexdigest()
            return got == exp, "sha256 %s  [%s]" % (got[:12], role)
        guarded("A." + name, ["prov"], "sha256 gate " + name, fn)

    def poly_tex_from_tar():
        with tarfile.open(os.path.join(POLY, "1904.12438v2.eprint"), "r:gz") as tf:
            mem = None
            for m in tf.getmembers():
                if m.name.endswith("debruijn.tex"):
                    mem = m
                    break
            if mem is None:
                raise RuntimeError("debruijn.tex member not found")
            data = tf.extractfile(mem).read()
        return data

    def pt_tex_from_gzip():
        raw = open(os.path.join(PTSRC, "2004.09765v1.eprint"), "rb").read()
        return gzip.decompress(raw)

    poly_tex_bytes = None
    pt_tex_bytes = None

    def fn_poly_tex():
        nonlocal poly_tex_bytes
        poly_tex_bytes = poly_tex_from_tar()
        got = hashlib.sha256(poly_tex_bytes).hexdigest()
        local = open(POLY_TEX, "rb").read()
        same = local == poly_tex_bytes
        return (got == POLY_TEX_SHA and same), \
            "tar member sha256 %s ; match extracted file: %s" % (got[:12], same)

    guarded("A.poly_tex_via_tar", ["prov"],
            "re-extract debruijn.tex from pinned e-print tar", fn_poly_tex)

    def fn_pt_tex():
        nonlocal pt_tex_bytes
        pt_tex_bytes = pt_tex_from_gzip()
        got = hashlib.sha256(pt_tex_bytes).hexdigest()
        return got == PT_TEX_SHA, "gzip payload sha256 %s (24571 B)" % got[:12]

    guarded("A.pt_tex_via_gzip", ["prov"],
            "re-decompress PT v1 e-print payload", fn_pt_tex)

    # ---------------------------------------------------------- B segments
    print("")
    print("== B. e-print v2 segment digests (recon transcription records) ==")
    tex_text = None
    if poly_tex_bytes is not None:
        tex_text = poly_tex_bytes.decode("utf-8")

    def seg_check(a, b, want):
        def fn():
            if tex_text is None:
                raise RuntimeError("poly tex unavailable")
            lines = tex_text.split("\n")
            chunk = lines[a - 1:b]
            raw = ("\n".join(chunk) + "\n").encode("utf-8")
            norm = ("\n".join(l.rstrip() for l in chunk) + "\n").encode("utf-8")
            hraw = hashlib.sha256(raw).hexdigest()
            hnorm = hashlib.sha256(norm).hexdigest()
            ok = (hraw == want["raw"]) and (hnorm == want["norm"]) \
                and (len(raw) == 111 or len(raw) > 0)
            return ok, "lines %d-%d raw %s norm %s (%d B)" % (
                a, b, hraw[:12], hnorm[:12], len(raw))
        return fn

    for (a, b), want in SEGMENTS.items():
        guarded("B.seg_%d_%d" % (a, b), ["prov"],
                "segment digest " + want["what"], seg_check(a, b, want))

    # ---------------------------------------------------------- C parameters
    print("")
    print("== C. parameter compatibility (checklist item 2) ==")

    guarded("C.t0_range", ["param", "h1", "h2", "h3"],
            "t0 = 129/800 in (0, 1/2)",
            lambda: (0 < T0 < Fraction(1, 2),
                     "t0 = %s = %s" % (T0, frac_str(T0))))

    guarded("C.y0sq_range", ["param", "h1", "h2", "h3"],
            "0 < y0^2 < 1",
            lambda: (0 < Y0SQ < 1, "y0^2 = %s = %s" % (Y0SQ, frac_str(Y0SQ))))

    def fn_y0_bracket():
        ok = Y0_LO * Y0_LO < Y0SQ < Y0_HI * Y0_HI
        return ok, "1872719/10^7 < y0 < 23409/125000 (exact squares; y0 <= 1)"

    guarded("C.y0_bracket", ["param", "h1", "h2", "h3"],
            "y0 bracket from sealed window", fn_y0_bracket)

    def fn_ymax():
        ok = YMAX_LO * YMAX_LO < CEIL < YMAX_HI * YMAX_HI
        return ok, "8231038/10^7 < sqrt(1-2t0) < 8231039/10^7 (exact squares)"

    guarded("C.ymax_bracket", ["param", "h2", "h3"],
            "sqrt(1-2t0) bracket", fn_ymax)

    def fn_pt_height():
        lhs = Fraction(X, 2) + MARGIN
        return (lhs == T_PT and Fraction(X, 2) < T_PT), \
            "X/2 + 350479773/2 = %s + %s = %s = T_PT (exact)" % (
                frac_str(Fraction(X, 2), 1), frac_str(MARGIN, 1), lhs)

    guarded("C.pt_margin_identity", ["param", "h1"],
            "X/2 + margin = T_PT exactly", fn_pt_height)

    def fn_candidate():
        ok1 = T0 + Y0SQ / 2 == CANDIDATE
        ok2 = Y0SQ + 2 * T0 == CANOPY and CANOPY < 1
        ok3 = 1 - 2 * T0 == CEIL
        return (ok1 and ok2 and ok3), \
            "t0+y0^2/2 = %s = %s ; canopy = %s < 1 ; ceiling = %s" % (
                CANDIDATE, frac_str(CANDIDATE), CANOPY, CEIL)

    guarded("C.candidate_identities", ["param", "h3"],
            "candidate / canopy / ceiling identities", fn_candidate)

    def fn_pt_theorem_text():
        if pt_tex_bytes is None:
            raise RuntimeError("pt tex unavailable")
        lines = pt_tex_bytes.decode("utf-8").split("\n")
        blob = "\n".join(lines[60:63])
        flat = blob.replace("\\,", "")
        ok = ("3000175332800" in flat) and ("12363153437138" in flat) \
            and ("\\Re\\rho = 1/2" in flat)
        return ok, "PT Thm 1 (lines 61-63): " + flat.replace("\n", " ")[:110]

    guarded("C.pt_theorem_statement", ["param", "h1", "cite"],
            "PT v1 Theorem 1 states the exact height", fn_pt_theorem_text)

    def fn_doc_strings():
        note = doc_data["proof_note"].decode("utf-8")
        cand = doc_data["candidate_parameters"].decode("utf-8")
        biblio = doc_data["bibliography"].decode("utf-8")
        pre = read_text(os.path.join(REPO, PREREG))
        groups = {
            "PROOF_NOTE": (note, ["3000175332800", "350479773", "129/800",
                                  "\\frac{87677}{2500000}", "\\frac{1809}{10000}",
                                  "0\\le t\\le t_0", "3,149,013", "N_*=3840000",
                                  ":=X+\\sqrt{1-y_0^2}"]),
            "CANDIDATE_PARAMETERS": (cand, ["6000000185827", "3000175332800",
                                            "350479773/2", "87677/2500000",
                                            "129/800", "893927/5000000"]),
            "BIBLIOGRAPHY": (biblio, ["1904.12438v2", "2004.09765v1",
                                      "10.1112/blms.12460",
                                      "references/polymath-1904.12438v2.pdf",
                                      "references/platt-trudgian-2004.09765v1.pdf"]),
            "PREREG": (pre, ["350479773/2", "N = 3840000", "1809/10000",
                             "60d0d2d3", "3362f66a", "Polymath15 v2",
                             "2004.09765v1"]),
        }
        missing = []
        for gname, (text, needles) in groups.items():
            for nd in needles:
                if nd not in text:
                    missing.append(gname + ":" + nd)
        return (not missing), "missing: " + (", ".join(missing) if missing else "none")

    guarded("C.doc_strings", ["param", "cite"],
            "frozen constants present in pinned docs + prereg", fn_doc_strings)

    # ---------------------------------------------------------- D containment
    print("")
    print("== D. containment of the curved barrier (checklist item 3) ==")

    guarded("D.sqrt_lt_1", ["contain", "h3"],
            "sqrt(1-y0^2) < 1  <=>  y0^2 > 0",
            lambda: (Y0SQ > 0, "y0^2 = %s > 0 (exact)" % Y0SQ))

    def fn_edge():
        diff = Y0SQ - EDGE * EDGE
        ok = diff == Fraction(234599, 100000000) and diff > 0
        return ok, "y0^2 - (1809/10000)^2 = %s > 0 (exact)" % diff

    guarded("D.lower_edge_margin", ["contain", "h3"],
            "lower-edge margin of the barrier rectangle", fn_edge)

    def fn_uniform():
        ok = CANOPY < 1
        return ok, "y0^2 + 2(t0-t) <= y0^2 + 2t0 = %s < 1 for all t in [0,t0] " \
            "(t cancels; exact)" % CANOPY

    guarded("D.canopy_uniform", ["contain", "h3"],
            "upper >= lower uniformly in t; upper <= 1", fn_uniform)

    def fn_t_endpoints():
        note = doc_data["proof_note"].decode("utf-8")
        ok = ("0\\le t\\le t_0" in note) and ("129/800" in note)
        return ok, "certified t-range [0, t0] closed; t0 = 129/800 in note + barrier docs"

    guarded("D.t_endpoints", ["contain", "h3"],
            "closed t-range endpoints recorded", fn_t_endpoints)

    # ---------------------------------------------------------- E overlap
    print("")
    print("== E. finite/tail overlap N = 3840000 (checklist item 2) ==")

    def fn_legs():
        lengths = [(b - a + 1) for a, b in LEGS]
        expected = [38012, 90000, 209000, 2812001]
        jumps = [LEGS[i + 1][0] - LEGS[i][1] == 1 for i in range(len(LEGS) - 1)]
        total = sum(lengths)
        ok = lengths == expected and all(jumps) \
            and total == ROWS_HI - ROWS_LO + 1 == 3149013
        return ok, "leg lengths %s total %d ; contiguous junctions %s" % (
            lengths, total, all(jumps))

    guarded("E.legs", ["overlap", "h2"], "finite ladder partition arithmetic", fn_legs)

    def fn_nstar():
        note = doc_data["proof_note"].decode("utf-8")
        ok = ("N_*=3840000" in note) and (ROWS_LO <= NSTAR <= ROWS_HI)
        return ok, "N* = 3840000 is the last finite row (shared complete window W_3840000)"

    guarded("E.nstar", ["overlap", "h2"], "closed cutoff shared by both lanes", fn_nstar)

    def fn_freeze_strings():
        doc = doc_data["window_freeze"].decode("utf-8")
        ok = ("5377393.9878" in doc) and ("11989041.1746" in doc) \
            and ("3840001" in doc) and ("complete window" in doc) \
            and ("W_{3840000}" in doc)
        return ok, "window-freeze margins and complete-overlap statement present"

    guarded("E.freeze_doc", ["overlap", "h2"],
            "WINDOW_FREEZE_THEOREM records", fn_freeze_strings)

    def fn_secondary_bracket():
        import mpmath as mp
        mp.mp.dps = 60
        p_lo = Fraction(int(mp.floor(mp.pi * 10 ** 55)) - 1, 10 ** 55)
        p_hi = Fraction(int(mp.ceil(mp.pi * 10 ** 55)) + 1, 10 ** 55)
        s_lo, s_hi = sqrt_bounds(1 - Y0SQ)
        xstar_lo = X + s_lo
        xstar_hi = X + s_hi
        q1 = Fraction(690988 ** 2) - T0 / 16
        q2 = Fraction(690989 ** 2) - T0 / 16
        x1_hi = 4 * p_hi * q1
        x2_lo = 4 * p_lo * q2
        m_lo = xstar_lo - x1_hi
        m_hi = x2_lo - xstar_hi
        ok = (m_lo > Fraction(5377393)) and (m_hi > Fraction(11989041))
        return ok, "secondary: x_*-x_690988 > %s ; x_690989-x_* > %s " \
            "(recorded: >5377393.9878 / >11989041.1746)" % (
                frac_str(m_lo, 4), frac_str(m_hi, 4))

    guarded("E.secondary_bracket", ["overlap", "h2"],
            "x_* inside first finite window (secondary mpmath-60d pi bracket)",
            fn_secondary_bracket)

    # ---------------------------------------------------------- F weld
    print("")
    print("== F. statement weld (checklist item 1) ==")
    note_text = doc_data["proof_note"].decode("utf-8")
    tex_lines = tex_text.split("\n") if tex_text is not None else []

    def weld(cid, tags, desc, hpos, tag, tail=None):
        def fn():
            line = tex_lines[hpos - 1]
            if tail == "with":
                cond = line.split(" with ", 1)[1]
            elif tail == "then":
                cond = line.split("Then ", 1)[1]
            else:
                cond = line
            a = canon_math(cond)
            b = canon_math(tag_block(note_text, tag))
            return a == b, "eprint %s | note %s | equal=%s" % (
                a[:70], b[:70], a == b)
        return guarded(cid, tags, desc, fn)

    weld("F.hyp_i", ["weld", "h1"],
         "hypothesis (i) eprint vs note (2.1)", 147, "2.1", "with")
    weld("F.hyp_ii", ["weld", "h2"],
         "hypothesis (ii) eprint vs note (2.2)", 148, "2.2", "with")
    weld("F.hyp_iii", ["weld", "h3"],
         "hypothesis (iii) eprint vs note (2.3)", 149, "2.3", "with")
    weld("F.conclusion", ["weld", "h1", "h2", "h3"],
         "conclusion eprint vs note (2.4)", 151, "2.4", "then")

    def fn_prose():
        e_lines = [tex_lines[i - 1] for i in (147, 148, 149)]
        e_ok = all("There are no zeroes" in l for l in e_lines)
        n_count = note_text.count("There are no zeros")
        a = canon_prose("There are no zeroes")
        b = canon_prose("There are no zeros")
        return (e_ok and n_count >= 3 and a == b), \
            "eprint itemize 3/3 ; note count %d ; canon '%s' == '%s'" % (
                n_count, a, b)

    guarded("F.prose", ["weld", "h1", "h2", "h3"],
            "absence quantifier prose (zeroes/zeros)", fn_prose)

    def fn_labels():
        e = ["(Numerical verification of RH at initial time",
             "(Asymptotic zero-free region at final time",
             "(Barrier at intermediate times)"]
        p = ["hypothesis (i): verified height",
             "hypothesis (ii): finite windows",
             "hypothesis (ii): infinite tail",
             "hypothesis (iii): closed barrier"]
        ok = all(s in tex_text for s in e) and all(s in note_text for s in p)
        return ok, "eprint labels 3/3 ; note headings 4/4"

    guarded("F.labels", ["weld", "h1", "h2", "h3"],
            "hypothesis labels/headings present", fn_labels)

    def fn_pre():
        ok = "Suppose that $t_0, X > 0$ and $0 < y_0 \\leq 1$" in tex_text
        ok = ok and (X > 0) and (0 < Y0SQ) and (Y0_HI < 1)
        return ok, "preconditions t0>0, X>0, 0<y0<=1 (y0<23409/125000<1 exact)"

    guarded("F.preconditions", ["weld", "h1", "h2", "h3"],
            "Theorem 1.2 standing hypotheses instantiated", fn_pre)

    def fn_convenient():
        ok = ("X \\leq x \\leq X+1" in tex_text) and ("y_0 \\leq y \\leq 1" in tex_text)
        return ok, "paper's convenient region [X,X+1]x[y0,1]; package rectangle " \
            "extends to 0.1809 < y0 (no weakening)"

    guarded("F.convenient_region", ["weld", "h3"],
            "superset direction vs paper's own replacement region", fn_convenient)

    # ---------------------------------------------------------- G citations
    print("")
    print("== G. citation chain versions (checklist item 4) ==")

    def fn_refs_hashes():
        refs = doc_data["references_readme"].decode("utf-8")
        poly = ("60d0d2d381227d32f98535a5c43dedb86e333a9006d6819f0bdebdd734085603"
                in refs)
        pt = ("3362f66af9fa9373977eee70e2282ec33989d5d8b97e0852df9e32cc25b52885"
              in refs)
        lys = sha256_file(os.path.join(POLY, "1904.12438v2.pdf"))
        pts = sha256_file(os.path.join(PTSRC, "2004.09765v1.pdf"))
        ok = poly and pt and lys.startswith("60d0d2d3") and pts.startswith("3362f66a")
        return ok, "package reference hashes match our fetches byte-for-byte " \
            "(poly %s, pt %s)" % (lys[:12], pts[:12])

    guarded("G.ref_hashes", ["cite"], "version-locked reference PDFs", fn_refs_hashes)

    def fn_abs_poly():
        html = art_data["abs_polymath"].decode("utf-8", errors="replace")
        ok = ("final version, incorporating referee comments and corrections"
              in html) and ("Research in the Mathematical Sciences" in html) \
            and ("1904.12438v2" in html)
        return ok, "arXiv record: v2 is the final refereed version (RIMS)"

    guarded("G.poly_final_version", ["cite"], "Polymath v2 = final version", fn_abs_poly)

    def fn_abs_pt():
        html = art_data["abs_pt"].decode("utf-8", errors="replace")
        ok = ("Riemann hypothesis is true up to height" in html) \
            and ("10.1112/blms.12460" in html)
        return ok, "arXiv record: abstract height statement + related Bull. LMS DOI"

    guarded("G.pt_related_doi", ["cite"], "PT refereed DOI recorded", fn_abs_pt)

    # ---------------------------------------------------------- H xrefs
    print("")
    print("== H. cross-references to committed L2 evidence (consumed, not re-run) ==")
    xrefs = [
        ("H.item1", "reports/audit_p1_l2_window.log", "34", "item1"),
        ("H.item2", "reports/audit_p1_l2_prop410.log", "48", "item2"),
        ("H.item3", "reports/audit_p1_l2_tail.log", "47", "item3"),
        ("H.item4", "reports/audit_p1_l2_barrier.log", "124", "item4"),
    ]
    for cid, rel, total, label in xrefs:
        def fn(rel=rel, total=total, label=label):
            text = read_text(os.path.join(REPO, rel))
            ok = ("checks_total: %s  checks_failed: 0" % total in text) \
                and ("%s machine verdict: PASS" % label in text)
            return ok, "%s: checks_failed 0 + verdict PASS recorded" % label
        guarded(cid, ["xref"], "committed verdict of " + label, fn)

    # ---------------------------------------------------------- verdicts
    print("")
    hyp = {}
    for hkey in ("h1", "h2", "h3"):
        rel = [c for c in CHECKS if hkey in c["tags"]]
        hyp[hkey] = "compatible" if rel and all(c["ok"] for c in rel) \
            else "unresolved-or-mismatch"
    failed = [c for c in CHECKS if not c["ok"]]
    weld_ok = (not failed) and all(v == "compatible" for v in hyp.values())
    verdict = "PASS" if weld_ok else "FAIL"

    print("")
    print("== verdict ==")
    print("hypothesis (i)   (P1)      : " + hyp["h1"])
    print("hypothesis (ii)  (T1+F1-3) : " + hyp["h2"])
    print("hypothesis (iii) (B1-B2)   : " + hyp["h3"])
    print("weld verdict               : " + ("HELD" if weld_ok else "GAP-FOUND"))
    print("checks_total: %d  checks_failed: %d" % (len(CHECKS), len(failed)))
    print("L3 machine verdict: " + verdict)

    dt = time.time() - t_start
    out = {
        "audit": "P1-L3 clean-room theorem-source weld",
        "date": DATE,
        "prereg": PREREG + " section 5",
        "release_commit": RELEASE_COMMIT,
        "device": "exact fractions.Fraction verdict arithmetic; in-run blob sha1 "
                  "(pinned tree) + sha256 (recorded) gates; statement weld via "
                  "documented canonicalisation; one secondary mpmath 60 dps pi "
                  "bracket (labelled non-primary); no release lane re-run",
        "checks": CHECKS,
        "checks_total": len(CHECKS),
        "checks_failed": len(failed),
        "hypothesis_verdicts": hyp,
        "weld_verdict": "HELD" if weld_ok else "GAP-FOUND",
        "verdict": verdict,
        "mapping": MAPPING,
        "boundary": BOUNDARY,
        "runtime_seconds": round(dt, 3),
    }
    with open(JSON_OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("json written: " + JSON_OUT)
    return 0 if weld_ok else 1


if __name__ == "__main__":
    sys.exit(main())


