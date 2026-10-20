# Perturbasi blok zeta ad hoc dengan nilai karakter Dirichlet — 2026-10-21

**Status:** eksekusi `PASS`; verdict matematis **`AD HOC NEGATIVE`**.
Verifikasi lokal; belum di-commit/di-push.
**Paket:** Opsi B dari
[`reports/SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md`](SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md).
**Pra-registrasi:**
[`reports/PREREG_GW_CHAR_ADHOC_2026-10-21.md`](PREREG_GW_CHAR_ADHOC_2026-10-21.md)
(`sha256LF 297b0c9bcce826f1b7b32d3b1d6d48dae6c10fd9aeb65aa485ddf83b8ca83976`).

## 1. Ringkasan hasil

Paket ini menjalankan eksperimen **ad hoc** yang mengganti hanya `Wp` pada
blok zeta dengan nilai karakter real:

```text
tau_pert(chi) = W02_zeta - WR_zeta - Wp_chi.
```

Hasil eksekusi:

- kontrol builder lokal versus `source_arb_ldlt_certify` **MATCH**;
- baseline zeta positif definit, inertia `(41,0)` pada kedua konfigurasi;
- **semua** lift primitif dan karakter non-primitif memberi inertia yang
  **bukan** `(41,0)`;
- tidak ada pivot undetermined pada run yang dikunci;
- receipt deterministik dan cocok dengan disk.

Karena sekurangnya satu matriks karakter tidak positif definit, verdict
matematis adalah **`AD HOC NEGATIVE`**. Ini adalah hasil eksperimen yang
sah, bukan kegagalan eksekusi, dan **bukan** klaim tentang positivity
`L(s,chi)`.

## 2. Definisi yang dikunci

```text
W02_zeta  = blok pole zeta (karakter-blind)
WR_zeta   = blok archimedean zeta (karakter-blind)
Wp_chi    = sum_{q_k=p^a<=c} log(p) q_k^{-1/2} chi(q_k) shape(q_k)
tau_pert  = W02_zeta - WR_zeta - Wp_chi
```

`chi(q_k)` exact `-1/0/+1`; `chi(q_k)=0` bila `p | q`. `W02` dan `WR`
tetap milik zeta. Karena itu `tau_pert` **bukan** explicit formula untuk
`L(s,chi)` dan bukan blok Guinand–Weil berkarakter.

## 3. Konfigurasi dan karakter

| Peran | `c` | `N` | `dim=2N+1` | `prec` |
|---|---:|---:|---:|---:|
| Primer | 100 | 20 | 41 | 600 bit |
| Replikasi | 200 | 20 | 41 | 600 bit |

Empat karakter non-primitif real yang dipakai:

| Karakter | `q` | `q*` | lift | prime baru | aktivasi `q_k<=100` |
|---|---:|---:|---|---|---:|
| `chi_{12,7}` | 12 | 4 | `chi_{4,3}` | 3 | 4 |
| `chi_{12,5}` | 12 | 3 | `chi_{3,2}` | 2 | 6 |
| `chi_{15,4}` | 15 | 5 | `chi_{5,4}` | 3 | 4 |
| `chi_{15,11}` | 15 | 3 | `chi_{3,2}` | 5 | 2 |

Aktivasi adalah prime power `q_k <= 100` dengan `chi(q_k)=0` dan
`chi*(q_k) != 0`. Jumlahnya berubah pada `c=200` karena lebih banyak prime
power yang masuk.

## 4. Kontrol builder

Builder lokal mereproduksi `tau_zeta` dari
`source_arb_ldlt_certify.build_arb_tau` pada kedua konfigurasi:

| Konfigurasi | `max_abs(local-external)` | ambang `2^{-(prec-32)}` | status |
|---|---:|---:|---|
| `c=100,N=20,prec=600` | `3.58498038198500018907896109209e-176` | `1.03505270065976189609743348056e-171` | MATCH |
| `c=200,N=20,prec=600` | `3.28428520783070607295398100467e-176` | `1.03505270065976189609743348056e-171` | MATCH |

Kontrol ini memastikan bahwa perbedaan hasil karakter berasal dari
`Wp_chi`, bukan dari pergeseran builder zeta.

## 5. Inertia interval

Inertia adalah pasangan `(n_+, n_-)` dari pivot LDL^T yang semuanya
terdefinisi. Baseline zeta:

| Konfigurasi | `n_+` | `n_-` | status |
|---|---:|---:|---|
| `c=100,N=20` | 41 | 0 | POSITIVE DEFINITE |
| `c=200,N=20` | 41 | 0 | POSITIVE DEFINITE |

Karakter non-primitif dan lift primitifnya:

| Karakter | `c=100` primitif | `c=100` non-primitif | `c=200` primitif | `c=200` non-primitif |
|---|---:|---:|---:|---:|
| `chi_{12,7}` | `(17,24)` | `(20,21)` | `(15,26)` | `(22,19)` |
| `chi_{12,5}` | `(16,25)` | `(21,20)` | `(13,28)` | `(19,22)` |
| `chi_{15,4}` | `(19,22)` | `(20,21)` | `(15,26)` | `(19,22)` |
| `chi_{15,11}` | `(16,25)` | `(19,22)` | `(13,28)` | `(21,20)` |

