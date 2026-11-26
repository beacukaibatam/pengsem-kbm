# Portal Layanan PENGSEM KBM Batam
### Pelayanan Pengeluaran Sementara Kendaraan Bermotor (KPU Bea dan Cukai Tipe B Batam)

Portal layanan terpadu resmi kepabeanan untuk pengajuan, verifikasi OCR, pemantauan berkas, penerbitan naskah persetujuan (SKEP & Nadine Kemenkeu), jaminan Simponi, pemeriksaan fisik (LHP), dan validasi SPPB Gate Out pengeluaran sementara kendaraan bermotor dari Kawasan Bebas Batam ke Tempat Lain Dalam Daerah Pabean (TLDDP).

---

## 🌐 Akses Publik & Tautan Halaman

- **Portal Publik (GitHub Pages)**: [https://beacukaibatam.github.io/pengsem-kbm/](https://beacukaibatam.github.io/pengsem-kbm/)
- **Halaman Masuk**: `https://beacukaibatam.github.io/pengsem-kbm/#/masuk`
- **Halaman Registrasi**: `https://beacukaibatam.github.io/pengsem-kbm/#/registrasi`
- **Halaman Lupa Sandi**: `https://beacukaibatam.github.io/pengsem-kbm/#/forgot`
- **Formulir Permohonan Pemohon**: `https://beacukaibatam.github.io/pengsem-kbm/#/formulir`
- **Dashboard Petugas Pabean**: `https://beacukaibatam.github.io/pengsem-kbm/#/dashboard`

---

## 🏛️ Kredensial Pengujian Akun Petugas (RBAC)

| Peran (Role) | Username | Kata Sandi | Deskripsi Tugas & Wewenang |
|---|---|---|---|
| **Super Admin** | `adminutama` | `123456` | Akses penuh ke seluruh menu dan tahapan pabean. |
| **Frontdesk** | `frontdesk` | `123456` | Pemeriksaan kelengkapan berkas & rekam naskah masuk Nadine. |
| **Loket** | `loket` | `123456` | Verifikasi dokumen loket & disposisi pabean. |
| **Seksi Jaminan** | `jaminan` | `123456` | Generate surat permohonan, lampiran KEP & billing jaminan. |
| **Seksi Fasilitas** | `fasilitas 1` | `123456` | Penerbitan nomor KEP & Naskah Keluar Persetujuan S Nadine. |
| **Pemeriksa Barang** | `pemeriksabarang` | `12345` | Rekam LHP fisik, foto kendaraan, nomor rangka & nomor mesin. |
| **Pemeriksa Dokumen** | `pemeriksadokumen` | `123456` | Penelitian berkas & LHP serta keputusan penerbitan SPPB. |
| **Gate Pelabuhan** | `gate` | `123456` | Pemindaian barcode SPPB & validasi izin keluar pelabuhan. |
| **Pemohon KBM** | `pemohon` | `123456` | Akun pemohon pengujian: Formulir, unggah berkas & lacak status. |
| **Pemohon KBM (WA)** | `081XXXXXXXXX_REDACTED` | `REDACTED_PASSWORD` | Pengisian formulir pabean & pelacakan status permohonan. |

---

## ⚙️ Menjalankan Backend Secara Mandiri

```bash
# Instal dependensi
pip install -r requirements.txt

# Jalankan server
python3 server.py
```
Backend akan aktif di `http://localhost:8080` dengan basis data SQLite WAL (`kbm_batam.db`).
Endpoint healthcheck: `GET /api/health`.

---
© 2026 KPU Bea dan Cukai Tipe B Batam - Kementerian Keuangan RI
