# Pra-registrasi: spectral closure Ulam untuk peta skew tent chaotik — 2026-10-21

**Status:** scope DIKUNCI untuk paket ini; implementasi dan eksekusi **belum**
dimulai. Eksekusi menunggu commit pra-registrasi ini, lalu dijalankan dengan
konfigurasi yang tertulis di bawah.

**Berkas target:** `msaf/ulam_spectral.py` (baru), guard
`msaf/tests/test_ulam_spectral.py` (baru), laporan
`reports/ULAM_SPECTRAL_2026-10-21.md`, receipt
`reports/ulam_spectral_2026-10-21.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (`fmpq`, `fmpq_mat`,
`arb`, `arb_mat`). Tidak ada `numpy`/`scipy` di jalur inti.

**Registry yang direncanakan:** `A-2026-0024`, hanya bila verdict inti
minimal `PARTIAL` dan integritas PASS.

**Tidak mengubah:** V1–V6 (`A-2026-0015`–`A-2026-0021`), `A-2026-0022`,
`A-2026-0023`, `ci.yml` (`A-2026-0016`), workflow spec, `lean/lakefile.toml`,
freeze pins, dan seluruh laporan/artefak beku. Tidak menjalankan ulang
kampanye quantum/H1/engine-B.

## 1. Maksud dan batas

Blueprint item 5 meminta spectral closure dari operator transfer
Frobenius–Perron melalui matriks Ulam non-simetris, dengan eigensolver
interval dan alarm resolusi. Paket ini menguji **satu keluarga finite**
yang dapat disertifikasi exact pada lapisan matriks:

- peta **skew tent** penuh-cabang `T_p:[0,1] -> [0,1]`,
- partisi interval seragam,
- matriks Ulam dengan entri rasional exact,
- eigensolver `arb_mat.eig` pada tangga presisi terbatas.

Paket ini **bukan**:

- klaim ergodisitas global, klaim mixing, atau klaim invariant density
  kontinu dari peta;
- klaim bahwa spektrum Ulam `N=16/32` adalah spektrum operator transfer
  kontinu, atau klaim batas thermodynamic;
- klaim kontraksi **Newton** 60 iterasi. Jalur Newton tidak diimplementasikan
  dan dicatat `NOT TESTED`; yang diuji adalah tangga presisi dan alarm
  resolusi di sekitar `arb_mat.eig`;
- klaim fisika, RH, lokasi nol, `σ=1/2`, faktorisasi, RSA/ECC, atau
  transisi Anderson;
- penggunaan ulang data/kampanye tersegel.

Peta logistic `r=4` adalah contoh motivasi di blueprint, tetapi **tidak**
dipakai untuk sertifikat spektral ini. Dengan partisi seragam, struktur
dua-cabang simetrisnya menghasilkan matriks Ulam rank-deficient dengan
klaster eigenvalue nol; `arb_mat.eig` tidak dapat mengisolasi klaster itu.
Paket ini memakai skew tent penuh-cabang yang memberi entri exact dan
spektrum simple. Tidak ada klaim tentang spektrum logistic.

## 2. Peta dan matriks Ulam yang dikunci

Untuk integer `N >= 2`, tetapkan

```text
p_N = N / (2(N+1)).
```

Peta skew tent:

```text
T_N(x) = x / p_N                         untuk 0 <= x <= p_N
T_N(x) = (1 - x) / (1 - p_N)             untuk p_N <= x <= 1.
```

Kedua cabang penuh: cabang kiri memetakan `[0,p_N]` ke `[0,1]`, cabang
kanan memetakan `[p_N,1]` ke `[1,0]`. Slopes mutlaknya

```text
a_N = 1/p_N       = 2(N+1)/N
b_N = 1/(1-p_N)   = 2(N+1)/(N+2),
```

keduanya > 1. Breakpoint `p_N` rasional, sehingga semua preimage endpoint
rasional.

Partisi seragam:

```text
I_i = [i/N, (i+1)/N],   i = 0,...,N-1.
```

Matriks Ulam `P^(N)` berukuran `N x N` dengan konvensi baris = interval
asal, kolom = interval tujuan:

```text
P_ij = | I_i ∩ T_N^{-1}(I_j) | / |I_i|
     = N * | I_i ∩ T_N^{-1}(I_j) |.
