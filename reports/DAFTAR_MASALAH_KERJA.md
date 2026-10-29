# Daftar Masalah Kerja â€” Antrian Terikat, Bukan Daftar Keinginan

 turunan dari `20_masalah_matematika_fisika_tersulit.md` (file user,
 tak tersentuh). Berkas ini milik program: tiap baris in sini punya
 definisi "selesai versi kita" which finit and teruji mesin, or
 alasan eksplisit mengapa ia TIDAK masuk antrian.

## 0. Aturan main (mengikat, bukan slogan)

1. **Kunci-lalu-pindah.** Trek baru dimulai hanya dari state tersegel
   (tes hijau â†’ docs sinkron â†’ commit + tag + push â†’ CI hijau). Tidak
   ada trek which ditinggalkan setengah-jadi tanpa status PARTIAL jujur.
2. **"Versi kita" berarti tiga hal, ketiganya wajib:**
   - *terbukti* â€” dicek kernel (Lean) ATAU komputasi tersertifikasi
     (enclosure rigorous / integer eksak) DITAMBAH kesepakatan dua
     implementasi independen;
   - *teruji* â€” terkunci test suite which gagal keras bila salah;
   - *dapat diuji global* â€” input eksak ter-commit, tanpa float,
     siapa pun menjalankan ulang mendapat integer which sama.
3. **Tiap masalah dikerjakan sebagai FRAGMEN FINIT + BATAS TERKUNCI.**
   Klaim global no pernah keluar dari file ini. Yang keluar
   adalah: "sejauh ini tercapai, sampai in sini batasnya, and ini
   buktinya" â€” bukan keheningan terbuka.
4. **Tag = result terverifikasi saja.** Dokumen rencana seperti file
   ini in-commit tanpa tag.

## 1. Prasyarat: segel berjalan selesai dulu

Trek aktif (Turing TERTUTUP v1.30.0; Hodge TERTUTUP v1.35.0 with
buntut offline k=10 + HODGE-CH OPEN) disegel penuh sebelum Q1 dibuka:
artefak k=10 terkunci â†’ CH for a_11 â†’ bound kuartik (berapa pun
nilainya, termasuk 20). Aturan Â§0.1 tanpa kecuali.

## 2. Disposisi 20 masalah (semua, tanpa kecuali)

| No | Masalah | Putusan | Alasan / fragmen finit |
|---|---|---|---|
| 1 | Riemann | TREK AKTIF | Hitungan nol terbatas + winding; G2/G3 riset/scope |
| 3 | Hodge | TREK AKTIF | Bound Picard atas per-permukaan-per-lapangan; CH for a_11 |
| 5 | Navier-Stokes | TREK AKTIF | Kernel diskrit tercek-Lean; regularitas global TAK tersentuh |
| 6 | Birchâ€“Swinnerton-Dyer | **Q1** | Rank via 2-descent eksak + L(E,1) simbol-modular rasional-eksak + regulator ball; formula BSD dicek per kurva |
| 12 | Twin Prime | **Q2** | Sensus twin + rekor gap s.d. N; dua sieve independen sepakat |
| 13 | abc | **Q3** | Sensus triple s.d. C + rekor kualitas; verifikasi ulang independen |
| 2 | P vs NP | DAFTAR-B (formalisasi saja) | Barier (relativisasi/natural proofs) bilang TAK ADA serangan komputasional; which mungkin hanya formalisasi fragmen (mis. Cook-Levin) in Lean |
| 16 | Three-Body | TREK AKTIF (T2 FAILED; T2-r2 FAILED; r3 belum dibuka) | T2 gagal in K3 karena singularitas translasi-x eksak (`DF e = 0`). T2-r2 (8x8 terreduksi, periode tetap) **FAILED in K2**: Newton 3 iterasi mencapai 4.22e-25 and K1 PASS, tetapi slack kuadratik T1b beku (`KAPPA_NL=1e18`) on `R_B=1e-10` memberi width 320 in step 96; mengecilkan `R_B` saja no stabil (1e-13: 3.2e-4; 1e-15: 2.05e6 in step 192). K3/K4/K5 no dievaluasi; **tanpa** registry A-2026-0041. Trek berikutnya memerlukan pra-registrasi r3 with metode tabung nonlinear lebih ketat sebelum kode |
| 19 | Anderson | DAFTAR-B (syarat) | Kriteria volume-hingga Germinet-Klein; SYARAT MASUK: enclosure probabilitas dulu |
| 20 | Soliton | DAFTAR-B (syarat) | Indeks stabilitas via fungsi Evans terenclosure; SYARAT MASUK: sama with Three-Body |
| 17 | Schanuel | DAFTAR-B (formalisasi saja) | Tak ada serangan komputasional; hanya formalisasi instans Lindemann-Weierstrass |
| 4 | Yang-Mills mass gap | TIDAK MASUK | Butuh konstruksi QFT; tak ada which bisa dihitung tools kami |
| 7 | Renormalisasi QFT | TIDAK MASUK | Fondasi, bukan klaim komputasional |
| 8 | Informasi black hole | TIDAK MASUK | Interpretasional; tak ada klaim terkunci which mungkin |
| 9 | Konstanta kosmologis | TIDAK MASUK | Puzzle fisika; energi vakum tak terhitung rigorous oleh kami |
| 10 | Pengukuran kuantum | TIDAK MASUK | Interpretasional |
| 11 | Gravitasi kuantum | TIDAK MASUK | Tak ada teori for dihitung |
| 14 | Asimetri materi | TIDAK MASUK | Model-dependent, kosmologi |
| 15 | Superkonduktivitas Tc-tinggi | TIDAK MASUK | Numerik Hubbard bukan rigorous-verifiable ala kita |
| 18 | Cosmic censorship | TIDAK MASUK | PDE Einstein tervalidasi in luar jangkauan dekat |

