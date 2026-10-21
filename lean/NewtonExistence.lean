import Mathlib.Analysis.Calculus.Deriv.MeanValue
import Mathlib.Analysis.Calculus.MeanValue
import Mathlib.Tactic

open scoped BigOperators NNReal

/-! # Interval-Newton existence (Moore test, proved).

`moore_test_existence`: inclusion `N(X) ⊆ X` with a clean enclosure
forces a zero -- proved by sign trichotomy (IVT) with each
single-signed case killed by an MVT endpoint argument, the negative
cases reduced through negation invariance (`moore_image_neg_eq`).
Together with `moore_unique_of_deriv_exclusion` this is the complete
existence+uniqueness story behind the Python counter's soundness
gate. All hypotheses explicit; standard axioms only.
-/

namespace NewtonExistence

/-- Newton map with explicit derivative function (avoids `deriv`
    API friction at the fixed-point characterization). -/
noncomputable def newtonMap (f f' : ℝ → ℝ) (x : ℝ) : ℝ := x - f x / f' x

/-- Newton map restricted to the box (pointwise invariance). -/
noncomputable def newtonMapOn (a b : ℝ) (f f' : ℝ → ℝ)
    (hmap : Set.MapsTo (newtonMap f f') (Set.Icc a b) (Set.Icc a b))
    (x : Set.Icc a b) : Set.Icc a b :=
  ⟨newtonMap f f' x.val, hmap x.property⟩

/-- A point is fixed by the Newton map iff it is a zero, provided
    the derivative does not vanish there. -/
lemma isFixedPt_newtonMap_iff (f f' : ℝ → ℝ) {x : ℝ} (hne : f' x ≠ 0) :
    newtonMap f f' x = x ↔ f x = 0 := by
  simp only [newtonMap]
  constructor
  · intro h
    have h₁ : f x / f' x = 0 := by
      have h₂ : x - f x / f' x = x := by linarith
      have h₃ : f x / f' x = 0 := by linarith
      exact h₃
  exact mul_left_cancel₀ hne h₁
  · intro h
    rw [h, zero_div, sub_zero]

/-- Mean value step: a derivative bound on the box yields Lipschitz
    continuity of the Newton map on the box subtype. -/
lemma newton_lipschitz_of_deriv_bound (a b : ℝ) (f f' : ℝ → ℝ)
    (K : ℝ≥0)
    (hmap : Set.MapsTo (newtonMap f f') (Set.Icc a b) (Set.Icc a b))
    (hdiff : ∀ x ∈ Set.Icc a b, DifferentiableAt ℝ (newtonMap f f') x)
    (hbound : ∀ x ∈ Set.Icc a b, ‖deriv (newtonMap f f') x‖ ≤ ↑K) :
    LipschitzWith K (newtonMapOn a b f f' hmap) := by
  apply LipschitzWith.of_dist_le_mul
  intro x y
  have hxy : ∀ u ∈ Set.Icc a b, ∀ v ∈ Set.Icc a b,
      dist (newtonMap f f' u) (newtonMap f f' v)
        ≤ ↑K * dist u v := by
    intro u hu v hv
    have h := Convex.norm_image_sub_le_of_norm_deriv_le (s := Set.Icc a b)
      (f := newtonMap f f') hdiff hbound (convex_Icc a b) hu hv
    rw [dist_eq_norm, dist_eq_norm,
      norm_sub_rev (newtonMap f f' u) (newtonMap f f' v),
      norm_sub_rev u v]
    exact h
  have key := hxy x.val x.property y.val y.property
  show dist (newtonMap f f' x.val) (newtonMap f f' y.val)
    ≤ ↑K * dist x.val y.val
  exact key

/-- Moore box theorem: a Newton map preserving a closed interval and
    Lipschitz below one on that interval has exactly one zero there
    (Banach fixed point + fixed-point-is-zero). The Lipschitz bound
    is required only on the box -- the precise output of the MVT
    lemma above -- alongside the explicit analytic inputs. -/
theorem moore_box (a b : ℝ) (hab : a < b) (f f' : ℝ → ℝ)
    (hne : ∀ x ∈ Set.Icc a b, f' x ≠ 0)
    (hmap : Set.MapsTo (newtonMap f f') (Set.Icc a b) (Set.Icc a b))
    (K : ℝ≥0) (hK : K < 1)
    (hlip : LipschitzWith K (newtonMapOn a b f f' hmap)) :
    ∃! z, z ∈ Set.Icc a b ∧ f z = 0 := by
  have hC : ContractingWith K (newtonMapOn a b f f' hmap) := ⟨hK, hlip⟩
  obtain ⟨y, hyfix, _, _⟩ := hC.exists_fixedPoint
    ⟨a, Set.left_mem_Icc.mpr hab.le⟩ (edist_ne_top _ _)
  have hval : y.val ∈ Set.Icc a b := y.property
  have hfix : newtonMap f f' y.val = y.val :=
    Subtype.ext_iff.mp hyfix
  have hz : f y.val = 0 :=
    (isFixedPt_newtonMap_iff f f' (hne _ hval)).mp hfix
  refine ⟨y.val, ⟨hval, hz⟩, ?_⟩
  intro z hP
  obtain ⟨hzmem, hfz⟩ := hP
  have hfzfix : newtonMap f f' z = z :=
    (isFixedPt_newtonMap_iff f f' (hne _ hzmem)).mpr hfz
  have hzfix : newtonMapOn a b f f' hmap ⟨z, hzmem⟩ = ⟨z, hzmem⟩ :=
    Subtype.ext hfzfix
  rcases hC.eq_or_edist_eq_top_of_fixedPoints hyfix hzfix with h | h
  · exact (congrArg Subtype.val h).symm
  · exact absurd h (edist_ne_top _ _)

/-- End-to-end existence from a derivative bound (the usable form:
    clean derivative + invariance + pointwise Newton-derivative bound
    on the box yields exactly one zero there). -/
theorem moore_box_of_deriv_bound (a b : ℝ) (hab : a < b) (f f' : ℝ → ℝ)
    (hne : ∀ x ∈ Set.Icc a b, f' x ≠ 0)
    (hmap : Set.MapsTo (newtonMap f f') (Set.Icc a b) (Set.Icc a b))
    (K : ℝ≥0) (hK : K < 1)
    (hdiff : ∀ x ∈ Set.Icc a b, DifferentiableAt ℝ (newtonMap f f') x)
    (hbound : ∀ x ∈ Set.Icc a b, ‖deriv (newtonMap f f') x‖ ≤ ↑K) :
    ∃! z, z ∈ Set.Icc a b ∧ f z = 0 :=
  moore_box a b hab f f' hne hmap K hK
    (newton_lipschitz_of_deriv_bound a b f f' K hmap hdiff hbound)

/-! ## Moore-test form (flagship in progress): Brouwer fixed point.

The counter's soundness gate is the single-step Moore test, not the
Banach iteration above. Its formalization needs interval images as
sets plus a fixed-point principle. This increment lands Brouwer on a
closed interval (via IVT) and the Moore-operator vocabulary as plain
definitions. Existence/uniqueness through the operator is the next
increment, explicitly not claimed yet. -/

/-- Brouwer fixed point on a closed interval (proved via IVT on the
    displacement map). -/
theorem brouwer_Icc (a b : ℝ) (hab : a ≤ b) (g : ℝ → ℝ)
    (hg : Continuous g)
    (hmap : Set.MapsTo g (Set.Icc a b) (Set.Icc a b)) :
    ∃ x ∈ Set.Icc a b, g x = x := by
  by_cases ha : g a = a
  · exact ⟨a, Set.left_mem_Icc.mpr hab, ha⟩
  · by_cases hb : g b = b
    · exact ⟨b, Set.right_mem_Icc.mpr hab, hb⟩
    · have hga : a ≤ g a :=
        (Set.mem_Icc.mp (hmap (Set.left_mem_Icc.mpr hab))).1
      have hgb : g b ≤ b :=
        (Set.mem_Icc.mp (hmap (Set.right_mem_Icc.mpr hab))).2
      have hapos : 0 < g a - a :=
        sub_pos.mpr (lt_of_le_of_ne hga (fun h => ha h.symm))
      have hbneg : g b - b < 0 :=
        sub_neg.mpr (lt_of_le_of_ne hgb hb)
      have hcont : ContinuousOn (fun x => x - g x) (Set.Icc a b) :=
        (continuous_id.sub hg).continuousOn
      have hka : (fun x => x - g x) a < 0 := by
        show a - g a < 0
        linarith [hapos]
      have hkb : 0 < (fun x => x - g x) b := by
        show 0 < b - g b
        linarith [hbneg]
      obtain ⟨c, hcmem, hceq⟩ := intermediate_value_Icc hab hcont
        ⟨le_of_lt hka, le_of_lt hkb⟩
      exact ⟨c, hcmem, (sub_eq_zero.mp hceq).symm⟩

/-- Moore operator image: `N(X) = m - f(m)/F'(X)` as an explicit
    image set over the derivative-image set `D`. -/
def mooreImage (m : ℝ) (f : ℝ → ℝ) (D : Set ℝ) : Set ℝ :=
  (fun d => m - f m / d) '' D

/-- The Moore operator is invariant under negating the field:
    negating swaps the enclosure bounds. -/
lemma moore_image_neg_eq (m : ℝ) (f : ℝ → ℝ) (l u : ℝ) :
    Set.image (fun d => m - -f m / d) (Set.Icc (-u) (-l))
      = Set.image (fun d => m - f m / d) (Set.Icc l u) := by
  have e : ∀ d : ℝ, (m - -f m / d) = (m - f m / -d) := by
    intro d
    rw [neg_div, div_neg]
  ext y
  simp only [Set.mem_image]
  constructor
  · rintro ⟨d', hd', rfl⟩
    have h1 : l ≤ -d' := by linarith [(Set.mem_Icc.mp hd').2]
    have h2 : -d' ≤ u := by linarith [(Set.mem_Icc.mp hd').1]
    refine ⟨-d', ⟨h1, h2⟩, ?_⟩
    show m - f m / -d' = m - -f m / d'
    rw [← e]
  · rintro ⟨d, hd, rfl⟩
    have h1 : -u ≤ -d := by linarith [(Set.mem_Icc.mp hd).2]
    have h2 : -d ≤ -l := by linarith [(Set.mem_Icc.mp hd).1]
    refine ⟨-d, ⟨h1, h2⟩, ?_⟩
    show m - -f m / -d = m - f m / d
    rw [e, neg_neg]

/-! ## Moore-test uniqueness half (Rolle via MVT).

A derivative enclosure excluding zero allows at most one zero per
box. The existence half through the operator is mapped future work,
explicitly not claimed here. -/

/-- At most one zero per box under a clean derivative enclosure. -/
theorem moore_unique_of_deriv_exclusion (a b : ℝ) (f f' : ℝ → ℝ)
    (hcont : ContinuousOn f (Set.Icc a b))
    (hdiff : ∀ x ∈ Set.Icc a b, HasDerivAt f (f' x) x)
    (D : Set ℝ) (henc : ∀ x ∈ Set.Icc a b, f' x ∈ D)
    (h0 : 0 ∉ D) :
    ∀ u ∈ Set.Icc a b, ∀ v ∈ Set.Icc a b,
      f u = 0 → f v = 0 → u = v := by
  have key : ∀ x ∈ Set.Icc a b, ∀ y ∈ Set.Icc a b, x < y →
      f x = 0 → f y = 0 → x = y := by
    intro x hx y hy hlt hfx hfy
    have hsub : Set.Icc x y ⊆ Set.Icc a b :=
      Set.Icc_subset_Icc hx.1 hy.2
    have hfc : ContinuousOn f (Set.Icc x y) := hcont.mono hsub
    have hfd : DifferentiableOn ℝ f (Set.Ioo x y) := by
      intro z hz
      have hzm : z ∈ Set.Icc a b := hsub (Set.Ioo_subset_Icc_self hz)
      exact ((hdiff z hzm).differentiableAt).differentiableWithinAt
    obtain ⟨c, hcmem, hceq⟩ := exists_deriv_eq_slope f hlt hfc hfd
    have hcIcc : c ∈ Set.Icc a b := hsub (Set.Ioo_subset_Icc_self hcmem)
    have hderiv : deriv f c = 0 := by
      rw [hceq, hfy, hfx, sub_self, zero_div]
    have hfp : f' c = 0 := by
      rw [← (hdiff c hcIcc).deriv]
      exact hderiv
    have hmem := henc c hcIcc
    rw [hfp] at hmem
    exact absurd hmem h0
  intro u hu v hv hfu hfv
  rcases le_total u v with h | h
  · rcases eq_or_lt_of_le h with rfl | hlt
    · rfl
    · exact key u hu v hv hlt hfu hfv
  · rcases eq_or_lt_of_le h with rfl | hlt
    · rfl
    · exact (key v hv u hu hlt hfv hfu).symm

/-! ## Moore-test existence: trichotomy helper + endpoint lemmas.

Strategy (verified by hand, formalized incrementally): either the
field changes sign (IVT zero, done) or it is single-signed; under a
single-signed nonzero derivative box, each sign combination forces
the Moore image outside the box (MVT endpoint argument), so the
inclusion hypothesis rules single-signedness out. -/

/-- Trichotomy helper: opposite (non-strict) signs force a zero. -/
lemma exists_zero_of_sign_change (a b : ℝ) (f : ℝ → ℝ)
    (hcont : ContinuousOn f (Set.Icc a b))
    (x₁ : ℝ) (hx₁ : x₁ ∈ Set.Icc a b) (h1 : f x₁ ≤ 0)
    (x₂ : ℝ) (hx₂ : x₂ ∈ Set.Icc a b) (h2 : 0 ≤ f x₂) :
    ∃ z ∈ Set.Icc a b, f z = 0 := by
  by_cases h10 : f x₁ = 0
  · exact ⟨x₁, hx₁, h10⟩
  · by_cases h20 : f x₂ = 0
    · exact ⟨x₂, hx₂, h20⟩
    · have h1' : f x₁ < 0 := lt_of_le_of_ne h1 h10
      have h2' : 0 < f x₂ := lt_of_le_of_ne h2 (fun h => h20 h.symm)
      rcases le_total x₁ x₂ with h | h
      · rcases eq_or_lt_of_le h with rfl | hlt
        · exact (not_lt_of_gt h2' h1').elim
        · have hsub : Set.Icc x₁ x₂ ⊆ Set.Icc a b :=
            Set.Icc_subset_Icc hx₁.1 hx₂.2
          have hc : ContinuousOn f (Set.Icc x₁ x₂) := hcont.mono hsub
          obtain ⟨z, hzmem, hzeq⟩ := intermediate_value_Icc hlt.le hc
            (show (0 : ℝ) ∈ Set.Icc (f x₁) (f x₂)
              from ⟨le_of_lt h1', le_of_lt h2'⟩)
          exact ⟨z, hsub hzmem, hzeq⟩
      · rcases eq_or_lt_of_le h with rfl | hlt
        · exact (not_lt_of_gt h2' h1').elim
        · have hsub : Set.Icc x₂ x₁ ⊆ Set.Icc a b :=
            Set.Icc_subset_Icc hx₂.1 hx₁.2
          have hc : ContinuousOn (-f) (Set.Icc x₂ x₁) :=
            hcont.neg.mono hsub
          obtain ⟨z, hzmem, hzeq⟩ := intermediate_value_Icc hlt.le hc
            (show (0 : ℝ) ∈ Set.Icc ((-f) x₂) ((-f) x₁) from by
              simp only [Pi.neg_apply]
              exact ⟨le_of_lt (neg_lt_zero.mpr h2'),
                le_of_lt (neg_pos.mpr h1')⟩)
          have hfz : f z = 0 := neg_eq_zero.mp hzeq
          exact ⟨z, hsub hzmem, hfz⟩

/-- Impossibility: positive field with positive derivative box
    cannot satisfy the Moore inclusion (left-end escape). -/
lemma moore_pos_image_pos (a b m : ℝ) (hab : a < b)
    (hm : m ∈ Set.Icc a b) (f f' : ℝ → ℝ)
    (hcont : ContinuousOn f (Set.Icc a b))
    (hdiff : ∀ x ∈ Set.Icc a b, HasDerivAt f (f' x) x)
    (hpos : ∀ x ∈ Set.Icc a b, 0 < f x)
    (l u : ℝ) (hl : 0 < l)
    (henc : ∀ x ∈ Set.Icc a b, f' x ∈ Set.Icc l u)
    (hN : Set.image (fun d => m - f m / d) (Set.Icc l u)
      ⊆ Set.Icc a b) :
    False := by
  have ha_mem : a ∈ Set.Icc a b := Set.left_mem_Icc.mpr hab.le
  have hlu : l ≤ u :=
    le_trans (Set.mem_Icc.mp (henc a ha_mem)).1
      (Set.mem_Icc.mp (henc a ha_mem)).2
  have hLmem : m - f m / l
      ∈ Set.image (fun d => m - f m / d) (Set.Icc l u) :=
    ⟨l, ⟨le_rfl, hlu⟩, rfl⟩
  have hLa : a ≤ m - f m / l := (Set.mem_Icc.mp (hN hLmem)).1
  by_cases hma : m = a
  · subst hma
    have h1 : 0 < f m / l :=
      div_pos (hpos m ha_mem) hl
    linarith [hLa, h1]
  · have ham : a < m :=
      lt_of_le_of_ne (Set.mem_Icc.mp hm).1 (fun h => hma h.symm)
    have hsub : Set.Icc a m ⊆ Set.Icc a b :=
      Set.Icc_subset_Icc le_rfl (Set.mem_Icc.mp hm).2
    have hfc : ContinuousOn f (Set.Icc a m) := hcont.mono hsub
    have hfd : DifferentiableOn ℝ f (Set.Ioo a m) := by
      intro z hz
      have hzm : z ∈ Set.Icc a b := hsub (Set.Ioo_subset_Icc_self hz)
      exact ((hdiff z hzm).differentiableAt).differentiableWithinAt
    obtain ⟨c, hcmem, hceq⟩ := exists_deriv_eq_slope f ham hfc hfd
    have hcIcc : c ∈ Set.Icc a b := hsub (Set.Ioo_subset_Icc_self hcmem)
    have hlc : l ≤ f' c := (Set.mem_Icc.mp (henc c hcIcc)).1
    have hdc : deriv f c = f' c := (hdiff c hcIcc).deriv
    have h1 : l * (m - a) ≤ f m - f a := by
      have h2 : f m - f a = f' c * (m - a) := by
        have hfp : f' c = (f m - f a) / (m - a) := by
          rw [← hdc]
          exact hceq
        rw [hfp, div_mul_cancel₀ _ (sub_ne_zero.mpr (ne_of_gt ham))]
      rw [h2]
      exact mul_le_mul_of_nonneg_right hlc
        (sub_nonneg.mpr (le_of_lt ham))
    have hfa : 0 < f a := hpos a ha_mem
    have h2 : l * (m - a) < f m := by linarith [h1, hfa]
    have h3 : m - f m / l < a := by
      have h4 : (m - a) * l < f m := by linarith [h2]
      have h5 : (m - a) < f m / l := (lt_div_iff₀ hl).mpr h4
      linarith [h5]
    exact (not_lt.mpr hLa) h3

/-- Impossibility: positive field with negative derivative box
    cannot satisfy the Moore inclusion (right-end escape). -/
lemma moore_pos_image_neg (a b m : ℝ) (hab : a < b)
    (hm : m ∈ Set.Icc a b) (f f' : ℝ → ℝ)
    (hcont : ContinuousOn f (Set.Icc a b))
    (hdiff : ∀ x ∈ Set.Icc a b, HasDerivAt f (f' x) x)
    (hpos : ∀ x ∈ Set.Icc a b, 0 < f x)
    (l u : ℝ) (hu : u < 0)
    (henc : ∀ x ∈ Set.Icc a b, f' x ∈ Set.Icc l u)
    (hN : Set.image (fun d => m - f m / d) (Set.Icc l u)
      ⊆ Set.Icc a b) :
    False := by
  have ha_mem : a ∈ Set.Icc a b := Set.left_mem_Icc.mpr hab.le
  have hb_mem : b ∈ Set.Icc a b := Set.right_mem_Icc.mpr hab.le
  have hlu : l ≤ u :=
    le_trans (Set.mem_Icc.mp (henc a ha_mem)).1
      (Set.mem_Icc.mp (henc a ha_mem)).2
  have hRmem : m - f m / u
      ∈ Set.image (fun d => m - f m / d) (Set.Icc l u) :=
    ⟨u, ⟨hlu, le_rfl⟩, rfl⟩
  have hRb : m - f m / u ≤ b := (Set.mem_Icc.mp (hN hRmem)).2
  by_cases hmb : m = b
  · have h1 : f m / u < 0 :=
      div_neg_of_pos_of_neg (hpos m hm) hu
    rw [hmb] at hRb h1
    have h2 : 0 ≤ f b / u := by linarith [hRb]
    exact (not_le.mpr h1) h2
  · have hmb_lt : m < b :=
      lt_of_le_of_ne (Set.mem_Icc.mp hm).2 (fun h => hmb h)
    have hsub : Set.Icc m b ⊆ Set.Icc a b :=
      Set.Icc_subset_Icc (Set.mem_Icc.mp hm).1 le_rfl
    have hfc : ContinuousOn f (Set.Icc m b) := hcont.mono hsub
    have hfd : DifferentiableOn ℝ f (Set.Ioo m b) := by
      intro z hz
      have hzm : z ∈ Set.Icc a b := hsub (Set.Ioo_subset_Icc_self hz)
      exact ((hdiff z hzm).differentiableAt).differentiableWithinAt
    obtain ⟨c, hcmem, hceq⟩ := exists_deriv_eq_slope f hmb_lt hfc hfd
    have hcIcc : c ∈ Set.Icc a b := hsub (Set.Ioo_subset_Icc_self hcmem)
    have hcu : f' c ≤ u := (Set.mem_Icc.mp (henc c hcIcc)).2
    have hdc : deriv f c = f' c := (hdiff c hcIcc).deriv
    have hfb : f b ≤ f m + u * (b - m) := by
      have e : f b - f m = f' c * (b - m) := by
        have hfp : f' c = (f b - f m) / (b - m) := by
          rw [← hdc]
          exact hceq
        rw [hfp, div_mul_cancel₀ _ (sub_ne_zero.mpr (ne_of_gt hmb_lt))]
      have e2 : f' c * (b - m) ≤ u * (b - m) :=
        mul_le_mul_of_nonneg_right hcu (sub_nonneg.mpr (le_of_lt hmb_lt))
      linarith [e, e2]
    have hfbpos : 0 < f b := hpos b hb_mem
    have hposu : 0 < -u := neg_pos.mpr hu
    have key0 : -u * (b - m) < f m := by linarith [hfb, hfbpos]
    have hdiv : (b - m) < f m / -u :=
      (lt_div_iff₀ hposu).mpr (by linarith [key0])
    have hu0 : u ≠ 0 := ne_of_lt hu
    have hnu0 : -u ≠ 0 := ne_of_gt hposu
    have e4 : f m / u = -(f m / -u) := by
      field_simp
    have hR : b < m - f m / u := by
      rw [e4]
      simp only [sub_neg_eq_add]
      linarith [hdiv]
    exact (not_lt.mpr hRb) hR

/-- Reduction: a negative field inherits the positive impossibility
    results through negation (the Moore operator is invariant). -/
lemma moore_neg_image (a b m : ℝ) (hab : a < b)
    (hm : m ∈ Set.Icc a b) (f f' : ℝ → ℝ)
    (hcont : ContinuousOn f (Set.Icc a b))
    (hdiff : ∀ x ∈ Set.Icc a b, HasDerivAt f (f' x) x)
    (hneg : ∀ x ∈ Set.Icc a b, f x < 0)
    (l u : ℝ)
    (henc : ∀ x ∈ Set.Icc a b, f' x ∈ Set.Icc l u)
    (hD0 : 0 ∉ Set.Icc l u)
    (hN : Set.image (fun d => m - f m / d) (Set.Icc l u)
      ⊆ Set.Icc a b) :
    False := by
  have hpos_g : ∀ x ∈ Set.Icc a b, 0 < -f x :=
    fun x hx => neg_pos.mpr (hneg x hx)
  have hdiff_g : ∀ x ∈ Set.Icc a b,
      HasDerivAt (-f) ((fun x => -f' x) x) x := fun x hx =>
    (hdiff x hx).neg
  have hcont_g : ContinuousOn (-f) (Set.Icc a b) := hcont.neg
  have henc_g : ∀ x ∈ Set.Icc a b, (fun x => -f' x) x ∈ Set.Icc (-u) (-l) := by
    intro x hx
    have hmem := Set.mem_Icc.mp (henc x hx)
    show -f' x ∈ Set.Icc (-u) (-l)
    rw [Set.mem_Icc]
    constructor <;> linarith [hmem.1, hmem.2]
  have hN_g : Set.image (fun d => m - -f m / d) (Set.Icc (-u) (-l))
      ⊆ Set.Icc a b := by
    rw [moore_image_neg_eq]
    exact hN
  by_cases hDpos : 0 < -u
  · exact moore_pos_image_pos a b m hab hm (-f) (fun x => -f' x)
      hcont_g hdiff_g hpos_g (-u) (-l) hDpos henc_g hN_g
  · have h1 : -u ≤ 0 := le_of_not_gt hDpos
    have hD0g : 0 ∉ Set.Icc (-u) (-l) := by
      intro hc
      have hmem := Set.mem_Icc.mp hc
      exact hD0 ⟨by linarith [hmem.2], by linarith [hmem.1]⟩
    have hnl : -l < 0 := by
      have hDpos : 0 < l := by exact hDpos
      linarith
    exact moore_pos_image_neg a b m hab hm (-f) (fun x => -f' x)
      hcont_g hdiff_g hpos_g (-u) (-l) hnl henc_g hN_g

/-- Moore existence test: inclusion plus clean enclosure forces a
    zero (trichotomy over the field sign; each single-signed case
    dies by the endpoint lemmas above). -/
theorem moore_test_existence (a b m : ℝ) (hab : a < b)
    (hm : m ∈ Set.Icc a b) (f f' : ℝ → ℝ)
    (hcont : ContinuousOn f (Set.Icc a b))
    (hdiff : ∀ x ∈ Set.Icc a b, HasDerivAt f (f' x) x)
    (l u : ℝ)
    (henc : ∀ x ∈ Set.Icc a b, f' x ∈ Set.Icc l u)
    (hD0 : 0 ∉ Set.Icc l u)
    (hN : Set.image (fun d => m - f m / d) (Set.Icc l u)
      ⊆ Set.Icc a b) :
    ∃ z ∈ Set.Icc a b, f z = 0 := by
  by_cases hneg : ∀ x ∈ Set.Icc a b, f x < 0
  · exact (moore_neg_image a b m hab hm f f' hcont hdiff hneg l u
      henc hD0 hN).elim
  · push Not at hneg
    obtain ⟨x₁, hx₁, hx1ge⟩ := hneg
    by_cases hpos : ∀ x ∈ Set.Icc a b, 0 < f x
    · by_cases hDpos : 0 < l
      · exact (moore_pos_image_pos a b m hab hm f f' hcont hdiff hpos
          l u hDpos henc hN).elim
      · have hu : u < 0 := by
        by_cases hu : u < 0
        · exact hu
        · -- If u ≥ 0, then 0 ∈ Set.Icc l u (since l > 0 by hDpos and u ≥ 0)
          -- This contradicts hD0 : 0 ∉ Set.Icc l u
          have hu' : u ≥ 0 := by linarith
          have h₁ : (0 : ℝ) ∈ Set.Icc l u := by
            constructor <;> linarith [hDpos]
          exact absurd h₁ hD0
        exact (moore_pos_image_neg a b m hab hm f f' hcont hdiff hpos
          l u hu henc hN).elim
    · push Not at hpos
      obtain ⟨x₀, hx₀, hx0le⟩ := hpos
      exact exists_zero_of_sign_change a b f hcont x₀ hx₀ hx0le
        x₁ hx₁ hx1ge

/-- Moore test, closed form: inclusion plus clean enclosure yields
    exactly one zero (existence + uniqueness combined). This is the
    REAL-INTERVAL analogue of the Python counter's soundness gate,
    not its formal counterpart: `counter.py` counts zeros in COMPLEX
    balls (circular containment, series-enclosed derivative over the
    whole ball), while everything in this file is stated over ℝ
    intervals. The ℂ-to-ℝ transfer is unformalized; counted boxes are
    certified by the ball arithmetic plus the winding cross-check,
    never by this theorem alone. -/
theorem moore_test (a b m : ℝ) (hab : a < b)
    (hm : m ∈ Set.Icc a b) (f f' : ℝ → ℝ)
    (hcont : ContinuousOn f (Set.Icc a b))
    (hdiff : ∀ x ∈ Set.Icc a b, HasDerivAt f (f' x) x)
    (l u : ℝ)
    (henc : ∀ x ∈ Set.Icc a b, f' x ∈ Set.Icc l u)
    (hD0 : 0 ∉ Set.Icc l u)
    (hN : Set.image (fun d => m - f m / d) (Set.Icc l u)
      ⊆ Set.Icc a b) :
    ∃! z ∈ Set.Icc a b, f z = 0 := by
  obtain ⟨z, hzm, hfz⟩ := moore_test_existence a b m hab hm f f'
    hcont hdiff l u henc hD0 hN
  refine ⟨z, ⟨hzm, hfz⟩, ?_⟩
  intro y hy
  obtain ⟨hym, hfy⟩ := hy
  exact moore_unique_of_deriv_exclusion a b f f' hcont hdiff _
    henc hD0 y hym z hzm hfy hfz

end NewtonExistence
