# Pra-registrasi: blok Guinandâ€“Weil berkarakter â€” derivasi kandidat and limit validasi â€” 2026-10-21

**Status:** scope DIKUNCI for paket C; implementasi and eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket C. Hash `sha256LF` file ini
dicatat in receipt and report.

**Paket:** Opsi C dari
[`reports/SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md`](SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md),
yaitu derivasi blok pole/archimedean which benar for karakter, with
validasi independen bila memungkinkan.

**Berkas target:** `msaf/gw_char_block.py` (baru), guard
`msaf/tests/test_gw_char_block.py` (baru), report
`reports/GW_CHAR_BLOCK_2026-10-21.md`, receipt
`reports/gw_char_block_2026-10-21.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0`, modul B
`msaf/gw_char_adhoc.py` for builder zeta/Wp/inertia, and modul A
`msaf/gw_character_arithmetic.py` for karakter exact. Tidak ada
`numpy`/`scipy` and no ada perubahan on modul eksternal.

**Registry:** **no ada** entri registry for paket C on fase ini.
Registry hanya boleh ditulis bila derivasi, validasi independen, and blok
pole principal semuanya ditutup. Sebelum itu, verdict harus
`INCONCLUSIVE`/`NOT READY` and no boleh dipromosikan menjadi `PASS`.

**Tidak mengubah:** V1â€“V6 (`A-2026-0015`â€“`A-2026-0021`),
`A-2026-0022`â€“`A-2026-0026`, `ci.yml` (`A-2026-0016`), workflow spec,
`lean/lakefile.toml`, freeze pins, seluruh report/artefak beku, and
`source_arb_ldlt_certify.py`. Tidak menjalankan ulang kampanye
quantum/H1/engine-B.

## 1. Maksud and limit

Blueprint item 1 meminta matriks `W02 - WR - Wp` for karakter
non-primitif. Audit Aâ€“B menunjukkan bahwa mengganti `Wp` saja no cukup.
Paket C mencoba menurunkan blok which benar for **L(s, chi) standar**:

```text
Lambda(s, chi) = (q*/pi)^((s+a)/2) Gamma((s+a)/2) L(s, chi)
```

with `chi` primitif modulo `q*`, paritas `a in {0,1}`, and `L(s,chi)`
non-principal sehingga **no ada pole**. Untuk karakter non-primitif,
L(s,chi) = L(s,chi*) and blok standar harus memakai `q*` and nilai `chi*`,
bukan modulus `q` or zero koefisien `chi`.

Kandidat blok which diuji:

```text
h_chi(r) = Re psi((1+2a)/4 + i r/2) + log q* - log pi
W02_chi  = 0                                  (non-principal)
WR_chi   = blok archimedean dari h_chi
Wp_chi   = sum_{q_k=p^b<=c} log(p) q_k^(-1/2) chi(q_k) shape(q_k)
tau_chi  = W02_chi - WR_chi - Wp_chi = -WR_chi - Wp_chi
```

Untuk mereduksi ke zeta, `q*=1`, `a=0`, and `chi` trivial harus memberi
`h_chi = h_+`, sehingga `WR_chi` harus sama with `WR_zeta` dalam ball.
Ini adalah kontrol implementasi, bukan bukti kebenaran penuh.

Paket C **no** mengklaim:

- bahwa kandidat blok already tervalidasi secara independen for semua
  `q*`/paritas;
- blok pole for karakter principal (belum diimplementasikan);
- klaim nol, lokasi nol, `sigma = 1/2`, critical-line lock, RH/GRH;
- positivity `L(s,chi)` or Weil positivity;
- faktorisasi, RSA/ECC, Anderson, or fisika.

## 2. Derivasi kandidat

Dengan `alpha = (1+2a)/4`, source archimedean adalah

```text
psi_R(x) = (1/(2 pi^2)) âˆ« h_chi(r) S(r,x,L) dr
S(r,x,L) = âˆ«_0^L sin(2 pi x (1-y/L)) cos(r y) dy
```

Untuk `x=n` integer, bentuk tertutup zeta digeneralisasi with:

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

Diagonal and off-diagonal:

```text
WR(n,n) = kappa_chi + 2 CC(n) + J - (2/L) XC(n)
WR(m,n) = (S_signed(m) - S_signed(n)) / (pi (n-m)),  m != n
kappa_chi = kappa_zeta + log q*
```

`J` and `kappa_zeta` tetap dari test function zeta. Konstanta `log q*`
menambah diagonal karena konstanta on `h_chi` menambah `psi_R'(n)` sebesar
konstanta itu and no mengubah beda terbagi off-diagonal. Ini adalah
section derivasi which harus divalidasi, bukan diasumsikan.

## 3. Konfigurasi and karakter which dikunci

Konfigurasi:

| Peran | `c` | `N` | `dim=2N+1` | `prec` |
|---|---:|---:|---:|---:|
| Primer | 100 | 20 | 41 | 600 bit |
| Replikasi | 200 | 20 | 41 | 600 bit |

