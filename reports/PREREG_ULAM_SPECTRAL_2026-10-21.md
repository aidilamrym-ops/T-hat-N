# Pra-registrasi: spectral closure Ulam for peta skew tent chaotik â€” 2026-10-21

**Status:** scope DIKUNCI for paket ini; implementasi and eksekusi **belum**
dimulai. Eksekusi menunggu commit pra-registrasi ini, lalu dijalankan with
konfigurasi which tertulis in bawah.

**Berkas target:** `msaf/ulam_spectral.py` (baru), guard
`msaf/tests/test_ulam_spectral.py` (baru), report
`reports/ULAM_SPECTRAL_2026-10-21.md`, receipt
`reports/ulam_spectral_2026-10-21.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (`fmpq`, `fmpq_mat`,
`arb`, `arb_mat`). Tidak ada `numpy`/`scipy` in jalur inti.

**Registry which direncanakan:** `A-2026-0024`, hanya bila verdict inti
minimal `PARTIAL` and integritas PASS.

**Tidak mengubah:** V1â€“V6 (`A-2026-0015`â€“`A-2026-0021`), `A-2026-0022`,
`A-2026-0023`, `ci.yml` (`A-2026-0016`), workflow spec, `lean/lakefile.toml`,
freeze pins, and seluruh report/artefak beku. Tidak menjalankan ulang
kampanye quantum/H1/engine-B.

## 1. Maksud and limit

Blueprint item 5 meminta spectral closure dari operator transfer
Frobeniusâ€“Perron melalui matriks Ulam non-simetris, with eigensolver
interval and alarm resolusi. Paket ini menguji **satu keluarga finite**
which dapat disertifikasi exact on lapisan matriks:

- peta **skew tent** penuh-cabang `T_p:[0,1] -> [0,1]`,
- partisi interval seragam,
- matriks Ulam with entri rasional exact,
- eigensolver `arb_mat.eig` on tangga presisi terbatas.

Paket ini **bukan**:

- klaim ergodisitas global, klaim mixing, or klaim invariant density
  kontinu dari peta;
- klaim bahwa spektrum Ulam `N=16/32` adalah spektrum operator transfer
  kontinu, or klaim limit thermodynamic;
- klaim kontraksi **Newton** 60 iterasi. Jalur Newton no diimplementasikan
  and dicatat `NOT TESTED`; which diuji adalah tangga presisi and alarm
  resolusi in sekitar `arb_mat.eig`;
- klaim fisika, RH, lokasi nol, `Ïƒ=1/2`, faktorisasi, RSA/ECC, or
  transisi Anderson;
- penggunaan ulang data/kampanye tersegel.

Peta logistic `r=4` adalah contoh motivasi in blueprint, tetapi **no**
dipakai for sertifikat spektral ini. Dengan partisi seragam, struktur
dua-cabang simetrisnya menghasilkan matriks Ulam rank-deficient with
klaster eigenvalue nol; `arb_mat.eig` no dapat mengisolasi klaster itu.
Paket ini memakai skew tent penuh-cabang which memberi entri exact and
spektrum simple. Tidak ada klaim tentang spektrum logistic.

## 2. Peta and matriks Ulam which dikunci

Untuk integer `N >= 2`, tetapkan

```text
p_N = N / (2(N+1)).
```

Peta skew tent:

```text
T_N(x) = x / p_N                         for 0 <= x <= p_N
T_N(x) = (1 - x) / (1 - p_N)             for p_N <= x <= 1.
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

Matriks Ulam `P^(N)` berukuran `N x N` with konvensi baris = interval
asal, kolom = interval tujuan:

```text
P_ij = | I_i âˆ© T_N^{-1}(I_j) | / |I_i|
     = N * | I_i âˆ© T_N^{-1}(I_j) |.
```

Preimage eksplisit:

```text
T_N^{-1}(I_j) =
  [ p_N*j/N, p_N*(j+1)/N ]
  âˆª
  [ 1 - (1-p_N)*(j+1)/N, 1 - (1-p_N)*j/N ].
```

