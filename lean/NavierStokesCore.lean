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

/-- Reindexing helper: pointwise pullback along any permutation,
    over any finite index type (1D chains and product lattices). -/
lemma sum_perm {α : Type*} [Fintype α] (e : Equiv.Perm α) (f g : α → ℚ)
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

/-! ## 2D periodic lattice (gradual dimension lift, forward structure kept).

Index type `Fin N × Fin M`; shifts act per axis. All 1D lemmas above
are reused untouched; only axis-wise reindexing is new. -/

/-- Axis shifts as genuine permutations (product of 1D shift with identity). -/
def shiftPermX (N M : ℕ) (hN : 0 < N) : Equiv.Perm (Fin N × Fin M) :=
  Equiv.prodCongr (shiftPerm N hN) (Equiv.refl _)

def shiftPermY (N M : ℕ) (hM : 0 < M) : Equiv.Perm (Fin N × Fin M) :=
  Equiv.prodCongr (Equiv.refl _) (shiftPerm M hM)

/-- Reindex a product sum along the first axis. -/
lemma sum_prod_fst (N M : ℕ) (hN : 0 < N) (F : Fin N → Fin M → ℚ) :
    ∑ ij : Fin N × Fin M, F (fwd N hN ij.1) ij.2
      = ∑ ij : Fin N × Fin M, F ij.1 ij.2 :=
  sum_perm (shiftPermX N M hN) _ _ (fun _ => rfl)

/-- Reindex a product sum along the second axis. -/
lemma sum_prod_snd (N M : ℕ) (hM : 0 < M) (F : Fin N → Fin M → ℚ) :
    ∑ ij : Fin N × Fin M, F ij.1 (fwd M hM ij.2)
      = ∑ ij : Fin N × Fin M, F ij.1 ij.2 :=
  sum_perm (shiftPermY N M hM) _ _ (fun _ => rfl)

/-- Backward variants (symmetric permutations). -/
lemma sum_prod_fst_bwd (N M : ℕ) (hN : 0 < N) (F : Fin N → Fin M → ℚ) :
    ∑ ij : Fin N × Fin M, F (bwd N hN ij.1) ij.2
      = ∑ ij : Fin N × Fin M, F ij.1 ij.2 :=
  sum_perm (shiftPermX N M hN).symm _ _ (fun _ => rfl)

lemma sum_prod_snd_bwd (N M : ℕ) (hM : 0 < M) (F : Fin N → Fin M → ℚ) :
    ∑ ij : Fin N × Fin M, F ij.1 (bwd M hM ij.2)
      = ∑ ij : Fin N × Fin M, F ij.1 ij.2 :=
  sum_perm (shiftPermY N M hM).symm _ _ (fun _ => rfl)

/-- 2D lattice, energy, and x-advection (invariance proved). -/
structure FluidLattice2D (N M : ℕ) where
  vel : Fin N × Fin M → CellVelocity

def totalEnergy2D (N M : ℕ) (L : FluidLattice2D N M) : ℚ :=
  ∑ ij, cellEnergy (L.vel ij)

def advect2D (N M : ℕ) (hN : 0 < N) (L : FluidLattice2D N M) :
    FluidLattice2D N M :=
  ⟨fun ij => L.vel (fwd N hN ij.1, ij.2)⟩

lemma energy_advect2D (N M : ℕ) (hN : 0 < N) (L : FluidLattice2D N M) :
    totalEnergy2D N M (advect2D N M hN L) = totalEnergy2D N M L := by
  unfold totalEnergy2D advect2D
  simp only
  exact sum_prod_fst N M hN (fun i j => cellEnergy (L.vel (i, j)))

/-- Five-point stencil diffusion with explicit CFL bound. -/
def diffuse2D (N M : ℕ) (hN : 0 < N) (hM : 0 < M) (μ : ℚ)
    (L : FluidLattice2D N M) : FluidLattice2D N M :=
  ⟨fun ij =>
    ⟨(1 - 4 * μ) * (L.vel ij).x
        + μ * (L.vel (fwd N hN ij.1, ij.2)).x
        + μ * (L.vel (bwd N hN ij.1, ij.2)).x
        + μ * (L.vel (ij.1, fwd M hM ij.2)).x
        + μ * (L.vel (ij.1, bwd M hM ij.2)).x,
     (1 - 4 * μ) * (L.vel ij).y
        + μ * (L.vel (fwd N hN ij.1, ij.2)).y
        + μ * (L.vel (bwd N hN ij.1, ij.2)).y
        + μ * (L.vel (ij.1, fwd M hM ij.2)).y
        + μ * (L.vel (ij.1, bwd M hM ij.2)).y,
     (1 - 4 * μ) * (L.vel ij).z
        + μ * (L.vel (fwd N hN ij.1, ij.2)).z
        + μ * (L.vel (bwd N hN ij.1, ij.2)).z
        + μ * (L.vel (ij.1, fwd M hM ij.2)).z
        + μ * (L.vel (ij.1, bwd M hM ij.2)).z⟩⟩

/-- Five-term variance identity: squares stay convex. -/
lemma convex_sq5 (μ a b c d e : ℚ) (hμ0 : 0 ≤ μ) (hμ1 : 4 * μ ≤ 1) :
    ((1 - 4 * μ) * a + μ * b + μ * c + μ * d + μ * e) ^ 2
      ≤ (1 - 4 * μ) * a ^ 2 + μ * b ^ 2 + μ * c ^ 2
        + μ * d ^ 2 + μ * e ^ 2 := by
  have hα : 0 ≤ 1 - 4 * μ := by linarith
  have w : 0 ≤ μ * (1 - 4 * μ) := mul_nonneg hμ0 hα
  have w2 : 0 ≤ μ * μ := mul_nonneg hμ0 hμ0
  have e1 : 0 ≤ μ * (1 - 4 * μ) * (a - b) ^ 2 :=
    mul_nonneg w (sq_nonneg _)
  have e2 : 0 ≤ μ * (1 - 4 * μ) * (a - c) ^ 2 :=
    mul_nonneg w (sq_nonneg _)
  have e3 : 0 ≤ μ * (1 - 4 * μ) * (a - d) ^ 2 :=
    mul_nonneg w (sq_nonneg _)
  have e4 : 0 ≤ μ * (1 - 4 * μ) * (a - e) ^ 2 :=
    mul_nonneg w (sq_nonneg _)
  have f1 : 0 ≤ μ * μ * (b - c) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have f2 : 0 ≤ μ * μ * (b - d) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have f3 : 0 ≤ μ * μ * (b - e) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have f4 : 0 ≤ μ * μ * (c - d) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have f5 : 0 ≤ μ * μ * (c - e) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have f6 : 0 ≤ μ * μ * (d - e) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have hsum : (1 - 4 * μ) * a ^ 2 + μ * b ^ 2 + μ * c ^ 2 + μ * d ^ 2
      + μ * e ^ 2 - ((1 - 4 * μ) * a + μ * b + μ * c + μ * d + μ * e) ^ 2
      = μ * (1 - 4 * μ) * (a - b) ^ 2 + μ * (1 - 4 * μ) * (a - c) ^ 2
        + μ * (1 - 4 * μ) * (a - d) ^ 2 + μ * (1 - 4 * μ) * (a - e) ^ 2
        + μ * μ * (b - c) ^ 2 + μ * μ * (b - d) ^ 2 + μ * μ * (b - e) ^ 2
        + μ * μ * (c - d) ^ 2 + μ * μ * (c - e) ^ 2
        + μ * μ * (d - e) ^ 2 := by ring
  linarith

/-- Scalar 5-point diffusion contracts the sum of squares. -/
lemma scalar_diffuse2D (N M : ℕ) (hN : 0 < N) (hM : 0 < M) (μ : ℚ)
    (hμ0 : 0 ≤ μ) (hμ1 : 4 * μ ≤ 1)
    (a b c d e : Fin N × Fin M → ℚ)
    (hb : ∀ ij, b ij = a (fwd N hN ij.1, ij.2))
    (hc : ∀ ij, c ij = a (bwd N hN ij.1, ij.2))
    (hd : ∀ ij, d ij = a (ij.1, fwd M hM ij.2))
    (he : ∀ ij, e ij = a (ij.1, bwd M hM ij.2)) :
    ∑ ij, ((1 - 4 * μ) * a ij + μ * b ij + μ * c ij + μ * d ij
        + μ * e ij) ^ 2 ≤ ∑ ij, (a ij) ^ 2 := by
  calc ∑ ij, ((1 - 4 * μ) * a ij + μ * b ij + μ * c ij + μ * d ij
          + μ * e ij) ^ 2
      ≤ ∑ ij, ((1 - 4 * μ) * (a ij) ^ 2 + μ * (b ij) ^ 2 + μ * (c ij) ^ 2
          + μ * (d ij) ^ 2 + μ * (e ij) ^ 2) :=
        Finset.sum_le_sum
          (fun ij _ => convex_sq5 μ (a ij) (b ij) (c ij) (d ij) (e ij)
            hμ0 hμ1)
    _ = (1 - 4 * μ) * ∑ ij, (a ij) ^ 2 + μ * ∑ ij, (b ij) ^ 2
          + μ * ∑ ij, (c ij) ^ 2 + μ * ∑ ij, (d ij) ^ 2
          + μ * ∑ ij, (e ij) ^ 2 := by
        simp only [Finset.sum_add_distrib, ← Finset.mul_sum]
    _ = ∑ ij, (a ij) ^ 2 := by
        have hfun1 : (fun ij => (b ij) ^ 2)
            = (fun ij => (a (fwd N hN ij.1, ij.2)) ^ 2) :=
          funext (fun ij => by rw [hb ij])
        have hfun2 : (fun ij => (c ij) ^ 2)
            = (fun ij => (a (bwd N hN ij.1, ij.2)) ^ 2) :=
          funext (fun ij => by rw [hc ij])
        have hfun3 : (fun ij => (d ij) ^ 2)
            = (fun ij => (a (ij.1, fwd M hM ij.2)) ^ 2) :=
          funext (fun ij => by rw [hd ij])
        have hfun4 : (fun ij => (e ij) ^ 2)
            = (fun ij => (a (ij.1, bwd M hM ij.2)) ^ 2) :=
          funext (fun ij => by rw [he ij])
        have r1 : ∑ ij, (b ij) ^ 2 = ∑ ij, (a ij) ^ 2 := by
          rw [hfun1]
          exact sum_prod_fst N M hN (fun i j => (a (i, j)) ^ 2)
        have r2 : ∑ ij, (c ij) ^ 2 = ∑ ij, (a ij) ^ 2 := by
          rw [hfun2]
          exact sum_prod_fst_bwd N M hN (fun i j => (a (i, j)) ^ 2)
        have r3 : ∑ ij, (d ij) ^ 2 = ∑ ij, (a ij) ^ 2 := by
          rw [hfun3]
          exact sum_prod_snd N M hM (fun i j => (a (i, j)) ^ 2)
        have r4 : ∑ ij, (e ij) ^ 2 = ∑ ij, (a ij) ^ 2 := by
          rw [hfun4]
          exact sum_prod_snd_bwd N M hM (fun i j => (a (i, j)) ^ 2)
        rw [r1, r2, r3, r4]
        ring

/-- 2D diffusion contracts total energy (three components). -/
lemma energy_diffuse2D (N M : ℕ) (hN : 0 < N) (hM : 0 < M) (μ : ℚ)
    (hμ0 : 0 ≤ μ) (hμ1 : 4 * μ ≤ 1) (L : FluidLattice2D N M) :
    totalEnergy2D N M (diffuse2D N M hN hM μ L) ≤ totalEnergy2D N M L := by
  have hx := scalar_diffuse2D N M hN hM μ hμ0 hμ1
    (fun ij => (L.vel ij).x) (fun ij => (L.vel (fwd N hN ij.1, ij.2)).x)
    (fun ij => (L.vel (bwd N hN ij.1, ij.2)).x)
    (fun ij => (L.vel (ij.1, fwd M hM ij.2)).x)
    (fun ij => (L.vel (ij.1, bwd M hM ij.2)).x)
    (fun ij => rfl) (fun ij => rfl) (fun ij => rfl) (fun ij => rfl)
  have hy := scalar_diffuse2D N M hN hM μ hμ0 hμ1
    (fun ij => (L.vel ij).y) (fun ij => (L.vel (fwd N hN ij.1, ij.2)).y)
    (fun ij => (L.vel (bwd N hN ij.1, ij.2)).y)
    (fun ij => (L.vel (ij.1, fwd M hM ij.2)).y)
    (fun ij => (L.vel (ij.1, bwd M hM ij.2)).y)
    (fun ij => rfl) (fun ij => rfl) (fun ij => rfl) (fun ij => rfl)
  have hz := scalar_diffuse2D N M hN hM μ hμ0 hμ1
    (fun ij => (L.vel ij).z) (fun ij => (L.vel (fwd N hN ij.1, ij.2)).z)
    (fun ij => (L.vel (bwd N hN ij.1, ij.2)).z)
    (fun ij => (L.vel (ij.1, fwd M hM ij.2)).z)
    (fun ij => (L.vel (ij.1, bwd M hM ij.2)).z)
    (fun ij => rfl) (fun ij => rfl) (fun ij => rfl) (fun ij => rfl)
  have hexpand : totalEnergy2D N M (diffuse2D N M hN hM μ L)
      = ∑ ij, ((1 - 4 * μ) * (L.vel ij).x
          + μ * (L.vel (fwd N hN ij.1, ij.2)).x
          + μ * (L.vel (bwd N hN ij.1, ij.2)).x
          + μ * (L.vel (ij.1, fwd M hM ij.2)).x
          + μ * (L.vel (ij.1, bwd M hM ij.2)).x) ^ 2
        + ∑ ij, ((1 - 4 * μ) * (L.vel ij).y
          + μ * (L.vel (fwd N hN ij.1, ij.2)).y
          + μ * (L.vel (bwd N hN ij.1, ij.2)).y
          + μ * (L.vel (ij.1, fwd M hM ij.2)).y
          + μ * (L.vel (ij.1, bwd M hM ij.2)).y) ^ 2
        + ∑ ij, ((1 - 4 * μ) * (L.vel ij).z
          + μ * (L.vel (fwd N hN ij.1, ij.2)).z
          + μ * (L.vel (bwd N hN ij.1, ij.2)).z
          + μ * (L.vel (ij.1, fwd M hM ij.2)).z
          + μ * (L.vel (ij.1, bwd M hM ij.2)).z) ^ 2 := by
    have rfl_expand : totalEnergy2D N M (diffuse2D N M hN hM μ L)
        = ∑ ij, ((((1 - 4 * μ) * (L.vel ij).x
            + μ * (L.vel (fwd N hN ij.1, ij.2)).x
            + μ * (L.vel (bwd N hN ij.1, ij.2)).x
            + μ * (L.vel (ij.1, fwd M hM ij.2)).x
            + μ * (L.vel (ij.1, bwd M hM ij.2)).x) ^ 2
          + ((1 - 4 * μ) * (L.vel ij).y
            + μ * (L.vel (fwd N hN ij.1, ij.2)).y
            + μ * (L.vel (bwd N hN ij.1, ij.2)).y
            + μ * (L.vel (ij.1, fwd M hM ij.2)).y
            + μ * (L.vel (ij.1, bwd M hM ij.2)).y) ^ 2)
          + ((1 - 4 * μ) * (L.vel ij).z
            + μ * (L.vel (fwd N hN ij.1, ij.2)).z
            + μ * (L.vel (bwd N hN ij.1, ij.2)).z
            + μ * (L.vel (ij.1, fwd M hM ij.2)).z
            + μ * (L.vel (ij.1, bwd M hM ij.2)).z) ^ 2) := rfl
    rw [rfl_expand]
    simp only [Finset.sum_add_distrib]
  have hexpand0 : totalEnergy2D N M L
      = ∑ ij, ((L.vel ij).x) ^ 2 + ∑ ij, ((L.vel ij).y) ^ 2
        + ∑ ij, ((L.vel ij).z) ^ 2 := by
    have rfl_expand0 : totalEnergy2D N M L
        = ∑ ij, ((((L.vel ij).x) ^ 2 + ((L.vel ij).y) ^ 2)
          + ((L.vel ij).z) ^ 2) := rfl
    rw [rfl_expand0]
    simp only [Finset.sum_add_distrib]
  rw [hexpand, hexpand0]
  linarith

