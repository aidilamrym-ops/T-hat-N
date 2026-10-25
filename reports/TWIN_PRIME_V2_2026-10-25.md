# Sensus Twin Prime Q2 v2 — N = 10^7

**Status: ALL PASS.** Dua sieve independen sepakat integer-per-integer pada
`N = 10_000_000`. Ini fragmen finit baru; `A-2026-0029` (N=100.000)
tetap `INCONCLUSIVE` dan tidak diubah.

| Item | Nilai |
|---|---|
| Prereg | `reports/PREREG_Q2_TWIN_PRIME_V2_2026-10-25.md` |
| Prereg SHA-256LF | `45ad2266516c4b6429ead77151ac160f043a1fb255a576f1e0c4c94f60201645` |
| Modul | `msaf/twin_prime_v2.py` |
| Modul SHA-256LF | `24c24a0b88f113ebc5ec2e9d356a82a96cc207200838e7979842ac9afa87017d` |
| Guard | `msaf/tests/test_twin_prime_v2.py` |
| Guard SHA-256LF | `da31890563a24f61b4ddd3b5b4da3ceffb08ce1d485bc6b94012c24d00ff247c` |
| Receipt | `reports/twin_prime_v2_2026-10-25.json` |
| Receipt SHA-256LF | `6c613dd573867e2d54cf7ed162413cb7f1b5e40b8be2724797681dddb72094d4` |
| Registry | `A-2026-0045` |

## 1. Hasil sensus

| Besaran | Nilai |
|---|---|
| `N` | 10.000.000 |
| Jumlah pasangan | **58.980** |
| `count_A` = `count_B` | 58.980 |
| `max_gap_A` = `max_gap_B` | 1.722 |
| Pasangan pertama | (3, 5) |
| Pasangan terakhir | (9.999.971, 9.999.973) |
| `pairs_A == pairs_B` | ya |
| Verdict | **ALL PASS** |

Nilai `58.980` konsisten dengan hitungan referensi `pi_2(10^7) = 58.980`.
Ini sensus eksak hingga `10^7`; bukan bukti konjektur twin prime dan bukan
klaim asimtotik.

## 2. Dua implementasi independen

- **Sieve A** — Eratosthenes bytearray penuh, scan `p` dan `p+2`.
- **Sieve B** — segmented sieve dengan base prime sampai `isqrt(N+2)`,
  blok `2^20`, lalu himpunan prima dan scan pasangan.

Keduanya memakai integer Python eksak; tidak ada float di jalur sensus.
Receipt tidak memuat runtime atau timestamp, sehingga dua run menghasilkan
byte yang sama.

## 3. Kriteria

- **C1** `count_A == count_B` — PASS.
- **C2** `pairs_A == pairs_B` element-wise — PASS.
- **C3** `max_gap_A == max_gap_B` — PASS.
- **C4** receipt kanonik deterministik — PASS. Dua run berturut-turut
  menghasilkan SHA-256 receipt yang sama:
  `6c613dd573867e2d54cf7ed162413cb7f1b5e40b8be2724797681dddb72094d4`.

## 4. Batas klaim

- Hanya sensus hingga `10^7`; tidak ada klaim tentang `N > 10^7`.
- Tidak ada klaim konjektur twin prime, distribusi asimtotik, RH/GRH,
  faktorisasi, RSA/ECC, Anderson, atau fisika.
- Registry baru `A-2026-0045` hanya mencatat fragmen finit ini.

## 5. Perintah verifikasi

```text
python -m pytest msaf/tests/test_twin_prime_v2.py -q
python -m pytest msaf/tests/test_fence_registry.py -q
python audit_quantum/freeze.py --verify
```
