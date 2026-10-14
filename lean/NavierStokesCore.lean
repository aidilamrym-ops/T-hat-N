import Mathlib.Tactic

open scoped BigOperators

/-!
# Hermetic Lean 4 Kernel: 1D periodic hydrodynamic channel

Finite model, no continuum. Cells are indexed by `Fin N` (never `ℝ`);
velocities are exact rational triples. The main theorem is a genuine
machine-checked discrete Chorin energy estimate:

  E(u^{n+1}) ≤ E(u*) ≤ E(u_adv) = E(u^n)

proved from three verified links: advection is a permutation
(`Equiv.sum_comp` style reindexing, fully elaborated), CFL diffusion is a
convex combination (pointwise variance identity), and the projection
is dissipative via two PROVED summation-by-parts identities plus the
solver contract `Δp = C · div u*` as an explicit hypothesis.

Scope notes (binding):
* 1D channel (`Fin N`), not the full N^3 product lattice: the product
  sums are future work. The estimate content is unaffected.
* Forward-difference gradient/divergence pair: the adjoint calculus
  closes exactly here; the central-difference variant lacks the same
  per-norm identity and is not claimed.
* Explicit hypotheses (`hN`, CFL bounds, `C > 0`, `hPoisson`) are the
  analytic inputs. `hPoisson` is the spectral solver's contract,
  discharged in the Python layer up to ball enclosure.
-/

namespace NavierStokesCore

/-- Cell velocity: exact rational triple (mirrors the ℚ entry point
    of the Python-Flint ball engine). -/
structure CellVelocity where
  x : ℚ
  y : ℚ
  z : ℚ

/-- Finite lattice of `N` cells, one triple per cell. -/
structure FluidLattice (N : ℕ) where
  vel : Fin N → CellVelocity

/-- Forward neighbor: pure integer-modulus index shift. -/
def fwd (N : ℕ) (hN : 0 < N) (i : Fin N) : Fin N :=
  ⟨(i.val + 1) % N, Nat.mod_lt _ hN⟩

/-- Backward neighbor. -/
def bwd (N : ℕ) (hN : 0 < N) (i : Fin N) : Fin N :=
  ⟨(i.val + N - 1) % N, Nat.mod_lt _ hN⟩

/-- Modulus round trip, forward then backward. -/
lemma mod_shift_cancel_left (N : ℕ) (hN : 0 < N) (x : ℕ) (hx : x < N) :
    (((x + 1) % N) + N - 1) % N = x := by
  by_cases h : x + 1 < N
  · have hm : (x + 1) % N = x + 1 := Nat.mod_eq_of_lt h
    rw [hm]
    have e : x + 1 + N - 1 = N + x := by omega
    rw [e, Nat.add_comm N x, Nat.add_mod_right, Nat.mod_eq_of_lt hx]
  · have hxN : x + 1 = N := by omega
    have hm : (x + 1) % N = 0 := by rw [hxN]; exact Nat.mod_self N
    rw [hm]
    have e : 0 + N - 1 = N - 1 := by omega
    rw [e, Nat.mod_eq_of_lt (by omega : N - 1 < N)]
    omega

/-- Modulus round trip, backward then forward. -/
lemma mod_shift_cancel_right (N : ℕ) (hN : 0 < N) (x : ℕ) (hx : x < N) :
    (((x + N - 1) % N) + 1) % N = x := by
  by_cases h : x = 0
  · subst h
    have e : 0 + N - 1 = N - 1 := by omega
    have hm : (0 + N - 1) % N = N - 1 := by
      rw [e]; exact Nat.mod_eq_of_lt (by omega)
    rw [hm]
    have e2 : N - 1 + 1 = N := by omega
    rw [e2]
    exact Nat.mod_self N
  · have h2 : x + N - 1 = (x - 1) + N := by omega
    have hm : (x + N - 1) % N = x - 1 := by
      rw [h2, Nat.add_mod_right]
      exact Nat.mod_eq_of_lt (by omega)
    rw [hm]
    have hsub : x - 1 + 1 = x := Nat.sub_add_cancel (by omega : 1 ≤ x)
    rw [hsub]
    exact Nat.mod_eq_of_lt hx

