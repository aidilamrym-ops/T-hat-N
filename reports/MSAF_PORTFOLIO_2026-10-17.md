# MSAF Portfolio 2026-10-17 â€” peta kampanye, registry pagar, and antrean eksekusi

Status: **DISETUJUI pemilik proyek (2026-10-17).** Dokumen
perencanaan hidup (non-binding); dikomit 2026-10-17 setelah C4 diamankan
(batch strategi);
isinya dapat direvisi kapan pun atas arahan pemilik proyek. Ditulis saat C4
(+5 seed) berjalan; satu tahap satu waktu tetap berlaku: no ada kampanye
baru dieksekusi sebelum C4 and 501 ditutup.

## 0. Prinsip which no berubah

- Tiga jenis klaim which boleh kita buat:
  - **(T) Teorema kelas finit** â€” pernyataan with kuantor which selesai in
    kelas finit/kompak, disertifikasi mesin (exhaustive/deduktif).
  - **(F) Pagar (fence)** â€” "no ada counterexample dalam rentang/kelas X",
    tersertifikasi; mempersempit ruang tempat kegagalan pertama bisa
    bersembunyi.
  - **(R) Refutasi** â€” satu counterexample eksplisit + sertifikat mungil:
    kuantor universal tumbang, selesai.
  - **(A) Verdict audit** â€” result pemeriksaan independen atas klaim pihak
    ketiga (klaim ber-sertifikat, dapat diperiksa mesin).
- Yang TIDAK pernah kita klaim: versi universal/infinite dari konjektur mana
  pun; "bukti" dari data finit; spin. Kalimat penutup standar: "ini bukan
  bukti RH / bukan teorema Montgomery / and seterusnya".
- Sertifikat dapat diperiksa mesin; pra-registrasi sebelum eksperimen;
  append-only; berhenti = catat limit (limit juga deliverable).
- Setiap result membukukan: artefak + entri registry (section 3) + guard CI +
  report bertanggal.

## 1. Hasil recon pass-1/pass-2 (2026-10-17; wajib dipin ulang in pass-3
sebelum pra-registrasi apa pun)

