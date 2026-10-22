# Pra-registrasi T2-r2 - Orbit figure-eight tervalidasi (three-body, reduced 8x8) - 2026-10-22

**Status: TERKUNCI SEBELUM KODE.** Dokumen ini ditulis dan di-commit
sebelum satu baris pun kode T2-r2 ditulis. Tidak ada amendemen setelah kode
dimulai; bila ditemukan cacat, jalur baru harus dibuka.

## 0. Garis keturunan dan alasan trek baru

- T1 (`A-2026-0039`) dan T1b (`A-2026-0040`) adalah primitif tervalidasi
  yang **beku**; T2-r2 hanya mengimpor, tidak mengubah.
- T2 (figure-eight, 11-dimensi) ditutup **FAILED** pada commit `1c6a2c8`:
  K3 singular eksak karena translasi-x seragam, `DF e = 0` dengan
  `e = (1,0,1,0,1,0,0,0,0,0,0)`; tidak ada registry `A-2026-0041`.
- T2-r2 adalah trek baru, bukan amendemen T2. Tujuan: sertifikasi lokal
  keberadaan **dan keunikan** satu orbit periodik figure-eight pada periode
  tetap `T0`, dalam sistem tereduksi 8x8 yang mengquotien translasi/boost dan
  mengunci fase serta rotasi.

## 1. Sistem dan koordinat tereduksi

Tiga massa sama `m = 1`, bidang, Hamiltonian

```
H = 1/2 (|v1|^2 + |v2|^2 + |v3|^2) - 1/|q1-q2| - 1/|q1-q3| - 1/|q2-q3|.
```

Pusat massa dikunci eksak:

```
q1 + q2 + q3 = 0,        v1 + v2 + v3 = 0.
```

Koordinat bebas `x = (q1x,q1y,q2x,q2y,v1x,v1y,v2x,v2y)`, dengan

```
q3 = -q1 - q2,           v3 = -v1 - v2.
```

Lift 12-dimensi `lift(x)` mengisi `q1,q2,v1,v2` dan menurunkan `q3,v3`;
pusat massa tepat nol untuk setiap `x`. Aliran `Phi_t` adalah aliran
three-body penuh; translasi dan boost tidak pernah masuk karena lift
selalu COM-zero.

Periode dikunci:

```
T0 = 632600304 / 10^8 = 6.326003040.
```

Peta yang disertifikasi:

```
P(x) = proj(Phi_{T0}(lift(x))) - x,          proj: 12 -> 8
G(x) = (P_0(x), P_1(x), P_3(x), P_4(x), P_5(x), P_6(x),
        q1y(x) - 1/5, I_xy(x)),
I_xy(x) = sum_{i=1}^3 q_ix q_iy.
```

Baris `P_2` dan `P_7` dibuang; pilihan ini dikunci dari probe float
(§9) karena memberi kondisi terbaik. `G: R^8 -> R^8` adalah sistem
tembak (shooting) kuadrat.

**Gauge dan mengapa cukup:**

1. `q1y = 1/5` mengunci fase. Nilai `1/5` dipilih generik dan
   **bukan** `q1y = 0`: pada `q1y = 0` orbit figure-eight mendekati
   konfigurasi kolinear, dan probe menunjukkan solusi kolinear degenerat.
   Pada `q1y = 1/5`, konfigurasi non-kolinear (`q3y` sekitar `-0.122`).
2. `I_xy = 0` mengunci rotasi dengan menyelaraskan sumbu utama tensor
   inersia ke sumbu-x. Turunan `I_xy` terhadap rotasi adalah
   `sum(qx^2 - qy^2)`, tidak nol pada konfigurasi generik.
3. Periode `T0` tetap **mengunci keluarga energi**: pada periode tetap,
   anggota keluarga figure-eight yang periodenya `T0` terisolasi. Tidak
   ada energi yang perlu dikunci sebagai persamaan tambahan.
4. Translasi/boost sudah hilang oleh lift COM-zero. Tidak ada arah nol
   translasi seperti di T2.

Klaim yang disertifikasi adalah: **terdapat tepat satu** `x*` dalam kotak
`B` yang memenuhi `G(x*) = 0`, sehingga `lift(x*)` adalah orbit periodik
periode `T0` dengan pusat massa nol, fase `q1y = 1/5`, dan orientasi
`I_xy = 0`. Keunikan hanya lokal di `B` dan modulo gauge yang dikunci.

## 2. Data eksak, seed, dan larangan

