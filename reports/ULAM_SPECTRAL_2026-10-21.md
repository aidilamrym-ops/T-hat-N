# Sertifikat spectral closure Ulam finite for peta skew tent chaotik â€” 2026-10-21

**Status:** `PASS` (CI run `39460603962`, commit `2ad4228`, conclusion
`success`).
**Paket:** item 5 dari
[`reports/FIVE_CORE_BLUEPRINT_TRIAGE_2026-10-20.md`](FIVE_CORE_BLUEPRINT_TRIAGE_2026-10-20.md).
**Pra-registrasi:** [`reports/PREREG_ULAM_SPECTRAL_2026-10-21.md`](PREREG_ULAM_SPECTRAL_2026-10-21.md)
(`sha256LF b07e3aba4ead7a3676db10b3ccfb204265eba1ef61eb31d9f17caebe3078f82d`,
commit `7cfbca5`).

## 1. Ringkasan result

Paket finite ini membangun matriks Ulam **exact-rational** for peta
skew tent penuh-cabang on dua dimensi, lalu menghitung enclosure
eigenvalue with `arb_mat.eig` on tangga presisi
`64, 128, 256, 512, 1024` bit. Kedua instance memberi verdict **`PASS`**:

- matriks exact, nonnegative, row-stochastic, non-simetris, full rank;
- `rank(P - I) = N - 1` and `discriminant(charpoly) != 0`, sehingga
  eigenvalue Perron `1` simple and seluruh spektrum simple;
- eigensolver interval mengembalikan tepat `N` eigenvalue in setiap rung;
- tepat satu eigenvalue memuat `1`; semua eigenvalue lain memiliki
  `abs_upper < 1`;
- target lebar `1e-25` tercapai pertama in **128 bit**;
- lebar menurun ketat sampai `5.70e-307` (`N=16`) and `1.15e-306`
  (`N=32`) on 1024 bit;
- `ResolutionAlarm` no terpicu on jalur kampanye; alarm sintetis
  diuji fail-closed in guard.

Verdict ini adalah **sertifikat matriks Ulam finite**, bukan klaim tentang
operator transfer kontinu, ergodisitas, mixing, or kontraksi Newton.
`newton_contraction_tested = false` dicatat eksplisit.

## 2. Peta and matriks Ulam

Untuk `N >= 2`, breakpoint rasional

```text
p_N = N / (2(N+1)).
```

Peta skew tent penuh-cabang:

```text
T_N(x) = x / p_N                    for 0 <= x <= p_N,
T_N(x) = (1 - x) / (1 - p_N)        for p_N <= x <= 1.
```

Kedua cabang memetakan ke `[0,1]`, with slope mutlak

```text
a_N = 1/p_N     = 2(N+1)/N,
b_N = 1/(1-p_N) = 2(N+1)/(N+2),
```

and keduanya > 1. Partisi seragam `I_i = [i/N,(i+1)/N]`. Matriks Ulam
with baris = interval asal and kolom = interval tujuan:

```text
P_ij = |I_i âˆ© T_N^{-1}(I_j)| / |I_i|
     = N * |I_i âˆ© T_N^{-1}(I_j)|.
```

Preimage eksplisit:

```text
T_N^{-1}(I_j) =
  [ p_N j/N, p_N (j+1)/N ]
  âˆª
  [ 1 - (1-p_N)(j+1)/N, 1 - (1-p_N)j/N ].
```

Semua endpoint rasional; setiap entri dihitung sebagai `Fraction` exact.
Tidak ada float or `arb` in lapisan konstruksi matriks.

## 3. Konfigurasi which dikunci

| Peran | `N` | `p_N` | slope kiri | slope kanan |
|---|---:|---:|---:|---:|
| Primer | 16 | `8/17` | `17/8` | `17/9` |
| Replikasi | 32 | `16/33` | `33/16` | `33/17` |

| Parameter | Nilai |
|---|---:|
| Target lebar eigenvalue | `1e-25` |
| Tangga presisi | 64, 128, 256, 512, 1024 bit |
| Eigensolver | `arb_mat.eig(multiple=True, algorithm="rump")` |
| Budget attempt | 60 |
| Cap presisi | 1024 bit |

Ladder memakai **5 dari 60** attempt. Angka 60 adalah limit attempt
resolusi, **bukan** 60 iterasi Newton. Jalur Newton no diimplementasikan
and no diklaim.

## 4. Lapisan exact

| Besaran | `N=16` | `N=32` |
|---|---|---|
| Matrix SHA-256 | `16ba75523f3a5ee0351dc226325342ea5e9b24753fd09b2e89a617b5bc28ade8` | `96236555230c87bab8c951d002a8ed20931cb884b355508c17ac8242be8ab396` |
| `rank(P)` | 16 | 32 |
| `rank(P-I)` | 15 | 31 |
| Determinan | `203212800/2862423051509815793` | `425479634944000000/1843706170846276747857062870605259735097` |
| Charpoly SHA-256 | `473e90cb405cfa452f5da7604b1217c2124b7acf3cdfb0fd89f62b3fbff134fd` | `d32ddcf8e41fa2ce706d3f7a0bc6fd8afe4c128b9bcc66b8fc6f80b0adc2e479` |
| Diskriminan charpoly | nonzero, tanda `+` | nonzero, tanda `-` |
| Entri nonzero | 46 / 256 | 94 / 1024 |
| Pasangan asimetris `i<j` | 41 | 90 |