/-- Two-sided axis shift for bilinear product sums (X axis). -/
lemma sum_prod_fwd_to_bwdX (N M : ℕ) (hN : 0 < N)
    (F : Fin N × Fin M → Fin N × Fin M → ℚ) :
    ∑ ij, F ij (fwd N hN ij.1, ij.2)
      = ∑ ij, F (bwd N hN ij.1, ij.2) ij := by
  have r : ∀ ij, F ij (fwd N hN ij.1, ij.2)
      = F (bwd N hN (fwd N hN ij.1), ij.2) (fwd N hN ij.1, ij.2) := by
    intro ij
    rw [show bwd N hN (fwd N hN ij.1) = ij.1 from
      (shiftPerm N hN).left_inv ij.1]
  rw [Finset.sum_congr rfl (fun ij _ => r ij)]
  exact Equiv.sum_comp (shiftPermX N M hN)
    (fun kl => F (bwd N hN kl.1, kl.2) kl)

/-- Two-sided axis shift for bilinear product sums (Y axis). -/
lemma sum_prod_fwd_to_bwdY (N M : ℕ) (hM : 0 < M)
    (F : Fin N × Fin M → Fin N × Fin M → ℚ) :
    ∑ ij, F ij (ij.1, fwd M hM ij.2)
      = ∑ ij, F (ij.1, bwd M hM ij.2) ij := by
  have r : ∀ ij, F ij (ij.1, fwd M hM ij.2)
      = F (ij.1, bwd M hM (fwd M hM ij.2)) (ij.1, fwd M hM ij.2) := by
    intro ij
    rw [show bwd M hM (fwd M hM ij.2) = ij.2 from
      (shiftPerm M hM).left_inv ij.2]
  rw [Finset.sum_congr rfl (fun ij _ => r ij)]
  exact Equiv.sum_comp (shiftPermY N M hM)
    (fun kl => F (kl.1, bwd M hM kl.2) kl)

/-- Forward-difference pressure gradients (kept structure). -/
def gradX (N M : ℕ) (hN : 0 < N) (p : Fin N × Fin M → ℚ)
    (ij : Fin N × Fin M) : ℚ :=
  p (fwd N hN ij.1, ij.2) - p ij

def gradY (N M : ℕ) (hM : 0 < M) (p : Fin N × Fin M → ℚ)
    (ij : Fin N × Fin M) : ℚ :=
  p (ij.1, fwd M hM ij.2) - p ij

/-- Backward-difference divergence (adjoint pair). -/
def bdiv2D (N M : ℕ) (hN : 0 < N) (hM : 0 < M)
    (u : Fin N × Fin M → CellVelocity) (ij : Fin N × Fin M) : ℚ :=
  ((u ij).x - (u (bwd N hN ij.1, ij.2)).x)
    + ((u ij).y - (u (ij.1, bwd M hM ij.2)).y)

/-- Summation by parts I in 2D (both axes, proved). -/
lemma sbp_grad_div2D (N M : ℕ) (hN : 0 < N) (hM : 0 < M)
    (u : Fin N × Fin M → CellVelocity) (p : Fin N × Fin M → ℚ) :
    (∑ ij, (u ij).x * gradX N M hN p ij)
        + (∑ ij, (u ij).y * gradY N M hM p ij)
      = -∑ ij, bdiv2D N M hN hM u ij * p ij := by
  have hX : ∑ ij, (u ij).x * gradX N M hN p ij
      = ∑ ij, (u (bwd N hN ij.1, ij.2)).x * p ij
        - ∑ ij, (u ij).x * p ij := by
    have e : ∀ ij ∈ (Finset.univ : Finset (Fin N × Fin M)),
        (u ij).x * gradX N M hN p ij
          = (u ij).x * p (fwd N hN ij.1, ij.2) - (u ij).x * p ij := by
      intro ij _
      simp only [gradX, mul_sub]
    rw [Finset.sum_congr rfl e, Finset.sum_sub_distrib]
    have hstep := sum_prod_fwd_to_bwdX N M hN (fun a b => (u a).x * p b)
    have r1 : (∑ ij, (u ij).x * p (fwd N hN ij.1, ij.2))
        = ∑ ij, (fun a b => (u a).x * p b) ij (fwd N hN ij.1, ij.2) := rfl
    have r2 : (∑ ij, (fun a b => (u a).x * p b) (bwd N hN ij.1, ij.2) ij)
        = ∑ ij, (u (bwd N hN ij.1, ij.2)).x * p ij := rfl
    rw [r1, hstep, r2]
  have hY : ∑ ij, (u ij).y * gradY N M hM p ij
      = ∑ ij, (u (ij.1, bwd M hM ij.2)).y * p ij
        - ∑ ij, (u ij).y * p ij := by
    have e : ∀ ij ∈ (Finset.univ : Finset (Fin N × Fin M)),
        (u ij).y * gradY N M hM p ij
          = (u ij).y * p (ij.1, fwd M hM ij.2) - (u ij).y * p ij := by
      intro ij _
      simp only [gradY, mul_sub]
    rw [Finset.sum_congr rfl e, Finset.sum_sub_distrib]
    have hstep := sum_prod_fwd_to_bwdY N M hM (fun a b => (u a).y * p b)
    have r1 : (∑ ij, (u ij).y * p (ij.1, fwd M hM ij.2))
        = ∑ ij, (fun a b => (u a).y * p b) ij (ij.1, fwd M hM ij.2) := rfl
    have r2 : (∑ ij, (fun a b => (u a).y * p b) (ij.1, bwd M hM ij.2) ij)
        = ∑ ij, (u (ij.1, bwd M hM ij.2)).y * p ij := rfl
    rw [r1, hstep, r2]
  rw [hX, hY]
  simp only [bdiv2D, add_mul, sub_mul, Finset.sum_add_distrib,
    Finset.sum_sub_distrib]
  ring

/-- Axis Laplacians and their sum. -/
def lapX (N M : ℕ) (hN : 0 < N) (p : Fin N × Fin M → ℚ)
    (ij : Fin N × Fin M) : ℚ :=
  p (fwd N hN ij.1, ij.2) - 2 * p ij + p (bwd N hN ij.1, ij.2)

def lapY (N M : ℕ) (hM : 0 < M) (p : Fin N × Fin M → ℚ)
    (ij : Fin N × Fin M) : ℚ :=
  p (ij.1, fwd M hM ij.2) - 2 * p ij + p (ij.1, bwd M hM ij.2)

def lap2D (N M : ℕ) (hN : 0 < N) (hM : 0 < M) (p : Fin N × Fin M → ℚ)
    (ij : Fin N × Fin M) : ℚ :=
  lapX N M hN p ij + lapY N M hM p ij

/-- X-axis Laplacian is negative-semidefinite (proved). -/
lemma sbp_lap_negX (N M : ℕ) (hN : 0 < N) (p : Fin N × Fin M → ℚ) :
    ∑ ij, lapX N M hN p ij * p ij = -∑ ij, (gradX N M hN p ij) ^ 2 := by
  have e1 : ∑ ij, p (fwd N hN ij.1, ij.2) * p ij
      = ∑ ij, p ij * p (fwd N hN ij.1, ij.2) :=
    Finset.sum_congr rfl (fun ij _ => mul_comm _ _)
  have e2 : ∑ ij, p (bwd N hN ij.1, ij.2) * p ij
      = ∑ ij, p ij * p (fwd N hN ij.1, ij.2) := by
    have hstep := sum_prod_fwd_to_bwdX N M hN (fun a b => p a * p b)
    have r1 : (∑ ij, p (bwd N hN ij.1, ij.2) * p ij)
        = ∑ ij, (fun a b => p a * p b) (bwd N hN ij.1, ij.2) ij := rfl
    have r2 : (∑ ij, (fun a b => p a * p b) ij (fwd N hN ij.1, ij.2))
        = ∑ ij, p ij * p (fwd N hN ij.1, ij.2) := rfl
    rw [r1, ← hstep, r2]
  have e3 : ∑ ij : Fin N × Fin M, (p (fwd N hN ij.1, ij.2)) ^ 2
      = ∑ ij : Fin N × Fin M, (p ij) ^ 2 :=
    sum_prod_fst N M hN (fun i j => (p (i, j)) ^ 2)
  have e4 : ∀ ij : Fin N × Fin M, (gradX N M hN p ij) ^ 2
      = (p (fwd N hN ij.1, ij.2)) ^ 2
        - 2 * (p (fwd N hN ij.1, ij.2) * p ij) + (p ij) ^ 2 := by
    intro ij
    simp only [gradX]
    ring
  have e5 : ∀ ij : Fin N × Fin M, lapX N M hN p ij * p ij
      = p (fwd N hN ij.1, ij.2) * p ij - 2 * (p ij) ^ 2
        + p (bwd N hN ij.1, ij.2) * p ij := by
    intro ij
    simp only [lapX]
    ring
  calc ∑ ij, lapX N M hN p ij * p ij
      = ∑ ij, (p (fwd N hN ij.1, ij.2) * p ij - 2 * (p ij) ^ 2
          + p (bwd N hN ij.1, ij.2) * p ij) :=
        Finset.sum_congr rfl (fun ij _ => e5 ij)
    _ = ∑ ij, p (fwd N hN ij.1, ij.2) * p ij - ∑ ij, (2 * (p ij) ^ 2)
          + ∑ ij, p (bwd N hN ij.1, ij.2) * p ij := by
        simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib]
    _ = 2 * ∑ ij, p ij * p (fwd N hN ij.1, ij.2)
          - 2 * ∑ ij, (p ij) ^ 2 := by
        have sB : ∑ ij, (2 * (p ij) ^ 2) = 2 * ∑ ij, (p ij) ^ 2 :=
          (Finset.mul_sum _ _ _).symm
        rw [e1, e2, sB]
        ring
    _ = -∑ ij, (gradX N M hN p ij) ^ 2 := by
        have g1 : ∑ ij, (gradX N M hN p ij) ^ 2
            = ∑ ij, ((p (fwd N hN ij.1, ij.2)) ^ 2
              - 2 * (p (fwd N hN ij.1, ij.2) * p ij))
              + ∑ ij, (p ij) ^ 2 := by
          have hcongr : ∀ ij ∈ (Finset.univ : Finset (Fin N × Fin M)),
              (gradX N M hN p ij) ^ 2
                = (p (fwd N hN ij.1, ij.2)) ^ 2
                  - 2 * (p (fwd N hN ij.1, ij.2) * p ij) + (p ij) ^ 2 :=
            fun ij _ => e4 ij
          rw [Finset.sum_congr rfl hcongr]
          simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib]
        rw [g1]
        have g2 : ∑ ij : Fin N × Fin M, ((p (fwd N hN ij.1, ij.2)) ^ 2
            - 2 * (p (fwd N hN ij.1, ij.2) * p ij))
            = ∑ ij : Fin N × Fin M, (p (fwd N hN ij.1, ij.2)) ^ 2
              - ∑ ij : Fin N × Fin M,
                (2 * (p (fwd N hN ij.1, ij.2) * p ij)) :=
          Finset.sum_sub_distrib _ _
        rw [g2, e3]
        have sD : ∑ ij : Fin N × Fin M, (2 * (p (fwd N hN ij.1, ij.2) * p ij))
            = 2 * ∑ ij, p (fwd N hN ij.1, ij.2) * p ij :=
          (Finset.mul_sum _ _ _).symm
        rw [sD, e1]
        ring

