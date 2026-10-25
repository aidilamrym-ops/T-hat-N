# Pra-registrasi T2-r4 - re-sertifikasi figure-eight dengan K6 diskriminatif

**Status: PRA-REGISTRASI, ditulis dan di-commit sebelum satu baris kode r4.**
T2-r4 adalah trek baru, bukan amendemen T2-r3. T2-r3 ditutup
**INCONCLUSIVE** karena K6/M5 non-diskriminatif; r3 tidak membuat registry
`A-2026-0042`. T2-r4 memakai matematika r3 yang sudah di-commit sebagai
base, lalu mengganti K6 dengan matriks mutasi yang harus benar-benar
menghasilkan kegagalan gate.

## 1. Garis keturunan dan base yang dipakai

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
| Registry r3 | tidak ada |

R4 **tidak menulis ulang** persamaan, gauge, konstanta, atau kampanye
K1-K5. R4 mengimpor base r3, menjalankan ulang kampanye base, memverifikasi
hash receipt base, lalu menjalankan K6 baru. Ini menjaga agar sertifikat
matematis yang dipromosikan tetap persis sertifikat yang sudah diperiksa,
bukan salinan yang dapat menyimpang tanpa terlihat.

Jika base r3 berubah, r4 harus gagal pada pin hash; r4 tidak boleh
"memperbaiki" base secara diam-diam. Perubahan matematis apa pun
memerlukan trek baru r5, bukan amendemen r4.

## 2. Lingkup dan batas klaim

Target tetap satu orbit periodik figure-eight pada periode eksak `T0`,
di dalam box lokal `B`, modulo gauge:

```
q1y = 1/5,
I_xy = q1x q1y + q2x q2y + q3x q3y = 0.
```

R4 hanya mempromosikan keberadaan dan **keunikan lokal** di dalam `B`
bila base K1-K5 dan seluruh K6 lulus. Tidak ada klaim global, stabilitas,
spektrum, chaos, ergodisitas, KAM, PDE, RH, fisika, prioritas, Lean/Coq,
atau penyelesaian umum three-body.

## 3. Matematika yang dikunci

Semua konstanta dan metode matematis mengikuti prereg r3 dan kode base r3.
R4 tidak mengubah:

- `T0 = 632600304 / 10^8`, `H_STEPS = 1536`, `BLOCK_STEPS = 96`;
- gauge `q1y = 1/5`, `I_xy = 0`;
- `R_B = 1e-18`, `K_MARGIN = 9/10`, `KAPPA_MAX = 1/2`;
- `POINT_TARGET = 1e-24`, `HESS_BOX = 1e-12`;
- `QUAD_SAFETY = 4`, `QUAD_CAP = 1e-18`, `DR_CAP = 1e-18`;
- `TUBE_CAP = 1e-10`, `GAUSS_DET_MIN = 1e-6`,
  `GAUSS_COND_MAX = 1e6`, `CHOREO_TOL = 1e-6`;
- batas Hessian path-box, `QUAD_STEP`, `DR_MAX`, Krawczyk, dan
  deskriptor koreografi seperti di r3.

Base r3 sudah memakai koreksi soundness path-box: `_step_with_box`
mengekspos Picard path box T1b dan `_local_bounds` mengevaluasi Hessian
serta turunan sisa Taylor pada path box tersebut. R4 mewarisi koreksi ini
dan tidak mengubah T1/T1b.

## 4. Kode, receipt, dan guard r4

File yang akan dibuat **setelah** prereg ini di-commit:

- `msaf/figure_eight_r4.py` - wrapper kampanye base + runner K6;
- `msaf/tests/test_figure_eight_r4.py` - guard K6;
- `reports/figure_eight_r4_2026-10-23.json` - receipt r4;
- `reports/FIGURE_EIGHT_R4_2026-10-23.md` - laporan r4.

Receipt r4 memuat:

- `schema = "msaf.figure_eight_r4.v1"`;
- hash prereg r4, hash base module r3, hash base receipt r3;
- status base K1-K5 dan hash kampanye base;
- setiap baris K6: nama mutasi, parameter yang diubah, gate yang
  diharapkan, nilai aktual, dan `passed`;
- `all_pass = base_k1_k5_pass and all(k6_rows.passed)`;
- `verdict = "ALL PASS"` hanya bila `all_pass`; selain itu `FAILED`;
- `registry = "A-2026-0043"` hanya bila `all_pass`; selain itu `null`.

Dua kampanye penuh r4 harus identik byte. Receipt yang ditulis setelah
dua kampanye identik menjadi receipt final; receipt yang berbeda berarti
r4 FAILED.

## 5. K6 baru - matriks mutasi diskriminatif

K6 r4 mengganti M5 lama r3 (`SWEEP_SIGNED = False`) karena r3 sudah
membuktikan mutasi itu **non-diskriminatif**. M5 baru adalah mutasi
sensitivitas gate: ambang yang dikunci diturunkan/dinaikkan ke sisi yang
salah dari nilai sertifikat base. Ini bukan perubahan metode matematis;
tujuannya memastikan setiap gate benar-benar dieksekusi, bukan no-op.

