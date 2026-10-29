# Sertifikat exact permutasi uniter `Z_N^Ã—` â€” 2026-10-20

**Status:** **PASS** for kriteria inti C1â€“C6 and guard/CI C7.
**CI utama:** run `39442388960` (commit `6d7b78a`) **success**:
`python-tests` 1m1s, `coq-kernel` 1m57s, `lean-kernel` 2m16s.
Registry `A-2026-0022` created setelah CI hijau.

**Pra-registrasi:** `reports/PREREG_ZN_PERMUTATION_2026-10-20.md`,
commit `8c5c642`, sha256LF
`80474c5447b5215bdc8e19548450ef68c60e879ff2423aac01a7d6ecc34e2cbf`.

**Receipt:** `reports/zn_permutation_2026-10-20.json`, sha256 kanonik
`c80b6621fcb1797a0c78f615176dc1400e6210011a084f733092bcb3719bda6c`.

## 1. Hasil per instance

| Item | `N=15` | `N=21` |
|---|---:|---:|
| `a` | 2 | 2 |
| `dim = Ï†(N)` | 8 | 12 |
| `M = ord_N(a)` | 4 | 6 |
| Siklus | `(1 2 4 8)`, `(7 14 13 11)` | `(1 2 4 8 16 11)`, `(5 10 20 19 17 13)` |
| `charpoly` | `x^8 - 2x^4 + 1` | `x^12 - 2x^6 + 1` |
| `minpoly` | `x^4 - 1` | `x^6 - 1` |
| Determinan | `+1` | `+1` |
| Matrix SHA-256 | `e4092e0155e3ea225966cc8a64e1e0a6cd9f47e4e25e510b3a8e24d99b9a58d8` | `e40b2334b942a2fc0feed818e5b5a5a39b79d745625e95acd3fe7f3b21cc2a85` |
| Verdict inti | **PASS** | **PASS** |

Semua pemeriksaan in receipt bernilai `true`:

```text
C1_permutation, C1_unitarity,
C2_order, C2_minimal, C2_expected_m,
C3_cycles,
C4_charpoly, C4_minpoly,
C5_cyclotomic, C5_factor
```

## 2. Metode exact

Untuk `X_N = {x : 1 â‰¤ x < N, gcd(x,N)=1}` which diurutkan, matriks
didefinisikan with indeks posisi 0-based:

```text
U[idx(a*x mod N), idx(x)] = 1,
```

and semua entri lain `0`. Semua perhitungan memakai `fmpq_mat`/`fmpq_poly`
dari `python-flint 0.9.0`; no ada `float`, `numpy`, or `arb` in jalur
inti.

Pemeriksaan which dijalankan:

1. `U` adalah permutation matrix `0/1`; `Uáµ€U = I` and `UUáµ€ = I`.
2. `M` dihitung dari perkalian modular exact, bukan diasumsikan; `U^M = I`
   and `U^k â‰  I` for `1 â‰¤ k < M`.
3. Dekomposisi siklus exact; dua siklus panjang `M` for kedua instance.
4. `charpoly`/`minpoly` exact, dibandingkan sebagai koefisien, bukan string.
5. Faktorisasi cyclotomic exact:
   - `N=15`: `(x-1)(x+1)(x^2+1) = x^4 - 1`
   - `N=21`: `(x-1)(x+1)(x^2+x+1)(x^2-x+1) = x^6 - 1`
   lalu `charpoly = (âˆ Î¦_d)^(Ï†(N)/M)`.
6. `fmpq_poly.factor()` dikalikan kembali and dicocokkan with charpoly;
   setiap faktor irreducible harus termasuk himpunan cyclotomic.

Kesimpulan which diizinkan: multiset eigenvalue `U` adalah akar ke-`M` dari
unity, masing-masing with multiplisitas `Ï†(N)/M`. Ini konsekuensi exact
dari charpoly, bukan result floating-point.

**Catatan Sturm:** Sturm no dipakai for `U`, karena `U` adalah matriks
permutation non-Hermitian with eigenvalue kompleks. Sturm menghitung akar
real and akan menjadi alat which salah in sini. Jika nanti ada `H` Hermitian,
Sturm dapat dipertimbangkan sebagai paket terpisah.

## 3. Komutasi `[H,U]` â€” result terpisah

Dengan `H = CyclicShift` exact on daftar unit which sama:

| Instance | Status | Witness pertama | Entri non-zero | `max |entry|` |
|---|---|---:|---:|---:|
| `N=15` | `NONZERO` | `(row=1, col=4, value=1)` | 10 | 1 |
| `N=21` | `NONZERO` | `(row=1, col=6, value=1)` | 14 | 1 |

Jadi `U` **no** komut with cyclic shift on ruang unit ini. Ini result
finite which sah: `U` memiliki dua orbit, sedangkan `CyclicShift` satu orbit.
Hasil ini no mengubah verdict inti and no dipaksa menjadi nol.

Kontrol `H_ctrl = U + Uáµ€` memberikan komutator `ZERO` exact, tetapi
**tautologis**: `H_ctrl` adalah polinomial in `U`, jadi komutasinya bukan
bukti independen. Kontrol ini hanya sanity check.

## 4. Verifikasi lokal

```text
python -m msaf.zn_permutation
  verdict: PASS
  receipt sha256: c80b6621fcb1797a0c78f615176dc1400e6210011a084f733092bcb3719bda6c

python -m pytest msaf/tests/test_zn_permutation.py -q
  9 passed

python -m pytest msaf -q
  471 passed (277,32 dtk)

python audit_quantum/freeze.py --verify
  verify OK: 14 pins
  digest f6352884d85bab5a68c01a4e1d4a73618304464fd300d56bce1f8cc2f62baa25

gh run view 39442388960
  conclusion: success
  python-tests 1m1s; coq-kernel 1m57s; lean-kernel 2m16s
```

Receipt deterministik: dua kali `build_receipt()` menghasilkan payload and
hash which sama. Guard menolak tamper entri matriks, charpoly which salah,
minpoly which salah, and memastikan no ada `float`/`numpy`/`arb` in AST
modul inti.

## 5. Batas eksplisit

- Ini sertifikat finite for dua instance mainan `N=15` and `N=21`; bukan
  teorema umum.
- **Bukan** algoritma faktorisasi, bukan pemecahan RSA/ECC, bukan klaim
  keamanan kriptografi, and bukan klaim period-finding which efisien.
- `M` adalah order publik `a mod N`; no ada klaim bahwa spektrum `U`
  mengekstrak rahasia.
- Tidak ada klaim RH, lokasi nol, `Ïƒ = 1/2`, fisika, Lean, Coq, or SMT.
- `PASS` berarti kriteria exact lokal and CI terpenuhi; registry
  `A-2026-0022` mencatat scope ini, bukan klaim umum.

## 6. Artefak

- `msaf/zn_permutation.py`
- `msaf/tests/test_zn_permutation.py` (9 uji)
- `reports/PREREG_ZN_PERMUTATION_2026-10-20.md`
- `reports/zn_permutation_2026-10-20.json`
- report ini

Registry `A-2026-0022` and HANDOFF Â§2.0ap mencatat result ini setelah CI
`39442388960` hijau.


