# P2 audit — execution report (Collatz convergence-verification record; Barina project)

Date: 2026-10-19. Registry: `A-2026-0003` (extension committed separately).
Pre-registration: `reports/AUDIT_COLLATZ_PREREG_2026-10-19.md`
(sha256LF `d9c334e2e9cc78c13bb66260ee7d9445940a24488b2dda79b118f173476d9cf8`),
commit `bbbe9ae`. Execution HEAD: `9d9c358798ab4859dd024759bedd8b90cc4aac6c`.
Transcript: `reports/AUDIT_COLLATZ_LOG_2026-10-19.log`
(sha256LF `ccf178d070c26e19a8c88af5e34a6d1fbffae743c189b0d8277a96b2b1714e4b`;
12,760 lines / 336,603 bytes; opened `2026-10-19T00:46:40Z`; last write
`00:59:52.99Z`).

Status: **EXECUTED**. All items S/W/E/H/P ran to completion inside the frozen
caps. Outcomes: S3 required one protocol rerun after a transient network
failure; S4/P produced a persistent difference against its frozen expectation
that is recorded as a **DISCREPANCY** and explained in-budget (§6.2). No
parameters were changed. T stayed NOT-RUN by owner decision. The E1 sweep
completed in 4 m 37 s of its 3.5 h wall.

## 1. Scope — what was and was not checked

This is the bounded, pre-registered replay of a published computation record
(C1/C1p/C2, §1 of the pre-registration). Everything below is finite and
bounded: page/archive captures, a 162-file snapshot comparison, battery
replays of 98 + 97 + 148 published rows, a 25/14-fragment transcription
check, an exhaustive drop-check for odd n < 2^34, and a record prefix below
2^24. It is *not* a check of the target claim C1 (convergence verified below
≈ 2^71.02 — not reachable on this host), not a proof or disproof of the
Collatz conjecture, and not peer review. No Lean/Coq/SMT artifact exists in
this audit; no such claim is made (§9 of the pre-registration).

## 2. Provenance and ordering

- The pre-registration and its frozen set were committed as `bbbe9ae` and
  pushed before any audit command; its CI run `39154348599` was green
  (`gh run view 39154348599` → success, headSha `bbbe9ae`).
- Preflight at execution start (log block `PREFLIGHT`): working tree clean
  (`STATUS_PORCELAIN: []`); HEAD = `9d9c358798ab4859dd024759bedd8b90cc4aac6c`;
  `git merge-base --is-ancestor bbbe9ae HEAD` → exit 0;
  `git diff --quiet bbbe9ae HEAD -- <prereg>` → exit 0 (frozen file
  unchanged); `git ls-remote origin main` = HEAD; CI run `39181863147` for
  `9d9c358` green (python-tests + lean-kernel); Windows git
  `2.53.0.windows.3`.
- The log's open block records date/host/HEAD, the sha256LF of all 11 frozen
  §2(b)/(c) files — every value matched the pre-registration — and the sha256
  of the prereg file `d9c334e2…` (equal to the frozen value).
- All commands ran sequentially ("satu dulu") under `nice -n 19`; every block
  is delimited in the log by `--- <ts> | <name> ---`, `CMD:`, the complete
  output, `EXIT:`; the log had a single writer at a time (`tee -a`).
