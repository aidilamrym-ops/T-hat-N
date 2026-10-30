# Pra-Registrasi Kampanye Dekomposisi SVD dan Otomatisasi Manifes SKILL.md (2026-10-30)

- **ID Pra-Registrasi:** PREREG-TAU-SVD-AUTOMATION-2026-10-30
- **Tanggal:** 2026-10-30
- **Scope:** {rh_claim: false, zero_location_claim: false, weil_positivity_claim: false}
- **Otoritas:** CURRENT_AUTHORITY.md dan aturan agen AGENTS.md.

## 1. Tujuan Kampanye
Melakukan analisis SVD (Singular Value Decomposition) terkurung (enclosed SVD) pada artefak matriks $	au$ (gw_matrix_100_100.json dan gw_matrix_100_150.json) menggunakan aritmatika bola Arb, serta mengotomatiskan manifes perkakas agen melalui skills/t2n_science/SKILL.md.

## 2. Cetak Biru Analisis SVD Terkurung (Enclosed SVD)
- Modul: msaf/chrono_runtime/svd_analysis.py
- Metode: Memuat matriks $	au$ dari berkas biner, mengeksekusi SVD rigorous via Flint Arb dengan penahanan bola presisi tinggi, dan menghasilkan profil energi singular.
- Target Output: 
eports/TAU_SVD_INSIGHTS.json.

## 3. Pembuatan Manifes Kecakapan Agen (SKILL.md)
- Berkas: skills/t2n_science/SKILL.md
- Konten: YAML frontmatter dan panduan interogasi perintah sub-command 	2n_science (termasuk uild_arb_tau, natomy_test, dan svd_analysis).

## 4. Batas Klaim dan Disiplin
- Tidak ada klaim Riemann Hypothesis, zero location, atau Weil positivity.
- Kepatuhan penuh pada aturan pra-registrasi sebelum kode.
