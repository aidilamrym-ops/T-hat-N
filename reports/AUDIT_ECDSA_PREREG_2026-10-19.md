# Audit V1 â€” ECDSA curve seeds: reproduction of the published (t, n) -> seed mapping

## Replay Record RR-2026-01 â€” PRE-REGISTRATION (FROZEN)

- Frozen: 2026-10-19 (this file + the frozen engines/tools/captures are committed
  together BEFORE the first audit command; git history is the ordering proof).
  No audit command runs before this commit is pushed and CI is green.
- Record format: `reports/REPLAY_RECORD_SPEC.md` v0.1 (frozen, same commit).
  Record id: **RR-2026-01**. Registry entry planned: **A-2026-0004** (post-execution).
- Claim source: Anthropic, "Claude reveals ECDSA curve origins" (2026-10-16),
  https://www.anthropic.com/research/ecdsa-curve-origins â€” captured 2026-10-19
  01:24:11 UTC; html sha256LF `266554ce...8781d`, txt sha256LF `35dfbdd8...77be`
  (full pins in section 2 / `audit_ecdsa/PINS.sha256`). Quotes below are byte-exact
  from the capture .txt (line numbers cited; the capture renders the page's curly
  punctuation).

## 0. Claim under test (verbatim quotes)

Key statements (line refs into `audit_ecdsa/captures/claim_anthropic_ecdsa_curve_origins.txt`):

- C1 (lines 29â€“30): "None of them were the results of any hash algorithm at all,
  but rather the output of the C libraryâ€™s lrand48 random-number generator, seeded
  with a Unix timestamp!"
- C2 (line 31): "The algorithm used would sample bytes from the random number
  generator (RNG) initialized by a Unix timestamp (t) for some number of iterations
  (n). Each iteration would draw 20 bytes as a candidate seed. So, the first 20
  bytes are candidate 1, the next 20 bytes are candidate 2, and so on. For example,
  P-256 required 1,842 iterations to output the standardized seed."
- C3 (line 37): "Written as five 32-bit words, four of the ten seeds have a 0 in
  the top bit for all 20 words. That would happen by chance with probability 1/5,810."
- C3b (line 40): "Five NIST prime-curve seeds plus five more from the ANSI X9.62
  standard all had the same pattern: lrand48() >> 23."
- C4 (line 43): "for the ten prime-curve seeds, every srand48 initialization was a
  Unix timestamp representing a date between May 1997 and April 1998" ... "The four
  binary-curve initializations read as February 1984. With the timestamps doubled,
  they map to April 17, 1998, two weeks after the P-224 run. So, the program may
  have halved the clock."
- Residue (line 60): "There is also one seed we were unable to recover. The fifth
  binary seed, B-163, fits nothing Claude has tried and remains unexplained."
- Context only (lines 25â€“26, NOT tested here): the 2015 Solinas quote about a
  humorous passphrase ("Give Bob and Jerry a raise" / "Bob and Jerry rule").
- Also noted, NOT tested here (line 57): skipped candidates (e.g., P-256 candidate
  876 "gives a prime-order curve of the right size"); we do not analyze curve
  selection criteria.