- **Sendov (1959) SELESAI â€” Agustus 2026.** Lech Mazur with alat AI
  (proofatlas.ai), diverifikasi in Lean; Terence Tao melakukan "digestion"
  menjadi bukti elementer which mengesankan (15.000 baris Lean;
  https://terrytao.wordpress.com/2026/08/12/ , arsip 2026-08-12). Phelpsâ€“
  Rodriguez ikut selesai. **Konsekuensi: Sendov keluar dari daftar buruan;
  menjadi studi kasus alur kerja "AI-proof + Lean + digestion"** (and
  pengingat bahwa lanskap bergerak cepat).
- **Î› (de Bruijnâ€“Newman) â€” papan skor BERGERAK in 2026, and lapisan
  klaimnya berstatus unrefereed:**
  - Î› â‰¥ 0 teorema (Rodgersâ€“Tao, Forum of Math Pi 2020).
  - Î› â‰¤ 0.2 (kombinasi Polymath15 + Plattâ€“Trudgian Cor. 2;
    arXiv:2004.09765v1, Bull. LMS; T_PT = 3000175332800) â€” acuan which
    dipakai semua kandidat 2026.
  - **Î› â‰¤ 893927/5000000 = 0.1787854 â€” Jude Gomila, 20 Agustus 2026**
    (humanâ€“AI, "fail-closed interval certificates", paket audit lengkap:
    sealed artifacts + SHA256SUMS + verify.sh + ADVERSE_REVIEW_PROTOCOL +
    OPEN_REVIEW_QUESTIONS; **unrefereed**; repo
    github.com/judegomila/dbn-lambda-01787854-candidate-audit). Parameter:
    X = 6000000185827, t0 = 129/800, y0Â² = 87677/2500000; klaim tunduk on
    kriteria Polymath15 Thm 1.2 and tinggi terverifikasi Plattâ€“Trudgian
    (T = 3000175332800).
  - **Î› â‰¤ 0.13963 KONDISIONAL** â€” Cetin Hakimoglu-Brown, arXiv:2610.12803
    (8 Okt 2026): bersyarat on asumsi "Î¶ tanpa nol with Re s > 7/8,"
    which **menurut abstraknya berasal dari preprint OpenAI which
    unrefereed** â€” status asumsi ini belum kami verifikasi. Versi-versi
    sebelumnya: 0.17973 / 0.17172 / 0.16408. Mengaku no memakai input
    Gordon maupun Gomila.
  - **Pass-3 potongan 2 selesai (2026-10-17, dipercepat):** rilis
    `review-01787854-v3` ter-pin (OCI digest `6e29bc53â€¦`); replay Level
    Aâ€“E terpetakan; audit adversarial internal mereka menemukan &
    memperbaiki 3 defek theorem-level sebelum seal; cros-cek eksposisi
    pihak ketiga penuh (â‰ˆ9 kelas koreksi). Potongan 3 sebagian besar juga
    selesai (barrier certificate + derivative box lemma + 4 SHA PDF
    referensi; sisa: transkripsi Thm 1.2/1.3 + template reviewer). Detail:
    `reports/AUDIT_DBN_RECON_2026-10-17.md` Â§7.
  - Juga tercatat: "A computer-assisted upper bound..." (Stefan Gordon,
    SSRN + repo) and "Collective Contraction in the de Bruijnâ€“Newman Heat
    Flow" (arXiv:2609.37164, Sep 2026).
  - **Bacaan strategis:** (a) genre "certified barrier computation" persis
    stack MSAF (interval/arb, pra-registrasi, veto); (b) which LANGKA in
    lapangan ini bukan klaim baru, melainkan **audit independen
    bersertifikat atas klaim-klaim beruntun which unrefereed** â€” termasuk
    peta ketergantungannya (mana which refereed, mana which asumsi, mana
    which saling bergantung). Ini titik buta which bisa kita isi **tanpa
    harus memenangkan balapan bound**.
- **Kislitsyn 1/3â€“2/3 (poset) â€” masih terbuka; frontier TERUPDAT
  (pass-3 potongan 2):** Peczarski 2006 (GPC â‡’ 1/3â€“2/3; GPC â‰¤11 elemen)
  â†’ **Gupta 2026, arXiv:2607.23926** (census eksak SEMUA
  1.338.193.159.771 poset-14; GPC â‰¤14 â‡’ 1/3â€“2/3 â‰¤14; Zenodo
  10.5281/zenodo.21865430; unrefereed). Dossier â‰¤10 informal kini bukan
  frontier. Kandidat P2: re-verifikasi kecil independen (â‰¤9/10/11) +
  audit metodologi census, or sweep parsial bersertifikat (exact
  rational; counterexample = refutasi definitif) â€” diputuskan setelah
  C4/501. Detail: `reports/AUDIT_DBN_RECON_2026-10-17.md` Â§7.7.
- **Backlog (dicatat, no dijadwalkan):** Tammes/spherical codes
  (kompetitif, sertifikat LP+interval), Conway 99-graph (gim SAT),
  Barnette (pencarian counterexample), lower bound Ramsey (SAT+LRAT),
  orde Hadamard (SAT), Giuga/Lehmer (jenuh spesialis).

## 2. Portofolio (P1â€“P6)

Format: Tujuan | Jenis klaim | Sertifikat | Status | Langkah pertama.

- **P1 â€” AUDIT Î› (bendera; domino: RH).**
  Tujuan: audit independen bersertifikat atas kandidat Î› on paket Gomila
  (and, jika dapat dipin, rantai kondisional Hakimoglu-Brown).
  Klaim: (A) verdict audit + (F) section which berhasil direplikasi
  independen + daftar eksplisit section which TIDAK teraudit (coverage).
  Sertifikat: report audit repo ini + artefak per-step (sha, perintah
  verifikasi).
  Status: RECON (pass-3 potongan 1+2 selesai 2026-10-17 â†’
  `reports/AUDIT_DBN_RECON_2026-10-17.md`; sisa potongan 3).
  Rencana audit bertingkat (pra-registrasi dulu, sebelum eksekusi):
  - L1 replay paket in container terpin (provenance replication; bukan
    independensi matematis â€” dilabeli demikian).
  - L2 replikasi independen terarah on 2â€“3 titik tumpu terkecil:
    (a) anggaran error Prop 4.10 versi kita sendiri (Arb) vs margin
    T_min âˆ’ E_max â‰¥ 5.57871094787e-7; (b) sampling ulang prisma barrier
    (883 prisma; verifikasi margin â‰¥ 0.51984989â€¦ on subset terpilih +
    skema peluruhan); (c) tail lemma: re-derivasi sempit + spot-check.
  - L3 audit weld logis: kompatibilitas parameter (X/2 vs T_PT, margin
    350479773/2), overlap jendela N = 3840000, kontainmen persegi barrier
    [X,X+1]+i[0.1809,1] âŠ‚ syarat Thm 1.2, rantai sitasi Plattâ€“Trudgian &
    Polymath (dipin ke versi refereed).
  - L4 verdict bertingkat: INDEPENDENTLY-CERTIFIED (section X) /
    GAP-FOUND (deskripsi gap) / UNVERIFIABLE-WITH-OUR-RESOURCES (section
    mana, kenapa). Semua verdict = klaim finit, masuk registry.
  Risiko jujur: cakupan penuh mungkin in luar 4-core kita; partial audit
  with coverage eksplisit tetap deliverable.

- **P2 â€” KISLITSYN SWEEP (1/3â€“2/3 poset).**
  Tujuan: pin frontier; perluas sapuan eksak bersertifikat (or audit
  independen sapuan â‰¤14).
  Klaim: (F) "semua poset â‰¤n elemen memenuhi, tersertifikasi eksak" +
  (R, jika ditemukan) counterexample.
  Sertifikat: enumerasi + fungsi balance eksak per-poset (rasio bilangan
  bulat), checksum per-shard.
  Status: RECON (frontier dipin 2026-10-17: GPC â‰¤14 = Gupta 2026,
  arXiv:2607.23926 â€” census 1.338.193.159.771 poset-14; Peczarski 2006
  â‰¤11). Langkah pertama: pilih mode â€” (i) re-verifikasi kecil independen
  (â‰¤9/10/11) + audit metodologi census â‰¤14, or (ii) sweep parsial
  bersertifikat (â‰¤12 â‰ˆ 1,1e9 poset â€” hanya with pruning); diputuskan
  setelah C4/501.
  Catatan: konjektur ini juga gagal for poset infinit (lihat "Breaking
  the infinite barrier") â€” versi finit adalah which kita klaim.

- **P3 â€” FENCE REGISTRY (instrumen "banyak klaim").**
  Tujuan: buku besar setiap klaim T/F/R/A kita â€” which bisa dihitung and
  dijaga CI. File: `reports/FENCE_REGISTRY.md` (+ skema JSON bila perlu).
  Skema entri: ID (F-2026-0001), Jenis, Pernyataan (satu kalimat, kuantor
  eksplisit), Batas (which TIDAK diklaim), Sertifikat (artefak + sha +
  perintah verifikasi), Status (PROPOSED/RECON/PRE-REG/RUNNING/CERTIFIED/
  FAILED/RETRACTED), Domino (RH / kombinatorik / ...), Relasi (supersedes).
  Entri awal dari arsip MSAF: positif-tertutup dim 201/301 (ladder Route
  S), Î»_min tersertifikasi dim 321, (menyusul) 501, verdict S2 seri
  Montgomery, replikasi Engine B, and (menyusul) verdict audit P1.
  Guard CI: setiap entri CERTIFIED wajib menunjuk artefak which ada with
  sha cocok (fail-closed).

- **P4 â€” SERI GW (tulang punggung metrologi; lanjutan A1).**
  Tujuan: tutup 501; studi margin-vs-N (deskriptif, pra-registrasi
  terpisah); cadangan rung lebih lebar (641?) bila menarik.
  Klaim: (F) pagar positivity per dimensi + deskripsi skala margin.
  Status: 501 pra-registrasi tersusun (belum in-commit; menunggu C4);
  sisanya PROPOSED.

- **P5 â€” PLATFORM `msaf/certify/` (pertumbuhan infrastruktur).**
  Tujuan: KIT minimal which dipakai lintas track â€” skema sertifikat
  (fail-closed), harness verifier, kerangka interval branch-and-bound,
  and perluasan skill anti-circularity ke mode "audit paket pihak ketiga".
  Prinsip: hanya dibangun saat track pertama which membutuhkannya berjalan
  (tanpa framework spekulatif).
  Status: PROPOSED (aktif setelah kebutuhan nyata P1 teridentifikasi
  on pass-3).

- **P6 â€” BACKLOG RESMI (dicatat; no dijadwalkan):** lihat section 1
  (Tammes, Conway-99, Barnette, Ramsey-lower, Hadamard, dll).

## 3. Eksekusi & antrean (satu kampanye komputasi berat on satu waktu)

**Status 2026-10-17 (bertanggal; source hidup = `reports/HANDOFF.md`):**
butir 1â€“3 SELESAI â€” C4 S10 tuntas
(`reports/C4_SEEDS10_RESULTS_2026-10-17.md`, commit `19fe938` +
`15f767f`); titik ke-4 seri resolusi (dim 501) DIJALANKAN and DITUTUP
sebagai OUTCOME non-PD in ladder (statistik berakhir, tanpa C/M, tanpa
rerun; `reports/GW_RESOLUTION4_DIM501_2026-10-17.md`, commit `b7e0e8f`);
pass-3 recon P1 selesai. Butir 4 DIMULAI: pra-registrasi audit P1
SELESAI (`reports/AUDIT_DBN_PREREG_2026-10-17.md`, commit `86a32c9`) â€”
eksekusi menyusul; L1 conditional (mesin tanpa engine container;
keputusan pemilik). Butir 5 (skema registry P3 + entri awal) BELUM
mulai. Urutan eksekusi audit which beku: `reports/AUDIT_DBN_PREREG_2026-10-17.md`
+ `reports/HANDOFF.md` Â§2.0f.

1. [SEKARANG] C4 (+5 seed) berjalan â†’ verifikasi â†’ ekstraksi `--write` â†’
   commit result â†’ push â†’ CI hijau.
2. Commit pra-registrasi 501 + runner seri â†’ push â†’ CI hijau â†’ launch 501
   (Lâ†’Câ†’M; ~3,5â€“7,5 jam).
3. [selama 501 berjalan â€” float] **pass-3 recon P1**: potongan 1+2+3
   (sebagian besar) SELESAI 2026-10-17 (dipercepat atas persetujuan) â†’
   `reports/AUDIT_DBN_RECON_2026-10-17.md`; pin kunci: HEAD `a74738de`,
   PDF-pin `6222740e`, rilis `review-01787854-v3` + OCI digest `6e29bc53â€¦`,
   frontier P2 TERUPDAT (GPC â‰¤14, arXiv:2607.23926). Sisa: transkripsi
   penuh Thm 1.2/1.3 + Lemma 8.4 (L3), template reviewer, watch berkala
   selama run 501.
4. Setelah 501 ditutup: tulis **pra-registrasi audit P1** (scope L1â€“L4,
   protokol verifikasi, kriteria verdict) â†’ commit+push â†’ eksekusi L1
   (replay container, CPU-berat) â†’ L2/L3 â†’ report audit + entri registry.
5. Paralel dokumen (selama run): skema registry P3 + entri awal; kerangka
   P5 hanya sesuai kebutuhan P1/P2.
6. Keputusan lanjutan (P2 eksekusi, P4 rung berikutnya) diambil setelah
   verdict P1 pertama â€” or lebih cepat bila pemilik proyek meminta.

## 4. Definisi "banyak klaim" (metrik jujur)

Registry P3 adalah penghitungnya. Target realistis jangka menengah:
+1 entri audit (P1 â€” paket Gomila; kandidat berikutnya menyusul),
+1â€“2 entri pagar (P2 partial / P4 501), +N replikasi terverifikasi. Klaim universal tetap nol â€” sesuai prinsip Â§0.

## 5. Lampiran A â€” source pass-1 (URL + tanggal akses 2026-10-17)

- Tao, "A digestion of the proof of Sendov's conjecture", 2026-08-12:
  https://terrytao.wordpress.com/2026/08/12/a-digestion-of-the-proof-of-sendovs-conjecture/
- Gomila, Î› â‰¤ 0.1787854 (release 2026-08-20; unrefereed):
  https://github.com/judegomila/dbn-lambda-01787854-candidate-audit
- Hakimoglu-Brown, arXiv:2610.12803 (0.13963 kondisional), 2026-10-08:
  https://arxiv.org/abs/2610.12803
- Polymath15, arXiv:1904.12438; Rodgersâ€“Tao, Forum Math Pi 8 (2020).
- Gordon, SSRN 7608638 + repo stefangordon/dbn-upper-bound.
- Kislitsyn: frontier Peczarski 2006 (GPC â‰¤11) â†’ Gupta, arXiv:2607.23926
  (GPC â‰¤14; 2026; Zenodo 10.5281/zenodo.21865430); Olsonâ€“Sagan
  arXiv:1706.04985 (2017) = result keluarga poset (bukan sapuan); dossier
  â‰¤10 informal (kini bukan frontier).
- Catatan: semua nomor pass-1 wajib direcheck in pass-3; no ada angka
  in dokumen ini which dipakai sebagai input pra-registrasi tanpa pin ulang.

Ditulis oleh sesi analisis, 2026-10-17 (disetujui pemilik proyek;
in-commit setelah C4 diamankan).


