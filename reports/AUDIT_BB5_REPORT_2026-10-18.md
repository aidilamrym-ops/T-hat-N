# P1 probe audit â€” report (BB(5) = 47,176,870; Coq-BB5 release v1.0.0) â€” A-2026-0002

Date: 2026-10-18. Status: **execution complete for items W/S/H/E/P; item R
NOT-RUN (owner-gated).** This is the post-execution record for the item list
and frozen labels of `reports/AUDIT_BB5_PREREG_2026-10-18.md` (commit
`fe90659`, pushed 2026-10-18 04:14Z; CI run `39096422610` success).

Ordering: Phase A ran 2026-10-18 04:15:36Z â†’ 04:17:01Z (85 s wall; cap was
90 min), strictly after the pre-registration push. The verbatim runner
script, tool hashes, and all raw outputs are in
`reports/audit_bb5_phaseA_2026-10-18.log`. Read-only reference notes
(pre-execution): `reports/AUDIT_BB5_RECON_2026-10-18.md`.

## 1. Headline results (labels at the frozen maximum)

| item | result | what the label means (frozen) |
|---|---|---|
| W witness replay | **PASS-EXACT** | both published halt witnesses replayed exactly by two independent in-repo engines; all 15 battery entries reproduced their published run lengths and ones counts |
| S statement | RECORDED | statement file at the pinned commit downloaded, sha256LF-hashed, transcribed verbatim (Â§3) |
| H hygiene | RECORDED (textual only) | scan run; counts and flags listed verbatim (Â§4); not a kernel check |
| E BB(3) replay | **CONSISTENT** (frozen decision table) | published enumeration file replayed row-by-row for its halt rows; numbers as recorded (Â§5) |
| P weld | LISTED | archive md5 exact; file-by-file weld listed (Â§6) |
| R rebuild | **NOT-RUN** | owner-gated; preconditions: L1 sweep complete + explicit owner consent (Â§7) |
| anti-circularity gate | TOOL NOT RUN (NO_LEAN_FILES) | verbatim in Â§8; never reported as success |

Key numbers (machine-extracted from the canonical engine outputs):

- `mb89-shift` `1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA`: **47,176,870 steps,
  4,098 ones** â€” identical in engine P and engine Q.
- `mb89-sigma` `1RB1RA_1LC1LB_1RA1LD_1RA1LE_1RZ0LC`: **11,798,826 steps,
  4,098 ones** â€” identical in both engines.
- statement file sha256LF
  `cac368d2d0d018c580b7fd88233f1da3111ee5f63776921b79b97bd78a75927d`
  (120 lines, 3,768 bytes).
- Zenodo tarball md5 `3389c379d35186549eb600b547a81a3c` **matches** the
  md5 pinned from the Zenodo API; weld: 218/218 files present, 217
  identical, 1 changed (`README.md`).
- BB(3) enumeration: 5,417 rows; 1,772 `halt` rows replayed; max steps
  (partial-counting) 20, max ones 6; argmax machines are the `---`-form
  counterparts of the published BB(3) champions.

## 2. W â€” witness replay (frozen battery of 15 fixtures)

Engines (committed in `fe90659`; raw hashes in Â§10): `audit_bb5/bb5_engine_p.py`
(direct interpreter, centered growing list tape) and `audit_bb5/bb5_engine_q.py`
(two-stack tape, flat transition table), stdlib-only Python 3.14.4 (WSL2).
Frozen semantics: bbch standard format; all-zero tape; state A; every
executed clause counts as one step, **including** a clause whose target is
`Z` (write and move performed, then halt); `---` = undefined (halt on that
read, write/move not performed, uncounted).

Protocol executed: engine P run 1 â†’ canonical
`reports/audit_bb5_witnesses_p_2026-10-18.json`; engine P run 2 â†’ temp;
`cmp` byte-equal; engine Q run 1 â†’ canonical
`reports/audit_bb5_witnesses_q_2026-10-18.json`; engine Q run 2 â†’ temp;
`cmp`; cross-engine comparison of every (label, steps, ones).

Results â€” identical in both engines; canonical JSONs agree entry-by-entry
(all 15 rows `MATCH`; `all_match = true` in both files):