Claim input table (the claim's published t/n values, transcribed to
`audit_ecdsa/v1_rows.tsv`; the manifest build enforces transcription == claim
capture, and records the claim's own printed seed strings as cross-check):

| id | curve | t (claim; interpreted as UTC) | n |
|---|---|---|---|
| R01 | prime239v1 | 1997-05-15 15:49:03 | 2185 |
| R02 | prime239v2 | 1997-05-15 15:49:03 | 2320 |
| R03 | prime239v3 | 1997-05-15 15:49:03 | 3048 |
| R04 | P-192 | 1997-05-18 14:45:34 | 139 |
| R05 | prime192v3 | 1997-05-18 14:45:34 | 5228 |
| R06 | prime192v2 | 1997-05-18 14:45:34 | 6013 |
| R07 | P-521 | 1997-08-08 01:12:04 | 1136 |
| R08 | P-256 | 1997-08-16 01:52:34 | 1842 |
| R09 | P-384 | 1997-08-30 14:50:08 | 2688 |
| R10 | P-224 | 1998-04-03 12:52:07 | 7026 |
| R11 | B-233 | 1998-04-17 15:24:18 | 155 |
| R12 | B-283 | 1998-04-17 15:27:44 | 32 |
| R13 | B-409 | 1998-04-17 15:30:18 | 60 |
| R14 | B-571 | 1998-04-17 15:32:08 | 73 |
| R15 | B-163 | (none published; residue) | â€” |

Comparison values (the target seeds) come ONLY from the captured standard
documents/implementation (see SOURCES.md); the claim's printed strings are never
a comparison source.

## 1. Scope

Reproduce, from the claim's published (t, n): the standardized seed strings of the
10 prime curves (5 NIST + 5 X9.62 v-curves) and 4 binary curves (B-233, B-283,
B-409, B-571), using two independently written engines both faithful to the POSIX/
glibc `srand48`/`lrand48` specification; plus the claim's word-structure statistic
(C3), the timestamp arithmetic (C4), and source multiplicity (I6). Full non-claims
in section 9. Out of scope: base points, skipped candidates, B-163 derivation,
security implications.

## 2. Frozen artifacts (pins; sha256LF; raw = LF unless noted)

Engines (reimplemented from the POSIX/glibc spec of srand48/lrand48; NOT from the
claim's code):

| file | bytes | sha256LF |
|---|---|---|
| audit_ecdsa/engine_e1.c | 4909 | b939b8fdf6482dcb07cf3f8f24197600cf63c53e3c109a440a0947b04d8a89cd |
| audit_ecdsa/engine_e1w.c | 815 | 3ecd223ea7d73f8ac370b08d3c2dd8f7370d0188762b4cb6b7e3825ea83f96f7 |
| audit_ecdsa/engine_e2.py | 2240 | b5ae8c2b6c9e17b435ce6b17cb0425884565699bc13cd8371b867d551a4e3c98 |

Tools and data:

| file | bytes | sha256LF |
|---|---|---|
| audit_ecdsa/selftest_v1.py | 5345 | 788556901d7d3d7c2b61222c696c0b29d978d19e266fda27a275b02f215325b1 |
| audit_ecdsa/run_v1.py | 9782 | 9654766ca8d53481cd07623dae776cfbdd645d98a2063bb5ba4abda279f0b91b |
| audit_ecdsa/build_manifest.py | 12759 | a0fcd9e1c37aa95d91809773ccf98187e000fd0af60c6d63f0258fb2a8b76fcc |
| audit_ecdsa/tool_claim_text.py | 1419 | 2ec7baec006783b1fdeb80c9f7f25cae04aefff57ad8440dada67d261049f3d7 |
| audit_ecdsa/v1_rows.tsv | 826 | e27c3202aab424a68759da435d95da3bc5a70042f282c4b5f0b9ae1249f236fe |
| audit_ecdsa/seeds_manifest.json | 22588 | 3b39e4e5ad41ff00f8e1f5b97f7f6d1357424c5e908c85b7a7605eec259ba6d4 |
| audit_ecdsa/SOURCES.md | 8445 | 8ac938dc75c31fc498d2096cba70e7b88b5711433b3203c26604badae86335dd |
| reports/REPLAY_RECORD_SPEC.md | 11844 | 669db7ab045c770fa2d04792da710a9a3f7ed3a9d685fefcc92e073321038805 |

Captures (17 files under `audit_ecdsa/captures/`): transitively pinned by
`seeds_manifest.json` ("captures" block: size + raw + LF sha256 per file) and
mirrored human-readably in `SOURCES.md`. PDFs are byte-pinned raw and committed
unconverted (`.gitattributes`: `audit_ecdsa/**/*.pdf binary`; they contain CRLF
byte pairs, so raw sha256 != sha256LF â€” both values recorded).

Machine-checkable companion: `audit_ecdsa/PINS.sha256` (raw sha256 for every
package file including captures; generated after this prereg â€” it contains this
file's sha256 â€” and verified with `sha256sum -c` at freeze; re-verified at
execution start; any mismatch = STOP).

Engines are built at execution from the pinned sources; the source pins above are
verified before building. Binaries themselves are execution artifacts (hashed
into the log), not frozen.

## 3. Items, exact commands, criteria

Execution environment (as measured at freeze): WSL2 Ubuntu 26.04.1 LTS (kernel
6.18.54.1-microsoft-standard-WSL2), gcc 15.2.0-16ubuntu1, Python 3.14.4,
pdftotext 26.01.0, nice/sha256sum uutils coreutils 0.8.0; Windows curl 8.13.0,
git 2.53.0.windows.3. All commands run in WSL from the repo root; git commands run
from PowerShell only. Log wrapper for every step:

    bash -lc 'set -o pipefail; cd "/mnt/d/Opencode AI Agent" && <COMMANDS> 2>&1 | tee -a reports/AUDIT_ECDSA_LOG_2026-10-19.log'

Step 0 â€” pin check + build (log):

    sha256sum -c audit_ecdsa/PINS.sha256
    mkdir -p audit_ecdsa/exec_2026-10-19
    gcc -O2 -std=gnu11 -o audit_ecdsa/exec_2026-10-19/e1  audit_ecdsa/engine_e1.c
    gcc -O2 -std=gnu11 -o audit_ecdsa/exec_2026-10-19/e1w audit_ecdsa/engine_e1w.c
    sha256sum audit_ecdsa/exec_2026-10-19/e1 audit_ecdsa/exec_2026-10-19/e1w

Stop condition: any pin mismatch or nonzero `sha256sum -c` => STOP (no fixes; a
change would be a new version).

I1 â€” engine self-tests (mechanistic; synthetic vectors):

    nice -n 19 python3 audit_ecdsa/selftest_v1.py --e1 audit_ecdsa/exec_2026-10-19/e1 --e1w audit_ecdsa/exec_2026-10-19/e1w --e2 audit_ecdsa/engine_e2.py --json audit_ecdsa/exec_2026-10-19/i1_selftest.json

   A) draws E1==E1w (7 seeds x 250); B) draws E2==E1; C) range 31-bit;
   D) cand/scan equality + semantics (2 formats x 3 t x 3 n = 18 cases x 2
   checks = 36 subchecks; mutated no-match target brute-force verified).
   Criterion: exit 0, "SELFTEST: ALL OK", JSON `all_ok: true`. Else STOP â€”
   engines stay frozen; no substitution, no edits (that would itself be a finding).

