import Mathlib

open Finset
open scoped BigOperators

/-!
# Stage 6 — analytic `XC` tail: finite sum bound and vanishing majorant

This file formalises the finite-sum and limit steps of the P2 claim
pre-registered in `reports/PREREG_ANALYTIC_TAIL_2026-10-26.md`.

## What is proved

For `1 ≤ N` and `N + 1 ≤ n ≤ M`:

* `sum_Ico_one_div_sq_le`: the harmonic-square block is bounded by the
  telescoping majorant `1/N`,
  `∑_{n=N+1}^{M} 1/n² ≤ 1/N`;
* `sum_Ico_abs_le_of_pointwise`: a pointwise bound `|x n| ≤ 1/n²` passes to
  the finite tail sum;
* `epsilon_le_of_pointwise`: multiplication by `4/L` preserves the bound;
* `tendsto_epsilon_majorant`: `(4/L)/N → 0` as `N → ∞`.

## What is **not** proved

* No formalisation of the trigamma integral representation, the digamma or
  trigamma functions, or the geometric sums `gX1`/`gX2`.  The pointwise
  analytic bound `|XC(n)| < 1/n²` is an input from
  `reports/ANALYTIC_TAIL_BOUND_2026-10-26.md` and the Arb grid record
  `reports/analytic_tail_bound_c13.json`.
* No claim about the full Guinand–Weil matrix, its off-diagonal entries,
  its positive definiteness, zeta zeros, Weil positivity, or the Riemann
  Hypothesis.  This is a diagonal-tail lemma only.
-/

/-- Harmonic-square block bound: `∑_{n=N+1}^{M} 1/n² ≤ 1/N` for `1 ≤ N`.