/-- The shift is a genuine permutation (both round trips). -/
def shiftPerm (N : ℕ) (hN : 0 < N) : Equiv.Perm (Fin N) where
  toFun := fwd N hN
  invFun := bwd N hN
  left_inv := by
    intro i
    apply Fin.ext
    show (((i.val + 1) % N) + N - 1) % N = i.val
    exact mod_shift_cancel_left N hN _ i.isLt
  right_inv := by
    intro i
    apply Fin.ext
    show (((i.val + N - 1) % N) + 1) % N = i.val
    exact mod_shift_cancel_right N hN _ i.isLt

/-- Reindexing helper: pointwise pullback along any permutation. -/
lemma sum_perm (N : ℕ) (e : Equiv.Perm (Fin N)) (f g : Fin N → ℚ)
    (h : ∀ i, f i = g (e i)) : ∑ i, f i = ∑ i, g i :=
  Fintype.sum_equiv e f g h

/-- The coercions unfold to the modulus shifts (normal form). -/
@[simp] lemma perm_apply (N : ℕ) (hN : 0 < N) (i : Fin N) :
    (shiftPerm N hN) i = fwd N hN i := rfl

@[simp] lemma symm_apply (N : ℕ) (hN : 0 < N) (i : Fin N) :
    (shiftPerm N hN).symm i = bwd N hN i := rfl

lemma sum_fwd (N : ℕ) (hN : 0 < N) (g : Fin N → ℚ) :
    ∑ i, g (fwd N hN i) = ∑ i, g i :=
  Equiv.sum_comp (shiftPerm N hN) g

lemma sum_bwd (N : ℕ) (hN : 0 < N) (g : Fin N → ℚ) :
    ∑ i, g (bwd N hN i) = ∑ i, g i :=
  Equiv.sum_comp (shiftPerm N hN).symm g

/-- Two-sided shift: forward-anchored sums equal backward-anchored sums. -/
lemma sum_fwd_to_bwd (N : ℕ) (hN : 0 < N) (F : Fin N → Fin N → ℚ) :
    ∑ i, F i (fwd N hN i) = ∑ j, F (bwd N hN j) j := by
  have r : ∀ i, F i (fwd N hN i)
      = F (bwd N hN (fwd N hN i)) (fwd N hN i) := by
    intro i
    rw [show bwd N hN (fwd N hN i) = i from (shiftPerm N hN).left_inv i]
  rw [Finset.sum_congr rfl (fun i _ => r i)]
  exact Equiv.sum_comp (shiftPerm N hN) (fun j => F (bwd N hN j) j)

/-- Cell energy: sum of exact rational squares (no float). -/
def cellEnergy (u : CellVelocity) : ℚ := u.x ^ 2 + u.y ^ 2 + u.z ^ 2

/-- Total kinetic energy over the finite lattice. -/
def totalEnergy (N : ℕ) (L : FluidLattice N) : ℚ :=
  ∑ i, cellEnergy (L.vel i)

/-- Cyclic advection operator T-hat: pure index permutation. -/
def advect_shift (N : ℕ) (hN : 0 < N) (L : FluidLattice N) : FluidLattice N :=
  ⟨fun i => L.vel (fwd N hN i)⟩

/-- Advection preserves energy exactly (permutation reindexing). -/
lemma energy_advect (N : ℕ) (hN : 0 < N) (L : FluidLattice N) :
    totalEnergy N (advect_shift N hN L) = totalEnergy N L := by
  unfold totalEnergy advect_shift
  simp only
  exact Equiv.sum_comp (shiftPerm N hN) (fun i => cellEnergy (L.vel i))

/-- CFL diffusion: convex combination with periodic neighbors.
    `μ` obeys the explicit stability bound `2 * μ ≤ 1`. -/
