# Replay Certificate Spec v0.2 â€” Campaign V2 "quantum entropy kernel" (SIMULATED)

Status: FROZEN 2026-10-19 in this repository. This file, the frozen
`msaf/quantum_entropy/` package, `audit_quantum/freeze.py` and
`audit_quantum/PINS.sha256` are committed together BEFORE the first campaign
command; git history is the ordering proof (same discipline as RR-2026-01).

Series note: v0.1 of this series is `reports/REPLAY_RECORD_SPEC.md` ("Replay
Record", records `RR-<year>-<seq>`); this document keeps the owner's GO-1 file
label. Planned campaign record: **RR-2026-02**; planned registry entry
**A-2026-0005** (post-execution, owner-gated). Nothing in this document
executes anything. In every artifact of the campaign the entropy source is
labelled **SIMULATED** (D1).

## 1. Scope and non-goals

In scope: a four-coordinate run of two independent interval engines (Engine A:
Arb, 6000 bits; Engine B: mpmath, dps 50) plus a float64 statistical layer fed
by a SIMULATED operating-system entropy stream, at dims 201/301/401, producing
a hash-chained append-only ledger, one standalone HTML diagnostic, and a frozen
digest over the code that produced them.

Non-goals (explicit): this is not a physical quantum-entropy measurement. The
model matrix is a finite tridiagonal instance frozen in section 2 and is
explicitly NOT a claim about the Riemann zeta zeros or any arithmetic Weil
form. The statistical layer is a diagnostic only and never feeds the certified
layer. No RH / Pâ‰ NP / physical claims appear anywhere in the artifact set
(K-Q7: `global_claim_supported` is hardcoded `False`).

## 2. The certified object

Model instance (exact rationals; `runner._build_matrices`):

* dimension D âˆˆ {201, 301, 401} per row;
* diagonal a_i = 2 + (i+1)Â²Â·hâ´, i = 0..Dâˆ’1, h = 1/(D+1); off-diagonal âˆ’1
  (symmetric tridiagonal, bÂ² = 1 exact);
* eigenvalue location: Gershgorin gives spectrum âŠ‚ (0, 4.1); bisection runs on
  the exact-rational interval [0, 41/10].

Coordinates K(D) = {D//4, D//2, 3D//4, D} sorted (D=401: {100, 200, 300, 401}).

Certified per coordinate:

1. an exact-rational bracket [lo, hi] âˆ‹ Î»_k with hi âˆ’ lo â‰¤ (41/10)/2Â¹âµâ°
   (exact-rational bisection, 150 steps; invariants cnt(lo) < k, cnt(hi) â‰¥ k);
2. an endpoint count certificate (section 3.3);
3. a Newton contraction diagnostic in both engines (section 3.4);
4. registered envelope relative width â‰¤ 0.02 (resolution floor, section 3.5).

## 3. Numeric engines and protocols

### 3.1 Dual engines (L41)

Engine A: python-flint `arb` at 6000 bits, locked first (`lock_engine_a`); a
drift guard asserts the precision cannot change afterwards. Engine B: `mpmath`
mpf at dps 50 (â‰ˆ169 bits) with directed-rounding helpers; `_b_env()` resets dps
inside every B call, so B never silently rides another context. All
rational â†’ ball conversions go through exact-decimal parsing
(`intervals.parse_decimal`); no float path exists in the certified layer (L39).

### 3.2 Decision protocol (interval Sturm count)

Decision variable: the interval Sturm count

    cnt(Î») = # strictly positive LDL pivots of Î»Â·I âˆ’ A = #{model eigenvalues < Î»}

(Sylvester inertia; exact for a rational point). At each of the 150 bisection
midpoints, Engine A returns `pivot_count_a(mid)` and Engine B
`pivot_count_b(mid)`. Both must be definite (no pivot ball touching zero) and
EQUAL; that is a dual agreement. Disagreements (must be 0 in a passing run)
are counted; ambiguity in either engine is resolved by the exact-rational
`pivot_sign_counts` fallback, whose rate over a coordinate must stay â‰¤ 5%
(`FALLBACK_MAX_RATIO`), else the dim is UNDETERMINED. An exact hit
(lt < k â‰¤ le) sets lo = hi = mid (point bracket).

Design rationale (pre-freeze revision, on the record): a determinant-sign
parity rule converges to the nearest root of the truncated leading block (the
parity flips at Î»â‚ for even-size blocks, probe 7); the Sturm count pins the
index k directly at the same per-step cost. Count semantics: #positive pivots
of Î»Â·I âˆ’ A; below the whole spectrum the count is 0, above it is D.

### 3.3 Endpoint certificate

With Îµ = 1/250 (section 3.5), set e_lo = lo âˆ’ Îµ and e_hi = hi + Îµ. The
certificate `ok` holds iff each engine returns definite counts with

    cnt(e_lo) â‰¤ k âˆ’ 1   AND   cnt(e_hi) â‰¥ k.

Equality of the two counts is NOT required: model gaps can be smaller than 2Îµ,
so the envelope may legitimately contain other eigenvalues; the two
inequalities together still pin k, certifying Î»_k âˆˆ [e_lo, e_hi]. A det-sign
flip across the envelope is not a valid criterion (parity-even envelopes exist,
e.g. the D=401 top edge) and is not used.

### 3.4 Newton contraction diagnostic

From the certified bracket midpoint, both engines run an interval Newton with
NEWTON_ITERS = 60, NEWTON_TARGET = 1e-25, and ball half-width
NEWTON_START_HALF = 5e-10. The half-width is frozen from the pre-freeze
rehearsal with three constraints: (i) far clear of every leading-minor
eigenvalue (interlace distances â‰¥ ~3e-7 at D=401), so no intermediate LDL
pivot can straddle inside the ball; (ii) small enough that the derivative
enclosure keeps a definite sign at every campaign coordinate â€” the enclosure
width scales ~linearly with the ball width and the chaotic pivot-orbit
amplification at the worst coordinate (D=401, k=300) was measured ~1e10,
leaving â‰¥100Ã— margin; (iii) wide enough for visible quadratic contraction from
1e-9 width to below 1e-25 in a few iterations. The derivative uses the LDL
pivot-product form in both engines,

    f' = (Î _{i<n} v_i) Â· (v_n' + v_n Â· Î£_{i<n} v_i'/v_i),

never dividing by the last pivot (the root-containing ball makes v_n straddle
zero). The side-by-side naive derivative recurrence was rejected at freeze
time: its interval width grows like the recurrence's growing solution râ‚Šâ¿
(râ‚Š â‰ˆ 1.94 away from the oscillatory band; probe 13 measured straddles up to
Â±2.3e+148). Statuses: CONTRACTED / DERIVATIVE_AMBIGUOUS / CAP_REACHED /
BROKEN_IMAGE / VALUE_AMBIGUOUS. Any non-CONTRACTED status is NOT_RESOLVED,
except DERIVATIVE_AMBIGUOUS which is UNDETERMINED.

### 3.5 Envelope, perturbation reading, resolution floor (L39)

Îµ = 1/250 = 0.004 exact (= NOISE_BASE 0.0005 Ã— ENVELOPE_FACTOR 4). Interval
policy: symmetric Minkowski widening only; widths are never shrunk by
asymmetric rounding (landmine L39). Weyl reading: a per-channel diagonal
perturbation E = diag(v_iÂ·w_iÂ·x_i) with v_i = (i+1)/D, w_i = 0.0005Â·(1+(i+1)/D)
â‰¤ 0.001 and |x_i| â‰¤ 4 (ENVELOPE_FACTOR) has max diagonal entry â‰¤ 0.004 = Îµ and
spectral norm â€–Eâ€–â‚‚ â‰¤ Îµ; Weyl's inequality then keeps Î»_k(A0+E) inside the
certified envelope [Î»_k âˆ’ Îµ, Î»_k + Îµ]. Samples with max_i |x_i| > 4 are
counted as `envelope_exceeded` (diagnostic only). Resolution floor: the
registered envelope relative width rel = (e_hi âˆ’ e_lo)/mid_k must be â‰¤ 0.02
(`WIDTH_FLOOR_REL`), else NOT_RESOLVED; planned coordinates meet it with
margin (worst â‰ˆ 0.0139).

Structural note (K-Q2 interpretation): the Îµ-box [loâˆ’Îµ, hi+Îµ] contains
non-positive-definite members already at D â‰³ 80 (Î»_min(A0) â‰ˆ (Ï€/(D+1))Â² < Îµ).
The K-Q2 Sylvester protocol therefore certifies positive-definiteness of the
MODEL block itself (interval LDL of A0 over the exact rational data, both
engines), not of every Îµ-perturbed member; the perturbation statement is the
Weyl envelope above.

### 3.6 K-Q2 Sylvester protocol

`sylvester_a` / `sylvester_b` run interval LDL^T of the model block in each
engine; statuses: CERTIFIED_PD (every pivot ball excludes zero and is strictly
positive in that engine's arithmetic â€” the ALL_EXCLUDE_ZERO principle),
FENCE_ZERO (some pivot ball touches zero â†’ loud fence â†’ UNDETERMINED, campaign
exit code 2), NEGATIVE_PIVOT (some pivot ball strictly negative â†’ NOT_RESOLVED,
exit 1). A0 is positive definite by construction (diagonal â‰¥ 2 + hâ´ > 2,
|off-diagonal| = 1); the protocol certifies it by machine instead.

## 4. SIMULATED entropy stream and statistical layer

### 4.1 Entropy source (K-Q1, D2)

`EntropySource` draws from `secrets.token_bytes` â€” the operating-system CSPRNG
â€” in 512-byte (4096-bit) blocks. Raw blocks are never retained
(non-invertibility accepted by design): per batch only the sha256 digest of the
consumed byte stream and its byte count are recorded in the ledger (BLOCK
records). There is no `--seed` argument anywhere in the package; any `--seed`
occurrence on a command line is refused loudly with exit code 2 (K-Q1), both
`--seed N` and `--seed=N` forms.

### 4.2 Sampling (float64 by design, D3)

Per dim D: channel weights v_i = (i+1)/D and w_i = 0.0005Â·(1+(i+1)/D);
Ïƒ0 = sqrt(Î£ (v_iÂ·w_i)Â²) computed in float64. Per sample: D iid standard
normals x (Boxâ€“Muller over 53-bit uniforms taken from 8-byte big-endian
chunks; u1 = 0 replaced by 2â»âµÂ³ to keep log finite), s = Î£ v_iÂ·w_iÂ·x_i, and
z = s/Ïƒ0. Under iid standard-normal x, z has variance 1 by construction of Ïƒ0;
z is otherwise unbounded. The sampling layer is float64 by design and never
feeds the certified layer.

### 4.3 Frozen statistics (K-Q4)

S = 20000 samples/dim in batches of 500. Bins: 16, delimited by the 15 frozen
knots q_k = Î¦â»Â¹(k/16) (literals in `chispec.KNOTS`; qâ‚ˆ = 0 exact, symmetric).
Expected counts E_b = S/16 exact rational (1250 each at S = 20000). Floor
rule: cells with expected count < 5 are dropped and recorded (none at full S).
Ï‡Â² is computed as an exact rational over kept cells and accepted iff
0 â‰¤ Ï‡Â² â‰¤ 60 (`CHI2_MAX`). Exceedance diagnostic: count of z â‰¥ 3.5, compared
against the frozen literal P_STAR only as a diagnostic (no p-value decision).
The per-dim z list is written to `audit_quantum/exec_<date>/stats_d{D}.bin`
(float64, native) with its sha256 recorded in the ledger (STATS record).
Wall cap: 30 minutes total (`WALL_CAP_MIN`); hitting it records
`budget_exceeded` and reduces nothing else (samples actually taken are what
the ledger says).

## 5. Ledger format (K-Q6)

Format `msaf-hashchain-1` (append-only JSONL): one canonical JSON object per
LF-terminated line; canonical JSON sorts keys, uses compact separators and
keeps non-ASCII characters. Chaining:

    record_hash = sha256(previous_hash + "\n" + canonical_json(record \ record_hash))

with `previous_hash` = "GENESIS" for the first record. Allowed record types:
GENESIS, BLOCK, STATS, VERDICT, REVERT. The record type REJECT is refused by
construction: a failed reproduction is recorded as REVERT, never as a fitness
REJECT. Verification: `python -m msaf.quantum_entropy.ledger --verify PATH`
(exits non-zero on the first broken link, hash mismatch or schema violation).

## 6. Standalone dashboard

`reports/gw_quantum_diagnostic_v1.html` is a single self-contained file: raw
inline SVG, inline CSS, no external references. `assert_self_contained`
rejects the page if any of `<script`, `http://`, `https://`, `@import`,
`<link`, `javascript:`, `src=` occurs, and requires the SIMULATED label. The
inline SVG carries no xmlns attribute precisely so the `http://` forbiddance
stays absolute (inline HTML SVG renders without it).

## 7. Verdicts, gates, exit codes

Per dim and for the campaign: RESOLVED / NOT_RESOLVED / UNDETERMINED.
Campaign precedence: UNDETERMINED (exit 2) > NOT_RESOLVED (exit 1) >
RESOLVED (exit 0). Gates: ledger chain must verify before and after the run;
K-Q2 fence â†’ UNDETERMINED; K-Q1 `--seed` â†’ exit 2 before anything runs; the
CI guard `msaf/tests/test_quantum_entropy.py` runs the frozen selftest (14
checks, ZERO FAILURE required). Runner CLI (paths caller-anchored, L42):

    python -m msaf.quantum_entropy.runner [--dims 201,301,401] [--samples 20000]
        [--batch 500] [--outdir DIR] [--ledger PATH] [--html PATH]
        [--time-cap-min 30] [--quiet]

## 8. Artifact set and the Codebase/Manifest Digest

`audit_quantum/PINS.sha256` pins the raw sha256 of the 14 frozen files (the
package modules, the CI test, `audit_quantum/freeze.py`, this spec and the
preregistration), one `sha  path` line each, path-sorted. The **Codebase/
Manifest Digest** is defined as sha256 over the raw bytes of PINS.sha256
itself; `audit_quantum/freeze.py --build` prints it and
`FREEZE_MANIFEST_V2.json` records it together with the per-file table and the
ledger snapshot at freeze time (path, raw sha256, record count, chain head).
The ledger is intentionally NOT a pinned file: it is append-only and grows
during the GO-2 campaign run; only its freeze-time snapshot is recorded.
`freeze.py --verify` recomputes every pin and the digest binding and exits 2
on any mismatch.

## 9. Landmines and decisions

* **L39** interval discipline: exact-decimal rational parsing; symmetric
  widening only; certified-layer widths never shrunk; Îµ from NOISE_BASE Ã— 4.
* **L40** "1 pixel â‰¡ 1 t_P" is an abstract gloss only, recorded in the
  preregistration as prose; it is never a functional variable anywhere in the
  runtime.
* **L41** engine discipline: Engine A locked first; `_b_env()` resets dps in
  every B call; drift guard on A's precision.
* **L42** no CWD anchoring: all paths are caller-provided or ROOT-anchored
  (ROOT = repository root resolved from the module file); the ledger CLI takes
  an explicit path.
* **D1** SIMULATED label is locked in every code line, ledger record, report
  and the HTML dashboard; no physical-quantum claim is made.
* **D2** entropy source: operating-system CSPRNG surrogate, 4096-bit blocks,
  no seeds, no raw-block retention, per-batch digests only.
* **D3** statistical layer float64 (documented); certified layer
  exact-rational/ball; the layers never mix.
* **D4** "1 pixel â‰¡ 1 t_P" abstract gloss only (see L40).
* **D5** additive scope: sealed V1 paths stay byte-identical; V2 adds a new
  package, a new ledger and new reports only.
* **D6** two-GO workflow: the freeze commit (GO-1) is pushed with green CI
  BEFORE any campaign command runs (GO-2); no campaign execution pre-freeze.
* **D7** repo-style CI guard kept separate: the campaign runner is standalone;
  `msaf/tests/test_quantum_entropy.py` runs the frozen selftest inside the
  repository CI together with the other guards.

## 10. Reproduction

    python -m msaf.quantum_entropy.selftest                    # 14 checks, ZERO FAILURE
    python audit_quantum/freeze.py --verify                    # pins + digest binding
    python -m msaf.quantum_entropy.ledger --verify ledger/quantum_evolution.jsonl
    python -m msaf.quantum_entropy.runner                     # GO-2 campaign run

The digest of a reproduced checkout equals the digest above iff every pinned
file matches byte-for-byte; platform line endings are pinned to LF via
`.gitattributes` for every pinned path.

## 11. Non-claims

No physical-quantum-entropy claim; no Riemann-zeta statement; no claim about
the arithmetic Weil form; no complexity-theoretic statement; the model matrix
is a finite model instance with a stated precision discipline; the statistical
layer is a diagnostic built on a SIMULATED entropy surrogate. The only claims
are the machine-checked statements in sections 2â€“3 and the artifact hashes in
section 8.


