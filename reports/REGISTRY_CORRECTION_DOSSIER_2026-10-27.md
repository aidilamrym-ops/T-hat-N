# Dossier Koreksi Registry — r7, BSD v2, BSD v3 — 2026-10-27

**Status:** DRAFT. Belum ada perubahan pada `reports/FENCE_REGISTRY.md`.
Dokumen ini mengumpulkan bukti dan opsi; eksekusi menunggu keputusan pemilik.

**Ruang lingkup:** `A-2026-0049` (r7), `T-2026-0049` (BSD v2), dan
`A-2026-0051` (BSD v3). Tidak menyentuh `A-2026-0047` (r6), `A-2026-0052`
(Q3 v3), P0/P1/P2, `shp_asymmetric_wager`, atau `shp_bridge`.

## 1. Ringkasan

| ID | Klaim saat ini | Bukti aktual | Status yang jujur |
|---|---|---|---|
| `A-2026-0049` | Figure-eight r7 `CERTIFIED` | Receipt `result: {}`; report placeholder; modul hanya memanggil r5; test registry tidak ada | STUB / RETRACTED |
| `T-2026-0049` | Heading hilang; badan BSD v2 yatim | Badan `Jenis: T`, `CERTIFIED`, sertifikat bsd_v2 valid, tetapi tidak punya heading | Pulihkan heading |
| `A-2026-0051` | BSD v3 `CERTIFIED (pending CI)` | Stub pemanggil bsd_v2; prereg bukan prereg (berisi pytest + hash placeholder); relasi ke `A-2026-0048` salah | STUB (bukan CERTIFIED) |

## 2. `A-2026-0049` — r7 diklaim CERTIFIED tanpa artefak r7

**Fakta:**

- Entri registry berbunyi `Figure-eight r7 – certified`, `Status: CERTIFIED`,
  dengan alasan "Certified based on base r5 receipt".
- `reports/figure_eight_r7_2026-10-26.json` berisi
  `{"schema": "msaf.figure_eight_r7.v1", "result": {}}`; sha256LF
  `1be5f3d3a3ca41b2da51539a143599d17f010cf76b78a364be35a633f632c1bb`.
- `reports/FIGURE_EIGHT_R7_2026-10-26.md` menyebut dirinya placeholder,
  status `PROPOSED`, dan ID `A-2026-00??`.
- `msaf/figure_eight_r7.py` hanya memanggil `figure_eight_r5.run_campaign()`;
  tidak ada mutasi r7 baru.
- `msaf/tests/test_figure_eight_r7.py` **tidak ada**, padahal perintah
  verifikasi registry merujuk file itu.
- `brain.md` §10.3 sudah mencatat r7 sebagai `STUB`, bukan `CERTIFIED`.

**Cacat klaim:** sertifikasi r7 memakai receipt r5, bukan receipt r7. Receipt
r7 kosong, jadi tidak ada artefak r7 yang bisa disertifikasi.

**Opsi:**

- **A. Retract + stub note (disarankan):** ubah status menjadi `RETRACTED`,
  tambahkan catatan tanggal, pertahankan artefak sebagai bukti stub.
- **B. Reclassify as STUB:** ubah status menjadi `STUB` (di luar enum guard
  registry, jadi perlu padanan schema seperti `PROPOSED`/`RECON`), pertahankan
  ID dan artefak; tidak ada klaim sertifikasi.
- **C. Complete r7:** tulis prereg r7, implementasi mutasi baru, test, receipt,
  lalu jalankan CI; sertifikasi hanya setelah artefak nyata.

## 3. `T-2026-0049` — badan BSD v2 yatim

**Fakta:**

- Commit `d56242c` mengganti heading
  `### T-2026-0049 — BSD Q1 v2: verifikasi eksak formula BSD rank-0 untuk 5 kurva pilot`
  dengan `### A-2026-0049 — Figure-eight r7 – certified`.
- Badan BSD v2 (`Jenis: T`, `Status: CERTIFIED`, sertifikat
  `PREREG_Q1_BSD_V2_2026-10-30.md`, `bsd_v2_2026-10-30.json`, `msaf/bsd_v2.py`)
  tetap ada tanpa heading, sehingga menempel di entri `A-2026-0050`.
- Tiga baris `sha256LF` badan itu masih cocok dengan file saat ini; guard
  registry lulus, tetapi struktur Markdown rusak.
- Code fence sertifikat badan yatim tidak ditutup sebelum `A-2026-0051`,
  sehingga heading `A-2026-0051` berada di dalam fence.
- `A-2026-0051` menulis "melanjutkan `A-2026-0048` (BSD Q1 v2)", padahal
  `A-2026-0048` adalah twin prime v4.

**Opsi:**

