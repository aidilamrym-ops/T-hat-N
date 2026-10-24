# T2-r5 — Perketat R_B (1e-30) + matriks K6 M1-M10: FAILED (dua baris non-diskriminatif)

**Status formal: FAILED.**
Base K1-K5 (sertifikat r3) lulus penuh (byte-reproduksi), K6 M1-M10 mengandung dua baris non-diskriminatif (M3, M8) — verdict kampanye `all_pass=false, summary=FAILED`.
Registry **tidak dibuat**: `A-2026-0044` tetap kosong; klaim bersertifikat tetap `A-2026-0043` (r4), tidak ditarik.

| Item | Nilai |
|---|---|
| Prereg | `reports/PREREG_FIGURE_EIGHT_R5_2026-10-23.md` |
| Prereg SHA-256LF | `6c845bbbdbc8724d9bb07b7798927bacee9bebab5714a69328ccc3d6bc1edd03` |
| Base modul r3 | `msaf/figure_eight_r3.py` |
| Base modul SHA-256LF | `8eddc2bb17647d452e15325397e852e224e1af028f055fa4fe41de94af939ec6` |
| Base receipt r3 | `reports/figure_eight_r3_2026-10-23.json` |
| Base receipt SHA-256LF | `6b0b71e91c9b38a2e8b43e8b2da12dbf2ce273321ffe2c4376e09bbbbdf829c9` |
| Modul r5 | `msaf/figure_eight_r5.py` |
| Modul r5 SHA-256LF | `246857d4742067838814ec1da869552d0263ba8cebf50d9e13ed305e5bc0a62d` |
| Receipt r5 | `reports/figure_eight_r5_2026-10-23.json` (5314 byte) |
| Receipt r5 SHA-256LF | `1932be979a9ee91066fd169c83e8eeba6fcb3b9d0a5f8dd988ad881fad46b0cf` |
| Verdict | **FAILED** (base K1-K5 ALL PASS; K6 M1-M10: 8 baris diskriminatif-lulus, 2 non-diskriminatif) |
| Registry | **null — `A-2026-0044` TIDAK dibuat** |

Semua anggota tabel di atas diambil/direkomputasi mesin:
`t2n_repokeeper.receipt_verify` memverifikasi receipt ini **consistent
under applied checks** (2 hash di-record direkomputasi ulang: module r3
dan receipt r3; hash prereg cocok dengan `prereg_sha256lf` di receipt;
disclosed sebagai unpaired-adjacent, direkomputasi terpisah di atas).

---

## 0. Ringkasan eksekutif

- T2-r5 dibuka persis mengikuti protokol: **prereg dikunci sebelum
  kode** (`PREREG_FIGURE_EIGHT_R5_2026-10-23.md`, SHA-256LF
  `6c845bbb...`), lalu implementasi kampanye (tabel di atas
  merekap keduanya).
- **Base K1-K5: PASS** — byte-reproduksi sertifikat r3 (nilai sama
  dengan base r4-r3, karena base memang receipt r3 yang sama).
- **K6 M1-M10: FAILED** — dua baris tidak membedakan:
  - **M3** (`C = 1/3`): ekspektasi prereg "Gauge `I_xy != 0`, K1
    should fail"; actual `K1_passed=true` → mutasi tidak memindahkan
    lampu gerbang → **non-diskriminatif** (`passed=false`).
  - **M8** (`GAUSS_COND_MAX=10^6`): ekspektasi "K4 FAILED dengan
    `cond_ok=False`"; actual kondisi terukur ≈ `29649.6376...`
    tetap jauh **di bawah** cap hasil mutasi → `cond_ok=true`,
    K4 tetap lulus → **non-diskriminatif** (`passed=false`).
    Pelajaran teknis: mutasi mem-perlebar cap tidak dapat memaksa K4
    gagal; untuk diskriminatif harus **mengetatkan** di bawah nilai
    terukur (mis. cap di bawah ≈2.96e4), bukan melonggarkan ke 1e6.
- **M6** (`GAUSS_DET_MIN=10^6`) & **M7** (`CHOREO_TOL=10^-50`
  → `K5_defect`): actual `INCONCLUSIVE` oleh aturan modul;
  `passed=true` (tidak ikut memblok verdict) — dicatat apa adanya.