Pemeriksaan exact which semuanya `true`:

- `C1_nonnegative`;
- `C1_row_stochastic` (setiap baris berjumlah tepat 1);
- `C1_nonsymmetric` (ada pasangan `P_ij != P_ji`);
- `C1_full_rank` (`rank(P)=N`);
- `C1_perron_simple` (`rank(P-I)=N-1`);
- `C1_squarefree` (`discriminant != 0`).

`rank(P-I)=N-1` memberi bahwa eigenvalue `1` memiliki multiplisitas
aljabar satu; diskriminan nonzero memberi bahwa seluruh eigenvalue simple.
Ini adalah fakta exact tentang matriks finite, bukan tentang operator
kontinu.

## 5. Tangga enclosure spektral

Lebar rung didefinisikan sebagai

```text
w(bits) = max_k max(rad(Re Î»_k), rad(Im Î»_k)).
```

### 5.1 Instance primer `N=16`, `p=8/17`

| Presisi | `w(bits)` | `max abs_upper` non-Perron | `1 - max abs_upper` | target `1e-25` |
|---:|---|---:|---:|---|
| 64 | `6.31116690636331979349427957759e-18` | `0.386933032680479977968076438222` | `0.613066967319520022031923561778` | no |
| 128 | `3.10427204587030327159557855871e-37` | `0.386933032680479976368322441313` | `0.613066967319520023631677558687` | ya |
| 256 | `9.80267846785866507658477974166e-76` | `0.386933032680479976368322441313` | `0.613066967319520023631677558687` | ya |
| 512 | `8.74323930538747816586116088920e-153` | `0.386933032680479976368322441313` | `0.613066967319520023631677558687` | ya |
| 1024 | `5.69818735325730332153036496334e-307` | `0.386933032680479976368322441313` | `0.613066967319520023631677558687` | ya |

Eigenvalue Perron berada in indeks solver `0` on semua rung; tepat satu
enclosure memuat `1`. Target pertama tercapai in **128 bit**.

### 5.2 Instance replikasi `N=32`, `p=16/33`

| Presisi | `w(bits)` | `max abs_upper` non-Perron | `1 - max abs_upper` | target `1e-25` |
|---:|---|---:|---:|---|
| 64 | `9.67219903066706220473832734431e-18` | `0.404643695810857524072573151996` | `0.595356304189142475900321793691` | no |
| 128 | `5.10321652451993165972149250526e-37` | `0.404643695810857523170248435944` | `0.595356304189142476829751564056` | ya |
| 256 | `1.86561833903030126126113950203e-75` | `0.404643695810857523170248435944` | `0.595356304189142476829751564056` | ya |
| 512 | `1.43246585782921310350575175514e-152` | `0.404643695810857523170248435944` | `0.595356304189142476829751564056` | ya |
| 1024 | `1.15252761100602663347533850672e-306` | `0.404643695810857523170248435944` | `0.595356304189142476829751564056` | ya |

Sama seperti instance primer: satu Perron, semua non-Perron `< 1`, target
pertama in **128 bit**.

### 5.3 Kontraksi and alarm

Untuk kedua instance, lebar menurun ketat antar-rung:

```text
upper(w(bits_{k+1})) < lower(w(bits_k))   for semua k.
```

Rasio penurunan dari 64 ke 128 bit sekitar `2e19`; dari 128 ke 1024 bit
mencapai sekitar `1e270`. Ini adalah kontraksi **presisi eigensolver**,
bukan kontraksi Newton.

`ResolutionAlarm` dilempar bila eigensolver gagal, target no tercapai
sampai 1024 bit, or lebar no menurun. Jalur kampanye nyata no
memicu alarm (`alarm_triggered=false`); guard menguji jalur gagal secara
sintetis with `pytest.raises`.

## 6. Verdict

| Kriteria | Hasil `N=16` | Hasil `N=32` | Status |
|---|---|---|---|
| C1 exact construction | semua checks `true` | semua checks `true` | PASS |
| C2 semua rung eigensolver | 5/5 | 5/5 | PASS |
| C2 target `1e-25` | pertama 128 bit | pertama 128 bit | PASS |
| C2 kontraksi ketat | 4/4 transisi | 4/4 transisi | PASS |
| C3 alarm fail-closed | no terpicu | no terpicu | PASS |
| C4 receipt deterministik | dua run identik | dua run identik | PASS |
| **Total** | status `PASS` | status `PASS` | **PASS** |

Receipt kanonik:

