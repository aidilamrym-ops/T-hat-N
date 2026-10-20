import Mathlib.NumberTheory.LSeries.HurwitzZetaEven
import Mathlib.Analysis.SpecificLimits.Normed
import Mathlib.Analysis.SpecialFunctions.Gamma.Basic
import Mathlib.Analysis.SpecialFunctions.Gaussian.GaussianIntegral
import Mathlib.Tactic
import spec_v4.XiUnconditional

/-!
# V6: certified bridge from the finite lattice to `completedCosZeta (1/2)`

This file proves four kernel-checked statements:

* `abs_kHalf_sub_lattice_le` (T1): the alternating theta tail is bounded by
  its first omitted term.
* `completedCosZeta_half_lattice_error` (T2): the exact finite-lattice value
  `latticeValue N x` approximates `completedCosZeta (1/2) (x : ℂ)` with the
  explicit error `latticeError N x`.
* `completedCosZeta_half_neg_of_lattice_certificate` (T3): a negative
  lattice certificate transfers the sign to the infinite object.
* `completedCosZeta_half_neg_of_first_term` (K1): the one-term certificate
  already suffices for every `x > 0`.

No project axiom, no `sorry`. This is **not** a proof of RH and says nothing
about zero locations; the object is the cosine completed zeta, not
`completedRiemannZeta`.
-/

open Real HurwitzZeta Filter Set MeasureTheory Topology
open scoped BigOperators

noncomputable section

namespace FiniteLatticeBridge

/-- The real half-kernel `cosKernel (1/2) t - 1`. -/
def kHalf (t : ℝ) : ℝ := cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1

/-- Magnitude of the `n`-th alternating theta term. -/
def latticeTerm (t : ℝ) (n : ℕ) : ℝ :=
  2 * Real.exp (-Real.pi * ((n : ℝ) + 1) ^ 2 * t)

/-- The `N`-term finite-lattice truncation of the half-kernel. -/
def latticeSum (N : ℕ) (t : ℝ) : ℝ :=
  Finset.sum (Finset.range N) (fun n => (-1 : ℝ) ^ (n + 1) * latticeTerm t n)

lemma kHalf_eq (t : ℝ) : kHalf t = cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1 := rfl

lemma latticeTerm_eq (t : ℝ) (n : ℕ) :
    latticeTerm t n = 2 * Real.exp (-Real.pi * ((n : ℝ) + 1) ^ 2 * t) := rfl

lemma latticeSum_eq (N : ℕ) (t : ℝ) :
    latticeSum N t = Finset.sum (Finset.range N) (fun n => (-1 : ℝ) ^ (n + 1) * latticeTerm t n) :=
  rfl

/-- The half-kernel is the sum of its alternating theta series. -/
theorem kernelHalf_hasSum (t : ℝ) (ht : 0 < t) :
    HasSum (fun n : ℕ => (-1 : ℝ) ^ (n + 1) * latticeTerm t n)
      (cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1) := by
  refine (hasSum_nat_cosKernel₀ (1 / 2 : ℝ) ht).congr_fun fun n => ?_
  rw [latticeTerm_eq]
  have hcos : Real.cos (2 * Real.pi * (1 / 2 : ℝ) * (((n : ℕ) : ℝ) + 1))
      = (-1 : ℝ) ^ (n + 1) := by
    have harg : 2 * Real.pi * (1 / 2 : ℝ) * (((n : ℕ) : ℝ) + 1)
        = (↑(n + 1) : ℝ) * Real.pi := by
      push_cast
      ring
    rw [harg]
    exact Real.cos_nat_mul_pi (n + 1)
  rw [hcos]
  ring

lemma latticeTerm_pos {t : ℝ} (_ht : 0 < t) (n : ℕ) : 0 < latticeTerm t n := by
  rw [latticeTerm_eq]
  exact mul_pos zero_lt_two (Real.exp_pos _)

