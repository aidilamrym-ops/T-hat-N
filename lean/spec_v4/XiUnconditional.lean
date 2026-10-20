import Mathlib.NumberTheory.LSeries.HurwitzZetaEven
import Mathlib.NumberTheory.LSeries.RiemannZeta
import Mathlib.Analysis.SpecificLimits.Normed
import Mathlib.Analysis.Normed.Module.Connected
import Mathlib.Tactic

/-!
# XI unconditional: the midpoint sign of completed zeta

`hmid : ∀ x : ℝ, 0 < x → x < 1 → (completedRiemannZeta (x : ℂ)).re < 0`,
proved unconditionally: no project axiom, no `sorry`.

Route (the full map, including the recorded rejection of the symmetry attempt
where `1 - x` stays in `(0, 1)`, is in
`reports/PREREG_XI_UNCONDITIONAL_2026-10-20.md`):

1. `cosKernel (1/2) t - 1 < 0` for every `t > 0`, from pairwise theta gaps.
2. `completedCosZeta (1/2) s = mellin fC (s / 2) / 2` on `0 < re s`, from the
   decay bounds and the Mellin differentiability template.
3. Linearity of `mellin` and the real negativity of the integral give
   `completedCosZeta (1/2) x < 0` for `x > 0`.
4. `Gammaℝ x > 0` removes the completed factor:
   `cosZeta (1/2) x < 0` on `(0, 1)`.
5. The eta identity `cosZeta (1/2) s = (2 ^ (1 - s) - 1) * ζ(s)`: first on
   `1 < re s` by parity splitting of the Dirichlet series, then on `{1}ᶜ` by
   analytic continuation.
6. `2 ^ (1 - x) - 1 > 0` for `x < 1` gives `ζ(x) < 0`, and
   `completedRiemannZeta = Gammaℝ * ζ` closes `hmid`.
-/

open Real HurwitzZeta Filter Set MeasureTheory Topology

noncomputable section

/-! ## Alternating powers of `-1` -/

private lemma negOne_pow_two_mul (k : ℕ) : (-1 : ℝ) ^ (2 * k) = 1 := by
  induction k with
  | zero => simp
  | succ m ih =>
    have h2 : 2 * (m + 1) = 2 * m + 2 := by ring
    rw [h2, pow_add, ih, pow_two]
    norm_num

private lemma negOne_pow_odd (k : ℕ) : (-1 : ℝ) ^ (2 * k + 1) = -1 := by
  rw [pow_succ, negOne_pow_two_mul k, one_mul]

private lemma negOne_pow_two_succ (k : ℕ) : (-1 : ℝ) ^ (2 * k + 2) = 1 := by
  have h2 : 2 * k + 2 = 2 * (k + 1) := by ring
  rw [h2, negOne_pow_two_mul]

/-! ## The magnitude series of the half-kernel expansion -/

/-- Magnitude of the `n`-th term of the alternating expansion of
`cosKernel (1/2) t - 1` (form matching `hasSum_nat_cosKernel₀`). -/
private def kiTerm (t : ℝ) (n : ℕ) : ℝ :=
  2 * exp (-Real.pi * (((n : ℕ) : ℝ) + 1) ^ 2 * t)

private lemma kiTerm_eq (t : ℝ) (n : ℕ) :
    kiTerm t n = 2 * exp (-Real.pi * (((n : ℕ) : ℝ) + 1) ^ 2 * t) := rfl

private lemma kiTerm_pos {t : ℝ} (_ht : 0 < t) (n : ℕ) : 0 < kiTerm t n := by
  rw [kiTerm_eq]
  exact mul_pos zero_lt_two (exp_pos _)

/-- The magnitude sequence is strictly decreasing in `n`. -/
private lemma kiTerm_step {t : ℝ} (ht : 0 < t) (n : ℕ) : kiTerm t (n + 1) < kiTerm t n := by
  rw [kiTerm_eq, kiTerm_eq]
  refine mul_lt_mul_of_pos_left ?_ zero_lt_two
  refine exp_lt_exp.mpr ?_
  push_cast
  have hsq : ((n : ℝ) + 1) ^ 2 = ((n : ℝ) + 1) ^ 2 + (0 : ℝ) := by ring
  have hpt : (0 : ℝ) < Real.pi * t := mul_pos Real.pi_pos ht
  have hexp : ((n : ℝ) + 1) ^ 2 = ((n : ℝ) + 1) * ((n : ℝ) + 1) := by ring
  nlinarith [hsq, hpt, hexp]

/-- Summability of the magnitude series, by geometric comparison:
`kiTerm t n ≤ (2 * e^{-π t}) * (e^{-π t})^n` with `e^{-π t} ∈ (0, 1)`. -/
private lemma kiTerm_summable {t : ℝ} (ht : 0 < t) : Summable (fun n : ℕ => kiTerm t n) := by
  have hq1 : exp (-Real.pi * t) < 1 := by
    rw [show (1 : ℝ) = exp 0 by rw [exp_zero]]
    refine exp_lt_exp.mpr ?_
    rw [show (-Real.pi * t) = -(Real.pi * t) by ring]
    linarith [mul_pos Real.pi_pos ht]
  have hgeo := (summable_geometric_of_abs_lt_one
    (by
      rw [abs_of_nonneg (le_of_lt (exp_pos (-Real.pi * t)))]
      exact hq1)).mul_left (2 * exp (-Real.pi * t))
  refine Summable.of_nonneg_of_le (fun n => le_of_lt (kiTerm_pos ht n)) (fun n => ?_) hgeo
  rw [kiTerm_eq]
  -- pointwise: `2 * exp (-π (n+1)^2 t) ≤ (2 * exp (-π t)) * exp (-π t)^n`
  have hpt : (0 : ℝ) ≤ Real.pi * t := le_of_lt (mul_pos Real.pi_pos ht)
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
    2 * exp (-Real.pi * ((n : ℝ) + 1) ^ 2 * t)
        ≤ 2 * exp ((n : ℝ) * (-Real.pi * t) + (-Real.pi * t)) :=
          mul_le_mul_of_nonneg_left
            (by
              refine exp_le_exp.mpr ?_
              rw [show (-Real.pi * ((n : ℝ) + 1) ^ 2 * t)
                      = -(((n : ℝ) + 1) ^ 2 * (Real.pi * t)) by ring,
                  show ((n : ℝ) * (-Real.pi * t) + (-Real.pi * t))
                      = -(((n : ℝ) + 1) * (Real.pi * t)) by ring,
                  neg_le_neg_iff]
              exact hge)
            zero_le_two
    _ = (2 * exp (-Real.pi * t)) * exp (-Real.pi * t) ^ (n : ℕ) := by
          rw [exp_add, exp_nat_mul]; ring

