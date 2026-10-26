import Stage_2_Tail_Bound
import Mathlib.Tactic
import Mathlib.LinearAlgebra.Matrix.PosDef
import Mathlib.Algebra.Order.Chebyshev
import Mathlib.Data.Matrix.Mul
import Mathlib.LinearAlgebra.Matrix.DotProduct
import Mathlib.Algebra.Order.Star.Real

open Matrix
open scoped BigOperators

/-!
# Stage 5 — entry-error envelope and finite perturbation theorem

This file formalises the finite arithmetic behind the P1 entry-error envelope
pre-registered in `reports/PREREG_ENTRY_ERROR_ENVELOPE_2026-10-26.md`.

## What is proved

For a real matrix `A` with a quadratic lower bound `λ * ‖x‖² ≤ xᵀAx` and a
Hermitian perturbation `E` whose quadratic form is bounded by
`|xᵀEx| ≤ δ * ‖x‖²`, the matrix `A + E` is positive definite whenever
`δ < λ` and `λ > 0`.

The entrywise envelope is converted into the quadratic bound by

    |xᵀEx| ≤ dim * ε * ‖x‖²,   provided |E_ij| ≤ ε for every entry,

using the Cauchy–Schwarz inequality on `∑ |x_i|`.

The concrete instance uses the pre-registered constants

    dim = 321,  ε = 10^-100,  δ = 321 * 10^-100,
    λ = gw_lambda_min = 3123458832662237 / 10^74.

## What is **not** proved

* No claim that Lean diagonalised the Arb matrix or proved `A.PosDef`;
  `A.PosDef` and the quadratic bound on `A` are hypotheses.
* No claim about the analytic tail, zeta zeros, the Riemann Hypothesis, or
  Weil positivity.
* No claim that `δ` is the exact entry-error of the Arb matrix.  The
  envelope record `reports/entry_error_envelope_c13_n160.json` is the
  external numerical certificate; the Lean theorem only checks the
  perturbation arithmetic.
-/

variable {n : Type*} [Fintype n] [DecidableEq n]

/-- Real quadratic form `x ⬝ᵥ (M *ᵥ x)`. -/
def qform (M : Matrix n n ℝ) (x : n → ℝ) : ℝ :=
  x ⬝ᵥ (M *ᵥ x)

omit [DecidableEq n] in
/-- The quadratic form is additive in the matrix. -/
theorem qform_add (A E : Matrix n n ℝ) (x : n → ℝ) :
    qform (A + E) x = qform A x + qform E x := by
  simp [qform, Matrix.add_mulVec, dotProduct_add]

/-- An entrywise bound `|E_ij| ≤ ε` gives the quadratic-form bound
`|xᵀEx| ≤ dim * ε * ‖x‖²`; no symmetry of `E` is needed for this estimate. -/
theorem abs_qform_le_of_entrywise (E : Matrix n n ℝ) (ε : ℝ) (hε : 0 ≤ ε)
    (hE : ∀ i j, |E i j| ≤ ε) (x : n → ℝ) :
    |qform E x| ≤ (Fintype.card n : ℝ) * ε * qform 1 x := by
  have hq1 : qform 1 x = ∑ i, x i ^ 2 := by
    simp [qform, dotProduct, pow_two]
  have hq : qform E x = ∑ i, ∑ j, x i * E i j * x j := by
    simp [qform, Matrix.mulVec, dotProduct, Finset.mul_sum, mul_assoc]
  rw [hq, hq1]
  have h1 : |∑ i, ∑ j, x i * E i j * x j| ≤ ∑ i, ∑ j, |x i| * ε * |x j| := by
    refine le_trans
      (Finset.abs_sum_le_sum_abs (fun i => ∑ j, x i * E i j * x j) Finset.univ)
      ?_
    apply Finset.sum_le_sum
    intro i _
    refine le_trans
      (Finset.abs_sum_le_sum_abs (fun j => x i * E i j * x j) Finset.univ)
      ?_
    apply Finset.sum_le_sum
    intro j _
    rw [abs_mul, abs_mul]
    exact mul_le_mul_of_nonneg_right
      (mul_le_mul_of_nonneg_left (hE i j) (abs_nonneg (x i)))
      (abs_nonneg (x j))
  have h2 : (∑ i, ∑ j, |x i| * ε * |x j|) =
      ε * ((∑ i, |x i|) * (∑ i, |x i|)) := by
    have hinner : ∀ i, (∑ j, |x i| * ε * |x j|) =
        (|x i| * ε) * (∑ j, |x j|) := by
      intro i
      rw [Finset.mul_sum]
    calc
      (∑ i, ∑ j, |x i| * ε * |x j|) =
          ∑ i, (|x i| * ε) * (∑ j, |x j|) := by
        apply Finset.sum_congr rfl
        intro i _
        exact hinner i
      _ = (∑ i, |x i| * ε) * (∑ j, |x j|) := by
        rw [← Finset.sum_mul]
      _ = ((∑ i, |x i|) * ε) * (∑ j, |x j|) := by
        rw [← Finset.sum_mul]
      _ = ε * ((∑ i, |x i|) * (∑ i, |x i|)) := by ring
  have h3 : ε * ((∑ i, |x i|) * (∑ i, |x i|)) ≤
      ε * ((Fintype.card n : ℝ) * ∑ i, x i ^ 2) := by
    apply mul_le_mul_of_nonneg_left _ hε
    have h := sq_sum_le_card_mul_sum_sq (s := Finset.univ) (f := fun i => |x i|)
    have h' : (∑ i, |x i|) * (∑ i, |x i|) ≤
        (Fintype.card n : ℝ) * ∑ i, x i ^ 2 := by
      simpa [sq, sq_abs] using h
    exact h'
  calc
    |∑ i, ∑ j, x i * E i j * x j| ≤ ∑ i, ∑ j, |x i| * ε * |x j| := h1
    _ = ε * ((∑ i, |x i|) * (∑ i, |x i|)) := h2
    _ ≤ ε * ((Fintype.card n : ℝ) * ∑ i, x i ^ 2) := h3
    _ = (Fintype.card n : ℝ) * ε * ∑ i, x i ^ 2 := by ring

