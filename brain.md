# MSAF Project Memory (brain.md)

Living work history for the Matrix-constraint Spectral Analysis Framework
project. Read this file first when opening a new session. Updated every time
the project state changes. Language of this file: Indonesian (project memory,
not code).

Last updated: 2026-10-13 — adversarial self-audit done (blind spots L31–L35,
one UNSOUND: L33 one-sided widening, fixed + verified). 67 tests green, both
ledgers V(L)=True, final seal=True, artifacts workspace-local.

---

## 1. Who / roles

- Researcher: Muhammad Aidil Amry (South Sulawesi, Indonesia,
  ORCID 0009-0002-9718-9710). Owner of `aidilamrym-ops/guinand-weil-rigorous-numerics`
  and `aidilamrym-ops/the-asymmetric-wager-msaf`.
- Agent (OpenCode): Chief Software Architect + LinAlg Expert + Mathematical
  Programmer. Translates MSAF formalism into rigid code, audits precision
  landmines, optimizes ball-arithmetic simulation.

## 2. Binding rules (from system_prompt_opencode.md)

1. All code, identifiers, docstrings, comments: ENGLISH only.
   Scan: `Select-String -Pattern '[^\x00-\x7F]'` over `msaf/*.py` must return empty.
2. Chat with researcher: formal, rigid, technical Indonesian.
3. Zero-fudging: `flint.arb` / `flint.acb` / `flint.arb_mat` enclosures only.
   No `float()` on any numeric path. Zero claims only via containment
   (`residual.contains(0)`), never `== 0`.
4. Precision discipline: `flint.ctx.prec` set ONCE at entry
   (`precision.set_precision`), never drifted. `mpmath`/`gmpy2` in
   `sys.modules` = contaminated process, abort.
5. Python 3.14+, modular, circulant/block structure for memory, no redundant comments.

## 3. Reference inputs (workspace root, all kept)

| File | Status |
|---|---|
| `Matrix-constraint Spectral Analysis Framework (MSAF).md` | Manuscript, 6 sections. Axioms source. |
| `Kompilasi Rumus, Turunan, dan Penjelasan Simbol.md` | Symbol reference. |
| `system_prompt_opencode.md` | Agent contract. |
| `instruksi_pertama_opencode.md` | Task 1: `msaf_core_lattice.py` (4 functions). DONE. |
| `instruksi_lanjutan_newton_arb.md` | Task 2: Newton-xi blueprint. DONE (with 7 API fixes + 2 substantive corrections). |
| `msaf_execution_manual.md` | 7-day Terminus plan (Day 1-2 / 3-4 / 5-7). Intake 2026-10-13. |
| `msaf_terminus_phase1.md` | Newton-xi class blueprint. Superseded by `msaf/zeta_inversion.py` (blueprint has API errors, see §7). |
| `msaf_terminus_phase2.md` | Visualizer blueprint. Implemented as `msaf/visualizer.py` with rigid projection (no float/numpy in computation). |
| `msaf_terminus_phase3.md` | Final-audit blueprint. Implemented as `msaf/final_audit.py` reusing `Ledger` + Arb capacity check. |

## 4. Kernel architecture (all English, all Arb, 0 non-ASCII)

- `msaf_core_lattice.py` — `initialize_precision`, `generate_shift_operator(n)`,
  `quantized_von_mangoldt(k)`, `verify_commutation(h,t)` + `verify_truncation`,
  `verify_unitarity`, `von_mangoldt_log_kernel`, `is_circulant`.
- `msaf/precision.py` — lock-once precision, mutator audit, `log2/exp2/log_base`.
- `msaf/constants.py` — `ELL_P`, `D_OBS`, `N_STEPS`, `DECAY_B/A`, `ZETA_SIGMA`
  (POSTULATE, not derived), `T_SPECTRAL`.
- `msaf/grid.py` — exact `fmpq` decimal parser, `floor(N_steps)`, bit length, storage bound.
- `msaf/certify.py` — `contains_zero` (Arb), `contains_zero_complex` (Acb),
  matrix certificates, reports.
- `msaf/operators.py` — `CyclicShift` (permutation, O(n)), `CirculantHamiltonian`
  (symbol c), materialisation cap 4096, structural `[H,T]=0` theorem.
- `msaf/guinand.py` — Weil matrix + DFT spectrum (`multiple=True` not needed;
  structural DFT used), Shannon entropy.
- `msaf/budget.py` — dual-path `n_crit`: manuscript `H:=n` vs measured
  `H:=0.5+0.5·log2(2(n-1))`.
- `msaf/zeta_inversion.py` — rigorous interval Newton on xi via `acb_series`
  Taylor + analytic tail bound; `ball()` helper; `locate_zero`,
  `certify_sigma_one_half` (always `global_claim_supported=False`),
  `certify_zero_exclusion`.
