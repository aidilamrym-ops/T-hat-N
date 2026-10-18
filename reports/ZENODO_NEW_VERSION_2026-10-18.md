# ZENODO — VERSI BARU v1.41.0-alpha (SUKSESOR) — 2026-10-18

Operasi: menerbitkan **VERSI BARU** (bukan edit) dari record T-hat-N
`10.5281/zenodo.23338271`, mengarsipkan keadaan suksesor repositori,
lewat mode baru `--new-version-of` di `msaf/zenodo_deposit.py`.

## 1. Hasil

| medan | nilai |
|---|---|
| DOI versi baru | `10.5281/zenodo.23445149` |
| Concept DOI | `10.5281/zenodo.23338271` (tetap) |
| Versi | `v1.41.0-alpha` |
| publication_date | 2026-10-18 |
| Tag annotated | `v1.41.0-alpha` (tag object `6c6f719846849984119e76995ed5720cd10181a4`) → commit `cf32fca7c45a87ee523e466982a6ad5eacdc5853` |
| Commit arsip | `cf32fca…` (tooling-first; CI hijau `39090625982`) |
| Tarball | `T-hat-N-cf32fca7c45a.tar.gz` — 1.068.890 byte |
| sha256 arsip | `722258413f6dc416daf6702234d11699f1add25411fdd405807480952c2e946f` |
| md5 arsip (Zenodo) | `07fd2e2a598d8f6fc0778c6fd4b68923` (== hash lokal, byte-identik) |
| Deskripsi | 3764 byte — sha256 `218f902570d3a14759bc8d4c8ee7b92606c442b0830596e8406935e984b77988` |
| Keywords | 14 (sama dengan v1.40.0-alpha) |
| related_identifiers | `isSupplementTo` https://github.com/aidilamrym-ops/T-hat-N |
| Berkas di record baru | hanya tarball commit ini (warisan dihapus oleh tool) |

Rantai konsep setelah operasi (query `allversions`): 4 versi —
`v1.41.0-alpha` (23445149) · `v1.40.0-alpha` (23410894) · `v1.2.0`
(23340971) · `v1.1.0` (23338272).

Record lama **tidak tersentuh**: deskripsi `c25ae517…` (3529 byte),
berkas `T-hat-N-a37b50b7dbdd.tar.gz` md5
`f90bc238bcda0170c5cb8b717afedddd` (546.800 byte) — identik dengan
snapshot sebelum operasi (`zenodo_v141_dep_23410894.json`).

## 2. Tooling (dua commit)

1. `cf32fca` — mode `--new-version-of` + komposer terpisah
   (`compose_description` / `compose_metadata`) + kontrak klaim-beku
   divalidasi SEBELUM tulis di semua mode + 6 tes baru (file tes
   9 → 15); sinkron hitungan README 369 → 375. CI hijau `39090625982`.
2. `b1e23ab` — perbaikan resume + guard checksum berkas, ditulis
   SETELAH kuirk API terukur pada percobaan publish pertama (§4);
   2 tes baru (15 → 17); README 375 → 377. CI hijau `39091124813`.

Mode baru memakai kontrak yang sama dengan mode deposit/edit: SCOPE +
disclosure + pasangan klaim (commit + sha256 arsip) dikomposisi di
dalam kode (bukan parameter), echo `PUT` harus cocok verbatim sebelum
apa pun diterbitkan, dan default (tanpa `--publish`) berhenti sebagai
checkpoint draft.

## 3. Urutan yang dijalankan (aktual)

1. Commit tooling `cf32fca` dipush; CI hijau `39090625982`.
2. Tag annotated `v1.41.0-alpha` dibuat di `cf32fca` dan dipush;
   `git ls-remote` memastikan tag menunjuk commit arsip.
3. Pratinjau deskripsi di luar repo (`preview_v141.py`): unduh tarball
   commit dari GitHub, hitung sha256, komposisi via fungsi yang sama,
   cek kontrak (`[]`), simpan 3764 byte.
4. **Isi draft** (tanpa `--publish`): `actions/newversion` → draft
   `23445149` (state `unsubmitted`); berkas warisan
   `T-hat-N-a37b50b7dbdd.tar.gz` dihapus; unggah
   `T-hat-N-cf32fca7c45a.tar.gz`; `PUT` metadata; echo verbatim;
   BERHENTI (checkpoint aman).
5. Verifikasi draft (owner view): sha256 deskripsi, md5 berkas,
   konsep, versi — cocok; md5 lokal berkas == md5 draft
   (byte-identik).
6. Publish pertama → **kuirk API** (§4) → gagal SEBELUM ada operasi
   tulis; state tidak berubah.
7. Perbaikan tooling `b1e23ab` dipush; CI hijau `39091124813` — baru
   publish lagi (disiplin: hanya tooling yang CI-nya hijau yang boleh
   menulis ke Zenodo).
