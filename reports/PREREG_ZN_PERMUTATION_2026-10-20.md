# Pra-registrasi: sertifikat permutasi uniter `Z_N^Ã—` â€” 2026-10-20

**Status:** scope DIKUNCI for paket ini; implementasi and eksekusi **belum**
dimulai. Eksekusi menunggu GO eksplisit pemilik setelah pra-registrasi ini
in-hash and (bila diminta) in-commit.

**Berkas target:** `msaf/zn_permutation.py` (baru), guard
`msaf/tests/test_zn_permutation.py` (baru), report
`reports/ZN_PERMUTATION_2026-10-20.md`, receipt
`reports/zn_permutation_2026-10-20.json`.

**Dependensi:** `python-flint==0.9.0` (`fmpq_mat`, `fmpq_poly`), Python 3.14
in CI; no ada float in jalur inti.

**Registry which direncanakan:** `A-2026-0022`, hanya bila kriteria inti PASS.

**Tidak mengubah:** V1â€“V6 (`A-2026-0015`â€“`A-2026-0021`), `ci.yml`
(`A-2026-0016`), workflow `spec-v3.yml`/`spec-v4.yml`/`spec-v5.yml`/
`spec-v6.yml`, `lean/lakefile.toml`, `freeze` pins, and seluruh report beku.

## 1. Latar and pemisahan

Blueprint lima masalah eksperimental menempatkan item 2 sebagai kandidat
paling eksak: matriks permutasi dari perkalian modular on grup unit.
Paket ini menguji **struktur finite** tersebut, bukan membuat algoritma
faktorisasi.

Paket ini **bukan**:

- algoritma faktorisasi RSA/ECC, bukan pemecahan kunci, and bukan klaim
  kriptografi praktis;
- klaim bahwa periode `M` adalah rahasia; `N=15` and `N=21` adalah instance
  mainan which faktorisasinya already diketahui;
- klaim RH, klaim lokasi nol, or turunan `Ïƒ = 1/2`;
- penggunaan H1/engine-B/dashboard, data spektral, or kampanye numerik
  which already beku;
- formalisasi Lean/Coq baru. Ini paket exact finite Python.

## 2. Definisi which dikunci

Untuk `N â‰¥ 2`, misalkan

```text
X_N = { x : 1 â‰¤ x < N, gcd(x, N) = 1 },   diurutkan menaik
n   = |X_N| = Ï†(N)
```

Untuk `a` with `gcd(a, N) = 1`, definisikan permutasi

```text
U_N(a) |xâŸ© = |a x mod NâŸ©,   x âˆˆ X_N.
```

Konvensi matriks: kolom adalah state input, baris adalah state output.
Indeks baris/kolom adalah posisi 0-based dalam daftar `X_N` which diurutkan
menaik, bukan nilai `x` itu sendiri. Dengan demikian

```text
U[idx(a x mod N), idx(x)] = 1,   semua entri lain 0,
```

with `idx(y)` = posisi `y` in `X_N`.

Periode `M` adalah order multiplikatif minimal:

```text
M = min { m â‰¥ 1 : a^m â‰¡ 1 (mod N) }.
```

`U` adalah matriks permutation real, sehingga `Uâ€  = Uáµ€`. Klaim uniternya
adalah `Uáµ€ U = I` and `U Uáµ€ = I` secara exact.

## 3. Instance which dikunci

Dua instance dijalankan dalam paket which sama; keduanya harus PASS for
verdict inti PASS.

| Peran | `N` | `a` | `n = Ï†(N)` | `M` which diharapkan | Siklus which diharapkan |
|---|---:|---:|---:|---:|---:|
| Primer | 15 | 2 | 8 | 4 | 2 siklus panjang 4 |
| Replikasi | 21 | 2 | 12 | 6 | 2 siklus panjang 6 |

Daftar unit which dikunci:

```text
X_15 = [1, 2, 4, 7, 8, 11, 13, 14]
X_21 = [1, 2, 4, 5, 8, 10, 11, 13, 16, 17, 19, 20]
```

Siklus which dikunci (mulai dari elemen terkecil in setiap orbit):

