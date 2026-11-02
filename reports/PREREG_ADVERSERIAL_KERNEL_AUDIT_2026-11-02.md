# Pre-Registration: Adversarial Kernel & Anti-Circularity Audit (2026-11-02)

## Scope
1. Axiom Trusted Base Audit (`lean/spec/`, `lean/spec_v2/`, Mathlib axioms).
2. Anti-Circularity Gate Inspection (`msaf/tests/test_anti_circularity_gate.py`).
3. Boundary Escape & Widening Vulnerabilities (interval arithmetic serialization & precision overrides).
4. Soundness / Contradiction Triggers (vacuous preconditions, Z3 SMT boundary collisions).

## Baseline
- Lean 4.33.1 + Mathlib
- Z3 SMT solver via `mcp_oracle_toe_z3_tribunal`
- Verified via `test_lean_axiom_audit.py` and `test_anti_circularity_gate.py`
