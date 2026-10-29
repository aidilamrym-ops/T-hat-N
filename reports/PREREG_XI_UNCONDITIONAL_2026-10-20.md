# Pra-registrasi V4 â€” penutup `hmid` (tanda completed zeta on `0 < x < 1`) â€” REVISI 2026-10-20

**Status:** scope DIKUNCI for revisi ini; eksekusi berjalan in bawah persetujuan pemilik
"lanjutkan and selesaikan" which tercatat in awal sesi. Revisi ini MENGgantikan draf
sebelumnya which memakai rute simetri; rute simetri ditolak and no boleh dipakai lagi.

**Berkas target:** `lean/spec_v4/XiUnconditional.lean` (baru; draf lama no valid and
already diganti).
**Dependensi:** Mathlib v4.33.1 (nama lemma which dipakai daftar in Â§3, semuanya
difaktakan dari file source Mathlib in checkout ini, bukan dari ingatan).
**Registry which direncanakan:** `A-2026-0019`.
**Tidak mengubah:** V1 (`lean/spec/XiAnalyticSpec.lean`, `A-2026-0015`), V2
(`lean/spec_v2/XiAnalyticSpecV2.lean`, `A-2026-0017`), V3
(`lean/spec_v3/XiAnalyticFaithful.lean`, `A-2026-0018`), `ci.yml` (`A-2026-0016`),
seluruh report beku, and `lean/lakefile.toml` no diubah for tahap ini
(V4 direncanakan standalone terhadap Mathlib saja; koneksi ke V3 dilakukan lewat
pernyataan lokal, bukan `import spec_v3`).

## 1. Latar

V3 (`A-2026-0018`) membuktikan `xi_pos_on_reals` secara kondisional terhadap satu
hipotesis analitik `hmid`:

```text
hmid : âˆ€ x : â„, 0 < x â†’ x < 1 â†’ (completedRiemannZeta (x : â„‚)).re < 0
```

V4 menutup `hmid` tanpa aksioma proyek, sehingga V3 menjadi teorema tanpa syarat.
Tidak ada klaim RH or klaim fisika apa pun dalam paket ini.

## 2. Rute which ditolak (rekaman wajib)

Draf pertama memakai argumen "simetri": memandang `1 - x` sebagai titik cermin
with `1 - x > 1` for `0 < x < 1`. Itu keliru secara matematis: `1 - x` tetap in
`(0, 1)`, bukan in `x > 1`. Buktiaktu: kompilasi Lean draf lama gagal on
`have h1x_gt : 1 < 1 - x := by linarith` with pesan
`linarith failed ... aâœ : 1 - x â‰¤ 1`. Karena itu:

- rute simetri ditolak and no boleh dipakai in V4 maupun revisi berikutnya;
- draf source Lean lama on `lean/spec_v4/XiUnconditional.lean` no valid and
  telah diganti seluruhnya;
- draf prapendaftaran lama on file ini diganti seluruhnya oleh revisi ini.

## 3. Rute baru â€” rangkaian lima sublangkah

Notasi: `UnitAddCircle` = lingkaran duket perbandingan `â„/â„¤` Mathlib; `1/2`
adalah elemennya; `kHalf t := ((cosKernel (1/2) t : â„) - 1) / 2`.

1. **Tanda kernel (negatif).** Untuk setiap `t > 0`, `kHalf t < 0`.
   Path: `HurwitzZeta.hasSum_nat_cosKernelâ‚€ (a := 1/2)` memberi
   `cosKernel (1/2) t - 1 = âˆ‘' n, 2 * cos (Ï€ * (n+1)) * exp (-Ï€ * (n+1)^2 * t)`;
   with `Real.cos_nat_mul_pi` urutan `(n+1) * Ï€` and pemisahan `even/odd`
   (`tsum_even_add_odd`, pertermian `(-1)`), deret terurai menjadi jumlah selang
   `2 * (exp (-(4k+2)Ï€ t) - exp (-(4k+4)Ï€ t))` < 0 term-per-term; keketatan diberi
   oleh selang pertama lewat `tsum_le_tsum_of_hasSum`-aljabar and `Summable`
   deret geometri (perbandingan `(n+1)^2 â‰¥ 2(n+1)` for `n â‰¥ 1`).

