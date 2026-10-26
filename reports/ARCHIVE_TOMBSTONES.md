# Archive Tombstones

Catatan berkas yang dihapus, diganti stub, atau dinyatakan historis. File ini
dibuat pada fase authority layer yang **aditif**: belum ada tombstone yang
dieksekusi. Penghapusan dan penggantian stub menunggu persetujuan pemilik
yang tercatat di `reports/DECISION_LOG.md`.

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

Belum ada tombstone yang dieksekusi. Eksekusi dijadwalkan pada commit Phase 2,
setelah authority layer Phase 1 masuk `main` dan CI-nya hijau.

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
