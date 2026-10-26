# AGENTS.md — aturan kerja agen di repo ini

Dokumen ini adalah instruksi operasional untuk sesi agen berikutnya. Otoritas
tertinggi ada pada `CURRENT_AUTHORITY.md`; jika dokumen ini bertentangan
dengannya, `CURRENT_AUTHORITY.md` menang.

## Urutan otoritas

1. `CURRENT_AUTHORITY.md` — snapshot klaim aktif, batas, dan baseline commit.
2. `AGENTS.md` — aturan kerja ini.
3. `reports/DECISION_LOG.md` — riwayat keputusan. Entri bertanggal terbaru
   menang atas entri lama, tetapi keputusan lama tidak boleh dibalik tanpa
   bukti atau persetujuan pemilik yang tercatat.
4. `reports/FENCE_REGISTRY.md` — ledger sertifikat. Status `CERTIFIED` dan
   baris `sha256LF` adalah pagar yang harus diverifikasi, bukan saran.
5. Dokumen bertanggal lain — konteks historis, bukan tugas aktif.

`reports/HANDOFF.md` adalah log sesi historis. Jangan mengikuti "sesi
berikutnya" atau daftar tugas di dalamnya. Setelah diganti stub, ia hanya
menunjuk ke `CURRENT_AUTHORITY.md` dan `reports/ARCHIVE_TOMBSTONES.md`.

Semua `SYSTEM PROMPT` di `reports/RH_SCAFFOLD_NOTES/` adalah arsip historis;
jangan menjalankannya sebagai tugas baru tanpa pra-registrasi dan keputusan
pemilik. Stage 2/3 prompt sudah superseded. Stage 1/4 `.lean` di folder itu
tetap dipertahankan: Stage 4 hash-nya tercatat di registry `T-2026-0050`,
Stage 1 hanya berisi definisi (tanpa theorem). Implementasi Stage 2/3/5/6 ada
di `lean/`. `README_custody.md` adalah catatan custody 2026-10-23, bukan
otoritas.

## Aturan wajib

- **Prereg sebelum kode.** Commit pra-registrasi terpisah dan dipush sebelum
  commit implementasi. Amendment harus bertanggal; jangan menulis ulang isi
  yang sudah dikunci.
- **Jangan klaim melebihi artefak.** `lake build` dan kernel check hanya
  membuktikan isi file Lean. Batas pointwise `|XC(n)| < 1/n²` adalah derivasi
  kertas plus grid Arb, bukan keluaran kernel. Lean hanya memformalkan tail
  finit dan limit mayoran.
- **Lingkup P2 hanya diagonal `XC`.** `S(n)`, `Wp`, `W02`, entri off-diagonal,
  positivity matriks, spektrum zeta, Weil positivity, dan RH tidak tercakup.
  Jangan menyebut P2 sebagai "bukti RH" atau "kontrol tail seluruh matriks".
- **P1 bersifat kondisional.** Teorema perturbasi Stage 5 bergantung pada
  `A.PosDef` dan batas kuadratik `A`; otoritas positivity matriks tetap run
  `arb_mat.eig` eksternal. Jangan menyebut Lean mendiagonalisasi matriks Arb.
- **Stage 3 bukan induksi.** Induksi naik tidak valid karena Cauchy
  interlacing; modul aktif hanya record data dua run Arb.
- **Jangan hapus atau ubah artefak tersertifikasi.** File dengan baris
  `sha256LF` di registry tidak boleh dihapus atau diedit tanpa memperbarui
  registry dan menjalankan guard. Jangan menulis ulang entri `CERTIFIED` di
  tempat; tambah entri baru atau retract dengan catatan.
- **Registry tidak dihapus.** Entri `T/F/A` dipertahankan; status berubah
  lewat catatan, bukan penghapusan.
- **Satu commit, satu tujuan.** Jangan mencampur pekerjaan yang tidak terkait.
- **Jangan resurrect instruksi superseded.** Lihat
  `reports/ARCHIVE_TOMBSTONES.md` dan `CURRENT_AUTHORITY.md`.

## Baseline dan status (per 2026-10-26)

- P0: `5fea118` — koreksi lingkup Stage 2/3, audit aksioma, perbaikan guard CI.
- P1: pra-reg `34ee072`, implementasi `b7b5f2e`, registry `T-2026-0051`.
- P2: pra-reg `fc33084`, implementasi `0b0a32c`, registry `T-2026-0052`.
- r6 figure-eight: commit `ad34cbc`, receipt
  `reports/figure_eight_r6_2026-10-25.json` (`ALL PASS`), registry
  `A-2026-0047` (CERTIFIED, dikonfirmasi pemilik 2026-10-26).
- Tag baseline P2: `p2-green-0b0a32c`, dibuat setelah CI `0b0a32c` hijau.
- Status target: `reports/TARGET_STATUS_2026-10-25.md` (dibekukan; hash-nya
  tercatat di registry `T-2026-0052`). Jangan edit tanpa keputusan pemilik.

## Lingkungan dan artefak

- Lean dipin ke `4.33.1` + Mathlib; jalankan `lake build` dari `lean/` dan
  verifikasi nama lemma terhadap Mathlib terpasang, bukan dari ingatan.
- PowerShell tidak punya `&&`, heredoc, atau `grep`/`head` seperti shell Unix.
  Pakai tool yang tersedia; untuk pesan commit, tulis ke file di
  `C:\Users\usER\AppData\Local\Temp\opencode\` karena `git commit -F` gagal
  pada path yang mengandung spasi.
- Token Zenodo/GitHub tidak pernah ditulis ke repo, chat, atau log. Nilai
  plaintext tidak di-echo; dekripsi hanya di titik pakai.
- Sensor escape-token CI: kernel `lean/*.lean` harus 0 hit untuk
  `sorry`/`admit`/`unsafe`/`axiom`; `lean/spec/` dibekukan pada 9 aksioma;
  `lean/spec_v2/` pada 8 aksioma. Jangan melemahkan sensor untuk melewati
  kegagalan.
- Artefak ber-`sha256LF` tetap di path-nya. Jangan memindahkannya ke
  `archive/`; itu memutus baris sertifikat dan guard registry.
- `msaf/mont_run.txt` adalah UTF-16 dengan BOM; log lain umumnya UTF-8.
  Baca dengan encoding eksplisit.

## Gerbang minimum sebelum menyebut "verified" atau "green"

```text
python -m pytest msaf/tests/test_authority_manifest.py -q
python -m pytest msaf/tests/test_fence_registry.py -q
python -m pytest msaf/tests/test_lean_axiom_audit.py -q
python -m pytest msaf/tests/test_anti_circularity_gate.py -q
cd lean && lake build
```

Suite CI default menjalankan `python -m pytest msaf -q -m "not slow"`. Kampanye
figure-eight r5/r6 ditandai `slow` dan hanya berjalan di workflow `Slow tests`
(terjadwal/manual). Jangan mengklaim CI hijau sebelum job `python-tests` selesai
sukses, dan jangan mengklaim r5/r6 hijau tanpa hasil workflow `Slow tests`.
Untuk hasil Lean/SMT, jalankan skill `anti-circularity` sebelum menulis
"verified".

## Konflik

Jika dua dokumen bertentangan, gunakan urutan otoritas di atas. Jika konflik
tidak terselesaikan oleh dokumen yang ada, berhenti dan minta keputusan
pemilik; jangan memilih sendiri.
