# Investigasi Struktur Non-Sirkulan Blok Guinand-Weil — 2026-10-30

**Status:** Analisis terbatas pada **spektrum saja**; **tidak ada matriks tersedia** untuk uji struktur Toeplitz/Hankel/SVD langsung.

---

## 1. Batasan Fundamental: Artefak Hanya Spektrum

Berkas bukti yang tersertifikasi hanya memuat **spektrum eigenvalue**, **bukan matriks**:

| Artefak | Sumber Matriks (Build Chain) | Tersedia di Repo? |
|---|---|---|
| `gw_spectrum_100_100.json` (dim 201) | `source_arb_ldlt_certify.build_arb_tau(c=100,N=100,prec=6000)` | **TIDAK** |
| `gw_spectrum_100_150.json` (dim 301) | `source_arb_ldlt_certify.build_arb_tau(c=100,N=150,prec=6000)` | **TIDAK** |

Modul `source_arb_ldlt_certify` dan fungsi `build_arb_tau` **tidak ada** di repositori ini. Rekonstruksi matriks dari spektrum saja **bukan** masalah yang terdefinisi dengan baik (solusi tidak unik) dan **dilarang keras** oleh pra-registrasi (F12: fabrikasi).

---

## 2. Apa yang Dapat Disimpulkan dari Spektrum Saja

### 2.1 Spektrum Riil Murni ($L_{Im} = 0$)
- Kedua dimensi memiliki $L_{Im} = 0$ **eksak** (radius 0).
- Ini berarti **semua eigenvalue riil** dalam penahanan interval.
- **Implikasi aljabar:** Matriks asal (jika simetris/Hermitian) harus memiliki spektrum riil. Blok Guinand-Weil terpotong memang dibangun sebagai matriks **riil simetris** (sesuai literatur GW), sehingga ini konsisten.

### 2.2 Bukti Non-Sirkulan (`NOT-SYMMETRIC-CIRCULANT`)
- Verdiks pairing: **bukan** sirkulan simetris riil.
- Witness defect: ~7.15 (dim 201), ~7.87 (dim 301) — **non-nol terukur**.
- **Kesimpulan:** Blok GW **tidak** memiliki struktur sirkulan (diagonal konstan per baris bergeser).

### 2.3 Apa yang **Tidak** Bisa Diklaim dari Spektrum Saja
| Struktur Matriks | Dapat Diuji dari Spektrum Saja? | Alasan |
|---|---|---|
| Toeplitz (diagonal konstan) | **TIDAK** | Spektrum tidak menentukan entri diagonal |
| Hankel (skew-diagonal konstan) | **TIDAK** | Sama |
| SVD / Nilai Singular | **TIDAK** | Membutuhkan matriks $A$, bukan hanya $\lambda(A)$ |
| Semi-Local / Deformation Quantisation | **TIDAK** | Membutuhkan struktur entri matriks |

**Alasan matematis:** Spektrum $\{\lambda_i\}$ hanya menentukan polinomial karakteristik $\det(A - \lambda I)$. Banyak matriks non-sirkulan, non-Toeplitz, non-Hankel yang berbagi spektrum yang sama (isospektral). Tanpa matriks $A$ (atau setidaknya entri-entrinya), klasifikasi struktur matriks **mustahil**.

---

## 3. Alternatif yang Sah: Uji Spektral Lebih Lanjut (Tanpa Matriks)

Jika tujuannya memahami sifat operator dari spektrum, yang **bisa** dilakukan:

1. **Distribusi Jarak Eigenvalue (Level Spacing):** Uji statistik Montgomery/Odlyzko pada jarak antar eigenvalue berurutan.
2. **Moment Spektral:** Hitung $\frac{1}{n}\sum \lambda_i^k$ untuk $k=1..K$ dan bandingkan dengan momen teoretis kelas operator tertentu.
3. **Fungsi Green / Resolvent:** Bangun $G(z) = \frac{1}{n}\sum (\lambda_i - z)^{-1}$ untuk $z \in \mathbb{C}$ dan analisis perilaku asimtotik.

Namun, ini **bukan** uji struktur matriks (Toeplitz/Hankel/SVD), dan pra-registrasi baru diperlukan.

---

## 4. Kesimpulan Investigasi

| Pertanyaan | Jawaban |
|---|---|
| Apakah blok GW adalah Toeplitz? | **Tidak dapat diuji** — matriks tidak tersedia. |
| Apakah blok GW adalah Hankel? | **Tidak dapat diuji** — matriks tidak tersedia. |
| Apa kelas operator non-sirkulan yang melestarikan spektrum riil ini? | **Tidak dapat diklasifikasikan** dari spektrum saja; banyak kelas operator (simetris, Hermitian, normal riil, dll.) yang berbagi properti ini. |
| Apakah SVD terkurung dapat dihitung? | **TIDAK** — membutuhkan matriks $A$, bukan spektrum. |

**Rekomendasi:** Jika investigasi struktur matriks diperlukan, kampanye baru harus:
1. Pra-registrasi yang mengunci pembangunan ulang matriks $\tau$ dari `source_arb_ldlt_certify` (jika kode tersedia) atau komputasi baru.
2. Menyimpan matriks (atau faktorisasi LDU/Cholesky-nya) sebagai artefak tersertifikasi, bukan hanya spektrum.

---

## 5. Blok Pengecualian Cakupan (Scope Block)

```json
{
  "rh_claim": false,
  "zero_location_claim": false,
  "weil_positivity_claim": false
}
```

---

## 6. Verifikasi Integritas

```bash
python -m pytest msaf/tests/test_anti_circularity_gate.py -q  # PASS
python -m pytest msaf/tests/test_fence_registry.py -q         # PASS
```

Tidak ada artefak baru yang mengubah status sertifikasi `T-2026-0068`, `T-2026-0069`, `A-2026-0054`. Laporan ini murni mendokumentasikan **batasan epistemik** dari data yang ada.