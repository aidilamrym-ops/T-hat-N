# P1 audit — reconnaissance (BB(5) = 47,176,870, bbchallenge / Coq-BB5)

Date: 2026-10-18 (local). Status: **reference, not result.** Read-only
fetches only. No simulation, no download-and-hash of targets, and no
source scan was executed before the pre-registration file
`reports/AUDIT_BB5_PREREG_2026-10-18.md`. This document records what was
read, from where, and under which identifiers, so pre-registered
expectations can be checked against pinned public sources.

## 1. Pinned sources

- S1. Repository of record for the formal artifact:
  `github.com/ccz181078/Coq-BB5`, branch `main`, commit
  `9142e219229baf2245d3f70851947230ea28a318` (2025-09-20; commit
  signature verified by GitHub per API), tree
  `616f07b54639263638a09dabde7312ca1b534b50`; 218 blobs, ≈ 853 KB.
- S2. Archival release: Zenodo record `17061968` (concept `17061967`),
  DOI `10.5281/zenodo.17061968`, "Coq-BB5 release v1.0.0". File md5s
  pinned from the Zenodo API: `Coq-BB5-1.0.0.tar.gz` (616,415 B, md5
  `3389c379d35186549eb600b547a81a3c`), `Coq-BB5-1.0.0.zip` (710,014 B,
  md5 `dc24f72317503339476d3028128de0f6`).
- S3. Paper: arXiv:2509.12337v2 (2026-03-23), "Determination of the
  fifth Busy Beaver value". Abstract: "S(5) = 47,176,870"; "enumerates
  181,385,789 Turing machines with 5 states"; "first Busy Beaver value
  ever to be formally verified".
- S4. BusyBeaverWiki "BB(5)", oldid `9024` (2026-10-08), CC BY.
  (Rendered preview + MediaWiki API wikitext; `action=raw` was blocked
  by an anti-bot interstitial — the API path was used instead.)
- S5. BusyBeaverWiki "5-state busy beaver winner", oldid `4369`
  (2025-10-07), CC BY.
- S6. BusyBeaverWiki "BB(2)", oldid `5358` (2025-12-04), CC BY.
- S7. BusyBeaverWiki "BB(3)", oldid `8372` (2026-08-23), CC BY.
- S8. Pascal Michel, "Behavior of busy beavers",
  `bbchallenge.org/~pascal.michel/beh` (fetched 2026-10-18).

## 2. Published values transcribed (frozen expectations)

- Shift champion (S(5) witness): `1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA`
  — "halts after 47176870 steps with 4098 ones" [S5; same string S4;
  S8: s = 47,176,870, sigma = 4098]. S5 shows the A..E transition
  table, clause-for-clause equal to the bbch string.
- Ones champion (Σ(5) witness, second ones champion in TNF):
  `1RB1RA_1LC1LB_1RA1LD_1RA1LE_1RZ0LC` — "runs for 11,798,826 steps"
  [S4 champions section; S4 top-halters row 15: 11798826/4098; S8].
- Battery ladder (Appendix A): historical machines and values from S4
  timeline (shown there with "≥" prenotation; treated as the machines'
  actual run lengths — the W protocol handles any mismatch as a
  discrepancy, not as a rationalization), S4 top-halters (exact 20-row
  list), S6 (2-state classic), S7 (BB(3) champion).
- Winner-page trajectory segment times sum exactly to 47,176,870:
  15+73+277+907+2757+7957+22777+64407+180307+504027+1403967+3906393
  +10861903+30196527+24576 = 47,176,870 (checked by hand; corroboration
  only; not an audit item).
- BB(3) facts used for item E [S7]: S(3)=21; unique TNF shift champion
  `1RB1RZ_1LB0RC_1LC1LA` (21 steps, 5 ones); Σ(3)=6.
- Coq-BB5 README claim relevant to item R: "outputted at the end of the
  compilation, the proof only depends on Coq's standard library axiom
  functional_extensionality_dep" (their claim; compared in R only).

## 3. Statement file (read at pinned commit; re-fetched and hashed at execution)

Path: `CoqBB5/BB5/BB5_Statement.v` (commit S1). Key transcribed fragments
(small excerpts for audit commentary; the repository declares no
license on GitHub — recorded as-is):

    Definition BB5 := 47176870%N.

    Definition BB5_value_statement :=
      (forall tm n0, HaltsAtPlusOne Σ tm n0 (InitES Σ Σ0) -> n0 <= N.to_nat BB5) /\
      (exists tm, HaltsAtPlusOne Σ tm (N.to_nat BB5) (InitES Σ Σ0)).

The file's own comment states that `HaltsAt` is off by one compared to
Radò's definition, "which is why we have to use `HaltsAtPlusOne` here
in order to prove BB(5) = 47176870 and not BB(5) = 47176869". The file
defines `TM := St -> Σ -> option Trans` (partial transition function),
states St0..St4, symbols Σ0/Σ1, directions Dneg/Dpos. `Hypothesis Σ:Set`
and `Hypothesis Σ0:Σ` occur inside `Section TM` (section-local;
discharged into the definitions). The main theorem name is expected in
`CoqBB5/BB5/BB5_Theorem.v` (to be confirmed in item R only).

## 4. Repository facts (from the tree listing at S1)

- Top level: `README.md`, `BusyCoq/`, `CoqBB5/`. No license file; the
  GitHub API reports no license — recorded, not a verdict.
