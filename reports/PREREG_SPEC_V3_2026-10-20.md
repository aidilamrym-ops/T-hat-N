# Pra-registrasi Spec V3 — xi faithful dari `completedRiemannZeta` (2026-10-20)

**Status:** scope DIKUNCI sebelum implementasi; disetujui pemilik lewat
instruksi "lanjutkan dan selesaikan secara berurutan".
**Berkas target:** `lean/spec_v3/XiAnalyticFaithful.lean` (baru)
**Dependensi:** Mathlib v4.33.1 (`riemannZeta`,
`completedRiemannZeta`, `completedRiemannZeta_one_sub`, `Gammaℝ`,
`Complex.Gamma_ofReal`, `Real.Gamma_pos_of_pos`,
`riemannZeta_pos_of_one_lt`, `ComplexOrder`).
**Registry yang direncanakan:** `A-2026-0018`.
**Tidak mengubah:** `lean/spec/XiAnalyticSpec.lean` (`A-2026-0015`),
`lean/spec_v2/XiAnalyticSpecV2.lean` (`A-2026-0017`), `ci.yml`
(`A-2026-0016`), dan laporan beku.

## 1. Latar

V2 memperbaiki kontradiksi endpoint tetapi masih abstrak: `zetaReal` dan
`gammaReal` opak, delapan aksioma deklaratif, dan bentuk produk tidak
faithful di bilangan bulat genap negatif. V3 mengganti simbol opak dengan
fungsi Mathlib yang sebenarnya dan membuktikan persamaan fungsional,
sehingga yang tersisa hanyalah satu hipotesis analitik eksplisit.

## 2. Pernyataan yang akan dibuktikan

Untuk `x : ℝ`, definisikan

```text
xiReal x = 1/2                         jika x = 0 atau x = 1
         = 1/2 * x * (x-1) * Re Λ(x)   otherwise
```

dengan `Λ = completedRiemannZeta` dari Mathlib. Akan dibuktikan:

1. `xiReal (1 - x) = xiReal x` untuk semua `x : ℝ` (tanpa aksioma;
   memakai `completedRiemannZeta_one_sub`);
2. `0 < xiReal x` untuk `x > 1` (tanpa aksioma; memakai
   `riemannZeta_pos_of_one_lt` dan positivity `Gammaℝ`);
3. `0 < xiReal x` untuk `0 < x < 1` **dengan hipotesis eksplisit**
   `hmid : ∀ x, 0 < x → x < 1 → (Λ(x : ℂ)).re < 0`;
4. `xi_pos_on_reals (hmid) (x) : 0 < xiReal x` untuk semua `x : ℝ`.

## 3. Kriteria penerimaan (PASS/FAIL)

- `lake env lean spec_v3/XiAnalyticFaithful.lean` exit 0.
- `#print axioms XiAnalyticFaithful.xi_pos_on_reals` hanya memuat
  `propext`, `Classical.choice`, `Quot.sound`; **nol aksioma proyek**.
- `#print axioms` untuk `xiReal_one_sub` dan lemma positivity `x>1` juga
  hanya tiga aksioma standar.
- Tidak ada `axiom`, `sorry`, `admit`, atau `unsafe` di berkas V3.
- `hmid` adalah parameter eksplisit teorema, bukan aksioma global.
- Guard `msaf/tests/test_xi_spec_v3.py` lulus; workflow baru
  `.github/workflows/spec-v3.yml` hijau.
- Berkas V2 dan V1 tidak berubah; registry lama tetap valid.

## 4. Batas yang dikunci

- `hmid` **tidak** dibuktikan di paket ini. Itu fakta benar tentang
  `Λ` di `(0,1)`, tetapi belum tersedia di Mathlib; V3 hanya
  memindahkannya menjadi hipotesis eksplisit.
- Realness `Λ(x)` untuk `x` real tidak dibuktikan terpisah; `xiReal`
  didefinisikan sebagai bagian real dari ekspresi standar. Tidak ada
  klaim tambahan tentang nilai kompleks di luar bagian real.
- Bukan bukti Riemann Hypothesis, bukan peer review, bukan verifikasi
  SMT, dan tidak mengubah trusted base Coq empat aksioma stdlib.
- Tidak ada klaim RH/P≠NP/fisika.

## 5. Rencana verifikasi

```text
lake env lean spec_v3/XiAnalyticFaithful.lean
python -m pytest msaf/tests/test_xi_spec_v3.py -q
python -m pytest msaf -q
python audit_quantum/freeze.py --verify
```

CI: workflow `spec-v3.yml` (path filter `lean/spec_v3/**`,
`msaf/tests/test_xi_spec_v3.py`, workflow itu sendiri) menjalankan
`lake build` + guard Lean V3. Workflow utama tidak diubah.
