# Dossier Koreksi Registry â€” r7, BSD v2, BSD v3 â€” 2026-10-27

**Status:** DRAFT. Belum ada perubahan on `reports/FENCE_REGISTRY.md`.
Dokumen ini mengumpulkan bukti and opsi; eksekusi menunggu keputusan pemilik.

**Ruang lingkup:** `A-2026-0049` (r7), `T-2026-0049` (BSD v2), and
`A-2026-0051` (BSD v3). Tidak menyentuh `A-2026-0047` (r6), `A-2026-0052`
(Q3 v3), P0/P1/P2, `shp_asymmetric_wager`, or `shp_bridge`.

## 1. Ringkasan

| ID | Klaim saat ini | Bukti aktual | Status which jujur |
|---|---|---|---|
| `A-2026-0049` | Figure-eight r7 `CERTIFIED` | Receipt `result: {}`; report placeholder; modul hanya memanggil r5; test registry no ada | STUB / RETRACTED |
| `T-2026-0049` | Heading hilang; badan BSD v2 yatim | Badan `Jenis: T`, `CERTIFIED`, sertifikat bsd_v2 valid, tetapi no punya heading | Pulihkan heading |
| `A-2026-0051` | BSD v3 `CERTIFIED (pending CI)` | Stub pemanggil bsd_v2; prereg bukan prereg (berisi pytest + hash placeholder); relasi ke `A-2026-0048` salah | STUB (bukan CERTIFIED) |

## 2. `A-2026-0049` â€” r7 diklaim CERTIFIED tanpa artefak r7

**Fakta:**

- Entri registry berbunyi `Figure-eight r7 â€“ certified`, `Status: CERTIFIED`,
  with alasan "Certified based on base r5 receipt".
- `reports/figure_eight_r7_2026-10-26.json` berisi
  `{"schema": "msaf.figure_eight_r7.v1", "result": {}}`; sha256LF
  `1be5f3d3a3ca41b2da51539a143599d17f010cf76b78a364be35a633f632c1bb`.
- `reports/FIGURE_EIGHT_R7_2026-10-26.md` menyebut dirinya placeholder,
  status `PROPOSED`, and ID `A-2026-00??`.
- `msaf/figure_eight_r7.py` hanya memanggil `figure_eight_r5.run_campaign()`;
  no ada mutasi r7 baru.
- `msaf/tests/test_figure_eight_r7.py` **no ada**, padahal perintah
  verifikasi registry merujuk file itu.
- `brain.md` Â§10.3 already mencatat r7 sebagai `STUB`, bukan `CERTIFIED`.

**Cacat klaim:** sertifikasi r7 memakai receipt r5, bukan receipt r7. Receipt
r7 kosong, jadi no ada artefak r7 which bisa disertifikasi.

**Opsi:**

- **A. Retract + stub note (disarankan):** ubah status menjadi `RETRACTED`,
  tambahkan note tanggal, pertahankan artefak sebagai bukti stub.
- **B. Reclassify as STUB:** ubah status menjadi `STUB` (in luar enum guard
  registry, jadi perlu padanan schema seperti `PROPOSED`/`RECON`), pertahankan
  ID and artefak; no ada klaim sertifikasi.
- **C. Complete r7:** tulis prereg r7, implementasi mutasi baru, test, receipt,
  lalu jalankan CI; sertifikasi hanya setelah artefak nyata.

## 3. `T-2026-0049` â€” badan BSD v2 yatim

**Fakta:**

- Commit `d56242c` mengganti heading
  `### T-2026-0049 â€” BSD Q1 v2: verifikasi eksak formula BSD rank-0 for 5 kurva pilot`
  with `### A-2026-0049 â€” Figure-eight r7 â€“ certified`.
- Badan BSD v2 (`Jenis: T`, `Status: CERTIFIED`, sertifikat
  `PREREG_Q1_BSD_V2_2026-10-30.md`, `bsd_v2_2026-10-30.json`, `msaf/bsd_v2.py`)
  tetap ada tanpa heading, sehingga menempel in entri `A-2026-0050`.
- Tiga baris `sha256LF` badan itu masih cocok with file saat ini; guard
  registry lulus, tetapi struktur Markdown rusak.
- Code fence sertifikat badan yatim no ditutup sebelum `A-2026-0051`,
  sehingga heading `A-2026-0051` berada in dalam fence.
- `A-2026-0051` menulis "melanjutkan `A-2026-0048` (BSD Q1 v2)", padahal
  `A-2026-0048` adalah twin prime v4.

**Opsi:**

