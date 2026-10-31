# Archive Tombstones

Catatan file which dihapus, diganti stub, or dinyatakan historis. Lapisan
authority ini created with prinsip **aditif**: eksekusi tombstone hanya
berlaku setelah persetujuan pemilik which tercatat in
`reports/DECISION_LOG.md`, and entri which telah dieksekusi dicatat on section
"Tombstone which already dieksekusi" in bawah.

## Skema

| Path | Status | Pengganti | Recovery | Tanggal | Keputusan |
|---|---|---|---|---|---|
| `<path>` | `tombstoned` / `stubbed` / `historical` | `<path or dokumen>` | `git show <commit>:<path>` | `YYYY-MM-DD` | `<ID/log entry>` |

Aturan:

- File with baris `sha256LF` in `reports/FENCE_REGISTRY.md` **no boleh**
  dihapus tanpa memperbarui registry and menjalankan guard.
- Receipt and file Lean which pernah lulus kernel tetap disimpan sebagai
  artefak historis, meskipun prompt which melahirkannya already superseded.
- Setiap tombstone harus menyebut commit recovery which masih reachable dari
  `main`, bukan hash which hanya ada in reflog lokal.

## Tombstone which already dieksekusi

| Path | Status | Pengganti | Recovery | Tanggal | Keputusan |
|---|---|---|---|---|---|
| `reports/RH_SCAFFOLD_NOTES/Stage_2_Derivation_Analytic_Tail_Bound.md` | `tombstoned` | `lean/Stage_2_Tail_Bound.lean`; `reports/GW_TAIL_CONSTANTS_2026-10-26.md`; `reports/ANALYTIC_TAIL_BOUND_2026-10-26.md` | `git show 995576c~1:reports/RH_SCAFFOLD_NOTES/Stage_2_Derivation_Analytic_Tail_Bound.md` | 2026-10-26 | `995576c` (Phase 2), atas persetujuan pemilik on tabel "Kandidat which disetujui pemilik (2026-10-26)" |
| `reports/RH_SCAFFOLD_NOTES/Stage_3_Eigenvalue_Locking_Dimension_Induction.md` | `tombstoned` | `lean/Stage_3_Eigenvalue_Locking.lean`; `reports/RH_SCAFFOLD_NOTES/STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md` | `git show 995576c~1:reports/RH_SCAFFOLD_NOTES/Stage_3_Eigenvalue_Locking_Dimension_Induction.md` | 2026-10-26 | `995576c` (Phase 2), atas persetujuan pemilik (tabel kandidat 2026-10-26) |
| `reports/RH_SCAFFOLD_NOTES/append_status.py` | `tombstoned` | Tidak ada; status historis ada in `reports/RH_SCAFFOLD_NOTES/KERNEL_CHECK_2026-10-25.md` | `git show 995576c~1:reports/RH_SCAFFOLD_NOTES/append_status.py` | 2026-10-26 | `995576c` (Phase 2), atas persetujuan pemilik (tabel kandidat 2026-10-26) |
| `reports/HANDOFF.md` | `stubbed` | `CURRENT_AUTHORITY.md`; `reports/DECISION_LOG.md`; file ini | `git show 995576c~1:reports/HANDOFF.md` (log sesi lengkap) | 2026-10-26 | `995576c` (Phase 2), atas persetujuan pemilik (tabel kandidat 2026-10-26) |
| `reports/RH_SCAFFOLD_NOTES/README_custody.md` | `stubbed` | `reports/RH_SCAFFOLD_NOTES/STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md` | `git show 995576c~1:reports/RH_SCAFFOLD_NOTES/README_custody.md` (versi pra-stub) | 2026-10-26 | `995576c` (Phase 2), atas persetujuan pemilik (tabel kandidat 2026-10-26) |
| `msaf/lmbig.txt` | `tombstoned` | `reports/lambda_min_eig_ladder_big.json` (data dim 257) | `git show feee3ce:msaf/lmbig.txt` | 2026-10-28 | Housekeeping 2026-10-28; dump konsol, no dirujuk, data ada in JSON |
| `msaf/lmb3000.txt` | `tombstoned` | `reports/lambda_min_ladder_p3000.json` | `git show f56f25f:msaf/lmb3000.txt` | 2026-10-28 | Housekeeping 2026-10-28; dump konsol, no dirujuk, data ada in JSON |
| `msaf/ladder9000.txt` | `tombstoned` | `reports/lambda_min_eig_ladder_9000.json`; `reports/gw_route_s_ladder_9000.json` | `git show f56f25f:msaf/ladder9000.txt` | 2026-10-28 | Housekeeping 2026-10-28; dump konsol, no dirujuk, data ada in JSON |
| `msaf/ladders6000.txt` | `tombstoned` | `reports/lambda_min_eig_ladder.json` | `git show f56f25f:msaf/ladders6000.txt` | 2026-10-28 | Housekeeping 2026-10-28; dump konsol, no dirujuk, data ada in JSON |
| `reports/TAW_clean_worktree_suite.txt` | `tombstoned` | Tidak ada; output workspace `TAW-clean`, bukan artefak repo ini | `git show ffd79f4:reports/TAW_clean_worktree_suite.txt` | 2026-10-28 | Housekeeping 2026-10-28; output suite workspace lain, no dirujuk |
| `reports/c4_s20261005_stderr.log` | `tombstoned` | `reports/c4_s20261005_stdout.log` (baris DONE exit=0) | `git show 19fe938:reports/c4_s20261005_stderr.log` | 2026-10-28 | Housekeeping 2026-10-28; file nol byte, no memuat informasi |
| `reports/c4_s20261006_stderr.log` | `tombstoned` | `reports/c4_s20261006_stdout.log` (baris DONE exit=0) | `git show 19fe938:reports/c4_s20261006_stderr.log` | 2026-10-28 | Housekeeping 2026-10-28; file nol byte, no memuat informasi |
| `reports/c4_s20261007_stderr.log` | `tombstoned` | `reports/c4_s20261007_stdout.log` (baris DONE exit=0) | `git show 19fe938:reports/c4_s20261007_stderr.log` | 2026-10-28 | Housekeeping 2026-10-28; file nol byte, no memuat informasi |
| `reports/c4_s20261008_stderr.log` | `tombstoned` | `reports/c4_s20261008_stdout.log` (baris DONE exit=0) | `git show 19fe938:reports/c4_s20261008_stderr.log` | 2026-10-28 | Housekeeping 2026-10-28; file nol byte, no memuat informasi |
| `reports/c4_s20261009_stderr.log` | `tombstoned` | `reports/c4_s20261009_stdout.log` (baris DONE exit=0) | `git show 19fe938:reports/c4_s20261009_stderr.log` | 2026-10-28 | Housekeeping 2026-10-28; file nol byte, no memuat informasi |

