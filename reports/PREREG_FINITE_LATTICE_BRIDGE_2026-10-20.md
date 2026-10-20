# Pra-registrasi V6 — jembatan kisi berhingga → Mellin tak hingga (batas galat eksplisit) — 2026-10-20

**Status:** scope DIKUNCI untuk paket ini; eksekusi di bawah arahan pemilik
"formulasikan teorema analitik murni ... yang mampu menjembatani sifat tak terhingga
matematika kontinu menuju representasi kisi berhingga" yang tercatat di sesi
2026-10-20, dan jawaban eksplisit "Eksekusi V6 sekarang".

**Berkas target:** `lean/spec_v6/FiniteLatticeBridge.lean` (baru).
**Dependensi:** Mathlib v4.33.1 (nama lemma difaktakan dari checkout ini), dan
`lean/spec_v4/XiUnconditional.lean` (baca-saja) untuk
`completedCosZeta_half_eq_mellin`.
**Registry yang direncanakan:** `A-2026-0020`.
**Tidak mengubah:** V1 (`A-2026-0015`), V2 (`A-2026-0017`), V3 (`A-2026-0018`),
V4 (`A-2026-0019`), `ci.yml` (`A-2026-0016`), `spec-v3.yml`, `spec-v4.yml`,
seluruh laporan beku, dan `lean/lakefile.toml`.

## 1. Latar

V4 membuktikan `hmid` secara analitik murni, **tanpa** memakai kisi berhingga:
`completedCosZeta (1/2)` dinyatakan sebagai transformasi Mellin dari kernel
`cosKernel (1/2) t - 1`, lalu tanda negatifnya dibaca dari integral riil.
Deret kernel itu sendiri adalah deret alternating tak hingga. Instrumen kisi
(MSAF) selama ini hanya memotong deret/integral pada N suku; tanpa teorema galat,
pemotongan itu bukan representasi yang sah dari objek tak hingga.

V6 menutup celah itu: ia membuktikan bahwa **nilai kisi N-suku** merupakan
aproksimasi bersertifikat dari `completedCosZeta (1/2)`, dengan galat eksplisit,
dan bahwa tanda negatif objek tak hingga dapat **ditransfer** dari sertifikat
kisi berhingga. Ini murni analitik (tanpa numerik, tanpa aksioma proyek), dan
tidak mengklaim RH.

## 2. Objek dan notasi

Untuk `t > 0`:

```text
kHalf t    := cosKernel (1/2) t - 1                      (riil)
a_n(t)     := 2 * exp(-π * (n+1)^2 * t)                  (magnitudo suku ke-n)
S_N(t)     := Σ_{n<N} (-1)^(n+1) * a_n(t)                (kisi berhingga N suku)
```

Karena `∫_0^∞ t^(x/2-1) e^{-r t} dt = Γ(x/2) / r^(x/2)` (Mathlib
`integral_rpow_mul_exp_neg_mul_Ioi`), nilai kisi **tertutup**:

```text
Λ_N(x) := Γ(x/2) * π^(-x/2) * Σ_{n<N} (-1)^(n+1) * (n+1)^(-x)
E_N(x) := Γ(x/2) * π^(-x/2) * (N+1)^(-x)
```

`Λ_N` adalah bilangan riil yang dapat dihitung (jumlah hingga + Γ), bukan
integral. `E_N` adalah batas galat eksplisit.

## 3. Pernyataan yang dibuktikan

```text
T1  abs_kHalf_sub_lattice_le :
      ∀ t > 0, ∀ N, |kHalf t - S_N t| ≤ a_N(t)

T2  completedCosZeta_half_lattice_error :
      ∀ x > 0, ∀ N,
        ‖completedCosZeta (1/2) (x : ℂ) - (Λ_N(x) : ℂ)‖ ≤ E_N(x)

T3  completedCosZeta_half_neg_of_lattice_certificate :
      ∀ x > 0, ∀ N, Λ_N(x) + E_N(x) < 0 →
        (completedCosZeta (1/2) (x : ℂ)).re < 0

K1  completedCosZeta_half_neg_of_first_term :
      ∀ x > 0, (completedCosZeta (1/2) (x : ℂ)).re < 0
      (khususnya N = 1: Λ_1(x) + E_1(x) = Γ(x/2) π^(-x/2) (2^(-x) - 1) < 0)
```

T2 adalah jembatan kuantitatif; T3 adalah transfer tanda; K1 menunjukkan bahwa
sertifikat N=1 sudah cukup untuk seluruh sumbu positif. **K1 bukan bukti RH**
dan bukan pengganti V4: objeknya `completedCosZeta`, bukan
`completedRiemannZeta`; konversi ke `hmid` memerlukan identitas eta V4 yang
tetap menjadi rute tersegel V4.

## 4. Rute pembuktian

1. **T1.** Deret kernel dari `hasSum_nat_cosKernel₀ (a := 1/2)` (sama seperti
   V4). Magnitudo `a_n(t)` antiton (`latticeTerm_antitone`) dan summable
   (perbandingan geometrik, pola V4). Terapkan
   `alternating_series_error_bound` (`Mathlib/Analysis/SpecificLimits/Normed.lean:856`)
   pada `a_n`; peniadaan tanda `(-1)^(n+1) = -(-1)^n` tidak mengubah nilai mutlak.

