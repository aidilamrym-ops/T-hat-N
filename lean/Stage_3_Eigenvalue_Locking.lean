import Stage_2_Tail_Bound
import Mathlib.Tactic
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.MeasureTheory.Measure.Lebesgue.Basic

open Matrix MeasureTheory Real

/-!
# Stage 3 — certified Guinand–Weil run records

This file replaces the synthetic `N = 100`, `λ_min = 0.1` example with data
from the c=13 magnitude ladder:

* `c = 13`, `N = 160`, dimension `321`, recorded decimal
  `λ_min_lo = 3.123458832662237e-59`;
* `c = 13`, `N = 128`, dimension `257`, recorded decimal
  `λ_min_lo = 3.2990200597971055e-59`.

`λ_min` is the **recorded decimal image** of the lower endpoint printed by
`arb_mat.eig` in
`msaf/lambda_min_eig_ladder.py`.  The structure below is a data record: it
does not assert that Lean has diagonalised the matrix, and it does not assert
the Riemann Hypothesis.  The external Arb certificate is the pair
`all_exclude_zero = true` and the conservative lower bound in the JSON files
`reports/lambda_min_eig_ladder_dim321.json` and
`reports/lambda_min_eig_ladder_big.json`.

The `bound_from_tail` field records the machine-checked comparison with the
**archimedean truncation remainder** from Stage 2.  That remainder is
exponential in the truncation index, not a polynomial decay law in the
conductor; see the Stage 2 docstring for the scope limit.
-/

/-- A finite record for one certified Guinand–Weil run.

`c` is the conductor, `N` the block half-width, and `dim = 2N + 1`.
`lam_min` is the recorded decimal image of the Arb lower bound.
`bound_from_tail` says that the archimedean truncation remainder at the same
conductor is strictly below that recorded decimal. -/
structure EigenvalueLock (c N : ℕ) : Type where
  dim : ℕ
  dim_eq : dim = 2 * N + 1
  lam_min : ℝ
  lam_min_pos : 0 < lam_min
  bound_from_tail : ∃ tb : TailBound c, tb.C / (c : ℝ) ^ tb.α < lam_min

/-- The recorded λ_min is positive. -/
theorem eigenvalue_min_positive {c N : ℕ} (h : EigenvalueLock c N) : 0 < h.lam_min :=
  h.lam_min_pos

/-- Real record for `c = 13`, `N = 160`, dimension 321. -/
noncomputable def gw_eigenvalue_lock : EigenvalueLock gw_conductor gw_block :=
  { dim := gw_dim,
    dim_eq := gw_dim_eq,
    lam_min := gw_lambda_min,
    lam_min_pos := gw_lambda_min_pos,
    bound_from_tail := ⟨gw_tail_bound, gw_tail_bound_lt_lambda_min⟩ }

/-- Real record for `c = 13`, `N = 128`, dimension 257. -/
noncomputable def gw_eigenvalue_lock_257 : EigenvalueLock gw_conductor gw_block_257 :=
  { dim := gw_dim_257,
    dim_eq := gw_dim_257_eq,
    lam_min := gw_lambda_min_257,
    lam_min_pos := gw_lambda_min_257_pos,
    bound_from_tail := ⟨gw_tail_bound, gw_tail_bound_lt_lambda_min_257⟩ }