- The runner scripts were kept outside the repo during execution
  (`%TEMP%\opencode\p2exec\`) and were committed **unmodified** afterwards to
  `audit_collatz/p2_runners/`; byte-identity was verified with `cmp` for all
  eight files before the copy (hashes in §8).

## 3. Host, tools, invocation notes

- Windows host (WSL2 Ubuntu); WSL `python3` 3.14.4; WSL `gcc`
  15.2.0-16ubuntu1; CPU i7-6600U (2C/4T); laptop otherwise idle during the
  run.
- Network captures used Windows `curl.exe` 8.13.0 through WSL interop with
  Windows-form `-o` targets, because the frozen commands name `curl.exe`.
  Commands as executed are in the log.
- `git` was the Windows binary (`C:\Program Files\Git\cmd\git.exe`) invoked via
  interop for S3 — repo Git was never run from WSL, per standing rule.
- E1's hard wall was implemented exactly as pre-registered:
  `timeout -s INT 12600 …` (SIGINT at 3.5 h; exit 124 would have been recorded
  as-is). It was not triggered.
- The `w1`/`w2`/`e3` engines print their full result JSON to stdout; the
  transcript therefore contains those JSONs in-line.

## 4. Chronology and caps (UTC; from the log's block delimiters)

| Item | Start | Next block | Wall | Frozen cap |
|---|---|---|---|---|
| open | 00:46:40 | — | — | setup ≤ 1 h |
| preflight | 00:46:41 | — | — | — |
| S1 | 00:46:53 | 00:47:08 | 15 s | S ≤ 0.5 h |
| S2 | 00:47:08 | 00:47:12 | 4 s | |
| S3 attempt 1 | 00:47:12 | 00:47:51 (failed) | 39 s | §9 rerun-once |
| S3 rerun | 00:47:51 | 00:48:00 | 9 s | |
| S4/P | 00:48:00 | 00:48:04 | 4 s | P/S4 ≤ 30 m |
| H1+H2 | 00:48:04 | 00:48:05 | 1 s | H ≤ 20 m |
| S5 | 00:48:05 | 00:49:38 | 93 s | |
| S4 discrepancy rerun | 00:49:38 | 00:49:39 | 1 s | §9 |
| S4 investigation | 00:49:39 | 00:49:53 | 14 s | §9 (in budget) |
| W1a/W1b | 00:49:53 | 00:51:21 | 88 s | W ≤ 1 h |
| W1 criteria | 00:51:21 | 00:51:21 | < 1 s | |
| W2 | 00:51:21 | 00:52:02 | 41 s | |
| W criteria | 00:52:02 | — | < 1 s | |
| E setup (gcc build) | 00:52:15 | 00:52:16 | 1 s | setup ≤ 1 h |
| E2 | 00:52:16 | 00:52:37 | 21 s | E ≤ 4 h |
| E3 | 00:52:37 | 00:55:16 | 2 m 39 s | |
| E1 | 00:55:16 | 00:59:52.8 | 4 m 36.8 s | wall 3.5 h |
| log frozen | 00:59:52.99 | | | |

- Setup span (log open 00:46:40 → C build done 00:52:16): 5 m 36 s ≤ 1 h.
- S window 00:46:53 → 00:49:38 (S5 end; 00:49:53 including the S4
  investigation): 2 m 45 s / 3 m 00 s ≤ 30 m.
- W: 2 m 09 s ≤ 1 h. H: 1 s ≤ 20 m. P/S4: 4 s + 15 s ≤ 30 m.
- E: 00:52:15 → 00:59:52.8 = 7 m 37.8 s ≤ 4 h; E1 alone 4 m 36.8 s against
  the 3.5 h hard wall.
- Total first command → last write: 00:46:53 → 00:59:52.99 = 12 m 59.99 s
  (≈ 13 m) ≤ 6 h.
- No overruns; no `UNRESOLVED-BUDGET` entries.

## 5. Outcomes and the frozen maximum labels

The labels below are quoted verbatim from §10 of the pre-registration; the
observed values follow each quote.

### S (sources)

> "the named pages and the pinned revision were captured at the recorded
> times and hashed; the six expected-stable captures matched their freeze
> copies byte-for-byte; site_main.html matched after normalization of the
> Generated line only; the frozen quoted fragments were located verbatim;
> this is a snapshot, not a verdict."

Observed: S1 — `curl.exe` HTTP 200 ×3 (path-records, news, main); `cmp` 0 for
`site_path_records.html` and `site_news.html`; `site_main.html` normalized on
both sides with `sed -E 's/Generated: [^<]*/Generated: X/'` → `cmp` 0.
S2 — HTTP 200 ×4 and `cmp` 0 ×4 (A006884, A006885, A006877, A006878). The six
expected-stable captures (2 site + 4 OEIS) matched byte-for-byte. S3 rerun —
HEAD `e98d0294a7ff77e783907e307a80e83b92f4a164`, tree
`b290c47a7f3b4be37f1992e7ccd5bae2dafefa2f`. Fragments: H1 25/25, H2 14/14
(below). Caveat: S3's first attempt failed on a transient network error and
the recorded rerun succeeded (§6.1).

### W (published record replays)

> "every published path-record row (98), standard-height row (97), and
> delay-record row (148) was re-simulated by two independent in-repo
> engines; each trajectory reached 1 and the recomputed values equalled the
> published ones; the published lists' monotonicity was confirmed; the
> engines' result JSONs were deep-equal and re-run-stable. Finite
> arithmetic check; not peer review; not a proof of the conjecture."

Observed: W1 — `path_checked = 98`, `std_checked = 97`, `mismatch_path = []`,
`mismatch_std = []`, `cap_hits = []` (both engines). W2 — `checked = 148`,
`mismatches = []`, `cap_hits = []` (both engines). Every row carries
`ok`/`ok_std: true`; no trajectory hit the 10^6 step cap (empty `cap_hits`),
i.e. each simulation reached 1. Deep-equal `compare` printed MATCH three
times per item (P r1↔r2, Q r1↔r2, P↔Q). Monotonicity (strictly increasing
n and t(n) in all four lists) is asserted by the frozen
`build_batteries.py` and recorded in the S5 build report
(`battery_build_report.txt`, sha256LF `10be3c18…`, §8). Artifact hashes: §8.

### E (bounded exhaustive drop-check)

> "an independent in-repo C engine checked that every odd n below 2^34
> reaches a value below itself under the shortcut map within the step cap
> of 10^6; the independently written Python engine reproduced the identical
> 2^24 digest (drop metrics), and the recomputed record prefix below 2^24
> matched the published table (38 rows) between both engines. Bounded
> replay; no claim for any n ≥ 2^34."

Observed: C engine (binary sha256 `46d419ad…`, gcc 15.2.0) —
`odd_checked = 8589934591` (= 2^33 − 1; the enumerated domain is odd n with
3 ≤ n < 2^34 — n = 1 is the trivial 1↔2 cycle and never goes below itself,
the same domain convention as the E2 cross-check), `cap_hits = []` (no n
reached the 10^6 step cap), `max_steps_to_drop = 547` at
`argmax = 12235060455`, `sum_drop = "54594891213685909421"` (Σ over the
checked odd n of the first value below n under the shortcut map). E2 —
Python reproduced the identical 2^24 digest (`odd_checked = 8388607`,
`max_steps_to_drop = 287`, `argmax = 13421671`,
`sum_drop = "52066189353824"`, `cap_hits = []`) → `compare-prefix` MATCH;
the `prefix24` block inside `c_drop34.json` is identical to the
`c_drop24.json` result block → `compare-prefix` MATCH (informational check). E3 —
Python `record_count = 38`, `prefix_compare.match = true` with
`battery_rows_in_range = 38`; C `records 24` `record_count = 38`;
`compare-fields … records record_count` MATCH; `check-prefix` MATCH
(38 entries). Timing: §4.

### H (transcription of quoted fragments)

> "the frozen quoted fragments were found verbatim in the captured pages
> and in the clone at the pinned commit; this is a transcription match
> only."

Observed: H1 — `claims: 25 rows, 0 miss` (exit 0) against the fresh
captures. H2 — `claims: 14 rows, 0 miss` (exit 0) against the clone at the
pin.

### P/S4 (archive vs clone)

> "the GitHub archive at the pinned commit was compared to a fresh clone
> file-by-file; differences are listed verbatim."

Observed: `identical = 147`, `changed = []`, `only_in_tarball = []`,
`only_in_clone = 15` (all 15 paths listed in §6.2). The frozen expectation
was `only_in_clone = []`, `identical = 162`; the difference is a recorded
DISCREPANCY with a documented mechanism (§6.2) — no content drift in any
compared regular file.

### T (excluded)

> "NOT-RUN — excluded from v1 scope by the owner decision recorded in this
> file."

Observed: NOT-RUN (no command executed for T).

## 6. Findings and discrepancy records (§9 outcomes)

### 6.1 S3 — transient network failure, one protocol rerun

First attempt (block `00:47:12Z`) died mid-transfer:

```
error: RPC failed; curl 56 Recv failure: Connection was reset
error: 14 bytes of body are still expected
fetch-pack: unexpected disconnect while reading sideband packet
fatal: early EOF
fatal: fetch-pack: invalid index-pack output
EXIT: 128
```

Git removed the partial clone itself, so the subsequent `checkout` and
`rev-parse` commands in the same block failed with
`cannot change to '…': No such file or directory` (full block in the log
under the `00:47:12Z` header). Per §9 the exact command block was rerun once
(`00:47:51Z`) and succeeded: clone exit 0, `HEAD is now at e98d029 port
5008`, HEAD `e98d0294…`, tree `b290c47a…`. Recorded as-is; no parameters
changed. This was an environment/network failure, not a mismatch of audit
results.

### 6.2 S4/P — persistent difference against the frozen expectation

- Frozen expectation (prereg §4): `only_in_tarball []`,
  `only_in_clone []`, `changed []`, `identical 162`.
- Observed (block `00:48:00Z`; reproduced by the §9 rerun at `00:49:38Z`,
  identical): `identical = 147`, `changed = []`,
  `only_in_tarball = []`, `file_counts = {tarball: 147, clone: 162}`,
  `only_in_clone = 15`:
  `src/gpuworker/compat.h`, `src/gpuworker/kernel.cl`,
  `src/gpuworker/wideint.h`, `src/mclient/compat.h`,
  `src/rs-client/compat.h`, `src/rs-server/compat.h`,
  `src/rs-server/wideint.h`, `src/rs-worker/compat.h`,
  `src/rs-worker/wideint.h`, `src/server/compat.h`,
  `src/server/wideint.h`, `src/steps/compat.h`,
  `src/steps/wideint.h`, `src/worker/compat.h`,
  `src/worker/wideint.h`.
- In-budget investigation (`00:49:39Z`–`00:49:53Z`), all recorded in the log:
  1. the tarball stores those 15 paths as **symlink members**
     (`lrwxrwxrwx … -> ../common/compat.h` etc.;
     `src/gpuworker/kernel.cl -> kernel32.cl`), while
     `src/common/compat.h` and `src/common/wideint.h` are regular members
     (964 B / 876 B);
  2. the clone's index holds exactly **15 mode-120000 entries** at the same
     15 paths (`git ls-tree -r HEAD | grep -c '^120000'` → `15`);
  3. symlink counts on both sides: `15` (tar `grep -c '^l'`) = `15`
     (ls-tree);
  4. the materialized files' content equals the link target:
     `cat src/worker/wideint.h src/gpuworker/kernel.cl` prints
     `../common/wideint.hkernel32.cl`;
  5. the clone has 162 tracked entries in total (`ls-tree -r HEAD | wc -l`).
- Mechanism: the GitHub archive stores the repository's symlinks as link
  members; the Windows checkout (`core.symlinks=false`, the default without
  developer mode) materializes each link as a regular file whose content is
  the link target; `weld-tar` compares only regular tar members against
  regular files (`if not member.isfile(): continue`). Hence the 15
  materialized files appear only on the clone side. Net effect: every one of
  the 147 comparable regular blobs is byte-identical; nothing changed and
  nothing is missing from the clone.
- Disposition: the frozen expectation `0/162` was a derivation error at
  freeze time (it did not account for symlink members and the Windows
  checkout policy). It is recorded as a DISCREPANCY as-is; the exact command
  was rerun once per §9 with the identical result; `weld-tar` was **not**
  modified (frozen tool from the BB5 package, hash in `A-2026-0002` and
  re-listed in `A-2026-0003`); no parameters changed. The listing above is
  the difference verbatim, as required by the P/S4 label.

### 6.3 W1 criteria extraction — tooling note (transparency)

The first extraction attempt (`00:51:21Z`) read the five criteria fields at
the top level of the W1 JSONs and printed `MISSING` (the fields live under
`result`); the corrected extraction was appended at `00:52:02Z` and is the
one reported in §5. Both blocks are kept in the log as-is. No audit value
depends on the first block.

## 7. Anti-circularity gate (attached verbatim; can only downgrade)

Per prereg §9 the gate was run at report time over the audit artifact tree
(`audit_collatz/`). Output attached verbatim:

```
------------------------------------------------------------------------------
ANTI-CIRCULARITY GATE [check]
  NOT RUN  NO_LEAN_FILES: no .lean input matched
  SKIP     D:\Opencode AI Agent\audit_collatz\exec_2026-10-19\clone\.git (dependency/VCS dir, out of scope)
  result: FAIL=0  NOT_RUN=1  SKIP=1
  verdict: TOOL NOT RUN
```

Exit code: 2 (`TOOL NOT RUN`). Gate self-test on its own fixtures: 13 cases,
0 failed, exit 0. As pre-registered: no Lean/Coq/SMT artifact exists in P2
and no such claim is made anywhere in this audit; the verdict is recorded
as-is.

## 8. Artifacts and hashes

All values below are sha256LF (LF-normalized SHA-256, the registry
convention), computed after the log was frozen. The log and this report are
committed with the report commit; the result JSONs, the S5 build report and
the eight runner scripts are committed with the registry commit. Every hash
in the three tables below is a certificate line in `A-2026-0003` (CI
re-verifies each one).

**Transcript**

| artifact | sha256LF |
|---|---|
| `reports/AUDIT_COLLATZ_LOG_2026-10-19.log` | `ccf178d070c26e19a8c88af5e34a6d1fbffae743c189b0d8277a96b2b1714e4b` |

**Result artifacts (`audit_collatz/exec_2026-10-19/…`)**

| artifact | sha256LF |
|---|---|
| `w1_p_r1.json` | `0bdbb5a0b14a730a26e215e63952bd198d5542115115ec5b3df79b7c03eb5cda` |
| `w1_p_r2.json` | `974c2aef4493b7a7e830a37cecc99b60132c277fec311109eeae6a45d3a1e0f1` |
| `w1_q_r1.json` | `ea4239909d941fefa393cb667a7a3c4308b0a703b9295edc08b1c266bb4b81f1` |
| `w1_q_r2.json` | `800c52445e8c709cbcf6745118607df1bf5ba47668c8c643e8e2d3d587bf9e03` |
| `w2_p_r1.json` | `96b92a332f985c85b11a2c9e51b0c76030c320b6058a4bdb6c62f6a764b30488` |
| `w2_p_r2.json` | `5926fd6ac5a8d8db7a3d6b7b651d7ac815ab2af8dcb0ae1ab16c7fc3f30ae5f7` |
| `w2_q_r1.json` | `0318eaa1c89d026e3342463e5f666a733c186631971fde44c00cba4013cec185` |
| `w2_q_r2.json` | `7d00d7c964073794296deadac847fac01a68ad97653ef77bd2a4c3e099fbfd91` |
| `c_drop24.json` | `1f6126b209a62793c7b6a3b0d385ffa0a4e60a73a4dcb5b44207c62c2ee02b86` |
| `p_e2_24.json` | `8faaaa59181c0c2543cdf4b4906581963050d03030f6024fceb9d1019deb4130` |
| `p_e3_24.json` | `c06f38bf3468280be984857e28b4e1bb4fa94a570d54a336e0505727f55ef5e6` |
| `c_rec24.json` | `daa3a5d7a8d3ddb22d3ff069c5091a8819c2927f2b3406e82f68cd9f2ebaef38` |
| `c_drop34.json` | `458ac1241ffea0b7e39e0974281ea3d946747a7bb111a6298758ca1c8244cf45` |
| `weld.json` | `5ca7703e2884e9a0b3a4d28b14251232a2ed570e8df04a11be44016d801b37e6` |
| `refetch/battery_build_report.txt` | `10be3c18bbbf61377225972f5b4cb20313d0f3c5ea2e3cd8d2ea9b55335e80ce` |

**Runner scripts (`audit_collatz/p2_runners/…`; used from `%TEMP%` and
committed unmodified, `cmp`-verified)**

| artifact | sha256LF |
|---|---|
| `p2_final_hashes.sh` | `2a3dea6ff79f664910ed94073125a174dded81f26de3c084226b793dc1af11f9` |
| `p2_note_preflight.sh` | `eef821b1e1181ce62ff798e34b03b05ebcb7f095ca17a3a039eb7669236a47b9` |
| `p2_note_s3retry.sh` | `74453d879f983765148dfbf85728fdb775ff108924724ce4423948142fbbc250` |
| `p2_open_log.sh` | `24bb6e83e089d5441aba5aa469d81ac67b611b334bd80f2dc039984c63618df3` |
| `p2_s4_discrepancy.sh` | `ef5d3898b430a0e51ee8ba9a6f7b2904e92754754ae3c2a06256ae89e3a92801` |
| `p2_steps.sh` | `6a7f408ef4010b1f2cbc7ebab5ca6b36f40650ec8f43b228ff2fe22c607c009c` |
| `p2_w1_criteria.sh` | `74a6612b324bf864dbf45a7db1bc45caf55942482da52fb12b4aea7dbb0d5b52` |
| `p2_w_criteria.sh` | `b4ae5295bd6880acefc7d5b80cd187d7d882b12592be30b66aa89b36fac5de57` |

**Other evidence (local, untracked; hashes recorded here and in the registry)**

- tarball `collatz-e98d0294.tar.gz` (181,085 B): sha256LF
  `daa821f4393680d0e39aa7829586d56145dfb8ddf5fc0a636e6a3d01c4be6721`.
- C binary `collatz_sweep` (20,824 B, built by gcc 15.2.0): sha256
  `46d419ad97e344c162b90ea92d86cf30c76860c99ade86d37f36bae7e15e720b` (raw;
  rebuildable from `collatz_sweep.c` with the frozen build line).
- Execution tree `audit_collatz/exec_2026-10-19/` (2.8 MB total): clone at
  the pin (Windows checkout, symlinks materialized), re-fetch copies
  (`cmp`-equal to the committed captures), re-derived batteries (`cmp`-equal
  to the frozen TSVs), normalized main files, the binary and the archive.
  These bulk/third-party inputs are not committed; the committed subset is
  the log, this report, the 15 result artifacts of the second table and the
  eight runner scripts.

## 9. Non-claims and limits

- No statement about the Collatz conjecture, and none for any n ≥ 2^34; the
  target claim C1 (≈ 2^71.02) was not reproduced — it is out of reach on this
  host (recon §5), and T is NOT-RUN by owner decision.
- C1p/C2 contents were not audited beyond the frozen quoted fragments H1/H2;
  H is a transcription match only.
- The S outcomes describe the state of the named pages at capture time and of
  the pinned GitHub revision; they are a snapshot, not a verdict about the
  project.
- The W/E outcomes are finite arithmetic replays; they are not peer review
  and not a substitute for an independent implementation study of the
  project's own workers (T NOT-RUN).
- No secrets are displayed in this report or the log; staging was per named
  file only.

## 10. Reproduction

- Every command, its complete output and its exit code are in the frozen log;
  the eight runner scripts are in `audit_collatz/p2_runners/` (hashes above).
- The registry entry `A-2026-0003` carries the certificate lines and the CI
  guard command (`python -m pytest msaf/tests/test_fence_registry.py -q`)
  that re-verifies every sha256LF line.
- The E1 sweep is reproducible with the frozen build line
  (`gcc -O2 -std=gnu11 -o collatz_sweep audit_collatz/collatz_sweep.c`) and
  `collatz_sweep drop 34 --out c_drop34.json`.

## 11. Changelog and non-modification statement

- 2026-10-19: first version, written after the log was frozen (last write
  `00:59:52.99Z`). Values are quoted from the log and from post-freeze hash
  runs; nothing was recomputed or edited after the fact.
- Non-modifications: no existing file was edited; the §2 frozen files were
  never overwritten (S5 wrote to `exec_2026-10-19/batteries_re/` and compared
  with `cmp`); third-party artifacts were read-only; the runner scripts were
  added to the repo unmodified after execution (`cmp`-verified). `weld-tar`
  and all frozen engines/tools were left untouched (hashes verified at open).