2. **Konvergensi Mellin in strip penuh.** Fungsi `kHalf` (nilai riil) and versi
   kompleksnya `fC t := ((cosKernel (1/2) t - 1 : â„) : â„‚) / 2` adalah
   `LocallyIntegrableOn (Ioi 0)`; penurunan eksponensial in `+âˆž` dari
   `HurwitzZeta.isBigO_atTop_cosKernel_sub (1/2)`; terbatas in `0âº` dari
   hubungan fungsional `evenKernel (1/2) y = y^{-1/2} * cosKernel (1/2) (1/y)`
   (`HurwitzZeta.evenKernel_functional_equation`-form, nama persis diverifikasi saat
   kompilasi) ditambah hambatan atas `evenKernel (1/2)` dari namespace
   `HurwitzKernelBounds` which dipakai Mathlib sendiri on bukti
   `isBigO_atTop_cosKernel_sub`. Akibatnya `MellinConvergent fC (x/2)` and
   `DifferentiableAt â„‚ (mellin fC) s` for semua `s` with `0 < s.re` ( versatility
   `MellinTransform.mellin_differentiableAt_of_isBigO_rpow_exp` with `b := 0`,
   `a := p > 0` dari lemma penurunan eksponensial).

3. **Jembatan Mellin â†” completed.** Pada strip `D := {s | 0 < s.re}`:
   - `completedCosZeta (1/2) s = mellin fC (s/2)` for `1 < s.re` oleh
     `(hurwitzEvenFEPair (1/2)).symm.hasMellin` (skema sama with pembuktian
     `hasSum_int_completedCosZeta` in Mathlib, HurwitzZetaEven.lean:488â€“508);
   - kedua fungsi `DifferentiableOn â„‚ Â· D` (sisi kiri: `differentiableAt_completedCosZeta`
     with `a â‰  0`; sisi kanan: step 2 via aturan rantai on `s â†¦ s/2`);
   - `IsPreconnected D` dari `Complex.convex_halfSpace_re_gt 0 |>.isPreconnected`
     (`Mathlib/Analysis/Complex/Convex.lean:57`);
   - `AnalyticOnNhd.eqOn_of_preconnected_of_eventuallyEq` on `zâ‚€ := 2` with
     kesetaraan-eventual on `{re s > 1}` which terbuka memuat `2`;
   - jadi kesetaraan berlaku in seluruh `D`, khususnya on sumbu riil `(0, 1)`.

4. **Nilai riil negatif.** Untuk `0 < x < 1` riil:
   - integran Mellin bernilai `ofReal`: `(t : â„‚) ^ ((x/2 - 1 : â„) : â„‚) * fC t =
     ((t^(x/2-1) * kHalf t : â„) : â„‚)` via `Complex.ofReal_cpow` (basis positif)
     and perhitungan `Complex.cpow` on basis `ofReal` riil positif;
   - `mellin fC (x/2) = ((âˆ« t in Ioi 0, t^(x/2-1) * kHalf t : â„) : â„‚)` via
     `MeasureTheory.integral_ofReal` (integran `ofReal`-bernilai titik-demi-titik);
   - integran riil `t^(x/2-1) * kHalf t < 0` titik-demi-titik: faktor pangkat positif
     (`Real.rpow_pos_of_pos`) karena `x/2 - 1 > -1` and step 1;
   - keketatan: limit bawah titik-demi-titik on `t âˆˆ [1, 2]` (dari step 1,
     selang pertama `â‰¥ 2*(exp (-2Ï€) - exp (-4Ï€))`, dikali faktor `â‰¥ 2^{-1}`) memberi
     `âˆ« > 0` for fungsi `-integran` (perbandingan integral terhadap konstanta
     on pengukuran `Icc 1 2` which berukuran `1 > 0`),
     sehingga `mellin fC (x/2) < 0` sebagai bilangan kompleks riil-negatif;
   - `cosZeta (1/2) x = completedCosZeta (1/2) x / Gammaâ„ x` for `x â‰  0`
     (definisi `cosZeta` = update on titik 0), and `Gammaâ„ x > 0` riil for
     `0 < x` (faktur which sama with `gammaR_pos_of_pos` V3); karena itu
     `cosZeta (1/2) x < 0` riil.

