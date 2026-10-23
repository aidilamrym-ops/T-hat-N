# Pra-registrasi T2-r5 - re-sertifikasi figure-eight reduced 8x8 dengan K6 diskriminatif baru (A-2026-0044)

**Status: PRA-REGISTRASI, ditulis dan di-commit sebelum satu baris kode r5.**
T2-r5 adalah trek baru, bukan amendemen T2-r4. T2-r4 ditutup **ALL PASS** dengan registry `A-2026-0043`; r5 memakai base r4 (atau r3 yang sama) sebagai kampanye base, lalu mengganti K6 dengan matriks mutasi baru dan box B yang lebih ketat.

## 1. Garis keturunan dan base yang dipakai

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

R5 **tidak menulis ulang** persamaan, gauge, konstanta, atau kampanye K1-K5. R5 mengimpor base r3, menjalankan ulang kampanye base, memverifikasi hash receipt base, lalu menjalankan K6 baru. Ini menjaga agar sertifikat matematis yang dipromosikan tetap persis sertifikat yang sudah diperiksa, bukan salinan yang dapat menyimpang tanpa terlihat.

Jika base r3 berubah, r5 harus gagal pada pin hash; r5 tidak boleh "memperbaiki" base secara diam-diam. Perubahan matematis apa pun memerlukan trek baru r6, bukan amendemen r5.

## 2. Lingkup dan batas klaim

Target tetap satu orbit periodik figure-eight pada periode eksak `T0`, di dalam box lokal `B`, modulo gauge:

```
q1y = 1/5,
I_xy = q1x q1y + q2x q2y + q3x q3y = 0.
```

R5 hanya mempromosikan keberadaan dan **keunikan lokal** di dalam `B`
bila base K1-K5 dan seluruh K6 baru lulus. Tidak ada klaim global, stabilitas,
spektrum, chaos, ergodisitas, KAM, PDE, RH, fisika, prioritas, Lean/Coq,
atau penyelesaian umum three-body.

## 3. Matematika yang dikunci

Semua konstanta dan metode matematis mengikuti prereg r3 dan kode base r3.
R5 tidak mengubah:

- `T0 = 632600304 / 10^8`, `H_STEPS = 1536`, `BLOCK_STEPS = 96`;
- gauge `q1y = 1/5`, `I_xy = 0`;
- `R_B = 1e-30` (dikeratkan dari r4 `1e-18`), `K_MARGIN = 9/10`, `KAPPA_MAX = 1/2`;
- `POINT_TARGET = 1e-24`, `HESS_BOX = 1e-12`;
- `QUAD_SAFETY = 4`, `QUAD_CAP = 1e-18`, `DR_CAP = 1e-18`;
- `TUBE_CAP = 1e-10`, `GAUSS_DET_MIN = 1e-6`,
  `GAUSS_COND_MAX = 1e6`, `CHOREO_TOL = 1e-6`;
- batas Hessian path-box, `QUAD_STEP`, `DR_MAX`, Krawczyk, dan
  deskriptor koreografi seperti di r3.

Perbedaan utama r5 vs r4: `R_B` dikeratkan dari `1e-18` ke `1e-30`, dan
K6 baru (M1-M10) menggantikan K6 r4 (M1-M9).

Base r3 sudah memakai koreksi soundness path-box: `_step_with_box`
mengekspos Picard path box T1b dan `_local_bounds` mengevaluasi Hessian
serta turunan sisa Taylor pada path box tersebut. R5 mewarisi koreksi ini
dan tidak mengubah T1/T1b.

## 4. Kode, receipt, dan guard r5

File yang akan dibuat **setelah** prereg ini di-commit:

- `msaf/figure_eight_r5.py` - wrapper kampanye base + runner K6 baru;
- `msaf/tests/test_figure_eight_r5.py` - guard K6 baru;
- `reports/figure_eight_r5_2026-10-23.json` - receipt r5;
- `reports/FIGURE_EIGHT_R5_2026-10-23.md` - laporan r5.

Receipt r5 memuat:

- `schema = "msaf.figure_eight_r5.v1"`;
- hash prereg r5, hash base module r3, hash base receipt r3;
- status base K1-K5 dan hash kampanye base;
- setiap baris K6: nama mutasi, parameter yang diubah, gate yang
  diharapkan, nilai aktual, dan `passed`;
- `all_pass = base_k1_k5_pass and all(k6_rows.passed)`;
- `verdict = "ALL PASS"` hanya bila `all_pass`; selain itu `FAILED`;
- `registry = "A-2026-0044"` hanya bila `all_pass`; selain itu `null`.

Dua kampanye penuh r5 harus identik byte. Receipt yang ditulis setelah
dua kampanye identik menjadi receipt final; receipt yang berbeda berarti
r5 FAILED.

## 5. K6 baru - matriks mutasi diskriminatif baru (M1-M10)

K6 r5 mengganti M1-M9 r4 dengan mutasi baru yang benar-benar diskriminatif
dan tidak pernah digunakan di trek r4. Beberapa mutasi mengambang parameter
ke sisi yang jauh lebih ekstrem dari nilai sertifikat base; satu mutasi
mengubah gauge; dua mutasi adalah integritas (receipt tamper, AST scanner).

