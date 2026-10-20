# Pra-registrasi V4 — penutup `hmid` (tanda completed zeta pada `0 < x < 1`) — REVISI 2026-10-20

**Status:** scope DIKUNCI untuk revisi ini; eksekusi berjalan di bawah persetujuan pemilik
"lanjutkan dan selesaikan" yang tercatat di awal sesi. Revisi ini MENGgantikan draf
sebelumnya yang memakai rute simetri; rute simetri ditolak dan tidak boleh dipakai lagi.

**Berkas target:** `lean/spec_v4/XiUnconditional.lean` (baru; draf lama tidak valid dan
sudah diganti).
**Dependensi:** Mathlib v4.33.1 (nama lemma yang dipakai daftar di §3, semuanya
difaktakan dari berkas sumber Mathlib di checkout ini, bukan dari ingatan).
**Registry yang direncanakan:** `A-2026-0019`.
**Tidak mengubah:** V1 (`lean/spec/XiAnalyticSpec.lean`, `A-2026-0015`), V2
(`lean/spec_v2/XiAnalyticSpecV2.lean`, `A-2026-0017`), V3
(`lean/spec_v3/XiAnalyticFaithful.lean`, `A-2026-0018`), `ci.yml` (`A-2026-0016`),
seluruh laporan beku, dan `lean/lakefile.toml` tidak diubah untuk tahap ini
(V4 direncanakan standalone terhadap Mathlib saja; koneksi ke V3 dilakukan lewat
pernyataan lokal, bukan `import spec_v3`).

## 1. Latar

V3 (`A-2026-0018`) membuktikan `xi_pos_on_reals` secara kondisional terhadap satu
hipotesis analitik `hmid`:

```text
hmid : ∀ x : ℝ, 0 < x → x < 1 → (completedRiemannZeta (x : ℂ)).re < 0
```

V4 menutup `hmid` tanpa aksioma proyek, sehingga V3 menjadi teorema tanpa syarat.
Tidak ada klaim RH atau klaim fisika apa pun dalam paket ini.

## 2. Rute yang ditolak (rekaman wajib)

Draf pertama memakai argumen "simetri": memandang `1 - x` sebagai titik cermin
dengan `1 - x > 1` untuk `0 < x < 1`. Itu keliru secara matematis: `1 - x` tetap di
`(0, 1)`, bukan di `x > 1`. Buktiaktu: kompilasi Lean draf lama gagal pada
`have h1x_gt : 1 < 1 - x := by linarith` dengan pesan
`linarith failed ... a✝ : 1 - x ≤ 1`. Karena itu:

- rute simetri ditolak dan tidak boleh dipakai di V4 maupun revisi berikutnya;
- draf sumber Lean lama pada `lean/spec_v4/XiUnconditional.lean` tidak valid dan
  telah diganti seluruhnya;
- draf prapendaftaran lama pada berkas ini diganti seluruhnya oleh revisi ini.

## 3. Rute baru — rangkaian lima sublangkah

Notasi: `UnitAddCircle` = lingkaran duket perbandingan `ℝ/ℤ` Mathlib; `1/2`
adalah elemennya; `kHalf t := ((cosKernel (1/2) t : ℝ) - 1) / 2`.

1. **Tanda kernel (negatif).** Untuk setiap `t > 0`, `kHalf t < 0`.
   Path: `HurwitzZeta.hasSum_nat_cosKernel₀ (a := 1/2)` memberi
   `cosKernel (1/2) t - 1 = ∑' n, 2 * cos (π * (n+1)) * exp (-π * (n+1)^2 * t)`;
   dengan `Real.cos_nat_mul_pi` urutan `(n+1) * π` dan pemisahan `even/odd`
   (`tsum_even_add_odd`, pertermian `(-1)`), deret terurai menjadi jumlah selang
   `2 * (exp (-(4k+2)π t) - exp (-(4k+4)π t))` < 0 term-per-term; keketatan diberi
   oleh selang pertama lewat `tsum_le_tsum_of_hasSum`-aljabar dan `Summable`
   deret geometri (perbandingan `(n+1)^2 ≥ 2(n+1)` untuk `n ≥ 1`).