I2 â€” prime rows (R01â€“R10): regenerate seed at candidate n and compare to the
source-captured standard seed:

    nice -n 19 python3 audit_ecdsa/run_v1.py i2 --manifest audit_ecdsa/seeds_manifest.json --e1 audit_ecdsa/exec_2026-10-19/e1 --e2 audit_ecdsa/engine_e2.py --out audit_ecdsa/exec_2026-10-19/i2_prime.json

   Model per row: srand48(t_epoch); candidate n = the n-th block of 20
   successive states, each contributing one byte ((state >> 40), i.e.,
   lrand48() >> 23, the top 8 bits), formatted %02X and concatenated (40 hex).
   Criterion per row: MATCH iff
   e1_cand == e2_cand == std_hex. Recorded separately (not part of the label):
   first-reappearance index via scan (expected n), and claim-string cross-check
   (e1_cand == claim_hex; expected equal for all 14 published rows).

I3 â€” binary rows (R11â€“R14): same protocol; per candidate: 5 successive states,
   each contributing (state >> 17) = lrand48() formatted %08X (32-bit word
   slots), concatenated (40 hex); engine arg = floor(t_epoch / 2) ("halved
   clock"); B-163 has no published (t, n)
   and is NOT reproduced (residue; only its word structure is used in I4):

    nice -n 19 python3 audit_ecdsa/run_v1.py i3 --manifest audit_ecdsa/seeds_manifest.json --e1 audit_ecdsa/exec_2026-10-19/e1 --e2 audit_ecdsa/engine_e2.py --out audit_ecdsa/exec_2026-10-19/i3_binary.json

Criterion: as I2.

I4 â€” word-structure statistic (C3): for the 10 NIST seeds (5 P + 5 B, incl.
   B-163 from sources), count seeds whose five 32-bit words all have top bit 0;
   recompute P(X >= 4), X ~ Binomial(10, 2^-5), exact rational:

    nice -n 19 python3 audit_ecdsa/run_v1.py i4 --manifest audit_ecdsa/seeds_manifest.json --out audit_ecdsa/exec_2026-10-19/i4_wordstats.json

   Criterion: count == 4 AND 1/P within +/-1% of the claim's 5,810. (Pre-derived
   during dev, section 6: P(X>=4) = 48446969237/281474976710656 ~= 1.7215e-4;
   1/P = 281474976710656/48446969237 ~= 5809.96.)

