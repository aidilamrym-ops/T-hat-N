import ComplexMoore
import XiNoRealZero

/-! Axiom footprint for the widening lemmas. All five are expected to
depend on the three standard axioms and nothing else -- the Minkowski
budget results are elementary interval arithmetic, and a widening lemma
that needed an analytic input would be a warning sign. -/

#print axioms ComplexMoore.widen_contains
#print axioms ComplexMoore.zero_excluded_iff_budget
#print axioms ComplexMoore.widen_loses_zero_above_budget
#print axioms ComplexMoore.derivative_exclusion_survives_budget
#print axioms ComplexMoore.offaxis_ball_avoids_axis
