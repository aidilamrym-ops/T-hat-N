# Pra-registrasi: perturbasi blok zeta ad hoc dengan nilai karakter — 2026-10-21

**Status:** scope DIKUNCI untuk paket B; implementasi dan eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket B. Hash `sha256LF` berkas ini
dicatat di receipt dan laporan.

**Paket:** Opsi B dari
[`reports/SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md`](SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md),
yaitu eksperimen matriks **`AD HOC PERTURBATION`**, bukan blok
Guinand–Weil yang benar untuk `L(s, chi)`.

**Berkas target:** `msaf/gw_char_adhoc.py` (baru), guard
`msaf/tests/test_gw_char_adhoc.py` (baru), laporan
`reports/GW_CHAR_ADHOC_2026-10-21.md`, receipt
`reports/gw_char_adhoc_2026-10-21.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0`, dan modul eksternal
`source_arb_ldlt_certify.py` di `C:/Users/usER/oracle-toe/GUINAND_WEIL`
(hanya dibaca/diimpor; **tidak diubah**). Modul A
`msaf/gw_character_arithmetic.py` dipakai untuk nilai karakter exact.

**Registry yang direncanakan:** `A-2026-0026`, hanya bila eksekusi dan
integritas PASS; hasil positif/negatif matriks dicatat sebagai hasil
matematis terpisah, bukan otomatis `PASS`.

**Tidak mengubah:** V1–V6 (`A-2026-0015`–`A-2026-0021`), `A-2026-0022`–
`A-2026-0025`, `ci.yml` (`A-2026-0016`), workflow spec,
`lean/lakefile.toml`, freeze pins, seluruh laporan/artefak beku, dan
`source_arb_ldlt_certify.py`. Tidak menjalankan ulang kampanye
quantum/H1/engine-B.

## 1. Maksud dan batas

Paket A sudah memverifikasi aritmetika karakter dan zero struktural
koefisien. Paket B menguji apa yang terjadi bila **hanya** `Wp` pada
builder zeta diganti dengan nilai karakter, sementara `W02` dan `WR` tetap
milik zeta:

```text
tau_pert(chi) = W02_zeta - WR_zeta - Wp_chi.
```

Ini adalah perturbasi eksplisit dan sengaja **tidak** diklaim sebagai
explicit formula untuk `L(s, chi)` atau untuk deret Dirichlet
non-primitif. Tujuannya adalah mengukur apakah blok zeta lama masih
memberi matriks positif definit ketika `Wp` diberi karakter. Hasil negatif
adalah hasil yang sah dan diharapkan; ia tidak boleh dilabeli `PASS`
positivitas.

Paket ini **bukan**:

- blok Guinand–Weil berkarakter yang benar (itu opsi C);
- klaim nol, lokasi nol, `sigma = 1/2`, critical-line lock, RH/GRH;
- klaim bahwa `L(s,chi)` standar sama dengan deret Dirichlet
  non-primitif;
- klaim global positivity, Weil positivity, atau kontinum operator;
- klaim faktorisasi, RSA/ECC, Anderson, atau fisika.

## 2. Definisi matriks yang dikunci

Untuk `c > 1`, `N >= 1`, dan `prec` bit, paket memakai fungsi eksternal
yang sudah ada untuk `W02`, `WR`, dan bentuk `Wp` zeta:

```text
W02_zeta  = blok pole zeta (pole_B; karakter-blind)
WR_zeta   = blok archimedean zeta (karakter-blind)
Wp_chi    = blok prime-power dengan bobot log(p) q_k^{-1/2} chi(q_k)
tau_pert  = W02_zeta - WR_zeta - Wp_chi
```

`Wp_chi` memakai `q_k = p^a <= c`, `chi(q_k)` exact `-1/0/+1`, dan
`chi(q_k) = 0` bila `p | q`. Tidak ada perubahan pada `W02` atau `WR`.
Matriks berukuran `dim = 2N+1`, simetris real; inertia dihitung dengan
`certified_inertia` (interval LDL^T) dari modul eksternal.

