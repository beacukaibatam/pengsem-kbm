# scripts/ — Audit Automation

Alat bantu untuk mempercepat proses cek+audit pekerjaan Antigravity/Cline
di proyek PENGSEM KBM Batam, dipakai oleh Claude (dan sebaiknya juga oleh
Antigravity/Cline sendiri sebelum mengklaim tugas selesai).

## `audit_check.py` — checker mekanis + existence-check

Menjalankan 3 jenis cek mekanis (zero-diff `index.html` vs
`Formulir_Pemohon_CEISA_PENGSEM_KBM.html`, `py_compile`, `node --check`
pada blok `<script>` inline) ditambah existence-check sesuai manifest
(apakah suatu fungsi/field/istilah benar-benar ada di file, dengan jumlah
kemunculan minimum/maksimum).

```bash
python3 scripts/audit_check.py --manifest scripts/manifests/<nama_tugas>.json
python3 scripts/audit_check.py --manifest scripts/manifests/<nama_tugas>.json --json   # output JSON
```

Manifest baru dibuat per tugas/audit (lihat contoh
`scripts/manifests/poin61_cline_akordion.json`). Saat Claude menyiapkan
prompt untuk Antigravity/Cline, idealnya manifest untuk tugas itu ditulis
bersamaan, lalu disertakan sebagai langkah wajib di protokol penyelesaian
prompt tersebut.

**Batasan penting (baca sebelum percaya hasilnya):** script ini HANYA
membuktikan sesuatu itu *ada* di file dan lolos cek sintaks/diff. Ini
TIDAK membuktikan logikanya benar, dan TIDAK bisa menemukan regresi atau
efek samping yang tidak dituliskan di manifest (butuh baca kode manual
untuk itu). Jangan pernah menganggap "semua cek PASS" = "tugas pasti
benar seluruhnya".

## `audit_check_selftest.py` — meta-verifikasi `audit_check.py`

Membangun fixture proyek tiruan (benar & rusak) di direktori sementara,
lalu memastikan `audit_check.py` benar-benar membedakan keduanya untuk
tiap kategori cek. Jalankan ini setiap kali `audit_check.py` sendiri
diedit, untuk memastikan checker tidak diam-diam jadi buta terhadap satu
jenis kegagalan.

```bash
python3 scripts/audit_check_selftest.py
```

Kalau selftest ini gagal, JANGAN percaya hasil `audit_check.py` sampai
diperbaiki.
