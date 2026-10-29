# Replay Record â€” Specification v0.1 (FROZEN)

Status: FROZEN 2026-10-19 in this repository. This is the working spec for the
Replay Record series; changes require a version bump with a dated note. Nothing
in this document executes anything; it defines a record format and a process.
(Series name resolved from the draft working title "Replay Certificate" to the
owner's term "Replay Record"; one instance is a *record*, id `RR-<year>-<seq>`.)

Purpose (one paragraph): a *Replay Record* turns a public claim into a record
that a third party can independently replay, byte-for-byte, and reach the same
verdict â€” including honest records of failure, resource exhaustion, and
tool-unavailability. It is a packaging discipline for claims we already audit
in this programme: pre-registered protocol, as-is log, certificate lines,
gates, explicit non-claims.

## 1. Scope and non-goals

In scope: computational and documentary claims that can be checked by executing
commands and comparing artifacts (proof rebuilds, dataset replays, parameter
reproductions, source snapshots, pin/weld checks).

Non-goals: this is not peer review, not a security audit, not a truth oracle.
It records *what was run, what was observed, and what is (not) claimed*. A
record never asserts more than its evidence; absence of evidence is
recorded, never converted into a verdict.

## 2. Definitions

- **Claim**: a short quotable statement attributed to a source (URL/doc + pin).
- **Protocol**: frozen, ordered, exact commands + caps + expected artifacts +
  decision rules + label set.
- **Prereg**: the protocol (and this record's skeleton) committed *before* the
  first audit command; git history is the ordering proof.
- **Record**: the finished artifact (this format).
- **Gate**: an executable check that can only *downgrade* labels
  (e.g., anti-circularity gate; TOOL-NOT-RUN is a valid gate outcome).
- **sha256LF**: SHA-256 over LF-normalized bytes (the registry convention);
  equals raw sha256 when a file is LF-only. Raw sha256 recorded for binaries.
- **As-is**: outputs appended via `tee`; failures kept; no retro-editing of logs.
- **Registry**: canonical hash ledger (fence registry) with a CI guard that
  re-verifies every certificate line.

## 3. Design principles (P1â€“P8)

- P1 Pre-registration: no audit command before the protocol is committed;
  caps and criteria frozen; no parameter changes after results. Any change =
  new version + dated decision recorded BEFORE proceeding (no silent retries).
- P2 As-is: logs append-only during runs; interruptions, OOM kills, and
  budget overruns are entries, not embarrassments.
- P3 Byte-exactness: one normalization (sha256LF) for text artifacts; scoped
  `.gitattributes` rules (e.g., `text eol=lf`) to protect byte-exact `cmp`;
  normalization events, if any, recorded in the log.
- P4 Minimal trust: third-party tools pinned by hash at use time; if a tool is
  re-used, its hash is recorded; if trust matters, re-implement from spec
  (e.g., reimplementing an RNG rather than running the claimant's code).
- P5 No verdict without evidence: every label cites log lines + artifact hashes.
- P6 Anti-circularity: a gate output (including TOOL-NOT-RUN) attaches verbatim;
  machine-verified vocabulary is only used where a machine actually ran.
- P7 Explicit non-claims: every record lists out-of-scope items, excluded
  items (NOT-RUN), and unresolved residues (e.g., unexplained leftovers).
- P8 Replayability first: prefer plain text, git, and a handful of scripts;
  no special infrastructure required to replay.

## 4. Record anatomy (fields)

1. `id` â€” `RR-<year>-<seq>` + `registry_ref` (fence-registry entry).
2. `title` â€” short, searchable (repo style).
3. `claim` â€” verbatim quote(s), source(s) with pins (commit hash / URL + fetch
   date + capture hash).
4. `class` â€” one of: `proof-rebuild`, `data-replay`, `claim-reproduction`,
   `source-snapshot`, `weld-pin` (extensible; v0.1 lists only used classes).
5. `prerequisites` â€” toolchain (name + version; e.g., "Coq 8.20.1 vanilla, NO
   coq-native"), host minima *measured* (cores, RAM, swap), OS notes.
6. `resource_class` â€” light (<1 min) / standard (â‰¤1 h) / heavy (â‰¤14 h) /
   extreme (multi-attempt, caps + deadline + supervision). Measured, not guessed.
7. `protocol` â€” frozen ordered commands, caps, dev-only vs audit boundary,
   freeze commit hash.
8. `expected_artifacts` â€” list + how to recompute each (sha256LF / sha256).
9. `decision_rules` â€” enumerated criteria â†’ labels (see Â§5).
10. `as_is_log` â€” pointer + hash of the append-only transcript; supervision
    notes; normalization events.
11. `failure_ledger` â€” attempts table (n, window, exit, cause, evidence line
    numbers); interruptions; OOM kills; environment fixes (recorded BEFORE
    retry, with commit id).
12. `gate_outputs` â€” verbatim (e.g., anti-circularity: PASS / FAIL /
    TOOL-NOT-RUN with exit codes).
13. `certificate_lines` â€” the sha256LF block (registry convention).
14. `non_claims` â€” out-of-scope list; NOT-RUN items with reasons; unresolved
    residues (unexplained leftovers) â€” kept as open items, never as claims.
15. `record_provenance` â€” dates, roles (human + agent), repo commit adding the
    record, CI run id; strict rule: frozen reports are never edited; the
    registry/record update is the record.
16. `replay_guide` â€” how a third party replays (expected diffs, e.g.,
    `Generated:` timestamp lines; known non-determinism).

## 5. Label set and verdict rules (v0.1)

- `MATCH` â€” observation meets the frozen criterion (verbatim).
- `MISMATCH` â€” reproducible disagreement with the claim.
- `PARTIAL` â€” some items matched; each item enumerated; no aggregate claim.
- `NOT-RUN` â€” excluded by decision, recorded before execution.
- `TOOL-NOT-RUN` â€” a gate/tool could not run; never counted as success.
- `UNRESOLVED-BUDGET` â€” caps/deadline exceeded before completion; recorded as-is.

Rules: (a) labels are per-item, not aggregate; (b) gates may only downgrade;
(c) every label cites evidence (log lines + hashes); (d) discrepancy protocol:
on anything unexpected â†’ stop, record, dated decision BEFORE proceeding.

## 6. Process (six steps)

1. Prereg: freeze protocol + criteria + caps + labels; commit; push; CI green.
2. Execute: sequential ("one at a time"), `nice -n 19`, every stdout/stderr
   appended via `tee`; exec dir per date; no editing during runs.
3. Evidence: extract verbatim blocks; compute certificates AFTER the log stops
   growing (hash drift otherwise).
4. Gates: run gate(s); record verdicts (downgrade-only); reconcile labels.
5. Record: write the record (Â§4); extend registry; run guard test; commit;
   CI green; publish snapshot (optional DOI) per Â§10.
6. Publish/index (optional for v0.1): update index; announce with non-claims
   attached, not buried.

## 7. Gates and guards

- Anti-circularity gate (three executable checks: placeholder scan,
  comment-only-claim detection, SMT-LIB2 circularity audit) â†’ PASS / FAIL /
  TOOL-NOT-RUN; output verbatim; downgrade-only.
- Registry guard: CI re-verifies every certificate line (sha256LF) â€” a broken
  certificate fails the build.
- Optional v0.2: rubric machine-checked with SMT (e.g., label exclusivity,
  "no verdict without evidence"). Scope caveat: this checks the *logic of the
  rubric*, not the mathematics; must be framed to avoid circularity.

## 8. Case-study anchors (programme history)

- **BB5R** â€” proof-rebuild (extreme; COMPLETED 2026-10-18). 2-core laptop,
  vanilla Coq 8.20.1, no coq-native; attempts ledger incl. kernel OOM kill
  (make: Error 137) and -j2 mitigation; phase R attempt 5 finished with 50/50
  .vo and `Print Assumptions` checked; registry A-2026-0002.
- **COLLATZ-P2** â€” data-replay + weld-pin (heavy; COMPLETED 2026-10-19).
  Pre-registered at commit `bbbe9ae` BEFORE any audit command; independent
  engines P/Q/C; batteries from frozen captures; execution gated on BB5R
  completion + owner signal; report + registry A-2026-0003.
- **ECDSA-V1** â€” claim-reproduction (light; IN FLIGHT). Independently
  reimplement the 1990s C `lrand48`/`srand48` from specification (not running
  the claimant's code), reproduce published curve seeds from given timestamps
  + indices; record residues (unexplained seed, unexplained base points,
  skipped candidates) as non-claims. Record id RR-2026-01; registry
  A-2026-0004 planned (post-execution).

## 9. Definition of done (checklist)

- [ ] Prereg committed before first audit command (git ordering proof).
- [ ] Caps frozen; no post-result parameter changes (or new version + dated
      decision, committed before retry).
- [ ] Log append-only; failures/OOM/interruptions present as entries.
- [ ] All expected artifacts listed; recompute instructions included.
- [ ] Certificates computed post-run; guard test green in CI.
- [ ] Gate output attached verbatim (including TOOL-NOT-RUN if so).
- [ ] Every label cites evidence; no aggregate overclaims.
- [ ] Non-claims section complete (out-of-scope + NOT-RUN + residues).
- [ ] Registry entry + seal row; frozen files unedited.
- [ ] Replay guide with expected diffs.

## 10. Decisions and open items

Resolved for v0.1 (this freeze):

1. Name: **Replay Record** (RR). Supersedes the draft working title.
2. Home: this repository (records under `reports/`, working assets under
   `audit_<claim>/`); a separate public template repo is deferred.
3. ID namespace: records use `RR-<year>-<seq>`; the fence registry keeps
   `A-<year>-<n>` ids; each record names its `registry_ref`
   (working mapping: RR-2026-01 -> A-2026-0004, post-execution).

Still open (not blocking v0.1):

4. Machine-readable sidecar schema: already practiced ad hoc (V1 ships
   `audit_ecdsa/seeds_manifest.json` + per-item JSONs); schema enforcement is
   a v0.2 candidate.
5. License for spec/template: candidate CC0 (matching the ECDSA reproduction
   code's dedication); not finalized here.
6. Publication venue/DOI: Zenodo snapshot (programme plan `docs/ZENODO_ACTIVATE.md`)
   vs preprint; when.
7. Whether the telemetry annex (Appendix B) is mandatory for heavy/extreme
   class; v0.1: not mandatory (V1 is light class).

## 11. Related work and honesty note

Components exist in adjacent practice: artifact evaluation / badging
(conferences), reproducible builds (distro ecosystems), software-supply-chain
provenance (SLSA-style attestations), pre-registration and registered reports
(psychology/medicine), and replication packages in empirical science. The
components are NOT novel. The intended delta â€” to our knowledge, pending a
documented novelty scan if this becomes a claim â€” is the bundle applied to
*famous computational claims*: as-is failure ledgers + measured resource
telemetry + byte-exact normalization with CI-enforced certificates +
downgrade-only gates + explicit non-claims, all public. Any "first / never
done" phrasing must pass its own scan or not be used.

## Appendix A â€” Template skeleton

```markdown
# RR-<year>-<seq>: <title>
- claim: "<verbatim>" â€” source <pin/url, fetched YYYY-MM-DD, capture sha256LF ...>
- class: <...>  |  resource_class: <...>
- prereg commit: <hash>  |  record commit: <hash>  |  CI: <run id>
## Prerequisites
## Protocol (frozen)
## Expected artifacts
## Decision rules
## As-is log (pointer + sha256LF)
## Failure ledger
## Gate outputs (verbatim)
## Certificates
## Non-claims
## Replay guide
```

## Appendix B â€” Telemetry annex (template)

| target | wall time | peak RSS | cores | exit | notes |
|---|---|---|---|---|---|
| (per build step / per item) | | | | | |

Host: CPU model, cores, RAM/swap, OS, toolchain versions. Measured during the
run (e.g., from `time` output and process monitors); used for reproducibility
planning by third parties. Mandatory for heavy/extreme class if Â§10.7 adopted.


