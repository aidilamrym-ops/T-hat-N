(* ===================================================================== *)
(*  Paket 8: L5 limit step (conditional) for f_k(x) = x^(-(k+1)).       *)
(*                                                                       *)
(*  This file imports the sealed Paket 7 finite-core module              *)
(*  (IntegralComparison.v, registry A-2026-0012) and proves the limit    *)
(*  comparison under explicit Un_cv hypotheses.  It does NOT prove that  *)
(*  the limits exist; that is Paket 9.                                   *)
(*                                                                       *)
(*  Trusted base: the four stdlib axioms inherited from Coq.Reals /      *)
(*  RiemannInt.  No project axioms.                                      *)
(* ===================================================================== *)

Require Import Coq.Reals.Reals.
Require Import Coq.Reals.Rseries.
Require Import Coq.micromega.Lia.
Require Import Coq.micromega.Lra.
Require Import IntegralComparison.

(* 1 <= N+1 from 1 <= N. *)
Definition HN_succ (N : nat) (HN : (1 <= N)%nat) : (1 <= N + 1)%nat :=
  Nat.le_trans 1%nat N (N + 1)%nat HN (Nat.le_add_r N 1).

(* If u_n <= v_n for every n and both sequences converge, then
   lim u <= lim v.  The stdlib fragment has no order-limit lemma. *)
Lemma Un_cv_le :
  forall (u v : nat -> R) (lu lv : R),
    Un_cv u lu ->
    Un_cv v lv ->
    (forall n : nat, u n <= v n) ->
    lu <= lv.
Proof.
  intros u v lu lv Hu Hv Hle.
  apply Rnot_lt_le.
  intros Hlt.
  remember ((lu - lv) / 2) as eps eqn:Heps_def.
  assert (Heps : 0 < eps) by lra.
  destruct (Hu eps Heps) as [Nu HNu].
  destruct (Hv eps Heps) as [Nv HvN].
  set (N := Nat.max Nu Nv).
  assert (HNuN : (N >= Nu)%nat) by (subst N; apply Nat.le_max_l).
  assert (HvNN : (N >= Nv)%nat) by (subst N; apply Nat.le_max_r).
  specialize (HNu N HNuN).
  specialize (HvN N HvNN).
  unfold Rdist in HNu, HvN.
  apply Rabs_def2 in HNu.
  apply Rabs_def2 in HvN.
  destruct HNu as [HNu1 HNu2].
  destruct HvN as [HvN1 HvN2].
  assert (H1 : (lu + lv) / 2 < u N) by lra.
  assert (H2 : v N < (lu + lv) / 2) by lra.
  assert (H3 : u N <= v N) by apply Hle.
  lra.
Qed.

(* The tail sum from N+1 is bounded above by the integral from N. *)
Lemma tail_sum_le_whole :
  forall (k N M : nat) (HN : (1 <= N)%nat),
    (1 <= k)%nat ->
    sum_upto (fun i => fk k (INR (N + 1 + i))) M
      <= whole_val k N M HN.
Proof.
  intros k N M HN Hk.
  rewrite (sum_upto_ext
             (fun i => fk k (INR (N + 1 + i)))
             (fun i => fk k (INR (N + i + 1))) M).
  - apply (proj2 (integral_comparison_power_finite k N M HN Hk)).
  - intros i Hi. f_equal. f_equal. lia.
Qed.

(* The integral from N+1 is bounded above by the same tail sum. *)
Lemma whole_succ_le_tail_sum :
  forall (k N M : nat) (HN : (1 <= N)%nat),
    (1 <= k)%nat ->
    whole_val k (N + 1) M (HN_succ N HN)
      <= sum_upto (fun i => fk k (INR (N + 1 + i))) M.
Proof.
  intros k N M HN Hk.
  apply (proj1 (integral_comparison_power_finite
                 k (N + 1) M (HN_succ N HN) Hk)).
Qed.

(* Conditional L5 limit comparison. *)
Theorem integral_comparison_power_limit :
  forall (k N : nat) (HN : (1 <= N)%nat) (Hk : (1 <= k)%nat)
         (L_N L_N1 L_S : R),
    Un_cv (fun M => whole_val k N M HN) L_N ->
    Un_cv (fun M => whole_val k (N + 1) M (HN_succ N HN)) L_N1 ->
    Un_cv (fun M => sum_upto (fun i => fk k (INR (N + 1 + i))) M) L_S ->
    L_N1 <= L_S /\ L_S <= L_N.
Proof.
  intros k N HN Hk L_N L_N1 L_S H_N H_N1 H_S.
  split.
  - eapply Un_cv_le.
    + exact H_N1.
    + exact H_S.
    + intros M. apply whole_succ_le_tail_sum; assumption.
  - eapply Un_cv_le.
    + exact H_S.
    + exact H_N.
    + intros M. apply tail_sum_le_whole; assumption.
Qed.

Print Assumptions Un_cv_le.
Print Assumptions tail_sum_le_whole.
Print Assumptions whole_succ_le_tail_sum.
Print Assumptions integral_comparison_power_limit.
