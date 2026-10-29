# AUDIT BB(5) â€” Phase R addendum: the rebuild completed (attempt 5)

Addendum to the Phase R item of the registered BB(5) audit. Companion to the
frozen preregistration `reports/AUDIT_BB5_PREREG_2026-10-18.md`, the
reconnaissance `reports/AUDIT_BB5_RECON_2026-10-18.md`, the frozen report
`reports/AUDIT_BB5_REPORT_2026-10-18.md` (NOT modified) and the transcript
`reports/audit_bb5_phaseR_2026-10-18.log` (frozen at its final line, the
attempt-5 end block, quoted in Â§6). Written 2026-10-19 (UTC) after the
completion event. Registry entry: `A-2026-0002` (extended; this file is its
own record, the frozen report surface is untouched).

## 1. Status

- **Item R outcome: rebuild completed â€” attempt 5, `2026-10-19T00:31:14Z`.**
  All runner steps `EXIT: 0`; the artifact set is complete (50/50 `.vo`); `PHASER_COMPLETE`
  marker set; the transcript's final line is the end block quoted in Â§6.
- Result label (frozen formula, values filled in from Â§6): *"the proof was
  rebuilt with Coq 8.20.1 on this host; compilation exited 0; the
  end-of-build assumption print reads:"*

  ```text
  Axioms:
  FunctionalExtensionality.functional_extensionality_dep :
    forall (A : Type) (B : A -> Type) (f g : forall x : A, B x),
    (forall x : A, f x = g x) -> f = g
  ```

- The 17 h backstop (deadline epoch `1792364575` = `2026-10-18T23:02:55Z`,
  never reset) was reached **during** attempt 5. It was recorded as-is at the
  wall (`UNRESOLVED-BUDGET`; kill suppressed â€” pre-registered decision D-R5);
  the build continued undisturbed and completed 1 h 28 m 19 s after the wall.
  The overrun is recorded as-is (this file); no parameter was changed; no
  silent retry occurred (every attempt is recorded in the transcript before
  the next began; the precise `attempt N (resume) start` count is 4, no
  second start block).
- No earlier attempt produced any audit result (setup abort; two environment
  interruptions; one OOM kill â€” Â§4). Only attempt 5 reached compilation of
  `BB5_Theorem.v`.

## 2. Scope

- This is a **rebuild of the pinned upstream artifact** (recon S1):
  `github.com/ccz181078/Coq-BB5`, branch `main`, commit
  `9142e219229baf2245d3f70851947230ea28a318` (2025-09-20); archival release
  Zenodo `10.5281/zenodo.17061968` (recon S2). Same sources; vanilla Coq
  8.20.1; `coq-native` disabled (as pre-registered).
- It is **not** an independent re-verification of the BB(5) claim: the
  sources are the upstream sources. The added value is a reproducible
  *rebuild record* on a different host/configuration (no native compute,
  2 physical cores, `make -j2`): exit codes, the complete axiom dependency
  list, file counts, and byte-level hashes.
- The Coq kernel is the checking authority for the output below. This
  addendum adds no verification of its own; the anti-circularity gate output
  (Â§7) is `TOOL NOT RUN` and is attached as-is (it can only downgrade
  wording, never upgrade it).

## 3. Environment (as recorded in the transcript)

- Windows host + WSL2 Ubuntu; WSL 3.0.3.0, kernel
  `6.18.54.1-microsoft-standard-WSL2`; CPU Intel i7-6600U (2 cores /
  4 threads); 9.7 GiB RAM + 3 GiB swap in WSL.
- opam switch `/root/.opam/4.14.2`; `coqc --version` (transcript L577â€“578;
  repeated verbatim in each attempt's preflight, L1320â€“1321, L1401â€“1402,
  L1540â€“1541):

  ```text
  The Coq Proof Assistant, version 8.20.1
  compiled with OCaml 4.14.2
  ```

- `coq-native` disabled at configure time (vanilla, as pre-registered): the
  compiler emits `native_compute disabled at configure time; falling back to
  vm_compute` warnings throughout.
- Build command (attempt 5): `cd â€¦/CoqBB5/BB5 && time make -j2` â€” `-j2` is
  the OOM mitigation; the prereg cap "no `-j` > 4" was respected in every
  attempt (attempts 2â€“4 used `-j4`).

## 4. Attempts ledger (all times UTC; date 2026-10-18 unless noted; line numbers = transcript)

