import Mathlib.Analysis.Calculus.MeanValue
import Mathlib.Tactic

open scoped BigOperators NNReal

/-! # Interval-Newton existence (Moore box theorem, proved).

`moore_box`: a Newton map preserving a closed interval and globally
Lipschitz below one has exactly one zero there (Banach fixed point +
fixed-point-is-zero). This is the machine-checked counterpart of the
Python counter's strict-existence gate (`msaf/riemann/counter.py`):
containment + clean derivative + contraction ⟹ existence+uniqueness.

Explicit hypotheses (the analytic inputs, as in the hydrodynamic
kernel): clean derivative, invariance, Lipschitz bound. Deriving the
Lipschitz bound from a derivative bound via the mean value theorem is
explicit future work, not claimed.
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
    by_contra hfz
    have h1 : f x / f' x ≠ 0 := div_ne_zero hfz hne
    have h0 : f x / f' x = 0 := by linarith [h]
    exact h1 h0
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

end NewtonExistence