2. **Konvergensi Mellin di strip penuh.** Fungsi `kHalf` (nilai riil) dan versi
   kompleksnya `fC t := ((cosKernel (1/2) t - 1 : ℝ) : ℂ) / 2` adalah
   `LocallyIntegrableOn (Ioi 0)`; penurunan eksponensial di `+∞` dari
   `HurwitzZeta.isBigO_atTop_cosKernel_sub (1/2)`; terbatas di `0⁺` dari
   hubungan fungsional `evenKernel (1/2) y = y^{-1/2} * cosKernel (1/2) (1/y)`
   (`HurwitzZeta.evenKernel_functional_equation`-form, nama persis diverifikasi saat
   kompilasi) ditambah hambatan atas `evenKernel (1/2)` dari namespace
   `HurwitzKernelBounds` yang dipakai Mathlib sendiri pada bukti
   `isBigO_atTop_cosKernel_sub`. Akibatnya `MellinConvergent fC (x/2)` dan
   `DifferentiableAt ℂ (mellin fC) s` untuk semua `s` dengan `0 < s.re` ( versatility
   `MellinTransform.mellin_differentiableAt_of_isBigO_rpow_exp` dengan `b := 0`,
   `a := p > 0` dari lemma penurunan eksponensial).

3. **Jembatan Mellin ↔ completed.** Pada strip `D := {s | 0 < s.re}`:
   - `completedCosZeta (1/2) s = mellin fC (s/2)` untuk `1 < s.re` oleh
     `(hurwitzEvenFEPair (1/2)).symm.hasMellin` (skema sama dengan pembuktian
     `hasSum_int_completedCosZeta` di Mathlib, HurwitzZetaEven.lean:488–508);
   - kedua fungsi `DifferentiableOn ℂ · D` (sisi kiri: `differentiableAt_completedCosZeta`
     dengan `a ≠ 0`; sisi kanan: langkah 2 via aturan rantai pada `s ↦ s/2`);
   - `IsPreconnected D` dari `Complex.convex_halfSpace_re_gt 0 |>.isPreconnected`
     (`Mathlib/Analysis/Complex/Convex.lean:57`);
   - `AnalyticOnNhd.eqOn_of_preconnected_of_eventuallyEq` pada `z₀ := 2` dengan
     kesetaraan-eventual pada `{re s > 1}` yang terbuka memuat `2`;
   - jadi kesetaraan berlaku di seluruh `D`, khususnya pada sumbu riil `(0, 1)`.

4. **Nilai riil negatif.** Untuk `0 < x < 1` riil:
   - integran Mellin bernilai `ofReal`: `(t : ℂ) ^ ((x/2 - 1 : ℝ) : ℂ) * fC t =
     ((t^(x/2-1) * kHalf t : ℝ) : ℂ)` via `Complex.ofReal_cpow` (basis positif)
     dan perhitungan `Complex.cpow` pada basis `ofReal` riil positif;
   - `mellin fC (x/2) = ((∫ t in Ioi 0, t^(x/2-1) * kHalf t : ℝ) : ℂ)` via
     `MeasureTheory.integral_ofReal` (integran `ofReal`-bernilai titik-demi-titik);
   - integran riil `t^(x/2-1) * kHalf t < 0` titik-demi-titik: faktor pangkat positif
     (`Real.rpow_pos_of_pos`) karena `x/2 - 1 > -1` dan langkah 1;
   - keketatan: batas bawah titik-demi-titik pada `t ∈ [1, 2]` (dari langkah 1,
     selang pertama `≥ 2*(exp (-2π) - exp (-4π))`, dikali faktor `≥ 2^{-1}`) memberi
     `∫ > 0` untuk fungsi `-integran` (perbandingan integral terhadap konstanta
     pada pengukuran `Icc 1 2` yang berukuran `1 > 0`),
     sehingga `mellin fC (x/2) < 0` sebagai bilangan kompleks riil-negatif;
   - `cosZeta (1/2) x = completedCosZeta (1/2) x / Gammaℝ x` untuk `x ≠ 0`
     (definisi `cosZeta` = update pada titik 0), dan `Gammaℝ x > 0` riil untuk
     `0 < x` (faktur yang sama dengan `gammaR_pos_of_pos` V3); karena itu
     `cosZeta (1/2) x < 0` riil.

