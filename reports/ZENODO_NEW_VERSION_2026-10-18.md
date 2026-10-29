# ZENODO â€” VERSI BARU v1.41.0-alpha (SUKSESOR) â€” 2026-10-18

Operasi: menerbitkan **VERSI BARU** (bukan edit) dari record T-hat-N
`10.5281/zenodo.23338271`, mengarsipkan keadaan suksesor repositori,
lewat mode baru `--new-version-of` in `msaf/zenodo_deposit.py`.

## 1. Hasil

| medan | nilai |
|---|---|
| DOI versi baru | `10.5281/zenodo.23445149` |
| Concept DOI | `10.5281/zenodo.23338271` (tetap) |
| Versi | `v1.41.0-alpha` |
| publication_date | 2026-10-18 |
| Tag annotated | `v1.41.0-alpha` (tag object `6c6f719846849984119e76995ed5720cd10181a4`) â†’ commit `cf32fca7c45a87ee523e466982a6ad5eacdc5853` |
| Commit arsip | `cf32fcaâ€¦` (tooling-first; CI hijau `39090625982`) |
| Tarball | `T-hat-N-cf32fca7c45a.tar.gz` â€” 1.068.890 byte |
| sha256 arsip | `722258413f6dc416daf6702234d11699f1add25411fdd405807480952c2e946f` |
| md5 arsip (Zenodo) | `07fd2e2a598d8f6fc0778c6fd4b68923` (== hash lokal, byte-identik) |
| Deskripsi | 3764 byte â€” sha256 `218f902570d3a14759bc8d4c8ee7b92606c442b0830596e8406935e984b77988` |
| Keywords | 14 (sama with v1.40.0-alpha) |
| related_identifiers | `isSupplementTo` https://github.com/aidilamrym-ops/T-hat-N |
| Berkas in record baru | hanya tarball commit ini (warisan dihapus oleh tool) |

Rantai konsep setelah operasi (query `allversions`): 4 versi â€”
`v1.41.0-alpha` (23445149) Â· `v1.40.0-alpha` (23410894) Â· `v1.2.0`
(23340971) Â· `v1.1.0` (23338272).

Record lama **no tersentuh**: deskripsi `c25ae517â€¦` (3529 byte),
file `T-hat-N-a37b50b7dbdd.tar.gz` md5
`f90bc238bcda0170c5cb8b717afedddd` (546.800 byte) â€” identik with
snapshot sebelum operasi (`zenodo_v141_dep_23410894.json`).

## 2. Tooling (dua commit)

1. `cf32fca` â€” mode `--new-version-of` + komposer terpisah
   (`compose_description` / `compose_metadata`) + kontrak klaim-beku
   divalidasi SEBELUM tulis in semua mode + 6 tes baru (file tes
   9 â†’ 15); sinkron hitungan README 369 â†’ 375. CI hijau `39090625982`.
2. `b1e23ab` â€” perbaikan resume + guard checksum file, ditulis
   SETELAH kuirk API terukur on percobaan publish pertama (Â§4);
   2 tes baru (15 â†’ 17); README 375 â†’ 377. CI hijau `39091124813`.

Mode baru memakai kontrak which sama with mode deposit/edit: SCOPE +
disclosure + pasangan klaim (commit + sha256 arsip) dikomposisi in
dalam kode (bukan parameter), echo `PUT` harus cocok verbatim sebelum
apa pun published, and default (tanpa `--publish`) berhenti sebagai
checkpoint draft.

## 3. Urutan which dijalankan (aktual)

1. Commit tooling `cf32fca` dipush; CI hijau `39090625982`.
2. Tag annotated `v1.41.0-alpha` created in `cf32fca` and dipush; push
   ref tag memicu run `39090834877` (hijau, 2m5s); `git ls-remote`
   memastikan tag menunjuk commit arsip.
3. Pratinjau deskripsi in luar repo (`preview_v141.py`): unduh tarball
   commit dari GitHub, hitung sha256, komposisi via fungsi which sama,
   cek kontrak (`[]`), simpan 3764 byte.
4. **Isi draft** (tanpa `--publish`): `actions/newversion` â†’ draft
   `23445149` (state `unsubmitted`); file warisan
   `T-hat-N-a37b50b7dbdd.tar.gz` dihapus; unggah
   `T-hat-N-cf32fca7c45a.tar.gz`; `PUT` metadata; echo verbatim;
   BERHENTI (checkpoint aman).
5. Verifikasi draft (owner view): sha256 deskripsi, md5 file,
   konsep, versi â€” cocok; md5 lokal file == md5 draft
   (byte-identik).
6. Publish pertama â†’ **kuirk API** (Â§4) â†’ gagal SEBELUM ada operasi
   tulis; state no berubah.
7. Perbaikan tooling `b1e23ab` dipush; CI hijau `39091124813` â€” baru
   publish lagi (disiplin: hanya tooling which CI-nya hijau which boleh
   menulis ke Zenodo).
