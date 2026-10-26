# Pra-Registrasi — Pemisahan Suite Lambat dari CI Default — 2026-10-27

**Status:** PREREG. Dikunci sebelum kode/CI diubah.

**Ruang lingkup:** `.github/workflows/ci.yml`,
`.github/workflows/slow-tests.yml` (baru), `pytest.ini` (baru),
`msaf/tests/test_figure_eight_r5.py`, `msaf/tests/test_figure_eight_r6.py`.
Tidak mengubah asersi, ambang, atau artefak ber-`sha256LF`. Tidak menyentuh
`lean/`, `formal_bridge/`, atau `shp_*`.

## 1. Masalah yang dikunci

1. Job `python-tests` dibatasi `timeout-minutes: 60`, sedangkan suite penuh
   memuat kampanye Arb figure-eight r5 dan r6. Run `40401144645` (commit
   `38c5787`) berjalan 57+ menit tanpa selesai; run-run berikutnya menumpuk.
2. `msaf/tests/test_figure_eight_r6.py` memanggil `r6.run_campaign()` **dua
   kali** (`test_campaign` dan `test_registry_entry`) tanpa cache, sehingga
   biayanya dua kali kampanye penuh.
3. Tidak ada mekanisme seleksi, sehingga verifikasi cepat dan verifikasi
   mahal selalu berjalan bersama dan tidak ada yang selesai tepat waktu.

## 2. Keputusan desain

- Marker pytest `slow` menandai **hanya** uji kampanye mahal.
- Uji murah (hash pra-registrasi, hash modul/receipt, AST float, registry
  shape) tetap di default dan tetap wajib lulus.
- CI default menjalankan `-m "not slow"`; suite lambat dipindah ke workflow
  terpisah `Slow tests` yang berjalan terjadwal + manual, bukan pada setiap
  push.
- `r6` memakai fixture `scope="module"` sehingga kampanye dijalankan sekali
  per sesi, bukan dua kali. Ini menghapus duplikasi, bukan mengurangi uji.

## 3. Kontrak terukur (acceptance criteria)

| # | Kriteria | Ambang |
|---|---|---|
| K1 | Koleksi uji lambat | `pytest msaf -q -m slow --collect-only` tepat 4 uji: r5 `test_campaign`, r5 `test_registry_entry`, r6 `test_campaign`, r6 `test_registry_entry` |
| K2 | Uji murah tetap default | `pytest msaf -q -m "not slow" --collect-only` memuat r5/r6 `test_prereg_hash`, `test_base_module_hash`, `test_base_receipt_hash`, `test_ast_float_forbid` |
| K3 | Tidak ada uji hilang | jumlah koleksi `-m slow` + `-m "not slow"` = jumlah koleksi tanpa `-m` |
| K4 | r6 satu kampanye | hanya satu fixture `campaign` yang dipakai kedua uji r6; tidak ada panggilan `run_campaign()` langsung di test |
| K5 | CI default | `ci.yml` memakai `python -m pytest msaf -q -m "not slow"` |
| K6 | Workflow lambat | `slow-tests.yml` ada, berjalan `-m slow`, dipicu `schedule` + `workflow_dispatch`, `timeout-minutes: 300` |

Kegagalan salah satu kriteria = pekerjaan belum selesai.

## 4. Batas dan non-klaim

- Status "CI hijau" setelah perubahan ini berarti **suite cepat** hijau.
  Kampanye r5/r6 hanya dibuktikan oleh workflow `Slow tests`; jangan
  menyebut r5/r6 hijau tanpa hasil workflow itu.
- Tidak ada uji, asersi, atau ambang yang dihapus/dilemahkan.
- Tidak ada klaim ilmiah baru; r5 tetap `FAILED` dan r6 tetap `CERTIFIED`
  sesuai registry.
- `timeout-minutes` job default dipertahankan 60 menit sampai suite cepat
  terukur di bawah batas itu.

## 5. Artefak

1. `pytest.ini` — registrasi marker `slow`.
2. `msaf/tests/test_figure_eight_r5.py` — dua uji kampanye ditandai `slow`.
3. `msaf/tests/test_figure_eight_r6.py` — fixture modul + dua uji ditandai
   `slow`.
4. `.github/workflows/ci.yml` — seleksi `-m "not slow"`.
5. `.github/workflows/slow-tests.yml` — baru.
6. `reports/DECISION_LOG.md`, `brain.md`, `AGENTS.md`,
   `reports/AUTHORITY_MANIFEST.json`.

## 6. Verifikasi

```text
python -m pytest msaf -q -m slow --collect-only
python -m pytest msaf -q -m "not slow" --collect-only
python -m pytest msaf/tests/test_figure_eight_r5.py msaf/tests/test_figure_eight_r6.py -q -m "not slow"
```

## 7. Non-goals

- Tidak menjalankan kampanye r5/r6 penuh secara lokal (mahal/panas).
- Tidak mengubah jadwal menjadi setiap push.
- Tidak menyentuh workflow `spec-v3`..`spec-v6`.
