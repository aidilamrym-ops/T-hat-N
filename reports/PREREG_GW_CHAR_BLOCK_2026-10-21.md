# Pra-registrasi: blok Guinand–Weil berkarakter — derivasi kandidat dan batas validasi — 2026-10-21

**Status:** scope DIKUNCI untuk paket C; implementasi dan eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket C. Hash `sha256LF` berkas ini
dicatat di receipt dan laporan.

**Paket:** Opsi C dari
[`reports/SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md`](SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md),
yaitu derivasi blok pole/archimedean yang benar untuk karakter, dengan
validasi independen bila memungkinkan.

**Berkas target:** `msaf/gw_char_block.py` (baru), guard
`msaf/tests/test_gw_char_block.py` (baru), laporan
`reports/GW_CHAR_BLOCK_2026-10-21.md`, receipt
`reports/gw_char_block_2026-10-21.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0`, modul B
`msaf/gw_char_adhoc.py` untuk builder zeta/Wp/inertia, dan modul A
`msaf/gw_character_arithmetic.py` untuk karakter exact. Tidak ada
`numpy`/`scipy` dan tidak ada perubahan pada modul eksternal.

**Registry:** **tidak ada** entri registry untuk paket C pada fase ini.
Registry hanya boleh ditulis bila derivasi, validasi independen, dan blok
pole principal semuanya ditutup. Sebelum itu, verdict harus
`INCONCLUSIVE`/`NOT READY` dan tidak boleh dipromosikan menjadi `PASS`.

**Tidak mengubah:** V1–V6 (`A-2026-0015`–`A-2026-0021`),
`A-2026-0022`–`A-2026-0026`, `ci.yml` (`A-2026-0016`), workflow spec,
`lean/lakefile.toml`, freeze pins, seluruh laporan/artefak beku, dan
`source_arb_ldlt_certify.py`. Tidak menjalankan ulang kampanye
quantum/H1/engine-B.

## 1. Maksud dan batas

Blueprint item 1 meminta matriks `W02 - WR - Wp` untuk karakter
non-primitif. Audit A–B menunjukkan bahwa mengganti `Wp` saja tidak cukup.
Paket C mencoba menurunkan blok yang benar untuk **L(s, chi) standar**:

```text
Lambda(s, chi) = (q*/pi)^((s+a)/2) Gamma((s+a)/2) L(s, chi)
```

dengan `chi` primitif modulo `q*`, paritas `a in {0,1}`, dan `L(s,chi)`
non-principal sehingga **tidak ada pole**. Untuk karakter non-primitif,
L(s,chi) = L(s,chi*) dan blok standar harus memakai `q*` dan nilai `chi*`,
bukan modulus `q` atau zero koefisien `chi`.

Kandidat blok yang diuji:

```text
h_chi(r) = Re psi((1+2a)/4 + i r/2) + log q* - log pi
W02_chi  = 0                                  (non-principal)
WR_chi   = blok archimedean dari h_chi
Wp_chi   = sum_{q_k=p^b<=c} log(p) q_k^(-1/2) chi(q_k) shape(q_k)
tau_chi  = W02_chi - WR_chi - Wp_chi = -WR_chi - Wp_chi
```

Untuk mereduksi ke zeta, `q*=1`, `a=0`, dan `chi` trivial harus memberi
`h_chi = h_+`, sehingga `WR_chi` harus sama dengan `WR_zeta` dalam ball.
Ini adalah kontrol implementasi, bukan bukti kebenaran penuh.

Paket C **tidak** mengklaim:

- bahwa kandidat blok sudah tervalidasi secara independen untuk semua
  `q*`/paritas;
- blok pole untuk karakter principal (belum diimplementasikan);
- klaim nol, lokasi nol, `sigma = 1/2`, critical-line lock, RH/GRH;
- positivity `L(s,chi)` atau Weil positivity;
- faktorisasi, RSA/ECC, Anderson, atau fisika.

## 2. Derivasi kandidat

Dengan `alpha = (1+2a)/4`, sumber archimedean adalah

```text
psi_R(x) = (1/(2 pi^2)) ∫ h_chi(r) S(r,x,L) dr
S(r,x,L) = ∫_0^L sin(2 pi x (1-y/L)) cos(r y) dy
```

Untuk `x=n` integer, bentuk tertutup zeta digeneralisasi dengan:

```text
c_k = 2k + 2 alpha
gS  = sum_k e^{-c_k L} / (c_k^2 + w^2)
gCC = sum_k e^{-c_k L} w^2 / (c_k (c_k^2+w^2))      (n != 0)
gX1 = sum_k e^{-c_k L} c_k / (c_k^2+w^2)
gX2 = sum_k e^{-c_k L} (c_k^2-w^2) / (c_k^2+w^2)^2
w   = 2 pi n / L
S(n)  = (1/2) Im psi(alpha + i pi n/L) - w gS
CC(n) = -(1/2)(Re psi(alpha + i pi n/L) - psi(alpha)) + gCC
XC(n) = (1/4) Re psi'(alpha + i pi n/L) - L gX1 - gX2
```

Diagonal dan off-diagonal:

```text
WR(n,n) = kappa_chi + 2 CC(n) + J - (2/L) XC(n)
WR(m,n) = (S_signed(m) - S_signed(n)) / (pi (n-m)),  m != n
kappa_chi = kappa_zeta + log q*
```

`J` dan `kappa_zeta` tetap dari test function zeta. Konstanta `log q*`
menambah diagonal karena konstanta pada `h_chi` menambah `psi_R'(n)` sebesar
konstanta itu dan tidak mengubah beda terbagi off-diagonal. Ini adalah
bagian derivasi yang harus divalidasi, bukan diasumsikan.