| label | machine | steps | ones | source |
|---|---|---|---|---|
| classic-2state | `1RB1LB_1LA1RZ` | 6 | 4 | wiki BB(2) oldid 5358 |
| green-1964 | `1LD1LB_1LZ1LA_0LB1LD_0LE0LD_1RE1RC` | 79 | 13 | wiki BB(5) oldid 9024 timeline |
| brady-1964 | `1RB1LD_0LC0RC_1LC1LA_1RZ0LA` | 84 | 11 | same |
| lee-1965 | `1RB0RC_1LA1RA_1RZ1RD_1LD0LB` | 96 | 13 | same |
| brady-1966 | `1RB1LB_1LA0LC_1RZ1LD_1RD0RA` | 107 | 13 | same |
| lynn-1972 | `1RB1RA_1LC0LD_0RA1LB_1RZ0LE_1RC1RB` | 435 | 15 | same |
| weimann-1973 | `1RB0LD_1RC0RB_1LA0RA_0LC0LE_1LC1RZ` | 992 | 23 | same |
| lynn-1974 | `0RB1RZ_1RC0LD_1RD0RE_1LB0LD_1RE1RA` | 7,707 | 88 | same |
| schult-1982 | `1RB0LC_1RC1RD_1LA0RB_0RE1RZ_1LC1RA` | 134,467 | 501 | same |
| uhing-1984 | `1RB1LC_0LA0LD_1LA1RZ_1LB1RE_0RD0RB` | 2,133,492 | 1,915 | same |
| feb-1986 | `1RB1RZ_1LC1RC_0RE0LD_1LC0LB_1RD1RA` | 2,358,064 | 1,471 | same + top-halters |
| mb89-sigma (**PRIMARY**) | `1RB1RA_1LC1LB_1RA1LD_1RA1LE_1RZ0LC` | 11,798,826 | 4,098 | oldid 9024 champions/top-halters; oldid 4369; michel/beh |
| mb89-runner | `1RB0LD_1LC1RD_1LA1LC_1RZ1RE_1RA0RB` | 23,554,764 | 4,097 | same |
| mb89-shift (**PRIMARY**) | `1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA` | 47,176,870 | 4,098 | same |
| bb3-champion | `1RB1RZ_1LB0RC_1LC1LA` | 21 | 5 | wiki BB(3) oldid 8372 |

Every row halted via the `Z` path; the `---` (undefined) path was exercised
in item E. Determinism: `DETERMINISM_P_OK`, `DETERMINISM_Q_OK`
(byte-identical reruns). Cross-engine: `CROSS_ENGINE_AGREE=True`. Wall
clock: the whole of Phase A â€” four battery passes plus S/H/E/P â€” took 85 s.

## 3. S â€” statement transcription (pinned, hashed, quoted)

Fetched at the pinned commit `9142e219229baf2245d3f70851947230ea28a318`:
`CoqBB5/BB5/BB5_Statement.v` via `raw.githubusercontent.com`; a second,
independent copy of the same path came from the item-H git clone checked
out at the same commit; the two sha256 values agree exactly
(log, "two-path file hash").

- file: 120 lines, 3,768 bytes; sha256LF
  `cac368d2d0d018c580b7fd88233f1da3111ee5f63776921b79b97bd78a75927d`
  (equals the raw sha256: the file has LF endings).
- structure as read (line numbers from the fetched bytes): file-level
  `Inductive St` (5 states) and `Inductive Î£ := Î£0 | Î£1` (2-symbol alphabet)
  with their helpers; `Section TM.` (47) â€¦ `End TM.` (110), inside which
  `Hypothesis Î£:Set` / `Hypothesis Î£0:Î£` (50â€“51) shadow the file-level names
  and are discharged into the definitions (`Trans`, `TM := St->Î£->option
  Trans`, `ExecState`, `InitES`, `upd`, `mov`, `step`, `Steps`,
  `HaltsAtPlusOne`) when the section closes; after the section, the
  definitions are applied at the file-level `Î£`/`Î£0` in the statement.
- verified fragments (verbatim):

  line 112: `Definition BB5 := 47176870%N.`

  lines 100â€“108 (the file's own off-by-one note and the inductive it
  justifies):
  ```coq
  (** `HaltsAtPlusOne tm n st` holds if Turing machine `tm` halts at configuration `st` after `n` steps.

    Note: Coq-BB5 'HaltsAt' definition (see TM.v) is off by one compared to RadÃ²'s definition which is why we have to use 'HaltsAtPlusOne'
          here in order to prove BB(5) = 47176870 and not BB(5) = 47176869.
  *)
  Inductive HaltsAtPlusOne(tm:TM): nat->ExecState->Prop :=
  | HaltsAtPlusOne_intro n st:
    (exists st', Steps tm n st st' /\ step tm st' = None) ->
    HaltsAtPlusOne tm (S n) st.
  ```

  lines 119â€“121:
  ```coq
  Definition BB5_value_statement :=
    (forall tm n0, HaltsAtPlusOne Î£ tm n0 (InitES Î£ Î£0) -> n0 <= N.to_nat BB5) /\
    (exists tm, HaltsAtPlusOne Î£ tm (N.to_nat BB5) (InitES Î£ Î£0)).
  ```
