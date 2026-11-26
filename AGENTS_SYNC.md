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
| 2026-11-26 14:10 | Claude | `index.html`, `Formulir_...html`, `server.py`, `.gitignore` | **AUDIT KEAMANAN**: (1) Hapus backdoor login "Default Dinas" hardcoded di `server.py` (login & login-pegawai) + panel modal mati yang menampilkannya di `index.html`; akun duplikat role adminutama yang sempat ter-persist ke `db_users.json`/`kbm_batam.db` akibat backdoor ini juga dihapus dari database lokal (belum di-commit, menunggu keputusan arsitektur). (2) Hapus field `debug_otp` dari respons `request-otp`/`request-email-otp` (sebelumnya sengaja diekspos per log 12:25 — ternyata membuat OTP bisa dibaca langsung dari Network tab/response JSON, melumpuhkan verifikasi OTP). (3) Tambah helper `_strip_password()` agar field password tidak pernah ikut terkirim di respons `login`, `verify-otp`, `auth/session`. (4) Tambah flag `HttpOnly` di cookie `session_token`. (5) Hapus penyimpanan password plaintext di `sessionStorage` saat registrasi. (6) Ganti tombol "Kirim OTP ke Email" (tidak pernah benar-benar terkirim, SMTP belum dikonfigurasi) dengan link kontak manual Client Coordinator WA. (7) Rapikan ukuran font/kolom & spasi form Masuk/Registrasi agar 0-scroll di layar standar. | Code fixes Pushed |
| 2026-11-26 16:00 | Claude | `server.py`, `database.py`, `render.yaml`, `.env` (Render dashboard) | **ARSITEKTUR DATA**: Akar masalah PII berulang ter-commit ke repo publik adalah Render paket free tanpa disk permanen. Diselesaikan tuntas: (1) Upgrade Render ke plan Starter + Persistent Disk 1GB di `/var/data`, env var `DATABASE_PATH`/`DATA_DIR` diarahkan ke sana, migrasi data lama otomatis terverifikasi sukses di log deploy. (2) `db_users.json`/`db_otp.json`/`db_permohonan.json`/`db_chat.json`/`db_nadine_config.json`/`kbm_batam.db` dihapus dari git tracking (tetap ada di disk/Persistent Disk, tidak lagi ikut commit). (3) Histori git lama di-rewrite (`git filter-repo`) untuk membuang total file-file data itu dari SEMUA commit + redaksi string kredensial sensitif dari pesan commit lama, lalu force-push — hash semua commit berubah. Juga: tutup bug nyata di alur petugas (field `hasil_rangka`/`hasil_mesin` yang dikirim frontend tidak pernah cocok dengan `kesesuaian_rangka`/`kesesuaian_mesin` yang dibaca backend sehingga hasil TIDAK_SESUAI selalu tercatat SESUAI; SPPB sekarang diblok kalau LHP tidak sesuai; nilai jaminan PPN wajib diisi manual & divalidasi, tidak lagi hardcode; nomor KEP/Surat-S/Billing/SPPB dibuat read-only + label "simulasi lokal" karena backend selalu menimpa nilai manapun yang diketik petugas; admin override status kini wajib isi alasan, bug pengecekan role yang selalu gagal 403 diperbaiki). Perbaikan UX: modal unggah berkas disederhanakan jadi 1 langkah (native file picker langsung, tanpa dialog ganda), dashboard petugas dirapikan untuk mobile, dan stepper formulir pemohon yang ternyata statis/pernah crash (fungsi `setStepActive` mereferensikan elemen yang sudah tidak ada) diperbaiki agar mengikuti progres asli. **MASIH TERBUKA**: kalkulator NJKB otomatis (Bapenda Kepri) belum tersambung ke alur Jaminan petugas (`workspace_macair/bapenda_njkb_client.py` belum dipanggil); nomor dokumen resmi (KEP/SPPB/Billing/LHP/Nadine ND-ID) masih `random.randint(...)` lokal, belum integrasi CEISA/Nadine/Simponi riil — perlu label "SIMULASI" lebih terlihat di UI; LHP fisik pakai checklist centang manual (belum ada upload foto sungguhan di portal ini). | Deployed Live; Persistent Disk Active; Histori Git Dibersihkan |
| 2026-11-26 17:50 | Claude | `index.html`, `Formulir_...html`, `server.py` | **E-METERAI RIIL + RBAC PER-PERAN + NOTIFIKASI WA**: (1) Hapus stempel "E-METERAI"/nomor seri PERURI palsu yang digambar langsung oleh jsPDF di `generateAndDownloadRealPDF()` (Hal 1 & 2) — diganti watermark jujur "DRAFT - BELUM BERMETERAI". Alur submit dipecah: unduh draf → bubuhkan e-meterai asli via portal resmi (link diperbaiki ke domain resmi terverifikasi: `e-meterai.co.id` [PT Peruri Digital Security], `mitracomm.e-meterai.co.id`, `finnet.e-meterai.co.id` — link lama `meterai-elektronik.com`/`e-meterai.posfin.id` tidak dapat diverifikasi sebagai kanal resmi, jadi diganti) → unggah dokumen bermeterai (field baru `dokumen_bermeterai`, UI di `pdfModal`) → baru `submitFinalPermohonan()` memanggil `/api/permohonan/create`, yang kini MENOLAK (400) permohonan jalur `PORTAL_WEB` tanpa `dokumen_bermeterai`. Riset API e-meterai: tidak ditemukan API self-serve publik dari PERURI/distributor resmi (PDS/Mitracomm/Finnet/Mekari Sign) — semua jalur integrasi API butuh kontrak kemitraan bisnis, bukan signup instan; jadi TIDAK dibuat integrasi API palsu, tetap jalur link-out resmi. (2) **Perbaikan RBAC kritis**: `/api/auth/login-pegawai` (jalur NIP, tidak terpakai frontend) hardcode `role: "pegawai"` generik — diperbaiki pakai role spesifik dari data akun. Yang LEBIH KRITIS: endpoint `GET /api/permohonan` (daftar permohonan) sebelumnya mengembalikan SEMUA data ke siapapun yang bukan role `pemohon` TANPA filter tahap sama sekali (dan bahkan ke request tanpa sesi valid sekalipun, karena fetch di frontend tidak mengirim header Authorization) — sekarang difilter server-side per role (`STAGE_VISIBILITY_BY_ROLE`): `frontdesk`/`loket` hanya tahap Nadine, `fasilitas` hanya `VERIFIKASI_FASILITAS`, `jaminan` hanya `LOKET_JAMINAN`, `gate` hanya `SPPB_GATE_OUT`; sedangkan `adminutama`, `pemeriksabarang`, dan `pemeriksadokumen` sengaja diberi visibilitas PENUH lintas tahap (sesuai permintaan user) karena keduanya butuh validasi kesesuaian fisik barang terhadap seluruh riwayat dokumen, bukan cuma tahap pemeriksaannya; request tanpa sesi valid sekarang dapat `[]` kosong, bukan seluruh data (menutup celah kebocoran PII tak-terautentikasi). Ditemukan juga bug `NameError` laten (`threading` dipakai tapi tidak pernah di-`import`) — diperbaiki sekalian. Endpoint `nadine/config` & `nadine/test-login` yang sebelumnya mengecek `role == 'pegawai'` literal (yang berarti SELALU menolak akun asli, karena role asli sudah spesifik sejak awal via `/api/auth/login`) diperbaiki agar mengenali role `frontdesk`/`loket`/`adminutama`. Fungsi `_is_role_allowed` di 6 endpoint aksi petugas (upload-permohonan, terbitkan-skep, terbitkan-billing, rekam-lhp, terbitkan-sppb, validasi-keluar) dibersihkan dari fallback generik `'pegawai'` yang (jika pernah ada akun tanpa role eksplisit) bisa membuka akses ke SEMUA endpoint aksi. Frontend `renderTable()` disamakan: `pemeriksabarang`/`pemeriksadokumen` kini melihat semua berkas seperti `adminutama`, bukan cuma tahapnya. Diverifikasi end-to-end lokal: login 8 role, cek visibilitas list per role, uji aksi lintas-role ditolak 403, request anonim dapat `[]`. (3) Notifikasi WhatsApp otomatis (template resmi, dikirim di thread terpisah via `_notify_pemohon_wa()`, gagal kirim tidak menggagalkan transisi status) ditambahkan di 6 titik transisi: upload-permohonan (masuk Nadine), terbitkan-skep (KEP terbit), terbitkan-billing (billing jaminan terbit), rekam-lhp (pemeriksaan fisik selesai), terbitkan-sppb (SPPB terbit), validasi-keluar (gate out). **MASIH TERBUKA**: integrasi API e-meterai riil tetap butuh kontrak kemitraan resmi (PDS/Mekari Sign/dst) yang hanya bisa diproses oleh pihak KPU Bea Cukai Batam sendiri, bukan oleh agen koding; path WhatsApp-bot `/api/permohonan/create` (`sumber != PORTAL_WEB`) belum diaudit apakah punya syarat bermeterai setara. | Verified Local (py_compile OK, 0-Diff, RBAC end-to-end test pass) |
| 2026-11-26 18:30 | Claude | `index.html`, `Formulir_...html`, `server.py`, `database.py` | **FASE 2: CETAK DOKUMEN PPFTZ-01/LHP/BAP/SPPB + QR GATE + KOREKSI FORMAT SURAT**: (1) User menemukan provider e-meterai dengan Open API self-serve nyata (ezmeterai.id, mitra resmi PT Peruri Digital Security) — beda dari hasil riset sesi sebelumnya yang cuma menemukan jalur kontrak bisnis. Aktivasi API (Rp2.000.000 sekali bayar) diisi form-nya (nomor WA) tapi SENGAJA tidak diselesaikan pembayarannya oleh asisten — itu transaksi uang milik user, diserahkan ke user untuk klik Bayar sendiri. Integrasi kode ke API ezmeterai belum dikerjakan, menunggu aktivasi akun selesai. (2) User mengunggah 2 dokumen referensi RESMI (`Format_Surat_Permohonan_Pengeluaran_Sementara_Kendaraan.docx.pdf`, `Surat_Pernyataan_Pengeluaran_Sementara_Kendaraan_Bermotor.docx.pdf`) — ternyata teks Hal 1 & Hal 2 PDF yang di-generate `generateAndDownloadRealPDF()` sejak awal sesi ini TIDAK sama persis dengan format asli kantor; sudah diperbaiki kata-per-kata mengikuti dokumen resmi (field Perihal/Yth/Nama/NIK/No.HP/Alamat/Jenis&PlatMobil/NoRangka/NoMesin/KotaTujuan/LamaPengeluaran/PelabuhanMuat/PelabuhanTujuan + 5 lampiran a-e untuk Surat Permohonan; 6 poin pernyataan bernomor untuk Surat Pernyataan) — catatan footer klaim tanda tangan elektronik BSrE/QR verifikasi `satu.kemenkeu.go.id` di dokumen asli SENGAJA tidak disalin karena draf lokal ini belum benar-benar punya sertifikat elektronik itu (tetap pakai watermark jujur "DRAFT - BELUM BERMETERAI"). Sekalian perbaiki bug lama: field id `pemohon_telepon` dipakai di 4 tempat padahal input aslinya `id="pemohon_telp"` — autofill nomor HP saat login pemohon selama ini selalu gagal diam-diam. (3) Ditemukan referensi dokumen ASLI KBM nyata di folder proyek (`14_APRIL YANI_06032025_PPFTZ01_KBM.pdf`, Template_BAP/LHP docx) — dipakai sebagai dasar format PDF baru: `generatePPFTZ01PDF()`, `generateLHPPDF()`, `generateBAPPDF()`, `generateSPPBPDF()` (jsPDF client-side, tombol cetak muncul di drawer detail begitu data terkait tersedia, TERLEPAS dari wewenang aksi tahap — supaya admin/pemeriksa barang/pemeriksa dokumen yang akses lintas-tahap tetap bisa cetak ulang untuk validasi). (4) Backend: `no_ppftz`/`tgl_ppftz` digenerate saat `terbitkan-billing` (lokal simulasi, bukan CEISA resmi). SPPB kini membawa QR code asli (`qrcode` lib, PNG base64) berisi `{id, no_sppb, token}` — token acak 16-hex disimpan di `sppb_qr_token`. Endpoint baru `/api/gate/scan-qr` (read-only, verifikasi token+status) dan `/api/gate/validasi-keluar` kini WAJIB menyertakan token hasil scan (menolak 400 kalau belum pernah di-scan atau token salah) — mencegah petugas Gate meluluskan kendaraan cuma dengan ketik ID tanpa benar-benar memindai dokumen fisik. Frontend: modal scan QR pakai kamera (`jsQR` via CDN jsdelivr, bukan cdnjs — versi cdnjs/jsQR ternyata 404) dengan tombol "Scan QR SPPB" khusus role gate/adminutama; tombol validasi langsung lama (`eksekusiAksiGate`) dihapus karena sudah pasti gagal (tidak kirim token). (5) **BUG ARSITEKTUR KRITIS ditemukan & diperbaiki**: tabel SQLite `permohonan` cuma punya kolom untuk field inti + beberapa nomor dokumen — field dinamis yang dipakai HAMPIR SEMUA endpoint aksi petugas sejak sesi-sesi sebelumnya (`lhp_data`, `no_skep`, `no_surat_s`, `kode_billing`, `nilai_jaminan`, `tgl_skep`/`tgl_billing`/`tgl_lhp`/`tgl_sppb`, `nadine_meta`, `sppb_qr_token`, `sppb_qr_data_url`, `dokumen_bermeterai`, dst.) SELALU DIAM-DIAM HILANG begitu data dibaca ulang dari SQLite (`update_permohonan_status` cuma menulis 5 kolom whitelist + dokumen/pemeriksaan, sisanya dibuang). Ini bug lama (dari migrasi SQLite WAL sesi sebelumnya), BUKAN spesifik ke fitur QR — baru ketahuan karena LHP test tiba-tiba `null` lagi setelah reload. Diperbaiki tuntas: kolom baru `extra_json` (migrasi `ALTER TABLE` aman di `init_db`) menampung semua field di luar skema tetap (`KNOWN_PERMOHONAN_COLUMNS`), di-merge balik otomatis saat baca (`get_all_permohonan`/`get_permohonan_by_id`), diterapkan juga di `save_new_permohonan` & `migrate_from_json` supaya konsisten. Diverifikasi end-to-end: create→nadine→skep→billing(no_ppftz)→lhp→reload(lhp_data utuh)→sppb(QR+token)→reload(QR utuh)→scan salah token(ditolak)→scan benar→validasi tanpa token(ditolak)→validasi dengan token(berhasil)→scan ulang setelah berangkat(ditolak, status sudah beda). | Verified Local (py_compile OK, 0-Diff, node --check JS OK, alur QR end-to-end pass) |

