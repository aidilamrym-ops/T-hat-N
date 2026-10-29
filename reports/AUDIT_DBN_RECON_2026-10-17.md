# AUDIT DBN â€” Recon pass-3, potongan 1+2+3 (2026-10-17)

Status: **DRAF (potongan 1+2+3), dikomit 2026-10-17 (batch strategi; potongan 3 dilengkapi
selama run dim 501).** Non-binding; bahan mentah for
pra-registrasi audit P1 on `reports/MSAF_PORTFOLIO_2026-10-17.md` Â§2.
Ditulis selama C4 (+5 seed) berjalan, dilengkapi selama run dim 501;
**mesin no disentuh** â€” murni
pekerjaan dokumen. Semua kutipan verbatim dari dokumen source which
in-fetch 2026-10-17 (daftar in Â§6; result potongan 3 in Â§7.11â€“Â§7.12). Catatan anti-cocoklogi: seluruh angka
in bawah adalah **deskripsi klaim pihak ketiga**, bukan klaim MSAF; no
satu pun menjadi result kita sampai audit dieksekusi and dilaporkan.

## 0. Ringkasan potongan 1

- Objek audit: paket Gomila `Î› â‰¤ 893927/5000000 = 0.1787854`
  (`github.com/judegomila/dbn-lambda-01787854-candidate-audit`).
