# ZENODO 23410894 â€” REFRESH METADATA DI TEMPAT (JUDUL / DESKRIPSI / KEYWORDS) â€” 2026-10-18

Status: **SELESAI â€” REPUBLISHED.** Judul, deskripsi and keywords record
versi-of-record `10.5281/zenodo.23410894` diganti DI TEMPAT. DOI versi,
DOI konsep, and file arsip no berubah. Persetujuan pemilik (satu
ronde): judul opsi A; repo tetap `T-hat-N`; mode edit in tempat (bukan
versi baru); registry audit P1 disertakan ringkas in README.
Dua pass on 2026-10-18: (1) refresh judul/deskripsi/keywords (Â§1â€“Â§7);
(2) paragraf provenance/AI-tooling disclosure + perluasan Metadata note
(Â§8).

## 1. Sebelum â†’ sesudah (owner view; cadangan JSON in luar repo)

| medan | sebelum | sesudah |
|---|---|---|
| judul | `T-hat-N: Matrix-constraint Spectral Analysis Framework - Rigid Ball-Arithmetic Kernel, Interval Newton Zeta Inversion, and Certified Dirichlet Bracketing` | `Rigorous Ball Arithmetic for Zeta, L-Function, and Weil Spectra` |
| deskripsi | 2076 byte â€” sha256 `bd0d6f8fb9b2e766270683e1518c6c280bdf0da568a16421759589c32dea02f9` | 2722 byte â€” sha256 `d7e30f5bf4826c87f944857e698a8036fad7748dc7aeac36c7b3ef48abe29920` |
| keywords | 10 | 14 (+ `certified computation`, `interval Newton method`, `computational number theory`, `Lean 4`) |

Paragraf pembuka baru (verbatim, section which membawa kata kunci pencarian):

> Rigorous, replayable numerical certification for the Riemann zeta
> function, Dirichlet L-functions and truncated Guinand-Weil
> (explicit-formula) spectra, from the T-hat-N / Matrix-constraint
> Spectral Analysis Framework (MSAF). Every reported number is an
> interval enclosure computed with python-flint ball arithmetic
> (arb / acb / arb_mat 0.9.0): no floating-point value enters the numeric
> path, every certificate is re-derivable from committed artefacts under
> a fail-closed public CI harness, and no zero claim is certified by
> equality -- only by containment.

Tidak berubah: DOI versi `10.5281/zenodo.23410894`; DOI konsep
`10.5281/zenodo.23338271`; `version` = `v1.40.0-alpha`; `publication_date`
= `2026-10-16`; license `mit-license`; creators (Amry, Muhammad Aidil;
ORCID 0009-0002-9718-9710); file arsip `T-hat-N-a37b50b7dbdd.tar.gz`
546.800 byte â€” md5 `f90bc238bcda0170c5cb8b717afedddd`. `modified`
pasca-edit: `2026-10-18T01:35:31.065740+00:00`; state `done`.
Pass kedua (Â§8) mengubah deskripsi lagi: 2722 â†’ 3529 byte â€” sha256
`c25ae517bf35d6177be1af93a5ac12cfeeabc391618ab51be85a1b449306ae4a`;
`modified` â†’ `2026-10-18T02:13:01.174772+00:00`.

## 2. Kontrak edit (ditegakkan sebelum tulis; diuji tanpa jaringan)

Mode baru `--edit-record` in `msaf/zenodo_deposit.py` (commit `aa4f4e8`)
menolak mengubah klaim objek arsip. Deskripsi pengganti wajib: (1) diawali
judul baru; (2) memuat klaim commit arsip which sama (`a37b50bâ€¦`); (3)
memuat sha256 tarball which sama (`44bdfb87â€¦`); (4) memuat paragraf SCOPE
tetap (verbatim dari modul); (5) memuat baris `LICENSE:`; (6) memuat frasa
`AI-tooling disclosure` (sejak commit `fc7a965`). PUT gagal â†’
`actions/discard` (record kembali persis seperti terbit); echo PUT
(judul + sha256 deskripsi) no cocok â†’ publish diblokir. Tes kontrak:
`msaf/tests/test_zenodo_deposit.py` (9 tes, tanpa jaringan; suite total
369). Dry-run
mencetak sha256 deskripsi baru â€” nilai itu identik with which terpasang
pasca-publish (kecocokan byte).

## 3. Alur API (legacy deposit API; urutan aktual)

1. `GET /api/deposit/depositions/23410894` (owner) â€” state `done`;
   metadata lama + klaim arsip diekstrak mesin (`extract_archive_claims`).
2. `POST .../actions/edit` â€” unlock ("record unlocked for editing").
3. `PUT /api/deposit/depositions/23410894` body `{"metadata": {...}}` â€”
   gabungan medan lama which dipertahankan (`upload_type`, `creators`,
   `publication_date`, `access_right`, `related_identifiers`, `license`,
   `version`) + judul/deskripsi/keywords baru. Echo PUT diverifikasi.
4. `POST .../actions/publish` â€” REPUBLISHED; DOI versi + konsep sama.
5. `GET /api/records/23410894` (publik) â€” judul baru, 14 keywords.

## 4. Verifikasi pasca-edit

- Owner view: judul/deskripsi/keywords terpasang; file arsip tetap
  (nama, ukuran, md5); state `done`.