2. **T2.** Pakai `completedCosZeta_half_eq_mellin` (V4) dan representasi integral
   riil (`mellin_fC_real`, disalin dari V4 karena `fC` V4 privat; V6 mendefinisikan
   `fC t := (cosKernel (1/2) t : ℂ) - 1`, yang **terbukti definisi-sama** dengan
   `fC` V4 — probe kompilasi exit 0). Lalu:
   - `(1/2) ∫ t^(x/2-1) S_N(t) dt = Λ_N(x)` (jumlah hingga integral Gamma,
     `integral_finset_sum` + `integral_rpow_mul_exp_neg_mul_Ioi`);
   - selisihnya = `(1/2) ∫ t^(x/2-1) (kHalf - S_N)`, dibatasi T1;
   - `abs_integral_le_integral_abs` + `integral_mono_ae`;
   - integral mayoran = `2 E_N(x)`, dikali `1/2` menjadi `E_N(x)`.
   Integrabilitas mayoran dari `integrableOn_rpow_mul_exp_neg_mul_rpow`
   (`Mathlib/Analysis/SpecialFunctions/Gaussian/GaussianIntegral.lean:74`).

3. **T3.** Dari T2: `(z - Λ_N).re ≤ ‖z - Λ_N‖ ≤ E_N`, jadi
   `z.re ≤ Λ_N + E_N < 0` (`Complex.re_le_norm`). Tidak perlu realness `z`.

4. **K1.** `N = 1`: `Λ_1 = -Γ(x/2) π^(-x/2)`, `E_1 = Γ(x/2) π^(-x/2) 2^(-x)`,
   dan `2^(-x) < 1` untuk `x > 0` (`Real.rpow_lt_rpow_of_exponent_lt`).

## 5. Kriteria penerimaan

1. `lake env lean lean/spec_v6/FiniteLatticeBridge.lean` keluar 0, dari eksekusi
   nyata (dengan olean V4 tersedia di `.lake/build/lib/lean/spec_v4/`).
2. `#print axioms` untuk T1, T2, T3, K1 hanya `propext`, `Classical.choice`,
   `Quot.sound`; tanpa `sorryAx`, tanpa aksioma proyek.
3. Guard `msaf/tests/test_xi_spec_v6.py`: pemindaian statis (tanpa `axiom`,
   tanpa `sorry/admit/unsafe`), probe `#print axioms`, dan pemeriksaan workflow;
   fail-closed.
4. Workflow `.github/workflows/spec-v6.yml` (pola V4), scoped ke
   `lean/spec_v6/**` dan guard; tanpa `continue-on-error`.
5. Gate log `reports/anti_circularity_gate_v6_2026-10-20.log`; sub-gerbang audit
   SMT tetap `TOOL NOT RUN` (tidak ada `.smt2`) dan tidak dihitung sukses.
6. Registry `A-2026-0020` (5 sertifikat sha256LF), `HANDOFF` §2.0am,
   `test_fence_registry.py` hijau, suite penuh hijau, freeze-verify OK.

## 6. Batas eksplisit

- **Bukan** bukti RH, bukan lokasi nol, bukan penurunan `σ = 1/2` dari kisi.
  Audit L11/L12 (`msaf/AUDIT.md`) sudah menunjukkan klaim kisi lama tautologis
  atau imposisi; V6 tidak mengubah itu.
- Jembatan yang menyentuh garis kritis secara langsung memerlukan rumus eksplisit
  Weil–Guinand atau konvergensi spektral nol; keduanya tidak ada di Mathlib
  v4.33.1 dan **tidak diklaim**.
- T3 bersifat kondisional pada sertifikat `Λ_N + E_N < 0`; K1 membuktikan bahwa
  untuk `N = 1` sertifikat itu valid untuk semua `x > 0`, tetapi K1 hanya
  menyimpulkan tanda `completedCosZeta`, bukan `completedRiemannZeta`.
- Tidak ada angka numerik yang diklaim sebagai fakta; semua pernyataan T1–K1
  adalah teorema kernel. `TOOL NOT RUN` tidak pernah dihitung sukses.
- Gate PASS hanya pemindaian placeholder, bukan bukti kebenaran; kernel adalah
  otoritas.

## 7. Rekaman koreksi formulasi

Formulasi awal di sesi memakai kotak hingga `[1/T, T]` dengan galat
`(2/x)T^(-x/2)`. Saat formalisasi, ternyata integral kisi N-suku memiliki bentuk
tertutup Gamma, sehingga pemotongan kotak tidak diperlukan dan galat yang benar
adalah `E_N(x) = Γ(x/2) π^(-x/2) (N+1)^(-x)`. Koreksi ini dicatat di sini dan
menggantikan formulasi kotak; tidak ada rute yang diganti secara diam-diam.

### 7.1 Penyelarasan definisi formal (2026-10-20)

Selama pengembangan, bentuk basis gabungan `(π (n+1)^2)^(-x/2)` sempat dipakai
karena lebih mudah dibaca oleh `integral_rpow_mul_exp_neg_mul_Ioi`. Lemma
`rpow_pi_mul_sq` membuktikan

```text
(π (n+1)^2)^(-x/2) = π^(-x/2) * (n+1)^(-x)      (x ∈ ℝ, n ∈ ℕ),
```

sehingga bentuk itu identik dengan §2. Definisi final `latticeValue` dan
`latticeError` memakai bentuk terpisah §2 (`latticeScale x = Γ(x/2) π^(-x/2)`);
pernyataan T1–K1 tidak berubah. Catatan ini menutup celah antara rumus yang
dipra-registrasi dan definisi formal yang dikompilasi.

Satu detail sintaksis yang wajib dijaga: integral harus ditulis
`(∫ t : ℝ in Ioi 0, body) - X`, bukan `∫ t : ℝ in Ioi 0, body - X`,
karena bentuk kedua menyerap `- X` ke dalam integran. Kesalahan parsing ini
sempat muncul saat menyusun T2 dan diperbaiki sebelum seal; bentuk berparentesis
dipakai di seluruh bukti V6.