Semua konstanta di jalur tersertifikasi adalah `Fraction`/`arb`; tidak ada
literal float, `float(...)`, `math`, `numpy`, `scipy`, `random`, atau waktu.
Pemindaian AST memakai `ode_validated.ast_scan` plus pemindai lokal
(`_ast_hits`) yang juga menolak nama `float` dan literal float.

Seed rasional (16-17 desimal; aproksimasi float dari probe, bukan hasil
tersertifikasi):

```
SEED_R2 = (
    Fraction("0.1448544459401314"),   # q1x
    Fraction("0.2"),                  # q1y  (= 1/5 tepat)
    Fraction("-1.04839609289586"),    # q2x
    Fraction("-0.07773682382648972"), # q2y
    Fraction("-0.7922166346262658"),  # v1x
    Fraction("-0.9821886530957104"),  # v1y
    Fraction("0.15139114003894605"),  # v2x
    Fraction("0.5091019520994268"),   # v2y
)
```

Seed ini memenuhi `q1y = 1/5` tepat dan `I_xy` sekitar `1.4e-17`; residu
float `|G(seed)|_inf` sekitar `8.04e-14`. Newton tersertifikasi wajib
memperbaikinya sampai `|G|_inf <= 1e-24` sebelum Krawczyk.

Energi orbit pada `T0` (float, hanya informasi) sekitar
`-1.287129915397`; energi **tidak** dikunci dan **tidak** diklaim sebagai
energi figure-eight fisik. Yang diklaim adalah orbit periode tepat `T0`.

## 3. Sertifikat K1-K6

### K1 - data eksak dan AST

- `ast_scan`/`_ast_hits` pada sumber modul: tidak ada literal float, nama
  `float`, `math`, `numpy`, `scipy`, `np`, `random`, atau waktu.
- Semua konstanta yang dipakai di jalur sertifikat adalah `Fraction`
  (langsung atau lewat `Fraction("...")`); tidak ada pembulatan float.
- Hash pra-registrasi ini, hash dua modul beku T1/T1b, dan path receipt
  dipin di modul dan guard.
- Kode dan docstring berbahasa Inggris; dokumen peneliti berbahasa
  Indonesia.

### K2 - tabung tervalidasi

- Kotak awal `B = xh + [-R_B, R_B]^8`, dengan `xh` titik hasil Newton
  (atau seed bila Newton belum dipakai); lift 12-dimensi memakai
  `q3 = -q1 - q2`, `v3 = -v1 - v2`, sehingga COM tetap nol.
- Integrasi 12-dimensi dengan `ode_validated_block.forward_step`
  (`coeffs_three_body`, `rhs_three_body`, `ORDER`, `PREC`), `H_STEPS`
  langkah eksak `h = T0/H_STEPS`, dengan sertifikat sapuan bertanda T1b
  (`t1b.certificate`) pada checkpoint blok.
- Lulus bila: setiap langkah Picard lolos (tidak ada
  `ValidationError`), lebar tabung state maksimum pada checkpoint
  `<= TUBE_CAP`, dan tidak ada error aritmetika.
- Tidak ada klaim collision terpisah; Picard yang gagal adalah alarm
  collision. Jarak pasangan minimum sepanjang lintasan dicatat sebagai
  catatan internal, bukan kriteria lulus.

### K3 - Newton + Krawczyk 8x8

- Newton dari `SEED_R2`, maksimum `NEWTON_MAX = 6` iterasi, pembulatan
  25 desimal (`ROUND_DEC = 10^25`), target `|G|_inf <= NEWTON_TARGET =
  1e-24`. Bila target tidak tercapai: K3 FAILED.
- Di titik akhir `xh`, hitung `G(xh)` dan `DG(xh)`; `W = inv(mid(DG(xh)))`
  (interval inverse); bila singular: K3 FAILED.
- Kotak `B = xh + [-R_B, R_B]^8`; hitung enclosure `DG(B)` dari produk
  Jacobian langkah 12-dimensi yang diproyeksikan ke 8x8, plus gradien
  gauge eksak.
- Krawczyk:

```
K(B) = xh - W G(xh) + (I - W DG(B)) (B - xh).
```

- Lulus bila:
  - `kappa_inf = max_i sum_j |(I - W DG(B))_{ij}| <= 1/2`,
  - setiap baris `|W G(xh)|_i + sum_j |(I - W DG(B))_{ij}| R_B <=
    K_MARGIN R_B` dengan `K_MARGIN = 9/10`,
  - `K(B) subset B` (implisit dari dua syarat di atas).
- Receipt mencatat `w_max`, `kappa_inf`, semua baris, `|G(xh)|_inf`,
  jumlah iterasi Newton, dan `included`.