| # | window | outcome | point of stop / result | evidence |
|---|--------|---------|------------------------|----------|
| 1 (setup) | 06:02:55â€“06:09:32 | ABORT (toolchain install) | `opam pin add coq 8.20.1` EXIT 10: `libgmp-dev` depext missing; opam refuses non-interactive apt; Coq not installed; no audit step ran | L62, L471; decision recorded L474 |
| 2 | 06:15:01â€“~07:12 | interrupted (environment) | WSL VM auto-stopped (idle) and killed the build; last `.vo` = `TNF_Root_4_5.vo` (07:12:35Z); died during `TNF_Root_4_6.v`; log ended without an end marker | L495; interruption note L1291 |
| 3 | 08:23:51â€“09:27:36 | interrupted (environment) | Ubuntu instance terminated by WSL (known WSL 3.x class; journal shows orderly systemd shutdown); last `.vo` = `TNF_Root_4_6.vo` (09:21:01Z); 40/50 | L1299; interruption note L1371 |
| 4 | 11:00:17â€“20:03:11 | OOM-kill + ABORT | kernel OOM-killed `coqc` on `TNF_Root_4_11.v` (15:08:59Z; `make` Error 137), `-j4` on 9.7 GiB; remaining jobs drained; ABORT written 20:03:11Z | L1383; interruption note L1453; ABORT L1516 |
| 5 | 20:03:14â€“00:31:14 (Oct 19) | **COMPLETED** | 50/50 `.vo`; `BB5_Theorem.vo` present; all steps `EXIT: 0`; `PHASER_COMPLETE` | L1520; wall L1572; end L1645 |

Mitigations (each committed/recorded **before** the attempt it fixed; no audit
result was ever seen before a retry, and no parameter was changed silently):

- after attempt 2: `%USERPROFILE%\.wslconfig` â†’ `vmIdleTimeout=86400000`
  (24 h), verified with an idle test (VM survived without clients);
- after attempt 3: Windows-side keepalive supervisor (PowerShell loop,
  ~10 s tick; each tick is a short WSL session: heartbeat, deadline backstop
  with single-writer claim via noclobber, self-healing relaunch via `flock`
  only when the runner is absent and no `DAEMON_FAIL`); the runner then
  executed directly from the repo path (single source of truth); markers
  `PHASER_COMPLETE` / `STOP_KEEPALIVE` / `STOP_RECORDED` / `DAEMON_FAIL`;
  non-admin supervision paths used because Task Scheduler registration was
  denied (elevated option provided: `audit_bb5/bb5_phaseR_keepalive_task.ps1`);
- after attempt 4: `make -j2` (down from `-j4`).

Cap accounting as recorded: setup used 6 m 37 s (attempt 1) + 8 m 05 s
(attempt 2 pre-roll) of the â‰¤ 3 h cap. Build wall times: attempt 2 30 m 25 s
(as recorded); attempt 3 63 m 44 s; attempt 4 11:00:17Zâ†’20:03:11Z (OOM at
15:08:59Z; the tail consists of draining the two standing jobs and writing
the ABORT); attempt 5 4 h 28 m 00 s (`make` self-reported `real
267m59.105s`). No single attempt exceeded the 14 h build cap; the cumulative
wall time across the four partial attempts (including the attempt-4 drain
tail) is â‰ˆ 15 h 05 m â€” recorded here as-is. The terminal disposition applied
was the pre-registered `UNRESOLVED-BUDGET` at the 17 h wall (Â§5); completion
followed, and this file is the as-is record of that overrun.

## 5. Supervision efficacy (wall event, D-R5)

- The supervisor is the Windows-side tick (loops + Startup item; ~10 s
  cadence, single-writer discipline) that writes liveness heartbeats,
  enforces the deadline backstop, and can relaunch a dead runner. Heartbeat
  was verified fresh at repeated independent checks during the run; loop
  turnover occurred without loss of cadence; no relaunch was ever needed
  after attempt 5 started (start-block count stayed 4).
- At `23:02:55Z` the backstop fired exactly. Transcript L1572, verbatim:

  ```text
  --- 2026-10-18T23:02:55Z | KEEPALIVE STOP: wall backstop reached (deadline epoch 1792364575); kill SUPPRESSED (pre-registered D-R5: attempt 5 continues undisturbed, no parameter changes); item recorded UNRESOLVED-BUDGET.
  ```