/-- Y-axis Laplacian is negative-semidefinite (proved). -/
lemma sbp_lap_negY (N M : ℕ) (hM : 0 < M) (p : Fin N × Fin M → ℚ) :
    ∑ ij, lapY N M hM p ij * p ij = -∑ ij, (gradY N M hM p ij) ^ 2 := by
  have e1 : ∑ ij, p (ij.1, fwd M hM ij.2) * p ij
      = ∑ ij, p ij * p (ij.1, fwd M hM ij.2) :=
    Finset.sum_congr rfl (fun ij _ => mul_comm _ _)
  have e2 : ∑ ij, p (ij.1, bwd M hM ij.2) * p ij
      = ∑ ij, p ij * p (ij.1, fwd M hM ij.2) := by
    have hstep := sum_prod_fwd_to_bwdY N M hM (fun a b => p a * p b)
    have r1 : (∑ ij, p (ij.1, bwd M hM ij.2) * p ij)
        = ∑ ij, (fun a b => p a * p b) (ij.1, bwd M hM ij.2) ij := rfl
    have r2 : (∑ ij, (fun a b => p a * p b) ij (ij.1, fwd M hM ij.2))
        = ∑ ij, p ij * p (ij.1, fwd M hM ij.2) := rfl
    rw [r1, ← hstep, r2]
  have e3 : ∑ ij : Fin N × Fin M, (p (ij.1, fwd M hM ij.2)) ^ 2
      = ∑ ij : Fin N × Fin M, (p ij) ^ 2 :=
    sum_prod_snd N M hM (fun i j => (p (i, j)) ^ 2)
  have e4 : ∀ ij : Fin N × Fin M, (gradY N M hM p ij) ^ 2
      = (p (ij.1, fwd M hM ij.2)) ^ 2
        - 2 * (p (ij.1, fwd M hM ij.2) * p ij) + (p ij) ^ 2 := by
    intro ij
    simp only [gradY]
    ring
  have e5 : ∀ ij : Fin N × Fin M, lapY N M hM p ij * p ij
      = p (ij.1, fwd M hM ij.2) * p ij - 2 * (p ij) ^ 2
        + p (ij.1, bwd M hM ij.2) * p ij := by
    intro ij
    simp only [lapY]
    ring
  calc ∑ ij, lapY N M hM p ij * p ij
      = ∑ ij, (p (ij.1, fwd M hM ij.2) * p ij - 2 * (p ij) ^ 2
          + p (ij.1, bwd M hM ij.2) * p ij) :=
        Finset.sum_congr rfl (fun ij _ => e5 ij)
    _ = ∑ ij, p (ij.1, fwd M hM ij.2) * p ij - ∑ ij, (2 * (p ij) ^ 2)
          + ∑ ij, p (ij.1, bwd M hM ij.2) * p ij := by
        simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib]
    _ = 2 * ∑ ij, p ij * p (ij.1, fwd M hM ij.2)
          - 2 * ∑ ij, (p ij) ^ 2 := by
        have sB : ∑ ij, (2 * (p ij) ^ 2) = 2 * ∑ ij, (p ij) ^ 2 :=
          (Finset.mul_sum _ _ _).symm
        rw [e1, e2, sB]
        ring
    _ = -∑ ij, (gradY N M hM p ij) ^ 2 := by
        have g1 : ∑ ij, (gradY N M hM p ij) ^ 2
            = ∑ ij, ((p (ij.1, fwd M hM ij.2)) ^ 2
              - 2 * (p (ij.1, fwd M hM ij.2) * p ij))
              + ∑ ij, (p ij) ^ 2 := by
          have hcongr : ∀ ij ∈ (Finset.univ : Finset (Fin N × Fin M)),
              (gradY N M hM p ij) ^ 2
                = (p (ij.1, fwd M hM ij.2)) ^ 2
                  - 2 * (p (ij.1, fwd M hM ij.2) * p ij) + (p ij) ^ 2 :=
            fun ij _ => e4 ij
          rw [Finset.sum_congr rfl hcongr]
          simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib]
        rw [g1]
        have g2 : ∑ ij : Fin N × Fin M, ((p (ij.1, fwd M hM ij.2)) ^ 2
            - 2 * (p (ij.1, fwd M hM ij.2) * p ij))
            = ∑ ij : Fin N × Fin M, (p (ij.1, fwd M hM ij.2)) ^ 2
              - ∑ ij : Fin N × Fin M,
                (2 * (p (ij.1, fwd M hM ij.2) * p ij)) :=
          Finset.sum_sub_distrib _ _
        rw [g2, e3]
        have sD : ∑ ij : Fin N × Fin M, (2 * (p (ij.1, fwd M hM ij.2) * p ij))
            = 2 * ∑ ij, p (ij.1, fwd M hM ij.2) * p ij :=
          (Finset.mul_sum _ _ _).symm
        rw [sD, e1]
        ring

/-- Full 2D Laplacian is negative-semidefinite (both axes). -/
lemma sbp_lap_neg2D (N M : ℕ) (hN : 0 < N) (hM : 0 < M)
    (p : Fin N × Fin M → ℚ) :
    ∑ ij, lap2D N M hN hM p ij * p ij
      = -(∑ ij, (gradX N M hN p ij) ^ 2
        + ∑ ij, (gradY N M hM p ij) ^ 2) := by
  have hX := sbp_lap_negX N M hN p
  have hY := sbp_lap_negY N M hM p
  have hsplit : ∀ ij ∈ (Finset.univ : Finset (Fin N × Fin M)),
      lap2D N M hN hM p ij * p ij
        = lapX N M hN p ij * p ij + lapY N M hM p ij * p ij := by
    intro ij _
    simp only [lap2D, add_mul]
  rw [Finset.sum_congr rfl hsplit, Finset.sum_add_distrib, hX, hY]
  ring

/-- 2D Chorin projection (x via gradX, y via gradY). -/
def project2D (N M : ℕ) (hN : 0 < N) (hM : 0 < M) (c : ℚ)
    (L : FluidLattice2D N M) (p : Fin N × Fin M → ℚ) : FluidLattice2D N M :=
  ⟨fun ij => ⟨(L.vel ij).x - c * gradX N M hN p ij,
    (L.vel ij).y - c * gradY N M hM p ij, (L.vel ij).z⟩⟩

/-- 2D projection dissipates energy under the solver contract. -/
lemma energy_project2D (N M : ℕ) (hN : 0 < N) (hM : 0 < M) (c C : ℚ)
    (hc : c * C = 1) (hC : 0 < C) (L : FluidLattice2D N M)
    (p : Fin N × Fin M → ℚ)
    (hPoisson : ∀ ij, lap2D N M hN hM p ij
      = C * bdiv2D N M hN hM L.vel ij) :
    totalEnergy2D N M (project2D N M hN hM c L p)
      ≤ totalEnergy2D N M L := by
  have hCne : C ≠ 0 := hC.ne'
  have hSnn : 0 ≤ ∑ ij, (gradX N M hN p ij) ^ 2
      + ∑ ij, (gradY N M hM p ij) ^ 2 := by
    apply add_nonneg
    · exact Finset.sum_nonneg (fun ij _ => sq_nonneg _)
    · exact Finset.sum_nonneg (fun ij _ => sq_nonneg _)
  have hlink2D : (∑ ij, (L.vel ij).x * gradX N M hN p ij)
        + (∑ ij, (L.vel ij).y * gradY N M hM p ij)
      = (1 / C) * (∑ ij, (gradX N M hN p ij) ^ 2
        + ∑ ij, (gradY N M hM p ij) ^ 2) := by
    have h1 := sbp_grad_div2D N M hN hM L.vel p
    have h2 := sbp_lap_neg2D N M hN hM p
    have h3 : ∑ ij, bdiv2D N M hN hM L.vel ij * p ij
        = (1 / C) * ∑ ij, lap2D N M hN hM p ij * p ij := by
      have hper : ∀ ij : Fin N × Fin M, bdiv2D N M hN hM L.vel ij * p ij
          = (1 / C) * (lap2D N M hN hM p ij * p ij) := by
        intro ij
        rw [hPoisson ij]
        field_simp
      rw [Finset.sum_congr rfl (fun ij _ => hper ij), ← Finset.mul_sum]
    rw [h1, h3, h2]
    ring
  have hE : totalEnergy2D N M (project2D N M hN hM c L p)
      = totalEnergy2D N M L - c ^ 2 * (∑ ij, (gradX N M hN p ij) ^ 2
        + ∑ ij, (gradY N M hM p ij) ^ 2) := by
    have hexpand : totalEnergy2D N M (project2D N M hN hM c L p)
        = ∑ ij, ((L.vel ij).x - c * gradX N M hN p ij) ^ 2
          + ∑ ij, ((L.vel ij).y - c * gradY N M hM p ij) ^ 2
          + ∑ ij, ((L.vel ij).z) ^ 2 := by
      have rfl_expand : totalEnergy2D N M (project2D N M hN hM c L p)
          = ∑ ij, ((((L.vel ij).x - c * gradX N M hN p ij) ^ 2
            + ((L.vel ij).y - c * gradY N M hM p ij) ^ 2)
            + ((L.vel ij).z) ^ 2) := rfl
      rw [rfl_expand]
      simp only [Finset.sum_add_distrib]
    have hexpand0 : totalEnergy2D N M L
        = ∑ ij, ((L.vel ij).x) ^ 2 + ∑ ij, ((L.vel ij).y) ^ 2
          + ∑ ij, ((L.vel ij).z) ^ 2 := by
      have rfl_expand0 : totalEnergy2D N M L
          = ∑ ij, ((((L.vel ij).x) ^ 2 + ((L.vel ij).y) ^ 2)
            + ((L.vel ij).z) ^ 2) := rfl
      rw [rfl_expand0]
      simp only [Finset.sum_add_distrib]
    rw [hexpand, hexpand0]
    have hx : ∀ ij : Fin N × Fin M,
        ((L.vel ij).x - c * gradX N M hN p ij) ^ 2
          = ((L.vel ij).x) ^ 2 - 2 * c * ((L.vel ij).x * gradX N M hN p ij)
            + c ^ 2 * (gradX N M hN p ij) ^ 2 := by
      intro ij
      ring
    have hy : ∀ ij : Fin N × Fin M,
        ((L.vel ij).y - c * gradY N M hM p ij) ^ 2
          = ((L.vel ij).y) ^ 2 - 2 * c * ((L.vel ij).y * gradY N M hM p ij)
            + c ^ 2 * (gradY N M hM p ij) ^ 2 := by
      intro ij
      ring
    rw [Finset.sum_congr rfl (fun ij _ => hx ij),
      Finset.sum_congr rfl (fun ij _ => hy ij)]
    simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib]
    have t1x : ∑ ij, (2 * c * ((L.vel ij).x * gradX N M hN p ij))
        = 2 * c * ∑ ij, (L.vel ij).x * gradX N M hN p ij :=
      (Finset.mul_sum _ _ _).symm
    have t1y : ∑ ij, (2 * c * ((L.vel ij).y * gradY N M hM p ij))
        = 2 * c * ∑ ij, (L.vel ij).y * gradY N M hM p ij :=
      (Finset.mul_sum _ _ _).symm
    have t2x : ∑ ij, (c ^ 2 * (gradX N M hN p ij) ^ 2)
        = c ^ 2 * ∑ ij, (gradX N M hN p ij) ^ 2 :=
      (Finset.mul_sum _ _ _).symm
    have t2y : ∑ ij, (c ^ 2 * (gradY N M hM p ij) ^ 2)
        = c ^ 2 * ∑ ij, (gradY N M hM p ij) ^ 2 :=
      (Finset.mul_sum _ _ _).symm
    rw [t1x, t1y, t2x, t2y]
    have hC : 2 * c * (∑ ij, (L.vel ij).x * gradX N M hN p ij)
        + 2 * c * (∑ ij, (L.vel ij).y * gradY N M hM p ij)
        = 2 * (c * c) * (∑ ij, (gradX N M hN p ij) ^ 2
          + ∑ ij, (gradY N M hM p ij) ^ 2) := by
      have hcC : c * (1 / C) = c ^ 2 := by
        field_simp
        nlinarith [hc]
      have step3 : (2 : ℚ) * (c * (1 / C)) = 2 * (c * c) := by
        nlinarith [hcC]
      calc 2 * c * (∑ ij, (L.vel ij).x * gradX N M hN p ij)
            + 2 * c * (∑ ij, (L.vel ij).y * gradY N M hM p ij)
          = 2 * c * ((∑ ij, (L.vel ij).x * gradX N M hN p ij)
            + (∑ ij, (L.vel ij).y * gradY N M hM p ij)) := by ring
        _ = 2 * c * ((1 / C) * (∑ ij, (gradX N M hN p ij) ^ 2
            + ∑ ij, (gradY N M hM p ij) ^ 2)) := by rw [hlink2D]
        _ = 2 * (c * (1 / C)) * (∑ ij, (gradX N M hN p ij) ^ 2
            + ∑ ij, (gradY N M hM p ij) ^ 2) := by ring
        _ = 2 * (c * c) * (∑ ij, (gradX N M hN p ij) ^ 2
            + ∑ ij, (gradY N M hM p ij) ^ 2) := by rw [step3]
    linear_combination -hC
  have hdrop : 0 ≤ c ^ 2 * (∑ ij, (gradX N M hN p ij) ^ 2
      + ∑ ij, (gradY N M hM p ij) ^ 2) :=
    mul_nonneg (sq_nonneg _) hSnn
  linarith

/-- 2D Godunov predictor and full fractional step. -/
def godunov2D (N M : ℕ) (hN : 0 < N) (hM : 0 < M) (μ : ℚ)
    (L : FluidLattice2D N M) : FluidLattice2D N M :=
  diffuse2D N M hN hM μ (advect2D N M hN L)

def full_ns_step2D (N M : ℕ) (hN : 0 < N) (hM : 0 < M) (μ c : ℚ)
    (L : FluidLattice2D N M) (p : Fin N × Fin M → ℚ) : FluidLattice2D N M :=
  project2D N M hN hM c (godunov2D N M hN hM μ L) p

/-- Main theorem in 2D: one full step never increases energy. -/
theorem energy_monotonic_decay2D (N M : ℕ) (hN : 0 < N) (hM : 0 < M)
    (μ c C : ℚ) (hμ0 : 0 ≤ μ) (hμ1 : 4 * μ ≤ 1) (hc : c * C = 1)
    (hC : 0 < C) (L : FluidLattice2D N M) (p : Fin N × Fin M → ℚ)
    (hPoisson : ∀ ij, lap2D N M hN hM p ij
      = C * bdiv2D N M hN hM (godunov2D N M hN hM μ L).vel ij) :
    totalEnergy2D N M (full_ns_step2D N M hN hM μ c L p)
      ≤ totalEnergy2D N M L :=
  le_trans (energy_project2D N M hN hM c C hc hC _ _ hPoisson)
    (le_trans (energy_diffuse2D N M hN hM μ hμ0 hμ1 _)
      (le_of_eq (energy_advect2D N M hN _)))

