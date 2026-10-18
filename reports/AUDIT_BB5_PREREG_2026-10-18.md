# P1 audit — pre-registration (BB(5) = 47,176,870, bbchallenge / Coq-BB5)

Date: 2026-10-18 (local). Status: **PRE-REGISTERED BEFORE ANY AUDIT
EXECUTION.** At the time of this declaration no simulation of any
machine, no download-and-hash of any target artifact, and no source
scan of Coq-BB5 has been executed for this audit. This file is committed
and pushed BEFORE the first audit command; the git add-commit time and
the wall-clock timestamps in the audit logs record the ordering.
Read-only reconnaissance that PRECEDED this file is documented in
`reports/AUDIT_BB5_RECON_2026-10-18.md`; that document is reference,
not result.

## 1. Target and scope

- Target claims (exact, as published):
  - **C1: S(5) = 47,176,870.**
  - **C2: Σ(5) = 4,098.**
- Depots of record:
  - Formal artifact: Zenodo release **Coq-BB5 v1.0.0**
    (DOI `10.5281/zenodo.17061968`), file md5s pinned from the Zenodo
    API (recon §1 S2); sibling repository pinned at commit
    `9142e219229baf2245d3f70851947230ea28a318` (recon §1 S1).
  - Published values: BusyBeaverWiki BB(5) oldid `9024`, 5-state winner
    oldid `4369`, BB(2) oldid `5358`, BB(3) oldid `8372` (CC BY);
    P. Michel "Behavior of busy beavers"; arXiv:2509.12337v2.
- What this audit checks (frozen item list, §2): witness replay (W),
  statement transcription (S), hygiene scan (H), enumeration-file
  replay for BB(3) (E), release/repository weld (P), and — optionally,
  owner-gated, post-sweep — proof rebuild (R).
