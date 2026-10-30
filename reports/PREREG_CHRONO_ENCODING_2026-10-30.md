# Pra-registrasi Chrono Encoding – T-hat-N interval enclosure to Lean encoding – 2026-10-30

**Status:** scope DIKUNCI for Chrono Encoding v0.1; implementasi belum in-commit.
Berkas ini mengunci target masalah yang akan diintegrasikan ke MSAF **ChronoGeometric_Framework** (`ChronoGeometric_Framework/`). Isi file ini dikunci sebagai snapshot kebijakan yang dikunci, mengambil konsep dari `ChronoGeometric_Framework/ANALYSIS_TARGETS.md` dan berisi spesifikasi target (target masalah) bersama dengan target masalah yang terencana.

**Alasan supersession:** Target Encoding saat ini sepenuhnya placeholder (<true, true, true>) dan target masalah roadmap telah dirinci dalam `ANALYSIS_TARGETS.md`. File preregistrasi ini mengunci roadmap sebagai artefak target yang disahkan; implementasi selanjutnya harus membuat file yang memenuhi target target tersebut sebelum menambahkan entry klaim ke FENCE_REGISTRY.

**Tidak mengubah:** klaim yang ada (T-2026-0064 Russell, T-2026-0060 Stage-7 Tail-Extension, A-2026-0016 gate anti-circularity, dll.) dan semua validasi MSAF yang ada.

## 1. Definisi yang dikunci

Semua deklarasi JSON yang dikutip di sini adalah literal statis yang dikutip dari `lean/enclosures/*.json` hari ini. Tidak ada parsing runtime JSON yang dikunci; parser JSONLean masa depan akan membangun struktur Lean statis yang merepresentasikan data yang sama.

### 1.1 Data enclosure

- `moore_premises.json` (`lean/enclosures/moore_premises.json`) menggambarkan tiga kondisi Banach (invariance, clean derivative, Lipschitz < 1) untuk isolasi Riemann nol pertama. Bidang: `verdict`, `failed_gate`, `maps_to`, `deriv_excludes_zero`, `lipschitz_K`, `k_below_one`, `scope`, `box{real_mid, real_rad, imag_mid, imag_rad}`, `degree`.
- `derivative_enclosures.json` (`lean/enclosures/derivative_enclosures.json`) memuat enclosure tiga bilangan yang benar (1st, 2nd) yang relevan untuk kondisi clean derivative and Lipschitz bagi isolasi yang sama.
- `gw_bounds.json` (`lean/enclosures/gw_bounds.json`) (saat ini placeholder) adalah target untuk bound Guinand-Weil aktual untuk setiap indeks Nol (misalnya, `t_center`, `derivative_bound`, `character_sum_bound`, `orthogonality`, `note`).

### 1.2 Koleksi target

Target masalah yang dirinci di `ChronoGeometric_Framework/ANALYSIS_TARGETS.md` adalah:
1. **JSON → Lean Data Import** – buat `ChronoGeometric_Framework/lean/EnclosureData.lean` yang mengekspos konstanta `moore`, `derivative`, `gw` yang dapat dibandingkan dengan data JSON statis.
2. **Real ZetaStep / sign_budget_shape** – definisikan `ZetaStep n` dan `sign_budget_shape n` di `ChronoBridge.lean` dan `ChronoRiemann.lean` dengan cara yang mereferensikan value `gw_bounds[n]` dan `moore_premises[n]` yang sebenarnya (saat ini placeholder `<true,true,true>`).
3. **Bukti encoding correctness** – tulis theorem `zeta_step_encoding_correct` dan `riemann_encoding_correct` non-trivial yang membuktikan `ZetaStep n` sesuai dengan bound GW yang sebenarnya dan `sign_budget_shape n` sesuai dengan premises Moore.
4. **SAT encoding correctness** – tulis `SATEncodingCorrect` di `ChronoSAT.lean` yang menghubungkan `Sat f` ↔ `collapse_to_harmony(simulate_sat f)`.
5. **GW bounds integration** – implementasi `export_gw_bounds` (skrip Python baru atau diperluas `export_enclosures.py`) yang menghasilkan `gw_bounds.json` yang sebenarnya dari `msaf.hodge.run_weil_search_offline` (atau `msaf.gw_*` jika tersedia). Tulis file yang sama di `lean/enclosures/gw_bounds.json`.
6. **CI / anti-circularity integration** – perbarui `Makefile` dan menambahkan target `make verify` (atau CI workflow) yang membangun kerangka kerja dan menjalankan anti-circularity gate secara otomatis.
7. **Register FENCE_REGISTRY** – tambahkan klaim baru `T-2026-0065` (Riemann encoding) `T-2026-0066` (Zeta/GW encoding) `T-2026-0067` (SAT encoding) dengan hash file yang sesuai.

