# Sensus abc Tersertifikasi Q3 v3 — hingga C = 10^7

**Tanggal:** 2026-10-27
**Status:** `ALL PASS` (dua sieve sepakat eksak, receipt deterministik)
**Registry:** `A-2026-0052`
**Pra-registrasi:** `reports/PREREG_Q3_ABC_CENSUS_V3_2026-10-27.md`
sha256LF `aed8e63cdbb463b58bf207686ddf562ae50114b1d38b40f52174e53f1a6001a2`

## 1. Ringkasan

Sensus lengkap abc hingga C = 10^7 untuk kualitas
`q = log(c) / log(rad(a*b*c)) > 1.4` menemukan **17 triple**. Kedua sieve
independen sepakat eksak pada count, max_gap, dan daftar triple.

| C | Count | Max gap | Verdict | Canonical SHA-256 |
|---|---:|---:|---|---|
| 100.000 | 6 | 6.825 | ALL PASS | `cc077c8a0d5b9b07ea6fcb7cf63b9f801b57dd176a7f3b9ab05dd898aaaf163f` |
| 1.000.000 | 11 | 6.825 | ALL PASS | `fb8cd831eaed0753b9cee6e62f028d9536771a83ab0ee97a2e6887957808d1fe` |
| 10.000.000 | 17 | 40.640 | ALL PASS | `fb0ea6f8345054058d7d1b9659e8c167d82602f90d349908f9b67284e73f3c4d` |

Gate C=10^5 mereproduksi `A-2026-0032` persis: 6 triple, max_gap 6825,
daftar triple identik.

## 2. Koreksi penting: v2 100-smooth tidak lengkap

Versi v2 mengunci `max_prime = 100` (hanya bilangan 100-halus). Itu bukan
batas yang sah untuk kelengkapan. Batas yang benar dari `q > 1.4` hanyalah

```text
rad(abc) < c^(5/7) <= N^(5/7)
```

sehingga faktor prima individual boleh jauh di atas 100 selama radikal
totalnya tetap kecil. Akibatnya v2 menemukan 12 triple, bukan 17.

Lima triple yang hilang dari v2:

| Triple | Faktor prima > 100 | q |
|---|---|---:|
| (5, 177147, 177152) | 173 | 1,412681 |
| (25, 4804839, 4804864) | 137 | 1,413279 |
| (43840, 4782969, 4826809) | 137 | 1,413698 |
| (2, 6436341, 6436343) | 109 | 1,629912 |
| (11, 9565927, 9565938) | 167 | 1,428323 |

v2 tetap sah sebagai **sensus parsial bilangan 100-halus**, tetapi tidak sah
sebagai sensus lengkap. Receipt v2 parsial dipertahankan di
`reports/abc_census_v2_10000000.json`
(sha256LF `402e9acd2a136432918420498bf9282c5ff148888cf75255e823d9cc7308a46b`)
dan tidak disertifikasi.

## 3. Metodologi v3

### 3.1 Kelengkapan

Jika `q > 1.4`, maka:

```text
log(c) / log(rad(abc)) > 1.4
log(rad(abc)) < (5/7) log(c)
rad(abc) < c^(5/7) <= N^(5/7)
```

Karena `rad(a)`, `rad(b)`, dan `rad(c)` masing-masing tidak melebihi
`rad(abc)`, ketiganya berada di himpunan low-rad

```text
L_N = { n <= N : rad(n) <= floor(N^(5/7)) + 1 }.
```

Jadi enumerasi atas `L_N` lengkap; tidak ada triple `q > 1.4` yang bisa lolos.

### 3.2 Aturan kandidat

1. Iterasi `c` di `L_N`, `c >= 3`.
2. Uji eksak integer `rad(c)^7 < c^5`.
3. Untuk `a` di `L_N` yang diurutkan berdasarkan rad, dengan
   `rad(a) <= floor(c^(5/7) / rad(c)) + 2` dan `2a < c`:
   - `b = c - a`;
   - `b` harus di `L_N`;
   - uji eksak integer `(rad(a) rad(b) rad(c))^7 < c^5`;
   - `gcd(a,b) = 1` (ekuivalen dengan `gcd(a,b,c) = 1` untuk `a+b=c`);
   - terima; hitung `q` float64 untuk pelaporan.
4. `max_gap` dihitung dari selisih `a` berurutan dalam urutan `c` menaik.

Uji `prod^7 < c^5` adalah uji eksak untuk `q > 1.4` dalam aritmetika real;
`math.log` float64 hanya dipakai untuk pelaporan.

### 3.3 Dua sieve independen

| Sieve | Rad | Himpunan low-rad | Verifikasi akhir |
|---|---|---|---|
| A | multiplicative list sieve | scan `rad` + urut rad | — |
| B | segmented `array("I")` sieve | scan `rad` B sendiri | `sympy.factorint` per triple final |

Sieve B tidak mengimpor helper internal A. `factorint` tidak pernah dipanggil
untuk setiap bilangan 3..N; ia hanya dipakai pada 17 triple final.

### 3.4 Receipt, progress, checkpoint

- Receipt ditulis atomik ke `--out` melalui `.tmp` lalu `os.replace`.
- Progress log mencatat prep/scan per sieve dan penulisan receipt.
- Checkpoint menyimpan `next_index`, count, max_gap, last_a, pairs, runtime,
  dan done per sieve; resume menghasilkan canonical hash yang sama.
- `canonical_sha256` mengecualikan `runtime_a`, `runtime_b`, dan dirinya
  sendiri.

## 4. Hasil penuh C = 10^7

17 triple, urut sesuai scan:

