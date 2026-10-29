# Pra-registrasi T2-r4 - re-sertifikasi figure-eight with K6 diskriminatif

**Status: PRA-REGISTRASI, ditulis and in-commit sebelum satu baris kode r4.**
T2-r4 adalah trek baru, bukan amendemen T2-r3. T2-r3 ditutup
**INCONCLUSIVE** karena K6/M5 non-diskriminatif; r3 no membuat registry
`A-2026-0042`. T2-r4 memakai matematika r3 which already in-commit sebagai
base, lalu mengganti K6 with matriks mutasi which harus benar-benar
menghasilkan kegagalan gate.

## 1. Garis keturunan and base which dipakai

| Item | Nilai |
|---|---|
| Prereg r3 | `reports/PREREG_FIGURE_EIGHT_R3_2026-10-23.md` |
| Prereg r3 commit | `38d19e8` |
| Prereg r3 SHA-256LF | `23ab24254f13539dddf1bd3cccd87dbbcef01b3398dab1ccf5fb2d75099a6b93` |
| Base modul r3 | `msaf/figure_eight_r3.py` |
| Base modul SHA-256LF | `8eddc2bb17647d452e15325397e852e224e1af028f055fa4fe41de94af939ec6` |
| Base receipt r3 | `reports/figure_eight_r3_2026-10-23.json` |
| Base receipt SHA-256LF | `6b0b71e91c9b38a2e8b43e8b2da12dbf2ce273321ffe2c4376e09bbbbdf829c9` |
| Base verdict r3 | INCONCLUSIVE: K1-K5 PASS, K6/M5 non-diskriminatif |
| Registry r3 | no ada |

R4 **no menulis ulang** persamaan, gauge, konstanta, or kampanye
K1-K5. R4 mengimpor base r3, menjalankan ulang kampanye base, verifying
hash receipt base, lalu menjalankan K6 baru. Ini menjaga agar sertifikat
matematis which dipromosikan tetap persis sertifikat which already diperiksa,
bukan salinan which dapat menyimpang tanpa terlihat.

Jika base r3 berubah, r4 harus gagal on pin hash; r4 no boleh
"memperbaiki" base secara diam-diam. Perubahan matematis apa pun
memerlukan trek baru r5, bukan amendemen r4.

## 2. Lingkup and limit klaim

Target tetap satu orbit periodik figure-eight on periode eksak `T0`,
in dalam box lokal `B`, modulo gauge:

```
q1y = 1/5,
I_xy = q1x q1y + q2x q2y + q3x q3y = 0.
```

R4 hanya mempromosikan keberadaan and **keunikan lokal** in dalam `B`
bila base K1-K5 and seluruh K6 lulus. Tidak ada klaim global, stabilitas,
spektrum, chaos, ergodisitas, KAM, PDE, RH, fisika, prioritas, Lean/Coq,
or penyelesaian umum three-body.

## 3. Matematika which dikunci

Semua konstanta and metode matematis mengikuti prereg r3 and kode base r3.
R4 no mengubah:

- `T0 = 632600304 / 10^8`, `H_STEPS = 1536`, `BLOCK_STEPS = 96`;
- gauge `q1y = 1/5`, `I_xy = 0`;
- `R_B = 1e-18`, `K_MARGIN = 9/10`, `KAPPA_MAX = 1/2`;
- `POINT_TARGET = 1e-24`, `HESS_BOX = 1e-12`;
- `QUAD_SAFETY = 4`, `QUAD_CAP = 1e-18`, `DR_CAP = 1e-18`;
- `TUBE_CAP = 1e-10`, `GAUSS_DET_MIN = 1e-6`,
  `GAUSS_COND_MAX = 1e6`, `CHOREO_TOL = 1e-6`;
- limit Hessian path-box, `QUAD_STEP`, `DR_MAX`, Krawczyk, and
  deskriptor koreografi seperti in r3.

Base r3 already memakai koreksi soundness path-box: `_step_with_box`
mengekspos Picard path box T1b and `_local_bounds` mengevaluasi Hessian
serta turunan sisa Taylor on path box tersebut. R4 mewarisi koreksi ini
and no mengubah T1/T1b.

## 4. Kode, receipt, and guard r4

File which akan created **setelah** prereg ini in-commit:

- `msaf/figure_eight_r4.py` - wrapper kampanye base + runner K6;
- `msaf/tests/test_figure_eight_r4.py` - guard K6;
- `reports/figure_eight_r4_2026-10-23.json` - receipt r4;
- `reports/FIGURE_EIGHT_R4_2026-10-23.md` - report r4.

Receipt r4 memuat:

- `schema = "msaf.figure_eight_r4.v1"`;
- hash prereg r4, hash base module r3, hash base receipt r3;
- status base K1-K5 and hash kampanye base;
- setiap baris K6: nama mutasi, parameter which diubah, gate which
  diharapkan, nilai aktual, and `passed`;
- `all_pass = base_k1_k5_pass and all(k6_rows.passed)`;
- `verdict = "ALL PASS"` hanya bila `all_pass`; selain itu `FAILED`;
- `registry = "A-2026-0043"` hanya bila `all_pass`; selain itu `null`.

Dua kampanye penuh r4 harus identik byte. Receipt which ditulis setelah
dua kampanye identik menjadi receipt final; receipt which berbeda berarti
r4 FAILED.

