# Keputusan Pembersihan File Usang — 2026-11-02

**Otoritas:** `CURRENT_AUTHORITY.md`, `AGENTS.md`, `ARCHIVE_TOMBSTONES.md`
**Dasar:** Analisis dependensi, baris `sha256LF`, dan referensi test/CI

---

## Prinsip Keputusan

1. **TIDAK BOLEH DIHAPUS** jika memiliki baris `sha256LF` di `FENCE_REGISTRY.md`
2. **TIDAK BOLEH DIHAPUS** jika digunakan oleh file lain (dependensi import)
3. **TIDAK BOLEH DIHAPUS** jika masih diperlukan untuk reproducibility
4. **BOLEH DIHAPUS** jika: (a) tidak ada `sha256LF`, (b) tidak digunakan, (c) benar-benar superseded, (d) tidak ada test yang mengujinya

---

## Kategori A: FILE YANG AMAN DIHAPUS (Tidak ada sha256LF, tidak digunakan, superseded)

### 1. `msaf/figure_eight_r2.py`
- **Alasan:** Versi paling lama, FAILED (K2 slack kuadratik), digantikan r4/r6
- **sha256LF:** TIDAK ADA
- **Dependensi:** Hanya oleh `msaf/tests/test_figure_eight_r2.py`
- **Status test:** Test akan gagal jika file dihapus (tapi test ini sendiri sudah tidak relevan)
- **Recovery:** `git show 0b0a32c:msaf/figure_eight_r2.py`
- **Keputusan:** **HAPUS** + tombstone test_r2

### 2. `msaf/figure_eight.py`
- **Alasan:** Versi paling lama (sebelum r2), digantikan r4/r6
- **sha256LF:** TIDAK ADA
- **Dependensi:** TIDAK ADA
- **Status test:** Tidak ada test yang mengujinya
- **Recovery:** `git show 0b0a32c:msaf/figure_eight.py`
- **Keputusan:** **HAPUS**

### 3. `msaf/learnharness_prototype.py`
- **Alasan:** Prototipe stub, digantikan `learnharness_v1.py` (CERTIFIED A-2026-0050)
- **sha256LF:** TIDAK ADA
- **Dependensi:** Hanya oleh `msaf/tests/test_learnharness_prototype.py`
- **Status test:** Test akan gagal jika file dihapus (tapi test ini sendiri sudah tidak relevan)
- **Recovery:** `git show 0b0a32c:msaf/learnharness_prototype.py`
- **Keputusan:** **HAPUS** + tombstone test_learnharness_prototype

### 4. `msaf/lambda_min_ladder.py`
- **Alasan:** Digantikan `lambda_min_eig_ladder.py` (yang aktif digunakan)
- **sha256LF:** TIDAK ADA
- **Dependensi:** TIDAK ADA
- **Status test:** Tidak ada test yang mengujinya
- **Recovery:** `git show 0b0a32c:msaf/lambda_min_ladder.py`
- **Keputusan:** **HAPUS**

### 5. `msaf/tests/test_figure_eight_r2.py`
- **Alasan:** Test untuk versi yang sudah superseded
- **sha256LF:** TIDAK ADA
- **Dependensi:** TIDAK ADA
- **Recovery:** `git show 0b0a32c:msaf/tests/test_figure_eight_r2.py`
- **Keputusan:** **HAPUS** (bersamaan dengan figure_eight_r2.py)

### 6. `msaf/tests/test_learnharness_prototype.py`
- **Alasan:** Test untuk prototipe yang sudah superseded
- **sha256LF:** TIDAK ADA
- **Dependensi:** TIDAK ADA
- **Recovery:** `git show 0b0a32c:msaf/tests/test_learnharness_prototype.py`
- **Keputusan:** **HAPUS** (bersamaan dengan learnharness_prototype.py)

---

## Kategori B: FILE YANG HARUS DIPERTAHANKAN (Memiliki sha256LF atau digunakan)

### 1. `msaf/twin_prime_v2.py`
- **Alasan:** Memiliki baris `sha256LF` (A-2026-0045), digunakan oleh `test_twin_prime_v3.py`
- **sha256LF:** ADA (registry A-2026-0045)
- **Dependensi:** Digunakan oleh `msaf/tests/test_twin_prime_v3.py`
- **Keputusan:** **PERTAHANKAN** (tidak boleh dihapus)