| # | a | b | c |
|---:|---:|---:|---:|
| 1 | 3 | 125 | 128 |
| 2 | 1 | 2.400 | 2.401 |
| 3 | 1 | 4.374 | 4.375 |
| 4 | 37 | 32.768 | 32.805 |
| 5 | 343 | 59.049 | 59.392 |
| 6 | 7.168 | 78.125 | 85.293 |
| 7 | 5 | 177.147 | 177.152 |
| 8 | 121 | 255.879 | 256.000 |
| 9 | 338 | 390.625 | 390.963 |
| 10 | 1 | 512.000 | 512.001 |
| 11 | 2.197 | 700.928 | 703.125 |
| 12 | 1.701 | 1.046.875 | 1.048.576 |
| 13 | 25 | 4.804.839 | 4.804.864 |
| 14 | 3.200 | 4.823.609 | 4.826.809 |
| 15 | 43.840 | 4.782.969 | 4.826.809 |
| 16 | 2 | 6.436.341 | 6.436.343 |
| 17 | 11 | 9.565.927 | 9.565.938 |

`first_triple = (3, 125, 128)`, `last_triple = (11, 9565927, 9565938)`.

## 5. Determinisme dan resume

- Gate C=10^5 dijalankan dua kali: canonical
  `cc077c8a...` identik.
- Validasi C=10^6 dijalankan dua kali (run kedua oleh proses verifikasi
  terpisah): canonical `fb8cd831...` identik.
- Full C=10^7 dijalankan dua kali: canonical `fb0ea6f8...` identik.
- Uji `test_resume_matches_clean_run` memaksa chunking pada C=10^5 dan
  membandingkan canonical hash dengan run bersih: identik.

Runtime di receipt tidak deterministik dan dikecualikan dari canonical hash.
Run full pertama selesai sekitar 4 menit; run kedua sekitar 5 menit karena
berjalan bersamaan dengan proses verifikasi lain.

## 6. Verifikasi

```text
python -m msaf.abc_census --N 100000 --max-seconds 0 \
  --out reports/abc_census_v3_100000.json
python -m msaf.abc_census --N 1000000 --max-seconds 0 \
  --out reports/abc_census_v3_1000000.json
python -m msaf.abc_census --N 10000000 --max-seconds 0 \
  --out reports/abc_census_v3_10000000.json
python -m pytest msaf/tests/test_abc_census.py -q
python -m pytest msaf/tests/test_fence_registry.py -q
```

`--max-seconds 0` berarti tanpa deadline per chunk. Default produksi adalah
900 detik per chunk dengan checkpoint/resume.

## 7. Artefak

| Artefak | sha256LF |
|---|---|
| `reports/PREREG_Q3_ABC_CENSUS_V3_2026-10-27.md` | `aed8e63cdbb463b58bf207686ddf562ae50114b1d38b40f52174e53f1a6001a2` |
| `msaf/abc_census.py` | `d3834fc91fd238cd8e27c76e07fa47eabd113d1a07ea21002c2a42105d28a293` |
| `msaf/tests/test_abc_census.py` | `1628c60a26dde17082a1fbb66b5dc8158c97d647e94059c75fe4cc338916dd2e` |
| `reports/abc_census_v3_100000.json` | `ef5e1905545f0dafda551c99dc7c69bda8d6a855102e61efac239492b0778bcb` |
| `reports/abc_census_v3_1000000.json` | `82be0eb719bc642ed0b3ab3d9a37f79ada603aa25ca80208efb8b0aee69f82d6` |
| `reports/abc_census_v3_10000000.json` | `e2176e22df095e19015422e6ed2d7564b131ca90f8d866cfa3edaa6dbef69af8` |
| `reports/abc_census_exploratory_2026-10-27.json` | `82bb92a186adb8b1f3a32de0fc9c98a22d6ac2c612ba4363c1dcc1ba9f3a4351` |

Receipt eksploratori `abc_census_exploratory_2026-10-27.json` adalah run
independen awal yang menemukan 17 triple; ia bukan sertifikat dan tidak
dipakai sebagai bukti formal. Sertifikat adalah receipt v3 di atas.

## 8. Batas dan non-klaim

- Ini sensus finit hingga C = 10^7; bukan pembuktian konjektur abc.
- Tidak ada klaim asimtotik, RH, GRH, faktorisasi, RSA/ECC, Anderson, atau
  fisika.
- Threshold dikunci pada q > 1.4.
- `q` dilaporkan dengan float64 `math.log`; keputusan kelengkapan memakai uji
  integer eksak `prod^7 < c^5`.
- `max_gap` adalah maksimum selisih `a` berurutan dalam urutan scan `c`,
  bukan selisih `c`.
- Tidak ada `numpy`/`scipy` di jalur inti.

## 9. Catatan integritas registry

- `A-2026-0032` (C=100.000, 6 triple) tidak di-retract. Karena modul dan guard
  berubah untuk v3, dua baris `sha256LF` miliknya diperbarui ke hash v3 dan
  diberi catatan tanggal di entri. Klaim 6 triple tidak berubah.
- `A-2026-0052` adalah entri baru untuk Q3 v3; ia tidak menulis ulang entri
  lama.
- v2 (12 triple) adalah hasil parsial yang superseded; receipt-nya
  dipertahankan sebagai bukti, bukan sertifikat.

## 10. Kesimpulan

Q3 v3 lulus semua kriteria C1–C7: gate C=10^5 mereproduksi 6/6825, validasi
C=10^6 menghasilkan 11/6825, full C=10^7 menghasilkan 17/40640, kedua sieve
sepakat eksak, receipt deterministik, resume identik, dan verifikasi
`factorint` berhasil untuk seluruh 17 triple.
