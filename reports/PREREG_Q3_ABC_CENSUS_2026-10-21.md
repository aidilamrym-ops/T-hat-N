# Pra-registrasi: Sensus abc Tersertifikasi — Pencarian Triple (a,b,c) hingga C — 2026-10-21

**Status:** scope DIKUNCI untuk paket Q3; implementasi dan eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket Q3. Hash `sha256LF` berkas ini
dicatat di receipt dan laporan.

**Paket:** Q3 dari
[`reports/DAFTAR_MASALAH_KERJA.md`](DAFTAR_MASALAH_KERJA.md),
yaitu Sensus abc Tersertifikasi — pencarian semua triple (a,b,c) hingga C
dengan kualitas q = log(c)/log(rad(abc)) > 1.4 yang diverifikasi ulang independen.

**Berkas target:** `msaf/abc_census.py` (baru), guard
`msaf/tests/test_abc_census.py` (baru), laporan
`reports/ABC_CENSUS_2026-10-21.md`, receipt
`reports/abc_census_2026-10-21.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (`fmpz`, `fmpz_factor`), `math.gcd`. Tidak ada `numpy`/`scipy` di jalur inti.

**Registry yang direncanakan:** `A-2026-0032`, hanya bila verdict inti
`ALL PASS` dan integritas PASS.

**Tidak mengubah:** V1–V6 (`A-2026-0015`–`A-2026-0021`), `A-2026-0022`–`A-2026-0031`, `ci.yml` (`A-2026-0016`), workflow spec, `lean/lakefile.toml`, freeze pins, seluruh laporan/artefak beku.

## 1. Maksud dan batas

Paket ini melakukan **sensus abc lengkap hingga batas C**: menghitung semua triple
(a,b,c) dengan a+b=c, a,b,c positif integer, gcd(a,b,c)=1, hingga batas C yang
dikunci, dan merekam semua triple dengan kualitas q = log(c)/log(rad(abc)) > 1.4.

**Objek sensus:**
- Semua triple (a,b,c) dengan a+b=c, a,b,c > 0, gcd(a,b,c)=1, c ≤ C
- Kualitas q = log(c) / log(rad(abc)) di mana rad(n) = produk faktor prima unik dari n
- Hanya triple dengan q > 1.4 dicatat sebagai "rekord kualitas"

**Dua implementasi sieve independen (wajib):**
1. **Sieve A**: Sieve of Eratosthenes berbasis `fmpz` + `fmpz_factor` untuk rad(abc)
2. **Sieve B**: Sieve terpisah total (mis. `sympy.factorint` atau implementasi trial division terpisah) yang **tidak berbagi kode** dengan Sieve A

**Kriteria kesepakatan (sepakat integer-per-integer):**
- Jumlah total triple (a,b,c) hingga C identik
- Daftar triple (a,b,c) identik (jika C ≤ 10^5)
- Semua triple dengan q > 1.4 identik (daftar lengkap)

Paket ini **bukan**:
- Pembuktian konjektur abc (hanya sensus hingga C)
- Klaim asimtotik (hanya hitungan hingga C)
- Klaim RH, GRH, faktorisasi, RSA/ECC, Anderson, atau fisika

## 2. Definisi yang dikunci

**Definisi radikal:** rad(n) = produk faktor prima unik dari n (mis. rad(60) = 2*3*5 = 30)

**Kualitas:** q(a,b,c) = log(c) / log(rad(a*b*c))

**Triple valid:** a,b,c ∈ ℕ, a+b=c, gcd(a,b,c)=1, a,b,c > 0

**Threshold kualitas:** q > 1.4 (threshold standar untuk "abc hits")

**Batas C (dikunci):** C = 10^7 (10 juta) untuk kampanye ini; N = 10^6 untuk verifikasi cepat

## 3. Algoritma yang dikunci

**Sieve A (fmpz-based):**
- Bangun array `rad[1..C]` dengan sieve linear O(N log log N)
- Untuk setiap a ∈ [1, C/2], iterasi b dari a+1 hingga C-a
- c = a + b; hitung rad(a*b*c) = rad(a)*rad(b)*rad(c) / rad(gcd(a,b,c))^2 (approximate, sebenarnya perlu rad(abc) langsung)
- Hitung q = log(c) / log(rad(a*b*c))
- Catat jika q > 1.4

**Optimasi:**
- Hanya iterasi a < b < c untuk menghindari duplikasi
- Precompute rad[1..C] dengan sieve linear O(C log log C)
- Early termination jika rad(a*b*c) terlalu besar

**Dua implementasi independen:**
1. `abc_sieve_a.py` - implementasi `fmpz` + `fmpz_factor` (FLINT)
2. `abc_sieve_b.py` - implementasi terpisah (mis. `sympy.factorint` atau trial division)

**Kriteria kesepakatan (sepakat integer-per-integer):**
- `count_A == count_B`
- `list_triples_A == list_triples_B` (untuk C ≤ 10^5)

## 4. Konfigurasi yang dikunci

| Parameter | Nilai |
|-----------|-------|
| C_max | 10^7 (10 juta) |
| Threshold kualitas | q > 1.4 |
| Verifikasi cepat | N = 10^6 |

Tidak ada parameter tambahan setelah hasil terlihat.

## 4. Pemeriksaan integritas (C1–C4)

**C1: Kedua sieve menghasilkan count identik**
- `count_A == count_B` untuk C = 10^7

**C2: Kualitas triple identik**
- Semua triple (a,b,c) dengan q > 1.4 identik antara kedua sieve

**C3: Determinisme & receipt**
- Receipt deterministik: dua run berturut-turut menghasilkan payload kanonik identik
- Hash sha256 terkunci

**C4: Verifikasi independen (opsi)**
- Verifikasi sampel triple q > 1.4 terhadap database LMFDB/abc-hits (jika tersedia)

## 5. Verdict

- **ALL PASS**: C1, C2, C3, C4 PASS untuk C = 10^7
- **PARTIAL**: tidak ada (paket ini all-or-nothing)
- **FAILED**: salah satu C1–C4 gagal
- **INCONCLUSIVE**: tool error, memori tidak cukup, atau hash mismatch

Registry `A-2026-0032` hanya bila verdict `ALL PASS` dan integritas PASS.

## 5. Falsifier

Paket ini falsified bila:
- `count_A != count_B` untuk C yang dikunci
- Ada triple q > 1.4 yang hanya ditemukan satu sieve
- Receipt tidak deterministik atau hash mismatch
- Memori melebihi batas sistem (OOM)

## 6. Artefak dan urutan eksekusi

1. Tulis dan hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/abc_census.py` dengan dua sieve independen.
3. Guard `msaf/tests/test_abc_census.py`: uji kesepakatan count, list triple, q > 1.4, determinisme.
4. Jalankan kampanye untuk C = 10^6 (verifikasi cepat) dan C = 10^7 (full).
5. Tulis laporan `reports/ABC_CENSUS_2026-10-21.md` dengan angka verbatim.
6. Bila `ALL PASS`: registry `A-2026-0032`, HANDOFF §2.0ay, sertifikat sha256LF.
7. Suite penuh dan `freeze.py --verify`; commit/push hanya bila diminta.

## 6. Batas eksplisit

- Hanya C = 10^7 (10 juta) untuk kampanye ini
- Threshold kualitas q > 1.4 (tidak ada threshold lain)
- Tidak ada klaim konjektur abc terbukti/tidak terbukti
- Tidak ada klaim RH, GRH, faktorisasi, RSA/ECC, Anderson, atau fisika
- Tidak ada klaim asimtotik (hanya sensus hingga C)
- Hanya sensus hingga C = 10^7 untuk kampanye ini