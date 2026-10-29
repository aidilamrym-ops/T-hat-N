#!/usr/bin/env python3
"""V1 freeze tool: build audit_ecdsa/seeds_manifest.json from the frozen captures.

The manifest fixes, per row, the COMPARISON value (source-captured standard seed
hex) plus every source occurrence; the claim's own printed strings are recorded
as a cross-check only. Deterministic: byte-identical on re-run (verified in
item I6). Aborts (exit 2) on any inconsistency.

Usage: build_manifest.py [--rows audit_ecdsa/v1_rows.tsv]
                         [--captures audit_ecdsa/captures]
                         [--out audit_ecdsa/seeds_manifest.json] [--quiet]
"""
import argparse
import datetime
import hashlib
import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent

P_NAMES = ["P-192", "P-224", "P-256", "P-384", "P-521"]
B_NAMES = ["B-163", "B-233", "B-283", "B-409", "B-571"]
V_CURVES = ["prime192v2", "prime192v3", "prime239v1", "prime239v2", "prime239v3"]
SEC_MAP = {
    "secp192r1": "P-192", "secp224r1": "P-224", "secp256r1": "P-256",
    "secp384r1": "P-384", "secp521r1": "P-521",
    "sect163r2": "B-163", "sect233r1": "B-233", "sect283r1": "B-283",
    "sect409r1": "B-409", "sect571r1": "B-571",
}
X962_ANCHORS = {
    "prime239v1": [6146, 6752],
    "prime239v2": [6769],
    "prime239v3": [6786],
    "prime192v2": [6712],
    "prime192v3": [6725],
}
SOURCE_META = {
    "claim-anthropic": {"origin": "https://www.anthropic.com/research/ecdsa-curve-origins", "role": "claim (verbatim) + cross-check strings"},
    "fips186-4": {"origin": "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.pdf", "role": "standards copy"},
    "fips186-2-change1": {"origin": "https://csrc.nist.gov/CSRC/media/Publications/fips/186/2/archive/2001-10-05/documents/FIPS186-2-change1.pdf", "role": "standards copy"},
    "sec2-v2": {"origin": "https://www.secg.org/sec2-v2.pdf", "role": "standards copy"},
    "x962-1998-draft": {"origin": "https://safecurves.cr.yp.to/grouper.ieee.org/groups/1363/private/x9-62-09-20-98.pdf", "role": "standards copy (archival mirror)"},
    "bc-java": {"origin": "https://raw.githubusercontent.com/bcgit/bc-java/main/core/src/main/java/org/bouncycastle/asn1/sec/SECNamedCurves.java", "role": "independent implementation table"},
    "neuromancer": {"origin": "https://neuromancer.sk/std/x962/<curve>/", "role": "independent curve database"},
    "saweis-context": {"origin": "https://saweis.net/posts/nist-curve-seed-origins.html", "role": "context only (derived from the neuromancer database; NOT a comparison source)"},
}
SOURCE_FILES = {
    "claim-anthropic": ["claim_anthropic_ecdsa_curve_origins.html", "claim_anthropic_ecdsa_curve_origins.txt"],
    "fips186-4": ["fips186-4.pdf", "fips186-4.txt"],
    "fips186-2-change1": ["fips186-2-change1.pdf", "fips186-2-change1.txt"],
    "sec2-v2": ["sec2-v2.pdf", "sec2-v2.txt"],
    "x962-1998-draft": ["x962-1998-draft.pdf", "x962-1998-draft.txt"],
    "bc-java": ["bc_SECNamedCurves.java"],
    "neuromancer": [f"neuromancer_{c}.html" for c in V_CURVES],
    "saweis-context": ["saweis_nist_curve_seed_origins.html"],
}
CLAIM_RE = re.compile(
    r"^(prime\d+v\d|P-\d{3}|B-\d{3})\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(\d+)\s+([0-9A-Fa-f]{40})\s*$",
    re.M,
)


def norm(h):
    return h.replace(" ", "").upper()