- K3 PASS berarti tepat satu nol `G` di `B` (Krawczyk), jadi tepat satu
  orbit periode `T0` dengan gauge terkunci di kotak itu. Tidak ada klaim
  global.

### K4 - matriks Gauss 8x8 (bukan klaim stabilitas)

- Hitung `det(DG(xh))` interval dan `cond_inf <= ||W||_inf ||DG(B)||_inf`.
- Lulus bila `det(DG(xh))` tidak memuat nol, `det_lower >= GAUSS_DET_MIN =
  1e-6`, dan `cond_inf <= GAUSS_COND_MAX = 1e6`.
- Ini **bukan** analisis monodromy/eigenvalue dan **bukan** klaim
  stabilitas. Tidak ada spektrum yang diklaim.

### K5 - deskriptor koreografi (absolut, phase-independent)

- Dari lintasan tervalidasi kotak/point yang sama, ambil state pada
  `t = T0/3` (512 langkah) dan `t = 2T0/3` (1024 langkah).
- Defek koreografi:

```
max( |q1(T0/3) - q2(0)|, |q2(T0/3) - q3(0)|, |q3(T0/3) - q1(0)|,
     |q1(2T0/3) - q3(0)|, |q2(2T0/3) - q1(0)|, |q3(2T0/3) - q2(0)| )
<= CHOREO_TOL = 1e-6.
```

- Ini menggantikan jendela waktu relatif K5 T2 yang salah frame. Tidak
  ada jendela absolute yang rapuh; koreografi adalah invarian fase.
- Lulus bila defek <= `CHOREO_TOL`. Ini uji konsistensi bentuk, bukan
  bukti koreografi untuk semua waktu.

### K6 - guard dan mutasi

Guard `msaf/tests/test_figure_eight_r2.py` wajib memuat:

- verifikasi hash pra-registrasi, receipt, modul beku T1/T1b, dan path;
- kampanye ulang byte-identik dengan receipt (dua run identik);
- M1 `REMAINDER_FACTOR := 10^70`: harus FAILED/fail-fast (Picard atau
  cap K2); langkah abort aktual diungkap di receipt/guard;
- M2 `T0 := T0 + 1/10`: periode salah; K3 harus FAILED (mutasi periode
  yang diskriminatif, bukan sekadar pergeseran seed);
- M3 satu byte receipt diubah: deteksi hash/payload;
- M4 injeksi literal float dan `float(x)`: `_ast_hits` menolak;
- M5 `SWEEP_SIGNED := False`: sapuan reset tak bertanda; K2/K3 harus
  FAILED (enclosure cukup lebar untuk menolak), sehingga mutasi
  diskriminatif pada sistem nonsingular.

K6 lulus hanya bila semua mutasi berperilaku seperti di atas. Bila M1/M5
gagal karena alasan yang salah, itu diungkap dan K6 tidak lulus.

## 4. Ambang dan konstanta terkunci

| Konstanta | Nilai | Catatan |
|---|---|---|
| `T0` | `Fraction(632600304, 10**8)` | periode tetap |
| `C` | `Fraction(1, 5)` | gauge fase `q1y` |
| `SEED_R2` | §2 | seed rasional 16-17 desimal |
| `ROWS_KEEP` | `(0,1,3,4,5,6)` | drop `(2,7)` |
| `R_B` | `Fraction(1, 10**10)` | radius kotak Krawczyk |
| `K_MARGIN` | `Fraction(9, 10)` | inklusi K(B) |
| `KAPPA_MAX` | `Fraction(1, 2)` | kontraksi |
| `NEWTON_MAX` | `6` | iterasi |
| `NEWTON_TARGET` | `Fraction(1, 10**24)` | target residu |
| `ROUND_DEC` | `10**25` | grid pembulatan |
| `H_STEPS` | `1536` | `h = T0/1536` eksak |
| `PREC` | `256` | presisi arb |
| `ORDER` | `24` | Taylor |
| `TUBE_CAP` | `Fraction(1, 10**7)` | lebar tabung K2 |
| `GAUSS_DET_MIN` | `Fraction(1, 10**6)` | K4 |
| `GAUSS_COND_MAX` | `10**6` | K4 |
| `CHOREO_TOL` | `Fraction(1, 10**6)` | K5 |
| `BLOCK_STEPS` | `96` | checkpoint sertifikat |
| `REMAINDER_FACTOR` | `1` | M1 -> `10**70` |
| `SWEEP_SIGNED` | `True` | M5 -> `False` |

Ambang ini dikunci sebelum kode. Bila kampanye jujur melewatinya, verdict
FAILED/INCONCLUSIVE; tidak ada pelonggaran setelah kode.