- Publik: `https://doi.org/10.5281/zenodo.23410894` menampilkan judul
  baru; keywords 14; version `v1.40.0-alpha` tetap.
- Token: blob DPAPI `%USERPROFILE%\.config\zenodo_token.sec` (60 char;
  sidik jari sha256 `2765a54428ed8dddc4c50d03dbc872900adce337bfec52f7014482739433f12c`),
  didekripsi hanya in titik pakai; nilai no pernah ditampilkan or
  ditulis.

## 5. Bukti in luar repo (Temp\opencode; no in-commit)

- `zenodo_backup_23410894_2026-10-18.json` â€” owner view pra-edit.
- `zenodo_backup_23410894_2026-10-18_after.json` â€” owner view pasca-edit.
- `zenodo_public_after_2026-10-18.json` â€” record publik pasca-edit.
- `zenodo_desc_23410894_2026-10-18.txt` â€” teks deskripsi which dipasang.
- `zenodo_edit_run_2026-10-18.log` + `zenodo_verify_after_2026-10-18.log`.
- Pass kedua: `zenodo_desc_23410894_2026-10-18_b.txt`,
  `zenodo_dryrun_b_2026-10-18.log`, `zenodo_edit_run_b_2026-10-18.log`,
  `zenodo_backup_23410894_2026-10-18_after2.json`,
  `zenodo_public_after2_2026-10-18.json`,
  `zenodo_verify_after_edit_b_2026-10-18.log`.

## 6. Selaras in source which sama (satu push with skrip)

- `.zenodo.json` (config jalur webhook, tetap nonaktif): judul/deskripsi/
  keywords diselaraskan; field `version` usang dihapus (bila webhook
  diaktifkan kelak, tag rilis which menentukan versi).
- GitHub repo: deskripsi (~205 char, sejalan judul) + homepage = DOI
  konsep + 14 topics (riemann-zeta-function, dirichlet-l-functions,
  interval-arithmetic, ball-arithmetic, rigorous-numerics,
  certified-computation, computational-number-theory, interval-newton,
  python-flint, spectral-analysis, guinand-weil, reproducible-research,
  lean4, random-matrix-theory).
- README: H1 = judul baru (identik judul record), banner status
  2026-10-18, paragraf registry audit `A-2026-0001`, paragraf
  provenance/AI-tooling disclosure (pass 2).

## 7. Catatan

- Tidak ada angka/klaim record which diubah selain judul, deskripsi
  pengantar + note metadata, and keywords; seluruh klaim arsip
  (commit, sha256, SCOPE, LICENSE) lewat verbatim.
- Baris "Metadata note (2026-10-18)" ditambahkan ke deskripsi for
  menyatakan bahwa ini refresh metadata, bukan arsip baru.

## 8. Pass kedua (2026-10-18 02:13:01Z) â€” paragraf provenance/disclosure AI

Latar: FAQ kebijakan generatif-AI Zenodo (2026-04-27) mengharapkan
depositor mengungkap pemakaian AI substantif DI DESKRIPSI record
(tool apa, for apa, section mana); panduan SSI menyarankan hal sama in
README. Keputusan owner: tiga permukaan (README, deskripsi Zenodo,
`.zenodo.json`) + aturan HANDOFF Â§5 + pengunci validator; nama tool
"OpenCode" disebut; versi model no disebut (berganti antar sesi).

| medan | pass 1 | pass 2 |
|---|---|---|
| deskripsi | 2722 byte â€” sha256 `d7e30f5bâ€¦` | 3529 byte â€” sha256 `c25ae517bf35d6177be1af93a5ac12cfeeabc391618ab51be85a1b449306ae4a` |

- Paragraf "Provenance and AI-tooling disclosure." disisipkan antara
  paragraf versi and Metadata note; Metadata note diperluas satu kalimat
  which mencatat pass kedua (per kebijakan Zenodo).
- `modified`: `2026-10-18T02:13:01.174772+00:00`; state `done`;
  REPUBLISHED; DOI versi/konsep, keywords (14), `version`,
  `publication_date`, and file arsip TIDAK berubah (md5
  `f90bc238bcda0170c5cb8b717afedddd`, 546.800 byte).
- Kontrak edit diperluas (commit `fc7a965`): validator MENOLAK deskripsi
  which kehilangan frasa `AI-tooling disclosure`; tes baru
  `test_ai_tooling_disclosure_is_pinned`; suite 368 â†’ 369.
- Verifikasi: owner view + record publik + halaman publik memuat
  paragraf. Bukti baru: lihat Â§5 (baris "Pass kedua").
- Permukaan lain: README top-matter (commit `d0fe74d`) + `.zenodo.json`
  selaras; aturan Â§5 HANDOFF ditambahkan oleh docs commit.

## 9. Lanjutan hari which sama â€” VERSI BARU suksesor (bukan edit)

Record `23410894` no diubah lagi setelah pass 2. Keadaan suksesor
diarsipkan sebagai VERSI BARU dari record which sama: DOI versi
`10.5281/zenodo.23445149` (`v1.41.0-alpha`, commit `cf32fca`). Laporan
penuh: `reports/ZENODO_NEW_VERSION_2026-10-18.md`.


