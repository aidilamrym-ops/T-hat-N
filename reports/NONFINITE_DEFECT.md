# Dua silent-pass di kernel penghitung nol (2026-10-15)

Ditemukan saat menimbang urutan trek berikutnya, bukan karena ada yang
melihat kernel itu. Keduanya adalah kelas yang paling mahal: **komputasi
yang GAGAL dilaporkan sebagai hasil yang benar**.

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
 finiteness. Dan Arb menjawab **True** untuk `nan`: pustaka itu
memperlakukan "tidak ada informasi" sebagai "semua stuff ada di dalam".
Bukti langsung:

```
nan  -> contains_zero=True   is_finite=False
inf  -> contains_zero=False
```

Dengan `certified=True` dan `exact=False`, `_classify` jatuh ke cabang
ketiga — `PASS-BY-ENCLOSURE`. Jadi residual yang gagal dievaluasi
menghasilkan sertifikat **PASS**.

### Mengapa ini yang paling merusak

`evaluate_xi` sendiri menuliskan: *"a fake root is the most damaging
possible defect in a zero-finding kernel"*. Dan inilah jalannya: bukan roots
palsu yang disuntikkan lewat tabel nilai, tapi lewat residual `nan` yang
mengakucontains zero. Setiap pembanding teoretis tentang penghitung nol
menjadi tidak berlaku, karena "nol terdeteksi" dan "perhitungan gagal"
sama-sama menghasilkan PASS.

### Perbaikan

- `is_finite()` menjadi gerbang **semua** pertanyaan containment di
  modul (`contains_zero`, `contains_zero_complex`,
  `contains_zero_matrix`).
- Non-finite menjawab **False**, bukan melempar exception: pemanggilnya
  ada di loop panas atas matriks dan enclosure, dan jawaban yang jujur
  ("residual ini tidak certifying apa pun")|RD Deliverable ada di
  verdict, bukan di traceback.
- Verdict baru, `NOT_FINITE_VERDICT`, menyebut kegagalan evaluasinya
  sendiri: *"NOT a refutation and NOT a confirmation"*. Kata "FAIL:
  residual does not contain zero" saja akan menyesatkan, karena
  pembacanya akan mencatat refutasi yang tidak pernah terjadi.
- Field baru `ZeroCertificate.finite`, karena `certified` saja tidak
  bisa membawa perbedaan itu. Field-nya diletakkan paling akhir —
  `NamedTuple` tidak boleh punya default sebelum field biasa; ini
  ketahuan saat runtime dan sudah dikoreksi.

### Bukti

14 tes regresi di `msaf/tests/test_certify_nonfinite.py`:
`nan`/`inf`/`-inf` tidak pernah `certified`, tidak pernah `exact`,
verdict tidak pernah diawali `PASS`, jalur matriks dan kompleks punya
gerbang yang sama, dan jalur finite yang biasa tidak berubah (nol eksak
tetap PASS, ball yang misses zero tetap FAIL).

---

## 2. `evaluate_xi` mengembalikan `nan` tepat di dua kutubnya sendiri

### Gejala

Test yang tugging menjaga hal ini **lolos**:

```
test_xi_is_regular_at_zero_and_one
    assert contains_zero_complex(value - acb("0.5"))
```

dan nilai `value` adalah `nan + nanj`. Dengan kata lain: guard test
meloloskan diri karena guard-nya sendiri yang rusak.

### Akar

Formula harfiah di `evaluate_xi`

```
xi(s) = 1/2 * s * (s - 1) * pi^(-s/2) * Gamma(s/2) * zeta(s)
```

menghasilkan `0 * tak hingga` di s = 0 (Gamma) dan di s = 1 (zeta) —
keduanya `nan`. Docstring lama*fungsi itu mengklaim *"No special case is
taken at s = 0 or s = 1"*; kodenya memang mengambil special case, yaitu
`return nothing`.

### Perbaikan: identitas eksak, bukan tabel nilai

1. `s * Gamma(s/2) = 2 * Gamma(1 + s/2)` — identik untuk semua s.
   Menghilangkan kutub Gamma di s = 0; prefaktor menjadi
   `Gamma(1 + t/2) * (t - 1) * pi^(-t/2) * zeta(t)`, dan di t = 0 itu
   `1 * (-1) * 1 * (-1/2) = 1/2` ✓
2. `xi(s) = xi(1 - s)` (persamaan fungsional) — dipakai untuk
   menjauhi kutub yang lebih dekat: bila titik tengah real bola di atas
   1/2, bola yang direfleksikan dievaluasi. Refleksi adalah isometri,
   jadi supremum `|xi - c|` — itulah arti enclosure — tidak berubah,
      dan radius bola hasilnya juga tidak berubah. Kutub 0 dan 1 jadi
   simetris: hanya satu dari dua titik yang dievaluasi bisa dekat kutub,
   dan tidak pernah dekat s = 1.

Tabel nilai khas would've persis cara menyuntikkan root palsu ke
penghitung nol; identitas tidak bisa.

### Bukti

47 tes di `msaf/tests/test_xi_identities.py`:

- xi(0) dan xi(1) tepat 1/2, finite;
- **regresi nol**: di 15 titik pada garis kritikal, enclosure baru
  memuat titik tengah enclosure formula lama dan tidak lebih lebar dari
  4× radii — sehingga hitungan tersegel tidak bergeser. (Formulanya
  tidak menyentuh `weil_search.py`, jadi artefak a_11 = 354294 tidak
  terkait dan tidak diulang: 75 menit yang tidak akan membuktikan
  apa pun.)