- related constant, observed: `Definition BB5_minus_one:N := 47176869.`
  (`CoqBB5/BB5/BB5_Encodings.v:13`). Under the file's own stated
  convention (HaltsAt off by one; HaltsAtPlusOne = the standard count), the
  replayed bbch count 47,176,870 (item W) and the pair
  (BB5_minus_one = 47,176,869 under `HaltsAt`, BB5 = 47,176,870 under
  `HaltsAtPlusOne`) line up; this audit records the correspondence and does
  **not** formalize it.
- transcription check: every fragment quoted in recon Â§3 occurs verbatim in
  the fetched bytes; no divergence.
- boundary: transcription only. Nothing here says the statement compiles,
  is proved, or is true; compilation and assumption print belong to item R.

## 4. H â€” hygiene scan (textual; frozen pattern list)

Command (verbatim in the log; run from the item-H clone, `git rev-parse
HEAD` = pinned commit, working tree clean):

`grep -rnE '\b(Admitted|admit|Axiom|Axioms|Parameter|Parameters|Conjecture|Hypothesis|Abort)\b' --include='*.v' .`

Counts (case-sensitive, whole words): `Admitted` 0 Â· `admit` 3 Â· `Axiom` 1 Â·
`Axioms` 0 Â· `Parameter` 14 Â· `Parameters` 0 Â· `Conjecture` 0 Â·
`Hypothesis` 344 Â· `Abort` 0 â€” total 362 â‰¤ 400 display cap, so the log holds
the complete hit list. Classification, from the contexts inspected at the
same clone (all quoted in the log):

- **14Ã— `Parameter`** â€” all in `BusyCoq/TM.v` lines 17â€“43, inside
  `Module Type Ctx.` (16â€“44): the interface fields `Q, Sym, q0, s0, q1,
  q0_neq_q1, s1, s0_neq_s1, eqb_q, eqb_sym, all_qs, all_qs_spec, all_syms,
  all_syms_spec`; consumed by `Module TM (Ctx : Ctx)` and instantiated with
  concrete types **and proofs** in `BusyCoq/BB52.v` (`Module BB52 <: Ctx`:
  `q0_neq_q1`/`s0_neq_s1` by `discriminate`, `eqb_*` by `decide equality`,
  `all_*_spec` by `destruct`). Module-functor interface, not global axioms.
- **344Ã— `Hypothesis`** â€” the section-local pattern. Sample inspections:
  `CoqBB5/BB5/TM.v` `Section TM.` (11) â€¦ `End TM.` (714) contains
  `Hypothesis Î£:Set` / `Î£0:Î£` (25â€“26); `CoqBB5/BB5/BB5_Statement.v` 50â€“51
  is the same pattern (shadowing, discharged â€” Â§3); the other `TM.v` copies
  (BB2â€“BB4, BB2x3, BB2x4, legacy monoliths) repeat it. When a section
  closes, these become parameters of the objects defined inside it; they
  are not top-level axioms. Recorded as-is; not a kernel check.
- **1Ã— `Axiom`** â€” `BusyCoq/LibTactics.v:2725`: `Axiom inj_pair2 :` with type
  `forall (U:Type)(P:U->Type)(p:U)(x y:P p), existT P p x = existT P p y ->
  x = y`, the in-file comment "is in fact derivable from the axioms in
  LibAxiom.v" and a commented-out proof line; it feeds `Ltac inverts_tactic`
  immediately below. `BusyCoq/Helper.v:11` (`From BusyCoq Require Export
  LibTactics.`) and `CoqBB5/BB5/BB5_Skelet17.v:3` (`From BusyCoq Require
  Import Individual52.`) put the file in the import closure of the BB5
  development. Whether `inj_pair2` occurs in the proof-term dependency cone
  of `BB5_value` cannot be decided by text; the source's own resolver is the
  last line of `BB5_Theorem.v`, `Print Assumptions BB5_value.`, whose
  output belongs to item R. Flag recorded; **no defect claim, no cleanliness
  claim.**
