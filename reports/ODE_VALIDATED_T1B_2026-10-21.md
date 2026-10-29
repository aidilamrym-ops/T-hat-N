# T1b - Integrator ODE tervalidasi: propagasi blok bertanda - 2026-10-21

**Verdict: ALL PASS** (C1-C7 PASS; guard C6 lengkap with mutasi M1-M5).
Sesuai pra-registrasi Â§5, entri registry `A-2026-0040` **created** with
sertifikat `sha256LF`. T1 (FAILED, `reports/ODE_VALIDATED_2026-10-21.md`)
tetap berlaku sebagai rekaman historis and no diubah; modul T1
`msaf/ode_validated.py` tetap beku with hash which sama.

T1b mengganti **mekanisme propagasi ketidakpastian** (radius skalar per
step -> himpunan bertanda with respons linear eksplisit) tanpa
mengubah sistem, konfigurasi, or toleransi T1. Yang disertifikasi tetap
**mesin enclosure**, bukan fisika; ini bukan bukti formal Lean; ini bukan
bukti keberadaan/stabilitas orbit figure-eight apa pun (lihat Â§10).

| Acuan | Nilai |
|---|---|
| Pra-registrasi | `reports/PREREG_ODE_VALIDATED_T1B_2026-10-21.md` |
| sha256LF pra-registrasi (setelah Â§12; dipinjam in receipt) | `921a502d7c8663bdad22e779a22ac7c8a6ba7b2755c7f166bd657ce2dfcfa2d2` |
| Linieage pra-registrasi | `79a4e87965cdc1682d4fa5ddb38cd2719201e316ddba1f2b32004c8379c9b0b1` (versi awal commit `8d4b261`, disebut in Â§10) -> `9e77aaa1823bf5773eac545bb8930ab47622726e189e25b3d27c3dc933ba7c67` (setelah Â§10, commit `1922684`) -> `fd31210f7e5ad6e19f6f3a1aa5776ee108276bafa306d29bd87860ca5cf0a04d` (setelah Â§11, commit `d9da2a0`, sebelum kode T1b; sesuai note Â§2.0bj HANDOFF) -> `921a502d7c8663bdad22e779a22ac7c8a6ba7b2755c7f166bd657ce2dfcfa2d2` (setelah Â§12, sebelum kampanye bersertifikat) |
| Modul T1b | `msaf/ode_validated_block.py` |
| sha256LF modul T1b | `42d196a51c5ae45e3b87b8c1e36319abfeb93df776b3c2317e812f7c2c0b5b97` |
| Modul T1 beku (diimpor, no diubah) | `msaf/ode_validated.py` |
| sha256LF modul T1 | `c1d9b5d60036a5f0772f7e3f1b8c78969efaa7146a713c762531ddce346251b9` |
| Guard | `msaf/tests/test_ode_validated_block.py` |
| sha256LF guard | `0c2e50bf4d2fb56bb562db56d7611a0fc9d2d3b50f9cbe7cbc522daf36b1518d` |
| Receipt | `reports/ode_validated_t1b_2026-10-21.json` |
| sha256LF receipt | `fa2c27f045a299231b45135bd85c1a6db5ae8cab5a327ab2454072a65e3daaf8` |
| Determinisme | dua run `python -m msaf.ode_validated_block` berturut-turut identik byte (hash sama); guard mererun kampanye penuh and payloadnya cocok byte with receipt |
| Lingkungan | Python 3.14.4, `python-flint` 0.9.0, `flint.ctx.workprec(256)`, orde 24, `kappa_nl = 1e18` |

## 1. Ringkasan result

