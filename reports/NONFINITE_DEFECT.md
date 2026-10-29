# Dua silent-pass in kernel penghitung nol (2026-10-15)

Ditemukan saat menimbang urutan trek berikutnya, bukan karena ada which
melihat kernel itu. Keduanya adalah kelas which paling mahal: **komputasi
which GAGAL dilaporkan sebagai result which benar**.

---

## 1. `certify()` mengesahkan `nan` sebagai nol

### Gejala

```python
>>> from flint import arb
>>> from msaf.certify import certify
>>> certify('residual', arb('nan')).verdict
'PASS-BY-ENCLOSURE: 0 lies in the residual ball'
```

### Akar

`contains_zero()` meneruskan `x.contains(0)` ke Arb tanpa memeriksa
 finiteness. Dan Arb menjawab **True** for `nan`: pustaka itu
memperlakukan "no ada informasi" sebagai "semua stuff ada in dalam".
Bukti langsung:

```
nan  -> contains_zero=True   is_finite=False
inf  -> contains_zero=False
```

Dengan `certified=True` and `exact=False`, `_classify` jatuh ke cabang
ketiga â€” `PASS-BY-ENCLOSURE`. Jadi residual which gagal dievaluasi
menghasilkan sertifikat **PASS**.

### Mengapa ini which paling merusak

`evaluate_xi` sendiri menuliskan: *"a fake root is the most damaging
possible defect in a zero-finding kernel"*. Dan inilah jalannya: bukan roots
palsu which disuntikkan lewat tabel nilai, tapi lewat residual `nan` which
mengakucontains zero. Setiap pembanding teoretis tentang penghitung nol
menjadi no berlaku, karena "nol terdeteksi" and "perhitungan gagal"
sama-sama menghasilkan PASS.

### Perbaikan

- `is_finite()` menjadi gerbang **semua** question containment in
  modul (`contains_zero`, `contains_zero_complex`,
  `contains_zero_matrix`).
- Non-finite menjawab **False**, bukan melempar exception: pemanggilnya
  ada in loop panas atas matriks and enclosure, and answer which jujur
  ("residual ini no certifying apa pun")|RD Deliverable ada in
  verdict, bukan in traceback.
- Verdict baru, `NOT_FINITE_VERDICT`, menyebut kegagalan evaluasinya
  sendiri: *"NOT a refutation and NOT a confirmation"*. Kata "FAIL:
  residual does not contain zero" saja akan menyesatkan, karena
  pembacanya akan mencatat refutasi which no pernah terjadi.
- Field baru `ZeroCertificate.finite`, karena `certified` saja no
  bisa membawa perbedaan itu. Field-nya diletakkan paling akhir â€”
  `NamedTuple` no boleh punya default sebelum field biasa; ini
  ketahuan saat runtime and already dikoreksi.

### Bukti

14 tes regresi in `msaf/tests/test_certify_nonfinite.py`:
`nan`/`inf`/`-inf` no pernah `certified`, no pernah `exact`,
verdict no pernah diawali `PASS`, jalur matriks and kompleks punya
gerbang which sama, and jalur finite which biasa no berubah (nol eksak
tetap PASS, ball which misses zero tetap FAIL).

---

## 2. `evaluate_xi` mengembalikan `nan` tepat in dua kutubnya sendiri

### Gejala

Test which tugging menjaga hal ini **lolos**:

```
test_xi_is_regular_at_zero_and_one
    assert contains_zero_complex(value - acb("0.5"))
```

and nilai `value` adalah `nan + nanj`. Dengan kata lain: guard test
meloloskan diri karena guard-nya sendiri which rusak.

### Akar

Formula harfiah in `evaluate_xi`

```
xi(s) = 1/2 * s * (s - 1) * pi^(-s/2) * Gamma(s/2) * zeta(s)
```

menghasilkan `0 * tak hingga` in s = 0 (Gamma) and in s = 1 (zeta) â€”
keduanya `nan`. Docstring lama*fungsi itu mengklaim *"No special case is
taken at s = 0 or s = 1"*; kodenya memang mengambil special case, yaitu
`return nothing`.

### Perbaikan: identitas eksak, bukan tabel nilai

1. `s * Gamma(s/2) = 2 * Gamma(1 + s/2)` â€” identik for semua s.
   Menghilangkan kutub Gamma in s = 0; prefaktor menjadi
   `Gamma(1 + t/2) * (t - 1) * pi^(-t/2) * zeta(t)`, and in t = 0 itu
   `1 * (-1) * 1 * (-1/2) = 1/2` âœ“
2. `xi(s) = xi(1 - s)` (persamaan fungsional) â€” dipakai for
   menjauhi kutub which lebih dekat: bila titik tengah real bola in atas
   1/2, bola which direfleksikan dievaluasi. Refleksi adalah isometri,
   jadi supremum `|xi - c|` â€” itulah arti enclosure â€” no berubah,
      and radius bola hasilnya juga no berubah. Kutub 0 and 1 jadi
   simetris: hanya satu dari dua titik which dievaluasi bisa dekat kutub,
   and no pernah dekat s = 1.

Tabel nilai khas would've persis cara menyuntikkan root palsu ke
penghitung nol; identitas no bisa.

### Bukti

47 tes in `msaf/tests/test_xi_identities.py`:

- xi(0) and xi(1) tepat 1/2, finite;
- **regresi nol**: in 15 titik on garis kritikal, enclosure baru
  memuat titik tengah enclosure formula lama and no lebih lebar dari
  4Ã— radii â€” sehingga hitungan tersegel no bergeser. (Formulanya
  no menyentuh `weil_search.py`, jadi artefak a_11 = 354294 no
  terkait and no diulang: 75 menit which no akan membuktikan
  apa pun.)
