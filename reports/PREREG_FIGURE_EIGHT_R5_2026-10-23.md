# Pra-registrasi T2-r5 - re-sertifikasi figure-eight reduced 8x8 with K6 diskriminatif baru (A-2026-0044)

**Status: PRA-REGISTRASI, ditulis and in-commit sebelum satu baris kode r5.**
T2-r5 adalah trek baru, bukan amendemen T2-r4. T2-r4 ditutup **ALL PASS** with registry `A-2026-0043`; r5 memakai base r4 (or r3 which sama) sebagai kampanye base, lalu mengganti K6 with matriks mutasi baru and box B which lebih ketat.

## 1. Garis keturunan and base which dipakai

| Item | Nilai |
|---|---|
| Prereg r4 | `reports/PREREG_FIGURE_EIGHT_R4_2026-10-23.md` |
| Prereg r4 commit | `c8aff3a` (README Section 8) / prereg commit terpisah |
| Prereg r4 SHA-256LF | `14cf5c9fbaff6b2e6e67617fe724e1fc01ec18fe2e4323c51e5531256bcb21c5` |
| Base modul r3/r4 | `msaf/figure_eight_r3.py` |
| Base modul SHA-256LF | `8eddc2bb17647d452e15325397e852e224e1af028f055fa4fe41de94af939ec6` |
| Base receipt r3 | `reports/figure_eight_r3_2026-10-23.json` |
| Base receipt SHA-256LF | `6b0b71e91c9b38a2e8b43e8b2da12dbf2ce273321ffe2c4376e09bbbbdf829c9` |
| R4 modul | `msaf/figure_eight_r4.py` |
| R4 modul SHA-256LF | `e34e2303ecc17fa591aa00c4449cebae6a3f5e7db88c147d173d4414b916e2ac` |
| R4 receipt | `reports/figure_eight_r4_2026-10-23.json` |
| R4 receipt SHA-256LF | `8b6088c27f79129f8d28109a75efe2f888406b9d7e6d884c9cf7ab95cf611086` |
| R4 verdict | ALL PASS (registry `A-2026-0043`) |

R5 **no menulis ulang** persamaan, gauge, konstanta, or kampanye K1-K5. R5 mengimpor base r3, menjalankan ulang kampanye base, verifying hash receipt base, lalu menjalankan K6 baru. Ini menjaga agar sertifikat matematis which dipromosikan tetap persis sertifikat which already diperiksa, bukan salinan which dapat menyimpang tanpa terlihat.

Jika base r3 berubah, r5 harus gagal on pin hash; r5 no boleh "memperbaiki" base secara diam-diam. Perubahan matematis apa pun memerlukan trek baru r6, bukan amendemen r5.

## 2. Lingkup and limit klaim

Target tetap satu orbit periodik figure-eight on periode eksak `T0`, in dalam box lokal `B`, modulo gauge:

```
q1y = 1/5,
I_xy = q1x q1y + q2x q2y + q3x q3y = 0.
```

R5 hanya mempromosikan keberadaan and **keunikan lokal** in dalam `B`
bila base K1-K5 and seluruh K6 baru lulus. Tidak ada klaim global, stabilitas,
spektrum, chaos, ergodisitas, KAM, PDE, RH, fisika, prioritas, Lean/Coq,
or penyelesaian umum three-body.

## 3. Matematika which dikunci

Semua konstanta and metode matematis mengikuti prereg r3 and kode base r3.
R5 no mengubah:

- `T0 = 632600304 / 10^8`, `H_STEPS = 1536`, `BLOCK_STEPS = 96`;
- gauge `q1y = 1/5`, `I_xy = 0`;
- `R_B = 1e-30` (dikeratkan dari r4 `1e-18`), `K_MARGIN = 9/10`, `KAPPA_MAX = 1/2`;
- `POINT_TARGET = 1e-24`, `HESS_BOX = 1e-12`;
- `QUAD_SAFETY = 4`, `QUAD_CAP = 1e-18`, `DR_CAP = 1e-18`;
- `TUBE_CAP = 1e-10`, `GAUSS_DET_MIN = 1e-6`,
  `GAUSS_COND_MAX = 1e6`, `CHOREO_TOL = 1e-6`;
- limit Hessian path-box, `QUAD_STEP`, `DR_MAX`, Krawczyk, and
  deskriptor koreografi seperti in r3.

Perbedaan utama r5 vs r4: `R_B` dikeratkan dari `1e-18` ke `1e-30`, and
K6 baru (M1-M10) menggantikan K6 r4 (M1-M9).

Base r3 already memakai koreksi soundness path-box: `_step_with_box`
mengekspos Picard path box T1b and `_local_bounds` mengevaluasi Hessian
serta turunan sisa Taylor on path box tersebut. R5 mewarisi koreksi ini
and no mengubah T1/T1b.

## 4. Kode, receipt, and guard r5

File which akan created **setelah** prereg ini in-commit:

- `msaf/figure_eight_r5.py` - wrapper kampanye base + runner K6 baru;
- `msaf/tests/test_figure_eight_r5.py` - guard K6 baru;
- `reports/figure_eight_r5_2026-10-23.json` - receipt r5;
- `reports/FIGURE_EIGHT_R5_2026-10-23.md` - report r5.

Receipt r5 memuat:

- `schema = "msaf.figure_eight_r5.v1"`;
- hash prereg r5, hash base module r3, hash base receipt r3;
- status base K1-K5 and hash kampanye base;
- setiap baris K6: nama mutasi, parameter which diubah, gate which
  diharapkan, nilai aktual, and `passed`;
- `all_pass = base_k1_k5_pass and all(k6_rows.passed)`;
- `verdict = "ALL PASS"` hanya bila `all_pass`; selain itu `FAILED`;
- `registry = "A-2026-0044"` hanya bila `all_pass`; selain itu `null`.

