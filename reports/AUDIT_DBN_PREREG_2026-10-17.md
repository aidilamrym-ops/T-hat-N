# P1 audit — pre-registration (Gomila DBN Λ candidate, release review-01787854-v3)

Date: 2026-10-17 (local). Status: **PRE-REGISTERED BEFORE ANY AUDIT
EXECUTION.** At the time of this declaration no L1 replay command, no L2
replication computation, and no L3/L4 verdict step of this audit has been
executed. This file is committed and pushed BEFORE the first audit
command; the git add-commit time of this file and the timestamps in the
audit logs record the ordering. Reconnaissance that PRECEDED this file is
documented (read-only fetches; no computation) in
`reports/AUDIT_DBN_RECON_2026-10-17.md`; that document is reference, not
result, and no claim below is modified by it.

## 1. Target and scope

- Target claim: **Λ ≤ 893927/5000000 = 0.1787854** — unrefereed
  (Jude Gomila et al., 20 Aug 2026; repo
  `judegomila/dbn-lambda-01787854-candidate-audit` + Lean layer).
- Depot of record for this audit: the immutable release
  **`review-01787854-v3` (28 Jul 2026)**, NOT the moving HEAD
  (`a74738de…` per the 2026-10-17 watch; if HEAD moves during the audit,
  the release stays the target and the movement is noted, never merged
  into the target).
- Release identity pins (from recon §7.1; full digests machine-verified
  at fetch time and recorded verbatim in the L1 log): release commit
  `2e9976c4becbf97e31c56fe75fce07cdff5dd4ea` (single parentless commit);
  seal `SHA256SUMS` sha256 `89a20156…`; release manifest sha256
  `e0f134ca…`; referee PDF sha256 `b1151d56…`; OCI image digest
  `sha256:6e29bc53adc5a4337802da2b5a219720e3da9dcc1b87c546b96b6126d8b9975d`;
  offline OCI archive `dbn-lambda-01787854-review-v3.oci.tar` sha256
  `87a4695e…` (172,810,240 byte); container Ubuntu 24.04 linux/amd64,
  replays `--network none`, read-only.
- Obligation IDs are THEIR blueprint IDs (adversarial protocol, recon
  §2): P1 P2 P3 G1 F1 F2 F3 T1 T2 B1 B2 C1. Our verdicts attach to
  these IDs.
- Scope limits (adopted from their own protocol, quoted): "A successful
  repository replay is necessary evidence, but it is not by itself a
  mathematical review." No verdict of this audit is a peer review, a
  physical statement, a universal statement, or a statement about RH.
  Every verdict is a finite claim about pinned artifacts of the release
  above.
- Classes of theorem-level defects their own internal adversarial audit
  had found and fixed before the seal (recon §7.2) are explicit L2
  targets here, not assumed clean: (1) weak frozen angle bound,
  (2) integral-vs-sum, (3) complex-ball → real-part projection breaking
  the holomorphic callback.

## 2. Audit levels L1–L4 (frozen definitions)

- **L1 — replay & provenance (not a mathematical claim).** In the pinned
  container: `verify.sh`; `run_prop410_arb.sh`; `run_tail_arb.sh`;
  `run_barrier_replay.sh`; `run_full_sweep.sh` optional (budget, §8).
  Output: transcripts + sha256 of every produced artifact; labeled
  "repository replay reproduction" — following their own sentence.
- **L2 — independent replication (our own implementation; no reuse of
  their source, parser, interval partition, or intermediate decimal
  tables).** Stack decision (frozen here): Python 3 + `mpmath`
  (interval `mpmath.iv`) + `fractions` for exact rational brackets — a
  different stack from their C/FLINT path (their authoritative
  cross-backend lane is C/FLINT/Arb; our primary lane must not be
  FLINT/Arb). Optional corroboration with python-flint is allowed only
  if labeled "same-family backend (Arb) — corroboration, not the
  independence claim". Priorities and acceptance metrics in §4.
- **L3 — clean-room theorem-source weld.** Transcriptions already
  completed (Polymath15 Thm 1.2/1.3 + Lemma 8.4, per-region digests in
  recon §7.11; pinned PDF byte-identical to the package's own reference
  hash); remaining items (Platt–Trudgian refereed statement; weld
  checklist) frozen in §5. Honest limitation, recorded in advance: one
  operator → transcriptions were produced and reviewed in
  time-separated passes; that is mitigation, not two independent
  auditors.