- Per-result folders: `CoqBB5/BB{2,3,4,5}/`, `CoqBB5/BB2x{3,4}/`, each
  with `*_Statement.v`, `*_Theorem.v`, `Makefile`, `_CoqProject`,
  `*_Deciders_*.v` and decider folders; plus `CoqBB5/BB5/BB5_Extraction/`.
- Build (README, S1): opam switch 4.14.2; opam install coq-native; pin
  coq 8.20.1; then `make` in `BusyCoq/` ("~8 min / 13 cores") and in
  `CoqBB5/BB5/` ("~45 min with coq-native; ~3 h without"). Our host has
  4 logical cores; caps in pre-registration §9.
- README also: 13 sporadic machines (12 via the `BusyCoq/` snapshot
  pinned by them at `333695b79707189d49f5e560a55c3ab8dda1cdc6`;
  Skelet17 in-repo), hardcoded decider parameters for 8,032 machines,
  and a 10 GB extracted CSV (not downloaded by this audit; its "shasum
  ending ...510583a39" recorded as their claim only).

## 5. Auxiliary data files examined (small files only)

- `BB5_normal_form_table_based_machines.csv` (1,470 B): header
  `machine,status,decider`; 26 data rows observed, of which two lack the
  status field (`0RB0LE_1LC1RB_1LA1LD_---0LA_0RA1LE,FAR_certificates`
  and `0RB0LE_1LC1RB_1RB1LD_---0LA_0RA1LE,FAR_certificates`), while
  `CoqBB5/BB5/README.md` reports NORMAL_FORM_TABLE_BASED totals of
  9+14+1 = 24. Recorded as an observed quirk of an auxiliary file, not
  a defect claim.
- `BB3_verified_enumeration.csv` (Zenodo, 240,821 B, md5
  `c8379d1ff7fe5e7e0cc5674ade695cd6`): header `machine,status,decider`;
  3 state groups per machine; clauses `---` = undefined; deciders
  `LOOP1_params_21`, `NGRAM_CPS_IMPL2_params_1_1_100`, etc. Used by
  item E (≈ 5,417 data rows; exact count at execution).

## 6. Environment (verified 2026-10-18)

- WSL2 Ubuntu: python3 3.14.4, git 2.53.0, coreutils (sha256sum);
  no C compiler, no perl/ruby/node/php/go/rustc/java/dotnet. Both
  engines are therefore stdlib-only Python.
- The same host is running the P1 DBN L1 full sweep (started
  2026-10-18T03:10Z); Phase A runs single-core with `nice`.

## 7. What this reconnaissance did NOT do

No audit computation: no machine simulation; no clone of S1; no
download of S2/S2-files or of the BB3 CSV; no hash computation of any
target; no source scan. All such steps happen strictly after the
pre-registration commit, per its §11.

## Appendix A — frozen fixture battery

Sources: W2=§1 S6; W3=§1 S7; W5=S4 timeline; W5t=S4 top-halters; Wc=S5;
M=S8.

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

## Appendix B — BB(5) top halters (S4 wikitext, verbatim; CC BY)

    1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA  Halt 47176870 4098
    1RB0LD_1LC1RD_1LA1LC_1RZ1RE_1RA0RB  Halt 23554764 4097
    1RB1RA_1LC1LB_1RA0LD_0RB1LE_1RZ0RB  Halt 11821234 4097
    1RB1RA_1LC1LB_1RA0LD_1RC1LE_1RZ0RB  Halt 11821220 4097
    1RB1RA_0LC0RC_1RZ1RD_1LE0LA_1LA1LE  Halt 11821190 4096
    1RB1RA_1LC0RD_1LA1LC_1RZ1RE_1LC0LA  Halt 11815076 4096
    1RB1RA_1LC1LB_1RA0LD_0RB1LE_1RZ1LC  Halt 11811040 4097
    1RB1RA_1LC1LB_0RC1LD_1RA0LE_1RZ1LC  Halt 11811040 4097
    1RB1RA_1LC1LB_1RA0LD_1RC1LE_1RZ1LC  Halt 11811026 4097
    1RB1RA_0LC0RC_1RZ1RD_1LE1RB_1LA1LE  Halt 11811010 4096
    1RB1RA_1LC1LB_1RA1LD_0RE0LE_1RZ1LC  Halt 11804940 4097
    1RB1RA_1LC1LB_1RA1LD_1RA0LE_1RZ1LC  Halt 11804926 4097
    1RB1RA_1LC0RD_1LA1LC_1RZ1RE_0LE1RB  Halt 11804910 4096
    1RB1RA_1LC0RD_1LA1LC_1RZ1RE_1LC1RB  Halt 11804896 4096
    1RB1RA_1LC1LB_1RA1LD_1RA1LE_1RZ0LC  Halt 11798826 4098
    1RB1RA_1LC1RD_1LA1LC_1RZ0RE_1LC1RB  Halt 11798796 4097
    1RB1RA_1LC1RD_1LA1LC_1RZ1RE_0LE0RB  Halt 11792724 4097
    1RB1RA_1LC1RD_1LA1LC_1RZ1RE_1LA0RB  Halt 11792696 4097
    1RB1RA_1LC1RD_1LA1LC_1RZ1RE_1RA0RB  Halt 11792682 4097
    1RB1RZ_1LC1RC_0RE0LD_1LC0LB_1RD1RA  Halt 2358064  1471
