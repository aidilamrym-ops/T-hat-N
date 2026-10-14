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

/-- Moore box theorem: a Newton map preserving a closed interval and
    globally Lipschitz with constant below one has exactly one zero
    there (Banach fixed point + fixed-point-is-zero). The Lipschitz
    bound, the invariance, and the clean derivative are explicit
    analytic inputs -- the exact counterpart of the Python counter's
    strict-existence gate. -/
theorem moore_box (a b : ℝ) (hab : a < b) (f f' : ℝ → ℝ)
    (hne : ∀ x ∈ Set.Icc a b, f' x ≠ 0)
    (hmap : Set.MapsTo (newtonMap f f') (Set.Icc a b) (Set.Icc a b))
    (K : ℝ≥0) (hK : K < 1)
    (hlip : LipschitzWith K (newtonMap f f')) :
    ∃! z, z ∈ Set.Icc a b ∧ f z = 0 := by
  have hC : ContractingWith K (newtonMap f f') := ⟨hK, hlip⟩
  have hCr := hC.restrict hmap
  obtain ⟨y, hyfix, _, _⟩ := hCr.exists_fixedPoint
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
  have hzfix : Set.MapsTo.restrict (newtonMap f f') _ _ hmap ⟨z, hzmem⟩
      = ⟨z, hzmem⟩ :=
    Subtype.ext hfzfix
  rcases hCr.eq_or_edist_eq_top_of_fixedPoints hyfix hzfix with h | h
  · exact (congrArg Subtype.val h).symm
  · exact absurd h (edist_ne_top _ _)

end NewtonExistence