- The tick that fired was v4.1 (sha256LF
  `6eda81a5fb7e2d2653edb3342faf1631fa4fe9816c9d3ef0a195d9b906643bb4`,
  commit `0a97f2b`) â€” a **record-only** fix committed before the wall. The
  pre-fix v4 kill path was defective: its `pkill -f` pattern matched only
  the wrapper shell (`make`/`coqc` run with relative paths), so a wall kill
  would have orphaned the build and the self-healing relaunch would have
  re-started the same targets â€” a double compile of
  `TNF_Root_4_11/4_12` and an OOM risk on this host. The defect, the fix
  and the dated decision D-R5 (no kill at the wall; record
  `UNRESOLVED-BUDGET` as-is; no parameter change; a *new* `DAEMON_FAIL`
  would still stop for a fresh decision) were appended to the transcript at
  20:12Z (L1567), **before** the wall.
- Observed effect: `TNF_Root_4_11.vo` finished at `23:19:39Z` â€” 17 minutes
  **after** the wall â€” undamaged; after the run the tick exited on
  `PHASER_COMPLETE`, loops stopped, and the heartbeat stopped at the
  completion timestamp (`/root/bb5r` listing; marker `PHASER_COMPLETE`
  present).
- Post-wall check note (L1577) records the same facts as observed at
  `00:15Z`, ~16 minutes before completion.

## 6. Result blocks (verbatim; quoted from the frozen transcript)

1. Attempt-5 start block (L1520â€“1521):

   ```text
   === phase R attempt 5 (resume) start 2026-10-18T20:03:14Z ===
   runner: /mnt/d/Opencode AI Agent/audit_bb5/bb5_phaseR_resume4.sh (repo path; single source of truth) sha256 4b55010dd5365a25706c9c00b87d3eb9aad18ff155904c4f9065d9ddb46b9db7
   ```

   (the block records: resume count 44/50; `make -j2`; deadline epoch
   unchanged; tick v4 with a single-use `APPROVE_ATTEMPT5` token)

2. End-of-build assumption print â€” the output of `Print Assumptions
   BB5_value.` (last line of `BB5_Theorem.v`), L1606â€“1611:

   ```text
   Finished transaction in 12.262 secs (11.972u,0.281s) (successful)
   Axioms:
   FunctionalExtensionality.functional_extensionality_dep :
     forall (A : Type) (B : A -> Type) (f g : forall x : A, B x),
     (forall x : A, f x = g x) -> f = g
   make[1]: Leaving directory '/root/bb5r/Coq-BB5-git/CoqBB5/BB5'
   ```

