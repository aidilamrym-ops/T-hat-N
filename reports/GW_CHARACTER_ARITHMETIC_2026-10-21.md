# Sertifikat aritmetika karakter Dirichlet dan zero struktural — 2026-10-21

**Status:** `PASS` (verifikasi lokal; belum di-commit/di-push).
**Paket:** Opsi A dari
[`reports/SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md`](SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md).
**Pra-registrasi:**
[`reports/PREREG_GW_CHARACTER_ARITHMETIC_2026-10-21.md`](PREREG_GW_CHARACTER_ARITHMETIC_2026-10-21.md)
(`sha256LF 526b731b89b5351192c959c84034da6860dd85e8841caa0a1fdc41b5f1cb7074`).

## 1. Ringkasan hasil

Paket finite ini memverifikasi **aritmetika koefisien** lima karakter
Dirichlet real pada cutoff `C=200`. Empat instance non-primitif dan satu
kontrol principal semuanya memberi verdict **`PASS`**:

- metadata `conductor`, `is_primitive`, `parity`, dan `order` cocok dengan
  tabel yang dikunci;
- setiap nilai karakter yang dievaluasi adalah exact `0`, `+1`, atau `-1`;
- periodisitas dan multiplikativitas berlaku pada rentang yang dikunci;
- `chi(n) = 0` **iff** `gcd(n, modulus) > 1` untuk semua `1 <= n <= 200`;
- primitive lift ditemukan tunggal, primitif, dan cocok pada semua unit;
- tidak ada modulus proper yang karakternya cocok pada semua unit;
- prime baru `p | q`, `p tidak | q*` menghasilkan aktivasi
  `chi(p^a) = 0` sementara `chi*(p^a) != 0`;
- receipt deterministik dan hash kanonik cocok.

Verdict ini adalah sertifikat **tabel aritmetika**. Ia tidak membangun
matriks Guinand–Weil, tidak mengevaluasi `L(s, chi)`, dan tidak mengklaim
nol, `sigma = 1/2`, atau critical-line lock.

## 2. Dua objek yang dibedakan

Untuk karakter non-primitif `chi` modulo `q` dengan induk primitif `chi*`
modulo `q*`:

```text
L(s, chi)             = L(s, chi*)                          (L standar)
F(s) = sum chi(n)n^-s = L(s, chi*) * prod_{p|q, p tidak |q*} (1 - chi*(p)p^-s)
                                                               (deret Dirichlet)
```

Paket A hanya menguji koefisien `chi(n)`. Fakta `chi(p)=0` untuk `p | q`
adalah fakta aritmetika koefisien; itu bukan zero dari `L(s,chi)` dan bukan
zero dari `F(s)`. Tidak ada objek analitik yang dipilih atau diklaim di
sini.

## 3. Instance yang dikunci

| Peran | Karakter | `q` | `q*` | paritas | order | lift | prime baru | unit | zero `n<=200` | aktivasi |
|---|---|---:|---:|---:|---:|---|---|---:|---:|---:|
| utama | `chi_{12,7}` | 12 | 4 | 1 | 2 | `chi_{4,3}` | 3 | 4 | 133 | 33 |
| utama | `chi_{12,5}` | 12 | 3 | 1 | 2 | `chi_{3,2}` | 2 | 4 | 133 | 67 |
| utama | `chi_{15,4}` | 15 | 5 | 0 | 2 | `chi_{5,4}` | 3 | 8 | 93 | 53 |
| utama | `chi_{15,11}` | 15 | 3 | 1 | 2 | `chi_{3,2}` | 5 | 8 | 93 | 27 |
| kontrol | `chi_{12,1}` | 12 | 1 | 0 | 1 | `chi_{1,1}` | 2, 3 | 4 | 133 | 133 |

`unit` adalah jumlah unit modulo `q` yang diperiksa. `zero` adalah jumlah
`n` dengan `chi(n)=0`. `aktivasi` adalah jumlah `n <= 200` dengan
`gcd(n,q)>1` dan `gcd(n,q*)=1`; untuk semua `n` itu, `chi(n)=0` dan
`chi*(n) != 0`.