Kontrol zeta:

```text
tau_zeta = W02_zeta - WR_zeta - Wp_zeta
```

`Wp_zeta` adalah bentuk yang sama dengan semua nilai karakter `1`.
Implementasi lokal harus mereproduksi `tau_zeta` dari
`source_arb_ldlt_certify.build_arb_tau(c,N,prec)` sebelum dipakai; kontrol
ini adalah syarat integritas, bukan klaim baru.

## 3. Instance dan konfigurasi yang dikunci

Karakter yang dipakai adalah empat instance non-primitif real dari paket A:

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

Untuk setiap konfigurasi dan setiap karakter, dihitung inertia dari:

1. baseline zeta (`Wp_zeta`);
2. lift primitif (`Wp_{chi*}`);
3. karakter non-primitif (`Wp_chi`).

Tidak ada instance, cutoff, atau presisi tambahan setelah hasil terlihat.

## 4. Pemeriksaan integritas (C1)

1. Builder lokal untuk `tau_zeta` harus cocok dengan
   `source_arb_ldlt_certify.build_arb_tau` pada `(c,N,prec)` yang dikunci;
   selisih entrywise harus nol atau di bawah ambang ball
   `2^{-(prec-32)}`.
2. Semua entri `W02`, `WR`, `Wp`, dan `tau_pert` harus finite.
3. `Wp_chi(q_k)=0` tepat ketika `gcd(q_k,q)>1`; `Wp_{chi*}(q_k)=0` tepat
   ketika `gcd(q_k,q*)>1`; pada prime power dengan `p | q` dan
   `p tidak | q*`, `Wp_chi=0` tetapi `Wp_{chi*}` tidak nol.
4. Daftar istilah aktivasi `{q_k <= c : chi(q_k)=0, chi*(q_k)!=0}` harus
   tidak kosong untuk setiap karakter non-primitif.
5. Inertia baseline zeta harus terdefinisi (tidak ada pivot undetermined)
   dan, pada konfigurasi yang dikunci, harus `(dim,0)`.

C1 PASS hanya bila semua butir benar.

## 5. Inertia interval (C2)

Untuk setiap matriks, `certified_inertia` harus mengembalikan:

- `n_pos`, `n_neg`, dan `undetermined_pivot`;
- transcript pivot dengan panjang `dim`;
- `entries_finite=true`.

Inertia `(n_pos,n_neg)` adalah pernyataan **tanda** matriks finite, bukan
magnitude eigenvalue. Tidak ada eigenvalue, jarak spektral, atau ambang
positivitas yang diklaim dari inertia.

C2 PASS bila semua run menghasilkan pivot yang terdefinisi. Bila ada
`undetermined_pivot`, hasil dicatat `INCONCLUSIVE` untuk run itu; tidak
dinaikkan menjadi positif/negatif.

## 6. Hasil matematis yang dilaporkan (C3)

Untuk setiap karakter dan konfigurasi, catat:

```text
status_baseline    in {POSITIVE DEFINITE, NOT POSITIVE DEFINITE, INCONCLUSIVE}
status_primitive   in {POSITIVE DEFINITE, NOT POSITIVE DEFINITE, INCONCLUSIVE}
status_nonprimitive in {POSITIVE DEFINITE, NOT POSITIVE DEFINITE, INCONCLUSIVE}
```

`POSITIVE DEFINITE` berarti `(n_pos,n_neg)=(dim,0)` dengan semua pivot
terdefinisi dan entri finite. `NOT POSITIVE DEFINITE` berarti inertia
terdefinisi tetapi bukan `(dim,0)`.

Verdict matematis paket:

- `AD HOC POSITIVE` bila ketiga status untuk semua karakter/konfigurasi
  adalah `POSITIVE DEFINITE`;
- `AD HOC NEGATIVE` bila semua inertia terdefinisi dan sekurangnya satu
  status karakter bukan `POSITIVE DEFINITE`;
- `INCONCLUSIVE` bila ada pivot undetermined atau run tidak lengkap.