## 3. Konfigurasi dan karakter yang dikunci

Konfigurasi:

| Peran | `c` | `N` | `dim=2N+1` | `prec` |
|---|---:|---:|---:|---:|
| Primer | 100 | 20 | 41 | 600 bit |
| Replikasi | 200 | 20 | 41 | 600 bit |

Karakter primitif non-principal yang dikunci:

| Karakter | `q*` | paritas `a` | `alpha` |
|---|---:|---:|---:|
| `chi_{4,3}` | 4 | 1 | 3/4 |
| `chi_{3,2}` | 3 | 1 | 3/4 |
| `chi_{5,4}` | 5 | 0 | 1/4 |

Untuk uji non-primitif, empat parent dari paket B dipetakan ke lift-nya:
`chi_{12,7}->chi_{4,3}`, `chi_{12,5}->chi_{3,2}`,
`chi_{15,4}->chi_{5,4}`, `chi_{15,11}->chi_{3,2}`. Blok **standar**
memakai lift primitif; blok **deret Dirichlet** memakai nilai parent
(nol di prime baru) tetapi tetap `q*` dan `alpha` yang sama. Kedua objek
harus dibedakan dan tidak boleh disebut sama.

## 4. Pemeriksaan (C1–C4)

**C1: reduksi zeta.** Untuk `q*=1`, `a=0`, `c=13,N=4,prec=200`, blok
`WR_chi` harus sama dengan `WR_zeta` dari builder B dalam ball; selisih
entrywise harus di bawah ambang `2^{-(prec-32)}`.

**C2: finite dan struktur.** Semua entri `WR_chi`, `Wp_chi`, `tau_chi`
harus finite; `Wp_chi(q_k)=0` tepat ketika `gcd(q_k,q*)>1`; untuk blok
standar, nilai prime power memakai `chi*`; untuk blok deret, memakai
`chi` dan berbeda pada prime baru.

**C3: inertia eksploratif.** Hitung interval LDL^T untuk setiap blok
standar dan deret pada dua konfigurasi. Inertia adalah pernyataan tanda
matriks finite; tidak ada eigenvalue, magnitude, atau klaim nol. Bila ada
pivot undetermined, catat `INCONCLUSIVE`.

**C4: pemisahan objek.** Untuk setiap parent non-primitif, blok standar
dan blok deret harus dibandingkan; selisih `Wp` harus tidak nol pada
prime baru, dan statusnya dicatat terpisah. Tidak boleh ada klaim bahwa
keduanya adalah L-function yang sama.

## 5. Validasi independen dan verdict

Validasi yang benar-benar independen untuk `alpha=3/4` dan `log q*` belum
tersedia dalam paket ini. Reduksi `q*=1, alpha=1/4` hanya menguji jalur
implementasi; ia tidak memvalidasi pergeseran paritas, konduktor, atau
blok pole principal. Karena itu:

- `execution_status` boleh `PASS` bila C1–C4 berjalan dan finite;
- `certification_status` tetap **`INCONCLUSIVE`**;
- `verdict` tetap **`INCONCLUSIVE`** / **`NOT READY`**;
- tidak ada registry entry;
- angka inertia hanya dilaporkan sebagai **eksploratif**.

Paket C baru boleh menjadi `PASS` bila (i) blok `alpha=3/4` dan `log q*`
divalidasi independen (mis. quadrature/sumber eksplisit atau pencocokan
nol), (ii) blok pole principal diturunkan dan diuji, dan (iii) guard
menolak promosi tanpa kedua hal itu. Kondisi ini **tidak** dipenuhi pada
fase ini.

## 6. Falsifier

- Reduksi zeta `q*=1` gagal di luar ball → `FAILED`.
- Ada entri non-finite atau `Wp` salah zero → `FAILED`.
- Blok standar dan deret tidak berbeda pada prime baru → `FAILED`.
- Inertia undetermined → `INCONCLUSIVE` untuk run itu.
- Klaim `PASS`, registry, atau klaim nol/critical-line tanpa validasi
  independen dan blok principal → pelanggaran scope.

## 7. Artefak dan urutan eksekusi

1. Tulis dan hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/gw_char_block.py` dengan kandidat, kontrol q*=1, dan
   pemisahan standar/deret.
3. Guard `msaf/tests/test_gw_char_block.py`: uji reduksi, finite, inertia,
   pemisahan objek, verdict `INCONCLUSIVE`, dan scope flag.
4. Jalankan kampanye eksploratif; hasilkan receipt.
5. Tulis laporan `reports/GW_CHAR_BLOCK_2026-10-21.md` dengan derivasi,
   angka eksploratif, dan alasan `INCONCLUSIVE`.
6. Tidak menulis registry. HANDOFF §2.0au mencatat status `NOT READY`.
7. Suite penuh dan `freeze.py --verify`; commit/push hanya bila diminta.

## 8. Batas eksplisit

- Hanya tiga karakter primitif real non-principal dan empat parent.
- Hanya `c=100,N=20` dan `c=200,N=20`, `prec=600`.
- Blok principal/pole tidak diimplementasikan.
- Tidak ada klaim nol, `sigma=1/2`, critical-line lock, RH/GRH, global
  positivity, faktorisasi, RSA/ECC, Anderson, atau fisika.
- Tidak ada kampanye tersegel yang dijalankan ulang.
- Verdict `INCONCLUSIVE` adalah status yang sah; bukan kegagalan yang
  boleh diubah menjadi `PASS` secara retoris.