| Kriteria | Hasil | Angka verbatim utama |
|---|---|---|
| C1 primitif bola | **PASS** | 2.000 kasus, `failures: []` |
| C2 step Taylor S1 | **PASS** | orde 16: lebar `5.138763746119934803636026189897550650598212484965188195928931236267089843750e-20` (<= `1e-12`), memuat 2; orde 24: `[7.224694168684901095634572581555194915764176417314603936836725495140854036435e-30 +/- 4.85e-106]` (<= `1e-18`), memuat 2; rasio lebar `~7.1e9` >> `1e4` |
| C3 osilator harmonik S2 | **PASS** | 32 step: memuat `(-1,0)`, lebar `1.808211958078260972915916839732455940079384011420334996703789896929662478812e-49` / `2.706615176271856931474388239987522389755125846385266026246933091608958485216e-49`; 64 step: memuat `(1,0)`, `3.616423916156521945831833679464911880158768022840669993407579793859324957624e-49` / `5.413230352543713862948776479975044779510251692770532052493866183217916970433e-49` (<= `1e-20`) |
| C4 Kepler sirkular S3 | **PASS** | 10/10 checkpoint (256..2560): semua `energy_ok`/`angular_ok`/`width_ok` true; lebar energi maksimum `[4.490592590381955201797400852730644345643499799197728705735244147945195436478e-25 +/- 3.39e-101]` (<= `1e-12`); checkpoint 1024 (titik gagal T1: `1.388201187303098743663909431234060321003198623657226562500000000000000000000e-11`) kini `1.259481798924398876545007804758425848459962735748019705164682012304110114709e-34`; `error: null` |
| C5 three-body S4 (RHS) | **PASS** | 8/8 checkpoint (64..512): `energy_ok`/`angular_ok`/`com_ok`/`width_ok` true; lebar energi maksimum `[5.259447368674909888295650856740895431940379105457961106395714523387141525745e-26 +/- 3.92e-102]` (<= `1e-10`); `error: null` (T1 abort in step 42) |
| C6 determinisme/integritas | **PASS** | receipt identik byte antar dua run (sha256 `fa2c27f0...`); guard `msaf/tests/test_ode_validated_block.py`: 8/8 tes lulus (kampanye penuh direrun, 209.99 s, payload cocok byte); mutasi M1-M5 semuanya GAGAL sebagaimana mestinya; `ast_scan_hits: []` on kedua modul |
| C7 pembeda mekanisme (M5) | **PASS** | mekanisme T1 beku direproduksi verbatim: S3 `aborted at step 1557: ValidationError: Picard enclosure failed` (= limit 1557), S4 `aborted at step 42: ValidationError: Picard enclosure failed` (= limit 42) |

Verdict mengikuti pra-registrasi Â§5: C1-C7 semuanya PASS -> `ALL PASS`,
sehingga registry `A-2026-0040` and sertifikat `sha256LF` created.

## 2. Mekanisme which berubah (ringkas; definisi in pra-registrasi Â§2, Â§10-Â§12)

- Ketidakpastian dibawa sebagai himpunan bertanda `X = m + S*xi + slack`,
  `xi in [-1,1]^m`; per step `S' = J_step * S` memakai **perkalian
  matriks interval bertanda**, bukan radius skalar `||J_step|| * r`
  (mekanisme T1 which gagal, digunakan kembali hanya oleh mutasi M5/C7).
- Sisa Taylor orde `(p+1)` dibatasi on **kotak jalur tervalidasi**
  (Â§12.1; varian kotak masukan terbukti no sound saat diagnostik and
  ditinggalkan sebelum kampanye bersertifikat).
- Sertifikat checkpoint = **satu sapuan mundur kontinu** dari step
  checkpoint sampai step 0 (`P = J_{t-1} ... J_{k+1}`), tanpa reset in
  limit blok (Â§2.4, Â§12.3); setara-aljabar with formulasi kolom tanpa
  penggabungan (Â§11.1). Hasil dicapai lewat dua pass (pass maju menyimpan
  `m_k`, kotak Picard, `rem_k`, `quad_k`, `J_k`; pass mundur mengalikan)
  with produk **midpoint-radius** (Â§12.4).
- Kotak Picard memakai inflasi `factor` which digandakan sampai cek Picard
  which sama persis lulus (Â§12.2); gerbang soundness no diubah.
- Slack per blok `kappa_nl * r_tot^2` dihitung dari radius sertifikat
  **sebelum** slack (non-referensi-diri, Â§12.5), disisipkan sebagai radius
  noise per step on bloknya, and **mengunci `passed`** `check_c4`/
  `check_c5` (kewajiban Â§2.3, bukan sekadar angka which direkam).

## 3. C1-C3 (identik T1; angka verbatim)

