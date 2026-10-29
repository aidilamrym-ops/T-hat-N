# REF â€” Audit korpus openai/math oleh proyek lain (eksternal) â€” 2026-10-17

Status: **Referensi eksternal; bukan result MSAF; dikomit 2026-10-17 (batch strategi).**
Sumber: `D:\THE ASYMMETRIC WAGER\openai_math_audit` â€” proyek lain pemilik
proyek, DI LUAR workspace kita. Dibaca read-only 2026-10-17; no ada
file in folder itu which diubah; no ada file dari folder itu which
disalin utuh ke repo ini (hanya kutipan kecil, mis. satu entri antrean).
Berguna sebagai bahan registry P3 + pin status klaim OpenAI (recon Â§7.8).

## 1. Apa which diaudit

Audit katalog-struktur atas korpus `openai/math` (salinan lokal anchor
`informasi mentah/math-main`; 749 directory preprint; snapshot Â± 11 Okt
2026, `history.md` terakhir 7 Okt 2026). 20 fase (0, Aâ€“S, U/Y), 20
artefak JSON deterministik (3-run SHA-256 identik), semua gate + selftest
lulus; exit contract 0/1/2. Batasan eksplisit (kutip): "Nothing in this
report vouches for any analytic claim inside the audited corpus; it
vouches only for catalogue structure and dependency edges." â†’ Korektnes
Lean TIDAK diaudit in sana.

## 2. Verifikasi silang MSAF (2026-10-17)

SHA-256 dihitung ulang dari file nyata; **cocok persis** with pin
artefak mereka:

| Berkas | SHA-256 (verified) |
|---|---|
| `registry.json` | `755A84F6186C22579F10266F9C9B2EBDF9FDAB04C8FEDFE4CC32B54AAF6853B8` |
| `edges.json` | `5944B13257EB3BF702864B25E16DDC3202CE64AAC83E0A3A6BF107A2F937DB91` |
| `scc.json` | `E4EA9889B22E5D95C1E6F91B96EE15B3E68B08E8212DC84665B2C406A824CF03` |
| `formalization_queue.json` | `5B64AA1B79B538E87EB9543839627E6229C11FD6C4F5C90C9B2AF38DE19A8D92` |
| `master_index.json` | `6C94B3824FBD855469332AEFFB1FAC09043A118E335907249A9939AAC8E92BED` |
| `anomaly.json` | `891A47E617222BD7DDA7573CA48F31A513270239A7111614DB8DF4C9B7895637` |

## 3. Fakta kunci (for registry kita)

- **Keluarga 003 "The quasi-Riemann hypothesis"** = 3 anggota:
  `The-Quasi-Riemann-Hypothesis-September-30-2026`,
  `The-Quasi-Riemann-Hypothesis-October-5-2026` (edisi terkini; lineage
  resmi Sep-30 â†’ Oct-5, keduanya linked), and
  `Uniform-exclusion-of-Landau-Siegel-zeros-October-1-2026`.
- **Status formalisasi** (per snapshot): `formalization.yaml` memuat
  entri for edisi **Sep-30** (zeta; judul "The Quasi-Riemann
  Hypothesis: A Zero-Free Half-Plane Re(s)>7/8") and for makalah
  **Dirichlet Landauâ€“Siegel Oct-1**; edisi **Oct-5 no punya entri**
  and berada in antrean unformalized (rank 572/576):

  ```json
  {"dir": "The-Quasi-Riemann-Hypothesis-October-5-2026", "family": "003",
   "family_exposure": 0, "family_formalized_count": 2,
   "family_is_gap": false, "family_member_count": 3, "impact": 0,
   "rank": 572}
  ```

  â†’ "the zeta and Dirichlet statements" (HB Â§1.1) = dua entri itu;
  edisi zeta TERBARU belum terformalisasi.
- Sep-30 = salah satu **top-10 in-degree** korpus (centrality);
  **SCC#100** = siklus Sep-30 â†” Landauâ€“Siegel (via scope-edge
  co-formalization); sitasi: Oct-5 â†’ Sep-30; Sep-30 â†’ makalah cubic
  Gauss sums (Sep-25); Landau â†’ (kosong).
- **Statistik korpus**: 749 dir disk; 719 linked (topline terbit
  "300/719 formalized â‰ˆ 42%"); 30 disk-only = 3 withdrawn + 27 edisi
  superseded + 0 unexplained; 372 keluarga; 173 source formalisasi;
  antrean unformalized 576. 3 withdrawn semuanya rantai
  K3/Hodge-algebraicity, with 2 notice-edge ke dependents; 0 lalu
  lintas sitasi ke/dari withdrawn.
- **Inventaris verifikasi (faktual)**: 30 dir `verification/` = 300
  file (125 `.py`, 73 `.json`, 29 `.md`, 28 `.txt`, 14 `.cpp`);
  **0 file `.lean`/`.v`**; isi no dieksekusi/dinilai oleh audit itu.
- Catatan drift kecil: narasi Fase H (SCC) menyebut salinan Oct-5
  "un-linked"; artefak final (Fase A/registri) menunjukkan lineage edge
  resmi Sep-30 â†’ Oct-5. Rekaman final tersebut which dipakai in sini.

## 4. Sikap MSAF

Semua angka = deskripsi struktur katalog oleh audit eksternal; bukan
verifikasi matematis, bukan result MSAF, and no mengubah verdict mana
pun. Snapshot lokal Â± 11 Okt 2026 â€” sebelum dikutip in registry P3,
re-pin ke live `openai/math` (tetap TO-PIN in recon Â§7.8: perbedaan isi
Sep-30 vs Oct-5; status refereeing kapan pun).

Ditulis 2026-10-17 (sesi analisis). Eksternal read-only; no ada
file folder source which dimodifikasi.