## 4. Pemeriksaan exact

Semua pemeriksaan berikut bernilai `true` untuk kelima instance:

| Check | Isi |
|---|---|
| `C1_metadata` | konduktor, status primitif, paritas, order, dan lift cocok |
| `C1_periodic` | `chi(n+q)=chi(n)` untuk `1 <= n <= 200` |
| `C1_multiplicative` | `chi(ab)=chi(a)chi(b)` untuk `gcd(a,b)=1`, `a,b <= 200` |
| `C1_parity` | `chi(-1)=(-1)^parity` |
| `C1_order` | `chi(n)^order=1` pada unit; order 1/2 konsisten |
| `C2_structural_zero` | `chi(n)=0` iff `gcd(n,q)>1` untuk `1 <= n <= 200` |
| `C2_prime_power_table` | tabel `p^a <= 200` konsisten dengan kriteria gcd |
| `C3_lift_metadata` | `chi*` primitif, konduktor `q*`, paritas/order sama |
| `C3_lift_agreement` | `chi(a)=chi*(a)` untuk semua unit `a <= 200` |
| `C3_lift_zero` | `chi*(n)=0` iff `gcd(n,q*)>1` |
| `C3_minimality` | tidak ada modulus proper `d | q` yang cocok pada semua unit |
| `C3_activation` | prime baru aktif; `chi=0`, `chi* != 0` |

Contoh nilai dan aktivasi:

```text
chi_{12,7}:   chi(2)=0, chi(3)=0, chi(5)=1, chi(7)=-1
              chi_{4,3}(3)=-1, chi_{4,3}(9)=1
chi_{12,5}:   chi(2)=0, chi(3)=0, chi(5)=-1, chi(7)=1
              chi_{3,2}(2)=-1, chi_{3,2}(4)=1
chi_{15,4}:   chi(2)=-1, chi(3)=0, chi(5)=0, chi(7)=-1
              chi_{5,4}(3)=-1, chi_{5,4}(6)=1
chi_{15,11}:  chi(2)=-1, chi(3)=0, chi(5)=0, chi(11)=-1
              chi_{3,2}(5)=-1, chi_{3,2}(10)=1
chi_{12,1}:   chi(2)=0, chi(3)=0, chi(5)=1
              chi_{1,1}(2)=1, chi_{1,1}(3)=1
```

## 5. Hash tabel

| Karakter | Hash tabel nilai `1..200` | Hash tabel prime power |
|---|---|---|
| `chi_{12,7}` | `f0e23d1be9ed55120a095cf2f43f58e621f0728ef778732d70576d51660d688f` | `43eae80f81f4376f1065e3da65a469554bc774aba668b3c2e5066c81772f6008` |
| `chi_{12,5}` | `e190df42e564d161de08950dbb10e0bf53a6272c84cb2ab49c63b54325307c47` | `4fc212ce7ae0c53046b3268e16d74184697cf8083a08ae06583a82cb995cb2d5` |
| `chi_{15,4}` | `a70f405a39e74ef29dc46322ce8673a53e021f58c223ed231dc63810c7ab89b5` | `2002a45ccdecac13c5d1eae3e97814ebb3a32307e119373a6646ea3e7d46636e` |
| `chi_{15,11}` | `f0f9753fa9997617e5daaa4fb8fc07c3c37f4a755e15668146f51c5a2b21c314` | `b4451a0c7f312b4a27d6f292d1c51783c4c535d054a14fb9941760e8470da5c3` |
| `chi_{12,1}` | `062d62fc2ba0e6753ead94b329efc0d37b5763113d87bc9cf41400b027145e99` | `3f86eafafc37e1546c1efd6571153a928b4b378335c089dff8d1c6679464dd93` |

Hash tabel adalah SHA-256 dari baris kanonik
`n|chi(n)|chi*(n)|gcd(n,q)|gcd(n,q*)`, dan hash prime power dari
`q_k|p|a|chi(q_k)|chi*(q_k)|gcd(q_k,q)|gcd(q_k,q*)`.