Nilai r3 di bawah hanya dasar pemilihan mutant; nilai itu bukan hasil r4.

| Mutasi | Perubahan | Gate yang harus gagal | Alasan pemilihan |
|---|---|---|---|
| M1 | `REMAINDER_FACTOR = 10^70` | K2 `passed=False`; error memuat `aborted at step 2` dan `Picard enclosure failed` | sisa Taylor yang dipompa harus ditolak |
| M2 | `T0 -> T0 + 1/10`, `H_GRID = T0/H_STEPS` | K3 `passed=False` (Krawczyk ada); K5 `passed=False` | periode salah tidak boleh lolos K3 |
| M3 | satu byte receipt r4 diubah | canonical/hash receipt berbeda | integritas receipt |
| M4 | injeksi literal float `1.5` dan panggilan `float(x)` ke salinan source | AST scan menghasilkan hit | larangan float |
| M5 | `TUBE_CAP = 10^-30` | K2 `passed=False`, `widths_ok=False` | lebar base ~`4.3758e-14` jauh di atas `10^-30`; gate lebar harus hidup |
| M6 | `KAPPA_MAX = 10^-12` | K3 `passed=False`, `krawczyk.kappa_ok=False` | kappa base ~`3.3768e-4` jauh di atas `10^-12` |
| M7 | `GAUSS_DET_MIN = 10^3` | K4 `passed=False`, `det_ok=False` | `|det|` base ~`7.6234` di bawah `10^3` |
| M8 | `CHOREO_TOL = 10^-30` | K5 `passed=False` | defect base ~`1.2121e-14` di atas `10^-30` |
| M9 | `GAUSS_COND_MAX = 10^3` | K4 `passed=False`, `cond_ok=False` | `cond_inf` base ~`29649.6376` di atas `10^3` |

M5 lama r3 tetap dicatat sebagai kontrol non-diskriminatif di laporan,
tetapi **tidak** dipakai untuk menentukan K6 PASS. R4 tidak boleh
mengklaim K6 PASS hanya karena M1/M2 lulus bila M5-M9 tidak dijalankan.

K6 PASS hanya bila:

1. base K1-K5 PASS dan hash base cocok;
2. setiap baris M1-M9 menghasilkan gate yang diminta **FAIL**;
3. baseline menunjukkan gate yang sama **PASS** (dari base receipt);
4. M3 dan M4 terdeteksi oleh guard;
5. tidak ada baris yang berakhir `None` atau error tak terduga tanpa
   gate yang diminta.

Jika satu baris gagal, K6 FAILED, r4 FAILED, dan tidak ada registry.

## 6. Registry

R4 memakai **`A-2026-0043`**, bukan `A-2026-0042`. Alasannya:

- r3 tidak pernah membuat `A-2026-0042`;
- guard r3 yang sudah di-commit mem-pin bahwa `A-2026-0041` dan
  `A-2026-0042` tidak ada;
- memakai `A-2026-0043` menjaga artefak r3 tetap valid dan tidak
  memaksa amendemen retrospektif;
- `A-2026-0041` dan `A-2026-0042` tetap tidak ada.

Registry `A-2026-0043` hanya boleh ditambahkan setelah:

```
python -m pytest msaf/tests/test_figure_eight_r4.py -q
python -m pytest msaf/tests -q
python audit_quantum/freeze.py --verify
```

semuanya lulus, receipt r4 byte-identik, dan `all_pass = true`.
Entry registry harus memuat: base r3 receipt hash, r4 receipt hash, modul
r4 hash, verdict, K6 matrix, dan perintah verifikasi. Tidak ada entry bila
salah satu syarat gagal.

## 7. Aturan bug dan amendemen

Tidak ada amendemen setelah kode r4 dimulai. Bug implementasi yang tidak
mengubah konstanta/kriteria/metode boleh diperbaiki sebelum receipt final
dengan pengungkapan eksplisit (preseden r2/r3). Perubahan metode,
konstanta, atau matriks K6 setelah kode dimulai memerlukan pra-registrasi
baru r5 dan receipt r4 yang jujur sebagai FAILED/INCONCLUSIVE.

R4 tidak boleh menambah registry secara retroaktif, tidak boleh
mengubah r3, dan tidak boleh mengubah `FENCE_REGISTRY.md` sebelum K6
benar-benar PASS.

## 8. Kriteria verdict

| Kondisi | Verdict r4 |
|---|---|
| Base K1-K5 PASS dan semua M1-M9 sesuai | `ALL PASS`; registry `A-2026-0043` boleh ditambahkan |
| Base K1-K5 PASS tetapi satu K6 row tidak sesuai | `FAILED`; tidak ada registry |
| Base K1-K5 tidak PASS | `FAILED`; tidak ada registry |
| Bug/ketidakpastian yang tidak dapat diselesaikan tanpa mengubah metode | `INCONCLUSIVE`; tidak ada registry |

Verdict r4 ditulis di laporan dan receipt; `ALL PASS` di receipt tanpa
K6 lengkap tidak sah.
