(* ===================================================================== *)
(*  GeometricLimit.v -- closing the ANALYTIC side of [J] for the
    geometric bridge (companion to GeometricBridge.v, A-2026-0008).

    SCOPE (locked; do not widen without a new pre-registration):

      GeometricBridge.v proved the FINITE algebraic identity:
        1/(1-r) - geom_sum r n = r^n/(1-r)
      but left the limit step OPEN. This file takes that step for the
      geometric case only:

        Un_cv (fun n => geom_sum r n) (1/(1-r))     for 0 <= r < 1

      i.e. the partial sums converge, in Coq's epsilon-N sense
      (Coq.Reals.Rseries.Un_cv, Rdist), to the closed form. The tail
      r^n/(1-r) is the explicit error term, and pow_lt_1_zero turns it
      into the epsilon-N witness.

    It does NOT formalise: any other series, any other bridge, the
    periodic-box bridge ([J] there stays OPEN), zeta/Weil/RH, P != NP,
    or any physical claim. GeometricBridge.v is imported unchanged; this
    file adds no axiom and redefines nothing.

    Trusted base: Coq 8.20.1 stdlib. Coq.Reals is axiomatic; the audit
    block at the end prints the assumptions of every exported result.
   ===================================================================== *)

Require Import Coq.Reals.Reals.
Require Import Coq.Reals.Rseries.
Require Import Coq.micromega.Lra.
Require Import GeometricBridge.
Open Scope R_scope.

(* --------------------------------------------------------------------- *)
(*  The tail term IS the distance to the closed form.                     *)
(* --------------------------------------------------------------------- *)

Lemma geom_dist_eq_tail : forall r n, 0 <= r -> r < 1 ->
  Rdist (geom_sum r n) (1 / (1 - r)) = geom_tail r n.
Proof.
  intros r n H0 H1.
  unfold Rdist.
  replace (geom_sum r n - 1 / (1 - r))
    with (- (1 / (1 - r) - geom_sum r n)) by ring.
  rewrite Rabs_Ropp.
  rewrite (geom_tail_identity r n ltac:(lra)).
  apply Rabs_right. apply Rle_ge.
  apply geom_tail_nonneg; assumption.
Qed.

(* --------------------------------------------------------------------- *)
(*  The epsilon-N limit: the analytic half of [J], geometric case.        *)
(* --------------------------------------------------------------------- *)

Theorem geom_sum_cv : forall r, 0 <= r -> r < 1 ->
  Un_cv (fun n => geom_sum r n) (1 / (1 - r)).
Proof.
  intros r H0 H1 eps Heps.
  assert (Hpos : 0 < 1 - r) by lra.
  assert (Habs : Rabs r < 1) by
    (rewrite Rabs_right by lra; lra).
  assert (Hy : 0 < eps * (1 - r)) by
    (apply Rmult_lt_0_compat; lra).
  destruct (pow_lt_1_zero r Habs (eps * (1 - r)) Hy) as [N HN].
  exists N. intros n Hn.
  rewrite geom_dist_eq_tail by assumption.
  unfold geom_tail.
  apply Rmult_lt_reg_r with (r := 1 - r).
  - exact Hpos.
  - replace (r ^ n / (1 - r) * (1 - r)) with (r ^ n).
    2: { field. lra. }
    destruct (Rabs_def2 (r ^ n) (eps * (1 - r)) (HN n Hn)) as [Hlt _].
    exact Hlt.
Qed.

(* --------------------------------------------------------------------- *)
(*  Concrete instance, matching the kit demo's exact r = 1/2 case.       *)
(* --------------------------------------------------------------------- *)

Corollary geom_sum_cv_half :
  Un_cv (fun n => geom_sum (1 / 2) n) (1 / (1 - 1 / 2)).
Proof.
  apply geom_sum_cv; lra.
Qed.

(* The closed form at r = 1/2 is 2; stated separately so the numeral 2
   cannot collide with the 2 inside 1/2 during rewriting. *)
Remark geom_half_limit_value : 1 / (1 - 1 / 2) = 2.
Proof. field. Qed.

(* A concrete epsilon witness: at n = 11 the distance is 1/1024. *)
Lemma geom_half_dist_11 :
  Rdist (geom_sum (1 / 2) 11) (1 / (1 - 1 / 2)) = 1 / 1024.
Proof.
  rewrite geom_dist_eq_tail by lra.
  unfold geom_tail.
  field.
Qed.

(* And that witness is already below eps = 1/100. *)
Lemma geom_half_dist_11_lt :
  Rdist (geom_sum (1 / 2) 11) (1 / (1 - 1 / 2)) < 1 / 100.
Proof.
  rewrite geom_half_dist_11. lra.
Qed.

(* --------------------------------------------------------------------- *)
(*  Audit block: trusted base of every exported result.                   *)
(*  The list is checked by msaf/tests/test_coq_bridge_limit.py, which     *)
(*  fails if a result is added without a matching Print Assumptions.      *)
(* --------------------------------------------------------------------- *)

Print Assumptions geom_dist_eq_tail.
Print Assumptions geom_sum_cv.
Print Assumptions geom_sum_cv_half.
Print Assumptions geom_half_limit_value.
Print Assumptions geom_half_dist_11.
Print Assumptions geom_half_dist_11_lt.