- **C1** - generator LCG `s_{n+1} = (1103515245*s_n + 12345) mod 2^31`,
  seed 20261021: 1.000 pasangan operasi `+ - * /` and 1.000 kasus `sqrt`
  semuanya memuat result `Fraction` eksak (`cases: 2000`,
  `failures: []`).
- **C2** - S1 `x' = x^2`, `x(0)=1`, 16 step `h=1/32`, on `t=1/2`
  (solusi eksak `x=2`): orde 16 and orde 24 keduanya memuat 2; rasio lebar
  orde 24 terhadap orde 16 `~7.1e9`, jauh melebihi `1e4`. Kontrol mutasi
  M2 (guard): tanpa remainder, `contains_2` false in kedua orde (lebar
  tersisa `3.9306595583828064e-77` / `3.929558675978935e-77`, hanya
  pembulatan) - lihat Â§8.
- **C3** - S2 `x'' = -x`, `(x(0),v(0))=(1,0)`: on `t=pi` enclosure
  `[-1.00000000000000000000000000000000000000000000000 +/- 1.03e-49]`,
  `[+/- 2.65e-49]` memuat `(-1,0)`; on `t=2pi`
  `[1.00000000000000000000000000000000000000000000000 +/- 2.06e-49]`,
  `[+/- 5.30e-49]` memuat `(1,0)`; lebar orde `1e-49` << `1e-20`.

## 4. C4 - Kepler sirkular (S3, 10 periode, 2.560 step)

Checkpoint tiap 256 step; toleransi lebar maksimum `1e-12` (energi and
momentum sudut); selang energi wajib memuat `-1/2`, momentum sudut wajib
memuat `1`. Semua `energy_ok`, `angular_ok`, `width_ok` bernilai true;
`error: null` (integrasi 10 periode penuh tanpa abort).

| Langkah | Lebar energi (verbatim) | Lebar momentum sudut | Slack `kappa_nl*r_tot^2` |
|---|---|---|---|
| 256 | `[3.148704492826842105523104884940129954622175219273211048906854561137656778325e-35 +/- 3.89e-111]` | `[3.148649126963997246270705860014802336719861883611782731018106130666932979123e-35 +/- 1.84e-112]` | `[1.6398758507773863216087324258166731759796889083711676628575871758655408209e-51 +/- 2.26e-125]` |
| 512 | `[6.297408994621994382725039023792129242299813678740098525823410061520550573544e-35 +/- 1.14e-111]` | `[6.297298253927994492541411720029604673439723767223565462036212261333865958246e-35 +/- 3.67e-112]` | `[2.4849503540525108322490052927691038402313250079514963534724372979927323845e-50 +/- 6.97e-124]` |
| 768 | `[9.446113505385456831605802416555997863032915378400662430749666501148681385658e-35 +/- 1.77e-111]` | `[9.445947376407836652972702953088472343631854030738509979049467922378180428922e-35 +/- 2.77e-111]` | `[1.2461536087095482243430986396485783551827014878177411958233562220974041151e-49 +/- 3.57e-123]` |
| 1024 | `[1.259481798924398876545007804758425848459962735748019705164682012304110114709e-34 +/- 2.23e-110]` | `[1.259459650785598898508282344005920934687944753444713092407242452266773191649e-34 +/- 2.08e-110]` | `[3.926470682673253744262349350913854366741475759537466565641938814102001745e-49 +/- 1.92e-122]` |
| 1280 | `[1.574352241929265966922137815514130310783355989539767310448576810946209880715e-34 +/- 2.57e-111]` | `[1.574324560343090063047762691138246901790518807738104615705657736597633533648e-34 +/- 3.78e-110]` | `[9.573790894573513331906126852753778905626901775232078506979044263121458796e-49 +/- 5.85e-122]` |
| 1536 | `[1.889222713632725606671521438787816638884231611951279485363514615173068100784e-34 +/- 9.29e-111]` | `[1.889189482456215467937603993747189935170741398302643138217654335871825699300e-34 +/- 7.51e-111]` | `[1.983973880864067270559649217775843270454576792127423782088473614583278703e-48 +/- 4.48e-121]` |
| 1792 | `[2.204166275270422394543558593014193502399422164786944653739167080232566608977e-34 +/- 1.52e-110]` | `[2.204127514233860398643523185914936036687298047717422795811707662318179590244e-34 +/- 2.84e-111]` | `[3.674324397986974301748682965335032498222558182452351338904628316205767572e-48 +/- 6.42e-121]` |
| 2048 | `[3.142538214580272094644797478325886341150357934527339414899964288238609633197e-34 +/- 2.94e-111]` | `[3.142485484503786691800316178098955708248690891787413289062321901943045099337e-34 +/- 1.30e-110]` | `[6.480111927069797175451956806407577710421473754179309118335825558600386155e-48 +/- 7.92e-121]` |
| 2304 | `[5.197301827605150837378166469169431445580880012639390363722406707136514114609e-31 +/- 1.29e-107]` | `[5.197231452227735045552923765873868621259956106405838364807603380057798858616e-31 +/- 4.31e-107]` | `[1.301070231753753135796310331229950132542474936308914272061675623916739696e-43 +/- 9.27e-116]` |
| 2560 | `[4.490592590381955201797400852730644345643499799197728705735244147945195436478e-25 +/- 3.39e-101]` | `[4.490531784921751007987048169395041054318198914252491249499144032597541809082e-25 +/- 3.13e-102]` | `[9.51146745745473119526150099062976831482355573694027752747131933560092598e-32 +/- 9.85e-104]` |