### 1.3 Batas eksplisit

- Tidak ada klaim matematik RH, N(zeta) ≠ 1, Weil positivity, atau full matrix positivity. Framework hanya mengodekan hasil numerik terverifikasi yang diberikan oleh T-hat-N – bukti RH, GF, dll., tetap di repo induk.
- Semua bound numerik diambil dari keluaran verifier Arb/MSAF `msaf.zeta_inversion`, `msaf.hodge.weil_search`, `moore_premises` Python – bukan dari proof intermediet internal.
- File target ini tidak mencakup implementasi algoritma T-hat-N – hanya integrasi output terverifikasi mereka.
- *Preregistrasi ini akan tetap terbuka untuk korigasi sebelum commit yang mengimplementasikan target (1)-(7) – silahkan hubungi pemilik yang bertanggung jawab untuk perubahan yang dikunci.*

## 2. Algoritma yang dikunci (untuk integrasi di masa depan)

1. **Crawl JSON** `lean/enclosures/*.json` di Build Lean.
2. **Tulis parser statis Lean** (dapat menggunakan `structure` untuk merepresentasikan bidang JSON secara eksplisit).
3. **Ekspor GW bounds** – jalankan `run_weil_search_offline.py` (atau skrip `msaf.hodge` yang setara) untuk mengisi `gw_bounds.json`.
4. **Build lintasan**: `lake build` di `ChronoGeometric_Framework/lean` harus menyelesaikan tanpa placeholder (`sorry`/`admit`).
5. **Jalankan verifikasi**: `make verify` (atau CI) menjalankan `lake build` + anti-circularity gate.
6. **Jalankan pengujian**: jalankan uji coba `pytest` untuk Python verifier (`moore_premises`) jika `msaf` ada.
7. **Tulis laporan**: `reports/CHRONO_ENCODING_2026-10-30.md` dengan angka verbatim dari file target JSONLean.
8. **Tambahkan claim** ke FENCE_REGISTRY (`T-2026-0065`, `T-2026-0066`, `T-2026-0067`) setelah verifikasi berlalu dan hash yang diuji disimpan dalam file.

## 3. Konfigurasi yang dikunci

| Parameter | Nilai |
|----------|-------|
| Root repo | `D:\Opencode AI Agent\ChronoGeometric_Framework` |
| File JSON yang menjadi tujuan | `lean/enclosures/*.json` (moore_premises.json, derivative_enclosures.json, gw_bounds.json) |
| Library Lean | `ChronoGeometric_Framework` (lakefile.toml `name = "ChronoGeometric_Framework"`) |
| Scope CI | `make verify` â€” `lake build` + external anti-circularity gate (`scripts/gate.py`) |
| Batas verifikasi | `lake build` harus exit 0; tidak ada `sorry`/`admit` di semua file Lean; anti-circularity gate mengembalikan PASS |
| Artefak | `reports/CHRONO_ENCODING_2026-10-30.md` (laporan), `reports/PREREG_CHRONO_ENCODING_2026-10-30.md` (preregistrasi) |

## 4. Receipt and determinisme

Receipt JSON minimal:

```json
{
  "schema": "msaf.chrono_encoding.v0.1",
  "target_files": [
    "lean/enclosures/moore_premises.json",
    "lean/enclosures/derivative_enclosures.json",
    "lean/enclosures/gw_bounds.json"
  ],
  "lean_build_status": "SUCCESS",
  "anti_circularity_verdict": "PASS",
  "registry_entries": [
    "T-2026-0065",
    "T-2026-0066",
    "T-2026-0067"
  ],
  "prereg_sha256lf": "...",
  "lean_sha256lf": "..."
}
```

