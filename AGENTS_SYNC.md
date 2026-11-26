# AGENTS_SYNC.md: Living Source of Truth (Antigravity ⇄ Claude)

> [!IMPORTANT]
> **ATURAN WAJIB DUA ARAH (SYSTEM INSTRUCTION)**:
> 1. **Sebelum Memulai Pekerjaan**: Setiap agen (Antigravity atau Claude) **WAJIB membaca berkas ini terlebih dahulu** untuk memahami status sistem terkini, arsitektur aktif, kredensial yang berlaku, dan pekerjaan terakhir yang dilakukan agen lain.
> 2. **Setelah Menyelesaikan Pekerjaan**: Setiap agen **WAJIB mencatatkan log perubahan pada tabel di bawah** dan memperbarui status To-Do sebelum mengakhiri sesi/respon.

---

## 1. Arsitektur Sistem Produksi Cloud 24/7

```
                      +------------------------------------------+
                      |               PENGGUNA                   |
                      |  (Pemohon KBM & Petugas Bea Cukai Batam) |
                      +--------------------+---------------------+
                                           |
                                           v
                  +--------------------------------------------------+
                  |         FRONTEND STATIC HOSTING (SPA)            |
                  |          GitHub Pages (beacukaibatam)            |
                  |     https://beacukaibatam.github.io/pengsem-kbm/ |
                  |       - Dynamic API_BASE_URL (Local/Cloud)       |
                  |       - Client-side Hash Routing (SPA)           |
                  |       - Auto-Crop & WebCam/Galeri/PDF OCR        |
                  +------------------------+-------------------------+
                                           | HTTPS / JSON API
                                           v
                  +--------------------------------------------------+
                  |           BACKEND SERVICE CLOUD (24/7)           |
                  |       Render.com Web Service / Python 3.9+       |
                  |   https://api-kbm-beacukaibatam.onrender.com     |
                  |       - High-Concurrency ThreadPool (Anti-OOM)   |
                  |       - Dynamic Image Compression (Max 1600px)   |
                  |       - CORS Preflight Support (OPTIONS)         |
                  |       - Healthcheck Endpoint (/api/health)       |
                  +------------+-----------------------+-------------+
                               |                       |
            +------------------+                       +-------------------+
            | SQLite WAL                               | Webhooks & APIs   |
            v                                          v                   v
+-----------------------+              +--------------------+  +--------------------+
|  SQLITE 3 DATABASE    |              |  WHATSAPP META     |  |   SMTP EMAIL       |
|  (kbm_batam.db)       |              |  CLOUD API         |  |   GATEWAY          |
|  - WAL Mode           |              |  - Notifikasi OTP  |  |  - Graceful        |
|  - Thread-Safe        |              |  - Auto-Fallback   |  |    Fallback saat   |
|  - Users & Permohonan |              |    on Rate Limit   |  |    WA 429 / limit  |
+-----------------------+              +--------------------+  +--------------------+
```

---

## 2. Struktur Direktori & Peran File

| File / Folder | Peran & Deskripsi Utama |
|---|---|
| `index.html` | Entry point utama Frontend SPA (Login, Registrasi, Dashboard Monitoring Petugas, & Formulir Pemohon). |
| `Formulir_Pemohon_CEISA_PENGSEM_KBM.html` | Salinan identik dari `index.html` untuk kompatibilitas tautan langsung pabean. |
| `server.py` | Backend HTTP API Server Python (Autentikasi RBAC, Endpoint Permohonan, Healthcheck, WhatsApp & Email Gateway). |
| `database.py` | Modul koneksi SQLite terisolasi thread-safe dengan mode `PRAGMA journal_mode=WAL;`. |
| `kbm_batam.db` | Database relasional SQLite (tabel: `users`, `otp_sessions`, `permohonan`, `system_logs`). |
| `requirements.txt` | Daftar dependensi Python untuk deployment cloud (Render/VPS). |
| `render.yaml` | Blueprint konfigurasi 1-click Web Service di Render.com. |
| `AGENTS_SYNC.md` | Berkas sinkronisasi memori bersama (Living Source of Truth) antara Antigravity dan Claude. |
| `CLAUDE.md` | Panduan instruksi kerja Claude Code / Claude Assistant saat beroperasi di workspace ini. |
| `Jalankan_Portal_PENGSEM.command` | Skrip klik dua kali macOS untuk menjalankan server dan browser lokal secara otomatis. |

---

## 3. Daftar Environment Variables (Cloud & Local)

