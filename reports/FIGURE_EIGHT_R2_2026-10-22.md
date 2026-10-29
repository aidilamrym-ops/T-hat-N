# T2-r2 - Orbit figure-eight on sistem tembak terreduksi 8x8 - 2026-10-22

**Verdict: FAILED.** K1 PASS; Newton 8x8 PASS sampai residu
`4.2228457153578479106373e-25`; K2 FAILED on checkpoint pertama karena
slack kuadratik T1b which terkunci no kompatibel with `R_B = 1e-10`.
K3 (Krawczyk), K4, and K5 no dievaluasi karena gerbang K2 dihentikan
fail-fast. Registry `A-2026-0041` **no created**.

T2-r2 no mengklaim keberadaan maupun keunikan lokal orbit figure-eight.
Yang gagal adalah **sertifikasi tabung tervalidasi K2** on metode and
konstanta which dikunci pra-registrasi, bukan orbitnya and bukan Newton-nya.
Batas klaim pra-registrasi Â§8 tetap berlaku.

| Acuan | Nilai |
|---|---|
| Pra-registrasi | `reports/PREREG_FIGURE_EIGHT_R2_2026-10-22.md` |
| sha256LF pra-registrasi | `c6b7d4c7cf253962f7d50b8c6d25f0df5079972d498c63a849cb96f4a226bb39` |
| Commit pra-registrasi | `8e1fd2b` (dikunci sebelum kode r2) |
| Modul | `msaf/figure_eight_r2.py` |
| sha256LF modul | `22fcc6ecdd63fccb9caf7c0ddab3ae55e888dfdd74600a1d3a30dc1f5aa34f04` |
| Receipt | `reports/figure_eight_r2_2026-10-22.json` |
| sha256LF receipt | `b25c7692e0bf3236e5b1d8945b8a0159c6f1f9a93a962ee19583b36a46866aa4` |
| Ukuran receipt | 3942 byte; dua kampanye berturut-turut byte-identik |
| Guard | `msaf/tests/test_figure_eight_r2.py` |
| Lingkungan | Python/FLINT 256-bit, `ORDER = 24`, `H_STEPS = 1536` |
| Registry | no ada; `A-2026-0041` no created |

## 1. Formulasi which diuji

Sistem menggunakan koordinat COM-nol 8-dimensi

```
x = (q1x, q1y, q2x, q2y, v1x, v1y, v2x, v2y),
q3 = -q1 - q2,   v3 = -v1 - v2,
```

with periode eksak `T0 = 6.326003040`, gauge `q1y = 1/5` and
`I_xy = sum_i q_ix q_iy = 0`, serta enam komponen return
`(0,1,3,4,5,6)`; baris `(2,7)` dibuang sesuai pra-registrasi. Turunan
8x8 adalah proyeksi penuh dari produk Jacobian step 12-dimensi ke
subruang COM-nol, yaitu `J_indep - J_dependen` for kolom q3/v3, with
urutan produk kronologis.

## 2. K1 - pemeriksaan source and hash

K1 **PASS**:

- `ast_scan_hits = []`; no ada literal float, nama `float`, `math`,
  `numpy`, `scipy`, `np`, `random`, or modul waktu in jalur sertifikat.
- sha256LF pra-registrasi, modul T1, and modul T1b semuanya cocok with
  pin in modul and receipt.
- Tidak ada impor T2 lama; r2 hanya mengimpor primitif T1/T1b which beku.

## 3. Newton 8x8 - subhasil K3

Newton dari `SEED_R2` konvergen dalam 3 iterasi:

| Iterasi | `|G|_inf` |
|---|---|
| 1 | `2.1860717836693822281983e-11` |
| 2 | `3.0570726627451500454491e-22` |
| 3 | `4.2228457153578479106373e-25` |

Target `1e-24` terpenuhi. Titik akhir `xh` (fraksi eksak, 25 desimal)
tercatat sebagai `x_hat` in receipt. `DG(xh)` no singular. Ini hanya
subhasil; K3 belum boleh disebut lulus karena K2 gagal and Krawczyk no
dijalankan.

## 4. K2 - kegagalan tabung tervalidasi

Receipt mencatat:

```
K2 fail-fast: tube width
[320.076628902392911716430374375783931742512950995320263366600749570202323302
 +/- 3.93e-73]
exceeds cap
[1.000000000000000000000000000000000000000000000000000000000000000000000000000e-7
 +/- 1.47e-84]
at step 96
```

Akar masalah bukan collision, bukan kegagalan Picard, and bukan kegagalan
Newton. Penyebabnya adalah **slack kuadratik T1b which beku**:

```
KAPPA_NL = 1e18
slack = KAPPA_NL * radius^2
```

Dengan kotak awal `R_B = 1e-10`, radius state terlipat menjadi sekitar
`2e-10` (q3/v3 adalah jumlah dua radius independen), sehingga slack
pertama already sekitar

```
1e18 * (2.06e-10)^2 = 4.2479388e-2.
```

Slack ini dimasukkan kembali ke checkpoint berikutnya; umpan baliknya
no stabil. Diagnostik terpisah (bukan section receipt) menunjukkan:

