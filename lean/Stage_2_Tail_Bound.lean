import Mathlib.Tactic
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.MeasureTheory.Measure.Lebesgue.Basic
import Mathlib.Tactic.NormNum

open Real MeasureTheory Set

/-!
# Stage 2 — real archimedean tail constants for the Guinand–Weil assembly

This file replaces the synthetic example constants (`N = 100`, `C = 5`,
`α = 1`, `λ_min = 0.1`) with constants from the actual cutoff-free
Guinand–Weil work: `K`, `C`, `α` come from `_geom_sums` in
`source_arb_ldlt_certify.py` (external `oracle-toe/GUINAND_WEIL` checkout),
and the two `λ_min` values come from the Arb `arb_mat.eig` runs recorded by
`msaf/lambda_min_eig_ladder.py`.

## What the implementation actually bounds

The archimedean block uses the series

  `rho(x) = Σ_{k=0}^∞ exp(-(2k + 1/2) x)`.

The implementation truncates this series after the last retained index `K`
and adds the rigorous geometric remainder

  `rem(c, K) = 4 * c^(-(2K + 5/2)) / (1 - c^(-2))`,   `c > 1`,

because `exp(-L) = 1/c` with `L = log c`.  This is the expression used
verbatim by `_geom_sums` in `source_arb_ldlt_certify.py`.

For the certified run `c = 13`, `N = 160` (dimension `321`) at 6000 bits,
the loop stops at `K = 814`, hence

  `α = 2K + 5/2 = 3261/2`,
  `C = 4 / (1 - 13^(-2)) = 169/42`.

## Scope limit — read this before quoting the constants

`rem(c, K)` is an **archimedean truncation remainder**.  It is an exponential
tail in the truncation index `K`, written with base `c`.  It is *not* a
polynomial decay law in the conductor `c`, and it is *not* the analytic
test-function tail that the earlier scaffold called `C / N^α`.

No polynomial `C / c^α` tail bound is supplied by the implementation.
Fitting one from the `λ_min` ladder would be fabrication: the ladder script
`msaf/lambda_min_eig_ladder.py` explicitly refuses to fit an exponent, and the
c=13 slopes damp rather than follow a constant power law.  The constants
below are real, but they belong to the geometric truncation bound, not to a
fitted decay law.
-/

/-- Constants of the rigorous geometric tail remainder `C / c^α`.

`K` is the last retained index of `rho`; the implementation fixes the
exponent by `α = 2K + 5/2`.  The real instance in this file also fixes
`C = 4 / (1 - c^(-2))`; the structure keeps `C` as a field so that the
interface does not silently assume that formula for arbitrary `c`.
-/
structure TailBound (c : ℕ) : Type where
  K : ℕ
  C : ℝ
  α : ℝ
  α_eq : α = 2 * (K : ℝ) + 5 / 2
  C_nonneg : 0 ≤ C
  α_gt_half : (1 / 2 : ℝ) < α
  c_gt_one : 1 < c

/-- The geometric tail remainder is non-negative. -/
theorem tail_bound_nonneg {c : ℕ} (h : TailBound c) :
    0 ≤ h.C / (c : ℝ) ^ h.α := by
  have hc : (0 : ℝ) < (c : ℝ) := by
    exact_mod_cast (lt_trans Nat.zero_lt_one h.c_gt_one)
  exact div_nonneg h.C_nonneg (le_of_lt (Real.rpow_pos_of_pos hc h.α))

/-! ### Real constants from the c = 13, N = 160 certified run -/

/-- Conductor of the certified run. -/
def gw_conductor : ℕ := 13

/-- Block half-width; the matrix dimension is `2 * 160 + 1 = 321`. -/
def gw_block : ℕ := 160

/-- Matrix dimension recorded by the certified run. -/
def gw_dim : ℕ := 321

/-- Last retained index of the geometric series at 6000 bits and `c = 13`.

This is the value at which `_geom_sums` stops: it breaks at `k = 814`,
so the next half-integer exponent is `2 * 815 + 1/2 = 1630.5`. -/
def gw_tail_K : ℕ := 814

/-- `C = 4 / (1 - 13^(-2)) = 169/42`. -/
noncomputable def gw_tail_C : ℝ := 169 / 42

/-- `α = 2 * 814 + 5/2 = 3261/2`. -/
noncomputable def gw_tail_alpha : ℝ := 3261 / 2

/-- Recorded lower-bound decimal for `reports/lambda_min_eig_ladder_dim321.json`,
`c = 13`, `N = 160`, dimension 321, precision 6000 bits.

The JSON stores a float64 image of the Arb lower endpoint (`float(lo.lower())`);
this Lean value is the exact decimal rational equal to that printed image.  It
can differ from the Arb endpoint by at most one ulp.  The Arb enclosure itself,
not this decimal, is the certificate; see the registry entry for the provenance
and the float64 caveat. -/
noncomputable def gw_lambda_min : ℝ := 3123458832662237 / 10 ^ 74