Karakter primitif non-principal which dikunci:

| Karakter | `q*` | paritas `a` | `alpha` |
|---|---:|---:|---:|
| `chi_{4,3}` | 4 | 1 | 3/4 |
| `chi_{3,2}` | 3 | 1 | 3/4 |
| `chi_{5,4}` | 5 | 0 | 1/4 |

Untuk uji non-primitif, empat parent dari paket B dipetakan ke lift-nya:
`chi_{12,7}->chi_{4,3}`, `chi_{12,5}->chi_{3,2}`,
`chi_{15,4}->chi_{5,4}`, `chi_{15,11}->chi_{3,2}`. Blok **standar**
memakai lift primitif; blok **deret Dirichlet** memakai nilai parent
(nol in prime baru) tetapi tetap `q*` and `alpha` which sama. Kedua objek
harus dibedakan and no boleh disebut sama.

## 4. Pemeriksaan (C1â€“C4)

**C1: reduksi zeta.** Untuk `q*=1`, `a=0`, `c=13,N=4,prec=200`, blok
`WR_chi` harus sama with `WR_zeta` dari builder B dalam ball; selisih
entrywise harus in bawah ambang `2^{-(prec-32)}`.

**C2: finite and struktur.** Semua entri `WR_chi`, `Wp_chi`, `tau_chi`
harus finite; `Wp_chi(q_k)=0` tepat ketika `gcd(q_k,q*)>1`; for blok
standar, nilai prime power memakai `chi*`; for blok deret, memakai
`chi` and berbeda on prime baru.

**C3: inertia eksploratif.** Hitung interval LDL^T for setiap blok
standar and deret on dua konfigurasi. Inertia adalah pernyataan tanda
matriks finite; no ada eigenvalue, magnitude, or klaim nol. Bila ada
pivot undetermined, catat `INCONCLUSIVE`.

**C4: pemisahan objek.** Untuk setiap parent non-primitif, blok standar
and blok deret harus dibandingkan; selisih `Wp` harus no nol on
prime baru, and statusnya dicatat terpisah. Tidak boleh ada klaim bahwa
keduanya adalah L-function which sama.

## 5. Validasi independen and verdict

Validasi which benar-benar independen for `alpha=3/4` and `log q*` belum
tersedia dalam paket ini. Reduksi `q*=1, alpha=1/4` hanya menguji jalur
implementasi; ia no memvalidasi pergeseran paritas, konduktor, or
blok pole principal. Karena itu:

- `execution_status` boleh `PASS` bila C1â€“C4 berjalan and finite;
- `certification_status` tetap **`INCONCLUSIVE`**;
- `verdict` tetap **`INCONCLUSIVE`** / **`NOT READY`**;
- no ada registry entry;
- angka inertia hanya dilaporkan sebagai **eksploratif**.

Paket C baru boleh menjadi `PASS` bila (i) blok `alpha=3/4` and `log q*`
divalidasi independen (mis. quadrature/source eksplisit or pencocokan
nol), (ii) blok pole principal diturunkan and diuji, and (iii) guard
menolak promosi tanpa kedua hal itu. Kondisi ini **no** dipenuhi on
fase ini.

## 6. Falsifier

- Reduksi zeta `q*=1` gagal in luar ball â†’ `FAILED`.
- Ada entri non-finite or `Wp` salah zero â†’ `FAILED`.
- Blok standar and deret no berbeda on prime baru â†’ `FAILED`.
- Inertia undetermined â†’ `INCONCLUSIVE` for run itu.
- Klaim `PASS`, registry, or klaim nol/critical-line tanpa validasi
  independen and blok principal â†’ pelanggaran scope.

## 7. Artefak and urutan eksekusi

1. Tulis and hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/gw_char_block.py` with kandidat, kontrol q*=1, and
   pemisahan standar/deret.
3. Guard `msaf/tests/test_gw_char_block.py`: uji reduksi, finite, inertia,
   pemisahan objek, verdict `INCONCLUSIVE`, and scope flag.
4. Jalankan kampanye eksploratif; hasilkan receipt.
5. Tulis report `reports/GW_CHAR_BLOCK_2026-10-21.md` with derivasi,
   angka eksploratif, and alasan `INCONCLUSIVE`.
6. Tidak menulis registry. HANDOFF Â§2.0au mencatat status `NOT READY`.
7. Suite penuh and `freeze.py --verify`; commit/push hanya bila diminta.

## 8. Batas eksplisit

- Hanya tiga karakter primitif real non-principal and empat parent.
- Hanya `c=100,N=20` and `c=200,N=20`, `prec=600`.
- Blok principal/pole no diimplementasikan.
- Tidak ada klaim nol, `sigma=1/2`, critical-line lock, RH/GRH, global
  positivity, faktorisasi, RSA/ECC, Anderson, or fisika.
- Tidak ada kampanye tersegel which dijalankan ulang.
- Verdict `INCONCLUSIVE` adalah status which sah; bukan kegagalan which
  boleh diubah menjadi `PASS` secara retoris.