## 3. Antrian kerja (A-list: serangan komputasional langsung)

**Q1 â€” BSD pilot.** Fragmen: 5 kurva rank 0 konduktor kecil (label
Cremona eksplisit); rank 0 via 2-descent integer-eksak; L(E,1)/Omega
via simbol modular (rasional eksak, tanpa float); identitas
BSD dicek sebagai persamaan rasional. TERKUNCI bila 5/5 cocok dua
implementasi independen. Modul baru: descent + simbol modular.
Reuse: counting kurva, enclosure ball, pola cross-lock.

Measured capability (probe, dihapus setelah mengunci angka in sini):
naive #E(F_p) eksak, gerbang Hasse lolos in semua p, naive==Legendre
in p=101,499; ~84 ms/prima in p~500; semua-p-s.d.-10^3 ~57 dtk,
s.d.-10^4 ~12 jam (naive, Python). Konsekuensi: L(E,1) eksak HARUS
via simbol modular (rasional-eksak), bukan produk Euler; counting
naive hanya for sanity s.d. 10^3 (or jalur Legendre tervektorisasi,
pola which sama with counter kuartik). Peringatan ID-model, tercatat:
model "11a1" dari ingatan berdiskriminan -51931 = 11 x 4721, BUKAN
-11 -- identitas Cremona tetap unverified sampai milestone Q1 sendiri;
probe no mengunci fakta apa pun tentang kurva bernama mana pun.

**Q2 â€” Sensus twin prime.** Fragmen: semua pasangan twin + gap
maksimal s.d. N (N dari anggaran ukur-dulu; mulai 10^9). TERKUNCI
bila dua sieve independen (segmented, implementasi terpisah) sepakat
integer-per-integer. Modul baru: sieve tersertifikasi.

**Q3 â€” Sensus abc.** Fragmen: semua triple s.d. C + rekor kualitas
q > 1.4 which terverifikasi ulang independen. Modul baru: pencarian
triple + pemeriksa kualitas.

**Status Q3:** CERTIFIED (A-2026-0052) â€” sensus hingga C=10^7, 17 triple
with q>1.4, max_gap=40640, dua sieve independen sepakat, receipt
`reports/abc_census_v3_10000000.json` (verdict ALL PASS). Gate C=10^5:
6/6825; validasi C=10^6: 11/6825.

**Q4 â€” Ekstensi RH.** Fragmen: T = 100 with mesin which sama
(COMPLETE + winding cross-lock), DENGAN ukur-dinding-dulu. Latar:
kerja literatur G2. Ini background, bukan trek utama.

## 4. Daftar-B (pintu bersyarat, bukan janji)

Masuk A-list hanya bila syaratnya terpenuhi TERLEBIH DULU sebagai
milestone tersegel sendiri: integrator ODE tervalidasi (for
Three-Body/Soliton), enclosure probabilitas (for Anderson),
target formalisasi Lean which dirumuskan presisi (for P-vs-NP/
Schanuel). Tanpa itu mereka tetap in sini, tertulis, no dikerjakan.

## 5. Catatan kejujuran tentang "actual infinity" (dibaca sebelum debat)

Tiga hal which benar sekaligus:

(a) **Actual infinity no bisa "dipatahkan" oleh komputasi finit.**
 Ia adalah pilihan aksioma fondasional (aksioma infinity ZFC; tipe
 tak hingga + Classical.choice in Lean). Komputasi hingga hanya bisa
 diam tentangnya â€” seperti penggaris which diam tentang warna.

(b) **Tools kita sendiri mengasumsikannya.** Bukti Lean kami
 bergantung on propext, Classical.choice, Quot.sound â€” choice atas
 tipe tak hingga MENGHASILKAN objek infinit aktual (ultrafilter
 nonprinsipal, well-ordering). Memakai Lean+Mathlib for mematahkan
 actual infinity adalah kontradiksi performatif; Mathlib itu
 infinitary sampai ke tulang. Audit aksioma 73/73 kami justru
 MENDOKUMENTASIKAN ketergantungan ini, bukan menghilangkannya.

(c) **Yang BISA dilakukan â€” and itulah file ini:** metodologi
 finitist for klaim kami sendiri. Setiap angka which kami laporkan
 berasal dari komputasi hingga with limit eksplisit; "tak hingga"
 tak pernah muncul sebagai objek which kami hitung â€” hanya sebagai
 limit which eksplisit kami tolak lewati (verdict PARTIAL/
 INCONCLUSIVE, pagar scope, non-klaim tertulis). Setiap masalah
 diubah dari "terbuka and diam" menjadi "terukur sampai sini,
 terkunci, with bukti" â€” itulah Â§0â€“Â§4 in atas.

 Posisi jujur program ini bukan finitisme sebagai teorema, melainkan
 **finitisme sebagai disiplin klaim**.