- **A. Pulihkan heading `T-2026-0049` (disarankan):** sisipkan kembali heading
  asli di atas badan yatim dan tutup code fence. Tidak ada perubahan klaim.
- **B. Pindahkan ke ID baru `T-2026-0053`:** badan lama diberi ID baru;
  `T-2026-0049` dibiarkan kosong dengan catatan.
- **C. Biarkan:** tidak disarankan; Markdown tetap rusak dan sejarah ID
  menyesatkan.

## 4. `A-2026-0051` — BSD v3 berstatus tidak sah

**Fakta:**

- Entri berjudul "placeholder stub" tetapi `Status: CERTIFIED (pending CI)`.
  "Pending CI" bukan status yang sah; guard hanya mengenal `PROPOSED`,
  `RECON`, `PRE-REG`, `RUNNING`, `CERTIFIED`, `FAILED`, `RETRACTED`,
  `INCONCLUSIVE`.
- CI `0e8b623` (run `40354788572`) **gagal**:
  - `msaf/bsd_v3.py:22`: `module 'msaf.bsd_v2' has no attribute 'run_campaign'`;
  - fence registry: hash drift `reports/bsd_v2_2026-10-30.json` dan
    `msaf/bsd_v2.py`;
  - fence registry: `reports/bsd_v3_2026-10-27.json` missing.
- `ad1fd91` menambahkan wrapper `run_campaign`; test lokal
  `msaf/tests/test_bsd_v3.py` sekarang lulus (1 passed).
- Receipt `reports/bsd_v3_2026-10-27.json` (sha256LF
  `cb22a1d80540beea5a482cac06d0dae05b846b428419ec94c07e1c7447a2cd4f`)
  berisi hasil bsd_v2 yang dibungkus; `all_pass: true` untuk 5 kurva.
- `reports/PREREG_BSD_V3_2026-10-27.md` (539 byte) **bukan pra-registrasi**:
  isinya kode pytest dan `PREREG_SHA = "4e45fc..."  # placeholder`.
- `msaf/bsd_v3.py` hanya mengimpor `bsd_v2`; tidak ada kurva atau logika baru.
- Relasi entri ke `A-2026-0048` salah; BSD v2 yang dirujuk adalah
  `T-2026-0049`.

**Opsi:**

- **A. Reclassify as STUB (disarankan):** ubah status menjadi `PROPOSED` atau
  `RECON`, perbaiki relasi ke `T-2026-0049`, pertahankan receipt sebagai bukti
  stub; tidak ada klaim sertifikasi.
- **B. Retract:** ubah status menjadi `RETRACTED`, pertahankan receipt sebagai
  bukti; ID tidak dipakai lagi sampai ada prereg baru.
- **C. Complete BSD v3:** tulis pra-registrasi nyata, kunci hash sebelum kode,
  tambah data/kurva baru, jalankan ulang, lalu sertifikasi. Ini pekerjaan baru,
  bukan koreksi registry.

## 5. Dampak jika disetujui

- `reports/FENCE_REGISTRY.md` diperbaiki secara aditif: status dan catatan
  tanggal, bukan penghapusan entri.
- `reports/DECISION_LOG.md` mendapat entri keputusan pemilik.
- `brain.md` §10.3 diperbarui: r7 dan BSD v3 menjadi `STUB`/`RETRACTED`,
  BSD v2 kembali ke `T-2026-0049`.
- `reports/AUTHORITY_MANIFEST.json` diperbarui jika `DECISION_LOG.md` berubah.
- Tidak ada artefak ber-`sha256LF` yang dihapus.

## 6. Non-klaim

Dossier ini tidak menyatakan r7, BSD v2, atau BSD v3 sebagai bukti baru. Ia
hanya mencatat bahwa status registry saat ini tidak cocok dengan artefak.
Tidak ada klaim RH/GRH, faktorisasi, RSA/ECC, Anderson, atau fisika.

## 7. Resolusi (2026-10-27)

Ditambahkan pada paket D6 (housekeeping, persetujuan pemilik). Ketiga
masukan dossier sudah dieksekusi di `reports/FENCE_REGISTRY.md` oleh commit
`6fb3e17` ("Correct registry status for r7, BSD v2, and BSD v3"):
- `A-2026-0049` (r7): heading kini
  "Figure-eight r7: RETRACTED (stub)", `Status: RETRACTED` — opsi A.
- `T-2026-0049` (BSD v2): heading yang dirusak `d56242c` dipulihkan,
  `Status: CERTIFIED`.
- `A-2026-0051` (BSD v3): heading dan `Status: RECON` (placeholder stub).
Bagian 1–6 di atas tetap dibaca sebagai state ketika dossier ditulis
(DRAFT); bagian 7 mencatat resolusinya.