Selang energi on checkpoint pertama
`[-0.5000000000000000000000000000000000 +/- 1.58e-35]` and terakhir
`[-0.5000000000000000000000 +/- 2.25e-25]` keduanya memuat `-1/2`;
selang momentum sudut `[1.000000000000000000000000000000000 +/- 1.58e-35]`
sampai `[1.00000000000000000000000 +/- 2.25e-25]` memuat `1`. Sisa Taylor
terbesar per blok
`[3.758144008195213755279038435440880728101341154399661716811458018194475469025e-38 +/- 4.27e-114]`
(blok 4); bound berjalan terbesar (mid)
`1.386282169486696889755764093986968809001067842066753400653702123995114891e-27`
(blok 10).

Perbandingan with T1: setiap checkpoint S3 kini berada 10+ orde in
bawah toleransi, in mana T1 already melanggar `1e-12` in checkpoint 1024
(`1.388201187303098743663909431234060321003198623657226562500000000000000000000e-11`)
lalu abort in step 1557.

## 5. C5 - three-body RHS (S4, 1 periode, 512 step)

Checkpoint tiap 64 step; selang energi wajib memuat `E0 =
-257428899017/200000000000`, momentum sudut wajib memuat `0`, pusat massa
posisi/kecepatan wajib memuat `0`; toleransi lebar energi `1e-10`. Semua
`energy_ok`, `angular_ok`, `com_ok`, `width_ok` true; `error: null`.