5. **Identita eta and penutup.** Untuk semua `s : â„‚` with `s â‰  1`:
   `cosZeta (1/2) s = (2^{1-s} - 1) * riemannZeta s`.
   - Basis on `1 < s.re`: `hasSum_nat_cosZeta (1/2)` memberi
     `cosZeta (1/2) s = âˆ‘' n, (-1)^n / n^s` (term `n = 0` nol karena
     `(0:â„‚)^s = 0` for `0 < s.re`, pola `Complex.zero_cpow` seperti
     HurwitzZetaEven.lean:516); sisi kanan dari
     `zeta_eq_tsum_one_div_nat_add_one_cpow` + `tsum_even_add_odd` + aljabar
     `âˆ‘' ganjil = Î¶ - 2^{-s} Î¶` memberi identitas on `1 < re s`;
   - kedua fungsi diferensiabel on `{1}á¶œ`: sisi kiri `differentiable_cosZeta_of_ne_zero`
     (`a â‰  0`); sisi kanan produk diferensiabel (`Î¶` diferensiabel in luar `1`);
   - `IsPreconnected {1}á¶œ` via
     `isPathConnected_compl_singleton_of_one_lt_rank rank_real_complex`
     (`Mathlib/Analysis/Normed/Module/Connected.lean:120`,
     `rank_real_complex : Module.rank â„ â„‚ = 2`);
   - `AnalyticOnNhd.eqOn_of_preconnected_of_eventuallyEq` on `zâ‚€ := 2`
     (preseden persis: `Mathlib/NumberTheory/LSeries/DirichletContinuation.lean:129â€“131`);
   - on `0 < x < 1`: `2^{1-x} - 1 > 0` riil, jadi `Î¶(x) = cosZeta (1/2) x / (2^{1-x} - 1) < 0` riil
     (kereal-an `Î¶` in sumbu riil via `riemannZeta_conj` + `Complex.conj_eq_iff_real`);
   - `completedRiemannZeta (x : â„‚) = Gammaâ„ (x : â„‚) * riemannZeta (x : â„‚)`
     (`riemannZeta_def_of_ne_zero`, juga dipakai oleh V3), `Gammaâ„ (x : â„‚)` riil
     positif, sehingga `(completedRiemannZeta (x : â„‚)).re < 0` â€” yaitu `hmid`.

## 4. Pernyataan which dibuktikan

```text
XiUnconditional.completedRiemannZeta_re_neg_of_mem_Ioo :
    âˆ€ x : â„, 0 < x â†’ x < 1 â†’ (completedRiemannZeta (x : â„‚)).re < 0
```

plus lemma-faktur antara publik-kebutuhan: tanda kernel (step 1), jembatan
(step 3), identita eta (step 5). Tidak ada deklarasi `axiom`; no ada
`sorry`/`admit` dalam bentuk final; no ada definisi baru which menutupi
`completedRiemannZeta` â€” semuanya dari Mathlib.

## 5. Kriteria penerimaan

1. `lake env lean lean/spec_v4/XiUnconditional.lean` keluar 0 (or `lake build`
   target setara) â€” dari eksekusi nyata, bukan klaim.
2. `#print axioms XiUnconditional.completedRiemannZeta_re_neg_of_mem_Ioo`
   hanya menampilkan `propext`, `Classical.choice`, `Quot.sound`; tanpa
   `sorryAx` and tanpa aksioma proyek â€” dari eksekusi nyata.
3. Gerbang anti-sirkularitas: pemindaian placeholder on source Lean â†’ PASS
   ( hanya itu which diklaim; SMT sub-gerbang belum ada and no dihitung).
4. Uji guard Python baru `msaf/tests/test_xi_spec_v4.py` mengikuti pola
   `test_xi_spec_v3.py` (pemindaian statis + probe `#print axioms`, fail-closed).
5. Workflow tercakup `.github/workflows/spec-v4.yml` (pola `spec-v3.yml`),
   berjalan hijau.
6. Registry `reports/FENCE_REGISTRY.md` menerima `A-2026-0019`; `HANDOFF`
   menerima Â§2.0al; freeze-verify tetap OK.
7. Pemeriksaan numerik (SIMULATED, mpmath) sebelum penyetelan: tabel nilai
   `Î¶(x)` on sampel `x âˆˆ {0.25, 0.4, 0.6, 0.75}` semuanya negatif; no
   menggantikan bukti formal.

## 6. Batas eksplisit

- Tidak ada klaim `Î¶(x) > 0` on `x > 1` baru, no ada RH, no ada Pâ‰ NP,
  no ada klaim fisika/kwantum.
- Rute simetri tetap ditolak (Â§2) meskipun revisi ini tersegel.
- Jika satu sublangkah gagal ditutup with lemma which difaktakan, hasilnya
  "belum tersegel" â€” bukan PASS-songsong; no ada penggantian rute diam-diam.
- `TOOL NOT RUN` no pernah dihitung sebagai sukses.


