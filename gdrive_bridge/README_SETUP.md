# Panduan Aktivasi Google Drive Bridge (`ridwanmuham17@gmail.com`)

Skrip ini menghubungkan server Render Cloud (`api-kbm-beacukaibatam.onrender.com`) secara langsung ke Google Drive `ridwanmuham17@gmail.com` untuk mengarsipkan:
- Unggahan asli pemohon: KTP, NPWP, STNK, BPKB, dokumen pendukung, Surat Permohonan & Pernyataan bermeterai
- Dokumen pabean terbitan petugas: PPFTZ-01, LHP, BAP Pemeriksaan, SPPB
- Backup berkala database SQLite (`_BACKUP_DATABASE/`)

## Langkah Setup (1 Menit, Cukup Sekali)

1. Buka **https://script.google.com** (pastikan login sebagai `ridwanmuham17@gmail.com`).
2. Klik **New project**, beri nama: `KBM Batam Drive Bridge`.
3. Hapus seluruh isi editor, lalu salin-tempel seluruh isi file `Code.gs` di folder ini.
4. Klik ikon gerigi **Project Settings** di sidebar kiri → bagian **Script Properties** → klik **Add script property**:
   - Property: `BRIDGE_SECRET`
   - Value: buat kata sandi acak yang panjang (misal: `KBM-BATAM-GDRIVE-2026-x9Q4mP7vR2kL`)
5. Klik tombol **Deploy** (kanan atas) → **New deployment**:
   - Klik ikon gerigi di samping *Select type* → pilih **Web app**
   - Description: `v1`
   - Execute as: **Me (`ridwanmuham17@gmail.com`)**
   - Who has access: **Anyone** *(akses tetap terkunci oleh `BRIDGE_SECRET`)*
   - Klik **Deploy** → klik **Authorize access** → pilih akun `ridwanmuham17@gmail.com` → *Advanced* → *Go to KBM Batam Drive Bridge (unsafe)* → **Allow**.
6. Salin **Web app URL** (format: `https://script.google.com/macros/s/.../exec`).
7. Pasang 2 Environment Variable di **Render Cloud** (Dashboard Render → `api-kbm-beacukaibatam` → Environment) dan di file `.env` lokal:
   - `GDRIVE_BRIDGE_URL` = `<Web app URL yang disalin>`
   - `GDRIVE_BRIDGE_SECRET` = `<nilai BRIDGE_SECRET yang sama>`

Setelah disimpan, setiap permohonan baru & dokumen pabean otomatis masuk ke folder **`My Drive / ARSIP_PENGSEM_KBM_BATAM /`** di Google Drive Anda.
