# Blok Guinand–Weil berkarakter — kandidat derivasi, status `INCONCLUSIVE` — 2026-10-21

**Status:** eksekusi `PASS`, **sertifikasi `INCONCLUSIVE` / `NOT READY`**.
Tidak ada entri registry untuk paket C. Verifikasi lokal; belum
di-commit/di-push.

**Paket:** Opsi C dari
[`reports/SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md`](SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md).

**Pra-registrasi:**
[`reports/PREREG_GW_CHAR_BLOCK_2026-10-21.md`](PREREG_GW_CHAR_BLOCK_2026-10-21.md)
(`sha256LF 9a3f46c1f59c9e37088603d2d1e15d328369428d366557bb8e1870faa94afa64`).

## 1. Ringkasan hasil

Paket C menurunkan **kandidat** blok Guinand–Weil berkarakter dari explicit
formula dan mengujinya secara finite:

- kandidat `h_chi(r) = Re psi((1+2a)/4 + i r/2) + log q* - log pi`
  diimplementasikan dengan pergeseran pole digamma `c_k = 2k + 2 alpha`,
  `alpha = (1+2a)/4`;
- blok pole `W02_chi = 0` untuk karakter non-principal (L(s,chi) tidak
  ber-pole);
- kontrol reduksi zeta `q*=1, a=0` **lolos**: selisih maks
  `3.99513295963740023489496109252e-57` terhadap ambang
  `2.67276471009219564614053646715e-51`;
- seluruh entri `WR_chi`, `Wp_chi`, `tau_chi` finite dan semua pivot LDL^T
  terdefinisi;
- blok **standar** (koefisien `chi*`, konduktor `q*`) dan blok **deret
  Dirichlet** (koefisien `chi` non-primitif, konduktor sama) terbukti
  **objek berbeda** pada prime baru.

Verdict tetap **`INCONCLUSIVE`** karena dua hal belum tertutup:

1. tidak ada validasi independen untuk pergeseran paritas `alpha = 3/4`
   maupun konstanta konduktor `log q*`;
2. blok pole untuk karakter **principal** belum diturunkan maupun diuji.

Angka inertia di bawah bersifat **eksploratif** dan tidak boleh dipromosikan ke
`PASS`.

## 2. Derivasi kandidat

Untuk karakter primitif real `chi` modulo `q*` dengan paritas `a`:

```text
Lambda(s, chi) = (q*/pi)^((s+a)/2) Gamma((s+a)/2) L(s, chi)
h_chi(r)       = Re psi(alpha + i r/2) + log q* - log pi,  alpha = (1+2a)/4
```

Sumber archimedean `psi_R(x) = (1/(2 pi^2)) ∫ h_chi(r) S(r,x,L) dr` dengan
`S(r,x,L) = ∫_0^L sin(2 pi x (1-y/L)) cos(r y) dy`. Bentuk tertutup zeta
digeneralisasi dengan:

```text
c_k = 2k + 2 alpha
S(n)  = (1/2) Im psi(alpha + i pi n/L) - w gS
CC(n) = -(1/2)(Re psi(alpha + i pi n/L) - psi(alpha)) + gCC
XC(n) = (1/4) Re psi'(alpha + i pi n/L) - L gX1 - gX2
WR(n,n) = kappa_chi + 2 CC(n) + J - (2/L) XC(n)
WR(m,n) = (S_signed(m) - S_signed(n)) / (pi (n-m))
kappa_chi = kappa_zeta + log q*
```

`J` dan `kappa_zeta` tetap berasal dari test function zeta. Konstanta
`log q*` masuk lewat diagonal: konstanta pada `h_chi` menambah
`psi_R'(n)` sebesar konstanta itu dan tidak mengubah beda terbagi
off-diagonal. Bagian inilah yang **belum** divalidasi independen.

Blok hasil:

```text
tau_chi = W02_chi - WR_chi - Wp_chi = -WR_chi - Wp_chi   (non-principal)
```

dengan `Wp_chi(q_k) = log(p) q_k^(-1/2) chi(q_k) shape(q_k)` untuk
`q_k = p^b <= c`.

## 3. Dua objek yang tetap dipisah

| Objek | konduktor | paritas | koefisien prime power | status |
|---|---:|---:|---|---|
| Standar `L(s,chi)` | `q*` | `a` | `chi*(q_k)` | kandidat |
| Deret Dirichlet `F(s)=sum chi(n) n^{-s}` | `q*` | `a` | `chi(q_k)` (nol di prime baru) | kandidat |

Untuk karakter non-primitif, `L(s,chi) = L(s,chi*)`; karena itu blok
standar memakai `chi*` dan konduktor `q*`. Blok deret memakai koefisien
parent dan **bukan** L-function standar. Keduanya tidak boleh disamakan.

## 4. Kontrol C1 (reduksi zeta)

| Item | Nilai |
|---|---|
| Konfigurasi kontrol | `q*=1`, `a=0`, `alpha=1/4`, `c=13`, `N=4`, `prec=200` |
| `max_abs(WR_chi - WR_zeta)` | `3.99513295963740023489496109252e-57` |
| ambang `2^{-(prec-32)}` | `2.67276471009219564614053646715e-51` |
| Status | **PASS** |

Kontrol ini **hanya** memverifikasi jalur implementasi untuk `alpha=1/4`
tanpa konduktor. Ia tidak memvalidasi `alpha=3/4` maupun `log q*`.