def diffuse_step (N : ℕ) (hN : 0 < N) (μ : ℚ) (L : FluidLattice N) :
    FluidLattice N :=
  ⟨fun i =>
    ⟨(1 - 2 * μ) * (L.vel i).x + μ * (L.vel (fwd N hN i)).x
        + μ * (L.vel (bwd N hN i)).x,
     (1 - 2 * μ) * (L.vel i).y + μ * (L.vel (fwd N hN i)).y
        + μ * (L.vel (bwd N hN i)).y,
     (1 - 2 * μ) * (L.vel i).z + μ * (L.vel (fwd N hN i)).z
        + μ * (L.vel (bwd N hN i)).z⟩⟩

/-- Pointwise variance identity: squares are convex. -/
lemma convex_sq (μ a b c : ℚ) (hμ0 : 0 ≤ μ) (hμ1 : 2 * μ ≤ 1) :
    ((1 - 2 * μ) * a + μ * b + μ * c) ^ 2
      ≤ (1 - 2 * μ) * a ^ 2 + μ * b ^ 2 + μ * c ^ 2 := by
  have hα : 0 ≤ 1 - 2 * μ := by linarith
  have e1 : 0 ≤ μ * (1 - 2 * μ) * (a - b) ^ 2 :=
    mul_nonneg (mul_nonneg hμ0 hα) (sq_nonneg _)
  have e2 : 0 ≤ μ * μ * (b - c) ^ 2 :=
    mul_nonneg (mul_nonneg hμ0 hμ0) (sq_nonneg _)
  have e3 : 0 ≤ μ * (1 - 2 * μ) * (c - a) ^ 2 :=
    mul_nonneg (mul_nonneg hμ0 hα) (sq_nonneg _)
  have hsum : (1 - 2 * μ) * a ^ 2 + μ * b ^ 2 + μ * c ^ 2
      - ((1 - 2 * μ) * a + μ * b + μ * c) ^ 2
      = μ * (1 - 2 * μ) * (a - b) ^ 2 + μ * μ * (b - c) ^ 2
        + μ * (1 - 2 * μ) * (c - a) ^ 2 := by ring
  linarith

/-- Scalar diffusion contracts the sum of squares. -/
lemma scalar_diffuse_le (N : ℕ) (hN : 0 < N) (μ : ℚ)
    (hμ0 : 0 ≤ μ) (hμ1 : 2 * μ ≤ 1)
    (a b c : Fin N → ℚ)
    (hb : ∀ i, b i = a (fwd N hN i))
    (hc : ∀ i, c i = a (bwd N hN i)) :
    ∑ i, ((1 - 2 * μ) * a i + μ * b i + μ * c i) ^ 2 ≤ ∑ i, (a i) ^ 2 := by
  calc ∑ i, ((1 - 2 * μ) * a i + μ * b i + μ * c i) ^ 2
      ≤ ∑ i, ((1 - 2 * μ) * (a i) ^ 2 + μ * (b i) ^ 2 + μ * (c i) ^ 2) :=
        Finset.sum_le_sum (fun i _ => convex_sq μ (a i) (b i) (c i) hμ0 hμ1)
    _ = (1 - 2 * μ) * ∑ i, (a i) ^ 2 + μ * ∑ i, (b i) ^ 2
          + μ * ∑ i, (c i) ^ 2 := by
        simp only [Finset.sum_add_distrib, ← Finset.mul_sum]
    _ = ∑ i, (a i) ^ 2 := by
        have hfun1 : (fun i => (b i) ^ 2) = (fun i => (a (fwd N hN i)) ^ 2) :=
          funext (fun i => by rw [hb i])
        have hfun2 : (fun i => (c i) ^ 2) = (fun i => (a (bwd N hN i)) ^ 2) :=
          funext (fun i => by rw [hc i])
        have e1 : ∑ i, (b i) ^ 2 = ∑ i, (a i) ^ 2 := by
          rw [hfun1]
          exact sum_fwd N hN (fun i => (a i) ^ 2)
        have e2 : ∑ i, (c i) ^ 2 = ∑ i, (a i) ^ 2 := by
          rw [hfun2]
          exact sum_bwd N hN (fun i => (a i) ^ 2)
        rw [e1, e2]
        ring