- **A. Pulihkan heading `T-2026-0049` (disarankan):** sisipkan kembali heading
  asli in atas badan yatim and tutup code fence. Tidak ada perubahan klaim.
- **B. Pindahkan ke ID baru `T-2026-0053`:** badan lama diberi ID baru;
  `T-2026-0049` dibiarkan kosong with note.
- **C. Biarkan:** no disarankan; Markdown tetap rusak and sejarah ID
  menyesatkan.

## 4. `A-2026-0051` â€” BSD v3 berstatus no sah

**Fakta:**

- Entri berjudul "placeholder stub" tetapi `Status: CERTIFIED (pending CI)`.
  "Pending CI" bukan status which sah; guard hanya mengenal `PROPOSED`,
  `RECON`, `PRE-REG`, `RUNNING`, `CERTIFIED`, `FAILED`, `RETRACTED`,
  `INCONCLUSIVE`.
- CI `0e8b623` (run `40354788572`) **gagal**:
  - `msaf/bsd_v3.py:22`: `module 'msaf.bsd_v2' has no attribute 'run_campaign'`;
  - fence registry: hash drift `reports/bsd_v2_2026-10-30.json` and
    `msaf/bsd_v2.py`;
  - fence registry: `reports/bsd_v3_2026-10-27.json` missing.
- `ad1fd91` menambahkan wrapper `run_campaign`; test lokal
  `msaf/tests/test_bsd_v3.py` sekarang lulus (1 passed).
- Receipt `reports/bsd_v3_2026-10-27.json` (sha256LF
  `cb22a1d80540beea5a482cac06d0dae05b846b428419ec94c07e1c7447a2cd4f`)
  berisi result bsd_v2 which dibungkus; `all_pass: true` for 5 kurva.
- `reports/PREREG_BSD_V3_2026-10-27.md` (539 byte) **bukan pra-registrasi**:
  isinya kode pytest and `PREREG_SHA = "4e45fc..."  # placeholder`.
- `msaf/bsd_v3.py` hanya mengimpor `bsd_v2`; no ada kurva or logika baru.
- Relasi entri ke `A-2026-0048` salah; BSD v2 which dirujuk adalah
  `T-2026-0049`.

**Opsi:**

- **A. Reclassify as STUB (disarankan):** ubah status menjadi `PROPOSED` or
  `RECON`, perbaiki relasi ke `T-2026-0049`, pertahankan receipt sebagai bukti
  stub; no ada klaim sertifikasi.
- **B. Retract:** ubah status menjadi `RETRACTED`, pertahankan receipt sebagai
  bukti; ID no dipakai lagi sampai ada prereg baru.
- **C. Complete BSD v3:** tulis pra-registrasi nyata, kunci hash sebelum kode,
  tambah data/kurva baru, jalankan ulang, lalu sertifikasi. Ini pekerjaan baru,
  bukan koreksi registry.

## 5. Dampak jika disetujui

- `reports/FENCE_REGISTRY.md` diperbaiki secara aditif: status and note
  tanggal, bukan penghapusan entri.
- `reports/DECISION_LOG.md` mendapat entri keputusan pemilik.
- `brain.md` Â§10.3 diperbarui: r7 and BSD v3 menjadi `STUB`/`RETRACTED`,
  BSD v2 kembali ke `T-2026-0049`.
- `reports/AUTHORITY_MANIFEST.json` diperbarui jika `DECISION_LOG.md` berubah.
- Tidak ada artefak ber-`sha256LF` which dihapus.

## 6. Non-klaim

Dossier ini no menyatakan r7, BSD v2, or BSD v3 sebagai bukti baru. Ia
hanya mencatat bahwa status registry saat ini no cocok with artefak.
Tidak ada klaim RH/GRH, faktorisasi, RSA/ECC, Anderson, or fisika.

## 7. Resolusi (2026-10-27)

Ditambahkan on paket D6 (housekeeping, persetujuan pemilik). Ketiga
masukan dossier already dieksekusi in `reports/FENCE_REGISTRY.md` oleh commit
`6fb3e17` ("Correct registry status for r7, BSD v2, and BSD v3"):
- `A-2026-0049` (r7): heading kini
  "Figure-eight r7: RETRACTED (stub)", `Status: RETRACTED` â€” opsi A.
- `T-2026-0049` (BSD v2): heading which dirusak `d56242c` dipulihkan,
  `Status: CERTIFIED`.
- `A-2026-0051` (BSD v3): heading and `Status: RECON` (placeholder stub).
Bagian 1â€“6 in atas tetap dibaca sebagai state ketika dossier ditulis
(DRAFT); section 7 mencatat resolusinya.


