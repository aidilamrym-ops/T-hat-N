(* ===================================================================== *)
(*  PseriesL2.v -- L2 for INTEGER exponent (p = k+1, k >= 1), two-sided.  *)
(*
    Scope (locked in reports/PREREG_PAKET6_2026-10-19.md):
    for every k >= 1 and N >= 1,
      exists L,
        Un_cv (fun M => sum_{i=0..M} 1/(N+1+i)^(k+1)) L
        /\ 1/(k (N+1)^k) <= L <= 1/(k N^k).
    This is the kit's L2 p-series two-sided bound (msaf/bridge.py) for
    integer p >= 2 only. Real p > 1, L3, L4, L5, the periodic-box study
    and every external claim are OUT OF SCOPE.
*
    Method: Bernoulli (integer) -> upper/lower step inequalities ->
    finite telescoping -> Un_cv_crit -> order-limit lemmas.
*
    Trusted base: Coq 8.20.1 stdlib; Coq.Reals is axiomatic. The audit
    block at the end prints the assumptions of every exported result.
   ===================================================================== *)

Require Import Coq.Reals.Reals.
Require Import Coq.Reals.Rseries.
Require Import Coq.micromega.Lia.
Require Import Coq.micromega.Lra.
Open Scope R_scope.

(* --------------------------------------------------------------------- *)
(*  Bernoulli for integer exponent, valid on [-1, +inf).                  *)
(* --------------------------------------------------------------------- *)

Lemma bernoulli_int :
  forall (x : R) (n : nat), -1 <= x -> 1 + INR n * x <= (1 + x) ^ n.
Proof.
  intros x n Hx.
  induction n as [| n IH].
  - simpl. lra.
  - change (1 + INR (S n) * x <= (1 + x) * (1 + x) ^ n).
    rewrite S_INR.
    eapply Rle_trans with (r2 := (1 + x) * (1 + INR n * x)).
    + pose proof (pos_INR n) as Hn. nra.
    + apply Rmult_le_compat_l; [lra | exact IH].
Qed.

(* --------------------------------------------------------------------- *)
(*  x >= 1 implies x <= x^n for n >= 1 (used for the lower-limit tail).   *)
(* --------------------------------------------------------------------- *)

Lemma one_le_pow : forall (x : R) (n : nat), 1 <= x -> 1 <= x ^ n.
Proof.
  intros x n Hx.
  induction n as [| n IH].
  - simpl. lra.
  - simpl.
    replace 1 with (1 * 1) by ring.
    apply Rmult_le_compat; [lra | lra | exact Hx | exact IH].
Qed.

Lemma pow_ge_self :
  forall (x : R) (n : nat), 1 <= x -> (1 <= n)%nat -> x <= x ^ n.
Proof.
  intros x n Hx Hn.
  destruct n as [| m]; [lia|].
  destruct m as [| m].
  - simpl. rewrite Rmult_1_r. apply Rle_refl.
  - simpl.
    eapply Rle_trans with (r2 := x * 1).
    + rewrite Rmult_1_r. apply Rle_refl.
    + apply Rmult_le_compat_l; [lra | exact (one_le_pow x (S m) Hx)].
Qed.

(* --------------------------------------------------------------------- *)
(*  Helper: a nonzero number times a nonzero power is nonzero.            *)
(* --------------------------------------------------------------------- *)

Lemma prod_pow_neq_0 : forall (a b : R) (k : nat),
  a <> 0 -> b <> 0 -> a * b ^ k <> 0.
Proof.
  intros a b k Ha Hb H.
  apply Rmult_integral in H. destruct H as [H | H].
  - exact (Ha H).
  - exact (pow_nonzero b k Hb H).
Qed.

(* --------------------------------------------------------------------- *)
(*  Upper step: 1/(S m)^(k+1) <= (1/k)(1/m^k - 1/(S m)^k), m >= 1.        *)
(* --------------------------------------------------------------------- *)

Lemma pterm_upper_step :
  forall (k m : nat), (1 <= k)%nat -> (1 <= m)%nat ->
    1 / (INR (S m)) ^ (S k)
      <= (1 / INR k) *
         (1 / (INR m) ^ k - 1 / (INR (S m)) ^ k).