/-- Diffusion contracts total energy (three components). -/
lemma energy_diffuse (N : ℕ) (hN : 0 < N) (μ : ℚ)
    (hμ0 : 0 ≤ μ) (hμ1 : 2 * μ ≤ 1) (L : FluidLattice N) :
    totalEnergy N (diffuse_step N hN μ L) ≤ totalEnergy N L := by
  have hx := scalar_diffuse_le N hN μ hμ0 hμ1
    (fun i => (L.vel i).x) (fun i => (L.vel (fwd N hN i)).x)
    (fun i => (L.vel (bwd N hN i)).x) (fun i => rfl) (fun i => rfl)
  have hy := scalar_diffuse_le N hN μ hμ0 hμ1
    (fun i => (L.vel i).y) (fun i => (L.vel (fwd N hN i)).y)
    (fun i => (L.vel (bwd N hN i)).y) (fun i => rfl) (fun i => rfl)
  have hz := scalar_diffuse_le N hN μ hμ0 hμ1
    (fun i => (L.vel i).z) (fun i => (L.vel (fwd N hN i)).z)
    (fun i => (L.vel (bwd N hN i)).z) (fun i => rfl) (fun i => rfl)
  have hexpand : totalEnergy N (diffuse_step N hN μ L)
      = ∑ i, ((1 - 2 * μ) * (L.vel i).x + μ * (L.vel (fwd N hN i)).x
          + μ * (L.vel (bwd N hN i)).x) ^ 2
        + ∑ i, ((1 - 2 * μ) * (L.vel i).y + μ * (L.vel (fwd N hN i)).y
          + μ * (L.vel (bwd N hN i)).y) ^ 2
        + ∑ i, ((1 - 2 * μ) * (L.vel i).z + μ * (L.vel (fwd N hN i)).z
          + μ * (L.vel (bwd N hN i)).z) ^ 2 := by
    have rfl_expand : totalEnergy N (diffuse_step N hN μ L)
        = ∑ i, ((((1 - 2 * μ) * (L.vel i).x + μ * (L.vel (fwd N hN i)).x
            + μ * (L.vel (bwd N hN i)).x) ^ 2
          + ((1 - 2 * μ) * (L.vel i).y + μ * (L.vel (fwd N hN i)).y
            + μ * (L.vel (bwd N hN i)).y) ^ 2)
          + ((1 - 2 * μ) * (L.vel i).z + μ * (L.vel (fwd N hN i)).z
            + μ * (L.vel (bwd N hN i)).z) ^ 2) := rfl
    rw [rfl_expand]
    simp only [Finset.sum_add_distrib]
  have hexpand0 : totalEnergy N L
      = ∑ i, ((L.vel i).x) ^ 2 + ∑ i, ((L.vel i).y) ^ 2
        + ∑ i, ((L.vel i).z) ^ 2 := by
    have rfl_expand0 : totalEnergy N L
        = ∑ i, ((((L.vel i).x) ^ 2 + ((L.vel i).y) ^ 2)
          + ((L.vel i).z) ^ 2) := rfl
    rw [rfl_expand0]
    simp only [Finset.sum_add_distrib]
  rw [hexpand, hexpand0]
  linarith

/-- Forward-difference pressure gradient. -/
def gradFwd (N : ℕ) (hN : 0 < N) (p : Fin N → ℚ) (i : Fin N) : ℚ :=
  p (fwd N hN i) - p i

/-- Backward-difference divergence (adjoint of `gradFwd`). -/
def bdivAt (N : ℕ) (hN : 0 < N) (u : Fin N → CellVelocity) (i : Fin N) : ℚ :=
  (u i).x - (u (bwd N hN i)).x

