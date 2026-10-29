# Pra-registrasi: perturbasi blok zeta ad hoc with nilai karakter â€” 2026-10-21

**Status:** scope DIKUNCI for paket B; implementasi and eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket B. Hash `sha256LF` file ini
dicatat in receipt and report.

**Paket:** Opsi B dari
[`reports/SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md`](SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md),
yaitu eksperimen matriks **`AD HOC PERTURBATION`**, bukan blok
Guinandâ€“Weil which benar for `L(s, chi)`.

**Berkas target:** `msaf/gw_char_adhoc.py` (baru), guard
`msaf/tests/test_gw_char_adhoc.py` (baru), report
`reports/GW_CHAR_ADHOC_2026-10-21.md`, receipt
`reports/gw_char_adhoc_2026-10-21.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0`, and modul eksternal
`source_arb_ldlt_certify.py` in `C:/Users/usER/oracle-toe/GUINAND_WEIL`
(hanya dibaca/diimpor; **no diubah**). Modul A
`msaf/gw_character_arithmetic.py` dipakai for nilai karakter exact.

**Registry which direncanakan:** `A-2026-0026`, hanya bila eksekusi and
integritas PASS; result positif/negatif matriks dicatat sebagai result
matematis terpisah, bukan otomatis `PASS`.

**Tidak mengubah:** V1â€“V6 (`A-2026-0015`â€“`A-2026-0021`), `A-2026-0022`â€“
`A-2026-0025`, `ci.yml` (`A-2026-0016`), workflow spec,
`lean/lakefile.toml`, freeze pins, seluruh report/artefak beku, and
`source_arb_ldlt_certify.py`. Tidak menjalankan ulang kampanye
quantum/H1/engine-B.

## 1. Maksud and limit

Paket A already verifying aritmetika karakter and zero struktural
koefisien. Paket B menguji apa which terjadi bila **hanya** `Wp` on
builder zeta diganti with nilai karakter, sementara `W02` and `WR` tetap
milik zeta:

```text
tau_pert(chi) = W02_zeta - WR_zeta - Wp_chi.
```

Ini adalah perturbasi eksplisit and sengaja **no** diklaim sebagai
explicit formula for `L(s, chi)` or for deret Dirichlet
non-primitif. Tujuannya adalah mengukur apakah blok zeta lama masih
memberi matriks positif definit ketika `Wp` diberi karakter. Hasil negatif
adalah result which sah and diharapkan; ia no boleh dilabeli `PASS`
positivitas.

Paket ini **bukan**:

- blok Guinandâ€“Weil berkarakter which benar (itu opsi C);
- klaim nol, lokasi nol, `sigma = 1/2`, critical-line lock, RH/GRH;
- klaim bahwa `L(s,chi)` standar sama with deret Dirichlet
  non-primitif;
- klaim global positivity, Weil positivity, or kontinum operator;
- klaim faktorisasi, RSA/ECC, Anderson, or fisika.

## 2. Definisi matriks which dikunci

Untuk `c > 1`, `N >= 1`, and `prec` bit, paket memakai fungsi eksternal
which already ada for `W02`, `WR`, and bentuk `Wp` zeta:

```text
W02_zeta  = blok pole zeta (pole_B; karakter-blind)
WR_zeta   = blok archimedean zeta (karakter-blind)
Wp_chi    = blok prime-power with bobot log(p) q_k^{-1/2} chi(q_k)
tau_pert  = W02_zeta - WR_zeta - Wp_chi
```

`Wp_chi` memakai `q_k = p^a <= c`, `chi(q_k)` exact `-1/0/+1`, and
`chi(q_k) = 0` bila `p | q`. Tidak ada perubahan on `W02` or `WR`.
Matriks berukuran `dim = 2N+1`, simetris real; inertia dihitung with
`certified_inertia` (interval LDL^T) dari modul eksternal.

Kontrol zeta:

```text
tau_zeta = W02_zeta - WR_zeta - Wp_zeta
```

