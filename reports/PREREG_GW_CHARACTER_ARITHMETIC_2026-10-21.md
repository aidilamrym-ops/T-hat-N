# Pra-registrasi: sertifikat aritmetika karakter Dirichlet dan zero struktural — 2026-10-21

**Status:** scope DIKUNCI untuk paket A; implementasi dan eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket A. Hash `sha256LF` berkas ini
dicatat di receipt dan laporan.

**Paket:** Opsi A dari
[`reports/SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md`](SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md),
yaitu sertifikat aritmetika karakter/structural-zero lebih dulu.

**Berkas target:** `msaf/gw_character_arithmetic.py` (baru), guard
`msaf/tests/test_gw_character_arithmetic.py` (baru), laporan
`reports/GW_CHARACTER_ARITHMETIC_2026-10-21.md`, receipt
`reports/gw_character_arithmetic_2026-10-21.json`.

**Dependensi:** Python 3.14 dan `python-flint==0.9.0`
(`dirichlet_char`, `acb`, `arb`). Tidak ada `numpy`/`scipy`, tidak ada
matriks, dan tidak ada eigensolver/LDL^T di jalur inti.

**Registry yang direncanakan:** `A-2026-0025`, hanya bila verdict inti
`PASS` dan integritas PASS.

**Tidak mengubah:** V1–V6 (`A-2026-0015`–`A-2026-0021`), `A-2026-0022`,
`A-2026-0023`, `A-2026-0024`, `ci.yml` (`A-2026-0016`), workflow spec,
`lean/lakefile.toml`, freeze pins, dan seluruh laporan/artefak beku. Tidak
menjalankan ulang kampanye quantum/H1/engine-B.

## 1. Maksud dan batas

Paket ini menguji **lapisan aritmetika** yang menjadi prasyarat jujur untuk
item 1, bukan blok Guinand–Weil. Untuk karakter Dirichlet real non-primitif
dan satu kontrol principal, paket ini:

1. membaca metadata karakter dari FLINT (`conductor`, `is_primitive`,
   `parity`, `order`);
2. mengevaluasi nilai karakter pada integer sebagai nilai exact `0`, `+1`,
   atau `-1`, tanpa float;
3. memverifikasi kriteria zero struktural `chi(n) = 0` **iff**
   `gcd(n, modulus) > 1`;
4. mencari dan memverifikasi **primitive lift** `chi*` modulo konduktor
   `q*`, lalu membandingkan nilai pada unit;
5. mengidentifikasi prime baru `p | q` dengan `p tidak | q*`, tempat
   `chi(p) = 0` tetapi `chi*(p) != 0`;
6. menulis receipt deterministik.

Paket ini **bukan**:

- konstruksi matriks `tau = W02 - WR - Wp`, baik untuk zeta maupun untuk
  karakter;
- klaim bahwa `L(s, chi)` standar dan deret Dirichlet non-primitif
  `sum chi(n) n^{-s}` adalah objek yang sama;
- klaim nol, klaim lokasi nol, klaim `sigma = 1/2`, klaim critical-line
  lock, atau klaim RH/GRH;
- klaim bahwa zero struktural dari koefisien karakter adalah zero dari
  fungsi L;
- klaim faktorisasi, RSA/ECC, Anderson, atau fisika.

## 2. Dua objek yang dibedakan

Untuk karakter non-primitif `chi` modulo `q` dengan induk primitif `chi*`
modulo `q*`:

```text
L(s, chi)             = L(s, chi*)                         (objek standar)
F(s) = sum chi(n)n^-s = L(s, chi*) * prod_{p|q, p tidak |q*} (1 - chi*(p)p^-s)
                                                              (deret Dirichlet)
```

Paket A hanya bekerja pada **koefisien** `chi(n)` dan **tidak** memilih atau
mengklaim salah satu objek analitik di atas. Fakta bahwa `chi(p)=0` untuk
`p | q` adalah fakta aritmetika koefisien; fakta itu tidak mengatakan bahwa
`F` atau `L` mempunyai zero di suatu tempat. Zero tambahan dari faktor Euler
hingga, bila ada, adalah properti objek `F` dan bukan isi paket ini.

