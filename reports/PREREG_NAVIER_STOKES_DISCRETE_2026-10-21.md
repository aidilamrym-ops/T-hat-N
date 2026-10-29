# Pra-registrasi: Navier-Stokes â€” Kernel Diskrit Tercek Lean â€” 2026-10-21

**Status:** scope DIKUNCI for paket Navier-Stokes; implementasi and eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket. Hash `sha256LF` file ini
dicatat in receipt and report.

**Paket:** Navier-Stokes â€” Kernel diskrit tercek-Lean (dari `DAFTAR_MASALAH_KERJA.md`,
item 5 "Navier-Stokes TREK AKTIF â€” Kernel diskrit tercek-Lean; regularitas global TAK tersentuh").

**Berkas target:** `lean/spec_v7/NavierStokesDiscrete.lean` (baru), `lean/spec_v7/NavierStokesDiscrete.lean` (already ada: `NavierStokesCore.lean`), guard Lean `lake build`, report `reports/NAVIER_STOKES_DISCRETE_2026-10-21.md`, receipt `reports/navier_stokes_discrete.json`.

**Dependensi:** Lean 4, Mathlib4, `NavierStokesCore.lean` (tersegel, 60 lemmas/theorems), `lakefile.toml`, freeze pins. Tidak ada `numpy`/`scipy` in jalur inti.

**Registry which direncanakan:** `A-2026-0038`, hanya bila verdict inti `ALL PASS` and integritas PASS.

**Tidak mengubah:** V1â€“V6 (`A-2026-0015`â€“`A-2026-0021`), `A-2026-0022`â€“`A-2026-0037`, `ci.yml` (`A-2026-0016`), workflow spec, `lean/lakefile.toml`, freeze pins, seluruh report/artefak beku.

## 1. Maksud and limit

Paket ini melakukan **verifikasi formal Lean 4** atas kernel diskrit Navier-Stokes which already tersegel in Python/Arb (`msaf/navier_stokes/fluid_lattice.py`), khususnya:

1. **Adveksi (T-hat):** Permutasi siklik exak â€” `energy_advect`, `energy_advect2D`, `energy_advect3D` tersegel.
2. **Difusi (CFL):** Kombinasi konveks titik-titik â€” `energy_diffuse`, `energy_diffuse2D`, `energy_diffuse3D` tersegel.
3. **Proyeksi (Chorin):** `Î”p = C Â· div u*` kontrak â€” `energy_project`, `energy_project2D`, `energy_project3D` tersegel.
4. **Langkah penuh:** `energy_monotonic_decay`, `energy_monotonic_decay2D`, `energy_monotonic_decay3D` tersegel.

**Paket ini BUKAN:**
- Pembuktian regularitas global Navier-Stokes (hanya kernel diskrit)
- Klaim regularitas/blow-up for PDE kontinu
- Klaim RH, faktorisasi, RSA/ECC, Anderson, fisika
- Rekomputasi numerik (hanya verifikasi formal Lean atas lemmas tersegel)

## 2. Artefak which already tersegel (NavierStokesCore.lean)

**60 lemmas/theorems tersegel in `lean/NavierStokesCore.lean`:**

| Kategori | Lema/Teorema |
|---|---|
| Permutasi T-hat | `mod_shift_cancel_left`, `mod_shift_cancel_right`, `shiftPerm`, `sum_fwd`, `sum_bwd`, `sum_fwd_to_bwd` |
| Adveksi | `energy_advect`, `energy_advect2D`, `energy_advect3D` |
| Difusi CFL | `convex_sq`, `scalar_diffuse_le`, `energy_diffuse`, `convex_sq5`, `scalar_diffuse2D`, `energy_diffuse2D`, `convex_sq7`, `scalar_diffuse3D`, `energy_diffuse3D` |
| Proyeksi Chorin | `energy_project`, `energy_project2D`, `energy_project3D` |
| SBP (Summation by Parts) | `sbp_grad_div`, `sbp_lap_neg`, `sbp_grad_div2D`, `sbp_lap_negX`, `sbp_lap_negY`, `sbp_lap_neg2D`, `sbp_lap_negX3D`, `sbp_lap_negY3D`, `sbp_lap_negZ3D`, `sbp_lap_neg3D` |
| Proyeksi Chorin (energi) | `energy_project`, `energy_project2D`, `energy_project3D` |
| Energi Monotonik | `energy_monotonic_decay`, `energy_monotonic_decay2D`, `energy_monotonic_decay3D` |
| 2D/3D Ekstensi | Semua lemmas in atas punya varian 2D/3D tersegel |

**Total: 60 lemmas/theorems tersegel in `NavierStokesCore.lean`**

## 3. Scope which dikunci

**Verifikasi formal Lean 4 atas lemmas tersegel:**
- Tidak ada lemmas/theorems baru which dibuktikan
- Hanya verifying bahwa `lake build` lolos for `NavierStokesCore.lean`
- Memastikan no ada regresi (semua 60 lemmas/theorems tetap tersegel)
- Memastikan `lakefile.toml` and `lean-toolchain` konsisten

**Parameter which dikunci:**
| Parameter | Nilai |
|---|---|
| Lean version | `leanprover/lean4:4.9.0` (or which in `lean-toolchain`) |
| Mathlib version | Yang in `lake-manifest.json` |
| File target | `lean/NavierStokesCore.lean` (already ada) |

## 4. Pemeriksaan integritas (C1â€“C4)

**C1: Lean Build PASS**
- `lake build` exit code 0
- Semua 60 lemmas/theorems tersegel tanpa error

**C2: Tidak Ada Regresi**
- Semua 60 lemmas/theorems tetap tersegel
- Tidak ada lemmas which dihapus/dimodifikasi

**C3: Determinisme**
- `lake build` deterministik (exit code 0, output konsisten)

**C4: Integritas Freeze**
- `python audit_quantum/freeze.py --verify` PASS (14 pins)

## 5. Verdict

- **ALL PASS**: `lake build` PASS, 0 regressi, freeze PASS
- **PARTIAL**: Build PASS tapi ada warning (no error)
- **FAILED**: `lake build` gagal / ada error / regresi lemmas
- **INCONCLUSIVE**: Tool error / timeout

Registry `A-2026-0038` hanya bila verdict `ALL PASS` and integritas PASS.

## 6. Falsifier

Paket ini falsified bila:
- `lake build` gagal / exit code â‰  0
- Ada lemmas which no tersegel (regressi)
- Ada lemmas which dihapus dari `NavierStokesCore.lean`
- `freeze.py --verify` gagal
- Ada modifikasi on `NavierStokesCore.lean` which no disengaja

## 7. Artefak and urutan eksekusi

1. Tulis and hash pra-registrasi ini sebelum kode.
2. Verifikasi `lake build` for `lean/NavierStokesCore.lean`.
3. Jalankan `lake build` ulang for memastikan determinisme.
4. Tulis report `reports/NAVIER_STOKES_DISCRETE_2026-10-21.md` with status build.
5. Bila `ALL PASS`: registry `A-2026-0038`, HANDOFF Â§2.0be, sertifikat sha256LF.
6. `freeze.py --verify`; commit/push hanya bila diminta.

## 8. Batas eksplisit

- Hanya verifikasi formal Lean atas lemmas tersegel (bukan pembuktian baru)
- Tidak ada klaim regularitas global Navier-Stokes
- Tidak ada klaim blow-up/blow-down PDE kontinu
- Tidak ada klaim RH, faktorisasi, RSA/ECC, Anderson, fisika
- Hanya verifikasi kernel diskrit which already tersegel

