# CURRENT AUTHORITY â€” 2026-10-26

**Status:** otoritatif sampai digantikan versi bertanggal lebih baru.
**Baseline P2:** `0b0a32c` (commit). Tag `p2-green-0b0a32c` created setelah
CI run `40261066426` hijau (lean-kernel, coq-kernel, python-tests).
**Registry r6:** `A-2026-0047` (CERTIFIED, dikonfirmasi pemilik 2026-10-26;
entri ledger ditambahkan for menutup celah `ad34cbc`).
**Menggantikan:** `reports/HANDOFF.md` sebagai source tugas aktif; target
`C/n`; induksi Stage 3; pembacaan placeholder Stage 2/3 sebagai implementasi.

**Pembaruan 2026-10-27 (D1 dikoreksi/D2):** ledger tombstone
(`reports/ARCHIVE_TOMBSTONES.md`) disinkronkan with eksekusi `995576c`,
termasuk guard `msaf/tests/test_authority_manifest.py`; status
`T-2026-0049`, `A-2026-0048`, `A-2026-0049`, and `A-2026-0050` telah dibawa
keputusan pemilik 2026-10-27 (rincian in Â§5 and `reports/DECISION_LOG.md`).

## 1. Klaim aktif

| ID | Klaim | Artefak utama | Batas |
|---|---|---|---|
| P0 | Koreksi lingkup Stage 2/3, audit aksioma per-deklarasi, and perbaikan guard CI | `5fea118`; `reports/AUDIT_2026-10-24_26_REVIEW.md`; `reports/RH_SCAFFOLD_NOTES/STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md` | Audit artefak; bukan klaim matematika baru |
| P1 / `T-2026-0051` | Envelope entry `c=13, N=160, dim=321`: `epsilon = 10^-100`, `delta = 321 * 10^-100`, `lambda_min = 3.123458832662237e-59`; lima teorema Lean | `reports/PREREG_ENTRY_ERROR_ENVELOPE_2026-10-26.md`; `msaf/entry_error_envelope.py`; `lean/Stage_5_EntryError_Perturbation.lean` | Kondisional on `A.PosDef` and `hAquad`; bukan positivity matriks Arb |
| P2 / `T-2026-0052` | `abs(XC(n)) < 1/nÂ²` and `epsilon_XC(N) = (4/L) * sum_{n>N} abs(XC(n)) < 2/N -> 0` for `c=13` | `reports/PREREG_ANALYTIC_TAIL_2026-10-26.md`; `msaf/analytic_tail_bound.py`; `reports/ANALYTIC_TAIL_BOUND_2026-10-26.md`; `lean/Stage_6_Analytic_Tail.lean` | Hanya diagonal `XC`; pointwise = kertas + grid Arb; Lean hanya tail finit and limit mayoran |
| `A-2026-0047` | Figure-eight reduced 8x8 r6: base K1-K5 r3 + K6 M1-M10 diskriminatif; `all_pass: true`, `summary: ALL PASS` | `reports/PREREG_FIGURE_EIGHT_R6_2026-10-25.md`; `msaf/figure_eight_r6.py`; `msaf/tests/test_figure_eight_r6.py`; `reports/figure_eight_r6_2026-10-25.json` | Lokal in box B and kondisional on base K1-K5 + K6; bukan global/stabilitas/chaos/KAM/fisika/RH. Prereg timing dicatat in audit Â§T6 |

### 1.1 P2 secara eksplisit

- `|XC(n)| < 1/nÂ²` adalah limit **diagonal**, bukan limit operator.
- `epsilon_XC` hanya menjumlahkan kontribusi diagonal `-(2/L) XC(n)` for
  `n > N` and `-n < -N`.
- Lean memformalkan `sum_Ico_one_div_sq_le`, `sum_Ico_abs_le_of_pointwise`,
  `epsilon_le_of_pointwise`, and `tendsto_epsilon_majorant`. Keempatnya
  lulus kernel with aksioma hanya `propext`, `Classical.choice`,
  `Quot.sound`.
- Grid Arb `n = 1..4096` on 512 bit memberi
  `max nÂ²|XC(n)| = 0.0661824765...` in `n = 1`; ini verifikasi numerik,
  bukan bukti pointwise.
