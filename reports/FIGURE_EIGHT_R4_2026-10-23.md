# T2-r4 - Re-sertifikasi figure-eight reduced 8x8 with K6 diskriminatif

**Status formal: ALL PASS.**  
K1-K5 lulus penuh, K6 (M1-M9) seluruhnya diskriminatif and lulus.
Registry **`A-2026-0043`** created.

| Item | Nilai |
|---|---|
| Prereg | `reports/PREREG_FIGURE_EIGHT_R4_2026-10-23.md` |
| Prereg SHA-256LF | `14cf5c9fbaff6b2e6e67617fe724e1fc01ec18fe2e4323c51e5531256bcb21c5` |
| Base modul r3 | `msaf/figure_eight_r3.py` |
| Base modul SHA-256LF | `8eddc2bb17647d452e15325397e852e224e1af028f055fa4fe41de94af939ec6` |
| Base receipt r3 | `reports/figure_eight_r3_2026-10-23.json` |
| Base receipt SHA-256LF | `6b0b71e91c9b38a2e8b43e8b2da12dbf2ce273321ffe2c4376e09bbbbdf829c9` |
| Modul r4 | `msaf/figure_eight_r4.py` |
| Receipt r4 | `reports/figure_eight_r4_2026-10-23.json` |
| Receipt r4 SHA-256LF | `8b6088c27f79129f8d28109a75efe2f888406b9d7e6d884c9cf7ab95cf611086` |
| T1 SHA-256LF | `c1d9b5d60036a5f0772f7e3f1b8c78969efaa7146a713c762531ddce346251b9` |
| T1b SHA-256LF | `42d196a51c5ae45e3b87b8c1e36319abfeb93df776b3c2317e812f7c2c0b5b97` |
| Verdict | **ALL PASS** (K1-K5 + K6 M1-M9) |
| Registry | **`A-2026-0043`** |

---

## 0. Ringkasan eksekutif

- T2-r3 ditutup **INCONCLUSIVE** karena K6/M5 (`SWEEP_SIGNED=False`) **non-diskriminatif** (tetap ALL PASS). Tidak ada registry `A-2026-0042`.
- T2-r4 memakai sertifikat matematis r3 which already in-commit sebagai base, lalu mengganti K6 with matriks M1-M9 which benar-benar diskriminatif.
- Dua kampanye r4 penuh **identik byte-per-byte** (SHA-256LF `8b6088c...`).
- Guard r4 verifying base receipt, K1-K5, and semua 9 baris K6.
- Registry `A-2026-0043` ditambahkan ke `FENCE_REGISTRY.md`.

---

## 1. Garis keturunan and base which dipakai

| Item | Nilai |
|---|---|
| Prereg r3 | `reports/PREREG_FIGURE_EIGHT_R3_2026-10-23.md` |
| Prereg r3 commit | `38d19e8` |
| Prereg r3 SHA-256LF | `23ab24254f13539dddf1bd3cccd87dbbcef01b3398dab1ccf5fb2d75099a6b93` |
| Base receipt r3 SHA-256LF | `6b0b71e91c9b38a2e8b43e8b2da12dbf2ce273321ffe2c4376e09bbbbdf829c9` |
| Base verdict r3 | INCONCLUSIVE (K1-K5 PASS, K6/M5 non-diskriminatif) |
| Registry r3 | no ada |

R4 **no menulis ulang** persamaan, gauge, konstanta, or kampanye K1-K5. R4 mengimpor base r3, menjalankan ulang kampanye base, verifying hash receipt base, lalu menjalankan K6 baru.

---

## 2. Lingkup and limit klaim

Target tetap orbit periodik figure-eight on periode eksak `T0`, in dalam box lokal `B`, modulo gauge:

```
q1y = 1/5,
I_xy = q1x q1y + q2x q2y + q3x q3y = 0.
```

R4 mempromosikan keberadaan and **keunikan lokal** in dalam `B` karena base K1-K5 and seluruh K6 lulus. Tidak ada klaim global, stabilitas, spektrum, chaos, ergodisitas, KAM, PDE, RH, fisika, prioritas, Lean/Coq, or penyelesaian umum three-body.

---

## 3. Matematika which dikunci

Semua konstanta and metode mengikuti prereg r3 and kode base r3. R4 no mengubah:
- `T0 = 632600304 / 10^8`, `H_STEPS = 1536`, `BLOCK_STEPS = 96`;
- gauge `q1y = 1/5`, `I_xy = 0`;
- `R_B = 1e-18`, `K_MARGIN = 9/10`, `KAPPA_MAX = 1/2`;
- `POINT_TARGET = 1e-24`, `HESS_BOX = 1e-12`;
- `QUAD_SAFETY = 4`, `QUAD_CAP = 1e-18`, `DR_CAP = 1e-18`;
- `TUBE_CAP = 1e-10`, `GAUSS_DET_MIN = 1e-6`, `GAUSS_COND_MAX = 1e6`, `CHOREO_TOL = 1e-6`;
- limit Hessian path-box, `QUAD_STEP`, `DR_MAX`, Krawczyk, deskriptor koreografi.

Base r3 already memakai koreksi soundness path-box (`_step_with_box` + `_local_bounds`).

---

## 4. Kode, receipt, and guard r4

File which created:
- `msaf/figure_eight_r4.py` â€” wrapper kampanye base + runner K6;
- `msaf/tests/test_figure_eight_r4.py` â€” guard K6;
- `reports/figure_eight_r4_2026-10-23.json` â€” receipt r4;
- `reports/FIGURE_EIGHT_R4_2026-10-23.md` â€” report ini.