## 3. Instance yang dikunci

Lima instance dijalankan dalam paket yang sama. Empat non-primitif adalah
instance utama; satu principal non-primitif adalah kontrol untuk memastikan
bahwa paket tidak mengacaukan "principal" dengan "non-primitif".

| Peran | Karakter | modulus `q` | konduktor `q*` | paritas | order | lift primitif | prime baru |
|---|---|---:|---:|---:|---:|---|---|
| utama | `chi_{12,7}` | 12 | 4 | 1 | 2 | `chi_{4,3}` | 3 |
| utama | `chi_{12,5}` | 12 | 3 | 1 | 2 | `chi_{3,2}` | 2 |
| utama | `chi_{15,4}` | 15 | 5 | 0 | 2 | `chi_{5,4}` | 3 |
| utama | `chi_{15,11}` | 15 | 3 | 1 | 2 | `chi_{3,2}` | 5 |
| kontrol | `chi_{12,1}` | 12 | 1 | 0 | 1 | `chi_{1,1}` | 2, 3 |

`prime baru` berarti prima `p` dengan `p | q` dan `p tidak | q*`. Tabel ini
dikunci sebelum nilai-nilai dihitung; tidak ada instance tambahan setelah
hasil terlihat.

## 4. Cutoff dan tabel exact (C1)

Cutoff dikunci:

```text
C = 200
```

Untuk setiap instance, modul harus:

1. membangun karakter dengan `dirichlet_char(q, number)`;
2. mengevaluasi `chi(n)` untuk semua `1 <= n <= C + q`;
3. menerima hanya nilai yang real exact dan imajiner nol; nilai harus
   tepat `0`, `+1`, atau `-1` (bukan pembulatan);
4. memverifikasi periodisitas `chi(n + q) = chi(n)` untuk `1 <= n <= C`;
5. memverifikasi multiplikativitas `chi(ab) = chi(a) chi(b)` untuk semua
   `1 <= a,b <= C` dengan `gcd(a,b) = 1`;
6. memverifikasi paritas `chi(-1) = (-1)^parity`;
7. memverifikasi order: `chi(n)^order = 1` untuk semua unit `n`, dan
   `order` adalah 1 atau 2.

C1 PASS hanya bila semua butir benar untuk kelima instance.

## 5. Zero struktural (C2)

Untuk setiap `1 <= n <= C`, definisikan:

```text
structural_zero(n) := [chi(n) = 0]
coprime_modulus(n) := [gcd(n, q) = 1]
```

C2 menuntut, untuk setiap instance:

```text
chi(n) = 0  iff  gcd(n, q) > 1.
```

Selain itu, untuk tabel prime power `q_k = p^a <= C`, catat nilai
`chi(q_k)`, `gcd(q_k, q)`, dan `gcd(q_k, q*)`. Tabel ini harus konsisten
dengan kriteria di atas. Yang lenyap adalah **suku koefisien** `chi(q_k)`,
bukan entri matriks mana pun.

C2 PASS hanya bila ekuivalensi berlaku untuk semua `n` di rentang yang
dikunci dan tabel prime power konsisten.

## 6. Primitive lift dan aktivasi prime baru (C3)

Untuk setiap instance non-primitif:

1. `conductor` yang dilaporkan FLINT harus sama dengan `q*` di tabel §3;
2. lift `chi*` harus primitif modulo `q*` dan metadata paritas/order-nya
   harus sama dengan `chi`;
3. untuk semua `1 <= a <= C` dengan `gcd(a, q) = 1`, harus berlaku
   `chi(a) = chi*(a)`;
4. untuk semua `1 <= n <= C`, harus berlaku
   `chi*(n) = 0 iff gcd(n, q*) > 1`;
5. tidak boleh ada modulus `d | q` dengan `d < q*` dan karakter modulo `d`
   yang nilainya sama dengan `chi` pada semua unit modulo `q`;
6. himpunan aktivasi

   ```text
   A = { n <= C : gcd(n,q) > 1 and gcd(n,q*) = 1 }
   ```

   harus tidak kosong untuk setiap instance non-primitif, dan untuk setiap
   `n in A` harus berlaku `chi(n) = 0` serta `chi*(n) != 0`.

