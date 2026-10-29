# P2 audit â€” pre-registration (Collatz convergence-verification record; Barina project)

Date: 2026-10-19 (local). Status: **PRE-REGISTERED BEFORE ANY AUDIT
EXECUTION.** At the time of this declaration no simulation of any target
trajectory, no sweep, no engine-vs-battery comparison, and no source scan of
the pinned tree has been executed for this audit. This file and the frozen
engines/batteries listed in Â§2 are committed and pushed BEFORE the first
audit command; the git commit time and the audit log's first entries record
the ordering. Read-only reconnaissance that PRECEDED this file is documented
in `reports/AUDIT_COLLATZ_RECON_2026-10-19.md`; that document is reference,
not result. Pre-freeze development checks of the engines are listed in Â§12;
they are not audit evidence.

## 1. Target and scope

- Target claims (third party, as published):
  - **C1** (project-site record claim, live page): "The convergence of all
    numbers below 2075 Ã— 2^60 (â‰ˆ 2^71.02) has been verified." with project
    log 2^68 (2020-05-07) â†’ 2^69 (2021-12-10) â†’ 2^70 (2023-07-09) â†’
    1.5Ã—2^70 (2023-11-03) â†’ 2^71 (2025-01-15); news text 2^68.
  - **C1p** (papers of record): Barina, J. Supercomput. 77:2681â€“2688 (2021),
    doi 10.1007/s11227-020-03368-x; Barina, J. Supercomput. 81:810 (2025),
    doi 10.1007/s11227-025-07337-0.
  - **C2** (records lists): the site path-records table ("known path records
    for all n below 2^71", 98 rows under the page's shortcut map,
    cross-listed with OEIS A006884); the standard-map height list OEIS
    A006885 (97 terms); the delay records OEIS A006877 / A006878 (148
    terms).
- Depots of record: pcbarina.fit.vutbr.cz pages (live; snapshot discipline
  in Â§4/S1); OEIS b-files (pinned by capture + hash, Â§2); repository
  github.com/xbarin02/collatz pinned at
  `e98d0294a7ff77e783907e307a80e83b92f4a164`.
- What this audit checks: items S (source snapshots), W (records replay by
  two independent engines), E (bounded independent sweep), H (textual
  claims), P (pin weld). Item **T** (compile and run the project's own
  worker) is EXCLUDED from v1 and recorded NOT-RUN (owner decision,
  2026-10-19): its audit value for C1/C2 is low relative to toolchain cost.
- Out of scope (explicit): the Collatz conjecture itself â€” no claim either
  way; any n â‰¥ 2^34 for the sweep; record-ness "for all m < n" beyond the
  published lists and internal monotonicity; performance claims (GPU
  speeds, work-unit timing); DOI landing pages and PDFs; arXiv:2602.10466;
  cycle-length bounds; the negative-number analogue; "verified" vocabulary
  beyond the maximum labels in Â§10.

## 2. Frozen artifacts and hashes

Hash convention: sha256LF (LF-normalized), the repository registry
convention. All frozen files below are LF-only, so sha256LF equals raw
sha256.

**(a) Captures** â€” `audit_collatz/captures/` (raw sha256; URLs and fetch
times in `captures/SOURCES.md`, sha256LF `d9220fbb...`):

| file | sha256 |
|---|---|
| site_path_records.html | c4cc03a16ab4c642c9b1fff65fcd82b3c156cbc6ad6074d07c712d406dba468b |
| site_news.html | 642dcfb92326b05eb623fa933cce7cfac77817d3416b6cb31bb7423386395ea3 |
| site_main.html | c31f4bbbdbcbe58778b75bb5c2ec4386ad57216f3c74a0ff53682bf24a48798e |
| oeis_A006884.txt | 657ec2fbc0ade279ce052005ae11234ea795c47b0fdaf9add6fff5d4f214de86 |
| oeis_A006885.txt | 7007b273e50fc2d51afba6e740b201ae61e3ae4f8b5898e3880bb6c5156bf053 |
| oeis_A006877.txt | 4bdd9c264ffb33f6252adad6716f8f0ad55c84687d4300a9bfbe646a1a81327f |
| oeis_A006878.txt | 1aebb537ac7cbb0290e8614b8e58e879efa24843277c0c437a72672f965233ac |