The proof compares each term with the telescoping difference
`1/(n-1) - 1/n`, then sums the telescope. -/
theorem sum_Ico_one_div_sq_le (N M : ℕ) (hN : 1 ≤ N) :
    (∑ n ∈ Finset.Ico (N + 1) (M + 1), (1 : ℝ) / (n : ℝ) ^ 2) ≤ 1 / (N : ℝ) := by
  have hNpos : (0 : ℝ) < (N : ℝ) := by exact_mod_cast hN
  by_cases hM : M + 1 ≤ N + 1
  · rw [Finset.Ico_eq_empty (by omega)]
    positivity
  · have hNM : N ≤ M := by omega
    rw [Finset.sum_Ico_eq_sum_range]
    have hsub : M + 1 - (N + 1) = M - N := by omega
    rw [hsub]
    have hterm :
        ∀ k ∈ Finset.range (M - N),
          (1 : ℝ) / ((N + 1 + k : ℕ) : ℝ) ^ 2 ≤
            1 / ((N + k : ℕ) : ℝ) - 1 / ((N + k + 1 : ℕ) : ℝ) := by
      intro k hk
      have hk' : k < M - N := Finset.mem_range.mp hk
      have hNk : (0 : ℝ) < ((N + k : ℕ) : ℝ) := by
        exact_mod_cast (by omega : 0 < N + k)
      have hstep : (1 : ℝ) / ((N + 1 + k : ℕ) : ℝ) ^ 2 ≤
          1 / (((N + k : ℕ) : ℝ) * (((N + k : ℕ) : ℝ) + 1)) := by
        have hle : ((N + k : ℕ) : ℝ) * (((N + k : ℕ) : ℝ) + 1) ≤
            (((N + 1 + k : ℕ) : ℝ)) ^ 2 := by
          push_cast
          nlinarith [hNk]
        exact one_div_le_one_div_of_le (by positivity) hle
      have hsplit :
          (1 : ℝ) / (((N + k : ℕ) : ℝ) * (((N + k : ℕ) : ℝ) + 1)) =
            1 / ((N + k : ℕ) : ℝ) - 1 / ((N + k + 1 : ℕ) : ℝ) := by
        push_cast
        field_simp [hNk.ne']
        ring
      calc
        (1 : ℝ) / ((N + 1 + k : ℕ) : ℝ) ^ 2
            ≤ 1 / (((N + k : ℕ) : ℝ) * (((N + k : ℕ) : ℝ) + 1)) := hstep
        _ = 1 / ((N + k : ℕ) : ℝ) - 1 / ((N + k + 1 : ℕ) : ℝ) := hsplit
    calc
      (∑ k ∈ Finset.range (M - N), (1 : ℝ) / ((N + 1 + k : ℕ) : ℝ) ^ 2)
          ≤ ∑ k ∈ Finset.range (M - N),
              (1 / ((N + k : ℕ) : ℝ) - 1 / ((N + k + 1 : ℕ) : ℝ)) := by
            exact Finset.sum_le_sum hterm
      _ = 1 / (N : ℝ) - 1 / (M : ℝ) := by
            have htel : ∀ d : ℕ,
                (∑ k ∈ Finset.range d,
                  ((1 : ℝ) / ((N + k : ℕ) : ℝ) - 1 / ((N + k + 1 : ℕ) : ℝ)))
                  = 1 / (N : ℝ) - 1 / ((N + d : ℕ) : ℝ) := by
              intro d
              induction d with
              | zero => simp
              | succ d ih =>
                  rw [Finset.sum_range_succ, ih]
                  push_cast
                  ring
            rw [htel (M - N)]
            have hNM' : N + (M - N) = M := by omega
            rw [hNM']
      _ ≤ 1 / (N : ℝ) := by
            have hMpos : (0 : ℝ) ≤ 1 / (M : ℝ) := by positivity
            linarith

/-- A pointwise bound `|x n| ≤ 1/n²` passes to the finite tail sum. -/
theorem sum_Ico_abs_le_of_pointwise
    (x : ℕ → ℝ) (hx : ∀ n, 1 ≤ n → |x n| ≤ 1 / (n : ℝ) ^ 2)
    (N M : ℕ) (hN : 1 ≤ N) :
    (∑ n ∈ Finset.Ico (N + 1) (M + 1), |x n|) ≤ 1 / (N : ℝ) := by
  calc
    (∑ n ∈ Finset.Ico (N + 1) (M + 1), |x n|)
        ≤ ∑ n ∈ Finset.Ico (N + 1) (M + 1), (1 : ℝ) / (n : ℝ) ^ 2 := by
          apply Finset.sum_le_sum
          intro n hn
          have hn1 : 1 ≤ n := by
            have := (Finset.mem_Ico.mp hn).1
            omega
          exact hx n hn1
    _ ≤ 1 / (N : ℝ) := sum_Ico_one_div_sq_le N M hN

/-- Multiplication of the finite tail bound by the positive constant `4/L`. -/
theorem epsilon_le_of_pointwise
    (x : ℕ → ℝ) (hx : ∀ n, 1 ≤ n → |x n| ≤ 1 / (n : ℝ) ^ 2)
    (L : ℝ) (hL : 0 < L) (N M : ℕ) (hN : 1 ≤ N) :
    (4 / L) * (∑ n ∈ Finset.Ico (N + 1) (M + 1), |x n|) ≤
      (4 / L) * (1 / (N : ℝ)) := by
  apply mul_le_mul_of_nonneg_left
  · exact sum_Ico_abs_le_of_pointwise x hx N M hN
  · positivity

/-- The majorant `(4/L)/N` tends to zero, so the `XC` tail majorant vanishes. -/
theorem tendsto_epsilon_majorant (L : ℝ) (_hL : 0 < L) :
    Filter.Tendsto (fun N : ℕ => (4 / L) / (N : ℝ)) Filter.atTop (nhds 0) := by
  have h : Filter.Tendsto (fun N : ℕ => (1 : ℝ) / (N : ℝ)) Filter.atTop (nhds 0) :=
    tendsto_one_div_atTop_nhds_zero_nat
  have hmul := h.const_mul (4 / L)
  simpa [div_eq_mul_inv, mul_comm, mul_left_comm, mul_assoc] using hmul