def sha256_lf(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def parse_rows(path):
    rows = []
    lines = pathlib.Path(path).read_text(encoding="utf-8").split("\n")
    if lines[0] != "id\trole\tcurve\tkind\tt_utc\tn\ti4":
        raise SystemExit(f"bad rows header: {lines[0]!r}")
    for line in lines[1:]:
        if not line.strip():
            continue
        f = line.split("\t")
        if len(f) != 7:
            raise SystemExit(f"bad row: {line!r}")
        rid, role, curve, kind, t_utc, n, i4 = f
        rows.append({"id": rid, "role": role, "curve": curve, "kind": kind,
                     "t_utc": t_utc, "n": None if n == "-" else int(n), "i4": i4 == "1"})
    return rows


def extract_fips186_4(text):
    out, cur = {}, None
    for ln, line in enumerate(text.split("\n"), 1):
        m = re.match(r"^\s*D\.\d+(?:\.\d+)*\s+Curve\s+([PBK]-\d+)\s*$", line)
        if m:
            cur = m.group(1)
            continue
        m = re.match(r"^\s*SEED\s*=\s*((?:[0-9a-fA-F]{8}\s*){5})", line)
        if m and cur in P_NAMES + B_NAMES:
            out.setdefault(cur, []).append((ln, norm(m.group(1))))
    return out


def extract_fips186_2c1(text):
    out, cur = {}, None
    for ln, line in enumerate(text.split("\n"), 1):
        m = re.match(r"^\s*Curve\s+([PBK]-\d+)\s*:?\s*$", line)
        if m:
            cur = m.group(1)
            continue
        m = re.match(r"^\s*s\s*=\s*((?:[0-9a-fA-F]{8}\s*){5})", line)
        if m and cur in P_NAMES + B_NAMES:
            out.setdefault(cur, []).append((ln, norm(m.group(1))))
    return out


def extract_sec2(text):
    out, cur = {}, None
    for ln, line in enumerate(text.split("\n"), 1):
        m = re.match(r"^\s*(?:\d+\.\d+\.\d+\s+)?Recommended Parameters\s+(sec[a-z0-9]+)\s*$", line)
        if m:
            cur = SEC_MAP.get(m.group(1))
            continue
        m = re.match(r"^\s*S\s*=\s*((?:[0-9a-fA-F]{8}\s*){5})", line)
        if m and cur:
            out.setdefault(cur, []).append((ln, norm(m.group(1))))
    return out


def extract_bc(java):
    out, cur = {}, None
    for ln, line in enumerate(java.split("\n"), 1):
        m = re.search(r"static X9ECParametersHolder\s+(sec[a-z0-9]+)\s*=", line)
        if m:
            cur = SEC_MAP.get(m.group(1))
            continue
        m = re.search(r'byte\[\] S = Hex\.decodeStrict\("([0-9A-Fa-f]{40})"\);', line)
        if m and cur:
            out.setdefault(cur, []).append((ln, norm(m.group(1))))
    return out


def extract_x962(text):
    lines = text.split("\n")
    out = {}
    for curve, anchors in X962_ANCHORS.items():
        for ln in anchors:
            line = lines[ln - 1]
            m = re.search(r"SEED\s*=\s*((?:[0-9A-Fa-f]{8}\s*){5})", line)
            if not m:
                raise SystemExit(f"x962 anchor miss: {curve} line {ln}: {line!r}")
            out.setdefault(curve, []).append((ln, norm(m.group(1))))
    return out


def extract_claim(text):
    out = {}
    for m in CLAIM_RE.finditer(text):
        name = m.group(1)
        if name in out:
            raise SystemExit(f"claim duplicate row: {name}")
        out[name] = {"t_utc": m.group(2), "n": int(m.group(3)), "hex": norm(m.group(4))}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", default=str(HERE / "v1_rows.tsv"))
    ap.add_argument("--captures", default=str(HERE / "captures"))
    ap.add_argument("--out", default=str(HERE / "seeds_manifest.json"))
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    captures = pathlib.Path(a.captures)
    rows = parse_rows(a.rows)

    captures_meta = {}
    for p in sorted(captures.iterdir()):
        if not p.is_file():
            continue
        data = p.read_bytes()
        captures_meta[f"audit_ecdsa/captures/{p.name}"] = {
            "bytes": len(data), "sha256_raw": hashlib.sha256(data).hexdigest(),
            "sha256_lf": sha256_lf(data),
        }

    texts = {n: (captures / n).read_text(encoding="utf-8", errors="replace")
             for n in ["fips186-4.txt", "fips186-2-change1.txt", "sec2-v2.txt",
                       "x962-1998-draft.txt", "claim_anthropic_ecdsa_curve_origins.txt",
                       "bc_SECNamedCurves.java"]}

    ex = {
        "fips186-4": extract_fips186_4(texts["fips186-4.txt"]),
        "fips186-2-change1": extract_fips186_2c1(texts["fips186-2-change1.txt"]),
        "sec2-v2": extract_sec2(texts["sec2-v2.txt"]),
        "bc-java": extract_bc(texts["bc_SECNamedCurves.java"]),
        "x962-1998-draft": extract_x962(texts["x962-1998-draft.txt"]),
    }
    ex_neuro = {}
    for c in V_CURVES:
        txt = html.unescape((captures / f"neuromancer_{c}.html").read_text(encoding="utf-8", errors="replace"))
        vals = set(norm(v) for v in re.findall(r'"seed"\s*:\s*"([0-9A-Fa-f]{40})"', txt))
        if len(vals) != 1:
            raise SystemExit(f"neuromancer {c}: expected 1 distinct seed, got {sorted(vals)}")
        ex_neuro[c] = [(f"neuromancer_{c}.html", vals.pop())]

    claim = extract_claim(texts["claim_anthropic_ecdsa_curve_origins.txt"])
    expected_claim = set(V_CURVES + P_NAMES + ["B-233", "B-283", "B-409", "B-571"])
    if set(claim) != expected_claim:
        raise SystemExit(f"claim table mismatch: missing={sorted(expected_claim - set(claim))} extra={sorted(set(claim) - expected_claim)}")

    wanted = {}
    for c in V_CURVES:
        wanted[c] = ["x962-1998-draft", "neuromancer"]
    for c in P_NAMES + B_NAMES:
        wanted[c] = ["fips186-4", "fips186-2-change1", "sec2-v2", "bc-java"]

    def get_occurrences(src, curve):
        if src == "neuromancer":
            return ex_neuro[curve]
        occ = ex[src].get(curve)
        return occ if occ else None

    rows_out = []
    for r in rows:
        curve = r["curve"]
        if curve not in wanted:
            raise SystemExit(f"no source mapping for {curve}")
        sources = []
        for src in wanted[curve]:
            occ = get_occurrences(src, curve)
            if not occ:
                continue
            hexes = {h for _, h in occ}
            if len(hexes) != 1:
                raise SystemExit(f"{src}:{curve}: inconsistent occurrences {occ}")
            ref = "captures/" + occ[0][0] if src == "neuromancer" else f"captures/{ {"fips186-4":"fips186-4.txt","fips186-2-change1":"fips186-2-change1.txt","sec2-v2":"sec2-v2.txt","x962-1998-draft":"x962-1998-draft.txt","bc-java":"bc_SECNamedCurves.java"}[src] } line " + ",".join(str(ln) for ln, _ in occ)
            sources.append({"id": src, "hex": hexes.pop(), "ref": ref})
        if len(sources) < 2:
            raise SystemExit(f"{curve}: fewer than 2 sources at freeze")
        std_hex = sources[0]["hex"]
        for s in sources:
            if s["hex"] != std_hex:
                raise SystemExit(f"{curve}: source disagreement {s['id']} {s['hex']} != {std_hex}")

        row = {
            "id": r["id"], "role": r["role"], "curve": curve, "kind": r["kind"],
            "n": r["n"], "std_hex": std_hex, "std_source": sources[0]["id"],
            "sources": sources, "i4": r["i4"],
        }
        if r["role"] == "reproduce":
            cl = claim[curve]
            if cl["t_utc"] != r["t_utc"] or cl["n"] != r["n"]:
                raise SystemExit(f"{curve}: claim table {cl['t_utc']}/{cl['n']} != rows tsv {r['t_utc']}/{r['n']}")
            epoch = int(datetime.datetime.strptime(r["t_utc"], "%Y-%m-%d %H:%M:%S")
                        .replace(tzinfo=datetime.timezone.utc).timestamp())
            row.update({
                "t_utc": r["t_utc"], "t_epoch": epoch,
                "seed_arg": epoch // 2 if r["kind"] == "binary" else epoch,
                "per": 5 if r["kind"] == "binary" else 20,
                "shift": 17 if r["kind"] == "binary" else 40,
                "width": 8 if r["kind"] == "binary" else 2,
                "claim_hex": cl["hex"],
            })
            if r["kind"] == "binary":
                row["seed_arg_mode"] = "floor(t_epoch/2)"
        else:
            row.update({"t_utc": None, "t_epoch": None, "seed_arg": None,
                        "per": None, "shift": None, "width": None, "claim_hex": None})
        rows_out.append(row)

    i4_rows = [r["curve"] for r in rows_out if r["i4"]]
    if sorted(i4_rows) != sorted(P_NAMES + B_NAMES):
        raise SystemExit(f"I4 row set wrong: {sorted(i4_rows)}")

    man = {
        "format": "replay-record/v0.1 seeds-manifest",
        "generated_by": "audit_ecdsa/build_manifest.py",
        "rows_file": "audit_ecdsa/v1_rows.tsv",
        "rows_file_sha256_lf": sha256_lf(pathlib.Path(a.rows).read_bytes()),
        "model": "srand48(t): x=(t&0xFFFFFFFF)<<16|0x330E; x=(0x5DEECE66D*x+0xB) mod 2^48; lrand48()=x>>17",
        "captures": captures_meta,
        "sources": {k: dict(v, files=SOURCE_FILES[k]) for k, v in SOURCE_META.items()},
        "rows": rows_out,
    }
    out = json.dumps(man, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    pathlib.Path(a.out).write_text(out, encoding="utf-8", newline="\n")

    if not a.quiet:
        print(f"manifest: {a.out}")
        for r in rows_out:
            extra = f"t_epoch={r['t_epoch']} seed_arg={r['seed_arg']} n={r['n']}" if r["role"] == "reproduce" else "seed_only"
            print(f"  {r['id']} {r['curve']:<11} {r['std_hex']}  src={len(r['sources'])}  {extra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


