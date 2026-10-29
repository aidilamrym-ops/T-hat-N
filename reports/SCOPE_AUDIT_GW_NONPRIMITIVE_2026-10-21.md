# Audit scope item 1 - Guinand-Weil non-primitif (2026-10-21)

**Status:** `AUDIT READ-ONLY`. Tidak ada eksperimen, pra-registrasi,
implementasi, or klaim baru. Satu file audit ini created; no ada
file terlacak which diubah.

**Putusan singkat:** blueprint item 1 **belum siap diimplementasikan apa
adanya** (`NOT IMPLEMENTATION-READY`). Yang bisa dikerjakan sekarang adalah
paket aritmetika karakter/struktural-zero which kecil, or eksperimen
matriks *ad hoc* with label which jujur. Blok Guinand-Weil which benar
for karakter membutuhkan derivasi ulang blok archimedean/pole, bukan
hanya mengganti `Wp`.

---

## 1. Yang diminta blueprint

Sumber: `Five Core Experimental Problem Blueprint.md`, baris 7-20.

- Matriks `tau = W02 - WR - Wp`, dimensi `2N+1`.
- `W02`, `WR` disebut blok archimedean; `Wp` adalah jumlah prime power
  `q_k = p^a <= c` with bobot `log(p) q_k^{-1/2}` dikali nilai karakter
  `chi_{q,n}(q_k)`.
- "Entries must be structurally zero when `gcd(q_k, q) > 1`."
- Route S: `certified_inertia` (interval LDL^T), target `n_+ = dim`,
  `n_- = 0`.
- Route A2: interval Newton for "pull non-trivial zeros" and
  zero-containment.
- Bahasa klaim: "critical line lock (`sigma = 0.5`)".

## 2. Infrastruktur which benar-benar ada

| Berkas | Isi | Batas |
|---|---|---|
| `msaf/dirichlet.py` | karakter real **primitif** + Hardy `Z(t)` bracketing | menolak imprimitive (`ValueError`, baris 162-171); no ada blok GW; no ada Taylor/Newton for `L` |
| `msaf/AUDIT.md` L35 | menyatakan FLINT no mengekspos power-series `L`; Taylor Newton `zeta_inversion` no punya analog | Route A2 no didukung |
| `C:/Users/usER/oracle-toe/GUINAND_WEIL/source_arb_ldlt_certify.py` | `build_arb_tau(c, N, prec)` for `tau = W02 - WR - Wp` | **no punya parameter karakter**; `Wp` memakai bobot tanpa `chi` (baris 149-180) |
| `msaf/gw_route_s_ladder.py` | wrapper Route S; import builder eksternal, panggil `certified_inertia` | hanya meneruskan `(c, N, prec)`; no ada jalur karakter |
| `msaf/guinand.py` | keluarga mainan `W[i][j] = cos(2*pi*i*j/n) - delta` | bukan blok Guinand-Weil which dimaksud |
| `gw_qinf.py` (repo source) | mendefinisikan `pole_B` and `Q_full` | `W02` adalah blok **pole**, bukan blok archimedean |

Tidak ada "existing MSAF primitive Dirichlet kernel (`chi_{4,3}`)" berupa
blok Guinand-Weil in repo ini. `git log` for `msaf/dirichlet.py` hanya
menunjukkan kampanye Hardy-Z; no ada builder GW berkarakter. Premis
blueprint karena itu no sesuai with codebase.

## 3. Temuan matematis

### F1. `W02` adalah blok pole, bukan blok archimedean

Formula `W02` in `source_arb_ldlt_certify.py:165-167` identik with
`pole_B` in `gw_qinf.py:138-140`:

```text
32 L sinh(L/4)^2 (L^2 - 16 pi^2 m n)
------------------------------------
(L^2 + 16 pi^2 m^2)(L^2 + 16 pi^2 n^2)
```

`gw_opt_a_diff.py:17-21` juga memetakan `source : tau = W02 - WR - Wp`
terhadap `ours : Q = pole_A + ...`. Jadi `W02` adalah kontribusi pole
(zeta), bukan blok archimedean umum.

Konsekuensinya:

- Untuk karakter non-principal, `L(s, chi)` no punya pole in `s=1`;
  `W02` seharusnya no ada (or diganti blok pole which sesuai).
- Untuk karakter principal modulo `q`, pole tetap ada tetapi residunya
  berubah (bergantung on `phi(q)/q`), sehingga `W02` juga no bisa
  dibiarkan apa adanya.

### F2. `WR` juga character-blind

`WR` dibangun dari digamma/trigamma on `1/4 + i*pi*n/L` with fungsi
gamma zeta. Faktor gamma Dirichlet bergantung on paritas karakter:
`Gamma((s+a)/2)` with `a = 0` (even) or `a = 1` (odd), and on
konduktor. Mengganti hanya `Wp` no menghasilkan blok Weil for
`L(s, chi)`. Ini bukan perturbasi kecil: blok archimedean and pole adalah
section dari definisi explicit formula.

