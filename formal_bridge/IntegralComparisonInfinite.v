(* ===================================================================== *)
(*  Paket 9: L5 infinite (unconditional) for f_k(x) = x^(-(k+1)).       *)
(*                                                                       *)
(*  This file closes the pilot L5 statement for f_k by proving that the  *)
(*  three limits used in Paket 8 actually exist:                         *)
(*    - the tail sum limit comes from pseries_L2_integer (A-2026-0010);  *)
(*    - the integral limits come from Un_cv_crit (monotone + bounded);   *)
(*    - Paket 8 then gives the two-sided comparison.                     *)
(*                                                                       *)
(*  Trusted base: the four stdlib axioms inherited from Coq.Reals /      *)
(*  RiemannInt.  No project axioms.                                      *)
(* ===================================================================== *)

Require Import Coq.Reals.Reals.
Require Import Coq.Reals.Rseries.
Require Import Coq.micromega.Lia.
Require Import Coq.micromega.Lra.
Require Import IntegralComparison.
Require Import IntegralComparisonLimit.
Require Import PseriesL2.

(* The tail sum from N+1, with M terms: f(N+1) + ... + f(N+M). *)
Definition tail_sum (k N M : nat) : R :=
  sum_upto (fun i => fk k (INR (N + 1 + i))) M.

(* sum_f_R0 g M and sum_upto g (S M) are the same finite sum. *)
Lemma sum_f_R0_eq_sum_upto :
  forall (g : nat -> R) (M : nat),
    sum_f_R0 g M = sum_upto g (S M).
Proof.
  intros g M.
  induction M as [| M IH].
  - simpl. rewrite Rplus_0_l. reflexivity.
  - simpl. rewrite IH. reflexivity.
Qed.

(* Extensionality for sum_f_R0. *)
Lemma sum_f_R0_ext :
  forall (f g : nat -> R) (M : nat),
    (forall i : nat, (i <= M)%nat -> f i = g i) ->
    sum_f_R0 f M = sum_f_R0 g M.
Proof.
  intros f g M.
  induction M as [| M IH]; intros H.
  - simpl. apply H. lia.
  - simpl. rewrite IH.
    + rewrite (H (S M) (le_n (S M))). reflexivity.
    + intros i Hi. apply H. lia.
Qed.

(* pterm is f_k on the corresponding real point. *)
Lemma pterm_eq_fk :
  forall (k n : nat), pterm k n = fk k (INR n).
Proof.
  intros k n.
  unfold pterm, fk, Rdiv.
  rewrite Rmult_1_l.
  reflexivity.
Qed.

(* psum is the sum_f_R0 form of the f_k tail. *)
Lemma psum_eq_sum_f_R0_fk :
  forall (k N M : nat),
    psum k N M =
      sum_f_R0 (fun i => fk k (INR (N + 1 + i))) M.
Proof.
  intros k N M.
  unfold psum.
  apply sum_f_R0_ext.
  intros i Hi.
  apply pterm_eq_fk.
Qed.

(* psum k N M is the tail sum with one extra term. *)
Lemma psum_eq_tail_sum_succ :
  forall (k N M : nat),
    psum k N M = tail_sum k N (S M).
Proof.
  intros k N M.
  rewrite psum_eq_sum_f_R0_fk.
  unfold tail_sum.
  rewrite sum_f_R0_eq_sum_upto.
  reflexivity.
Qed.

(* Pointwise equality preserves Un_cv. *)
Lemma Un_cv_ext_local :
  forall (u v : nat -> R) (L : R),
    (forall n : nat, u n = v n) ->
    Un_cv u L ->
    Un_cv v L.
Proof.
  intros u v L Heq Hcv eps Heps.
  destruct (Hcv eps Heps) as [N HN].
  exists N. intros n Hn.
  rewrite <- Heq.
  apply HN. exact Hn.
Qed.

(* Dropping the first term preserves a limit. *)
Lemma Un_cv_tail_shift :
  forall (f : nat -> R) (L : R),
    Un_cv (fun M => f (S M)) L ->
    Un_cv f L.