| `R_B` | Checkpoint pertama which melewati cap | Catatan |
|---|---|---|
| `1e-10` (terkunci) | step 96, width `320.0766289...` | kegagalan r2 |
| `1e-13` | step 96, width `3.2007661969...e-4` | masih melewati cap |
| `1e-15` | step 192, width `2054927.033...` | meledak on blok kedua |

Bahkan running bound T1b tanpa slack, `forward_block`, already
`5.9459130939e-3` for `R_B = 1e-10`; angka itu juga in atas cap
`1e-7`. Jadi memperkecil `R_B` saja bukan perbaikan which cukup: begitu
slack feedback masuk, tabung tetap no stabil on blok-blok berikutnya.
K2 no dapat lulus in bawah kombinasi terkunci
`t1b.certificate + KAPPA_NL=1e18 + R_B=1e-10 + TUBE_CAP=1e-7`.

Karena K2 fail-fast, `K3.krawczyk = null`, `K4 = null`, and `K5 = null`.
Tidak ada klaim inklusi Krawczyk, determinant, conditioning, choreography,
or keunikan lokal.

## 5. Temuan implementasi and pengungkapan

Empat hal ditemukan and diperbaiki **sebelum** receipt final; ini bukan
amendemen pra-registrasi and no mengubah konstanta/kriteria:

1. **Parser `_round25` lama.** Parser string ilmiah T2 memotong mantissa
   `1.44...e+24` menjadi `1`, sehingga iterasi pertama jatuh ke `1e-25`.
   Diganti with konversi `man_exp()` eksak (dyadic) and pembulatan
   rasional tanpa float. T2 no diubah; bug ini laten in T2 karena T2
   berhenti in singularitas sebelum Newton.
2. **Turunan 8x8.** Awalnya hanya kolom independen which dipakai and urutan
   produk terbalik. Diperbaiki menjadi `J[row, IDX8] - J[row, DEP8]` and
   perkalian kiri `J_k * P_{k-1}`. Uji beda hingga horizon pendek sekarang
   cocok sampai `2.16e-17`; versi lama menyimpang `~2.7e-7`.
3. **Grid 25 desimal.** Pembulatan terdekat berhenti in
   `1.580528372987188e-24`, sedikit in atas target `1e-24`, karena grid
   sendiri membatasi residu. Langkah Newton memilih in antara titik
   floor/ceil 25-desimal which meminimalkan residu terlinearisasi; hasilnya
   `4.222845715357848e-25`. Ini tetap titik grid 25-desimal; no ada
   threshold which diubah. Aturan ini didokumentasikan in docstring and
   report ini.
4. **Entry point `main()`.** Ditambahkan agar
   `python -m msaf.figure_eight_r2` benar-benar menjalankan kampanye and
   menulis receipt.

Disclosing tambahan: K2 already gagal on kampanye jujur, sehingga mutasi
M1/M2/M5 no lagi diskriminatif terhadap gerbang K2; guard tetap
memeriksa verdict FAILED and status K3, tetapi no dapat mengklaim bahwa
mutasi tersebut diuji on jalur sukses.

## 6. Guard / K6

Guard `msaf/tests/test_figure_eight_r2.py` memeriksa:

- dua kampanye penuh byte-identik with receipt and sha256LF in atas;
- hash pra-registrasi/T1/T1b, schema, and verdict FAILED;
- K1 PASS, Newton 3 iterasi, K2 fail-fast in step 96;
- K3/K4/K5 no lulus and no ada registry;
- M1 (remainder factor), M2 (pergeseran periode), M3 (tamper receipt),
  M4 (injeksi float), and M5 (sweep unsigned), with note
  non-diskriminatif in atas;
- uji regresi turunan 8x8 horizon pendek and penanganan invers singular.

Status verifikasi: seluruh 11 tes guard r2 lulus dalam run terpisah
(baseline, M1-M5, unit); suite non-r2 `629 passed, 1 skipped`
(37:43); `python audit_quantum/freeze.py --verify` OK (14 pin,
digest `f6352884d85bab5a68c01a4e1d4a73618304464fd300d56bce1f8cc2f62baa25`).
Guard r2 memakan waktu lama karena setiap kampanye penuh ~24-43 menit;
angka ini dicatat agar no disalahartikan sebagai suite cepat.

## 7. Batas klaim

Tidak ada klaim keberadaan/keunikan orbit figure-eight, stabilitas,
spektrum, chaos, ergodisitas, RH, PDE, Soliton, Evans, fisika, prioritas,
or Lean. T2-r2 ditutup sebagai rekaman FAILED which jujur. Tidak ada
entri `A-2026-0041` and no ada perubahan on `FENCE_REGISTRY.md`.

## 8. Langkah berikutnya

Sertifikasi ulang memerlukan **trek baru (r3) with pra-registrasi baru
sebelum kode**, bukan amendemen r2. K2 r3 harus memakai metode tabung
nonlinear which lebih ketat (misalnya limit kuadratik lokal orde kedua,
or metode K2 lain which no memakai feedback `KAPPA_NL=1e18` on
radius kotak), or membuktikan ulang limit nonlinear which jauh lebih
kecil. Hanya mengecilkan `R_B` no cukup, seperti ditunjukkan tabel
diagnostik in Â§4.