- tanpa `nan` di 25 titik garis kritikal (daerah kerja penghitung);
- cabang refleksi benar-benar berbeda dari cabang langsung, dan keduanya benar.

### Kesalahan saya sendiri, tercatat

Uji simetri pertama menyatakan `xi(0.25+it) == xi(0.75+it)` dan gagal —
dan itu **salah asumsi**. Yang benar:

```
xi(s) = xi(1-s)              persamaan fungsional
xi(conj s) = conj(xi(s))     koefisien Taylor riil
=> xi(0.75 + it) = conj(xi(0.25 + it))
```

Angkanya persis begitu: `-4.64e-8 - 3.145e-7j` vs `-4.64e-8 +
3.145e-7j`. Kode benar, assertionsalah. Ditulis di docstring tes
karena versi yang salah adalah yang paling natural untuk ditulis, dan ia
gagal dengan alasan yang terlihat seperti kerusakan kode.

---

## 3. Residual TERBUKA: presisi global bocor antar modul tes

Ditemukan karena mengalahkannya. `msaf/tests/test_xi_identities.py`
awalnyaTNsets `ctx.prec = 200` di level modul; dua tes stres di
`test_adversarial_stress.py` lalu gagal **hanya pada run penuh**
(311 → 2 gagal) sementara lolos sendiri-sendiri.-fixed dengan fixture
yang menyimpan dan memulihkan presisi.

Tapi empat modul lama melakukan hal yang sama persis di level modul:

- `test_convergence_order.py:16` → 256
- `test_moore_premises.py:13,27` → 256
- `test_sbp_correspondence.py:56,67` → 256
- `test_tail_decay.py:26` → 256

Suite hijau sekarang, jadi tidak ada kegagalan yang aktif -- tapi mekanismenya
sama, dan tidak ada yang mencegah modul kelima menyusul. Perbaikan yang
benar adalah satu `conftest.py` dengan fixture presisi yang dipakai
semua modul; sengaja TIDAK dikerjakan di commit ini karena menyentuh
empat modul lain tanpa perlu, dan cukup dicatat sebagai OPEN.

Koreksi 2026-10-27 (D6): verifikasi manual membantah deskripsi "di level
modul". Keenam lokasi di atas berada di dalam fungsi (indent 4, dijalankan
saat tes berjalan, bukan saat modul diimpor) dan tidak memulihkan presisi,
sehingga kelas kebocoran lintas-modul yang disebut tetap nyata.
Perbaikan direalisasi SEBAGAI `msaf/tests/conftest.py`: fixture autouse
`arb_ctx_prec_guard` menyimpan `ctx.prec` di awal setiap tes dan
memulihkan nilai yang sama di akhirnya, sehingga tulisan presisi yang
acau di satu tes tidak lagi mengubah lingkungan yang dilihat tes lain —
tanpa menyentuh badan enam modul test. Enam tulisan persisi tidak dihapus:
menghapusnya akan membuat hasil bergantung urutan eksekusi (ambient presisi
tidak lagi teridentifikasi), sedangkan guard menjaga nilainya eksplisit.
Validasi empiris saat diterapkan: subset 10 modul flint (186 test) hijau
sebelum dan sesudah conftest ditambahkan; verdict untuk suite utuh adalah
job CI `python-tests` pada commit ini.

---

## 4. Urutan trek: koreksi terhadap rencana sebelumnya

Rencana lama: formalkan `CORR-MOORE-COMPLEX` dulu, baru Q1 BSD.
Setelah membaca `lean/NewtonExistence.lean` baris 433-480, rencana itu
harus dikoreksi.

`moore_test` di Lean dinyatakan atas **interval ℝ**:

```lean
theorem moore_test (a b m : ℝ) (hab : a < b) (f f' : ℝ → ℝ) ...
    : ∃ z ∈ Set.Icc a b, f z = 0
```

Kesimpulannya adalah Statement tentang bilangan **real**. Tapi nol yang
dihitung program ini ada di bola **kompleks** di garis kritikal. Jadi
transfer C→R bukan "belum diformalisasi" — secara struktural mustahil
sebagai pernyataan: sertifikat interval real hanya bisa certifying nol
real, sedangkan ξ tidak punya nol real (diperiksa dengan aritmetika
ball: enclosure ξ pada enam interval real, 0 tidak termasuk di
semuanya). Menutup "jembatan" ini berarti memformalkan **Moore atau
prinsip argumen di ℂ** — pengembangan Lean baru, bukanjemporting.

Konsekuensi untuk urutan:

1. Yang **mel-blocking** dan murah adalah `CORR-MOORE-COMPLEX` yang
   ditulis sebagai *batasan* terukur: buktikan di Lean bahwa ξ tidak
   punya nol real (dengan begitu sertifikat real mustahil ada), lalu
      segel RH sebagai PARTIAL dengan landasan yang jujur, dan sebut
   "ball arithmetic + winding cross-check". Itu hasil yang bisa
   disegel, bukan quest tanpa akhir.
2. Rujukan B-list (§4 daftar-kerja-kerja), bukan A-list: "Moore/Rouché
   di ℂ di Lean" adalah prasyarat kapabilitas, persis seperti
   "integrator ODE tervalidasi" yang sudah tercatat di sana.
3. Baru setelah itu Q1 BSD, dengan pilot terukur lebih dulu — karena
   `weil_search.py` membuktikan bahwa pekerjaan F₃ dan ξ tidak
   berinteraksi, jadi Q1 tidak menanggung risiko yang sama.