- **L4 — verdict.** Per-obligation table using their blueprint IDs;
  coverage list; reviewer-template layers (recon §7.12); aggregates as
  defined in §6. Registry P3 entries follow the L4 report.

## 3. L1 — replay & provenance (protocol)

1. Step 1 — engine availability, recorded as-is: check for docker /
   podman / other OCI engines on the audit machine; record the result in
   `reports/audit_p1_l1_launch.log`. **Current status (pre-registered
   before execution): as of 2026-10-17 the audit machine has NO container
   engine (docker/podman absent; WSL2 present but no distribution
   installed) and the OCI archive is not local.**
2. Step 2 — only if an engine exists: fetch the OCI archive, verify
   sha256 `87a4695e…` (full value recorded in the log), load it, and run
   the four bounded scripts read-only with `--network none`; optional
   full sweep only if §8 budget allows.
3. Every command, exit code, transcript hash: `reports/audit_p1_l1_*.log`.
   Nonzero exits and missing artifacts are recorded as-is.
4. **Stop rule (frozen):** if no engine exists at L1 attempt time, L1 is
   recorded as **NOT-RUN-ENVIRONMENT** in the L4 coverage list; L2/L3
   proceed regardless (they do not depend on L1). Enabling a container
   engine is an owner-gated system change, not part of this audit.
5. L1 can never yield "independently verified": at most "release
   replayed; numbers reproduced from the release's own tooling".

## 4. L2 — independent replication (protocol; scope frozen here)

Order of execution and acceptance metrics (all comparisons against the
sealed values pinned in recon §7.2/§7.9; every number machine-extracted
from our logs):

1. **Window freeze & sign map (cheap; first).** Re-derive exact rational
   brackets with `fractions`: Machin rational π bound < 10⁻¹⁰⁰; window
   margin 5.37e6 / 1.19e7; `1872719/10^7 < y0 < 23409/125000`; and
   `8231038/10^7 < √(1−2t0) ≤ 8231039/10^7` via exact squaring
   comparisons; affine sign-map algebra re-derived by us.
2. **Prop 4.10 error budget.** From the formula statements (20)–(23)
   +(vi) as transcribed by us (constants from the pinned docs; NOT
   their code): recompute `e_A+e_B`, `e_C,0`, `E_max` and the margin
   against the sealed target `5.57871094787e-7`.
3. **Tail lane.** Re-derive the partition from the formula statements
   and spot-check with our own enclosures: two-sided corridor
   `0.999719 < D < 0.999721`; `(1−D)/M_max > 0.0001735326089372`;
   tail error `< 0.000000011671604`; post-error margin
   `> 0.0001735209373337`; anchors `M = 153814`, `M_err = 3000`,
   `M_max < 1.608290`.
4. **Barrier subset (risk-first; budget-capped).** From the sealed
   certificate descriptors as INPUT (input reuse allowed; computation
   must be ours): select K = 8 prisms with the smallest sealed margins,
   plus their seam faces plus the first and last prisms; recheck
   winding-nonzero with our own enclosure method (NOT interior
   sampling); compare against sealed claims: total uniform error
   `< 0.000356523011600040 < 0.00125` (`e_A+e_B < 3.639278679550541e-10`,
   `e_C,0 < 0.000356522647672172`), gate
   `M_i > D_z,i/(2(num−1)) + D_t,i·Δt_i + 0.00125`, winding aggregate
   `[−8.95, 8.95]×10⁻¹³`, minimum sealed margin
   `0.519849894613872543374989997`. Budget cap: 4 h wall on the audit
   machine; if exceeded, the item is recorded UNRESOLVED-BUDGET with
   the covered subset listed.
5. **Verdict values per L2 item** (frozen): REPRODUCED (our independent
   chain certifies the sealed inequality at the sealed constants);
   PARTIAL (certifies a strictly weaker but still positive/valid bound;
   magnitude recorded); NOT-REPRODUCED (cannot certify; counterexample
   or violation); UNRESOLVED (infeasible within budget/environment;
   reason recorded). Weaker-but-sufficient never upgrades to
   REPRODUCED.
6. Out of L2 scope (coverage): full independent re-sweep of all 883
   prisms; full producer sweep re-implementation; mutation-kill testing
   of their verifier (their protocol item; noted as not performed);
   `prop43`/`prop62` lane re-implementation.

## 5. L3 — clean-room theorem-source weld (protocol)