## 5. Inertia eksploratif

Blok standar (kandidat, `dim=41`, `prec=600`):

| Karakter | `q*` | paritas | `alpha` | `c=100` | `c=200` |
|---|---:|---:|---:|---:|---:|
| `chi_{4,3}` | 4 | 1 | 3/4 | `(4,37)` | `(6,35)` |
| `chi_{3,2}` | 3 | 1 | 3/4 | `(6,35)` | `(6,35)` |
| `chi_{5,4}` | 5 | 0 | 1/4 | `(16,25)` | `(14,27)` |

Blok deret Dirichlet (kandidat, `dim=41`, `prec=600`):

| Parent | `q*` | `c=100` | `c=200` | aktivasi prime baru (`c=100`) |
|---|---:|---:|---:|---:|
| `chi_{12,7}` | 4 | `(4,37)` | `(4,37)` | 4 |
| `chi_{12,5}` | 3 | `(3,38)` | `(6,35)` | 6 |
| `chi_{15,4}` | 5 | `(16,25)` | `(14,27)` | 4 |
| `chi_{15,11}` | 3 | `(2,39)` | `(5,36)` | 2 |

Selisih `max_abs(tau_deret - tau_standar)` pada `c=100`:
`1.44180937487476979636611744410` (`chi_{12,7}`),
`1.79638449857630038578569653613` (`chi_{12,5}`),
`1.44180937487476979636611744410` (`chi_{15,4}`),
`1.12933236224854582518748303030` (`chi_{15,11}`).

Blok standar untuk parent identik dengan blok primitifnya sampai toleransi
ball (`<= 2^{-536}`), konsisten dengan `L(s,chi)=L(s,chi*)`.

Semua inertia di atas **tidak** positif definit, tetapi ini adalah status
kandidat: ia tidak boleh dipakai sebagai kesimpulan tentang `L(s,chi)`.

## 6. Verdict

| Kriteria | Hasil |
|---|---|
| Konfigurasi kontrol | `q*=1`, `a=0`, `alpha=1/4`, `c=13`, `N=4`, `prec=200` |
| C1 reduksi zeta | PASS |
| C2 blok finite dan struktur | PASS |
| C3 inertia terdefinisi | PASS (tanpa pivot undetermined) |
| C4 standar vs deret terpisah | PASS |
| **Eksekusi** | **PASS** |
| Validasi independen `alpha=3/4`, `log q*` | **tidak ada** |
| Blok pole principal | **NOT IMPLEMENTED** |
| **Sertifikasi / verdict** | **`INCONCLUSIVE` / `NOT READY`** |

Receipt kanonik:

```text
execution_status      PASS
certification_status  INCONCLUSIVE
candidate_result      CANDIDATE NOT POSITIVE DEFINITE
verdict               INCONCLUSIVE
registry_entry        None
canonical sha256      25e61d7dc3e3d818b0c6978f34c4c6e123c922d0fd733cb33b86707372efa9ba
file sha256LF         b23afd04f3054ce194d60cdd92b67cee0f896da60bb5cd99230859b79a86afeb
prereg sha256LF       9a3f46c1f59c9e37088603d2d1e15d328369428d366557bb8e1870faa94afa64
```

## 7. Yang tidak diklaim dan jalan penutup

Tidak diklaim: bahwa kandidat blok ini adalah blok Guinand–Weil berkarakter
yang benar; bahwa `L(s,chi)` positif; lokasi nol, `sigma=1/2`,
critical-line lock, RH/GRH; global positivity; faktorisasi, RSA/ECC,
Anderson, atau fisika.

Untuk menutup C (dan baru boleh menulis registry), minimal diperlukan:

1. validasi independen blok `alpha=3/4` dan `log q*` — misalnya pencocokan
   explicit formula pada test vector terhadap jumlah nol `L(s,chi)` yang
   dihitung numerik, atau implementasi kedua yang independen;
2. derivasi blok pole principal (sumber `psi_0` diskalakan residu
   `phi(q)/q`) beserta uji fungsinya;
3. guard yang menolak promosi tanpa kedua hal tersebut.

Catatan metodologis: ball `arb` untuk fungsi transenden (`log`, `digamma`)
tidak bit-reproduktif antar pemanggilan pada presisi yang sama, sehingga
kesamaan antar blok dinilai dengan ambang ball, bukan kesamaan bit.

## 8. Artefak dan verifikasi

- Modul: `msaf/gw_char_block.py` —
  `sha256LF 1b71bb05fc283a9e3c90bf48821500694b2d14e0e5e757dfdb287d78a6d2c8b5`
- Guard: `msaf/tests/test_gw_char_block.py` —
  `sha256LF 5633e08454bf33d5116de0232eb416ec6cb0f86595cda43be85ab35fc4912adb`
- Pra-registrasi:
  `sha256LF 9a3f46c1f59c9e37088603d2d1e15d328369428d366557bb8e1870faa94afa64`
- Receipt:
  `sha256LF b23afd04f3054ce194d60cdd92b67cee0f896da60bb5cd99230859b79a86afeb`
- Runtime kampanye lokal: **8,04 s**.
- Guard baru: **12 tests**, lulus **15,17 s**.

Perintah reproduksi:

```bash
python -m msaf.gw_char_block --out reports/gw_char_block_2026-10-21.json
python -m pytest msaf/tests/test_gw_char_block.py -q
python -m pytest msaf -q
python audit_quantum/freeze.py --verify
```
