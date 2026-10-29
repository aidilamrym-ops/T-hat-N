# Pra-registrasi Spec V3 â€” xi faithful dari `completedRiemannZeta` (2026-10-20)

**Status:** scope DIKUNCI sebelum implementasi; disetujui pemilik lewat
instruksi "lanjutkan and selesaikan secara berurutan".
**Berkas target:** `lean/spec_v3/XiAnalyticFaithful.lean` (baru)
**Dependensi:** Mathlib v4.33.1 (`riemannZeta`,
`completedRiemannZeta`, `completedRiemannZeta_one_sub`, `Gammaâ„`,
`Complex.Gamma_ofReal`, `Real.Gamma_pos_of_pos`,
`riemannZeta_pos_of_one_lt`, `ComplexOrder`).
**Registry which direncanakan:** `A-2026-0018`.
**Tidak mengubah:** `lean/spec/XiAnalyticSpec.lean` (`A-2026-0015`),
`lean/spec_v2/XiAnalyticSpecV2.lean` (`A-2026-0017`), `ci.yml`
(`A-2026-0016`), and report beku.

## 1. Latar

V2 memperbaiki kontradiksi endpoint tetapi masih abstrak: `zetaReal` and
`gammaReal` opak, delapan aksioma deklaratif, and bentuk produk no
faithful in bilangan bulat genap negatif. V3 mengganti simbol opak with
fungsi Mathlib which sebenarnya and membuktikan persamaan fungsional,
sehingga which tersisa hanyalah satu hipotesis analitik eksplisit.

## 2. Pernyataan which akan dibuktikan

Untuk `x : â„`, definisikan

```text
xiReal x = 1/2                         jika x = 0 or x = 1
         = 1/2 * x * (x-1) * Re Î›(x)   otherwise
```

with `Î› = completedRiemannZeta` dari Mathlib. Akan dibuktikan:

1. `xiReal (1 - x) = xiReal x` for semua `x : â„` (tanpa aksioma;
   memakai `completedRiemannZeta_one_sub`);
2. `0 < xiReal x` for `x > 1` (tanpa aksioma; memakai
   `riemannZeta_pos_of_one_lt` and positivity `Gammaâ„`);
3. `0 < xiReal x` for `0 < x < 1` **with hipotesis eksplisit**
   `hmid : âˆ€ x, 0 < x â†’ x < 1 â†’ (Î›(x : â„‚)).re < 0`;
4. `xi_pos_on_reals (hmid) (x) : 0 < xiReal x` for semua `x : â„`.

## 3. Kriteria penerimaan (PASS/FAIL)

- `lake env lean spec_v3/XiAnalyticFaithful.lean` exit 0.
- `#print axioms XiAnalyticFaithful.xi_pos_on_reals` hanya memuat
  `propext`, `Classical.choice`, `Quot.sound`; **nol aksioma proyek**.
- `#print axioms` for `xiReal_one_sub` and lemma positivity `x>1` juga
  hanya tiga aksioma standar.
- Tidak ada `axiom`, `sorry`, `admit`, or `unsafe` in file V3.
- `hmid` adalah parameter eksplisit teorema, bukan aksioma global.
- Guard `msaf/tests/test_xi_spec_v3.py` lulus; workflow baru
  `.github/workflows/spec-v3.yml` hijau.
- Berkas V2 and V1 no berubah; registry lama tetap valid.

## 4. Batas which dikunci

- `hmid` **no** dibuktikan in paket ini. Itu fakta benar tentang
  `Î›` in `(0,1)`, tetapi belum tersedia in Mathlib; V3 hanya
  memindahkannya menjadi hipotesis eksplisit.
- Realness `Î›(x)` for `x` real no dibuktikan terpisah; `xiReal`
  didefinisikan sebagai section real dari ekspresi standar. Tidak ada
  klaim tambahan tentang nilai kompleks in luar section real.
- Bukan bukti Riemann Hypothesis, bukan peer review, bukan verifikasi
  SMT, and no mengubah trusted base Coq empat aksioma stdlib.
- Tidak ada klaim RH/Pâ‰ NP/fisika.

## 5. Rencana verifikasi

```text
lake env lean spec_v3/XiAnalyticFaithful.lean
python -m pytest msaf/tests/test_xi_spec_v3.py -q
python -m pytest msaf -q
python audit_quantum/freeze.py --verify
```

CI: workflow `spec-v3.yml` (path filter `lean/spec_v3/**`,
`msaf/tests/test_xi_spec_v3.py`, workflow itu sendiri) menjalankan
`lake build` + guard Lean V3. Workflow utama no diubah.