/-! ## 3D periodic lattice (stencil-7, all three channels corrected).

Index type `(Fin N × Fin M) × Fin K`, addressed as `ijk.1.1`,
`ijk.1.2`, `ijk.2`. Same forward-gradient structure, one more axis. -/

/-- Axis shifts as genuine permutations (nested `prodCongr`). -/
def shiftPerm3DX (N M K : ℕ) (hN : 0 < N)
    : Equiv.Perm ((Fin N × Fin M) × Fin K) :=
  Equiv.prodCongr (Equiv.prodCongr (shiftPerm N hN) (Equiv.refl _))
    (Equiv.refl _)

def shiftPerm3DY (N M K : ℕ) (hM : 0 < M)
    : Equiv.Perm ((Fin N × Fin M) × Fin K) :=
  Equiv.prodCongr (Equiv.prodCongr (Equiv.refl _) (shiftPerm M hM))
    (Equiv.refl _)

def shiftPerm3DZ (N M K : ℕ) (hK : 0 < K)
    : Equiv.Perm ((Fin N × Fin M) × Fin K) :=
  Equiv.prodCongr (Equiv.refl _) (shiftPerm K hK)

/-- Product-sum reindexing along each axis, both directions. -/
lemma sum_3d_fst (N M K : ℕ) (hN : 0 < N) (F : Fin N → Fin M → Fin K → ℚ) :
    ∑ ijk : (Fin N × Fin M) × Fin K, F (fwd N hN ijk.1.1) ijk.1.2 ijk.2
      = ∑ ijk : (Fin N × Fin M) × Fin K, F ijk.1.1 ijk.1.2 ijk.2 :=
  sum_perm (shiftPerm3DX N M K hN) _ _ (fun _ => rfl)

lemma sum_3d_fst_bwd (N M K : ℕ) (hN : 0 < N)
    (F : Fin N → Fin M → Fin K → ℚ) :
    ∑ ijk : (Fin N × Fin M) × Fin K, F (bwd N hN ijk.1.1) ijk.1.2 ijk.2
      = ∑ ijk : (Fin N × Fin M) × Fin K, F ijk.1.1 ijk.1.2 ijk.2 :=
  sum_perm (shiftPerm3DX N M K hN).symm _ _ (fun _ => rfl)

lemma sum_3d_snd (N M K : ℕ) (hM : 0 < M) (F : Fin N → Fin M → Fin K → ℚ) :
    ∑ ijk : (Fin N × Fin M) × Fin K, F ijk.1.1 (fwd M hM ijk.1.2) ijk.2
      = ∑ ijk : (Fin N × Fin M) × Fin K, F ijk.1.1 ijk.1.2 ijk.2 :=
  sum_perm (shiftPerm3DY N M K hM) _ _ (fun _ => rfl)

lemma sum_3d_snd_bwd (N M K : ℕ) (hM : 0 < M)
    (F : Fin N → Fin M → Fin K → ℚ) :
    ∑ ijk : (Fin N × Fin M) × Fin K, F ijk.1.1 (bwd M hM ijk.1.2) ijk.2
      = ∑ ijk : (Fin N × Fin M) × Fin K, F ijk.1.1 ijk.1.2 ijk.2 :=
  sum_perm (shiftPerm3DY N M K hM).symm _ _ (fun _ => rfl)

lemma sum_3d_trd (N M K : ℕ) (hK : 0 < K) (F : Fin N → Fin M → Fin K → ℚ) :
    ∑ ijk : (Fin N × Fin M) × Fin K, F ijk.1.1 ijk.1.2 (fwd K hK ijk.2)
      = ∑ ijk : (Fin N × Fin M) × Fin K, F ijk.1.1 ijk.1.2 ijk.2 :=
  sum_perm (shiftPerm3DZ N M K hK) _ _ (fun _ => rfl)

lemma sum_3d_trd_bwd (N M K : ℕ) (hK : 0 < K)
    (F : Fin N → Fin M → Fin K → ℚ) :
    ∑ ijk : (Fin N × Fin M) × Fin K, F ijk.1.1 ijk.1.2 (bwd K hK ijk.2)
      = ∑ ijk : (Fin N × Fin M) × Fin K, F ijk.1.1 ijk.1.2 ijk.2 :=
  sum_perm (shiftPerm3DZ N M K hK).symm _ _ (fun _ => rfl)

/-- 3D lattice, energy, and x-advection (invariance proved). -/
structure FluidLattice3D (N M K : ℕ) where
  vel : (Fin N × Fin M) × Fin K → CellVelocity

def totalEnergy3D (N M K : ℕ) (L : FluidLattice3D N M K) : ℚ :=
  ∑ ijk, cellEnergy (L.vel ijk)

def advect3D (N M K : ℕ) (hN : 0 < N) (L : FluidLattice3D N M K) :
    FluidLattice3D N M K :=
  ⟨fun ijk => L.vel ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)⟩

lemma energy_advect3D (N M K : ℕ) (hN : 0 < N) (L : FluidLattice3D N M K) :
    totalEnergy3D N M K (advect3D N M K hN L) = totalEnergy3D N M K L := by
  unfold totalEnergy3D advect3D
  simp only
  exact sum_3d_fst N M K hN (fun i j k => cellEnergy (L.vel ((i, j), k)))

/-- Two-sided shifts for bilinear product sums (X axis). -/
lemma sum_3d_fwd_to_bwdX (N M K : ℕ) (hN : 0 < N)
    (F : ((Fin N × Fin M) × Fin K) → ((Fin N × Fin M) × Fin K) → ℚ) :
    ∑ ijk, F ijk ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)
      = ∑ ijk, F ((bwd N hN ijk.1.1, ijk.1.2), ijk.2) ijk := by
  have r : ∀ ijk, F ijk ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)
      = F ((bwd N hN (fwd N hN ijk.1.1), ijk.1.2), ijk.2)
        ((fwd N hN ijk.1.1, ijk.1.2), ijk.2) := by
    intro ijk
    rw [show bwd N hN (fwd N hN ijk.1.1) = ijk.1.1 from
      (shiftPerm N hN).left_inv ijk.1.1]
  rw [Finset.sum_congr rfl (fun ijk _ => r ijk)]
  exact Equiv.sum_comp (shiftPerm3DX N M K hN)
    (fun kl => F ((bwd N hN kl.1.1, kl.1.2), kl.2) kl)

/-- Two-sided shifts for bilinear product sums (Y axis). -/
lemma sum_3d_fwd_to_bwdY (N M K : ℕ) (hM : 0 < M)
    (F : ((Fin N × Fin M) × Fin K) → ((Fin N × Fin M) × Fin K) → ℚ) :
    ∑ ijk, F ijk ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)
      = ∑ ijk, F ((ijk.1.1, bwd M hM ijk.1.2), ijk.2) ijk := by
  have r : ∀ ijk, F ijk ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)
      = F ((ijk.1.1, bwd M hM (fwd M hM ijk.1.2)), ijk.2)
        ((ijk.1.1, fwd M hM ijk.1.2), ijk.2) := by
    intro ijk
    rw [show bwd M hM (fwd M hM ijk.1.2) = ijk.1.2 from
      (shiftPerm M hM).left_inv ijk.1.2]
  rw [Finset.sum_congr rfl (fun ijk _ => r ijk)]
  exact Equiv.sum_comp (shiftPerm3DY N M K hM)
    (fun kl => F ((kl.1.1, bwd M hM kl.1.2), kl.2) kl)

/-- Two-sided shifts for bilinear product sums (Z axis). -/
lemma sum_3d_fwd_to_bwdZ (N M K : ℕ) (hK : 0 < K)
    (F : ((Fin N × Fin M) × Fin K) → ((Fin N × Fin M) × Fin K) → ℚ) :
    ∑ ijk, F ijk ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)
      = ∑ ijk, F ((ijk.1.1, ijk.1.2), bwd K hK ijk.2) ijk := by
  have r : ∀ ijk, F ijk ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)
      = F ((ijk.1.1, ijk.1.2), bwd K hK (fwd K hK ijk.2))
        ((ijk.1.1, ijk.1.2), fwd K hK ijk.2) := by
    intro ijk
    rw [show bwd K hK (fwd K hK ijk.2) = ijk.2 from
      (shiftPerm K hK).left_inv ijk.2]
  rw [Finset.sum_congr rfl (fun ijk _ => r ijk)]
  exact Equiv.sum_comp (shiftPerm3DZ N M K hK)
    (fun kl => F ((kl.1.1, kl.1.2), bwd K hK kl.2) kl)

/-- Seven-point stencil diffusion with explicit CFL bound. -/
def diffuse3D (N M K : ℕ) (hN : 0 < N) (hM : 0 < M) (hK : 0 < K) (μ : ℚ)
    (L : FluidLattice3D N M K) : FluidLattice3D N M K :=
  ⟨fun ijk =>
    ⟨(1 - 6 * μ) * (L.vel ijk).x
        + μ * (L.vel ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)).x
        + μ * (L.vel ((bwd N hN ijk.1.1, ijk.1.2), ijk.2)).x
        + μ * (L.vel ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)).x
        + μ * (L.vel ((ijk.1.1, bwd M hM ijk.1.2), ijk.2)).x
        + μ * (L.vel ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)).x
        + μ * (L.vel ((ijk.1.1, ijk.1.2), bwd K hK ijk.2)).x,
     (1 - 6 * μ) * (L.vel ijk).y
        + μ * (L.vel ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)).y
        + μ * (L.vel ((bwd N hN ijk.1.1, ijk.1.2), ijk.2)).y
        + μ * (L.vel ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)).y
        + μ * (L.vel ((ijk.1.1, bwd M hM ijk.1.2), ijk.2)).y
        + μ * (L.vel ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)).y
        + μ * (L.vel ((ijk.1.1, ijk.1.2), bwd K hK ijk.2)).y,
     (1 - 6 * μ) * (L.vel ijk).z
        + μ * (L.vel ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)).z
        + μ * (L.vel ((bwd N hN ijk.1.1, ijk.1.2), ijk.2)).z
        + μ * (L.vel ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)).z
        + μ * (L.vel ((ijk.1.1, bwd M hM ijk.1.2), ijk.2)).z
        + μ * (L.vel ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)).z
        + μ * (L.vel ((ijk.1.1, ijk.1.2), bwd K hK ijk.2)).z⟩⟩

/-- Seven-term variance identity: 6 center-neighbor + 15 neighbor pairs. -/
lemma convex_sq7 (μ a b c d e f g : ℚ) (hμ0 : 0 ≤ μ) (hμ1 : 6 * μ ≤ 1) :
    ((1 - 6 * μ) * a + μ * b + μ * c + μ * d + μ * e + μ * f + μ * g) ^ 2
      ≤ (1 - 6 * μ) * a ^ 2 + μ * b ^ 2 + μ * c ^ 2 + μ * d ^ 2
        + μ * e ^ 2 + μ * f ^ 2 + μ * g ^ 2 := by
  have hα : 0 ≤ 1 - 6 * μ := by linarith
  have w : 0 ≤ μ * (1 - 6 * μ) := mul_nonneg hμ0 hα
  have w2 : 0 ≤ μ * μ := mul_nonneg hμ0 hμ0
  have e1 : 0 ≤ μ * (1 - 6 * μ) * (a - b) ^ 2 :=
    mul_nonneg w (sq_nonneg _)
  have e2 : 0 ≤ μ * (1 - 6 * μ) * (a - c) ^ 2 :=
    mul_nonneg w (sq_nonneg _)
  have e3 : 0 ≤ μ * (1 - 6 * μ) * (a - d) ^ 2 :=
    mul_nonneg w (sq_nonneg _)
  have e4 : 0 ≤ μ * (1 - 6 * μ) * (a - e) ^ 2 :=
    mul_nonneg w (sq_nonneg _)
  have e5 : 0 ≤ μ * (1 - 6 * μ) * (a - f) ^ 2 :=
    mul_nonneg w (sq_nonneg _)
  have e6 : 0 ≤ μ * (1 - 6 * μ) * (a - g) ^ 2 :=
    mul_nonneg w (sq_nonneg _)
  have f1 : 0 ≤ μ * μ * (b - c) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have f2 : 0 ≤ μ * μ * (b - d) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have f3 : 0 ≤ μ * μ * (b - e) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have f4 : 0 ≤ μ * μ * (b - f) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have f5 : 0 ≤ μ * μ * (b - g) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have f6 : 0 ≤ μ * μ * (c - d) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have f7 : 0 ≤ μ * μ * (c - e) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have f8 : 0 ≤ μ * μ * (c - f) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have f9 : 0 ≤ μ * μ * (c - g) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have f10 : 0 ≤ μ * μ * (d - e) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have f11 : 0 ≤ μ * μ * (d - f) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have f12 : 0 ≤ μ * μ * (d - g) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have f13 : 0 ≤ μ * μ * (e - f) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have f14 : 0 ≤ μ * μ * (e - g) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have f15 : 0 ≤ μ * μ * (f - g) ^ 2 := mul_nonneg w2 (sq_nonneg _)
  have hsum : (1 - 6 * μ) * a ^ 2 + μ * b ^ 2 + μ * c ^ 2 + μ * d ^ 2
      + μ * e ^ 2 + μ * f ^ 2 + μ * g ^ 2
      - ((1 - 6 * μ) * a + μ * b + μ * c + μ * d + μ * e + μ * f
        + μ * g) ^ 2
      = μ * (1 - 6 * μ) * (a - b) ^ 2 + μ * (1 - 6 * μ) * (a - c) ^ 2
        + μ * (1 - 6 * μ) * (a - d) ^ 2 + μ * (1 - 6 * μ) * (a - e) ^ 2
        + μ * (1 - 6 * μ) * (a - f) ^ 2 + μ * (1 - 6 * μ) * (a - g) ^ 2
        + μ * μ * (b - c) ^ 2 + μ * μ * (b - d) ^ 2 + μ * μ * (b - e) ^ 2
        + μ * μ * (b - f) ^ 2 + μ * μ * (b - g) ^ 2 + μ * μ * (c - d) ^ 2
        + μ * μ * (c - e) ^ 2 + μ * μ * (c - f) ^ 2 + μ * μ * (c - g) ^ 2
        + μ * μ * (d - e) ^ 2 + μ * μ * (d - f) ^ 2 + μ * μ * (d - g) ^ 2
        + μ * μ * (e - f) ^ 2 + μ * μ * (e - g) ^ 2
        + μ * μ * (f - g) ^ 2 := by ring
  linarith

