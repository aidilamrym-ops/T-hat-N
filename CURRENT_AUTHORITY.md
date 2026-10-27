# CURRENT AUTHORITY — 2026-10-26

**Status:** otoritatif sampai digantikan versi bertanggal lebih baru.
**Baseline P2:** `0b0a32c` (commit). Tag `p2-green-0b0a32c` dibuat setelah
CI run `40261066426` hijau (lean-kernel, coq-kernel, python-tests).
**Registry r6:** `A-2026-0047` (CERTIFIED, dikonfirmasi pemilik 2026-10-26;
entri ledger ditambahkan untuk menutup celah `ad34cbc`).
**Menggantikan:** `reports/HANDOFF.md` sebagai sumber tugas aktif; target
`C/n`; induksi Stage 3; pembacaan placeholder Stage 2/3 sebagai implementasi.

**Pembaruan 2026-10-27 (D1 dikoreksi/D2):** ledger tombstone
(`reports/ARCHIVE_TOMBSTONES.md`) disinkronkan dengan eksekusi `995576c`,
termasuk guard `msaf/tests/test_authority_manifest.py`; status
`T-2026-0049`, `A-2026-0048`, `A-2026-0049`, dan `A-2026-0050` telah dibawa
keputusan pemilik 2026-10-27 (rincian di §5 dan `reports/DECISION_LOG.md`).

## 1. Klaim aktif

| ID | Klaim | Artefak utama | Batas |
|---|---|---|---|
| P0 | Koreksi lingkup Stage 2/3, audit aksioma per-deklarasi, dan perbaikan guard CI | `5fea118`; `reports/AUDIT_2026-10-24_26_REVIEW.md`; `reports/RH_SCAFFOLD_NOTES/STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md` | Audit artefak; bukan klaim matematika baru |
| P1 / `T-2026-0051` | Envelope entry `c=13, N=160, dim=321`: `epsilon = 10^-100`, `delta = 321 * 10^-100`, `lambda_min = 3.123458832662237e-59`; lima teorema Lean | `reports/PREREG_ENTRY_ERROR_ENVELOPE_2026-10-26.md`; `msaf/entry_error_envelope.py`; `lean/Stage_5_EntryError_Perturbation.lean` | Kondisional pada `A.PosDef` dan `hAquad`; bukan positivity matriks Arb |
| P2 / `T-2026-0052` | `abs(XC(n)) < 1/n²` dan `epsilon_XC(N) = (4/L) * sum_{n>N} abs(XC(n)) < 2/N -> 0` untuk `c=13` | `reports/PREREG_ANALYTIC_TAIL_2026-10-26.md`; `msaf/analytic_tail_bound.py`; `reports/ANALYTIC_TAIL_BOUND_2026-10-26.md`; `lean/Stage_6_Analytic_Tail.lean` | Hanya diagonal `XC`; pointwise = kertas + grid Arb; Lean hanya tail finit dan limit mayoran |
| `A-2026-0047` | Figure-eight reduced 8x8 r6: base K1-K5 r3 + K6 M1-M10 diskriminatif; `all_pass: true`, `summary: ALL PASS` | `reports/PREREG_FIGURE_EIGHT_R6_2026-10-25.md`; `msaf/figure_eight_r6.py`; `msaf/tests/test_figure_eight_r6.py`; `reports/figure_eight_r6_2026-10-25.json` | Lokal di box B dan kondisional pada base K1-K5 + K6; bukan global/stabilitas/chaos/KAM/fisika/RH. Prereg timing dicatat di audit §T6 |

### 1.1 P2 secara eksplisit

- `|XC(n)| < 1/n²` adalah batas **diagonal**, bukan batas operator.
- `epsilon_XC` hanya menjumlahkan kontribusi diagonal `-(2/L) XC(n)` untuk
  `n > N` dan `-n < -N`.
- Lean memformalkan `sum_Ico_one_div_sq_le`, `sum_Ico_abs_le_of_pointwise`,
  `epsilon_le_of_pointwise`, dan `tendsto_epsilon_majorant`. Keempatnya
  lulus kernel dengan aksioma hanya `propext`, `Classical.choice`,
  `Quot.sound`.
- Grid Arb `n = 1..4096` pada 512 bit memberi
  `max n²|XC(n)| = 0.0661824765...` di `n = 1`; ini verifikasi numerik,
  bukan bukti pointwise.
- Tidak ada klaim `epsilon_XC(N) < lambda_min(N)`. Perbandingan itu tidak
  dibuktikan di P2.

### 1.2 r6 secara eksplisit

- Receipt `reports/figure_eight_r6_2026-10-25.json` mencatat `all_pass: true`
  dan `summary: ALL PASS`; sepuluh baris K6 (M1-M10) semuanya `passed: true`.