Proof.
  intros k m Hk Hm.
  set (A := INR m).
  set (B := INR (S m)).
  assert (HA : 0 < A) by (subst A; apply lt_0_INR; lia).
  assert (HB : 0 < B) by (subst B; apply lt_0_INR; lia).
  assert (HK : 0 < INR k) by (apply lt_0_INR; lia).
  assert (HAB : B = A + 1) by (subst A; subst B; rewrite S_INR; ring).
  assert (HApow : A ^ (S k) = A * A ^ k) by reflexivity.
  assert (HBpow : B ^ (S k) = B * B ^ k) by reflexivity.
  assert (Hbern : 1 + INR (S k) * (1 / A) <= (1 + 1 / A) ^ (S k)).
  { apply bernoulli_int.
    assert (Hinv : 0 < 1 / A).
    { unfold Rdiv. rewrite Rmult_1_l. apply Rinv_0_lt_compat. lra. }
    lra. }
  rewrite S_INR in Hbern.
  assert (Hkey : (B + INR k) * A ^ k <= B ^ (S k)).
  { assert (Hmul : A ^ (S k) * (1 + (INR k + 1) * (1 / A))
                   <= A ^ (S k) * (1 + 1 / A) ^ (S k)).
    { apply Rmult_le_compat_l.
      - apply Rlt_le, pow_lt. exact HA.
      - exact Hbern. }
    rewrite <- (Rpow_mult_distr A (1 + 1 / A) (S k)) in Hmul.
    replace (A * (1 + 1 / A)) with B in Hmul
      by (rewrite HAB; field; lra).
    rewrite HApow in Hmul.
    replace (A * A ^ k * (1 + (INR k + 1) * (1 / A)))
      with ((B + INR k) * A ^ k) in Hmul
      by (rewrite HAB; field; try (apply pow_nonzero); lra).
    exact Hmul. }
  rewrite HBpow in Hkey.
  rewrite HBpow.
  assert (Hden : 0 < INR k * A ^ k * (B * B ^ k)).
  { repeat apply Rmult_lt_0_compat.
    - exact HK.
    - apply pow_lt; lra.
    - exact HB.
    - apply pow_lt; lra. }
  apply Rmult_le_reg_r with (r := INR k * A ^ k * (B * B ^ k)); [exact Hden|].
  replace ((1 / (B * B ^ k)) * (INR k * A ^ k * (B * B ^ k)))
    with (INR k * A ^ k)
    by (field; repeat split; try (apply pow_nonzero); lra).
  replace (((1 / INR k) * (1 / A ^ k - 1 / B ^ k)) *
             (INR k * A ^ k * (B * B ^ k)))
    with (B * B ^ k - A ^ k * B)
    by (field; repeat split; try (apply pow_nonzero); lra).
  lra.
Qed.

(* --------------------------------------------------------------------- *)
(*  Lower step: 1/(n)^(k+1) >= (1/k)(1/n^k - 1/(S n)^k), n >= 1.          *)
(* --------------------------------------------------------------------- *)

Lemma pterm_lower_step :
  forall (k n : nat), (1 <= k)%nat -> (1 <= n)%nat ->
    (1 / INR k) * (1 / (INR n) ^ k - 1 / (INR (S n)) ^ k)
      <= 1 / (INR n) ^ (S k).