Catatan housekeeping 2026-10-28: sepuluh baris in atas adalah dump konsol
and file stderr nol byte which no dirujuk oleh kode, test, workflow,
or baris `sha256LF`. Data numeriknya tetap ada in JSON/report which
tercatat; salinan karantina eksternal and hash-nya disimpan in
`C:\Users\usER\AppData\Local\Temp\opencode\quarantine_T-hat-N_2026-10-28\`.
Berkas build Coq which no in-track (`formal_bridge/*.vo`, `*.glob`,
`*.vok`, `*.vos`, `.*.aux`) dihapus karena dapat dibangun ulang dari
source `.v`; file bersertifikat no disentuh.

Catatan sinkronisasi 2026-10-27 (D1): guard
`msaf/tests/test_authority_manifest.py` no lagi mengunci pernyataan
"belum ada tombstone which dieksekusi"; ia verifying bahwa tabel in atas
ada and menyebut commit eksekusi `995576c`. State in
`reports/AUTHORITY_MANIFEST.json` for kelima path ini selaras with disk
(`tombstoned` / `stubbed`).

## Kandidat which disetujui pemilik (2026-10-26)

Pemilik menyetujui daftar ini with syarat setiap file diperiksa ulang
sebelum dihapus. Pemeriksaan itu already dijalankan; hasilnya ada in section
"Verifikasi sebelum eksekusi" in bawah. Tabel ini **bukan** izin for
menghapus file lain in luar daftar.

| Path | Rencana | Alasan | Pengganti | Recovery |
|---|---|---|---|---|
| `reports/HANDOFF.md` | Ganti stub | Log sesi 2026-10-15..24, 2.913 baris; memuat instruksi basi "baca file ini dulu" and target which already dikoreksi | Stub which menunjuk `CURRENT_AUTHORITY.md`, `reports/DECISION_LOG.md`, and file ini | `git show 0b0a32c:reports/HANDOFF.md` |
| `reports/RH_SCAFFOLD_NOTES/Stage_2_Derivation_Analytic_Tail_Bound.md` | Tombstone | Prompt placeholder; target `C/n` salah; implementasi aktif ada in `lean/Stage_2_Tail_Bound.lean` | `lean/Stage_2_Tail_Bound.lean`; `reports/GW_TAIL_CONSTANTS_2026-10-26.md`; `reports/ANALYTIC_TAIL_BOUND_2026-10-26.md` | `git show 0b0a32c:reports/RH_SCAFFOLD_NOTES/Stage_2_Derivation_Analytic_Tail_Bound.md` |
| `reports/RH_SCAFFOLD_NOTES/Stage_3_Eigenvalue_Locking_Dimension_Induction.md` | Tombstone | Prompt placeholder; induksi naik no valid karena Cauchy interlacing | `lean/Stage_3_Eigenvalue_Locking.lean`; `reports/RH_SCAFFOLD_NOTES/STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md` | `git show 0b0a32c:reports/RH_SCAFFOLD_NOTES/Stage_3_Eigenvalue_Locking_Dimension_Induction.md` |
| `reports/RH_SCAFFOLD_NOTES/README_custody.md` | Ganti stub | Catatan custody 2026-10-23; teks rusak, masih berstatus "USULAN", and instruksi Stage 2/3 in dalamnya basi | Stub custody historis which menunjuk `CURRENT_AUTHORITY.md` and `STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md` | `git show 0b0a32c:reports/RH_SCAFFOLD_NOTES/README_custody.md` |
| `reports/RH_SCAFFOLD_NOTES/append_status.py` | Tombstone | Skrip satu-kali, path hardcoded `D:/...`, memakai `receipt["sha256"]` which no ada, no dirujuk apa pun | Tidak ada; status historis already ada in `KERNEL_CHECK_2026-10-25.md` | `git show 0b0a32c:reports/RH_SCAFFOLD_NOTES/append_status.py` |

## Verifikasi sebelum eksekusi (2026-10-26)

1. **Registry:** no ada baris `sha256LF` which menunjuk kelima path in atas.
   Satu-satunya `sha256LF` in `reports/RH_SCAFFOLD_NOTES/` adalah
   `Stage_4_Containment_Proof.lean` (`5786929a...`, registry `T-2026-0050`);
   file itu tetap disimpan.
2. **Dependensi:** `git grep` atas `msaf/tests`, `.github`, and seluruh tree
   no menemukan test or workflow which membaca kelima path itu.
   `generate_receipts.py` hanya membaca file `.lean`.
3. **Recovery:** kelima file ada in commit `0b0a32c`, and `origin/main`
   berada tepat in `0b0a32c`; `git show 0b0a32c:<path>` dapat dipakai.
4. **Isi prompt:** Stage 2 masih memasang `SYSTEM PROMPT` + `MANDATORY
   EXECUTION STEPS` with target `C_arch/n`; Stage 3 masih meminta induksi
   naik. Addendum koreksi hanya ada setelahnya, sehingga prompt no aman
   dibiarkan sebagai instruksi.
5. **Yang no disentuh:** `mcp/t2n/repokeeper.py` hanya menulis outbox
   `mcp/out/handoff/`; ia no merujuk `reports/HANDOFF.md`, jadi no
   diubah.

## Yang sengaja no dihapus

| Path | Alasan |
|---|---|
| `reports/RH_SCAFFOLD_NOTES/Stage_2_Derivation_Analytic_Tail_Bound.lean` | Pernah lulus kernel and hash-nya tercatat in `KERNEL_CHECK_2026-10-25.md`; simpan sebagai artefak historis |
| `reports/RH_SCAFFOLD_NOTES/Stage_3_Eigenvalue_Locking_Dimension_Induction.lean` | Sama; pernah lulus kernel and hash-nya tercatat |
| `reports/RH_SCAFFOLD_NOTES/*_receipt.json` | Receipt kernel-check historis; bukan instruksi aktif |
| `reports/RH_SCAFFOLD_NOTES/Stage_4_Containment_Proof.lean` | Hash-nya ada in registry `T-2026-0050`; already ditulis ulang, bukan superseded |
| `reports/RH_SCAFFOLD_NOTES/STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md` | Dokumen koreksi otoritatif for Stage 2/3 |
| `reports/TARGET_STATUS_2026-10-25.md` | Status beku; hash-nya tercatat in registry `T-2026-0052` |

## Penanda historis paket koreksi (D4, 2026-10-27)

| Path | Status | Pengganti | Recovery | Tanggal | Keputusan |
|---|---|---|---|---|---|
| `reports/RH_SCAFFOLD_NOTES/Stage_4_Containment_Proof_receipt.json` | `historical` | `reports/RH_SCAFFOLD_NOTES/KERNEL_CHECK_2026-10-25.md`; `.lean` Stage 4 tetap tersegel sebagai artefak (`T-2026-0050`) | `git show a55fe79:reports/RH_SCAFFOLD_NOTES/Stage_4_Containment_Proof_receipt.json` (byte identik with file saat ini, sha256LF no berubah) | 2026-10-27 | Paket koreksi D4 2026-10-27 atas persetujuan pemilik; marked via ledger, byte file no diubah |

Catatan D4: header peringatan historis ditambahkan (aditif) on section atas
`Stage_1_Formalization_Test_Function_Space.md`,
`Stage_4_Containment_Proof.md`, and docstring
`generate_receipts.py` (jangan dieksekusi). Byte receipt and kode skrip
no diubah.

## Penyisihan sisa kerja 2026-10-31 (tanpa artefak tersertifikasi)

Empat path untracked disisihkan atas keputusan pemilik 2026-10-31. Tidak satu
pun pernah masuk commit, tidak ada baris `sha256LF` yang merujuknya, dan tidak
ada test/workflow yang membacanya. Karena tidak pernah di-commit, tidak ada
recovery commit; hash di bawah adalah hash byte saat penyisihan (CRLF
dinormalisasi ke LF, sama with konvensi registry).

| Path | Status | sha256LF saat disisihkan | Pengganti / alasan |
|---|---|---|---|
| `reports/RH_SCAFFOLD_NOTES/STAGE_7_TAIL_EXTENSION.md` | `tombstoned` | `fe48ce1fa00d9855b1c36982767241829ec7f0a50d4de5f90dc129d1f7732ac2` | Rencana Task A-D which already dieksekusi: `reports/PREREG_TAIL_EXTENSION_2026-10-30.md` and `lean/Stage_7_Tail_Extension.lean` (blok sertifikat in registry). Dokumen ini no boleh dijalankan sebagai instruksi baru. |
| `msaf/chrono_bridge.py` | `tombstoned` | `7354a4128c16f13876c15e37921acac7b6041a8565e81537c75f953059d6bf64` | Duplikat byte-identik (modulo line ending) dari `msaf/bridge/chrono_bridge.py` which tracked; bukan artefak and no dirujuk. |
| `msaf/reports/RELEASE_v1.41.0-alpha.md` | `tombstoned` | `87823b5a456c66ddfde0fa9cf534833adf87ec88f926e71d330e2612a5676706` | Template rilis which mengklaim "CI passes; all tests green" tanpa dasar; no dirujuk and no boleh dipakai sebagai bukti status CI. |
| `reports/anti_circularity_gate_current.log` | `tombstoned` | `93634a02bc0652601dc1a761d9123d537525bd8009050f06a4416e340ac29892` | Log runtime which dapat dibuat ulang; bukan bukti tersertifikasi and no dirujuk registry. |