/-- Scalar 7-point diffusion contracts the sum of squares. -/
lemma scalar_diffuse3D (N M K : ℕ) (hN : 0 < N) (hM : 0 < M) (hK : 0 < K)
    (μ : ℚ) (hμ0 : 0 ≤ μ) (hμ1 : 6 * μ ≤ 1)
    (a b c d e f g : (Fin N × Fin M) × Fin K → ℚ)
    (hb : ∀ ijk, b ijk = a ((fwd N hN ijk.1.1, ijk.1.2), ijk.2))
    (hc : ∀ ijk, c ijk = a ((bwd N hN ijk.1.1, ijk.1.2), ijk.2))
    (hd : ∀ ijk, d ijk = a ((ijk.1.1, fwd M hM ijk.1.2), ijk.2))
    (he : ∀ ijk, e ijk = a ((ijk.1.1, bwd M hM ijk.1.2), ijk.2))
    (hf : ∀ ijk, f ijk = a ((ijk.1.1, ijk.1.2), fwd K hK ijk.2))
    (hg : ∀ ijk, g ijk = a ((ijk.1.1, ijk.1.2), bwd K hK ijk.2)) :
    ∑ ijk, ((1 - 6 * μ) * a ijk + μ * b ijk + μ * c ijk + μ * d ijk
        + μ * e ijk + μ * f ijk + μ * g ijk) ^ 2
      ≤ ∑ ijk, (a ijk) ^ 2 := by
  calc ∑ ijk, ((1 - 6 * μ) * a ijk + μ * b ijk + μ * c ijk + μ * d ijk
          + μ * e ijk + μ * f ijk + μ * g ijk) ^ 2
      ≤ ∑ ijk, ((1 - 6 * μ) * (a ijk) ^ 2 + μ * (b ijk) ^ 2
          + μ * (c ijk) ^ 2 + μ * (d ijk) ^ 2 + μ * (e ijk) ^ 2
          + μ * (f ijk) ^ 2 + μ * (g ijk) ^ 2) :=
        Finset.sum_le_sum
          (fun ijk _ => convex_sq7 μ (a ijk) (b ijk) (c ijk) (d ijk)
            (e ijk) (f ijk) (g ijk) hμ0 hμ1)
    _ = (1 - 6 * μ) * ∑ ijk, (a ijk) ^ 2 + μ * ∑ ijk, (b ijk) ^ 2
          + μ * ∑ ijk, (c ijk) ^ 2 + μ * ∑ ijk, (d ijk) ^ 2
          + μ * ∑ ijk, (e ijk) ^ 2 + μ * ∑ ijk, (f ijk) ^ 2
          + μ * ∑ ijk, (g ijk) ^ 2 := by
        simp only [Finset.sum_add_distrib, ← Finset.mul_sum]
    _ = ∑ ijk, (a ijk) ^ 2 := by
        have hfun1 : (fun ijk => (b ijk) ^ 2)
            = (fun ijk => (a ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)) ^ 2) :=
          funext (fun ijk => by rw [hb ijk])
        have hfun2 : (fun ijk => (c ijk) ^ 2)
            = (fun ijk => (a ((bwd N hN ijk.1.1, ijk.1.2), ijk.2)) ^ 2) :=
          funext (fun ijk => by rw [hc ijk])
        have hfun3 : (fun ijk => (d ijk) ^ 2)
            = (fun ijk => (a ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)) ^ 2) :=
          funext (fun ijk => by rw [hd ijk])
        have hfun4 : (fun ijk => (e ijk) ^ 2)
            = (fun ijk => (a ((ijk.1.1, bwd M hM ijk.1.2), ijk.2)) ^ 2) :=
          funext (fun ijk => by rw [he ijk])
        have hfun5 : (fun ijk => (f ijk) ^ 2)
            = (fun ijk => (a ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)) ^ 2) :=
          funext (fun ijk => by rw [hf ijk])
        have hfun6 : (fun ijk => (g ijk) ^ 2)
            = (fun ijk => (a ((ijk.1.1, ijk.1.2), bwd K hK ijk.2)) ^ 2) :=
          funext (fun ijk => by rw [hg ijk])
        have r1 : ∑ ijk, (b ijk) ^ 2 = ∑ ijk, (a ijk) ^ 2 := by
          rw [hfun1]
          exact sum_3d_fst N M K hN (fun i j k => (a ((i, j), k)) ^ 2)
        have r2 : ∑ ijk, (c ijk) ^ 2 = ∑ ijk, (a ijk) ^ 2 := by
          rw [hfun2]
          exact sum_3d_fst_bwd N M K hN (fun i j k => (a ((i, j), k)) ^ 2)
        have r3 : ∑ ijk, (d ijk) ^ 2 = ∑ ijk, (a ijk) ^ 2 := by
          rw [hfun3]
          exact sum_3d_snd N M K hM (fun i j k => (a ((i, j), k)) ^ 2)
        have r4 : ∑ ijk, (e ijk) ^ 2 = ∑ ijk, (a ijk) ^ 2 := by
          rw [hfun4]
          exact sum_3d_snd_bwd N M K hM (fun i j k => (a ((i, j), k)) ^ 2)
        have r5 : ∑ ijk, (f ijk) ^ 2 = ∑ ijk, (a ijk) ^ 2 := by
          rw [hfun5]
          exact sum_3d_trd N M K hK (fun i j k => (a ((i, j), k)) ^ 2)
        have r6 : ∑ ijk, (g ijk) ^ 2 = ∑ ijk, (a ijk) ^ 2 := by
          rw [hfun6]
          exact sum_3d_trd_bwd N M K hK (fun i j k => (a ((i, j), k)) ^ 2)
        rw [r1, r2, r3, r4, r5, r6]
        ring

/-- 3D diffusion contracts total energy (three components). -/
lemma energy_diffuse3D (N M K : ℕ) (hN : 0 < N) (hM : 0 < M) (hK : 0 < K)
    (μ : ℚ) (hμ0 : 0 ≤ μ) (hμ1 : 6 * μ ≤ 1) (L : FluidLattice3D N M K) :
    totalEnergy3D N M K (diffuse3D N M K hN hM hK μ L)
      ≤ totalEnergy3D N M K L := by
  have hx := scalar_diffuse3D N M K hN hM hK μ hμ0 hμ1
    (fun ijk => (L.vel ijk).x)
    (fun ijk => (L.vel ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)).x)
    (fun ijk => (L.vel ((bwd N hN ijk.1.1, ijk.1.2), ijk.2)).x)
    (fun ijk => (L.vel ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)).x)
    (fun ijk => (L.vel ((ijk.1.1, bwd M hM ijk.1.2), ijk.2)).x)
    (fun ijk => (L.vel ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)).x)
    (fun ijk => (L.vel ((ijk.1.1, ijk.1.2), bwd K hK ijk.2)).x)
    (fun ijk => rfl) (fun ijk => rfl) (fun ijk => rfl)
    (fun ijk => rfl) (fun ijk => rfl) (fun ijk => rfl)
  have hy := scalar_diffuse3D N M K hN hM hK μ hμ0 hμ1
    (fun ijk => (L.vel ijk).y)
    (fun ijk => (L.vel ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)).y)
    (fun ijk => (L.vel ((bwd N hN ijk.1.1, ijk.1.2), ijk.2)).y)
    (fun ijk => (L.vel ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)).y)
    (fun ijk => (L.vel ((ijk.1.1, bwd M hM ijk.1.2), ijk.2)).y)
    (fun ijk => (L.vel ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)).y)
    (fun ijk => (L.vel ((ijk.1.1, ijk.1.2), bwd K hK ijk.2)).y)
    (fun ijk => rfl) (fun ijk => rfl) (fun ijk => rfl)
    (fun ijk => rfl) (fun ijk => rfl) (fun ijk => rfl)
  have hz := scalar_diffuse3D N M K hN hM hK μ hμ0 hμ1
    (fun ijk => (L.vel ijk).z)
    (fun ijk => (L.vel ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)).z)
    (fun ijk => (L.vel ((bwd N hN ijk.1.1, ijk.1.2), ijk.2)).z)
    (fun ijk => (L.vel ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)).z)
    (fun ijk => (L.vel ((ijk.1.1, bwd M hM ijk.1.2), ijk.2)).z)
    (fun ijk => (L.vel ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)).z)
    (fun ijk => (L.vel ((ijk.1.1, ijk.1.2), bwd K hK ijk.2)).z)
    (fun ijk => rfl) (fun ijk => rfl) (fun ijk => rfl)
    (fun ijk => rfl) (fun ijk => rfl) (fun ijk => rfl)
  have hexpand : totalEnergy3D N M K (diffuse3D N M K hN hM hK μ L)
      = ∑ ijk, ((1 - 6 * μ) * (L.vel ijk).x
          + μ * (L.vel ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)).x
          + μ * (L.vel ((bwd N hN ijk.1.1, ijk.1.2), ijk.2)).x
          + μ * (L.vel ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)).x
          + μ * (L.vel ((ijk.1.1, bwd M hM ijk.1.2), ijk.2)).x
          + μ * (L.vel ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)).x
          + μ * (L.vel ((ijk.1.1, ijk.1.2), bwd K hK ijk.2)).x) ^ 2
        + ∑ ijk, ((1 - 6 * μ) * (L.vel ijk).y
          + μ * (L.vel ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)).y
          + μ * (L.vel ((bwd N hN ijk.1.1, ijk.1.2), ijk.2)).y
          + μ * (L.vel ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)).y
          + μ * (L.vel ((ijk.1.1, bwd M hM ijk.1.2), ijk.2)).y
          + μ * (L.vel ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)).y
          + μ * (L.vel ((ijk.1.1, ijk.1.2), bwd K hK ijk.2)).y) ^ 2
        + ∑ ijk, ((1 - 6 * μ) * (L.vel ijk).z
          + μ * (L.vel ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)).z
          + μ * (L.vel ((bwd N hN ijk.1.1, ijk.1.2), ijk.2)).z
          + μ * (L.vel ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)).z
          + μ * (L.vel ((ijk.1.1, bwd M hM ijk.1.2), ijk.2)).z
          + μ * (L.vel ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)).z
          + μ * (L.vel ((ijk.1.1, ijk.1.2), bwd K hK ijk.2)).z) ^ 2 := by
    have rfl_expand : totalEnergy3D N M K (diffuse3D N M K hN hM hK μ L)
        = ∑ ijk, ((((1 - 6 * μ) * (L.vel ijk).x
            + μ * (L.vel ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)).x
            + μ * (L.vel ((bwd N hN ijk.1.1, ijk.1.2), ijk.2)).x
            + μ * (L.vel ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)).x
            + μ * (L.vel ((ijk.1.1, bwd M hM ijk.1.2), ijk.2)).x
            + μ * (L.vel ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)).x
            + μ * (L.vel ((ijk.1.1, ijk.1.2), bwd K hK ijk.2)).x) ^ 2
          + ((1 - 6 * μ) * (L.vel ijk).y
            + μ * (L.vel ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)).y
            + μ * (L.vel ((bwd N hN ijk.1.1, ijk.1.2), ijk.2)).y
            + μ * (L.vel ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)).y
            + μ * (L.vel ((ijk.1.1, bwd M hM ijk.1.2), ijk.2)).y
            + μ * (L.vel ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)).y
            + μ * (L.vel ((ijk.1.1, ijk.1.2), bwd K hK ijk.2)).y) ^ 2)
          + ((1 - 6 * μ) * (L.vel ijk).z
            + μ * (L.vel ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)).z
            + μ * (L.vel ((bwd N hN ijk.1.1, ijk.1.2), ijk.2)).z
            + μ * (L.vel ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)).z
            + μ * (L.vel ((ijk.1.1, bwd M hM ijk.1.2), ijk.2)).z
            + μ * (L.vel ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)).z
            + μ * (L.vel ((ijk.1.1, ijk.1.2), bwd K hK ijk.2)).z) ^ 2) := rfl
    rw [rfl_expand]
    simp only [Finset.sum_add_distrib]
  have hexpand0 : totalEnergy3D N M K L
      = ∑ ijk, ((L.vel ijk).x) ^ 2 + ∑ ijk, ((L.vel ijk).y) ^ 2
        + ∑ ijk, ((L.vel ijk).z) ^ 2 := by
    have rfl_expand0 : totalEnergy3D N M K L
        = ∑ ijk, ((((L.vel ijk).x) ^ 2 + ((L.vel ijk).y) ^ 2)
          + ((L.vel ijk).z) ^ 2) := rfl
    rw [rfl_expand0]
    simp only [Finset.sum_add_distrib]
  rw [hexpand, hexpand0]
  linarith

/-- Forward-difference pressure gradients (3 axes, kept structure). -/
def gradX3D (N M K : ℕ) (hN : 0 < N) (p : (Fin N × Fin M) × Fin K → ℚ)
    (ijk : (Fin N × Fin M) × Fin K) : ℚ :=
  p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2) - p ijk

def gradY3D (N M K : ℕ) (hM : 0 < M) (p : (Fin N × Fin M) × Fin K → ℚ)
    (ijk : (Fin N × Fin M) × Fin K) : ℚ :=
  p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2) - p ijk

def gradZ3D (N M K : ℕ) (hK : 0 < K) (p : (Fin N × Fin M) × Fin K → ℚ)
    (ijk : (Fin N × Fin M) × Fin K) : ℚ :=
  p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2) - p ijk