| Langkah | Selang energi (verbatim) | Lebar energi (verbatim) | Selang momentum sudut | Pusat massa (4 komponen) |
|---|---|---|---|---|
| 64 | `[-1.287144495085000000000000000 +/- 3.84e-28]` | `[7.663086928879436844903979603702227418038740654497240067932750662293983623385e-28 +/- 4.30e-104]` | `[+/- 2.49e-28]` | `[+/- 1.97e-29]`, `[+/- 2.25e-29]`, `[+/- 5.18e-29]`, `[+/- 7.49e-29]` |
| 128 | `[-1.28714449508500000000000000 +/- 1.64e-27]` | `[3.274684756718239263156440041078549663163908942011687264184160994773264974356e-27 +/- 3.03e-103]` | `[+/- 1.24e-27]` | `[+/- 1.34e-28]`, `[+/- 1.46e-28]`, `[+/- 2.10e-28]`, `[+/- 3.50e-28]` |
| 192 | `[-1.28714449508500000000000000 +/- 5.07e-27]` | `[1.012526771530456417513007752787881619024899294053548848282275685050990432501e-26 +/- 1.61e-102]` | `[+/- 2.29e-27]` | `[+/- 4.33e-28]`, `[+/- 3.77e-28]`, `[+/- 9.34e-28]`, `[+/- 2.31e-28]` |
| 256 | `[-1.2871444950850000000000000 +/- 9.36e-27]` | `[1.871660895413885451980936474201002549832444017989183104866413032141281291842e-26 +/- 4.61e-102]` | `[+/- 6.04e-27]` | `[+/- 9.19e-28]`, `[+/- 1.07e-27]`, `[+/- 9.95e-28]`, `[+/- 9.91e-28]` |
| 320 | `[-1.28714449508500000000000000 +/- 1.73e-26]` | `[3.456435526312390743567494636631576575260640417103924493247291138686705380678e-26 +/- 1.77e-102]` | `[+/- 1.03e-26]` | `[+/- 1.03e-27]`, `[+/- 2.13e-27]`, `[+/- 1.94e-27]`, `[+/- 2.17e-27]` |
| 384 | `[-1.28714449508500000000000000 +/- 2.21e-26]` | `[4.417438284041469178718956055357017007180471881728350824758422277227509766817e-26 +/- 9.29e-103]` | `[+/- 1.43e-26]` | `[+/- 2.30e-27]`, `[+/- 2.06e-27]`, `[+/- 2.37e-27]`, `[+/- 3.90e-27]` |
| 448 | `[-1.28714449508500000000000000 +/- 2.63e-26]` | `[5.259447368674909888295650856740895431940379105457961106395714523387141525745e-26 +/- 3.92e-102]` | `[+/- 1.74e-26]` | `[+/- 2.63e-27]`, `[+/- 2.77e-27]`, `[+/- 2.82e-27]`, `[+/- 3.73e-27]` |
| 512 | `[-1.28714449508500000000000000 +/- 2.01e-26]` | `[4.008536032716973013206506706459176513798501142495089855088963304297067224979e-26 +/- 4.01e-102]` | `[+/- 1.35e-26]` | `[+/- 1.77e-27]`, `[+/- 4.46e-27]`, `[+/- 4.82e-27]`, `[+/- 2.17e-27]` |

Sisa Taylor terbesar per blok (blok 5)
`[4.399927468131312423176601411015924837644305381462064611355982478329403347467e-30 +/- 1.85e-106]`;
bound berjalan terbesar (mid, blok 8)
`6.668022502333399424158472906588592021993463222506977634398158000916170809e-26`.
S4 tetaplah **data uji stress for RHS**, bukan klaim orbit periodik
figure-eight (pra-registrasi Â§3, Â§8); which disertifikasi adalah enclosure
terhadap `E0`, `L0 = 0`, and pusat massa `= 0` which diketahui eksak.

## 6. Kewajiban Â§2.3: `kappa_nl * r_tot^2 <= 1e-30` per blok

Ambang `1e-30` dikunci (Â§2.3) and kini **mengunci `passed`** `check_c4`/
`check_c5` (Â§12.5). Receipt merekam `slack` for setiap blok; semua nilainya
in bawah ambang:

- S3 (10 blok): dari `[1.6398758507773863216087324258166731759796889083711676628575871758655408209e-51 +/- 2.26e-125]`
  (blok 1) naik monoton sampai maksimum blok 10
  `[9.51146745745473119526150099062976831482355573694027752747131933560092598e-32 +/- 9.85e-104]`
  (margin `~10.5x` terhadap ambang - lihat note jujur Â§10).
- S4 (8 blok): maksimum blok 6
  `[3.383707261598853680946110591789996036372725241384919026248304153922956054e-35 +/- 1.54e-108]`
  (margin `~3e4`); semua `slack_ok: true` in kedua sistem
  (`section2_3_slack_ok: true`).

Catatan jujur tentang angka Â§12.3: amendemen Â§12 ditulis saat jalur
diagnostik (sebelum kampanye bersertifikat) and menyebut slack maksimum S4
`9.724087015952757e-36`. Pada receipt final angka itu identik with slack
**blok 5**, tetapi maksimum keseluruhan S4 adalah blok 6
(`3.383707261598853680946110591789996036372725241384919026248304153922956054e-35`).
Ambang Â§2.3 no berubah (`1e-30`); ketiga angka sama-sama jauh in bawah
ambang, jadi verdict no terpengaruh. Pra-registrasi no diubah
setelahnya (hash `921a502d...` dipinjam receipt).

