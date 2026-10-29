# Status Target Program â€” 2026-10-25

Dokumen ini mengumpulkan semua target matematika/fisika which pernah masuk
antrian program, beserta status jujurnya per 2026-10-25. Sumber utama:
`reports/DAFTAR_MASALAH_KERJA.md`, `reports/FENCE_REGISTRY.md`,
`reports/HANDOFF.md`, and file kampanye in `reports/`.

**Prinsip which no berubah:** no ada klaim universal/infinite; setiap
target hanya boleh berstatus CERTIFIED jika ada artefak finit, receipt
deterministik, guard CI, and entri registry. Status FAILED/INCONCLUSIVE/
PARTIAL dicatat apa adanya and no "dinaikkan" menjadi CERTIFIED.

---

## 1. Ringkasan eksekutif

| Kelompok | Status ringkas |
|---|---|
| Figure-eight three-body (T2-r3/r4/r5) | r3 INCONCLUSIVE; **r4 CERTIFIED (T-2026-0043)**; r5 FAILED (tanpa A-2026-0044) |
| T1/T1b integrator ODE | CERTIFIED (A-2026-0040) |
| Navierâ€“Stokes diskrit | CERTIFIED terbatas (A-2026-0038/0039); regularitas global TIDAK diklaim |
| RH / Guinandâ€“Weil (ladder, T=100..500) | Beberapa fragmen CERTIFIED (T-2026-0001/0002, F-2026-0001/0002, A-2026-0033/0034/0035); RH global TIDAK diklaim |
| Hodge Picard bound | CERTIFIED terbatas (A-2026-0036/0037); result F_5/F_7 no informatif |
| BSD Q1 | **CERTIFIED v2 (T-2026-0049)**: 5 kurva rank-0 (11a1, 14a1, 15a1, 17a1, 19a1) verifikasi eksak formula BSD L(E,1)/Î© = |Ð¨|Â·âˆc_p/|E(Q)_tors|Â² with parameter LMFDB; v1 (A-2026-0028) INCONCLUSIVE diganti |
| Twin prime Q2 | Sensus v4 N=10^10 **ALL PASS** (A-2026-0048); v3 N=10^9 **ALL PASS** (A-2026-0046); v2 N=10^7 tetap CERTIFIED (A-2026-0045); entri lama N=100.000 tetap INCONCLUSIVE (A-2026-0029) |
| ABC Q3 | CERTIFIED sensus C=100.000 (A-2026-0032) â€” 6 triple q>1.4 |
| RH scaffold Stage 1â€“6 | Stage 1â€“4 scaffold **kernel-checked PASS**; Stage 5 menambahkan teorema perturbasi finit kondisional + envelope error entry `c=13,N=160` (`T-2026-0051`); Stage 6 menambahkan limit tail diagonal `XC` finit and limit mayoran (`T-2026-0052`); **bukan bukti analitik penuh, bukan kontrol seluruh matriks, and bukan RH** |
| Quantum audit | Statistik 16-bin + Ï‡Â² + tail zâ‰¥3.5 direproduksi; verdict RESOLVED (layer statistik, bukan klaim fisika) |
| Learnharness | Prototipe stub (engine + test); model nyata belum ada |
| MCP T2N | Modul asli dipulihkan; `opencode.jsonc` tetap menunjuk enam server |

---

## 2. Disposisi 20 masalah (`DAFTAR_MASALAH_KERJA.md`)

