# Pra-registrasi: sertifikat permutasi uniter `Z_N^×` — 2026-10-20

**Status:** scope DIKUNCI untuk paket ini; implementasi dan eksekusi **belum**
dimulai. Eksekusi menunggu GO eksplisit pemilik setelah pra-registrasi ini
di-hash dan (bila diminta) di-commit.

**Berkas target:** `msaf/zn_permutation.py` (baru), guard
`msaf/tests/test_zn_permutation.py` (baru), laporan
`reports/ZN_PERMUTATION_2026-10-20.md`, receipt
`reports/zn_permutation_2026-10-20.json`.

**Dependensi:** `python-flint==0.9.0` (`fmpq_mat`, `fmpq_poly`), Python 3.14
di CI; tidak ada float di jalur inti.

**Registry yang direncanakan:** `A-2026-0022`, hanya bila kriteria inti PASS.

**Tidak mengubah:** V1–V6 (`A-2026-0015`–`A-2026-0021`), `ci.yml`
(`A-2026-0016`), workflow `spec-v3.yml`/`spec-v4.yml`/`spec-v5.yml`/
`spec-v6.yml`, `lean/lakefile.toml`, `freeze` pins, dan seluruh laporan beku.

## 1. Latar dan pemisahan

Blueprint lima masalah eksperimental menempatkan item 2 sebagai kandidat
paling eksak: matriks permutasi dari perkalian modular pada grup unit.
Paket ini menguji **struktur finite** tersebut, bukan membuat algoritma
faktorisasi.

Paket ini **bukan**:

- algoritma faktorisasi RSA/ECC, bukan pemecahan kunci, dan bukan klaim
  kriptografi praktis;
- klaim bahwa periode `M` adalah rahasia; `N=15` dan `N=21` adalah instance
  mainan yang faktorisasinya sudah diketahui;
- klaim RH, klaim lokasi nol, atau turunan `σ = 1/2`;
- penggunaan H1/engine-B/dashboard, data spektral, atau kampanye numerik
  yang sudah beku;
- formalisasi Lean/Coq baru. Ini paket exact finite Python.

## 2. Definisi yang dikunci

Untuk `N ≥ 2`, misalkan

```text
X_N = { x : 1 ≤ x < N, gcd(x, N) = 1 },   diurutkan menaik
n   = |X_N| = φ(N)
```

Untuk `a` dengan `gcd(a, N) = 1`, definisikan permutasi

```text
U_N(a) |x⟩ = |a x mod N⟩,   x ∈ X_N.
```

Konvensi matriks: kolom adalah state input, baris adalah state output.
Indeks baris/kolom adalah posisi 0-based dalam daftar `X_N` yang diurutkan
menaik, bukan nilai `x` itu sendiri. Dengan demikian

```text
U[idx(a x mod N), idx(x)] = 1,   semua entri lain 0,
```

dengan `idx(y)` = posisi `y` di `X_N`.

Periode `M` adalah order multiplikatif minimal:

```text
M = min { m ≥ 1 : a^m ≡ 1 (mod N) }.
```

`U` adalah matriks permutation real, sehingga `U† = Uᵀ`. Klaim uniternya
adalah `Uᵀ U = I` dan `U Uᵀ = I` secara exact.

## 3. Instance yang dikunci

Dua instance dijalankan dalam paket yang sama; keduanya harus PASS untuk
verdict inti PASS.

| Peran | `N` | `a` | `n = φ(N)` | `M` yang diharapkan | Siklus yang diharapkan |
|---|---:|---:|---:|---:|---:|
| Primer | 15 | 2 | 8 | 4 | 2 siklus panjang 4 |
| Replikasi | 21 | 2 | 12 | 6 | 2 siklus panjang 6 |

Daftar unit yang dikunci:

```text
X_15 = [1, 2, 4, 7, 8, 11, 13, 14]
X_21 = [1, 2, 4, 5, 8, 10, 11, 13, 16, 17, 19, 20]
```

Siklus yang dikunci (mulai dari elemen terkecil di setiap orbit):

```text
N=15: (1 → 2 → 4 → 8 → 1), (7 → 14 → 13 → 11 → 7)
N=21: (1 → 2 → 4 → 8 → 16 → 11 → 1),
      (5 → 10 → 20 → 19 → 17 → 13 → 5)
```