## 6. Verdict dan receipt

| Kriteria | Hasil |
|---|---|
| C1 aritmetika dasar | PASS untuk 5/5 instance |
| C2 zero struktural | PASS untuk 5/5 instance |
| C3 primitive lift/minimalitas/aktivasi | PASS untuk 5/5 instance |
| C4 determinisme receipt | PASS (dua build identik) |
| **Total** | **PASS** |

Receipt kanonik:

```text
verdict          PASS
canonical sha256 cfd966c5795d3e0b7e0009ee89f80e9b26592745e0a6b0c08f430b24d4473eb2
file sha256LF    bf52cc5c69db44d536c2ace411bfb86a973b0a32ac5823f93a07d74052cbfbf3
prereg sha256LF  526b731b89b5351192c959c84034da6860dd85e8841caa0a1fdc41b5f1cb7074
```

## 7. Yang disertifikasi dan yang tidak

Yang benar-benar disertifikasi:

1. Lima tabel karakter real exact pada `1 <= n <= 200`.
2. Kriteria zero struktural `chi(n)=0` iff `gcd(n,q)>1`.
3. Primitive lift tunggal dan cocok pada semua unit.
4. Minimalitas konduktor terhadap seluruh modulus proper.
5. Aktivasi prime baru: koefisien nol, lift primitif nonzero.
6. Receipt deterministik dan fail-closed.

Yang **tidak** diklaim:

- bahwa `L(s,chi)` standar dan deret Dirichlet non-primitif adalah objek
  yang sama;
- bahwa zero koefisien `chi(p)=0` adalah zero fungsi L atau deret `F`;
- lokasi nol, `sigma = 1/2`, critical-line lock, RH/GRH;
- konstruksi atau inertia matriks `W02 - WR - Wp`;
- bahwa paket ini adalah blok Guinand–Weil berkarakter;
- faktorisasi, RSA/ECC, Anderson, atau fisika.

## 8. Artefak dan verifikasi

- Modul: `msaf/gw_character_arithmetic.py` —
  `sha256LF 4047537e3e4557f91feca05a34aa03cbbbc0e3a6d5f4317c7aaf5d5aefbbd68f`
- Guard: `msaf/tests/test_gw_character_arithmetic.py` —
  `sha256LF 9c0e4205db7c46c202a4ebe0d94860f1a4ef9e4ca558748d5a1500bcdfc07bd2`
- Pra-registrasi:
  `sha256LF 526b731b89b5351192c959c84034da6860dd85e8841caa0a1fdc41b5f1cb7074`
- Receipt:
  `sha256LF bf52cc5c69db44d536c2ace411bfb86a973b0a32ac5823f93a07d74052cbfbf3`
- Runtime kampanye lokal: **0,65 s**.
- Guard baru: **12 tests**, lulus **1,15 s**.

Perintah reproduksi:

```bash
python -m msaf.gw_character_arithmetic --out reports/gw_character_arithmetic_2026-10-21.json
python -m pytest msaf/tests/test_gw_character_arithmetic.py -q
python -m pytest msaf -q
python audit_quantum/freeze.py --verify
```

## 9. Hubungan dengan opsi B dan C

Opsi A sengaja berhenti di aritmetika. Opsi B akan memakai `Wp` dengan
nilai karakter ini pada blok zeta lama dan harus diberi label
`AD HOC PERTURBATION`; opsi C membutuhkan derivasi ulang blok archimedean
dan pole untuk karakter. Tidak ada hasil A yang boleh dipakai untuk
menaikkan verdict B atau C secara otomatis.

## 10. Batas penutup

`PASS` di sini berarti **lima tabel aritmetika karakter yang dikunci lolos
C1–C4**. Ia bukan peer review, bukan sertifikat analitik, bukan klaim nol,
dan bukan klaim critical-line. Tidak ada kampanye tersegel yang dijalankan
ulang, dan tidak ada artefak beku yang diubah.
