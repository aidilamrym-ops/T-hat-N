# Pra-registrasi: sensus twin prime Q2 v3 — N = 10^9

**Status:** scope DIKUNCI untuk paket Q2 v3; implementasi dan eksekusi
**belum** dimulai. Berkas ini ditulis sebelum kode v3. Hash `sha256LF`
berkas ini dicatat di receipt dan laporan.

**Paket:** Q2 dari `reports/DAFTAR_MASALAH_KERJA.md`, yaitu sensus finit
pasangan twin prime `(p, p+2)`. v2 sudah CERTIFIED pada `N = 10^7`
(`A-2026-0045`). v3 adalah fragmen finit baru pada target asli
`N = 10^9`; v3 **tidak** mengubah atau menarik `A-2026-0045`.

**Berkas target:** `msaf/twin_prime_v3.py` (baru), guard
`msaf/tests/test_twin_prime_v3.py` (baru), laporan
`reports/TWIN_PRIME_V3_2026-10-25.md` (baru), receipt
`reports/twin_prime_v3_2026-10-25.json` (baru).

**Registry yang direncanakan:** `A-2026-0046`, hanya bila verdict inti
`ALL PASS` dan semua kriteria C1–C4 terpenuhi. Bila gagal, tidak ada
entri registry; laporan harus menyatakan `FAILED`/`PARTIAL` apa adanya.

**Tidak mengubah:** `msaf/twin_prime_v2.py`,
`msaf/tests/test_twin_prime_v2.py`,
`reports/twin_prime_v2_2026-10-25.json`,
`reports/TWIN_PRIME_V2_2026-10-25.md`,
`reports/PREREG_Q2_TWIN_PRIME_V2_2026-10-25.md`, `A-2026-0045`, entri
registry tersegel lain, `ci.yml`, dan freeze pins.

## 1. Pertanyaan yang dijawab

Berapa banyak pasangan twin prime `(p, p+2)` dengan `p <= 10^9`, dan
apakah dua implementasi sieve independen menghasilkan daftar pasangan
yang identik integer-per-integer pada seluruh rentang?

Ini adalah sensus finit. Hasilnya **bukan** bukti konjektur twin prime,
bukan klaim asimtotik, dan tidak berlaku untuk `N > 10^9`.

## 2. Konfigurasi yang dikunci

| Parameter | Nilai |
|---|---|
| `N` | `1_000_000_000` |
| Batas bilangan prima basis | `isqrt(N + 2) = 31623` |
| Blok sieve B | `2^24 = 16_777_216` |
| Aritmetika | integer Python eksak; tanpa float, tanpa numpy |
| Pasangan | `(p, p+2)` dengan `p` prima dan `p+2` prima, `p <= N` |
| Checkpoint | `10^6`, `10^7`, `10^8`, `10^9` |
| Digest pasangan | SHA-256 atas records 16 byte big-endian: `p.to_bytes(8,'big') + (p+2).to_bytes(8,'big')`, berurutan naik |

Nilai referensi checkpoint yang diketahui (digunakan sebagai pemeriksaan
tambahan, bukan satu-satunya kriteria):

| `x` | Banyak pasangan dengan `p <= x` |
|---:|---:|
| `10^6` | `8_169` |
| `10^7` | `58_980` |
| `10^8` | `440_312` |
| `10^9` | `3_424_506` |

## 3. Dua implementasi independen

**Sieve A — full Eratosthenes.** Alokasi `bytearray` untuk
`0..N+2`, tandai kelipatan setiap prima `q <= isqrt(N+2)`, lalu pindai
`p` ganjil dari `3` sampai `N`; pasangan diterima bila `p` dan `p+2`
keduanya bertanda prima. Implementasi A tidak memakai fungsi sieve B.

**Sieve B — segmented Eratosthenes.** Hitung bilangan prima basis sampai
`31623` dengan sieve sederhana terpisah. Untuk setiap blok
`[low, high]` berukuran `2^24`, bangun segmen `[low, high+2]`, tandai
kelipatan bilangan prima basis, lalu pindai `p` ganjil di
`[low, high]`; pasangan diterima bila `p` dan `p+2` bertanda prima.
Blok berikutnya mulai di `high+1`, sehingga tidak ada pasangan yang
terlewat atau terhitung dua kali. Implementasi B tidak memakai bytearray
penuh milik A.

Kedua generator menghasilkan pasangan dalam urutan naik. Perbandingan
dilakukan **element-wise** dengan `zip_longest`: setiap posisi harus
memuat pasangan yang sama; panjang kedua stream harus sama. Tidak cukup
hanya membandingkan count.

## 4. Kriteria C1–C4

**C1: dua sieve independen, aritmetika eksak.**
- A memakai bytearray penuh; B memakai segmented sieve dan basis prima
  terpisah.
- Tidak ada float, numpy, atau pemanggilan modul v2 di jalur sensus.
- Guard statis memeriksa tidak ada import numpy/float di jalur sensus.

**C2: kesepakatan penuh.**
- `count_a == count_b`.
- `max_gap_a == max_gap_b`, dengan `max_gap` = maksimum
  `p_{i+1} - p_i` atas pasangan berurutan.
- `first_pair_a == first_pair_b` dan `last_pair_a == last_pair_b`.
- `pairs_sha256_a == pairs_sha256_b`.
- Perbandingan element-wise tidak menemukan mismatch dan tidak ada
  perbedaan panjang.

**C3: checkpoint referensi.**
- Count pada `10^6`, `10^7`, `10^8`, `10^9` harus sama dengan nilai
  referensi di §2 untuk kedua sieve.
- Checkpoint `10^9` harus sama dengan `count` total.

**C4: determinisme receipt.**
- Receipt kanonik (JSON terurut, indentasi tetap, newline akhir) tanpa
  timestamp, runtime, path absolut, atau nama mesin.
- Dua run penuh berturut-turut harus menghasilkan byte receipt yang
  identik (SHA-256 sama).
- `prereg_sha256lf` di receipt harus sama dengan hash berkas ini.

## 5. Verdict

`all_pass = true` hanya bila C1–C4 semuanya terpenuhi. Bila salah satu
gagal, `all_pass = false`, `summary = "FAILED"`, dan tidak ada entri
registry. Tidak ada penarikan status v2/A-2026-0045.

## 6. Perintah verifikasi

```text
python msaf/twin_prime_v3.py
python -m pytest msaf/tests/test_twin_prime_v3.py -q
python -m pytest msaf/tests/test_fence_registry.py -q
python audit_quantum/freeze.py --verify
```

## 7. Batas klaim

- Hanya sensus finit hingga `N = 10^9`.
- Bukan bukti konjektur twin prime; tidak ada klaim asimtotik,
  distribusi, `N > 10^9`, RH/GRH, faktorisasi, RSA/ECC, Anderson, atau
  fisika.
- `A-2026-0045` (v2, `N = 10^7`) tetap menjadi klaim certified yang
  terpisah; v3 tidak menggantikannya.
