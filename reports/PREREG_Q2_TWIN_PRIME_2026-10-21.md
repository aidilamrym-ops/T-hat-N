# Pra-registrasi: Sensus Twin Prime Tersertifikasi (Q2) — 2026-10-21

**Status:** scope DIKUNCI untuk paket Q2; implementasi dan eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket Q2. Hash `sha256LF` berkas ini
dicatat di receipt dan laporan.

**Paket:** Q2 dari
[`reports/DAFTAR_MASALAH_KERJA.md`](DAFTAR_MASALAH_KERJA.md),
yaitu sensus twin prime tersertifikasi hingga N (mulai N = 10^9).

**Berkas target:** `msaf/twin_prime_sieve.py` (baru), guard
`msaf/tests/test_twin_prime_sieve.py` (baru), laporan
`reports/TWIN_PRIME_CENSUS_2026-10-21.md`, receipt
`reports/twin_prime_census_2026-10-21.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (opsional, untuk verifikasi),
modul `msaf.primes` (akan dibuat), hanya library standar Python.

**Registry yang direncanakan:** `A-2026-0029`, hanya bila verdict inti
`ALL PASS` dan integritas PASS.

**Tidak mengubah:** V1–V6, `A-2026-0022`–`A-2026-0028`, `ci.yml`,
workflow spec, `lean/lakefile.toml`, freeze pins, artefak beku.

## 1. Maksud dan batas

Paket ini membangun **sieve twin prime tersertifikasi** yang menghitung
semua pasangan twin prime (p, p+2) dengan p ≤ N, untuk N yang dikunci
(mulai N = 10^9). Hanya dihitung pasangan di mana p dan p+2 keduanya prima.

Kunci: **dua implementasi sieve independen** (segmented, implementasi
terpisah) harus **sepakat integer-per-integer** pada:
- Jumlah total pasangan twin prime ≤ N
- Daftar pasangan (p, p+2) (jika N cukup kecil untuk disimpan)
- Gap maksimum antara twin prime berurutan ≤ N

Ini adalah **sensus**, bukan pencarian: semua pasangan hingga N dihitung,
bukan hanya pencarian contoh.

Paket ini **bukan**:
- pembuktian konjektur twin prime tak hingga (hanya sensus hingga N).
- klaim tentang distribusi asimtotik (hanya hitungan eksak hingga N).
- klaim RH, GRH, faktorisasi, RSA/ECC, Anderson, atau fisika.

## 2. Arsitektur Sieve Tersertifikasi

**Dua implementasi independen (wajib):**

1. **Sieve A: Segmented Eratosthenes + Wheel Factorization**
   - Segment size dikunci (mis. 2^20)
   - Wheel 2,3,5,7 (skip multiples of 2,3,5,7)
   - Bit-packed array (1 bit per kandidat)
   - Output: count + daftar pasangan (jika N ≤ threshold)

2. **Sieve B: Bitwise Segmented Sieve dengan Wheel 30 (2,3,5)**
   - Implementasi terpisah total (tidak share code dengan Sieve A)
   - Wheel 30 (skip multiples of 2,3,5)
   - Block-based dengan precomputed pattern
   - Output identik: count + daftar pasangan

**Kriteria kesepakatan (sepakat integer-per-integer):**
- `count_A == count_B`
- Jika N ≤ 10^7: `pairs_A == pairs_B` (element-wise)
- Gap maksimum: `max_gap_A == max_gap_B`

**Output tercatat:**
- `count`: total pasangan twin prime ≤ N
- `pairs`: array of [p, p+2] (jika N ≤ 10^7, opsional untuk N lebih besar)
- `max_gap`: gap maksimum antara twin prime berurutan
- `first_pair`, `last_pair`: pasangan pertama dan terakhir
- `runtime_seconds`: waktu eksekusi per sieve
- `memory_peak_mb`: puncak memori

## 3. Konfigurasi yang dikunci

| Parameter | Nilai |
|-----------|-------|
| N_min | 10^9 (1,000,000,000) |
| N_max | 10^9 (untuk kampanye ini; N lebih besar untuk sesi depan) |
| Segment size | 2^20 = 1,048,576 |
| Wheel A | 2,3,5,7 (mod 210) |
| Wheel B | 2,3,5 (mod 30) |
| Threshold simpan pasangan | N ≤ 10^7 |

Tidak ada parameter tambahan setelah hasil terlihat.

## 4. Pemeriksaan integritas (C1–C4)

**C1: Kedua sieve menghasilkan count identik**
- `count_A == count_B` untuk N yang dikunci.

**C2: Daftar pasangan identik (jika N ≤ 10^7)**
- `pairs_A == pairs_B` element-wise.

**C3: Gap maksimum identik**
- `max_gap_A == max_gap_B`.

**C4: Determinisme & receipt**
- Dua run berturut-turut menghasilkan payload kanonik identik.
- Receipt sha256 terkunci.

## 5. Verdict

- **ALL PASS**: C1, C2, C3, C4 PASS untuk N yang dikunci.
- **PARTIAL**: tidak ada (paket ini all-or-nothing).
- **FAILED**: salah satu C1–C4 gagal.
- **INCONCLUSIVE**: tool error, memori tidak cukup, atau hash mismatch.

Registry `A-2026-0029` hanya bila verdict `ALL PASS` dan integritas PASS.

## 6. Falsifier

Paket ini falsified bila:
- `count_A != count_B` untuk N yang dikunci.
- `pairs_A != pairs_B` (untuk N ≤ 10^7).
- `max_gap_A != max_gap_B`.
- Receipt tidak deterministik atau hash mismatch.
- Memori melebihi batas sistem (OOM).

## 6. Artefak dan urutan eksekusi

1. Tulis dan hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/twin_prime_sieve.py` dengan dua sieve independen.
3. Guard `msaf/tests/test_twin_prime_sieve.py`: uji kesepakatan count, pairs, gap, determinisme.
4. Jalankan kampanye untuk N = 10^9 (dua sieve berjalan).
5. Tulis laporan `reports/TWIN_PRIME_CENSUS_2026-10-21.md` dengan angka verbatim.
6. Bila `ALL PASS`: registry `A-2026-0029`, HANDOFF §2.0aw, sertifikat sha256LF.
7. Suite penuh dan `freeze.py --verify`; commit/push hanya bila diminta.

## 7. Batas eksplisit

- Hanya N = 10^9 untuk kampanye ini (N lebih besar sesi depan).
- Hanya twin prime (p, p+2); bukan prime k-tuples umum.
- Tidak ada klaim tak hingga, asimtotik, RH, GRH, faktorisasi, RSA/ECC, Anderson, atau fisika.
- Tidak ada klaim "bukti" konjektur twin prime.
- Hanya sensus hingga N = 10^9; klaim asimtotik di luar scope.