- `msaf/evolution.py` — symbol-mutation campaign + `RootPullGenome` campaign
  (certified zeros, REVERT state), SHA-256 hash-chained `Ledger`, `replay()`.
  CLI: `python -m msaf.evolution --replay LEDGER`.
- `msaf/visualizer.py` — rigid pixel projection
  `k = floor(gamma/(2π)·log2(N_steps)) mod N_steps` in pure Arb/integer;
  JSON report + optional PNG (integers only cross the render boundary).
- `msaf/final_audit.py` — chain verify + replay + Arb holographic capacity
  check. No float, no numpy.
- `msaf/audit.py` — CLI report, 10 sections. Ledger/reports default under
  workspace (`ledger/`, `reports/`).
- `msaf/AUDIT.md` — landmine register L1–L25 (Part I kernel, Part II Newton
  directive). `msaf/tests/test_msaf.py` — regression suite.

## 5. Measured results (do not re-derive, cite them)

- `N_steps = 5.44468544329815837306650e+61`, never integer; `log2 = 206` bit;
  storage lower bound `6.8e60` byte. `N×N` materialisation structurally impossible.
- `[H,T]` n=16 @256bit: PASS-BY-ENCLOSURE, half-width ~2.4e-77.
  `T^dag·T−I`, `T^n−I`: exact zero (rational 0/1 entries).
- `[H,T]=0` is an algebraic TAUTOLOGY for every circulant H → verdict TRIVIAL,
  `carries_information=False`. Constrain nothing about zeta zeros (L11).
- Weil spectrum: `λ_0 = n−1`, `λ_k = −1`; `min|λ| = 1` exactly. NO exponential
  decay → `B≈0.115` has no measured source in-framework (L8).
- `n_crit(H:=n) = 1.8e31 ± 3.2e29` (manuscript arithmetic reproduces exactly;
  premise `H≡n` is the problem) vs `n_crit(measured) = 3.16e60` (29 orders gap).
- `|λ|=1e-59` at `n=1181.33`; relative demand at n=800 is 142 bit. Precision
  demand, not absolute underflow (L9).
- `σ=0.5` is IMPOSED, not derived (L12). Circulant+Hermitian ⇒ real eigenvalues
  ⇒ only conjugate pairing. `ZETA_SIGMA` documented as postulate.
- `E_trunc≡0` measurably false: `ℓ_P·e^(−N)` has positive lower endpoint,
  rel. radius 3.09e-7 in Arb; float64 gives 0.0 on identical input (L13).
- Newton-xi: ρ₁/ρ₂/ρ₃ ZERO-LOCALIZED, `Re = 0.5 ± (7.5e-71 / 8.7e-78 / 4.7e-71)`,
  γ agrees with `acb.zeta_zero` < 1e-24. Exclusion at t=30.5: True.
  `global_claim_supported = False` on ALL paths. `acb.zeta_zero` presupposes the
  critical line → valid for γ cross-check only, never σ evidence (L23).