/-- Discrete Laplacian (unscaled units). -/
def lapAt (N : ℕ) (hN : 0 < N) (p : Fin N → ℚ) (i : Fin N) : ℚ :=
  p (fwd N hN i) - 2 * p i + p (bwd N hN i)

/-- Summation by parts I (proved by periodic reindexing). -/
lemma sbp_grad_div (N : ℕ) (hN : 0 < N) (u : Fin N → CellVelocity)
    (p : Fin N → ℚ) :
    ∑ i, (u i).x * gradFwd N hN p i = -∑ i, bdivAt N hN u i * p i := by
  calc ∑ i, (u i).x * gradFwd N hN p i
      = ∑ i, ((u i).x * p (fwd N hN i) - (u i).x * p i) := by
        apply Finset.sum_congr rfl
        intro i _
        simp only [gradFwd, mul_sub]
    _ = ∑ i, (u i).x * p (fwd N hN i) - ∑ i, (u i).x * p i :=
        Finset.sum_sub_distrib _ _
    _ = ∑ i, (u (bwd N hN i)).x * p i - ∑ i, (u i).x * p i := by
        have hstep := sum_fwd_to_bwd N hN (fun a b => (u a).x * p b)
        have r1 : (∑ i, (u i).x * p (fwd N hN i))
            = ∑ i, (fun a b => (u a).x * p b) i (fwd N hN i) := rfl
        have r2 : (∑ j, (fun a b => (u a).x * p b) (bwd N hN j) j)
            = ∑ i, (u (bwd N hN i)).x * p i := rfl
        rw [r1, hstep, r2]
    _ = -∑ i, bdivAt N hN u i * p i := by
        simp only [bdivAt, sub_mul, Finset.sum_sub_distrib]
        ring

/-- Summation by parts II: Laplacian is negative-semidefinite (proved). -/
lemma sbp_lap_neg (N : ℕ) (hN : 0 < N) (p : Fin N → ℚ) :
    ∑ i, lapAt N hN p i * p i = -∑ i, (gradFwd N hN p i) ^ 2 := by
  have e1 : ∑ i, p (fwd N hN i) * p i = ∑ i, p i * p (fwd N hN i) :=
    Finset.sum_congr rfl (fun i _ => mul_comm _ _)
  have e2 : ∑ i, p (bwd N hN i) * p i = ∑ i, p i * p (fwd N hN i) := by
    have hstep := sum_fwd_to_bwd N hN (fun a b => p a * p b)
    have r1 : (∑ i, p (bwd N hN i) * p i)
        = ∑ j, (fun a b => p a * p b) (bwd N hN j) j := rfl
    have r2 : (∑ i, (fun a b => p a * p b) i (fwd N hN i))
        = ∑ i, p i * p (fwd N hN i) := rfl
    rw [r1, ← hstep, r2]
  have e3 : ∑ i, (p (fwd N hN i)) ^ 2 = ∑ i, (p i) ^ 2 :=
    sum_fwd N hN (fun i => (p i) ^ 2)
  have e4 : ∀ i : Fin N, (gradFwd N hN p i) ^ 2
      = (p (fwd N hN i)) ^ 2 - 2 * (p (fwd N hN i) * p i) + (p i) ^ 2 := by
    intro i
    simp only [gradFwd]
    ring
  have e5 : ∀ i : Fin N, lapAt N hN p i * p i
      = p (fwd N hN i) * p i - 2 * (p i) ^ 2 + p (bwd N hN i) * p i := by
    intro i
    simp only [lapAt]
    ring
  calc ∑ i, lapAt N hN p i * p i
      = ∑ i, (p (fwd N hN i) * p i - 2 * (p i) ^ 2
          + p (bwd N hN i) * p i) :=
        Finset.sum_congr rfl (fun i _ => e5 i)
    _ = ∑ i, p (fwd N hN i) * p i - ∑ i, (2 * (p i) ^ 2)
          + ∑ i, p (bwd N hN i) * p i := by
        simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib]
    _ = 2 * ∑ i, p i * p (fwd N hN i) - 2 * ∑ i, (p i) ^ 2 := by
        have sB : ∑ i, (2 * (p i) ^ 2) = 2 * ∑ i, (p i) ^ 2 :=
          (Finset.mul_sum _ _ _).symm
        rw [e1, e2, sB]
        ring
    _ = -∑ i, (gradFwd N hN p i) ^ 2 := by
        have g1 : ∑ i, (gradFwd N hN p i) ^ 2
            = ∑ i, ((p (fwd N hN i)) ^ 2 - 2 * (p (fwd N hN i) * p i))
              + ∑ i, (p i) ^ 2 := by
          have hcongr : ∀ i ∈ (Finset.univ : Finset (Fin N)),
              (gradFwd N hN p i) ^ 2
                = (p (fwd N hN i)) ^ 2 - 2 * (p (fwd N hN i) * p i)
                  + (p i) ^ 2 := fun i _ => e4 i
          rw [Finset.sum_congr rfl hcongr]
          simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib]
        rw [g1]
        have g2 : ∑ i, ((p (fwd N hN i)) ^ 2 - 2 * (p (fwd N hN i) * p i))
            = ∑ i, (p (fwd N hN i)) ^ 2
              - ∑ i, (2 * (p (fwd N hN i) * p i)) :=
          Finset.sum_sub_distrib _ _
        rw [g2, e3]
        have sD : ∑ i, (2 * (p (fwd N hN i) * p i))
            = 2 * ∑ i, p (fwd N hN i) * p i :=
          (Finset.mul_sum _ _ _).symm
        rw [sD, e1]
        ring

