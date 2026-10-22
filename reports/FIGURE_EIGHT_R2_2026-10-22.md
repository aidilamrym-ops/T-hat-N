# T2-r2 - Orbit figure-eight pada sistem tembak terreduksi 8x8 - 2026-10-22

**Verdict: FAILED.** K1 PASS; Newton 8x8 PASS sampai residu
`4.2228457153578479106373e-25`; K2 FAILED pada checkpoint pertama karena
slack kuadratik T1b yang terkunci tidak kompatibel dengan `R_B = 1e-10`.
K3 (Krawczyk), K4, dan K5 tidak dievaluasi karena gerbang K2 dihentikan
fail-fast. Registry `A-2026-0041` **tidak dibuat**.

T2-r2 tidak mengklaim keberadaan maupun keunikan lokal orbit figure-eight.
Yang gagal adalah **sertifikasi tabung tervalidasi K2** pada metode dan
konstanta yang dikunci pra-registrasi, bukan orbitnya dan bukan Newton-nya.
Batas klaim pra-registrasi §8 tetap berlaku.

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
| Registry | tidak ada; `A-2026-0041` tidak dibuat |

## 1. Formulasi yang diuji

Sistem menggunakan koordinat COM-nol 8-dimensi

```
x = (q1x, q1y, q2x, q2y, v1x, v1y, v2x, v2y),
q3 = -q1 - q2,   v3 = -v1 - v2,
```

dengan periode eksak `T0 = 6.326003040`, gauge `q1y = 1/5` dan
`I_xy = sum_i q_ix q_iy = 0`, serta enam komponen return
`(0,1,3,4,5,6)`; baris `(2,7)` dibuang sesuai pra-registrasi. Turunan
8x8 adalah proyeksi penuh dari produk Jacobian langkah 12-dimensi ke
subruang COM-nol, yaitu `J_indep - J_dependen` untuk kolom q3/v3, dengan
urutan produk kronologis.

## 2. K1 - pemeriksaan sumber dan hash

K1 **PASS**:

- `ast_scan_hits = []`; tidak ada literal float, nama `float`, `math`,
  `numpy`, `scipy`, `np`, `random`, atau modul waktu di jalur sertifikat.
- sha256LF pra-registrasi, modul T1, dan modul T1b semuanya cocok dengan
  pin di modul dan receipt.
- Tidak ada impor T2 lama; r2 hanya mengimpor primitif T1/T1b yang beku.

## 3. Newton 8x8 - subhasil K3

Newton dari `SEED_R2` konvergen dalam 3 iterasi:

| Iterasi | `|G|_inf` |
|---|---|
| 1 | `2.1860717836693822281983e-11` |
| 2 | `3.0570726627451500454491e-22` |
| 3 | `4.2228457153578479106373e-25` |

Target `1e-24` terpenuhi. Titik akhir `xh` (fraksi eksak, 25 desimal)
tercatat sebagai `x_hat` di receipt. `DG(xh)` tidak singular. Ini hanya
subhasil; K3 belum boleh disebut lulus karena K2 gagal dan Krawczyk tidak
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

Akar masalah bukan collision, bukan kegagalan Picard, dan bukan kegagalan
Newton. Penyebabnya adalah **slack kuadratik T1b yang beku**:

```
KAPPA_NL = 1e18
slack = KAPPA_NL * radius^2
```

Dengan kotak awal `R_B = 1e-10`, radius state terlipat menjadi sekitar
`2e-10` (q3/v3 adalah jumlah dua radius independen), sehingga slack
pertama sudah sekitar

```
1e18 * (2.06e-10)^2 = 4.2479388e-2.
```

Slack ini dimasukkan kembali ke checkpoint berikutnya; umpan baliknya
tidak stabil. Diagnostik terpisah (bukan bagian receipt) menunjukkan:

| `R_B` | Checkpoint pertama yang melewati cap | Catatan |
|---|---|---|
| `1e-10` (terkunci) | step 96, width `320.0766289...` | kegagalan r2 |
| `1e-13` | step 96, width `3.2007661969...e-4` | masih melewati cap |
| `1e-15` | step 192, width `2054927.033...` | meledak pada blok kedua |

Bahkan running bound T1b tanpa slack, `forward_block`, sudah
`5.9459130939e-3` untuk `R_B = 1e-10`; angka itu juga di atas cap
`1e-7`. Jadi memperkecil `R_B` saja bukan perbaikan yang cukup: begitu
slack feedback masuk, tabung tetap tidak stabil pada blok-blok berikutnya.
K2 tidak dapat lulus di bawah kombinasi terkunci
`t1b.certificate + KAPPA_NL=1e18 + R_B=1e-10 + TUBE_CAP=1e-7`.