Inputs: pinned Polymath15 v2 (sha `60d0d2d3…`, the package's own
reference hash), e-print v2 sources (digests in recon §7.11);
Platt–Trudgian arXiv:2004.09765v1 (sha `3362f66a…`) with the refereed
Bull. LMS statement as reference. Frozen checklist:

1. Hypothesis mapping: (i)/(ii)/(iii) of Polymath Thm 1.2 ↔ the package's
   claims (their P1/T1/B1–B2 slots); domain, endpoint, quantifier,
   substitution per slot.
2. Parameter compatibility: X/2 vs T_PT; margin `350479773/2`; window
   overlap `N = 3840000`.
3. Containment: barrier rectangle `[X, X+1] + i[1809/10000, 1]` ⊂ Thm
   1.2 conditions for `0 ≤ t ≤ t0`.
4. Citation chain versions: each cited result pinned to its refereed
   version where one exists.
5. Verdict per hypothesis: {compatible / mismatch / unresolved} with
   file+line references; then the weld verdict (all hypotheses
   compatible → weld holds; any mismatch → GAP-FOUND with the exact
   slot).

## 6. L4 — verdict (protocol)

- Table schema: obligation ID | L1 evidence | L2 evidence | L3 evidence |
  verdict ∈ {accepted / rejected / unresolved} | file/line references.
  "Accepted" for an obligation backed only by L1 = "accepted at replay
  level" (explicitly weaker); the L2/L3 columns carry the independence
  weight.
- Coverage list: every step NOT performed (starting with the §3/§4/§5
  out-of-scope items and the L1 stop-rule outcome), each with reason.
- Standard sentences (frozen): "A repository replay is not a
  mathematical review"; "their PASS is not peer acceptance"; "no verdict
  here asserts or denies RH or any universal statement".
- Aggregates: GAP-FOUND (with description) / INDEPENDENTLY-CERTIFIED
  (parts, with level) / UNVERIFIABLE-WITH-OUR-RESOURCES (parts, why).
- Report file: `reports/AUDIT_DBN_L4REPORT_<date>.md`, using the
  release's own reviewer-template structure (recon §7.12) with its
  required fields (commit SHA, OS, Python version, stored/container
  check status) filled from the actual logs. Registry P3 entry follows
  the report, verbatim, as a finite claim.

## 7. Gates, failure handling, anti-circularity

- No parameter (constants, tolerances, precision, selection rules) is
  changed in response to any interim or final result.
- Infrastructure failure handling: identical rerun only after the issue
  is fixed and logged; every attempt logged; numbers from a failed
  attempt are never used.
- Anti-circularity static gate over the release's `lean/` tree BEFORE
  L2 verdicts are stated: placeholder scan (`sorry` / `admit` /
  `unsafe`), axiom-statement inventory, and cross-check of any claimed
  `#print axioms` output against what the source actually declares.
  This is a textual gate over pinned files; it is NOT a Lean rebuild
  and never yields "kernel-verified" language about their layer. It
  directly addresses their own open question about circular software
  checks (their P8(3)-style question), at the level stated.
- All numbers in every audit artifact are machine-extracted from logs;
  none retyped by hand.

## 8. Environment and budget (measured anchors; not promises)

- Audit machine: this Windows host, 4 logical cores. Baseline measured
  as-needed during execution and recorded.
- Their machine anchors (pinned from their docs, recon §7.2): finite
  producer replay ≈ 16 m 45 s; comparator 1.89 s; barrier + tail lanes
  add hours; full sweep = 3,149,013 lines.
- Frozen budget caps: L2 item 4 = 4 h wall (else UNRESOLVED-BUDGET);
  total L2 ≤ 1 working day; L1 full sweep optional only within these
  caps. No cap extension after seeing results (a cap change would be a
  new dated decision, never a silent one).

## 9. Artifacts and non-modifications

- This file; audit code under `audit_p1/` (new directory); logs and
  JSON under `reports/audit_p1_*`; L4 report per §6; registry entries
  after it.
- Non-modifications: the release package is accessed read-only; none of
  this repository's sealed artifacts (series logs, C4 artifacts, engine
  B artifacts, dashboards, README machine block) are touched by this
  audit; the 501-point public record is closed and unaffected.

## 10. Ordering proof

- This file is committed and pushed BEFORE the first audit command.
  Audit logs carry wall-clock timestamps; the L1/L2/L3 logs must begin
  later than the add-commit time of this file.
- The target is the immutable release; later package activity (HEAD
  movement, new releases) does not change what was audited.

Declared by the analysis session on 2026-10-17, before execution.