Karena semua endpoint rasional and panjang irisan rasional, setiap `P_ij`
adalah `fractions.Fraction` exact. Tidak ada pembulatan on lapisan ini.

## 3. Instance which dikunci

Dua instance dijalankan dalam paket which sama; keduanya harus PASS for
verdict inti PASS.

| Peran | `N` | `p_N` | `a_N` | `b_N` |
|---|---:|---:|---:|---:|
| Primer | 16 | `8/17` | `17/8` | `17/9` |
| Replikasi | 32 | `16/33` | `33/16` | `33/17` |

`N=16` adalah instance utama; `N=32` adalah replikasi which menguji apakah
perilaku enclosure bertahan saat dimensi naik dua kali. Tidak ada instance
lain which boleh ditambahkan setelah result terlihat.

## 4. Pemeriksaan exact (C1)

Untuk setiap instance:

1. Semua entri `P_ij` nonnegative and merupakan `Fraction` exact.
2. Setiap baris berjumlah tepat `1`; setiap entri berada in `[0,1]`.
3. Matriks no simetris: sekurangnya satu pasangan `(i,j)` with
   `P_ij != P_ji`.
4. `rank(P) = N` exact melalui `fmpq_mat.rank()`.
5. `rank(P - I) = N - 1` exact; jadi eigenvalue `1` simple secara aljabar.
6. `discriminant(charpoly(P)) != 0` exact; jadi semua eigenvalue simple
   (characteristic polynomial squarefree).

C1 PASS hanya bila keenam butir benar for kedua instance. Jika C1 gagal,
verdict `FAILED`; no ada penyelarasan parameter setelah result.

## 5. Enclosure spektral (C2)

Untuk setiap instance, matriks `P` dikonversi ke `arb_mat` dari `fmpq`
exact. Pada setiap presisi in tangga

```text
L = (64, 128, 256, 512, 1024) bit,
```

hitung

```text
E(bits) = arb_mat(P).eig(multiple=True, algorithm="rump").
```

`multiple=True` dipakai karena API eigensolver membutuhkannya for
spektrum with potensi overlap; `algorithm="rump"` dikunci karena lebih
ketat daripada default on instance ini.

Untuk setiap rung:

- eigensolver harus mengembalikan tepat `N` eigenvalue;
- definisikan lebar rung sebagai

  ```text
  w(bits) = max_k max(rad(Re Î»_k), rad(Im Î»_k));
  ```

- tepat satu eigenvalue harus memenuhi `Re Î» âˆ‹ 1` and `Im Î» âˆ‹ 0`
  (Perron eigenvalue);
- for semua eigenvalue lain, `abs_upper(Î») < 1` secara ball;
- target resolusi adalah `w(bits) <= 1e-25`.

C2 PASS bila:

1. kelima rung berhasil tanpa exception;
2. Perron and spectral-gap checks benar in setiap rung;
3. sekurangnya satu rung memenuhi target `1e-25`;
4. lebar menurun ketat antar-rung:

   ```text
   upper(w(bits_{k+1})) < lower(w(bits_k)).
   ```

Rung pertama which memenuhi target dicatat sebagai `first_pass_bits`; nilai
itu no boleh diubah setelah run.

## 6. Alarm resolusi and budget (C3)

Modul harus menyediakan exception `ResolutionAlarm` with semantik:

- dilempar bila no ada rung which memenuhi target `1e-25`;
- dilempar bila eigensolver gagal mengisolasi eigenvalue in semua rung;
- dilempar bila budget attempt habis sebelum target;
- alarm adalah kegagalan kapasitas finite, bukan bukti ledakan chaos.

Budget which dikunci:

```text
MAX_RESOLUTION_ATTEMPTS = 60
MAX_PRECISION_BITS      = 1024
RESOLUTION_LADDER       = (64, 128, 256, 512, 1024)
TARGET_WIDTH            = 1e-25
```

Ladder memakai 5 rung dari budget 60. Ini **bukan** 60 iterasi Newton;
istilah "60" hanya limit atas attempt resolusi. Jalur kontraksi Newton
dicatat eksplisit sebagai `NOT TESTED`.

