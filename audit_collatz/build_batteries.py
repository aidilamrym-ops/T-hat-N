#!/usr/bin/env python3
"""P2 (Collatz) freeze-time battery builder and transcription validator.

Reads the frozen recon captures (path-records page HTML + OEIS b-files),
validates internal consistency (indexes, monotonicity, B-column bit lengths,
ratio column, cross-source n-list equality, newest-row constants), runs the
freeze-time convention check on hand-traced rows only, and writes the battery
TSVs consumed by the audit engines.

Transcription artifacts only: no trajectory simulation beyond the hand-traced
convention-check rows (n=3, n=7, shortcut map).

Usage: python build_batteries.py [SRC_DIR] [OUT_DIR]
Defaults: SRC_DIR = C:\\Users\\usER\\AppData\\Local\\Temp\\opencode\\collatz_probe2
          OUT_DIR = directory of this script (audit_collatz/)

At execution time, this script may be re-run against freshly fetched sources
into a scratch OUT_DIR to re-derive batteries and diff them against the frozen
TSVs (item S5 of the pre-registration; the frozen TSVs are never overwritten).
"""
import hashlib
import math
import re
import sys
from pathlib import Path

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    r"C:\Users\usER\AppData\Local\Temp\opencode\collatz_probe2")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent

NEWEST_FIVE = [
    274133054632352106267,
    1378299700343633691495,
    1735519168865914451271,
    1765856170146672440559,
    2358909599867980429759,
]


