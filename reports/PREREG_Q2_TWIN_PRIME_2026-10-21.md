# Pra-registrasi: Sensus Twin Prime Tersertifikasi (Q2) â€” 2026-10-21

**Status:** scope DIKUNCI for paket Q2; implementasi and eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket Q2. Hash `sha256LF` file ini
dicatat in receipt and report.

**Paket:** Q2 dari
[`reports/DAFTAR_MASALAH_KERJA.md`](DAFTAR_MASALAH_KERJA.md),
yaitu sensus twin prime tersertifikasi hingga N (mulai N = 10^9).

**Berkas target:** `msaf/twin_prime_sieve.py` (baru), guard
`msaf/tests/test_twin_prime_sieve.py` (baru), report
`reports/TWIN_PRIME_CENSUS_2026-10-21.md`, receipt
`reports/twin_prime_census_2026-10-21.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (opsional, for verifikasi),
modul `msaf.primes` (akan created), hanya library standar Python.

**Registry which direncanakan:** `A-2026-0029`, hanya bila verdict inti
`ALL PASS` and integritas PASS.

**Tidak mengubah:** V1â€“V6, `A-2026-0022`â€“`A-2026-0028`, `ci.yml`,
workflow spec, `lean/lakefile.toml`, freeze pins, artefak beku.

## 1. Maksud and limit

Paket ini membangun **sieve twin prime tersertifikasi** which menghitung
semua pasangan twin prime (p, p+2) with p â‰¤ N, for N which dikunci
(mulai N = 10^9). Hanya dihitung pasangan in mana p and p+2 keduanya prima.

Kunci: **dua implementasi sieve independen** (segmented, implementasi
terpisah) harus **sepakat integer-per-integer** on:
- Jumlah total pasangan twin prime â‰¤ N
- Daftar pasangan (p, p+2) (jika N cukup kecil for disimpan)
- Gap maksimum antara twin prime berurutan â‰¤ N

Ini adalah **sensus**, bukan pencarian: semua pasangan hingga N dihitung,
bukan hanya pencarian contoh.

Paket ini **bukan**:
- pembuktian konjektur twin prime tak hingga (hanya sensus hingga N).
- klaim tentang distribusi asimtotik (hanya hitungan eksak hingga N).
- klaim RH, GRH, faktorisasi, RSA/ECC, Anderson, or fisika.

## 2. Arsitektur Sieve Tersertifikasi

**Dua implementasi independen (wajib):**

1. **Sieve A: Segmented Eratosthenes + Wheel Factorization**
   - Segment size dikunci (mis. 2^20)
   - Wheel 2,3,5,7 (skip multiples of 2,3,5,7)
   - Bit-packed array (1 bit per kandidat)
   - Output: count + daftar pasangan (jika N â‰¤ threshold)

2. **Sieve B: Bitwise Segmented Sieve with Wheel 30 (2,3,5)**
   - Implementasi terpisah total (no share code with Sieve A)
   - Wheel 30 (skip multiples of 2,3,5)
   - Block-based with precomputed pattern
   - Output identik: count + daftar pasangan

**Kriteria kesepakatan (sepakat integer-per-integer):**
- `count_A == count_B`
- Jika N â‰¤ 10^7: `pairs_A == pairs_B` (element-wise)
- Gap maksimum: `max_gap_A == max_gap_B`

**Output tercatat:**
- `count`: total pasangan twin prime â‰¤ N
- `pairs`: array of [p, p+2] (jika N â‰¤ 10^7, opsional for N lebih besar)
- `max_gap`: gap maksimum antara twin prime berurutan
- `first_pair`, `last_pair`: pasangan pertama and terakhir
- `runtime_seconds`: waktu eksekusi per sieve
- `memory_peak_mb`: puncak memori

## 3. Konfigurasi which dikunci

| Parameter | Nilai |
|-----------|-------|
| N_min | 10^9 (1,000,000,000) |
| N_max | 10^9 (for kampanye ini; N lebih besar for sesi depan) |
| Segment size | 2^20 = 1,048,576 |
| Wheel A | 2,3,5,7 (mod 210) |
| Wheel B | 2,3,5 (mod 30) |
| Threshold simpan pasangan | N â‰¤ 10^7 |

Tidak ada parameter tambahan setelah result terlihat.

## 4. Pemeriksaan integritas (C1â€“C4)

**C1: Kedua sieve menghasilkan count identik**
- `count_A == count_B` for N which dikunci.

**C2: Daftar pasangan identik (jika N â‰¤ 10^7)**
- `pairs_A == pairs_B` element-wise.

**C3: Gap maksimum identik**
- `max_gap_A == max_gap_B`.

**C4: Determinisme & receipt**
- Dua run berturut-turut menghasilkan payload kanonik identik.
- Receipt sha256 terkunci.

## 5. Verdict

- **ALL PASS**: C1, C2, C3, C4 PASS for N which dikunci.
- **PARTIAL**: no ada (paket ini all-or-nothing).
- **FAILED**: salah satu C1â€“C4 gagal.
- **INCONCLUSIVE**: tool error, memori no cukup, or hash mismatch.

Registry `A-2026-0029` hanya bila verdict `ALL PASS` and integritas PASS.

## 6. Falsifier

Paket ini falsified bila:
- `count_A != count_B` for N which dikunci.
- `pairs_A != pairs_B` (for N â‰¤ 10^7).
- `max_gap_A != max_gap_B`.
- Receipt no deterministik or hash mismatch.
- Memori melebihi limit sistem (OOM).

## 6. Artefak and urutan eksekusi

1. Tulis and hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/twin_prime_sieve.py` with dua sieve independen.
3. Guard `msaf/tests/test_twin_prime_sieve.py`: uji kesepakatan count, pairs, gap, determinisme.
4. Jalankan kampanye for N = 10^9 (dua sieve berjalan).
5. Tulis report `reports/TWIN_PRIME_CENSUS_2026-10-21.md` with angka verbatim.
6. Bila `ALL PASS`: registry `A-2026-0029`, HANDOFF Â§2.0aw, sertifikat sha256LF.
7. Suite penuh and `freeze.py --verify`; commit/push hanya bila diminta.

## 7. Batas eksplisit

- Hanya N = 10^9 for kampanye ini (N lebih besar sesi depan).
- Hanya twin prime (p, p+2); bukan prime k-tuples umum.
- Tidak ada klaim tak hingga, asimtotik, RH, GRH, faktorisasi, RSA/ECC, Anderson, or fisika.
- Tidak ada klaim "bukti" konjektur twin prime.
- Hanya sensus hingga N = 10^9; klaim asimtotik in luar scope.