`sha256LF` dihitung dari isi file ini tanpa line ending CRLF (`b'
'` digantikan `b'
'`) – sama seperti yang dihitung oleh sensor registry.

## 5. Kriteria penerimaan (C1-C5)

- **C1 â€” Scope JSON**: Semua field yang didefinisikan dalam blok 1 ada di file target (moore_premises, derivative_enclosures, gw_bounds).
- **C2 â€” Realized enclosure**: `EnclosureData.lean` mengimpor tiga struktur yang sebenarnya dengan konstanta (nilai JSON statis) – file tidak mengandung `sorry`/`admit`/`axiom`.
- **C3 â€” Konversi nyata**: `ZetaStep n` dan `sign_budget_shape n` menggunakan field *bound* dari `EnclosureData.gw` dan `EnclosureData.moore` (saat ini placeholder, akan diganti).
- **C4 â€” Pembuktian encoding**: `zeta_step_encoding_correct` dan `riemann_encoding_correct` adalah lemma Lean yang sebenarnya yang bergantung pada konstanta statis; keduanya diverifikasi oleh `lake build`.
- **C5 â€” Validasi CI**: `make verify` (atau CI) menjalankan `lake build` + anti-circularity gate dan exit dengan status 0.

## 6. Artefak and eksekusi

1. Bekukan dan hash file preregistrasi ini.
2. Commit and push **sebelum** commit target file Lean (EnclosureData.lean, Realized bridges, SAT correctness, dll.).
3. Buat `ChronoGeometric_Framework/lean/EnclosureData.lean`, perbarui `lakefile.toml` (tambahkan lean_lib `EnclosureData`).
4. Jalankan `make verify` (atau CI). Jalankan uji coba `pytest` untuk Python jika msaf ada.
5. Tulis `reports/CHRONO_ENCODING_2026-10-30.md` report dengan angka verbatim.
6. Perbarui `reports/FENCE_REGISTRY.md` dengan klaim `T-2026-0065`, `T-2026-0066`, `T-2026-0067` (status CERTIFIED) dan sertakan hash file.
7. Perbarui decision log dan manifest.

## 7. Falsifier

- File JSON tidak sesuai format.
- `lake build` gagal dengan placeholder (`sorry`/`admit`).
- Anti-circularity gate PASS terganggu oleh file kernel baru yang tidak ada di KERNEL_FILES.
- `EnclosureData` tidak mereferensikan struktur JSON yang sebenarnya.
- `ZetaStep` dan `sign_budget_shape` masih hardcode `<true,true,true>`.
- Encoding correctness theorem berupa `rfl` yang bergantung pada placeholder.
- `gw_bounds.json` tetap placeholder.

## 8. Catatan (untuk masa depan)

- File preregistrasi ini mengunci roadmap teknis; implementasi dapat menambah file sementara, tahap uji, skrip, dll., selama scope terpelihara.
- Semua hash SHA256LF harus dihitung menggunakan newline LF bersih.
- Solusi Lean di masa depan dapat menambah dependensi ke library eksternal (`msaf` Python) melalui `lakefile.toml`, tetapi CI sekarang hanya membutuhkan `lake build` (tanpa ketergantungan runtime).
- Proyek ini bersifat iteratif: target masalah 1-7 akan diimplementasikan dalam commit terpisah; file target masalah memberikan ketergantungan dan perintah (baca `ChronoGeometric_Framework/ANALYSIS_TARGETS.md`).

```text
SHA256LF <hash> reports/PREREG_CHRONO_ENCODING_2026-10-30.md
```

**Pemilik masalah:** <pada tahap ini>
**Catatan custody:** Dokumen ini menandai entry awal; implementasi dapat meminta perubahan yang bertanggal melalui amendment.

---

**File ini mengunci snapshot target masalah saat ini (2026-10-30).**
Lanjut: Implementasikan target masalah 1 – `EnclosureData.lean` dan constants JSON statis.**