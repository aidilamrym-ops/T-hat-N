# RR-2026-01: ECDSA curve seeds — reproduction of the published (t, n) -> seed mapping

- **id / registry_ref:** `RR-2026-01` / `A-2026-0004` (`reports/FENCE_REGISTRY.md`)
- **class:** `claim-reproduction`
- **resource_class:** light — measured execution wall 8 s (2026-10-19T02:00:15Z →
  02:00:23Z); frozen cap 60 min (prereg §5).
- **status:** COMPLETE. Per-item labels (no aggregate claim): I1 OK;
  I2 `10/10 MATCH`; I3 `4/4 MATCH`; I4 `MATCH`; I5 `MATCH`; I6 `MATCH`.
  Gate: `TOOL NOT RUN` (never counted as success).
- **frozen prereg:** `reports/AUDIT_ECDSA_PREREG_2026-10-19.md` (sha256LF
  `660e3cc6…3d89`), freeze commit `3026d12` pushed before the first audit
  command; record spec: `reports/REPLAY_RECORD_SPEC.md` v0.1.

## Claim

Source: Anthropic, "Claude reveals ECDSA curve origins" (2026-10-16),
https://www.anthropic.com/research/ecdsa-curve-origins — fetched 2026-10-19
01:24:11Z. Captures: `audit_ecdsa/captures/claim_anthropic_ecdsa_curve_origins.html`
(sha256LF `266554ce…8781d`) and `…_curve_origins.txt` (sha256LF
`35dfbdd8…77be`); quotes are byte-exact from the `.txt`, line numbers cited.

- **C1 (lines 29–30):** "In under half an hour, Claude discovered the origins of
  the NIST P-192, P-224, P-256, P-384, and P-521 seeds. None of them were the
  results of any hash algorithm at all, but rather the output of the C library’s
  lrand48 random-number generator, seeded with a Unix timestamp!"
- **C2 (line 31):** "The algorithm used would sample bytes from the random
  number generator (RNG) initialized by a Unix timestamp (t) for some number of
  iterations (n). Each iteration would draw 20 bytes as a candidate seed. So,
  the first 20 bytes are candidate 1, the next 20 bytes are candidate 2, and so
  on. For example, P-256 required 1,842 iterations to output the standardized
  seed."
- **C3 (line 37):** "Written as five 32-bit words, four of the ten seeds have a
  0 in the top bit for all 20 words. That would happen by chance with
  probability 1/5,810."
- **C3b (line 40):** "Five NIST prime-curve seeds plus five more from the ANSI
  X9.62 standard all had the same pattern: lrand48() >> 23."
- **C4 (line 43):** "However, for the ten prime-curve seeds, every srand48
  initialization was a Unix timestamp representing a date between May 1997 and
  April 1998. … The four binary-curve initializations read as February 1984.
  With the timestamps doubled, they map to April 17, 1998, two weeks after the
  P-224 run. So, the program may have halved the clock."
- **Residue (line 60):** "There is also one seed we were unable to recover. The
  fifth binary seed, B-163, fits nothing Claude has tried and remains
  unexplained."
- **Scope disclaimer (line 34):** "This is not a cryptographic break, new
  attack, or weakness in the ECDSA curves."
- The claim's own caveats are accepted as-is (lines 42/59): a `0x330E`-form
  state "would come up once every 65,536 steps, so reaching one is not evidence
  on its own", and "Nothing in the numbers shows how many runs there were".

The claim's input table (t, n per curve) was transcribed to
`audit_ecdsa/v1_rows.tsv`; the manifest build enforces transcription == capture
and records the claim's own printed seed strings as a cross-check only.

## Prerequisites

- **Toolchain** (frozen at the freeze commit; re-confirmed in log line 2):
  WSL2 `Ubuntu 26.04.1 LTS` (kernel `6.18.54.1-microsoft-standard-WSL2`); gcc
  `15.2.0-16ubuntu1` (`gcc -O2 -std=gnu11`); Python `3.14.4`; `nice`/`sha256sum`
  uutils coreutils `0.8.0`. Windows side (capture/git): curl `8.13.0`, git
  `2.53.0.windows.3`.
- **Host minima** (measured): 4 vCPU, 9 882 MB RAM, 3 072 MB swap — a single
  WSL2 VM on the owner's laptop (kept on); light-load discipline (`nice -n 19`),
  no parallel heavy tasks during the run.