I5 â€” timestamp arithmetic (C4):

    nice -n 19 python3 audit_ecdsa/run_v1.py i5 --manifest audit_ecdsa/seeds_manifest.json --out audit_ecdsa/exec_2026-10-19/i5_timestamps.json

   Subchecks: (a) halved seed args of the four binary rows read as February 1984;
   (b) doubled values land on 1998-04-17; (c) floor((t_B233 - t_P224)/86400) == 14
   days; (d) prime rows' t span May 1997..April 1998. Criterion: all four (each
   recorded verbatim; exact intermediate values in JSON).

I6 â€” sources + packaging:

    nice -n 19 python3 audit_ecdsa/run_v1.py i6 --manifest audit_ecdsa/seeds_manifest.json --out audit_ecdsa/exec_2026-10-19/i6_sources.json

   Subchecks: (a) every row has >= 2 independent sources; (b) all source
   occurrences agree with the manifest value; (c) rebuilding the manifest from
   the frozen captures is byte-identical to the pinned manifest (determinism /
   packaging check).

I7 â€” record: hash the exec artifacts, run the anti-circularity gate (expected:
   the Lean/SMT checks have no targets in scope -> TOOL-NOT-RUN, recorded
   verbatim; NEVER counted as success), write the record `RR-2026-01`
   (reports/AUDIT_ECDSA_REPORT_2026-10-19.md), extend the fence registry
   (A-2026-0004), run the registry guard test, commit, CI green, update HANDOFF.

## 4. Conventions (carried from P2; binding)

- As-is: stdout/stderr appended via `tee -a`; failures kept; no editing during
  runs; no retro-editing; append-only logs.
- One item at a time; `nice -n 19` for engine runs; light/zero-load discipline
  during runs (laptop stays on).
- sha256LF (CRLF->LF) for all certificate lines; raw sha256 where explicitly
  noted (PDFs, PINS.sha256).
- Byte policy: `.gitattributes` pins `audit_ecdsa/** text eol=lf`,
  `audit_ecdsa/**/*.pdf binary`, and this prereg + the spec `text eol=lf`
  (same commit as this prereg).
- Git from PowerShell only; never from WSL. Stage only named files. Secrets
  are never displayed.
- Frozen files are never edited; any fix = new version + dated decision BEFORE
  retry (recorded in the log).
- Labels: MATCH / MISMATCH / PARTIAL / NOT-RUN / TOOL-NOT-RUN; per-item, never
  aggregate. No verdict without evidence (log lines + hashes).

## 5. Preconditions and budget

Preconditions: BB5 phase R complete (2026-10-18); Collatz P2 finalized
(A-2026-0003, 2026-10-19); owner GO (2026-10-19); this freeze commit pushed and
CI green; no uncommitted changes to tracked files (untracked P2 bulk artifacts
stay untracked by design).

Budget: light class. Caps (wall): step 0 <= 5 min; I1 <= 10 min; I2 <= 20 min;
I3 <= 10 min; I4/I5/I6 <= 5 min each; total <= 60 min. Expected actual: ~1 min.
Overrun is recorded as-is (no retries in the same run).

## 6. Development disclosure (pre-freeze; dev artifacts are NOT audit evidence)

- Engines were developed and tested in a Temp dev dir before freeze. During dev,
  two scan-mode bugs (candidate vs draw indexing; per x nmax loop bound) were
  found by the D selftest and fixed BEFORE the frozen hashes in section 2. No
  audit results existed at fix time.