```text
verdict          PASS
canonical sha256 4a850532be255fd0f68a55d529c12d3406696b50e281997daba20528dcb883ac
```

## 7. Interpretasi which diizinkan

Yang benar-benar disertifikasi:

1. Matriks Ulam exact for dua instance skew tent penuh-cabang.
2. Spektrum simple and Perron eigenvalue `1` simple secara exact.
3. Enclosure interval for seluruh eigenvalue matriks finite on lima
   presisi.
4. Spectral gap interval positif: `> 0.6130` (`N=16`) and `> 0.5953`
   (`N=32`) berdasarkan `1 - max abs_upper`.
5. Target lebar `1e-25` tercapai on 128 bit and bertahan hingga cap
   1024 bit.
6. Alarm resolusi fail-closed berfungsi.

Yang **no** diklaim:

- bahwa spektrum Ulam `N=16/32` adalah spektrum operator transfer kontinu;
- bahwa peta memiliki ergodisitas global, mixing, or invariant density
  kontinu which telah dibuktikan;
- bahwa lebar eigenvalue adalah error discretization operator;
- bahwa ada kontraksi Newton 60 iterasi;
- bahwa result ini berlaku for peta logistic, semua peta chaotik, or
  limit `N -> âˆž`;
- bahwa ada hubungan with RH, lokasi nol, `Ïƒ=1/2`, faktorisasi, RSA/ECC,
  Anderson, or fisika.

## 8. Mengapa skew tent, bukan logistic r=4

Blueprint menyebut logistic `r=4` sebagai contoh. Paket ini memakai skew
tent penuh-cabang karena dua alasan which dapat diaudit:

1. breakpoint rasional and slope rasional memberi entri Ulam **exact**;
2. partisi seragam menghasilkan matriks full-rank with spektrum simple
   on kedua instance.

Logistic `r=4` with partisi seragam memiliki struktur dua-cabang simetris
which membuat matriks Ulam rank-deficient with klaster eigenvalue nol;
`arb_mat.eig` no dapat mengisolasi klaster tersebut on instance uji.
Itu adalah keterbatasan metode finite for instance itu, bukan klaim bahwa
logistic no chaotik. Paket ini no membuat klaim spektrum logistic.

## 9. Artefak and verifikasi

- Modul: `msaf/ulam_spectral.py` â€”
  `sha256LF 0b722f6402142235cc40ff4e3a62d1b0c7d589df813cf07565e88c352ac7a0ff`
- Guard: `msaf/tests/test_ulam_spectral.py` â€”
  `sha256LF 7729ad2f5566b05c5baec96f58584bcddf55fcfe7626f25cd5a815e38650fa2d`
- Prereg: `reports/PREREG_ULAM_SPECTRAL_2026-10-21.md` â€”
  `sha256LF b07e3aba4ead7a3676db10b3ccfb204265eba1ef61eb31d9f17caebe3078f82d`
- Receipt: `reports/ulam_spectral_2026-10-21.json` â€”
  `sha256LF 5b2cc32a795053fdac13e12e1f7e4cf763c7a46aacc8113b280268d9766903b7`
- Receipt kanonik:
  `4a850532be255fd0f68a55d529c12d3406696b50e281997daba20528dcb883ac`
- Runtime kampanye lokal: **4.01 s**.
- Guard baru: **9 tests**, lulus **7.25 s**.
- Suite penuh: **489 passed** dalam **238.31 s**.
- Freeze: `verify OK: 14 pins`; digest
  `f6352884d85bab5a68c01a4e1d4a73618304464fd300d56bce1f8cc2f62baa25`.
- CI run `39460603962` (commit `2ad4228`) **success**: `python-tests`
  49 s, `coq-kernel` 2m10s, `lean-kernel` 2m35s.

Perintah reproduksi:

```bash
python -m msaf.ulam_spectral --out reports/ulam_spectral_2026-10-21.json
python -m pytest msaf/tests/test_ulam_spectral.py -q
python -m pytest msaf -q
python audit_quantum/freeze.py --verify
python -m pytest msaf/tests/test_fence_registry.py -q
```

## 10. Hubungan with item 2 and item 4

Item 2 (`A-2026-0022`) adalah sertifikat exact permutasi `Z_N^Ã—`; item 4
(`A-2026-0023`) adalah benchmark statistik RBM Anderson. Paket item 5 ini
no bergantung secara logis on keduanya. Kesamaannya hanya disiplin:
pra-registrasi terpisah, lapisan exact/ball which dipisahkan dari klaim,
receipt deterministik, guard CI, and limit eksplisit.

## 11. Batas penutup

`PASS` in sini berarti **kedua instance matriks Ulam finite which dikunci
lolos C1â€“C4**. Ia bukan peer review, bukan sertifikat operator kontinu,
bukan klaim ergodisitas/mixing, and bukan klaim Newton. Tidak ada
kampanye quantum/H1/engine-B which dijalankan ulang, and no ada artefak
beku which diubah.


