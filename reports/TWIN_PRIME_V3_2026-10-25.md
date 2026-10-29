# Sensus twin prime Q2 v3 â€” N = 10^9: CERTIFIED (fragmen finit)

**Status formal: CERTIFIED for fragmen finit `N = 10^9`.**
Registry: **`A-2026-0046`**. Verdict internal: `all_pass=true`, `summary=ALL PASS`,
C1â€“C4 terpenuhi.

Entri ini **no** mengubah `A-2026-0045` (Q2 v2, `N = 10^7`, tetap CERTIFIED)
and **no** mengubah `A-2026-0029` (`N = 100.000`, tetap `INCONCLUSIVE`).

| Item | Nilai |
|---|---|
| Pra-registrasi | `reports/PREREG_Q2_TWIN_PRIME_V3_2026-10-25.md` |
| Pra-registrasi SHA-256LF | `5c46e9e0b0a9d82fd58b451b1e83af65f42352fdde81bfeb1a9901d200cebf3d` |
| Modul | `msaf/twin_prime_v3.py` |
| Modul SHA-256LF | `55a4683324836054971ce4dc5b7e6f8a716e60bb04242f9306c1f325ce401322` |
| Guard | `msaf/tests/test_twin_prime_v3.py` |
| Guard SHA-256LF | `58cd11bdbaa7dbc83d0d8d23a62b40ec6b8fb9f8c51e066c60aed95c4a9cf60d` |
| Receipt | `reports/twin_prime_v3_2026-10-25.json` |
| Receipt SHA-256LF | `61e6731b012a90282ffecc29a9da070db8ee5247279ab45b812bea3c7245ab70` |
| Ukuran receipt | 1.715 byte |
| Skema | `msaf.twin_prime_v3.v1` |
| Mesin | Windows, Python 3.14.4, RAM 19,87 GB |
| Runtime run kedua | 83,47 detik |
| Determinisme | dua run penuh menghasilkan receipt byte-identik |

## 1. Pertanyaan and answer

Berapa banyak pasangan twin prime `(p, p + 2)` with `p <= 10^9`, and apakah
dua implementasi sieve independen menghasilkan daftar pasangan which identik
integer-per-integer on seluruh rentang?

Jawaban sensus:

| Besaran | Sieve A | Sieve B |
|---|---:|---:|
| `count` | **3.424.506** | **3.424.506** |
| `max_gap` | **4.770** | **4.770** |
| Pasangan pertama | `(3, 5)` | `(3, 5)` |
| Pasangan terakhir | `(999.999.191, 999.999.193)` | `(999.999.191, 999.999.193)` |
| Digest pasangan | `427f9211b736afbb6acdc98faec4ed97be9f85f20d5334381dacae12619ea1b8` | sama |
| Mismatch element-wise | 0 | 0 |

Ini adalah sensus finit. Hasilnya **bukan** bukti konjektur twin prime, bukan
klaim asimtotik, and no berlaku for `N > 10^9`.

## 2. Konfigurasi terkunci

| Parameter | Nilai |
|---|---|
| `N` | `1_000_000_000` |
| Batas bilangan prima basis | `31_623` |
| Blok sieve B | `2^24 = 16_777_216` |
| Aritmetika | integer Python eksak; tanpa float; tanpa numpy |
| Pasangan | `(p, p + 2)` with `p` prima and `p + 2` prima, `p <= N` |
| Checkpoint | `10^6`, `10^7`, `10^8`, `10^9` |
| Digest pasangan | SHA-256 atas record 16 byte big-endian: `p.to_bytes(8, "big") + (p + 2).to_bytes(8, "big")`, berurutan naik |
| Definisi `max_gap` | maksimum `p_{i+1} - p_i` atas pasangan berurutan, bukan selisih ujung pasangan |

Catatan aritmetika limit basis: `isqrt(1_000_000_002) = 31.622`, bukan
`31.623`. Pra-registrasi menulis `31.623`; nilai itu which dikunci and dipakai.
Karena `31.623 = 3 Ã— 10.541` komposit, daftar prima basis no berubah and
limit `31.623` adalah superset aman dari `31.622`. Perbedaan satu step ini
no memengaruhi C1â€“C4 or result sensus.

## 3. Dua implementasi independen

**Sieve A â€” Eratosthenes penuh.** `bytearray` for `0 .. N + 2`, tandai
kelipatan setiap prima sampai `isqrt(N + 2)`, lalu pindai hanya bilangan ganjil.
Untuk mempercepat ekstraksi, 1 MiB byte flag ganjil dikemas menjadi integer,
in-AND with versi tergeser satu posisi, lalu byte hasilnya dipindai with
`find`. Operasi ini eksak: setiap byte flag bernilai 0 or 1, sehingga AND
integer no dapat menghasilkan carry.