```text
N=15: (1 â†’ 2 â†’ 4 â†’ 8 â†’ 1), (7 â†’ 14 â†’ 13 â†’ 11 â†’ 7)
N=21: (1 â†’ 2 â†’ 4 â†’ 8 â†’ 16 â†’ 11 â†’ 1),
      (5 â†’ 10 â†’ 20 â†’ 19 â†’ 17 â†’ 13 â†’ 5)
```

Nilai `M` no diasumsikan dari tabel: modul harus menghitungnya with
perkalian modular exact, lalu membandingkan with nilai which diharapkan.
Jika result hitung berbeda, kriteria FAIL, bukan disesuaikan.

## 4. Kriteria inti (PASS/FAIL)

### C1 â€” Konstruksi and permutation matrix

- `U` berukuran `n Ã— n`, semua entri `0` or `1`.
- Setiap baris and setiap kolom berjumlah tepat `1`.
- Untuk setiap `x âˆˆ X_N`, entri `U[(a*x) mod N, x]` adalah `1`.
- `Uáµ€ U = I` and `U Uáµ€ = I` exact.

### C2 â€” Order minimal

- `U^M = I` exact.
- `U^k â‰  I` for semua `1 â‰¤ k < M`.
- `M` result hitung sama with nilai which dikunci in Â§3.

### C3 â€” Dekomposisi siklus

- Dekomposisi `x â†’ a x mod N` menghasilkan tepat `n/M` siklus.
- Semua siklus panjangnya tepat `M`.
- Untuk kedua instance: tepat `2` siklus, panjang `4` and `6`.
- Daftar siklus dicatat in receipt.

### C4 â€” Charpoly and minpoly exact

- `charpoly(U)` sama with `(x^M - 1)^(n/M)` sebagai polinomial rasional.
- `minpoly(U)` sama with `x^M - 1`.
- Perbandingan memakai vektor koefisien exact, bukan string or float.

Nilai which diharapkan:

```text
N=15: charpoly = (x^4 - 1)^2 = x^8 - 2 x^4 + 1
      minpoly  = x^4 - 1
N=21: charpoly = (x^6 - 1)^2 = x^12 - 2 x^6 + 1
      minpoly  = x^6 - 1
```

### C5 â€” Faktorisasi cyclotomic

- Hitung `Î¦_d(x)` secara rekursif exact for setiap `d | M`.
- Verifikasi `âˆ_{d|M} Î¦_d(x) = x^M - 1`.
- Verifikasi `charpoly(U) = (âˆ_{d|M} Î¦_d(x))^(n/M)`.
- Faktorisasi `fmpq_poly.factor()` harus konsisten with result rekursif.
- Kesimpulan which diizinkan: multiset eigenvalue `U` adalah akar ke-`M`
  dari unity, masing-masing with multiplisitas `n/M`.

Faktor which diharapkan:

```text
N=15, M=4: Î¦1 = x-1, Î¦2 = x+1, Î¦4 = x^2+1
N=21, M=6: Î¦1 = x-1, Î¦2 = x+1, Î¦3 = x^2+x+1, Î¦6 = x^2-x+1
```

### C6 â€” Receipt deterministik

- JSON kanonik (key diurutkan, tanpa float, tanpa timestamp in payload inti).
- Memuat: versi skema, `N`, `a`, daftar unit, `n`, `M`, siklus, hash matriks
  kanonik, koefisien charpoly/minpoly, faktor cyclotomic, status C1â€“C5,
  status subklaim komutasi, and verdict.
- Hash SHA-256 payload dicatat in report.
- Re-run dari input which sama menghasilkan payload which sama.

### C7 â€” Guard and CI

- Guard `msaf/tests/test_zn_permutation.py` menguji C1â€“C6.
- Guard menolak tamper minimal: ubah satu entri `U`, ubah `M`, ubah satu
  koefisien charpoly, or rusak receipt; semuanya harus FAIL.
- Guard statis memastikan jalur inti no memakai `float`, `numpy`,
  `numpy.float64`, or `arb`; hanya integer/`fmpq`/`fmpq_mat`.
- Suite penuh and CI utama hijau.
- Tidak ada workflow baru; guard masuk suite `msaf` which already ada.

### C8 â€” Verdict