Proof.
  intros k n Hk Hn.
  set (A := INR n).
  set (B := INR (S n)).
  assert (HA : 0 < A) by (subst A; apply lt_0_INR; lia).
  assert (HB : 0 < B) by (subst B; apply lt_0_INR; lia).
  assert (HK : 0 < INR k) by (apply lt_0_INR; lia).
  assert (HAB : B = A + 1) by (subst A; subst B; rewrite S_INR; ring).
  assert (HApow : A ^ (S k) = A * A ^ k) by reflexivity.
  assert (HBpow : B ^ (S k) = B * B ^ k) by reflexivity.
  assert (Hbern : 1 + INR (S k) * (- (1 / B)) <= (1 + - (1 / B)) ^ (S k)).
  { apply bernoulli_int.
    assert (HB1 : 1 <= B) by (rewrite HAB; lra).
    assert (Hle : 1 / B <= 1).
    { apply Rmult_le_reg_r with (r := B); [exact HB|].
      replace ((1 / B) * B) with 1 by (field; lra).
      rewrite Rmult_1_l. exact HB1. }
    exact (Ropp_le_contravar 1 (1 / B) Hle). }
  rewrite S_INR in Hbern.
  assert (Hkey : (A - INR k) * B ^ k <= A ^ (S k)).
  { assert (Hmul : B ^ (S k) * (1 + (INR k + 1) * (- (1 / B)))
                   <= B ^ (S k) * (1 + - (1 / B)) ^ (S k)).
    { apply Rmult_le_compat_l.
      - apply Rlt_le, pow_lt. exact HB.
      - exact Hbern. }
    rewrite <- (Rpow_mult_distr B (1 + - (1 / B)) (S k)) in Hmul.
    replace (B * (1 + - (1 / B))) with A in Hmul
      by (rewrite HAB; field; lra).
    rewrite HBpow in Hmul.
    replace (B * B ^ k * (1 + (INR k + 1) * (- (1 / B))))
      with ((A - INR k) * B ^ k) in Hmul
      by (rewrite HAB; field; try (apply pow_nonzero); lra).
    exact Hmul. }
  rewrite HApow.
  assert (Hden : 0 < INR k * A ^ k * B ^ k * (A * A ^ k)).
  { apply Rmult_lt_0_compat.
    - apply Rmult_lt_0_compat.
      + apply Rmult_lt_0_compat; [exact HK | apply pow_lt; lra].
      + apply pow_lt; lra.
    - apply Rmult_lt_0_compat; [exact HA | apply pow_lt; lra]. }
  apply Rmult_le_reg_r
    with (r := INR k * A ^ k * B ^ k * (A * A ^ k)); [exact Hden|].
  replace (((1 / INR k) * (1 / A ^ k - 1 / B ^ k)) *
             (INR k * A ^ k * B ^ k * (A * A ^ k)))
    with ((B ^ k - A ^ k) * (A * A ^ k))
    by (field; repeat split; try (apply pow_nonzero); lra).
  replace ((1 / (A * A ^ k)) * (INR k * A ^ k * B ^ k * (A * A ^ k)))
    with (INR k * A ^ k * B ^ k)
    by (field; repeat split; try (apply pow_nonzero); lra).
  assert (Hkey2 : (A - INR k) * B ^ k * A ^ k <= (A * A ^ k) * A ^ k).
  { apply Rmult_le_compat_r; [apply pow_le; lra | exact Hkey]. }
  nra.
Qed.

(* --------------------------------------------------------------------- *)
(*  The p-series term and its finite partial sums (tail starting at N+1). *)
(* --------------------------------------------------------------------- *)

Definition pterm (k n : nat) : R := 1 / (INR n) ^ (S k).

Definition psum (k N M : nat) : R :=
  sum_f_R0 (fun i => pterm k (N + 1 + i)) M.

Lemma pterm_nonneg : forall (k n : nat), (1 <= n)%nat -> 0 <= pterm k n.
Proof.
  intros k n Hn.
  unfold pterm, Rdiv.
  apply Rlt_le.
  apply Rmult_lt_0_compat; [lra|].
  apply Rinv_0_lt_compat.
  apply pow_lt.
  apply lt_0_INR. lia.
Qed.

(* --------------------------------------------------------------------- *)
(*  Sum lemmas missing from the stdlib fragment we import.                *)
(* --------------------------------------------------------------------- *)

Lemma sum_f_R0_le_all : forall (An Bn : nat -> R) (M : nat),
  (forall i, (i <= M)%nat -> An i <= Bn i) ->
  sum_f_R0 An M <= sum_f_R0 Bn M.
Proof.
  intros An Bn M H.
  induction M as [| M IH].
  - simpl. apply H. lia.
  - rewrite tech5. rewrite tech5.
    apply Rplus_le_compat.
    + apply IH. intros i Hi. apply H. lia.
    + apply H. lia.
Qed.

Lemma sum_f_R0_const_mul : forall (c : R) (f : nat -> R) (M : nat),
  sum_f_R0 (fun i => c * f i) M = c * sum_f_R0 f M.
Proof.
  intros c f M.
  induction M as [| M IH].
  - simpl. ring.
  - rewrite tech5. rewrite tech5. rewrite IH. ring.
Qed.

(* --------------------------------------------------------------------- *)
(*  Telescoping identity for a finite sum of consecutive differences.     *)
(* --------------------------------------------------------------------- *)

Lemma telescope : forall (g : nat -> R) (a M : nat),
  sum_f_R0 (fun i => g ((a + i)%nat) - g ((a + i + 1)%nat)) M
    = g a - g ((a + M + 1)%nat).
Proof.
  intros g a M.
  induction M as [| M IH].
  - simpl. replace ((a + 0)%nat) with a by lia. ring.
  - simpl. rewrite IH.
    replace ((a + S M)%nat) with ((a + M + 1)%nat) by lia.
    ring.