Semua entri di atas adalah `NOT POSITIVE DEFINITE`; tidak ada
`undetermined_pivot`. Perhatikan bahwa **lift primitif pun** tidak positif
dengan `W02`/`WR` zeta. Ini memperkuat kesimpulan audit: yang gagal bukan
hanya nilai karakter non-primitif, tetapi kecocokan blok archimedean/pole
zeta dengan karakter.

`max_abs(Wp_nonprimitive - Wp_primitive)` pada `c=100`:

| Karakter | nilai |
|---|---:|
| `chi_{12,7}` | `1.44180937487476979636611744410` |
| `chi_{12,5}` | `1.79638449857630038578569653613` |
| `chi_{15,4}` | `1.44180937487476979636611744410` |
| `chi_{15,11}` | `1.12933236224854582518748303030` |

## 6. Verdict

| Kriteria | Hasil |
|---|---|
| Kontrol builder lokal vs eksternal | MATCH (2/2) |
| Baseline zeta `(dim,0)` | 2/2 |
| Entri finite | 2/2 konfigurasi, semua matriks |
| Pivot undetermined | tidak ada |
| Aktivasi prime baru | nonempty untuk 4/4 karakter |
| Determinisme receipt | PASS |
| **Eksekusi** | **PASS** |
| **Verdict matematis** | **AD HOC NEGATIVE** |

Receipt kanonik:

```text
execution_status     PASS
mathematical_verdict AD HOC NEGATIVE
verdict              AD HOC NEGATIVE
canonical sha256     76e43dac29f299cd7ec222bbf5bafce74850d1b6a24a33046f2b3ea9676093c1
file sha256LF        f7cb0327fa0b9a559513b18dc4fda8e5d3ec5fbca8ee440698d0ba4dc185b37f
prereg sha256LF      297b0c9bcce826f1b7b32d3b1d6d48dae6c10fd9aeb65aa485ddf83b8ca83976
```

## 7. Yang disertifikasi dan yang tidak

Yang disertifikasi:

1. Builder lokal mereproduksi matriks zeta eksternal pada dua konfigurasi.
2. `Wp_chi` memakai nilai karakter exact dan nol tepat pada `p | q`.
3. Inertia interval baseline zeta `(41,0)`.
4. Inertia interval semua matriks karakter bukan `(41,0)`.
5. Tidak ada pivot undetermined pada run yang dikunci.
6. Receipt deterministik dan label `AD HOC` konsisten.

Yang **tidak** diklaim:

- bahwa `tau_pert` adalah blok Guinand–Weil untuk `L(s,chi)`;
- bahwa `L(s,chi)` atau deret Dirichlet non-primitif tidak positif;
- lokasi nol, `sigma=1/2`, critical-line lock, RH/GRH;
- global positivity/Weil positivity;
- eigenvalue, magnitude, atau spectral gap dari inertia;
- faktorisasi, RSA/ECC, Anderson, atau fisika.

`AD HOC NEGATIVE` berarti **matriks perturbasi zeta yang dikunci tidak
positif definit**. Ia tidak boleh dikutip sebagai bukti tentang
`L(s,chi)`.

## 8. Artefak dan verifikasi

- Modul: `msaf/gw_char_adhoc.py` —
  `sha256LF b0e7b6a7e85ca7d9155276af5b904eb30bc9d39a745d1348380c7ab102f88713`
- Guard: `msaf/tests/test_gw_char_adhoc.py` —
  `sha256LF 0f5850da81a86f2062f83412181e186133c0ac0ab8a4a33c69dc79b8c5910bf3`
- Pra-registrasi:
  `sha256LF 297b0c9bcce826f1b7b32d3b1d6d48dae6c10fd9aeb65aa485ddf83b8ca83976`
- Receipt:
  `sha256LF f7cb0327fa0b9a559513b18dc4fda8e5d3ec5fbca8ee440698d0ba4dc185b37f`
- Runtime kampanye lokal: **9,06 s**.
- Guard baru: **12 tests**, lulus **12,38 s**.

Perintah reproduksi:

```bash
python -m msaf.gw_char_adhoc --out reports/gw_char_adhoc_2026-10-21.json
python -m pytest msaf/tests/test_gw_char_adhoc.py -q
python -m pytest msaf -q
python audit_quantum/freeze.py --verify
```

## 9. Hubungan dengan opsi C

Hasil B menunjukkan bahwa mengganti `Wp` saja tidak cukup: bahkan lift
primitif memberi matriks indefinite dengan `W02`/`WR` zeta. Opsi C karena
itu harus menurunkan ulang blok pole/archimedean untuk karakter
(`Gamma((s+a)/2)`, konduktor `q*`, pole principal) sebelum ada klaim
Guinand–Weil yang bermakna. Tidak ada hasil B yang boleh dipakai untuk
menaikkan verdict C.

## 10. Batas penutup

`PASS` eksekusi berarti **dua konfigurasi ad hoc yang dikunci berjalan
lengkap, deterministik, dan lolos kontrol builder**. Verdict matematisnya
adalah **`AD HOC NEGATIVE`**. Tidak ada klaim nol, critical-line, RH/GRH,
global positivity, atau fisika. Tidak ada kampanye tersegel yang dijalankan
ulang, dan tidak ada artefak beku yang diubah.
