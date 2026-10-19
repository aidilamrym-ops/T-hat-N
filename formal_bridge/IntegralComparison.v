(* ===================================================================== *)
(*  IntegralComparison.v -- Paket 7: L5 finite core.                     *)
(*                                                                       *)
(*  Scope locked in reports/PREREG_PAKET7_2026-10-20.md.                 *)
(*                                                                       *)
(*  For f_k(x) = 1 / x^(k+1), k >= 1, and integers 1 <= N, M:            *)
(*                                                                       *)
(*      int_N^(N+M) f_k  <=  sum_{i=0}^{M-1} f_k(N+i)                    *)
(*      sum_{i=0}^{M-1} f_k(N+i+1)  <=  int_N^(N+M) f_k                  *)
(*                                                                       *)
(*  The finite integral is the stdlib Riemann integral (RiemannInt).    *)
(*  This is the finite core of the kit's L5 integral comparison.         *)
(*  The infinite integral, the limit step, general f, real exponents,    *)
(*  L3, L4 and the periodic-box [J] study are OUT OF SCOPE.              *)
(*                                                                       *)
(*  No FTC_Riemann / C1_fun, no Rpower, no project axioms.               *)
(* ===================================================================== *)

Require Import Coq.Reals.Reals.
Require Import Coq.Reals.RiemannInt.
Require Import Coq.Reals.Ranalysis1.
Require Import Coq.Reals.Rfunctions.
Require Import Coq.micromega.Lia.
Require Import Coq.micromega.Lra.

Open Scope R_scope.

(* --------------------------------------------------------------------- *)
(*  Definitions.                                                         *)
(* --------------------------------------------------------------------- *)

Definition fk (k : nat) (x : R) : R := / (x ^ S k).

(* sum_upto g M = g 0 + g 1 + ... + g (M-1), and 0 for M = 0. *)
Fixpoint sum_upto (g : nat -> R) (M : nat) : R :=
  match M with
  | 0%nat => 0
  | S m => sum_upto g m + g m
  end.

(* endN N M = N + M, defined recursively on M so that the split point of
   [N, N+M+1] is definitionally endN N M and the next endpoint is
   definitionally endN N (S M). *)
Fixpoint endN (N M : nat) : nat :=
  match M with
  | 0%nat => N
  | S m => S (endN N m)
  end.

Lemma endN_eq_add :
  forall N M : nat, endN N M = (N + M)%nat.
Proof.
  intros N M.
  induction M as [| M IH].
  - simpl. rewrite Nat.add_0_r. reflexivity.
  - simpl. rewrite IH. rewrite Nat.add_succ_r. reflexivity.
Qed.

Lemma endN_succ_eq :
  forall N M : nat, endN N (S M) = (N + M + 1)%nat.
Proof.
  intros N M.
  rewrite endN_eq_add.
  lia.
Qed.

Lemma le_endN :
  forall N M : nat, (N <= endN N M)%nat.
Proof.
  intros N M.
  induction M as [| M IH].
  - simpl. apply Nat.le_refl.
  - simpl. apply Nat.le_trans with (endN N M).
    + exact IH.
    + apply Nat.le_succ_diag_r.
Qed.

Lemma INR_pos_of_ge1 :
  forall n : nat, (1 <= n)%nat -> 0 < INR n.
Proof.
  intros n Hn.
  apply lt_0_INR.
  lia.
Qed.

(* --------------------------------------------------------------------- *)
(*  Continuity of f_k on positive reals.                                 *)
(* --------------------------------------------------------------------- *)

Lemma continuity_pt_fk :
  forall (k : nat) (x : R), 0 < x -> continuity_pt (fk k) x.
Proof.
  intros k x Hx.
  unfold fk.
  apply continuity_pt_inv.
  - apply derivable_continuous_pt.
    apply derivable_pt_pow.
  - apply Rgt_not_eq.
    apply pow_lt.
    exact Hx.
Qed.

(* Integrability of f_k on [a,b] from continuity on the interval. *)
Definition fk_int (k : nat) (a b : R) (Hab : a <= b)
    (Hpos : forall x : R, a <= x <= b -> 0 < x) :
    Riemann_integrable (fk k) a b :=
  @continuity_implies_RiemannInt (fk k) a b Hab
    (fun x Hx => continuity_pt_fk k x (Hpos x Hx)).

(* The finite integral over one unit interval [endN N i, endN N (S i)]. *)
Definition unit_val (k N i : nat) (HN : (1 <= N)%nat) : R :=
  RiemannInt
    (fk_int k (INR (endN N i)) (INR (endN N (S i)))
       (le_INR (endN N i) (endN N (S i))
          (Nat.le_succ_diag_r (endN N i)))
       (fun x Hx =>
          Rlt_le_trans 0 (INR N) x
            (INR_pos_of_ge1 N HN)
            (Rle_trans (INR N) (INR (endN N i)) x
               (le_INR N (endN N i) (le_endN N i))
               (proj1 Hx)))).

(* The finite integral over [N, endN N M]. *)
Definition whole_val (k N M : nat) (HN : (1 <= N)%nat) : R :=
  RiemannInt
    (fk_int k (INR N) (INR (endN N M))
       (le_INR N (endN N M) (le_endN N M))
       (fun x Hx =>
          Rlt_le_trans 0 (INR N) x
            (INR_pos_of_ge1 N HN)
            (proj1 Hx))).

(* --------------------------------------------------------------------- *)
(*  Finite sums.                                                         *)
(* --------------------------------------------------------------------- *)

Lemma sum_upto_le :
  forall (g h : nat -> R) (M : nat),
    (forall i : nat, (i < M)%nat -> g i <= h i) ->
    sum_upto g M <= sum_upto h M.
Proof.
  intros g h M.
  induction M as [| M IH]; intros H.
  - simpl. apply Rle_refl.
  - simpl. apply Rplus_le_compat.
    + apply IH. intros i Hi. apply H. lia.
    + apply H. lia.
Qed.

Lemma sum_upto_ext :
  forall (g h : nat -> R) (M : nat),
    (forall i : nat, (i < M)%nat -> g i = h i) ->
    sum_upto g M = sum_upto h M.
Proof.
  intros g h M.
  induction M as [| M IH]; intros H.
  - reflexivity.
  - simpl. rewrite IH.
    + rewrite H.
      * reflexivity.
      * lia.
    + intros i Hi. apply H. lia.
Qed.

(* --------------------------------------------------------------------- *)
(*  Degenerate integral and finite additivity.                           *)
(* --------------------------------------------------------------------- *)

Lemma RiemannInt_degenerate :
  forall (f : R -> R) (a : R) (pr : Riemann_integrable f a a),
    RiemannInt pr = 0.
Proof.
  intros f a pr.
  assert (H : RiemannInt pr + RiemannInt pr = RiemannInt pr).
  { apply (@RiemannInt_P25 f a a a pr pr pr); apply Rle_refl. }
  lra.
Qed.

Lemma whole_val_split :
  forall (k N M : nat) (HN : (1 <= N)%nat),
    whole_val k N (S M) HN = whole_val k N M HN + unit_val k N M HN.
Proof.
  intros k N M HN.
  unfold whole_val, unit_val.
  symmetry.
  eapply @RiemannInt_P25.
  - apply le_INR. apply le_endN.
  - apply le_INR. simpl. apply Nat.le_succ_diag_r.
Qed.

Lemma whole_val_eq_sum :
  forall (k N M : nat) (HN : (1 <= N)%nat),
    whole_val k N M HN = sum_upto (fun i => unit_val k N i HN) M.
Proof.
  intros k N M HN.
  induction M as [| M IH].
  - unfold whole_val, sum_upto.
    rewrite RiemannInt_degenerate.
    reflexivity.
  - rewrite whole_val_split.
    rewrite IH.
    simpl.
    reflexivity.
Qed.

(* --------------------------------------------------------------------- *)
(*  Unit-interval comparison: the finite L5 mechanism.                   *)
(* --------------------------------------------------------------------- *)

Lemma INR_endN_length :
  forall N i : nat, INR (endN N (S i)) - INR (endN N i) = 1.
Proof.
  intros N i.
  change (INR (S (endN N i)) - INR (endN N i) = 1).
  rewrite S_INR.
  ring.
Qed.

Lemma integral_unit_upper :
  forall (k N i : nat) (HN : (1 <= N)%nat),
    unit_val k N i HN <= fk k (INR (endN N i)).
Proof.
  intros k N i HN.
  unfold unit_val.
  eapply Rle_trans with
    (r2 := RiemannInt
             (RiemannInt_P14 (INR (endN N i)) (INR (endN N (S i)))
                (fk k (INR (endN N i))))).
  - eapply @RiemannInt_P19.
    + apply le_INR. apply Nat.le_succ_diag_r.
    + intros x Hx.
      unfold fk, fct_cte.
      apply (Rinv_le_contravar ((INR (endN N i)) ^ S k) (x ^ S k)).
      * apply pow_lt.
        apply lt_0_INR.
        apply Nat.lt_le_trans with N.
        -- lia.
        -- apply le_endN.
      * apply pow_incr.
        split.
        -- apply Rlt_le.
           apply lt_0_INR.
           apply Nat.lt_le_trans with N.
           ++ lia.
           ++ apply le_endN.
        -- apply Rlt_le.
           exact (proj1 Hx).
  - rewrite (@RiemannInt_P15 (INR (endN N i)) (INR (endN N (S i)))
               (fk k (INR (endN N i)))
               (RiemannInt_P14 (INR (endN N i)) (INR (endN N (S i)))
                  (fk k (INR (endN N i))))).
    rewrite INR_endN_length.
    rewrite Rmult_1_r.
    apply Rle_refl.
Qed.

Lemma integral_unit_lower :
  forall (k N i : nat) (HN : (1 <= N)%nat),
    fk k (INR (endN N (S i))) <= unit_val k N i HN.
Proof.
  intros k N i HN.
  unfold unit_val.
  eapply Rle_trans with
    (r2 := RiemannInt
             (RiemannInt_P14 (INR (endN N i)) (INR (endN N (S i)))
                (fk k (INR (endN N (S i)))))).
  - rewrite (@RiemannInt_P15 (INR (endN N i)) (INR (endN N (S i)))
               (fk k (INR (endN N (S i))))
               (RiemannInt_P14 (INR (endN N i)) (INR (endN N (S i)))
                  (fk k (INR (endN N (S i)))))).
    rewrite INR_endN_length.
    rewrite Rmult_1_r.
    apply Rle_refl.
  - eapply @RiemannInt_P19.
    + apply le_INR. apply Nat.le_succ_diag_r.
    + intros x Hx.
      unfold fk, fct_cte.
      apply (Rinv_le_contravar (x ^ S k) ((INR (endN N (S i))) ^ S k)).
      * apply pow_lt.
        apply Rlt_trans with (INR (endN N i)).
        -- apply lt_0_INR.
           apply Nat.lt_le_trans with N.
           ++ lia.
           ++ apply le_endN.
        -- exact (proj1 Hx).
      * apply pow_incr.
        split.
        -- apply Rlt_le.
           apply Rlt_trans with (INR (endN N i)).
           ++ apply lt_0_INR.
              apply Nat.lt_le_trans with N.
              ** lia.
              ** apply le_endN.
           ++ exact (proj1 Hx).
        -- apply Rlt_le.
           exact (proj2 Hx).
Qed.

(* --------------------------------------------------------------------- *)
(*  Main finite-core theorem.                                            *)
(* --------------------------------------------------------------------- *)

Theorem integral_comparison_power_finite :
  forall (k N M : nat) (HN : (1 <= N)%nat),
    (1 <= k)%nat ->
    whole_val k N M HN
      <= sum_upto (fun i => fk k (INR (N + i))) M /\
    sum_upto (fun i => fk k (INR (N + i + 1))) M
      <= whole_val k N M HN.
Proof.
  intros k N M HN Hk.
  induction M as [| M IH].
  - simpl.
    unfold whole_val.
    rewrite RiemannInt_degenerate.
    split; apply Rle_refl.
  - rewrite whole_val_split.
    change (whole_val k N M HN + unit_val k N M HN <=
              sum_upto (fun i => fk k (INR (N + i))) M + fk k (INR (N + M)) /\
            sum_upto (fun i => fk k (INR (N + i + 1))) M +
              fk k (INR (N + M + 1)) <=
              whole_val k N M HN + unit_val k N M HN).
    split.
    + apply Rplus_le_compat.
      * exact (proj1 IH).
      * rewrite <- endN_eq_add.
        apply integral_unit_upper.
    + apply Rplus_le_compat.
      * exact (proj2 IH).
      * rewrite <- endN_succ_eq.
        apply integral_unit_lower.
Qed.

(* --------------------------------------------------------------------- *)
(*  Assumption audit.                                                    *)
(* --------------------------------------------------------------------- *)

Print Assumptions endN_eq_add.
Print Assumptions endN_succ_eq.
Print Assumptions le_endN.
Print Assumptions INR_pos_of_ge1.
Print Assumptions continuity_pt_fk.
Print Assumptions sum_upto_le.
Print Assumptions sum_upto_ext.
Print Assumptions RiemannInt_degenerate.
Print Assumptions whole_val_split.
Print Assumptions whole_val_eq_sum.
Print Assumptions INR_endN_length.
Print Assumptions integral_unit_upper.
Print Assumptions integral_unit_lower.
Print Assumptions integral_comparison_power_finite.