`Wp_zeta` adalah bentuk which sama with semua nilai karakter `1`.
Implementasi lokal harus mereproduksi `tau_zeta` dari
`source_arb_ldlt_certify.build_arb_tau(c,N,prec)` sebelum dipakai; kontrol
ini adalah syarat integritas, bukan klaim baru.

## 3. Instance and konfigurasi which dikunci

Karakter which dipakai adalah empat instance non-primitif real dari paket A:

| Karakter | modulus `q` | konduktor `q*` | lift primitif | prime baru |
|---|---:|---:|---|---|
| `chi_{12,7}` | 12 | 4 | `chi_{4,3}` | 3 |
| `chi_{12,5}` | 12 | 3 | `chi_{3,2}` | 2 |
| `chi_{15,4}` | 15 | 5 | `chi_{5,4}` | 3 |
| `chi_{15,11}` | 15 | 3 | `chi_{3,2}` | 5 |

Dua konfigurasi dijalankan:

| Peran | `c` | `N` | `dim=2N+1` | `prec` |
|---|---:|---:|---:|---:|
| Primer | 100 | 20 | 41 | 600 bit |
| Replikasi | 200 | 20 | 41 | 600 bit |

Untuk setiap konfigurasi and setiap karakter, dihitung inertia dari:

1. baseline zeta (`Wp_zeta`);
2. lift primitif (`Wp_{chi*}`);
3. karakter non-primitif (`Wp_chi`).

Tidak ada instance, cutoff, or presisi tambahan setelah result terlihat.

## 4. Pemeriksaan integritas (C1)

1. Builder lokal for `tau_zeta` harus cocok with
   `source_arb_ldlt_certify.build_arb_tau` on `(c,N,prec)` which dikunci;
   selisih entrywise harus nol or in bawah ambang ball
   `2^{-(prec-32)}`.
2. Semua entri `W02`, `WR`, `Wp`, and `tau_pert` harus finite.
3. `Wp_chi(q_k)=0` tepat ketika `gcd(q_k,q)>1`; `Wp_{chi*}(q_k)=0` tepat
   ketika `gcd(q_k,q*)>1`; on prime power with `p | q` and
   `p no | q*`, `Wp_chi=0` tetapi `Wp_{chi*}` no nol.
4. Daftar istilah aktivasi `{q_k <= c : chi(q_k)=0, chi*(q_k)!=0}` harus
   no kosong for setiap karakter non-primitif.
5. Inertia baseline zeta harus terdefinisi (no ada pivot undetermined)
   and, on konfigurasi which dikunci, harus `(dim,0)`.

C1 PASS hanya bila semua butir benar.

## 5. Inertia interval (C2)

Untuk setiap matriks, `certified_inertia` harus mengembalikan:

- `n_pos`, `n_neg`, and `undetermined_pivot`;
- transcript pivot with panjang `dim`;
- `entries_finite=true`.

Inertia `(n_pos,n_neg)` adalah pernyataan **tanda** matriks finite, bukan
magnitude eigenvalue. Tidak ada eigenvalue, jarak spektral, or ambang
positivitas which diklaim dari inertia.

C2 PASS bila semua run menghasilkan pivot which terdefinisi. Bila ada
`undetermined_pivot`, result dicatat `INCONCLUSIVE` for run itu; no
dinaikkan menjadi positif/negatif.

## 6. Hasil matematis which dilaporkan (C3)

Untuk setiap karakter and konfigurasi, catat:

```text
status_baseline    in {POSITIVE DEFINITE, NOT POSITIVE DEFINITE, INCONCLUSIVE}
status_primitive   in {POSITIVE DEFINITE, NOT POSITIVE DEFINITE, INCONCLUSIVE}
status_nonprimitive in {POSITIVE DEFINITE, NOT POSITIVE DEFINITE, INCONCLUSIVE}
```

`POSITIVE DEFINITE` berarti `(n_pos,n_neg)=(dim,0)` with semua pivot
terdefinisi and entri finite. `NOT POSITIVE DEFINITE` berarti inertia
terdefinisi tetapi bukan `(dim,0)`.

Verdict matematis paket:

- `AD HOC POSITIVE` bila ketiga status for semua karakter/konfigurasi
  adalah `POSITIVE DEFINITE`;