- Base K1-K5 memakai modul dan receipt r3 yang di-hash ulang:
  `8eddc2bb...` dan `6b0b71e9...`.
- Entri ledger `A-2026-0047` ditambahkan 2026-10-26 atas konfirmasi pemilik,
  karena commit `ad34cbc` menyebut ID itu tetapi tidak menulis registry.
- Batas: hanya keberadaan dan keunikan lokal di dalam box B, bukan klaim
  global, stabilitas, spektrum, chaos, ergodisitas, KAM, PDE, fisika,
  prioritas, Lean/Coq, atau RH. Tidak ada laporan formal terpisah; receipt,
  pra-registrasi, modul, dan test adalah sertifikatnya.
- Catatan proses: pra-registrasi r6 di-commit bersama kode pada `ad34cbc`
  (temuan audit §T6). Catatan itu dipertahankan; sertifikasi berlaku atas
  keputusan pemilik, bukan karena temuan itu dihapus.

## 2. Batas yang tidak boleh dilanggar

- **Tidak ada klaim RH, Weil positivity, spektrum zeta, atau lokasi nol.**
- Tidak ada klaim positivity matriks penuh, termasuk matriks Guinand–Weil
  penuh.
- P1 tidak membuktikan bahwa matriks Arb positif-definit; `A.PosDef` dan
  batas kuadratik `A` adalah hipotesis. Otoritas positivity tetap run
  `arb_mat.eig` eksternal (`all_exclude_zero = true`).
- P2 tidak mencakup `S(n)`, `Wp`, `W02`, entri off-diagonal, atau tail
  seluruh matriks.
- P2 tidak memformalkan representasi integral trigamma, `psi'`, atau deret
  `gX1`/`gX2` di Lean.
- Stage 4 hanya membuktikan containment L² dari hipotesis polynomial decay,
  bukan containment spektrum zeta.
- Stage 3 adalah record data dua run Arb, bukan induksi dimensi. Induksi naik
  tidak valid karena Cauchy interlacing memberi
  `lambda_min(A_{N+1}) <= lambda_min(A_N)`.

## 3. Yang superseded

| Path / klaim | Status | Pengganti |
|---|---|---|
| `reports/HANDOFF.md` | Log sesi historis; jangan dipakai sebagai instruksi aktif | `CURRENT_AUTHORITY.md`; `reports/DECISION_LOG.md`; `reports/ARCHIVE_TOMBSTONES.md` |
| `reports/RH_SCAFFOLD_NOTES/Stage_2_Derivation_Analytic_Tail_Bound.md` | Placeholder prompt; target `C/n` salah | `lean/Stage_2_Tail_Bound.lean`; `reports/GW_TAIL_CONSTANTS_2026-10-26.md`; `reports/ANALYTIC_TAIL_BOUND_2026-10-26.md` |
| `reports/RH_SCAFFOLD_NOTES/Stage_3_Eigenvalue_Locking_Dimension_Induction.md` | Placeholder prompt; induksi tidak valid | `lean/Stage_3_Eigenvalue_Locking.lean`; `reports/RH_SCAFFOLD_NOTES/STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md` |
| `reports/RH_SCAFFOLD_NOTES/README_custody.md` | Catatan custody 2026-10-23; teks rusak dan instruksi Stage 2/3 basi | `CURRENT_AUTHORITY.md`; `reports/RH_SCAFFOLD_NOTES/STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md` |
| `reports/RH_SCAFFOLD_NOTES/append_status.py` | Skrip satu-kali yang hardcoded dan sudah rusak | Tidak ada; status historis ada di `KERNEL_CHECK_2026-10-25.md` |
| Target `abs(XC(n)) <= C_arch / n` dan tail `C_arch L²/(pi N)` | Salah secara internal; tail harmonik divergen | Target `1/n²` di P2 / `T-2026-0052` |

Berkas `.lean` dan receipt Stage 2/3 yang lama tetap disimpan sebagai
artefak historis yang pernah lulus kernel; jangan menghapusnya tanpa
keputusan pemilik dan tombstone. `Stage_4_Containment_Proof.lean` **bukan**
superseded: ia sudah ditulis ulang dan hash-nya tercatat di registry
`T-2026-0050`.

Semua `SYSTEM PROMPT` di `reports/RH_SCAFFOLD_NOTES/` adalah arsip. Jangan
menjalankan Stage 1/2/3/4 prompt sebagai tugas baru tanpa pra-registrasi.
Stage 1 dan Stage 4 `.lean` tetap berada di folder itu sebagai artefak yang
dipertahankan; Stage 4 hash-nya tercatat di registry `T-2026-0050`, Stage 1
hanya berisi definisi (tanpa theorem). Stage 2 dan Stage 3 digantikan modul di
`lean/`. `README_custody.md` (2026-10-23) adalah catatan custody, bukan
otoritas; instruksi Stage 2/3 di dalamnya sudah basi.