- Out of scope (explicit): the universal direction ("no 5-state machine
  beats 47,176,870") is NOT verified by items W/S/H/E/P; the hygiene
  scan is textual, not a kernel check; no claim about Coq's own
  correctness; no BB(6); no re-implementation of the TNF enumeration;
  no download of the 10 GB enumeration CSV; no verdict on the phrase
  "first formally verified" beyond what the artifacts themselves show.

## 2. Audit items (frozen definitions) and their maximum labels

- **W — witness replay.** Both published halt witnesses (the S champion
  and the Σ champion) are simulated on the all-zero tape by two
  independent engines committed with this file; the full validation
  battery (Appendix A) must reproduce its published run lengths and
  ones counts first. Maximum label: *"both published halt witnesses
  replayed exactly by two independent in-repo engines; every battery
  entry reproduced its published run length and ones count."* This is
  a finite arithmetic check, not a peer review and not a proof.
- **S — statement transcription.** `CoqBB5/BB5/BB5_Statement.v` is
  re-fetched from the pinned commit, hashed (sha256LF), and its claim
  content transcribed with line numbers into the report. Maximum label:
  *"the isolated statement file at the pinned commit was downloaded,
  hashed, and transcribed; it defines BB5 as 47176870 and states
  upper-bound-forall plus lower-bound-exists over its own semantics."*
  No claim that the statement is proved.
- **H — hygiene scan.** A textual scan of the pinned tree for proof
  escapes (`Admitted`, `admit`, `Axiom(+s)`, `Parameter(+s)`,
  `Conjecture`, `Hypothesis`, `Abort`). Maximum label: *"a textual scan
  of the pinned tree found the recorded hit list; this is not a kernel
  check and no statement about proof correctness is made."*
- **E — enumeration-file replay (BB3, secondary).** The published
  `BB3_verified_enumeration.csv` from the same release is parsed,
  structurally checked, and every `halt` row is replayed by both
  engines; maxima are compared against published BB(3) values under a
  frozen decision table (§6). Maximum label: *"the published BB(3)
  enumeration file was replayed row-by-row for its halting rows; its
  maxima behave as recorded in the report; this is not an independent
  enumeration and proves no non-halting claim."*
- **P — release/repository weld.** The Zenodo `Coq-BB5-1.0.0.tar.gz`
  is downloaded, md5-verified against the Zenodo API value,
  sha256-recorded, and compared file-by-file against a clone at the
  pinned commit. Maximum label: *"the archival release archive was
  compared to the pinned repository commit; differences are listed
  verbatim."* No verdict beyond the listing.
- **R — proof rebuild (OPTIONAL; owner-gated; after sweep).** Rebuild
  Coq-BB5 with vanilla Coq 8.20.1 on this host, capture the build
  transcript and the axiom-dependency print at end of compilation.
  Maximum label: *"the proof was rebuilt with Coq 8.20.1 on this host;
  compilation exited [0/other]; the end-of-build assumption print reads
  [verbatim]."* Installing a toolchain is an owner-gated system change;
  without explicit consent R is recorded NOT-RUN-OWNER-GATE.

## 3. W protocol (frozen)

- Engines: `audit_bb5/bb5_engine_p.py` (centered growing list tape) and
  `audit_bb5/bb5_engine_q.py` (two-stack tape), stdlib-only Python,
  structurally disjoint implementations; the battery table is
  textually duplicated in both.
- Frozen semantics: machine strings in bbch standard format (groups
  A.., two 3-char clauses per group, `[01][LR][A-Z]`; `Z` = halt;
  `---` = undefined). Start: all-zero tape, head at position 0, state
  A. Every executed clause counts as one step, including a clause whose
  target is Z (write and move are performed, then the machine halts).
  S = executed clauses; Σ = 1s on tape at halt. A `---` read halts the
  machine without write/move and is not counted (supported for item E).
- Battery: Appendix A (15 entries; 2 are the primaries). Acceptance:
  every entry must match its published (steps, ones) exactly.
- Runs (after this file's push): engine P full battery twice; engine Q
  full battery twice; runs 1 of each engine are committed as canonical
  outputs; runs 2 are byte-compared for determinism (engines emit
  timing only to stdout, never into the JSON). Cross-check: the two
  canonical JSONs must agree on every (label, steps, ones). Any
  mismatch → §8.
- Commands (from repo root, in WSL):
  `python3 audit_bb5/bb5_engine_p.py --out reports/audit_bb5_witnesses_p_2026-10-18.json`
  `python3 audit_bb5/bb5_engine_q.py --out reports/audit_bb5_witnesses_q_2026-10-18.json`
  plus determinism reruns to a temp path; all stdout teed into
  `reports/audit_bb5_phaseA_2026-10-18.log`.

## 4. S protocol (frozen)

- Command: `curl -sSfL <raw.githubusercontent.com URL of BB5_Statement.v
  at the pinned commit>` into a temp file; then
  `python3 audit_bb5/artifact_checks.py sha256lf <file>`; `wc -l -c`.
- The transcription already recorded in recon §3 is compared against
  the downloaded bytes (the quoted fragments must occur verbatim); any
  divergence → §8. The sha256LF is recorded in the final report; no
  other interpretation of the file is attempted in Phase A.

## 5. H protocol (frozen)

- Commands: `git clone` (pinned commit; `git rev-parse HEAD` verified),
  then
  `grep -rnE '\b(Admitted|admit|Axiom|Axioms|Parameter|Parameters|Conjecture|Hypothesis|Abort)\b' --include='*.v' .`
  from the clone root; hit list and per-pattern counts captured into
  the log verbatim.
- Classification (frozen): hits under `BusyCoq/` = third-party snapshot
  (their own pinned commit); `Hypothesis`/`Parameter` inside `Section`
  scopes = section-local (expected in `BB5_Statement.v`); a top-level
  `Parameter`/`Axiom` = flag (recorded, not silently excused); any
  `Admitted`/`admit`/`Abort` = FAIL-CLOSED flag for the file(s) where it
  occurs. The scan is textual: no grepping rule of ours is a kernel
  check, and blunt-string hits may over- or under-count; both are
  recorded as-is.
- Reference claim for later comparison (recorded now, not treated as
  evidence): the Coq-BB5 README states the proof depends only on
  `functional_extensionality_dep` (recon §2). A full assumptions check
  requires Coq and belongs to item R only.

## 6. E protocol (frozen)

- Download `BB3_verified_enumeration.csv` (Zenodo; md5 must equal
  `c8379d1ff7fe5e7e0cc5674ade695cd6`), sha256 recorded.
- E1 (structure): header must be `machine,status,decider`; count rows,
  statuses, duplicates; every machine must split into 3 groups of 6
  chars in `[01LRABCDEZ-]`. Issues recorded verbatim.
- E2 (replay): every `halt` row simulated by engine P and by engine Q
  with the frozen semantics (`---` halts, uncounted; `--max-steps`
  1,000,000). X = max executed steps, Y = max ones, with full argmax
  lists. Engine P and Q must agree on (X, Y, argmax sets).
- E3 (decision table, frozen):
  - X in {20, 21} and Y in {5, 6} → CONSISTENT; sub-note: X = 20 is
    recorded as the documented one-step difference between partial
    (`---`) encoding counts and the standard counting (cf. the
    `HaltsAtPlusOne` note in `BB5_Statement.v`), X = 21 as EXACT; the
    exact (X, Y) and argmax machines are quoted in the report.
  - anything else → DISCREPANCY (§8).
  - a `halt` row not halting within the cap, or any engine crash on a
    row → DISCREPANCY.
- E4 (informational probes, presence not required): the partial forms
  `1RB---_1LB0RC_1LC1LA` and `1RB---_0RC1RB_1LC1LA`, and the Z-form
  wiki champion strings, are looked up and their presence/absence
  recorded.
- No independent enumeration claim is made: E checks the published
  file against itself and against two published constants only.

## 7. P protocol (frozen)

- Download `Coq-BB5-1.0.0.tar.gz` from Zenodo; `md5sum` must equal the
  API value `3389c379d35186549eb600b547a81a3c`; sha256 recorded.
- Clone the repository, checkout the pinned commit, verify
  `git rev-parse HEAD`; then
  `python3 audit_bb5/artifact_checks.py weld-tar <tgz> <clone>`.
- Output JSON lists only-in-tar / only-in-clone / changed (relative
  paths + hashes). Recorded a priori as hypothesis, not expectation:
  the archive was created 2025-09-05, the pinned commit is 2025-09-20
  (a later README bibliography edit is known to exist), so ≥ 1 changed
  file is plausible; whatever the listing shows is quoted verbatim.

## 8. Discrepancy protocol (frozen)

- Any mismatch in W/S/H/E/P: record as DISCREPANCY with full details
  (inputs, outputs, commands); rerun once; if persistent, investigate
  inside the cap and document; never hand-edit expectations, never
  silently change tools or constants. No parameter (constants, battery,
  semantics, caps, patterns) is changed in response to any interim or
  final result. Tool fixes after first execution (e.g., a genuine
  crash) are allowed but must keep the ENTIRE battery green and are
  listed in the report changelog with the final tool hashes.
- Cap changes are only via a new dated decision entry, never silent.
- Anti-circularity gate (repo skill) is run at report time over this
  audit's own claim surface; its output is attached to the report; it
  can only downgrade wording, never upgrade it.

## 9. Environment and budget (frozen)

- Machine: this Windows host + WSL2 Ubuntu (python3 3.14.4); engines
  single-threaded, stdlib only. The host is concurrently finishing the
  P1 DBN L1 sweep; Phase A runs one core with `nice -n 10`.
- Phase A caps (wall): W ≤ 30 min (four engine passes); S ≤ 5 min;
  H ≤ 10 min; E ≤ 15 min; P ≤ 20 min; Phase A total ≤ 90 min. Overrun
  → UNRESOLVED-BUDGET recorded; partial outputs stay as-is.
- Phase R (optional): precondition = L1 sweep complete AND explicit
  owner consent (installing opam/Coq = owner-gated system change).
  Setup cap ≤ 3 h wall; build cap ≤ 14 h wall; overrun or failure →
  recorded as-is (NOT-RUN-ENVIRONMENT / BUILD-FAILED / UNRESOLVED-
  BUDGET). The 10 GB extraction step is excluded by design.

## 10. Artifacts and non-modifications

- Produced by this audit: this file; `AUDIT_BB5_RECON_2026-10-18.md`;
  `audit_bb5/{bb5_engine_p,bb5_engine_q,artifact_checks}.py`;
  `reports/audit_bb5_phaseA_2026-10-18.log`; canonical witness JSONs;
  E/P JSONs; the final report `AUDIT_BB5_REPORT_<date>.md`; afterwards
  the fence-registry entry `A-2026-0002` (registry convention: entry
  follows the final report, mirroring A-2026-0001).
- Non-modifications: nothing existing is edited; the live sweep log is
  not touched; third-party artifacts (GitHub, Zenodo, wiki, Michel
  page) are accessed read-only; no secrets are displayed; staging is
  per named file only (never `git add -A`).

## 11. Ordering proof

- This file (with the engines) is committed and pushed BEFORE the
  first audit command (the engine battery run). Evidence: git commit
  timestamp of this file; the audit log's first line records the
  wall-clock start (> commit time); the pinned commit, Zenodo record,
  and wiki oldids make every target immutable for the duration.
- Repo CI must be green for the push; `origin/main == HEAD` verified.

Declared by the analysis session on 2026-10-18, before execution.

## Appendix A — frozen fixture battery (identical table in both engines)

Sources: W2=wiki BB(2) oldid 5358; W3=wiki BB(3) oldid 8372;
W5=wiki BB(5) oldid 9024 timeline; W5t=wiki BB(5) oldid 9024
top-halters; Wc=5-state winner oldid 4369; M=Michel/beh.

    classic-2state  1RB1LB_1LA1RZ                                6         4        W2
    green-1964      1LD1LB_1LZ1LA_0LB1LD_0LE0LD_1RE1RC            79        13       W5
    brady-1964      1RB1LD_0LC0RC_1LC1LA_1RZ0LA                   84        11       W5
    lee-1965        1RB0RC_1LA1RA_1RZ1RD_1LD0LB                   96        13       W5
    brady-1966      1RB1LB_1LA0LC_1RZ1LD_1RD0RA                   107       13       W5
    lynn-1972       1RB1RA_1LC0LD_0RA1LB_1RZ0LE_1RC1RB            435       15       W5
    weimann-1973    1RB0LD_1RC0RB_1LA0RA_0LC0LE_1LC1RZ            992       23       W5
    lynn-1974       0RB1RZ_1RC0LD_1RD0RE_1LB0LD_1RE1RA            7707      88       W5
    schult-1982     1RB0LC_1RC1RD_1LA0RB_0RE1RZ_1LC1RA            134467    501      W5
    uhing-1984      1RB1LC_0LA0LD_1LA1RZ_1LB1RE_0RD0RB            2133492   1915     W5
    feb-1986        1RB1RZ_1LC1RC_0RE0LD_1LC0LB_1RD1RA            2358064   1471     W5/W5t
    mb89-sigma      1RB1RA_1LC1LB_1RA1LD_1RA1LE_1RZ0LC            11798826  4098     W5/W5t/Wc/M  PRIMARY
    mb89-runner     1RB0LD_1LC1RD_1LA1LC_1RZ1RE_1RA0RB            23554764  4097     W5/W5t
    mb89-shift      1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA            47176870  4098     W5/W5t/Wc/M  PRIMARY
    bb3-champion    1RB1RZ_1LB0RC_1LC1LA                          21        5        W3

(Rows marked W5 are shown on the wiki timeline with "≥" prenotation and
are frozen here as the machines' actual run lengths; a mismatch is a
§8 discrepancy, never a re-labeling.)