Untuk kontrol principal `chi_{12,1}`, butir 1–5 tetap diuji; butir 6 harus
menghasilkan aktivasi dari prime 2 dan 3, dengan `chi*(n)=1` untuk lift
trivial.

C3 PASS hanya bila semua butir benar.

## 7. Determinisme dan receipt (C4)

Receipt deterministik harus memuat:

- `schema`, `cutoff`, dan hash `sha256LF` pra-registrasi ini;
- untuk setiap instance: modulus, number, konduktor, status primitif,
  paritas, order, identifier lift, prime baru;
- hash tabel nilai exact, jumlah zero struktural, jumlah aktivasi;
- tabel prime power terpilih (nilai, gcd modulus, gcd konduktor, status
  zero/aktivasi);
- daftar ringkas aktivasi prime baru;
- hasil setiap check C1–C3;
- `scope` dengan flag matrix/zero/critical-line semuanya `false`;
- verdict.

C4 PASS bila dua build receipt berturut-turut menghasilkan payload kanonik
identik dan receipt di disk cocok dengan hasil hitung ulang.

## 8. Verdict

- **PASS:** C1, C2, C3, C4 PASS untuk kelima instance.
- **FAILED:** salah satu check exact gagal, metadata tidak cocok, lift tidak
  ditemukan/tidak tunggal, atau determinisme/hash rusak.
- **TOOL NOT RUN:** `python-flint`/`dirichlet_char` tidak tersedia.

Tidak ada kategori `PARTIAL` untuk paket ini karena semua keputusan bersifat
exact integer/character-table; angka floating-point tidak dipakai. `PASS`
berarti **aritmetika karakter dan zero struktural koefisien** lolos kriteria,
bukan klaim analitik tentang `L(s, chi)` atau `F(s)`.

## 9. Falsifier

Paket ini falsified bila salah satu dari berikut muncul:

- ada nilai karakter yang bukan exact `0`, `+1`, atau `-1`;
- periodisitas atau multiplikativitas gagal;
- `chi(n) = 0` tidak ekuivalen dengan `gcd(n,q) > 1`;
- primitive lift tidak ditemukan, tidak tunggal, atau tidak cocok pada unit;
- ada modulus lebih kecil yang karakternya cocok pada semua unit;
- tidak ada aktivasi prime baru untuk instance non-primitif;
- receipt tidak deterministik atau hash tidak cocok.

Falsifier dicatat sebagai `FAILED`; tidak ada perubahan cutoff, instance,
atau definisi setelah hasil terlihat.

## 10. Artefak dan urutan eksekusi

1. Tulis dan hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/gw_character_arithmetic.py` dengan konfigurasi penuh.
3. Guard `msaf/tests/test_gw_character_arithmetic.py`: uji metadata, nilai
   exact, zero struktural, primitive lift, minimalitas konduktor, aktivasi,
   determinisme receipt, dan tamper hash.
4. Jalankan kampanye penuh sekali; hasilkan receipt.
5. Tulis laporan `reports/GW_CHARACTER_ARITHMETIC_2026-10-21.md` dengan
   angka verbatim, verdict, runtime, dan hash.
6. Bila verdict `PASS` dan integritas PASS: registry `A-2026-0025`,
   HANDOFF §2.0as, sertifikat sha256LF.
7. Suite penuh dan `freeze.py --verify`; commit/push hanya bila diminta.

## 11. Batas eksplisit

- Hanya lima instance dan cutoff `C=200`; tidak ada ekstrapolasi.
- Hanya karakter real (order `<= 2`); karakter kompleks tidak diuji.
- Tidak ada matriks Guinand–Weil, tidak ada `W02`/`WR`/`Wp`, tidak ada
  inertia, dan tidak ada eigensolver.
- Tidak ada klaim nol, `sigma=1/2`, critical-line lock, RH/GRH, faktorisasi,
  RSA/ECC, Anderson, atau fisika.
- Tidak ada kampanye tersegel yang dijalankan ulang.
- `PASS` adalah verdict finite untuk tabel aritmetika yang dikunci, bukan
  peer review atau klaim eksternal.