Qed.

(* --------------------------------------------------------------------- *)
(*  Finite upper bound: psum <= (1/k)(1/N^k - 1/(N+M+1)^k)                *)
(* --------------------------------------------------------------------- *)

Lemma psum_upper_sharp : forall (k N M : nat),
  (1 <= k)%nat -> (1 <= N)%nat ->
  psum k N M <=
    (1 / INR k) *
      (1 / (INR N) ^ k - 1 / (INR ((N + M + 1)%nat)) ^ k).
Proof.
  intros k N M Hk HN.
  unfold psum.
  eapply Rle_trans with
    (r2 := sum_f_R0
             (fun i => (1 / INR k) *
                (1 / (INR ((N + i)%nat)) ^ k -
                 1 / (INR ((N + i + 1)%nat)) ^ k)) M).
  - apply sum_f_R0_le_all. intros i Hi.
    unfold pterm.
    replace ((N + 1 + i)%nat) with ((S (N + i))%nat) by lia.
    replace ((N + i + 1)%nat) with ((S (N + i))%nat) by lia.
    apply pterm_upper_step; [exact Hk | lia].
  - rewrite sum_f_R0_const_mul.
    rewrite (telescope (fun m => 1 / (INR m) ^ k) N M).
    apply Rle_refl.
Qed.

Lemma psum_upper : forall (k N M : nat),
  (1 <= k)%nat -> (1 <= N)%nat ->
  psum k N M <= 1 / (INR k * (INR N) ^ k).
Proof.
  intros k N M Hk HN.
  eapply Rle_trans.
  - apply psum_upper_sharp; auto.
  - set (c := 1 / INR k).
    set (a := 1 / (INR N) ^ k).
    set (b := 1 / (INR ((N + M + 1)%nat)) ^ k).
    assert (Hk0 : INR k <> 0) by (apply Rgt_not_eq, lt_0_INR; lia).
    assert (HN0 : INR N <> 0) by (apply Rgt_not_eq, lt_0_INR; lia).
    assert (HNk : (INR N) ^ k <> 0) by (apply pow_nonzero; exact HN0).
    replace (1 / (INR k * (INR N) ^ k)) with (c * a)
      by (subst c; subst a; field; auto).
    assert (Hc : 0 <= c).
    { subst c. unfold Rdiv. rewrite Rmult_1_l. apply Rlt_le.
      apply Rinv_0_lt_compat. apply lt_0_INR. lia. }
    assert (Hb : 0 <= b).
    { subst b. unfold Rdiv. rewrite Rmult_1_l. apply Rlt_le.
      apply Rinv_0_lt_compat. apply pow_lt. apply lt_0_INR. lia. }
    assert (Hle : a - b <= a).
    { replace (a - b) with (a + (- b)) by ring.
      eapply Rle_trans with (r2 := a + 0).
      - apply Rplus_le_compat_l.
        replace 0 with (- 0) by ring.
        apply Ropp_le_contravar. exact Hb.
      - rewrite Rplus_0_r. apply Rle_refl. }
    apply Rmult_le_compat_l; [exact Hc | exact Hle].
Qed.

(* --------------------------------------------------------------------- *)
(*  Finite lower bound: psum >= (1/k)(1/(N+1)^k - 1/(N+M+2)^k)            *)
(* --------------------------------------------------------------------- *)

Lemma psum_lower_sharp : forall (k N M : nat),
  (1 <= k)%nat -> (1 <= N)%nat ->
  (1 / INR k) *
    (1 / (INR ((N + 1)%nat)) ^ k - 1 / (INR ((N + M + 2)%nat)) ^ k)
    <= psum k N M.
Proof.
  intros k N M Hk HN.
  unfold psum.
  eapply Rle_trans with
    (r2 := sum_f_R0
             (fun i => (1 / INR k) *
                (1 / (INR ((N + 1 + i)%nat)) ^ k -
                 1 / (INR ((N + 1 + i + 1)%nat)) ^ k)) M).
  - rewrite sum_f_R0_const_mul.
    rewrite (telescope (fun m => 1 / (INR m) ^ k) (N + 1) M).
    replace ((N + 1 + M + 1)%nat) with ((N + M + 2)%nat) by lia.
    apply Rle_refl.
  - apply sum_f_R0_le_all. intros i Hi.
    unfold pterm.
    replace ((N + 1 + i + 1)%nat) with ((S (N + 1 + i))%nat) by lia.
    apply pterm_lower_step; [exact Hk | lia].
