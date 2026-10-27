# Archive Tombstones

Catatan berkas yang dihapus, diganti stub, atau dinyatakan historis. Lapisan
authority ini dibuat dengan prinsip **aditif**: eksekusi tombstone hanya
berlaku setelah persetujuan pemilik yang tercatat di
`reports/DECISION_LOG.md`, dan entri yang telah dieksekusi dicatat pada bagian
"Tombstone yang sudah dieksekusi" di bawah.

## Skema

| Path | Status | Pengganti | Recovery | Tanggal | Keputusan |
|---|---|---|---|---|---|
| `<path>` | `tombstoned` / `stubbed` / `historical` | `<path atau dokumen>` | `git show <commit>:<path>` | `YYYY-MM-DD` | `<ID/log entry>` |

Aturan:

- File dengan baris `sha256LF` di `reports/FENCE_REGISTRY.md` **tidak boleh**
  dihapus tanpa memperbarui registry dan menjalankan guard.
- Receipt dan file Lean yang pernah lulus kernel tetap disimpan sebagai
  artefak historis, meskipun prompt yang melahirkannya sudah superseded.
- Setiap tombstone harus menyebut commit recovery yang masih reachable dari
  `main`, bukan hash yang hanya ada di reflog lokal.

## Tombstone yang sudah dieksekusi

| Path | Status | Pengganti | Recovery | Tanggal | Keputusan |
|---|---|---|---|---|---|
| `reports/RH_SCAFFOLD_NOTES/Stage_2_Derivation_Analytic_Tail_Bound.md` | `tombstoned` | `lean/Stage_2_Tail_Bound.lean`; `reports/GW_TAIL_CONSTANTS_2026-10-26.md`; `reports/ANALYTIC_TAIL_BOUND_2026-10-26.md` | `git show 995576c~1:reports/RH_SCAFFOLD_NOTES/Stage_2_Derivation_Analytic_Tail_Bound.md` | 2026-10-26 | `995576c` (Phase 2), atas persetujuan pemilik pada tabel "Kandidat yang disetujui pemilik (2026-10-26)" |
| `reports/RH_SCAFFOLD_NOTES/Stage_3_Eigenvalue_Locking_Dimension_Induction.md` | `tombstoned` | `lean/Stage_3_Eigenvalue_Locking.lean`; `reports/RH_SCAFFOLD_NOTES/STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md` | `git show 995576c~1:reports/RH_SCAFFOLD_NOTES/Stage_3_Eigenvalue_Locking_Dimension_Induction.md` | 2026-10-26 | `995576c` (Phase 2), atas persetujuan pemilik (tabel kandidat 2026-10-26) |
| `reports/RH_SCAFFOLD_NOTES/append_status.py` | `tombstoned` | Tidak ada; status historis ada di `reports/RH_SCAFFOLD_NOTES/KERNEL_CHECK_2026-10-25.md` | `git show 995576c~1:reports/RH_SCAFFOLD_NOTES/append_status.py` | 2026-10-26 | `995576c` (Phase 2), atas persetujuan pemilik (tabel kandidat 2026-10-26) |
| `reports/HANDOFF.md` | `stubbed` | `CURRENT_AUTHORITY.md`; `reports/DECISION_LOG.md`; file ini | `git show 995576c~1:reports/HANDOFF.md` (log sesi lengkap) | 2026-10-26 | `995576c` (Phase 2), atas persetujuan pemilik (tabel kandidat 2026-10-26) |
| `reports/RH_SCAFFOLD_NOTES/README_custody.md` | `stubbed` | `reports/RH_SCAFFOLD_NOTES/STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md` | `git show 995576c~1:reports/RH_SCAFFOLD_NOTES/README_custody.md` (versi pra-stub) | 2026-10-26 | `995576c` (Phase 2), atas persetujuan pemilik (tabel kandidat 2026-10-26) |
| `msaf/lmbig.txt` | `tombstoned` | `reports/lambda_min_eig_ladder_big.json` (data dim 257) | `git show feee3ce:msaf/lmbig.txt` | 2026-10-28 | Housekeeping 2026-10-28; dump konsol, tidak dirujuk, data ada di JSON |
| `msaf/lmb3000.txt` | `tombstoned` | `reports/lambda_min_ladder_p3000.json` | `git show f56f25f:msaf/lmb3000.txt` | 2026-10-28 | Housekeeping 2026-10-28; dump konsol, tidak dirujuk, data ada di JSON |
| `msaf/ladder9000.txt` | `tombstoned` | `reports/lambda_min_eig_ladder_9000.json`; `reports/gw_route_s_ladder_9000.json` | `git show f56f25f:msaf/ladder9000.txt` | 2026-10-28 | Housekeeping 2026-10-28; dump konsol, tidak dirujuk, data ada di JSON |
| `msaf/ladders6000.txt` | `tombstoned` | `reports/lambda_min_eig_ladder.json` | `git show f56f25f:msaf/ladders6000.txt` | 2026-10-28 | Housekeeping 2026-10-28; dump konsol, tidak dirujuk, data ada di JSON |
| `reports/TAW_clean_worktree_suite.txt` | `tombstoned` | Tidak ada; output workspace `TAW-clean`, bukan artefak repo ini | `git show ffd79f4:reports/TAW_clean_worktree_suite.txt` | 2026-10-28 | Housekeeping 2026-10-28; output suite workspace lain, tidak dirujuk |
| `reports/c4_s20261005_stderr.log` | `tombstoned` | `reports/c4_s20261005_stdout.log` (baris DONE exit=0) | `git show 19fe938:reports/c4_s20261005_stderr.log` | 2026-10-28 | Housekeeping 2026-10-28; berkas nol byte, tidak memuat informasi |
| `reports/c4_s20261006_stderr.log` | `tombstoned` | `reports/c4_s20261006_stdout.log` (baris DONE exit=0) | `git show 19fe938:reports/c4_s20261006_stderr.log` | 2026-10-28 | Housekeeping 2026-10-28; berkas nol byte, tidak memuat informasi |
| `reports/c4_s20261007_stderr.log` | `tombstoned` | `reports/c4_s20261007_stdout.log` (baris DONE exit=0) | `git show 19fe938:reports/c4_s20261007_stderr.log` | 2026-10-28 | Housekeeping 2026-10-28; berkas nol byte, tidak memuat informasi |
| `reports/c4_s20261008_stderr.log` | `tombstoned` | `reports/c4_s20261008_stdout.log` (baris DONE exit=0) | `git show 19fe938:reports/c4_s20261008_stderr.log` | 2026-10-28 | Housekeeping 2026-10-28; berkas nol byte, tidak memuat informasi |
| `reports/c4_s20261009_stderr.log` | `tombstoned` | `reports/c4_s20261009_stdout.log` (baris DONE exit=0) | `git show 19fe938:reports/c4_s20261009_stderr.log` | 2026-10-28 | Housekeeping 2026-10-28; berkas nol byte, tidak memuat informasi |