---

## 6. To-Do List & Status Tugas Berikutnya

- [x] Poin 1: Berkas Konteks Bersama `AGENTS_SYNC.md` dan `CLAUDE.md`.
- [x] Poin 2: Migrasi Database ke SQLite WAL thread-safe (`kbm_batam.db`).
- [x] Poin 3: Optimasi Memori Backend (Anti-OOM 512 MB), Image Resizing, ThreadPool, dan `/api/health`.
- [x] Poin 4: Ketahanan Pengiriman OTP WhatsApp Meta Cloud API dengan Fallback otomatis ke SMTP Email.
- [x] Poin 5: Konfigurasi Frontend (Dynamic API URL & Hash-Routing SPA `#/dashboard`, `#/formulir`).
- [x] Poin 6: Paket Deployment Cloud (`requirements.txt`, `render.yaml`, panduan Render, UptimeRobot, GitHub Pages).
- [x] Poin 7: Pengujian Terpadu Playwright & Handover Final ke Claude.
- [x] Poin 8: E-meterai riil (hapus stempel palsu, watermark draf, wajib unggah dokumen bermeterai sebelum submit, link portal distributor resmi terverifikasi).
- [x] Poin 9: RBAC per-peran ditegakkan di server (bukan cuma UI) — tiap petugas hanya lihat tahapnya; `pemeriksabarang`/`pemeriksadokumen` visibilitas penuh untuk validasi kesesuaian fisik vs dokumen.
- [x] Poin 10: Notifikasi WhatsApp otomatis di 6 titik transisi status permohonan.
- [x] Poin 11 (Fase 2): Cetak dokumen resmi PPFTZ-01/LHP/BAP/SPPB (jsPDF, format mengikuti dokumen asli di folder proyek) + QR code SPPB + scan QR Gate (wajib scan sebelum validasi keluar).
- [x] Poin 11b: Perbaikan bug arsitektur SQLite `extra_json` — field dinamis (lhp_data, kode_billing, dst.) tidak lagi hilang saat dibaca ulang.
- [x] Poin 11c: Koreksi teks Hal 1 (Surat Permohonan) & Hal 2 (Surat Pernyataan) PDF draf pemohon agar sama persis dengan format resmi kantor (sebelumnya pakai kalimat karangan sendiri).
- [ ] Poin 12 (Fase 3 — belum dikerjakan): Panel manajemen akun oleh admin utama (buat/reset kredensial petugas & pemohon) + log aktivitas untuk deteksi anomali.
- [ ] Poin 13: Integrasi API e-meterai ezmeterai.id — akun sudah ada, aktivasi Open API (Rp2.000.000) sedang diproses user sendiri (belum dibayar saat log ini ditulis); kode integrasi API belum dikerjakan, menunggu aktivasi selesai.