`AD HOC NEGATIVE` **bukan** kegagalan eksekusi. Ia adalah hasil eksperimen
yang sah dan harus dilaporkan apa adanya.

## 7. Determinisme dan receipt (C4)

Receipt deterministik harus memuat:

- `schema`, hash `sha256LF` pra-registrasi ini, dan konfigurasi yang
  dikunci;
- kontrol kecocokan builder lokal versus eksternal;
- untuk setiap konfigurasi/karakter: `n_pos`, `n_neg`,
  `undetermined_pivot`, `pivots_recorded`, hash transcript, status
  baseline/primitif/non-primitif;
- daftar istilah aktivasi prime power dan `max_abs(Wp_chi-Wp_{chi*})`
  sebagai ball;
- `scope` dengan flag `ad_hoc_perturbation=true`,
  `correct_character_weil_block=false`, `global_claim_supported=false`,
  `critical_line_claim=false`, `zero_localization_claim=false`;
- `execution_status` dan `mathematical_verdict` terpisah.

C4 PASS bila dua build receipt berturut-turut menghasilkan payload kanonik
identik dan receipt di disk cocok dengan hasil hitung ulang.

## 8. Verdict

- **EXECUTION PASS:** C1, C2, C4 PASS; hasil matematis boleh
  `AD HOC NEGATIVE` atau `AD HOC POSITIVE`.
- **INCONCLUSIVE:** ada pivot undetermined, tool gagal, atau kontrol builder
  tidak dapat dijalankan.
- **FAILED:** kontrol builder gagal, ada entri non-finite, aktivasi kosong,
  atau determinisme/hash rusak.

Registry `A-2026-0026` hanya boleh mencatat **eksekusi** dan hasil
matematis yang dilaporkan; ia tidak boleh menyatakan positivity karakter
sebagai klaim Guinand–Weil.

## 9. Falsifier

Paket ini falsified bila:

- builder lokal tidak mereproduksi `tau_zeta` eksternal;
- ada entri non-finite;
- `Wp_chi` tidak nol tepat pada `gcd(q_k,q)>1`;
- tidak ada aktivasi prime baru;
- baseline zeta bukan `(dim,0)` pada konfigurasi yang dikunci;
- receipt tidak deterministik atau hash tidak cocok.

Falsifier dicatat `FAILED`/`INCONCLUSIVE`; tidak ada perubahan parameter
setelah hasil.

## 10. Artefak dan urutan eksekusi

1. Tulis dan hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/gw_char_adhoc.py` dengan builder lokal dan kontrol
   eksternal.
3. Guard `msaf/tests/test_gw_char_adhoc.py`: uji kontrol builder, aktivasi,
   inertia, status, determinisme, tamper hash, dan scope flag.
4. Jalankan kampanye penuh sekali; hasilkan receipt.
5. Tulis laporan `reports/GW_CHAR_ADHOC_2026-10-21.md` dengan angka
   verbatim, `AD HOC` di judul/verdict, dan batas eksplisit.
6. Bila eksekusi/integritas PASS: registry `A-2026-0026`, HANDOFF §2.0at,
   sertifikat sha256LF. Positivitas tetap dilaporkan terpisah.
7. Suite penuh dan `freeze.py --verify`; commit/push hanya bila diminta.

## 11. Batas eksplisit

- Hanya `c=100,N=20` dan `c=200,N=20`, `prec=600`.
- Hanya empat karakter real non-primitif dan lift primitifnya.
- `W02`/`WR` tetap blok zeta; ini bukan explicit formula karakter.
- Inertia hanya tanda; tidak ada eigenvalue, magnitude, atau gap.
- Tidak ada klaim nol, `sigma=1/2`, critical-line lock, RH/GRH, global
  positivity, faktorisasi, RSA/ECC, Anderson, atau fisika.
- Tidak ada kampanye tersegel yang dijalankan ulang.
- `AD HOC NEGATIVE` adalah hasil eksperimen, bukan klaim bahwa
  `L(s,chi)` tidak positif.
