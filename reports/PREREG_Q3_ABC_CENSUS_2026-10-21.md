# Pra-registrasi: Sensus abc Tersertifikasi â€” Pencarian Triple (a,b,c) hingga C â€” 2026-10-21

**Status:** scope DIKUNCI for paket Q3; implementasi and eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket Q3. Hash `sha256LF` file ini
dicatat in receipt and report.

**Paket:** Q3 dari
[`reports/DAFTAR_MASALAH_KERJA.md`](DAFTAR_MASALAH_KERJA.md),
yaitu Sensus abc Tersertifikasi â€” pencarian semua triple (a,b,c) hingga C
with kualitas q = log(c)/log(rad(abc)) > 1.4 which diverifikasi ulang independen.

**Berkas target:** `msaf/abc_census.py` (baru), guard
`msaf/tests/test_abc_census.py` (baru), report
`reports/ABC_CENSUS_2026-10-21.md`, receipt
`reports/abc_census_2026-10-21.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (`fmpz`, `fmpz_factor`), `math.gcd`. Tidak ada `numpy`/`scipy` in jalur inti.

**Registry which direncanakan:** `A-2026-0032`, hanya bila verdict inti
`ALL PASS` and integritas PASS.

**Tidak mengubah:** V1â€“V6 (`A-2026-0015`â€“`A-2026-0021`), `A-2026-0022`â€“`A-2026-0031`, `ci.yml` (`A-2026-0016`), workflow spec, `lean/lakefile.toml`, freeze pins, seluruh report/artefak beku.

## 1. Maksud and limit

Paket ini melakukan **sensus abc lengkap hingga limit C**: menghitung semua triple
(a,b,c) with a+b=c, a,b,c positif integer, gcd(a,b,c)=1, hingga limit C which
dikunci, and merekam semua triple with kualitas q = log(c)/log(rad(abc)) > 1.4.

**Objek sensus:**
- Semua triple (a,b,c) with a+b=c, a,b,c > 0, gcd(a,b,c)=1, c â‰¤ C
- Kualitas q = log(c) / log(rad(abc)) in mana rad(n) = produk faktor prima unik dari n
- Hanya triple with q > 1.4 dicatat sebagai "rekord kualitas"

**Dua implementasi sieve independen (wajib):**
1. **Sieve A**: Sieve of Eratosthenes berbasis `fmpz` + `fmpz_factor` for rad(abc)
2. **Sieve B**: Sieve terpisah total (mis. `sympy.factorint` or implementasi trial division terpisah) which **no berbagi kode** with Sieve A

**Kriteria kesepakatan (sepakat integer-per-integer):**
- Jumlah total triple (a,b,c) hingga C identik
- Daftar triple (a,b,c) identik (jika C â‰¤ 10^5)
- Semua triple with q > 1.4 identik (daftar lengkap)

Paket ini **bukan**:
- Pembuktian konjektur abc (hanya sensus hingga C)
- Klaim asimtotik (hanya hitungan hingga C)
- Klaim RH, GRH, faktorisasi, RSA/ECC, Anderson, or fisika

## 2. Definisi which dikunci

**Definisi radikal:** rad(n) = produk faktor prima unik dari n (mis. rad(60) = 2*3*5 = 30)

**Kualitas:** q(a,b,c) = log(c) / log(rad(a*b*c))

**Triple valid:** a,b,c âˆˆ â„•, a+b=c, gcd(a,b,c)=1, a,b,c > 0

**Threshold kualitas:** q > 1.4 (threshold standar for "abc hits")

**Batas C (dikunci):** C = 10^7 (10 juta) for kampanye ini; N = 10^6 for verifikasi cepat

## 3. Algoritma which dikunci

**Sieve A (fmpz-based):**
- Bangun array `rad[1..C]` with sieve linear O(N log log N)
- Untuk setiap a âˆˆ [1, C/2], iterasi b dari a+1 hingga C-a
- c = a + b; hitung rad(a*b*c) = rad(a)*rad(b)*rad(c) / rad(gcd(a,b,c))^2 (approximate, sebenarnya perlu rad(abc) langsung)
- Hitung q = log(c) / log(rad(a*b*c))
- Catat jika q > 1.4

**Optimasi:**
- Hanya iterasi a < b < c for menghindari duplikasi
- Precompute rad[1..C] with sieve linear O(C log log C)
- Early termination jika rad(a*b*c) terlalu besar

**Dua implementasi independen:**
1. `abc_sieve_a.py` - implementasi `fmpz` + `fmpz_factor` (FLINT)
2. `abc_sieve_b.py` - implementasi terpisah (mis. `sympy.factorint` or trial division)

**Kriteria kesepakatan (sepakat integer-per-integer):**
- `count_A == count_B`
- `list_triples_A == list_triples_B` (for C â‰¤ 10^5)

## 4. Konfigurasi which dikunci

| Parameter | Nilai |
|-----------|-------|
| C_max | 10^7 (10 juta) |
| Threshold kualitas | q > 1.4 |
| Verifikasi cepat | N = 10^6 |

Tidak ada parameter tambahan setelah result terlihat.

## 4. Pemeriksaan integritas (C1â€“C4)

**C1: Kedua sieve menghasilkan count identik**
- `count_A == count_B` for C = 10^7

**C2: Kualitas triple identik**
- Semua triple (a,b,c) with q > 1.4 identik antara kedua sieve

**C3: Determinisme & receipt**
- Receipt deterministik: dua run berturut-turut menghasilkan payload kanonik identik
- Hash sha256 terkunci

**C4: Verifikasi independen (opsi)**
- Verifikasi sampel triple q > 1.4 terhadap database LMFDB/abc-hits (jika tersedia)

## 5. Verdict

- **ALL PASS**: C1, C2, C3, C4 PASS for C = 10^7
- **PARTIAL**: no ada (paket ini all-or-nothing)
- **FAILED**: salah satu C1â€“C4 gagal
- **INCONCLUSIVE**: tool error, memori no cukup, or hash mismatch

Registry `A-2026-0032` hanya bila verdict `ALL PASS` and integritas PASS.

## 5. Falsifier

Paket ini falsified bila:
- `count_A != count_B` for C which dikunci
- Ada triple q > 1.4 which hanya ditemukan satu sieve
- Receipt no deterministik or hash mismatch
- Memori melebihi limit sistem (OOM)

## 6. Artefak and urutan eksekusi

1. Tulis and hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/abc_census.py` with dua sieve independen.
3. Guard `msaf/tests/test_abc_census.py`: uji kesepakatan count, list triple, q > 1.4, determinisme.
4. Jalankan kampanye for C = 10^6 (verifikasi cepat) and C = 10^7 (full).
5. Tulis report `reports/ABC_CENSUS_2026-10-21.md` with angka verbatim.
6. Bila `ALL PASS`: registry `A-2026-0032`, HANDOFF Â§2.0ay, sertifikat sha256LF.
7. Suite penuh and `freeze.py --verify`; commit/push hanya bila diminta.

## 6. Batas eksplisit

- Hanya C = 10^7 (10 juta) for kampanye ini
- Threshold kualitas q > 1.4 (no ada threshold lain)
- Tidak ada klaim konjektur abc terbukti/no terbukti
- Tidak ada klaim RH, GRH, faktorisasi, RSA/ECC, Anderson, or fisika
- Tidak ada klaim asimtotik (hanya sensus hingga C)
- Hanya sensus hingga C = 10^7 for kampanye ini