| Nama Variabel | Nilai Default / Contoh | Deskripsi |
|---|---|---|
| `PORT` | `8080` (Lokal) / `10000` (Render) | Port listen server HTTP backend. |
| `ENVIRONMENT` | `production` / `development` | Mode operasi server. |
| `DATABASE_PATH` | `kbm_batam.db` | Jalur absolut/relatif file SQLite. |
| `OCR_MAX_WORKERS` | `4` | Batasan thread OCR simultan untuk anti-OOM (RAM 512 MB). |
| `CORS_ORIGINS` | `https://beacukaibatam.github.io,http://localhost:8080,http://127.0.0.1:8080` | Daftar domain yang diizinkan mengakses API. |
| `WA_META_PHONE_NUMBER_ID` | `102938475610293` | Phone Number ID dari Meta Developer Portal. |
| `WA_META_ACCESS_TOKEN` | `EAAB...` | Permanent System User Access Token Meta Cloud API. |
| `WA_WEBHOOK_VERIFY_TOKEN` | `KBM_BATAM_SECURE_TOKEN_2026` | Token verifikasi webhook WhatsApp Meta. |
| `SMTP_HOST` | `smtp.gmail.com` | Host server SMTP pengiriman email OTP. |
| `SMTP_PORT` | `587` | Port TLS SMTP. |
| `SMTP_USER` | `layanan.kbm.batam@gmail.com` | Akun pengguna email pengirim OTP. |
| `SMTP_PASS` | `xxxx xxxx xxxx xxxx` | App Password aman (16 digit) dari akun Google/SMTP. |
| `SMTP_FROM` | `Bea Cukai Batam <layanan.kbm.batam@gmail.com>` | Nama & alamat pengirim email. |

---

## 4. Matriks Peran & Akun Pengguna Terdaftar (RBAC)

| Akun / Username | Sandi | Role Sistem | Wewenang & Status yang Ditangani |
|---|---|---|---|
| `adminutama` | `123456` | `adminutama` | Super Admin Pabean: Akses penuh seluruh tahapan & override status. |
| `frontdesk` | `123456` | `frontdesk` | Cek berkas pemohon dan rekam/unggah surat masuk ke Nadine Kemenkeu (`FRONTDESK_NADINE`). |
| `loket` | `123456` | `loket` | Cek berkas pemohon dan rekam/unggah surat masuk ke Nadine Kemenkeu (`FRONTDESK_NADINE`). |
| `jaminan` | `123456` | `jaminan` | Menerbitkan kode billing Simponi jaminan PPN 11% & dokumen permohonan pemohon (`LOKET_JAMINAN`). |
| `fasilitas 1` / `fasilitas1` | `123456` | `fasilitas` | Menerbitkan naskah dinas keluar S dan KEP Persetujuan (`VERIFIKASI_FASILITAS`). |
| `pemeriksabarang` | `12345` *(5 digit)* | `pemeriksabarang` | Pemeriksaan fisik kendaraan di hanggar pelabuhan & rekam LHP foto (`PPFTZ_CEK_FISIK`). |
| `pemeriksadokumen` | `123456` | `pemeriksadokumen` | Meneliti LHP fisik dan memutuskan penerbitan dokumen SPPB (`PEMERIKSA_DOKUMEN`). |
| `gate` | `123456` | `gate` | Validasi keberangkatan KBM di gate pelabuhan Roro Batam (`SPPB_GATE_OUT`). |
| `pemohon` | `123456` | `pemohon` | Akun Uji Pemohon: Pengisian formulir, unggah berkas pabean, & pelacakan status KBM. |
| `081XXXXXXXXX_REDACTED` | `REDACTED_PASSWORD` | `pemohon` | Wajib Pajak Pemohon: Mengajukan formulir & memantau status kendaraannya sendiri. |

---

## 5. Log Riwayat Perubahan Terkini (Collaboration History)

