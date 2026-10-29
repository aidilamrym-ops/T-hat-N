# Pra-registrasi: sertifikat aritmetika karakter Dirichlet and zero struktural â€” 2026-10-21

**Status:** scope DIKUNCI for paket A; implementasi and eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket A. Hash `sha256LF` file ini
dicatat in receipt and report.

**Paket:** Opsi A dari
[`reports/SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md`](SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md),
yaitu sertifikat aritmetika karakter/structural-zero lebih dulu.

**Berkas target:** `msaf/gw_character_arithmetic.py` (baru), guard
`msaf/tests/test_gw_character_arithmetic.py` (baru), report
`reports/GW_CHARACTER_ARITHMETIC_2026-10-21.md`, receipt
`reports/gw_character_arithmetic_2026-10-21.json`.

**Dependensi:** Python 3.14 and `python-flint==0.9.0`
(`dirichlet_char`, `acb`, `arb`). Tidak ada `numpy`/`scipy`, no ada
matriks, and no ada eigensolver/LDL^T in jalur inti.

**Registry which direncanakan:** `A-2026-0025`, hanya bila verdict inti
`PASS` and integritas PASS.

**Tidak mengubah:** V1â€“V6 (`A-2026-0015`â€“`A-2026-0021`), `A-2026-0022`,
`A-2026-0023`, `A-2026-0024`, `ci.yml` (`A-2026-0016`), workflow spec,
`lean/lakefile.toml`, freeze pins, and seluruh report/artefak beku. Tidak
menjalankan ulang kampanye quantum/H1/engine-B.

## 1. Maksud and limit

Paket ini menguji **lapisan aritmetika** which menjadi prasyarat jujur for
item 1, bukan blok Guinandâ€“Weil. Untuk karakter Dirichlet real non-primitif
and satu kontrol principal, paket ini:

1. membaca metadata karakter dari FLINT (`conductor`, `is_primitive`,
   `parity`, `order`);
2. mengevaluasi nilai karakter on integer sebagai nilai exact `0`, `+1`,
   or `-1`, tanpa float;
3. verifying kriteria zero struktural `chi(n) = 0` **iff**
   `gcd(n, modulus) > 1`;
4. mencari and verifying **primitive lift** `chi*` modulo konduktor
   `q*`, lalu membandingkan nilai on unit;
5. mengidentifikasi prime baru `p | q` with `p no | q*`, tempat
   `chi(p) = 0` tetapi `chi*(p) != 0`;
6. menulis receipt deterministik.

Paket ini **bukan**:

- konstruksi matriks `tau = W02 - WR - Wp`, baik for zeta maupun for
  karakter;
- klaim bahwa `L(s, chi)` standar and deret Dirichlet non-primitif
  `sum chi(n) n^{-s}` adalah objek which sama;
- klaim nol, klaim lokasi nol, klaim `sigma = 1/2`, klaim critical-line
  lock, or klaim RH/GRH;
- klaim bahwa zero struktural dari koefisien karakter adalah zero dari
  fungsi L;
- klaim faktorisasi, RSA/ECC, Anderson, or fisika.

## 2. Dua objek which dibedakan

Untuk karakter non-primitif `chi` modulo `q` with induk primitif `chi*`
modulo `q*`:

```text
L(s, chi)             = L(s, chi*)                         (objek standar)
F(s) = sum chi(n)n^-s = L(s, chi*) * prod_{p|q, p no |q*} (1 - chi*(p)p^-s)
                                                              (deret Dirichlet)
```

Paket A hanya bekerja on **koefisien** `chi(n)` and **no** memilih or
mengklaim salah satu objek analitik in atas. Fakta bahwa `chi(p)=0` for
`p | q` adalah fakta aritmetika koefisien; fakta itu no mengatakan bahwa
`F` or `L` mempunyai zero in suatu tempat. Zero tambahan dari faktor Euler
hingga, bila ada, adalah properti objek `F` and bukan isi paket ini.

