# ZENODO 23410894 — REFRESH METADATA DI TEMPAT (JUDUL / DESKRIPSI / KEYWORDS) — 2026-10-18

Status: **SELESAI — REPUBLISHED.** Judul, deskripsi dan keywords record
versi-of-record `10.5281/zenodo.23410894` diganti DI TEMPAT. DOI versi,
DOI konsep, dan berkas arsip tidak berubah. Persetujuan pemilik (satu
ronde): judul opsi A; repo tetap `T-hat-N`; mode edit di tempat (bukan
versi baru); registry audit P1 disertakan ringkas di README.

## 1. Sebelum → sesudah (owner view; cadangan JSON di luar repo)

| medan | sebelum | sesudah |
|---|---|---|
| judul | `T-hat-N: Matrix-constraint Spectral Analysis Framework - Rigid Ball-Arithmetic Kernel, Interval Newton Zeta Inversion, and Certified Dirichlet Bracketing` | `Rigorous Ball Arithmetic for Zeta, L-Function, and Weil Spectra` |
| deskripsi | 2076 byte — sha256 `bd0d6f8fb9b2e766270683e1518c6c280bdf0da568a16421759589c32dea02f9` | 2722 byte — sha256 `d7e30f5bf4826c87f944857e698a8036fad7748dc7aeac36c7b3ef48abe29920` |
| keywords | 10 | 14 (+ `certified computation`, `interval Newton method`, `computational number theory`, `Lean 4`) |

Paragraf pembuka baru (verbatim, bagian yang membawa kata kunci pencarian):

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
ORCID 0009-0002-9718-9710); berkas arsip `T-hat-N-a37b50b7dbdd.tar.gz`
546.800 byte — md5 `f90bc238bcda0170c5cb8b717afedddd`. `modified`
pasca-edit: `2026-10-18T01:35:31.065740+00:00`; state `done`.

## 2. Kontrak edit (ditegakkan sebelum tulis; diuji tanpa jaringan)

Mode baru `--edit-record` di `msaf/zenodo_deposit.py` (commit `aa4f4e8`)
menolak mengubah klaim objek arsip. Deskripsi pengganti wajib: (1) diawali
judul baru; (2) memuat klaim commit arsip yang sama (`a37b50b…`); (3)
memuat sha256 tarball yang sama (`44bdfb87…`); (4) memuat paragraf SCOPE
tetap (verbatim dari modul); (5) memuat baris `LICENSE:`. PUT gagal →
`actions/discard` (record kembali persis seperti terbit); echo PUT
(judul + sha256 deskripsi) tidak cocok → publish diblokir. Tes kontrak:
`msaf/tests/test_zenodo_deposit.py` (8 tes, tanpa jaringan). Dry-run
mencetak sha256 deskripsi baru — nilai itu identik dengan yang terpasang
pasca-publish (kecocokan byte).

## 3. Alur API (legacy deposit API; urutan aktual)

1. `GET /api/deposit/depositions/23410894` (owner) — state `done`;
   metadata lama + klaim arsip diekstrak mesin (`extract_archive_claims`).
2. `POST .../actions/edit` — unlock ("record unlocked for editing").
3. `PUT /api/deposit/depositions/23410894` body `{"metadata": {...}}` —
   gabungan medan lama yang dipertahankan (`upload_type`, `creators`,
   `publication_date`, `access_right`, `related_identifiers`, `license`,
   `version`) + judul/deskripsi/keywords baru. Echo PUT diverifikasi.
4. `POST .../actions/publish` — REPUBLISHED; DOI versi + konsep sama.
5. `GET /api/records/23410894` (publik) — judul baru, 14 keywords.

## 4. Verifikasi pasca-edit

- Owner view: judul/deskripsi/keywords terpasang; berkas arsip tetap
  (nama, ukuran, md5); state `done`.
- Publik: `https://doi.org/10.5281/zenodo.23410894` menampilkan judul
  baru; keywords 14; version `v1.40.0-alpha` tetap.
- Token: blob DPAPI `%USERPROFILE%\.config\zenodo_token.sec` (60 char;
  sidik jari sha256 `2765a54428ed8dddc4c50d03dbc872900adce337bfec52f7014482739433f12c`),
  didekripsi hanya di titik pakai; nilai tidak pernah ditampilkan atau
  ditulis.

## 5. Bukti di luar repo (Temp\opencode; tidak di-commit)

- `zenodo_backup_23410894_2026-10-18.json` — owner view pra-edit.
- `zenodo_backup_23410894_2026-10-18_after.json` — owner view pasca-edit.
- `zenodo_public_after_2026-10-18.json` — record publik pasca-edit.
- `zenodo_desc_23410894_2026-10-18.txt` — teks deskripsi yang dipasang.
- `zenodo_edit_run_2026-10-18.log` + `zenodo_verify_after_2026-10-18.log`.

## 6. Selaras di sumber yang sama (satu push dengan skrip)

- `.zenodo.json` (config jalur webhook, tetap nonaktif): judul/deskripsi/
  keywords diselaraskan; field `version` usang dihapus (bila webhook
  diaktifkan kelak, tag rilis yang menentukan versi).
- GitHub repo: deskripsi (~205 char, sejalan judul) + homepage = DOI
  konsep + 14 topics (riemann-zeta-function, dirichlet-l-functions,
  interval-arithmetic, ball-arithmetic, rigorous-numerics,
  certified-computation, computational-number-theory, interval-newton,
  python-flint, spectral-analysis, guinand-weil, reproducible-research,
  lean4, random-matrix-theory).
- README: H1 = judul baru (identik judul record), banner status
  2026-10-18, paragraf registry audit `A-2026-0001`.

## 7. Catatan

- Tidak ada angka/klaim record yang diubah selain judul, deskripsi
  pengantar + catatan metadata, dan keywords; seluruh klaim arsip
  (commit, sha256, SCOPE, LICENSE) lewat verbatim.
- Baris "Metadata note (2026-10-18)" ditambahkan ke deskripsi untuk
  menyatakan bahwa ini refresh metadata, bukan arsip baru.
