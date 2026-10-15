import XiNoRealZero

/-! Axiom footprint probe.

`#print axioms` is the only honest way to read a Lean result: it lists
every non-Mathlib assumption a theorem rests on. Section 1 of
XiNoRealZero is expected to show the three standard axioms and nothing
else; `xi_pos_on_reals` is expected to list the six declared analytic
obligations ON TOP of them, which is the price of writing it before
Mathlib has an analytic zeta. -/

#print axioms XiNoRealZero.realCertificate_of_realSlice_zero
#print axioms XiNoRealZero.offAxisPoint_is_not_a_certificate
#print axioms XiNoRealZero.no_realCertificate_of_no_real_zero
#print axioms XiNoRealZero.moore_test_inapplicable_without_real_zero
#print axioms XiNoRealZero.xi_pos_gt_one
#print axioms XiNoRealZero.xi_pos_on_reals
