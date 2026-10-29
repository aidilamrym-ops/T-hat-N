import Mathlib
import Stage_6_Analytic_Tail
open Finset
open scoped BigOperators

/-!
# Stage 7 – tail extensions formalisation (stub)

Provides off‑diagonal tail bound lemma reusing existing diagonal bound.
-/

/-- Off‑diagonal tail bound (stub). Uses same harmonic‑square bound as diagonal case. -/
theorem sum_Ico_offdiag_le (N M : ℕ) (hN : 1 ≤ N) :
  (∑ n ∈ Finset.Ico (N + 1) (M + 1), (1 : ℝ) / (n : ℝ) ^ 2) ≤ 1 / (N : ℝ) :=
by
  exact sum_Ico_one_div_sq_le N M hN

/-! Test lemma – compile without `sorry`. -/
example (N M : ℕ) (hN : 1 ≤ N) :
  (∑ n ∈ Finset.Ico (N+1) (M+1), (1:ℝ)/(n:ℝ)^2) ≤ 1/(N:ℝ) :=
  sum_Ico_offdiag_le N M hN

