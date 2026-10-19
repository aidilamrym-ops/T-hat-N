(* ===================================================================== *)
(*  PseriesL2Bounds.v -- Paket 6b: conditional two-axiom L2 bounds.      *)
(*
    Imports the frozen PseriesL2.v (A-2026-0010) WITHOUT modifying it.

    Statement (locked in reports/PREREG_PAKET6B_2026-10-20.md):
    if the p-series tail limit L exists (Un_cv hypothesis), then the
    two-sided bound of the kit's L2 holds for integer p = k+1 >= 2.

    Purpose: isolate the third stdlib axiom of A-2026-0010
    (ClassicalDedekindReals.sig_not_dec, entering through Un_cv_crit /
    completeness of R) to the EXISTENCE step only.  The conditional
    bounds here must rest on the same two stdlib axioms as the other 19
    results of A-2026-0010.

    This file must NOT use pseries_L2_integer and must NOT use Un_cv_crit.
    Real p > 1, L3, L4, L5 and the periodic-box study are OUT OF SCOPE.
   ===================================================================== *)

Require Import Coq.Reals.Reals.
Require Import Coq.Reals.Rseries.
Require Import Coq.micromega.Lia.
Require Import Coq.micromega.Lra.
Require Import PseriesL2.

Open Scope R_scope.

(* --------------------------------------------------------------------- *)
(*  Conditional bounds: Un_cv hypothesis in, two-sided bound out.        *)
(* --------------------------------------------------------------------- *)

Theorem pseries_L2_integer_bounds :
  forall (k N : nat) (L : R),
    (1 <= k)%nat -> (1 <= N)%nat ->
    Un_cv (fun M => psum k N M) L ->
    (1 / (INR k * (INR ((N + 1)%nat)) ^ k) <= L) /\
    (L <= 1 / (INR k * (INR N) ^ k)).
Proof.
  intros k N L Hk HN Hcv. split.
  - set (a := 1 / (INR k * (INR ((N + 1)%nat)) ^ k)).
    apply Rnot_lt_le. intros Hlt.
    set (eps := a - L).
    assert (Heps : 0 < eps)
      by (change (0 < a - L); apply lt_sub_pos; exact Hlt).
    destruct (tail_term_small k N Hk HN eps Heps) as [M HM].
    set (z := (1 / INR k) * (1 / (INR ((N + M + 2)%nat)) ^ k)).
    assert (Hz : z < eps) by exact HM.
    assert (Hfin : a - z <= psum k N M).
    { change (1 / (INR k * (INR ((N + 1)%nat)) ^ k) -
              (1 / INR k) * (1 / (INR ((N + M + 2)%nat)) ^ k)
              <= psum k N M).
      eapply Rle_trans with
        (r2 := (1 / INR k) *
                 (1 / (INR ((N + 1)%nat)) ^ k -
                  1 / (INR ((N + M + 2)%nat)) ^ k)).
      - assert (Hk0 : INR k <> 0) by (apply Rgt_not_eq, lt_0_INR; lia).
        assert (H10 : INR ((N + 1)%nat) <> 0)
          by (apply Rgt_not_eq, lt_0_INR; lia).
        assert (H20 : INR ((N + M + 2)%nat) <> 0)
          by (apply Rgt_not_eq, lt_0_INR; lia).
        replace (1 / (INR k * (INR ((N + 1)%nat)) ^ k) -
                   (1 / INR k) * (1 / (INR ((N + M + 2)%nat)) ^ k))
          with ((1 / INR k) *
                  (1 / (INR ((N + 1)%nat)) ^ k -
                   1 / (INR ((N + M + 2)%nat)) ^ k))
          by (field; repeat split; try (apply pow_nonzero); auto).
        apply Rle_refl.
      - apply psum_lower_sharp; auto. }
    assert (Hpartial : psum k N M <= L).
    { unfold psum.
      eapply sum_incr.
      - change (Un_cv
                  (fun n => sum_f_R0 (fun i => pterm k (N + 1 + i)) n) L).
        exact Hcv.
      - intros i. apply pterm_nonneg. lia. }
    assert (HaL' : a - z <= L)
      by (eapply Rle_trans; [exact Hfin | exact Hpartial]).
    change (z < a - L) in Hz.
    assert (Hzle : a - L <= z) by (apply sub_le_swap; exact HaL').
    assert (Habs : z < z) by (eapply Rlt_le_trans; [exact Hz | exact Hzle]).
    exact (Rlt_irrefl z Habs).
  - eapply Un_cv_le_const.
    + exact Hcv.
    + intros M. apply psum_upper; auto.
Qed.

(* --------------------------------------------------------------------- *)
(*  Assumption audit: the conditional bounds must rest only on the two   *)
(*  stdlib axioms shared by the other 19 results of A-2026-0010.         *)
(* --------------------------------------------------------------------- *)

Print Assumptions pseries_L2_integer_bounds.
