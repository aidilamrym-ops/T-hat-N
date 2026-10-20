# Pra-registrasi: BSD pilot Q1 — 2-descent + simbol modular untuk 5 kurva rank-0 — 2026-10-21

**Status:** scope DIKUNCI untuk paket Q1 BSD; implementasi dan eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket Q1 BSD. Hash `sha256LF` berkas ini
dicatat di receipt dan laporan.

**Paket:** Q1 BSD pilot dari
[`reports/DAFTAR_MASALAH_KERJA.md`](DAFTAR_MASALAH_KERJA.md),
yaitu verifikasi BSD untuk 5 kurva elliptik rank-0 (11a1, 14a1, 15a1, 17a1, 19a1)
melalui 2-descent eksak + simbol modular.

**Berkas target:** `msaf/bsd_descent.py` (baru), guard
`msaf/tests/test_bsd_descent.py` (baru), laporan
`reports/BSD_PILOT_Q1_2026-10-21.md`, receipt
`reports/bsd_pilot_2026-10-21.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (untuk aritmetika eksak),
modul `msaf.hodge` (sudah tersegel), modul `msaf.gw_char_block` (sudah tersegel).

**Registry yang direncanakan:** `A-2026-0028`, hanya bila verdict inti
`ALL PASS` dan integritas PASS.

**Tidak mengubah:** V1–V6 (`A-2026-0015`–`A-2026-0021`),
`A-2026-0022`–`A-2026-0027`, `ci.yml` (`A-2026-0016`), workflow spec,
`lean/lakefile.toml`, freeze pins, seluruh laporan/artefak beku.

## 1. Maksud dan batas

Paket ini memverifikasi formula Birch–Swinnerton-Dyer untuk 5 kurva
elliptik rank-0 konduktor kecil melalui:

1. **2-descent eksak** — menghitung 2-Selmer group via aritmetika integer
   eksak (tanpa float), memverifikasi rank = 0 (Selmer rank = 0).
2. **Simbol modular** — menghitung L(E,1)/Ω_E sebagai bilangan rasional
   eksak via simbol modular (Manin symbols / modular symbols).
3. **Verifikasi identitas BSD** — memverifikasi
   L(E,1)/Ω = |Ш| · (∏ c_p) · 2^{ω(N)-1} / |E(Q)_tors|^2
   dengan aritmetika eksak (Fraction).

5 kurva pilot (semua rank 0, konduktor kecil):
- 11a1: y² + y = x³ - x² - 10x - 20 (conductor 11)
- 14a1: y² + xy + y = x³ + 4x - 6 (conductor 14)
- 15a1: y² + xy + y = x³ + x² - 10x - 10 (conductor 15)
- 17a1: y² + xy + y = x³ - x² - x - 14 (conductor 17)
- 19a1: y² + y = x³ + x² - 9x - 15 (conductor 19)

Paket ini **bukan**:
- klaim BSD untuk kurva secara umum (hanya 5 kurva pilot spesifik).
- klaim tentang rank > 0 atau Ш tidak trivial.
- implementasi 2-descent umum untuk kurva sembarang (hanya 5 kurva pilot).
- klaim RH, GRH, faktorisasi, RSA/ECC, Anderson, atau fisika.

## 2. Definisi yang dikunci

**2-descent eksak (Selmer group):**
- 2-Selmer group dihitung via homogeneous spaces eksak.
- Rank = 0 dibuktikan melalui Selmer rank = 0.
- Semua operasi integer eksak (Fraction, integer Python).

**Simbol modular (Modular symbols):**
- L(E,1)/Ω dihitung via simbol modular (Manin symbols).
- Nilai L(E,1)/Ω_E sebagai Fraction eksak (tanpa float).
- Dibandingkan dengan nilai tabel Cremona/LMFDB.

**Formula BSD (rank 0):**
```
L(E,1)/Ω = |Ш| · (∏ c_p) · 2^{ω(N)-1} / |E(Q)_tors|²
```
- ω(N) = jumlah faktor prima berbeda konduktor N
- c_p = bilangan Tamagawa
- |E(Q)_tors| = orde torsi
- |Ш| = orde Tate-Shafarevich group (di sini = 1 untuk 5 kurva ini)
- Regulator = 1 (karena rank = 0)

## 3. Instance dan konfigurasi yang dikunci

| Kurva | Conductor | Torsi | c_p | L(E,1)/Ω (diharapkan) |
|-------|-----------|-------|-----|----------------------|
| 11a1 | 11 | 5 | 5 | 1/5 |
| 14a1 | 14 | 6 | 6 | 1/3 |
| 15a1 | 15 | 4 | 4 | 1/4 |
| 17a1 | 17 | 4 | 4 | 1/4 |
| 19a1 | 19 | 3 | 3 | 1/3 |

Semua kurva: rank = 0, Ш = 1 (diketahui).

Tidak ada instance, kurva, atau parameter tambahan setelah hasil terlihat.

## 4. Pemeriksaan integritas (C1–C4)

**C1: 2-descent rank-zero**
- Selmer rank = 0 untuk semua 5 kurva.
- 2-descent via homogeneous spaces eksak, rank = 0 terbukti.

**C2: Simbol modular eksak**
- L(E,1)/Ω sebagai Fraction eksak untuk setiap kurva.
- Cocok dengan nilai tabel Cremona/LMFDB.

**C3: Identitas BSD**
- LHS = L(E,1)/Ω (dari simbol modular)
- RHS = |Ш| · ∏c_p · 2^{ω(N)-1} / |E(Q)_tors|²
- LHS = RHS untuk semua 5 kurva (Fraction equality eksak).

**C4: Determinisme & receipt**
- Receipt deterministik: dua run berturut-turut menghasilkan payload
  kanonik identik, hash sha256 cocok dengan berkas di disk.
- Receipt berisi: schema, prereg_sha256, config, results, verdict.

## 5. Verdict

- **ALL PASS**: C1, C2, C3, C4 PASS untuk semua 5 kurva.
- **PARTIAL**: tidak ada (paket ini all-or-nothing).
- **FAILED**: salah satu C1–C4 gagal untuk kurva manapun.
- **INCONCLUSIVE**: tool error, dependensi tidak tersedia, atau hash mismatch.

Registry `A-2026-0028` hanya bila verdict `ALL PASS` dan integritas PASS.

## 6. Falsifier

Paket ini falsified bila:
- Selmer rank ≠ 0 untuk salah satu kurva pilot.
- L(E,1)/Ω tidak cocok dengan nilai tabel Cremona.
- LHS ≠ RHS dalam identitas BSD untuk kurva manapun.
- Receipt tidak deterministik atau hash mismatch.
- Float/float64 leakage terdeteksi di jalur komputasi.

Falsifier dicatat sebagai `FAILED`; tidak ada perubahan parameter setelah hasil.

## 7. Artefak dan urutan eksekusi

1. Tulis dan hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/bsd_descent.py` dengan 2-descent + simbol modular.
3. Guard `msaf/tests/test_bsd_descent.py`: uji 2-descent, simbol modular,
   identitas BSD, determinisme receipt, scope flag.
4. Jalankan kampanye penuh sekali; hasilkan receipt.
5. Tulis laporan `reports/BSD_PILOT_Q1_2026-10-21.md` dengan angka
   verbatim, verdict, runtime, dan hash.
6. Bila verdict `ALL PASS` dan integritas PASS: registry `A-2026-0028`,
   HANDOFF §2.0av, sertifikat sha256LF.
7. Suite penuh dan `freeze.py --verify`; commit/push hanya bila diminta.

## 8. Batas eksplisit

- Hanya 5 kurva pilot (11a1, 14a1, 15a1, 17a1, 19a1).
- Hanya rank 0 (Selmer rank = 0).
- Hanya BSD formula rank 0 (regulator = 1, Ш = 1).
- Tidak ada klaim tentang kurva rank > 0, Ш > 1, atau kurva non-modular.
- Tidak ada klaim RH, GRH, faktorisasi, RSA/ECC, Anderson, atau fisika.
- Tidak ada kampanye tersegel yang dijalankan ulang.
- `ALL PASS` berarti **5 kurva pilot spesifik lolos C1–C4**, bukan
  bukti BSD secara umum.