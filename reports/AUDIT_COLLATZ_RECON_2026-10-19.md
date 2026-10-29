# P2 audit â€” reconnaissance (Collatz convergence-verification record; Barina project)

Date: 2026-10-19 (local). Status: **reference, not result.** Read-only
fetches. No trajectory simulation, no sweep, no engine-vs-battery
comparison, and no source scan of the pinned tree was executed for this
audit before the pre-registration file
`reports/AUDIT_COLLATZ_PREREG_2026-10-19.md` was committed. This document
records what was read, from where, and under which identifiers, so the
pre-registered expectations can be checked against pinned public sources.
The engines were written during this reconnaissance; their pre-freeze
development checks are listed in the pre-registration (Â§12) and are
explicitly not audit evidence.

## 1. Target claims (verbatim fragments; live site = snapshot discipline)

Project of David Barina (FIT VUT Brno); site `pcbarina.fit.vutbr.cz`.

- Main page (frozen capture `captures/site_main.html`, sha256 `c31f4bbb...`):
  - "The convergence of all numbers below 2075 &times; 2<sup>60</sup>
    (&asymp; 2<sup>71.02</sup>) has been verified. The work unit is
    2<sup>40</sup> numbers. On modern GPUs, verification of one work unit
    takes 5 seconds on average."
  - Progress heading: "Progress towards verifying all numbers below
    2076 &times; 2<sup>60</sup>"; snapshot lines "Lowest incomplete:
    17.8734 % (work unit 2175982616 &times; 2<sup>40</sup>, all work units
    below are verified)" and "Lowest unassigned: 17.8734 % (work unit
    2175982616 &times; 2<sup>40</sup>, all work units below are assigned or
    even verified)". The percentage is not interpreted anywhere; these are
    snapshot lines of a live page.
  - Project log, verbatim: "2019-09-04 started the project"; "2020-05-07 the
    convergence of all numbers below 2^68 is verified"; "2021-12-10 the
    convergence of all numbers below 2^69 is verified"; "2023-07-09 the
    convergence of all numbers below 2^70 is verified"; "2023-11-03 the
    convergence of all numbers below 1.5 Ã— 2^70 is verified"; "2025-01-15
    the convergence of all numbers below 2^71 is verified".
  - References to the papers of record: Barina, D. J Supercomput 77,
    2681â€“2688 (2021), doi 10.1007/s11227-020-03368-x; Barina, D. J
    Supercomput 81, 810 (2025), doi 10.1007/s11227-025-07337-0.
- News page (`captures/site_news.html`, sha256 `642dcfb9...`): "On May 7,
  2020, I managed to verify this conjecture for all numbers below
  $2^{68}$."; "The results confirm that the highest number occurring in the
  Collatz sequence starting at $n$ grows to approximately $n^2$." (Its meta
  description still carries the 2^68 line â€” stale vs the main-page log;
  recorded as-is.)
- Path-records page (`captures/site_path_records.html`, sha256
  `c4cc03a1...`):
  - the map, verbatim: T(n) = ((3n+1)/2 if n is odd, or n/2 if n is even)
    rendered as a `\begin{cases}` block â€” the shortcut map;
  - "Define $t(n)$ the highest number occurring in the sequence starting at
    $n$."; "The $n$ is called the path record if for all $m &lt; n$ the
    inequality $t(m) &lt; t(n)$ holds.";
  - "The following table lists the known path records for all $n$ below
    $2^{71}$."; column note "$B(n)$ and $B(t(n))$ are the sizes of their
    arguments measured in the number of bits.";
  - "Lagarias and Weiss (1992) predicted using the theory for random walks
    that limsup log t(n)/log n = 2."; "In other words, the highest number
    occurring in the sequence for a path record $n$ grows like $n^2$."

All fragments above are frozen in `audit_collatz/claims_site.tsv` (25 rows)
and are checked verbatim at execution time (item H1).

## 2. Pinned sources, captures, and byte-stability

### 2.1 Frozen captures (7 files)

Full table with URLs and hashes: `audit_collatz/captures/SOURCES.md`.
Summary: site main / path-records / news pages; OEIS b-files A006884,
A006885, A006877, A006878 â€” all fetched over HTTPS, all LF-only.

### 2.2 Stability check (freeze-time; reference only)

All seven URLs were re-fetched once with `curl.exe` 8.13.0: six were
byte-identical to their captures; `site_main.html` differed from an earlier
capture (`ebdf4f29...`) only in the generated line
`Generated: Sun, 18 Oct 2026 20:06:19 +0200`. The frozen copy is the later
fetch (`c31f4bbb...`). The audit freezes a normalization rule for exactly
that line (item S1) and nothing else.

### 2.3 OEIS

- A006884: 98 terms = the path-record starts (site n column); no header
  line.
- A006885: 97 terms = the same starts under the standard map (heights,
  standard convention); header verbatim: "A006885 b-file, terms 1..84 from
  T. D. Noe, extended to n=97 using data from E. Rosendaal's 3x+1 Path
  Records by Hugo Pfoertner 2025-01-13".
- A006877 / A006878: 148 terms each (record starts / standard-map delays);
  headers verbatim: "A006877 b-file using data from
  http://www.ericr.nl/wondrous/delrecs.html as of 2024-08-06" (A006878
  analogous). Spot check (hand trace): n = 3 has delay 7 under the standard
  map (3â†’10â†’5â†’16â†’8â†’4â†’2â†’1), matching term 3.
- URL rule: b-file basename drops the leading "A" (`b006884.txt`).

### 2.4 Repository of record

