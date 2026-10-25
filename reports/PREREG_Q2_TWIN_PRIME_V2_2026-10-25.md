# Pra-registrasi: Sensus Twin Prime Q2 v2 — N = 10^7

**Status: PRA-REGISTRASI, ditulis dan di-commit sebelum kode Q2 v2.**
Ini adalah fragmen finit baru, bukan amendemen `A-2026-0029`. Entri lama
tetap `INCONCLUSIVE` dan tidak diubah.

## 1. Maksud dan batas

Menghitung **semua** pasangan twin prime `(p, p+2)` dengan `p <= N` untuk
`N = 10_000_000`, memakai **dua implementasi sieve independen** yang tidak
berbagi kode inti. Hasilnya adalah sensus finit, bukan bukti konjektur twin
prime, bukan klaim asimtotik, bukan klaim RH/GRH/faktorisasi/RSA/ECC/
Anderson/fisika.

## 2. Konfigurasi yang dikunci

| Parameter | Nilai |
|---|---|
| N | `10_000_000` |
| Sieve A | Eratosthenes bytearray penuh, scan `p` dan `p+2` |
| Sieve B | segmented sieve, base prime sampai `isqrt(N+2)`, block `2^20` |
| Arithmetic | integer Python eksak; tanpa float di jalur sensus |
| Runtime di receipt | tidak ada |
| Pasangan disimpan | ya, seluruh daftar `(p, p+2)` |

## 3. Kriteria verdict

- **C1**: `count_A == count_B`.
- **C2**: `pairs_A == pairs_B` element-wise.
- **C3**: `max_gap_A == max_gap_B`.
- **C4**: dua run berturut-turut menghasilkan receipt kanonik byte-identik.

**ALL PASS** hanya bila C1–C4 lulus. Tidak ada PARTIAL. Jika salah satu
gagal: **FAILED**. Jika tool error/OOM: **INCONCLUSIVE**.

## 4. Artefak yang akan dibuat setelah prereg ini

- `msaf/twin_prime_v2.py` — dua sieve independen + receipt writer.
- `msaf/tests/test_twin_prime_v2.py` — guard C1–C3 pada N kecil + determinisme.
- `reports/twin_prime_v2_2026-10-25.json` — receipt sensus N=10^7.
- `reports/TWIN_PRIME_V2_2026-10-25.md` — laporan.
- Registry `A-2026-0045` hanya bila ALL PASS.

## 5. Batas klaim

Sensus hingga `10^7` tidak membuktikan apa pun tentang tak hingga banyak
twin prime. Tidak ada klaim distribusi asimtotik. Tidak ada klaim tentang
bilangan prima di luar rentang yang dihitung.