- tanpa `nan` in 25 titik garis kritikal (daerah kerja penghitung);
- cabang refleksi benar-benar berbeda dari cabang langsung, and keduanya benar.

### Kesalahan saya sendiri, tercatat

Uji simetri pertama menyatakan `xi(0.25+it) == xi(0.75+it)` and gagal â€”
and itu **salah asumsi**. Yang benar:

```
xi(s) = xi(1-s)              persamaan fungsional
xi(conj s) = conj(xi(s))     koefisien Taylor riil
=> xi(0.75 + it) = conj(xi(0.25 + it))
```

Angkanya persis begitu: `-4.64e-8 - 3.145e-7j` vs `-4.64e-8 +
3.145e-7j`. Kode benar, assertionsalah. Ditulis in docstring tes
karena versi which salah adalah which paling natural for ditulis, and ia
gagal with alasan which terlihat seperti kerusakan kode.

---

## 3. Residual TERBUKA: presisi global bocor antar modul tes

Ditemukan karena mengalahkannya. `msaf/tests/test_xi_identities.py`
awalnyaTNsets `ctx.prec = 200` in level modul; dua tes stres in
`test_adversarial_stress.py` lalu gagal **hanya on run penuh**
(311 â†’ 2 gagal) sementara lolos sendiri-sendiri.-fixed with fixture
which menyimpan and memulihkan presisi.

Tapi empat modul lama melakukan hal which sama persis in level modul:

- `test_convergence_order.py:16` â†’ 256
- `test_moore_premises.py:13,27` â†’ 256
- `test_sbp_correspondence.py:56,67` â†’ 256
- `test_tail_decay.py:26` â†’ 256

Suite hijau sekarang, jadi no ada kegagalan which aktif -- tapi mekanismenya
sama, and no ada which mencegah modul kelima menyusul. Perbaikan which
benar adalah satu `conftest.py` with fixture presisi which dipakai
semua modul; sengaja TIDAK dikerjakan in commit ini karena menyentuh
empat modul lain tanpa perlu, and cukup dicatat sebagai OPEN.

Koreksi 2026-10-27 (D6): verifikasi manual membantah deskripsi "in level
modul". Keenam lokasi in atas berada in dalam fungsi (indent 4, dijalankan
saat tes berjalan, bukan saat modul diimpor) and no memulihkan presisi,
sehingga kelas kebocoran lintas-modul which disebut tetap nyata.
Perbaikan direalisasi SEBAGAI `msaf/tests/conftest.py`: fixture autouse
`arb_ctx_prec_guard` menyimpan `ctx.prec` in awal setiap tes and
memulihkan nilai which sama in akhirnya, sehingga tulisan presisi which
acau in satu tes no lagi mengubah lingkungan which dilihat tes lain â€”
tanpa menyentuh badan enam modul test. Enam tulisan persisi no dihapus:
menghapusnya akan membuat result bergantung urutan eksekusi (ambient presisi
no lagi teridentifikasi), sedangkan guard menjaga nilainya eksplisit.
Validasi empiris saat diterapkan: subset 10 modul flint (186 test) hijau
sebelum and sesudah conftest ditambahkan; verdict for suite utuh adalah
job CI `python-tests` on commit ini.

---

## 4. Urutan trek: koreksi terhadap rencana sebelumnya

Rencana lama: formalkan `CORR-MOORE-COMPLEX` dulu, baru Q1 BSD.
Setelah membaca `lean/NewtonExistence.lean` baris 433-480, rencana itu
harus dikoreksi.

`moore_test` in Lean dinyatakan atas **interval â„**:

```lean
theorem moore_test (a b m : â„) (hab : a < b) (f f' : â„ â†’ â„) ...
    : âˆƒ z âˆˆ Set.Icc a b, f z = 0
```

Kesimpulannya adalah Statement tentang bilangan **real**. Tapi nol which
dihitung program ini ada in bola **kompleks** in garis kritikal. Jadi
transfer Câ†’R bukan "belum diformalisasi" â€” secara struktural mustahil
sebagai pernyataan: sertifikat interval real hanya bisa certifying nol
real, sedangkan Î¾ no punya nol real (diperiksa with aritmetika
ball: enclosure Î¾ on enam interval real, 0 no termasuk in
semuanya). Menutup "jembatan" ini berarti memformalkan **Moore or
prinsip argumen in â„‚** â€” pengembangan Lean baru, bukanjemporting.

Konsekuensi for urutan:

1. Yang **mel-blocking** and murah adalah `CORR-MOORE-COMPLEX` which
   ditulis sebagai *batasan* terukur: buktikan in Lean bahwa Î¾ no
   punya nol real (with begitu sertifikat real mustahil ada), lalu
      segel RH sebagai PARTIAL with landasan which jujur, and sebut
   "ball arithmetic + winding cross-check". Itu result which bisa
   disegel, bukan quest tanpa akhir.
2. Rujukan B-list (Â§4 daftar-kerja-kerja), bukan A-list: "Moore/RouchÃ©
   in â„‚ in Lean" adalah prasyarat kapabilitas, persis seperti
   "integrator ODE tervalidasi" which already tercatat in sana.
3. Baru setelah itu Q1 BSD, with pilot terukur lebih dulu â€” karena
   `weil_search.py` membuktikan bahwa pekerjaan Fâ‚ƒ and Î¾ no
   berinteraksi, jadi Q1 no menanggung risiko which sama.


