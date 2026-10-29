# ChronoGeometric Framework — Target Problem Analysis

## Executive Summary

The **ChronoGeometric_Framework** is a Lean 4 library that implements a "Chrono-Geometric" triad (Arithmetic + Geometry + Time) designed to **encode verified interval-arithmetic results from T-hat-N** (`msaf.zeta_inversion`, `msaf.gw_*`) into Lean theorems. Currently it builds and tests green, but the **encoding correctness theorems are trivial** because they use hardcoded `⟨true, true, true⟩` placeholders instead of real verified data.

---

## Current State (as of 2026-10-30)

| Module | Status | Gap |
|--------|--------|-----|
| `NewArithmetic.lean` | ✅ Complete | — |
| `ChronoNat.lean` | ✅ Complete | — |
| `ChronoReduction.lean` | ✅ Complete | — |
| `ChronoBridge.lean` | ⚠️ Placeholder | `verified_zeta_condition_from_enclosure` hardcoded |
| `ChronoSAT.lean` | ⚠️ Structure only | `Sat` predicate defined but no connection to collapse |
| `ChronoRiemann.lean` | ⚠️ Placeholder | `verified_condition_from_enclosure` hardcoded |
| `GeometryEncoding.lean` | 🚧 Stub | Identity mapping only |
| `Test.lean` | ✅ All `rfl` | Tests only the toy structure |
| `moore_premises.py` | ✅ Working | Verifies 3 Banach gates on complex balls |
| `export_enclosures.py` | ✅ Working | Exports Moore premises + derivatives to JSON |
| `lean/enclosures/*.json` | ✅ Real data | Moore premises = `PREMISES-HOLD` at ρ₁ |

**Key fact**: The Python verifier (`moore_premises.py`) **already produces `PREMISES-HOLD`** for the first Riemann zero box using T-hat-N's `msaf.zeta_inversion`. The JSON files in `lean/enclosures/` contain actual verified Arb enclosures.

---

## Target Problems (ordered by dependency)

### 1. JSON → Lean Data Import
**Files**: New Lean module `EnclosureData.lean`, update `lakefile.toml`
- Parse `moore_premises.json`, `derivative_enclosures.json`, `gw_bounds.json` into Lean structures
- Use Lake data-file support or `IO.FS.read` at build time
- Replace `verified_condition_from_enclosure : MyNat → VerifiedDerivativeCondition` with actual JSON lookup by index
- Replace `verified_zeta_condition_from_enclosure : MyNat → VerifiedZetaBoundCondition` similarly

### 2. Real `ZetaStep` / `sign_budget_shape` from Enclosure Data
**Files**: `ChronoBridge.lean`, `ChronoRiemann.lean`
- Current: `ZetaStep n` = `Shape.space` of `n` points (toy)
- Target: `ZetaStep n` encodes the **three GW gates** (derivative bound, character sum, orthogonality) for index `n`
- Current: `sign_budget_shape n` = `Shape.space` of `n` points (toy)
- Target: `sign_budget_shape n` encodes the **three Moore gates** (deriv≠0, Lipschitz<1, invariance) for the n-th isolation box

### 3. Prove Encoding Correctness Theorems (non-trivial)
**Files**: `ChronoBridge.lean`, `ChronoRiemann.lean`
- `zeta_step_encoding_correct`: Currently trivial (`simp [hshape]`) because both sides are `true`
- `riemann_encoding_correct`: Currently trivial for same reason
- After (1) and (2), these become **real theorems** requiring proof that the geometric collapse ↔ the three verified gates

### 4. SAT Encoding Correctness
**Files**: `ChronoSAT.lean`
- Define `SATEncodingCorrect : Formula → Prop` linking satisfiability to collapse behaviour
- Current `sat_instant_reduction` only checks shape collapse, not logical equivalence
- Target: `Sat f ↔ (collapse_to_harmony (simulate_sat f)).shape = Shape.point` (or similar)

### 5. GW Bounds Integration
**Files**: `export_enclosures.py`, `ChronoBridge.lean`
- `export_gw_bounds` currently returns placeholders
- Implement actual `msaf.gw_*` import and export real GW character-arithmetic bounds
- Connect to `VerifiedZetaBoundCondition` structure

### 6. Continuous Integration
**Files**: `.github/workflows/verify.yml` (new), update `Makefile`
- CI must run `lake build` + anti-circularity gate on every push
- Python tests for `moore_premises` when `msaf` available
- Ensure `lean/enclosures/*.json` are regenerated from latest T-hat-N verified runs

### 7. Anti-Circularity Gate Integration
**Files**: `msaf/tests/test_anti_circularity_gate.py` (extend) or new gate
- Current framework `Makefile` calls external gate script
- Should be integrated into T-hat-N's existing `test_anti_circularity_gate.py` scope
- Add `ChronoGeometric_Framework/lean/*.lean` to SCAFFOLD or new category

### 8. Registry Entries (FENCE_REGISTRY)
**Files**: `reports/FENCE_REGISTRY.md`
- Each certified encoding correctness theorem → `T-2026-XXXX` entry
- Moore premises verification → `A-2026-XXXX` audit entry
- GW bounds verification → `A-2026-XXXX` audit entry

---

## Dependency Graph

```
1. JSON Import (EnclosureData.lean)
    │
    ├─→ 2. Real ZetaStep / sign_budget_shape
    │       │
    │       └─→ 3. Encoding Correctness Proofs (zeta_step_encoding_correct, riemann_encoding_correct)
    │
    └─→ 5. GW Bounds Integration
            │
            └─→ 3. (for ZetaStep side)

4. SAT Encoding Correctness (independent, can run parallel)

6. CI / 7. Gate / 8. Registry (process, after 3+4+5 green)
```

---

## Scope Boundaries (per AGENTS.md / CURRENT_AUTHORITY.md)

- **IN SCOPE**: Formalising the *encoding* of already-verified T-hat-N computational results (interval arithmetic, GW character arithmetic) into Lean.
- **OUT OF SCOPE**: Proving RH, zeta zero locations, Weil positivity, full matrix positivity. Those remain in T-hat-N proper (P1/P2/r6).
- The framework **does not** replace `arb_mat.eig` or `msaf.zeta_inversion`; it *consumes* their verified output.

---

## Recommended First Commit (Pre-registration)

Create `reports/PREREG_CHRONO_ENCODING_2026-10-30.md` with:
1. JSON import specification
2. Real `ZetaStep` / `sign_budget_shape` definition sketch
3. Encoding correctness theorem statements (non-trivial versions)
4. Registry IDs to be claimed: `T-2026-0061` (Riemann encoding), `T-2026-0062` (Zeta/GW encoding), `T-2026-0063` (SAT encoding)
5. Verification commands: `lake build`, `python -m pytest python/test_moore.py`, anti-circularity gate

Then implement in separate commits per target above.