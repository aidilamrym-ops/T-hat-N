# Daftar Masalah Kerja — Antrian Terikat, Bukan Daftar Keinginan

 turunan dari `20_masalah_matematika_fisika_tersulit.md` (berkas user,
 tak tersentuh). Berkas ini milik program: tiap baris di sini punya
 definisi "selesai versi kita" yang finit dan teruji mesin, atau
 alasan eksplisit mengapa ia TIDAK masuk antrian.

## 0. Aturan main (mengikat, bukan slogan)

1. **Kunci-lalu-pindah.** Trek baru dimulai hanya dari state tersegel
   (tes hijau → docs sinkron → commit + tag + push → CI hijau). Tidak
   ada trek yang ditinggalkan setengah-jadi tanpa status PARTIAL jujur.
2. **"Versi kita" berarti tiga hal, ketiganya wajib:**
   - *terbukti* — dicek kernel (Lean) ATAU komputasi tersertifikasi
     (enclosure rigorous / integer eksak) DITAMBAH kesepakatan dua
     implementasi independen;
   - *teruji* — terkunci test suite yang gagal keras bila salah;
   - *dapat diuji global* — input eksak ter-commit, tanpa float,
     siapa pun menjalankan ulang mendapat integer yang sama.
3. **Tiap masalah dikerjakan sebagai FRAGMEN FINIT + BATAS TERKUNCI.**
   Klaim global tidak pernah keluar dari berkas ini. Yang keluar
   adalah: "sejauh ini tercapai, sampai di sini batasnya, dan ini
   buktinya" — bukan keheningan terbuka.
4. **Tag = hasil terverifikasi saja.** Dokumen rencana seperti berkas
   ini di-commit tanpa tag.

## 1. Prasyarat: segel berjalan selesai dulu

Trek aktif (Turing TERTUTUP v1.30.0; Hodge TERTUTUP v1.35.0 dengan
buntut offline k=10 + HODGE-CH OPEN) disegel penuh sebelum Q1 dibuka:
artefak k=10 terkunci → CH untuk a_11 → bound kuartik (berapa pun
nilainya, termasuk 20). Aturan §0.1 tanpa kecuali.

## 2. Disposisi 20 masalah (semua, tanpa kecuali)

| No | Masalah | Putusan | Alasan / fragmen finit |
|---|---|---|---|
| 1 | Riemann | TREK AKTIF | Hitungan nol terbatas + winding; G2/G3 riset/scope |
| 3 | Hodge | TREK AKTIF | Bound Picard atas per-permukaan-per-lapangan; CH untuk a_11 |
| 5 | Navier-Stokes | TREK AKTIF | Kernel diskrit tercek-Lean; regularitas global TAK tersentuh |
| 6 | Birch–Swinnerton-Dyer | **Q1** | Rank via 2-descent eksak + L(E,1) simbol-modular rasional-eksak + regulator ball; formula BSD dicek per kurva |
| 12 | Twin Prime | **Q2** | Sensus twin + rekor gap s.d. N; dua sieve independen sepakat |
| 13 | abc | **Q3** | Sensus triple s.d. C + rekor kualitas; verifikasi ulang independen |
| 2 | P vs NP | DAFTAR-B (formalisasi saja) | Barier (relativisasi/natural proofs) bilang TAK ADA serangan komputasional; yang mungkin hanya formalisasi fragmen (mis. Cook-Levin) di Lean |
| 16 | Three-Body | TREK AKTIF (T2 FAILED; T2-r2 FAILED; r3 belum dibuka) | T2 gagal di K3 karena singularitas translasi-x eksak (`DF e = 0`). T2-r2 (8x8 terreduksi, periode tetap) **FAILED di K2**: Newton 3 iterasi mencapai 4.22e-25 dan K1 PASS, tetapi slack kuadratik T1b beku (`KAPPA_NL=1e18`) pada `R_B=1e-10` memberi width 320 di step 96; mengecilkan `R_B` saja tidak stabil (1e-13: 3.2e-4; 1e-15: 2.05e6 di step 192). K3/K4/K5 tidak dievaluasi; **tanpa** registry A-2026-0041. Trek berikutnya memerlukan pra-registrasi r3 dengan metode tabung nonlinear lebih ketat sebelum kode |
| 19 | Anderson | DAFTAR-B (syarat) | Kriteria volume-hingga Germinet-Klein; SYARAT MASUK: enclosure probabilitas dulu |
| 20 | Soliton | DAFTAR-B (syarat) | Indeks stabilitas via fungsi Evans terenclosure; SYARAT MASUK: sama dengan Three-Body |
| 17 | Schanuel | DAFTAR-B (formalisasi saja) | Tak ada serangan komputasional; hanya formalisasi instans Lindemann-Weierstrass |
| 4 | Yang-Mills mass gap | TIDAK MASUK | Butuh konstruksi QFT; tak ada yang bisa dihitung tools kami |
| 7 | Renormalisasi QFT | TIDAK MASUK | Fondasi, bukan klaim komputasional |
| 8 | Informasi black hole | TIDAK MASUK | Interpretasional; tak ada klaim terkunci yang mungkin |
| 9 | Konstanta kosmologis | TIDAK MASUK | Puzzle fisika; energi vakum tak terhitung rigorous oleh kami |
| 10 | Pengukuran kuantum | TIDAK MASUK | Interpretasional |
| 11 | Gravitasi kuantum | TIDAK MASUK | Tak ada teori untuk dihitung |
| 14 | Asimetri materi | TIDAK MASUK | Model-dependent, kosmologi |
| 15 | Superkonduktivitas Tc-tinggi | TIDAK MASUK | Numerik Hubbard bukan rigorous-verifiable ala kita |
| 18 | Cosmic censorship | TIDAK MASUK | PDE Einstein tervalidasi di luar jangkauan dekat |