| No | Masalah | Status 2026-10-25 | Artefak / limit |
|---|---|---|---|
| 1 | Riemann | TREK AKTIF â€” fragmen finit | Ladder 201/301/401, dim 501 OUTCOME non-PD, T=100..500 winding cross-lock (A-2026-0033/0034/0035); RH global TIDAK diklaim |
| 2 | P vs NP | DAFTAR-B â€” formalisasi saja | Belum ada serangan komputasional; hanya rencana formalisasi fragmen |
| 3 | Hodge | TREK AKTIF â€” fragmen finit | Picard bound CH a_11 F_3 (A-2026-0036); F_5/F_7 non-informatif (A-2026-0037) |
| 4 | Yangâ€“Mills mass gap | TIDAK MASUK | Butuh konstruksi QFT; in luar alat |
| 5 | Navierâ€“Stokes | TREK AKTIF â€” diskrit | Kernel diskrit Lean (A-2026-0038), regularitas diskrit (A-2026-0039); global TIDAK diklaim |
| 6 | BSD | **Q1 v2 CERTIFIED (T-2026-0049)** â€” 5 kurva rank-0 | v2 verifikasi eksak formula BSD rank-0; A-2026-0028 v1 tetap INCONCLUSIVE; v2 receipt `82fa29fcâ€¦`; pra-reg `reports/PREREG_Q1_BSD_V2_2026-10-30.md` |
| 7 | Renormalisasi QFT | TIDAK MASUK | Fondasi, bukan klaim komputasional |
| 8 | Informasi black hole | TIDAK MASUK | Interpretasional |
| 9 | Konstanta kosmologis | TIDAK MASUK | Puzzle fisika; energi vakum tak terhitung rigorous |
| 10 | Pengukuran kuantum | TIDAK MASUK | Interpretasional |
| 11 | Gravitasi kuantum | TIDAK MASUK | Tak ada teori for dihitung |
| 12 | Twin prime | Q2 - fragmen finit CERTIFIED | A-2026-0048: N=10^10 (count=27.412.679, identik dua sieve); A-2026-0046: N=10^9 (count=3.424.506, max_gap=4.770, digest 427f9211â€¦); A-2026-0045: N=10^7 (count=58.980); A-2026-0029 (N=100.000) tetap INCONCLUSIVE |
| 13 | abc | Q3 â€” CERTIFIED sensus | A-2026-0032: C=100.000, 6 triple q>1.4 |
| 14 | Asimetri materi | TIDAK MASUK | Model-dependent, kosmologi |
| 15 | Superkonduktivitas Tc-tinggi | TIDAK MASUK | Numerik Hubbard bukan rigorous-verifiable |
| 16 | Three-body | TREK AKTIF â€” r4 CERTIFIED, r5 FAILED | r3 INCONCLUSIVE; r4 T-2026-0043; r5 FAILED (M3/M8 non-diskriminatif), tanpa A-2026-0044 |
| 17 | Schanuel | DAFTAR-B â€” formalisasi saja | Hanya rencana instans Lindemannâ€“Weierstrass |
| 18 | Cosmic censorship | TIDAK MASUK | PDE Einstein in luar jangkauan |
| 19 | Anderson | DAFTAR-B â€” syarat | Benchmark RBM S1/S2 (A-2026-0023) ada, tetapi transisi Anderson fisik TIDAK diklaim |
| 20 | Soliton | DAFTAR-B â€” syarat | Belum ada enclosure Evans; menunggu integrator tervalidasi |

---

## 3. Garis figure-eight (three-body reduced 8Ã—8)

| Trek | Verdict | Registry | Catatan |
|---|---|---|---|
| T2 | FAILED | â€” | K3 singularitas translasi-x eksak (`DF e = 0`) |
| T2-r2 | FAILED | â€” | K2: slack kuadratik T1b beku, width 320 in step 96 |
| T2-r3 | INCONCLUSIVE | â€” | K6/M5 non-diskriminatif; no ada A-2026-0042 |
| T2-r4 | **CERTIFIED** | **T-2026-0043** + A-2026-0043 | K1â€“K5 + K6 M1â€“M9 diskriminatif; receipt `8b6088c2â€¦` |
| T2-r5 | FAILED | â€” | M3 (`C=1/3`) and M8 (`GAUSS_COND_MAX=10^6`) non-diskriminatif; A-2026-0044 no created |

Klaim r4 tetap: keberadaan and **keunikan lokal** orbit figure-eight in dalam
box `B`, modulo gauge `q1y=1/5`, `I_xy=0`, with `R_B=1e-18`. Tidak ada
klaim global, stabilitas, chaos, ergodisitas, KAM, PDE, RH, fisika, or
prioritas.