**Sieve B â€” segmented Eratosthenes.** Daftar prima basis sampai `31.623`
dihitung oleh fungsi sederhana terpisah. Setiap blok `[low, high]` berukuran
`2^24` membangun segmen `[low, high + 2]`, menandai kelipatan prima basis, and
memindai `p` ganjil in `[low, high]`. Blok berikutnya mulai in `high + 1`.
Karena segmen mencakup `high + 2`, pasangan which dimulai in ujung blok tetap
diputuskan in blok which sama; no ada pasangan which terlewat or terhitung
dua kali.

Keduanya menghasilkan pasangan dalam urutan naik. Perbandingan memakai
`zip_longest`, sehingga perbedaan panjang stream and perbedaan isi on posisi
mana pun terdeteksi. `count` saja no dipakai sebagai pengganti perbandingan
element-wise.

## 4. Checkpoint referensi

| `x` | Referensi `pi_2(x)` | Count A | Count B | Cocok |
|---:|---:|---:|---:|---|
| `10^6` | 8.169 | 8.169 | 8.169 | ya |
| `10^7` | 58.980 | 58.980 | 58.980 | ya |
| `10^8` | 440.312 | 440.312 | 440.312 | ya |
| `10^9` | 3.424.506 | 3.424.506 | 3.424.506 | ya |

Checkpoint `10^9` sama with count total on kedua sieve. Nilai referensi
adalah pemeriksaan tambahan; kesepakatan penuh A/B and digest tetap menjadi
kriteria utama.

## 5. Kriteria C1â€“C4

| Kriteria | Isi | Hasil |
|---|---|---|
| C1 | Dua sieve independen, aritmetika eksak, tanpa float/numpy/v2 in jalur sensus | **PASS** â€” AST guard menolak import numpy/v2 and pemakaian `float`; A memakai bytearray penuh, B memakai segmented sieve and basis prima terpisah |
| C2 | Kesepakatan penuh | **PASS** â€” count, max_gap, first, last, digest sama; 0 mismatch element-wise; panjang stream sama |
| C3 | Checkpoint referensi | **PASS** â€” keempat checkpoint cocok on kedua sieve; `10^9` sama with count total |
| C4 | Determinisme receipt | **PASS** â€” JSON kanonik, tanpa timestamp/runtime/path absolut; dua run penuh byte-identik with SHA-256 `61e6731bâ€¦5ab70` |

Receipt juga mencatat `module_sha256lf` and `prereg_sha256lf`. Hash
pra-registrasi in receipt sama with hash file terkunci in atas.

## 6. Determinisme dua run

Dua eksekusi penuh `python msaf/twin_prime_v3.py` berturut-turut menghasilkan
output ringkas which sama and receipt with SHA-256 which sama:

```text
61e6731b012a90282ffecc29a9da070db8ee5247279ab45b812bea3c7245ab70
```

Run kedua memerlukan 83,47 detik. Peak memori teoretis didominasi sieve A:
bytearray penuh sekitar 1 GB ditambah salinan flag ganjil sekitar 0,5 GB;
sieve B hanya menyimpan satu blok sekitar 16,7 MB. Tidak ada timestamp or
nama mesin in receipt, sehingga byte receipt no bergantung on waktu.

## 7. Perintah verifikasi

```text
python msaf/twin_prime_v3.py
python -m pytest msaf/tests/test_twin_prime_v3.py -q
python -m pytest msaf/tests/test_twin_prime_v2.py msaf/tests/test_fence_registry.py -q
python audit_quantum/freeze.py --verify
```

Hasil guard on 2026-10-25:

- `msaf/tests/test_twin_prime_v3.py`: 8 passed.
- Gabungan v3 + v2 + fence registry: 12 passed.
- `freeze.py --verify`: `verify OK: 14 pins`.

## 8. Batas klaim

- Hanya sensus finit hingga `N = 10^9`.
- Bukan bukti konjektur twin prime; no ada klaim asimtotik, distribusi,
  kerapatan, or perilaku for `N > 10^9`.
- Tidak ada klaim RH/GRH, faktorisasi, RSA/ECC, Anderson, fisika, or
  prioritas.
- `A-2026-0045` (v2, `N = 10^7`) tetap menjadi klaim certified which terpisah;
  v3 no menggantikannya. `A-2026-0029` (`N = 100.000`) tetap
  `INCONCLUSIVE`.
- Angka `count` and `max_gap` adalah result dua sieve repo ini; checkpoint
  referensi adalah data eksternal which dipakai sebagai pembanding, bukan
  sertifikat baru.


