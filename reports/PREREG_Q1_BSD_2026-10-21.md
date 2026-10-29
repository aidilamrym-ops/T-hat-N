# Pra-registrasi: BSD pilot Q1 â€” 2-descent + simbol modular for 5 kurva rank-0 â€” 2026-10-21

**Status:** scope DIKUNCI for paket Q1 BSD; implementasi and eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket Q1 BSD. Hash `sha256LF` file ini
dicatat in receipt and report.

**Paket:** Q1 BSD pilot dari
[`reports/DAFTAR_MASALAH_KERJA.md`](DAFTAR_MASALAH_KERJA.md),
yaitu verifikasi BSD for 5 kurva elliptik rank-0 (11a1, 14a1, 15a1, 17a1, 19a1)
melalui 2-descent eksak + simbol modular.

**Berkas target:** `msaf/bsd_descent.py` (baru), guard
`msaf/tests/test_bsd_descent.py` (baru), report
`reports/BSD_PILOT_Q1_2026-10-21.md`, receipt
`reports/bsd_pilot_2026-10-21.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (for aritmetika eksak),
modul `msaf.hodge` (already tersegel), modul `msaf.gw_char_block` (already tersegel).

**Registry which direncanakan:** `A-2026-0028`, hanya bila verdict inti
`ALL PASS` and integritas PASS.

**Tidak mengubah:** V1â€“V6 (`A-2026-0015`â€“`A-2026-0021`),
`A-2026-0022`â€“`A-2026-0027`, `ci.yml` (`A-2026-0016`), workflow spec,
`lean/lakefile.toml`, freeze pins, seluruh report/artefak beku.

## 1. Maksud and limit

Paket ini verifying formula Birchâ€“Swinnerton-Dyer for 5 kurva
elliptik rank-0 konduktor kecil melalui:

1. **2-descent eksak** â€” menghitung 2-Selmer group via aritmetika integer
   eksak (tanpa float), verifying rank = 0 (Selmer rank = 0).
2. **Simbol modular** â€” menghitung L(E,1)/Î©_E sebagai bilangan rasional
   eksak via simbol modular (Manin symbols / modular symbols).
3. **Verifikasi identitas BSD** â€” verifying
   L(E,1)/Î© = |Ð¨| Â· (âˆ c_p) Â· 2^{Ï‰(N)-1} / |E(Q)_tors|^2
   with aritmetika eksak (Fraction).

5 kurva pilot (semua rank 0, konduktor kecil):
- 11a1: yÂ² + y = xÂ³ - xÂ² - 10x - 20 (conductor 11)
- 14a1: yÂ² + xy + y = xÂ³ + 4x - 6 (conductor 14)
- 15a1: yÂ² + xy + y = xÂ³ + xÂ² - 10x - 10 (conductor 15)
- 17a1: yÂ² + xy + y = xÂ³ - xÂ² - x - 14 (conductor 17)
- 19a1: yÂ² + y = xÂ³ + xÂ² - 9x - 15 (conductor 19)

Paket ini **bukan**:
- klaim BSD for kurva secara umum (hanya 5 kurva pilot spesifik).
- klaim tentang rank > 0 or Ð¨ no trivial.
- implementasi 2-descent umum for kurva sembarang (hanya 5 kurva pilot).
- klaim RH, GRH, faktorisasi, RSA/ECC, Anderson, or fisika.

## 2. Definisi which dikunci

**2-descent eksak (Selmer group):**
- 2-Selmer group dihitung via homogeneous spaces eksak.
- Rank = 0 dibuktikan melalui Selmer rank = 0.
- Semua operasi integer eksak (Fraction, integer Python).

**Simbol modular (Modular symbols):**
- L(E,1)/Î© dihitung via simbol modular (Manin symbols).
- Nilai L(E,1)/Î©_E sebagai Fraction eksak (tanpa float).
- Dibandingkan with nilai tabel Cremona/LMFDB.

**Formula BSD (rank 0):**
```
L(E,1)/Î© = |Ð¨| Â· (âˆ c_p) Â· 2^{Ï‰(N)-1} / |E(Q)_tors|Â²
```
- Ï‰(N) = jumlah faktor prima berbeda konduktor N
- c_p = bilangan Tamagawa
- |E(Q)_tors| = orde torsi
- |Ð¨| = orde Tate-Shafarevich group (in sini = 1 for 5 kurva ini)
- Regulator = 1 (karena rank = 0)

## 3. Instance and konfigurasi which dikunci

| Kurva | Conductor | Torsi | c_p | L(E,1)/Î© (diharapkan) |
|-------|-----------|-------|-----|----------------------|
| 11a1 | 11 | 5 | 5 | 1/5 |
| 14a1 | 14 | 6 | 6 | 1/3 |
| 15a1 | 15 | 4 | 4 | 1/4 |
| 17a1 | 17 | 4 | 4 | 1/4 |
| 19a1 | 19 | 3 | 3 | 1/3 |

Semua kurva: rank = 0, Ð¨ = 1 (diketahui).

Tidak ada instance, kurva, or parameter tambahan setelah result terlihat.

## 4. Pemeriksaan integritas (C1â€“C4)

**C1: 2-descent rank-zero**
- Selmer rank = 0 for semua 5 kurva.
- 2-descent via homogeneous spaces eksak, rank = 0 terbukti.

**C2: Simbol modular eksak**
- L(E,1)/Î© sebagai Fraction eksak for setiap kurva.
- Cocok with nilai tabel Cremona/LMFDB.

**C3: Identitas BSD**
- LHS = L(E,1)/Î© (dari simbol modular)
- RHS = |Ð¨| Â· âˆc_p Â· 2^{Ï‰(N)-1} / |E(Q)_tors|Â²
- LHS = RHS for semua 5 kurva (Fraction equality eksak).

**C4: Determinisme & receipt**
- Receipt deterministik: dua run berturut-turut menghasilkan payload
  kanonik identik, hash sha256 cocok with file in disk.
- Receipt berisi: schema, prereg_sha256, config, results, verdict.

## 5. Verdict

- **ALL PASS**: C1, C2, C3, C4 PASS for semua 5 kurva.
- **PARTIAL**: no ada (paket ini all-or-nothing).
- **FAILED**: salah satu C1â€“C4 gagal for kurva manapun.
- **INCONCLUSIVE**: tool error, dependensi no tersedia, or hash mismatch.

Registry `A-2026-0028` hanya bila verdict `ALL PASS` and integritas PASS.

## 6. Falsifier

Paket ini falsified bila:
- Selmer rank â‰  0 for salah satu kurva pilot.
- L(E,1)/Î© no cocok with nilai tabel Cremona.
- LHS â‰  RHS dalam identitas BSD for kurva manapun.
- Receipt no deterministik or hash mismatch.
- Float/float64 leakage terdeteksi in jalur komputasi.

Falsifier dicatat sebagai `FAILED`; no ada perubahan parameter setelah result.

## 7. Artefak and urutan eksekusi

1. Tulis and hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/bsd_descent.py` with 2-descent + simbol modular.
3. Guard `msaf/tests/test_bsd_descent.py`: uji 2-descent, simbol modular,
   identitas BSD, determinisme receipt, scope flag.
4. Jalankan kampanye penuh sekali; hasilkan receipt.
5. Tulis report `reports/BSD_PILOT_Q1_2026-10-21.md` with angka
   verbatim, verdict, runtime, and hash.
6. Bila verdict `ALL PASS` and integritas PASS: registry `A-2026-0028`,
   HANDOFF Â§2.0av, sertifikat sha256LF.
7. Suite penuh and `freeze.py --verify`; commit/push hanya bila diminta.

## 8. Batas eksplisit

- Hanya 5 kurva pilot (11a1, 14a1, 15a1, 17a1, 19a1).
- Hanya rank 0 (Selmer rank = 0).
- Hanya BSD formula rank 0 (regulator = 1, Ð¨ = 1).
- Tidak ada klaim tentang kurva rank > 0, Ð¨ > 1, or kurva non-modular.
- Tidak ada klaim RH, GRH, faktorisasi, RSA/ECC, Anderson, or fisika.
- Tidak ada kampanye tersegel which dijalankan ulang.
- `ALL PASS` berarti **5 kurva pilot spesifik lolos C1â€“C4**, bukan
  bukti BSD secara umum.