## 3. Instance which dikunci

Lima instance dijalankan dalam paket which sama. Empat non-primitif adalah
instance utama; satu principal non-primitif adalah kontrol for memastikan
bahwa paket no mengacaukan "principal" with "non-primitif".

| Peran | Karakter | modulus `q` | konduktor `q*` | paritas | order | lift primitif | prime baru |
|---|---|---:|---:|---:|---:|---|---|
| utama | `chi_{12,7}` | 12 | 4 | 1 | 2 | `chi_{4,3}` | 3 |
| utama | `chi_{12,5}` | 12 | 3 | 1 | 2 | `chi_{3,2}` | 2 |
| utama | `chi_{15,4}` | 15 | 5 | 0 | 2 | `chi_{5,4}` | 3 |
| utama | `chi_{15,11}` | 15 | 3 | 1 | 2 | `chi_{3,2}` | 5 |
| kontrol | `chi_{12,1}` | 12 | 1 | 0 | 1 | `chi_{1,1}` | 2, 3 |

`prime baru` berarti prima `p` with `p | q` and `p no | q*`. Tabel ini
dikunci sebelum nilai-nilai dihitung; no ada instance tambahan setelah
result terlihat.

## 4. Cutoff and tabel exact (C1)

Cutoff dikunci:

```text
C = 200
```

Untuk setiap instance, modul harus:

1. membangun karakter with `dirichlet_char(q, number)`;
2. mengevaluasi `chi(n)` for semua `1 <= n <= C + q`;
3. menerima hanya nilai which real exact and imajiner nol; nilai harus
   tepat `0`, `+1`, or `-1` (bukan pembulatan);
4. verifying periodisitas `chi(n + q) = chi(n)` for `1 <= n <= C`;
5. verifying multiplikativitas `chi(ab) = chi(a) chi(b)` for semua
   `1 <= a,b <= C` with `gcd(a,b) = 1`;
6. verifying paritas `chi(-1) = (-1)^parity`;
7. verifying order: `chi(n)^order = 1` for semua unit `n`, and
   `order` adalah 1 or 2.

C1 PASS hanya bila semua butir benar for kelima instance.

## 5. Zero struktural (C2)

Untuk setiap `1 <= n <= C`, definisikan:

```text
structural_zero(n) := [chi(n) = 0]
coprime_modulus(n) := [gcd(n, q) = 1]
```

C2 menuntut, for setiap instance:

```text
chi(n) = 0  iff  gcd(n, q) > 1.
```

Selain itu, for tabel prime power `q_k = p^a <= C`, catat nilai
`chi(q_k)`, `gcd(q_k, q)`, and `gcd(q_k, q*)`. Tabel ini harus konsisten
with kriteria in atas. Yang lenyap adalah **suku koefisien** `chi(q_k)`,
bukan entri matriks mana pun.

C2 PASS hanya bila ekuivalensi berlaku for semua `n` in rentang which
dikunci and tabel prime power konsisten.

## 6. Primitive lift and aktivasi prime baru (C3)

Untuk setiap instance non-primitif:

1. `conductor` which dilaporkan FLINT harus sama with `q*` in tabel Â§3;
2. lift `chi*` harus primitif modulo `q*` and metadata paritas/order-nya
   harus sama with `chi`;
3. for semua `1 <= a <= C` with `gcd(a, q) = 1`, harus berlaku
   `chi(a) = chi*(a)`;
4. for semua `1 <= n <= C`, harus berlaku
   `chi*(n) = 0 iff gcd(n, q*) > 1`;
5. no boleh ada modulus `d | q` with `d < q*` and karakter modulo `d`
   which nilainya sama with `chi` on semua unit modulo `q`;
6. himpunan aktivasi

   ```text
   A = { n <= C : gcd(n,q) > 1 and gcd(n,q*) = 1 }
   ```

   harus no kosong for setiap instance non-primitif, and for setiap
   `n in A` harus berlaku `chi(n) = 0` serta `chi*(n) != 0`.

