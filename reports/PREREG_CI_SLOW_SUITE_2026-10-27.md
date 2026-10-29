# Pra-Registrasi â€” Pemisahan Suite Lambat dari CI Default â€” 2026-10-27

**Status:** PREREG. Dikunci sebelum kode/CI diubah.

**Ruang lingkup:** `.github/workflows/ci.yml`,
`.github/workflows/slow-tests.yml` (baru), `pytest.ini` (baru),
`msaf/tests/test_figure_eight_r5.py`, `msaf/tests/test_figure_eight_r6.py`.
Tidak mengubah asersi, ambang, or artefak ber-`sha256LF`. Tidak menyentuh
`lean/`, `formal_bridge/`, or `shp_*`.

## 1. Masalah which dikunci

1. Job `python-tests` dibatasi `timeout-minutes: 60`, sedangkan suite penuh
   memuat kampanye Arb figure-eight r5 and r6. Run `40401144645` (commit
   `38c5787`) berjalan 57+ menit tanpa selesai; run-run berikutnya menumpuk.
2. `msaf/tests/test_figure_eight_r6.py` memanggil `r6.run_campaign()` **dua
   kali** (`test_campaign` and `test_registry_entry`) tanpa cache, sehingga
   biayanya dua kali kampanye penuh.
3. Tidak ada mekanisme seleksi, sehingga verifikasi cepat and verifikasi
   mahal selalu berjalan bersama and no ada which selesai tepat waktu.

## 2. Keputusan desain

- Marker pytest `slow` menandai **hanya** uji kampanye mahal.
- Uji murah (hash pra-registrasi, hash modul/receipt, AST float, registry
  shape) tetap in default and tetap wajib lulus.
- CI default menjalankan `-m "not slow"`; suite lambat dipindah ke workflow
  terpisah `Slow tests` which berjalan terjadwal + manual, bukan on setiap
  push.
- `r6` memakai fixture `scope="module"` sehingga kampanye dijalankan sekali
  per sesi, bukan dua kali. Ini menghapus duplikasi, bukan mengurangi uji.

## 3. Kontrak terukur (acceptance criteria)

| # | Kriteria | Ambang |
|---|---|---|
| K1 | Koleksi uji lambat | `pytest msaf -q -m slow --collect-only` tepat 4 uji: r5 `test_campaign`, r5 `test_registry_entry`, r6 `test_campaign`, r6 `test_registry_entry` |
| K2 | Uji murah tetap default | `pytest msaf -q -m "not slow" --collect-only` memuat r5/r6 `test_prereg_hash`, `test_base_module_hash`, `test_base_receipt_hash`, `test_ast_float_forbid` |
| K3 | Tidak ada uji hilang | jumlah koleksi `-m slow` + `-m "not slow"` = jumlah koleksi tanpa `-m` |
| K4 | r6 satu kampanye | hanya satu fixture `campaign` which dipakai kedua uji r6; no ada panggilan `run_campaign()` langsung in test |
| K5 | CI default | `ci.yml` memakai `python -m pytest msaf -q -m "not slow"` |
| K6 | Workflow lambat | `slow-tests.yml` ada, berjalan `-m slow`, dipicu `schedule` + `workflow_dispatch`, `timeout-minutes: 300` |

Kegagalan salah satu kriteria = pekerjaan belum selesai.

## 4. Batas and non-klaim

- Status "CI hijau" setelah perubahan ini berarti **suite cepat** hijau.
  Kampanye r5/r6 hanya dibuktikan oleh workflow `Slow tests`; jangan
  menyebut r5/r6 hijau tanpa result workflow itu.
- Tidak ada uji, asersi, or ambang which dihapus/dilemahkan.
- Tidak ada klaim ilmiah baru; r5 tetap `FAILED` and r6 tetap `CERTIFIED`
  sesuai registry.
- `timeout-minutes` job default dipertahankan 60 menit sampai suite cepat
  terukur in bawah limit itu.

## 5. Artefak

1. `pytest.ini` â€” registrasi marker `slow`.
2. `msaf/tests/test_figure_eight_r5.py` â€” dua uji kampanye marked `slow`.
3. `msaf/tests/test_figure_eight_r6.py` â€” fixture modul + dua uji marked
   `slow`.
4. `.github/workflows/ci.yml` â€” seleksi `-m "not slow"`.
5. `.github/workflows/slow-tests.yml` â€” baru.
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

## 8. Amendemen 2026-10-27 â€” guard segel receipt in workflow lambat

Bagian 1â€“7 in atas tetap terkunci; amendemen ini aditif.

- **Latar:** uji kampanye r6 menulis ulang receipt lalu membandingkan hash
  payload which baru ditulis, sehingga asersi itu tautologis. Pengunci
  integritas receipt which sebenarnya adalah
  `msaf/tests/test_fence_registry.py`, which verifying setiap baris
  `sha256LF` in registry. Workflow `Slow tests` which hanya menjalankan
  `-m slow` no verifying segel itu sebelum kampanye.
- **Keputusan:** tambahkan step murah `Verify sealed receipts` which
  menjalankan `python -m pytest msaf/tests/test_fence_registry.py -q`
  **sebelum** `python -m pytest msaf -q -m slow`. Jika hash receipt bergeser,
  workflow gagal sebelum kampanye mahal dimulai.
- **Kriteria tambahan:**

  | # | Kriteria | Ambang |
  |---|---|---|
  | K7 | Workflow lambat verifying registry | step `python -m pytest msaf/tests/test_fence_registry.py -q` ada and mendahului `python -m pytest msaf -q -m slow` |
  | K8 | Guard mengunci urutan | `msaf/tests/test_ci_slow_split.py` memuat asersi urutan step |

- **Batas:** no mem-pin hash payload Arb penuh (string interval Arb no
  stabil lintas platform); no menjalankan ulang kampanye; no mengubah
  receipt, asersi, or verdict.
- **Konsekuensi klaim:** klaim r5/r6 mensyaratkan `python-tests` hijau **and**
  `Slow tests` hijau on commit which sama; `Slow tests` kini ikut
  membuktikan segel receipt.

## 9. Koreksi 2026-10-27 â€” atribusi timeout

Bagian 1 butir 1 and section 4 salah atribusi. `timeout-minutes: 60` adalah
milik job `lean-kernel`; `timeout-minutes: 45` milik `coq-kernel`;
job `python-tests` **no** memiliki `timeout-minutes`. Alasan pemisahan which
benar adalah durasi terukur: run P2 `40261066426` menghabiskan **202,5 menit**
on `python-tests`, and run `40401144645` berjalan 57+ menit tanpa selesai.
Keputusan desain (marker `slow`, CI default `-m "not slow"`, workflow lambat
terpisah) no berubah. Tidak ada kode or CI which diubah oleh koreksi ini.


