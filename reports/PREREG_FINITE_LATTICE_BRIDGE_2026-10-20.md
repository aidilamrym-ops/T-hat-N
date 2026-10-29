# Pra-registrasi V6 â€” jembatan kisi berhingga â†’ Mellin tak hingga (limit galat eksplisit) â€” 2026-10-20

**Status:** scope DIKUNCI for paket ini; eksekusi in bawah arahan pemilik
"formulasikan teorema analitik murni ... which mampu menjembatani sifat tak terhingga
matematika kontinu menuju representasi kisi berhingga" which tercatat in sesi
2026-10-20, and answer eksplisit "Eksekusi V6 sekarang".

**Berkas target:** `lean/spec_v6/FiniteLatticeBridge.lean` (baru).
**Dependensi:** Mathlib v4.33.1 (nama lemma difaktakan dari checkout ini), and
`lean/spec_v4/XiUnconditional.lean` (baca-saja) for
`completedCosZeta_half_eq_mellin`.
**Registry which direncanakan:** `A-2026-0020`.
**Tidak mengubah:** V1 (`A-2026-0015`), V2 (`A-2026-0017`), V3 (`A-2026-0018`),
V4 (`A-2026-0019`), `ci.yml` (`A-2026-0016`), `spec-v3.yml`, `spec-v4.yml`,
seluruh report beku, and `lean/lakefile.toml`.

## 1. Latar

V4 membuktikan `hmid` secara analitik murni, **tanpa** memakai kisi berhingga:
`completedCosZeta (1/2)` dinyatakan sebagai transformasi Mellin dari kernel
`cosKernel (1/2) t - 1`, lalu tanda negatifnya dibaca dari integral riil.
Deret kernel itu sendiri adalah deret alternating tak hingga. Instrumen kisi
(MSAF) selama ini hanya memotong deret/integral on N suku; tanpa teorema galat,
pemotongan itu bukan representasi which sah dari objek tak hingga.

V6 menutup celah itu: ia membuktikan bahwa **nilai kisi N-suku** merupakan
aproksimasi bersertifikat dari `completedCosZeta (1/2)`, with galat eksplisit,
and bahwa tanda negatif objek tak hingga dapat **ditransfer** dari sertifikat
kisi berhingga. Ini murni analitik (tanpa numerik, tanpa aksioma proyek), and
no mengklaim RH.

## 2. Objek and notasi

Untuk `t > 0`:

```text
kHalf t    := cosKernel (1/2) t - 1                      (riil)
a_n(t)     := 2 * exp(-Ï€ * (n+1)^2 * t)                  (magnitudo suku ke-n)
S_N(t)     := Î£_{n<N} (-1)^(n+1) * a_n(t)                (kisi berhingga N suku)
```

Karena `âˆ«_0^âˆž t^(x/2-1) e^{-r t} dt = Î“(x/2) / r^(x/2)` (Mathlib
`integral_rpow_mul_exp_neg_mul_Ioi`), nilai kisi **tertutup**:

```text
Î›_N(x) := Î“(x/2) * Ï€^(-x/2) * Î£_{n<N} (-1)^(n+1) * (n+1)^(-x)
E_N(x) := Î“(x/2) * Ï€^(-x/2) * (N+1)^(-x)
```

`Î›_N` adalah bilangan riil which dapat dihitung (jumlah hingga + Î“), bukan
integral. `E_N` adalah limit galat eksplisit.

## 3. Pernyataan which dibuktikan

```text
T1  abs_kHalf_sub_lattice_le :
      âˆ€ t > 0, âˆ€ N, |kHalf t - S_N t| â‰¤ a_N(t)

T2  completedCosZeta_half_lattice_error :
      âˆ€ x > 0, âˆ€ N,
        â€–completedCosZeta (1/2) (x : â„‚) - (Î›_N(x) : â„‚)â€– â‰¤ E_N(x)

T3  completedCosZeta_half_neg_of_lattice_certificate :
      âˆ€ x > 0, âˆ€ N, Î›_N(x) + E_N(x) < 0 â†’
        (completedCosZeta (1/2) (x : â„‚)).re < 0

K1  completedCosZeta_half_neg_of_first_term :
      âˆ€ x > 0, (completedCosZeta (1/2) (x : â„‚)).re < 0
      (khususnya N = 1: Î›_1(x) + E_1(x) = Î“(x/2) Ï€^(-x/2) (2^(-x) - 1) < 0)
```

T2 adalah jembatan kuantitatif; T3 adalah transfer tanda; K1 menunjukkan bahwa
sertifikat N=1 already cukup for seluruh sumbu positif. **K1 bukan bukti RH**
and bukan pengganti V4: objeknya `completedCosZeta`, bukan
`completedRiemannZeta`; konversi ke `hmid` memerlukan identitas eta V4 which
tetap menjadi rute tersegel V4.

## 4. Rute pembuktian

1. **T1.** Deret kernel dari `hasSum_nat_cosKernelâ‚€ (a := 1/2)` (sama seperti
   V4). Magnitudo `a_n(t)` antiton (`latticeTerm_antitone`) and summable
   (perbandingan geometrik, pola V4). Terapkan
   `alternating_series_error_bound` (`Mathlib/Analysis/SpecificLimits/Normed.lean:856`)
   on `a_n`; peniadaan tanda `(-1)^(n+1) = -(-1)^n` no mengubah nilai mutlak.