Qed.

(* --------------------------------------------------------------------- *)
(*  Small algebraic helpers.                                             *)
(* --------------------------------------------------------------------- *)

Lemma div_mul_cancel : forall x : R, x <> 0 -> 1 / x * x = 1.
Proof.
  intros x Hx. field. exact Hx.
Qed.

Lemma mul_neq_0 : forall a b : R, a <> 0 -> b <> 0 -> a * b <> 0.
Proof.
  intros a b Ha Hb H.
  apply Rmult_integral in H. destruct H as [H | H].
  - exact (Ha H).
  - exact (Hb H).
Qed.

Lemma sub_le_swap : forall a z L : R, a - z <= L -> a - L <= z.
Proof. intros. lra. Qed.

(* --------------------------------------------------------------------- *)
(*  If every term of a convergent sequence is <= B, its limit is <= B.    *)
(* --------------------------------------------------------------------- *)

Lemma Un_cv_le_const : forall (Un : nat -> R) (l B : R),
  Un_cv Un l -> (forall n, Un n <= B) -> l <= B.
Proof.
  intros Un l B Hcv Hle.
  apply Rnot_lt_le. intros H.
  set (eps := l - B).
  assert (Heps : 0 < eps) by (change (0 < l - B); lra).
  destruct (Hcv eps Heps) as [N HN].
  specialize (HN N (le_n N)).
  unfold Rdist in HN.
  apply Rabs_def2 in HN.
  destruct HN as [H1 H2].
  specialize (Hle N).
  subst eps. lra.
Qed.

(* --------------------------------------------------------------------- *)
(*  The lower-limit remainder can be made arbitrarily small.             *)
(* --------------------------------------------------------------------- *)

Lemma tail_term_small : forall (k N : nat),
  (1 <= k)%nat -> (1 <= N)%nat ->
  forall eps : R, 0 < eps ->
  exists M : nat,
    (1 / INR k) * (1 / (INR ((N + M + 2)%nat)) ^ k) < eps.
Proof.
  intros k N Hk HN eps Heps.
  destruct (INR_unbounded (1 / (INR k * eps))) as [m Hm].
  exists m.
  set (I := (N + m + 2)%nat).
  assert (Hk0 : INR k <> 0) by (apply Rgt_not_eq, lt_0_INR; lia).
  assert (HI0 : INR I <> 0) by (apply Rgt_not_eq, lt_0_INR; subst I; lia).
  assert (HIm : 1 / (INR k * eps) < INR I).
  { eapply Rlt_le_trans; [exact Hm | apply le_INR; subst I; lia]. }
  assert (HI1 : 1 <= INR I).
  { apply Rle_trans with (INR 1); [simpl; lra | apply le_INR; subst I; lia]. }
  assert (Hpow : INR I <= (INR I) ^ k)
    by (apply pow_ge_self; [exact HI1 | exact Hk]).
  assert (Hinv : 1 / (INR I) ^ k <= 1 / INR I).
  { unfold Rdiv. rewrite !Rmult_1_l.
    apply Rinv_le_contravar; [apply lt_0_INR; subst I; lia | exact Hpow]. }
  assert (Hc : 0 <= 1 / INR k).
  { unfold Rdiv. rewrite Rmult_1_l. apply Rlt_le.
    apply Rinv_0_lt_compat. apply lt_0_INR; lia. }
  assert (Hstep : (1 / INR k) * (1 / (INR I) ^ k)
                  <= (1 / INR k) * (1 / INR I)).
  { apply Rmult_le_compat_l; [exact Hc | exact Hinv]. }
  assert (Hrpos : 0 < INR k * eps)
    by (apply Rmult_lt_0_compat; [apply lt_0_INR; lia | exact Heps]).
  assert (Hm2 : 1 < INR I * (INR k * eps)).
  { assert (Htmp : (1 / (INR k * eps)) * (INR k * eps) < INR I * (INR k * eps))
      by (apply Rmult_lt_compat_r; [exact Hrpos | exact HIm]).
    replace ((1 / (INR k * eps)) * (INR k * eps)) with 1 in Htmp
      by (symmetry; apply div_mul_cancel, mul_neq_0;
          [apply Rgt_not_eq, lt_0_INR; lia | apply Rgt_not_eq; exact Heps]).
    exact Htmp. }
  assert (Hsmall : 1 / (INR k * INR I) < eps).
  { apply Rmult_lt_reg_r with (r := INR k * INR I).
    - apply Rmult_lt_0_compat; [apply lt_0_INR; lia | apply lt_0_INR; subst I; lia].
    - replace ((1 / (INR k * INR I)) * (INR k * INR I)) with 1
        by (symmetry; apply div_mul_cancel, mul_neq_0;
            [apply Rgt_not_eq, lt_0_INR; lia | apply Rgt_not_eq, lt_0_INR; subst I; lia]).
      replace (eps * (INR k * INR I)) with (INR I * (INR k * eps)) by ring.
      exact Hm2. }
  eapply Rle_lt_trans.
  - exact Hstep.
  - replace ((1 / INR k) * (1 / INR I)) with (1 / (INR k * INR I)) by (field; auto).
    exact Hsmall.