## 5. K6 baru - matriks mutasi diskriminatif

K6 r4 mengganti M5 lama r3 (`SWEEP_SIGNED = False`) karena r3 already
membuktikan mutasi itu **non-diskriminatif**. M5 baru adalah mutasi
sensitivitas gate: ambang which dikunci diturunkan/dinaikkan ke sisi which
salah dari nilai sertifikat base. Ini bukan perubahan metode matematis;
tujuannya memastikan setiap gate benar-benar dieksekusi, bukan no-op.

Nilai r3 in bawah hanya dasar pemilihan mutant; nilai itu bukan result r4.

| Mutasi | Perubahan | Gate which harus gagal | Alasan pemilihan |
|---|---|---|---|
| M1 | `REMAINDER_FACTOR = 10^70` | K2 `passed=False`; error memuat `aborted at step 2` and `Picard enclosure failed` | sisa Taylor which dipompa harus ditolak |
| M2 | `T0 -> T0 + 1/10`, `H_GRID = T0/H_STEPS` | K3 `passed=False` (Krawczyk ada); K5 `passed=False` | periode salah no boleh lolos K3 |
| M3 | satu byte receipt r4 diubah | canonical/hash receipt berbeda | integritas receipt |
| M4 | injeksi literal float `1.5` and panggilan `float(x)` ke salinan source | AST scan menghasilkan hit | larangan float |
| M5 | `TUBE_CAP = 10^-30` | K2 `passed=False`, `widths_ok=False` | lebar base ~`4.3758e-14` jauh in atas `10^-30`; gate lebar harus hidup |
| M6 | `KAPPA_MAX = 10^-12` | K3 `passed=False`, `krawczyk.kappa_ok=False` | kappa base ~`3.3768e-4` jauh in atas `10^-12` |
| M7 | `GAUSS_DET_MIN = 10^3` | K4 `passed=False`, `det_ok=False` | `|det|` base ~`7.6234` in bawah `10^3` |
| M8 | `CHOREO_TOL = 10^-30` | K5 `passed=False` | defect base ~`1.2121e-14` in atas `10^-30` |
| M9 | `GAUSS_COND_MAX = 10^3` | K4 `passed=False`, `cond_ok=False` | `cond_inf` base ~`29649.6376` in atas `10^3` |

M5 lama r3 tetap dicatat sebagai kontrol non-diskriminatif in report,
tetapi **no** dipakai for menentukan K6 PASS. R4 no boleh
mengklaim K6 PASS hanya karena M1/M2 lulus bila M5-M9 no dijalankan.

K6 PASS hanya bila:

1. base K1-K5 PASS and hash base cocok;
2. setiap baris M1-M9 menghasilkan gate which diminta **FAIL**;
3. baseline menunjukkan gate which sama **PASS** (dari base receipt);
4. M3 and M4 terdeteksi oleh guard;
5. no ada baris which berakhir `None` or error tak terduga tanpa
   gate which diminta.

Jika satu baris gagal, K6 FAILED, r4 FAILED, and no ada registry.

## 6. Registry

R4 memakai **`A-2026-0043`**, bukan `A-2026-0042`. Alasannya:

- r3 no pernah membuat `A-2026-0042`;
- guard r3 which already in-commit mem-pin bahwa `A-2026-0041` and
  `A-2026-0042` no ada;
- memakai `A-2026-0043` menjaga artefak r3 tetap valid and no
  memaksa amendemen retrospektif;
- `A-2026-0041` and `A-2026-0042` tetap no ada.

Registry `A-2026-0043` hanya boleh ditambahkan setelah:

```
python -m pytest msaf/tests/test_figure_eight_r4.py -q
python -m pytest msaf/tests -q
python audit_quantum/freeze.py --verify
```

semuanya lulus, receipt r4 byte-identik, and `all_pass = true`.
Entry registry harus memuat: base r3 receipt hash, r4 receipt hash, modul
r4 hash, verdict, K6 matrix, and perintah verifikasi. Tidak ada entry bila
salah satu syarat gagal.

## 7. Aturan bug and amendemen

Tidak ada amendemen setelah kode r4 dimulai. Bug implementasi which no
mengubah konstanta/kriteria/metode boleh diperbaiki sebelum receipt final
with pengungkapan eksplisit (preseden r2/r3). Perubahan metode,
konstanta, or matriks K6 setelah kode dimulai memerlukan pra-registrasi
baru r5 and receipt r4 which jujur sebagai FAILED/INCONCLUSIVE.

R4 no boleh menambah registry secara retroaktif, no boleh
mengubah r3, and no boleh mengubah `FENCE_REGISTRY.md` sebelum K6
benar-benar PASS.

## 8. Kriteria verdict

| Kondisi | Verdict r4 |
|---|---|
| Base K1-K5 PASS and semua M1-M9 sesuai | `ALL PASS`; registry `A-2026-0043` boleh ditambahkan |
| Base K1-K5 PASS tetapi satu K6 row no sesuai | `FAILED`; no ada registry |
| Base K1-K5 no PASS | `FAILED`; no ada registry |
| Bug/ketidakpastian which no dapat diselesaikan tanpa mengubah metode | `INCONCLUSIVE`; no ada registry |

Verdict r4 ditulis in report and receipt; `ALL PASS` in receipt tanpa
K6 lengkap no sah.