### 2. `msaf/figure_eight_r3.py`
- **Alasan:** Memiliki baris `sha256LF`, digunakan oleh r4, r5, r6
- **sha256LF:** ADA
- **Dependensi:** Digunakan oleh `figure_eight_r4.py`, `figure_eight_r5.py`, `figure_eight_r6.py`
- **Keputusan:** **PERTAHANKAN** (tidak boleh dihapus)

### 3. `msaf/figure_eight_r5.py`
- **Alasan:** Tidak ada `sha256LF`, tapi digunakan oleh r7
- **sha256LF:** TIDAK ADA
- **Dependensi:** Digunakan oleh `figure_eight_r7.py`
- **Catatan:** r7 RETRACTED, tapi file masih ada
- **Keputusan:** **PERTAHANKAN** (digunakan oleh r7 meskipun r7 RETRACTED)

### 4. `msaf/figure_eight_r7.py`
- **Alasan:** Memiliki baris `sha256LF` (A-2026-0049)
- **sha256LF:** ADA (registry A-2026-0049)
- **Status:** RETRACTED stub
- **Keputusan:** **PERTAHANKAN** (tidak boleh dihapus, tapi jangan digunakan)

### 5. `msaf/bsd_descent.py`
- **Alasan:** Memiliki baris `sha256LF` (A-2026-0028)
- **sha256LF:** ADA (registry A-2026-0028)
- **Status:** INCONCLUSIVE, kode lama dengan tabel lookup
- **Keputusan:** **PERTAHANKAN** (tidak boleh dihapus)

### 6. `msaf/bsd_full.py`
- **Alasan:** Memiliki baris `sha256LF` (A-2026-0030)
- **sha256LF:** ADA (registry A-2026-0030)
- **Status:** INCONCLUSIVE
- **Keputusan:** **PERTAHANKAN** (tidak boleh dihapus)

### 7. `msaf/bsd_v3.py`
- **Alasan:** Memiliki baris `sha256LF` (A-2026-0051)
- **sha256LF:** ADA (registry A-2026-0051)
- **Status:** RECON (bukan pra-registrasi sah)
- **Keputusan:** **PERTAHANKAN** (tidak boleh dihapus)

### 8. `msaf/gw_dashboard_v4.py`
- **Alasan:** Digunakan oleh v5, v6
- **sha256LF:** TIDAK ADA
- **Dependensi:** Digunakan oleh `gw_dashboard_v5.py`, `gw_dashboard_v6.py`
- **Status:** Sealed (preserved byte-identical)
- **Keputusan:** **PERTAHANKAN** (digunakan oleh versi lebih baru)

### 9. `msaf/gw_dashboard_v5.py`
- **Alasan:** Digunakan oleh v6
- **sha256LF:** TIDAK ADA
- **Dependensi:** Digunakan oleh `gw_dashboard_v6.py`
- **Status:** Sealed (preserved byte-identical)
- **Keputusan:** **PERTAHANKAN** (digunakan oleh versi lebih baru)

---

## Kategori C: FILE DOKUMEN YANG BISA DIPERTAHANKAN SEBAGAI ARSIP

### 1. `reports/WEEKLY_REVIEW_2026-10-20_27.md`
- **Alasan:** Dokumen historis, tapi masih menunjukkan proses pengembangan
- **Relevansi:** Rendah (informasi sudah diganti dokumen lebih baru)
- **Keputusan:** **PERTAHANKAN sebagai arsip** (tidak mengganggu)

### 2. `reports/TWIN_PRIME_V2_2026-10-25.md`
- **Alasan:** Laporan resmi untuk A-2026-0045
- **Relevansi:** Masih relevan untuk reproducibility v2
- **Keputusan:** **PERTAHANKAN sebagai arsip**

### 3. `reports/TWIN_PRIME_V3_2026-10-25.md`
- **Alasan:** Laporan resmi untuk A-2026-0046
- **Relevansi:** Masih relevan untuk reproducibility v3
- **Keputusan:** **PERTAHANKAN sebagai arsip**