Catatan housekeeping 2026-10-28: sepuluh baris di atas adalah dump konsol
dan berkas stderr nol byte yang tidak dirujuk oleh kode, test, workflow,
atau baris `sha256LF`. Data numeriknya tetap ada di JSON/report yang
tercatat; salinan karantina eksternal dan hash-nya disimpan di
`C:\Users\usER\AppData\Local\Temp\opencode\quarantine_T-hat-N_2026-10-28\`.
Berkas build Coq yang tidak di-track (`formal_bridge/*.vo`, `*.glob`,
`*.vok`, `*.vos`, `.*.aux`) dihapus karena dapat dibangun ulang dari
sumber `.v`; berkas bersertifikat tidak disentuh.

Catatan sinkronisasi 2026-10-27 (D1): guard
`msaf/tests/test_authority_manifest.py` tidak lagi mengunci pernyataan
"belum ada tombstone yang dieksekusi"; ia memverifikasi bahwa tabel di atas
ada dan menyebut commit eksekusi `995576c`. State di
`reports/AUTHORITY_MANIFEST.json` untuk kelima path ini selaras dengan disk
(`tombstoned` / `stubbed`).

## Kandidat yang disetujui pemilik (2026-10-26)

Pemilik menyetujui daftar ini dengan syarat setiap berkas diperiksa ulang
sebelum dihapus. Pemeriksaan itu sudah dijalankan; hasilnya ada di bagian
"Verifikasi sebelum eksekusi" di bawah. Tabel ini **bukan** izin untuk
menghapus berkas lain di luar daftar.

| Path | Rencana | Alasan | Pengganti | Recovery |
|---|---|---|---|---|
| `reports/HANDOFF.md` | Ganti stub | Log sesi 2026-10-15..24, 2.913 baris; memuat instruksi basi "baca berkas ini dulu" dan target yang sudah dikoreksi | Stub yang menunjuk `CURRENT_AUTHORITY.md`, `reports/DECISION_LOG.md`, dan file ini | `git show 0b0a32c:reports/HANDOFF.md` |
| `reports/RH_SCAFFOLD_NOTES/Stage_2_Derivation_Analytic_Tail_Bound.md` | Tombstone | Prompt placeholder; target `C/n` salah; implementasi aktif ada di `lean/Stage_2_Tail_Bound.lean` | `lean/Stage_2_Tail_Bound.lean`; `reports/GW_TAIL_CONSTANTS_2026-10-26.md`; `reports/ANALYTIC_TAIL_BOUND_2026-10-26.md` | `git show 0b0a32c:reports/RH_SCAFFOLD_NOTES/Stage_2_Derivation_Analytic_Tail_Bound.md` |
| `reports/RH_SCAFFOLD_NOTES/Stage_3_Eigenvalue_Locking_Dimension_Induction.md` | Tombstone | Prompt placeholder; induksi naik tidak valid karena Cauchy interlacing | `lean/Stage_3_Eigenvalue_Locking.lean`; `reports/RH_SCAFFOLD_NOTES/STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md` | `git show 0b0a32c:reports/RH_SCAFFOLD_NOTES/Stage_3_Eigenvalue_Locking_Dimension_Induction.md` |
| `reports/RH_SCAFFOLD_NOTES/README_custody.md` | Ganti stub | Catatan custody 2026-10-23; teks rusak, masih berstatus "USULAN", dan instruksi Stage 2/3 di dalamnya basi | Stub custody historis yang menunjuk `CURRENT_AUTHORITY.md` dan `STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md` | `git show 0b0a32c:reports/RH_SCAFFOLD_NOTES/README_custody.md` |
| `reports/RH_SCAFFOLD_NOTES/append_status.py` | Tombstone | Skrip satu-kali, path hardcoded `D:/...`, memakai `receipt["sha256"]` yang tidak ada, tidak dirujuk apa pun | Tidak ada; status historis sudah ada di `KERNEL_CHECK_2026-10-25.md` | `git show 0b0a32c:reports/RH_SCAFFOLD_NOTES/append_status.py` |

## Verifikasi sebelum eksekusi (2026-10-26)

1. **Registry:** tidak ada baris `sha256LF` yang menunjuk kelima path di atas.
   Satu-satunya `sha256LF` di `reports/RH_SCAFFOLD_NOTES/` adalah
   `Stage_4_Containment_Proof.lean` (`5786929a...`, registry `T-2026-0050`);
   berkas itu tetap disimpan.
2. **Dependensi:** `git grep` atas `msaf/tests`, `.github`, dan seluruh tree
   tidak menemukan test atau workflow yang membaca kelima path itu.
   `generate_receipts.py` hanya membaca berkas `.lean`.
3. **Recovery:** kelima berkas ada di commit `0b0a32c`, dan `origin/main`
   berada tepat di `0b0a32c`; `git show 0b0a32c:<path>` dapat dipakai.
4. **Isi prompt:** Stage 2 masih memasang `SYSTEM PROMPT` + `MANDATORY
   EXECUTION STEPS` dengan target `C_arch/n`; Stage 3 masih meminta induksi
   naik. Addendum koreksi hanya ada setelahnya, sehingga prompt tidak aman
   dibiarkan sebagai instruksi.
5. **Yang tidak disentuh:** `mcp/t2n/repokeeper.py` hanya menulis outbox
   `mcp/out/handoff/`; ia tidak merujuk `reports/HANDOFF.md`, jadi tidak
   diubah.

## Yang sengaja tidak dihapus

| Path | Alasan |
|---|---|
| `reports/RH_SCAFFOLD_NOTES/Stage_2_Derivation_Analytic_Tail_Bound.lean` | Pernah lulus kernel dan hash-nya tercatat di `KERNEL_CHECK_2026-10-25.md`; simpan sebagai artefak historis |
| `reports/RH_SCAFFOLD_NOTES/Stage_3_Eigenvalue_Locking_Dimension_Induction.lean` | Sama; pernah lulus kernel dan hash-nya tercatat |
| `reports/RH_SCAFFOLD_NOTES/*_receipt.json` | Receipt kernel-check historis; bukan instruksi aktif |
| `reports/RH_SCAFFOLD_NOTES/Stage_4_Containment_Proof.lean` | Hash-nya ada di registry `T-2026-0050`; sudah ditulis ulang, bukan superseded |
| `reports/RH_SCAFFOLD_NOTES/STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md` | Dokumen koreksi otoritatif untuk Stage 2/3 |
| `reports/TARGET_STATUS_2026-10-25.md` | Status beku; hash-nya tercatat di registry `T-2026-0052` |

## Penanda historis paket koreksi (D4, 2026-10-27)

| Path | Status | Pengganti | Recovery | Tanggal | Keputusan |
|---|---|---|---|---|---|
| `reports/RH_SCAFFOLD_NOTES/Stage_4_Containment_Proof_receipt.json` | `historical` | `reports/RH_SCAFFOLD_NOTES/KERNEL_CHECK_2026-10-25.md`; `.lean` Stage 4 tetap tersegel sebagai artefak (`T-2026-0050`) | `git show a55fe79:reports/RH_SCAFFOLD_NOTES/Stage_4_Containment_Proof_receipt.json` (byte identik dengan berkas saat ini, sha256LF tidak berubah) | 2026-10-27 | Paket koreksi D4 2026-10-27 atas persetujuan pemilik; ditandai via ledger, byte berkas tidak diubah |

Catatan D4: header peringatan historis ditambahkan (aditif) pada bagian atas
`Stage_1_Formalization_Test_Function_Space.md`,
`Stage_4_Containment_Proof.md`, dan docstring
`generate_receipts.py` (jangan dieksekusi). Byte receipt dan kode skrip
tidak diubah.