- Tidak ada klaim `epsilon_XC(N) < lambda_min(N)`. Perbandingan itu no
  dibuktikan in P2.

### 1.2 r6 secara eksplisit

- Receipt `reports/figure_eight_r6_2026-10-25.json` mencatat `all_pass: true`
  and `summary: ALL PASS`; sepuluh baris K6 (M1-M10) semuanya `passed: true`.
- Base K1-K5 memakai modul and receipt r3 which in-hash ulang:
  `8eddc2bb...` and `6b0b71e9...`.
- Entri ledger `A-2026-0047` ditambahkan 2026-10-26 atas konfirmasi pemilik,
  karena commit `ad34cbc` menyebut ID itu tetapi no menulis registry.
- Batas: hanya keberadaan and keunikan lokal in dalam box B, bukan klaim
  global, stabilitas, spektrum, chaos, ergodisitas, KAM, PDE, fisika,
  prioritas, Lean/Coq, or RH. Tidak ada report formal terpisah; receipt,
  pra-registrasi, modul, and test adalah sertifikatnya.
- Catatan proses: pra-registrasi r6 in-commit bersama kode on `ad34cbc`
  (temuan audit Â§T6). Catatan itu dipertahankan; sertifikasi berlaku atas
  keputusan pemilik, bukan karena temuan itu dihapus.

## 2. Batas which no boleh dilanggar

- **Tidak ada klaim RH, Weil positivity, spektrum zeta, or lokasi nol.**
- Tidak ada klaim positivity matriks penuh, termasuk matriks Guinandâ€“Weil
  penuh.
- P1 no membuktikan bahwa matriks Arb positif-definit; `A.PosDef` and
  limit kuadratik `A` adalah hipotesis. Otoritas positivity tetap run
  `arb_mat.eig` eksternal (`all_exclude_zero = true`).
- P2 no mencakup `S(n)`, `Wp`, `W02`, entri off-diagonal, or tail
  seluruh matriks.
- P2 no memformalkan representasi integral trigamma, `psi'`, or deret
  `gX1`/`gX2` in Lean.
- Stage 4 hanya membuktikan containment LÂ² dari hipotesis polynomial decay,
  bukan containment spektrum zeta.
- Stage 3 adalah record data dua run Arb, bukan induksi dimensi. Induksi naik
  no valid karena Cauchy interlacing memberi
  `lambda_min(A_{N+1}) <= lambda_min(A_N)`.

## 3. Yang superseded

| Path / klaim | Status | Pengganti |
|---|---|---|
| `reports/HANDOFF.md` | Log sesi historis; jangan dipakai sebagai instruksi aktif | `CURRENT_AUTHORITY.md`; `reports/DECISION_LOG.md`; `reports/ARCHIVE_TOMBSTONES.md` |
| `reports/RH_SCAFFOLD_NOTES/Stage_2_Derivation_Analytic_Tail_Bound.md` | Placeholder prompt; target `C/n` salah | `lean/Stage_2_Tail_Bound.lean`; `reports/GW_TAIL_CONSTANTS_2026-10-26.md`; `reports/ANALYTIC_TAIL_BOUND_2026-10-26.md` |
| `reports/RH_SCAFFOLD_NOTES/Stage_3_Eigenvalue_Locking_Dimension_Induction.md` | Placeholder prompt; induksi no valid | `lean/Stage_3_Eigenvalue_Locking.lean`; `reports/RH_SCAFFOLD_NOTES/STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md` |
| `reports/RH_SCAFFOLD_NOTES/README_custody.md` | Catatan custody 2026-10-23; teks rusak and instruksi Stage 2/3 basi | `CURRENT_AUTHORITY.md`; `reports/RH_SCAFFOLD_NOTES/STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md` |
| `reports/RH_SCAFFOLD_NOTES/append_status.py` | Skrip satu-kali which hardcoded and already rusak | Tidak ada; status historis ada in `KERNEL_CHECK_2026-10-25.md` |
| Target `abs(XC(n)) <= C_arch / n` and tail `C_arch LÂ²/(pi N)` | Salah secara internal; tail harmonik divergen | Target `1/nÂ²` in P2 / `T-2026-0052` |