Receipt r4 memuat:
- `schema = "msaf.figure_eight_r4.v1"`;
- hash prereg r4, hash base module r3, hash base receipt r3;
- status base K1-K5 and hash kampanye base;
- setiap baris K6: nama mutasi, parameter, gate which diharapkan, nilai aktual, `passed`;
- `all_pass = base_k1_k5_pass and all(k6_rows.passed)`;
- `verdict = "ALL PASS"` hanya bila `all_pass`; selain itu `FAILED`;
- `registry = "A-2026-0043"` hanya bila `all_pass`; selain itu `null`.

Dua kampanye penuh r4 identik byte â†’ receipt final.

---

## 5. K6 baru - matriks mutasi diskriminatif (result aktual)

| Mutasi | Parameter | Gate which harus gagal | Hasil aktual | Passed |
|---|---|---|---|---|
| M1 | `REMAINDER_FACTOR=10^70` | K2 abort step 2 (Picard) | K2 FAILED, error memuat "aborted at step 2" and "Picard enclosure failed" | âœ… |
| M2 | `T0 -> T0 + 1/10` | K3 FAILED + Krawczyk; K5 FAILED | K3 FAILED, Krawczyk present, K5 FAILED | âœ… |
| M3 | 1 byte receipt diubah | SHA-256 berubah | SHA sebelum â‰  SHA sesudah | âœ… |
| M4 | injeksi `1.5` / `float(x)` | AST scan hit | AST hit for literal and call; source asli bersih | âœ… |
| M5 | `TUBE_CAP=10^-30` | K2 `widths_ok=False` | K2 FAILED, `widths_ok=False` | âœ… |
| M6 | `KAPPA_MAX=10^-12` | K3 `kappa_ok=False` | K3 FAILED, `kappa_ok=False` | âœ… |
| M7 | `GAUSS_DET_MIN=10^3` | K4 `det_ok=False` | K4 FAILED, `det_ok=False` | âœ… |
| M8 | `CHOREO_TOL=10^-30` | K5 FAILED | K5 FAILED | âœ… |
| M9 | `GAUSS_COND_MAX=10^3` | K4 `cond_ok=False` | K4 FAILED, `cond_ok=False` | âœ… |

**Semua 9 baris K6 `passed: true`.**  
K6 `all_pass: true` â†’ r4 `all_pass: true` â†’ `summary: "ALL PASS"` â†’ `registry: "A-2026-0043"`.

---

## 6. Hasil base K1-K5 (diambil dari receipt r3 which already tersegel)

| Besaran | Nilai |
|---|---|
| `|G(xh)|_inf` | `4.222845715357847910...e-25` (â‰¤ `1e-24`) |
| `kappa_inf` | `3.376789173614763082...e-4` (â‰¤ `1/2`) |
| `w_max` | `51.9242140445...` |
| `det` | `-7.623407555838881...` (`|det|` jauh > `1e-6`) |
| `cond_inf` | `29649.6376039...` (â‰¤ `1e6`) |
| K5 defect | `1.212132602582...e-14` (â‰¤ `1e-6`) |
| K2 lebar maks | `4.375764330275...e-14` (â‰¤ `1e-10`) |
| K2 radius berjalan | `8.164954245581...e-14` (â‰¤ `HESS_BOX = 1e-12`) |
| `QUAD_STEP` | `1.894728982373...e-19` (â‰¤ `1e-18`) |
| `DR_MAX` | `1.114186167976...e-42` (â‰¤ `1e-18`) |
| Tabrakan | jarak minimum `0.68081344...` > `1/2`; radius tabung `8.16e-14` |

Semua gate base K1-K5 **PASS**.

---

## 7. Pengungkapan K6 lama r3 (M5 `SWEEP_SIGNED=False`)

Mutasi M5 r3 (`SWEEP_SIGNED = False`) dieksekusi in r3 and menghasilkan **ALL PASS** (non-diskriminatif). R3 prereg mensyaratkan M5 gagal, sehingga K6 r3 no boleh diklaim PASS and verdict r3 **INCONCLUSIVE**. R4 **no** menggunakan M5 lama sebagai syarat K6; ia hanya tercatat sebagai kontrol non-diskriminatif in report and receipt. R4 menggantinya with M5-M9 baru which benar-benar diskriminatif.

---

## 8. Registry

- **`A-2026-0043`** ditambahkan ke `FENCE_REGISTRY.md` (baru, bukan `A-2026-0042`).
- `A-2026-0041` and `A-2026-0042` tetap no ada.
- Entry registry memuat: base r3 receipt hash, r4 receipt hash, modul r4 hash, verdict, K6 matrix, and perintah verifikasi.

---

## 9. Verifikasi

Perintah which lulus sebelum commit:

```
python -m pytest msaf/tests/test_figure_eight_r4.py -q
python -m pytest msaf/tests -q
python audit_quantum/freeze.py --verify
```

Hasil eksekusi final:

- Guard r4 (run final, pasca-fiks): 19 passed in 9033.27s (2:30:33); hash test `c91d96a0805853d424f0b49a6efc8d895951188ba8f6557499a117e09537e279`.
- Full suite: `19 passed, 0 skipped in 9033.27s (2:30:33)`.
- Freeze: `verify OK: 14 pins; Codebase/Manifest Digest =
  sha256(PINS.sha256) = f6352884d85bab5a68c01a4e1d4a73618304464fd300d56bce1f8cc2f62baa25`.

---

## 10. Langkah berikutnya

- Jika registry `A-2026-0044` diinginkan: buka trek r5 with pra-registrasi baru **sebelum kode**, K6 which benar-benar diskriminatif, tanpa mengubah r4 retrospektif.
- R4 ditutup sebagai **ALL PASS** with registry `A-2026-0043`.