/-- Backward-difference divergence (adjoint triple). -/
def bdiv3D (N M K : ℕ) (hN : 0 < N) (hM : 0 < M) (hK : 0 < K)
    (u : (Fin N × Fin M) × Fin K → CellVelocity)
    (ijk : (Fin N × Fin M) × Fin K) : ℚ :=
  ((u ijk).x - (u ((bwd N hN ijk.1.1, ijk.1.2), ijk.2)).x)
    + ((u ijk).y - (u ((ijk.1.1, bwd M hM ijk.1.2), ijk.2)).y)
    + ((u ijk).z - (u ((ijk.1.1, ijk.1.2), bwd K hK ijk.2)).z)

/-- Summation by parts I in 3D (all three axes, proved). -/
lemma sbp_grad_div3D (N M K : ℕ) (hN : 0 < N) (hM : 0 < M) (hK : 0 < K)
    (u : (Fin N × Fin M) × Fin K → CellVelocity)
    (p : (Fin N × Fin M) × Fin K → ℚ) :
    (∑ ijk, (u ijk).x * gradX3D N M K hN p ijk)
        + (∑ ijk, (u ijk).y * gradY3D N M K hM p ijk)
        + (∑ ijk, (u ijk).z * gradZ3D N M K hK p ijk)
      = -∑ ijk, bdiv3D N M K hN hM hK u ijk * p ijk := by
  have hX : ∑ ijk, (u ijk).x * gradX3D N M K hN p ijk
      = ∑ ijk, (u ((bwd N hN ijk.1.1, ijk.1.2), ijk.2)).x * p ijk
        - ∑ ijk, (u ijk).x * p ijk := by
    have e : ∀ ijk ∈ (Finset.univ : Finset ((Fin N × Fin M) × Fin K)),
        (u ijk).x * gradX3D N M K hN p ijk
          = (u ijk).x * p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)
            - (u ijk).x * p ijk := by
      intro ijk _
      simp only [gradX3D, mul_sub]
    rw [Finset.sum_congr rfl e, Finset.sum_sub_distrib]
    have hstep := sum_3d_fwd_to_bwdX N M K hN (fun a b => (u a).x * p b)
    have r1 : (∑ ijk, (u ijk).x * p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2))
        = ∑ ijk, (fun a b => (u a).x * p b) ijk
          ((fwd N hN ijk.1.1, ijk.1.2), ijk.2) := rfl
    have r2 : (∑ ijk, (fun a b => (u a).x * p b)
          ((bwd N hN ijk.1.1, ijk.1.2), ijk.2) ijk)
        = ∑ ijk, (u ((bwd N hN ijk.1.1, ijk.1.2), ijk.2)).x * p ijk := rfl
    rw [r1, hstep, r2]
  have hY : ∑ ijk, (u ijk).y * gradY3D N M K hM p ijk
      = ∑ ijk, (u ((ijk.1.1, bwd M hM ijk.1.2), ijk.2)).y * p ijk
        - ∑ ijk, (u ijk).y * p ijk := by
    have e : ∀ ijk ∈ (Finset.univ : Finset ((Fin N × Fin M) × Fin K)),
        (u ijk).y * gradY3D N M K hM p ijk
          = (u ijk).y * p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)
            - (u ijk).y * p ijk := by
      intro ijk _
      simp only [gradY3D, mul_sub]
    rw [Finset.sum_congr rfl e, Finset.sum_sub_distrib]
    have hstep := sum_3d_fwd_to_bwdY N M K hM (fun a b => (u a).y * p b)
    have r1 : (∑ ijk, (u ijk).y * p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2))
        = ∑ ijk, (fun a b => (u a).y * p b) ijk
          ((ijk.1.1, fwd M hM ijk.1.2), ijk.2) := rfl
    have r2 : (∑ ijk, (fun a b => (u a).y * p b)
          ((ijk.1.1, bwd M hM ijk.1.2), ijk.2) ijk)
        = ∑ ijk, (u ((ijk.1.1, bwd M hM ijk.1.2), ijk.2)).y * p ijk := rfl
    rw [r1, hstep, r2]
  have hZ : ∑ ijk, (u ijk).z * gradZ3D N M K hK p ijk
      = ∑ ijk, (u ((ijk.1.1, ijk.1.2), bwd K hK ijk.2)).z * p ijk
        - ∑ ijk, (u ijk).z * p ijk := by
    have e : ∀ ijk ∈ (Finset.univ : Finset ((Fin N × Fin M) × Fin K)),
        (u ijk).z * gradZ3D N M K hK p ijk
          = (u ijk).z * p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)
            - (u ijk).z * p ijk := by
      intro ijk _
      simp only [gradZ3D, mul_sub]
    rw [Finset.sum_congr rfl e, Finset.sum_sub_distrib]
    have hstep := sum_3d_fwd_to_bwdZ N M K hK (fun a b => (u a).z * p b)
    have r1 : (∑ ijk, (u ijk).z * p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2))
        = ∑ ijk, (fun a b => (u a).z * p b) ijk
          ((ijk.1.1, ijk.1.2), fwd K hK ijk.2) := rfl
    have r2 : (∑ ijk, (fun a b => (u a).z * p b)
          ((ijk.1.1, ijk.1.2), bwd K hK ijk.2) ijk)
        = ∑ ijk, (u ((ijk.1.1, ijk.1.2), bwd K hK ijk.2)).z * p ijk := rfl
    rw [r1, hstep, r2]
  rw [hX, hY, hZ]
  simp only [bdiv3D, add_mul, sub_mul, Finset.sum_add_distrib,
    Finset.sum_sub_distrib]
  ring

/-- Axis Laplacians and their sum (stencil-7 split). -/
def lapX3D (N M K : ℕ) (hN : 0 < N) (p : (Fin N × Fin M) × Fin K → ℚ)
    (ijk : (Fin N × Fin M) × Fin K) : ℚ :=
  p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2) - 2 * p ijk
    + p ((bwd N hN ijk.1.1, ijk.1.2), ijk.2)

def lapY3D (N M K : ℕ) (hM : 0 < M) (p : (Fin N × Fin M) × Fin K → ℚ)
    (ijk : (Fin N × Fin M) × Fin K) : ℚ :=
  p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2) - 2 * p ijk
    + p ((ijk.1.1, bwd M hM ijk.1.2), ijk.2)

def lapZ3D (N M K : ℕ) (hK : 0 < K) (p : (Fin N × Fin M) × Fin K → ℚ)
    (ijk : (Fin N × Fin M) × Fin K) : ℚ :=
  p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2) - 2 * p ijk
    + p ((ijk.1.1, ijk.1.2), bwd K hK ijk.2)

def lap3D (N M K : ℕ) (hN : 0 < N) (hM : 0 < M) (hK : 0 < K)
    (p : (Fin N × Fin M) × Fin K → ℚ)
    (ijk : (Fin N × Fin M) × Fin K) : ℚ :=
  lapX3D N M K hN p ijk + lapY3D N M K hM p ijk + lapZ3D N M K hK p ijk

/-- X-axis Laplacian is negative-semidefinite (proved). -/
lemma sbp_lap_negX3D (N M K : ℕ) (hN : 0 < N)
    (p : (Fin N × Fin M) × Fin K → ℚ) :
    ∑ ijk, lapX3D N M K hN p ijk * p ijk
      = -∑ ijk, (gradX3D N M K hN p ijk) ^ 2 := by
  have e1 : ∑ ijk : (Fin N × Fin M) × Fin K,
        p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2) * p ijk
      = ∑ ijk : (Fin N × Fin M) × Fin K,
        p ijk * p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2) :=
    Finset.sum_congr rfl (fun ijk _ => mul_comm _ _)
  have e2 : ∑ ijk : (Fin N × Fin M) × Fin K,
        p ((bwd N hN ijk.1.1, ijk.1.2), ijk.2) * p ijk
      = ∑ ijk : (Fin N × Fin M) × Fin K,
        p ijk * p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2) := by
    have hstep := sum_3d_fwd_to_bwdX N M K hN (fun a b => p a * p b)
    have r1 : (∑ ijk : (Fin N × Fin M) × Fin K,
          p ((bwd N hN ijk.1.1, ijk.1.2), ijk.2) * p ijk)
        = ∑ ijk, (fun a b => p a * p b)
          ((bwd N hN ijk.1.1, ijk.1.2), ijk.2) ijk := rfl
    have r2 : (∑ ijk, (fun a b => p a * p b) ijk
          ((fwd N hN ijk.1.1, ijk.1.2), ijk.2))
        = ∑ ijk : (Fin N × Fin M) × Fin K,
          p ijk * p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2) := rfl
    rw [r1, ← hstep, r2]
  have e3 : ∑ ijk : (Fin N × Fin M) × Fin K,
        (p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)) ^ 2
      = ∑ ijk : (Fin N × Fin M) × Fin K, (p ijk) ^ 2 :=
    sum_3d_fst N M K hN (fun i j k => (p ((i, j), k)) ^ 2)
  have e4 : ∀ ijk : (Fin N × Fin M) × Fin K,
      (gradX3D N M K hN p ijk) ^ 2
      = (p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)) ^ 2
        - 2 * (p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2) * p ijk)
        + (p ijk) ^ 2 := by
    intro ijk
    simp only [gradX3D]
    ring
  have e5 : ∀ ijk : (Fin N × Fin M) × Fin K,
      lapX3D N M K hN p ijk * p ijk
      = p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2) * p ijk - 2 * (p ijk) ^ 2
        + p ((bwd N hN ijk.1.1, ijk.1.2), ijk.2) * p ijk := by
    intro ijk
    simp only [lapX3D]
    ring
  calc ∑ ijk, lapX3D N M K hN p ijk * p ijk
      = ∑ ijk : (Fin N × Fin M) × Fin K,
          (p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2) * p ijk - 2 * (p ijk) ^ 2
          + p ((bwd N hN ijk.1.1, ijk.1.2), ijk.2) * p ijk) :=
        Finset.sum_congr rfl (fun ijk _ => e5 ijk)
    _ = ∑ ijk : (Fin N × Fin M) × Fin K,
            p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2) * p ijk
          - ∑ ijk : (Fin N × Fin M) × Fin K, (2 * (p ijk) ^ 2)
          + ∑ ijk : (Fin N × Fin M) × Fin K,
            p ((bwd N hN ijk.1.1, ijk.1.2), ijk.2) * p ijk := by
        simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib]
    _ = 2 * ∑ ijk : (Fin N × Fin M) × Fin K,
            p ijk * p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)
          - 2 * ∑ ijk : (Fin N × Fin M) × Fin K, (p ijk) ^ 2 := by
        have sB : ∑ ijk : (Fin N × Fin M) × Fin K, (2 * (p ijk) ^ 2)
            = 2 * ∑ ijk : (Fin N × Fin M) × Fin K, (p ijk) ^ 2 :=
          (Finset.mul_sum _ _ _).symm
        rw [e1, e2, sB]
        ring
    _ = -∑ ijk, (gradX3D N M K hN p ijk) ^ 2 := by
        have g1 : ∑ ijk, (gradX3D N M K hN p ijk) ^ 2
            = ∑ ijk : (Fin N × Fin M) × Fin K,
              ((p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)) ^ 2
              - 2 * (p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2) * p ijk))
              + ∑ ijk : (Fin N × Fin M) × Fin K, (p ijk) ^ 2 := by
          have hcongr : ∀ ijk ∈ (Finset.univ : Finset ((Fin N × Fin M) × Fin K)),
              (gradX3D N M K hN p ijk) ^ 2
                = (p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)) ^ 2
                  - 2 * (p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2) * p ijk)
                  + (p ijk) ^ 2 := fun ijk _ => e4 ijk
          rw [Finset.sum_congr rfl hcongr]
          simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib]
        rw [g1]
        have g2 : ∑ ijk : (Fin N × Fin M) × Fin K,
              ((p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)) ^ 2
              - 2 * (p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2) * p ijk))
            = ∑ ijk : (Fin N × Fin M) × Fin K,
                (p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2)) ^ 2
              - ∑ ijk : (Fin N × Fin M) × Fin K,
                (2 * (p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2) * p ijk)) :=
          Finset.sum_sub_distrib _ _
        rw [g2, e3]
        have sD : ∑ ijk : (Fin N × Fin M) × Fin K,
              (2 * (p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2) * p ijk))
            = 2 * ∑ ijk : (Fin N × Fin M) × Fin K,
              p ((fwd N hN ijk.1.1, ijk.1.2), ijk.2) * p ijk :=
          (Finset.mul_sum _ _ _).symm
        rw [sD, e1]
        ring