```

Preimage eksplisit:

```text
T_N^{-1}(I_j) =
  [ p_N*j/N, p_N*(j+1)/N ]
  ∪
  [ 1 - (1-p_N)*(j+1)/N, 1 - (1-p_N)*j/N ].
```

Karena semua endpoint rasional dan panjang irisan rasional, setiap `P_ij`
adalah `fractions.Fraction` exact. Tidak ada pembulatan pada lapisan ini.

## 3. Instance yang dikunci

Dua instance dijalankan dalam paket yang sama; keduanya harus PASS untuk
verdict inti PASS.

| Peran | `N` | `p_N` | `a_N` | `b_N` |
|---|---:|---:|---:|---:|
| Primer | 16 | `8/17` | `17/8` | `17/9` |
| Replikasi | 32 | `16/33` | `33/16` | `33/17` |

`N=16` adalah instance utama; `N=32` adalah replikasi yang menguji apakah
perilaku enclosure bertahan saat dimensi naik dua kali. Tidak ada instance
lain yang boleh ditambahkan setelah hasil terlihat.

## 4. Pemeriksaan exact (C1)

Untuk setiap instance:

1. Semua entri `P_ij` nonnegative dan merupakan `Fraction` exact.
2. Setiap baris berjumlah tepat `1`; setiap entri berada di `[0,1]`.
3. Matriks tidak simetris: sekurangnya satu pasangan `(i,j)` dengan
   `P_ij != P_ji`.
4. `rank(P) = N` exact melalui `fmpq_mat.rank()`.
5. `rank(P - I) = N - 1` exact; jadi eigenvalue `1` simple secara aljabar.
6. `discriminant(charpoly(P)) != 0` exact; jadi semua eigenvalue simple
   (characteristic polynomial squarefree).

C1 PASS hanya bila keenam butir benar untuk kedua instance. Jika C1 gagal,
verdict `FAILED`; tidak ada penyelarasan parameter setelah hasil.

## 5. Enclosure spektral (C2)

Untuk setiap instance, matriks `P` dikonversi ke `arb_mat` dari `fmpq`
exact. Pada setiap presisi di tangga

```text
L = (64, 128, 256, 512, 1024) bit,
```

hitung

```text
E(bits) = arb_mat(P).eig(multiple=True, algorithm="rump").
```

`multiple=True` dipakai karena API eigensolver membutuhkannya untuk
spektrum dengan potensi overlap; `algorithm="rump"` dikunci karena lebih
ketat daripada default pada instance ini.

Untuk setiap rung:

- eigensolver harus mengembalikan tepat `N` eigenvalue;
- definisikan lebar rung sebagai

  ```text
  w(bits) = max_k max(rad(Re λ_k), rad(Im λ_k));
  ```

- tepat satu eigenvalue harus memenuhi `Re λ ∋ 1` dan `Im λ ∋ 0`
  (Perron eigenvalue);
- untuk semua eigenvalue lain, `abs_upper(λ) < 1` secara ball;
- target resolusi adalah `w(bits) <= 1e-25`.

C2 PASS bila:

1. kelima rung berhasil tanpa exception;
2. Perron dan spectral-gap checks benar di setiap rung;
3. sekurangnya satu rung memenuhi target `1e-25`;
4. lebar menurun ketat antar-rung:

   ```text
   upper(w(bits_{k+1})) < lower(w(bits_k)).
   ```

Rung pertama yang memenuhi target dicatat sebagai `first_pass_bits`; nilai
itu tidak boleh diubah setelah run.

## 6. Alarm resolusi dan budget (C3)

Modul harus menyediakan exception `ResolutionAlarm` dengan semantik:

- dilempar bila tidak ada rung yang memenuhi target `1e-25`;
- dilempar bila eigensolver gagal mengisolasi eigenvalue di semua rung;
- dilempar bila budget attempt habis sebelum target;
- alarm adalah kegagalan kapasitas finite, bukan bukti ledakan chaos.

Budget yang dikunci:

```text
MAX_RESOLUTION_ATTEMPTS = 60
MAX_PRECISION_BITS      = 1024
RESOLUTION_LADDER       = (64, 128, 256, 512, 1024)
TARGET_WIDTH            = 1e-25
```

Ladder memakai 5 rung dari budget 60. Ini **bukan** 60 iterasi Newton;
istilah "60" hanya batas atas attempt resolusi. Jalur kontraksi Newton
dicatat eksplisit sebagai `NOT TESTED`.

C3 PASS bila implementasi alarm lolos uji sintetis di guard dan jalur
kampanye nyata tidak memicu alarm (`alarm_triggered = false`).

## 7. Integritas dan receipt (C4)

Receipt deterministik memuat, untuk setiap instance:

- parameter `N`, `p`, dan hash matrix exact;
- `rank`, `rank(P-I)`, determinant, degree/discriminant status charpoly;
- untuk setiap rung: presisi, status eigensolver, `w(bits)`, jumlah
  eigenvalue, indeks Perron, `max_other_abs_upper`, `target_met`;
- `first_pass_bits`, `alarm_triggered`, `attempts_used`;
- `newton_contraction_tested: false` dan `scope_notes`;
- hash pra-registrasi (SHA-256 LF-normalised).

C4 PASS bila dua run deterministik menghasilkan payload kanonik identik dan
receipt di disk cocok dengan hasil hitung ulang.

## 8. Verdict

- **PASS:** C1, C2, C3, C4 PASS untuk kedua instance.
- **PARTIAL:** C1 PASS dan integritas PASS, tetapi C2 (target/contraction)
  atau C3 gagal; hasil dilaporkan tanpa klaim spectral closure.
- **INCONCLUSIVE:** eigensolver tidak tersedia/berperilaku tidak stabil
  sehingga C2 tidak dapat diputuskan; tidak dinaikkan menjadi PASS.
- **FAILED:** C1 gagal, atau hash/determinisme rusak.
- **TOOL NOT RUN:** dependensi `python-flint`/`arb_mat.eig` tidak tersedia.

`PASS` di sini berarti **enclosure interval untuk matriks Ulam finite yang
dikunci** lolos kriteria; bukan klaim tentang operator transfer kontinu,
bukan klaim ergodisitas/mixing, dan bukan klaim Newton.

## 9. Artefak dan urutan eksekusi

1. Commit pra-registrasi ini sebelum kode.
2. Implementasi `msaf/ulam_spectral.py` dengan konfigurasi penuh.
3. Guard `msaf/tests/test_ulam_spectral.py`: uji exact construction,
   rank, discriminant, eigensolver pada instance kecil, alarm sintetis,
   determinisme receipt, dan tamper hash. Guard tidak boleh mengubah
   parameter yang dikunci.
4. Jalankan kampanye penuh sekali; hasilkan receipt.
5. Tulis laporan `reports/ULAM_SPECTRAL_2026-10-21.md` dengan angka verbatim,
   verdict, runtime, hash, dan batas.
6. Bila verdict minimal `PARTIAL` dan integritas PASS: registry
   `A-2026-0024`, HANDOFF §2.0ar, sertifikat sha256LF.
7. Suite penuh, `freeze.py --verify`, push/CI hanya bila diminta.

## 10. Falsifier

Paket ini falsified bila salah satu dari berikut muncul:

- ada entri negatif, baris tidak berjumlah 1, atau matriks ternyata simetris;
- `rank(P) < N`, `rank(P-I) != N-1`, atau discriminant charpoly = 0;
- eigensolver mengembalikan jumlah eigenvalue salah, atau tidak ada
  eigenvalue yang memuat 1;
- ada eigenvalue non-Perron dengan `abs_upper >= 1`;
- tidak ada rung yang mencapai `1e-25`, atau lebar tidak menurun;
- receipt tidak deterministik atau hash tidak cocok.

Falsifier dicatat sebagai `FAILED`/`PARTIAL`; tidak ada perubahan ambang
setelah hasil.

## 11. Batas eksplisit

- Hanya `N=16` dan `N=32`; tidak ada ekstrapolasi ke `N -> ∞`.
- Hanya peta skew tent dengan `p_N = N/(2(N+1))`; bukan klaim untuk semua
  peta chaotik.
- Enclosure `arb_mat.eig` adalah untuk matriks finite yang dibangun, bukan
  untuk operator transfer kontinu; discretization error tidak dibatasi.
- Tidak ada klaim ergodisitas global, mixing, atau invariant density.
- Tidak ada klaim Newton 60 iterasi; `newton_contraction_tested = false`.
- Tidak ada klaim RH, lokasi nol, `σ=1/2`, faktorisasi, RSA/ECC, Anderson,
  atau fisika.
- `PASS` adalah verdict finite di bawah kriteria yang dikunci, bukan peer
  review atau klaim eksternal.
