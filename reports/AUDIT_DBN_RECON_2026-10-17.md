# AUDIT DBN — Recon pass-3, potongan 1+2+3 (2026-10-17)

Status: **DRAF (potongan 1+2+3), dikomit 2026-10-17 (batch strategi; potongan 3 dilengkapi
selama run dim 501).** Non-binding; bahan mentah untuk
pra-registrasi audit P1 pada `reports/MSAF_PORTFOLIO_2026-10-17.md` §2.
Ditulis selama C4 (+5 seed) berjalan, dilengkapi selama run dim 501;
**mesin tidak disentuh** — murni
pekerjaan dokumen. Semua kutipan verbatim dari dokumen sumber yang
di-fetch 2026-10-17 (daftar di §6; hasil potongan 3 di §7.11–§7.12). Catatan anti-cocoklogi: seluruh angka
di bawah adalah **deskripsi klaim pihak ketiga**, bukan klaim MSAF; tidak
satu pun menjadi hasil kita sampai audit dieksekusi dan dilaporkan.

## 0. Ringkasan potongan 1

- Objek audit: paket Gomila `Λ ≤ 893927/5000000 = 0.1787854`
  (`github.com/judegomila/dbn-lambda-01787854-candidate-audit`).
- Pin repo (diakses 2026-10-17): HEAD =
  `a74738deb6d5e0f76887cb36901da08b68dca705` (21 Agu 2026, commit
  "Add the Aristotle-formalized complete lemma layer under lean/aristotle
  (#29)"); PDF rilis mem-pin program links ke commit `6222740e`.
  Status self-stated (kutip): "computer-assisted unconditional proof, not
  yet peer reviewed". Eksplisit juga: "The result does not prove the
  Riemann hypothesis."
- **Temuan penentu potongan 1: paket sudah punya lapisan Lean 4.** Commit
  HEAD menambahkan 7 proyek Lean ("Aristotle", 2026-08-20), kernel-verified
  (kutip pesan commit): "lake build green on all seven; no sorry, axiom, or
  native_decide; #print axioms on all 223 theorems shows only [propext,
  Classical.choice, Quot.sound]; independent statement-faithfulness review
  passed (six faithful as generated; two statement-level transcription
  defects in tail_lemma corrected by hand and re-verified, documented in
  lean/aristotle/README.md)". Cakupan: TAIL_LEMMA, WINDOW_FREEZE_THEOREM,
  NATIVE_BINDING, ERROR_CONSTANT_WELD, DERIVATIVE_BOX_LEMMA, dan weld
  Theorem 1.2 → Λ ≤ 893927/5000000 — **dengan Polymath 1.2/1.3,
  Platt–Trudgian, dan numerik Arb sebagai hipotesis eksplisit**.
  Konsekuensi untuk audit kita: yang tersisa di luar formalisasi persis
  wilayah kita — (a) weld theorem-source, (b) numerik Arb, (c)
  proof-to-code dari para produsen/verifier. Kandidat cek murah: jalankan
  gate anti-circularity kita (placeholder scan `sorry`/`admit`/`axiom`;
  cek klaim `#print axioms`) di atas `lean/`.
- Sumber asumsi "7/8" pada arXiv:2610.12803 teridentifikasi:
  **OpenAI, "The Quasi-Riemann Hypothesis: A Zero-Free Half-Plane
  Re(s) > 7/8"** — preprint bertanggal 30 Sep 2026, dirilis 6 Okt 2026,
  bagian dari rilis ~722 makalah dari model internal (sumber sekunder;
  kini terpin — §7.8). Unrefereed. → Masuk registry sebagai klaim pihak ketiga;
  **bukan** target audit kita sekarang.

## 1. Fakta terpin dari dokumen paket (angka eksak, seperti tertulis)

- Parameter: `X = 6000000185827`, `t0 = 129/800 = 0.16125`,
  `y0² = 87677/2500000 = 0.0350708`; `t0 + y0²/2 = 893927/5000000`;
  `y0² + 2t0 = 893927/2500000 < 1`; `1 − 2t0 = 271/400`.
- Kriteria: instantiasi Polymath Theorem 1.2 (arXiv:1904.12438v2):
  - (i) verified height: Platt–Trudgian `T_PT = 3000175332800`; kebutuhan
    hanya `X/2 = 3000000092913.5`; surplus eksak `350479773/2 > 0`.
  - (ii) final-time: jendela `x_N = 4π(N² − t0/16)`, `W_N = [x_N, x_{N+1})`;
    `x_690988 < x_* < x_690989` (margin > 5.37×10⁶ dan > 1.19×10⁷);
    coverage `[x_*, x_3840001)`; 3,149,013 baris; empat prime-legs dengan
    `min T_N`: 0.000000791366 | 0.000315112459 | 0.000305788807 |
    0.000309285478; Dini cells `3^5,3^4,3^3,3^2`; worst ratio
    ≤ 0.99999860767275095 < 1; laju koreksi normalizer
    −1.3631121547576400 < 0; budget error:
    `e_A+e_B ≤ 0.000000000002057023688667`,
    `e_C,0 ≤ 0.000000233492848188649183`,
    `E_max ≤ 0.000000233494905212337849`; margin
    ≥ 0.000000557871094787 > 0.
  - Tail: `N_* = 3840000`; `D < 0.999721`;
    `(1−D)/M_max − (e_A+e_B+e_C,0) > 0.00017352`.
  - (iii) barrier: `R = [X, X+1] + i[1809/10000, 1]`; margin tepi bawah
    `y0² − (1809/10000)² = 234599/100000000 > 0`; error total di box
    < 0.000356523011600040 < 0.00125; indeks Riemann–Siegel N = 690988
    di seluruh box; gate per-prisma:
    `M_i > D_z,i/(2(num−1)) + D_t,i(t_{i+1}−t_i) + 0.00125`; 883 prisma
    tertutup; 7,688 komponen koefisien diregenerasi; Taylor tail
    1.954234593244762×10⁻²² < 10⁻²⁰; margin prisma min
    ≥ 0.519849894613872543374989997.
  - Backend Prop 4.10: `verify_prop410_arb.c` (FLINT/Arb, 256 & 512 bit);
    konstanta sebagai rasional eksak (0.02=1/50, 0.626=313/500, 1.24=31/25,
    6.66=333/50, 10.50=21/2, 0.125=1/8); menolak presisi < 256 bit;
    transkrip `logs/prop410_arb_256.log` / `_512.log` (prasyarat P17).
    Jalur `mpmath.iv` lama = corroboration satu-backend (bukan independen).
  - Transkrip assembly (kutip): `RESULT: UNCONDITIONAL PROOF ASSEMBLY
    PASS` + `STATUS: computer-assisted unconditional proof; not yet peer
    reviewed.` — dengan peringatan README: "PASS" hanya berarti predikat
    terkode tersertifikasi; bukan peer review.
- Replay tersedia: container docker (linux/amd64, `--network none`,
  read-only); `verify.sh`; `scripts/run_barrier_replay.sh`,
  `run_tail_arb.sh`, `run_prop410_arb.sh`, `run_full_sweep.sh`
  (regenerasi 3,149,013 tuple vs 15 shard tersegel);
  `scripts/fetch_release_image_oci.py` + `verify_release_image_archive.py`
  (rekonstruksi image offline). Replay penuh tercatat: Linux/GCC/FLINT
  3.0.1 dan macOS/Clang/FLINT 3.6.0, parser ketat 54-cek.
- Higiene berkas: dua file beda isi berbagi basename
  `gomila-proof-exposition.pdf`; hanya salinan `paper/external/` yang
  ter-pin (SHA-256 + daftar koreksi). Eksposisi pihak ketiga (22 hal.)
  punya "known numerical, logical, attribution, and supplement-provenance
  defects" → diperlakukan sebagai draf suplemen, bukan sign-off.
- Lisensi: kode MIT; dokumen CC BY; manuskrip authored + `dan-reworking/`
  + program `independent/` (karya Dan Romik) = all rights reserved.
  **Untuk L2 kita tidak boleh (dan tidak akan) memakai ulang program
  `independent/` maupun verifier mereka.**

## 2. Protokol adversarial paket — blueprint obligasi (ringkas)

Dari `ADVERSARIAL_REVIEW_PROTOCOL.md` (ID milik **mereka**; jangan
tertukar dengan P1–P6 portfolio kita):

| ID | Obligasi (ringkas) | Bukti utama |
|---|---|---|
| P1 | Teorema verified-height: normalisasi & rentang | BIBLIOGRAPHY; PROOF_NOTE §1–3 |
| P2 | Transkripsi Thm 1.2/1.3 & Lemma 8.4 | references/; BARRIER_CERTIFICATE |
| P3 | Corollary 6.6(vi) ⇒ bound `x−12, 10.50` (tanpa eq. (24) 10.44) | ERROR_CONSTANT_WELD; verify_error_constant_weld.py |
| G1 | Parameter eksak, konvensi tanda, substitusi final | CANDIDATE_PARAMETERS; NATIVE_BINDING; verify_assembly_1787854.py |
| F1 | Konvolusi native finite + jembatan effective-error | NATIVE_BINDING; WINDOW_FREEZE_THEOREM |
| F2 | Dini atas + monotonisitas normalizer (semua nol/kink) | provenance/TRIANGLE_Y_DINI_THEOREM.independent.md |
| F3 | Semua baris finite + seam jendela setengah-terbuka | logs/; scripts/run_full_sweep.sh |
| T1 | Tail all-N: endpoint-cap, partisi, monotonisitas | TAIL_LEMMA; TAIL_PROVENANCE |
| T2 | Dua implementasi tail independen | verify_tail_arb.c; Python interval; transkrip tersegel |
| B1 | Batas derivatif box, kuadratur, Taylor, provenance koefisien | DERIVATIVE_BOX_LEMMA; BARRIER_CERTIFICATE; barrier/ |
| B2 | Setiap prisma + seam + homotopi winding bebas nol | barrier/certificates/; run_barrier_replay.sh |
| C1 | Overlap domain + weld tiga hipotesis tanpa pelemahan | PROOF_NOTE §4–7; verify_assembly_1787854.py |

Poin prosedural mereka yang kita adopsi:

- "A successful repository replay is necessary evidence, but it is not by
  itself a mathematical review." → L1 ≠ review.
- Standar independensi: "An implementation counts as independent only if
  it does not reuse the repository's source, parser, interval partition,
  or intermediate decimal tables."
- Clean-room: transkripsi teorema langsung dari paper versi-nya, tanpa
  prosa ringkasan repo.
- Matriks batas: t=0, t=t0, y=y0, y=√(1−2t), endpoint jendela, transisi
  presisi, N=3840000, nol koefisien/kink, floor/ceil bergerak, cabang log,
  endpoint ball, face pertama/terakhir prisma. "Passing interior sample
  points is not evidence for an untested boundary."
- 10 mutation tests wajib (kill rate dilaporkan; survivor =
  release-blocking sampai terbukti irrelevan).
- Perturbasi parameter (t0, y0, cutoff, presisi, mesh) harus bergerak ke
  arah yang diprediksi; pipeline harus menolak konfigurasi gagal.
- Sign-off terpisah 7 kategori: theorem-source / reduksi tulisan tangan /
  proof-to-code / replay lingkungan bersih / komputasi independen /
  hasil mutasi / asumsi tak terselesaikan.
- Lean bukan prasyarat rilis bagi mereka; jangan puas dengan "axiom semua
  analitik lalu restate desimal".

## 3. Protokol audit MSAF — L1–L4 versi konkret (draf pra-registrasi)

- **L1 — replay & provenance (bukan klaim matematis).** Di container
  ter-pin: `verify.sh` + `run_prop410_arb.sh` + `run_tail_arb.sh` +
  `run_barrier_replay.sh` (+ `run_full_sweep.sh` bila anggaran CPU 4-core
  memungkinkan). Output: transkrip + sha artefak; dilabeli "repository
  replay reproduction" — mengikuti kalimat mereka sendiri.
- **L2 — replikasi independen (implementasi sendiri; tanpa source/parser/
  partisi/tabel desimal mereka).** Prioritas:
  1. Budget Prop 4.10 dari rumus (20)–(23)+(vi): bandingkan
     `e_A+e_B`, `e_C,0`, `E_max`, dan margin 5.57871094787×10⁻⁷.
     (Mereka menutup blocker satu-backend via C/FLINT; replikasi kita =
     cross-implementation. Pilihan library/bahasa diputuskan di
     pra-registrasi; wajib berbeda dari jalur C mereka.)
  2. Tail lane: re-derivasi partisi + spot cek koridor dua sisi
     `0.999719 < D < 0.999721` + margin pasca-error
     `> 0.0001735209373337` (§7.2).
  3. Barrier: subset prisma tersempit + seam — winding via enclosure
     sendiri (bukan sampling interior).
  4. Window freeze & sign map: re-derivasi bracket Machin/sqrt rasional
     eksak + aljabar affine `verify_criterion_sign_map.py` (murah; L2 awal
     yang baik).
  Independence note: dua presisi program yang sama ≠ independen (standar
  mereka, kita ikuti).
- **L3 — clean-room theorem-source.** Transkripsi Thm 1.2/1.3 + Lemma 8.4
  dari arXiv:1904.12438v2 + Platt–Trudgian versi refereed; bandingkan
  domain/endpoint/kuantor/substitusi; verdict per hipotesis (i)(ii)(iii) +
  weld. Batasan jujur: satu operator → dua pass terpisah-waktu dicatat
  sebagai mitigasi, bukan dua auditor independen.
- **L4 — verdict.** Tabel per-obligasi (pakai ID blueprint mereka)
  {accepted / rejected / unresolved} + referensi file/baris; daftar
  coverage eksplisit (bagian yang TIDAK diaudit); kata-kata standar:
  "PASS otomatis mereka bukan peer acceptance"; agregat: GAP-FOUND
  (deskripsi) / INDEPENDENTLY-CERTIFIED (bagian X) / UNVERIFIABLE
  (bagian mana, kenapa). Entri registry P3 menyusul.
- Cek murah tambahan (pra-L2): gate anti-circularity kita atas `lean/`
  (scan `sorry`/`admit`/`axiom`; verifikasi klaim `#print axioms`;
  placeholder scan). Ini menjawab langsung pertanyaan P8(3) mereka
  ("is any software check circular").
- Anggaran: full sweep + 883 prisma = jam–hari di 4-core (data
  MAXIMUM_CHECKS: replay produsen finit ≈ 16m45s + comparator 1.89s di
  mesin audit mereka; barrier + tail lane menambah jam); scope wajib vs
  opsional diputuskan **sebelum** eksekusi di pra-registrasi.

## 4. TO-PIN — status per potongan 2 (2026-10-17)

Selesai hari ini (dipercepat atas persetujuan; detail di §7):

- [x] OCI digest + container ter-pin: image teruji
      `ghcr.io/judegomila/dbn-lambda-01787854-review@sha256:6e29bc53…`;
      rilis immutable `review-01787854-v3` (28 Jul 2026; commit
      `2e9976c4…`; seal `89a20156…`; arsip OCI `87a4695e…`) — §7.1.
- [x] `REVIEW_SCOPE.md` + `MAXIMUM_CHECKS.md` + `CANDIDATE_PARAMETERS.md`
      dibaca; replay Level A–E + hierarki bukti terpetakan — §7.2–§7.3.
- [x] `paper/external/README.md`: cros-cek eksposisi pihak ketiga (≈9
      kelas koreksi; anchor `2e9976c4…`) — §7.4.
- [x] Platt–Trudgian (arXiv:2004.09765v1; Bull. LMS) & Polymath15
      (arXiv:1904.12438v2, versi final 4 Agu 2019) dari sumber primer;
      transkripsi penuh §Theorem 1.2 → potongan 3.
- [x] OpenAI "The Quasi-Riemann Hypothesis": terpin ke repo `openai/math`
      (+ entry `lean/formalization.yaml`) — §7.8. Ditambah: audit korpus
      eksternal (proyek lain) dibaca + 6 pin SHA-256 diverifikasi ulang
      kita → `reports/REF_AW_OAI_AUDIT_2026-10-17.md`.
- [x] Hakimoglu-Brown arXiv:2610.12803v1: rantai dependensi + titik masuk
      asumsi (M(0) ≤ 9/16) — §7.6.
- [x] Kislitsyn/GPC frontier: Peczarski 2006 (≤11) → **Gupta 2026
      arXiv:2607.23926 (≤14; census 1.338.193.159.771 poset-14)** — §7.7.
- [x] `independent/README.md`: celah prop43 + kandidat promosi Romik —
      §7.5.

Potongan 3 (mulai 2026-10-17; **selesai 2026-10-17 selama run dim 501**):

- [x] `BARRIER_CERTIFICATE.md` + `DERIVATIVE_BOX_LEMMA.md` dibaca penuh
      (bahan butir barrier L2) — ringkasan §7.9–§7.10.
- [x] Transkripsi penuh Thm 1.2/1.3 + Lemma 8.4 dari arXiv:1904.12438v2
      (bahan L3; PDF versi terkunci kini ter-pin — §7.9; **selesai**:
      PDF byte-identik (`references/README.md`), sumber e-print v2
      ter-pin, digest per-region — §7.11).
- [x] `references/README.md`: SHA-256 empat PDF upstream ter-pin — §7.9.
- [x] `dan-reworking/`: listing per 2026-10-17 (unsealed; `CLAUDE.md`,
      `code/`, `latex/`); `REVIEWER_REPORT_TEMPLATE.md` ternyata di **root
      repo** — dibaca 2026-10-17 (SHA + ringkasan §7.12).
- [x] Repo GPC: struktur terkonfirmasi (`src/`, `tests/`, `scripts/`,
      `paper/`, `data/`) — verifier kecil di `tests/`+`src/` (pin detail
      saat P2 dipra-registrasi).
- [x] Watch 2026-10-17 (dua cek; cek-2 saat potongan 3): HEAD tetap
      `a74738de` (PGP-signed); rilis tetap hanya `review-01787854-v3`;
      revisi OpenAI `paper2.pdf` (5 Okt) masih TO-PIN.

## 5. Peta klaim (bahan awal registry P3)

| Klaim | Sumber | Status | Dependensi | Sikap kita |
|---|---|---|---|---|
| Λ ≥ 0 | Rodgers–Tao, Forum Math Pi (2020) | refereed | — | acuan |
| Λ ≤ 0.2 | Platt–Trudgian, Cor. 2 (kombinasi Polymath15); arXiv:2004.09765v1; Bull. LMS | refereed | — | acuan |
| Λ ≤ 0.1875 | "Mosaic Intelligence", Zenodo 10.5281/zenodo.21175533 (`references/dbn21a-main.pdf`) | non-refereed (rekaman Zenodo) | — | predecessor paket (`vendor/dbn21a`); acuan |
| Λ ≤ 0.1787854 | Gomila (20 Agu 2026), repo + Lean layer | **unrefereed** | Platt–Trudgian; Polymath 1.2/1.3; cert Arb (repo) | **target audit P1** |
| Λ ≤ 0.13963 | Hakimoglu-Brown, arXiv:2610.12803v1 (8 Okt 2026) | unrefereed + **kondisional** | asumsi "7/8" = OpenAI preprint (unrefereed); masuk sekali di M(0) ≤ 9/16 (§7.6) | registry |
| "7/8 zero-free half-plane" | OpenAI, `openai/math` (30 Sep 2026; rilis ~722 makalah) | unrefereed; Lean "dideskripsikan" (§7.8) | — | registry; bukan scope audit |
| Λ (Gordon) piecewise-affine | SSRN + `stefangordon/dbn-upper-bound` | unrefereed | — | TO-PIN status |
| "Collective Contraction…" | arXiv:2609.37164 (Sep 2026) | belum dinilai | — | TO-PIN |
| GPC ⇒ 1/3–2/3 (≤14 elemen) | Gupta, arXiv:2607.23926 (27 Jul 2026; Zenodo 10.5281/zenodo.21865430) | unrefereed | census 1.338.193.159.771 poset-14; Peczarski ≤11 (2006) | kandidat P2 (§7.7) |

## 6. Sumber (diakses 2026-10-17)

- `raw.githubusercontent.com/judegomila/dbn-lambda-01787854-candidate-audit/main/`
  → `README.md`, `PROOF_NOTE.md`, `OPEN_REVIEW_QUESTIONS.md`,
  `ADVERSARIAL_REVIEW_PROTOCOL.md` (semua di-fetch hari ini).
- `api.github.com/repos/judegomila/dbn-lambda-01787854-candidate-audit/commits?per_page=1`
  → HEAD `a74738de…` (21 Agu 2026) + pesan commit Lean (dikutip §0).
- arXiv:2610.12803 (abstrak, 8 Okt 2026); arXiv:1904.12438v2 (dirujuk
  dokumen paket); pencarian web untuk OpenAI "Quasi-Riemann Hypothesis"
  (hasil sekunder: Medium/BigGo/Reddit/awesome-ai-proofs — simpang-siur,
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
  — verifikasi silang + ringkasan:
  `reports/REF_AW_OAI_AUDIT_2026-10-17.md`,
  `reports/REF_AW_MSAF_FAMILY017_2026-10-17.md`.

## 7. Potongan 2 — hasil (dipercepat 2026-10-17, atas persetujuan pemilik)

Murni dokumen (fetch + baca); mesin C4 tidak disentuh. Checklist §4
diperbarui; sisanya = potongan 3. Semua angka di §7 adalah deskripsi
klaim pihak ketiga (anti-cocoklogi: bukan hasil MSAF).

Sorotan audit-relevan:

1. Identitas rilis ter-pin lengkap (commit/tag/seal/OCI digest/arsip
   offline) → L1 bisa dijalankan tanpa tebakan (§7.1).
2. Mereka **sudah** menemukan & memperbaiki 3 defek theorem-level lewat
   audit adversarial internal sebelum seal (§7.2) — kelas kesalahan itu
   jadi target eksplisit L2 kita, bukan asumsi "sudah bersih".
3. Eksposisi pihak ketiga sudah mereka cros-cek (≈9 kelas koreksi,
   §7.4) — pola banding "eksposisi ↔ segel" yang kita tiru di L3.
4. Celah yang mereka akui sendiri: reproduktibilitas `prop43` (§7.5).
5. Frontier P2 bergerak: GPC ≤14 (2026) melampaui ≤11 (Peczarski 2006)
   (§7.7).

### 7.1 Identitas rilis & container (pin L1)

- Rilis immutable `review-01787854-v3` (28 Jul 2026): commit
  `2e9976c4becbf97e31c56fe75fce07cdff5dd4ea` (single parentless commit —
  "single evidence surface intended for an external referee"), tree
  `7f15ecf8…`, tag `585586bb…`; seal `SHA256SUMS` sha256 `89a20156…`;
  release manifest sha256 `e0f134ca…`; PDF referee sha256 `b1151d56…`.
- **OCI digest teruji:** `ghcr.io/judegomila/dbn-lambda-01787854-review@sha256:6e29bc53adc5a4337802da2b5a219720e3da9dcc1b87c546b96b6126d8b9975d`.
- Arsip OCI offline (tanpa registry): `dbn-lambda-01787854-review-v3.oci.tar`
  sha256 `87a4695e…`, 172.810.240 byte.
- Container: Ubuntu 24.04 linux/amd64 (digest child-manifest ter-pin di
  `Dockerfile`); replays `--network none`, read-only.
- Eksekusi terverifikasi di rilis: run `30317899517` (finite replay penuh
  3.149.013 baris diregenerasi) dan run `30322974859` (satu image, dua
  lane).

### 7.2 Parameter & margin tambahan (bahan L2)

Dari `CANDIDATE_PARAMETERS.md` + `MAXIMUM_CHECKS.md` (penguatan §1):

- Head konvolusi `M = 153814`; head error `M_err = 3000`;
  `M_max < 1.608290`; koridor tail **dua sisi**
  `0.999719 < D < 0.999721` (jadi `0.000279 < 1 − D < 0.000281`);
  `(1 − D)/M_max > 0.0001735326089372`; error tail
  `< 0.000000011671604`; margin pasca-error `> 0.0001735209373337`
  (angka presisi ini menggantikan pembulatan `0.00017352` di §1).
- Bracket eksak: `1872719/10^7 < y0 < 23409/125000`;
  `8231038/10^7 < √(1−2t0) ≤ 8231039/10^7`.
- Ladder finit (baris / min T_N @N): P11 38012 / 0.000000791366 @690988;
  P7 90000 / 0.000315112459 @729000; P5 209000 / 0.000305788807 @819000;
  P23 2812001 / 0.000309285478 @1028000.
- Kotak finite leg lanjut: `t ∈ [161250000/10^9, 161250001/10^9]`,
  `y0² = 350708/10^7`; kotak singleton P11 `t = 16125/100000`.
- Runtime lock historis (paket finit): image `dbn21a-flint`
  `sha256:bedf7303…`; Python `mpmath 1.4.1`.
- Dua toolchain barrier: Linux/GCC/FLINT 3.0.1 (transkrip sha256
  `2d010f70…`; margin min berakhir …997) dan macOS/Clang/FLINT 3.6.0
  (`34f8ed82…`; berakhir …999); parser ketat 54 cek. Enclosure winding
  agregat `[−8.95, 8.95]×10⁻¹³`.
- Waktu (mesin audit mereka): replay produsen finit penuh ≈ 16m45s;
  comparator tersegel 1.89s — bahan estimasi biaya L1 di 4-core.
- Cek langsung 256-bit: 30 singleton; UBSan bersih. Dini 180/256 bit
  dengan margin rasio `1 − ratio_ub = 0.00000139232724905`. Native
  binding: 13 gate; 216 uji fase kompleks; slack min > 0.03056. Window
  freeze: Machin rasional π < 10⁻¹⁰⁰; margin jendela 5.37e6 / 1.19e7.
- Higiene: ASan/UBSan/LSan; scrub `PYTHONOPTIMIZE`; scrub override
  `BARRIER_*`; perbaikan leak 4.304 byte / 91 alokasi.
- **Audit adversarial internal mereka (sebelum seal): 3 defek
  theorem-level ditemukan & diperbaiki** — (1) bound sudut ter-freeze
  lemah, (2) integral-vs-sum, (3) proyeksi ball kompleks ke bagian riil
  melanggar callback holomorfik FLINT — plus probe terarah 126/256 bit;
  sumber barrier teraudit sha256 `76e4d4f8…`. Kutipan status mereka:
  "This is an internal adversarial audit, not the requested external
  mathematical review."

### 7.3 Replay Level A–E & hierarki bukti (`REVIEW_SCOPE.md`)

- Level replay: **A** `verify.sh`; **B** replays dalam container ter-pin;
  **C** replay barrier; **D** tail Arb; **E** full sweep (3.149.013 baris
  ≈ 16m45s; comparator 1.89s).
- Hierarki bukti 6 level; kalimat kunci (kutip): "Agreement at levels 4–6
  cannot repair an error at levels 1–3."
- Lane independen: `prop43` & `prop62` = implementasi independen;
  `prop410` = **same-backend** (berbagi `mpmath.iv` + fungsi budget
  identik baris-per-baris) → cross-backend otoritatif =
  `verifiers/verify_prop410_arb.c` (FLINT/Arb; prasyarat P17).
- Ruang kerja tak tersegel `dan-reworking/` + `research/` = BUKAN bukti;
  promosi lewat `independent/README.md`.
- Daftar "what is not claimed" eksplisit (termasuk: belum lulus review
  independen; tidak menetapkan RH) — kita adopsi di kalimat L4.

### 7.4 Cros-cek eksposisi pihak ketiga (`paper/external/README.md`)

- Eksposisi 22 hal.: SHA-256
  `fd98f4e91dea6c02c7705665aaa95d0cb0b0cf46f8a22276e2c693a56a489313`,
  442.088 byte, pdfTeX 1.40.25, tanggal terlihat 27 Jul 2026; baseline
  cros-cek: tag `review-01787854-v3` / commit `2e9976c4…`.
- ≈9 kelas koreksi, di antaranya: arah dependensi terbalik; dua floor di
  eksposisi LEBIH KUAT dari nilai tersegel (0.000315112481 vs
  0.000315112459; 0.000305788816 vs 0.000305788807 — tanda bahaya kita
  juga); isu pembulatan total error; pertidaksamaan tail terbalik
  (`1 − D < 0.000279` vs koridor tersegel `0.000279 < 1 − D < 0.000281`);
  Thm 5.6 memakai bound bulat (`> 0.0001735` vs `> 0.0001735326089372`);
  premis kelayakan endpoint-cap `σ > (t/2)·log c`; suplemen finit
  eksternal (prop43 dkk.) yang hilang; orientasi independence winding;
  bahasa/atribusi.
- Transkrip historis 38 gate (era "candidate") vs verifier kini 40 gate;
  kutip: "No fatal counterexample … found in this cross-check. That is
  not independent peer acceptance."

### 7.5 Lane independen Romik (`independent/README.md`)

- `prop43` (Prop 4.3): ≈3 jam atas sembilan shard; invokasi dipulihkan
  (`INVOCATIONS.md`); **belum ada job CI** yang menjalankannya (butuh
  workflow khusus) → celah reproduktibilitas yang mereka tandai sendiri.
- `prop62` independen; `prop410` same-backend (lihat §7.3).
- Kandidat promosi BELUM dipromosikan: `prop49`, `prop510`, `prop612`,
  `prop65`.
- Origin: ditulis Dan Romik; dipromosikan dari `dan-reworking/code/` pada
  commit `f4d2d03ebc6342b3bce4e0c0b695b82f2e213f1a`; tersegel dan
  dieksekusi lewat `verifiers/verify_independent_crosscheck.py`.

### 7.6 Hakimoglu-Brown arXiv:2610.12803v1 — rantai dependensi

- Versi: draf 7 Okt 2026; v1 arXiv 8 Okt 2026; CC BY 4.0.
- Kondisional: asumsi "7/8" masuk **tepat sekali** di `M(0) ≤ 9/16` via
  `|y| = |2·Re ρ − 1| ≤ 3/4`; hasil `Λ ≤ 0.13963`. Kutip: "The
  seven-eighths assertion … remains an assumption and its source proof
  is not assessed here."
- Jalur perbaikan: 0.1938798366 → 0.1797275414 → 0.16408 → 0.13963
  (bobot panas + produk Euler + subdivisi waktu; langkah akhir
  perbandingan kernel via S' vertikal).
- Memakai boundary §8.4 Polymath (published) + tinggi terverifikasi Platt
  3.06·10^10 untuk Lemma 2; mencatat Platt–Trudgian Cor. 2 = `Λ ≤ 0.2`.
- CATATAN KOREKSI mereka pada eq. (91) Polymath (suku interpolasi
  `D_t|t'−t|` vs `/(2n)`) — status kutipan: "This inspection concerns
  that formula only and is not a verification of the full computation."
  → material TO-PIN potongan 3; belum mengubah apa pun.
- Makalah pendamping di rilis OpenAI yang sama: `Re s > 11/12`
  (q0 = 25/36); tanpa tabel tersertifikasi.

### 7.7 Frontier Kislitsyn/GPC (P2) — TERUPDAT

- Pin lama (pass-1): dossier informal ≤10 (2.769.961 poset) — bukan lagi
  frontier.
- **Peczarski 2006:** GPC (konjektur Peczarski; GPC ⇒ 1/3–2/3)
  diverifikasi komputer untuk semua poset ≤11 elemen.
- **Baru (27–30 Jul 2026):** Anish Gupta, "Balance Constants, Majority
  Cycles, and the Gold Partition Conjecture through Fourteen Elements",
  arXiv:2607.23926 (v2): data ekstremal eksak SEMUA
  **1.338.193.159.771 poset-14 unlabeled**; konstanta balance terkecil
  >1/3 = `37/106`; terkecil pada poset non-ordinal-sum nontrivial =
  `254/725` ("ladder with broken rungs", konfirmasi konjektur Peczarski
  orde 14); orde 12/13 mereproduksi census De Loof–De Baets–De Meyer;
  tidak ada konstanta balance di celah >1/3 yang diduga kosong.
  Aritmetika eksak (tanpa float di jalur keputusan); witness dihitung
  ulang dari string witness oleh program tanpa algoritma bersama.
- Repo `agupta/gold-partition-conjecture`: Zenodo DOI
  10.5281/zenodo.21576029 (manuscript); arsip imutabel Release 2.1
  `10.5281/zenodo.21865430`, Release 2 `10.5281/zenodo.21696940`;
  berisi source GPC eksak + census "production-equivalent", tool
  sharding/agregasi, verifier kecil independen.
- Implikasi P2: frontier = **≤14 (klaim 2026, unrefereed)**; volume:
  ≤12 ≈ 1,1e9; ≤14 ≈ 1,3e12 poset — arah realistis: (i) re-verifikasi
  kecil independen (≤9/10/11) + audit metodologi census ≤14, atau
  (ii) sweep parsial bersertifikat dengan pruning. Diputuskan di
  pra-registrasi P2 (setelah C4/501).

### 7.8 OpenAI "The Quasi-Riemann Hypothesis" — pin registry

- Repo resmi: `github.com/openai/math` (Apache-2.0). Entry katalog
  `lean/formalization.yaml` (skema mathlib-initiative v0.4):
  "The Quasi-Riemann Hypothesis…", `authors: [OpenAI]`, id
  `../preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/paper.pdf`.
  Revisi 5 Okt 2026 = direktori tersendiri (lineage resmi Sep-30 →
  Oct-5; dikonfirmasi audit eksternal). Perbedaan isi kedua edisi belum
  diperiksa (TO-PIN).
- Status katalog: "Partial progress"; HB §1.1: "The repository also
  describes a Lean formalization of the zeta and Dirichlet statements."
  → klaim Lean "dideskripsikan", **tidak** diverifikasi kita.
- Konteks: rilis ~722 makalah dari model internal (6 Okt 2026; sumber
  sekunder). Unrefereed; registry saja.
- **Pembaruan (audit eksternal proyek lain; pin kami verifikasi ulang
  2026-10-17):** keluarga 003 = {Sep-30, Oct-5, Landau–Siegel-Oct-1};
  `formalization.yaml` memuat entri Sep-30 (zeta) + Landau (Dirichlet) —
  cocok dengan frasa HB §1.1 — dan **edisi Oct-5 belum terformalisasi**
  (antrean unformalized rank 572; impact 0). Sep-30 = top-10 in-degree
  korpus; SCC#100 = siklus Sep-30 ↔ Landau. Detail:
  `reports/REF_AW_OAI_AUDIT_2026-10-17.md`.

### 7.9 Potongan 3 — hasil awal: referensi terkunci & barrier certificate

- **Referensi versi-terkunci mereka (`references/README.md`)** — 4 PDF,
  SHA-256 diharapkan: Polymath15 `1904.12438v2` (68 hal.) `60d0d2d3…`;
  Platt–Trudgian `2004.09765v1` (8 hal.) `3362f66a…`; Romik `1902.06330`
  (background) `e81eecf4…`; `dbn21a-main.pdf` (Zenodo 21175533, CC BY 4.0)
  `10648df3…`. L3 kita: unduh dari URL arXiv persis + verifikasi SHA —
  byte-identik dengan versi yang mereka review. **Selesai 2026-10-17
  untuk Polymath15: cocok penuh (68 hal.); transkripsi + digest §7.11.**
- **Barrier certificate (`BARRIER_CERTIFICATE.md`, ringkas)** — klaim:
  `H_t(z) ≠ 0` untuk `z ∈ R = [X, X+1] + i[1809/10000, 1]`, `0 ≤ t ≤ t0`;
  superset persegi dari barrier lengkung Thm 1.2. Lebar:
  `y0² − (1809/10000)² = 234599/100000000 > 0`; `√(1−y0²) < 1`;
  `0 < y0² + 2(t0−t) ≤ y0² + 2t0 < 1`.
  - Error uniform (termasuk `t=0` via argumen limit 4 langkah, bukan
    asumsi): `e_A+e_B < 3.639278679550541e-10`,
    `e_{C,0} < 0.000356522647672172`, total `< 0.000356523011600040 <
    0.00125` (256-bit Arb); transkripsi Python yang sengaja lebih kasar:
    `< 0.000356942`. Keduanya memakai `x−6.66` (A+B) dan `x−12, 10.50`
    (C,0); **tidak ada** yang memakai angka `10.44` di eq. (24).
  - Gate prisma: `M_i > D_z,i/(2(num−1)) + D_t,i(t_{i+1}−t_i) + 0.00125`;
    faktor 1/2 rigor sebagai homotopi bebas-nol (argumen disk), bukan
    estimasi interpolasi pointwise; D_t dievaluasi ulang per prisma yang
    diusulkan (tanpa asumsi monotonisitas).
  - Poligon batas: enclosure endpoint bebas nol; kenaikan argumen di
    `(−π, π)`; winding di `(−1/4, 1/4)`; orientasi argumen terbalik vs
    beberapa eksposisi (tidak mengubah kesimpulan winding = 0).
  - Koefisien tersimpan: 62×62 desimal 20 digit + radius
    `10⁻²⁰·max(1,|c|)`; `StoredSumSinglemat_interval.c` meregenerasi 7.688
    komponen (0 kegagalan kontainmen, rasio allowance terbesar < 0.018);
    `StoredSumTaylorTail_cert.c`: sisa Taylor < 1.954234593244762e-22.
  - Hasil tersegel: 883 prisma tertutup; seam serialisasi byte-identik;
    `t=0` eksak; endpoint akhir `129/800`; winding agregat
    `[−8.95, 8.95]×10⁻¹³`; margin minimum `0.519849894613872543374989997`;
    terminal `RESULT: CLOSED SLAB CERTIFIED`; dua transkrip (Linux/GCC/
    FLINT 3.0.1 kanonik + macOS/Clang/FLINT 3.6.0) lolos 54 cek parser.
  - Prisma terakhir boleh berakhir ≥ t0; teorema memakai prisma ∩ [0,t0].

### 7.10 Derivative box lemma & sisa item potongan 3

- **`DERIVATIVE_BOX_LEMMA.md` (ringkas)** — memperbaiki kelas defect
  nyata: Lemma 8.4 bersifat pointwise; evaluasi di `(X, y_min)` lalu
  dipakai sebagai bound kotak TIDAK konservatif (mis. suku `log(x/(4πn))`
  pada D_t membesar dengan x; di `t=0` tak ada decay panas).
  Perbaikan: `c(x,y) = ¼log q(x) − h₊/(2x²)` naik di x,y
  (`h_y = −3 + 4(1+2y)/x² < 0`, `h_x = −8y(1+y)/x³ ≤ 0`);
  `Re s_* ≥ (1+y)/2 + t·c(X,y_min)` seragam di kotak; gate fail-closed
  `1/(4(X+1)) − 2/X³ > 0` (untuk `c_x > 0`); gate slope A-core
  `η ≤ 0.02 − ½log q(X) + t0·log N/(2(X−6)) + ½log N < 0` menjamin
  maksimum di `y = y_min`; `2 log N < log(X/(4π))`.
  - Sum diskret: **bukan** kuadratur mentah; head 16 suku dievaluasi
    langsung (Arb) + integral ekor yang dibuktikan menurun (gate
    `c0 > ½log N`, `(y_min−1)/2 + 1/log K < 0`, `C − log(N)/4 > 0`);
    `Σ ≤ Σ₁..₁₆ + ∫₁₆..N`.
  - Kontrak kuadratur holomorfik: callback menerima ball kompleks penuh;
    `acb_log_analytic` / `acb_pow_analytic` (flag analitik tepat saat
    `order ≠ 0`); tolak order > 1; sentuhan branch cut → nonfinite →
    fail-closed; counter runtime mewajibkan minimal satu panggilan
    `order=1` per integral. → kelas defect yang sama dengan temuan audit
    internal mereka (proyeksi real) kini punya gate eksplisit.
- **`dan-reworking/`** (per 2026-10-17): berisi `CLAUDE.md` (13,5 KB —
  instruksi workspace Romik), `code/` (prop43, prop49, prop510, prop612,
  prop62, prop65 + `runs/`), `latex/` (eksposisi + manuskrip
  `research-paper/debruijn-newman.tex`); unsealed. Template
  `REVIEWER_REPORT_TEMPLATE.md` ternyata di **root repo** (bukan di
  dan-reworking) — dibaca 2026-10-17; ringkasan + kutipan §7.12.
- **Repo GPC** (`agupta/gold-partition-conjecture`): struktur `src/`,
  `tests/`, `scripts/`, `paper/`, `data/`, `Makefile`, `CITATION.cff` —
  kandidat re-verifikasi kecil di `tests/`+`src/` (pin detail saat P2
  dipra-registrasi).
- **Watch 2026-10-17:** HEAD paket Gomila **tetap** `a74738de` (PGP-signed,
  tree `babfa77e…`, parent `6d3b2230…`); tidak ada commit baru sejak
  21 Agu 2026.

### 7.11 Transkripsi theorem-source L3 — Thm 1.2/1.3 + Lemma 8.4 (selesai)

Provenance (fetch + hash di mesin ini, 2026-10-17; run dim 501 yang
sedang berjalan **tidak disentuh**; PDF/e-print **tidak dikomit** —
kebijakan redistribusi sama seperti paket):

- PDF terbit: `https://arxiv.org/pdf/1904.12438v2`, 68 hal.; SHA-256
  `60d0d2d381227d32f98535a5c43dedb86e333a9006d6819f0bdebdd734085603`
  = **byte-identik** dengan hash acuan `references/README.md` paket
  (unduh-verifikasi persis jalur L3 §7.9). Verifikasi silang render:
  pernyataan Thm 1.2 di hal. 2, Thm 1.3 di hal. 6, Lemma 8.4 di hal. 46.
- Sumber transkripsi: `https://arxiv.org/e-print/1904.12438v2` (tar
  2.229.636 byte, sha256
  `1be3bc38d203ad0142f1c97c267c7deaa06b84c97716c9a1ec1f56456d826863`;
  isi: `debruijn.tex` + 23 PNG). `debruijn.tex` = 170.017 byte, sha256
  `560a28fe31bec92dd793820222e9e73a1fc6958a08344033a946b2ccaba225e5`
  (sumber submisi v2; basis file PDF yang direview).
- Semua blok di bawah = teks **verbatim** dari `debruijn.tex`; angka
  baris mengacu ke file itu. Digest per-region (sha256 atas teks UTF-8,
  LF, termasuk newline akhir, **tanpa** nomor baris; raw vs norm =
  rstrip per baris — identik kecuali thm13):

  | region | baris tex | byte | sha256 |
  |---|---|---|---|
  | (5) domain | 168–170 | 111 | `4353e6c842cf7ff5c811228a53212ea2260a619824e581d4843474a827fbb12e` |
  | Thm 1.2 | 145–152 | 765 | `06290d46cbbbe1670c4e9d4ee9957f0f8dc06367a9907644a654d048b7e331ec` |
  | Thm 1.3 | 223–244 | 2019 | raw `2bdd6d87d0a0c1d90a114b934eb905a46a4c40e99cb0fcc27993414ea0e1e08d` / norm `cebe9801b3c2b57414fa65d55506df0987dd01f94851bada291e51d6a85d68b2` (beda hanya spasi akhir baris 234) |
  | Lemma 8.4 | 1442–1453 | 1021 | `b2fbc004252e3f47d2f821febba43b684a49d4fd47125a429c1ed8012d0bc57f` |

  Re-ekstraksi: unduh e-print v2 → cek sha256 tar/tex di atas → potong
  baris sesuai tabel (verifikasi digest). Pemetaan nomor render PDF
  hal. 6: eq. (13) `ratio-form-eff` · (14) `ft-def` · (15) `bn-def` ·
  (16) `lambda-def` · (17) `sn-def` · (18) `kappa-def` · (19)
  `N-def-main` · (20) `gamma-bound` · (21) `res-bound` · (22)
  `kappa-bound` · (23) `eab-bound` · (24) `ec-bound`.

**Region domain (5)** — `\label{region}`, tex 168–170 (dirujuk pernyataan Thm 1.3):

```latex
\begin{equation}\label{region}
0 < t \leq \frac{1}{2}; \quad 0 \leq y \leq 1; \quad x \geq 200,
\end{equation}
```

**Theorem 1.2 (Upper bound criterion)** — `\label{ubc-0}`, tex 145–152, PDF hal. 2:

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

**Theorem 1.3 (Effective Riemann-Siegel approximation to $H_t(x+iy)$)** — `\label{eff}`, tex 223–244, PDF hal. 6:

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

**Lemma 8.4** — tex 1442–1453, PDF hal. 46 (konteks sumber: "To run this algorithm, we need bounds on $D_t$ and $D_z$. This is achieved by the following lemma [...]"):

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

Catatan keterkaitan (bahan L3; **belum ada verdict** — verifikasi simbolik menyusul saat audit):

- Hipotesis (i)/(ii)/(iii) Thm 1.2 = slot yang di paket diisi oleh klaim P1/T1/B1–B2; pemetaan formal dilakukan di L3/L4, bukan di recon ini.
- Thm 1.3 eq. (23) memuat `0.626`, `x-6.66`; eq. (24) memuat `1.24`, `N-0.125`, `10.44`, `x-12`. Obligasi P3 paket membahas bound `x-12, 10.50` **tanpa** eq. (24) — perbandingan teks/verifikasi nanti.
- Lemma 8.4 bersifat **pointwise** ("In the region (5), and away from the jump discontinuities of $N$"); paket memakainya lewat `DERIVATIVE_BOX_LEMMA.md` (§7.10). Lemma tak berjudul di sumber; nomor 8.4 dari render PDF.

### 7.12 `REVIEWER_REPORT_TEMPLATE.md` (root repo; selesai) + watch cek-2

- Lokasi: **root repo** pada commit ter-pin `a74738de` (bukan di
  `dan-reworking/`); fetch 2026-10-17:
  `raw.githubusercontent.com/judegomila/dbn-lambda-01787854-candidate-audit/a74738deb6d5e0f76887cb36901da08b68dca705/REVIEWER_REPORT_TEMPLATE.md`
  — 1.518 byte, sha256
  `4ef9d6decd23be0894f1b66e3bfb3e212f58e8fd819f2b18e31c32eaf94bb524`.
  Lisensi dokumen paket: CC BY; kutipan penuh di bawah (atribusi ke paket).
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

- Relevansi kita: struktur 7-lapis + pilihan assessment = kerangka laporan
  L4; lapis 1 ("exact Polymath Theorem 1.2 statement and Platt--Trudgian
  height input") persis fokus §7.11; template mensyaratkan commit SHA, OS,
  versi Python, dan status cek stored/container per review — akan diisi
  saat audit dieksekusi (bukan sekarang; pra-registrasi tetap ditahan).
- Watch cek-2 (2026-10-17, saat potongan 3): HEAD tetap
  `a74738deb6d5e0f76887cb36901da08b68dca705` (21 Agu 2026, PGP-signed);
  rilis tetap hanya `review-01787854-v3` (28 Jul 2026). Tidak ada commit
  atau rilis baru; watch berkala lanjut selama run 501.

Ditulis oleh sesi analisis, 2026-10-17. Potongan 2 dan sebagian besar
potongan 3 dikerjakan lebih awal pada hari yang sama (atas persetujuan
pemilik proyek); **potongan 3 dilengkapi 2026-10-17 selama run dim 501**
(transkripsi penuh Thm 1.2/1.3 + Lemma 8.4 → §7.11; template reviewer →
§7.12; watch ulang bersih). Sisa: watch berkala selama run 501.
Pra-registrasi audit tidak dibuat sebelum C4/501 ditutup.
