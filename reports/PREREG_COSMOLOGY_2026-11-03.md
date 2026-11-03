# Pra-registrasi: PLAN-10 — Cosmological Quantisation and Spectral Refutation of Infinite Dark Energy

**Status:** PRE-REG, dikunci sebelum kode PLAN-10.
**Tanggal:** 2026-11-03.
**Kampanye:** Q-COSMOLOGICAL-QUANTIZATION
**Bidang:** Cosmological Quantisation, Finite Information Lattice, Dark Energy Vacuum Catastrophe Refutation.

## 1. Pertanyaan yang Dijawab
Dapatkah malapetaka konstanta kosmologi (divergensi energi vakum QFT $10^{120}$) direduksi secara konstruktif melalui operator spektral kuantisasi $\\Theta_{\\text{cosmo}}$ ke dalam blok matriks MSAF berdimensi tinggi ($N = 401$, matriks $802 \\times 802$) dengan presisi interval 24000-bit Arb, sehingga kerapatan energi gelap tak-berhingga runtuh (collapse) menjadi penutup spektral berbatas diskrit di bawah batasan Finite Information Lattice, rasio makro $N_{\\text{steps}} = D_{\\text{obs}}/l_P \\approx 5.44 \\times 10^{61}$, dan celah entropi Planck?

## 2. Parameter dan Batas yang Dikunci
- **Dimensi Tensor:** $N = 401$ (Matriks $802 \\times 802$).
- **Presisi Arb:** 24000 bit (`flint.ctx.prec = 24000`).
- **Celah Entropi Planck $(\\Delta S_{\\text{planck}})$:** $0.5614 \\pm 3.36 \\times 10^{-74}$ bit (Pillar II).
- **Redaman $\\lambda_{\\min}$:** Pilar III (redaman peluruhan spektral vakum kosmologis).
- **Token Validasi:** `\"COSMOLOGICAL-CONTINUUM-SHATTERED\"` (dikeluarkan hanya jika faktorisasi LDL^T spektral terverifikasi positif dan batas informasi Planck-lattice mengunci energi vakum).

## 3. Batasan Cakupan (Scope Limits)
- Ini adalah analisis spektral finit berbasis interval Arb dan batas informasi Planck-lattice untuk densitas vakum diskrit, bukan kosmologi relativitas umum kontinu universal tanpa batasan domain diskrit.
- Bergantung pada fondasi matriks MSAF dan validasi Route S.
- Tidak menyimpulkan teorema di luar fragmen diskrit yang diuji.

## 4. Amendment 2026-11-03 — metode verifikasi

**Status:** AMENDMENT bertanggal; isi yang sudah dikunci di atas tidak diubah.

Run awal memakai `arb_mat.eig()` penuh pada matriks $802 \times 802$ dengan
presisi 24000 bit. Benchmark pada mesin kerja (i7-6600U): $n=32$ = 37,7 s;
$n=64$ = 324,7 s; skala sekitar $n^{3.1}$; ekstrapolasi $n=802$ sekitar
7–10 hari single-core. Karena itu metode verifikasi diubah tanpa mengubah
klaim, token, atau parameter:

- $\lambda_{\min}$ dan $\lambda_{\max}$ diverifikasi dengan batas Gershgorin
  rigorous.
- Positive definiteness $A$ dan $I - A$ diverifikasi dengan faktorisasi
  LDL$^T$ banded (bandwidth 2); semua pivot $D$ harus strictly positive.
- Residual LDL$^T$ harus mengandung entri matriks asli.

Alasan: kedua metode memberikan sertifikat rigorous untuk klaim yang sama
($\lambda_{\min} > 0$, $\lambda_{\max} < 1$) dan selesai dalam hitungan detik.
Tidak ada perubahan pada dimensi, presisi, celah entropi, atau token validasi.