Untuk kontrol principal `chi_{12,1}`, butir 1â€“5 tetap diuji; butir 6 harus
menghasilkan aktivasi dari prime 2 and 3, with `chi*(n)=1` for lift
trivial.

C3 PASS hanya bila semua butir benar.

## 7. Determinisme and receipt (C4)

Receipt deterministik harus memuat:

- `schema`, `cutoff`, and hash `sha256LF` pra-registrasi ini;
- for setiap instance: modulus, number, konduktor, status primitif,
  paritas, order, identifier lift, prime baru;
- hash tabel nilai exact, jumlah zero struktural, jumlah aktivasi;
- tabel prime power terpilih (nilai, gcd modulus, gcd konduktor, status
  zero/aktivasi);
- daftar ringkas aktivasi prime baru;
- result setiap check C1â€“C3;
- `scope` with flag matrix/zero/critical-line semuanya `false`;
- verdict.

C4 PASS bila dua build receipt berturut-turut menghasilkan payload kanonik
identik and receipt in disk cocok with result hitung ulang.

## 8. Verdict

- **PASS:** C1, C2, C3, C4 PASS for kelima instance.
- **FAILED:** salah satu check exact gagal, metadata no cocok, lift no
  ditemukan/no tunggal, or determinisme/hash rusak.
- **TOOL NOT RUN:** `python-flint`/`dirichlet_char` no tersedia.

Tidak ada kategori `PARTIAL` for paket ini karena semua keputusan bersifat
exact integer/character-table; angka floating-point no dipakai. `PASS`
berarti **aritmetika karakter and zero struktural koefisien** lolos kriteria,
bukan klaim analitik tentang `L(s, chi)` or `F(s)`.

## 9. Falsifier

Paket ini falsified bila salah satu dari berikut muncul:

- ada nilai karakter which bukan exact `0`, `+1`, or `-1`;
- periodisitas or multiplikativitas gagal;
- `chi(n) = 0` no ekuivalen with `gcd(n,q) > 1`;
- primitive lift no ditemukan, no tunggal, or no cocok on unit;
- ada modulus lebih kecil which karakternya cocok on semua unit;
- no ada aktivasi prime baru for instance non-primitif;
- receipt no deterministik or hash no cocok.

Falsifier dicatat sebagai `FAILED`; no ada perubahan cutoff, instance,
or definisi setelah result terlihat.

## 10. Artefak and urutan eksekusi

1. Tulis and hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/gw_character_arithmetic.py` with konfigurasi penuh.
3. Guard `msaf/tests/test_gw_character_arithmetic.py`: uji metadata, nilai
   exact, zero struktural, primitive lift, minimalitas konduktor, aktivasi,
   determinisme receipt, and tamper hash.
4. Jalankan kampanye penuh sekali; hasilkan receipt.
5. Tulis report `reports/GW_CHARACTER_ARITHMETIC_2026-10-21.md` with
   angka verbatim, verdict, runtime, and hash.
6. Bila verdict `PASS` and integritas PASS: registry `A-2026-0025`,
   HANDOFF Â§2.0as, sertifikat sha256LF.
7. Suite penuh and `freeze.py --verify`; commit/push hanya bila diminta.

## 11. Batas eksplisit

- Hanya lima instance and cutoff `C=200`; no ada ekstrapolasi.
- Hanya karakter real (order `<= 2`); karakter kompleks no diuji.
- Tidak ada matriks Guinandâ€“Weil, no ada `W02`/`WR`/`Wp`, no ada
  inertia, and no ada eigensolver.
- Tidak ada klaim nol, `sigma=1/2`, critical-line lock, RH/GRH, faktorisasi,
  RSA/ECC, Anderson, or fisika.
- Tidak ada kampanye tersegel which dijalankan ulang.
- `PASS` adalah verdict finite for tabel aritmetika which dikunci, bukan
  peer review or klaim eksternal.