---

## 4. RH scaffold, quantum audit, learnharness

### 4.1 RH scaffold (`reports/RH_SCAFFOLD_NOTES/`)

**Koreksi 2026-10-26.** Tabel in bawah adalah snapshot 2026-10-25. Sejak
`08ae970`/`9d13787`, implementasi aktif Stage 2/3 ada in `lean/`, bukan in
folder arsip prompt. Lihat
`reports/RH_SCAFFOLD_NOTES/STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md`.

| Stage | Arsip prompt | Implementasi aktif | Status jujur |
|---|---|---|---|
| 1 | `Stage_1_Formalization_Test_Function_Space.lean` | sama | definisi `MSAFTestFunctionSpace` and `continuous_quadratic_form`; **kernel-checked PASS**, belum ada bukti analitik penuh |
| 2 | `Stage_2_Derivation_Analytic_Tail_Bound.lean` (placeholder) | `lean/Stage_2_Tail_Bound.lean` | konstanta truncation archimedean GW nyata (`c=13`, `C=169/42`, `alpha=3261/2`, `K=814`) and ketaksamaan skalar; **bukan** derivasi tail analitik, **bukan** `C/n` or `C/n^2` |
| 3 | `Stage_3_Eigenvalue_Locking_Dimension_Induction.lean` (placeholder) | `lean/Stage_3_Eigenvalue_Locking.lean` | record data for dua run Arb (`dim=321`, `dim=257`); **bukan** induksi dimensi, and induksi naik memang no valid karena Cauchy interlacing |
| 4 | `Stage_4_Containment_Proof.lean` | sama (already ditulis ulang) | `test_function_l2_containment` dari polynomial decay; **bukan** containment spektrum zeta |
| 5 | â€” (no ada arsip prompt) | `lean/Stage_5_EntryError_Perturbation.lean` | envelope entry `epsilon=10^-100`, `delta=321*10^-100 < lambda_min`; `posDef_add_of_quadratic_bound` and `gw_entry_perturbation_posDef` **kondisional** on `A.PosDef` and limit kuadratik `A`; **bukan** bukti positivity matriks Arb |
| 6 | â€” (no ada arsip prompt) | `lean/Stage_6_Analytic_Tail.lean` | step tail finit `âˆ‘ 1/nÂ² â‰¤ 1/N`, propagasi limit pointwise, and `(4/L)/N â†’ 0`; limit pointwise `|XC(n)| < 1/nÂ²` adalah **input analitik + grid Arb**, bukan result kernel; **bukan** kontrol tail seluruh matriks |

Semua file Lean bebas `sorry`/`admit`/`unsafe`/`axiom`, and modul aktif
**lulus kernel check** with Lean 4.33.1 / Mathlib `0df444a360`. Namun isinya
tetap terbatas: Stage 2 bukan derivasi tail Archimedean, Stage 3 bukan induksi
dimensi, Stage 4 hanya containment LÂ² dari hipotesis polynomial decay, Stage 5
hanya aritmetika perturbasi finit which kondisional, and Stage 6 hanya step
tail finit/limit. Stage 5 **no** membuktikan bahwa matriks Arb
positif-definit; sertifikat eigenvalue tetap run `arb_mat.eig` eksternal, and
hubungan sertifikat itu ke hipotesis `A.PosDef`/`hAquad` belum diformalkan.
Stage 6 **no** memformalkan representasi integral trigamma: limit pointwise
`|XC(n)| < 1/nÂ²` adalah derivasi analitik in report P2 plus grid Arb, bukan
keluaran kernel. Jangan menyebutnya "bukti RH", "bukti analytic tail bound
penuh", or kontrol tail seluruh matriks. Rincian P1:
`reports/ENTRY_ERROR_ENVELOPE_2026-10-26.md`; rincian P2:
`reports/ANALYTIC_TAIL_BOUND_2026-10-26.md`.

