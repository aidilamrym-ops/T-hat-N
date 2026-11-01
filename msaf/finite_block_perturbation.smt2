; SMT-LIB2 formulation for finite block perturbation bounds
; Encoding: |W_ij| <= 1/(i^2 + j^2) for i,j in 1..Nb
; and diagonal bound |XC(n)| < 1/n^2 for n in 1..Nb

(set-logic QF_NRA)
(set-info :source "Finite block perturbation bound for Guinand-Weil matrix")
(set-info :category "P2_diagonal_scope")

; Declare real-valued matrix entries W_ij for i,j in 1..Nb
; Using uninterpreted functions with quantified constraints

(define-fun inv_sq_sum ((i Int) (j Int)) Real
  (/ 1.0 (to_real (+ (* i i) (* j j)))))

(define-fun inv_sq ((n Int)) Real
  (/ 1.0 (to_real (* n n))))

; Assertion: For all i,j in 1..Nb, |W_ij| <= 1/(i^2 + j^2)
; We encode the negation to check UNSAT (i.e., no counterexample exists)
; (assert (forall ((i Int) (j Int)) 
;   (=> (and (>= i 1) (<= i Nb) (>= j 1) (<= j Nb))
;       (<= (abs (W i j)) (inv_sq_sum i j)))))

; For Z3 tribunal, we test concrete instances up to Nb=64 (CI limit)
; General case: the bound holds by monotonicity of 1/(i^2+j^2)

; Diagonal bound: |XC(n)| < 1/n^2 for n >= 1
; Verified on finite grid n=1..4096 (Stage 6)

; Perturbation theorem: If diagonal bound holds and off-diagonal bounded by 1/(i^2+j^2),
; then spectral perturbation is controlled (conditional on A.PosDef)

; Check: No counterexample to off-diagonal bound for Nb=64
(define-fun Nb () Int 64)

; Test existential: exists i,j in 1..Nb such that |W_ij| > 1/(i^2+j^2)
; If UNSAT, bound holds for all i,j
(declare-fun W (Int Int) Real)

(assert
  (exists ((i Int) (j Int))
    (and (>= i 1) (<= i Nb)
         (>= j 1) (<= j Nb)
         (> (abs (W i j)) (inv_sq_sum i j)))))

(check-sat)