Qed.

Lemma lt_sub_pos : forall a L : R, L < a -> 0 < a - L.
Proof. intros. lra. Qed.

(* --------------------------------------------------------------------- *)
(*  L2 for integer p = k+1 >= 2: two-sided bound, limit included.         *)
(* --------------------------------------------------------------------- *)

Theorem pseries_L2_integer :
  forall (k N : nat),
    (1 <= k)%nat -> (1 <= N)%nat ->
    exists L : R,
      Un_cv (fun M => psum k N M) L /\
      (1 / (INR k * (INR ((N + 1)%nat)) ^ k) <= L) /\
      (L <= 1 / (INR k * (INR N) ^ k)).
Proof.
  intros k N Hk HN.
  assert (Hincr : Un_growing (fun M => psum k N M)).
  { intros M. unfold psum. rewrite tech5.
    eapply Rle_trans with
      (r2 := sum_f_R0 (fun i => pterm k (N + 1 + i)) M + 0).
    - rewrite Rplus_0_r. apply Rle_refl.
    - apply Rplus_le_compat_l.
      change (0 <= pterm k ((N + 1 + S M)%nat)).
      apply pterm_nonneg. lia. }
  assert (Hbound : bound (EUn (fun M => psum k N M))).
  { exists (1 / (INR k * (INR N) ^ k)).
    intros x Hx. destruct Hx as [M HM].
    rewrite HM. apply psum_upper; auto. }
  destruct (Un_cv_crit _ Hincr Hbound) as [L Hcv].
  exists L. split; [exact Hcv | split].
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
        assert (H10 : INR ((N + 1)%nat) <> 0) by (apply Rgt_not_eq, lt_0_INR; lia).
        assert (H20 : INR ((N + M + 2)%nat) <> 0) by (apply Rgt_not_eq, lt_0_INR; lia).
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
      - change (Un_cv (fun n => sum_f_R0 (fun i => pterm k (N + 1 + i)) n) L).
        exact Hcv.
      - intros i. apply pterm_nonneg. lia. }
    assert (HaL' : a - z <= L) by (eapply Rle_trans; [exact Hfin | exact Hpartial]).
    change (z < a - L) in Hz.
    assert (Hzle : a - L <= z) by (apply sub_le_swap; exact HaL').
    assert (Habs : z < z) by (eapply Rlt_le_trans; [exact Hz | exact Hzle]).
    exact (Rlt_irrefl z Habs).
  - eapply Un_cv_le_const.
    + exact Hcv.
    + intros M. apply psum_upper; auto.
Qed.

(* --------------------------------------------------------------------- *)
(*  Assumption audit: every exported result must rest only on the Coq    *)
(*  Reals axiomatic base (no project axioms, no Admitted).               *)
(* --------------------------------------------------------------------- *)

Print Assumptions bernoulli_int.
Print Assumptions one_le_pow.
Print Assumptions pow_ge_self.
Print Assumptions prod_pow_neq_0.
Print Assumptions pterm_upper_step.
Print Assumptions pterm_lower_step.
Print Assumptions pterm_nonneg.
Print Assumptions sum_f_R0_le_all.
Print Assumptions sum_f_R0_const_mul.
Print Assumptions telescope.
Print Assumptions psum_upper_sharp.
Print Assumptions psum_upper.
Print Assumptions psum_lower_sharp.
Print Assumptions div_mul_cancel.
Print Assumptions mul_neq_0.
Print Assumptions sub_le_swap.
Print Assumptions lt_sub_pos.
Print Assumptions Un_cv_le_const.
Print Assumptions tail_term_small.
Print Assumptions pseries_L2_integer.
