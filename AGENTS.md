# AGENTS.md â€” aturan kerja agen in repo ini

Dokumen ini adalah instruksi operasional for sesi agen berikutnya. Otoritas
tertinggi ada on `CURRENT_AUTHORITY.md`; jika dokumen ini bertentangan
dengannya, `CURRENT_AUTHORITY.md` menang.

## Urutan otoritas

1. `CURRENT_AUTHORITY.md` â€” snapshot klaim aktif, limit, and baseline commit.
2. `AGENTS.md` â€” aturan kerja ini.
3. `reports/DECISION_LOG.md` â€” riwayat keputusan. Entri bertanggal terbaru
   menang atas entri lama, tetapi keputusan lama no boleh dibalik tanpa
   bukti or persetujuan pemilik which tercatat.
4. `reports/FENCE_REGISTRY.md` â€” ledger sertifikat. Status `CERTIFIED` and
   baris `sha256LF` adalah pagar which harus diverifikasi, bukan saran.
5. Dokumen bertanggal lain â€” konteks historis, bukan tugas aktif.

`reports/HANDOFF.md` adalah log sesi historis. Jangan mengikuti "sesi
berikutnya" or daftar tugas in dalamnya. Setelah diganti stub, ia hanya
menunjuk ke `CURRENT_AUTHORITY.md` and `reports/ARCHIVE_TOMBSTONES.md`.

Semua `SYSTEM PROMPT` in `reports/RH_SCAFFOLD_NOTES/` adalah arsip historis;
jangan menjalankannya sebagai tugas baru tanpa pra-registrasi and keputusan
pemilik. Stage 2/3 prompt already superseded. Stage 1/4 `.lean` in folder itu
tetap dipertahankan: Stage 4 hash-nya tercatat in registry `T-2026-0050`,
Stage 1 hanya berisi definisi (tanpa theorem). Implementasi Stage 2/3/5/6 ada
in `lean/`. `README_custody.md` adalah note custody 2026-10-23, bukan
otoritas.

## Aturan wajib

- **Prereg sebelum kode.** Commit pra-registrasi terpisah and dipush sebelum
  commit implementasi. Amendment harus bertanggal; jangan menulis ulang isi
  which already dikunci.
- **Jangan klaim melebihi artefak.** `lake build` and kernel check hanya
  membuktikan isi file Lean. Batas pointwise `|XC(n)| < 1/nÂ²` adalah derivasi
  kertas plus grid Arb, bukan keluaran kernel. Lean hanya memformalkan tail
  finit and limit mayoran.
- **Lingkup P2 hanya diagonal `XC`.** `S(n)`, `Wp`, `W02`, entri off-diagonal,
  positivity matriks, spektrum zeta, Weil positivity, and RH no tercakup.
  Jangan menyebut P2 sebagai "bukti RH" or "kontrol tail seluruh matriks".
- **P1 bersifat kondisional.** Teorema perturbasi Stage 5 bergantung on
  `A.PosDef` and limit kuadratik `A`; otoritas positivity matriks tetap run
  `arb_mat.eig` eksternal. Jangan menyebut Lean mendiagonalisasi matriks Arb.
- **Stage 3 bukan induksi.** Induksi naik no valid karena Cauchy
  interlacing; modul aktif hanya record data dua run Arb.
- **Jangan hapus or ubah artefak tersertifikasi.** File with baris
  `sha256LF` in registry no boleh dihapus or diedit tanpa memperbarui
  registry and menjalankan guard. Jangan menulis ulang entri `CERTIFIED` in
  tempat; tambah entri baru or retract with note.
- **Registry no dihapus.** Entri `T/F/A` dipertahankan; status berubah
  lewat note, bukan penghapusan.
- **Satu commit, satu tujuan.** Jangan mencampur pekerjaan which no terkait.
- **Jangan resurrect instruksi superseded.** Lihat
  `reports/ARCHIVE_TOMBSTONES.md` and `CURRENT_AUTHORITY.md`.

## Baseline and status (per 2026-10-26)

- P0: `5fea118` â€” koreksi lingkup Stage 2/3, audit aksioma, perbaikan guard CI.
- P1: pra-reg `34ee072`, implementasi `b7b5f2e`, registry `T-2026-0051`.
- P2: pra-reg `fc33084`, implementasi `0b0a32c`, registry `T-2026-0052`.
- r6 figure-eight: commit `ad34cbc`, receipt
  `reports/figure_eight_r6_2026-10-25.json` (`ALL PASS`), registry
  `A-2026-0047` (CERTIFIED, dikonfirmasi pemilik 2026-10-26).
- Tag baseline P2: `p2-green-0b0a32c`, created setelah CI `0b0a32c` hijau.
- Status target: `reports/TARGET_STATUS_2026-10-25.md` (dibekukan; hash-nya
  tercatat in registry `T-2026-0052`). Jangan edit tanpa keputusan pemilik.

## Lingkungan and artefak

- Lean dipin ke `4.33.1` + Mathlib; jalankan `lake build` dari `lean/` and
  verifikasi nama lemma terhadap Mathlib terpasang, bukan dari ingatan.
- PowerShell no punya `&&`, heredoc, or `grep`/`head` seperti shell Unix.
  Pakai tool which tersedia; for pesan commit, tulis ke file in
  `C:\Users\usER\AppData\Local\Temp\opencode\` karena `git commit -F` gagal
  on path which mengandung spasi.
- Token Zenodo/GitHub no pernah ditulis ke repo, chat, or log. Nilai
  plaintext no in-echo; dekripsi hanya in titik pakai.
- Sensor escape-token CI: kernel `lean/*.lean` harus 0 hit for
  `sorry`/`admit`/`unsafe`/`axiom`; `lean/spec/` dibekukan on 9 aksioma;
  `lean/spec_v2/` on 8 aksioma. Jangan melemahkan sensor for melewati
  kegagalan.
- Artefak ber-`sha256LF` tetap in path-nya. Jangan memindahkannya ke
  `archive/`; itu memutus baris sertifikat and guard registry.
- `msaf/mont_run.txt` adalah UTF-16 with BOM; log lain umumnya UTF-8.
  Baca with encoding eksplisit.

## Gerbang minimum sebelum menyebut "verified" or "green"

```text
python -m pytest msaf/tests/test_authority_manifest.py -q
python -m pytest msaf/tests/test_fence_registry.py -q
python -m pytest msaf/tests/test_lean_axiom_audit.py -q
python -m pytest msaf/tests/test_anti_circularity_gate.py -q
cd lean && lake build
```

Suite CI default menjalankan `python -m pytest msaf -q -m "not slow"`. Kampanye
figure-eight r5/r6 marked `slow` and hanya berjalan in workflow `Slow tests`
(terjadwal/manual). Jangan mengklaim CI hijau sebelum job `python-tests` selesai
sukses. Klaim r5/r6 mensyaratkan `python-tests` hijau **and** `Slow tests` hijau
on commit which sama; r5 tetap `FAILED` and no boleh disebut "green".
Untuk result Lean/SMT, jalankan skill `anti-circularity` sebelum menulis
"verified".

## Konflik

Jika dua dokumen bertentangan, gunakan urutan otoritas in atas. Jika konflik
no terselesaikan oleh dokumen which ada, berhenti and minta keputusan
pemilik; jangan memilih sendiri.