Dua kampanye penuh r5 harus identik byte. Receipt which ditulis setelah
dua kampanye identik menjadi receipt final; receipt which berbeda berarti
r5 FAILED.

## 5. K6 baru - matriks mutasi diskriminatif baru (M1-M10)

K6 r5 mengganti M1-M9 r4 with mutasi baru which benar-benar diskriminatif
and no pernah digunakan in trek r4. Beberapa mutasi mengambang parameter
ke sisi which jauh lebih ekstrem dari nilai sertifikat base; satu mutasi
mengubah gauge; dua mutasi adalah integritas (receipt tamper, AST scanner).

Nilai r3 in bawah hanya dasar pemilihan mutant; nilai itu bukan result r5.

| Mutasi | Perubahan | Gate which harus gagal | Alasan pemilihan |
|---|---|---|---|
| M1 | `REMAINDER_FACTOR = 10^100` | K2 `passed=False`; error memuat `aborted at step 2` and `Picard enclosure failed` | sisa Taylor which dipompa jauh lebih parah dari r4 M1 (10^70) |
| M2 | `T0 -> T0 + 1`, `H_GRID = T0/H_STEPS` | K3 `passed=False` (Krawczyk ada); K5 `passed=False` | periode salah which lebih jauh dari r4 M2 (+1/10) |
| M3 | `TUBE_CAP = 10^-50` | K2 `passed=False`, `widths_ok=False` | lebar base ~`4.3758e-14` jauh in atas `10^-50`; gate lebar harus hidup |
| M4 | `KAPPA_MAX = 10^-20` | K3 `passed=False`, `krawczyk.kappa_ok=False` | kappa base ~`3.3768e-4` jauh in atas `10^-20` |
| M5 | `GAUSS_DET_MIN = 10^6` | K4 `passed=False`, `det_ok=False` | `|det|` base ~`7.6234` in bawah `10^6` |
| M6 | `CHOREO_TOL = 10^-50` | K5 `passed=False` | defect base ~`1.2121e-14` in atas `10^-50` |
| M7 | `GAUSS_COND_MAX = 10^6` | K4 `passed=False`, `cond_ok=False` | `cond_inf` base ~`29649.6376` in atas `10^6` |
| M8 | `q1y = 1/3` (gauge diubah dari 1/5) | K1-K5 gagal karena gauge no terpenuhi | perubahan gauge adalah validasi basis gauge |
| M9 | satu byte receipt r5 diubah | canonical/hash receipt berbeda | integritas receipt |
| M10 | injeksi literal float `1.5` and panggilan `float(x)` ke salinan source | AST scan menghasilkan hit | larangan float |

M5 lama r3 tetap dicatat sebagai kontrol non-diskriminatif in report,
tetapi **no** dipakai for menentukan K6 PASS. R5 no boleh
mengklaim K6 PASS hanya karena beberapa baris lulus bila M1-M10 no dijalankan
semua.

K6 PASS hanya bila:

1. base K1-K5 PASS and hash base cocok;
2. setiap baris M1-M10 menghasilkan gate which diminta **FAIL** (for M1-M8)
   or deteksi (for M9-M10);
3. baseline menunjukkan gate which sama **PASS** (dari base receipt);
4. M9 and M10 terdeteksi oleh guard;
5. no ada baris which berakhir `None` or error tak terduga tanpa
   gate which diminta.

Jika satu baris gagal, K6 FAILED, r5 FAILED, and no ada registry.

## 6. Registry

R5 memakai **`A-2026-0044`**. Alasannya:

- r4 membuat `A-2026-0043`;
- guard r4 which already in-commit mem-pin bahwa `A-2026-0041` and
  `A-2026-0042` no ada;
- memakai `A-2026-0044` menjaga artefak r4 tetap valid and no
  memaksa amendemen retrospektif;
- `A-2026-0041` and `A-2026-0042` tetap no ada.

Registry `A-2026-0044` hanya boleh ditambahkan setelah:

```
python -m pytest msaf/tests/test_figure_eight_r5.py -q
python -m pytest msaf/tests -q
python audit_quantum/freeze.py --verify
```

semua lulus, receipt r5 byte-identik, and `all_pass = true`.
Entry registry harus memuat: base r3 receipt hash, r5 receipt hash, modul
r5 hash, verdict, K6 matrix, and perintah verifikasi. Tidak ada entry bila
salah satu syarat gagal.

## 7. Aturan bug and amendemen

Tidak ada amendemen setelah kode r5 dimulai. Bug implementasi which no
mengubah konstanta/kriteria/metode boleh diperbaiki sebelum receipt final
with pengungkapan eksplisit (preseden r2/r3). Perubahan metode,
konstanta, or matriks K6 setelah kode dimulai memerlukan pra-registrasi
baru r6 and receipt r5 which jujur sebagai FAILED/INCONCLUSIVE.

R5 no boleh menambah registry secara retroaktif, no boleh
mengubah r4, and no boleh mengubah `FENCE_REGISTRY.md` sebelum K6
benar-benar PASS.

## 8. Kriteria verdict

| Kondisi | Verdict r5 |
|---|---|
| Base K1-K5 PASS and semua M1-M10 sesuai | `ALL PASS`; registry `A-2026-0044` boleh ditambahkan |
| Base K1-K5 PASS tetapi satu K6 row no sesuai | `FAILED`; no ada registry |
| Base K1-K5 no PASS | `FAILED`; no ada registry |
| Bug/ketidakpastian which no dapat diselesaikan tanpa mengubah metode | `INCONCLUSIVE`; no ada registry |

Verdict r5 ditulis in report and receipt; `ALL PASS` in receipt tanpa
K6 lengkap no sah.