/-- Chorin projection correction on the x-channel. -/
def project_step (N : ℕ) (hN : 0 < N) (c : ℚ) (L : FluidLattice N)
    (p : Fin N → ℚ) : FluidLattice N :=
  ⟨fun i => ⟨(L.vel i).x - c * gradFwd N hN p i, (L.vel i).y,
    (L.vel i).z⟩⟩

/-- Projection dissipates energy under the solver contract
    `Δp = C · div u*` with `C > 0` and `c * C = 1`. -/
lemma energy_project (N : ℕ) (hN : 0 < N) (c C : ℚ) (hc : c * C = 1)
    (hC : 0 < C) (L : FluidLattice N) (p : Fin N → ℚ)
    (hPoisson : ∀ i, lapAt N hN p i = C * bdivAt N hN L.vel i) :
    totalEnergy N (project_step N hN c L p) ≤ totalEnergy N L := by
  have hCne : C ≠ 0 := hC.ne'
  have hS2nn : 0 ≤ ∑ i, (gradFwd N hN p i) ^ 2 :=
    Finset.sum_nonneg (fun i _ => sq_nonneg _)
  have hlink : ∑ i, (L.vel i).x * gradFwd N hN p i
      = (1 / C) * ∑ i, (gradFwd N hN p i) ^ 2 := by
    have h1 := sbp_grad_div N hN L.vel p
    have h2 := sbp_lap_neg N hN p
    have h3 : ∑ i, bdivAt N hN L.vel i * p i
        = (1 / C) * ∑ i, lapAt N hN p i * p i := by
      have : ∀ i : Fin N, bdivAt N hN L.vel i * p i
          = (1 / C) * (lapAt N hN p i * p i) := by
        intro i
        rw [hPoisson i]
        field_simp
      rw [Finset.sum_congr rfl (fun i _ => this i), ← Finset.mul_sum]
    rw [h1, h3, h2]
    ring
  have hE : totalEnergy N (project_step N hN c L p)
      = totalEnergy N L - c ^ 2 * ∑ i, (gradFwd N hN p i) ^ 2 := by
    have hexpand : totalEnergy N (project_step N hN c L p)
        = ∑ i, ((L.vel i).x - c * gradFwd N hN p i) ^ 2
          + ∑ i, ((L.vel i).y) ^ 2 + ∑ i, ((L.vel i).z) ^ 2 := by
      have rfl_expand : totalEnergy N (project_step N hN c L p)
          = ∑ i, ((((L.vel i).x - c * gradFwd N hN p i) ^ 2
            + ((L.vel i).y) ^ 2) + ((L.vel i).z) ^ 2) := rfl
      rw [rfl_expand]
      simp only [Finset.sum_add_distrib]
    have hexpand0 : totalEnergy N L
        = ∑ i, ((L.vel i).x) ^ 2 + ∑ i, ((L.vel i).y) ^ 2
          + ∑ i, ((L.vel i).z) ^ 2 := by
      have rfl_expand0 : totalEnergy N L
          = ∑ i, ((((L.vel i).x) ^ 2 + ((L.vel i).y) ^ 2)
            + ((L.vel i).z) ^ 2) := rfl
      rw [rfl_expand0]
      simp only [Finset.sum_add_distrib]
    rw [hexpand, hexpand0]
    have hsq : ∀ i : Fin N, ((L.vel i).x - c * gradFwd N hN p i) ^ 2
        = ((L.vel i).x) ^ 2 - 2 * c * ((L.vel i).x * gradFwd N hN p i)
          + c ^ 2 * (gradFwd N hN p i) ^ 2 := by
      intro i
      ring
    rw [Finset.sum_congr rfl (fun i _ => hsq i)]
    simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib]
    have t1 : ∑ i, (2 * c * ((L.vel i).x * gradFwd N hN p i))
        = 2 * c * ∑ i, (L.vel i).x * gradFwd N hN p i :=
      (Finset.mul_sum _ _ _).symm
    have t2 : ∑ i, (c ^ 2 * (gradFwd N hN p i) ^ 2)
        = c ^ 2 * ∑ i, (gradFwd N hN p i) ^ 2 :=
      (Finset.mul_sum _ _ _).symm
    rw [t1, t2, hlink]
    have hcC : c * (1 / C) = c ^ 2 := by
      field_simp
      nlinarith [hc]
    rw [show (2 : ℚ) * c * ((1 / C) * ∑ i, (gradFwd N hN p i) ^ 2)
        = 2 * (c * (1 / C)) * ∑ i, (gradFwd N hN p i) ^ 2 by ring, hcC]
    ring
  have hdrop : 0 ≤ c ^ 2 * ∑ i, (gradFwd N hN p i) ^ 2 :=
    mul_nonneg (sq_nonneg _) hS2nn
  linarith

