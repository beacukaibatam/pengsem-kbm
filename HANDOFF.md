# HANDOFF — Layanan PENGSEM KBM Bea Cukai Batam

Dokumen estafet bersama untuk **Antigravity** dan **Claude** (di Mac Mini maupun MacBook Air) agar selalu sinkron dan bebas konflik.

---

## 1. Protokol Wajib Multi-Agent & Multi-Mac

1. **Gunakan clone lokal di luar Google Drive**, bukan folder `My Drive/...` (Google Drive rawan membuat file `.git/*.lock` nyangkut dan merusak repo `.git`).
   - Lokasi standar di tiap Mac: `~/Projects/pengsem-kbm`
   - Jembatan sinkronisasi satu-satunya antar Mac & antar agen: **GitHub (`origin main`)**.
2. **Kerja bergantian (1 agen aktif pada satu waktu).**
3. **Awal sesi (WAJIB):**
   ```bash
   git pull origin main
   git log -n 5 --oneline
   ```
   Baca bagian **Log Estafet Terbaru** di bawah sebelum menyentuh kode.
4. **Akhir sesi (WAJIB):**
   - Verifikasi sintaks (`node --check` untuk JS inline, `python3 -m py_compile server.py database.py` untuk Python).
   - Pastikan `diff -u index.html Formulir_Pemohon_CEISA_PENGSEM_KBM.html` menghasilkan **0 perbedaan**.
   - Perbarui bagian **Log Estafet Terbaru** di file ini jika ada perubahan besar/keputusan baru.
   - `git commit` dengan pesan jelas, lalu `git push origin main`.

---

## 2. Arsitektur & Endpoint Live

- **Repository:** `https://github.com/beacukaibatam/pengsem-kbm.git` (branch `main`)
- **Frontend Live (GitHub Pages):** `https://beacukaibatam.github.io/pengsem-kbm/`
- **Backend Live (Render Cloud):** `https://api-kbm-beacukaibatam.onrender.com`
- **File Utama:**
  - `index.html` — Frontend portal (Auth, Formulir Pemohon, Dashboard Petugas & Admin)
  - `Formulir_Pemohon_CEISA_PENGSEM_KBM.html` — Mirror wajib identik (`diff -u` = 0) dengan `index.html`
  - `server.py` — Backend Python (`http.server`) + integrasi Meta WA, Gemini Vision, RBAC, CORS whitelist
  - `database.py` — Persistensi SQLite WAL (`kbm_batam.db`, tidak di-commit ke Git)
  - `.env` — Rahasia lokal (`GEMINI_API_KEY`, `META_WA_ACCESS_TOKEN`, `META_PHONE_NUMBER_ID`, `META_WABA_ID`; **tidak pernah di-commit**)

---

## 3. Aturan Teknis Kritis

- **Zero-Diff Frontend:** Setiap edit di `index.html` wajib langsung disalin ke `Formulir_Pemohon_CEISA_PENGSEM_KBM.html`.
- **Anti-Halusinasi:** Jangan membuat kredensial/email dummy atau mengklaim integrasi eksternal aktif jika belum ada API/kredensial riilnya.
- **Keamanan:** Pertahankan CORS whitelist (CWE-942), sanitasi XSS `escapeHtml` (CWE-79), dan RBAC per-peran di server.
- **Data Produksi Bersih:** Jangan pernah menambahkan ulang data contoh/dummy permohonan (seperti `KBM-2026-001`) atau akun uji ke production.
- **Stepper Tahap 1 (`#stepBarBox1`):** Sengaja selalu berstatus *"Tahap 1 • Selesai — 1. Akun Pemohon Terdaftar"* setelah pemohon login (merepresentasikan status akun terdaftar, bukan pengisian form). Jangan ubah logika `setStepActive()` / `renderStepBarStatus()`.

---

## 4. Status Integrasi Saat Ini

- **Aktif Riil:**
  - WhatsApp OTP & notifikasi tahap via Meta Cloud API resmi (nomor bot `+62 851-4490-1346`, token permanen System User).
  - OCR dokumen (KTP, NPWP, STNK, BPKB) via Google Gemini Vision API (`GEMINI_API_KEY`).
  - Auto-crop dokumen berbasis Canvas di sisi browser.
  - Database SQLite WAL, RBAC petugas/admin, cetak dokumen PPFTZ-01/LHP/BAP/SPPB + QR gate.
  - Penyimpanan berkas fisik lokal per permohonan (`/var/data/uploads/<ID_NAMA_NOPOL>/`) + **Google Drive Apps Script Bridge** (`gdrive_bridge/Code.gs`) untuk arsip otomatis KTP, NPWP, STNK, BPKB, dokumen pendukung, Surat Permohonan/Pernyataan bermeterai, PPFTZ-01, LHP, BAP, SPPB, dan backup SQLite (`_BACKUP_DATABASE`).
  - Skrip backup force majeure proyek ke Google Drive: `./backup_to_gdrive.sh` → `My Drive/PENGELUARAN_SEMENTARA_KBM_BATAM/BACKUP_WEBSITE/`.
- **Belum Terhubung Eksternal / Lokal:**
  - **Google Drive Bridge Env:** Perlu deploy `gdrive_bridge/Code.gs` di `script.google.com` (`ridwanmuham17@gmail.com`) lalu isi `GDRIVE_BRIDGE_URL` & `GDRIVE_BRIDGE_SECRET` di Render Cloud.
  - **SMTP Email:** Belum ada akun SMTP produksi yang dipasang di Render (`SMTP_HOST`, `SMTP_USER`, `SMTP_PASS`).
  - **CEISA 4.0 DJBC & NADINE Kemenkeu:** Penomoran masih dikelola secara lokal oleh backend.

---

## 5. Log Estafet Terbaru

- **Arsip Google Drive & Force Majeure Backup** — Tambah `gdrive_bridge/Code.gs` + `README_SETUP.md`, simpan berkas asli pemohon (KTP/NPWP/STNK/BPKB/pendukung/bermeterai) & dokumen pabean (PPFTZ-01/LHP/BAP/SPPB) ke `/var/data/uploads/` + antrean arsip otomatis Google Drive, serta `backup_to_gdrive.sh` untuk snapshot proyek (Antigravity, Mac Mini).
- `0009783` — Tambah `HANDOFF.md` untuk sinkronisasi multi-agent & multi-Mac (Antigravity, Mac Mini).

- `8f5d143` — Perjelas label Tahap 1 stepper bar menjadi `1. Akun Pemohon Terdaftar` (Antigravity, Mac Mini).
- `2368f03` — Terapkan CORS whitelist (CWE-942), sanitasi XSS `escapeHtml` (CWE-79), hapus tuntas `KBM-2026-001` dari SQLite & JSON (Claude).
- `d3e446b` — Perbaiki dashboard pemohon agar menampilkan permohonan miliknya sendiri (Claude).
- `dd2420e` — Tambah panel admin kelola akun & log aktivitas, batasi Admin Override (Claude).
- `3fd9e86` — Cetak PPFTZ-01/LHP/BAP/SPPB + QR gate, perbaikan format surat & SQLite (Claude).
- `f5ab565` — Perbaikan e-meterai, RBAC per-peran di server, notifikasi WA tiap tahap (Claude).