lemma latticeTerm_antitone {t : ℝ} (ht : 0 < t) :
    Antitone (fun n : ℕ => latticeTerm t n) := by
  intro a b hab
  change latticeTerm t b ≤ latticeTerm t a
  rw [latticeTerm_eq, latticeTerm_eq]
  refine mul_le_mul_of_nonneg_left ?_ zero_le_two
  refine Real.exp_le_exp.mpr ?_
  have hpt : 0 ≤ Real.pi * t := le_of_lt (mul_pos Real.pi_pos ht)
  have h1 : (a : ℝ) + 1 ≤ (b : ℝ) + 1 := by
    exact_mod_cast Nat.add_le_add_right hab 1
  have h2 : ((a : ℝ) + 1) ^ 2 ≤ ((b : ℝ) + 1) ^ 2 :=
    pow_le_pow_left₀ (by positivity) h1 2
  nlinarith [mul_le_mul_of_nonneg_right h2 hpt]

lemma latticeTerm_summable {t : ℝ} (ht : 0 < t) :
    Summable (fun n : ℕ => latticeTerm t n) := by
  have hq1 : Real.exp (-Real.pi * t) < 1 := by
    rw [show (1 : ℝ) = Real.exp 0 by rw [Real.exp_zero]]
    refine Real.exp_lt_exp.mpr ?_
    rw [show (-Real.pi * t) = -(Real.pi * t) by ring]
    linarith [mul_pos Real.pi_pos ht]
  have hgeo := (summable_geometric_of_abs_lt_one
    (by
      rw [abs_of_nonneg (le_of_lt (Real.exp_pos (-Real.pi * t)))]
      exact hq1)).mul_left (2 * Real.exp (-Real.pi * t))
  refine Summable.of_nonneg_of_le (fun n => le_of_lt (latticeTerm_pos ht n)) (fun n => ?_) hgeo
  rw [latticeTerm_eq]
  have hpt : 0 ≤ Real.pi * t := le_of_lt (mul_pos Real.pi_pos ht)
  have h1 : (1 : ℝ) ≤ (n : ℝ) + 1 := by linarith [Nat.cast_nonneg (α := ℝ) n]
  have hx2 : ((n : ℝ) + 1) * 1 ≤ ((n : ℝ) + 1) * ((n : ℝ) + 1) :=
    mul_le_mul_of_nonneg_left h1 (by positivity)
  have hge : ((n : ℝ) + 1) * (Real.pi * t) ≤ ((n : ℝ) + 1) ^ 2 * (Real.pi * t) := by
    calc ((n : ℝ) + 1) * (Real.pi * t)
        = (((n : ℝ) + 1) * 1) * (Real.pi * t) := by ring
      _ ≤ (((n : ℝ) + 1) * ((n : ℝ) + 1)) * (Real.pi * t) :=
          mul_le_mul_of_nonneg_right hx2 hpt
      _ = ((n : ℝ) + 1) ^ 2 * (Real.pi * t) := by rw [pow_two]
  calc
    2 * Real.exp (-Real.pi * ((n : ℝ) + 1) ^ 2 * t)
        ≤ 2 * Real.exp ((n : ℝ) * (-Real.pi * t) + (-Real.pi * t)) :=
          mul_le_mul_of_nonneg_left
            (by
              refine Real.exp_le_exp.mpr ?_
              rw [show (-Real.pi * ((n : ℝ) + 1) ^ 2 * t)
                      = -(((n : ℝ) + 1) ^ 2 * (Real.pi * t)) by ring,
                  show ((n : ℝ) * (-Real.pi * t) + (-Real.pi * t))
                      = -(((n : ℝ) + 1) * (Real.pi * t)) by ring,
                  neg_le_neg_iff]
              exact hge)
            zero_le_two
    _ = (2 * Real.exp (-Real.pi * t)) * Real.exp (-Real.pi * t) ^ (n : ℕ) := by
          rw [Real.exp_add, Real.exp_nat_mul]
          ring