### F3. "Non-primitif" punya dua makna which no ekuivalen

1. **L-function standar:** `L(s, chi_{q,n}) = L(s, chi_{q*,n*})` for
   karakter primitif induknya. Zero-nya sama; no ada zero baru.
2. **Deret Dirichlet with koefisien karakter non-primitif:**
   `F(s) = sum chi(n) n^{-s} = L(s, chi*) * prod_{p|q, p no | q*}
   (1 - chi*(p) p^{-s})`. Ini punya zero tambahan dari faktor Euler
   hingga: `p^{-s} = chi*(p)` memberi `Re(s) = 0` for `chi*(p) = +-1`.
   Jadi zero tambahan berada in sumbu imajiner, bukan in `sigma = 1/2`;
   "critical line lock" for `F` no berlaku.

FLINT `dirichlet_char.l` menghitung objek (2), bukan (1). Cek numerik
on `s=2`:

| karakter | nilai FLINT `L(2)` | induk primitif | nilai induk | rasio |
|---|---:|---|---:|---:|
| `chi_{12,7}` | `1.0177395490857989...` | `chi_{4,3}` | `0.9159655941772190...` | `1 + 1/9` |
| `chi_{12,5}` | `0.9766280161206078...` | `chi_{3,2}` | `0.7813024128964862...` | `1 + 1/4` |
| `chi_{15,11}` | `0.8125545094123457...` | `chi_{3,2}` | `0.7813024128964862...` | `1 + 1/25` |

Jadi `chi_{12,7}` bukan "L-function primitive which sama" dalam
perhitungan FLINT; ia adalah deret Dirichlet with faktor Euler
tambahan. Blueprint no memilih objek (1) or (2). Tanpa pilihan ini,
"zero-vanishing" and "critical line lock" no terdefinisi.

### F4. Uji struktural-zero perlu diperjelas

Untuk karakter modulo `q`, `chi(n) = 0` iff `gcd(n, q) > 1`. Yang baru
on non-primitif adalah prime `p | q` with `p no | q*`; in situ
`chi(p) = 0` tetapi `chi*(p) != 0`. Jadi:

- uji `gcd(q_k, q) > 1` benar for nilai karakter;
- tetapi kalimat blueprint "sharing common prime factors with the
  conductor" keliru jika "conductor" berarti `q*`; which menentukan zero
  adalah modulus `q`, bukan konduktor `q*`;
- "entries must be structurally zero" juga ambigu: which lenyap adalah
  suku `Wp` for `q_k` itu, bukan seluruh entri matriks.

### F5. Route S hanya well-defined for karakter real

`Wp` adalah matriks simetris real jika `chi(q_k)` real. Untuk karakter
kompleks, `Wp` menjadi matriks simetris kompleks, **bukan Hermitian**;
inertia (jumlah pivot positif/negatif) no terdefinisi for matriks
non-Hermitian. `acb_mat` no memperbaiki ini. Route S harus dibatasi ke
`order(chi) <= 2` (real), or blueprint harus mendefinisikan objek
Hermitian lain (misalnya `Re(Wp)`), which merupakan definisi baru, bukan
explicit formula.

### F6. Route A2 no didukung API saat ini

`msaf/dirichlet.py:3-8` menyatakan FLINT no mengekspos power-series
`L`, sehingga Newton Taylor no punya analog. `hardy_z` for karakter
imprimitive bahkan abort:

```text
FLINT exception: hardy theta: need primitive character
```

Tidak ada zero localisation for karakter non-primitif in codebase.
Route A2 sebagaimana ditulis adalah pekerjaan riset baru, bukan ekstensi
infrastruktur which ada.

### F7. "Critical line lock" no bisa disimpulkan dari inertia finite

Inertia `n_+ = dim, n_- = 0` hanya menyatakan satu matriks finite positif
definit. Itu bukan bukti lokasi zero, bukan RH/GRH, and bukan
`sigma = 1/2`. Bahasa blueprint harus diganti menjadi klaim matriks
finite murni; jika no, report akan melanggar aturan scope proyek.

## 4. Probe read-only (bukan pra-registrasi, bukan klaim)

Untuk mengukur apakah hambatannya komputasi or definisi, dilakukan probe
read-only in luar repo:

- `c = 100`, `N = 20`, `dim = 41`, `prec = 600`;
- `W02`, `WR` dari builder zeta eksternal (no diubah);
- hanya `Wp` which dikali nilai karakter real eksak;
- `certified_inertia` which sama.

Hasil:

| matriks | inertia `(n_+, n_-)` | note |
|---|---:|---|
| tanpa karakter (baseline) | `(41, 0)` | jalur probe konsisten with result which dikenal |
| `chi_{12,7}` (cond 4, prime baru 3) | `(20, 21)` | no positif definit |
| `chi_{12,5}` (cond 3, prime baru 2) | `(21, 20)` | no positif definit |
| `chi_{15,4}` (cond 5, prime baru 3) | `(20, 21)` | no positif definit |
| `chi_{15,11}` (cond 3, prime baru 5) | `(19, 22)` | no positif definit |
| `chi_{4,3}` primitif | `(17, 24)` | bahkan primitif no positif with blok zeta |