- Dev cross-checks (disclosed; will be re-run at execution as I1/I2/I3 on the
  frozen hashes): KAT on 3 published (t, n) pairs (P-256 n=1842, prime239v2
  n=2320, B-233 n=155) matched on both engines; synthetic i2/i3 path tests and
  real-manifest I4/I5/I6 dry runs passed (values in section 7 pre-derive from
  these).
- The claimant's public page â€” INCLUDING its reproduction code block â€” was read
  by the agent during research (2026-10-18). Engines were nonetheless written
  from the POSIX/glibc specification of srand48/lrand48; independence rests on:
  (a) two engines agreeing; (b) both welded to the actual glibc lrand48 (E1w)
  on independent vectors; (c) comparison seeds come from standard documents,
  not from the claim.
- Temp dev scripts (kat_dev.py, synth_test.py, hash_lf.py, wrap_lines.py) stay
  in Temp; they are not part of the audit package.
- This prereg was drafted in Temp, then re-read and frozen as committed.

## 7. Expected outcomes (pre-registered)

- I1: ALL OK (Aâ€“D; D = 36 subchecks).
- I2: 10/10 MATCH (R01â€“R10); no claim cross-check mismatches; first-at-n true.
- I3: 4/4 MATCH (R11â€“R14).
- I4: count = 4; 1/P ~= 5809.96 (within +/-1% of 5,810) -> MATCH.
- I5: all four subchecks true (halved 1984-02-23; doubled 1998-04-17; interval
  14 days + 2h32m11s, floor 14; prime span 1997-05-15..1998-04-03).
- I6: min sources = 2; all agree; rebuild byte-identical -> MATCH.
- I7: gate output recorded; registry A-2026-0004; CI green.
- Overall: reproduction of the published (t, n) -> seed mapping: MATCH as-is.
Values above were pre-derived from dev validation (section 6); any deviation at
execution is recorded as-is (section 8).

## 8. Discrepancy protocol

Anything unexpected (pin mismatch, selftest failure, row mismatch, JSON anomaly,
tool unavailability): STOP; record verbatim in the log; write a dated decision
BEFORE proceeding (in the log); no parameter changes after results; affected
items get as-is labels; the record reports exactly what happened. A MISMATCH is
a result, not a failure of the process.

## 9. Non-claims

- NOT a statement about ECDSA security; not a break/attack/weakness analysis;
  the claim page itself says this is not one ("This is not a cryptographic
  break, new attack, or weakness in the ECDSA curves.").
- NOT testing base points of any curve (claim's FreeLIP findings out of scope).
- NOT testing skipped candidates / curve-selection criteria.
- NOT testing B-163's derivation (residue; the claim failed too) â€” I4 only uses
  its published 160-bit string as a statistic input.
- NOT verifying that "the NSA actually ran lrand48": we reproduce the mapping
  from the frozen model; no archival program was obtained or run.
- NOT testing the timing/timezone beyond the claim's printed UTC-less strings
  (interpreted as UTC; deviation would move timestamps, not the 160-bit matches).
- NOT a novelty or priority statement, and NOT an independent confirmation of
  the provenance story (single public source; our independence is from the
  claimant's code, not from the claim text).
- Excluded during source survey: OpenSSL ec_curve.c (v-curves present, no seed
  values), Crypto++ eccrypto.cpp (no seed fields), sawes.net (unreachable);
  saweis.net page is context only (derived from the neuromancer database).
- NOT covering the c2pnb/c2tnb, K-163..K-571, or other curves the claim does
  not list.

## 10. Outputs

- Exec dir `audit_ecdsa/exec_2026-10-19/`: e1, e1w, i1_selftest.json,
  i2_prime.json, i3_binary.json, i4_wordstats.json, i5_timestamps.json,
  i6_sources.json (+ hashes in the log).
- Log `reports/AUDIT_ECDSA_LOG_2026-10-19.log` (append-only).
- Record `reports/AUDIT_ECDSA_REPORT_2026-10-19.md` (RR-2026-01).
- Registry A-2026-0004 + guard green; HANDOFF seal row; commits + CI.

---

Note: this prereg cannot cite its own commit hash (it is created by the commit
it announces). The record (RR-2026-01) will cite the freeze commit hash.