Log lengkap: `reports/RH_SCAFFOLD_NOTES/KERNEL_CHECK_2026-10-25.md` (perintah
kernel, SHA-256LF, axiom footprint, and anti-circularity gate PASS).

### 4.2 Quantum audit (`audit_quantum/`)

- `audit_quantum/analyze_stats.py` membaca tiga binary `stats_d201.bin`,
  `stats_d301.bin`, `stats_d401.bin` (masing-masing 20.000 float64
  little-endian).
- Setiap set dibagi ke 16 bin equiprobable normal; expected 1250/bin.
- Hasil: Ï‡Â² = 7.508800 / 10.398400 / 11.592000, semuanya in dalam window
  [0, 60]; tail satu sisi z â‰¥ 3.5 = 2 / 4 / 3. Overall **RESOLVED**.
- `reports/audit_quantum_2026-10-19.md` memuat tabel bin, verdict, and
  receipt JSON; `reports/audit_quantum_2026-10-19.json` memuat receipt
  lengkap (hash file, counts, Ï‡Â², mean, stdev).
- **Batas:** ini layer statistik SIMULATED; bukan klaim fisika, bukan
  pengganti layer interval tersertifikasi.

### 4.3 Learnharness (`msaf/learnharness_prototype.py`)

- `msaf/learnharness_prototype.py`: kelas `LearnEngine` stub (`train` menyimpan
  panjang data, `predict` mengembalikan matriks identitas 8Ã—8).
- `msaf/tests/test_learnharness_prototype.py`: tes dasar.
- **Batas:** bukan model ML nyata, no dilatih on data kampanye, no
  terintegrasi ke pipeline figure-eight. Status: PROTOTIPE.
- Catatan: `msaf/learnharness/` adalah repo pihak ketiga terpisah (nested git,
  in-ignore oleh repo utama). Prototipe MSAF sengaja diletakkan in
  `msaf/learnharness_prototype.py` agar dapat dilacak oleh repo utama.

### 4.4 Twin prime Q2 v2 (`msaf/twin_prime_v2.py`)

- Dua sieve independen: A = Eratosthenes bytearray penuh; B = segmented
  sieve, base prime sampai `isqrt(N+2)`, blok `2^20`.
- Konfigurasi terkunci: `N = 10_000_000`; integer Python eksak; receipt tanpa
  runtime/timestamp.
- Hasil: `count = 58.980`, `max_gap = 1.722`, pasangan pertama `(3,5)`,
  pasangan terakhir `(9.999.971, 9.999.973)`; `pairs_A == pairs_B`;
  `pairs_sha256 = 64ecf493â€¦d380`.
- Determinisme: dua run menghasilkan receipt SHA-256
  `6c613dd573867e2d54cf7ed162413cb7f1b5e40b8be2724797681dddb72094d4`.
- Registry: `A-2026-0045` (CERTIFIED for fragmen finit ini).
- **Batas:** bukan bukti konjektur twin prime, bukan klaim asimtotik, and
  no mencakup `N = 10^9`.

### 4.5 BSD Q1 recon (`reports/BSD_Q1_RECON_2026-10-25.md`)

- Audit lama `A-2026-0028` hanya menunjukkan hardcode/tautologi; recon
  baru memeriksa nilai tabel terhadap LMFDB.
- Kode `msaf/bsd_descent.py` tetap hardcode: `two_descent()` tabel lookup,
  `modular_symbol_ec()` tabel, `real_period()` = 1,
  `verify_bsd()` membandingkan `invariants` with `rhs_map`, and
  `conductor` mengembalikan `|Î”|`.
- Formula pra-registrasi `2^(Ï‰(N)-1)` bukan formula BSD standar. Untuk
  `14a1` faktor itu menghasilkan `1/3`, sedangkan LMFDB memberi `1/6`.
  Untuk `15a1` pra-registrasi menulis torsion `4`/Tamagawa `4`/`1/4`,
  sedangkan LMFDB memberi torsion `8`/Tamagawa `8`/`1/8`.