## 4. Protokol perubahan

1. Tambahkan keputusan bertanggal ke `reports/DECISION_LOG.md`; jangan
   menulis ulang entri lama.
2. Perbarui dokumen ini jika klaim, batas, atau baseline berubah.
3. Perbarui hash di `reports/AUTHORITY_MANIFEST.json` pada commit yang sama.
4. Jalankan `python -m pytest msaf/tests/test_authority_manifest.py -q`,
   `test_fence_registry.py`, dan anti-circularity gate.
5. Untuk pekerjaan matematika baru: commit pra-registrasi terpisah dan
   dipush sebelum kode.
6. Jangan menghapus file ber-`sha256LF`; tambahkan entri registry baru atau
   retract dengan catatan, lalu tombstone jika pemilik menyetujui.

## 5. Known drift dan celah integritas

`reports/TARGET_STATUS_2026-10-25.md` dibekukan dan hash-nya tercatat di
registry. Bagian §6 "Sisa pekerjaan" adalah snapshot 2026-10-25 yang tidak
ikut diperbarui; jangan membacanya sebagai daftar tugas aktif.

| Teks beku | Keadaan sekarang | Otoritas |
|---|---|---|
| §6.4 menyebut r6 opsional | `reports/figure_eight_r6_2026-10-25.json` berisi `ALL PASS`; entri registry `A-2026-0047` ditambahkan 2026-10-26 atas konfirmasi pemilik | `FENCE_REGISTRY` `A-2026-0047`; commit `ad34cbc` |
| §6.5 menyebut verifikasi identitas BSD belum dimulai | `T-2026-0049` (BSD Q1 v2) berstatus `CERTIFIED` untuk 5 kurva pilot | Registry; timing pra-registrasi ditetapkan sebagai pengecualian proses oleh pemilik 2026-10-27 (`DECISION_LOG` D1) |
| §6.6 menyebut target twin prime N=10^9 belum dikerjakan | `A-2026-0046` (N=10^9) dan `A-2026-0048` (N=10^10) berstatus `CERTIFIED` | Registry; timing pra-registrasi v4 ditetapkan sebagai pengecualian proses oleh pemilik 2026-10-27 (`DECISION_LOG` D1) |
| `README.md` baris 26-27 menyebut r6 `A-2026-0047` dan Learn-harness `A-2026-0050` | r6 benar; entri `A-2026-0050` kini ada di `FENCE_REGISTRY.md`, `CERTIFIED` terbatas pada **stub deterministik** (`DECISION_LOG` D2, 2026-10-27) | `README.md` baris 26 juga menyebut r7 `CERTIFIED` — koreksi: r7 adalah `A-2026-0049` `RETRACTED`; README diselaraskan per 2026-10-27 |

Jangan menaikkan atau menurunkan status `T-2026-0049`, `A-2026-0047`,
`A-2026-0048`, `A-2026-0049`, atau `A-2026-0050` secara diam-diam. Status
resmi per 2026-10-27: `T-2026-0049` dan `A-2026-0048` `CERTIFIED` dengan
pengecualian proses tercatat; `A-2026-0047` `CERTIFIED`; `A-2026-0049`
(r7) `RETRACTED`; `A-2026-0050` `CERTIFIED` hanya untuk perilaku stub
deterministik (bukan klaim belajar/ML). Perubahan lanjut hanya lewat entri
`reports/DECISION_LOG.md` bertanggal, disusul sinkronisasi dokumen ini.

## 6. Rujukan

- Ledger sertifikat: `reports/FENCE_REGISTRY.md` (`A-2026-0047`,
  `T-2026-0050`, `T-2026-0051`, `T-2026-0052`).
- Status target beku: `reports/TARGET_STATUS_2026-10-25.md`.
- Audit jendela 2026-10-24..26: `reports/AUDIT_2026-10-24_26_REVIEW.md`.
- Koreksi lingkup Stage 2/3:
  `reports/RH_SCAFFOLD_NOTES/STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md`.
- P1: `reports/ENTRY_ERROR_ENVELOPE_2026-10-26.md`.
- P2: `reports/ANALYTIC_TAIL_BOUND_2026-10-26.md`.
- r6: `reports/PREREG_FIGURE_EIGHT_R6_2026-10-25.md`;
  `reports/figure_eight_r6_2026-10-25.json`.
