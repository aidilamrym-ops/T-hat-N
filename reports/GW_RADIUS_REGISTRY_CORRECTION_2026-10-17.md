# Koreksi terukur: klaim "radius tepat nol" / "Im bocor tepat nol" on tangga Route A2 (c=13)

Ditulis 2026-10-17. Status: **koreksi note terdokumentasi** â€” bukan result
baru, bukan perubahan verdict. Tidak ada angka result tersegel which berubah;
no ada komputasi dimensi besar which dijalankan ulang for koreksi ini
(ukur ulang on dim 17/33, c=13, 6000 bit â€” biaya detik).

## 1. Klaim lama which dikoreksi

1. `reports/THREE_TASKS_2026-10-15.md` Â§"Jalur which benar: eigensolver
   interval": *"Radius **tepat nol**: setiap eigenvalue terisolasi titik
   on presisi ini, and no satu pun enclosure-nya memuat nol. Bocoran
   imajiner **tepat nol**, jadi 'semua real' diukur, bukan diasumsikan."*
2. `reports/HANDOFF.md` Â§2.0b: *"radius **tepat nol**, Im bocor **tepat
   nol**"*; and bullet 9000-bit: *"radius tetap 0"*.
3. `reports/THREE_TASKS_2026-10-15.md` Â§"9000 bit": *"radius tetap 0"*.
4. Dashboard v5 (`reports/gw_diagnostic_v5.html`): caption Panel 1 *"with
   radius exactly 0"*, note Panel 7 *"radius exactly 0"*, and tooltip
   grafik (warisan v4) *"enclosure radius = 0.0"*.
5. Field JSON `lambda_min_rad` / `imag_leak_upper` = `0.0` on
   `reports/lambda_min_eig_ladder*.json`.

## 2. Yang diukur ulang (2026-10-17)

Skrip: `msaf/gw_radius_registry_check.py` (c=13, 6000 bit, dim 17 and 33;
transkrip verbatim in Â§4 and in `reports/gw_radius_diag_2026-10-17.log`).

* **Radius enclosure sejati BUKAN nol.** `float(lo.rad().abs_upper())`
  mencatat 0.0 karena radius ~1e-1790 jauh in bawah lantai subnormal
  float64 (~4,9e-324). Terukur: 4,73e-1792 (dim 17) and 5,37e-1788
  (dim 33); `is_exact() = False` â€” no ada enclosure which berupa titik.
* **Kebocoran imajiner BUKAN nol.** `imag_leak_upper` adalah artefak
  underflow which sama; leak maksimum terukur 1,97e-1792 (dim 17) and
  7,06e-1789 (dim 33); 0/17 and 0/33 section imajiner eksak nol.
* **Realness tetap sah, tetapi sebagai sifat struktur (terukur), bukan
  dari leak nol.** Matriks bola **simetris eksak** â€” uji eksak-dyadic
  mid/rad: 0/289 and 0/1089 entri berbeda (dim 17/33). Untuk matriks
  simetris, eigenvalue sejati real; leak imajiner solver adalah noise
  pembulatan in level radius bola.
* **Konten tersertifikasi no berubah:** `contains0(lo) = False` in
  semua kasus; verdict ladder tetap "CERTIFIED, all eigenvalues strictly
  positive"; eksklusi nol tetap which disertifikasi, bukan field float.
* **Jebakan tooling (dicatat):** `arb == arb` in python-flint menguji
  kesamaan **eksak** saja â€” `(arb(1)/3) == (arb(1)/3)` mengembalikan
  `False` for bola inexact. Uji simetri/kesamaan bola wajib lewat
  midpoint/radius eksak; `A == A.T` which `False` BUKAN bukti asimetri.
* **Preseden kernel:** `msaf/evolution.py` (baris 335â€“338) already
  mendokumentasikan kelas kesalahan which sama â€” radius < 1e-308 which
  ditulis sebagai angka JSON binary64 "manufacturing an exact zero that
  the measurement never produced". JSON ladder jatuh ke jebakan itu;
  prosa kemudian membacanya sebagai "tepat nol".

Untuk dim 65/129/257 (and rung berikutnya): field 0.0 dijelaskan oleh
mekanisme underflow which sama (no diukur ulang â€” biaya; no ada klaim
baru per-dimensi).

## 3. Apa which berubah setelah koreksi

* Wording in HANDOFF, THREE_TASKS (note bertanggal; riwayat no
  dihapus), README Â§6.3, and dashboard v5 (caption + note + tooltip;
  +1 patch deterministik â†’ total 15).
* Angka result, verdict, and hash artefak result no berubah. Tidak ada
  klaim baru tentang nilai Î»_min itu sendiri.
* `reports/gw_diagnostic_v4.html` tetap preserved byte-identik; tooltip
  lamanya sengaja no diubah (snapshot tersegel â€” koreksi hidup in v5 +
  dokumen ini).

## 4. Blok mesin verbatim