/-- Y-axis Laplacian is negative-semidefinite (proved). -/
lemma sbp_lap_negY3D (N M K : ℕ) (hM : 0 < M)
    (p : (Fin N × Fin M) × Fin K → ℚ) :
    ∑ ijk, lapY3D N M K hM p ijk * p ijk
      = -∑ ijk, (gradY3D N M K hM p ijk) ^ 2 := by
  have e1 : ∑ ijk : (Fin N × Fin M) × Fin K,
        p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2) * p ijk
      = ∑ ijk : (Fin N × Fin M) × Fin K,
        p ijk * p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2) :=
    Finset.sum_congr rfl (fun ijk _ => mul_comm _ _)
  have e2 : ∑ ijk : (Fin N × Fin M) × Fin K,
        p ((ijk.1.1, bwd M hM ijk.1.2), ijk.2) * p ijk
      = ∑ ijk : (Fin N × Fin M) × Fin K,
        p ijk * p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2) := by
    have hstep := sum_3d_fwd_to_bwdY N M K hM (fun a b => p a * p b)
    have r1 : (∑ ijk : (Fin N × Fin M) × Fin K,
          p ((ijk.1.1, bwd M hM ijk.1.2), ijk.2) * p ijk)
        = ∑ ijk, (fun a b => p a * p b)
          ((ijk.1.1, bwd M hM ijk.1.2), ijk.2) ijk := rfl
    have r2 : (∑ ijk, (fun a b => p a * p b) ijk
          ((ijk.1.1, fwd M hM ijk.1.2), ijk.2))
        = ∑ ijk : (Fin N × Fin M) × Fin K,
          p ijk * p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2) := rfl
    rw [r1, ← hstep, r2]
  have e3 : ∑ ijk : (Fin N × Fin M) × Fin K,
        (p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)) ^ 2
      = ∑ ijk : (Fin N × Fin M) × Fin K, (p ijk) ^ 2 :=
    sum_3d_snd N M K hM (fun i j k => (p ((i, j), k)) ^ 2)
  have e4 : ∀ ijk : (Fin N × Fin M) × Fin K,
      (gradY3D N M K hM p ijk) ^ 2
      = (p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)) ^ 2
        - 2 * (p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2) * p ijk)
        + (p ijk) ^ 2 := by
    intro ijk
    simp only [gradY3D]
    ring
  have e5 : ∀ ijk : (Fin N × Fin M) × Fin K,
      lapY3D N M K hM p ijk * p ijk
      = p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2) * p ijk - 2 * (p ijk) ^ 2
        + p ((ijk.1.1, bwd M hM ijk.1.2), ijk.2) * p ijk := by
    intro ijk
    simp only [lapY3D]
    ring
  calc ∑ ijk, lapY3D N M K hM p ijk * p ijk
      = ∑ ijk : (Fin N × Fin M) × Fin K,
          (p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2) * p ijk - 2 * (p ijk) ^ 2
          + p ((ijk.1.1, bwd M hM ijk.1.2), ijk.2) * p ijk) :=
        Finset.sum_congr rfl (fun ijk _ => e5 ijk)
    _ = ∑ ijk : (Fin N × Fin M) × Fin K,
            p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2) * p ijk
          - ∑ ijk : (Fin N × Fin M) × Fin K, (2 * (p ijk) ^ 2)
          + ∑ ijk : (Fin N × Fin M) × Fin K,
            p ((ijk.1.1, bwd M hM ijk.1.2), ijk.2) * p ijk := by
        simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib]
    _ = 2 * ∑ ijk : (Fin N × Fin M) × Fin K,
            p ijk * p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)
          - 2 * ∑ ijk : (Fin N × Fin M) × Fin K, (p ijk) ^ 2 := by
        have sB : ∑ ijk : (Fin N × Fin M) × Fin K, (2 * (p ijk) ^ 2)
            = 2 * ∑ ijk : (Fin N × Fin M) × Fin K, (p ijk) ^ 2 :=
          (Finset.mul_sum _ _ _).symm
        rw [e1, e2, sB]
        ring
    _ = -∑ ijk, (gradY3D N M K hM p ijk) ^ 2 := by
        have g1 : ∑ ijk, (gradY3D N M K hM p ijk) ^ 2
            = ∑ ijk : (Fin N × Fin M) × Fin K,
              ((p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)) ^ 2
              - 2 * (p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2) * p ijk))
              + ∑ ijk : (Fin N × Fin M) × Fin K, (p ijk) ^ 2 := by
          have hcongr : ∀ ijk ∈ (Finset.univ : Finset ((Fin N × Fin M) × Fin K)),
              (gradY3D N M K hM p ijk) ^ 2
                = (p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)) ^ 2
                  - 2 * (p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2) * p ijk)
                  + (p ijk) ^ 2 := fun ijk _ => e4 ijk
          rw [Finset.sum_congr rfl hcongr]
          simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib]
        rw [g1]
        have g2 : ∑ ijk : (Fin N × Fin M) × Fin K,
              ((p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)) ^ 2
              - 2 * (p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2) * p ijk))
            = ∑ ijk : (Fin N × Fin M) × Fin K,
                (p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2)) ^ 2
              - ∑ ijk : (Fin N × Fin M) × Fin K,
                (2 * (p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2) * p ijk)) :=
          Finset.sum_sub_distrib _ _
        rw [g2, e3]
        have sD : ∑ ijk : (Fin N × Fin M) × Fin K,
              (2 * (p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2) * p ijk))
            = 2 * ∑ ijk : (Fin N × Fin M) × Fin K,
              p ((ijk.1.1, fwd M hM ijk.1.2), ijk.2) * p ijk :=
          (Finset.mul_sum _ _ _).symm
        rw [sD, e1]
        ring

/-- Z-axis Laplacian is negative-semidefinite (proved). -/
lemma sbp_lap_negZ3D (N M K : ℕ) (hK : 0 < K)
    (p : (Fin N × Fin M) × Fin K → ℚ) :
    ∑ ijk, lapZ3D N M K hK p ijk * p ijk
      = -∑ ijk, (gradZ3D N M K hK p ijk) ^ 2 := by
  have e1 : ∑ ijk : (Fin N × Fin M) × Fin K,
        p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2) * p ijk
      = ∑ ijk : (Fin N × Fin M) × Fin K,
        p ijk * p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2) :=
    Finset.sum_congr rfl (fun ijk _ => mul_comm _ _)
  have e2 : ∑ ijk : (Fin N × Fin M) × Fin K,
        p ((ijk.1.1, ijk.1.2), bwd K hK ijk.2) * p ijk
      = ∑ ijk : (Fin N × Fin M) × Fin K,
        p ijk * p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2) := by
    have hstep := sum_3d_fwd_to_bwdZ N M K hK (fun a b => p a * p b)
    have r1 : (∑ ijk : (Fin N × Fin M) × Fin K,
          p ((ijk.1.1, ijk.1.2), bwd K hK ijk.2) * p ijk)
        = ∑ ijk, (fun a b => p a * p b)
          ((ijk.1.1, ijk.1.2), bwd K hK ijk.2) ijk := rfl
    have r2 : (∑ ijk, (fun a b => p a * p b) ijk
          ((ijk.1.1, ijk.1.2), fwd K hK ijk.2))
        = ∑ ijk : (Fin N × Fin M) × Fin K,
          p ijk * p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2) := rfl
    rw [r1, ← hstep, r2]
  have e3 : ∑ ijk : (Fin N × Fin M) × Fin K,
        (p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)) ^ 2
      = ∑ ijk : (Fin N × Fin M) × Fin K, (p ijk) ^ 2 :=
    sum_3d_trd N M K hK (fun i j k => (p ((i, j), k)) ^ 2)
  have e4 : ∀ ijk : (Fin N × Fin M) × Fin K,
      (gradZ3D N M K hK p ijk) ^ 2
      = (p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)) ^ 2
        - 2 * (p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2) * p ijk)
        + (p ijk) ^ 2 := by
    intro ijk
    simp only [gradZ3D]
    ring
  have e5 : ∀ ijk : (Fin N × Fin M) × Fin K,
      lapZ3D N M K hK p ijk * p ijk
      = p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2) * p ijk - 2 * (p ijk) ^ 2
        + p ((ijk.1.1, ijk.1.2), bwd K hK ijk.2) * p ijk := by
    intro ijk
    simp only [lapZ3D]
    ring
  calc ∑ ijk, lapZ3D N M K hK p ijk * p ijk
      = ∑ ijk : (Fin N × Fin M) × Fin K,
          (p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2) * p ijk - 2 * (p ijk) ^ 2
          + p ((ijk.1.1, ijk.1.2), bwd K hK ijk.2) * p ijk) :=
        Finset.sum_congr rfl (fun ijk _ => e5 ijk)
    _ = ∑ ijk : (Fin N × Fin M) × Fin K,
            p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2) * p ijk
          - ∑ ijk : (Fin N × Fin M) × Fin K, (2 * (p ijk) ^ 2)
          + ∑ ijk : (Fin N × Fin M) × Fin K,
            p ((ijk.1.1, ijk.1.2), bwd K hK ijk.2) * p ijk := by
        simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib]
    _ = 2 * ∑ ijk : (Fin N × Fin M) × Fin K,
            p ijk * p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)
          - 2 * ∑ ijk : (Fin N × Fin M) × Fin K, (p ijk) ^ 2 := by
        have sB : ∑ ijk : (Fin N × Fin M) × Fin K, (2 * (p ijk) ^ 2)
            = 2 * ∑ ijk : (Fin N × Fin M) × Fin K, (p ijk) ^ 2 :=
          (Finset.mul_sum _ _ _).symm
        rw [e1, e2, sB]
        ring
    _ = -∑ ijk, (gradZ3D N M K hK p ijk) ^ 2 := by
        have g1 : ∑ ijk, (gradZ3D N M K hK p ijk) ^ 2
            = ∑ ijk : (Fin N × Fin M) × Fin K,
              ((p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)) ^ 2
              - 2 * (p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2) * p ijk))
              + ∑ ijk : (Fin N × Fin M) × Fin K, (p ijk) ^ 2 := by
          have hcongr : ∀ ijk ∈ (Finset.univ : Finset ((Fin N × Fin M) × Fin K)),
              (gradZ3D N M K hK p ijk) ^ 2
                = (p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)) ^ 2
                  - 2 * (p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2) * p ijk)
                  + (p ijk) ^ 2 := fun ijk _ => e4 ijk
          rw [Finset.sum_congr rfl hcongr]
          simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib]
        rw [g1]
        have g2 : ∑ ijk : (Fin N × Fin M) × Fin K,
              ((p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)) ^ 2
              - 2 * (p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2) * p ijk))
            = ∑ ijk : (Fin N × Fin M) × Fin K,
                (p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2)) ^ 2
              - ∑ ijk : (Fin N × Fin M) × Fin K,
                (2 * (p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2) * p ijk)) :=
          Finset.sum_sub_distrib _ _
        rw [g2, e3]
        have sD : ∑ ijk : (Fin N × Fin M) × Fin K,
              (2 * (p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2) * p ijk))
            = 2 * ∑ ijk : (Fin N × Fin M) × Fin K,
              p ((ijk.1.1, ijk.1.2), fwd K hK ijk.2) * p ijk :=
          (Finset.mul_sum _ _ _).symm
        rw [sD, e1]
        ring

/-- Full 3D Laplacian is negative-semidefinite (all three axes). -/
lemma sbp_lap_neg3D (N M K : ℕ) (hN : 0 < N) (hM : 0 < M) (hK : 0 < K)
    (p : (Fin N × Fin M) × Fin K → ℚ) :
    ∑ ijk, lap3D N M K hN hM hK p ijk * p ijk
      = -(∑ ijk, (gradX3D N M K hN p ijk) ^ 2
        + ∑ ijk, (gradY3D N M K hM p ijk) ^ 2
        + ∑ ijk, (gradZ3D N M K hK p ijk) ^ 2) := by
  have hX := sbp_lap_negX3D N M K hN p
  have hY := sbp_lap_negY3D N M K hM p
  have hZ := sbp_lap_negZ3D N M K hK p
  have hsplit : ∀ ijk ∈ (Finset.univ : Finset ((Fin N × Fin M) × Fin K)),
      lap3D N M K hN hM hK p ijk * p ijk
        = lapX3D N M K hN p ijk * p ijk
          + lapY3D N M K hM p ijk * p ijk
          + lapZ3D N M K hK p ijk * p ijk := by
    intro ijk _
    simp only [lap3D, add_mul]
  rw [Finset.sum_congr rfl hsplit]
  simp only [Finset.sum_add_distrib]
  rw [hX, hY, hZ]
  ring

/-- 3D Chorin projection (all three channels, matching the runtime). -/
def project3D (N M K : ℕ) (hN : 0 < N) (hM : 0 < M) (hK : 0 < K) (c : ℚ)
    (L : FluidLattice3D N M K) (p : (Fin N × Fin M) × Fin K → ℚ)
    : FluidLattice3D N M K :=
  ⟨fun ijk => ⟨(L.vel ijk).x - c * gradX3D N M K hN p ijk,
    (L.vel ijk).y - c * gradY3D N M K hM p ijk,
    (L.vel ijk).z - c * gradZ3D N M K hK p ijk⟩⟩