2. **T2.** Pakai `completedCosZeta_half_eq_mellin` (V4) and representasi integral
   riil (`mellin_fC_real`, disalin dari V4 karena `fC` V4 privat; V6 mendefinisikan
   `fC t := (cosKernel (1/2) t : â„‚) - 1`, which **terbukti definisi-sama** with
   `fC` V4 â€” probe kompilasi exit 0). Lalu:
   - `(1/2) âˆ« t^(x/2-1) S_N(t) dt = Î›_N(x)` (jumlah hingga integral Gamma,
     `integral_finset_sum` + `integral_rpow_mul_exp_neg_mul_Ioi`);
   - selisihnya = `(1/2) âˆ« t^(x/2-1) (kHalf - S_N)`, dibatasi T1;
   - `abs_integral_le_integral_abs` + `integral_mono_ae`;
   - integral mayoran = `2 E_N(x)`, dikali `1/2` menjadi `E_N(x)`.
   Integrabilitas mayoran dari `integrableOn_rpow_mul_exp_neg_mul_rpow`
   (`Mathlib/Analysis/SpecialFunctions/Gaussian/GaussianIntegral.lean:74`).

3. **T3.** Dari T2: `(z - Î›_N).re â‰¤ â€–z - Î›_Nâ€– â‰¤ E_N`, jadi
   `z.re â‰¤ Î›_N + E_N < 0` (`Complex.re_le_norm`). Tidak perlu realness `z`.

4. **K1.** `N = 1`: `Î›_1 = -Î“(x/2) Ï€^(-x/2)`, `E_1 = Î“(x/2) Ï€^(-x/2) 2^(-x)`,
   and `2^(-x) < 1` for `x > 0` (`Real.rpow_lt_rpow_of_exponent_lt`).

## 5. Kriteria penerimaan

1. `lake env lean lean/spec_v6/FiniteLatticeBridge.lean` keluar 0, dari eksekusi
   nyata (with olean V4 tersedia in `.lake/build/lib/lean/spec_v4/`).
2. `#print axioms` for T1, T2, T3, K1 hanya `propext`, `Classical.choice`,
   `Quot.sound`; tanpa `sorryAx`, tanpa aksioma proyek.
3. Guard `msaf/tests/test_xi_spec_v6.py`: pemindaian statis (tanpa `axiom`,
   tanpa `sorry/admit/unsafe`), probe `#print axioms`, and pemeriksaan workflow;
   fail-closed.
4. Workflow `.github/workflows/spec-v6.yml` (pola V4), scoped ke
   `lean/spec_v6/**` and guard; tanpa `continue-on-error`.
5. Gate log `reports/anti_circularity_gate_v6_2026-10-20.log`; sub-gerbang audit
   SMT tetap `TOOL NOT RUN` (no ada `.smt2`) and no dihitung sukses.
6. Registry `A-2026-0020` (5 sertifikat sha256LF), `HANDOFF` Â§2.0am,
   `test_fence_registry.py` hijau, suite penuh hijau, freeze-verify OK.

## 6. Batas eksplisit

- **Bukan** bukti RH, bukan lokasi nol, bukan penurunan `Ïƒ = 1/2` dari kisi.
  Audit L11/L12 (`msaf/AUDIT.md`) already menunjukkan klaim kisi lama tautologis
  or imposisi; V6 no mengubah itu.
- Jembatan which menyentuh garis kritis secara langsung memerlukan rumus eksplisit
  Weilâ€“Guinand or konvergensi spektral nol; keduanya no ada in Mathlib
  v4.33.1 and **no diklaim**.
- T3 bersifat kondisional on sertifikat `Î›_N + E_N < 0`; K1 membuktikan bahwa
  for `N = 1` sertifikat itu valid for semua `x > 0`, tetapi K1 hanya
  menyimpulkan tanda `completedCosZeta`, bukan `completedRiemannZeta`.
- Tidak ada angka numerik which diklaim sebagai fakta; semua pernyataan T1â€“K1
  adalah teorema kernel. `TOOL NOT RUN` no pernah dihitung sukses.
- Gate PASS hanya pemindaian placeholder, bukan bukti kebenaran; kernel adalah
  otoritas.

## 7. Rekaman koreksi formulasi

Formulasi awal in sesi memakai kotak hingga `[1/T, T]` with galat
`(2/x)T^(-x/2)`. Saat formalisasi, ternyata integral kisi N-suku memiliki bentuk
tertutup Gamma, sehingga pemotongan kotak no diperlukan and galat which benar
adalah `E_N(x) = Î“(x/2) Ï€^(-x/2) (N+1)^(-x)`. Koreksi ini dicatat in sini and
menggantikan formulasi kotak; no ada rute which diganti secara diam-diam.

### 7.1 Penyelarasan definisi formal (2026-10-20)

Selama pengembangan, bentuk basis gabungan `(Ï€ (n+1)^2)^(-x/2)` sempat dipakai
karena lebih mudah dibaca oleh `integral_rpow_mul_exp_neg_mul_Ioi`. Lemma
`rpow_pi_mul_sq` membuktikan

```text
(Ï€ (n+1)^2)^(-x/2) = Ï€^(-x/2) * (n+1)^(-x)      (x âˆˆ â„, n âˆˆ â„•),
```

sehingga bentuk itu identik with Â§2. Definisi final `latticeValue` and
`latticeError` memakai bentuk terpisah Â§2 (`latticeScale x = Î“(x/2) Ï€^(-x/2)`);
pernyataan T1â€“K1 no berubah. Catatan ini menutup celah antara rumus which
dipra-registrasi and definisi formal which dikompilasi.

Satu detail sintaksis which wajib dijaga: integral harus ditulis
`(âˆ« t : â„ in Ioi 0, body) - X`, bukan `âˆ« t : â„ in Ioi 0, body - X`,
karena bentuk kedua menyerap `- X` ke dalam integran. Kesalahan parsing ini
sempat muncul saat menyusun T2 and diperbaiki sebelum seal; bentuk berparentesis
dipakai in seluruh bukti V6.