- Pin repo (diakses 2026-10-17): HEAD =
  `a74738deb6d5e0f76887cb36901da08b68dca705` (21 Agu 2026, commit
  "Add the Aristotle-formalized complete lemma layer under lean/aristotle
  (#29)"); PDF rilis mem-pin program links ke commit `6222740e`.
  Status self-stated (kutip): "computer-assisted unconditional proof, not
  yet peer reviewed". Eksplisit juga: "The result does not prove the
  Riemann hypothesis."
- **Temuan penentu potongan 1: paket already punya lapisan Lean 4.** Commit
  HEAD menambahkan 7 proyek Lean ("Aristotle", 2026-08-20), kernel-verified
  (kutip pesan commit): "lake build green on all seven; no sorry, axiom, or
  native_decide; #print axioms on all 223 theorems shows only [propext,
  Classical.choice, Quot.sound]; independent statement-faithfulness review
  passed (six faithful as generated; two statement-level transcription
  defects in tail_lemma corrected by hand and re-verified, documented in
  lean/aristotle/README.md)". Cakupan: TAIL_LEMMA, WINDOW_FREEZE_THEOREM,
  NATIVE_BINDING, ERROR_CONSTANT_WELD, DERIVATIVE_BOX_LEMMA, and weld
  Theorem 1.2 â†’ Î› â‰¤ 893927/5000000 â€” **with Polymath 1.2/1.3,
  Plattâ€“Trudgian, and numerik Arb sebagai hipotesis eksplisit**.
  Konsekuensi for audit kita: which tersisa in luar formalisasi persis
  wilayah kita â€” (a) weld theorem-source, (b) numerik Arb, (c)
  proof-to-code dari para produsen/verifier. Kandidat cek murah: jalankan
  gate anti-circularity kita (placeholder scan `sorry`/`admit`/`axiom`;
  cek klaim `#print axioms`) in atas `lean/`.
- Sumber asumsi "7/8" on arXiv:2610.12803 teridentifikasi:
  **OpenAI, "The Quasi-Riemann Hypothesis: A Zero-Free Half-Plane
  Re(s) > 7/8"** â€” preprint bertanggal 30 Sep 2026, dirilis 6 Okt 2026,
  section dari rilis ~722 makalah dari model internal (source sekunder;
  kini terpin â€” Â§7.8). Unrefereed. â†’ Masuk registry sebagai klaim pihak ketiga;
  **bukan** target audit kita sekarang.

## 1. Fakta terpin dari dokumen paket (angka eksak, seperti tertulis)

- Parameter: `X = 6000000185827`, `t0 = 129/800 = 0.16125`,
  `y0Â² = 87677/2500000 = 0.0350708`; `t0 + y0Â²/2 = 893927/5000000`;
  `y0Â² + 2t0 = 893927/2500000 < 1`; `1 âˆ’ 2t0 = 271/400`.
- Kriteria: instantiasi Polymath Theorem 1.2 (arXiv:1904.12438v2):
  - (i) verified height: Plattâ€“Trudgian `T_PT = 3000175332800`; kebutuhan
    hanya `X/2 = 3000000092913.5`; surplus eksak `350479773/2 > 0`.
  - (ii) final-time: jendela `x_N = 4Ï€(NÂ² âˆ’ t0/16)`, `W_N = [x_N, x_{N+1})`;
    `x_690988 < x_* < x_690989` (margin > 5.37Ã—10â¶ and > 1.19Ã—10â·);
    coverage `[x_*, x_3840001)`; 3,149,013 baris; empat prime-legs with
    `min T_N`: 0.000000791366 | 0.000315112459 | 0.000305788807 |
    0.000309285478; Dini cells `3^5,3^4,3^3,3^2`; worst ratio
    â‰¤ 0.99999860767275095 < 1; laju koreksi normalizer
    âˆ’1.3631121547576400 < 0; budget error:
    `e_A+e_B â‰¤ 0.000000000002057023688667`,
    `e_C,0 â‰¤ 0.000000233492848188649183`,
    `E_max â‰¤ 0.000000233494905212337849`; margin
    â‰¥ 0.000000557871094787 > 0.
  - Tail: `N_* = 3840000`; `D < 0.999721`;
    `(1âˆ’D)/M_max âˆ’ (e_A+e_B+e_C,0) > 0.00017352`.
  - (iii) barrier: `R = [X, X+1] + i[1809/10000, 1]`; margin tepi bawah
    `y0Â² âˆ’ (1809/10000)Â² = 234599/100000000 > 0`; error total in box
    < 0.000356523011600040 < 0.00125; indeks Riemannâ€“Siegel N = 690988
    in seluruh box; gate per-prisma:
    `M_i > D_z,i/(2(numâˆ’1)) + D_t,i(t_{i+1}âˆ’t_i) + 0.00125`; 883 prisma
    tertutup; 7,688 komponen koefisien diregenerasi; Taylor tail
    1.954234593244762Ã—10â»Â²Â² < 10â»Â²â°; margin prisma min
    â‰¥ 0.519849894613872543374989997.
  - Backend Prop 4.10: `verify_prop410_arb.c` (FLINT/Arb, 256 & 512 bit);
    konstanta sebagai rasional eksak (0.02=1/50, 0.626=313/500, 1.24=31/25,
    6.66=333/50, 10.50=21/2, 0.125=1/8); menolak presisi < 256 bit;
    transkrip `logs/prop410_arb_256.log` / `_512.log` (prasyarat P17).
    Jalur `mpmath.iv` lama = corroboration satu-backend (bukan independen).
  - Transkrip assembly (kutip): `RESULT: UNCONDITIONAL PROOF ASSEMBLY
    PASS` + `STATUS: computer-assisted unconditional proof; not yet peer
    reviewed.` â€” with peringatan README: "PASS" hanya berarti predikat
    terkode tersertifikasi; bukan peer review.
- Replay tersedia: container docker (linux/amd64, `--network none`,
  read-only); `verify.sh`; `scripts/run_barrier_replay.sh`,
  `run_tail_arb.sh`, `run_prop410_arb.sh`, `run_full_sweep.sh`
  (regenerasi 3,149,013 tuple vs 15 shard tersegel);
  `scripts/fetch_release_image_oci.py` + `verify_release_image_archive.py`
  (rekonstruksi image offline). Replay penuh tercatat: Linux/GCC/FLINT
  3.0.1 and macOS/Clang/FLINT 3.6.0, parser ketat 54-cek.
- Higiene file: dua file beda isi berbagi basename
  `gomila-proof-exposition.pdf`; hanya salinan `paper/external/` which
  ter-pin (SHA-256 + daftar koreksi). Eksposisi pihak ketiga (22 hal.)
  punya "known numerical, logical, attribution, and supplement-provenance
  defects" â†’ diperlakukan sebagai draf suplemen, bukan sign-off.
- Lisensi: kode MIT; dokumen CC BY; manuskrip authored + `and-reworking/`
  + program `independent/` (karya Dan Romik) = all rights reserved.
  **Untuk L2 kita no boleh (and no akan) memakai ulang program
  `independent/` maupun verifier mereka.**

## 2. Protokol adversarial paket â€” blueprint obligasi (ringkas)

Dari `ADVERSARIAL_REVIEW_PROTOCOL.md` (ID milik **mereka**; jangan
tertukar with P1â€“P6 portfolio kita):

| ID | Obligasi (ringkas) | Bukti utama |
|---|---|---|
| P1 | Teorema verified-height: normalisasi & rentang | BIBLIOGRAPHY; PROOF_NOTE Â§1â€“3 |
| P2 | Transkripsi Thm 1.2/1.3 & Lemma 8.4 | references/; BARRIER_CERTIFICATE |
| P3 | Corollary 6.6(vi) â‡’ bound `xâˆ’12, 10.50` (tanpa eq. (24) 10.44) | ERROR_CONSTANT_WELD; verify_error_constant_weld.py |
| G1 | Parameter eksak, konvensi tanda, substitusi final | CANDIDATE_PARAMETERS; NATIVE_BINDING; verify_assembly_1787854.py |
| F1 | Konvolusi native finite + jembatan effective-error | NATIVE_BINDING; WINDOW_FREEZE_THEOREM |
| F2 | Dini atas + monotonisitas normalizer (semua nol/kink) | provenance/TRIANGLE_Y_DINI_THEOREM.independent.md |
| F3 | Semua baris finite + seam jendela setengah-terbuka | logs/; scripts/run_full_sweep.sh |
| T1 | Tail all-N: endpoint-cap, partisi, monotonisitas | TAIL_LEMMA; TAIL_PROVENANCE |
| T2 | Dua implementasi tail independen | verify_tail_arb.c; Python interval; transkrip tersegel |
| B1 | Batas derivatif box, kuadratur, Taylor, provenance koefisien | DERIVATIVE_BOX_LEMMA; BARRIER_CERTIFICATE; barrier/ |
| B2 | Setiap prisma + seam + homotopi winding bebas nol | barrier/certificates/; run_barrier_replay.sh |
| C1 | Overlap domain + weld tiga hipotesis tanpa pelemahan | PROOF_NOTE Â§4â€“7; verify_assembly_1787854.py |

Poin prosedural mereka which kita adopsi:

- "A successful repository replay is necessary evidence, but it is not by
  itself a mathematical review." â†’ L1 â‰  review.
- Standar independensi: "An implementation counts as independent only if
  it does not reuse the repository's source, parser, interval partition,
  or intermediate decimal tables."
- Clean-room: transkripsi teorema langsung dari paper versi-nya, tanpa
  prosa ringkasan repo.
- Matriks limit: t=0, t=t0, y=y0, y=âˆš(1âˆ’2t), endpoint jendela, transisi
  presisi, N=3840000, nol koefisien/kink, floor/ceil bergerak, cabang log,
  endpoint ball, face pertama/terakhir prisma. "Passing interior sample
  points is not evidence for an untested boundary."
- 10 mutation tests wajib (kill rate dilaporkan; survivor =
  release-blocking sampai terbukti irrelevan).
- Perturbasi parameter (t0, y0, cutoff, presisi, mesh) harus bergerak ke
  arah which diprediksi; pipeline harus menolak konfigurasi gagal.
- Sign-off terpisah 7 kategori: theorem-source / reduksi tulisan tangan /
  proof-to-code / replay lingkungan bersih / komputasi independen /
  result mutasi / asumsi tak terselesaikan.
- Lean bukan prasyarat rilis bagi mereka; jangan puas with "axiom semua
  analitik lalu restate desimal".

## 3. Protokol audit MSAF â€” L1â€“L4 versi konkret (draf pra-registrasi)

- **L1 â€” replay & provenance (bukan klaim matematis).** Di container
  ter-pin: `verify.sh` + `run_prop410_arb.sh` + `run_tail_arb.sh` +
  `run_barrier_replay.sh` (+ `run_full_sweep.sh` bila anggaran CPU 4-core
  memungkinkan). Output: transkrip + sha artefak; dilabeli "repository
  replay reproduction" â€” mengikuti kalimat mereka sendiri.
- **L2 â€” replikasi independen (implementasi sendiri; tanpa source/parser/
  partisi/tabel desimal mereka).** Prioritas:
  1. Budget Prop 4.10 dari rumus (20)â€“(23)+(vi): bandingkan
     `e_A+e_B`, `e_C,0`, `E_max`, and margin 5.57871094787Ã—10â»â·.
     (Mereka menutup blocker satu-backend via C/FLINT; replikasi kita =
     cross-implementation. Pilihan library/bahasa diputuskan in
     pra-registrasi; wajib berbeda dari jalur C mereka.)
  2. Tail lane: re-derivasi partisi + spot cek koridor dua sisi
     `0.999719 < D < 0.999721` + margin pasca-error
     `> 0.0001735209373337` (Â§7.2).
  3. Barrier: subset prisma tersempit + seam â€” winding via enclosure
     sendiri (bukan sampling interior).
  4. Window freeze & sign map: re-derivasi bracket Machin/sqrt rasional
     eksak + aljabar affine `verify_criterion_sign_map.py` (murah; L2 awal
     which baik).
  Independence note: dua presisi program which sama â‰  independen (standar
  mereka, kita ikuti).
- **L3 â€” clean-room theorem-source.** Transkripsi Thm 1.2/1.3 + Lemma 8.4
  dari arXiv:1904.12438v2 + Plattâ€“Trudgian versi refereed; bandingkan
  domain/endpoint/kuantor/substitusi; verdict per hipotesis (i)(ii)(iii) +
  weld. Batasan jujur: satu operator â†’ dua pass terpisah-waktu dicatat
  sebagai mitigasi, bukan dua auditor independen.
- **L4 â€” verdict.** Tabel per-obligasi (pakai ID blueprint mereka)
  {accepted / rejected / unresolved} + referensi file/baris; daftar
  coverage eksplisit (section which TIDAK diaudit); kata-kata standar:
  "PASS otomatis mereka bukan peer acceptance"; agregat: GAP-FOUND
  (deskripsi) / INDEPENDENTLY-CERTIFIED (section X) / UNVERIFIABLE
  (section mana, kenapa). Entri registry P3 menyusul.
- Cek murah tambahan (pra-L2): gate anti-circularity kita atas `lean/`
  (scan `sorry`/`admit`/`axiom`; verifikasi klaim `#print axioms`;
  placeholder scan). Ini menjawab langsung question P8(3) mereka
  ("is any software check circular").
- Anggaran: full sweep + 883 prisma = jamâ€“hari in 4-core (data
  MAXIMUM_CHECKS: replay produsen finit â‰ˆ 16m45s + comparator 1.89s in
  mesin audit mereka; barrier + tail lane menambah jam); scope wajib vs
  opsional diputuskan **sebelum** eksekusi in pra-registrasi.

## 4. TO-PIN â€” status per potongan 2 (2026-10-17)

Selesai hari ini (dipercepat atas persetujuan; detail in Â§7):

- [x] OCI digest + container ter-pin: image teruji
      `ghcr.io/judegomila/dbn-lambda-01787854-review@sha256:6e29bc53â€¦`;
      rilis immutable `review-01787854-v3` (28 Jul 2026; commit
      `2e9976c4â€¦`; seal `89a20156â€¦`; arsip OCI `87a4695eâ€¦`) â€” Â§7.1.
- [x] `REVIEW_SCOPE.md` + `MAXIMUM_CHECKS.md` + `CANDIDATE_PARAMETERS.md`
      dibaca; replay Level Aâ€“E + hierarki bukti terpetakan â€” Â§7.2â€“Â§7.3.
- [x] `paper/external/README.md`: cros-cek eksposisi pihak ketiga (â‰ˆ9
      kelas koreksi; anchor `2e9976c4â€¦`) â€” Â§7.4.
- [x] Plattâ€“Trudgian (arXiv:2004.09765v1; Bull. LMS) & Polymath15
      (arXiv:1904.12438v2, versi final 4 Agu 2019) dari source primer;
      transkripsi penuh Â§Theorem 1.2 â†’ potongan 3.
- [x] OpenAI "The Quasi-Riemann Hypothesis": terpin ke repo `openai/math`
      (+ entry `lean/formalization.yaml`) â€” Â§7.8. Ditambah: audit korpus
      eksternal (proyek lain) dibaca + 6 pin SHA-256 diverifikasi ulang
      kita â†’ `reports/REF_AW_OAI_AUDIT_2026-10-17.md`.
- [x] Hakimoglu-Brown arXiv:2610.12803v1: rantai dependensi + titik masuk
      asumsi (M(0) â‰¤ 9/16) â€” Â§7.6.
- [x] Kislitsyn/GPC frontier: Peczarski 2006 (â‰¤11) â†’ **Gupta 2026
      arXiv:2607.23926 (â‰¤14; census 1.338.193.159.771 poset-14)** â€” Â§7.7.
- [x] `independent/README.md`: celah prop43 + kandidat promosi Romik â€”
      Â§7.5.

Potongan 3 (mulai 2026-10-17; **selesai 2026-10-17 selama run dim 501**):

- [x] `BARRIER_CERTIFICATE.md` + `DERIVATIVE_BOX_LEMMA.md` dibaca penuh
      (bahan butir barrier L2) â€” ringkasan Â§7.9â€“Â§7.10.
- [x] Transkripsi penuh Thm 1.2/1.3 + Lemma 8.4 dari arXiv:1904.12438v2
      (bahan L3; PDF versi terkunci kini ter-pin â€” Â§7.9; **selesai**:
      PDF byte-identik (`references/README.md`), source e-print v2
      ter-pin, digest per-region â€” Â§7.11).
- [x] `references/README.md`: SHA-256 empat PDF upstream ter-pin â€” Â§7.9.
- [x] `and-reworking/`: listing per 2026-10-17 (unsealed; `CLAUDE.md`,
      `code/`, `latex/`); `REVIEWER_REPORT_TEMPLATE.md` ternyata in **root
      repo** â€” dibaca 2026-10-17 (SHA + ringkasan Â§7.12).
- [x] Repo GPC: struktur terkonfirmasi (`src/`, `tests/`, `scripts/`,
      `paper/`, `data/`) â€” verifier kecil in `tests/`+`src/` (pin detail
      saat P2 dipra-registrasi).
- [x] Watch 2026-10-17 (dua cek; cek-2 saat potongan 3): HEAD tetap
      `a74738de` (PGP-signed); rilis tetap hanya `review-01787854-v3`;
      revisi OpenAI `paper2.pdf` (5 Okt) masih TO-PIN.

## 5. Peta klaim (bahan awal registry P3)

| Klaim | Sumber | Status | Dependensi | Sikap kita |
|---|---|---|---|---|
| Î› â‰¥ 0 | Rodgersâ€“Tao, Forum Math Pi (2020) | refereed | â€” | acuan |
| Î› â‰¤ 0.2 | Plattâ€“Trudgian, Cor. 2 (kombinasi Polymath15); arXiv:2004.09765v1; Bull. LMS | refereed | â€” | acuan |
| Î› â‰¤ 0.1875 | "Mosaic Intelligence", Zenodo 10.5281/zenodo.21175533 (`references/dbn21a-main.pdf`) | non-refereed (rekaman Zenodo) | â€” | predecessor paket (`vendor/dbn21a`); acuan |
| Î› â‰¤ 0.1787854 | Gomila (20 Agu 2026), repo + Lean layer | **unrefereed** | Plattâ€“Trudgian; Polymath 1.2/1.3; cert Arb (repo) | **target audit P1** |
| Î› â‰¤ 0.13963 | Hakimoglu-Brown, arXiv:2610.12803v1 (8 Okt 2026) | unrefereed + **kondisional** | asumsi "7/8" = OpenAI preprint (unrefereed); masuk sekali in M(0) â‰¤ 9/16 (Â§7.6) | registry |
| "7/8 zero-free half-plane" | OpenAI, `openai/math` (30 Sep 2026; rilis ~722 makalah) | unrefereed; Lean "dideskripsikan" (Â§7.8) | â€” | registry; bukan scope audit |
| Î› (Gordon) piecewise-affine | SSRN + `stefangordon/dbn-upper-bound` | unrefereed | â€” | TO-PIN status |
| "Collective Contractionâ€¦" | arXiv:2609.37164 (Sep 2026) | belum dinilai | â€” | TO-PIN |
| GPC â‡’ 1/3â€“2/3 (â‰¤14 elemen) | Gupta, arXiv:2607.23926 (27 Jul 2026; Zenodo 10.5281/zenodo.21865430) | unrefereed | census 1.338.193.159.771 poset-14; Peczarski â‰¤11 (2006) | kandidat P2 (Â§7.7) |

## 6. Sumber (diakses 2026-10-17)

- `raw.githubusercontent.com/judegomila/dbn-lambda-01787854-candidate-audit/main/`
  â†’ `README.md`, `PROOF_NOTE.md`, `OPEN_REVIEW_QUESTIONS.md`,
  `ADVERSARIAL_REVIEW_PROTOCOL.md` (semua in-fetch hari ini).
- `api.github.com/repos/judegomila/dbn-lambda-01787854-candidate-audit/commits?per_page=1`
  â†’ HEAD `a74738deâ€¦` (21 Agu 2026) + pesan commit Lean (dikutip Â§0).
- arXiv:2610.12803 (abstrak, 8 Okt 2026); arXiv:1904.12438v2 (dirujuk
  dokumen paket); pencarian web for OpenAI "Quasi-Riemann Hypothesis"
  (result sekunder: Medium/BigGo/Reddit/awesome-ai-proofs â€” simpang-siur,
  TO-PIN).
- Potongan 2 (raw, hari ini): `CONTAINER_IMAGE.md`, `REVIEW_SCOPE.md`,
  `MAXIMUM_CHECKS.md`, `CANDIDATE_PARAMETERS.md`, `BIBLIOGRAPHY.md`,
  `paper/external/README.md`, `independent/README.md`; API rilis
  `api.github.com/.../releases/tags/review-01787854-v3`.
- Potongan 2 (eksternal): arXiv:1904.12438 (abs), arXiv:2004.09765 (abs),
  arXiv:1706.04985 (abs), arXiv:2607.23926 (abs) +
  `raw.githubusercontent.com/agupta/gold-partition-conjecture/main/README.md`,
  `arxiv.org/html/2610.12803v1` (teks penuh),
  `raw.githubusercontent.com/openai/math/main/lean/formalization.yaml`.
- Eksternal (proyek lain; 2026-10-17): audit korpus `openai/math` +
  vault `MSAF Family 017` (`github.com/aidilamrym-ops/the-asymmetric-wager-msaf-family017`)
  â€” verifikasi silang + ringkasan:
  `reports/REF_AW_OAI_AUDIT_2026-10-17.md`,
  `reports/REF_AW_MSAF_FAMILY017_2026-10-17.md`.

## 7. Potongan 2 â€” result (dipercepat 2026-10-17, atas persetujuan pemilik)

Murni dokumen (fetch + baca); mesin C4 no disentuh. Checklist Â§4
diperbarui; sisanya = potongan 3. Semua angka in Â§7 adalah deskripsi
klaim pihak ketiga (anti-cocoklogi: bukan result MSAF).

Sorotan audit-relevan:

1. Identitas rilis ter-pin lengkap (commit/tag/seal/OCI digest/arsip
   offline) â†’ L1 bisa dijalankan tanpa tebakan (Â§7.1).
2. Mereka **already** menemukan & memperbaiki 3 defek theorem-level lewat
   audit adversarial internal sebelum seal (Â§7.2) â€” kelas kesalahan itu
   jadi target eksplisit L2 kita, bukan asumsi "already bersih".
3. Eksposisi pihak ketiga already mereka cros-cek (â‰ˆ9 kelas koreksi,
   Â§7.4) â€” pola banding "eksposisi â†” segel" which kita tiru in L3.
4. Celah which mereka akui sendiri: reproduktibilitas `prop43` (Â§7.5).
5. Frontier P2 bergerak: GPC â‰¤14 (2026) melampaui â‰¤11 (Peczarski 2006)
   (Â§7.7).

### 7.1 Identitas rilis & container (pin L1)

- Rilis immutable `review-01787854-v3` (28 Jul 2026): commit
  `2e9976c4becbf97e31c56fe75fce07cdff5dd4ea` (single parentless commit â€”
  "single evidence surface intended for an external referee"), tree
  `7f15ecf8â€¦`, tag `585586bbâ€¦`; seal `SHA256SUMS` sha256 `89a20156â€¦`;
  release manifest sha256 `e0f134caâ€¦`; PDF referee sha256 `b1151d56â€¦`.
- **OCI digest teruji:** `ghcr.io/judegomila/dbn-lambda-01787854-review@sha256:6e29bc53adc5a4337802da2b5a219720e3da9dcc1b87c546b96b6126d8b9975d`.
- Arsip OCI offline (tanpa registry): `dbn-lambda-01787854-review-v3.oci.tar`
  sha256 `87a4695eâ€¦`, 172.810.240 byte.
- Container: Ubuntu 24.04 linux/amd64 (digest child-manifest ter-pin in
  `Dockerfile`); replays `--network none`, read-only.
- Eksekusi terverifikasi in rilis: run `30317899517` (finite replay penuh
  3.149.013 baris diregenerasi) and run `30322974859` (satu image, dua
  lane).

### 7.2 Parameter & margin tambahan (bahan L2)

Dari `CANDIDATE_PARAMETERS.md` + `MAXIMUM_CHECKS.md` (penguatan Â§1):

- Head konvolusi `M = 153814`; head error `M_err = 3000`;
  `M_max < 1.608290`; koridor tail **dua sisi**
  `0.999719 < D < 0.999721` (jadi `0.000279 < 1 âˆ’ D < 0.000281`);
  `(1 âˆ’ D)/M_max > 0.0001735326089372`; error tail
  `< 0.000000011671604`; margin pasca-error `> 0.0001735209373337`
  (angka presisi ini menggantikan pembulatan `0.00017352` in Â§1).
- Bracket eksak: `1872719/10^7 < y0 < 23409/125000`;
  `8231038/10^7 < âˆš(1âˆ’2t0) â‰¤ 8231039/10^7`.
- Ladder finit (baris / min T_N @N): P11 38012 / 0.000000791366 @690988;
  P7 90000 / 0.000315112459 @729000; P5 209000 / 0.000305788807 @819000;
  P23 2812001 / 0.000309285478 @1028000.
- Kotak finite leg lanjut: `t âˆˆ [161250000/10^9, 161250001/10^9]`,
  `y0Â² = 350708/10^7`; kotak singleton P11 `t = 16125/100000`.
- Runtime lock historis (paket finit): image `dbn21a-flint`
  `sha256:bedf7303â€¦`; Python `mpmath 1.4.1`.
- Dua toolchain barrier: Linux/GCC/FLINT 3.0.1 (transkrip sha256
  `2d010f70â€¦`; margin min berakhir â€¦997) and macOS/Clang/FLINT 3.6.0
  (`34f8ed82â€¦`; berakhir â€¦999); parser ketat 54 cek. Enclosure winding
  agregat `[âˆ’8.95, 8.95]Ã—10â»Â¹Â³`.
- Waktu (mesin audit mereka): replay produsen finit penuh â‰ˆ 16m45s;
  comparator tersegel 1.89s â€” bahan estimasi biaya L1 in 4-core.
- Cek langsung 256-bit: 30 singleton; UBSan bersih. Dini 180/256 bit
  with margin rasio `1 âˆ’ ratio_ub = 0.00000139232724905`. Native
  binding: 13 gate; 216 uji fase kompleks; slack min > 0.03056. Window
  freeze: Machin rasional Ï€ < 10â»Â¹â°â°; margin jendela 5.37e6 / 1.19e7.
- Higiene: ASan/UBSan/LSan; scrub `PYTHONOPTIMIZE`; scrub override
  `BARRIER_*`; perbaikan leak 4.304 byte / 91 alokasi.
- **Audit adversarial internal mereka (sebelum seal): 3 defek
  theorem-level ditemukan & diperbaiki** â€” (1) bound sudut ter-freeze
  lemah, (2) integral-vs-sum, (3) proyeksi ball kompleks ke section riil
  melanggar callback holomorfik FLINT â€” plus probe terarah 126/256 bit;
  source barrier teraudit sha256 `76e4d4f8â€¦`. Kutipan status mereka:
  "This is an internal adversarial audit, not the requested external
  mathematical review."

### 7.3 Replay Level Aâ€“E & hierarki bukti (`REVIEW_SCOPE.md`)

- Level replay: **A** `verify.sh`; **B** replays dalam container ter-pin;
  **C** replay barrier; **D** tail Arb; **E** full sweep (3.149.013 baris
  â‰ˆ 16m45s; comparator 1.89s).
- Hierarki bukti 6 level; kalimat kunci (kutip): "Agreement at levels 4â€“6
  cannot repair an error at levels 1â€“3."
- Lane independen: `prop43` & `prop62` = implementasi independen;
  `prop410` = **same-backend** (berbagi `mpmath.iv` + fungsi budget
  identik baris-per-baris) â†’ cross-backend otoritatif =
  `verifiers/verify_prop410_arb.c` (FLINT/Arb; prasyarat P17).
- Ruang kerja tak tersegel `and-reworking/` + `research/` = BUKAN bukti;
  promosi lewat `independent/README.md`.
- Daftar "what is not claimed" eksplisit (termasuk: belum lulus review
  independen; no menetapkan RH) â€” kita adopsi in kalimat L4.

### 7.4 Cros-cek eksposisi pihak ketiga (`paper/external/README.md`)

- Eksposisi 22 hal.: SHA-256
  `fd98f4e91dea6c02c7705665aaa95d0cb0b0cf46f8a22276e2c693a56a489313`,
  442.088 byte, pdfTeX 1.40.25, tanggal terlihat 27 Jul 2026; baseline
  cros-cek: tag `review-01787854-v3` / commit `2e9976c4â€¦`.
- â‰ˆ9 kelas koreksi, in antaranya: arah dependensi terbalik; dua floor in
  eksposisi LEBIH KUAT dari nilai tersegel (0.000315112481 vs
  0.000315112459; 0.000305788816 vs 0.000305788807 â€” tanda bahaya kita
  juga); isu pembulatan total error; pertidaksamaan tail terbalik
  (`1 âˆ’ D < 0.000279` vs koridor tersegel `0.000279 < 1 âˆ’ D < 0.000281`);
  Thm 5.6 memakai bound bulat (`> 0.0001735` vs `> 0.0001735326089372`);
  premis kelayakan endpoint-cap `Ïƒ > (t/2)Â·log c`; suplemen finit
  eksternal (prop43 dkk.) which hilang; orientasi independence winding;
  bahasa/atribusi.
- Transkrip historis 38 gate (era "candidate") vs verifier kini 40 gate;
  kutip: "No fatal counterexample â€¦ found in this cross-check. That is
  not independent peer acceptance."

### 7.5 Lane independen Romik (`independent/README.md`)

- `prop43` (Prop 4.3): â‰ˆ3 jam atas sembilan shard; invokasi dipulihkan
  (`INVOCATIONS.md`); **belum ada job CI** which menjalankannya (butuh
  workflow khusus) â†’ celah reproduktibilitas which mereka tandai sendiri.
- `prop62` independen; `prop410` same-backend (lihat Â§7.3).
- Kandidat promosi BELUM dipromosikan: `prop49`, `prop510`, `prop612`,
  `prop65`.
- Origin: ditulis Dan Romik; dipromosikan dari `and-reworking/code/` on
  commit `f4d2d03ebc6342b3bce4e0c0b695b82f2e213f1a`; tersegel and
  dieksekusi lewat `verifiers/verify_independent_crosscheck.py`.

### 7.6 Hakimoglu-Brown arXiv:2610.12803v1 â€” rantai dependensi

- Versi: draf 7 Okt 2026; v1 arXiv 8 Okt 2026; CC BY 4.0.
- Kondisional: asumsi "7/8" masuk **tepat sekali** in `M(0) â‰¤ 9/16` via
  `|y| = |2Â·Re Ï âˆ’ 1| â‰¤ 3/4`; result `Î› â‰¤ 0.13963`. Kutip: "The
  seven-eighths assertion â€¦ remains an assumption and its source proof
  is not assessed here."
- Jalur perbaikan: 0.1938798366 â†’ 0.1797275414 â†’ 0.16408 â†’ 0.13963
  (bobot panas + produk Euler + subdivisi waktu; step akhir
  perbandingan kernel via S' vertikal).
- Memakai boundary Â§8.4 Polymath (published) + tinggi terverifikasi Platt
  3.06Â·10^10 for Lemma 2; mencatat Plattâ€“Trudgian Cor. 2 = `Î› â‰¤ 0.2`.
- CATATAN KOREKSI mereka on eq. (91) Polymath (suku interpolasi
  `D_t|t'âˆ’t|` vs `/(2n)`) â€” status kutipan: "This inspection concerns
  that formula only and is not a verification of the full computation."
  â†’ material TO-PIN potongan 3; belum mengubah apa pun.
- Makalah pendamping in rilis OpenAI which sama: `Re s > 11/12`
  (q0 = 25/36); tanpa tabel tersertifikasi.

### 7.7 Frontier Kislitsyn/GPC (P2) â€” TERUPDAT

- Pin lama (pass-1): dossier informal â‰¤10 (2.769.961 poset) â€” bukan lagi
  frontier.
- **Peczarski 2006:** GPC (konjektur Peczarski; GPC â‡’ 1/3â€“2/3)
  diverifikasi komputer for semua poset â‰¤11 elemen.
- **Baru (27â€“30 Jul 2026):** Anish Gupta, "Balance Constants, Majority
  Cycles, and the Gold Partition Conjecture through Fourteen Elements",
  arXiv:2607.23926 (v2): data ekstremal eksak SEMUA
  **1.338.193.159.771 poset-14 unlabeled**; konstanta balance terkecil
  >1/3 = `37/106`; terkecil on poset non-ordinal-sum nontrivial =
  `254/725` ("ladder with broken rungs", konfirmasi konjektur Peczarski
  orde 14); orde 12/13 mereproduksi census De Loofâ€“De Baetsâ€“De Meyer;
  no ada konstanta balance in celah >1/3 which diduga kosong.
  Aritmetika eksak (tanpa float in jalur keputusan); witness dihitung
  ulang dari string witness oleh program tanpa algoritma bersama.
- Repo `agupta/gold-partition-conjecture`: Zenodo DOI
  10.5281/zenodo.21576029 (manuscript); arsip imutabel Release 2.1
  `10.5281/zenodo.21865430`, Release 2 `10.5281/zenodo.21696940`;
  berisi source GPC eksak + census "production-equivalent", tool
  sharding/agregasi, verifier kecil independen.
- Implikasi P2: frontier = **â‰¤14 (klaim 2026, unrefereed)**; volume:
  â‰¤12 â‰ˆ 1,1e9; â‰¤14 â‰ˆ 1,3e12 poset â€” arah realistis: (i) re-verifikasi
  kecil independen (â‰¤9/10/11) + audit metodologi census â‰¤14, or
  (ii) sweep parsial bersertifikat with pruning. Diputuskan in
  pra-registrasi P2 (setelah C4/501).

### 7.8 OpenAI "The Quasi-Riemann Hypothesis" â€” pin registry

- Repo resmi: `github.com/openai/math` (Apache-2.0). Entry katalog
  `lean/formalization.yaml` (skema mathlib-initiative v0.4):
  "The Quasi-Riemann Hypothesisâ€¦", `authors: [OpenAI]`, id
  `../preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/paper.pdf`.
  Revisi 5 Okt 2026 = directory tersendiri (lineage resmi Sep-30 â†’
  Oct-5; dikonfirmasi audit eksternal). Perbedaan isi kedua edisi belum
  diperiksa (TO-PIN).
- Status katalog: "Partial progress"; HB Â§1.1: "The repository also
  describes a Lean formalization of the zeta and Dirichlet statements."
  â†’ klaim Lean "dideskripsikan", **no** diverifikasi kita.
- Konteks: rilis ~722 makalah dari model internal (6 Okt 2026; source
  sekunder). Unrefereed; registry saja.
- **Pembaruan (audit eksternal proyek lain; pin kami verifikasi ulang
  2026-10-17):** keluarga 003 = {Sep-30, Oct-5, Landauâ€“Siegel-Oct-1};
  `formalization.yaml` memuat entri Sep-30 (zeta) + Landau (Dirichlet) â€”
  cocok with frasa HB Â§1.1 â€” and **edisi Oct-5 belum terformalisasi**
  (antrean unformalized rank 572; impact 0). Sep-30 = top-10 in-degree
  korpus; SCC#100 = siklus Sep-30 â†” Landau. Detail:
  `reports/REF_AW_OAI_AUDIT_2026-10-17.md`.

### 7.9 Potongan 3 â€” result awal: referensi terkunci & barrier certificate

- **Referensi versi-terkunci mereka (`references/README.md`)** â€” 4 PDF,
  SHA-256 diharapkan: Polymath15 `1904.12438v2` (68 hal.) `60d0d2d3â€¦`;
  Plattâ€“Trudgian `2004.09765v1` (8 hal.) `3362f66aâ€¦`; Romik `1902.06330`
  (background) `e81eecf4â€¦`; `dbn21a-main.pdf` (Zenodo 21175533, CC BY 4.0)
  `10648df3â€¦`. L3 kita: unduh dari URL arXiv persis + verifikasi SHA â€”
  byte-identik with versi which mereka review. **Selesai 2026-10-17
  for Polymath15: cocok penuh (68 hal.); transkripsi + digest Â§7.11.**
- **Barrier certificate (`BARRIER_CERTIFICATE.md`, ringkas)** â€” klaim:
  `H_t(z) â‰  0` for `z âˆˆ R = [X, X+1] + i[1809/10000, 1]`, `0 â‰¤ t â‰¤ t0`;
  superset persegi dari barrier lengkung Thm 1.2. Lebar:
  `y0Â² âˆ’ (1809/10000)Â² = 234599/100000000 > 0`; `âˆš(1âˆ’y0Â²) < 1`;
  `0 < y0Â² + 2(t0âˆ’t) â‰¤ y0Â² + 2t0 < 1`.
  - Error uniform (termasuk `t=0` via argumen limit 4 step, bukan
    asumsi): `e_A+e_B < 3.639278679550541e-10`,
    `e_{C,0} < 0.000356522647672172`, total `< 0.000356523011600040 <
    0.00125` (256-bit Arb); transkripsi Python which sengaja lebih kasar:
    `< 0.000356942`. Keduanya memakai `xâˆ’6.66` (A+B) and `xâˆ’12, 10.50`
    (C,0); **no ada** which memakai angka `10.44` in eq. (24).
  - Gate prisma: `M_i > D_z,i/(2(numâˆ’1)) + D_t,i(t_{i+1}âˆ’t_i) + 0.00125`;
    faktor 1/2 rigor sebagai homotopi bebas-nol (argumen disk), bukan
    estimasi interpolasi pointwise; D_t dievaluasi ulang per prisma which
    diusulkan (tanpa asumsi monotonisitas).
  - Poligon limit: enclosure endpoint bebas nol; kenaikan argumen in
    `(âˆ’Ï€, Ï€)`; winding in `(âˆ’1/4, 1/4)`; orientasi argumen terbalik vs
    beberapa eksposisi (no mengubah kesimpulan winding = 0).
  - Koefisien tersimpan: 62Ã—62 desimal 20 digit + radius
    `10â»Â²â°Â·max(1,|c|)`; `StoredSumSinglemat_interval.c` meregenerasi 7.688
    komponen (0 kegagalan kontainmen, rasio allowance terbesar < 0.018);
    `StoredSumTaylorTail_cert.c`: sisa Taylor < 1.954234593244762e-22.
  - Hasil tersegel: 883 prisma tertutup; seam serialisasi byte-identik;
    `t=0` eksak; endpoint akhir `129/800`; winding agregat
    `[âˆ’8.95, 8.95]Ã—10â»Â¹Â³`; margin minimum `0.519849894613872543374989997`;
    terminal `RESULT: CLOSED SLAB CERTIFIED`; dua transkrip (Linux/GCC/
    FLINT 3.0.1 kanonik + macOS/Clang/FLINT 3.6.0) lolos 54 cek parser.
  - Prisma terakhir boleh berakhir â‰¥ t0; teorema memakai prisma âˆ© [0,t0].

### 7.10 Derivative box lemma & sisa item potongan 3

- **`DERIVATIVE_BOX_LEMMA.md` (ringkas)** â€” memperbaiki kelas defect
  nyata: Lemma 8.4 bersifat pointwise; evaluasi in `(X, y_min)` lalu
  dipakai sebagai bound kotak TIDAK konservatif (mis. suku `log(x/(4Ï€n))`
  on D_t membesar with x; in `t=0` tak ada decay panas).
  Perbaikan: `c(x,y) = Â¼log q(x) âˆ’ hâ‚Š/(2xÂ²)` naik in x,y
  (`h_y = âˆ’3 + 4(1+2y)/xÂ² < 0`, `h_x = âˆ’8y(1+y)/xÂ³ â‰¤ 0`);
  `Re s_* â‰¥ (1+y)/2 + tÂ·c(X,y_min)` seragam in kotak; gate fail-closed
  `1/(4(X+1)) âˆ’ 2/XÂ³ > 0` (for `c_x > 0`); gate slope A-core
  `Î· â‰¤ 0.02 âˆ’ Â½log q(X) + t0Â·log N/(2(Xâˆ’6)) + Â½log N < 0` menjamin
  maksimum in `y = y_min`; `2 log N < log(X/(4Ï€))`.
  - Sum diskret: **bukan** kuadratur mentah; head 16 suku dievaluasi
    langsung (Arb) + integral ekor which dibuktikan menurun (gate
    `c0 > Â½log N`, `(y_minâˆ’1)/2 + 1/log K < 0`, `C âˆ’ log(N)/4 > 0`);
    `Î£ â‰¤ Î£â‚..â‚â‚† + âˆ«â‚â‚†..N`.
  - Kontrak kuadratur holomorfik: callback menerima ball kompleks penuh;
    `acb_log_analytic` / `acb_pow_analytic` (flag analitik tepat saat
    `order â‰  0`); tolak order > 1; sentuhan branch cut â†’ nonfinite â†’
    fail-closed; counter runtime mewajibkan minimal satu panggilan
    `order=1` per integral. â†’ kelas defect which sama with temuan audit
    internal mereka (proyeksi real) kini punya gate eksplisit.
- **`and-reworking/`** (per 2026-10-17): berisi `CLAUDE.md` (13,5 KB â€”
  instruksi workspace Romik), `code/` (prop43, prop49, prop510, prop612,
  prop62, prop65 + `runs/`), `latex/` (eksposisi + manuskrip
  `research-paper/debruijn-newman.tex`); unsealed. Template
  `REVIEWER_REPORT_TEMPLATE.md` ternyata in **root repo** (bukan in
  and-reworking) â€” dibaca 2026-10-17; ringkasan + kutipan Â§7.12.
- **Repo GPC** (`agupta/gold-partition-conjecture`): struktur `src/`,
  `tests/`, `scripts/`, `paper/`, `data/`, `Makefile`, `CITATION.cff` â€”
  kandidat re-verifikasi kecil in `tests/`+`src/` (pin detail saat P2
  dipra-registrasi).
- **Watch 2026-10-17:** HEAD paket Gomila **tetap** `a74738de` (PGP-signed,
  tree `babfa77eâ€¦`, parent `6d3b2230â€¦`); no ada commit baru sejak
  21 Agu 2026.

### 7.11 Transkripsi theorem-source L3 â€” Thm 1.2/1.3 + Lemma 8.4 (selesai)

Provenance (fetch + hash in mesin ini, 2026-10-17; run dim 501 which
sedang berjalan **no disentuh**; PDF/e-print **no dikomit** â€”
kebijakan redistribusi sama seperti paket):

- PDF terbit: `https://arxiv.org/pdf/1904.12438v2`, 68 hal.; SHA-256
  `60d0d2d381227d32f98535a5c43dedb86e333a9006d6819f0bdebdd734085603`
  = **byte-identik** with hash acuan `references/README.md` paket
  (unduh-verifikasi persis jalur L3 Â§7.9). Verifikasi silang render:
  pernyataan Thm 1.2 in hal. 2, Thm 1.3 in hal. 6, Lemma 8.4 in hal. 46.
- Sumber transkripsi: `https://arxiv.org/e-print/1904.12438v2` (tar
  2.229.636 byte, sha256
  `1be3bc38d203ad0142f1c97c267c7deaa06b84c97716c9a1ec1f56456d826863`;
  isi: `debruijn.tex` + 23 PNG). `debruijn.tex` = 170.017 byte, sha256
  `560a28fe31bec92dd793820222e9e73a1fc6958a08344033a946b2ccaba225e5`
  (source submisi v2; basis file PDF which direview).
- Semua blok in bawah = teks **verbatim** dari `debruijn.tex`; angka
  baris mengacu ke file itu. Digest per-region (sha256 atas teks UTF-8,
  LF, termasuk newline akhir, **tanpa** nomor baris; raw vs norm =
  rstrip per baris â€” identik kecuali thm13):

  | region | baris tex | byte | sha256 |
  |---|---|---|---|
  | (5) domain | 168â€“170 | 111 | `4353e6c842cf7ff5c811228a53212ea2260a619824e581d4843474a827fbb12e` |
  | Thm 1.2 | 145â€“152 | 765 | `06290d46cbbbe1670c4e9d4ee9957f0f8dc06367a9907644a654d048b7e331ec` |
  | Thm 1.3 | 223â€“244 | 2019 | raw `2bdd6d87d0a0c1d90a114b934eb905a46a4c40e99cb0fcc27993414ea0e1e08d` / norm `cebe9801b3c2b57414fa65d55506df0987dd01f94851bada291e51d6a85d68b2` (beda hanya spasi akhir baris 234) |
  | Lemma 8.4 | 1442â€“1453 | 1021 | `b2fbc004252e3f47d2f821febba43b684a49d4fd47125a429c1ed8012d0bc57f` |

  Re-ekstraksi: unduh e-print v2 â†’ cek sha256 tar/tex in atas â†’ potong
  baris sesuai tabel (verifikasi digest). Pemetaan nomor render PDF
  hal. 6: eq. (13) `ratio-form-eff` Â· (14) `ft-def` Â· (15) `bn-def` Â·
  (16) `lambda-def` Â· (17) `sn-def` Â· (18) `kappa-def` Â· (19)
  `N-def-main` Â· (20) `gamma-bound` Â· (21) `res-bound` Â· (22)
  `kappa-bound` Â· (23) `eab-bound` Â· (24) `ec-bound`.

**Region domain (5)** â€” `\label{region}`, tex 168â€“170 (dirujuk pernyataan Thm 1.3):

```latex
\begin{equation}\label{region}
0 < t \leq \frac{1}{2}; \quad 0 \leq y \leq 1; \quad x \geq 200,
\end{equation}
```

**Theorem 1.2 (Upper bound criterion)** â€” `\label{ubc-0}`, tex 145â€“152, PDF hal. 2:

```latex
\begin{theorem}[Upper bound criterion]\label{ubc-0}  Suppose that $t_0, X > 0$ and $0 < y_0 \leq 1$ obey the following hypotheses:
\begin{itemize}
\item[(i)]  (Numerical verification of RH at initial time $0$) There are no zeroes $\zeta(\sigma+iT) = 0$ with $\frac{1+y_0}{2} \leq \sigma \leq 1$ and $0 \leq T \leq \frac{X}{2}$.
\item[(ii)]  (Asymptotic zero-free region at final time $t_0$) There are no zeroes $H_{t_0}(x+iy)=0$ with $x \geq X+\sqrt{1-y_0^2}$ and $y_0 \leq y \leq \sqrt{1-2t_0}$.
\item[(iii)]  (Barrier at intermediate times) There are no zeroes $H_{t}(x+iy)=0$ with $X \leq x \leq X+\sqrt{1-y_0^2}$, $\sqrt{y_0^2+2(t_0-t)} \leq y \leq \sqrt{1-2t}$, and $0 \leq t \leq t_0$.
\end{itemize}
Then $\Lambda \leq t_0 + \frac{1}{2} y_0^2$.
\end{theorem}
```

**Theorem 1.3 (Effective Riemann-Siegel approximation to $H_t(x+iy)$)** â€” `\label{eff}`, tex 223â€“244, PDF hal. 6:

```latex
\begin{theorem}[Effective Riemann-Siegel approximation to $H_t(x+iy)$]\label{eff}  Let $t,x,y$ lie in the region \eqref{region}.  Then we have
\begin{equation}\label{ratio-form-eff}
\frac{H_t(x+iy)}{B_t(x+iy)} = f_t(x+iy) + O_{\leq}\left( e_A + e_B + e_{C,0} \right)
\end{equation}
where
\begin{align}
f_t(x+iy) &\coloneqq \sum_{n=1}^N \frac{b_n^t}{n^{s_*}} + \gamma \sum_{n=1}^N n^y \frac{b_n^t}{n^{\overline{s_*} + \kappa}}\label{ft-def} \\
b_n^t &\coloneqq \exp( \frac{t}{4} \log^2 n ) \label{bn-def}\\
\gamma = \gamma(x+iy) &\coloneqq \frac{M_t\left(\frac{1-y+ix}{2}\right)}{M_t\left(\frac{1+y-ix}{2}\right)} \label{lambda-def} \\
s_* = s_*(x+iy) &\coloneqq \frac{1+y-ix}{2} +\frac{t}{2} \alpha\left(\frac{1+y-ix}{2}\right) \label{sn-def}\\
\kappa = \kappa(x+iy) &\coloneqq \frac{t}{2} \left(\alpha\left(\frac{1-y+ix}{2}\right) - \alpha\left(\frac{1+y+ix}{2}\right)\right) \label{kappa-def}\\
N &\coloneqq \left\lfloor \sqrt{\frac{x}{4\pi} + \frac{t}{16}} \right\rfloor \label{N-def-main} 
\end{align}
and $e_A, e_B, e_{C,0}$ are certain explicitly computable positive quantities\footnote{See \eqref{ea-def}-\eqref{ec-def} for the precise definition of these quantities.} depending on $t$ and $x+iy$.  Furthermore, we have the following bounds:
\begin{align}
|\gamma| &\leq e^{0.02 y} \left( \frac{x}{4\pi} \right)^{-y/2}  \label{gamma-bound} \\
\Re s_* &\geq \frac{1+y}{2} +\frac{t}{4} \log \frac{x}{4\pi} - \frac{t}{2x^2} \left(1-3y+\frac{4y(1+y)}{x^2}\right)_+  \label{res-bound} \\
|\kappa| &\leq  \frac{ty}{2(x-6)} \label{kappa-bound} \\
e_A + e_B &\leq \sum_{n=1}^N (1 + |\gamma| N^{|\kappa|} n^y) \frac{b_n^t}{n^{\Re s_*}} \left( \exp\left( \frac{\frac{t^2}{16} \log^2 \frac{x}{4\pi n^2} + 0.626}{x-6.66} \right)-1 \right) \label{eab-bound} \\
e_{C,0} &\leq \left(\frac{x}{4\pi}\right)^{-\frac{1+y}{4}} \exp\left( - \frac{t}{16} \log^2 \frac{x}{4\pi} + \frac{1.24 \times (3^y+3^{-y})}{N-0.125} + \frac{3 |\log \frac{x}{4\pi} + i \frac{\pi}{2}|+10.44}{x-12} \right) \label{ec-bound}
\end{align}
\end{theorem}
```

**Lemma 8.4** â€” tex 1442â€“1453, PDF hal. 46 (konteks source: "To run this algorithm, we need bounds on $D_t$ and $D_z$. This is achieved by the following lemma [...]"):

```latex
\begin{lemma} In the region \eqref{region}, and away from the jump discontinuities of $N$, we have
\begin{align*}
 \left|\frac{\partial f_t}{\partial z}\right| &\leq  \sum_{n=1}^N \frac{b_n^t}{n^{\Re s_*}} \left(\frac{\log n}{2} + \frac{t \log n}{4(x-6)}\right) \\
&\quad + |\gamma| N^{|\kappa|} \sum_{n=1}^N \frac{b_n^t n^{y} }{n^{\Re s_{*}}}
\left( \frac{t \log n}{4(x-6)} + \left(\log \frac{|1+y+ix|}{4\pi} + \pi + \frac{3}{x}\right) \left(\frac{1}{2} + \frac{t}{4(x-6)}\right)\right)
\end{align*}
and
\begin{align*} \left|\frac{\partial f_t}{\partial t}\right| &\leq \sum_{n=1}^N \frac{b_n^t}{n^{\Re s_*}} \left(\frac{1}{4} \log n \log \frac{x}{4\pi n} + \frac{\pi}{8} \log n + \frac{2 \log n}{x-6}\right) \\
&\quad + |\gamma| N^{|\kappa|} \sum_{n=1}^N \frac{b_n^t n^y}{n^{\Re s_{*}}}
\left(\frac{1}{4} \log n \log \frac{x}{4\pi n} + \frac{\pi}{8} \log n + \frac{2 \log n}{x-6} + \frac{1}{4} \left(\frac{\pi}{2} + \frac{8}{x-6}\right) \left(\log \frac{x}{4\pi} + \frac{8}{x-6}\right)\right).
\end{align*}
\end{lemma}
```

Catatan keterkaitan (bahan L3; **belum ada verdict** â€” verifikasi simbolik menyusul saat audit):

- Hipotesis (i)/(ii)/(iii) Thm 1.2 = slot which in paket diisi oleh klaim P1/T1/B1â€“B2; pemetaan formal dilakukan in L3/L4, bukan in recon ini.
- Thm 1.3 eq. (23) memuat `0.626`, `x-6.66`; eq. (24) memuat `1.24`, `N-0.125`, `10.44`, `x-12`. Obligasi P3 paket membahas bound `x-12, 10.50` **tanpa** eq. (24) â€” perbandingan teks/verifikasi nanti.
- Lemma 8.4 bersifat **pointwise** ("In the region (5), and away from the jump discontinuities of $N$"); paket memakainya lewat `DERIVATIVE_BOX_LEMMA.md` (Â§7.10). Lemma tak berjudul in source; nomor 8.4 dari render PDF.

### 7.12 `REVIEWER_REPORT_TEMPLATE.md` (root repo; selesai) + watch cek-2

- Lokasi: **root repo** on commit ter-pin `a74738de` (bukan in
  `and-reworking/`); fetch 2026-10-17:
  `raw.githubusercontent.com/judegomila/dbn-lambda-01787854-candidate-audit/a74738deb6d5e0f76887cb36901da08b68dca705/REVIEWER_REPORT_TEMPLATE.md`
  â€” 1.518 byte, sha256
  `4ef9d6decd23be0894f1b66e3bfb3e212f58e8fd819f2b18e31c32eaf94bb524`.
  Lisensi dokumen paket: CC BY; kutipan penuh in bawah (atribusi ke paket).
- Isi (verbatim, teks penuh):

```text
# Suggested referee response

## Overall assessment

Choose one:

- validated as stated;
- plausible but incomplete;
- repairable with specified changes;
- invalid for the stated conclusion;
- unable to assess.

## Claim reviewed

\[
\Lambda\le\frac{893927}{5000000}=0.1787854.
\]

State the commit SHA, operating system, Python version, and whether the stored
and container checks passed.

## Layer findings

For each layer, record `valid`, `needs repair`, `invalid`, or `not reviewed`,
with exact file/line references:

1. exact Polymath Theorem 1.2 statement and Platt--Trudgian height input;
2. finite producer, all 3,149,013 stored rows, and direct singleton checks;
3. direct all-height Triangle theorem and continuous window freeze;
4. native normalization and effective-error binding;
5. standalone infinite-tail theorem;
6. repaired 883-prism closed barrier, including the full spatial derivative
   envelope and \(t=0\) endpoint;
7. the three-hypothesis criterion weld and final exact substitution.

## Decisive objections or repairs

For every objection, please include:

- the precise false or unproved statement;
- a counterexample or missing hypothesis where possible;
- whether the issue affects only reproducibility or the mathematical
  conclusion;
- the smallest proposed repair and whether new computation is required.

## Disclosure recommendation

Choose one:

- keep private;
- circulate to additional specialists;
- prepare a corrected preprint;
- suitable for public release after named edits.
```

- Relevansi kita: struktur 7-lapis + pilihan assessment = kerangka report
  L4; lapis 1 ("exact Polymath Theorem 1.2 statement and Platt--Trudgian
  height input") persis fokus Â§7.11; template mensyaratkan commit SHA, OS,
  versi Python, and status cek stored/container per review â€” akan diisi
  saat audit dieksekusi (bukan sekarang; pra-registrasi tetap ditahan).
- Watch cek-2 (2026-10-17, saat potongan 3): HEAD tetap
  `a74738deb6d5e0f76887cb36901da08b68dca705` (21 Agu 2026, PGP-signed);
  rilis tetap hanya `review-01787854-v3` (28 Jul 2026). Tidak ada commit
  or rilis baru; watch berkala lanjut selama run 501.

Ditulis oleh sesi analisis, 2026-10-17. Potongan 2 and sebagian besar
potongan 3 dikerjakan lebih awal on hari which sama (atas persetujuan
pemilik proyek); **potongan 3 dilengkapi 2026-10-17 selama run dim 501**
(transkripsi penuh Thm 1.2/1.3 + Lemma 8.4 â†’ Â§7.11; template reviewer â†’
Â§7.12; watch ulang bersih). Sisa: watch berkala selama run 501.
Pra-registrasi audit no created sebelum C4/501 ditutup.