- `AD HOC NEGATIVE` bila semua inertia terdefinisi and sekurangnya satu
  status karakter bukan `POSITIVE DEFINITE`;
- `INCONCLUSIVE` bila ada pivot undetermined or run no lengkap.

`AD HOC NEGATIVE` **bukan** kegagalan eksekusi. Ia adalah result eksperimen
which sah and harus dilaporkan apa adanya.

## 7. Determinisme and receipt (C4)

Receipt deterministik harus memuat:

- `schema`, hash `sha256LF` pra-registrasi ini, and konfigurasi which
  dikunci;
- kontrol kecocokan builder lokal versus eksternal;
- for setiap konfigurasi/karakter: `n_pos`, `n_neg`,
  `undetermined_pivot`, `pivots_recorded`, hash transcript, status
  baseline/primitif/non-primitif;
- daftar istilah aktivasi prime power and `max_abs(Wp_chi-Wp_{chi*})`
  sebagai ball;
- `scope` with flag `ad_hoc_perturbation=true`,
  `correct_character_weil_block=false`, `global_claim_supported=false`,
  `critical_line_claim=false`, `zero_localization_claim=false`;
- `execution_status` and `mathematical_verdict` terpisah.

C4 PASS bila dua build receipt berturut-turut menghasilkan payload kanonik
identik and receipt in disk cocok with result hitung ulang.

## 8. Verdict

- **EXECUTION PASS:** C1, C2, C4 PASS; result matematis boleh
  `AD HOC NEGATIVE` or `AD HOC POSITIVE`.
- **INCONCLUSIVE:** ada pivot undetermined, tool gagal, or kontrol builder
  no dapat dijalankan.
- **FAILED:** kontrol builder gagal, ada entri non-finite, aktivasi kosong,
  or determinisme/hash rusak.

Registry `A-2026-0026` hanya boleh mencatat **eksekusi** and result
matematis which dilaporkan; ia no boleh menyatakan positivity karakter
sebagai klaim Guinandâ€“Weil.

## 9. Falsifier

Paket ini falsified bila:

- builder lokal no mereproduksi `tau_zeta` eksternal;
- ada entri non-finite;
- `Wp_chi` no nol tepat on `gcd(q_k,q)>1`;
- no ada aktivasi prime baru;
- baseline zeta bukan `(dim,0)` on konfigurasi which dikunci;
- receipt no deterministik or hash no cocok.

Falsifier dicatat `FAILED`/`INCONCLUSIVE`; no ada perubahan parameter
setelah result.

## 10. Artefak and urutan eksekusi

1. Tulis and hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/gw_char_adhoc.py` with builder lokal and kontrol
   eksternal.
3. Guard `msaf/tests/test_gw_char_adhoc.py`: uji kontrol builder, aktivasi,
   inertia, status, determinisme, tamper hash, and scope flag.
4. Jalankan kampanye penuh sekali; hasilkan receipt.
5. Tulis report `reports/GW_CHAR_ADHOC_2026-10-21.md` with angka
   verbatim, `AD HOC` in judul/verdict, and limit eksplisit.
6. Bila eksekusi/integritas PASS: registry `A-2026-0026`, HANDOFF Â§2.0at,
   sertifikat sha256LF. Positivitas tetap dilaporkan terpisah.
7. Suite penuh and `freeze.py --verify`; commit/push hanya bila diminta.

## 11. Batas eksplisit

- Hanya `c=100,N=20` and `c=200,N=20`, `prec=600`.
- Hanya empat karakter real non-primitif and lift primitifnya.
- `W02`/`WR` tetap blok zeta; ini bukan explicit formula karakter.
- Inertia hanya tanda; no ada eigenvalue, magnitude, or gap.
- Tidak ada klaim nol, `sigma=1/2`, critical-line lock, RH/GRH, global
  positivity, faktorisasi, RSA/ECC, Anderson, or fisika.
- Tidak ada kampanye tersegel which dijalankan ulang.
- `AD HOC NEGATIVE` adalah result eksperimen, bukan klaim bahwa
  `L(s,chi)` no positif.