Karena K2 fail-fast, `K3.krawczyk = null`, `K4 = null`, dan `K5 = null`.
Tidak ada klaim inklusi Krawczyk, determinant, conditioning, choreography,
atau keunikan lokal.

## 5. Temuan implementasi dan pengungkapan

Empat hal ditemukan dan diperbaiki **sebelum** receipt final; ini bukan
amendemen pra-registrasi dan tidak mengubah konstanta/kriteria:

1. **Parser `_round25` lama.** Parser string ilmiah T2 memotong mantissa
   `1.44...e+24` menjadi `1`, sehingga iterasi pertama jatuh ke `1e-25`.
   Diganti dengan konversi `man_exp()` eksak (dyadic) dan pembulatan
   rasional tanpa float. T2 tidak diubah; bug ini laten di T2 karena T2
   berhenti di singularitas sebelum Newton.
2. **Turunan 8x8.** Awalnya hanya kolom independen yang dipakai dan urutan
   produk terbalik. Diperbaiki menjadi `J[row, IDX8] - J[row, DEP8]` dan
   perkalian kiri `J_k * P_{k-1}`. Uji beda hingga horizon pendek sekarang
   cocok sampai `2.16e-17`; versi lama menyimpang `~2.7e-7`.
3. **Grid 25 desimal.** Pembulatan terdekat berhenti di
   `1.580528372987188e-24`, sedikit di atas target `1e-24`, karena grid
   sendiri membatasi residu. Langkah Newton memilih di antara titik
   floor/ceil 25-desimal yang meminimalkan residu terlinearisasi; hasilnya
   `4.222845715357848e-25`. Ini tetap titik grid 25-desimal; tidak ada
   threshold yang diubah. Aturan ini didokumentasikan di docstring dan
   laporan ini.
4. **Entry point `main()`.** Ditambahkan agar
   `python -m msaf.figure_eight_r2` benar-benar menjalankan kampanye dan
   menulis receipt.

Disclosing tambahan: K2 sudah gagal pada kampanye jujur, sehingga mutasi
M1/M2/M5 tidak lagi diskriminatif terhadap gerbang K2; guard tetap
memeriksa verdict FAILED dan status K3, tetapi tidak dapat mengklaim bahwa
mutasi tersebut diuji pada jalur sukses.

## 6. Guard / K6

Guard `msaf/tests/test_figure_eight_r2.py` memeriksa:

- dua kampanye penuh byte-identik dengan receipt dan sha256LF di atas;
- hash pra-registrasi/T1/T1b, schema, dan verdict FAILED;
- K1 PASS, Newton 3 iterasi, K2 fail-fast di step 96;
- K3/K4/K5 tidak lulus dan tidak ada registry;
- M1 (remainder factor), M2 (pergeseran periode), M3 (tamper receipt),
  M4 (injeksi float), dan M5 (sweep unsigned), dengan catatan
  non-diskriminatif di atas;
- uji regresi turunan 8x8 horizon pendek dan penanganan invers singular.

Status verifikasi: seluruh 11 tes guard r2 lulus dalam run terpisah
(baseline, M1-M5, unit); suite non-r2 `629 passed, 1 skipped`
(37:43); `python audit_quantum/freeze.py --verify` OK (14 pin,
digest `f6352884d85bab5a68c01a4e1d4a73618304464fd300d56bce1f8cc2f62baa25`).
Guard r2 memakan waktu lama karena setiap kampanye penuh ~24-43 menit;
angka ini dicatat agar tidak disalahartikan sebagai suite cepat.

## 7. Batas klaim

Tidak ada klaim keberadaan/keunikan orbit figure-eight, stabilitas,
spektrum, chaos, ergodisitas, RH, PDE, Soliton, Evans, fisika, prioritas,
atau Lean. T2-r2 ditutup sebagai rekaman FAILED yang jujur. Tidak ada
entri `A-2026-0041` dan tidak ada perubahan pada `FENCE_REGISTRY.md`.

## 8. Langkah berikutnya

Sertifikasi ulang memerlukan **trek baru (r3) dengan pra-registrasi baru
sebelum kode**, bukan amendemen r2. K2 r3 harus memakai metode tabung
nonlinear yang lebih ketat (misalnya batas kuadratik lokal orde kedua,
atau metode K2 lain yang tidak memakai feedback `KAPPA_NL=1e18` pada
radius kotak), atau membuktikan ulang batas nonlinear yang jauh lebih
kecil. Hanya mengecilkan `R_B` tidak cukup, seperti ditunjukkan tabel
diagnostik di §4.