Nilai `M` tidak diasumsikan dari tabel: modul harus menghitungnya dengan
perkalian modular exact, lalu membandingkan dengan nilai yang diharapkan.
Jika hasil hitung berbeda, kriteria FAIL, bukan disesuaikan.

## 4. Kriteria inti (PASS/FAIL)

### C1 — Konstruksi dan permutation matrix

- `U` berukuran `n × n`, semua entri `0` atau `1`.
- Setiap baris dan setiap kolom berjumlah tepat `1`.
- Untuk setiap `x ∈ X_N`, entri `U[(a*x) mod N, x]` adalah `1`.
- `Uᵀ U = I` dan `U Uᵀ = I` exact.

### C2 — Order minimal

- `U^M = I` exact.
- `U^k ≠ I` untuk semua `1 ≤ k < M`.
- `M` hasil hitung sama dengan nilai yang dikunci di §3.

### C3 — Dekomposisi siklus

- Dekomposisi `x → a x mod N` menghasilkan tepat `n/M` siklus.
- Semua siklus panjangnya tepat `M`.
- Untuk kedua instance: tepat `2` siklus, panjang `4` dan `6`.
- Daftar siklus dicatat di receipt.

### C4 — Charpoly dan minpoly exact

- `charpoly(U)` sama dengan `(x^M - 1)^(n/M)` sebagai polinomial rasional.
- `minpoly(U)` sama dengan `x^M - 1`.
- Perbandingan memakai vektor koefisien exact, bukan string atau float.

Nilai yang diharapkan:

```text
N=15: charpoly = (x^4 - 1)^2 = x^8 - 2 x^4 + 1
      minpoly  = x^4 - 1
N=21: charpoly = (x^6 - 1)^2 = x^12 - 2 x^6 + 1
      minpoly  = x^6 - 1
```

### C5 — Faktorisasi cyclotomic

- Hitung `Φ_d(x)` secara rekursif exact untuk setiap `d | M`.
- Verifikasi `∏_{d|M} Φ_d(x) = x^M - 1`.
- Verifikasi `charpoly(U) = (∏_{d|M} Φ_d(x))^(n/M)`.
- Faktorisasi `fmpq_poly.factor()` harus konsisten dengan hasil rekursif.
- Kesimpulan yang diizinkan: multiset eigenvalue `U` adalah akar ke-`M`
  dari unity, masing-masing dengan multiplisitas `n/M`.

Faktor yang diharapkan:

```text
N=15, M=4: Φ1 = x-1, Φ2 = x+1, Φ4 = x^2+1
N=21, M=6: Φ1 = x-1, Φ2 = x+1, Φ3 = x^2+x+1, Φ6 = x^2-x+1
```

### C6 — Receipt deterministik

- JSON kanonik (key diurutkan, tanpa float, tanpa timestamp di payload inti).
- Memuat: versi skema, `N`, `a`, daftar unit, `n`, `M`, siklus, hash matriks
  kanonik, koefisien charpoly/minpoly, faktor cyclotomic, status C1–C5,
  status subklaim komutasi, dan verdict.
- Hash SHA-256 payload dicatat di laporan.
- Re-run dari input yang sama menghasilkan payload yang sama.

### C7 — Guard dan CI

- Guard `msaf/tests/test_zn_permutation.py` menguji C1–C6.
- Guard menolak tamper minimal: ubah satu entri `U`, ubah `M`, ubah satu
  koefisien charpoly, atau rusak receipt; semuanya harus FAIL.
- Guard statis memastikan jalur inti tidak memakai `float`, `numpy`,
  `numpy.float64`, atau `arb`; hanya integer/`fmpq`/`fmpq_mat`.
- Suite penuh dan CI utama hijau.
- Tidak ada workflow baru; guard masuk suite `msaf` yang sudah ada.

### C8 — Verdict

- `PASS` hanya jika C1–C7 lulus untuk **kedua** instance.
- `FAILED` jika ada satu kriteria inti gagal; counterexample dicatat.
- `INCONCLUSIVE`/`TOOL NOT RUN` jika `fmpq_mat`/`fmpq_poly` API tidak
  tersedia atau eksekusi tidak lengkap. Status ini tidak boleh dinaikkan
  menjadi PASS.
