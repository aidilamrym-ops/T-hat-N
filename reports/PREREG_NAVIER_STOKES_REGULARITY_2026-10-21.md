# Pra-registrasi: Navier-Stokes — Analisis Regularitas Diskrit — 2026-10-21

**Status:** scope DIKUNCI untuk paket Navier-Stokes Regularitas; implementasi dan eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket. Hash `sha256LF` berkas ini
dicatat di receipt dan laporan.

**Paket:** Navier-Stokes Regularitas — Analisis kriteria regularitas diskrit
(Ladyzhenskaya-Prodi-Serrin diskrit, Beale-Kato-Majda diskrit, spektrum energi)
pada kernel diskrit 3D yang sudah tersegel (`A-2026-0038`).

**Berkas target:** `msaf/navier_stokes/regularity.py` (baru), `lean/spec_v8/NavierStokesRegularity.lean` (baru),
guard `msaf/tests/test_navier_stokes_regularity.py` (baru), laporan
`reports/NAVIER_STOKES_REGULARITY_2026-10-21.md`, receipt
`reports/navier_stokes_regularity.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (`arb`, `acb`), `msaf/navier_stokes/fluid_lattice.py`,
`lean/NavierStokesCore.lean` (tersegel `A-2026-0038`). Lean 4, Mathlib4 untuk formalisasi baru.
Tidak ada `numpy`/`scipy` di jalur inti.

**Registry yang direncanakan:** `A-2026-0039`, hanya bila verdict inti
`ALL PASS` dan integritas PASS.

**Tidak mengubah:** V1–V6 (`A-2026-0015`–`A-2026-0021`), `A-2026-0022`–`A-2026-0038`,
`ci.yml` (`A-2026-0016`), workflow spec, `lean/lakefile.toml`, freeze pins,
seluruh laporan/artefak beku.

## 1. Maksud dan batas

Paket ini menambahkan **analisis regularitas diskrit** pada kernel Navier-Stokes 3D
yang sudah tersegel (`A-2026-0038`), tanpa mengklaim regularitas PDE kontinu.

**Objek analisis:**
1. **Ladyzhenskaya-Prodi-Serrin Diskrit (LPS-D):** Kriteria regularitas berbasis norma
   diskrit `ℓ^p_t ℓ^q_x` pada laju `u` dan gradien `∇u`.
2. **Beale-Kato-Majda Diskrit (BKM-D):** Kriteria blow-up berbasis vortisitas
   `ω = ∇ × u` dan norma `ℓ^∞_t ℓ^1_x`.
3. **Spektrum Energi:** Analisis `E(k)` dan hukum kolmogorov `-5/3` pada grid diskrit.
4. **Struktur Fungsi (Structure Functions):** `S_p(r) = ⟨|δu|^p⟩` dan eksponen intermittent `ζ_p`.

**Paket ini BUKAN:**
- Pembuktian regularitas PDE Navier-Stokes kontinu (hanya analisis diskrit)
- Klaim blow-up/blow-down PDE kontinu
- Klaim RH, faktorisasi, RSA/ECC, Anderson, fisika
- Simulasi DNS penuh (hanya analisis pada kernel diskrit yang ada)

## 2. Data input (tersegel dari A-2026-0038)

**Kernel diskrit 3D tersegel:**
- `FluidLattice3D` (N×M×K grid, N=M=K=4, dx=DELTA_UNIV)
- Adveksi T-hat 3D (`advect3D`), Difusi 7-titik (`diffuse3D`), Proyeksi 3D (`project3D`)
- Energi monotonik (`energy_monotonic_decay3D` tersegel)
- Vortisitas diskrit `ω = ∇ × u` via `curl_at(i,j,k)` (perlu ditambahkan)

**Simulasi referensi:** Rotasi Taylor-Green (TG) pada grid 4³, ν=10⁻⁴, dt=1e-43 s.

## 3. Algoritma yang dikunci

### 3.1 Curl/Vortisitas Diskrit
```
ω_x = ∂_y u_z - ∂_z u_y
ω_y = ∂_z u_x - ∂_x u_z
ω_z = ∂_x u_y - ∂_y u_x
```
Menggunakan selisih tengah (central difference) pada grid periodik, ball arithmetic.

### 3.2 Ladyzhenskaya-Prodi-Serrin Diskrit (LPS-D)
Kriteria: `‖u‖_{ℓ^p_t ℓ^q_x} < ∞` dengan `2/p + 3/q = 1`, `q > 3`.
Implementasi: hitung norma `ℓ^q_x` per langkah waktu, akumulasi `ℓ^p_t`.

### 3.3 Beale-Kato-Majda Diskrit (BKM-D)
Kriteria: `∫_0^T ‖ω‖_{ℓ^∞_x} dt < ∞` → tidak blow-up.
Implementasi: `max_{i,j,k} |ω(i,j,k)|` per langkah, akumulasi waktu.

### 3.4 Spektrum Energi
`E(k) = 1/2 Σ_{|κ|=k} |û(κ)|²` via FFT diskrit (exact rational).
Validasi hukum Kolmogorov `E(k) ~ C ε^{2/3} k^{-5/3}`.

### 3.5 Struktur Fungsi
`S_p(r) = ⟨|u(x+r) - u(x)|^p⟩`, eksponen `ζ_p` dari regresi log-log.

## 4. Konfigurasi yang dikunci

| Parameter | Nilai |
|---|---|
| Grid | N=M=K=4 (dx=DELTA_UNIV) |
| Viskositas | ν=10⁻⁴ |
| dt | 1e-43 s (1 Planck tick) |
| Kondisi awal | Taylor-Green vortex |
| Langkah waktu | 20 langkah (20 Planck ticks) |
| Presisi | 384-bit (Arb) |

## 5. Pemeriksaan integritas (C1–C4)

**C1: LPS-D Terpenuhi**
- Norma `ℓ^p_t ℓ^q_x` terhitung, `2/p + 3/q = 1`, `q > 3`.

**C2: BKM-D Terpenuhi**
- `∫ ‖ω‖_∞ dt < ∞` terverifikasi (akumulasi terbatas).

**C3: Spektrum Energi**
- `E(k)` dihitung, regresi log-log untuk eksponen `-5/3`.

**C4: Determinisme & Receipt**
- Output deterministik, hash sha256LF terkunci.

## 6. Verdict

- **ALL PASS**: LPS-D, BKM-D, spektrum, struktur fungsi semuanya terverifikasi.
- **PARTIAL**: Sebagian terverifikasi, sebagian gagal/timeout.
- **FAILED**: Gagal fundamental (algoritma salah, overflow, dsb).
- **INCONCLUSIVE**: Tool error / timeout / hash mismatch.

Registry `A-2026-0039` hanya bila verdict `ALL PASS` dan integritas PASS.

## 7. Falsifier

Paket ini falsified bila:
- Algoritma curl/vortisitas salah (tidak memenuhi `∇·ω=0` diskrit).
- Norma LPS-D/BKM-D overflow/underflow.
- Spektrum energi tidak menunjukkan skala `-5/3` (pada skala inertial).
- Receipt tidak deterministik atau hash mismatch.

## 8. Artefak dan urutan eksekusi

1. Tulis dan hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/navier_stokes/regularity.py` (curl, LPS-D, BKM-D, spektrum, struktur fungsi).
3. Formalisasi Lean `lean/spec_v8/NavierStokesRegularity.lean` (definisi + teorema LPS-D/BKM-D diskrit).
3. Guard `msaf/tests/test_navier_stokes_regularity.py` (uji curl, LPS-D, BKM-D, spektrum).
4. Jalankan kampanye TG pada grid 4³, 20 langkah, presisi 384-bit.
5. Tulis laporan `reports/NAVIER_STOKES_REGULARITY_2026-10-21.md` dengan angka verbatim.
6. Bila `ALL PASS`: registry `A-2026-0039`, HANDOFF §2.0bf, sertifikat sha256LF.
7. Suite penuh dan `freeze.py --verify`; commit/push hanya bila diminta.

## 9. Batas eksplisit

- Hanya analisis regularitas **diskrit** pada kernel yang sudah tersegel.
- Tidak ada klaim regularitas PDE kontinu / Clay Millennium Prize.
- Tidak ada klaim blow-up/blow-down PDE kontinu.
- Tidak ada klaim RH, faktorisasi, RSA/ECC, Anderson, fisika.
- Grid 4³ (kecil), bukan DNS penuh.