| Waktu (WIB) | Agen Pelaksana | Berkas yang Dimodifikasi | Rincian Pembaruan | Status Deployment |
|---|---|---|---|---|
| 2026-11-26 08:35 | Antigravity | `index.html`, `server.py`, `db_users.json` | Implementasi RBAC 8 akun petugas & perbaikan proporsi form landing 0-scroll. | Verified Local (0-Diff) |
| 2026-11-26 08:55 | Antigravity | `CLAUDE.md`, `AGENTS_SYNC.md` | Pembuatan protokol memori bersama Antigravity ⇄ Claude dan panduan sinkronisasi. | Done |
| 2026-11-26 09:05 | Antigravity | `database.py`, `server.py` | Migrasi database JSON ke SQLite WAL terindeks, ThreadPoolExecutor, healthcheck `/api/health`, anti-OOM image resize max 1600px, & graceful fallback OTP Meta WA ke SMTP TLS. | Verified Local (200 OK) |
| 2026-11-26 09:15 | Antigravity | `index.html`, `Formulir_...html` | Penerapan dynamic `API_BASE_URL` dan Hash-Routing SPA (`#/masuk`, `#/registrasi`, `#/dashboard`, `#/formulir`) dengan auto-restore sesi. | Verified Playwright (0-Diff) |
| 2026-11-26 09:20 | Antigravity | `requirements.txt`, `render.yaml` | Pembuatan paket blueprint cloud deployment Render 24/7 dan panduan UptimeRobot & GitHub Pages. | Production Ready |
| 2026-11-26 09:22 | Antigravity | GitHub Repo & Pages | Inisialisasi repo publik `beacukaibatam/pengsem-kbm`, pengamanan secret push-protection, dan rilis GitHub Pages live di `https://beacukaibatam.github.io/pengsem-kbm/`. | Deployed Live (HTTP 200) |
| 2026-11-26 09:30 | Antigravity | `server.py`, `kbm_batam.db`, `db_users.json` | Penambahan user sisi pemohon: username `pemohon`, sandi `123456`, verifikasi login & perutean formulir. | Verified Local & Tunnel (200 OK) |
| 2026-11-26 09:32 | Antigravity | Akun GitHub & Remote | Migrasi nama akun GitHub resmi ke `beacukaibatam`. URL resmi aktif di `https://beacukaibatam.github.io/pengsem-kbm/`. | Verified Live (HTTP 200 OK) |
| 2026-11-26 09:34 | Antigravity | Tunnel & Kode Frontend | Penghentian total proses tunnel Cloudflare (PID 18154). Tunnel `trycloudflare.com` dinonaktifkan (530). | Deactivated / Cleaned |
| 2026-11-26 09:45 | Antigravity | Render Cloud 24/7 Live | Blueprint `beacukaibatam/pengsem-kbm` deployed live di `https://api-kbm-beacukaibatam.onrender.com`. Health & Auth 200 OK. | Deployed Live 24/7 |
| 2026-11-26 09:48 | Antigravity | UptimeRobot 24/7 Ping | Konfigurasi monitor HTTP(S) `API KBM Bea Cukai Batam` (interval 5 menit, target `/api/health`). Server Render anti-sleep. | Active Monitoring |
| 2026-11-26 09:56 | Antigravity | `index.html`, `Formulir_...html` | Penyempurnaan UI Pemohon: Ubah nama kartu 'STNK' & 'BPKB', hapus animasi scan sebelum upload (placeholder rapi), hapus label CEISA, sembunyikan seluruh tab dinas petugas dari pemohon. | Verified Live (0-Diff) |
| 2026-11-26 10:10 | Antigravity | `index.html`, `Formulir_...html` | Perbaikan total layout pemohon untuk Mac Air & Mac Mini: Zero-scroll viewport fit, hilangkan bayangan floating aneh pada preview-box, selaraskan tinggi & grid 4 kartu (KTP, NPWP, STNK, BPKB) 100% simetris, perbaiki DOM nesting (hapus duplikasi input & extra tag penutup), dan cegah teks e-Meterai tertimpa floating WA widget. | Verified Live (0-Diff) |
| 2026-11-26 10:28 | Antigravity | `index.html`, `Formulir_...html` | Perbaikan posisi popup panduan informasi berkas (`modalDocGuide`): Berikan styling `modal-overlay` dengan `position: fixed; inset: 0` dan centering penuh layar (backdrop blur 5px) sehingga popup muncul presisi di tengah layar (bukan terpotong di bagian bawah halaman). | Verified Playwright (0-Diff) |
| 2026-11-26 12:25 | Antigravity | `index.html`, `Formulir_...html`, `server.py` | 1. Simplifikasi flyer Client Coordinator ke FAB ramping (36px pill desktop / 36px icon mobile, dismiss `×`, z-index 900 aman bebas halangan).<br>2. Adaptif layout di segala ukuran layar: Split side-by-side fluid scaling (>880px) tanpa anjlok ke bawah saat dikecilkan; Sembunyikan kolase raksasa di mobile portrait (<=880px) dan tampilkan pita kolase minimalis 4-ubin mikro di atas form.<br>3. Algoritma auto-crop cerdas berbasis canvas edge & background separation: otomatis memotong meja/lingkungan luar berkas KTP, NPWP, STNK, BPKB menyisakan hanya dokumen.<br>4. Graceful OTP testing fallback: expose `debug_otp` saat Meta WA expired / SMTP cloud belum terisi agar registrasi pemohon tidak terblokir. | Verified Playwright (0-Diff) |
| 2026-11-26 12:49 | Antigravity | `index.html`, `Formulir_...html`, `server.py` | Pembuatan Token WhatsApp Permanen (Never Expire) via System User Meta Business Manager & pengujian kirim 200 OK. Flyer Client Coordinator disederhanakan murni menjadi ikon bulat WhatsApp floating button (`.fab-wa-clean`). Input Nama Lengkap otomatis kapital penuh tanpa placeholder lama. | Verified Live & Playwright (0-Diff) |
| 2026-11-26 14:10 | Claude | `index.html`, `Formulir_...html`, `server.py`, `.gitignore` | **AUDIT KEAMANAN**: (1) Hapus backdoor login "Default Dinas" hardcoded di `server.py` (login & login-pegawai) + panel modal mati yang menampilkannya di `index.html`; akun duplikat role adminutama yang sempat ter-persist ke `db_users.json`/`kbm_batam.db` akibat backdoor ini juga dihapus dari database lokal (belum di-commit, menunggu keputusan arsitektur). (2) Hapus field `debug_otp` dari respons `request-otp`/`request-email-otp` (sebelumnya sengaja diekspos per log 12:25 — ternyata membuat OTP bisa dibaca langsung dari Network tab/response JSON, melumpuhkan verifikasi OTP). (3) Tambah helper `_strip_password()` agar field password tidak pernah ikut terkirim di respons `login`, `verify-otp`, `auth/session`. (4) Tambah flag `HttpOnly` di cookie `session_token`. (5) Hapus penyimpanan password plaintext di `sessionStorage` saat registrasi. (6) Ganti tombol "Kirim OTP ke Email" (tidak pernah benar-benar terkirim, SMTP belum dikonfigurasi) dengan link kontak manual Client Coordinator WA. (7) Rapikan ukuran font/kolom & spasi form Masuk/Registrasi agar 0-scroll di layar standar. **TEMUAN TERBUKA (belum dieksekusi, menunggu keputusan user)**: satu nomor WA pemohon beserta password plaintext-nya sempat ter-commit ke histori git publik (lihat commit lama penambahan user pemohon); `db_chat.json` juga berisi nama/nomor WA/kode OTP asli pemohon dan sudah ter-commit — detail lengkap hanya dibahas di percakapan sesi, tidak ditulis ulang di sini demi keamanan. Render pakai `plan: free` tanpa `disk:` (ephemeral) sehingga `kbm_batam.db`/`db_users.json`/`db_chat.json` HARUS tetap ter-commit ke git agar data tidak hilang tiap deploy — ini akar masalah kenapa PII terus bocor ke repo publik. Nomor dokumen resmi (KEP, Surat-S, SPPB, LHP, billing Simponi, Nadine ND-ID) masih `random.randint(...)`, bukan integrasi CEISA/Nadine/Simponi riil — perlu dilabeli "SIMULASI" di UI. | Code fixes Pushed (`3af2afd`); data-file cleanup & keputusan arsitektur data PENDING |

---

## 6. To-Do List & Status Tugas Berikutnya

- [x] Poin 1: Berkas Konteks Bersama `AGENTS_SYNC.md` dan `CLAUDE.md`.
- [x] Poin 2: Migrasi Database ke SQLite WAL thread-safe (`kbm_batam.db`).
- [x] Poin 3: Optimasi Memori Backend (Anti-OOM 512 MB), Image Resizing, ThreadPool, dan `/api/health`.
- [x] Poin 4: Ketahanan Pengiriman OTP WhatsApp Meta Cloud API dengan Fallback otomatis ke SMTP Email.
- [x] Poin 5: Konfigurasi Frontend (Dynamic API URL & Hash-Routing SPA `#/dashboard`, `#/formulir`).
- [x] Poin 6: Paket Deployment Cloud (`requirements.txt`, `render.yaml`, panduan Render, UptimeRobot, GitHub Pages).
- [x] Poin 7: Pengujian Terpadu Playwright & Handover Final ke Claude.
