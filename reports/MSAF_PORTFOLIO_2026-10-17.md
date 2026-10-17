# MSAF Portfolio 2026-10-17 — peta kampanye, registry pagar, dan antrean eksekusi

Status: **DISETUJUI pemilik proyek (2026-10-17).** Dokumen
perencanaan hidup (non-binding); dikomit 2026-10-17 setelah C4 diamankan
(batch strategi);
isinya dapat direvisi kapan pun atas arahan pemilik proyek. Ditulis saat C4
(+5 seed) berjalan; satu tahap satu waktu tetap berlaku: tidak ada kampanye
baru dieksekusi sebelum C4 dan 501 ditutup.

## 0. Prinsip yang tidak berubah

- Tiga jenis klaim yang boleh kita buat:
  - **(T) Teorema kelas finit** — pernyataan dengan kuantor yang selesai di
    kelas finit/kompak, disertifikasi mesin (exhaustive/deduktif).
  - **(F) Pagar (fence)** — "tidak ada counterexample dalam rentang/kelas X",
    tersertifikasi; mempersempit ruang tempat kegagalan pertama bisa
    bersembunyi.
  - **(R) Refutasi** — satu counterexample eksplisit + sertifikat mungil:
    kuantor universal tumbang, selesai.
  - **(A) Verdict audit** — hasil pemeriksaan independen atas klaim pihak
    ketiga (klaim ber-sertifikat, dapat diperiksa mesin).
- Yang TIDAK pernah kita klaim: versi universal/infinite dari konjektur mana
  pun; "bukti" dari data finit; spin. Kalimat penutup standar: "ini bukan
  bukti RH / bukan teorema Montgomery / dan seterusnya".
- Sertifikat dapat diperiksa mesin; pra-registrasi sebelum eksperimen;
  append-only; berhenti = catat batas (batas juga deliverable).
- Setiap hasil membukukan: artefak + entri registry (bagian 3) + guard CI +
  laporan bertanggal.

## 1. Hasil recon pass-1/pass-2 (2026-10-17; wajib dipin ulang di pass-3
sebelum pra-registrasi apa pun)