3. Build duration (the runner's `time make -j2` step), L1613â€“1616:

   ```text
   real	267m59.105s
   user	462m57.192s
   sys	1m8.668s
   EXIT: 0
   ```

4. Final artifact checks (runner steps L1618â€“1644; each block `EXIT: 0`):

   ```text
   CMD: find /root/bb5r/Coq-BB5-git/BusyCoq -name '*.vo' | wc -l
   25
   CMD: find /root/bb5r/Coq-BB5-git/CoqBB5/BB5 -name '*.vo' | wc -l
   50
   CMD: ls -l /root/bb5r/Coq-BB5-git/CoqBB5/BB5/BB5_Theorem.vo
   -rw-r--r-- 1 root root 6859 Oct 19 08:31 /root/bb5r/Coq-BB5-git/CoqBB5/BB5/BB5_Theorem.vo
   ```

5. End block â€” the transcript's final line, L1645:

   ```text
   === phase R attempt 5 (resume) end 2026-10-19T00:31:14Z (all steps exit 0 as recorded above; PHASER_COMPLETE set) ===
   ```

## 7. Anti-circularity gate (verbatim)

- Command (repo skill `anti-circularity`, run from the skill directory with
  the z3-capable interpreter): `C:\Python314\python.exe scripts\gate.py
  check reports\audit_bb5_phaseR_2026-10-18.log
  reports\AUDIT_BB5_RECON_2026-10-18.md reports\FENCE_REGISTRY.md`.
- Output (verbatim):

  ```text
  ANTI-CIRCULARITY GATE [check]
    NOT RUN  NO_LEAN_FILES: no .lean input matched
    result: FAIL=0  NOT_RUN=1  SKIP=0
    verdict: TOOL NOT RUN
  ```

  exit code 2. Per prereg Â§8 this output is attached as-is; it certifies
  nothing here and can only downgrade wording.
- Gate self-test, same session: `gate self-test: 13 cases, 0 failed`
  (including negative fixtures that must fail).

## 8. Comparison with the upstream claim

- Upstream claim (pinned README, section "### Used Axiom"; recon L56â€“58):
  *"As outputted at the end of the compilation, the proof only depends on
  Coq's standard library axiom functional_extensionality_dep"*.
- Observed (Â§6 block 2): exactly one axiom in the
  `Print Assumptions BB5_value.` output â€”
  `FunctionalExtensionality.functional_extensionality_dep`, with the standard
  statement. **The claim matches the observed output** on this host, with
  vanilla Coq 8.20.1 and without `coq-native`.
- Context: the upstream README notes ~3 h on 13 cores *without* native
  compute; this rebuild took 4 h 28 m wall on 2 physical cores with
  `make -j2` â€” direction and magnitude consistent; no contradiction
  recorded.

## 9. Certificates (sha256LF)

Convention: `sha256LF` = SHA-256 over LF-normalized bytes, helper
`audit_bb5/artifact_checks.py` (its own sha256LF is certified in
`A-2026-0002`). Re-verify with
`python audit_bb5/artifact_checks.py sha256lf <filesâ€¦>`; registry guard:
`python -m pytest msaf/tests/test_fence_registry.py -q`.

```text
sha256LF 294d1dd423f9b4f596435fab813f082bfb781c58d7f810d53060d51c2c7b2cef reports/audit_bb5_phaseR_2026-10-18.log
sha256LF 4b55010dd5365a25706c9c00b87d3eb9aad18ff155904c4f9065d9ddb46b9db7 audit_bb5/bb5_phaseR_resume4.sh
sha256LF c3b5132e3c4918f90d7d3447641031fa38621a31d3be6aff07ccdcc821fa18f5 audit_bb5/bb5_phaseR_resume3.sh
sha256LF 86af54de441603b62195cc856d399de1ab19cf8c13dc00f00d75a73ec0c2cf73 audit_bb5/bb5_phaseR_resume2.sh
sha256LF 0261cae899a03423efc9d76960fe82d5dc06b00382c51a66448fee5f539c5c17 audit_bb5/bb5_phaseR_resume.sh
sha256LF 3f0415e57f6bef052d0e675524376995208c9611b123703d88ecad3c73a52d8c audit_bb5/bb5_phaseR.sh
sha256LF ff95fe17855a38bfdddfb6289f84b551d04c09ddb013ab5575c56bf54532b3ea audit_bb5/bb5_phaseR_watchdog.sh
sha256LF 6eda81a5fb7e2d2653edb3342faf1631fa4fe9816c9d3ef0a195d9b906643bb4 audit_bb5/bb5_phaseR_keepalive_tick.sh
sha256LF 151a8b467635586ac6f318bfb0ae211df4d129adcf695bf8baa5cc1e89db6f62 audit_bb5/bb5_phaseR_keepalive.ps1
sha256LF 40c2405d24e6d4188b055e39144cccddf0fc6edb7845bcad7591a1b55359c097 audit_bb5/bb5_phaseR_keepalive_spawn_wmi.ps1
sha256LF d1a312a1322a0515a1bb31059b86a256257fbba3f4905a5e863d698034a614ed audit_bb5/bb5_phaseR_keepalive_task.ps1
```

- The transcript's hash is over its **final** bytes (last line = end block,
  Â§6 block 5); the transcript is not appended to after this addendum.
- The addendum's own sha256LF is recorded in registry `A-2026-0002`
  (self-reference not possible in this file).

## 10. Non-claims and standing constraints

- No statement about the Riemann Hypothesis and no statement about P vs NP
  (standing prohibition); nothing here bears on either.
- No novelty or priority claim; upstream credit stands
  (`ccz181078/Coq-BB5`, DOI `10.5281/zenodo.17061968`).
- The BB(5) = 47,176,870 statement itself remains the upstream artifact's
  claim; this addendum certifies only rebuild facts (exit codes, the axiom
  list, file counts, hashes) â€” not peer review, not independent
  re-verification.
- AI provenance disclosure: this audit (including this addendum) was
  executed by an AI analysis session under owner oversight; no human
  line-by-line review of the transcript happened or is claimed.

Recorded by the analysis session, 2026-10-19 (UTC).