Waktu: build ~0.4 s, LDL^T ~0.02 s on ukuran ini. **Biaya komputasi
bukan penghalang.** Yang menjadi penghalang adalah blok `W02`/`WR` which
masih milik zeta: begitu `Wp` diberi karakter, matriks menjadi indefinite.
Artinya, jika eksperimen tetap dijalankan with `W02`/`WR` lama, result
positif/negatifnya mengukur ketidakcocokan blok, bukan properti
`L(s, chi)`.

## 5. Putusan feasibility

| Jalur | Status | Alasan |
|---|---|---|
| Blok GW benar for `L(s, chi)` | `NOT READY` | perlu derivasi ulang `W02`/`WR` (gamma factor, pole, konduktor) |
| Route S for karakter real non-primitif with blok zeta | `FEASIBLE AS AD HOC` | aritmetika jalan, tetapi bukan explicit formula; result harus berlabel ad hoc |
| Route S for karakter kompleks | `NOT WELL-DEFINED` | `Wp` simetris kompleks, bukan Hermitian |
| Route A2 (Newton zero) | `NOT FEASIBLE` | no ada power-series `L`; `hardy_z` imprimitive abort |
| Uji struktural-zero murni | `FEASIBLE NOW` | exact integer/character table, kecil, rigorous |
| Klaim "critical line lock" | `NOT CLAIMABLE` | in luar scope finite matrix |

## 6. Opsi which bisa dipilih pemilik

**A. P1 - Sertifikat aritmetika karakter (rekomendasi pertama).**
Instance real non-primitif kecil, misalnya `chi_{12,7}` and `chi_{12,5}`.
Isi: konduktor/paritas/order, tabel nilai eksak, uji
`chi(q_k) = 0 iff gcd(q_k, q) > 1`, perbandingan with induk primitif,
receipt deterministik. Tanpa matriks, tanpa klaim zero. Ini paket kecil
which bisa selesai cepat and menjadi prasyarat jujur.

**B. P2 - Perturbasi blok zeta ad hoc (jika ingin matriks sekarang).**
Definisikan eksplisit `tau_pert = W02_zeta - WR_zeta - Wp_chi`; batasi
ke karakter real; jalankan interval LDL^T; bandingkan baseline, primitif,
and non-primitif. Label wajib: `AD HOC PERTURBATION`, bukan blok Weil
`L(s, chi)`, `global_claim_supported=false`, tanpa klaim critical line.
Probe in atas menunjukkan hasilnya kemungkinan indefinite; itu result
negatif which sah, bukan PASS.

**C. P3 - Blok GW berkarakter which benar (riset).**
Turunkan ulang blok archimedean/pole for karakter (gamma factor
`Gamma((s+a)/2)`, konduktor `q*`, pole principal), lalu bandingkan with
lift non-primitif. Ini pekerjaan derivasi + validasi baru; perlu
pra-registrasi terpisah and waktu lebih panjang.

**D. Hold.**
Catat item 1 sebagai `PLANNING`/`INCONCLUSIVE` and jangan paksakan
implementasi. Ini pilihan which benar jika tujuannya adalah klaim
matematis which bermakna, bukan sekadar menjalankan matriks.

## 7. Permintaan keputusan

Belum ada kode which ditulis and belum ada pra-registrasi. Mohon pilih
arah:

1. **A** - sertifikat aritmetika karakter/struktural-zero lebih dulu;
2. **B** - matriks ad hoc with label terbatas;
3. **C** - kerjakan blok GW berkarakter which benar (riset);
4. **D** - tahan item 1, lanjut ke track lain.

Rekomendasi audit: **A lebih dulu**, lalu putuskan apakah B layak
dijalankan or C perlu didahulukan. Tanpa keputusan ini, implementasi
akan mengunci definisi which belum jelas and berisiko menghasilkan klaim
which no bisa dipertahankan.

---

### Lampiran: file and hash which dibaca

| Berkas | SHA-256 byte |
|---|---|
| `msaf/dirichlet.py` | `4b5cd5cdca4ee653868b29b95d27d45b601e0b028e56868f626e0e8a1b722978` |
| `msaf/gw_route_s_ladder.py` | `cc09ed5a35ac90b581cf2ef5660f3db903704843909b8a80b7fb21bf036a5b20` |
| `C:/Users/usER/oracle-toe/GUINAND_WEIL/source_arb_ldlt_certify.py` | `33617ce64b0e052c07873b196a3744f2f5142a4aaf7b4cfbe9e3de43d17c27bb` |
| `msaf/AUDIT.md` | `b72f615dd5036264409b04829d1607abcc8792426eff7e844bb5016a6da6c062` |
| `Five Core Experimental Problem Blueprint.md` | `f7739c2f7614281ec2228f5424d89e44bb492088e88e48420103203f2bbf0a1f` |


