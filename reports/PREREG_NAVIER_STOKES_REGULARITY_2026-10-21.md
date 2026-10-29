# Pra-registrasi: Navier-Stokes â€” Analisis Regularitas Diskrit â€” 2026-10-21

**Status:** scope DIKUNCI for paket Navier-Stokes Regularitas; implementasi and eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket. Hash `sha256LF` file ini
dicatat in receipt and report.

**Paket:** Navier-Stokes Regularitas â€” Analisis kriteria regularitas diskrit
(Ladyzhenskaya-Prodi-Serrin diskrit, Beale-Kato-Majda diskrit, spektrum energi)
on kernel diskrit 3D which already tersegel (`A-2026-0038`).

**Berkas target:** `msaf/navier_stokes/regularity.py` (baru), `lean/spec_v8/NavierStokesRegularity.lean` (baru),
guard `msaf/tests/test_navier_stokes_regularity.py` (baru), report
`reports/NAVIER_STOKES_REGULARITY_2026-10-21.md`, receipt
`reports/navier_stokes_regularity.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (`arb`, `acb`), `msaf/navier_stokes/fluid_lattice.py`,
`lean/NavierStokesCore.lean` (tersegel `A-2026-0038`). Lean 4, Mathlib4 for formalisasi baru.
Tidak ada `numpy`/`scipy` in jalur inti.

**Registry which direncanakan:** `A-2026-0039`, hanya bila verdict inti
`ALL PASS` and integritas PASS.

**Tidak mengubah:** V1â€“V6 (`A-2026-0015`â€“`A-2026-0021`), `A-2026-0022`â€“`A-2026-0038`,
`ci.yml` (`A-2026-0016`), workflow spec, `lean/lakefile.toml`, freeze pins,
seluruh report/artefak beku.

## 1. Maksud and limit

Paket ini menambahkan **analisis regularitas diskrit** on kernel Navier-Stokes 3D
which already tersegel (`A-2026-0038`), tanpa mengklaim regularitas PDE kontinu.

**Objek analisis:**
1. **Ladyzhenskaya-Prodi-Serrin Diskrit (LPS-D):** Kriteria regularitas berbasis norma
   diskrit `â„“^p_t â„“^q_x` on laju `u` and gradien `âˆ‡u`.
2. **Beale-Kato-Majda Diskrit (BKM-D):** Kriteria blow-up berbasis vortisitas
   `Ï‰ = âˆ‡ Ã— u` and norma `â„“^âˆž_t â„“^1_x`.
3. **Spektrum Energi:** Analisis `E(k)` and hukum kolmogorov `-5/3` on grid diskrit.
4. **Struktur Fungsi (Structure Functions):** `S_p(r) = âŸ¨|Î´u|^pâŸ©` and eksponen intermittent `Î¶_p`.

**Paket ini BUKAN:**
- Pembuktian regularitas PDE Navier-Stokes kontinu (hanya analisis diskrit)
- Klaim blow-up/blow-down PDE kontinu
- Klaim RH, faktorisasi, RSA/ECC, Anderson, fisika
- Simulasi DNS penuh (hanya analisis on kernel diskrit which ada)

## 2. Data input (tersegel dari A-2026-0038)

**Kernel diskrit 3D tersegel:**
- `FluidLattice3D` (NÃ—MÃ—K grid, N=M=K=4, dx=DELTA_UNIV)
- Adveksi T-hat 3D (`advect3D`), Difusi 7-titik (`diffuse3D`), Proyeksi 3D (`project3D`)
- Energi monotonik (`energy_monotonic_decay3D` tersegel)
- Vortisitas diskrit `Ï‰ = âˆ‡ Ã— u` via `curl_at(i,j,k)` (perlu ditambahkan)

**Simulasi referensi:** Rotasi Taylor-Green (TG) on grid 4Â³, Î½=10â»â´, dt=1e-43 s.

## 3. Algoritma which dikunci

### 3.1 Curl/Vortisitas Diskrit
```
Ï‰_x = âˆ‚_y u_z - âˆ‚_z u_y
Ï‰_y = âˆ‚_z u_x - âˆ‚_x u_z
Ï‰_z = âˆ‚_x u_y - âˆ‚_y u_x
```
Menggunakan selisih tengah (central difference) on grid periodik, ball arithmetic.

### 3.2 Ladyzhenskaya-Prodi-Serrin Diskrit (LPS-D)
Kriteria: `â€–uâ€–_{â„“^p_t â„“^q_x} < âˆž` with `2/p + 3/q = 1`, `q > 3`.
Implementasi: hitung norma `â„“^q_x` per step waktu, akumulasi `â„“^p_t`.

### 3.3 Beale-Kato-Majda Diskrit (BKM-D)
Kriteria: `âˆ«_0^T â€–Ï‰â€–_{â„“^âˆž_x} dt < âˆž` â†’ no blow-up.
Implementasi: `max_{i,j,k} |Ï‰(i,j,k)|` per step, akumulasi waktu.

### 3.4 Spektrum Energi
`E(k) = 1/2 Î£_{|Îº|=k} |Ã»(Îº)|Â²` via FFT diskrit (exact rational).
Validasi hukum Kolmogorov `E(k) ~ C Îµ^{2/3} k^{-5/3}`.

### 3.5 Struktur Fungsi
`S_p(r) = âŸ¨|u(x+r) - u(x)|^pâŸ©`, eksponen `Î¶_p` dari regresi log-log.

## 4. Konfigurasi which dikunci

| Parameter | Nilai |
|---|---|
| Grid | N=M=K=4 (dx=DELTA_UNIV) |
| Viskositas | Î½=10â»â´ |
| dt | 1e-43 s (1 Planck tick) |
| Kondisi awal | Taylor-Green vortex |
| Langkah waktu | 20 step (20 Planck ticks) |
| Presisi | 384-bit (Arb) |

## 5. Pemeriksaan integritas (C1â€“C4)

**C1: LPS-D Terpenuhi**
- Norma `â„“^p_t â„“^q_x` terhitung, `2/p + 3/q = 1`, `q > 3`.

**C2: BKM-D Terpenuhi**
- `âˆ« â€–Ï‰â€–_âˆž dt < âˆž` terverifikasi (akumulasi terbatas).

**C3: Spektrum Energi**
- `E(k)` dihitung, regresi log-log for eksponen `-5/3`.

**C4: Determinisme & Receipt**
- Output deterministik, hash sha256LF terkunci.

## 6. Verdict

- **ALL PASS**: LPS-D, BKM-D, spektrum, struktur fungsi semuanya terverifikasi.
- **PARTIAL**: Sebagian terverifikasi, sebagian gagal/timeout.
- **FAILED**: Gagal fundamental (algoritma salah, overflow, dsb).
- **INCONCLUSIVE**: Tool error / timeout / hash mismatch.

Registry `A-2026-0039` hanya bila verdict `ALL PASS` and integritas PASS.

## 7. Falsifier

Paket ini falsified bila:
- Algoritma curl/vortisitas salah (no memenuhi `âˆ‡Â·Ï‰=0` diskrit).
- Norma LPS-D/BKM-D overflow/underflow.
- Spektrum energi no menunjukkan skala `-5/3` (on skala inertial).
- Receipt no deterministik or hash mismatch.

## 8. Artefak and urutan eksekusi

1. Tulis and hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/navier_stokes/regularity.py` (curl, LPS-D, BKM-D, spektrum, struktur fungsi).
3. Formalisasi Lean `lean/spec_v8/NavierStokesRegularity.lean` (definisi + teorema LPS-D/BKM-D diskrit).
3. Guard `msaf/tests/test_navier_stokes_regularity.py` (uji curl, LPS-D, BKM-D, spektrum).
4. Jalankan kampanye TG on grid 4Â³, 20 step, presisi 384-bit.
5. Tulis report `reports/NAVIER_STOKES_REGULARITY_2026-10-21.md` with angka verbatim.
6. Bila `ALL PASS`: registry `A-2026-0039`, HANDOFF Â§2.0bf, sertifikat sha256LF.
7. Suite penuh and `freeze.py --verify`; commit/push hanya bila diminta.

## 9. Batas eksplisit

- Hanya analisis regularitas **diskrit** on kernel which already tersegel.
- Tidak ada klaim regularitas PDE kontinu / Clay Millennium Prize.
- Tidak ada klaim blow-up/blow-down PDE kontinu.
- Tidak ada klaim RH, faktorisasi, RSA/ECC, Anderson, fisika.
- Grid 4Â³ (kecil), bukan DNS penuh.