### 4. `reports/FIGURE_EIGHT_R5_2026-10-23.md`
- **Alasan:** Dokumen investigasi untuk r5 FAILED
- **Relevansi:** Rendah (r5 FAILED, digantikan r6)
- **Keputusan:** **PERTAHANKAN sebagai arsip**

### 5. `reports/FIGURE_EIGHT_R3_2026-10-23.md`
- **Alasan:** Dokumen investigasi untuk r3 INCONCLUSIVE
- **Relevansi:** Rendah (r3 INCONCLUSIVE, digantikan r4)
- **Keputusan:** **PERTAHANKAN sebagai arsip**

### 6. `reports/ABC_CENSUS_2026-10-21.md`
- **Alasan:** Laporan resmi untuk A-2026-0032 (C=100,000)
- **Relevansi:** Superseded oleh v3, tapi masih mencatat A-2026-0032
- **Keputusan:** **PERTAHANKAN sebagai arsip**

---

## Kategori D: FILE YANG TIDAK BOLEH DIHAPUS (Hash-frozen)

### 1. `reports/TARGET_STATUS_2026-10-25.md`
- **Alasan:** Hash-frozen, tercatat di registry T-2026-0052
- **Status:** DIBEKUKAN
- **Keputusan:** **TIDAK BOLEH DIHAPUS** (aturan dari ARCHIVE_TOMBSTONES.md)

---

## Rencana Eksekusi

### Fase 1: Verifikasi Keamanan
1. Verifikasi tidak ada test/CI aktif yang membaca file kandidat hapus
2. Verifikasi tidak ada baris `sha256LF` yang terpengaruh
3. Verifikasi recovery commit reachable dari `main`

### Fase 2: Eksekusi Hapus
1. Hapus 6 file dari Kategori A
2. Hapus 2 test terkait (test_figure_eight_r2.py, test_learnharness_prototype.py)

### Fase 3: Dokumentasi
1. Tambah entri di `reports/ARCHIVE_TOMBSTONES.md`
2. Update `reports/AUTHORITY_MANIFEST.json` jika perlu
3. Jalankan guard verifikasi

### Fase 4: Verifikasi Akhir
1. `python -m pytest msaf/tests/test_fence_registry.py -q`
2. `python -m pytest msaf/tests/test_authority_manifest.py -q`
3. `cd lean && lake build`

---

## Daftar File yang AKAN DIHAPUS

| No | Path | Alasan | sha256LF | Dependensi | Recovery |
|---|---|---|---|---|---|
| 1 | `msaf/figure_eight_r2.py` | Versi lama, FAILED, superseded | TIDAK ADA | test_r2 only | `git show 0b0a32c:...` |
| 2 | `msaf/figure_eight.py` | Versi paling lama, superseded | TIDAK ADA | TIDAK ADA | `git show 0b0a32c:...` |
| 3 | `msaf/learnharness_prototype.py` | Prototipe stub, superseded v1 | TIDAK ADA | test only | `git show 0b0a32c:...` |
| 4 | `msaf/lambda_min_ladder.py` | Superseded eig_ladder | TIDAK ADA | TIDAK ADA | `git show 0b0a32c:...` |
| 5 | `msaf/tests/test_figure_eight_r2.py` | Test untuk versi superseded | TIDAK ADA | TIDAK ADA | `git show 0b0a32c:...` |
| 6 | `msaf/tests/test_learnharness_prototype.py` | Test untuk prototipe superseded | TIDAK ADA | TIDAK ADA | `git show 0b0a32c:...` |

**Total: 6 file**

---

## Keputusan

Berdasarkan analisis di atas, saya memutuskan:

1. **HAPUS 6 file** dari Kategori A (aman, tidak ada sha256LF, tidak digunakan)
2. **PERTAHANKAN semua file** dari Kategori B (ada sha256LF atau digunakan)
3. **PERTAHANKAN sebagai arsip** file dari Kategori C
4. **TIDAK BOLEH DIHAPUS** file dari Kategori D (hash-frozen)

Keputusan ini mengikuti prinsip:
- Tidak menghapus file yang bersertifikat `sha256LF`
- Tidak merusak dependensi antar file
- Menjaga reproducibility
- Mematuhi aturan `ARCHIVE_TOMBSTONES.md`

---

Dokumen ini sebagai dasar eksekusi pembersihan file usang.