8. **Publish via jalur resume** (teruji): berkas draft cocok checksum
   → unggah dilewati → `PUT` → echo → PUBLISHED; DOI
   `10.5281/zenodo.23445149`.
9. Verifikasi owner + publik + rantai (§5); semua snapshot disimpan
   di luar repo (§6).

Tarball GitHub byte-identik pada TIGA pengambilan independen
(pratinjau, isi, resume): sha256 `72225841…` konsisten — dasar klaim
"digest arsip = digest di deskripsi".

## 4. Kuirk API (fakta baru; dipakai memperbaiki tooling)

Panggilan `actions/newversion` KEDUA — pada record yang draft barunya
sudah berisi berkas — dijawab:

    HTTP 400
    {"status": 400, "message": "A validation error occurred.",
     "errors": [{"field": "files.enabled",
                 "messages": ["Please remove all files first."]}]}

Jadi klaim dokumentasi Zenodo ("calling new version action multiple
times will have no effect") hanya berlaku selama draft baru KOSONG
dari berkas. Pola `isi → publish` wajib resume lewat id draft:

    python msaf/zenodo_deposit.py --new-version-of 23410894 \
        --deposition-id 23445149 --repo OWNER/NAME --sha <sha> \
        [...] --publish

Diperbaiki di `b1e23ab` (docstring + arg help + tes tanpa jaringan):
resume melewati `actions/newversion`, memverifikasi `conceptrecid`
draft == konsep sumber (`same_concept`), dan menambah guard
`file_matches_local` (checksum berkas draft harus == md5 byte lokal;
kosong = fail-closed) sebelum publish.

Percobaan publish yang gagal TIDAK mengubah apa pun: error terjadi
sebelum operasi tulis pertama; verifikasi ulang setelahnya
membuktikan draft tetap seperti ditinggalkan.

## 5. Verifikasi pasca-publish

- Owner view `23445149`: `submitted: true`, `state: done`, DOI
  `10.5281/zenodo.23445149`, konsep `23338271`, versi
  `v1.41.0-alpha`, 14 keywords, deskripsi sha256 `218f9025…`,
  berkas md5 `07fd2e2a…` — semua cocok.
- Publik anonim (`api/records`): DOI/versi/deskripsi/berkas cocok;
  judul `Rigorous Ball Arithmetic for Zeta, L-Function, and Weil
  Spectra`.
- Rantai konsep `allversions`: 4 versi utuh (§1).
- Record `23410894` — tidak berubah (§1).
- Tag: `git ls-remote --tags origin v1.41.0-alpha` → `6c6f7198…`
  (tag object) → commit `cf32fca…`; setiap push diverifikasi
  `origin/main` == HEAD.

## 6. Bukti di luar repo (Temp\opencode; tidak di-commit)

- `zenodo_v141_extra_note.txt` — naskah catatan versi (input komposer).
- `zenodo_v141_desc_preview.txt` — deskripsi pra-isi (3764 byte).
- `zenodo_v141_dep_23410894.json` — snapshot owner view record LAMA
  (sebelum operasi).
- `zenodo_v141_draft_23445149_prepublish.json` +
  `zenodo_v141_dep_23445149.json` — draft pra-publish + pasca-publish.
- `zenodo_v141_public.json`, `zenodo_v141_versions.json` — verifikasi
  publik + rantai.
- Skrip: `prep_v141.py`, `preview_v141.py`, `fetch_v141.py`,
  `verify_v141_public.py`.

## 7. Catatan

- Komposisi deskripsi: judul + Source (commit + sha256 arsip) + baris
  CI + SCOPE (tetap) + [paragraf pembuka verbatim v1.40.0-alpha +
  catatan versi 2026-10-18] + disclosure (tetap; invariant §5 aturan
  6) + LICENSE.
- `.zenodo.json` TIDAK diubah: tidak membawa klaim commit/hash; tetap
  akurat sebagai metadata repo-level (termasuk disclosure).
- TIDAK ada GitHub Release baru — hanya tag annotated; release object
  "Latest" tetap milik delivery final
  `v1.40.0-alpha-final-certified-delivery`.
- Webhook GitHub→Zenodo tetap OFF; `docs/ZENODO_ACTIVATE.md` konteks
  diperbarui.
- Deskripsi record baru menyebut: H1 (grid refined + C4 S10;
  ekspektasi falsified; NOT STABLE), engine B (18/18 eksak;
  PASS-WITH-ENUMERATED-EXCEPTIONS), dim-501 (UNDETERMINED at pivot
  446), amandemen manuskrip bertanggal, dashboard v6, registry
  A-2026-0001, disclosure, 375 tes pada commit arsip — semuanya
  telah tersegel di repo sebelum deposit.