/-- Godunov predictor: advect, then diffuse. -/
def godunov_predict (N : ℕ) (hN : 0 < N) (μ : ℚ) (L : FluidLattice N) :
    FluidLattice N :=
  diffuse_step N hN μ (advect_shift N hN L)

/-- Full fractional step: predict, then project. -/
def full_ns_step (N : ℕ) (hN : 0 < N) (μ c : ℚ) (L : FluidLattice N)
    (p : Fin N → ℚ) : FluidLattice N :=
  project_step N hN c (godunov_predict N hN μ L) p

/-- Main theorem: one full Navier-Stokes step never increases energy.
    Hypotheses are the explicit analytic inputs: lattice nontriviality,
    CFL stability, solver contract with positive constant. -/
theorem energy_monotonic_decay (N : ℕ) (hN : 0 < N) (μ c C : ℚ)
    (hμ0 : 0 ≤ μ) (hμ1 : 2 * μ ≤ 1) (hc : c * C = 1) (hC : 0 < C)
    (L : FluidLattice N) (p : Fin N → ℚ)
    (hPoisson : ∀ i, lapAt N hN p i
      = C * bdivAt N hN (godunov_predict N hN μ L).vel i) :
    totalEnergy N (full_ns_step N hN μ c L p) ≤ totalEnergy N L :=
  le_trans (energy_project N hN c C hc hC _ _ hPoisson)
    (le_trans (energy_diffuse N hN μ hμ0 hμ1 _)
      (le_of_eq (energy_advect N hN _)))

end NavierStokesCore