- **Sendov (1959) SELESAI — Agustus 2026.** Lech Mazur dengan alat AI
  (proofatlas.ai), diverifikasi di Lean; Terence Tao melakukan "digestion"
  menjadi bukti elementer yang mengesankan (15.000 baris Lean;
  https://terrytao.wordpress.com/2026/08/12/ , arsip 2026-08-12). Phelps–
  Rodriguez ikut selesai. **Konsekuensi: Sendov keluar dari daftar buruan;
  menjadi studi kasus alur kerja "AI-proof + Lean + digestion"** (dan
  pengingat bahwa lanskap bergerak cepat).
- **Λ (de Bruijn–Newman) — papan skor BERGERAK di 2026, dan lapisan
  klaimnya berstatus unrefereed:**
  - Λ ≥ 0 teorema (Rodgers–Tao, Forum of Math Pi 2020).
  - Λ ≤ 0.2 (kombinasi Polymath15 + Platt–Trudgian Cor. 2;
    arXiv:2004.09765v1, Bull. LMS; T_PT = 3000175332800) — acuan yang
    dipakai semua kandidat 2026.
  - **Λ ≤ 893927/5000000 = 0.1787854 — Jude Gomila, 20 Agustus 2026**
    (human–AI, "fail-closed interval certificates", paket audit lengkap:
    sealed artifacts + SHA256SUMS + verify.sh + ADVERSE_REVIEW_PROTOCOL +
    OPEN_REVIEW_QUESTIONS; **unrefereed**; repo
    github.com/judegomila/dbn-lambda-01787854-candidate-audit). Parameter:
    X = 6000000185827, t0 = 129/800, y0² = 87677/2500000; klaim tunduk pada
    kriteria Polymath15 Thm 1.2 dan tinggi terverifikasi Platt–Trudgian
    (T = 3000175332800).
  - **Λ ≤ 0.13963 KONDISIONAL** — Cetin Hakimoglu-Brown, arXiv:2610.12803
    (8 Okt 2026): bersyarat pada asumsi "ζ tanpa nol dengan Re s > 7/8,"
    yang **menurut abstraknya berasal dari preprint OpenAI yang
    unrefereed** — status asumsi ini belum kami verifikasi. Versi-versi
    sebelumnya: 0.17973 / 0.17172 / 0.16408. Mengaku tidak memakai input
    Gordon maupun Gomila.
  - **Pass-3 potongan 2 selesai (2026-10-17, dipercepat):** rilis
    `review-01787854-v3` ter-pin (OCI digest `6e29bc53…`); replay Level
    A–E terpetakan; audit adversarial internal mereka menemukan &
    memperbaiki 3 defek theorem-level sebelum seal; cros-cek eksposisi
    pihak ketiga penuh (≈9 kelas koreksi). Potongan 3 sebagian besar juga
    selesai (barrier certificate + derivative box lemma + 4 SHA PDF
    referensi; sisa: transkripsi Thm 1.2/1.3 + template reviewer). Detail:
    `reports/AUDIT_DBN_RECON_2026-10-17.md` §7.
  - Juga tercatat: "A computer-assisted upper bound..." (Stefan Gordon,
    SSRN + repo) dan "Collective Contraction in the de Bruijn–Newman Heat
    Flow" (arXiv:2609.37164, Sep 2026).
  - **Bacaan strategis:** (a) genre "certified barrier computation" persis
    stack MSAF (interval/arb, pra-registrasi, veto); (b) yang LANGKA di
    lapangan ini bukan klaim baru, melainkan **audit independen
    bersertifikat atas klaim-klaim beruntun yang unrefereed** — termasuk
    peta ketergantungannya (mana yang refereed, mana yang asumsi, mana
    yang saling bergantung). Ini titik buta yang bisa kita isi **tanpa
    harus memenangkan balapan bound**.
- **Kislitsyn 1/3–2/3 (poset) — masih terbuka; frontier TERUPDAT
  (pass-3 potongan 2):** Peczarski 2006 (GPC ⇒ 1/3–2/3; GPC ≤11 elemen)
  → **Gupta 2026, arXiv:2607.23926** (census eksak SEMUA
  1.338.193.159.771 poset-14; GPC ≤14 ⇒ 1/3–2/3 ≤14; Zenodo
  10.5281/zenodo.21865430; unrefereed). Dossier ≤10 informal kini bukan
  frontier. Kandidat P2: re-verifikasi kecil independen (≤9/10/11) +
  audit metodologi census, atau sweep parsial bersertifikat (exact
  rational; counterexample = refutasi definitif) — diputuskan setelah
  C4/501. Detail: `reports/AUDIT_DBN_RECON_2026-10-17.md` §7.7.
- **Backlog (dicatat, tidak dijadwalkan):** Tammes/spherical codes
  (kompetitif, sertifikat LP+interval), Conway 99-graph (gim SAT),
  Barnette (pencarian counterexample), lower bound Ramsey (SAT+LRAT),
  orde Hadamard (SAT), Giuga/Lehmer (jenuh spesialis).

## 2. Portofolio (P1–P6)

Format: Tujuan | Jenis klaim | Sertifikat | Status | Langkah pertama.

- **P1 — AUDIT Λ (bendera; domino: RH).**
  Tujuan: audit independen bersertifikat atas kandidat Λ pada paket Gomila
  (dan, jika dapat dipin, rantai kondisional Hakimoglu-Brown).
  Klaim: (A) verdict audit + (F) bagian yang berhasil direplikasi
  independen + daftar eksplisit bagian yang TIDAK teraudit (coverage).
  Sertifikat: laporan audit repo ini + artefak per-langkah (sha, perintah
  verifikasi).
  Status: RECON (pass-3 potongan 1+2 selesai 2026-10-17 →
  `reports/AUDIT_DBN_RECON_2026-10-17.md`; sisa potongan 3).
  Rencana audit bertingkat (pra-registrasi dulu, sebelum eksekusi):
  - L1 replay paket di container terpin (provenance replication; bukan
    independensi matematis — dilabeli demikian).
  - L2 replikasi independen terarah pada 2–3 titik tumpu terkecil:
    (a) anggaran error Prop 4.10 versi kita sendiri (Arb) vs margin
    T_min − E_max ≥ 5.57871094787e-7; (b) sampling ulang prisma barrier
    (883 prisma; verifikasi margin ≥ 0.51984989… pada subset terpilih +
    skema peluruhan); (c) tail lemma: re-derivasi sempit + spot-check.
  - L3 audit weld logis: kompatibilitas parameter (X/2 vs T_PT, margin
    350479773/2), overlap jendela N = 3840000, kontainmen persegi barrier
    [X,X+1]+i[0.1809,1] ⊂ syarat Thm 1.2, rantai sitasi Platt–Trudgian &
    Polymath (dipin ke versi refereed).
  - L4 verdict bertingkat: INDEPENDENTLY-CERTIFIED (bagian X) /
    GAP-FOUND (deskripsi gap) / UNVERIFIABLE-WITH-OUR-RESOURCES (bagian
    mana, kenapa). Semua verdict = klaim finit, masuk registry.
  Risiko jujur: cakupan penuh mungkin di luar 4-core kita; partial audit
  dengan coverage eksplisit tetap deliverable.

- **P2 — KISLITSYN SWEEP (1/3–2/3 poset).**
  Tujuan: pin frontier; perluas sapuan eksak bersertifikat (atau audit
  independen sapuan ≤14).
  Klaim: (F) "semua poset ≤n elemen memenuhi, tersertifikasi eksak" +
  (R, jika ditemukan) counterexample.
  Sertifikat: enumerasi + fungsi balance eksak per-poset (rasio bilangan
  bulat), checksum per-shard.
  Status: RECON (frontier dipin 2026-10-17: GPC ≤14 = Gupta 2026,
  arXiv:2607.23926 — census 1.338.193.159.771 poset-14; Peczarski 2006
  ≤11). Langkah pertama: pilih mode — (i) re-verifikasi kecil independen
  (≤9/10/11) + audit metodologi census ≤14, atau (ii) sweep parsial
  bersertifikat (≤12 ≈ 1,1e9 poset — hanya dengan pruning); diputuskan
  setelah C4/501.
  Catatan: konjektur ini juga gagal untuk poset infinit (lihat "Breaking
  the infinite barrier") — versi finit adalah yang kita klaim.

- **P3 — FENCE REGISTRY (instrumen "banyak klaim").**
  Tujuan: buku besar setiap klaim T/F/R/A kita — yang bisa dihitung dan
  dijaga CI. File: `reports/FENCE_REGISTRY.md` (+ skema JSON bila perlu).
  Skema entri: ID (F-2026-0001), Jenis, Pernyataan (satu kalimat, kuantor
  eksplisit), Batas (yang TIDAK diklaim), Sertifikat (artefak + sha +
  perintah verifikasi), Status (PROPOSED/RECON/PRE-REG/RUNNING/CERTIFIED/
  FAILED/RETRACTED), Domino (RH / kombinatorik / ...), Relasi (supersedes).
  Entri awal dari arsip MSAF: positif-tertutup dim 201/301 (ladder Route
  S), λ_min tersertifikasi dim 321, (menyusul) 501, verdict S2 seri
  Montgomery, replikasi Engine B, dan (menyusul) verdict audit P1.
  Guard CI: setiap entri CERTIFIED wajib menunjuk artefak yang ada dengan
  sha cocok (fail-closed).

- **P4 — SERI GW (tulang punggung metrologi; lanjutan A1).**
  Tujuan: tutup 501; studi margin-vs-N (deskriptif, pra-registrasi
  terpisah); cadangan rung lebih lebar (641?) bila menarik.
  Klaim: (F) pagar positivity per dimensi + deskripsi skala margin.
  Status: 501 pra-registrasi tersusun (belum di-commit; menunggu C4);
  sisanya PROPOSED.

- **P5 — PLATFORM `msaf/certify/` (pertumbuhan infrastruktur).**
  Tujuan: KIT minimal yang dipakai lintas track — skema sertifikat
  (fail-closed), harness verifier, kerangka interval branch-and-bound,
  dan perluasan skill anti-circularity ke mode "audit paket pihak ketiga".
  Prinsip: hanya dibangun saat track pertama yang membutuhkannya berjalan
  (tanpa framework spekulatif).
  Status: PROPOSED (aktif setelah kebutuhan nyata P1 teridentifikasi
  pada pass-3).

- **P6 — BACKLOG RESMI (dicatat; tidak dijadwalkan):** lihat bagian 1
  (Tammes, Conway-99, Barnette, Ramsey-lower, Hadamard, dll).

## 3. Eksekusi & antrean (satu kampanye komputasi berat pada satu waktu)

**Status 2026-10-17 (bertanggal; sumber hidup = `reports/HANDOFF.md`):**
butir 1–3 SELESAI — C4 S10 tuntas
(`reports/C4_SEEDS10_RESULTS_2026-10-17.md`, commit `19fe938` +
`15f767f`); titik ke-4 seri resolusi (dim 501) DIJALANKAN dan DITUTUP
sebagai OUTCOME non-PD di ladder (statistik berakhir, tanpa C/M, tanpa
rerun; `reports/GW_RESOLUTION4_DIM501_2026-10-17.md`, commit `b7e0e8f`);
pass-3 recon P1 selesai. Butir 4 DIMULAI: pra-registrasi audit P1
SELESAI (`reports/AUDIT_DBN_PREREG_2026-10-17.md`, commit `86a32c9`) —
eksekusi menyusul; L1 conditional (mesin tanpa engine container;
keputusan pemilik). Butir 5 (skema registry P3 + entri awal) BELUM
mulai. Urutan eksekusi audit yang beku: `reports/AUDIT_DBN_PREREG_2026-10-17.md`
+ `reports/HANDOFF.md` §2.0f.

1. [SEKARANG] C4 (+5 seed) berjalan → verifikasi → ekstraksi `--write` →
   commit hasil → push → CI hijau.
2. Commit pra-registrasi 501 + runner seri → push → CI hijau → launch 501
   (L→C→M; ~3,5–7,5 jam).
3. [selama 501 berjalan — float] **pass-3 recon P1**: potongan 1+2+3
   (sebagian besar) SELESAI 2026-10-17 (dipercepat atas persetujuan) →
   `reports/AUDIT_DBN_RECON_2026-10-17.md`; pin kunci: HEAD `a74738de`,
   PDF-pin `6222740e`, rilis `review-01787854-v3` + OCI digest `6e29bc53…`,
   frontier P2 TERUPDAT (GPC ≤14, arXiv:2607.23926). Sisa: transkripsi
   penuh Thm 1.2/1.3 + Lemma 8.4 (L3), template reviewer, watch berkala
   selama run 501.
4. Setelah 501 ditutup: tulis **pra-registrasi audit P1** (scope L1–L4,
   protokol verifikasi, kriteria verdict) → commit+push → eksekusi L1
   (replay container, CPU-berat) → L2/L3 → laporan audit + entri registry.
5. Paralel dokumen (selama run): skema registry P3 + entri awal; kerangka
   P5 hanya sesuai kebutuhan P1/P2.
6. Keputusan lanjutan (P2 eksekusi, P4 rung berikutnya) diambil setelah
   verdict P1 pertama — atau lebih cepat bila pemilik proyek meminta.

## 4. Definisi "banyak klaim" (metrik jujur)

Registry P3 adalah penghitungnya. Target realistis jangka menengah:
+1 entri audit (P1 — paket Gomila; kandidat berikutnya menyusul),
+1–2 entri pagar (P2 partial / P4 501), +N replikasi terverifikasi. Klaim universal tetap nol — sesuai prinsip §0.

## 5. Lampiran A — sumber pass-1 (URL + tanggal akses 2026-10-17)

- Tao, "A digestion of the proof of Sendov's conjecture", 2026-08-12:
  https://terrytao.wordpress.com/2026/08/12/a-digestion-of-the-proof-of-sendovs-conjecture/
- Gomila, Λ ≤ 0.1787854 (release 2026-08-20; unrefereed):
  https://github.com/judegomila/dbn-lambda-01787854-candidate-audit
- Hakimoglu-Brown, arXiv:2610.12803 (0.13963 kondisional), 2026-10-08:
  https://arxiv.org/abs/2610.12803
- Polymath15, arXiv:1904.12438; Rodgers–Tao, Forum Math Pi 8 (2020).
- Gordon, SSRN 7608638 + repo stefangordon/dbn-upper-bound.
- Kislitsyn: frontier Peczarski 2006 (GPC ≤11) → Gupta, arXiv:2607.23926
  (GPC ≤14; 2026; Zenodo 10.5281/zenodo.21865430); Olson–Sagan
  arXiv:1706.04985 (2017) = hasil keluarga poset (bukan sapuan); dossier
  ≤10 informal (kini bukan frontier).
- Catatan: semua nomor pass-1 wajib direcheck di pass-3; tidak ada angka
  di dokumen ini yang dipakai sebagai input pra-registrasi tanpa pin ulang.

Ditulis oleh sesi analisis, 2026-10-17 (disetujui pemilik proyek;
di-commit setelah C4 diamankan).