- **3Ã— `admit`** â€” `BusyCoq/LibTactics.v`: line 4853 inside the "Tactics
  for Development Purposes" block (`Tactic Notation "skip" := admit.`), plus
  comment mentions at 4855 and 4862 (`demo` / `admits` notations). A tactic
  *definition*; use-sites not resolved textually. Flag recorded, as frozen
  ("any admit = FAIL-CLOSED flag for the file").
- **0Ã—** `Admitted`, `Abort`, `Conjecture`, `Axioms`, `Parameters`.

Scope: this section reports a textual scan. It is not a kernel check; it
neither clears nor condemns any file; absence claims hold only for the exact
patterns listed.

## 5. E â€” BB(3) enumeration replay (secondary item)

File: `BB3_verified_enumeration.csv` from Zenodo record `17061968`; md5
`c8379d1ff7fe5e7e0cc5674ade695cd6` **matches** the API-pinned value; sha256
`d1b5df70df506eab6607edeaa181274d5f5a7c58e8aad24bba4a991c351e9c38`.

- E1 structure: header `machine,status,decider`; 5,417 data rows; statuses
  `halt` 1,772 / `nonhalt` 3,645; 5,417 unique machines; no duplicate rows;
  no malformed machine strings.
- E2 replay: every `halt` row simulated by both engines under the frozen
  semantics with `--max-steps 1000000`: all 1,772 halted; zero anomalies;
  engines agree on (X, Y, argmax) (`E-PQ-AGREE=True`).
  - **X = max executed steps = 20**, single argmax machine
    `1RB---_1LB0RC_1LC1LA`.
  - **Y = max ones = 6**, argmax machines: `1RB---_0RC1RB_1LC1LA`,
    `1RB1LC_1LA1RB_1LB---`, `1RB1LC_1RC---_1LA0LB`, `1RB1RA_1LC---_1RA1LB`,
    `1RB1RC_1LC---_1RA0LB`.
- E3 decision table (frozen): X âˆˆ {20, 21} and Y âˆˆ {5, 6} â†’ **CONSISTENT**;
  the X = 20 branch is recorded as the documented one-step convention
  difference (the `---`-form halts on the undefined read, so the Z-clause of
  the standard form is never executed â€” one step fewer than the standard
  count; cf. the `HaltsAtPlusOne` note in Â§3).
- E4 probes: `1RB---_1LB0RC_1LC1LA` present; `1RB---_0RC1RB_1LC1LA`
  present; `1RB1RZ_1LB0RC_1LC1LA` absent; `1RB1RZ_0RC1RB_1LC1LA` absent.
- Reading: the argmax machines are the `---`-form counterparts of the
  published BB(3) champions (shift: 20 + 1 unexecuted clause = 21; ones:
  Î£ = 6). This is a replay of the published file's halt rows â€” not an
  independent enumeration, and with no claim about any non-halting row.
- Outputs: `reports/audit_bb5_bb3_p_2026-10-18.json`,
  `reports/audit_bb5_bb3_q_2026-10-18.json`.

## 6. P â€” release/repository weld

- Download: `Coq-BB5-1.0.0.tar.gz` from the Zenodo API; md5
  `3389c379d35186549eb600b547a81a3c` **matches** the md5 pinned from the
  Zenodo record (`17061968`); sha256
  `3a9f42761c8d35be7b3c0f7aeb69cbc434d27d337b702a4251e3242f8f28045e`
  (616,415 bytes).
- Weld (`artifact_checks.py weld-tar`; JSON
  `reports/audit_bb5_weld_2026-10-18.json`): tarball 218 files / clone 218
  files; identical 217; **only difference: `README.md`** (content hash
  differs); no file exists on one side only.