**(b) Batteries** â€” `audit_collatz/`:

| file | rows | sha256LF |
|---|---|---|
| battery_path_records.tsv | 98 | faa157b296f6fe4924b81eead8dd1182b4104e4af04110075a2bc6f22a0e54ad |
| battery_heights_std_a006885.tsv | 97 | 9f5bed262520a10bafb292d3f1cf689fc6914062ba70d24cb256e07db28cdbe0 |
| battery_delay_records.tsv | 148 | 09a252407f6cc89e40499b341671014a8622d3c545d2b636b9ec8a1b45f85cf5 |

**(c) Engines, tools, claims** â€” `audit_collatz/`:

| file | sha256LF |
|---|---|
| collatz_engine_p.py | 18e763a50eb640866902e765d1bb39712bf6799a188e4bbaaf5901a094d23f6c |
| collatz_engine_q.py | 6761704f3f3a7559284e120bb25cc830e74a37adae85fd8a7b8f94457c45c10a |
| collatz_sweep.c | 4c8572927229b9b041cab5c2a186503c2e9d5858524c120c487640c01a6ce365 |
| collatz_tools.py | e00c728bb6335a290a9e7cdae9ddebdd8224794d638895361259806785a00374 |
| build_batteries.py | 4e3b3f2972d1a90bdb11f00785f8c44e49c0f5a864afbfc9ff5afb4ae6d810f5 |
| claims_check.py | d97e074a263efc69fc181dae3b264478ccf00fd300a6ef10b9edec18c4b9d4c5 |
| claims_site.tsv | 1555901ec9caed798296abff62b53b49336667d8060a455ae317b9445833f01c |
| claims_repo.tsv | 3c20159e0b0c8e6a2870b33e7b5cfa4ae048bb915b4a26319b4195f45dfe3879 |

**(d) Non-modification.** `audit_bb5/artifact_checks.py` (registry-
certified; sha256LF
`03d69223587e4fcae9ecab30e96931de99ccb531db5e20ff988ba7cfd4762ff4`) is
REUSED unmodified for `sha256lf` and `weld-tar`.

## 3. Frozen conventions and semantics