/-- **T1.** The alternating tail is bounded by its first omitted term. -/
theorem abs_kHalf_sub_lattice_le (t : ℝ) (ht : 0 < t) (N : ℕ) :
    |kHalf t - latticeSum N t| ≤ latticeTerm t N := by
  have hanti : Antitone (fun n : ℕ => latticeTerm t n) := latticeTerm_antitone ht
  have hsumm : Summable (fun n : ℕ => latticeTerm t n) := latticeTerm_summable ht
  have herr := alternating_series_error_bound (fun n : ℕ => latticeTerm t n) hanti hsumm N
  have hsum : HasSum (fun n : ℕ => (-1 : ℝ) ^ (n + 1) * latticeTerm t n) (kHalf t) := by
    rw [kHalf_eq]
    exact kernelHalf_hasSum t ht
  have hneg : HasSum (fun n : ℕ => (-1 : ℝ) ^ n * latticeTerm t n) (-(kHalf t)) := by
    have h := hsum.neg
    refine h.congr_fun fun n => ?_
    rw [pow_succ]
    ring
  have htsum : (∑' n : ℕ, (-1 : ℝ) ^ n * latticeTerm t n) = -(kHalf t) := hneg.tsum_eq
  have hpartial :
      (Finset.sum (Finset.range N) (fun n => (-1 : ℝ) ^ n * latticeTerm t n))
        = -latticeSum N t := by
    rw [latticeSum_eq, ← Finset.sum_neg_distrib]
    apply Finset.sum_congr rfl
    intro n _
    rw [pow_succ]
    ring
  rw [htsum, hpartial] at herr
  have hEq : (-(kHalf t)) - (-(latticeSum N t)) = latticeSum N t - kHalf t := by ring
  rw [hEq] at herr
  simpa [abs_sub_comm] using herr

/-- The complexified half-kernel, definitionally equal to V4's private `fC`
(complex subtraction, matching V4's `(cosKernel ... t - 1 : ℂ)`). -/
def fC (t : ℝ) : ℂ := (cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t : ℂ) - 1

lemma fC_eq (t : ℝ) : fC t = (cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t : ℂ) - 1 := rfl

lemma mellin_integrand_ofReal (x t : ℝ) (ht : 0 < t) :
    (t : ℂ) ^ ((x : ℂ) / 2 - 1) • fC t
      = ((t ^ (x / 2 - 1) * (cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1) : ℝ) : ℂ) := by
  have hs : (x : ℂ) / 2 - 1 = ((x / 2 - 1 : ℝ) : ℂ) := by
    push_cast
    ring
  rw [hs, ← Complex.ofReal_cpow (le_of_lt ht), smul_eq_mul]
  have hfCt : fC t = (↑(cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t) : ℂ) - 1 := fC_eq t
  rw [hfCt]
  rw [show (↑(cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t) : ℂ) - 1
      = ↑(cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1) by
    rw [Complex.ofReal_sub, Complex.ofReal_one]]
  rw [← Complex.ofReal_mul]

lemma mellin_fC_real (x : ℝ) (_hx : 0 < x) :
    mellin fC ((x : ℂ) / 2)
      = ((∫ t : ℝ in Ioi 0,
          t ^ (x / 2 - 1) * (cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1) : ℝ) : ℂ) := by
  rw [mellin]
  rw [setIntegral_congr_fun measurableSet_Ioi (fun t ht => mellin_integrand_ofReal x t ht)]
  exact integral_ofReal

/-- The Mellin scale `Γ(x/2) π^(-x/2)`. -/
def latticeScale (x : ℝ) : ℝ :=
  Real.Gamma (x / 2) * Real.pi ^ (-(x / 2))

lemma latticeScale_eq (x : ℝ) :
    latticeScale x = Real.Gamma (x / 2) * Real.pi ^ (-(x / 2)) := rfl

/-- Splitting the combined base `π (n+1)^2` into the separated prereg form. -/
lemma rpow_pi_mul_sq (x : ℝ) (n : ℕ) :
    (Real.pi * ((n : ℝ) + 1) ^ 2) ^ (-(x / 2))
      = Real.pi ^ (-(x / 2)) * ((n : ℝ) + 1) ^ (-x) := by
  rw [Real.mul_rpow (le_of_lt Real.pi_pos) (by positivity : 0 ≤ ((n : ℝ) + 1) ^ 2)]
  congr 1
  have h2 : (((n : ℝ) + 1) ^ 2 : ℝ) = Real.rpow ((n : ℝ) + 1) (2 : ℝ) :=
    (Real.rpow_natCast ((n : ℝ) + 1) 2).symm
  rw [h2]
  exact (Real.rpow_mul (by positivity : 0 ≤ (n : ℝ) + 1) (2 : ℝ) (-(x / 2))).symm.trans
    (by rw [show (2 : ℝ) * (-(x / 2)) = -x by ring])

/-- The exact finite-lattice value `Γ(x/2) π^(-x/2) Σ (-1)^(n+1)(n+1)^(-x)`. -/
def latticeValue (N : ℕ) (x : ℝ) : ℝ :=
  latticeScale x * Finset.sum (Finset.range N)
    (fun n => (-1 : ℝ) ^ (n + 1) * ((n : ℝ) + 1) ^ (-x))

lemma latticeValue_eq (N : ℕ) (x : ℝ) :
    latticeValue N x = latticeScale x * Finset.sum (Finset.range N)
      (fun n => (-1 : ℝ) ^ (n + 1) * ((n : ℝ) + 1) ^ (-x)) := rfl

/-- The explicit tail error `Γ(x/2) π^(-x/2) (N+1)^(-x)`. -/
def latticeError (N : ℕ) (x : ℝ) : ℝ :=
  latticeScale x * ((N : ℝ) + 1) ^ (-x)

lemma latticeError_eq (N : ℕ) (x : ℝ) :
    latticeError N x = latticeScale x * ((N : ℝ) + 1) ^ (-x) := rfl

lemma integrable_latticeTerm (x : ℝ) (hx : 0 < x) (n : ℕ) :
    IntegrableOn (fun t : ℝ => t ^ (x / 2 - 1) * latticeTerm t n) (Ioi 0) := by
  have hbase : IntegrableOn (fun t : ℝ =>
      t ^ (x / 2 - 1) * Real.exp (-(Real.pi * ((n : ℝ) + 1) ^ 2) * t ^ (1 : ℝ))) (Ioi 0) :=
    integrableOn_rpow_mul_exp_neg_mul_rpow (p := 1) (s := x / 2 - 1)
      (b := Real.pi * ((n : ℝ) + 1) ^ 2) (by linarith) one_pos (by positivity)
  have h2 : Integrable (fun t : ℝ =>
      2 * (t ^ (x / 2 - 1) * Real.exp (-(Real.pi * ((n : ℝ) + 1) ^ 2) * t)))
      (volume.restrict (Ioi 0)) := by
    have hb : Integrable (fun t : ℝ =>
        t ^ (x / 2 - 1) * Real.exp (-(Real.pi * ((n : ℝ) + 1) ^ 2) * t ^ (1 : ℝ)))
        (volume.restrict (Ioi 0)) := hbase
    simpa [Real.rpow_one] using hb.const_mul 2
  refine h2.congr ?_
  filter_upwards [ae_restrict_mem measurableSet_Ioi] with t _
  rw [latticeTerm_eq]
  ring

lemma integral_latticeTerm (x : ℝ) (hx : 0 < x) (n : ℕ) :
    ∫ t : ℝ in Ioi 0, t ^ (x / 2 - 1) * latticeTerm t n
      = 2 * (latticeScale x * ((n : ℝ) + 1) ^ (-x)) := by
  simp only [latticeTerm_eq]
  rw [show (∫ t : ℝ in Ioi 0,
        t ^ (x / 2 - 1) * (2 * Real.exp (-Real.pi * ((n : ℝ) + 1) ^ 2 * t)))
      = ∫ t : ℝ in Ioi 0,
        2 * (t ^ (x / 2 - 1) * Real.exp (-((Real.pi * ((n : ℝ) + 1) ^ 2) * t))) by
    congr 1
    ext t
    ring]
  rw [integral_const_mul,
    integral_rpow_mul_exp_neg_mul_Ioi (by linarith) (by positivity)]
  rw [one_div, Real.inv_rpow (le_of_lt (by positivity))]
  rw [← Real.rpow_neg (le_of_lt (by positivity))]
  rw [rpow_pi_mul_sq x n, latticeScale_eq]
  ring

lemma integral_latticeSum (x : ℝ) (hx : 0 < x) (N : ℕ) :
    ∫ t : ℝ in Ioi 0, t ^ (x / 2 - 1) * latticeSum N t = 2 * latticeValue N x := by
  simp only [latticeSum_eq, latticeValue_eq]
  rw [show (∫ t : ℝ in Ioi 0,
        t ^ (x / 2 - 1) *
          Finset.sum (Finset.range N) (fun n => (-1 : ℝ) ^ (n + 1) * latticeTerm t n))
      = ∫ t : ℝ in Ioi 0,
        Finset.sum (Finset.range N)
          (fun n => ((-1 : ℝ) ^ (n + 1)) * (t ^ (x / 2 - 1) * latticeTerm t n)) by
    congr 1
    ext t
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro n _
    ring]
  rw [integral_finsetSum]
  · simp_rw [integral_const_mul, integral_latticeTerm x hx]
    rw [Finset.mul_sum, Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro n _
    ring
  · intro n _
    have hbase : Integrable (fun t : ℝ => t ^ (x / 2 - 1) * latticeTerm t n)
        (volume.restrict (Ioi 0)) := integrable_latticeTerm x hx n
    exact hbase.const_mul _

/-- **T2.** The finite-lattice value approximates `completedCosZeta (1/2) x`
with explicit error `latticeError N x`. -/
theorem completedCosZeta_half_lattice_error (x : ℝ) (hx : 0 < x) (N : ℕ) :
    ‖completedCosZeta ((1 / 2 : ℝ) : UnitAddCircle) (x : ℂ) - (latticeValue N x : ℂ)‖
      ≤ latticeError N x := by
  have hV4 : completedCosZeta ((1 / 2 : ℝ) : UnitAddCircle) (x : ℂ)
      = mellin fC ((x : ℂ) / 2) / 2 :=
    completedCosZeta_half_eq_mellin (s := (x : ℂ)) (by simpa using hx)
  have hcompl : completedCosZeta ((1 / 2 : ℝ) : UnitAddCircle) (x : ℂ)
      = (1 / 2 : ℂ) * (↑(∫ t : ℝ in Ioi 0, t ^ (x / 2 - 1) * kHalf t) : ℂ) := by
    rw [hV4, mellin_fC_real x hx]
    have hk : (∫ t : ℝ in Ioi 0,
        t ^ (x / 2 - 1) * (cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1))
        = ∫ t : ℝ in Ioi 0, t ^ (x / 2 - 1) * kHalf t := rfl
    rw [hk]
    ring
  have hfin : (∫ t : ℝ in Ioi 0, t ^ (x / 2 - 1) * latticeSum N t)
      = 2 * latticeValue N x := integral_latticeSum x hx N
  have hIntS' : Integrable (fun t : ℝ => t ^ (x / 2 - 1) * latticeSum N t)
      (volume.restrict (Ioi 0)) := by
    have hterms : ∀ n ∈ Finset.range N,
        Integrable (fun t : ℝ =>
          t ^ (x / 2 - 1) * ((-1 : ℝ) ^ (n + 1) * latticeTerm t n))
          (volume.restrict (Ioi 0)) := by
      intro n _
      have hb : Integrable (fun t : ℝ => t ^ (x / 2 - 1) * latticeTerm t n)
          (volume.restrict (Ioi 0)) := integrable_latticeTerm x hx n
      have hc := hb.const_mul ((-1 : ℝ) ^ (n + 1))
      refine hc.congr ?_
      filter_upwards [ae_restrict_mem measurableSet_Ioi] with t _
      ring
    have h := integrable_finsetSum (Finset.range N) hterms
    refine h.congr ?_
    filter_upwards [ae_restrict_mem measurableSet_Ioi] with t _
    rw [latticeSum_eq, Finset.mul_sum]
  have hIntD' : Integrable
      (fun t : ℝ => t ^ (x / 2 - 1) * (kHalf t - latticeSum N t))
      (volume.restrict (Ioi 0)) := by
    have hmaj : Integrable (fun t : ℝ => t ^ (x / 2 - 1) * latticeTerm t N)
        (volume.restrict (Ioi 0)) := integrable_latticeTerm x hx N
    refine hmaj.mono' ?_ ?_
    · have hcont : ContinuousOn
          (fun t : ℝ => t ^ (x / 2 - 1) * (kHalf t - latticeSum N t)) (Ioi 0) := by
        refine ContinuousOn.mul ?_ ?_
        · exact continuousOn_id.rpow_const (fun t ht => Or.inl (ne_of_gt ht))
        · refine ContinuousOn.sub ?_ ?_
          · exact (continuousOn_cosKernel _).sub continuousOn_const
          · show ContinuousOn (fun t : ℝ => latticeSum N t) (Ioi 0)
            simp only [latticeSum_eq]
            refine continuousOn_finsetSum (Finset.range N) ?_
            intro n _
            exact continuousOn_const.mul
              (continuousOn_const.mul
                (Real.continuous_exp.comp_continuousOn (continuousOn_const.mul continuousOn_id)))
      exact hcont.aestronglyMeasurable measurableSet_Ioi
    · filter_upwards [ae_restrict_mem measurableSet_Ioi] with t ht
      rw [Real.norm_eq_abs, abs_mul, abs_of_pos (Real.rpow_pos_of_pos ht _)]
      exact mul_le_mul_of_nonneg_left (abs_kHalf_sub_lattice_le t ht N)
        (le_of_lt (Real.rpow_pos_of_pos ht _))
  have hIntK' : Integrable (fun t : ℝ => t ^ (x / 2 - 1) * kHalf t)
      (volume.restrict (Ioi 0)) := by
    have h := hIntS'.add hIntD'
    refine h.congr ?_
    filter_upwards [ae_restrict_mem measurableSet_Ioi] with t _
    simp only [Pi.add_apply]
    ring
  have hsplit : (∫ t : ℝ in Ioi 0, t ^ (x / 2 - 1) * kHalf t)
      - (∫ t : ℝ in Ioi 0, t ^ (x / 2 - 1) * latticeSum N t)
      = ∫ t : ℝ in Ioi 0, t ^ (x / 2 - 1) * (kHalf t - latticeSum N t) := by
    calc (∫ t : ℝ in Ioi 0, t ^ (x / 2 - 1) * kHalf t)
        - (∫ t : ℝ in Ioi 0, t ^ (x / 2 - 1) * latticeSum N t)
        = ∫ t : ℝ in Ioi 0,
            (t ^ (x / 2 - 1) * kHalf t - t ^ (x / 2 - 1) * latticeSum N t) :=
          (integral_sub hIntK' hIntS').symm
      _ = ∫ t : ℝ in Ioi 0,
            t ^ (x / 2 - 1) * (kHalf t - latticeSum N t) := by
          congr 1
          ext t
          ring
  have hdiff : ((1 / 2 : ℝ) * ∫ t : ℝ in Ioi 0, t ^ (x / 2 - 1) * kHalf t)
      - latticeValue N x
      = (1 / 2 : ℝ) * ∫ t : ℝ in Ioi 0,
          t ^ (x / 2 - 1) * (kHalf t - latticeSum N t) := by
    have hfin' : latticeValue N x
        = (1 / 2 : ℝ) * ∫ t : ℝ in Ioi 0, t ^ (x / 2 - 1) * latticeSum N t := by
      rw [hfin]
      ring
    rw [hfin', ← hsplit]
    ring
  rw [hcompl]
  have hcast : (1 / 2 : ℂ) * (↑(∫ t : ℝ in Ioi 0, t ^ (x / 2 - 1) * kHalf t) : ℂ)
        - (latticeValue N x : ℂ)
      = (((1 / 2 : ℝ) * (∫ t : ℝ in Ioi 0, t ^ (x / 2 - 1) * kHalf t)
          - latticeValue N x : ℝ) : ℂ) := by
    calc (1 / 2 : ℂ) * (↑(∫ t : ℝ in Ioi 0, t ^ (x / 2 - 1) * kHalf t) : ℂ)
          - (latticeValue N x : ℂ)
        = (↑((1 / 2 : ℝ) * (∫ t : ℝ in Ioi 0, t ^ (x / 2 - 1) * kHalf t)) : ℂ)
            - (latticeValue N x : ℂ) := by
          rw [Complex.ofReal_mul]
          rw [show ((1 / 2 : ℝ) : ℂ) = (1 / 2 : ℂ) by push_cast; ring]
      _ = (↑((1 / 2 : ℝ) * (∫ t : ℝ in Ioi 0, t ^ (x / 2 - 1) * kHalf t)
            - latticeValue N x) : ℂ) := by
          norm_cast
  rw [hcast]
  rw [Complex.norm_real]
  rw [Real.norm_eq_abs]
  have hgoal : |((1 / 2 : ℝ) * (∫ t : ℝ in Ioi 0, t ^ (x / 2 - 1) * kHalf t)
        - latticeValue N x : ℝ)| = |((1 / 2 : ℝ) * (∫ t : ℝ in Ioi 0,
          t ^ (x / 2 - 1) * (kHalf t - latticeSum N t)) : ℝ)| := by
    rw [hdiff]
  rw [hgoal]
  have hbound : |(1 / 2 : ℝ) * ∫ t : ℝ in Ioi 0,
        t ^ (x / 2 - 1) * (kHalf t - latticeSum N t)| ≤ latticeError N x := by
    have habs : |∫ t : ℝ in Ioi 0,
          t ^ (x / 2 - 1) * (kHalf t - latticeSum N t)|
        ≤ ∫ t : ℝ in Ioi 0,
          |t ^ (x / 2 - 1) * (kHalf t - latticeSum N t)| :=
      abs_integral_le_integral_abs
    have hmono : (∫ t : ℝ in Ioi 0,
          |t ^ (x / 2 - 1) * (kHalf t - latticeSum N t)|)
        ≤ ∫ t : ℝ in Ioi 0, t ^ (x / 2 - 1) * latticeTerm t N := by
      refine integral_mono_ae ?_ ?_ ?_
      · simpa only [Real.norm_eq_abs] using hIntD'.norm
      · exact integrable_latticeTerm x hx N
      · filter_upwards [ae_restrict_mem measurableSet_Ioi] with t ht
        rw [abs_mul, abs_of_pos (Real.rpow_pos_of_pos ht _)]
        exact mul_le_mul_of_nonneg_left (abs_kHalf_sub_lattice_le t ht N)
          (le_of_lt (Real.rpow_pos_of_pos ht _))
    calc |(1 / 2 : ℝ) * ∫ t : ℝ in Ioi 0,
          t ^ (x / 2 - 1) * (kHalf t - latticeSum N t)|
        = (1 / 2 : ℝ) * |∫ t : ℝ in Ioi 0,
            t ^ (x / 2 - 1) * (kHalf t - latticeSum N t)| := by
          rw [abs_mul, abs_of_pos (by norm_num : (0 : ℝ) < 1 / 2)]
      _ ≤ (1 / 2 : ℝ) * (∫ t : ℝ in Ioi 0,
            |t ^ (x / 2 - 1) * (kHalf t - latticeSum N t)|) := by
          gcongr
      _ ≤ (1 / 2 : ℝ) * (∫ t : ℝ in Ioi 0,
            t ^ (x / 2 - 1) * latticeTerm t N) := by
          gcongr
      _ = (1 / 2 : ℝ) *
            (2 * (latticeScale x * ((N : ℝ) + 1) ^ (-x))) := by
          rw [integral_latticeTerm x hx N]
      _ = latticeError N x := by
          rw [latticeError_eq]
          ring
  exact hbound

/-- **T3.** A negative finite-lattice certificate transfers the sign to
`completedCosZeta (1/2) x`. -/
theorem completedCosZeta_half_neg_of_lattice_certificate
    (x : ℝ) (hx : 0 < x) (N : ℕ)
    (hcert : latticeValue N x + latticeError N x < 0) :
    (completedCosZeta ((1 / 2 : ℝ) : UnitAddCircle) (x : ℂ)).re < 0 := by
  have h := completedCosZeta_half_lattice_error x hx N
  have hre : (completedCosZeta ((1 / 2 : ℝ) : UnitAddCircle) (x : ℂ)).re
        - latticeValue N x ≤ latticeError N x := by
    calc (completedCosZeta ((1 / 2 : ℝ) : UnitAddCircle) (x : ℂ)).re
          - latticeValue N x
        = ((completedCosZeta ((1 / 2 : ℝ) : UnitAddCircle) (x : ℂ))
            - (latticeValue N x : ℂ)).re := by simp
      _ ≤ ‖completedCosZeta ((1 / 2 : ℝ) : UnitAddCircle) (x : ℂ)
            - (latticeValue N x : ℂ)‖ := Complex.re_le_norm _
      _ ≤ latticeError N x := h
  linarith

/-- **K1.** The one-term certificate `N = 1` already gives the negative
sign for every `x > 0`. -/
theorem completedCosZeta_half_neg_of_first_term (x : ℝ) (hx : 0 < x) :
    (completedCosZeta ((1 / 2 : ℝ) : UnitAddCircle) (x : ℂ)).re < 0 := by
  have hscale : 0 < latticeScale x := by
    rw [latticeScale_eq]
    exact mul_pos (Real.Gamma_pos_of_pos (by linarith))
      (Real.rpow_pos_of_pos Real.pi_pos _)
  have h2 : (2 : ℝ) ^ (-x) < 1 := by
    have h := Real.rpow_lt_rpow_of_exponent_lt (by norm_num : (1 : ℝ) < 2)
      (by linarith : -x < 0)
    simpa using h
  have hcert : latticeValue 1 x + latticeError 1 x < 0 := by
    have hsum : latticeValue 1 x + latticeError 1 x
        = latticeScale x * (-1 + (2 : ℝ) ^ (-x)) := by
      rw [latticeValue_eq, latticeError_eq]
      rw [Finset.sum_range_one]
      have h0 : ((↑(0 : ℕ) : ℝ) + 1) = 1 := by norm_num
      have h1 : ((↑(1 : ℕ) : ℝ) + 1) = 2 := by norm_num
      rw [h0, h1]
      simp only [zero_add, pow_one, Real.one_rpow, mul_one]
      ring
    rw [hsum]
    exact mul_neg_of_pos_of_neg hscale (by linarith)
  exact completedCosZeta_half_neg_of_lattice_certificate x hx 1 hcert

end FiniteLatticeBridge