## 7. C7 / M5 - reproduksi kegagalan T1 oleh mekanisme beku

Mekanisme T1 (propagasi radius skalar per step, diimpor dari modul beku
`msaf/ode_validated.py` tanpa modifikasi) dijalankan on konfigurasi which
sama persis and mereproduksi kegagalan T1 verbatim:

- S3: `"aborted at step 1557: ValidationError: Picard enclosure failed"`
  (= limit `C7_LIMIT_S3 = 1557`); and
- S4: `"aborted at step 42: ValidationError: Picard enclosure failed"`
  (= limit `C7_LIMIT_S4 = 42`).

`c4_reproduced: true`, `c5_reproduced: true`. Dengan itu diagnosis T1
(inflasi eksponensial limit norma skalar per step, bukan pelanggaran
containment) terkonfirmasi, and mekanisme bertanda T1b-lah pembedanya:
kedua sistem which sama kini lulus penuh (Â§4, Â§5). Bila M5 no
mereproduksi kegagalan itu, verdict T1b wajib INCONCLUSIVE (Â§5); itu no
terjadi.

## 8. C6 - guard, mutasi M1-M5, determinisme

Guard `msaf/tests/test_ode_validated_block.py` (8 tes, semuanya lulus;
kampanye penuh direrun in dalam guard, 209.99 s):

- **Kampanye vs receipt**: rerun `run_campaign()` menghasilkan payload which
  **identik byte** with receipt tersimpan (and payload kanonik
  `json.dumps(sort_keys, separators)` hash-nya sama). Bersamaan with
  identitas byte dua run berturut-turut (sha256 receipt
  `fa2c27f045a299231b45135bd85c1a6db5ae8cab5a327ab2454072a65e3daaf8`),
  ini menutup kewajiban determinisme dua run.
- **M1 (endpoint in luar selang)**: satu endpoint interval C2 orde 24
  digeser sehingga nilai eksak `2` keluar dari selang -> `contains` false
  (kontrol jujur: selang asli `contains` true).
- **M2 (remainder = 0 on C2)**: `check_c2` with remainder dimatikan ->
  `passed` false; `contains_2` false in kedua orde (lebar tersisa hanya
  pembulatan `~3.93e-77`); kontrol jujur (remainder aktif) `passed` true.
- **M3 (ubah `E0` in receipt)**: pembawa `E0` on receipt
  (`[-1.287144495085000000000000000 +/- 3.84e-28]`, checkpoint C5 step
  64) dimanipulasi -> payload kanonik no lagi cocok with kampanye
  segar; perbandingan payload mendeteksinya.
- **M4 (suntik `float(`/`math.`)**: menambahkan `return float(x)` and
  `import math` ke salinan modul ditolak pemindai AST
  (`name:float:800`, `import:math:798`); kedua modul asli bersih
  (`ast_scan_hits: []`).
- **M5 = C7** (Â§7).
- **Gerbang Â§2.3**: with `slack_ok` dipalsukan false (serta seluruh cek
  konservasi tetap true), `check_c4`/`check_c5` mengembalikan `passed`
  false; with `slack_ok` true, passed true - kewajiban Â§2.3 no bisa
  diam-diam dibuang dari verdict.
- **Pemetaan hash**: receipt memuat `prereg_sha256lf` which cocok with
  file pra-registrasi hidup and `t1_module_sha256lf` which cocok with
  modul T1 beku (`c1d9b5d6...`).

## 9. Checklist falsifier (pra-registrasi Â§6)

| Falsifier | Status |
|---|---|
| Ada nilai eksak in luar enclosure which dilaporkan | **Tidak terjadi**: semua containment terukur (`contains_2`, `contains`, `energy_ok`, `angular_ok`, `com_ok`) bernilai true; mutasi M1 justru membuktikan detektor menolak selang which no memuat nilai eksak |
| Toleransi C2-C5 terlampaui | **Tidak terjadi**: semua lebar in bawah toleransi terkunci (Â§4, Â§5) |
| Receipt no identik byte antar dua run | **Tidak terjadi**: dua run identik byte + rerun guard identik byte (Â§8) |
| Pemindai menemukan float in jalur tersertifikasi | **Tidak terjadi**: `ast_scan_hits: []` on kedua modul; no ada `float`/`math`/`numpy`/`scipy` (AST) |
| Uji mutasi M1-M4 no gagal sebagaimana mestinya | **Tidak terjadi**: M1-M4 semuanya gagal persis sebagaimana dipersyaratkan (Â§8) |
| M5 no mereproduksi kegagalan T1 | **Tidak terjadi**: reproduksi verbatim step 1557 and 42 (Â§7) |
| Ada klaim in luar limit Â§1 | **Tidak terjadi**: limit in Â§10 report ini |