Nilai r3 di bawah hanya dasar pemilihan mutant; nilai itu bukan hasil r5.

| Mutasi | Perubahan | Gate yang harus gagal | Alasan pemilihan |
|---|---|---|---|
| M1 | `REMAINDER_FACTOR = 10^100` | K2 `passed=False`; error memuat `aborted at step 2` dan `Picard enclosure failed` | sisa Taylor yang dipompa jauh lebih parah dari r4 M1 (10^70) |
| M2 | `T0 -> T0 + 1`, `H_GRID = T0/H_STEPS` | K3 `passed=False` (Krawczyk ada); K5 `passed=False` | periode salah yang lebih jauh dari r4 M2 (+1/10) |
| M3 | `TUBE_CAP = 10^-50` | K2 `passed=False`, `widths_ok=False` | lebar base ~`4.3758e-14` jauh di atas `10^-50`; gate lebar harus hidup |
| M4 | `KAPPA_MAX = 10^-20` | K3 `passed=False`, `krawczyk.kappa_ok=False` | kappa base ~`3.3768e-4` jauh di atas `10^-20` |
| M5 | `GAUSS_DET_MIN = 10^6` | K4 `passed=False`, `det_ok=False` | `|det|` base ~`7.6234` di bawah `10^6` |
| M6 | `CHOREO_TOL = 10^-50` | K5 `passed=False` | defect base ~`1.2121e-14` di atas `10^-50` |
| M7 | `GAUSS_COND_MAX = 10^6` | K4 `passed=False`, `cond_ok=False` | `cond_inf` base ~`29649.6376` di atas `10^6` |
| M8 | `q1y = 1/3` (gauge diubah dari 1/5) | K1-K5 gagal karena gauge tidak terpenuhi | perubahan gauge adalah validasi basis gauge |
| M9 | satu byte receipt r5 diubah | canonical/hash receipt berbeda | integritas receipt |
| M10 | injeksi literal float `1.5` dan panggilan `float(x)` ke salinan source | AST scan menghasilkan hit | larangan float |

M5 lama r3 tetap dicatat sebagai kontrol non-diskriminatif di laporan,
tetapi **tidak** dipakai untuk menentukan K6 PASS. R5 tidak boleh
mengklaim K6 PASS hanya karena beberapa baris lulus bila M1-M10 tidak dijalankan
semua.

K6 PASS hanya bila:

1. base K1-K5 PASS dan hash base cocok;
2. setiap baris M1-M10 menghasilkan gate yang diminta **FAIL** (untuk M1-M8)
   atau deteksi (untuk M9-M10);
3. baseline menunjukkan gate yang sama **PASS** (dari base receipt);
4. M9 dan M10 terdeteksi oleh guard;
5. tidak ada baris yang berakhir `None` atau error tak terduga tanpa
   gate yang diminta.

Jika satu baris gagal, K6 FAILED, r5 FAILED, dan tidak ada registry.

## 6. Registry

R5 memakai **`A-2026-0044`**. Alasannya:

- r4 membuat `A-2026-0043`;
- guard r4 yang sudah di-commit mem-pin bahwa `A-2026-0041` dan
  `A-2026-0042` tidak ada;
- memakai `A-2026-0044` menjaga artefak r4 tetap valid dan tidak
  memaksa amendemen retrospektif;
- `A-2026-0041` dan `A-2026-0042` tetap tidak ada.

Registry `A-2026-0044` hanya boleh ditambahkan setelah:

```
python -m pytest msaf/tests/test_figure_eight_r5.py -q
python -m pytest msaf/tests -q
python audit_quantum/freeze.py --verify
```

semua lulus, receipt r5 byte-identik, dan `all_pass = true`.
Entry registry harus memuat: base r3 receipt hash, r5 receipt hash, modul
r5 hash, verdict, K6 matrix, dan perintah verifikasi. Tidak ada entry bila
salah satu syarat gagal.

## 7. Aturan bug dan amendemen

Tidak ada amendemen setelah kode r5 dimulai. Bug implementasi yang tidak
mengubah konstanta/kriteria/metode boleh diperbaiki sebelum receipt final
dengan pengungkapan eksplisit (preseden r2/r3). Perubahan metode,
konstanta, atau matriks K6 setelah kode dimulai memerlukan pra-registrasi
baru r6 dan receipt r5 yang jujur sebagai FAILED/INCONCLUSIVE.

R5 tidak boleh menambah registry secara retroaktif, tidak boleh
mengubah r4, dan tidak boleh mengubah `FENCE_REGISTRY.md` sebelum K6
benar-benar PASS.

## 8. Kriteria verdict

| Kondisi | Verdict r5 |
|---|---|
| Base K1-K5 PASS dan semua M1-M10 sesuai | `ALL PASS`; registry `A-2026-0044` boleh ditambahkan |
| Base K1-K5 PASS tetapi satu K6 row tidak sesuai | `FAILED`; tidak ada registry |
| Base K1-K5 tidak PASS | `FAILED`; tidak ada registry |
| Bug/ketidakpastian yang tidak dapat diselesaikan tanpa mengubah metode | `INCONCLUSIVE`; tidak ada registry |

Verdict r5 ditulis di laporan dan receipt; `ALL PASS` di receipt tanpa
K6 lengkap tidak sah.