`github.com/xbarin02/collatz`, MIT, pinned commit
`e98d0294a7ff77e783907e307a80e83b92f4a164` (2026-10-15T13:38:58Z, message
"port 5008", author David Barina; tree
`b290c47a7f3b4be37f1992e7ccd5bae2dafefa2f`; parent
`141e13aae243d509a01a43bec597f53a5b97a09f`; unsigned). 162 tracked blobs.
API facts at recon: id 200282545, created 2019-08-02, default branch
`master`, license MIT, size 1088 KB, stars 86.

Documents fetched raw at the pin (sha256 of raw bytes, recorded as
expectations): `README.md` `74623d12...` (1320 B); `doc/ALGORITHM.md`
`49b070bd...` (1030 B); `doc/PROTOCOL.md` `07d79c12...` (1862 B). Frozen
quote fragments in `audit_collatz/claims_repo.tsv` (14 rows), checked at
execution (item H2) against the fresh clone.

### 2.5 Recon corpus (Temp; not committed)

`C:\Users\usER\AppData\Local\Temp\opencode\collatz_probe2\` â€” fingerprints
of the working materials: earlier `site_main.html` variant `ebdf4f29...`;
re-fetch copies `chk_barina_main.htm` `c31f4bbb...`,
`chk_barina_pathrecords.htm` `c4cc03a1...`, `chk_barina_news.htm`
`642dcfb9...`, `chk_A006877.txt` `4bdd9c26...`, `chk_A006884.txt`
`657ec2fb...` (all byte-identical to captures); `site_delrecs.html`
`59dd4ca4...` (ericr.nl context, HTTP); owner-review drafts
`P2_COLLATZ_PREREG_DRAFT_v0.md` `a8c84135...` and
`P2_COLLATZ_RECON_MATERIALS_v0.md` `8de35bf5...` (superseded by this file
and the pre-registration); freeze-time battery build log
`battery_build_report.txt` `953a8d21...`.

## 3. Conventions and transcription (verified; hand-traced tiny rows only)

- Maps: shortcut `T(n) = (3n+1)/2` (odd), `n/2` (even) â€” the site's own
  map; standard `S(n) = 3n+1` (odd), `n/2` (even).
- `t_x(n)` = maximum of the trajectory of n until 1 (including n);
  `steps_x(n)` = number of map applications until 1.
- Hand-traced checks (transcription interpretation only):
  - shortcut: t(3) = 8 (5 steps), t(7) = 26 (11 steps), t(15) = 80;
  - standard: t_std(3) = 16 (7 steps), t_std(7) = 52 (16), t_std(15) = 160
    (17); A006885 spot terms 3â†’16, 4â†’52;
  - drop (first value below start under T): 3â†’(4,2), 7â†’(7,5), 15â†’(7,10),
    27â†’(59,23).
- Table structural checks (all pass at build): 98 rows, indexes 0..97
  (battery indexes 1..98); n and t(n) strictly increasing; B() columns
  equal bit lengths; log-ratio column equals log2 t / log2 n within 2e-6;
  A006884 n column identical positionally (98/98); the five newest rows
  equal the frozen 2025 constants.
- Coverage of the frozen batteries: path rows with n < 2^24: 38; n < 2^34:
  47; delay rows with n < 2^24: 57; n < 2^34: 76. A006885 stops at 97 terms
  (the 98th site row has no standard-height b-file term yet); W1b checks
  the 97.

## 4. Frozen batteries (reference)

- `audit_collatz/battery_path_records.tsv` â€” 98 rows, columns `i n t(n)`,
  shortcut-map t; sha256LF `faa157b2...`.
- `audit_collatz/battery_heights_std_a006885.tsv` â€” 97 rows, `i n t_std`,
  standard-map t; sha256LF `9f5bed26...`.
- `audit_collatz/battery_delay_records.tsv` â€” 148 rows, `i n steps_std`,
  standard-map steps; sha256LF `09a25240...`.

Reproducible from the captures by `audit_collatz/build_batteries.py`
(re-run and diffed at execution, item S5). The frozen TSVs are never
overwritten.

## 5. Environment (verified 2026-10-19)

Host: Windows + WSL2 Ubuntu; WSL python3 3.14.4; WSL gcc 15.2.0; Windows
python 3.14.4; `curl.exe` 8.13.0 (Windows). RAM 9.7 GiB, 2 cores; audit
runs are nice-19 and sequential.

## 6. What this reconnaissance did NOT do

- No target simulation, sweep, or battery comparison; no source scan of the
  pinned tree beyond fetching the three quoted documents; no reproduction
  of the 2^71 limit (out of reach on this host); no claim about the Collatz
  conjecture; no RH / Pâ‰ NP content.
- Engine development checks (selftests, â‰¤2^20 cross-runs, synthetic-only
  battery interfaces, claims-file dry runs) are documented in the
  pre-registration Â§12 and are explicitly not audit evidence.

## 7. Context-only items (not audited)

- `ericr.nl` (E. Roosendaal 3x+1 pages incl. "delrecs"): the HTTPS endpoint
  failed certificate verification at recon (curl exit 60); the HTTP site
  serves the classic pages. Not part of the target set; the OEIS b-files
  (which cite ericr.nl as their data source) are the pinned record used.
- Cycle-length bound 217976794617 (Wikipedia, 2025) â€” context only.
- arXiv:2602.10466 (V. Angeltveit, Feb 2026) â€” context only.

## Appendix A â€” five newest path records (battery rows 94..98, n column)

274133054632352106267; 1378299700343633691495; 1735519168865914451271;
1765856170146672440559; 2358909599867980429759.

(Their t(n) values are in the frozen battery.)