- Root-pull: SEED(zero#1) + PROMOTEs, chain intact, replay=True.
- Evolution: promotions with monotone incumbent, chain intact, replay=True.

## 6. Landmine index (full text in msaf/AUDIT.md)

L1 `arb(x,y)`=radius · L2 containment direction · L3 commutator never exact-zero ·
L4 `log/exp` take no args · L5 `flint.arb` not importable submodule ·
L6 `N_steps` non-integer · L7 `log(Λ_d+δ)` NaN → `log(1+Λ_d)` repair ·
L8 no Weil decay · L9 underflow=precision demand · L10 repeated-eigenvalue `eig`
failure · L11 `[H,T]` tautology gate · L12 σ imposed · L13 `E_trunc` false ·
L14 overlapping-ball `>=` stall → `_is_provably_worse` · L15 `log2(0)`→fitness cap +
refuse non-finite · L16 `arb` vs `acb` 2nd-arg semantics · L17 `complex_rad`→Acb ·
L18 `s.real` is value not radius · L19 rectangular-Acb containment → circular
criterion · L20 `arb<arb` overlap · L21 `return 0` at s=0/1 fabricates roots ·
L22 `VERIFIED_BY_CONFORMANCE` verifies nothing → separation metric ·
L23 `zeta_zero` presupposes line · L24 float literals bake binary64 error →
decimal strings · L25 converge at precision floor.

## 7. Blueprint deviations (directive → implementation, all measured)

Newton phase (`instruksi_lanjutan_newton_arb.md` / `msaf_terminus_phase1.md`):
`acb(2,prec)`→point not ball · `pi.pow` nonexistent → `exp(logπ·(−s/2))` ·
`acb.pi(prec)`→`acb.pi()` · `ldexp` nonexistent · `real()` method→property ·
finite-difference derivative NOT rigorous → `acb_series` Taylor + tail bound ·
`s=0/1→0` fabricates roots → regular evaluation (ξ=1/2) · conformance criterion
replaced by certified offset · series refuses `Re≥1` · floor-convergence rule.
Phase 2: `float()/np.log2/np.floor/sys.maxsize` in computation → pure Arb +
`fmpz` modular projection; matplotlib renders integer coordinates only.
Phase 3: `float` entropy + `"0"*64` genesis + recomputed-hash chain → reuse
`Ledger`/`replay` + Arb capacity `H(n)·b(n) ≤ N_steps`; genesis stays `GENESIS`
(existing ledgers must keep verifying).

## 8. Workspace policy (binding since 2026-10-13)

- Project lives ONLY in `D:\Opencode AI Agent`: code (`msaf/`,
  `msaf_core_lattice.py`), specs (`*.md`), memory (`brain.md`), artifacts
  (`ledger/`, `reports/`). Nothing in Temp except pytest tmpdirs.
- Deleted 2026-10-13 (confirmed, zero MSAF refs, 4966 files + 33 MB):
  `BootLoops-ai/`, `Dream-RSI-main/`, `hexagon_mhv_symbol_weight_18/`,
  `rea-work/`, `z3_judge.wasm`, `.pytest_cache/`, all `__pycache__/`.
- Ledger default: `ledger/msaf_ledger.jsonl`; root-pull: `ledger/rootpull.jsonl`.
  Radii serialised as decimal STRINGS (never JSON numbers → float64 → fake 0.0).
- Resume commands:
  `python -m pytest msaf -q`
  `python -m msaf.audit --prec 256 --evolve 6 --root-pull 3`
  `python -m msaf.evolution --replay ledger/msaf_ledger.jsonl`
  ASCII scan: `Select-String -Pattern '[^\x00-\x7F]' msaf/*.py` → must be empty.

## 9. Terminus status

Day 1–2 inversion + ledger lock: DONE (`zeta_inversion.py`, root-pull + REVERT).
Day 3–4 pixel projection + visualizer: DONE (`visualizer.py`, rigid + PNG;
pixels 461…/686…/816… for ρ₁/ρ₂/ρ₃).
Day 5–7 replay + stress + seal: DONE (`final_audit.py`, `--replay` CLI,
holographic check vs `n_crit≈3.16e60` measured path; seal=True).
Landmines L26–L30 recorded (Phase 2/3 blueprint float chain + mid-file guard).
Suite: 71 tests green. Artifacts: `ledger/msaf_ledger.jsonl`,
`ledger/rootpull.jsonl`, `reports/spectral_density.{json,png}`.
Blind-spot repairs are value-preserving: same verdicts, same seal, tighter tails;
root-pull ledger replays byte-identical under the renamed budget parameter.
Post-Terminus: repo initialised + sealed commit `2298140`, fresh-clone
reproduction green (67 tests then, both ledgers V(L)=True). Dirichlet campaign
live: `msaf/dirichlet.py`, chi_4_3 bracket (6.0, 6.1), audit section 13.
GRH class-gated rewrite: `DirichletCharacter` + `RigorousLFunction`
(straddle raises `StraddlingEnclosure`), 12-test purity suite, register L38.
GRH dossier: `reports/GRH_BRACKET_REPORT.json` (chi_4, 3 resolution levels to
1e-4, measured signs, string-only), 85 tests green.
v1.1.0 SEALED locally 2026-10-13: `.zenodo.json` (Title/Creators/ORCID/keywords/MIT),
`harness/release_tag.sh` (5 hard gates, local-only, never pushes), 85 green,
audit `--prec 256 --newton_max_iter 16 --final-audit` exit 0 with V(L)=True on
both ledgers. Tag object `v1.1.0` annotated. No remote contacted for release.
PUBLIC PUSH 2026-10-13: repo `aidilamrym-ops/T-hat-N` (public) created, branch
`main` pushed (commits `e446d1f`, `64abe12` rewritten with noreply author
email; placeholder email eliminated). Token file `T-hat-N.txt` consumed then
permanently deleted; remote URL carries no credential; no `ghp_` string
anywhere in tracked files. ACTION REQUIRED BY RESEARCHER: revoke the consumed
token at github.com/settings/tokens (it cannot be revoked via API here).
README rewritten 2026-10-13: 4-section auditor architecture (epistemology +
flow diagram, spectrum mechanics + 14-row 256-bit table, reproducibility
manual, L31-L35 amendments), LaTeX throughout, ASCII-strict, all numbers
measured. Second push 2026-10-13 (`443a004`, `fe45ae1`) via transient token
in memory only; remote verified credential-free afterwards.
README refresh 2026-10-13 (commit `a1c48ac`, local): full re-audit showed
zero numeric drift, table extended to 16 rows (ledger seal rows), ASCII
re-verified at 0 non-ASCII. Pending push (needs researcher auth).
Next (only if researcher orders): replace postulated γ_m DFT definition with
Newton-derived spectrum module (`zetazeros.py`); multi-precision stress sweep
(128/256/512/1024 bit) as campaign matrix.