8. **Publish via jalur resume** (teruji): file draft cocok checksum
   â†’ unggah dilewati â†’ `PUT` â†’ echo â†’ PUBLISHED; DOI
   `10.5281/zenodo.23445149`.
9. Verifikasi owner + publik + rantai (Â§5); semua snapshot disimpan
   in luar repo (Â§6).

Tarball GitHub byte-identik on TIGA pengambilan independen
(pratinjau, isi, resume): sha256 `72225841â€¦` konsisten â€” dasar klaim
"digest arsip = digest in deskripsi".

## 4. Kuirk API (fakta baru; dipakai memperbaiki tooling)

Panggilan `actions/newversion` KEDUA â€” on record which draft barunya
already berisi file â€” dijawab:

    HTTP 400
    {"status": 400, "message": "A validation error occurred.",
     "errors": [{"field": "files.enabled",
                 "messages": ["Please remove all files first."]}]}

Jadi klaim dokumentasi Zenodo ("calling new version action multiple
times will have no effect") hanya berlaku selama draft baru KOSONG
dari file. Pola `isi â†’ publish` wajib resume lewat id draft:

    python msaf/zenodo_deposit.py --new-version-of 23410894 \
        --deposition-id 23445149 --repo OWNER/NAME --sha <sha> \
        [...] --publish

Diperbaiki in `b1e23ab` (docstring + arg help + tes tanpa jaringan):
resume melewati `actions/newversion`, verifying `conceptrecid`
draft == konsep source (`same_concept`), and menambah guard
`file_matches_local` (checksum file draft harus == md5 byte lokal;
kosong = fail-closed) sebelum publish.

Percobaan publish which gagal TIDAK mengubah apa pun: error terjadi
sebelum operasi tulis pertama; verifikasi ulang setelahnya
membuktikan draft tetap seperti ditinggalkan.

## 5. Verifikasi pasca-publish

- Owner view `23445149`: `submitted: true`, `state: done`, DOI
  `10.5281/zenodo.23445149`, konsep `23338271`, versi
  `v1.41.0-alpha`, 14 keywords, deskripsi sha256 `218f9025â€¦`,
  file md5 `07fd2e2aâ€¦` â€” semua cocok.
- Publik anonim (`api/records`): DOI/versi/deskripsi/file cocok;
  judul `Rigorous Ball Arithmetic for Zeta, L-Function, and Weil
  Spectra`.
- Rantai konsep `allversions`: 4 versi utuh (Â§1).
- Record `23410894` â€” no berubah (Â§1).
- Tag: `git ls-remote --tags origin v1.41.0-alpha` â†’ `6c6f7198â€¦`
  (tag object) â†’ commit `cf32fcaâ€¦`; run ref tag `39090834877` hijau;
  setiap push diverifikasi `origin/main` == HEAD.

## 6. Bukti in luar repo (Temp\opencode; no in-commit)

- `zenodo_v141_extra_note.txt` â€” naskah note versi (input komposer).
- `zenodo_v141_desc_preview.txt` â€” deskripsi pra-isi (3764 byte).
- `zenodo_v141_dep_23410894.json` â€” snapshot owner view record LAMA
  (sebelum operasi).
- `zenodo_v141_draft_23445149_prepublish.json` +
  `zenodo_v141_dep_23445149.json` â€” draft pra-publish + pasca-publish.
- `zenodo_v141_public.json`, `zenodo_v141_versions.json` â€” verifikasi
  publik + rantai.
- Skrip: `prep_v141.py`, `preview_v141.py`, `fetch_v141.py`,
  `verify_v141_public.py`.

## 7. Catatan

- Komposisi deskripsi: judul + Source (commit + sha256 arsip) + baris
  CI + SCOPE (tetap) + [paragraf pembuka verbatim v1.40.0-alpha +
  note versi 2026-10-18] + disclosure (tetap; invariant Â§5 aturan
  6) + LICENSE.
- `.zenodo.json` TIDAK diubah: no membawa klaim commit/hash; tetap
  akurat sebagai metadata repo-level (termasuk disclosure).
- TIDAK ada GitHub Release baru â€” hanya tag annotated; release object
  "Latest" tetap milik delivery final
  `v1.40.0-alpha-final-certified-delivery`.
- Webhook GitHubâ†’Zenodo tetap OFF; `docs/ZENODO_ACTIVATE.md` konteks
  diperbarui.
- Deskripsi record baru menyebut: H1 (grid refined + C4 S10;
  ekspektasi falsified; NOT STABLE), engine B (18/18 eksak;
  PASS-WITH-ENUMERATED-EXCEPTIONS), dim-501 (UNDETERMINED at pivot
  446), amandemen manuskrip bertanggal, dashboard v6, registry
  A-2026-0001, disclosure, 375 tes on commit arsip â€” semuanya
  telah tersegel in repo sebelum deposit.