/-- 3D projection dissipates energy under the solver contract. -/
lemma energy_project3D (N M K : ℕ) (hN : 0 < N) (hM : 0 < M) (hK : 0 < K)
    (c C : ℚ) (hc : c * C = 1) (hC : 0 < C) (L : FluidLattice3D N M K)
    (p : (Fin N × Fin M) × Fin K → ℚ)
    (hPoisson : ∀ ijk, lap3D N M K hN hM hK p ijk
      = C * bdiv3D N M K hN hM hK L.vel ijk) :
    totalEnergy3D N M K (project3D N M K hN hM hK c L p)
      ≤ totalEnergy3D N M K L := by
  have hCne : C ≠ 0 := hC.ne'
  have hSnn : 0 ≤ ∑ ijk, (gradX3D N M K hN p ijk) ^ 2
      + ∑ ijk, (gradY3D N M K hM p ijk) ^ 2
      + ∑ ijk, (gradZ3D N M K hK p ijk) ^ 2 := by
    apply add_nonneg
    · apply add_nonneg
      · exact Finset.sum_nonneg (fun ijk _ => sq_nonneg _)
      · exact Finset.sum_nonneg (fun ijk _ => sq_nonneg _)
    · exact Finset.sum_nonneg (fun ijk _ => sq_nonneg _)
  have hlink3D : (∑ ijk, (L.vel ijk).x * gradX3D N M K hN p ijk)
        + (∑ ijk, (L.vel ijk).y * gradY3D N M K hM p ijk)
        + (∑ ijk, (L.vel ijk).z * gradZ3D N M K hK p ijk)
      = (1 / C) * (∑ ijk, (gradX3D N M K hN p ijk) ^ 2
        + ∑ ijk, (gradY3D N M K hM p ijk) ^ 2
        + ∑ ijk, (gradZ3D N M K hK p ijk) ^ 2) := by
    have h1 := sbp_grad_div3D N M K hN hM hK L.vel p
    have h2 := sbp_lap_neg3D N M K hN hM hK p
    have h3 : ∑ ijk, bdiv3D N M K hN hM hK L.vel ijk * p ijk
        = (1 / C) * ∑ ijk, lap3D N M K hN hM hK p ijk * p ijk := by
      have hper : ∀ ijk : (Fin N × Fin M) × Fin K,
          bdiv3D N M K hN hM hK L.vel ijk * p ijk
          = (1 / C) * (lap3D N M K hN hM hK p ijk * p ijk) := by
        intro ijk
        rw [hPoisson ijk]
        field_simp
      rw [Finset.sum_congr rfl (fun ijk _ => hper ijk), ← Finset.mul_sum]
    rw [h1, h3, h2]
    ring
  have hE : totalEnergy3D N M K (project3D N M K hN hM hK c L p)
      = totalEnergy3D N M K L - c ^ 2 * (∑ ijk, (gradX3D N M K hN p ijk) ^ 2
        + ∑ ijk, (gradY3D N M K hM p ijk) ^ 2
        + ∑ ijk, (gradZ3D N M K hK p ijk) ^ 2) := by
    have hexpand : totalEnergy3D N M K (project3D N M K hN hM hK c L p)
        = ∑ ijk, ((L.vel ijk).x - c * gradX3D N M K hN p ijk) ^ 2
          + ∑ ijk, ((L.vel ijk).y - c * gradY3D N M K hM p ijk) ^ 2
          + ∑ ijk, ((L.vel ijk).z - c * gradZ3D N M K hK p ijk) ^ 2 := by
      have rfl_expand : totalEnergy3D N M K (project3D N M K hN hM hK c L p)
          = ∑ ijk, ((((L.vel ijk).x - c * gradX3D N M K hN p ijk) ^ 2
            + ((L.vel ijk).y - c * gradY3D N M K hM p ijk) ^ 2)
            + ((L.vel ijk).z - c * gradZ3D N M K hK p ijk) ^ 2) := rfl
      rw [rfl_expand]
      simp only [Finset.sum_add_distrib]
    have hexpand0 : totalEnergy3D N M K L
        = ∑ ijk, ((L.vel ijk).x) ^ 2 + ∑ ijk, ((L.vel ijk).y) ^ 2
          + ∑ ijk, ((L.vel ijk).z) ^ 2 := by
      have rfl_expand0 : totalEnergy3D N M K L
          = ∑ ijk, ((((L.vel ijk).x) ^ 2 + ((L.vel ijk).y) ^ 2)
            + ((L.vel ijk).z) ^ 2) := rfl
      rw [rfl_expand0]
      simp only [Finset.sum_add_distrib]
    rw [hexpand, hexpand0]
    have hx : ∀ ijk : (Fin N × Fin M) × Fin K,
        ((L.vel ijk).x - c * gradX3D N M K hN p ijk) ^ 2
          = ((L.vel ijk).x) ^ 2
            - 2 * c * ((L.vel ijk).x * gradX3D N M K hN p ijk)
            + c ^ 2 * (gradX3D N M K hN p ijk) ^ 2 := by
      intro ijk
      ring
    have hy : ∀ ijk : (Fin N × Fin M) × Fin K,
        ((L.vel ijk).y - c * gradY3D N M K hM p ijk) ^ 2
          = ((L.vel ijk).y) ^ 2
            - 2 * c * ((L.vel ijk).y * gradY3D N M K hM p ijk)
            + c ^ 2 * (gradY3D N M K hM p ijk) ^ 2 := by
      intro ijk
      ring
    have hz : ∀ ijk : (Fin N × Fin M) × Fin K,
        ((L.vel ijk).z - c * gradZ3D N M K hK p ijk) ^ 2
          = ((L.vel ijk).z) ^ 2
            - 2 * c * ((L.vel ijk).z * gradZ3D N M K hK p ijk)
            + c ^ 2 * (gradZ3D N M K hK p ijk) ^ 2 := by
      intro ijk
      ring
    rw [Finset.sum_congr rfl (fun ijk _ => hx ijk),
      Finset.sum_congr rfl (fun ijk _ => hy ijk),
      Finset.sum_congr rfl (fun ijk _ => hz ijk)]
    simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib]
    have t1x : ∑ ijk, (2 * c * ((L.vel ijk).x * gradX3D N M K hN p ijk))
        = 2 * c * ∑ ijk, (L.vel ijk).x * gradX3D N M K hN p ijk :=
      (Finset.mul_sum _ _ _).symm
    have t1y : ∑ ijk, (2 * c * ((L.vel ijk).y * gradY3D N M K hM p ijk))
        = 2 * c * ∑ ijk, (L.vel ijk).y * gradY3D N M K hM p ijk :=
      (Finset.mul_sum _ _ _).symm
    have t1z : ∑ ijk, (2 * c * ((L.vel ijk).z * gradZ3D N M K hK p ijk))
        = 2 * c * ∑ ijk, (L.vel ijk).z * gradZ3D N M K hK p ijk :=
      (Finset.mul_sum _ _ _).symm
    have t2x : ∑ ijk, (c ^ 2 * (gradX3D N M K hN p ijk) ^ 2)
        = c ^ 2 * ∑ ijk, (gradX3D N M K hN p ijk) ^ 2 :=
      (Finset.mul_sum _ _ _).symm
    have t2y : ∑ ijk, (c ^ 2 * (gradY3D N M K hM p ijk) ^ 2)
        = c ^ 2 * ∑ ijk, (gradY3D N M K hM p ijk) ^ 2 :=
      (Finset.mul_sum _ _ _).symm
    have t2z : ∑ ijk, (c ^ 2 * (gradZ3D N M K hK p ijk) ^ 2)
        = c ^ 2 * ∑ ijk, (gradZ3D N M K hK p ijk) ^ 2 :=
      (Finset.mul_sum _ _ _).symm
    rw [t1x, t1y, t1z, t2x, t2y, t2z]
    have hC : 2 * c * (∑ ijk, (L.vel ijk).x * gradX3D N M K hN p ijk)
        + 2 * c * (∑ ijk, (L.vel ijk).y * gradY3D N M K hM p ijk)
        + 2 * c * (∑ ijk, (L.vel ijk).z * gradZ3D N M K hK p ijk)
        = 2 * (c * c) * (∑ ijk, (gradX3D N M K hN p ijk) ^ 2
          + ∑ ijk, (gradY3D N M K hM p ijk) ^ 2
          + ∑ ijk, (gradZ3D N M K hK p ijk) ^ 2) := by
      have hcC : c * (1 / C) = c ^ 2 := by
        field_simp
        nlinarith [hc]
      have step3 : (2 : ℚ) * (c * (1 / C)) = 2 * (c * c) := by
        nlinarith [hcC]
      calc 2 * c * (∑ ijk, (L.vel ijk).x * gradX3D N M K hN p ijk)
            + 2 * c * (∑ ijk, (L.vel ijk).y * gradY3D N M K hM p ijk)
            + 2 * c * (∑ ijk, (L.vel ijk).z * gradZ3D N M K hK p ijk)
          = 2 * c * ((∑ ijk, (L.vel ijk).x * gradX3D N M K hN p ijk)
            + (∑ ijk, (L.vel ijk).y * gradY3D N M K hM p ijk)
            + (∑ ijk, (L.vel ijk).z * gradZ3D N M K hK p ijk)) := by ring
        _ = 2 * c * ((1 / C) * (∑ ijk, (gradX3D N M K hN p ijk) ^ 2
            + ∑ ijk, (gradY3D N M K hM p ijk) ^ 2
            + ∑ ijk, (gradZ3D N M K hK p ijk) ^ 2)) := by rw [hlink3D]
        _ = 2 * (c * (1 / C)) * (∑ ijk, (gradX3D N M K hN p ijk) ^ 2
            + ∑ ijk, (gradY3D N M K hM p ijk) ^ 2
            + ∑ ijk, (gradZ3D N M K hK p ijk) ^ 2) := by ring
        _ = 2 * (c * c) * (∑ ijk, (gradX3D N M K hN p ijk) ^ 2
            + ∑ ijk, (gradY3D N M K hM p ijk) ^ 2
            + ∑ ijk, (gradZ3D N M K hK p ijk) ^ 2) := by rw [step3]
    linear_combination -hC
  have hdrop : 0 ≤ c ^ 2 * (∑ ijk, (gradX3D N M K hN p ijk) ^ 2
      + ∑ ijk, (gradY3D N M K hM p ijk) ^ 2
      + ∑ ijk, (gradZ3D N M K hK p ijk) ^ 2) :=
    mul_nonneg (sq_nonneg _) hSnn
  linarith

/-- 3D Godunov predictor and full fractional step. -/
def godunov3D (N M K : ℕ) (hN : 0 < N) (hM : 0 < M) (hK : 0 < K) (μ : ℚ)
    (L : FluidLattice3D N M K) : FluidLattice3D N M K :=
  diffuse3D N M K hN hM hK μ (advect3D N M K hN L)

def full_ns_step3D (N M K : ℕ) (hN : 0 < N) (hM : 0 < M) (hK : 0 < K)
    (μ c : ℚ) (L : FluidLattice3D N M K) (p : (Fin N × Fin M) × Fin K → ℚ)
    : FluidLattice3D N M K :=
  project3D N M K hN hM hK c (godunov3D N M K hN hM hK μ L) p

/-- Main theorem in 3D: one full step never increases energy. -/
theorem energy_monotonic_decay3D (N M K : ℕ) (hN : 0 < N) (hM : 0 < M)
    (hK : 0 < K) (μ c C : ℚ) (hμ0 : 0 ≤ μ) (hμ1 : 6 * μ ≤ 1)
    (hc : c * C = 1) (hC : 0 < C) (L : FluidLattice3D N M K)
    (p : (Fin N × Fin M) × Fin K → ℚ)
    (hPoisson : ∀ ijk, lap3D N M K hN hM hK p ijk
      = C * bdiv3D N M K hN hM hK (godunov3D N M K hN hM hK μ L).vel ijk) :
    totalEnergy3D N M K (full_ns_step3D N M K hN hM hK μ c L p)
      ≤ totalEnergy3D N M K L :=
  le_trans (energy_project3D N M K hN hM hK c C hc hC _ _ hPoisson)
    (le_trans (energy_diffuse3D N M K hN hM hK μ hμ0 hμ1 _)
      (le_of_eq (energy_advect3D N M K hN _)))

/-! ## Multi-step horizon: energy never exceeds its initial value.

Each axis below composes its one-step theorem by induction. The
trajectory and per-step pressures are explicit arguments; the step
relation and Poisson contract are explicit hypotheses per step. -/

theorem energy_monotonic_k_steps1D (N : ℕ) (hN : 0 < N) (μ c C : ℚ)
    (hμ0 : 0 ≤ μ) (hμ1 : 2 * μ ≤ 1) (hc : c * C = 1) (hC : 0 < C)
    (traj : ℕ → FluidLattice N) (ps : ℕ → Fin N → ℚ)
    (hstep : ∀ n, traj (n + 1)
      = full_ns_step N hN μ c (traj n) (ps n))
    (hpois : ∀ n, ∀ i, lapAt N hN (ps n) i
      = C * bdivAt N hN (godunov_predict N hN μ (traj n)).vel i)
    (k : ℕ) :
    totalEnergy N (traj k) ≤ totalEnergy N (traj 0) := by
  induction k with
  | zero => exact le_rfl
  | succ k ih =>
    calc totalEnergy N (traj (k + 1))
        = totalEnergy N (full_ns_step N hN μ c (traj k) (ps k)) := by
          rw [hstep k]
      _ ≤ totalEnergy N (traj k) :=
          energy_monotonic_decay N hN μ c C hμ0 hμ1 hc hC _ _ (hpois k)
      _ ≤ totalEnergy N (traj 0) := ih

theorem energy_monotonic_k_steps2D (N M : ℕ) (hN : 0 < N) (hM : 0 < M)
    (μ c C : ℚ) (hμ0 : 0 ≤ μ) (hμ1 : 4 * μ ≤ 1) (hc : c * C = 1)
    (hC : 0 < C) (traj : ℕ → FluidLattice2D N M)
    (ps : ℕ → Fin N × Fin M → ℚ)
    (hstep : ∀ n, traj (n + 1)
      = full_ns_step2D N M hN hM μ c (traj n) (ps n))
    (hpois : ∀ n, ∀ ij, lap2D N M hN hM (ps n) ij
      = C * bdiv2D N M hN hM (godunov2D N M hN hM μ (traj n)).vel ij)
    (k : ℕ) :
    totalEnergy2D N M (traj k) ≤ totalEnergy2D N M (traj 0) := by
  induction k with
  | zero => exact le_rfl
  | succ k ih =>
    calc totalEnergy2D N M (traj (k + 1))
        = totalEnergy2D N M (full_ns_step2D N M hN hM μ c (traj k) (ps k)) := by
          rw [hstep k]
      _ ≤ totalEnergy2D N M (traj k) :=
          energy_monotonic_decay2D N M hN hM μ c C hμ0 hμ1 hc hC _ _
            (hpois k)
      _ ≤ totalEnergy2D N M (traj 0) := ih

theorem energy_monotonic_k_steps3D (N M K : ℕ) (hN : 0 < N) (hM : 0 < M)
    (hK : 0 < K) (μ c C : ℚ) (hμ0 : 0 ≤ μ) (hμ1 : 6 * μ ≤ 1)
    (hc : c * C = 1) (hC : 0 < C) (traj : ℕ → FluidLattice3D N M K)
    (ps : ℕ → (Fin N × Fin M) × Fin K → ℚ)
    (hstep : ∀ n, traj (n + 1)
      = full_ns_step3D N M K hN hM hK μ c (traj n) (ps n))
    (hpois : ∀ n, ∀ ijk, lap3D N M K hN hM hK (ps n) ijk
      = C * bdiv3D N M K hN hM hK
        (godunov3D N M K hN hM hK μ (traj n)).vel ijk)
    (k : ℕ) :
    totalEnergy3D N M K (traj k) ≤ totalEnergy3D N M K (traj 0) := by
  induction k with
  | zero => exact le_rfl
  | succ k ih =>
    calc totalEnergy3D N M K (traj (k + 1))
        = totalEnergy3D N M K
            (full_ns_step3D N M K hN hM hK μ c (traj k) (ps k)) := by
          rw [hstep k]
      _ ≤ totalEnergy3D N M K (traj k) :=
          energy_monotonic_decay3D N M K hN hM hK μ c C hμ0 hμ1 hc hC _ _
            (hpois k)
      _ ≤ totalEnergy3D N M K (traj 0) := ih

end NavierStokesCore