Proof.
  intros f L H eps Heps.
  destruct (H eps Heps) as [N HN].
  exists (S N). intros n Hn.
  destruct n as [| m].
  - exfalso. lia.
  - apply HN. lia.
Qed.

(* A convergent sequence's one-step shift is convergent. *)
Lemma Un_cv_shift_succ :
  forall (f : nat -> R) (L : R),
    Un_cv f L ->
    Un_cv (fun M => f (S M)) L.
Proof.
  intros f L H eps Heps.
  destruct (H eps Heps) as [N HN].
  exists N. intros n Hn.
  apply HN. lia.
Qed.

(* The tail sum converges, by transporting the p-series limit. *)
Lemma tail_sum_cv :
  forall (k N : nat),
    (1 <= k)%nat -> (1 <= N)%nat ->
    exists L : R, Un_cv (fun M => tail_sum k N M) L.
Proof.
  intros k N Hk HN.
  destruct (pseries_L2_integer k N Hk HN) as [L [Hcv _]].
  exists L.
  apply Un_cv_tail_shift.
  eapply Un_cv_ext_local with (u := fun M => psum k N M).
  - intros M. apply psum_eq_tail_sum_succ.
  - exact Hcv.
Qed.

(* Positivity of f_k at integer points >= 1. *)
Lemma fk_nonneg :
  forall (k n : nat),
    (1 <= n)%nat -> 0 <= fk k (INR n).
Proof.
  intros k n Hn.
  unfold fk.
  apply Rlt_le.
  apply Rinv_0_lt_compat.
  apply pow_lt.
  apply lt_0_INR.
  lia.
Qed.

(* The integral over one unit interval is nonnegative. *)
Lemma unit_val_nonneg :
  forall (k N i : nat) (HN : (1 <= N)%nat),
    0 <= unit_val k N i HN.
Proof.
  intros k N i HN.
  eapply Rle_trans with (r2 := fk k (INR (endN N (S i)))).
  - apply Rlt_le.
    unfold fk.
    apply Rinv_0_lt_compat.
    apply pow_lt.
    apply lt_0_INR.
    pose proof (le_endN N (S i)).
    lia.
  - apply integral_unit_lower.
Qed.

(* The finite integral is monotone in the upper endpoint. *)
Lemma whole_val_growing :
  forall (k N : nat) (HN : (1 <= N)%nat),
    Un_growing (fun M => whole_val k N M HN).
Proof.
  intros k N HN M.
  rewrite whole_val_split.
  pose proof (unit_val_nonneg k N M HN).
  lra.
Qed.

(* The upper finite sum is f_k(N) plus the tail sum. *)
Lemma upper_sum_succ :
  forall (k N m : nat),
    sum_upto (fun i => fk k (INR (N + i))) (S m)
      = fk k (INR N) + tail_sum k N m.
Proof.
  intros k N m.
  induction m as [| m IH].
  - simpl. unfold tail_sum. simpl. rewrite Nat.add_0_r. lra.
  - change (sum_upto (fun i => fk k (INR (N + i))) (S m)
              + fk k (INR (N + S m))
            = fk k (INR N) + tail_sum k N (S m)).
    rewrite IH.
    replace (N + S m)%nat with (N + 1 + m)%nat by lia.
    unfold tail_sum. simpl. lra.
Qed.

(* A uniform bound on the upper finite sum, from the tail-sum limit. *)
Lemma upper_sum_bound :
  forall (k N : nat) (L : R),
    (1 <= k)%nat -> (1 <= N)%nat ->
    Un_cv (fun M => tail_sum k N M) L ->
    forall M : nat,
      sum_upto (fun i => fk k (INR (N + i))) M
        <= fk k (INR N) + L.
Proof.
  intros k N L Hk HN Htail M.
  assert (Hpsi :
    Un_cv
      (fun M => sum_f_R0 (fun i => fk k (INR (N + 1 + i))) M) L).
  { eapply Un_cv_ext_local.
    - intros m. symmetry. apply sum_f_R0_eq_sum_upto.
    - apply Un_cv_shift_succ. exact Htail. }
  assert (HAn : forall i : nat, 0 <= fk k (INR (N + 1 + i))).
  { intros i. apply fk_nonneg. lia. }
  assert (HL0 : 0 <= L).
  { eapply Rle_trans.
    - apply (HAn 0%nat).
    - apply (sum_incr (fun i => fk k (INR (N + 1 + i))) 0%nat L Hpsi HAn). }
  destruct M as [| m].
  - simpl.
    pose proof (fk_nonneg k N HN).
    lra.
  - rewrite upper_sum_succ.
    apply Rplus_le_compat_l.
    destruct m as [| m].
    + simpl. exact HL0.
    + change
        (sum_upto (fun i => fk k (INR (N + 1 + i))) (S m) <= L).
      rewrite <- sum_f_R0_eq_sum_upto.
      apply (sum_incr (fun i => fk k (INR (N + 1 + i))) m L Hpsi HAn).
Qed.

(* The finite integral is bounded by f_k(N) + tail-sum limit. *)
Lemma whole_val_bound :
  forall (k N : nat) (HN : (1 <= N)%nat) (L : R),
    (1 <= k)%nat ->
    Un_cv (fun M => tail_sum k N M) L ->
    forall M : nat,
      whole_val k N M HN <= fk k (INR N) + L.
Proof.
  intros k N HN L Hk Htail M.
  eapply Rle_trans.
  - apply (proj1 (integral_comparison_power_finite k N M HN Hk)).
  - apply upper_sum_bound; auto.
Qed.

(* The finite integral converges, by monotone bounded convergence. *)
Lemma whole_val_cv :
  forall (k N : nat) (HN : (1 <= N)%nat),
    (1 <= k)%nat ->
    exists L : R, Un_cv (fun M => whole_val k N M HN) L.
Proof.
  intros k N HN Hk.
  destruct (tail_sum_cv k N Hk HN) as [L Htail].
  assert (Hgrow : Un_growing (fun M => whole_val k N M HN)).
  { apply whole_val_growing. }
  assert (Hbound : bound (EUn (fun M => whole_val k N M HN))).
  { exists (fk k (INR N) + L).
    intros x Hx.
    destruct Hx as [M HM].
    rewrite HM.
    apply whole_val_bound; auto. }
  exact (Un_cv_crit _ Hgrow Hbound).
Qed.

(* Unconditional L5 for f_k: all three limits exist and satisfy the
   two-sided comparison. *)
Theorem integral_comparison_power_infinite :
  forall (k N : nat) (HN : (1 <= N)%nat),
    (1 <= k)%nat ->
    exists L_N L_N1 L_S : R,
      Un_cv (fun M => whole_val k N M HN) L_N /\
      Un_cv (fun M => whole_val k (N + 1) M (HN_succ N HN)) L_N1 /\
      Un_cv (fun M => tail_sum k N M) L_S /\
      L_N1 <= L_S /\ L_S <= L_N.
Proof.
  intros k N HN Hk.
  destruct (whole_val_cv k N HN Hk) as [L_N H_N].
  destruct (whole_val_cv k (N + 1) (HN_succ N HN) Hk) as [L_N1 H_N1].
  destruct (tail_sum_cv k N Hk HN) as [L_S H_S].
  exists L_N, L_N1, L_S.
  split; [exact H_N | split; [exact H_N1 | split; [exact H_S |]]].
  apply (integral_comparison_power_limit
           k N HN Hk L_N L_N1 L_S H_N H_N1 H_S).
Qed.

Print Assumptions sum_f_R0_eq_sum_upto.
Print Assumptions sum_f_R0_ext.
Print Assumptions pterm_eq_fk.
Print Assumptions psum_eq_sum_f_R0_fk.
Print Assumptions psum_eq_tail_sum_succ.
Print Assumptions Un_cv_ext_local.
Print Assumptions Un_cv_tail_shift.
Print Assumptions Un_cv_shift_succ.
Print Assumptions tail_sum_cv.
Print Assumptions fk_nonneg.
Print Assumptions unit_val_nonneg.
Print Assumptions whole_val_growing.
Print Assumptions upper_sum_succ.
Print Assumptions upper_sum_bound.
Print Assumptions whole_val_bound.
Print Assumptions whole_val_cv.
Print Assumptions integral_comparison_power_infinite.