5. **Identita eta dan penutup.** Untuk semua `s : ℂ` dengan `s ≠ 1`:
   `cosZeta (1/2) s = (2^{1-s} - 1) * riemannZeta s`.
   - Basis pada `1 < s.re`: `hasSum_nat_cosZeta (1/2)` memberi
     `cosZeta (1/2) s = ∑' n, (-1)^n / n^s` (term `n = 0` nol karena
     `(0:ℂ)^s = 0` untuk `0 < s.re`, pola `Complex.zero_cpow` seperti
     HurwitzZetaEven.lean:516); sisi kanan dari
     `zeta_eq_tsum_one_div_nat_add_one_cpow` + `tsum_even_add_odd` + aljabar
     `∑' ganjil = ζ - 2^{-s} ζ` memberi identitas pada `1 < re s`;
   - kedua fungsi diferensiabel pada `{1}ᶜ`: sisi kiri `differentiable_cosZeta_of_ne_zero`
     (`a ≠ 0`); sisi kanan produk diferensiabel (`ζ` diferensiabel di luar `1`);
   - `IsPreconnected {1}ᶜ` via
     `isPathConnected_compl_singleton_of_one_lt_rank rank_real_complex`
     (`Mathlib/Analysis/Normed/Module/Connected.lean:120`,
     `rank_real_complex : Module.rank ℝ ℂ = 2`);
   - `AnalyticOnNhd.eqOn_of_preconnected_of_eventuallyEq` pada `z₀ := 2`
     (preseden persis: `Mathlib/NumberTheory/LSeries/DirichletContinuation.lean:129–131`);
   - pada `0 < x < 1`: `2^{1-x} - 1 > 0` riil, jadi `ζ(x) = cosZeta (1/2) x / (2^{1-x} - 1) < 0` riil
     (kereal-an `ζ` di sumbu riil via `riemannZeta_conj` + `Complex.conj_eq_iff_real`);
   - `completedRiemannZeta (x : ℂ) = Gammaℝ (x : ℂ) * riemannZeta (x : ℂ)`
     (`riemannZeta_def_of_ne_zero`, juga dipakai oleh V3), `Gammaℝ (x : ℂ)` riil
     positif, sehingga `(completedRiemannZeta (x : ℂ)).re < 0` — yaitu `hmid`.

## 4. Pernyataan yang dibuktikan

```text
XiUnconditional.completedRiemannZeta_re_neg_of_mem_Ioo :
    ∀ x : ℝ, 0 < x → x < 1 → (completedRiemannZeta (x : ℂ)).re < 0
```

plus lemma-faktur antara publik-kebutuhan: tanda kernel (langkah 1), jembatan
(langkah 3), identita eta (langkah 5). Tidak ada deklarasi `axiom`; tidak ada
`sorry`/`admit` dalam bentuk final; tidak ada definisi baru yang menutupi
`completedRiemannZeta` — semuanya dari Mathlib.

## 5. Kriteria penerimaan

1. `lake env lean lean/spec_v4/XiUnconditional.lean` keluar 0 (atau `lake build`
   target setara) — dari eksekusi nyata, bukan klaim.
2. `#print axioms XiUnconditional.completedRiemannZeta_re_neg_of_mem_Ioo`
   hanya menampilkan `propext`, `Classical.choice`, `Quot.sound`; tanpa
   `sorryAx` dan tanpa aksioma proyek — dari eksekusi nyata.
3. Gerbang anti-sirkularitas: pemindaian placeholder pada sumber Lean → PASS
   ( hanya itu yang diklaim; SMT sub-gerbang belum ada dan tidak dihitung).
4. Uji guard Python baru `msaf/tests/test_xi_spec_v4.py` mengikuti pola
   `test_xi_spec_v3.py` (pemindaian statis + probe `#print axioms`, fail-closed).
5. Workflow tercakup `.github/workflows/spec-v4.yml` (pola `spec-v3.yml`),
   berjalan hijau.
6. Registry `reports/FENCE_REGISTRY.md` menerima `A-2026-0019`; `HANDOFF`
   menerima §2.0al; freeze-verify tetap OK.
7. Pemeriksaan numerik (SIMULATED, mpmath) sebelum penyetelan: tabel nilai
   `ζ(x)` pada sampel `x ∈ {0.25, 0.4, 0.6, 0.75}` semuanya negatif; tidak
   menggantikan bukti formal.

## 6. Batas eksplisit

- Tidak ada klaim `ζ(x) > 0` pada `x > 1` baru, tidak ada RH, tidak ada P≠NP,
  tidak ada klaim fisika/kwantum.
- Rute simetri tetap ditolak (§2) meskipun revisi ini tersegel.
- Jika satu sublangkah gagal ditutup dengan lemma yang difaktakan, hasilnya
  "belum tersegel" — bukan PASS-songsong; tidak ada penggantian rute diam-diam.
- `TOOL NOT RUN` tidak pernah dihitung sebagai sukses.