Tidak ada falsifier which terpenuhi; paket ini **no falsified** menurut
Â§6, and C1-C7 lulus penuh -> verdict `ALL PASS` menurut Â§5.

## 10. Batas and konsekuensi

- Registry `A-2026-0040` created with sertifikat `sha256LF` (Â§5, Â§7.6
  pra-registrasi); `reports/FENCE_REGISTRY.md` ditambah satu entri (entri
  lama no diubah).
- Item Daftar-B 16 (Three-Body) and 20 (Soliton): **prasyarat mekanisme**
  ("integrator ODE tervalidasi") kini terpenuhi with ALL PASS, tetapi
  pembukaan item tetap memerlukan trek and pra-registrasi tersendiri with
  kriteria masing-masing. Laporan ini **no** membuka item tersebut and
  **no** mengklaim keberadaan/stabilitas orbit figure-eight, Soliton,
  or Evans apa pun.
- S4 adalah data uji stress RHS (pra-registrasi Â§3); klaim which disertifikasi
  hanya enclosure rigor-terbatas terhadap konstanta gerak which diketahui,
  bukan periodisitas orbit.
- Catatan jujur margin: slack S3 blok 10 (`9.51e-32`) berada `~10.5x` in
  bawah ambang Â§2.3 (`1e-30`) - margin paling tipis in seluruh kampanye.
  Angka direkam apa adanya; ambang no dilonggarkan; no ada
  retry/tuning setelah result terlihat (Â§12.7-Â§12.8).
- Amendemen Â§12 ditulis **setelah** jalur diagnostik C4/C5 dijalankan for
  debug, tetapi **sebelum** kampanye bersertifikat and receipt; no ada
  toleransi, konfigurasi, ambang, or kriteria which berubah karenanya
  (posisi jujur dikutip in Â§12 pra-registrasi).
- T1 tetap `FAILED` apa adanya; modul T1, receipt T1, and report T1 no
  diubah (hash modul T1 dipinjam in receipt T1b sebagai bukti).
- Ini bukan bukti formal Lean and bukan bukti global; "terervalidasi" =
  enclosure rigor-terbatas terhadap nilai eksak which diketahui (Â§8
  pra-registrasi). Tidak ada klaim RH/GRH, faktorisasi, RSA/ECC, Anderson,
  chaos, ergodisitas, PDE kontinu/Navier-Stokes, or fisika.

## 11. Artefak

| Berkas | sha256LF |
|---|---|
| `reports/PREREG_ODE_VALIDATED_T1B_2026-10-21.md` | `921a502d7c8663bdad22e779a22ac7c8a6ba7b2755c7f166bd657ce2dfcfa2d2` |
| `msaf/ode_validated_block.py` | `42d196a51c5ae45e3b87b8c1e36319abfeb93df776b3c2317e812f7c2c0b5b97` |
| `msaf/tests/test_ode_validated_block.py` | `0c2e50bf4d2fb56bb562db56d7611a0fc9d2d3b50f9cbe7cbc522daf36b1518d` |
| `reports/ode_validated_t1b_2026-10-21.json` | `fa2c27f045a299231b45135bd85c1a6db5ae8cab5a327ab2454072a65e3daaf8` |
| `msaf/ode_validated.py` (T1 beku, no diubah) | `c1d9b5d60036a5f0772f7e3f1b8c78969efaa7146a713c762531ddce346251b9` |

Perintah verifikasi:
`python -m pytest msaf/tests/test_ode_validated_block.py -q` (mererun
kampanye penuh and membandingkan with receipt),
`python -m msaf.ode_validated_block` (menulis ulang receipt; wajib identik
byte), and `python audit_quantum/freeze.py --verify`.


