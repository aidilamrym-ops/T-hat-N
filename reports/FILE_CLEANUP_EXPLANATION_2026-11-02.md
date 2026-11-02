# Catatan Pembersihan Berkas Usang & Tidak Relevan (2026-11-02)

Dokumen ini mencatat konfirmasi dan daftar berkas yang dipertahankan atau ditandai sebagai historis/superseded, menanggapi instruksi ketelitian penanganan berkas agar tidak terjadi perulangan pengerjaan atau kebingungan kode.

## 1. Prinsip Penanganan Berkas (Sesuai Aturan Repo)
- **Baris `sha256LF` di `FENCE_REGISTRY.md`:** Tidak boleh dihapus atau diubah tanpa memperbarui register dan melewati gerbang audit.
- **Artefak Tes/Kernel Lulus:** Dipertahankan sebagai catatan sejarah verifikasi meskipun sudah ada versi yang lebih baru (misalnya `twin_prime_v2.py`, `bsd_full.py`, dll.).
- **Berkas Tanpa Registry / Supassed Murni:** Berkas yang terbukti merupakan prototipe awal yang ditinggalkan (seperti `figure_eight_r2.py`, `learnharness_prototype.py`, `lambda_min_ladder.py`, dll.) telah dibersihkan secara aman (tombstoned) karena tidak memiliki dependensi yang sah dan telah digantikan oleh implementasi mapan (`r6`, `v1`, `eig_ladder`).

## 2. Status Berkas Penting (Bukan untuk Dihapus)
Berikut adalah daftar berkas yang sering disangka usang tetapi **HARUS DIKERJAKAN / DIPERTAHANKAN** karena terikat pada sertifikat terdaftar atau referensi silang:
1. **`msaf/twin_prime_v2.py` & `reports/TWIN_PRIME_V2_2026-10-25.md`**: Memiliki sertifikat terdaftar `A-2026-0045`. Meskipun ada `v3` dan `v4`, versi ini tetap menjadi titik referensi rantai verifikasi.
2. **`msaf/bsd_full.py` & `msaf/bsd_extended.py` & `msaf/bsd_descent.py`**: Berkas terkait spektrum BSD. Meskipun `bsd_full.py` diberi status `INCONCLUSIVE` (`A-2026-0030`), berkasnya tetap harus ada di path asal untuk menjaga integritas hash ledger. Versi aktif saat ini yang murni dan benar adalah `msaf/bsd_v2.py` (`T-2026-0098` / `A-2026-0051` referensi).
3. **`msaf/figure_eight_r3.py`, `r5.py`, `r7.py`**: `r3` adalah basis bagi `r4`/`r6`. `r5` adalah basis template untuk `r7`. Meskipun `r7` berstatus `RETRACTED` (`A-2026-0049`), berkasnya dipertahankan sesuai aturan pagar historis.

## 3. Tindakan Pencegahan Duplikasi
- Jangan menggunakan kembali modul-modul lama bertipe `_v2` atau `_prototype` yang telah ditandai superseded dalam kode baru.
- Gunakan selalu implementasi mutakhir yang terverifikasi (misal: `twin_prime_v4.py` untuk twin prime, `bsd_v2.py` untuk BSD, `figure_eight_r6.py` untuk figure-eight).
