(* ===================================================================== *)
(*  GeometricBridge.v -- algebraic core of the L1 bridge (kit A-2026-0006)

    SCOPE (locked; do not widen without a new pre-registration):

      This file formalises the FINITE algebraic identity behind the
      geometric tail lemma L1 of msaf/bridge.py:

        geom_sum r n           = sum_{k=0}^{n-1} r^k
        geom_sum r n           = (1 - r^n) / (1 - r)        (r <> 1)
        1/(1-r) - geom_sum r n = r^n / (1 - r)              (the tail)
        geom_sum r n           <= 1/(1-r)          (0 <= r < 1)

      It does NOT formalise: infinite sums, limits, convergence, any
      analytic lemma, any statement about zeta/Weil/RH, any physical
      claim. The "total" 1/(1-r) is the classical closed form of the
      infinite geometric series; the inequality is a finite statement
      about partial sums and that closed form, with no limit taken.

    Trusted base: Coq 8.20.1 stdlib. Coq.Reals is axiomatic; the audit
    block at the end prints the assumptions of every exported result.
    No Axiom, Parameter, Admitted or admit appears in this file.
   ===================================================================== *)

Require Import Coq.Reals.Reals.
Require Import Coq.micromega.Lra.
Open Scope R_scope.

(* --------------------------------------------------------------------- *)
(*  Finite geometric partial sum                                          *)
(* --------------------------------------------------------------------- *)

Fixpoint geom_sum (r : R) (n : nat) : R :=
  match n with
  | O    => 0
  | S k  => geom_sum r k + r ^ k
  end.

Lemma geom_pow_nonneg : forall r n, 0 <= r -> 0 <= r ^ n.
Proof.
  intros r n H. induction n as [| n IH].
  - simpl. lra.
  - simpl. apply Rmult_le_pos; assumption.
Qed.

(* Closed form of the finite sum: the [B] block, exact. *)
Lemma geom_sum_mul : forall r n,
  geom_sum r n * (1 - r) = 1 - r ^ n.
Proof.
  intros r n. induction n as [| n IH].
  - simpl. ring.
  - simpl. rewrite Rmult_plus_distr_r. rewrite IH. ring.
Qed.

Lemma geom_sum_formula : forall r n, r <> 1 ->
  geom_sum r n = (1 - r ^ n) / (1 - r).
Proof.
  intros r n Hr.
  assert (H : 1 - r <> 0) by lra.
  rewrite <- geom_sum_mul.
  field. lra.
Qed.

(* --------------------------------------------------------------------- *)
(*  The bridge identity: gap between the closed-form total and the        *)
(*  finite partial sum is exactly the tail term of L1.                    *)
(* --------------------------------------------------------------------- *)

Definition geom_tail (r : R) (n : nat) : R := r ^ n / (1 - r).

Lemma geom_tail_identity : forall r n, r <> 1 ->
  1 / (1 - r) - geom_sum r n = geom_tail r n.
Proof.
  intros r n Hr.
  rewrite geom_sum_formula by assumption.
  unfold geom_tail.
  field.
  lra.
Qed.

Lemma geom_tail_nonneg : forall r n, 0 <= r -> r < 1 -> 0 <= geom_tail r n.
Proof.
  intros r n H0 H1.
  unfold geom_tail.
  apply Rmult_le_pos.
  - apply geom_pow_nonneg; assumption.
  - apply Rlt_le. apply Rinv_0_lt_compat. lra.
Qed.

(* The [B] <= [U] step: finite partial sum bounded by the closed form. *)
Lemma geom_sum_le_total : forall r n, 0 <= r -> r < 1 ->
  geom_sum r n <= 1 / (1 - r).
Proof.
  intros r n H0 H1.
  pose proof (geom_tail_identity r n ltac:(lra)) as Hid.
  pose proof (geom_tail_nonneg r n H0 H1) as Hnn.
  lra.
Qed.

(* --------------------------------------------------------------------- *)
(*  One concrete application, matching the kit demo's exact r = 1/2 case  *)
(* --------------------------------------------------------------------- *)

Lemma geom_sum_half_11 : geom_sum (1 / 2) 11 = 2047 / 1024.
Proof.
  rewrite geom_sum_formula by lra.
  field.
Qed.

Lemma geom_bridge_half_11 :
  1 / (1 - 1 / 2) - geom_sum (1 / 2) 11 = 1 / 1024.
Proof.
  rewrite geom_tail_identity by lra.
  unfold geom_tail.
  field.
Qed.

(* --------------------------------------------------------------------- *)
(*  Audit block: trusted base of every exported result.                   *)
(*  Expected: Coq.Reals axioms only (no project-specific axiom).          *)
(* --------------------------------------------------------------------- *)

(* Every lemma declared above is audited here. The list is checked by
   msaf/tests/test_coq_bridge_pilot.py, which fails if a lemma is added
   without a matching Print Assumptions line (an incomplete audit is a
   failure, not a pass). *)
Print Assumptions geom_pow_nonneg.
Print Assumptions geom_sum_mul.
Print Assumptions geom_sum_formula.
Print Assumptions geom_tail_identity.
Print Assumptions geom_tail_nonneg.
Print Assumptions geom_sum_le_total.
Print Assumptions geom_sum_half_11.
Print Assumptions geom_bridge_half_11.