- `PASS` hanya jika C1â€“C7 lulus for **kedua** instance.
- `FAILED` jika ada satu kriteria inti gagal; counterexample dicatat.
- `INCONCLUSIVE`/`TOOL NOT RUN` jika `fmpq_mat`/`fmpq_poly` API no
  tersedia or eksekusi no lengkap. Status ini no boleh dinaikkan
  menjadi PASS.
- Registry `A-2026-0022` hanya created bila verdict inti PASS.

## 5. Subklaim komutasi (terpisah dari verdict inti)

Blueprint menyebut uji `[H, U] = 0`. `H` no didefinisikan secara unik,
jadi subklaim ini **no** menjadi syarat PASS inti. Rencana testing:

1. `T` = cyclic shift exact on daftar `X_N` which sama:
   `T[(i+1) mod n, i] = 1`.
2. Hitung `C = T U - U T` exact. Status:
   - `ZERO` jika semua entri nol;
   - `NONZERO` jika ada entri no nol, with witness `(i, j, nilai)` and
     `max |entry|`.
3. `H_ctrl = U + Uáµ€` sebagai kontrol positif. `[H_ctrl, U] = 0` diharapkan
   exact, tetapi **tautologis** karena `H_ctrl` adalah polinomial in `U`.
   Statusnya dicatat sebagai kontrol, bukan bukti independen.
4. `U` memiliki dua orbit, sedangkan `T` satu orbit; karena itu
   `[T, U] = 0` no diasumsikan and result `NONZERO` tetap merupakan result
   finite which sah. Paket inti no boleh diklaim gagal hanya karena
   subklaim ini non-zero.
5. Jika pemilik ingin komutasi menjadi syarat PASS, `H` harus didefinisikan
   lebih dulu and pra-registrasi harus diamendemen sebelum eksekusi.

**Koreksi Sturm:** blueprint menyebut *exact Sturm bisection counts*.
Sturm menghitung akar real dari polinomial; `U` adalah matriks permutation
non-Hermitian with eigenvalue kompleks. Karena itu Sturm **no** dipakai
for spektrum `U`. Spektrum `U` disertifikasi oleh charpoly/minpoly and
faktorisasi cyclotomic exact. Sturm hanya relevan bila nanti ada `H`
Hermitian terpisah, and itu bukan scope paket ini.

## 6. Batas eksplisit

- Ini sertifikat finite for dua instance mainan, bukan teorema umum.
- Tidak ada klaim faktorisasi, keamanan RSA/ECC, or percepatan period
  finding.
- `M` adalah order publik `a mod N`; no ada klaim bahwa spektrum `U`
  mengekstrak rahasia.
- Tidak ada klaim RH, lokasi nol, `Ïƒ = 1/2`, or fisika.
- Tidak ada Lean/Coq/SMT; no ada perubahan on trusted base mana pun.
- PASS berarti kriteria exact in Â§4 terpenuhi, bukan peer review.

## 7. Artefak and urutan eksekusi

1. Pra-registrasi ini in-hash; bila disetujui, commit pra-registrasi
   sebelum kode.
2. Implementasi `msaf/zn_permutation.py`.
3. Guard `msaf/tests/test_zn_permutation.py`.
4. Jalankan kedua instance, hasilkan receipt JSON.
5. Tulis report `reports/ZN_PERMUTATION_2026-10-20.md` with result verbatim,
   hash receipt, and verdict per kriteria.
6. Bila PASS: registry `A-2026-0022`, HANDOFF Â§2.0ap, sertifikat sha256LF
   for modul/guard/report/prereg/receipt.
7. Suite penuh, `freeze.py --verify`, and CI; commit/push hanya bila diminta.

## 8. Falsifier

Paket ini FAIL bila salah satu terjadi:

- `U` bukan permutation matrix or `Uáµ€U â‰  I`;
- `M` result hitung bukan `4`/`6`, or ada `k < M` with `U^k = I`;
- jumlah/panjang siklus no sama with `n/M` and `M`;
- charpoly/minpoly berbeda dari nilai which dikunci;
- produk cyclotomic no sama with `x^M - 1`;
- receipt no deterministik or hash no cocok;
- guard no menangkap tamper which diwajibkan;
- ada `float`/`numpy`/`arb` in jalur inti.

Kegagalan subklaim komutasi **bukan** falsifier inti; ia dicatat sebagai
`NONZERO` on section result.