def sha256_raw(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sha256_lf(p):
    return hashlib.sha256(Path(p).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


report = []


def log(s):
    report.append(s)
    print(s)


def shortcut_max_steps(n):
    """Convention-check helper only (hand-traced rows).

    T(n) = (3n+1)/2 if n odd, n/2 if n even (site convention).
    Returns (max value, step count) for the trajectory of n down to 1.
    """
    mx = n
    c = 0
    while n != 1:
        n = (3 * n + 1) // 2 if n & 1 else n // 2
        if n > mx:
            mx = n
        c += 1
    return mx, c


def parse_bfile(p):
    out = []
    for line in Path(p).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        a, b = line.split()
        out.append((int(a), int(b)))
    return out


log("P2 battery build report (freeze package transcription)")
log("SRC = %s" % SRC)
log("OUT = %s" % OUT)
log("")

src_names = ["site_path_records.html", "oeis_A006884.txt", "oeis_A006885.txt",
             "oeis_A006877.txt", "oeis_A006878.txt"]
hashes = {}
for name in src_names:
    p = SRC / name
    hr, hl = sha256_raw(p), sha256_lf(p)
    hashes[name] = hr
    log("source %-24s len=%-7d sha256=%s sha256LF=%s" % (name, p.stat().st_size, hr, hl))
log("")

# ---- path records (site table) ----
html = (SRC / "site_path_records.html").read_text(encoding="utf-8")
rx = re.compile(r"<tr><td>(\d+)</td><td>(\d+)</td><td>(\d+)</td><td>(\d+)</td><td>(\d+)</td><td>([0-9.]+)</td></tr>")
rows = rx.findall(html)
assert len(rows) == 98, "expected 98 rows, got %d" % len(rows)
precs = []
for k, (i, n, h, b1, b2, r) in enumerate(rows):
    i, n, h, b1, b2, r = int(i), int(n), int(h), int(b1), int(b2), float(r)
    assert i == k, "index gap at row %d" % k
    assert b1 == n.bit_length(), "B(n) column mismatch at row %d" % k
    assert b2 == h.bit_length(), "B(t(n)) column mismatch at row %d" % k
    if n > 1:
        assert abs(r - math.log2(h) / math.log2(n)) < 2.0e-6, "ratio column mismatch at row %d (%r)" % (k, r)
    if k:
        assert precs[-1][1] < n, "n not strictly increasing at row %d" % k
        assert precs[-1][2] < h, "t(n) not strictly increasing at row %d" % k
    precs.append((k + 1, n, h))
log("path-records table: 98 rows; indexes 0..97; n and t(n) strictly increasing;")
log("  B(n)/B(t(n)) bit-length columns and log-ratio column all verified")
# convention check (hand-traced rows; transcription interpretation only)
for n_check, expect in [(3, 8), (7, 26)]:
    mx, _ = shortcut_max_steps(n_check)
    assert mx == expect, "convention check failed for n=%d" % n_check
assert precs[2] == (3, 3, 8) and precs[3] == (4, 7, 26)
log("convention check (hand-traced): table t(3)=8 and t(7)=26 reproduce under the")
log("  shortcut map stated by the page (T(n)=(3n+1)/2 odd, n/2 even)")
assert [n for _, n, _ in precs[93:98]] == NEWEST_FIVE
log("newest five rows (i=94..98) equal the frozen 2025 constants")
log("")

# ---- OEIS A006884 (path-record starts; positional cross-check) ----
n884 = parse_bfile(SRC / "oeis_A006884.txt")
assert len(n884) == 98, len(n884)
for (i, n), (i2, n2, h) in zip(n884, precs):
    assert i == i2 and n == n2, "A006884 alignment mismatch at term %d" % i
log("A006884: 98 terms; identical to site table n column (positional, 98/98)")
log("")

# ---- OEIS A006885 (standard-convention heights; 97 terms; battery 2) ----
h885 = parse_bfile(SRC / "oeis_A006885.txt")
assert len(h885) == 97, len(h885)
for k, (i, h) in enumerate(h885):
    assert i == k + 1, "A006885 index gap at %d" % k
    if k:
        assert h885[k - 1][1] < h, "A006885 not strictly increasing at %d" % k
assert h885[2] == (3, 16) and h885[3] == (4, 52), "A006885 spot rows"
log("A006885: 97 standard-convention heights; strictly increasing;")
log("  spot rows (hand-traced): term 3 = 16 for n=3; term 4 = 52 for n=7")
log("")

# ---- OEIS A006877 + A006878 (delay records) ----
n877 = parse_bfile(SRC / "oeis_A006877.txt")
d878 = parse_bfile(SRC / "oeis_A006878.txt")
assert len(n877) == 148 and len(d878) == 148, (len(n877), len(d878))
for k in range(148):
    assert n877[k][0] == k + 1 and d878[k][0] == k + 1, "delay index gap at %d" % k
    if k:
        assert n877[k - 1][1] < n877[k][1], "A006877 not strictly increasing at %d" % k
        assert d878[k - 1][1] < d878[k][1], "A006878 not strictly increasing at %d" % k
assert n877[2] == (3, 3) and d878[2] == (3, 7), "delay spot row n=3"
log("A006877: 148 delay-record starts; strictly increasing")
log("A006878: 148 standard-convention delays; strictly increasing;")
log("  spot row (hand-traced): n=3 -> 7 standard steps")
log("")

# ---- coverage statistics (for the pre-registration text) ----
k24 = sum(1 for _, n, _ in precs if n < (1 << 24))
k34 = sum(1 for _, n, _ in precs if n < (1 << 34))
d24 = sum(1 for _, n in n877 if n < (1 << 24))
d34 = sum(1 for _, n in n877 if n < (1 << 34))
log("coverage: path rows below 2^24: %d ; below 2^34: %d" % (k24, k34))
log("coverage: delay rows below 2^24: %d ; below 2^34: %d" % (d24, d34))
log("first path row: n=%d t=%d ; last: n=%d t=%d" % (precs[0][1], precs[0][2], precs[-1][1], precs[-1][2]))
log("")

# ---- write batteries ----
OUT.mkdir(parents=True, exist_ok=True)
p1 = OUT / "battery_path_records.tsv"
with p1.open("w", encoding="ascii", newline="\n") as fh:
    fh.write("# battery_path_records.tsv | columns: i n t(n) | shortcut map (site convention)\n")
    fh.write("# source: captures/site_path_records.html sha256=%s\n" % hashes["site_path_records.html"])
    for i, n, h in precs:
        fh.write("%d\t%d\t%d\n" % (i, n, h))
p2 = OUT / "battery_heights_std_a006885.tsv"
with p2.open("w", encoding="ascii", newline="\n") as fh:
    fh.write("# battery_heights_std_a006885.tsv | columns: i n t_std(n) | standard map (3n+1, n/2)\n")
    fh.write("# sources: captures/oeis_A006885.txt sha256=%s ; n column = captures/oeis_A006884.txt sha256=%s\n"
             % (hashes["oeis_A006885.txt"], hashes["oeis_A006884.txt"]))
    for k, (_i, h) in enumerate(h885):
        fh.write("%d\t%d\t%d\n" % (k + 1, n884[k][1], h))
p3 = OUT / "battery_delay_records.tsv"
with p3.open("w", encoding="ascii", newline="\n") as fh:
    fh.write("# battery_delay_records.tsv | columns: i n steps_std(n) | standard map steps\n")
    fh.write("# sources: captures/oeis_A006877.txt sha256=%s ; captures/oeis_A006878.txt sha256=%s\n"
             % (hashes["oeis_A006877.txt"], hashes["oeis_A006878.txt"]))
    for k in range(148):
        fh.write("%d\t%d\t%d\n" % (k + 1, n877[k][1], d878[k][1]))

for p in (p1, p2, p3):
    log("wrote %-40s len=%-6d sha256=%s sha256LF=%s"
        % (p.name, p.stat().st_size, sha256_raw(p), sha256_lf(p)))

report_path = SRC / "battery_build_report.txt"
report_path.write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
print("report written: %s" % report_path)
print("BUILD OK")