## 3. Antrian kerja (A-list: serangan komputasional langsung)

**Q1 — BSD pilot.** Fragmen: 5 kurva rank 0 konduktor kecil (label
Cremona eksplisit); rank 0 via 2-descent integer-eksak; L(E,1)/Omega
via simbol modular (rasional eksak, tanpa float); identitas
BSD dicek sebagai persamaan rasional. TERKUNCI bila 5/5 cocok dua
implementasi independen. Modul baru: descent + simbol modular.
Reuse: counting kurva, enclosure ball, pola cross-lock.

Measured capability (probe, dihapus setelah mengunci angka di sini):
naive #E(F_p) eksak, gerbang Hasse lolos di semua p, naive==Legendre
di p=101,499; ~84 ms/prima di p~500; semua-p-s.d.-10^3 ~57 dtk,
s.d.-10^4 ~12 jam (naive, Python). Konsekuensi: L(E,1) eksak HARUS
via simbol modular (rasional-eksak), bukan produk Euler; counting
naive hanya untuk sanity s.d. 10^3 (atau jalur Legendre tervektorisasi,
pola yang sama dengan counter kuartik). Peringatan ID-model, tercatat:
model "11a1" dari ingatan berdiskriminan -51931 = 11 x 4721, BUKAN
-11 -- identitas Cremona tetap unverified sampai milestone Q1 sendiri;
probe tidak mengunci fakta apa pun tentang kurva bernama mana pun.

**Q2 — Sensus twin prime.** Fragmen: semua pasangan twin + gap
maksimal s.d. N (N dari anggaran ukur-dulu; mulai 10^9). TERKUNCI
bila dua sieve independen (segmented, implementasi terpisah) sepakat
integer-per-integer. Modul baru: sieve tersertifikasi.

**Q3 — Sensus abc.** Fragmen: semua triple s.d. C + rekor kualitas
q > 1.4 yang terverifikasi ulang independen. Modul baru: pencarian
triple + pemeriksa kualitas.

**Q4 — Ekstensi RH.** Fragmen: T = 100 dengan mesin yang sama
(COMPLETE + winding cross-lock), DENGAN ukur-dinding-dulu. Latar:
kerja literatur G2. Ini background, bukan trek utama.

## 4. Daftar-B (pintu bersyarat, bukan janji)

Masuk A-list hanya bila syaratnya terpenuhi TERLEBIH DULU sebagai
milestone tersegel sendiri: integrator ODE tervalidasi (untuk
Three-Body/Soliton), enclosure probabilitas (untuk Anderson),
target formalisasi Lean yang dirumuskan presisi (untuk P-vs-NP/
Schanuel). Tanpa itu mereka tetap di sini, tertulis, tidak dikerjakan.

## 5. Catatan kejujuran tentang "actual infinity" (dibaca sebelum debat)

Tiga hal yang benar sekaligus:

(a) **Actual infinity tidak bisa "dipatahkan" oleh komputasi finit.**
 Ia adalah pilihan aksioma fondasional (aksioma infinity ZFC; tipe
 tak hingga + Classical.choice di Lean). Komputasi hingga hanya bisa
 diam tentangnya — seperti penggaris yang diam tentang warna.

(b) **Tools kita sendiri mengasumsikannya.** Bukti Lean kami
 bergantung pada propext, Classical.choice, Quot.sound — choice atas
 tipe tak hingga MENGHASILKAN objek infinit aktual (ultrafilter
 nonprinsipal, well-ordering). Memakai Lean+Mathlib untuk mematahkan
 actual infinity adalah kontradiksi performatif; Mathlib itu
 infinitary sampai ke tulang. Audit aksioma 73/73 kami justru
 MENDOKUMENTASIKAN ketergantungan ini, bukan menghilangkannya.

(c) **Yang BISA dilakukan — dan itulah berkas ini:** metodologi
 finitist untuk klaim kami sendiri. Setiap angka yang kami laporkan
 berasal dari komputasi hingga dengan batas eksplisit; "tak hingga"
 tak pernah muncul sebagai objek yang kami hitung — hanya sebagai
 batas yang eksplisit kami tolak lewati (verdict PARTIAL/
 INCONCLUSIVE, pagar scope, non-klaim tertulis). Setiap masalah
 diubah dari "terbuka dan diam" menjadi "terukur sampai sini,
 terkunci, dengan bukti" — itulah §0–§4 di atas.

 Posisi jujur program ini bukan finitisme sebagai teorema, melainkan
 **finitisme sebagai disiplin klaim**.