/-- The real `TailBound` instance for the c = 13 run. -/
noncomputable def gw_tail_bound : TailBound gw_conductor :=
  { K := gw_tail_K,
    C := gw_tail_C,
    α := gw_tail_alpha,
    α_eq := by norm_num [gw_tail_alpha, gw_tail_K],
    C_nonneg := by norm_num [gw_tail_C],
    α_gt_half := by norm_num [gw_tail_alpha],
    c_gt_one := by norm_num [gw_conductor] }

/-- Dimension check: `321 = 2 * 160 + 1`. -/
theorem gw_dim_eq : gw_dim = 2 * gw_block + 1 := by
  norm_num [gw_dim, gw_block]

/-- The recorded λ_min is positive. -/
theorem gw_lambda_min_pos : 0 < gw_lambda_min := by
  norm_num [gw_lambda_min]

/-- Helper: the real tail remainder is below any positive `x` that is already
above `C / 10^60`.

The crude comparison `13^(3261/2) > 13^102 > 10^60` is enough: the exact
remainder is around `2.1e-1816`, while `λ_min` is around `3.1e-59`.  We
deliberately use the crude bound so the proof does not depend on evaluating a
1600-digit power. -/
lemma gw_tail_bound_lt_of_gt_ten_pow_sixty (x : ℝ)
    (hx : gw_tail_C / (10 : ℝ) ^ 60 < x) :
    gw_tail_C / (gw_conductor : ℝ) ^ gw_tail_alpha < x := by
  have hbig : (10 : ℝ) ^ 60 < (gw_conductor : ℝ) ^ gw_tail_alpha := by
    have h1 : (10 : ℝ) ^ 60 < (13 : ℝ) ^ 102 := by norm_num
    have h2 : (13 : ℝ) ^ 102 = (13 : ℝ) ^ (102 : ℝ) := by
      exact (Real.rpow_natCast 13 102).symm
    have h3 : (13 : ℝ) ^ (102 : ℝ) ≤ (13 : ℝ) ^ gw_tail_alpha := by
      apply Real.rpow_le_rpow_of_exponent_le
      · norm_num
      · norm_num [gw_tail_alpha]
    calc
      (10 : ℝ) ^ 60 < (13 : ℝ) ^ 102 := h1
      _ = (13 : ℝ) ^ (102 : ℝ) := h2
      _ ≤ (13 : ℝ) ^ gw_tail_alpha := h3
  have h1 : gw_tail_C / (gw_conductor : ℝ) ^ gw_tail_alpha <
      gw_tail_C / (10 : ℝ) ^ 60 := by
    apply div_lt_div_of_pos_left
    · norm_num [gw_tail_C]
    · norm_num
    · simpa [gw_conductor] using hbig
  exact lt_trans h1 hx

/-- The real archimedean tail remainder is strictly below the recorded
λ_min decimal for `c = 13`, `N = 160`, dimension 321.

This is a machine-checked scalar inequality.  It does **not** assert that Lean
has computed the eigenvalue; the eigenvalue certificate is the external Arb
run with `all_exclude_zero = true`.  See the registry entry for the exact
scope. -/
theorem gw_tail_bound_lt_lambda_min :
    gw_tail_C / (gw_conductor : ℝ) ^ gw_tail_alpha < gw_lambda_min := by
  apply gw_tail_bound_lt_of_gt_ten_pow_sixty
  norm_num [gw_tail_C, gw_lambda_min]

/-! ### Second real rung: c = 13, N = 128, dimension 257

The c=13 magnitude ladder also records `λ_min_lo = 3.2990200597971055e-59` at
dimension 257.  Including it shows that the comparison is not a one-off; the
same archimedean remainder (same conductor and precision) is below both
recorded lower-bound decimals. -/

/-- Block half-width of the dim-257 rung. -/
def gw_block_257 : ℕ := 128

/-- Matrix dimension of the dim-257 rung. -/
def gw_dim_257 : ℕ := 257

/-- Recorded lower-bound decimal for the dim-257 rung. -/
noncomputable def gw_lambda_min_257 : ℝ := 32990200597971055 / 10 ^ 75

/-- Dimension check: `257 = 2 * 128 + 1`. -/
theorem gw_dim_257_eq : gw_dim_257 = 2 * gw_block_257 + 1 := by
  norm_num [gw_dim_257, gw_block_257]

/-- The dim-257 recorded λ_min is positive. -/
theorem gw_lambda_min_257_pos : 0 < gw_lambda_min_257 := by
  norm_num [gw_lambda_min_257]

/-- The same real archimedean tail remainder is below the dim-257 λ_min decimal. -/
theorem gw_tail_bound_lt_lambda_min_257 :
    gw_tail_C / (gw_conductor : ℝ) ^ gw_tail_alpha < gw_lambda_min_257 := by
  apply gw_tail_bound_lt_of_gt_ten_pow_sixty
  norm_num [gw_tail_C, gw_lambda_min_257]