- `11a1`, `17a1`, and `19a1` cocok with LMFDB; ketiganya berkonduktor
  prima sehingga faktor tambahan bernilai 1 and kesalahan formula no
  terlihat.
- Verdict: **INCONCLUSIVE/BLOCKED**; C1/C2/C3 no terpenuhi. Tidak ada
  entri registry baru; `A-2026-0028` and `A-2026-0030` tetap `INCONCLUSIVE`.

---

## 5. Registry (ringkas)

- Entri **T** (teorema finit): `T-2026-0001`, `T-2026-0002`, `T-2026-0043`,
  `T-2026-0049` (BSD Q1 v2), `T-2026-0050` (RH scaffold Stage 2â€“4),
  `T-2026-0051` (envelope error entry + perturbasi finit Stage 5),
  `T-2026-0052` (limit tail diagonal `XC` + step tail Stage 6).
- Entri **F** (pagar): `F-2026-0001`, `F-2026-0002`.
- Entri **A** (audit/verdict): `A-2026-0001` â€¦ `A-2026-0040` (with
  `A-2026-0031` no ada), `A-2026-0043`, `A-2026-0045` (Q2 v2),
  `A-2026-0046` (Q2 v3), `A-2026-0047` (r6), and `A-2026-0048` (Q2 v4).
- `A-2026-0041` and `A-2026-0042` **no ada** (r2/r3 gagal/inconclusive).
- `A-2026-0044` **no ada** (r5 FAILED).
- Entri terbaru figure-eight: `T-2026-0043` (r4), `A-2026-0043` (audit K6
  r4), and `A-2026-0047` (r6).
- Entri terbaru twin prime: `A-2026-0048` (Q2 v4, N=10^10); sebelumnya
  `A-2026-0046` (v3, N=10^9) and `A-2026-0045` (v2, N=10^7).

---

## 6. Sisa pekerjaan which jujur

1. **RH scaffold Stage 1â€“6**: Stage 5 already menambahkan teorema perturbasi
   finit which benar-benar diperiksa kernel, tetapi ia **kondisional** on
   `A.PosDef` and limit kuadratik `A`; envelope entry hanya membatasi radius
   entry, bukan tail analitik. Stage 6/P2 already menambahkan derivasi analitik
   `|XC(n)| < 1/n^2` (in report, bukan Lean) and step tail finit/limit
   which diperiksa kernel, tetapi hanya for **diagonal `XC`**. Sisa pekerjaan
   nyata: (a) tail `S(n)`, `Wp`, `W02`, and entri off-diagonal; (b) formalisasi
   representasi integral trigamma bila diinginkan; (c) formalisasi hubungan
   sertifikat Arb ke `A.PosDef`/`hAquad`, or jalur positivity lain. Jangan
   menaikkan status RH sebelum itu ada and lulus kernel check + receipt baru.
2. **Quantum audit lanjutan**: layer statistik 16-bin already selesai
   (Ï‡Â² 7.5088/10.3984/11.592; tail 2/4/3; RESOLVED). Jika ingin klaim
   fisik, perlu studi baru with null ensemble eksplisit and prereg
   terpisah.
3. **Learnharness**: tentukan use-case nyata, latih model on dataset
   kampanye, tambahkan guard agar prediksi no pernah menggantikan
   sertifikat.
4. **Figure-eight r6** (opsional): PRREG baru sebelum kode, perbaiki M3
   (mutasi gauge which benar-benar memindahkan `I_xy`) and M8 (cap in bawah
   nilai terukur â‰ˆ2.96e4), lalu jalankan K6 M1â€“M10.
5. **BSD Q1**: recon 2026-10-25
   (`reports/BSD_Q1_RECON_2026-10-25.md`) menunjukkan paket lama
   hardcode/tautologis and nilai pra-registrasi `14a1`/`15a1` salah.
   Verifikasi identitas BSD belum dimulai; perlu pra-registrasi baru
   sebelum kode baru. `A-2026-0028`/`A-2026-0030` tetap `INCONCLUSIVE`.