- A-priori hypothesis (pre-registration Â§7, recorded before execution): the
  archive was created 2025-09-05 and the pinned commit is 2025-09-20, with a
  known upstream README bibliography edit â€” so â‰¥ 1 changed file was
  plausible; the observed change set is exactly {`README.md`}. Recorded as a
  listing; no verdict beyond it (in particular: no claim about which side is
  "current" â€” the pinned commit is the audit's own reference throughout).

## 7. R â€” proof rebuild: NOT-RUN (owner-gated)

Status: **NOT-RUN-OWNER-GATE** (as of this report). Preconditions per
pre-registration Â§9: (1) the L1 DBN sweep complete (still running at report
time), and (2) explicit owner consent, because installing opam/Coq 8.20.1 is
a system-level change. What R would do, unchanged: vanilla Coq 8.20.1 in a
fresh opam switch; `make` in `BusyCoq/` then in `CoqBB5/BB5/`; capture the
build transcript and the end-of-build `Print Assumptions BB5_value.` output
(the command is the last line of `BB5_Theorem.v` â€” the source's own
assumption-print mechanism); compare against the README claim ("only
functional_extensionality_dep"). Caps: setup â‰¤ 3 h; build â‰¤ 14 h; the 10 GB
extraction step is excluded by design. Until R runs, the dependency-cone
flags of Â§4 remain open by design, and the README assumption claim remains
untested by this audit.

## 8. Anti-circularity gate (repo skill, run at report time)

Run against the eleven audit artifacts produced before this report (three
engines, recon, pre-registration, five JSONs, the Phase-A log); the report
itself is not fed to the gate (self-reference). Verbatim result:

```text
ANTI-CIRCULARITY GATE [check]
  NOT RUN  NO_LEAN_FILES: no .lean input matched
  result: FAIL=0  NOT_RUN=1  SKIP=0
  verdict: TOOL NOT RUN
```

Exit code 2. Per the skill, TOOL NOT RUN is never reported as success. This
audit contains no Lean or SMT artifacts, so the gate's placeholder/claim
machinery has no domain here; its only possible effect is to downgrade
wording. Consequence applied throughout this report: no "verified" or
"machine-checked" vocabulary is used about the Coq artifact; the labels of
Â§1 are the ones frozen in the pre-registration.

## 9. Non-claims (frozen; restated)

- The universal direction ("no 5-state machine beats 47,176,870") is NOT
  tested by anything in this report.
- W is a finite arithmetic replay of two published halt witnesses plus
  thirteen historical fixture machines â€” not a peer review, not a proof of
  BB(5).
- H is a textual scan, not a kernel check; it neither clears nor condemns
  any file.
- E replays only the published file's halt rows; no non-halting claim; not
  an independent enumeration.
- P lists differences; it makes no judgment beyond the listing.
- R did not run; no statement about compilation, proof checking, or
  assumption-dependence is made.
- Nothing here touches or supports any claim about RH or Pâ‰ NP; this is an
  external probe audit. (MAX-LABEL rule: nothing in this audit may be quoted
  above the labels of Â§1.)

## 10. Evidence chain, hashes, reproduction

- Ordering: pre-registration commit `fe90659` (push 04:14Z; CI run
  `39096422610` success) < Phase A start 04:15:36Z. The runner script is
  quoted verbatim at the top of the log; tool hashes (raw sha256, from the
  log): `audit_bb5/bb5_engine_p.py`
  `a94220774443486bad7ad2c38141a20ecfce43103204989867f49950ab4af1b4`,
  `audit_bb5/bb5_engine_q.py`
  `37b96a2b4a02530b31c0fe2e9b984a1d2c0a22bc7aea3648b3b5f98072f2a4b1`,
  `audit_bb5/artifact_checks.py`
  `03d69223587e4fcae9ecab30e96931de99ccb531db5e20ff988ba7cfd4762ff4`.
- LF-normalized hashes (`sha256LF`, registry convention) for every artifact
  of this audit are recorded in `reports/FENCE_REGISTRY.md`, entry
  `A-2026-0002`; the CI guard `msaf/tests/test_fence_registry.py` re-verifies
  each one on every push.
- Reproduction (from repo root, WSL):
  - `python3 audit_bb5/bb5_engine_p.py --out <file>` /
    `python3 audit_bb5/bb5_engine_q.py --out <file>` â€” battery W.
  - `python3 audit_bb5/artifact_checks.py bb3-max <csv> --engine p|q` â€” item E.
  - `python3 audit_bb5/artifact_checks.py weld-tar <tgz> <clone>` â€” item P.
  - `python3 audit_bb5/artifact_checks.py sha256lf <file...>` â€” hashing.
- Time budget: Phase A 85 s wall (cap 90 min); no overrun; no
  UNRESOLVED-BUDGET.
- Artifact inventory: this report; `AUDIT_BB5_RECON_2026-10-18.md`;
  `AUDIT_BB5_PREREG_2026-10-18.md`; `audit_bb5_phaseA_2026-10-18.log`;
  witness JSONs (P, Q); weld JSON; BB(3) JSONs (P, Q); engine/check scripts;
  registry entry `A-2026-0002`; HANDOFF Â§2.0q.