- Shortcut map T(n) = (3n+1)/2 if n odd, n/2 if n even (the site's map).
  Standard map S(n) = 3n+1 if n odd, n/2 if n even.
- t_x(n) = maximum of the trajectory until 1, including n; steps_x(n) =
  number of map applications until 1.
- Drop-check semantics: for odd n, iterate T until a value < start appears;
  step cap 10^6; a cap hit is recorded and is never counted as success.
- Batteries: `path` (i,n,t(n) shortcut), `std` (i,n,t_std standard),
  `delay` (i,n,steps_std standard); indexes 1-based contiguous; `#` lines
  are comments.
- JSON comparisons: only the `result` subtrees are compared (top-level
  `tool`/`params` are excluded); engines must be byte-stable across
  repeated invocations in their `result` subtrees. `collatz_tools.py`
  modes: `compare` (deep equality), `compare-fields` (named fields),
  `compare-prefix` (C `prefix24` digest vs a Python result), `check-prefix`
  (records vs battery rows below the bound).
- Log and artifacts: execution starts by creating
  `reports/AUDIT_COLLATZ_LOG_<YYYY-MM-DD>.log` (all stdout/stderr appended
  via `tee`) and the directory `audit_collatz/exec_<YYYY-MM-DD>/` for every
  produced artifact (`$EXEC` below). First log entries: current date -u,
  host, `git rev-parse HEAD` (must equal the commit that pushed this file),
  sha256LF of the Â§2(b)/(c) files, sha256 of this file. Commands run
  sequentially ("satu dulu") with `nice -n 19`.

## 4. Item S â€” sources (frozen commands and expectations)

S1 site re-fetch and byte-compare (`curl.exe` 8.13.0, run from Windows):
```
curl.exe -fsSL -w "%{http_code}\n" -o "$EXEC/refetch/site_path_records.html" https://pcbarina.fit.vutbr.cz/path-records.htm
curl.exe -fsSL -w "%{http_code}\n" -o "$EXEC/refetch/site_news.html"         https://pcbarina.fit.vutbr.cz/news.htm
curl.exe -fsSL -w "%{http_code}\n" -o "$EXEC/refetch/site_main.html"         https://pcbarina.fit.vutbr.cz/
cmp "$EXEC/refetch/site_path_records.html" audit_collatz/captures/site_path_records.html
cmp "$EXEC/refetch/site_news.html"         audit_collatz/captures/site_news.html
sed -E 's/Generated: [^<]*/Generated: X/' "$EXEC/refetch/site_main.html" > "$EXEC/n_main_refetched"
sed -E 's/Generated: [^<]*/Generated: X/' audit_collatz/captures/site_main.html > "$EXEC/n_main_frozen"
cmp "$EXEC/n_main_refetched" "$EXEC/n_main_frozen"
```
Expectation: all comparisons pass; any other difference is a DISCREPANCY
recorded as-is (upstream drift; the batteries stay frozen).

S2 OEIS re-fetch and byte-compare:
```
curl.exe -fsSL -w "%{http_code}\n" -o "$EXEC/refetch/oeis_A006884.txt" https://oeis.org/A006884/b006884.txt
curl.exe -fsSL -w "%{http_code}\n" -o "$EXEC/refetch/oeis_A006885.txt" https://oeis.org/A006885/b006885.txt
curl.exe -fsSL -w "%{http_code}\n" -o "$EXEC/refetch/oeis_A006877.txt" https://oeis.org/A006877/b006877.txt
curl.exe -fsSL -w "%{http_code}\n" -o "$EXEC/refetch/oeis_A006878.txt" https://oeis.org/A006878/b006878.txt
cmp "$EXEC/refetch/oeis_A006884.txt" audit_collatz/captures/oeis_A006884.txt
cmp "$EXEC/refetch/oeis_A006885.txt" audit_collatz/captures/oeis_A006885.txt
cmp "$EXEC/refetch/oeis_A006877.txt" audit_collatz/captures/oeis_A006877.txt
cmp "$EXEC/refetch/oeis_A006878.txt" audit_collatz/captures/oeis_A006878.txt
```

S3 clone at the pin:
```
git -c core.autocrlf=false clone https://github.com/xbarin02/collatz.git "$EXEC/clone"
git -c core.autocrlf=false -C "$EXEC/clone" checkout --detach e98d0294a7ff77e783907e307a80e83b92f4a164
git -C "$EXEC/clone" rev-parse HEAD            # expect e98d0294a7ff77e783907e307a80e83b92f4a164
git -C "$EXEC/clone" rev-parse 'HEAD^{tree}'   # expect b290c47a7f3b4be37f1992e7ccd5bae2dafefa2f
```

S4 (identical to item P; one execution, recorded jointly):
```
curl.exe -fsSL -w "%{http_code}\n" -o "$EXEC/collatz-e98d0294.tar.gz" https://codeload.github.com/xbarin02/collatz/tar.gz/e98d0294a7ff77e783907e307a80e83b92f4a164
python3 audit_bb5/artifact_checks.py sha256lf "$EXEC/collatz-e98d0294.tar.gz"
python3 audit_bb5/artifact_checks.py weld-tar "$EXEC/collatz-e98d0294.tar.gz" "$EXEC/clone" --out "$EXEC/weld.json"
```
Expectation: `only_in_tarball` [], `only_in_clone` [], `changed` [],
`identical` 162. Differences are listed verbatim; no verdict beyond the
listing.

S5 battery re-derivation (frozen TSVs are never overwritten):
```
python3 audit_collatz/build_batteries.py "$EXEC/refetch" "$EXEC/batteries_re"
cmp "$EXEC/batteries_re/battery_path_records.tsv"          audit_collatz/battery_path_records.tsv
cmp "$EXEC/batteries_re/battery_heights_std_a006885.tsv"   audit_collatz/battery_heights_std_a006885.tsv
cmp "$EXEC/batteries_re/battery_delay_records.tsv"         audit_collatz/battery_delay_records.tsv
```
Expectation: byte-identical (given S1/S2); differences are upstream drift,
recorded as-is.

## 5. Items W â€” records replay (frozen commands and criteria)

All commands from the repository root, `nice -n 19`, output to `$EXEC`,
stdout/stderr to the log. Each engine is invoked twice on the same
batteries; the two `result` subtrees must be deep-equal (determinism).

W1a (`path`, shortcut t, 98 rows) / W1b (`std`, standard t, 97 rows) â€”
one invocation covers both:
```
python3 audit_collatz/collatz_engine_p.py w1 --path-battery audit_collatz/battery_path_records.tsv --std-battery audit_collatz/battery_heights_std_a006885.tsv --out "$EXEC/w1_p_r1.json"
python3 audit_collatz/collatz_engine_p.py w1 --path-battery audit_collatz/battery_path_records.tsv --std-battery audit_collatz/battery_heights_std_a006885.tsv --out "$EXEC/w1_p_r2.json"
python3 audit_collatz/collatz_tools.py compare "$EXEC/w1_p_r1.json" "$EXEC/w1_p_r2.json"
python3 audit_collatz/collatz_engine_q.py w1 --path-battery audit_collatz/battery_path_records.tsv --std-battery audit_collatz/battery_heights_std_a006885.tsv --out "$EXEC/w1_q_r1.json"
python3 audit_collatz/collatz_engine_q.py w1 --path-battery audit_collatz/battery_path_records.tsv --std-battery audit_collatz/battery_heights_std_a006885.tsv --out "$EXEC/w1_q_r2.json"
python3 audit_collatz/collatz_tools.py compare "$EXEC/w1_q_r1.json" "$EXEC/w1_q_r2.json"
python3 audit_collatz/collatz_tools.py compare "$EXEC/w1_p_r1.json" "$EXEC/w1_q_r1.json"
```
W2 (`delay`, standard steps, 148 rows): same pattern with
`collatz_engine_{p,q}.py w2 --battery audit_collatz/battery_delay_records.tsv`
and artifacts `w2_{p,q}_r{1,2}.json`; final compare
`compare "$EXEC/w2_p_r1.json" "$EXEC/w2_q_r1.json"`.

Criteria (all required): every `compare` prints MATCH; in `w1_*_r1.json`:
`mismatch_path == []`, `mismatch_std == []`, `cap_hits == []`,
`path_checked == 98`, `std_checked == 97`; in `w2_*_r1.json`:
`mismatches == []`, `cap_hits == []`, `checked == 148`. Mismatch lists carry
indexes; values stay in the JSONs.

## 6. Items E â€” bounded sweep (frozen commands and criteria)

Setup (counts against the setup cap): 
```
gcc -O2 -std=gnu11 -o "$EXEC/collatz_sweep" audit_collatz/collatz_sweep.c    # sha256 of the binary recorded
```

- E2 (2^24 cross-check, C vs Python):
```
"$EXEC/collatz_sweep" drop 24 --out "$EXEC/c_drop24.json"
python3 audit_collatz/collatz_engine_p.py e2 --bound 16777216 --out "$EXEC/p_e2_24.json"
python3 audit_collatz/collatz_tools.py compare-prefix "$EXEC/c_drop24.json" "$EXEC/p_e2_24.json"
```
  Criteria: `compare-prefix` prints MATCH; `cap_hits == []` in both JSONs.
- E3 (records prefix at 2^24):
```
python3 audit_collatz/collatz_engine_p.py e3 --bound 16777216 --path-battery audit_collatz/battery_path_records.tsv --out "$EXEC/p_e3_24.json"
"$EXEC/collatz_sweep" records 24 --out "$EXEC/c_rec24.json"
python3 audit_collatz/collatz_tools.py compare-fields "$EXEC/p_e3_24.json" "$EXEC/c_rec24.json" records record_count
python3 audit_collatz/collatz_tools.py check-prefix "$EXEC/c_rec24.json" audit_collatz/battery_path_records.tsv
```
  Criteria: `compare-fields` prints MATCH; `check-prefix` prints MATCH (38
  entries); `p_e3_24.json` has `prefix_compare.match == true` with
  `battery_rows_in_range == 38`.
- E1 (the 2^34 sweep; run last within E):
```
"$EXEC/collatz_sweep" drop 34 --out "$EXEC/c_drop34.json"
```
  Criteria: completes within the E budget (hard wall 3.5 h; otherwise
  SIGINT and record INCOMPLETE-BUDGET with the last complete progress
  boundary from the log; no output file is expected in that case);
  `result.cap_hits == []`. The `prefix24` block is recorded and
  (informational, expected equal) compared against `c_drop24.json` via
  `compare-prefix "$EXEC/c_drop34.json" "$EXEC/c_drop24.json"`; if E1 was
  interrupted, this block is recorded as not produced. No claim beyond the
  completed boundary.

## 7. Items H â€” textual claims (frozen commands and criteria)

```
python3 audit_collatz/claims_check.py audit_collatz/claims_site.tsv "$EXEC/refetch"
python3 audit_collatz/claims_check.py audit_collatz/claims_repo.tsv "$EXEC/clone"
```
H1 expectation: 25 rows, 0 miss (exit 0). H2 expectation: 14 rows, 0 miss
(exit 0). These are transcription matches only.

## 8. Caps and budget (frozen)

- setup (log open, C build, directories) â‰¤ 1 h; S â‰¤ 0.5 h; W â‰¤ 1 h; H â‰¤ 20
  min (inside the S/W envelope); P/S4 â‰¤ 30 min; E â‰¤ 4 h total (E2 and E3
  first, then E1 with a hard wall of 3.5 h). Total â‰¤ 6 h.
- Overruns are recorded as-is (UNRESOLVED-BUDGET); parameters are never
  changed in response to results.
- Load discipline: `nice -n 19` for everything; laptop otherwise idle; no
  other heavy tasks during the run ("satu dulu" ordering). P1 item R must
  be finished and an explicit owner signal given before the first command.

## 9. Discrepancy protocol (frozen)

- Any mismatch in S/W/E/H/P: record as DISCREPANCY with full details
  (command, complete output); rerun the exact command once; if persistent,
  investigate inside the budget and document. Never hand-edit expectations;
  never change parameters (k = 34, batteries, semantics, caps) in response
  to results.
- Upstream drift in S (site changed since captures): recorded as a finding;
  the frozen batteries remain the reference of record; H1 then reports the
  fragments still found and any missed.
- Tool fixes after the first execution are allowed only if the entire
  battery stays green and the fix plus final tool hashes are listed in the
  report changelog.
- The anti-circularity gate output is attached verbatim at report time and
  can only downgrade wording. For this probe the gate is expected to report
  TOOL NOT RUN (no Lean/Coq/SMT artifacts); recorded as-is. No Lean/Coq/SMT
  claim is made anywhere in P2.

## 10. Maximum labels (frozen wording; values filled at report time)

- S: "the named pages and the pinned revision were captured at the recorded
  times and hashed; the six expected-stable captures matched their freeze
  copies byte-for-byte; site_main.html matched after normalization of the
  Generated line only; the frozen quoted fragments were located verbatim;
  this is a snapshot, not a verdict."
- W: "every published path-record row (98), standard-height row (97), and
  delay-record row (148) was re-simulated by two independent in-repo
  engines; each trajectory reached 1 and the recomputed values equalled the
  published ones; the published lists' monotonicity was confirmed; the
  engines' result JSONs were deep-equal and re-run-stable. Finite
  arithmetic check; not peer review; not a proof of the conjecture."
- E: "an independent in-repo C engine checked that every odd n below 2^34
  reaches a value below itself under the shortcut map within the step cap
  of 10^6; the independently written Python engine reproduced the identical
  2^24 digest (drop metrics), and the recomputed record prefix below 2^24
  matched the published table (38 rows) between both engines. Bounded
  replay; no claim for any n â‰¥ 2^34."
- H: "the frozen quoted fragments were found verbatim in the captured pages
  and in the clone at the pinned commit; this is a transcription match
  only."
- P/S4: "the GitHub archive at the pinned commit was compared to a fresh
  clone file-by-file; differences are listed verbatim."
- T: "NOT-RUN â€” excluded from v1 scope by the owner decision recorded in
  this file."

## 11. Execution order and gates (frozen)

1. Preconditions: P1 item R finished; explicit owner signal; this file and
   the frozen set committed and pushed; CI green; `origin/main == HEAD`.
2. Open the log; record the Â§3 first entries.
3. S1 â†’ S2 â†’ S3 â†’ S4/P â†’ H1 + H2 â†’ S5.
4. W1a/W1b â†’ W2.
5. E2 â†’ E3 â†’ E1.
6. Report (`reports/AUDIT_COLLATZ_REPORT_<date>.md`) with the Â§10 labels and
   the Â§9 outcomes; then a registry extension (A-2026-0003) committed
   separately.

## 12. Development checks performed before freeze (not audit evidence)

- Selftests at the frozen revisions: engine P 18 checks OK; engine Q 523
  checks OK; engine C 5 checks OK (`gcc -O2 -std=gnu11`).
- Cross-language dev runs at bound 2^20 (dev-only scale, synthetic
  batteries only): P `e2 --bound 1048576` vs C `drop 20` `prefix24` â†’
  MATCH with identical values (`odd_checked = 524287`,
  `max_steps_to_drop = 183` at `argmax = 1027431`,
  `sum_drop = 203394374771`); P `e3 --bound 1048576` vs C `records 20` on
  `records`/`record_count` â†’ MATCH.
- Interface tests with synthetic batteries only: `compare-prefix`,
  `compare-fields`, `check-prefix` MATCH; tampered synthetic â†’ MISMATCH and
  exit 1; Pâ†”Q `compare` MATCH for synthetic `w1` and `w2`.
- Claims dry runs: `claims_site.tsv` 25/25 FOUND against the captures;
  `claims_repo.tsv` 14/14 FOUND against the pin.
- No engine ever read the frozen battery TSVs before this file (the first
  such read happens at execution); no target simulation beyond the dev
  bounds above; dev issues found and fixed before freeze (two hand-constant
  corrections in selftest tables; one key-access fix in `collatz_tools.py`);
  the hashes in Â§2 are of the final frozen files.

## 13. Artifacts, non-modifications, registry

- Produced at execution: `audit_collatz/exec_<date>/` (re-fetches, clone,
  tarball, `weld.json`, re-derived batteries, all JSONs), the audit log,
  the report, then a registry entry (A-2026-0003) for the executed
  artifacts (sha256LF), committed separately.
- Non-modifications: no existing file is edited; third-party artifacts are
  read-only; the Â§2 frozen files are never overwritten; no secrets are
  displayed; staging is per named file only.

## 14. Ordering proof

This file (with the engines, batteries, captures, and claims files) is
committed and pushed BEFORE the first audit command; the audit log's first
entries record `git rev-parse HEAD` (equal to this push) and the wall-clock
time; CI must be green for the push and `origin/main == HEAD` must hold.