6. **Twin prime Q2 lanjutan**: v2 already ALL PASS on N=10^7 (A-2026-0045).
   Target asli N=10^9 belum dikerjakan; jika dilanjutkan, butuh pra-registrasi
   baru and mesin/memori which memadai. Jangan memperluas klaim tanpa sensus
   eksak baru.
7. **MCP T2N**: modul asli already dipulihkan; `opencode.jsonc` masih menunjuk
   enam server. Perubahan MCP belum dilakukan and no boleh dicampur with
   kampanye matematika.

8. **Arsip**: artefak which dirujuk `FENCE_REGISTRY.md` tetap in `reports/`;
   `archive/README.md` mencatat kebijakan ini. Jangan memindahkan sertifikat
   sealed ke `archive/` karena akan memutus baris `sha256LF <hash> <path>`.

---

## 7. Batas klaim

Dokumen ini **bukan** bukti RH, bukan bukti BSD, bukan bukti Navierâ€“Stokes
global, bukan bukti three-body global, bukan klaim Hodge umum, bukan klaim
fisika, and bukan klaim prioritas. Semua status in atas adalah status
artefak finit which dapat diperiksa mesin, with limit which ditulis eksplisit.

---

Ditulis 2026-10-25 sebagai indeks status program.

---

## 8. Addendum 2026-10-26

Tabel Â§4.1 adalah snapshot 2026-10-25. Sejak itu:

- Target lake `lean/Stage_2_Tail_Bound.lean` and
  `lean/Stage_3_Eigenvalue_Locking.lean` (berbeda dari salinan prompt-arsip
  in `reports/RH_SCAFFOLD_NOTES/`) diganti with konstanta tail archimedean
  nyata `c=13` (`C=169/42`, `Î±=3261/2`, `K=814`) and dua record `Î»_min`
  tersertifikasi (`dim 321`, `dim 257`).
- `reports/RH_SCAFFOLD_NOTES/Stage_4_Containment_Proof.lean` sekarang
  membuktikan `test_function_l2_containment` dari hipotesis polynomial decay,
  bukan predikat placeholder `TestFunctionInL2 := True`.
- Registry `T-2026-0050` diperbarui; provenance and limit klaim ada in
  `reports/GW_TAIL_CONSTANTS_2026-10-26.md`.

Ini tetap **bukan** bukti RH. `Î±=3261/2` adalah indeks truncation
archimedean, bukan eksponen decay polinomial.

### 8.1 P2 â€” limit tail diagonal `XC` (2026-10-26)

- Klaim which dikunci in `reports/PREREG_ANALYTIC_TAIL_2026-10-26.md`:
  for `c=13`, `L=log 13`, `|XC(n)| < 1/nÂ²` for semua `n â‰¥ 1`, sehingga
  `epsilon_XC(N) = (4/L) Î£_{n>N} |XC(n)| < 2/N â†’ 0`.
- Derivasi memakai representasi integral trigamma (DLMF 5.15.1), dua
  integrasi parsial, and mayoran geometrik `Q0 < 0.28`, `Q1 < 0.143`,
  `CÏˆ â‰¤ 47/12 < 4`, `L < 2.6`, `Ï€ > 3`; no ada eksponen which in-fit.
- Grid Arb `n = 1..4096` on 512 bit: `max nÂ²|XC(n)|` terukur
  `0.0661824765â€¦` in `n=1`, in bawah 1. Record:
  `reports/analytic_tail_bound_c13.json`.
- `lean/Stage_6_Analytic_Tail.lean` memformalkan empat deklarasi:
  `sum_Ico_one_div_sq_le`, `sum_Ico_abs_le_of_pointwise`,
  `epsilon_le_of_pointwise`, `tendsto_epsilon_majorant`; `#print axioms`
  hanya memuat `propext`, `Classical.choice`, `Quot.sound`.
- Batas: ini **hanya diagonal `XC`**. `S(n)`, `Wp`, `W02`, entri off-diagonal,
  positivity matriks, spektrum zeta, and RH **no** tercakup. Batas
  pointwise adalah input analitik + numerik, bukan result kernel.