C3 PASS bila implementasi alarm lolos uji sintetis in guard and jalur
kampanye nyata no memicu alarm (`alarm_triggered = false`).

## 7. Integritas and receipt (C4)

Receipt deterministik memuat, for setiap instance:

- parameter `N`, `p`, and hash matrix exact;
- `rank`, `rank(P-I)`, determinant, degree/discriminant status charpoly;
- for setiap rung: presisi, status eigensolver, `w(bits)`, jumlah
  eigenvalue, indeks Perron, `max_other_abs_upper`, `target_met`;
- `first_pass_bits`, `alarm_triggered`, `attempts_used`;
- `newton_contraction_tested: false` and `scope_notes`;
- hash pra-registrasi (SHA-256 LF-normalised).

C4 PASS bila dua run deterministik menghasilkan payload kanonik identik and
receipt in disk cocok with result hitung ulang.

## 8. Verdict

- **PASS:** C1, C2, C3, C4 PASS for kedua instance.
- **PARTIAL:** C1 PASS and integritas PASS, tetapi C2 (target/contraction)
  or C3 gagal; result dilaporkan tanpa klaim spectral closure.
- **INCONCLUSIVE:** eigensolver no tersedia/berperilaku no stabil
  sehingga C2 no dapat diputuskan; no dinaikkan menjadi PASS.
- **FAILED:** C1 gagal, or hash/determinisme rusak.
- **TOOL NOT RUN:** dependensi `python-flint`/`arb_mat.eig` no tersedia.

`PASS` in sini berarti **enclosure interval for matriks Ulam finite which
dikunci** lolos kriteria; bukan klaim tentang operator transfer kontinu,
bukan klaim ergodisitas/mixing, and bukan klaim Newton.

## 9. Artefak and urutan eksekusi

1. Commit pra-registrasi ini sebelum kode.
2. Implementasi `msaf/ulam_spectral.py` with konfigurasi penuh.
3. Guard `msaf/tests/test_ulam_spectral.py`: uji exact construction,
   rank, discriminant, eigensolver on instance kecil, alarm sintetis,
   determinisme receipt, and tamper hash. Guard no boleh mengubah
   parameter which dikunci.
4. Jalankan kampanye penuh sekali; hasilkan receipt.
5. Tulis report `reports/ULAM_SPECTRAL_2026-10-21.md` with angka verbatim,
   verdict, runtime, hash, and limit.
6. Bila verdict minimal `PARTIAL` and integritas PASS: registry
   `A-2026-0024`, HANDOFF Â§2.0ar, sertifikat sha256LF.
7. Suite penuh, `freeze.py --verify`, push/CI hanya bila diminta.

## 10. Falsifier

Paket ini falsified bila salah satu dari berikut muncul:

- ada entri negatif, baris no berjumlah 1, or matriks ternyata simetris;
- `rank(P) < N`, `rank(P-I) != N-1`, or discriminant charpoly = 0;
- eigensolver mengembalikan jumlah eigenvalue salah, or no ada
  eigenvalue which memuat 1;
- ada eigenvalue non-Perron with `abs_upper >= 1`;
- no ada rung which mencapai `1e-25`, or lebar no menurun;
- receipt no deterministik or hash no cocok.

Falsifier dicatat sebagai `FAILED`/`PARTIAL`; no ada perubahan ambang
setelah result.

## 11. Batas eksplisit

- Hanya `N=16` and `N=32`; no ada ekstrapolasi ke `N -> âˆž`.
- Hanya peta skew tent with `p_N = N/(2(N+1))`; bukan klaim for semua
  peta chaotik.
- Enclosure `arb_mat.eig` adalah for matriks finite which dibangun, bukan
  for operator transfer kontinu; discretization error no dibatasi.
- Tidak ada klaim ergodisitas global, mixing, or invariant density.
- Tidak ada klaim Newton 60 iterasi; `newton_contraction_tested = false`.
- Tidak ada klaim RH, lokasi nol, `Ïƒ=1/2`, faktorisasi, RSA/ECC, Anderson,
  or fisika.
- `PASS` adalah verdict finite in bawah kriteria which dikunci, bukan peer
  review or klaim eksternal.