- M1, M2, M4, M5, M9, M10: diskriminatif dan lulus seperti dituju.
- **Secara matematis ini BUKAN kelonggaran**: kegagalan r5 adalah
  kegagalan instrumen pengukuran (matriks mutasi) dalam menekan
  lampu gerbang — bukan bukti struktur figure-eight rusak, dan juga
  bukan penurunan-nilai sertifikat r4.

## 1. Jalur bukti r5 (apa yang terjadi)

1. `PREREG` r5 dikunci (`6c845bbb...`) di commit prereg, **sebelum**
   kode kampanye (`bb3fe56`).
2. Kampanye diimplementasi di `msaf/figure_eight_r5.py`
   (`246857d4...`), guard di `msaf/tests/test_figure_eight_r5.py`.
3. Rerun jujur (modul in-memory, run fase hari ini) menghasilkan
   receipt r5 (`1932be97...` 5314 byte).
4. `t2n_repokeeper.receipt_verify` memverifikasi receipt
   (0 problems; 2 hash dicocokkan; korespondensi prereg OK).
5. Receipt r5 TIDAK punya field waktu → dua pass kampanye penuh
   (pytest double-call: `test_campaign` + `test_registry_entry`)
   harus byte-identik. Pass-2 kini SELESAI (14425.95 dtk):
   receipt kerja tetap byte-identik dengan yang di-commit
   (`1932be97...`, `git diff` kosong) — reproduksi dipastikan;
   semua angka terekam sebagai event `r5_pass2_bytecheck` pada
   ledger `t2n_ledger_v1.jsonl`.

## 2. Tabel baris K6 (machine-extracted dari receipt)

| Baris | Mutasi | Epektasi prereg | Actual | Status baris |
|---|---|---|---|---|
| M1 | `REMAINDER_FACTOR=10^100` | K2 FAIL di Picard | K2 abort step 2 | lulus |
| M2 | `T0 -> T0 + 1` | K3/K5 FAIL | keduanya FAIL | lulus |
| M3 | `C = 1/3` | K1 FAIL (`I_xy != 0`) | **K1 tetap PASS** | **non-diskriminatif** |
| M4 | `TUBE_CAP=10^-50` | K2 FAIL `widths_ok=False` | keduanya cocok | lulus |
| M5 | `KAPPA_MAX=10^-20` | K3 FAIL `kappa_ok=False` | cocok | lulus |
| M6 | `GAUSS_DET_MIN=10^6` | K4 FAIL `det_ok=False` | `INCONCLUSIVE` (modul) | lulus (actual INKONklusif) |
| M7 | `CHOREO_TOL=10^-50` | K5 FAIL defect>cap | `INCONCLUSIVE` (modul) | lulus (actual INKONklusif) |
| M8 | `GAUSS_COND_MAX=10^6` | K4 FAIL `cond_ok=False` | **cond ≈29649.6 tetap di bawah cap** | **non-diskriminatif** |
| M9 | 1 byte payload flipped | SHA sebelum≠sesudah | berbeda ✓ | lulus |
| M10 | inject `1.5`/`float(x)` | AST hits; copy terkena | hits ✓ + clean ✓ | lulus |

## 3. Batas & petunjuk

- Tidak ada penarikan r4 (`A-2026-0043` tetap klaim figure-eight
  bersertifikat).
- **r6 opsional**: jika dilanjutkan, wajib prereg **sebelum kode**
  dengan dua perbaikan pelajaran di atas (mutasi M3 yang aljabar
  memindahkan `I_xy != 0`; M8 yang mengetatkan cap di bawah nilai
  terukur), tanpa menyentuh r3/r4/r5 secara retroaktif.
- Untuk menutup kueri pasar "kosong 0044": `A-2026-0044` menggantung
  sampai berita r6 (atau trek lain) mengklaimnya dengan protokol penuh.

## 4. Konteks infra saat jendela r5 (tidak mengubah matematika)

- `msaf/hodge/gauss_exact.py` (IndentationError diberikan di
  `4e282c9`) + realign guard + kasus p=7 baru — commit `4af845a`.
- Suite T2N MCP: `9649c10` (F0+F1, filing anti-pemalsuan berikut).
- Insiden `2026-10-24 15:19` (receipt palsu `ALL PASS` klaim 0044 +
  modul r5 diubah) dideteksi dan direstore; bukti forensik di
  temp khusus; suite anti-forgery (`t2n_repokeeper.receipt_verify`
  + ledger berantai-hash) lahir dari insiden ini.