/-- Finite perturbation theorem: a quadratic lower bound `λ‖x‖² ≤ xᵀAx` and a
quadratic error bound `|xᵀEx| ≤ δ‖x‖²` with `δ < λ` preserve positive
definiteness.  The hypotheses `A.PosDef` and the bound on `A` are supplied by
the caller; this lemma does not construct or diagonalise `A`. -/
theorem posDef_add_of_quadratic_bound (A E : Matrix n n ℝ) (lam delta : ℝ)
    (hA : A.PosDef)
    (hAquad : ∀ x, lam * qform 1 x ≤ qform A x)
    (hEquad : ∀ x, |qform E x| ≤ delta * qform 1 x)
    (hdelta : delta < lam) (hlam : 0 < lam)
    (hE : E.IsHermitian) :
    (A + E).PosDef := by
  have hlam_pos : 0 < lam := hlam
  refine Matrix.PosDef.of_dotProduct_mulVec_pos (hA.isHermitian.add hE) ?_
  intro x hx
  have hq1pos : 0 < qform 1 x := by
    simpa [qform] using (Matrix.dotProduct_star_self_pos_iff (v := x)).2 hx
  have hmain : 0 < qform (A + E) x := by
    rw [qform_add]
    have h1 := hAquad x
    have h2 := (abs_le.mp (hEquad x)).1
    have h3 : (lam - delta) * qform 1 x =
        lam * qform 1 x - delta * qform 1 x := by ring
    have hpos : 0 < (lam - delta) * qform 1 x :=
      mul_pos (sub_pos.mpr hdelta) hq1pos
    linarith
  simpa [qform] using hmain

/-! ### Pre-registered constants -/

/-- Pre-registered entry-error envelope `ε = 10^-100`. -/
noncomputable def gw_epsilon : ℝ := 1 / 10 ^ 100

/-- Pre-registered dimension times epsilon: `321 * 10^-100 = 3.21 * 10^-98`. -/
noncomputable def gw_entry_delta : ℝ := (gw_dim : ℝ) * gw_epsilon

/-- The pre-registered entry envelope is below the recorded λ_min decimal. -/
theorem gw_entry_delta_lt_lambda_min : gw_entry_delta < gw_lambda_min := by
  norm_num [gw_entry_delta, gw_epsilon, gw_dim, gw_lambda_min]

/-- Concrete instantiation for the `c = 13`, `N = 160`, `dim = 321` block.

The theorem takes the Arb positivity certificate only through the hypotheses
`hA : A.PosDef` and `hAquad`; it does **not** prove that Lean has computed the
eigenvalues of the Arb matrix. -/
theorem gw_entry_perturbation_posDef
    (A E : Matrix (Fin gw_dim) (Fin gw_dim) ℝ)
    (hA : A.PosDef)
    (hAquad : ∀ x, gw_lambda_min * qform 1 x ≤ qform A x)
    (hEentry : ∀ i j, |E i j| ≤ gw_epsilon)
    (hE : E.IsHermitian) :
    (A + E).PosDef := by
  have hε : 0 ≤ gw_epsilon := by
    unfold gw_epsilon
    positivity
  refine posDef_add_of_quadratic_bound A E gw_lambda_min gw_entry_delta
    hA hAquad ?_ gw_entry_delta_lt_lambda_min gw_lambda_min_pos hE
  intro x
  have h := abs_qform_le_of_entrywise E gw_epsilon hε hEentry x
  have hcard : (Fintype.card (Fin gw_dim) : ℝ) = (gw_dim : ℝ) := by simp
  rw [hcard] at h
  calc
    |qform E x| ≤ (gw_dim : ℝ) * gw_epsilon * qform 1 x := h
    _ = gw_entry_delta * qform 1 x := by
      unfold gw_entry_delta
      ring