- Registry `A-2026-0022` hanya dibuat bila verdict inti PASS.

## 5. Subklaim komutasi (terpisah dari verdict inti)

Blueprint menyebut uji `[H, U] = 0`. `H` tidak didefinisikan secara unik,
jadi subklaim ini **tidak** menjadi syarat PASS inti. Rencana pengujian:

1. `T` = cyclic shift exact pada daftar `X_N` yang sama:
   `T[(i+1) mod n, i] = 1`.
2. Hitung `C = T U - U T` exact. Status:
   - `ZERO` jika semua entri nol;
   - `NONZERO` jika ada entri tidak nol, dengan witness `(i, j, nilai)` dan
     `max |entry|`.
3. `H_ctrl = U + Uᵀ` sebagai kontrol positif. `[H_ctrl, U] = 0` diharapkan
   exact, tetapi **tautologis** karena `H_ctrl` adalah polinomial di `U`.
   Statusnya dicatat sebagai kontrol, bukan bukti independen.
4. `U` memiliki dua orbit, sedangkan `T` satu orbit; karena itu
   `[T, U] = 0` tidak diasumsikan dan hasil `NONZERO` tetap merupakan hasil
   finite yang sah. Paket inti tidak boleh diklaim gagal hanya karena
   subklaim ini non-zero.
5. Jika pemilik ingin komutasi menjadi syarat PASS, `H` harus didefinisikan
   lebih dulu dan pra-registrasi harus diamendemen sebelum eksekusi.

**Koreksi Sturm:** blueprint menyebut *exact Sturm bisection counts*.
Sturm menghitung akar real dari polinomial; `U` adalah matriks permutation
non-Hermitian dengan eigenvalue kompleks. Karena itu Sturm **tidak** dipakai
untuk spektrum `U`. Spektrum `U` disertifikasi oleh charpoly/minpoly dan
faktorisasi cyclotomic exact. Sturm hanya relevan bila nanti ada `H`
Hermitian terpisah, dan itu bukan scope paket ini.

## 6. Batas eksplisit

- Ini sertifikat finite untuk dua instance mainan, bukan teorema umum.
- Tidak ada klaim faktorisasi, keamanan RSA/ECC, atau percepatan period
  finding.
- `M` adalah order publik `a mod N`; tidak ada klaim bahwa spektrum `U`
  mengekstrak rahasia.
- Tidak ada klaim RH, lokasi nol, `σ = 1/2`, atau fisika.
- Tidak ada Lean/Coq/SMT; tidak ada perubahan pada trusted base mana pun.
- PASS berarti kriteria exact di §4 terpenuhi, bukan peer review.

## 7. Artefak dan urutan eksekusi

1. Pra-registrasi ini di-hash; bila disetujui, commit pra-registrasi
   sebelum kode.
2. Implementasi `msaf/zn_permutation.py`.
3. Guard `msaf/tests/test_zn_permutation.py`.
4. Jalankan kedua instance, hasilkan receipt JSON.
5. Tulis laporan `reports/ZN_PERMUTATION_2026-10-20.md` dengan hasil verbatim,
   hash receipt, dan verdict per kriteria.
6. Bila PASS: registry `A-2026-0022`, HANDOFF §2.0ap, sertifikat sha256LF
   untuk modul/guard/laporan/prereg/receipt.
7. Suite penuh, `freeze.py --verify`, dan CI; commit/push hanya bila diminta.

## 8. Falsifier

Paket ini FAIL bila salah satu terjadi:

- `U` bukan permutation matrix atau `UᵀU ≠ I`;
- `M` hasil hitung bukan `4`/`6`, atau ada `k < M` dengan `U^k = I`;
- jumlah/panjang siklus tidak sama dengan `n/M` dan `M`;
- charpoly/minpoly berbeda dari nilai yang dikunci;
- produk cyclotomic tidak sama dengan `x^M - 1`;
- receipt tidak deterministik atau hash tidak cocok;
- guard tidak menangkap tamper yang diwajibkan;
- ada `float`/`numpy`/`arb` di jalur inti.

Kegagalan subklaim komutasi **bukan** falsifier inti; ia dicatat sebagai
`NONZERO` pada bagian hasil.