- **Frozen package:** 29 files under `audit_ecdsa/` + 2 report files, pinned raw
  in `audit_ecdsa/PINS.sha256` (sha256LF `f64d66f5…56f7`, 3 021 B);
  `sha256sum -c` → 29/29 OK at execution start (log lines 4–33).

## Protocol (frozen)

- Freeze commit `3026d12cf6c25f72b48137f7c9bf646439886f59` ("V1 freeze package
  RR-2026-01…") was pushed BEFORE the first audit command; CI run `39187596038`
  green (python-tests + lean-kernel); `origin/main == HEAD`. Execution ran on
  exactly this commit; no parameter changes before or after.
- Engine model (POSIX/glibc spec; two independent engines + glibc weld):
  `srand48(t): x = ((t & 0xFFFFFFFF) << 16) | 0x330E; x = (0x5DEECE66D*x + 0xB) mod 2^48; lrand48() = x >> 17`.
  - Prime rows: candidate n = 20 successive states, each contributing
    `(state >> 40)` (i.e., `lrand48() >> 23`, one byte) formatted `%02X`.
  - Binary rows: candidate n = 5 successive states, each contributing
    `(state >> 17)` (`lrand48()`) formatted `%08X`; engine arg = `floor(t/2)`.
- Commands: exactly prereg §3 (`step 0` pin check + build; I1 selftest; I2–I6
  `run_v1.py` items); all output appended to the log via `tee -a` in one logged
  session; runner archived as `audit_ecdsa/exec_2026-10-19/v1_exec_steps.sh`
  (sha256LF `a7b20f21…9227f`).
- Dev-only vs audit boundary: development validation (KAT on 3 published rows,
  synthetic path tests) happened pre-freeze and is disclosed in prereg §6;
  every value cited below comes from the single audit session.

## Expected artifacts

| artifact | how to recompute | sha256LF (raw = LF; full in Certificates) |
|---|---|---|
| `audit_ecdsa/exec_2026-10-19/e1` | `gcc -O2 -std=gnu11` from `engine_e1.c` | `5188ed4eb174…d457` |
| `audit_ecdsa/exec_2026-10-19/e1w` | `gcc -O2 -std=gnu11` from `engine_e1w.c` | `0fcb720ed9bc…b77a` |
| `…/i1_selftest.json` | `selftest_v1.py --e1 … --e1w … --e2 … --json` | `80cc0d2c9d0c…4327` |
| `…/i2_prime.json` | `run_v1.py i2 --manifest … --e1 … --e2 …` | `22ed4fa09a30…7aac` |
| `…/i3_binary.json` | `run_v1.py i3 --manifest … --e1 … --e2 …` | `247f9e511d0e…1823` |
| `…/i4_wordstats.json` | `run_v1.py i4 --manifest …` | `1139975b4a0c…ef2d` |
| `…/i5_timestamps.json` | `run_v1.py i5 --manifest …` | `e1756ee8b5d1…6698` |
| `…/i6_sources.json` | `run_v1.py i6 --manifest …` | `da0eccfd38f3…e9b3` |
| `…/v1_exec_steps.sh` | runner archive (as-run) | `a7b20f214dec…227f` |
| `reports/AUDIT_ECDSA_LOG_2026-10-19.log` | as-is transcript | `07e7a6dcc05a…f8b5` |

Frozen inputs are pinned by `PINS.sha256` (verified with `-c`); the full
41-line certificate set is in registry `A-2026-0004`.

## Decision rules

As frozen (prereg §3, §8): I1 exit 0 + `SELFTEST: ALL OK` + JSON `all_ok:true`;
I2/I3 per-row `MATCH` iff `e1_cand == e2_cand == std_hex` (claim cross-check and
first-reappearance-at-n recorded as separate fields); I4 `count == 4` AND `1/P`
within ±1 % of the claim's 5,810; I5 all four subchecks; I6 min sources ≥ 2 +
all agree + manifest rebuild byte-identical. Discrepancy protocol: stop, record
as-is, dated decision before any proceed. Labels are per item; gates may only
downgrade; every label cites log lines + hashes.

## Results (as-is, per item)

**I1 — engine selftests (mechanistic; synthetic vectors; log lines 39–46).**
`[A] draws E1 == E1w (7 seeds x 250): OK`; `[B] draws E2 == E1 (same vectors):
OK`; `[C] draws range <= 0x7FFFFFFF: OK`; `[D] cand/scan equality + semantics
(36 subchecks): OK`; `SELFTEST: ALL OK`; `rc=0`; JSON `all_ok: true`. Label: OK
(not a claim item).

**I2 — prime rows R01–R10 (log lines 47–50).** Verbatim summary:
`{"item": "I2", "summary": {"all_match_std": true, "claim_crosscheck_mismatches": [], "n_match": 10, "n_mismatch": 0, "n_rows": 10, "rows_first_reappearance_not_at_n": []}}`
— label `10/10 MATCH`. For every row: `e1_cand == e2_cand == std_hex ==
claim_hex`, and the first reappearance index (scan) equals n on both engines.

src legend: X = `captures/x962-1998-draft`, N = neuromancer (5 pages),
F4 = `fips186-4`, F2 = `fips186-2-change1`, S2 = `sec2-v2`,
BC = `bc_SECNamedCurves.java`.

| id | curve | t (claim, UTC) | t_epoch | n | seed reproduced (= std = claim) | src |
|---|---|---|---|---|---|---|
| R01 | prime239v1 | 1997-05-15 15:49:03 | 863711343 | 2185 | E43BB460F0B80CC0C0B075798E948060F8321B7D | X,N |
| R02 | prime239v2 | 1997-05-15 15:49:03 | 863711343 | 2320 | E8B4011604095303CA3B8099982BE09FCB9AE616 | X,N |
| R03 | prime239v3 | 1997-05-15 15:49:03 | 863711343 | 3048 | 7D7374168FFE3471B60A857686A19475D3BFA2FF | X,N |
| R04 | P-192 | 1997-05-18 14:45:34 | 863966734 | 139 | 3045AE6FC8422F64ED579528D38120EAE12196D5 | F4,F2,S2,BC |
| R05 | prime192v3 | 1997-05-18 14:45:34 | 863966734 | 5228 | C469684435DEB378C4B65CA9591E2A5763059A2E | X,N |
| R06 | prime192v2 | 1997-05-18 14:45:34 | 863966734 | 6013 | 31A92EE2029FD10D901B113E990710F0D21AC6B6 | X,N |
| R07 | P-521 | 1997-08-08 01:12:04 | 871002724 | 1136 | D09E8800291CB85396CC6717393284AAA0DA64BA | F4,F2,S2,BC |
| R08 | P-256 | 1997-08-16 01:52:34 | 871696354 | 1842 | C49D360886E704936A6678E1139D26B7819F7E90 | F4,F2,S2,BC |
| R09 | P-384 | 1997-08-30 14:50:08 | 872952608 | 2688 | A335926AA319A27A1D00896A6773A4827ACDAC73 | F4,F2,S2,BC |
| R10 | P-224 | 1998-04-03 12:52:07 | 891607927 | 7026 | BD71344799D5C7FCDC45B59FA3B9AB8F6A948BC5 | F4,F2,S2,BC |

**I3 — binary rows R11–R14 (log lines 51–54).** Verbatim summary:
`{"item": "I3", "summary": {"all_match_std": true, "claim_crosscheck_mismatches": [], "n_match": 4, "n_mismatch": 0, "n_rows": 4, "rows_first_reappearance_not_at_n": []}}`
— label `4/4 MATCH`. Engine arg = `floor(t_epoch / 2)` (the claim's "halved
clock"); `e1_cand == e2_cand == std_hex == claim_hex`; scan = n on both engines.

| id | curve | t (claim, UTC) | t_epoch | arg | n | seed reproduced | src |
|---|---|---|---|---|---|---|---|
| R11 | B-233 | 1998-04-17 15:24:18 | 892826658 | 446413329 | 155 | 74D59FF07F6B413D0EA14B344B20A2DB049B50C3 | F4,F2,S2,BC |
| R12 | B-283 | 1998-04-17 15:27:44 | 892826864 | 446413432 | 32 | 77E2B07370EB0F832A6DD5B62DFC88CD06BB84BE | F4,F2,S2,BC |
| R13 | B-409 | 1998-04-17 15:30:18 | 892827018 | 446413509 | 60 | 4099B5A457F9D69F79213D094C4BCD4D4262210B | F4,F2,S2,BC |
| R14 | B-571 | 1998-04-17 15:32:08 | 892827128 | 446413564 | 73 | 2AA058F73A0E33AB486B0F610410C53A7F132310 | F4,F2,S2,BC |

**B-163 (R15):** no published (t, n) — NOT reproduced (residue; the claim,
line 60, agrees it was not recovered). Its published 160-bit seed
`85E25BFE5C86226CDB12016F7553F9D0E693A268` is used only as an I4 statistic
input.

**I4 — C3 word statistic (log lines 55–58).** Verbatim:
`{"count_all_top_bits_zero": 4, "item": "I4", "label": "MATCH", "subchecks": {"count_ok": true, "probability_within_tolerance": true}}`.
Count = 4: B-233, B-283, B-409, B-571 (top-bit words `00000` each); the other
six: P-192 `01111`, P-521 `10101`, P-256 `11001`, P-384 `11000`, P-224 `11110`,
B-163 `10101`. Exact: P(X≥4) = `48446969237/281474976710656`; 1/P =
`281474976710656/48446969237` = `5809.960481401744` vs the claim's 5,810
(relative deviation 6.8e-6 = 0.00068 % ≪ 1 %). Label: MATCH.

**I5 — C4 timestamps (log lines 59–62).** Verbatim:
`{"item": "I5", "label": "MATCH", "subchecks": {"doubled_dates_1998_04_17": true, "halved_dates_feb1984": true, "interval_b233_p224_floor_days_14": true, "prime_range_may1997_apr1998": true}}`.
Details: halved seed args read as `1984-02-23` for all four binary rows
(19:42:09 / 19:43:52 / 19:45:09 / 19:46:04 — February 1984 ✓); doubled dates →
`1998-04-17` (4/4); B-233 − P-224 = `1218731 s` = 14 d + 2 h 32 m 11 s (floor
14 = "two weeks" ✓); prime t range `1997-05-15 … 1998-04-03` (May 1997–April
1998 ✓).

**I6 — sources + packaging (log lines 63–66).** Verbatim:
`{"item": "I6", "label": "MATCH", "subchecks": {"min_sources_ge_2": true, "rebuild_from_captures_identical": true, "sources_all_agree_with_manifest": true}}`.
Source multiplicity: 2 per v-curve row (X9.62 draft + neuromancer DB), 4 per
NIST/binary row (FIPS 186-4 + FIPS 186-2 change-1 + SEC2 v2 + BouncyCastle);
all occurrences agree; manifest rebuild from the frozen captures is
byte-identical (determinism/packaging check).

## As-is log (pointer + sha256LF)

`reports/AUDIT_ECDSA_LOG_2026-10-19.log` — sha256LF
`07e7a6dcc05a7c90a25847deea696aaf2ba1cde9ef0ad2acc24e690e0c1ff8b5` (5 350 B, 76
lines). Single writer (`tee -a`); opened `2026-10-19T02:00:15Z`, closed
`02:00:23Z`; no appends after closure; no interruptions; no normalization
events.

## Failure ledger

None. Single attempt; every step `rc=0`; no interruptions, OOM kills, or
environment fixes; zero deviations from the pre-registered expected values
(prereg §7). Recorded as-is: nothing to record.

## Gate outputs (verbatim)

Command (repo root, 2026-10-19, post-execution):

    C:\Python314\python.exe C:\Users\usER\.config\opencode\skills\anti-circularity\scripts\gate.py check audit_ecdsa reports\AUDIT_ECDSA_PREREG_2026-10-19.md reports\REPLAY_RECORD_SPEC.md

Output:

```text
------------------------------------------------------------------------------
ANTI-CIRCULARITY GATE [check]
  NOT RUN  NO_LEAN_FILES: no .lean input matched
  result: FAIL=0  NOT_RUN=1  SKIP=0
  verdict: TOOL NOT RUN
GATE-EXIT=2
```

Exit 2 = `TOOL NOT RUN` — never counted as success. No Lean/SMT artifacts are in
this record's scope; no "machine-verified" wording is used for any result in
this record; every label rests on the log lines + hashes above.

## Certificates

sha256LF (raw = LF for all of these; execution set):

```text
sha256LF 07e7a6dcc05a7c90a25847deea696aaf2ba1cde9ef0ad2acc24e690e0c1ff8b5 reports/AUDIT_ECDSA_LOG_2026-10-19.log
sha256LF 5188ed4eb1740400252ce1db63f1d14a64e718cbbe8910fa549ae72a437bd457 audit_ecdsa/exec_2026-10-19/e1
sha256LF 0fcb720ed9bc67ccf8207b49981c0668f7833f63e72f2c45c28ce51ce0f3b77a audit_ecdsa/exec_2026-10-19/e1w
sha256LF 80cc0d2c9d0c0c1ed5581563acfbc96932bb1854409d566017ebf160ea974327 audit_ecdsa/exec_2026-10-19/i1_selftest.json
sha256LF 22ed4fa09a30ae2f787d966915766a3e8b1a21d84fbe4d933c39b7563fd67aac audit_ecdsa/exec_2026-10-19/i2_prime.json
sha256LF 247f9e511d0efdbe7a76b8f41f9b678b54d9006e8e7cc5d7a41ddab6e7201823 audit_ecdsa/exec_2026-10-19/i3_binary.json
sha256LF 1139975b4a0cc3f058291048ac0b8de5692af4a1ca4676167975d31a4adfef2d audit_ecdsa/exec_2026-10-19/i4_wordstats.json
sha256LF e1756ee8b5d1d12ef8f24b040c2ff1cbb1a6883fe440f754492ce4c504da6698 audit_ecdsa/exec_2026-10-19/i5_timestamps.json
sha256LF da0eccfd38f319d2dde559de7559e49d8578d3ca61bfe7c8a5de275b1368e9b3 audit_ecdsa/exec_2026-10-19/i6_sources.json
sha256LF a7b20f214dec09531b0d23f6d728a6f324a0c384a212a12544c3065c9919227f audit_ecdsa/exec_2026-10-19/v1_exec_steps.sh
```

Frozen inputs: `audit_ecdsa/PINS.sha256` sha256LF `f64d66f5…56f7` (29/29 via
`sha256sum -c`); prereg `660e3cc6…3d89`; spec `669db7ab…8805`. The full
41-line certificate set (spec + prereg + log + this report + 11 frozen package
files + 17 captures + 9 execution artifacts) is in registry `A-2026-0004`;
guard `msaf/tests/test_fence_registry.py` re-verifies every line in CI.

## Non-claims

- Not a statement about ECDSA security; not a break/attack/weakness analysis
  (the claim page says so itself, line 34).
- Not proof that the NSA actually ran lrand48 — no archival program was obtained
  or executed; the model match reproduces the published mapping, not a recovered
  artifact. The claim's own caveats (lines 42/59: the 1-in-65,536 state
  alignment is weak evidence on its own; the number of runs is invisible) stand.
- Base points, skipped candidates (e.g., P-256 candidate 876), and the B-163
  derivation are out of scope (residues kept open, never claims).
- The claim's t strings are printed without a timezone; this record reads them
  as UTC (every published row matches under that reading; another reading would
  move timestamps, not the 160-bit matches).
- Not a novelty/priority statement; not an independent confirmation of the
  provenance story (single public source; independence here is from the
  claimant's *code*, not from the claim text).
- Excluded during the source survey: OpenSSL `ec_curve.c` (v-curves present, no
  seed values), Crypto++ `eccrypto.cpp` (no seed fields), `sawes.net`
  (unreachable); the `saweis.net` page is context only.
- B-163's (t, n): NOT-RUN by construction (not published).
- Does not state or deny RH or P≠NP.

## Record provenance

- 2026-10-19 01:24–01:30Z: captures frozen (17 files; `SOURCES.md` records
  origins/hashes/fetch times); 01:56Z: freeze commit `3026d12` pushed
  (CI `39187596038` green).
- 02:00:15Z–02:00:23Z: audit execution on `3026d12` (agent session; owner GO
  2026-10-19; laptop kept on; light load only).
- This report + execution artifacts + log are committed in the commit carrying
  this file; registry entry `A-2026-0004` + seal row in the following commit.
- Roles: agent (OpenCode session) = execution + record authoring; owner = GO +
  repo maintainer. Frozen reports are never edited; the registry/record update
  is the record.

## Replay guide

1. Clone at the record commit: `sha256sum -c audit_ecdsa/PINS.sha256` → expect
   29/29 `OK` (raw sha256 by design; the two PDFs' LF-normalised hashes differ
   and are recorded separately in `SOURCES.md`).
2. Build: `gcc -O2 -std=gnu11 -o e1 audit_ecdsa/engine_e1.c` and
   `gcc -O2 -std=gnu11 -o e1w audit_ecdsa/engine_e1w.c`.
3. Run `audit_ecdsa/exec_2026-10-19/v1_exec_steps.sh` (WSL/bash; adjust the
   repo path at its top if your checkout differs) — or the exact commands from
   prereg §3 directly.
4. Expected diffs on replay: log timestamps + host line, and `e1`/`e1w` hashes
   if the toolchain differs (binaries are build artifacts, not pinned). All 8
   JSON outputs are expected byte-identical (deterministic; no timestamps
   inside). If any JSON differs, the affected item is MISMATCH — report it,
   do not paper over it.
5. Guard: `python -m pytest msaf/tests/test_fence_registry.py -q` (green; the
   registry re-verifies every certificate line in this record).