/-- The alternating expansion of the half-kernel, with magnitudes `kiTerm`. -/
theorem kernelHalf_hasSum (t : ℝ) (ht : 0 < t) :
    HasSum (fun n : ℕ => (-1 : ℝ) ^ (n + 1) * kiTerm t n)
      (cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1) := by
  refine (hasSum_nat_cosKernel₀ (1 / 2 : ℝ) ht).congr_fun fun n => ?_
  rw [kiTerm_eq]
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

/-- Pairwise dominance: the alternating expansion of the half-kernel is strictly
negative.  Even-index terms are `-kiTerm (2k)` and odd-index terms are
`+kiTerm (2k+1)`, so the value is `-A + B = -(A - B)` where `A - B` is the sum
of the positive one-step gaps. -/
theorem kernelHalf_sub_one_neg (t : ℝ) (ht : 0 < t) :
    cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1 < 0 := by
  set f : ℕ → ℝ := fun n => (-1 : ℝ) ^ (n + 1) * kiTerm t n
  have hf_sum : HasSum f (cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1) :=
    kernelHalf_hasSum t ht
  have hks : Summable (fun n : ℕ => kiTerm t n) := kiTerm_summable ht
  have hEven_inj : Function.Injective (fun k : ℕ => 2 * k) :=
    mul_right_injective₀ (two_ne_zero' ℕ)
  have hOdd_inj : Function.Injective (fun k : ℕ => 2 * k + 1) :=
    (add_left_injective 1).comp (mul_right_injective₀ (two_ne_zero' ℕ))
  have hA : Summable (fun k : ℕ => kiTerm t (2 * k)) := hks.comp_injective hEven_inj
  have hB : Summable (fun k : ℕ => kiTerm t (2 * k + 1)) := hks.comp_injective hOdd_inj
  have hE : HasSum (fun k : ℕ => f (2 * k)) (-(∑' k : ℕ, kiTerm t (2 * k))) := by
    refine hA.hasSum.neg.congr_fun fun k => ?_
    show (-1 : ℝ) ^ (2 * k + 1) * kiTerm t (2 * k) = -kiTerm t (2 * k)
    rw [negOne_pow_odd]
    ring
  have hO : HasSum (fun k : ℕ => f (2 * k + 1)) (∑' k : ℕ, kiTerm t (2 * k + 1)) := by
    refine hB.hasSum.congr_fun fun k => ?_
    show (-1 : ℝ) ^ ((2 * k + 1) + 1) * kiTerm t (2 * k + 1) = kiTerm t (2 * k + 1)
    have h2 : (2 * k + 1) + 1 = 2 * k + 2 := by ring
    rw [h2, negOne_pow_two_succ]
    ring
  have hsplit : HasSum f
      (-(∑' k : ℕ, kiTerm t (2 * k)) + ∑' k : ℕ, kiTerm t (2 * k + 1)) :=
    hE.even_add_odd hO
  have hval : cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1
      = -(∑' k : ℕ, kiTerm t (2 * k)) + ∑' k : ℕ, kiTerm t (2 * k + 1) := by
    have h1 := hf_sum.tsum_eq
    have h2 := hsplit.tsum_eq
    linarith
  have hgap : ∀ k : ℕ, 0 < kiTerm t (2 * k) - kiTerm t (2 * k + 1) :=
    fun k => sub_pos.mpr (kiTerm_step ht (2 * k))
  have hG : Summable (fun k : ℕ => kiTerm t (2 * k) - kiTerm t (2 * k + 1)) := hA.sub hB
  have hGpos : 0 < ∑' k : ℕ, (kiTerm t (2 * k) - kiTerm t (2 * k + 1)) :=
    hG.tsum_pos (fun k => le_of_lt (hgap k)) 0 (hgap 0)
  have hsub : ∑' k : ℕ, (kiTerm t (2 * k) - kiTerm t (2 * k + 1))
      = (∑' k : ℕ, kiTerm t (2 * k)) - ∑' k : ℕ, kiTerm t (2 * k + 1) :=
    hA.tsum_sub hB
  rw [hval]
  linarith

/-! ## Stage 2: the complexified half-kernel and its Mellin bounds -/

private lemma half_ne_zero : ((1 / 2 : ℝ) : UnitAddCircle) ≠ 0 := by
  intro h
  rw [AddCircle.coe_eq_zero_iff] at h
  obtain ⟨n, hn⟩ := h
  have h2 : (n : ℝ) = 1 / 2 := by simpa using hn
  have h3 : ((2 * n : ℤ) : ℝ) = 1 := by push_cast; linarith
  have h4 : (2 * n : ℤ) = 1 := by exact_mod_cast h3
  omega

private lemma half_not_mem : (2⁻¹ : ℝ) ∉ AddSubgroup.zmultiples (1 : ℝ) := by
  intro h
  rw [AddSubgroup.mem_zmultiples_iff] at h
  obtain ⟨n, hn⟩ := h
  have h2 : (n : ℝ) = 1 / 2 := by simpa using hn
  have h3 : ((2 * n : ℤ) : ℝ) = 1 := by push_cast; linarith
  have h4 : (2 * n : ℤ) = 1 := by exact_mod_cast h3
  omega

/-- The complexified half-kernel `cosKernel (1/2) t - 1`. -/
private def fC (t : ℝ) : ℂ := (cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1 : ℂ)

private lemma continuousOn_fC : ContinuousOn fC (Ioi 0) := by
  exact (Complex.continuous_ofReal.comp_continuousOn (continuousOn_cosKernel _)).sub continuousOn_const

private lemma locallyIntegrableOn_fC : LocallyIntegrableOn fC (Ioi 0) :=
  continuousOn_fC.locallyIntegrableOn measurableSet_Ioi

/-- `fC` decays exponentially at `+∞`. -/
private lemma fC_isBigO_top :
    ∃ p : ℝ, 0 < p ∧ fC =O[atTop] (fun t : ℝ => Real.exp (-p * t)) := by
  obtain ⟨p, hp, hpO⟩ := isBigO_atTop_cosKernel_sub ((1 / 2 : ℝ) : UnitAddCircle)
  refine ⟨p, hp, ?_⟩
  refine (Complex.isBigO_ofReal_left.mpr hpO).congr_left fun t => ?_
  exact Complex.ofReal_sub _ _

/-- The functional equation in the form `cosKernel = t^(-1/2) * evenKernel (1/t)`. -/
private lemma cosKernel_half_eq_inv (t : ℝ) (ht : 0 < t) :
    cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t
      = (1 / t) ^ (1 / 2 : ℝ) * evenKernel ((1 / 2 : ℝ) : UnitAddCircle) (1 / t) := by
  have ht' : (0 : ℝ) < 1 / t := by positivity
  have hne : (1 / t) ^ (1 / 2 : ℝ) ≠ 0 := (Real.rpow_pos_of_pos ht' _).ne'
  have h := evenKernel_functional_equation ((1 / 2 : ℝ) : UnitAddCircle) (1 / t)
  rw [one_div_one_div] at h
  have h1 : (1 / t) ^ (-(1 / 2 : ℝ)) = 1 / (1 / t) ^ (1 / 2 : ℝ) := by
    rw [Real.rpow_neg (le_of_lt ht')]
    exact (one_div _).symm
  rw [← h1] at h
  calc cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t
      = (1 / t) ^ (1 / 2 : ℝ) * ((1 / t) ^ (1 / 2 : ℝ))⁻¹ *
          cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t := by
        rw [mul_inv_cancel₀ hne, one_mul]
    _ = (1 / t) ^ (1 / 2 : ℝ) *
          ((1 / t) ^ (-(1 / 2 : ℝ)) * cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t) := by
        rw [Real.rpow_neg (le_of_lt ht')]
        ring
    _ = (1 / t) ^ (1 / 2 : ℝ) * evenKernel ((1 / 2 : ℝ) : UnitAddCircle) (1 / t) := by
        rw [← h]

/-- `cosKernel (1/2) t` tends to `0` as `t → 0⁺`. -/
private lemma tendsto_cosKernel_half_at_zero :
    Tendsto (fun t : ℝ => cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t) (𝓝[>] 0) (𝓝 0) := by
  obtain ⟨p, hp, hpO⟩ := isBigO_atTop_evenKernel_sub ((1 / 2 : ℝ) : UnitAddCircle)
  have hpO' : (fun y : ℝ => evenKernel ((1 / 2 : ℝ) : UnitAddCircle) y)
      =O[atTop] (fun y : ℝ => Real.exp (-p * y)) := by
    simpa [half_not_mem] using hpO
  have hmul : (fun y : ℝ => evenKernel ((1 / 2 : ℝ) : UnitAddCircle) y * y ^ (1 / 2 : ℝ))
      =O[atTop] (fun y : ℝ => Real.exp (-p * y) * y ^ (1 / 2 : ℝ)) :=
    hpO'.mul (Asymptotics.isBigO_refl (fun y : ℝ => y ^ (1 / 2 : ℝ)) atTop)
  have hlim : Tendsto (fun y : ℝ => Real.exp (-p * y) * y ^ (1 / 2 : ℝ)) atTop (𝓝 0) := by
    simpa [mul_comm] using tendsto_rpow_mul_exp_neg_mul_atTop_nhds_zero (1 / 2) p hp
  have htop : Tendsto
      (fun y : ℝ => y ^ (1 / 2 : ℝ) * evenKernel ((1 / 2 : ℝ) : UnitAddCircle) y)
      atTop (𝓝 0) := by
    simpa [mul_comm] using hmul.trans_tendsto hlim
  have hinv : Tendsto (fun t : ℝ => 1 / t) (𝓝[>] (0 : ℝ)) atTop := by
    simpa using tendsto_inv_nhdsGT_zero (𝕜 := ℝ)
  have hcomp := htop.comp hinv
  refine Filter.Tendsto.congr' ?_ hcomp
  filter_upwards [self_mem_nhdsWithin] with t ht
  exact (cosKernel_half_eq_inv t ht).symm

/-- `fC` is bounded at `0⁺` (it tends to `-1`), giving the Mellin bound `b = 0`. -/
private lemma fC_isBigO_bot : fC =O[𝓝[>] 0] (fun t : ℝ => t ^ (-(0 : ℝ))) := by
  have hlim : Tendsto (fun t : ℝ => cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1)
      (𝓝[>] 0) (𝓝 ((0 : ℝ) - 1)) :=
    tendsto_cosKernel_half_at_zero.sub_const 1
  have hlimC : Tendsto fC (𝓝[>] 0) (𝓝 (((0 : ℝ) - 1 : ℝ) : ℂ)) := by
    have h := (Complex.continuous_ofReal.tendsto ((0 : ℝ) - 1)).comp hlim
    exact Filter.Tendsto.congr (fun t => Complex.ofReal_sub _ _) h
  refine Asymptotics.IsBigO.of_bound 2 ?_
  have hb : ∀ᶠ t : ℝ in 𝓝[>] (0 : ℝ), ‖fC t‖ ≤ 2 := by
    have hball := hlimC.eventually
      (Metric.closedBall_mem_nhds (((0 : ℝ) - 1 : ℝ) : ℂ) (by norm_num : (0 : ℝ) < 1))
    filter_upwards [hball] with t ht
    have h1 : ‖fC t - (((0 : ℝ) - 1 : ℝ) : ℂ)‖ ≤ 1 := by
      simpa [Metric.mem_closedBall, dist_eq_norm] using ht
    have h2 : ‖(((0 : ℝ) - 1 : ℝ) : ℂ)‖ = 1 := by
      rw [show ((0 : ℝ) - 1) = -1 by norm_num, Complex.norm_real, Real.norm_eq_abs]
      norm_num
    calc ‖fC t‖ = ‖(fC t - (((0 : ℝ) - 1 : ℝ) : ℂ)) + (((0 : ℝ) - 1 : ℝ) : ℂ)‖ := by
          rw [sub_add_cancel]
      _ ≤ ‖fC t - (((0 : ℝ) - 1 : ℝ) : ℂ)‖ + ‖(((0 : ℝ) - 1 : ℝ) : ℂ)‖ := norm_add_le _ _
      _ ≤ 1 + 1 := add_le_add h1 (le_of_eq h2)
      _ = 2 := by norm_num
  filter_upwards [hb] with t ht
  have hz : ‖t ^ (-(0 : ℝ))‖ = 1 := by
    rw [neg_zero, Real.rpow_zero]
    simp
  calc ‖fC t‖ ≤ 2 := ht
    _ = 2 * ‖t ^ (-(0 : ℝ))‖ := by rw [hz]; ring

/-- The Mellin transform of `fC` converges on the half-plane `0 < re s`. -/
private lemma mellinConvergent_fC {s : ℂ} (hs : 0 < s.re) : MellinConvergent fC s := by
  obtain ⟨p, hp, hpO⟩ := fC_isBigO_top
  exact mellinConvergent_of_isBigO_rpow_exp hp locallyIntegrableOn_fC hpO fC_isBigO_bot hs

/-- The Mellin transform of `fC` is holomorphic on `0 < re s`. -/
private lemma differentiableAt_mellin_fC {s : ℂ} (hs : 0 < s.re) :
    DifferentiableAt ℂ (mellin fC) s := by
  obtain ⟨p, hp, hpO⟩ := fC_isBigO_top
  exact mellin_differentiableAt_of_isBigO_rpow_exp hp locallyIntegrableOn_fC hpO fC_isBigO_bot hs

/-- `completedCosZeta (1/2)` is analytic on `0 < re s`. -/
private lemma analyticOnNhd_completedCosZeta_half :
    AnalyticOnNhd ℂ (fun s : ℂ => completedCosZeta ((1 / 2 : ℝ) : UnitAddCircle) s)
      {s : ℂ | 0 < s.re} := by
  refine DifferentiableOn.analyticOnNhd (fun s hs => ?_) (isOpen_Ioi.preimage Complex.continuous_re)
  exact (differentiableAt_completedCosZeta ((1 / 2 : ℝ) : UnitAddCircle)
    (by rintro rfl; simp at hs) (Or.inr half_ne_zero)).differentiableWithinAt

/-- `s ↦ mellin fC (s / 2) / 2` is analytic on `0 < re s`. -/
private lemma analyticOnNhd_mellin_fC_div :
    AnalyticOnNhd ℂ (fun s : ℂ => mellin fC (s / 2) / 2) {s : ℂ | 0 < s.re} := by
  refine DifferentiableOn.analyticOnNhd (fun s hs => ?_) (isOpen_Ioi.preimage Complex.continuous_re)
  have hs2 : 0 < (s / 2).re := by
    have hsr : 0 < s.re := hs
    rw [Complex.div_ofNat_re]
    linarith
  have h1 : DifferentiableAt ℂ (fun s : ℂ => s / 2) s := differentiableAt_id.div_const 2
  have h2 : DifferentiableAt ℂ (mellin fC) (s / 2) := differentiableAt_mellin_fC hs2
  exact ((h2.comp s h1).div_const 2).differentiableWithinAt

/-- The Mellin representation of `completedCosZeta (1/2)` on the half-plane
`0 < re s`, obtained by analytic continuation from `1 < re s`. -/
theorem completedCosZeta_half_eq_mellin {s : ℂ} (hs : 0 < s.re) :
    completedCosZeta ((1 / 2 : ℝ) : UnitAddCircle) s = mellin fC (s / 2) / 2 := by
  have hfg : (fun s : ℂ => completedCosZeta ((1 / 2 : ℝ) : UnitAddCircle) s)
      =ᶠ[𝓝 (2 : ℂ)] (fun s : ℂ => mellin fC (s / 2) / 2) := by
    refine eventually_of_mem (U := {t : ℂ | 1 < t.re}) ?_ ?_
    · exact (isOpen_Ioi.preimage Complex.continuous_re).mem_nhds
        (by norm_num : (1 : ℝ) < (2 : ℂ).re)
    · intro t (ht : 1 < t.re)
      change completedCosZeta ((1 / 2 : ℝ) : UnitAddCircle) t = mellin fC (t / 2) / 2
      rw [show completedCosZeta ((1 / 2 : ℝ) : UnitAddCircle) t
          = mellin (fun u : ℝ =>
              (cosKernel ((1 / 2 : ℝ) : UnitAddCircle) u - 1 : ℂ) / 2) (t / 2) by
        rw [mellin_div_const, completedCosZeta]
        congr 1
        refine ((hurwitzEvenFEPair ((1 / 2 : ℝ) : UnitAddCircle)).symm.hasMellin
          (?_ : 1 / 2 < (t / 2).re)).2.symm
        rwa [Complex.div_ofNat_re, div_lt_div_iff_of_pos_right two_pos]]
      rw [mellin_div_const]
      rfl
  exact AnalyticOnNhd.eqOn_of_preconnected_of_eventuallyEq
    (𝕜 := ℂ)
    (f := fun s : ℂ => completedCosZeta ((1 / 2 : ℝ) : UnitAddCircle) s)
    (g := fun s : ℂ => mellin fC (s / 2) / 2)
    analyticOnNhd_completedCosZeta_half analyticOnNhd_mellin_fC_div
    (convex_halfSpace_re_gt 0).isPreconnected (by norm_num) hfg hs

/-! ## Stage 3: the real integral and its sign -/

/-- The Mellin integrand at a real exponent is the complexification of a real
integrand. -/
private lemma mellin_integrand_ofReal (x t : ℝ) (ht : 0 < t) :
    (t : ℂ) ^ ((x : ℂ) / 2 - 1) • fC t
      = ((t ^ (x / 2 - 1) *
          (cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1) : ℝ) : ℂ) := by
  have hs : (x : ℂ) / 2 - 1 = ((x / 2 - 1 : ℝ) : ℂ) := by push_cast; ring
  rw [hs, ← Complex.ofReal_cpow (le_of_lt ht), smul_eq_mul]
  have hfCt : fC t = (↑(cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t) : ℂ) - 1 := rfl
  rw [hfCt]
  rw [show (↑(cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t) : ℂ) - 1
      = ↑(cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1) by
    rw [Complex.ofReal_sub, Complex.ofReal_one]]
  rw [← Complex.ofReal_mul]

/-- At a real argument, `mellin fC` is the complexification of a real integral. -/
private lemma mellin_fC_real (x : ℝ) (_hx : 0 < x) :
    mellin fC ((x : ℂ) / 2)
      = ((∫ t : ℝ in Ioi 0,
          t ^ (x / 2 - 1) * (cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1) : ℝ) : ℂ) := by
  rw [mellin]
  rw [setIntegral_congr_fun measurableSet_Ioi (fun t ht => mellin_integrand_ofReal x t ht)]
  exact integral_ofReal

/-- The real Mellin integral is strictly negative. -/
private lemma integral_fC_neg (x : ℝ) (hx : 0 < x) (_hx1 : x < 1) :
    (∫ t : ℝ in Ioi 0,
      t ^ (x / 2 - 1) * (cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1)) < 0 := by
  set g : ℝ → ℝ := fun t =>
    t ^ (x / 2 - 1) * (cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1)
  have hs : 0 < ((x : ℂ) / 2).re := by
    rw [Complex.div_ofNat_re, Complex.ofReal_re]
    linarith
  have hC : IntegrableOn (fun t : ℝ => ((g t : ℝ) : ℂ)) (Ioi 0) := by
    have h : MellinConvergent fC ((x : ℂ) / 2) := mellinConvergent_fC hs
    refine h.congr_fun ?_ measurableSet_Ioi
    intro t ht
    exact mellin_integrand_ofReal x t ht
  have hR : IntegrableOn g (Ioi 0) := by
    have h1 := (Integrable.re_im_iff.mpr hC).1
    have h2 : (fun t => RCLike.re ((g t : ℝ) : ℂ)) = g := by
      ext t
      simp
    rwa [h2] at h1
  have hnonneg : 0 ≤ᵐ[volume.restrict (Ioi (0 : ℝ))] (fun t : ℝ => -g t) := by
    refine (ae_restrict_mem measurableSet_Ioi).mono ?_
    intro t ht
    have h1 : 0 < t ^ (x / 2 - 1) := Real.rpow_pos_of_pos ht _
    have h2 : cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1 < 0 := kernelHalf_sub_one_neg t ht
    exact le_of_lt (neg_pos.mpr (mul_neg_of_pos_of_neg h1 h2))
  have hpos : 0 < ∫ t : ℝ in Ioi 0, (-g t) := by
    rw [integral_pos_iff_support_of_nonneg_ae hnonneg hR.neg]
    have hle : (volume.restrict (Ioi (0 : ℝ))) (Ioi (0 : ℝ))
        ≤ (volume.restrict (Ioi (0 : ℝ))) (Function.support (fun t : ℝ => -g t)) := by
      refine measure_mono fun t ht => ?_
      have h1 : 0 < t ^ (x / 2 - 1) := Real.rpow_pos_of_pos ht _
      have h2 : cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1 < 0 := kernelHalf_sub_one_neg t ht
      have h3 : g t < 0 := mul_neg_of_pos_of_neg h1 h2
      exact Function.mem_support.mpr (neg_ne_zero.mpr (ne_of_lt h3))
    have htop : (volume.restrict (Ioi (0 : ℝ))) (Ioi (0 : ℝ)) = ⊤ := by
      rw [Measure.restrict_apply measurableSet_Ioi, Set.inter_self, Real.volume_Ioi]
    rw [htop] at hle
    exact lt_of_lt_of_le ENNReal.zero_lt_top hle
  have hneg : (∫ t : ℝ in Ioi 0, (-g t)) = -(∫ t : ℝ in Ioi 0, g t) := by
    rw [integral_neg]
  rw [hneg] at hpos
  linarith

/-- `completedCosZeta (1/2)` is a strictly negative real number on `0 < x < 1`. -/
theorem completedCosZeta_half_neg {x : ℝ} (hx : 0 < x) (hx1 : x < 1) :
    ∃ r : ℝ, r < 0 ∧ completedCosZeta ((1 / 2 : ℝ) : UnitAddCircle) (x : ℂ) = (r : ℂ) := by
  refine ⟨(∫ t : ℝ in Ioi 0,
      t ^ (x / 2 - 1) * (cosKernel ((1 / 2 : ℝ) : UnitAddCircle) t - 1)) / 2, ?_, ?_⟩
  · linarith [integral_fC_neg x hx hx1]
  · rw [completedCosZeta_half_eq_mellin (s := (x : ℂ)) (by simpa using hx),
      mellin_fC_real x hx]
    push_cast
    ring

/-! ## Stage 4: removing the positive Gamma factor -/

/-- `Gammaℝ` is a positive real number on the positive real axis. -/
private lemma Gammaℝ_ofReal_pos {x : ℝ} (hx : 0 < x) :
    ∃ g : ℝ, 0 < g ∧ Complex.Gammaℝ (x : ℂ) = (g : ℂ) := by
  refine ⟨Real.pi ^ (-x / 2) * Real.Gamma (x / 2), ?_, ?_⟩
  · exact mul_pos (Real.rpow_pos_of_pos Real.pi_pos _)
      (Real.Gamma_pos_of_pos (by linarith))
  · rw [Complex.Gammaℝ_def]
    have h1 : (-(x : ℂ) / 2) = ((-x / 2 : ℝ) : ℂ) := by push_cast; ring
    have h2 : (x : ℂ) / 2 = ((x / 2 : ℝ) : ℂ) := by push_cast; ring
    rw [h1, h2, ← Complex.ofReal_cpow (le_of_lt Real.pi_pos), Complex.Gamma_ofReal]
    rw [← Complex.ofReal_mul]

/-- `cosZeta (1/2)` is a strictly negative real number on `(0, 1)`. -/
theorem cosZeta_half_neg {x : ℝ} (hx : 0 < x) (hx1 : x < 1) :
    ∃ r : ℝ, r < 0 ∧ cosZeta ((1 / 2 : ℝ) : UnitAddCircle) (x : ℂ) = (r : ℂ) := by
  obtain ⟨r, hr, hcomp⟩ := completedCosZeta_half_neg hx hx1
  obtain ⟨g, hg, hGam⟩ := Gammaℝ_ofReal_pos hx
  refine ⟨r / g, div_neg_of_neg_of_pos hr hg, ?_⟩
  rw [cosZeta, Function.update_of_ne (by exact_mod_cast ne_of_gt hx), hcomp, hGam,
    ← Complex.ofReal_div]

/-! ## Stage 5: the eta identity for `cosZeta (1/2)` -/

/-- The eta identity `cosZeta (1/2) s = (2^(1-s) - 1) * ζ(s)` in the convergence
half-plane `1 < re s`, proved by splitting the Dirichlet series into even and odd
parts. -/
private lemma eta_series {s : ℂ} (hs : 1 < s.re) :
    cosZeta ((1 / 2 : ℝ) : UnitAddCircle) s
      = ((2 : ℂ) ^ (1 - s) - 1) * riemannZeta s := by
  have hs0 : s ≠ 0 := Complex.ne_zero_of_one_lt_re hs
  -- (1) the cosine series at `a = 1/2` is the alternating series
  have hcos : HasSum (fun n : ℕ => (-1 : ℂ) ^ n / (n : ℂ) ^ s)
      (cosZeta ((1 / 2 : ℝ) : UnitAddCircle) s) := by
    refine (hasSum_nat_cosZeta (1 / 2 : ℝ) hs).congr_fun fun n => ?_
    have harg : 2 * π * (1 / 2 : ℝ) * (n : ℝ) = (n : ℝ) * π := by ring
    rw [harg, Real.cos_nat_mul_pi]
    push_cast
    ring
  -- (2) drop the `n = 0` term
  have hcos' : HasSum (fun n : ℕ => (-1 : ℂ) ^ (n + 1) / ((n + 1 : ℕ) : ℂ) ^ s)
      (cosZeta ((1 / 2 : ℝ) : UnitAddCircle) s) := by
    refine (hasSum_nat_add_iff (f := fun n : ℕ => (-1 : ℂ) ^ n / (n : ℂ) ^ s) 1).mpr ?_
    simpa [Complex.zero_cpow hs0] using hcos
  -- (3) the zeta series, shifted by one
  have hζ0 : HasSum (fun n : ℕ => (1 : ℂ) / (n : ℂ) ^ s) (riemannZeta s) := by
    have h := hasSum_nat_cosZeta 0 hs
    simpa [cosZeta_zero] using h
  have hζ : HasSum (fun n : ℕ => (1 : ℂ) / ((n + 1 : ℕ) : ℂ) ^ s) (riemannZeta s) := by
    refine (hasSum_nat_add_iff (f := fun n : ℕ => (1 : ℂ) / (n : ℂ) ^ s) 1).mpr ?_
    simpa [Complex.zero_cpow hs0] using hζ0
  -- (4) the odd subsequence is `2^{-s}` times the whole series
  have hOdd : HasSum (fun k : ℕ => (1 : ℂ) / ((2 * k + 1 + 1 : ℕ) : ℂ) ^ s)
      ((2 : ℂ) ^ (-s) * riemannZeta s) := by
    refine (hζ.mul_left ((2 : ℂ) ^ (-s))).congr_fun fun k => ?_
    show (1 : ℂ) / ((2 * k + 1 + 1 : ℕ) : ℂ) ^ s
      = (2 : ℂ) ^ (-s) * ((1 : ℂ) / ((k + 1 : ℕ) : ℂ) ^ s)
    rw [show 2 * k + 1 + 1 = 2 * (k + 1) by ring,
      show (((2 * (k + 1) : ℕ)) : ℂ) = ((2 : ℝ) : ℂ) * (((k + 1 : ℕ) : ℝ) : ℂ) by
        push_cast; ring,
      Complex.mul_cpow_ofReal_nonneg (by norm_num) (by positivity)]
    simp only [one_div, mul_inv, ← Complex.cpow_neg]
    push_cast
    ring
  -- (5) summability of the even subsequence
  have hsum : Summable (fun n : ℕ => (1 : ℂ) / ((n + 1 : ℕ) : ℂ) ^ s) := hζ.summable
  have hEvenS : Summable (fun k : ℕ => (1 : ℂ) / ((2 * k + 1 : ℕ) : ℂ) ^ s) :=
    hsum.comp_injective (mul_right_injective₀ (two_ne_zero' ℕ))
  -- (6) split the zeta series
  have hsplit : riemannZeta s
      = (∑' k, (1 : ℂ) / ((2 * k + 1 : ℕ) : ℂ) ^ s) + (2 : ℂ) ^ (-s) * riemannZeta s :=
    hζ.unique (hEvenS.hasSum.even_add_odd hOdd)
  have hEvenVal : (∑' k, (1 : ℂ) / ((2 * k + 1 : ℕ) : ℂ) ^ s)
      = riemannZeta s - (2 : ℂ) ^ (-s) * riemannZeta s :=
    eq_sub_iff_add_eq.mpr hsplit.symm
  -- (7) the alternating series
  have hAlt : HasSum (fun n : ℕ => (-1 : ℂ) ^ n / ((n + 1 : ℕ) : ℂ) ^ s)
      ((∑' k, (1 : ℂ) / ((2 * k + 1 : ℕ) : ℂ) ^ s) - (2 : ℂ) ^ (-s) * riemannZeta s) := by
    set f : ℕ → ℂ := fun n => (-1 : ℂ) ^ n / ((n + 1 : ℕ) : ℂ) ^ s with hf
    have he : HasSum (fun k : ℕ => f (2 * k))
        (∑' k, (1 : ℂ) / ((2 * k + 1 : ℕ) : ℂ) ^ s) := by
      refine hEvenS.hasSum.congr_fun fun k => ?_
      show f (2 * k) = (1 : ℂ) / ((2 * k + 1 : ℕ) : ℂ) ^ s
      simp only [hf]
      rw [show (-1 : ℂ) ^ (2 * k) = 1 by rw [pow_mul]; norm_num]
    have ho : HasSum (fun k : ℕ => f (2 * k + 1))
        (-((2 : ℂ) ^ (-s) * riemannZeta s)) := by
      refine hOdd.neg.congr_fun fun k => ?_
      show f (2 * k + 1) = -((1 : ℂ) / ((2 * k + 1 + 1 : ℕ) : ℂ) ^ s)
      simp only [hf]
      rw [show (-1 : ℂ) ^ (2 * k + 1) = -1 by rw [pow_succ, pow_mul]; norm_num]
      ring
    exact he.even_add_odd ho
  -- (8) evaluate the alternating series
  have hAltVal : (∑' n, (-1 : ℂ) ^ n / ((n + 1 : ℕ) : ℂ) ^ s)
      = (1 - (2 : ℂ) ^ (1 - s)) * riemannZeta s := by
    have h2s : (2 : ℂ) ^ (-s) + (2 : ℂ) ^ (-s) = (2 : ℂ) ^ (1 - s) := by
      rw [show (2 : ℂ) ^ (-s) + (2 : ℂ) ^ (-s) = 2 * (2 : ℂ) ^ (-s) by ring]
      rw [show (2 : ℂ) * (2 : ℂ) ^ (-s) = (2 : ℂ) ^ (1 - s) by
        rw [show (1 : ℂ) - s = 1 + -s by ring,
          Complex.cpow_add _ _ (by norm_num : (2 : ℂ) ≠ 0), Complex.cpow_one]]
    rw [hAlt.tsum_eq, hEvenVal, sub_sub, ← add_mul, h2s, sub_mul, one_mul]
  -- (9) identify with `cosZeta` and conclude
  have hcosAlt : HasSum (fun n : ℕ => (-1 : ℂ) ^ n / ((n + 1 : ℕ) : ℂ) ^ s)
      (-(cosZeta ((1 / 2 : ℝ) : UnitAddCircle) s)) := by
    refine hcos'.neg.congr_fun fun n => ?_
    show (-1 : ℂ) ^ n / ((n + 1 : ℕ) : ℂ) ^ s
      = -((-1 : ℂ) ^ (n + 1) / ((n + 1 : ℕ) : ℂ) ^ s)
    rw [show (-1 : ℂ) ^ (n + 1) = -((-1 : ℂ) ^ n) by rw [pow_succ]; ring]
    ring
  have h2 : -(cosZeta ((1 / 2 : ℝ) : UnitAddCircle) s)
      = (1 - (2 : ℂ) ^ (1 - s)) * riemannZeta s :=
    hcosAlt.tsum_eq.symm.trans hAltVal
  rw [show cosZeta ((1 / 2 : ℝ) : UnitAddCircle) s
      = -((1 - (2 : ℂ) ^ (1 - s)) * riemannZeta s) by rw [← h2]; ring]
  ring

/-- The eta identity on the whole plane minus `s = 1`, by analytic continuation. -/
private lemma eta_identity {s : ℂ} (hs : s ≠ 1) :
    cosZeta ((1 / 2 : ℝ) : UnitAddCircle) s
      = ((2 : ℂ) ^ (1 - s) - 1) * riemannZeta s := by
  have hanL : AnalyticOnNhd ℂ (cosZeta ((1 / 2 : ℝ) : UnitAddCircle)) {1}ᶜ :=
    DifferentiableOn.analyticOnNhd
      (fun z _ => (differentiable_cosZeta_of_ne_zero half_ne_zero z).differentiableWithinAt)
      isOpen_compl_singleton
  have hanR : AnalyticOnNhd ℂ
      (fun s : ℂ => ((2 : ℂ) ^ (1 - s) - 1) * riemannZeta s) {1}ᶜ := by
    refine DifferentiableOn.analyticOnNhd (fun z hz => ?_) isOpen_compl_singleton
    have h1 : DifferentiableAt ℂ (fun s : ℂ => (1 : ℂ) - s) z :=
      (differentiableAt_const _).sub differentiableAt_id
    have h2 : DifferentiableAt ℂ (fun s : ℂ => (2 : ℂ) ^ ((1 : ℂ) - s)) z :=
      h1.const_cpow (Or.inl (by norm_num))
    exact ((h2.sub_const 1).mul (differentiableAt_riemannZeta hz)).differentiableWithinAt
  exact hanL.eqOn_of_preconnected_of_eventuallyEq hanR
    (isConnected_compl_singleton_of_one_lt_rank (by simp) 1).isPreconnected
    (by norm_num : (2 : ℂ) ≠ 1)
    (eventuallyEq_of_mem
      ((isOpen_lt continuous_const Complex.continuous_re).mem_nhds
        (by norm_num : (1 : ℝ) < (2 : ℂ).re))
      (fun x hx => eta_series hx))
    hs

/-! ## Stage 6: the sign of `riemannZeta` and of the completed zeta -/

/-- `riemannZeta` is a strictly negative real number on `(0, 1)`. -/
private lemma riemannZeta_half_real_neg {x : ℝ} (hx : 0 < x) (hx1 : x < 1) :
    ∃ r : ℝ, r < 0 ∧ riemannZeta (x : ℂ) = (r : ℂ) := by
  obtain ⟨r, hr, hcos⟩ := cosZeta_half_neg hx hx1
  have hne : (x : ℂ) ≠ 1 := by exact_mod_cast ne_of_lt hx1
  have hid := eta_identity hne
  have hpow : (2 : ℂ) ^ (1 - (x : ℂ)) = ((2 : ℝ) ^ (1 - x) : ℝ) := by
    rw [show (1 : ℂ) - (x : ℂ) = ((1 - x : ℝ) : ℂ) by push_cast; ring]
    exact (Complex.ofReal_cpow (by norm_num) (1 - x)).symm
  have hpos : 0 < (2 : ℝ) ^ (1 - x) - 1 := by
    have h := Real.one_lt_rpow (by norm_num : (1 : ℝ) < 2) (by linarith : (0 : ℝ) < 1 - x)
    linarith
  have hne' : (↑((2 : ℝ) ^ (1 - x)) - 1 : ℂ) ≠ 0 := by
    rw [show (↑((2 : ℝ) ^ (1 - x)) - 1 : ℂ) = ↑((2 : ℝ) ^ (1 - x) - 1) by
      push_cast; ring]
    exact_mod_cast ne_of_gt hpos
  refine ⟨r / ((2 : ℝ) ^ (1 - x) - 1), div_neg_of_neg_of_pos hr hpos, ?_⟩
  rw [hcos, hpow] at hid
  have hζ : riemannZeta (x : ℂ) = (↑r : ℂ) / (↑((2 : ℝ) ^ (1 - x)) - 1) := by
    rw [hid, mul_div_cancel_left₀ _ hne']
  rw [hζ, show (↑((2 : ℝ) ^ (1 - x)) - 1 : ℂ) = ↑((2 : ℝ) ^ (1 - x) - 1) by
      push_cast; ring,
    ← Complex.ofReal_div]

/-- **Main theorem (V4)**: the real part of `completedRiemannZeta` is negative on
the open interval `(0, 1)`. -/
theorem hmid : ∀ x : ℝ, 0 < x → x < 1 → (completedRiemannZeta (x : ℂ)).re < 0 := by
  intro x hx hx1
  obtain ⟨r, hr, hζ⟩ := riemannZeta_half_real_neg hx hx1
  obtain ⟨g, hg, hGam⟩ := Gammaℝ_ofReal_pos hx
  have hx0 : (x : ℂ) ≠ 0 := by exact_mod_cast ne_of_gt hx
  have hGne : Complex.Gammaℝ (x : ℂ) ≠ 0 :=
    Complex.Gammaℝ_ne_zero_of_re_pos (by simpa using hx)
  have hcomp : completedRiemannZeta (x : ℂ) =
      Complex.Gammaℝ (x : ℂ) * riemannZeta (x : ℂ) := by
    rw [riemannZeta_def_of_ne_zero hx0]
    field_simp
  rw [hcomp, hGam, hζ, ← Complex.ofReal_mul, Complex.ofReal_re]
  exact mul_neg_of_pos_of_neg hg hr
