import Mathlib.Order.Filter.Tendsto
import Mathlib.Topology.Basic
import Mathlib.MeasureTheory.Integral.IntegrableOn
import Mathlib.MeasureTheory.Integral.Bochner.Set
import Mathlib.Analysis.SpecialFunctions.ImproperIntegrals
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.MeasureTheory.Function.L1Space.Integrable

open MeasureTheory Set Filter
open scoped Topology

/-- Test function space (standalone copy of the Stage 1 definition). -/
def MSAFTestFunctionSpace : Type :=
  { f : ℝ → ℝ // ContinuousOn f (Ici (0 : ℝ)) ∧ f 0 = 0 ∧ Filter.Tendsto f atTop (𝓝 0) }

/-- Polynomial decay hypothesis: `|f x| ≤ C / x` for `x ≥ 1`. -/
structure PolynomialDecay (f : ℝ → ℝ) : Type where
  C : ℝ
  hC_nonneg : 0 ≤ C
  h_bound : ∀ x : ℝ, 1 ≤ x → |f x| ≤ C / x

/-- L² membership predicate: the square of `f` is integrable on `(0, ∞)`. -/
def TestFunctionInL2 (f : MSAFTestFunctionSpace) : Prop :=
  IntegrableOn (fun x : ℝ => (f.val x) ^ 2) (Ioi (0 : ℝ))

/-- Algebraic identity used to dominate the decay term by `x⁻²`. -/
private lemma div_sq_eq_const_mul_rpow (C x : ℝ) (hx : 0 < x) :
    (C / x) ^ 2 = C ^ 2 * x ^ (-2 : ℝ) := by
  have hx0 : x ≠ 0 := ne_of_gt hx
  calc
    (C / x) ^ 2 = (C * x⁻¹) ^ 2 := by rw [div_eq_mul_inv]
    _ = C ^ 2 * (x⁻¹) ^ 2 := by rw [mul_pow]
    _ = C ^ 2 * x ^ (-2 : ℝ) := by
      congr 1
      rw [Real.rpow_neg (le_of_lt hx), Real.rpow_two, inv_pow]

/-- Main theorem: polynomial decay implies L² containment.

The proof splits `(0, ∞)` into `(0, 1]` and `(1, ∞)`.
On `(0, 1]` the function is continuous on the compact interval `[0, 1]`,
hence square-integrable.  On `(1, ∞)` the decay estimate dominates
`f(x)²` by `(C / x)² = C² · x⁻²`, which is integrable because `-2 < -1`. -/
theorem test_function_l2_containment (f : MSAFTestFunctionSpace)
    (hDecay : PolynomialDecay f.val) : TestFunctionInL2 f := by
  have h_cont_sq : ContinuousOn (fun x : ℝ => (f.val x) ^ 2) (Ici (0 : ℝ)) :=
    f.property.1.pow 2

  -- Left piece: (0, 1]
  have h_left_Icc : IntegrableOn (fun x : ℝ => (f.val x) ^ 2) (Icc (0 : ℝ) 1) :=
    (h_cont_sq.mono Icc_subset_Ici_self).integrableOn_Icc
  have h_left : IntegrableOn (fun x : ℝ => (f.val x) ^ 2) (Ioc (0 : ℝ) 1) :=
    h_left_Icc.mono_set Ioc_subset_Icc_self

  -- Right piece: (1, ∞)
  have h_rpow : IntegrableOn (fun x : ℝ => x ^ (-2 : ℝ)) (Ioi (1 : ℝ)) :=
    integrableOn_Ioi_rpow_of_lt (by norm_num) (by norm_num)
  have h_const : IntegrableOn (fun x : ℝ => hDecay.C ^ 2 * x ^ (-2 : ℝ)) (Ioi (1 : ℝ)) :=
    h_rpow.const_mul (hDecay.C ^ 2)
  have h_dom : IntegrableOn (fun x : ℝ => (hDecay.C / x) ^ 2) (Ioi (1 : ℝ)) := by
    refine h_const.congr_fun ?_ measurableSet_Ioi
    intro x hx
    have hx1 : (1 : ℝ) < x := hx
    have hxpos : 0 < x := lt_trans zero_lt_one hx1
    exact (div_sq_eq_const_mul_rpow hDecay.C x hxpos).symm

  have h_bound_sq : ∀ x ∈ Ioi (1 : ℝ), (f.val x) ^ 2 ≤ (hDecay.C / x) ^ 2 := by
    intro x hx
    have hxlt : (1 : ℝ) < x := hx
    have hx1 : 1 ≤ x := le_of_lt hxlt
    have hxpos : 0 < x := lt_trans zero_lt_one hxlt
    have hb : |f.val x| ≤ hDecay.C / x := hDecay.h_bound x hx1
    have hCx_nonneg : 0 ≤ hDecay.C / x :=
      div_nonneg hDecay.hC_nonneg (le_of_lt hxpos)
    have hsquare : |f.val x| ^ 2 ≤ (hDecay.C / x) ^ 2 :=
      pow_le_pow_left₀ (abs_nonneg _) hb 2
    simpa [sq_abs] using hsquare

  have h_right : IntegrableOn (fun x : ℝ => (f.val x) ^ 2) (Ioi (1 : ℝ)) := by
    have h_cont_sq_Ioi : ContinuousOn (fun x : ℝ => (f.val x) ^ 2) (Ioi (1 : ℝ)) :=
      h_cont_sq.mono (fun x hx => by
        have hx' : (1 : ℝ) < x := hx
        exact le_of_lt (lt_trans zero_lt_one hx'))
    have hmeas : AEStronglyMeasurable (fun x : ℝ => (f.val x) ^ 2)
        (volume.restrict (Ioi (1 : ℝ))) :=
      h_cont_sq_Ioi.aestronglyMeasurable measurableSet_Ioi
    refine Integrable.mono' h_dom hmeas ?_
    filter_upwards [ae_restrict_mem measurableSet_Ioi] with x hx
    have hx' : x ∈ Ioi (1 : ℝ) := hx
    simpa [Real.norm_eq_abs, abs_of_nonneg (sq_nonneg (f.val x))] using h_bound_sq x hx'

  -- Assemble the two pieces
  have h_union : IntegrableOn (fun x : ℝ => (f.val x) ^ 2) (Ioc (0 : ℝ) 1 ∪ Ioi (1 : ℝ)) :=
    h_left.union h_right
  have h_set : Ioi (0 : ℝ) = Ioc (0 : ℝ) 1 ∪ Ioi (1 : ℝ) := by
    ext x
    constructor
    · intro hx
      by_cases hx1 : x ≤ 1
      · exact Or.inl ⟨hx, hx1⟩
      · exact Or.inr (lt_of_not_ge hx1)
    · intro hx
      rcases hx with hx | hx
      · exact hx.1
      · have hxlt : (1 : ℝ) < x := hx
        exact lt_trans zero_lt_one hxlt
  change IntegrableOn (fun x : ℝ => (f.val x) ^ 2) (Ioi (0 : ℝ))
  rw [h_set]
  exact h_union