Berkas `.lean` and receipt Stage 2/3 which lama tetap disimpan sebagai
artefak historis which pernah lulus kernel; jangan menghapusnya tanpa
keputusan pemilik and tombstone. `Stage_4_Containment_Proof.lean` **bukan**
superseded: ia already ditulis ulang and hash-nya tercatat in registry
`T-2026-0050`.

Semua `SYSTEM PROMPT` in `reports/RH_SCAFFOLD_NOTES/` adalah arsip. Jangan
menjalankan Stage 1/2/3/4 prompt sebagai tugas baru tanpa pra-registrasi.
Stage 1 and Stage 4 `.lean` tetap berada in folder itu sebagai artefak which
dipertahankan; Stage 4 hash-nya tercatat in registry `T-2026-0050`, Stage 1
hanya berisi definisi (tanpa theorem). Stage 2 and Stage 3 digantikan modul in
`lean/`. `README_custody.md` (2026-10-23) adalah note custody, bukan
otoritas; instruksi Stage 2/3 in dalamnya already basi.

## 4. Protokol perubahan

1. Tambahkan keputusan bertanggal ke `reports/DECISION_LOG.md`; jangan
   menulis ulang entri lama.
2. Perbarui dokumen ini jika klaim, limit, or baseline berubah.
3. Perbarui hash in `reports/AUTHORITY_MANIFEST.json` on commit which sama.
4. Jalankan `python -m pytest msaf/tests/test_authority_manifest.py -q`,
   `test_fence_registry.py`, and anti-circularity gate.
5. Untuk pekerjaan matematika baru: commit pra-registrasi terpisah and
   dipush sebelum kode.
6. Jangan menghapus file ber-`sha256LF`; tambahkan entri registry baru or
   retract with note, lalu tombstone jika pemilik menyetujui.

## 5. Known drift and celah integritas

`reports/TARGET_STATUS_2026-10-25.md` dibekukan and hash-nya tercatat in
registry. Bagian Â§6 "Sisa pekerjaan" adalah snapshot 2026-10-25 which no
ikut diperbarui; jangan membacanya sebagai daftar tugas aktif.

| Teks beku | Keadaan sekarang | Otoritas |
|---|---|---|
| Â§6.4 menyebut r6 opsional | `reports/figure_eight_r6_2026-10-25.json` berisi `ALL PASS`; entri registry `A-2026-0047` ditambahkan 2026-10-26 atas konfirmasi pemilik | `FENCE_REGISTRY` `A-2026-0047`; commit `ad34cbc` |
| Â§6.5 menyebut verifikasi identitas BSD belum dimulai | `T-2026-0049` (BSD Q1 v2) berstatus `CERTIFIED` for 5 kurva pilot | Registry; timing pra-registrasi ditetapkan sebagai pengecualian proses oleh pemilik 2026-10-27 (`DECISION_LOG` D1) |
| Â§6.6 menyebut target twin prime N=10^9 belum dikerjakan | `A-2026-0046` (N=10^9) and `A-2026-0048` (N=10^10) berstatus `CERTIFIED` | Registry; timing pra-registrasi v4 ditetapkan sebagai pengecualian proses oleh pemilik 2026-10-27 (`DECISION_LOG` D1) |
| `README.md` baris 26-27 menyebut r6 `A-2026-0047` and Learn-harness `A-2026-0050` | r6 benar; entri `A-2026-0050` kini ada in `FENCE_REGISTRY.md`, `CERTIFIED` terbatas on **stub deterministik** (`DECISION_LOG` D2, 2026-10-27) | `README.md` baris 26 juga menyebut r7 `CERTIFIED` â€” koreksi: r7 adalah `A-2026-0049` `RETRACTED`; README diselaraskan per 2026-10-27 |

Jangan menaikkan or menurunkan status `T-2026-0049`, `A-2026-0047`,
`A-2026-0048`, `A-2026-0049`, or `A-2026-0050` secara diam-diam. Status
resmi per 2026-10-27: `T-2026-0049` and `A-2026-0048` `CERTIFIED` with
pengecualian proses tercatat; `A-2026-0047` `CERTIFIED`; `A-2026-0049`
(r7) `RETRACTED`; `A-2026-0050` `CERTIFIED` hanya for perilaku stub
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