## 5. Prosedur kampanye dan receipt

- `python -m msaf.figure_eight_r2` menjalankan `run_campaign()` dan
  menulis `reports/figure_eight_r2_2026-10-22.json`; `main()` mencetak
  ringkasan JSON.
- Dua run berturut-turut harus byte-identical (sha256LF receipt sama).
- Receipt memuat: skema, hash pra-registrasi, hash modul beku, konstanta,
  `SEED_R2`, `K1`-`K6`, riwayat Newton, Krawczyk, K4, K5, K2 (lebar,
  checkpoint), versi Python/flint, dan `all_pass`.
- Guard menjalankan ulang kampanye dan membandingkan payload kanonik
  dengan receipt; guard juga menjalankan M1-M5.
- Tidak ada registry pada K3 gagal. Registry `A-2026-0041` hanya dibuat
  bila **ALL PASS (K1-K6)**.

## 6. Verdict

- `FAILED` bila K1, K2, K3, atau K6 gagal.
- `INCONCLUSIVE` bila K3 PASS tetapi K4 atau K5 gagal.
- `ALL PASS` hanya bila K1-K6 semuanya PASS; hanya itu yang boleh
  menghasilkan registry `A-2026-0041` dan klaim lokal.
- Tidak ada registry parsial; tidak ada klaim lokal bila K3 gagal.

## 7. Batas klaim

- Keunikan hanya **lokal** di kotak `B`, modulo gauge `q1y = 1/5` dan
  `I_xy = 0`, dan hanya untuk periode tepat `T0`.
- Tidak ada klaim global, tidak ada klaim "satu-satunya figure-eight",
  tidak ada klaim stabilitas/monodromy/eigenvalue, tidak ada klaim
  ergodisitas/chaos.
- K5 adalah uji konsistensi koreografi dalam toleransi, bukan bukti
  koreografi untuk semua waktu.
- Tidak ada klaim RH/PDE/Soliton/Evans/fisika/prioritas/Lean.
- T2 yang FAILED tetap tercatat; T2-r2 tidak mengubah T2, T1, T1b, atau
  modul beku.

## 8. Artefak yang direncanakan

- `reports/PREREG_FIGURE_EIGHT_R2_2026-10-22.md` (dokumen ini).
- `msaf/figure_eight_r2.py` (modul baru; tidak mengimpor
  `msaf/figure_eight.py`).
- `msaf/tests/test_figure_eight_r2.py` (guard baru).
- `reports/figure_eight_r2_2026-10-22.json` (receipt).
- `reports/FIGURE_EIGHT_R2_2026-10-22.md` (laporan peneliti).
- `reports/FENCE_REGISTRY.md` entri `A-2026-0041` hanya bila ALL PASS.

## 9. Probe desain float (bukan hasil tersertifikasi)

Probe float dilakukan di temp, bukan di repo, sebelum pra-registrasi ini.
Hasil yang memotivasi formulasi:

- Formulasi tereduksi naif (COM fixed, `T` unknown, seksi `q3y=0`):
  `sigma_min ~ 8.16e-10`, `cond ~ 1.03e11`; seksi `q1y=0`:
  `sigma_min ~ 1.04e-9`, `cond ~ 7.74e10`. Keduanya masih hampir singular
  karena keluarga energi/rotasi.
- Formulasi yang dipilih (COM, `T0` tetap, gauge `q1y=1/5` dan
  `I_xy=0`, drop baris `(2,7)`): pada titik konvergen,
  `sigma_min ~ 6.838e-3`, `cond ~ 1.36e4`, `det ~ -7.62`;
  residu seed `|G|_inf ~ 8.04e-14`; defek koreografi `~2.6e-11`;
  estimasi Lipschitz `DG` `~4.0e3` (float, noisy), sehingga
  `R_B = 1e-10` memberi margin Krawczyk yang lebar.
- Probe `q1y=0` + `I_xy=0` menemukan fase kolinear (q1y=0) dengan
  energi yang sama; gauge `q1y=1/5` menghindari degenerasi itu.
  Ini alasan nilai `1/5` dikunci, bukan `0`.
- Semua angka probe adalah float dan **tidak** menjadi klaim; kampanye
  tersertifikasi harus membuktikannya dengan interval.

## 10. Aturan amendemen

Tidak ada amendemen setelah kode T2-r2 dimulai. Bila ada bug/konstanta
yang harus diubah, buka pra-registrasi baru (T2-r2b) dan pertahankan
receipt gagal sebagai rekaman. Praxis proyek: verdict jujur lebih penting
daripada `ALL PASS`.