```
semantics: (arb(1)/3) == (arb(1)/3) -> False   (exact-equality-only semantics; use mid/rad tests instead)
semantics: x.mid() == x.mid() -> True ; arb(2) == 2 -> True
dim 17: n=17  float(rad)=0.0  is_exact(lo)=False  contains0(lo)=False
  ball-symmetry (exact-dyadic mid/rad test): mid-diff entries 0/289, rad-diff entries 0/289 -> EXACTLY SYMMETRIC as a ball matrix
  radius lo   = +/- 4.73e-1792 (repr tail, verbatim)
  radius hi   = +/- 3.42e-1792 (repr tail, verbatim)
  exact real parts in the whole spectrum: 0/17
  imag parts exactly zero: 0/17  max leak = 1.9719203792027645216574268722527256972064071291493557805199454517198272543810543094020423513865782867919479206177319160988407216419477326483442339212262601511485016783777875963465401781289802715962936426392440779920299085934933143673862420585332019043362120919245735002833979388631628029995253454667906000771100295065025548836040772972438185625510955863059960957106068745562803725442868105031247803443542400167683350888967997904429042194929434902089838395320477482647872768625328973271463984443429494348942315552697985368803423053236008520138864165426246747888752296387427680773699774543997190412374218917962538571188621972800302017899973746299105410200273538481845664240681248573894999616844038632429853496907895093910845859966663639295636496108034923137019048901344785115083426692865623666162696496240820822518195893066396735707732544447236103744437189076089566790484167773224065150134047845958882542122638623687760934645261615770095139096600238064734081831466483670656310204265679798731927172818947328409234725425554727681077433453200792649454268953385653614064398822607751829100694679053123535227821820619471165818701457685288852771009630806661387079355952270621678294829698501245200623494079076777025804014706271500004989563406609984018646405619615278238128369961266156332114975992568743295796298094064286965114389329379585138646329878971113843986448623462306743979783317823299674920850412034683410441181773953944221402337217567667621180691399354262676236792877563484438772108360400513926881028417295476315321793627389972799697993086035280176570551284707690499819588372800206342254762415029238296344655700530835330376049958470299369085780853804560842054486430508197770501623410475209779279009873786925480012289611611870431760014260872992070006139715394459991017179136028786908284828800207858352028022e-1792 (float registry = 0.0)
dim 33: n=33  float(rad)=0.0  is_exact(lo)=False  contains0(lo)=False
  ball-symmetry (exact-dyadic mid/rad test): mid-diff entries 0/1089, rad-diff entries 0/1089 -> EXACTLY SYMMETRIC as a ball matrix
  radius lo   = +/- 5.37e-1788 (repr tail, verbatim)
  radius hi   = +/- 1.43e-1788 (repr tail, verbatim)
  exact real parts in the whole spectrum: 0/33
  imag parts exactly zero: 0/33  max leak = 7.0570119639826919472860922484101660049723469328007876235327257831289719440131389967461293388335878839380263208519097999314480793671323303304790516043051785728877742216276233426793268296026732318031080220624507394547732471787714099360242979365618282367413906302250684309590450123048756703570783241012243606833957010022827262892668644120201659441260644176071675783198298450662472997002787886105226949193387933923224851116960740511717166630283822052201336408324304659227361140355065766298293526126294083126999618930900901315467452934418939548716150357357311001413661625412048079486472598704416420368846686485247564399573697241012717435234695961548342832718614503927715133359646961256179908488427056371548322464326856619405877586163477320964057298359711396460395141218480798101218268529365224230443206374943917237416579619253016115620420523176255560053491182647450890085375526473187831681308126415585697873461512277977722948671352106967871791214463053677148335997737144883677282274007388819941144926353800951321813621665253811266859808995221519167680308647062859780457512520351676834342735677454344628552041037956809724752239647038476286190831529419426675674518532756350284341822796567006631208878596644643718227387340626422143437790573689809049568061916656482661328365451049916138904985713267363313453479715517957166777657281822051778376878940294091954513957528637231126772782521638794786837611863110952450295100357910121791954527632882771199693502629050280768221565929408288246349571343644482705006676308862621638284729011483803732541499917260146818043839756775871930277638325051570587055610872417343957161096715289862603609412945356014632022521765653193209986999350354945812622818715563667375495075242827782494707998983235689071071940933514626049621447794125111220868343626017138937579273170860059464399324e-1789 (float registry = 0.0)
```

## 5. Berkas terkait

* `msaf/gw_radius_registry_check.py` â€” skrip pengukuran ulang (dapat
  dijalankan ulang; ASCII, aman for CI tanpa flint karena impor flint
  ada in dalam `main()`).
* `reports/gw_radius_diag_2026-10-17.log` â€” transkrip verbatim.
* `msaf/evolution.py` baris 335â€“338 â€” preseden kelas kesalahan.
* `reports/THREE_TASKS_2026-10-15.md`, `reports/HANDOFF.md`, `README.md`
  Â§6.3, `reports/gw_diagnostic_v5.html` â€” lokasi koreksi.


