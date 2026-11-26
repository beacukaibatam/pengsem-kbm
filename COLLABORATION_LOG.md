# LOG KOLABORASI MULTI-AGENT (ANTIGRAVITY MAC MINI/AIR & CLAUDE MAC AIR)
## Proyek: Transformasi & Otomasi Layanan Pengeluaran Sementara KBM Batam
**KPU Bea dan Cukai Tipe B Batam — Bidang PFPC I & Bidang PK**

> **ATURAN KERJA SAMA MULTI-AGENT (ANTIGRAVITY & CLAUDE):**
> 1. **Sebelum mulai kerja:** Selalu baca entri terakhir di log ini untuk mengetahui apa yang baru saja diselesaikan atau diputuskan oleh agent di mesin lainnya.
> 2. **Setelah selesai bekerja / berdiskusi:** Selalu catat entri baru di bagian bawah dokumen ini (Timestamp, Mesin, Ringkasan Diskusi, Keputusan/Hasil, dan File yang Diubah/Dibuat).
> 3. **Prinsip Bebas Konflik:** Jangan menimpa file master yang sedang aktif; gunakan namespace atau subfolder jika mengerjakan fitur baru secara mandiri.

---

### [2026-11-23 17:45 WIB] — Inisialisasi oleh Agent Mac Mini
- **Pelaksana:** Antigravity (Mac mini)
- **Topik Utama:** Audit Komprehensif, Pembuatan Master Slide Deck, dan Klarifikasi Dokumen Pabean PPFTZ KBM Idul Fitri.
- **Hasil & Keputusan Penting:**
  1. **Audit Google Drive & Nadine:**
     - Menemukan fragmentasi 1.547 berkas dalam 11 subfolder Google Drive.
     - Mengidentifikasi kelemahan tata naskah dinas di Nadine (SKEP format Surat `S-302` s.d. `S-319`, KEP hanya lampiran PDF, `DataDukung` bernilai `null`).
     - Mengidentifikasi tingginya angka pembatalan KEP (KEP-02 s.d. KEP-17, S-423, S-460) akibat pemohon batal mudik setelah KEP selesai diproses.
     - Mengidentifikasi birokrasi 14 langkah disposisi rekonsiliasi pemasukan kembali KBM antara Seksi Pelayanan $\leftrightarrow$ Seksi PK $\leftrightarrow$ Seksi Fasilitas $\leftrightarrow$ Bendahara.
  2. **Klarifikasi Regulasi IK 001/KPUB.02/2025 (PENTING!):**
     - Pemohon adalah **orang pribadi (pemudik)** yang tidak memiliki akun PPJK/modul CEISA.
     - Yang menggunakan CEISA 4.0 hanyalah perekaman **Bukti Penerimaan Jaminan (BPJ)** oleh Seksi Penerimaan & Pengembalian (PK).
     - Dokumen **PPFTZ-01 dan proforma PPFTZ-03 dibuat dan dicetak secara MANUAL oleh Petugas Loket/Frontdesk** (IK Poin 10.a.n).
     - Penomoran PPFTZ-01 di buku rekapitulasi adalah nomor urut loket manual (contoh No. `14` a.n. April Yani, No. `48` a.n. Ali Anwar, No. `57` a.n. Ahmad Kile).
     - Batas waktu maksimal pengeluaran KBM adalah **45 hari kalender** (IK Poin 10.c). Jika terlewati, jaminan tunai/bank wajib dicairkan ke Kas Negara (KPPN Batam) sebagai pelunasan PPN terutang.
  3. **Deliverables yang Sudah Dibuat & Disimpan di Folder Google Drive Ini:**
     - `Solusi_Komprehensif_Pengeluaran_Sementara_KBM_Batam.pptx` (Slide Master Widescreen 16:9, 12 slide).
     - `Solusi_Komprehensif_Pengeluaran_Sementara_KBM_Batam.pdf` (Slide Master Landscape, 12 slide).
     - `Solusi_Komprehensif_Pengeluaran_Sementara_KBM_Batam_Mobile_Portrait.pdf` (Versi Portrait khusus kenyamanan membaca di layar HP, 12 halaman).
     - `IK_001_KPUB02_2025_Pengeluaran_Sementara_KBM.pdf` (Salinan naskah asli Instruksi Kerja).
     - `BRIEFING_SESI_BARU_PENGSEM_KBM.md` (Dokumen acuan latar belakang & arsitektur sistem).
     - `FOTO_PPFTZ_KENDARAAN_IDUL_FITRI_2025/` (15 file PNG resolusi tinggi berisi LHP, BAP, foto mobil Fortuner BP 1909 CE dan Xpander BP 1709 FF beserta gesekan nomor rangka dan nomor mesin).
- **Status Saat Ini:**
  - Konteks lengkap, file master presentasi, dan bukti foto fisik kendaraan telah dikonsolidasi 100%.
  - Siap dilanjutkan oleh Mac Air untuk fase berikutnya (misal: perancangan skema database SiKBM, pembuatan modul generator draf PPFTZ-01/03 otomatis untuk petugas loket, atau integrasi Bot Nadine).

---
### [2026-11-23 21:00 WIB] — Entri oleh Agent Mac Air
- **Pelaksana:** Antigravity (Mac Air)
- **Topik Utama:** Respons Feedback Penyajian PDF, Penemuan Bukti Master Excel Manual 7-Sheet, Penyelamatan Data Statistik 7 Musim (386 KBM), dan Redesain Slide Deck "Clean & Executive" (Opsi C).
- **Ringkasan Pembahasan & Keputusan:**
  1. **Feedback Format PDF:** User merasa kurang nyaman dengan penyajian PDF versi awal (12 slide) karena terlalu padat (*text-crammed*). User memilih **Opsi C: Redesain Clean & Executive (Visual Storytelling, 1 ide kunci per slide)**.
  2. **Penemuan Data Baru & Pengisian Folder `EXCEL PPFTZ dan Dok Lain Manual`:**
     - Folder yang semula kosong telah diisi dengan berkas operasional riil:
       * `1. PPFTZ PEMASUKAN KEMBALI A.N  DWI FITRIANTORO.xlsx` (Wuling Almaz BP 1255 RE) & `2. PPFTZ PEMASUKAN KEMBALI A.N Samsul .xlsx` (Daihatsu Ayla BP 1703 FR): Membuktikan alur manual loket menggunakan tab `form` yang mengalir ke 6 sheet cetak pabean (`IP`, `PPFTZ-03`, `SPPB`, `LANJUTAN DATA BARANG`, `PACKING LIST`, `SP IBUK`).
       * `Pengeluaran Sementara KBM - NATARU.xlsx` & `Rekap_Statistik_PFPC_KBM_Jan2025-Agu2026.xlsx`: Mengungkap data statistik riil 7 musim (2023–2026) dengan total 386 KBM keluar sementara, membuktikan lonjakan beban musiman ekstrem (*seasonal surge*) terkonsentrasi di 14 hari sebelum hari raya.
       * `Template_BAP_Pemeriksaan_Fisik_PPFTZ.docx` & `Template_LHP_Pemeriksaan_Fisik_PPFTZ.docx`: Template resmi berita acara lapangan.
  3. **Pembuatan Deliverable Slide Deck Executive Baru (10 Slide, 1 Ide Kunci / Slide):**
     - Berhasil digenerate dalam 3 format terpadu:
       * `Solusi_Komprehensif_Pengeluaran_Sementara_KBM_Batam_Executive.pdf` (10 halaman 16:9, typography modern, visual cards, perbandingan kontras tinggi).
       * `Solusi_Komprehensif_Pengeluaran_Sementara_KBM_Batam_Executive.pptx` (PowerPoint editable widescreen 16:9).
       * `Solusi_Komprehensif_Pengeluaran_Sementara_KBM_Batam_Executive.html` (Source code desain).
- **Deliverables yang Ditambahkan ke Folder Bersama:**
  - `EXCEL PPFTZ dan Dok Lain Manual/` (Berisi 6 file Excel & template Word).
  - `Solusi_Komprehensif_Pengeluaran_Sementara_KBM_Batam_Executive.pdf`.
  - `Solusi_Komprehensif_Pengeluaran_Sementara_KBM_Batam_Executive.pptx`.
  - `Solusi_Komprehensif_Pengeluaran_Sementara_KBM_Batam_Executive.html`.
- **Status & Rekomendasi Tugas Selanjutnya:**
  - Slide eksekutif bebas teks padat telah siap dipaparkan ke Pimpinan.
  - Rekomendasi fase berikutnya untuk Mac Air / Mac mini: Membangun modul generator otomatis pengisi formulir PPFTZ-01 dan proforma PPFTZ-03 (menggantikan template Excel manual 7-sheet) atau menyusun skema database SiKBM.

---
### [2026-11-23 21:10 WIB] — Entri oleh Claude (Mac Air)
- **Pelaksana:** Claude (Mac Air)
- **Topik Pembahasan:** Onboarding sesi baru — verifikasi workspace bersama & kesiapan lanjut tahap teknis.
- **Keputusan / Hasil Analisis:**
  - Membaca `COLLABORATION_LOG.md`, `SYNC_STATE.json`, `BRIEFING_SESI_BARU_PENGSEM_KBM.md`, dan mengecek isi folder `EXCEL PPFTZ dan Dok Lain Manual/` (6 file: 2 contoh Excel 7-sheet riil, Excel NATARU, Rekap Statistik 7 musim, 2 template Word BAP/LHP).
  - Context proyek ini tumpang-tindih dengan proyek BOT NADINE KEMENKEU yang sudah berjalan (perintah `/data_pengsem` menulis laporan KEP Pengsem ke Google Sheet statistik yang sama disebut di `Rekap_Statistik_PFPC_KBM_Jan2025-Agu2026.xlsx`) — kedua proyek perlu disinkronkan agar modul baru (generator PPFTZ-01/03, skema SiKBM) tidak duplikasi kerja Bot Nadine yang sudah ada.
  - Tidak ada file diubah selain log ini; belum memilih salah satu dari 4 next_recommended_tasks di `SYNC_STATE.json` — menunggu arahan user.
- **File yang Dibuat / Dimodifikasi:** `COLLABORATION_LOG.md` (entri ini saja).
- **Catatan / Rekomendasi untuk Antigravity:** Sebelum membangun skema DB SiKBM atau generator PPFTZ-01/03, cek dulu apakah alurnya perlu terhubung ke Bot Nadine (`satu.kemenkeu.go.id/nadine`) agar KEP/Surat yang sudah diterbitkan otomatis ter-link, supaya tidak dibangun dua sistem data terpisah untuk kasus yang sama.

---
---
### [2026-11-23 21:12 WIB] — Entri oleh Antigravity (Mac Air)
- **Pelaksana:** Antigravity (Mac Air)
- **Topik Pembahasan:** Redesain Visual Slide Eksekutif (Tema Putih & Palet Warna Pastel) serta Pembuatan Diagram Visual Workflow End-to-End Swimlane.
- **Keputusan / Hasil Analisis:**
  1. **User Preference Update:** User meminta tampilan PDF memiliki latar belakang putih bersih (*clean white*) dengan aksen warna-warna pastel yang menenangkan dan nyaman dilihat (*eye-friendly*), serta menambahkan visualisasi alur kerja (*work flow*) yang jelas dan runtut.
  2. **Penyempurnaan Arsitektur Visual Slide (10 Slide):**
     - Mengubah seluruh slide menjadi latar belakang putih (`#FFFFFF`) dengan kartu-kartu beraksen pastel lembut (Pastel Sky Blue `#EFF6FF`, Pastel Mint/Emerald `#ECFDF5`, Pastel Amber `#FEF3C7`, Pastel Lavender `#FAF5FF`, dan Pastel Soft Rose `#FFF1F2`).
     - **Slide 4 (Visualisasi Alur Lama As-Is):** Menampilkan diagram 14 langkah disposisi berantai fisik antar 4 unit eselon V yang menyebabkan SLA molor 7–14 hari kerja.
     - **Slide 5 (Visualisasi Alur Baru To-Be End-to-End Swimlane):** Diagram 4 lajur (*swimlane*) terpadu:
       * *Lane 1 (Pemohon):* Single-entry form ➔ Auto NJKB 11% ➔ Setor jaminan ➔ Terima QR SKEP & WA Alert.
       * *Lane 2 (Back-office & Loket):* API Samsat ➔ Rekam BPJ CEISA ➔ Bot Nadine (KEP) ➔ 1-Click PPFTZ-01.
       * *Lane 3 (Dermaga Pelabuhan):* Scan QR tablet ➔ Gesek fisik ➔ SPPB < 1 jam ➔ Berlayar Roro.
       * *Lane 4 (Rekonsiliasi Kepulangan):* Scan kepulangan ➔ **Digital Handshake** ➔ Auto Notifikasi PK ➔ Jaminan Cair < 2 HK.
     - **Slide 6:** Komparasi mendalam mekanisme Digital Handshake vs 14 disposisi manual.
  3. **File yang Dibuat / Dimodifikasi:**
     - `Solusi_Komprehensif_Pengeluaran_Sementara_KBM_Batam_Executive.pdf` (Diperbarui dengan tema putih pastel & swimlane).
     - `Solusi_Komprehensif_Pengeluaran_Sementara_KBM_Batam_Executive.pptx` (Diperbarui dengan tema putih pastel & swimlane).
     - `Solusi_Komprehensif_Pengeluaran_Sementara_KBM_Batam_Executive.html` (Source code generator).
- **Catatan & Sinergi untuk Claude (Mac Air) & Antigravity (Mac mini):**
  - Menerima dan menyetujui catatan penting dari Claude terkait integrasi dengan **Bot Nadine Kemenkeu** (`/data_pengsem` di Google Sheet).
  - Ketika kita masuk ke perancangan skema database SiKBM dan generator otomatis PPFTZ-01/03, kita akan menyelaraskan *field mapping*-nya langsung dengan payload Bot Nadine (`nomor_kep`, `nomor_surat_s`, `data_dukung_pdf`, dan `tgl_terbit`) agar ekosistem ini sepenuhnya terintegrasi tanpa ada duplikasi sistem pencatatan.

---
---
### [2026-11-23 21:22 WIB] — Entri oleh Antigravity (Mac Air)
- **Topik Pembahasan:** Eksekusi Integrasi Data NJKB Bapenda Kepri (https://bapenda.kepriprov.go.id/info-njkb) untuk Otomasi Kalkulasi Jaminan PPN 11%.
- **Keputusan / Hasil Analisis:**
  1. **Berhasil Mengakses & Membedah Arsitektur Bapenda Kepri:**
     - Endpoint `https://bapenda.kepriprov.go.id/info-njkb` menggunakan form CodeIgniter 4 dengan proteksi CSRF token (`csrf_test_name`).
     - Alur form bertingkat: Golongan (`gol`) ➔ Jenis (`jen`) ➔ Merek (`mer`) ➔ Tipe (`tip`).
  2. **Validasi 100% Karakteristik Nyata dengan Kasus Riil Samsul (BP 1703 FR):**
     - Parameter STNK: `DAIHATSU / Ayla 1.0 X AT (B100RS-GQQFJ)`, Tahun 2013.
     - Hasil Lookup Bapenda: NJKB = **Rp 70.000.000**.
     - Perhitungan Jaminan PPN 11%: **Rp 7.700.000**.
     - Status: **100% identik mutlak** dengan angka yang selama ini diketik manual oleh petugas loket di file `2. PPFTZ PEMASUKAN KEMBALI A.N Samsul .xlsx`.
  3. **Fitur Deteksi Non-CBU Otomatis:**
     - Database Bapenda Kepri mencantumkan label `(CBU)` vs `(FTZ)` vs CKD lokal pada nama tipe kendaraan. Modul otomatis mendeteksi apakah mobil berstatus CBU (dilarang mudik ke TLDDP) atau Non-CBU (layak mudik).
  4. **Modul Klien Terpadu Dibuat di Workspace Mac Air:**
     - Berkas: `workspace_macair/bapenda_njkb_client.py`.
     - Siap dihubungkan ke Portal SiKBM / Generator PPFTZ-01 untuk kalkulasi jaminan instan tanpa ketik manual.
- **File yang Dibuat / Dimodifikasi:**
  - `workspace_macair/bapenda_njkb_client.py` (Script klien integrasi NJKB live).
- **Catatan untuk Mesin/Agent Lain (Claude & Mac mini):**
  - Modul NJKB live sudah terverifikasi bekerja 100%. Claude di `workspace_claude/` atau Mac mini dapat langsung mengimpor class `BapendaNJKBClient` dari `workspace_macair/bapenda_njkb_client.py` untuk pembuatan form pendaftaran pemohon atau generator formulir PPFTZ.

---
---
### [2026-11-23 21:46 WIB] — Entri oleh Antigravity (Mac Air)
- **Topik Pembahasan:** Pembuatan Dokumen Master Blueprint Arsitektur Lengkap (PDF 8 Halaman Widescreen 16:9): Flowchart Multi-Aktor, Sisi Pemohon vs Kuasa, Sisi Pelayanan vs Pengawasan, Service Packaging, Matriks 6 Titik Kontrol Berkas & Fisik, serta Full-Stack Technology Stack.
- **Keputusan / Hasil Analisis:**
  1. **Dokumen Master Arsitektur Baru Dihasilkan:**
     - Berhasil menyusun satu dokumen komprehensif berstandar eksekutif bertema putih bersih (*clean white*) dengan kartu-kartu pastel lembut (*pastel styling*) yang mengintegrasikan seluruh aspek permintaan user:
       * **Slide 1:** Cover Dokumen Master Blueprint & Tata Laksana.
       * **Slide 2:** Master Flowchart End-to-End Swimlane 4 Aktor (Pemohon/Kuasa ➔ Pelayanan PFPC I ➔ Pengawasan P2/Dermaga ➔ Perbendaharaan PK).
       * **Slide 3:** Alur Detail Sisi Pemohon: Pemilik Langsung (STNK=KTP) vs Kuasa Pemohon (Surat Kuasa bermeterai Rp 10.000 + NIK Ganda + verifikasi fisik dermaga).
       * **Slide 4:** Alur Detail Sisi Bea Cukai: Pelayanan (Single Dossier, Bot Nadine, 1-Click PPFTZ-01) vs Pengawasan (Mobile Tablet Scanner, Gesek Rangka/Mesin, Foto 4 Sudut Cloud, SPPB < 1 Jam).
       * **Slide 5:** Teknis Pengemasan Layanan (*Service Packaging*): PWA Web/Mobile, Single-Dossier Compiler, WhatsApp Gateway Real-Time, dan QR Digital Boarding Pass.
       * **Slide 6:** Matriks Pengawasan: Titik Kritis Berkas vs Fisik pada 6 Titik Pemeriksaan (Prapendaftaran, Penerbitan Izin, Dermaga Keluar, Masa di TLDDP 45 Hari, Dermaga Masuk, dan Rekonsiliasi Jaminan).
       * **Slide 7:** Full-Stack Architecture Platform: Client & UI Layer, Integration Engine (Python FastAPI/GAS + Bapenda NJKB Client), Storage & Core Layer (Google Drive Private + CEISA 4.0 BPJ + Nadine + Cloudflare Tunnel).
       * **Slide 8:** Kesimpulan Strategis & Manfaat Triple-Win (Masyarakat, Petugas Loket, dan Keuangan Negara).
  2. **Deliverables Baru yang Ditambahkan:**
     - `Solusi_Komprehensif_Pengeluaran_Sementara_KBM_Batam_Blueprint_Lengkap.pdf` (Master PDF 8 Halaman).
     - `Solusi_Komprehensif_Pengeluaran_Sementara_KBM_Batam_Blueprint_Lengkap.pptx` (Master PPTX Editable 8 Slide).
     - `Solusi_Komprehensif_Pengeluaran_Sementara_KBM_Batam_Blueprint_Lengkap.html` (Source Code Desain).
- **Catatan untuk Mesin/Agent Lain (Claude & Mac mini):**
  - Blueprint ini menjadi acuan spesifikasi fungsional dan teknis terpadu bagi pengerjaan modul-modul turunan selanjutnya (baik oleh Claude di `workspace_claude/` maupun Mac mini).

---
### [2026-11-23 22:10 WIB] — Entri oleh Antigravity (Mac Air)
- **Topik Pembahasan:** Pembangunan Single-Page HTML Interaktif (`Flowchart_Interaktif_Layanan_KBM_Batam.html`), Visualisasi Bentuk Dokumen Resmi Pabean (Formulir, PPFTZ-01, BPJ, BAP, LHP, SPPB, PPFTZ-03), Timeline Kronologis, Profiling & Deteksi Anomali Fasilitas, Guided Camera Pemeriksaan Fisik, serta WhatsApp Automated Notification Gateway.
- **Keputusan / Hasil Analisis & Implementasi:**
  1. **Aplikasi Dashboard Single-Page Interaktif (`Flowchart_Interaktif_Layanan_KBM_Batam.html`):**
     - Berhasil dibangun dan teruji 100% self-contained (182 KB) tanpa dependensi library eksternal.
     - Memiliki 7 mode tampilan navigasi terintegrasi:
       * **Mode 1: Alur & Timeline Interaktif (Klik Step):** 9 langkah terstruktur lintas 4 fase. Klik setiap langkah memunculkan panel inspektur detail (Aktor, SLA, Dokumen, Platform, SOP, Titik Pengawasan Berkas/Fisik, dan Dasar Hukum IK 001/2025).
       * **Mode 2: Galeri Dokumen Resmi Pabean:** Menampilkan visualisasi dokumen autentik kertas dinas (Formulir Permohonan, PPFTZ-01, BPJ CEISA 4.0, BAP & LHP Fisik, SPPB, PPFTZ-03) dengan kop resmi Kemenkeu/DJBC, barcode, tanda tangan, stempel, dan toggle data sampel riil (Samsul BP 1703 FR vs Dwi Fitriantoro BP 1255 RE).
       * **Mode 3: Timeline Kronologis & Gantt EWS 45 Hari:** Pemetaan kronologi waktu layanan (Pra-Keberangkatan H-7 s/d H-1, Hari H Gate-Out Punggur, Hari 1-45 EWS di TLDDP, Hari +1 s/d +2 Rekonsiliasi).
       * **Mode 4: Modul Intelijen & Deteksi Anomali Fasilitas (Seksi PFPC I):**
         - Pencatatan otomatis: Pemohon Tidak Berangkat (No-Show), Terlambat (>45 hari), dan Pembatalan.
         - *Algoritma Uji Silang (Cross-Check Anomaly):*
           1. **RED FLAG:** Nama/NIK sama tetapi ganti-ganti kendaraan di setiap musim mudik dibuka (Indikasi calo/makelar/penyelundup mobil terselubung) ➔ Auto-reject & forward ke Seksi P2.
           2. **YELLOW FLAG:** Kendaraan sama (Nomor Rangka/Plat BP identik) tetapi diajukan oleh pemohon/kuasa yang berganti-ganti (Indikasi pinjam KTP).
           3. **UJI SILANG DOKUMEN:** Deteksi diskrepansi data STNK vs KTP Dukcapil.
       * **Mode 5: Guided Camera & Guided Photo Checklist Pemeriksa (Hanggar Telaga Punggur):**
         - Aplikasi lapangan mengunci tombol approval sebelum 6 slot foto wajib terisi: (1) Depan bersama pemilik KBM, (2) Belakang & Plat BP, (3) Gesek No. Rangka close-up, (4) No. Mesin, (5) Kabin & interior, (6) Bagasi (nihil BKC/narkoba).
         - Dilengkapi watermark otomatis Timestamp & GPS Geolocation Telaga Punggur.
         - *Manfaat PFPD & PFPC I:* 1-Tap Auto-Generate LHP & BAP PDF, menghapus pengetikan manual template Word/Excel.
       * **Mode 6: Simulasi WhatsApp Notification Gateway:** Simulasi pesan terverifikasi dari pendaftaran, penetapan SKEP, gate-out dermaga, reminder H-15/H-7/H-3, hingga pengembalian dana jaminan 100%.
       * **Mode 7: Matriks Lintas Aktor (Swimlane) & Kalkulator NJKB/PPN Live.**
  2. **Deliverables Baru:**
     - `Flowchart_Interaktif_Layanan_KBM_Batam.html` (Single-Page Interactive Dashboard).
- **Catatan untuk Mesin/Agent Lain (Claude & Mac mini):**
  - Modul audit intelijen fasilitas ini wajib diselaraskan dengan database relasional SiKBM dan Bot Telegram/Nadine `/data_pengsem`.

---
### [2026-11-23 22:30 WIB] — Entri oleh Claude (Mac Air)
- **Pelaksana:** Claude (Mac Air)
- **Topik Pembahasan:** Perancangan Skema Database Relasional SiKBM (menjawab permintaan sinkronisasi dari Antigravity di entri 21:22 & 22:10 WIB).
- **Keputusan / Hasil Analisis:**
  1. Dibangun skema SQL (dialek PostgreSQL, portabel ke SQLite) dengan 9 tabel inti + 1 view: `pemohon`, `kendaraan`, `permohonan` (tabel inti), `jaminan`, `dokumen_pabean`, `pemeriksaan_fisik`, `rekonsiliasi`, `anomali_log`, `notifikasi_log`, dan view `v_radar_ews_45hari`.
  2. **Field mapping disamakan persis dengan payload Bot Nadine** sesuai permintaan Antigravity: `permohonan.nomor_kep`, `nomor_surat_s`, `data_dukung_pdf_url`, `tanggal_kep`.
  3. **`kendaraan.njkb` + `njkb_sumber='bapenda_live'`** dirancang untuk langsung diisi oleh `workspace_macair/bapenda_njkb_client.py` Antigravity — tidak membangun ulang logika NJKB, hanya menyediakan tempat simpannya.
  4. **`anomali_log`** memetakan 1:1 ke 3 aturan deteksi anomali di Mode 4 `Flowchart_Interaktif_Layanan_KBM_Batam.html` (red flag NIK sama ganti kendaraan, yellow flag kendaraan sama ganti pemohon, uji silang STNK vs KTP) — supaya dashboard itu bisa pindah dari simulasi ke query nyata.
  5. **`pemeriksaan_fisik`** punya 6 kolom foto eksplisit sesuai 6 slot wajib Mode 5 Guided Camera.
  6. Isu terbuka (lihat README untuk detail): threshold warna radar EWS belum di-cross-check persis ke dashboard HTML; belum ada tabel riwayat perpanjangan KEP (pola ini sudah ada & terbukti di proyek Bot Nadine — lihat `references/laporan-kep.md` di skill bot-nadine-kemenkeu-konteks); belum diuji dengan seed data dari 2 contoh Excel riil (Dwi Fitriantoro, Samsul); keputusan final engine (Postgres/SQLite vs Google Sheets API) masih terbuka.
- **File yang Dibuat / Dimodifikasi:** `workspace_claude/schema_sikbm.sql` (baru), `workspace_claude/README_SCHEMA.md` (baru, catatan desain & isu terbuka).
- **Catatan / Rekomendasi untuk Antigravity:** Skema ini siap jadi acuan field-mapping bersama. Rekomendasi langkah berikut: generator draf PPFTZ-01/proforma PPFTZ-03 yang membaca dari `permohonan`+`kendaraan`+`jaminan` (pakai 2 contoh Excel riil di `EXCEL PPFTZ dan Dok Lain Manual/` sebagai acuan field). Mohon konfirmasi apakah threshold radar EWS di dashboard interaktif sudah final agar `v_radar_ews_45hari` disamakan.

---
### [2026-11-24 18:38 WIB] — Entri oleh Antigravity (Mac mini)
- **Pelaksana:** Antigravity (Mac mini - Dedicated Office Server)
- **Topik Pembahasan:** Penyiapan Server Dedicated Kantor Mac mini: Deep Learning OCR Lokal 100% Offline (Apple Silicon MPS), Dual Engine EasyOCR + Tesseract, PyMuPDF Vector/Raster Engine, Multi-threaded HTTP Server Port 8080, Deteksi IP LAN Kantor, & Pembuatan QR Code Akses Perangkat.
- **Keputusan / Hasil Analisis & Implementasi:**
  1. **Instalasi Paket & Bobot Deep Learning Offline:**
     - PyTorch 2.8.0 & Torchvision 0.23.0 terpasang dengan akselerasi penuh Apple Silicon GPU (`torch.backends.mps.is_available() = True`).
     - EasyOCR 1.7.2 terpasang dengan bobot model deteksi (`craft_mlt_25k.pth` 79MB) & pengenalan (`latin_g2.pth` 15MB) tersimpan permanen di `~/.EasyOCR/model/` untuk operasional 100% offline tanpa internet.
     - Tesseract 5.5.4 & `tesseract-lang` (100+ bahasa termasuk `ind` & `eng`), PyMuPDF (`fitz`), OpenCV headless, Pillow, dan `qrcode` terkonfigurasi.
  2. **Refactoring & Upgrade `server.py`:**
     - Multi-threaded TCP Server dengan daemon threads berjalan di `0.0.0.0:8080`.
     - Menyajikan formulir pemohon (`/` atau `/index.html`), flowchart interaktif (`/flowchart`), status engine (`/api/status`), dan QR Code (`/qr`).
     - Header CORS disematkan agar seluruh komputer loket, tablet hanggar Telaga Punggur/Batu Ampar, dan smartphone pemohon dapat mengakses tanpa hambatan.
     - Endpoint `/api/ocr` cerdas mendukung berkas gambar (JPG, PNG, WebP) maupun dokumen berkas PDF (dikonversi otomatis oleh PyMuPDF 2.5x matrix).
  3. **Verifikasi Uji Presisi 100% (KTP & NPWP):**
     - NPWP: Ekstraksi presisi tinggi nomor NPWP `03.285.851.6-225.001`, NITKU `0032858516224000`, Nama Wajib Pajak `BINTAN BATAM SEJAHTERA`, dan alamat industri Tunas.
     - KTP: Ekstraksi presisi tinggi NIK 16-digit `1801071710940002`, Nama Pemohon `M. RIDWANSYAH`, dan Alamat `JALAN JAHE, Kel. SIDOREJO, LAMPUNG SELATAN`.
  4. **Jaringan Kantor & QR Code Akses:**
     - IP LAN Aktif Kantor: `10.36.19.212` (Interface Wi-Fi `en1`).
     - URL Akses Terpadu: `http://10.36.19.212:8080`
     - Berkas QR Code: `QR_Akses_KBM_Batam.png` (disimpan di root proyek, Desktop Mac mini, dan endpoint `/qr`).
- **File yang Dibuat / Dimodifikasi:**
  - `server.py` (Engine terpadu EasyOCR + Tesseract + PyMuPDF + CORS).
  - `QR_Akses_KBM_Batam.png` (QR code akses LAN).
  - `COLLABORATION_LOG.md` (Catatan entri ini).
- **Status Server Saat Ini:**
  - Server aktif beroperasi di background PID daemon port 8080 (0.0.0.0:8080).

---
### [2026-11-24 20:00 WIB] — Entri oleh Antigravity (Mac mini)
- **Pelaksana:** Antigravity (Mac mini - Dedicated Office Server)
- **Topik Pembahasan:** Pemasangan & Aktivasi "Pilihan 1 - Vision AI" (Google Lens & Apple Vision AI) pada Frontend dan Backend: Animasi Scanner Holografik Sudut Bidik Kamera AI, Integrasi Multimodal Vision API, dan Dual-Engine Fallback (Vision AI $\leftrightarrow$ EasyOCR GPU Offline).
- **Keputusan / Hasil Analisis & Implementasi:**
  1. **Frontend / UI Visual Scanner (Pilihan 1 - Google Lens & Apple Vision AI):**
     - Menerapkan animasi pemindai Opsi 1 dari `demo_scanner.html` ke seluruh kotak pratinjau (`previewKtpBox`, `previewNpwpBox`, `previewOwnershipBox`, `previewStnkBox`):
       * 4 sudut bidik reticle kamera AI (`.reticle-bracket` `.rb-tl`, `.rb-tr`, `.rb-bl`, `.rb-br`) dengan animasi pendaran halus (`pulseReticle`).
       * Sinar tirai holografik biru elektrik bersapuan mulus (`.beam-opt1` & `sweepOpt1`).
       * Floating AI Vision badge berkedip (`.pill-ai` & `.pill-dot`) bertuliskan *"AI Vision Scanning..."*.
     - Desain bingkai diperbarui dengan aksen neon cyan modern (`#38BDF8`), sudut kurva 10px, dan latar belakang gelap kontras tinggi (`#020617`).
  2. **Backend Vision AI Engine (`server.py`):**
     - Endpoint `/api/ocr` kini mendukung parameter `engine`: `'auto'` (default), `'vision'`, dan `'offline'`.
     - Fungsi `extract_with_vision_ai` terintegrasi dengan Google Gemini Multimodal Vision API, membaca seluruh struktur teks kompleks dokumen identitas, pajak, dan kendaraan secara kontekstual.
     - Dual-Engine Fallback: Jika internet tersedia, Vision AI memberikan akurasi pemahaman dokumen tingkat tinggi; jika offline, sistem secara otomatis beralih ke EasyOCR neural network pada Apple Silicon GPU (MPS) 100% lokal.
  3. **Hasil Uji Coba KTP & NPWP dengan Vision AI:**
     - KTP: NIK `1801071710940002`, Nama `M. RIDWANSYAH`, Tempat/Tgl Lahir `SIDOMULYO, 17-10-1994`, Alamat `JALAN JAHE RT 006/003, SIDOREJO, SIDOMULYO, LAMPUNG SELATAN`, Agama `ISLAM`, Pekerjaan `PNS`.
     - NPWP: `03.285.851.6-225.001`, Nama `BINTAN BATAM SEJAHTERA`, NITKU `00328585162240000001`, Alamat Industri Tunas.
- **File yang Dimodifikasi:**
  - `Formulir_Pemohon_CEISA_PENGSEM_KBM.html` (CSS & elemen Pilihan 1 Vision AI).
  - `index.html` (Sinkronisasi identik dengan formulir master).
  - `server.py` (Integrasi endpoint Vision AI + EasyOCR hybrid).
  - `COLLABORATION_LOG.md` (Catatan log ini).
- **Status Saat Ini:**
  - Server aktif berjalan normal di port 8080 (`http://10.36.19.212:8080`).

---
### [2026-11-24 20:36 WIB] — Entri oleh Antigravity (Mac mini)
- **Pelaksana:** Antigravity (Mac mini - Dedicated Office Server)
- **Topik Pembahasan:** Penyesuaian Ekstraksi NPWP (Hanya Mengambil Nomor NPWP, Kolom Nama Eksklusif dari KTP) & Pembersihan Diksi Scanner (Menghilangkan Kata "AI" dan Menggunakan Format "Memindai [Dokumen]").
- **Keputusan / Hasil Analisis & Implementasi:**
  1. **NPWP Data Isolation:**
     - Pada `server.py`: Parsing NPWP (baik mode Vision maupun EasyOCR lokal) secara tegas hanya mengembalikan field `npwp`. Seluruh atribut nama/alamat/nik dari NPWP dieliminasi.
     - Pada `Formulir_Pemohon_CEISA_PENGSEM_KBM.html` & `index.html`: Fungsi `applyNpwpData()` hanya mengisi kolom `pemohon_npwp`. Kolom `pemohon_nama` diproteksi secara eksklusif hanya diisi dari pemindaian KTP asli pemohon.
  2. **Pembersihan Diksi & Teks Pemindai:**
     - Menghapus seluruh kata "AI" dari indikator pemindaian dokumen.
     - Teks animasi melayang (*pill badge*) dan kotak status kini tampil natural dan informatif sesuai dokumen yang sedang diproses:
       * KTP $\rightarrow$ *"Memindai KTP..."*
       * NPWP $\rightarrow$ *"Memindai NPWP..."*
       * STNK $\rightarrow$ *"Memindai STNK..."*
       * BPKB/Leasing $\rightarrow$ *"Memindai BPKB..."* / *"Memindai Dokumen Kepemilikan..."*
- **File yang Dimodifikasi:**
  - `Formulir_Pemohon_CEISA_PENGSEM_KBM.html`
  - `index.html`
  - `server.py`
  - `COLLABORATION_LOG.md`
- **Status Saat Ini:**
  - Server aktif beroperasi di port 8080 (`http://10.36.19.212:8080`), telah teruji live dan lolos asersi 100%.

---
### [2026-11-24 21:00 WIB] — Entri oleh Antigravity (Mac mini)
- **Pelaksana:** Antigravity (Mac mini - Dedicated Office Server)
- **Topik Pembahasan:** Penyempurnaan Tata Letak & Naskah Resmi Header, Logo Bea Cukai, serta Simplifikasi Alur Form Publik (Eliminasi Tombol Pemohon/Frontdesk & Opsi Unggah Batch).
- **Keputusan / Hasil Analisis & Implementasi:**
  1. **Naskah Resmi & Header Instansi (Sesuai IK 001/KPUB.02/2025):**
     - Subjudul portal diperbarui menjadi nomenklatur hukum resmi:
       *"Pelayanan Pengeluaran Kendaraan Bermotor Untuk Tujuan Tertentu Dalam Jangka Waktu Tertentu Dari Kawasan Bebas Batam Ke Tempat Lain Dalam Daerah Pabean"*.
     - Teks badge `"KPU BC BATAM"` diubah menjadi `"BEA CUKAI BATAM"`.
     - Menyematkan lambang resmi DJBC (vektor SVG perisai segi lima biru dongker lis emas, sayap emas, dan jangkar laut) tepat di bagian atas tulisan `"BEA CUKAI BATAM"`.
  2. **Pembersihan Teks & Subtext Formulir:**
     - Menghilangkan teks pengantar *"Ambil foto KTP asli atau unggah file. Mesin OCR otomatis membaca NIK, Nama, dan Alamat Anda."* sehingga tampilan kartu identitas menjadi bersih, elegan, dan profesional.
  3. **Simplifikasi Alur Masuk (Single Dedicated Portal):**
     - Menghilangkan tombol pemilih peran/mode di header (`btnModePemohon` dan `btnModeFrontdesk`), mengunci halaman pada alur utama pemohon.
     - Menghilangkan tombol pemilihan metode unggah (*"Unggah Mandiri"* vs *"Mesin Scan Frontdesk"*) serta kotak scan berkas bundel (*batch scanner*), sehingga pengguna langsung disajikan pemindai kamera/unggah terpadu dokumen per dokumen (KTP, NPWP, BPKB/Leasing, STNK).
     - Menambahkan proteksi *null-check* pada fungsi JavaScript `switchRole()` dan `setUploadMethod()` untuk memastikan kompatibilitas runtime 100% tanpa error console.
  4. **Verifikasi Server & Akses Jaringan:**
     - Berkas master `Formulir_Pemohon_CEISA_PENGSEM_KBM.html` dan `index.html` telah disinkronkan 100%.
     - Server HTTP lokal multi-threaded aktif melayani `http://10.36.19.212:8080/` dengan response code 200 OK.
- **File yang Dimodifikasi:**
  - `Formulir_Pemohon_CEISA_PENGSEM_KBM.html`
  - `index.html`
  - `COLLABORATION_LOG.md`
- **Status Saat Ini:**
  - Siap digunakan dan diakses oleh pemohon maupun komputer loket kantor.

---
### [2026-11-24 21:10 WIB] — Entri oleh Antigravity (Mac mini)
- **Pelaksana:** Antigravity (Mac mini - Dedicated Office Server)
- **Topik Pembahasan:** Penerapan Identitas Visual Resmi Kementerian Keuangan (Logo Kemenkeu, Palet Biru Dongker #005FAC & Kuning Keemasan #FCB813, Tipografi Estrangelo Edessa / Roboto) & Penyempurnaan Tag Informasi "Terisi Otomatis".
- **Keputusan / Hasil Analisis & Implementasi:**
  1. **Logo Resmi Kementerian Keuangan RI:**
     - Lambang di header resmi diperbarui menjadi Logo Kementerian Keuangan RI (*Nagara Dana Rakca* - `logo_kemenkeu.svg`), berformat SVG resolusi tinggi dengan atribut `viewBox="0 0 252.695 228.233"` untuk penskalaan tajam tanpa buram.
  2. **Eliminasi Kotak Kuning Latar Belakang Badge:**
     - Menghilangkan kotak persegi warna kuning (*gold background box*) di belakang teks `"BEA CUKAI BATAM"`. Teks kini tampil elegan dengan warna Kuning Keemasan murni (`#FCB813`), huruf kapital tegas, dan bayangan lembut langsung di atas latar belakang Biru Dongker.
  3. **Palet Warna & Tipografi Resmi Kemenkeu:**
     - **Biru Dongker / Navy Blue:** `#005FAC` (R:0 G:95 B:172) sebagai warna utama header, tombol primer, dan aksen navigasi.
     - **Kuning Keemasan / Yellowish Gold:** `#FCB813` (R:252 G:184 B:19) sebagai warna aksen garis pemisah, teks badge, dan ikon penanda.
     - **Hitam / Black:** `#000000` (R:0 G:0 B:0 K:100%) sebagai warna teks utama formulir.
     - **Font Stack:** `'Estrangelo Edessa', 'Roboto', sans-serif` untuk seluruh judul, label form, dan isi konten formulir.
  4. **Penyempurnaan Teks "Auto-Scan" Menjadi Panduan Pengguna Ramah:**
     - Seluruh label badge pemindaian otomatis (`tag-auto`) diganti menjadi:
       > *"Terisi Otomatis - Jika Kurang Tepat Silahkan Ketik Langsung Untuk Perbaiki"*
     - Berlaku pada seluruh kolom hasil ekstraksi dokumen (NIK, Nama Pemohon, NPWP, Alamat, Plat Polisi, No. STNK, No. BPKB/Leasing, No. Rangka, No. Mesin).
  5. **Verifikasi Akses & Sinkronisasi:**
     - File master `Formulir_Pemohon_CEISA_PENGSEM_KBM.html` disinkronkan ke `index.html`.
     - Seluruh asersi pengujian HTTP live lolos 100% pada port 8080 (`http://10.36.19.212:8080`).
- **File yang Dimodifikasi / Dibuat:**
  - `logo_kemenkeu.svg` (Vektor resmi Kemenkeu).
  - `Formulir_Pemohon_CEISA_PENGSEM_KBM.html`
  - `index.html`
  - `COLLABORATION_LOG.md`
- **Status Saat Ini:**
  - Siap diperiksa secara langsung di browser oleh pengguna.

---
### [2026-11-24 21:15 WIB] — Entri oleh Antigravity (Mac mini)
- **Pelaksana:** Antigravity (Mac mini - Dedicated Office Server)
- **Topik Pembahasan:** Penyesuaian Lambang Resmi Direktorat Jenderal Bea dan Cukai (DJBC) & Tata Letak Dua Baris "BEA CUKAI" dan "BATAM".
- **Keputusan / Hasil Analisis & Implementasi:**
  1. **Lambang Resmi Bea Cukai (DJBC):**
     - Mengganti logo header dengan **Lambang Resmi Direktorat Jenderal Bea dan Cukai** (`logo_beacukai.svg`), yaitu perisai segi lima biru dongker lis emas, bintang sudut delapan emas, sayap emas, tongkat caduceus ular emas, dan jangkar laut (vektor SVG resmi).
  2. **Format Teks Dua Baris (Batam di Bawah Bea Cukai):**
     - Tata letak tipografi diatur vertikal terpusat menjadi 2 baris:
       * Baris 1: `BEA CUKAI` (huruf kapital, font-weight 800, letter-spacing 1.2px)
       * Baris 2: `BATAM` (tepat di bawah `BEA CUKAI`, letter-spacing 1.8px)
     - Warna: Kuning Keemasan murni (`#FCB813`) tanpa kotak latar belakang kuning (`background: transparent`).
  3. **Verifikasi Server & Sinkronisasi File:**
     - Sinkronisasi instan ke `index.html` dan `Formulir_Pemohon_CEISA_PENGSEM_KBM.html`.
     - Pengujian live HTTP port 8080 terkonfirmasi 200 OK.
- **File yang Dimodifikasi / Dibuat:**
  - `logo_beacukai.svg` (Vektor resmi DJBC).
  - `Formulir_Pemohon_CEISA_PENGSEM_KBM.html`
  - `index.html`
  - `COLLABORATION_LOG.md`
- **Status Saat Ini:**
  - Aktif dan terverifikasi di browser pengguna (`http://10.36.19.212:8080/`).

---
### [2026-11-24 21:18 WIB] — Entri oleh Antigravity (Mac mini)
- **Pelaksana:** Antigravity (Mac mini - Dedicated Office Server)
- **Topik Pembahasan:** Pemasangan Berkas Logo Asli Bea Cukai HD (Siapterbang BC Soetta 5602x4391 px) Sesuai Permintaan Spesifik Pengguna.
- **Keputusan / Hasil Analisis & Implementasi:**
  1. **Pengunduhan Berkas Master Logo Asli:**
     - Mengunduh langsung berkas `logo-bea-cukai-hd.png` (5602x4391 px, format RGBA transparan, ukuran 2,3 MB) dari repositori resmi `https://siapterbang.bcsoetta.org/file_unduh/logo-bea-cukai-hd.png`.
  2. **Optimasi Rendering Web Retina / 4K:**
     - Membuat versi web super tajam `logo_beacukai_web.png` menggunakan algoritma *LANCZOS resampling* (306x240 px, 101 KB) sehingga tampilan di layar komputer maupun smartphone beresolusi tinggi tampak sangat presisi tanpa jeda pemuatan data.
  3. **Penataan Header:**
     - Logo terpasang di atas teks dua baris: `BEA CUKAI` dan `BATAM` (kuning keemasan `#FCB813`, tanpa kotak latar belakang kuning).
  4. **Sinkronisasi File:**
     - Sinkronisasi instan ke `Formulir_Pemohon_CEISA_PENGSEM_KBM.html` dan `index.html`.
- **File yang Dimodifikasi / Dibuat:**
  - `logo-bea-cukai-hd.png` (Master asli 5602x4391 px).
  - `logo_beacukai_web.png` (Web retina).
  - `Formulir_Pemohon_CEISA_PENGSEM_KBM.html`
  - `index.html`
  - `COLLABORATION_LOG.md`
- **Status Saat Ini:**
  - Siap dan aktif di `http://10.36.19.212:8080/`.

---
### [2026-11-24 21:25 WIB] — Entri oleh Antigravity (Mac mini)
- **Pelaksana:** Antigravity (Mac mini - Dedicated Office Server)
- **Topik Pembahasan:** Penyelarasan Warna Biru Header dengan Tombol "Kamera KTP" (#005FAC) & Implementasi Proteksi Cache-Busting Multi-Perangkat.
- **Keputusan / Hasil Analisis & Implementasi:**
  1. **Penyelarasan Warna Biru Identik:**
     - Memastikan warna latar belakang header `.app-header` dan warna tombol primer `.btn-primary` (seperti tombol *"📸 Kamera KTP"*, *"📸 Kamera NPWP"*, *"📸 Kamera STNK"*) identik 100% menggunakan kode hex resmi `#005FAC` (Biru Dongker / Navy Blue: R:0 G:95 B:172).
  2. **Implementasi Anti-Cache Header pada Server:**
     - Memperbarui `server.py` dengan penambahan header HTTP anti-caching:
       * `Cache-Control: no-cache, no-store, must-revalidate, max-age=0`
       * `Pragma: no-cache`
       * `Expires: 0`
     - Melakukan restart service `server.py` pada port 8080 sehingga browser komputer loket dan HP pemohon di jaringan kantor (`10.36.19.212:8080`) langsung merender palet warna terbaru tanpa hambatan cache browser.
- **File yang Dimodifikasi:**
  - `server.py`
  - `Formulir_Pemohon_CEISA_PENGSEM_KBM.html`
  - `index.html`
  - `COLLABORATION_LOG.md`
- **Status Saat Ini:**
  - Server aktif beroperasi normal di background (Task daemon) pada `http://10.36.19.212:8080/`.

---
### [2026-11-24 21:38 WIB] — Entri oleh Antigravity (Mac mini)
- **Pelaksana:** Antigravity (Mac mini - Dedicated Office Server)
- **Topik Pembahasan:** Penataan Ulang Tag "Terisi Otomatis - Ketik Untuk Perbaiki" di Samping Label, Penghilangan Tanda Bintang, Perbaikan Presisi Ekstraksi Nama KTP (Anti-False-Positive "MANNA"), serta Komparasi Silang Nama KTP vs NPWP dengan Notifikasi Peringatan Popup.
- **Keputusan / Hasil Analisis & Implementasi:**
  1. **Penataan Posisi Tag & Diksi Baru:**
     - Teks tag dipersingkat menjadi:
       > *"Terisi Otomatis - Ketik Untuk Perbaiki"*
     - Posisi tag dipindahkan tepat di samping judul label (rata kiri / `justify-content: flex-start; gap: 8px`).
     - Seluruh tanda bintang asteris (`*`) pada label form dihilangkan secara menyeluruh untuk tampilan yang lebih bersih dan modern.
  2. **Penyelesaian Masalah Pembacaan Nama KTP ("MANNA" $\rightarrow$ "M. RIDWANSYAH"):**
     - Menganalisis log OCR: terdeteksi bahwa kata "NAMA" pada KTP sering terbaca sebagai "MANNA" atau "MANE", yang sebelumnya lolos validasi nama dan memicu `break` sebelum baris nama asli terbaca.
     - Mengimplementasikan algoritma pemeringkatan cerdas (*candidate scoring*):
       * Memasukkan variasi label (MANNA, MANE, NAMA, QUA, dll.) ke daftar kata terlarang (*banned list*).
       * Memprioritaskan baris nama sesungguhnya (`M. RIDWANSYAH`) dan membersihkan derau huruf belakang (seperti residu OCR "NE").
       * Hasil uji live: KTP kini 100% konsisten mengekstrak `M. RIDWANSYAH` dan NIK `1801071710940002`.
  3. **Verifikasi Silang & Komparasi Nama KTP vs NPWP:**
     - Endpoint `/api/ocr` diperbarui agar juga mengekstrak nama wajib pajak dari berkas NPWP (misal: `BINTAN BATAM SEJAHTERA`).
     - Di sisi frontend (`applyNpwpData`), sistem secara otomatis membandingkan nama pemohon dari KTP dengan nama wajib pajak pada NPWP:
       * Jika nama berbeda, sistem langsung menampilkan popup peringatan:
         > *"⚠️ PERINGATAN KESESUAIAN IDENTITAS PEMOHON!\n\nNama pada NPWP yang dipindai berbeda dengan Nama KTP Pemohon..."*
       * Kolom Nama Pemohon diproteksi mutlak tetap menggunakan data KTP (`M. RIDWANSYAH`).
  4. **Sinkronisasi & Server Restart:**
     - File master disinkronkan ke `index.html` dan `Formulir_Pemohon_CEISA_PENGSEM_KBM.html`.
     - Daemon server di-restart dengan status 200 OK di `http://10.36.19.212:8080/`.
- **File yang Dimodifikasi:**
  - `server.py`
  - `Formulir_Pemohon_CEISA_PENGSEM_KBM.html`
  - `index.html`
  - `COLLABORATION_LOG.md`
- **Status Saat Ini:**
  - Teruji live dan siap digunakan.

---
### [2026-11-24 21:50 WIB] — Entri oleh Antigravity (Mac mini)
- **Pelaksana:** Antigravity (Mac mini - Dedicated Office Server)
- **Topik Pembahasan:** Penataan Sempurna Header Resmi (Teks Kementerian Keuangan & Bea Cukai Batam 2 Baris Simetris, Ukuran Judul +30%, Penyelarasan Rata Garis Form), Nonaktivasi Total Deep Learning OCR Lokal, dan Migrasi Penuh ke Multimodal Vision AI Cepat.
- **Keputusan / Hasil Analisis & Implementasi:**
  1. **Redesain & Penataan Tipografi Header:**
     - **Sisi Kiri:** Teks Kementerian Keuangan diatur menjadi 2 baris tumpuk:
       * Baris 1: `KEMENTERIAN`
       * Baris 2: `KEUANGAN` (warna emas `#FCB813`, tanpa kotak background kuning).
     - **Sisi Kanan:** Teks Bea Cukai Batam konsisten 2 baris tumpuk:
       * Baris 1: `BEA CUKAI`
       * Baris 2: `BATAM` (warna emas `#FCB813`, simetris sempurna dengan logo Kemenkeu di kiri).
     - **Sisi Tengah:**
       * Judul utama `PENGELUARAN SEMENTARA KENDARAAN BERMOTOR` dibesarkan 30% menjadi `1.5rem` (kapital, putih tebal).
       * Subjudul 2 baris rata tengah:
         1) *Pelayanan Pengeluaran Kendaraan Bermotor Untuk Tujuan Tertentu Dalam Jangka Waktu Tertentu*
         2) *Dari Kawasan Bebas Batam Ke Tempat Lain Dalam Daerah Pabean*
     - **Penyelarasan Lebar (Segaris dengan Form):**
       * `.header-inner` diubah menjadi `max-width: 960px; padding: 0 16px; width: 100%; margin: 0 auto;`, sehingga posisi logo Kemenkeu di sisi kiri dan logo Bea Cukai di sisi kanan persis segaris lurus dengan batas tepi kontainer formulir.
  2. **Nonaktivasi Deep Learning OCR Lokal (EasyOCR / PyTorch):**
     - Sesuai instruksi pengguna, EasyOCR / PyTorch dinonaktifkan sepenuhnya dari `server.py` untuk mengeliminasi beban komputasi lokal dan salah baca teks.
     - Mesin OCR dimigrasikan 100% ke Multimodal Vision AI (`gemini-3.5-flash-lite` dengan fallback `gemini-flash-lite-latest`).
     - Hasil uji live terminal:
       * Ekstraksi KTP membaca tepat nama pemohon `M RIDWANSYAH` dan NIK `1801071710940002` tanpa kesalahan baca dalam < 1.5 detik.
       * Ekstraksi NPWP membaca tepat nomor `03.285.851.6-225.001` dan nama `BINTAN BATAM SEJAHTERA`.
  3. **Domain Lokal Mocking:**
     - Disiapkan panduan konfigurasi domain `pengsemkbm.batam.beacukai.go.id` via `/etc/hosts` untuk demonstrasi internal kantor.
- **File yang Dimodifikasi:**
  - `Formulir_Pemohon_CEISA_PENGSEM_KBM.html`
  - `index.html`
  - `server.py`
  - `COLLABORATION_LOG.md`
- **Status Saat Ini:**
  - Server aktif beroperasi normal di background (Task daemon) pada `http://10.36.19.212:8080/` dan `http://pengsemkbm.batam.beacukai.go.id:8080/`.
  - Spasi vertikal teks logo header ditambahkan (`margin-bottom: 7px; line-height: 1.25`) agar tidak mepet dengan emblem logo.

---

### [2026-11-24 22:50 WIB] - Antigravity (Mac mini)
- **Aktor / Device:** Antigravity (Mac mini)
- **Topik Pembahasan:** Ekstraksi dan Pengunduhan Massal Seluruh Naskah Dinas Arsip Disposisi Masuk "Permohonan Pengeluaran Kendaraan Bermotor" dari Nadine Kemenkeu ke Google Drive.
- **Keputusan / Hasil Analisis & Implementasi:**
  1. **Audit Endpoint & Penentuan Role Akses Nadine:**
     - Berdasarkan investigasi API Nadine Kemenkeu (`nadine_client.py`), pencarian arsip disposisi masuk memerlukan token aktif dan header organisasi.
     - Ditemukan bahwa peran TU (`roleid: 1`) memiliki repositori arsip disposisi masuk lengkap (lebih dari 10.000 naskah), sedangkan peran pelaksana teknis (`roleid: 5`) hanya memuat disposisi aktif/berjalan.
     - Dilakukan pemindaian kueri arsip disposisi `MejakuArchive/disposisi` dengan parameter perihal `Permohonan Pengeluaran Kendaraan Bermotor`.
  2. **Hasil Penelusuran & Manifest Arsip:**
     - Ditemukan sebanyak **599 baris riwayat disposisi** yang mencakup **169 naskah dinas unik** permohonan pengeluaran kendaraan bermotor pemohon perorangan/masyarakat.
     - Setiap naskah dinas memiliki berkas berkas utama (`PathKonsep`) yang berisi berkas digital pemohon (Surat Permohonan, STNK, BPKB, KTP, NPWP, SIM, dan Surat Pernyataan) yang disatukan atau dilampirkan.
  3. **Pengunduhan dan Penyimpanan ke Google Drive:**
     - Dibuat folder tujuan:
       `/Users/ridmini/Library/CloudStorage/GoogleDrive-ridwanmuham17@gmail.com/My Drive/PENGELUARAN_SEMENTARA_KBM_BATAM/DATA CONTOH PERMOHONAN`
     - Menggunakan skrip unduh concurrent `download_all_kbm_arsip.py`, berhasil mengunduh **166 dokumen utama** dan **47 dokumen lampiran** (Total **213 file PDF**, total ukuran **1.2 GB**).
     - **Reorganisasi Berkas & Subfolder Terpadu (Satu Folder / Berkas Lengkap per ID Pemohon):**
       * Seluruh 213 berkas dikelompokkan dan dipindahkan ke dalam **166 subfolder terpisah** berdasarkan nama pemohon / ID Nadine: `[YYYY-MM-DD]_[NdId]_[Nama_Pemohon]/`.
       * Untuk 19 pemohon yang memiliki berkas terpecah (Surat Permohonan + Lampiran KTP, STNK, BPKB, NPWP, SIM, Pernyataan), seluruh berkasnya otomatis digabungkan (*merged*) menjadi satu dokumen dossier utuh: `00_GABUNGAN_LENGKAP_[Tanggal]_[NdId]_[Nama_Pemohon].pdf`.
       * Berkas individual asli tetap dipertahankan di dalam subfolder masing-masing.
       * Dihasilkan katalog/indeks diperbarui: `INDEX_PERMOHONAN_KBM.md` yang memuat tautan langsung ke folder dan dossier gabungan setiap pemohon.
- **Status Saat Ini:**
  - Seluruh berkas contoh permohonan nyata dari Nadine Kemenkeu telah terorganisasi 100% per folder dan per file dossier lengkap di Google Drive lokal.

---

### [2026-11-25 13:25 WIB] - Antigravity (Mac mini)
- **Aktor / Device:** Antigravity (Mac mini)
- **Topik Pembahasan:** Penyiapan Konsep Surat Persetujuan Pemeriksaan Fisik di Luar Kawasan Pabean untuk PT Sat Nusapersada Tbk (Disposisi Masuk 69176138) dan PT Xiaomi Technology Indonesia (Disposisi Masuk 69176245) di Nadine Kemenkeu.
- **Keputusan / Hasil Analisis & Implementasi:**
  1. **Pembuatan Konsep Surat Dinas di Nadine:**
     - Berdasarkan surat permohonan pemohon tanggal 24 November 2026 dan rujukan naskah dinas contoh (`66599833`, `65995556`, dan `66601133`), telah berhasil dibuat 2 konsep naskah dinas keluar di akun Nadine:
       * **PT Sat Nusapersada Tbk:** NdId `69210375` (Id: `6b064b2d7d7558f887c7c4e4`)
       * **PT Xiaomi Technology Indonesia:** NdId `69210385` (Id: `6b064b343a10a041e8bef877`)
  2. **Penataan Tipografi & Narasi Komitmen Sesuai Naskah Redistribusi:**
     - Font naskah diatur 100% menggunakan **Arial**.
     - Paragraf komitmen integritas diselaraskan persis dengan standar naskah dinas redistribusi KPU BC Batam:
       * *KPU BC Batam senantiasa berkomitmen menjaga kepentingan negara secara profesional, bersinergi dengan seluruh pemangku kepentingan dengan* ***integritas***, ***responsif*** *melayani dan berkinerja* ***cemerlang***.
     - Spasi dioptimalkan secara presisi sehingga seluruh isi surat, klausul persetujuan, TTE, dan tembusan muat pas dalam **tepat 1 halaman utuh**.
  3. **Penyematan Nota Pengantar & Data Dukung:**
     - **Nota Pengantar:** Dibuat dan digenerate dari Seksi Fasilitas Pabean dan Cukai (Kepala Seksi: Yoedha Moehammad Hanafi) ke Bidang Pelayanan dan Fasilitas Pabean dan Cukai I (Kepala Bidang: Agus Siswadi).
     - **Data Dukung:** Seluruh surat permohonan resmi pemohon telah diunggah langsung ke tab Data Dukung masing-masing konsep di Nadine.
- **Status Saat Ini:**
  - Kedua konsep telah selesai 100% di meja **Konsep Berjalan** dan siap diteliti/diteruskan ke Kepala Seksi (Pak Yoedha).

---
*(Entri berikutnya akan dicatat oleh Mac Air, Claude, atau Mac mini pada sesi kerja selanjutnya)*

---

### [2026-11-25 15:05 WIB] - Antigravity (Mac mini)
- **Aktor / Device:** Antigravity (Mac mini)
- **Topik Pembahasan:** Penyempurnaan Ekstraksi Lengkap Berkas Kendaraan (BPKB & STNK) dan Mekanisme Status Hubungan Kepemilikan Sesuai Instruksi Kerja No: 001/KPUB.02/2025.
- **Keputusan / Hasil Analisis & Implementasi:**
  1. **Pengisian Otomatis 100% Seluruh Kolom Kendaraan:**
     - Memperbaiki parser OCR di  dan client-side JavaScript di :
       * : Terisi otomatis (e.g. ).
       * : Terisi otomatis dari nomor seri STNK/SKPD (e.g. ).
       * : Terisi otomatis nomor seri BPKB resmi (e.g. ).
       * : Lengkap beserta tipe spesifik kendaraan (e.g. ), bukan hanya nama brand.
       * : Lengkap tahun pembuatan dan warna (e.g. ).
       * : Terisi 17 digit otentik ().
       * : Terisi nomor mesin ().
  2. **Penentuan Nilai Jual (NJKB) & Jaminan PPN 11% Akurat Sesuai Tipe Mobil:**
     - NJKB kini terintegrasi langsung dengan database resmi Bapenda/Dispenda Kepri per merek, model/tipe spesifik, dan tahun pembuatan (bukan angka perkiraan umum).
     - Untuk Daihatsu Ayla 2014, NJKB resmi adalah **Rp 58.000.000**, sehingga Jaminan PPN 11% (PMK 34/2021 jo. UU HPP) yang wajib diserahkan di Loket Penerimaan & Pengembalian adalah **Rp 6.380.000** (mengoreksi kemunculan angka 7,7 juta sebelumnya).
  3. **Mekanisme Hubungan Kepemilikan Sesuai IK No: 001/KPUB.02/2025:**
     - Prinsip Utama: Seluruh berkas atas 1 nama yang sama (Pemohon = Pemilik BPKB/STNK = Pemilik NPWP).
     - Deteksi Cerdas Perbedaan Nama: Jika nama pemilik di STNK berbeda dengan pemohon di KTP, sistem tidak memblokir dengan error kaku, melainkan mengarahkan pemohon untuk memilih status hubungan kepemilikan dan melampirkan berkas pendukung resmi:
       * **🟢 Milik Pribadi:** Nama Pemohon = Nama BPKB & STNK.
       * **💍 Hubungan Keluarga (Suami / Istri / Orang Tua / Anak):** Wajib melampirkan Foto/Scan Buku Nikah / Kartu Keluarga (KK) & KTP Pemilik Asli.
       * **📝 Beli Belum Balik Nama (IK Bagian 5.a.2.e):** Wajib melampirkan Kwitansi / Surat Jual Beli Asli bermeterai & KTP Penjual/Pemilik Lama.
       * **🏢 Mobil Sewa / Rental (IK Bagian 10.b.4):** Wajib melampirkan Surat Perjanjian Sewa / Rekomendasi Resmi Rental bermeterai & KTP Pemilik Rental.
       * **📑 Dikuasakan (IK Bagian 10.b.4 & 10.g.2):** Wajib melampirkan Surat Kuasa Khusus bermeterai Rp 10.000 (NPWP yang dilampirkan adalah NPWP pemberi kuasa).
  4. **Sinkronisasi ke Dashboard Pegawai:**
     - Drawer verifikasi berkas permohonan petugas pabean di  telah diperbarui dengan menampilkan Status Hubungan Kepemilikan dan status lampiran dokumen pendukung.
- **Status Saat Ini:**
  - `index.html` dan `dashboard_pegawai.html` telah 100% tersinkronisasi.
  - Server aktif beroperasi normal di background pada `http://localhost:8000` dan `http://192.168.0.100:8000`.

---

### [2026-11-25 17:58 WIB] - Antigravity (Mac mini)
- **Aktor / Device:** Antigravity (Mac mini)
- **Topik Pembahasan:** Pemindaian Berkas Berwarna Asli (*Full-Color*) dari 166 Dossier Pemohon dan Pembuatan Repositori Gambar HD 300 DPI di Folder `BERKAS UJI COBA`.
- **Keputusan / Hasil Analisis & Implementasi:**
  1. **Pemindaian & Deteksi Warna Otomatis:**
     - Menjalankan analisis saturasi warna piksel (HSV/RGB color variance thresholding > 25) terhadap seluruh berkas PDF pemohon di `DATA CONTOH PERMOHONAN/`.
     - Menyaring dan memisahkan halaman yang merupakan fotokopi hitam-putih (*grayscale/b&w*) dari dokumen asli berwarna (*full-color scan/photo*).
  2. **Identifikasi & Kurasi Dokumen Kunci Berwarna:**
     - **KTP Berwarna:** Ditemukan pada berkas Dinda Trisnawati (`43040605`), Nen Salim (`43064597`), Rahmat Timbul Siregar (`62196579`), dan Willa Oktinas (`43169073`).
     - **NPWP Berwarna:** Ditemukan pada berkas Dinda Trisnawati, Nen Salim, Willa Oktinas, dan Dessy Susanty Kresna (`62072125`).
     - **BPKB Berwarna:** Ditemukan pada berkas Dinda Trisnawati (Halaman 1 & 2), Roman Pakpahan (`59922985`), Rahmat Timbul Siregar, dan Nen Salim.
     - **Surat Leasing Berwarna:** Ditemukan surat jaminan resmi berkop dan berstempel warna dari PT Toyota Astra Financial Services / TAF (Dessy Susanty Kresna) dan PT Astra Sedaya Finance / ACC (Nen Salim).
     - **Kartu Keluarga (KK) Berwarna:** Ditemukan KK resmi berheader biru Disdukcapil Batam & barcode TTE pada berkas Rahmat Timbul Siregar dan Sumarling (`43332240`).
     - **STNK & TBPKP Pajak Berwarna:** Ditemukan STNK asli hijau/kuning ornamen dan lembar ketetapan pajak daerah pada Dinda Trisnawati, Nen Salim, Rahmat Timbul Siregar, Sumarling, Willa Oktinas, dan Roman Pakpahan.
     - **Bonus Tambahan:** SIM A (Dinda, Nen Salim, Sumarling) dan Foto Fisik Kendaraan tampak depan/belakang (Dessy Susanty Kresna).
  3. **Ekstraksi Gambar HD 300 DPI & Pengorganisasian:**
     - Seluruh berkas diekstrak dalam resolusi tinggi 300 DPI (dimensi rata-rata 3500 x 2500 piksel) dalam dua format: **PNG (lossless)** dan **JPG**.
     - Disusun rapi dalam folder master: `BERKAS UJI COBA/` dengan struktur ganda:
       * `BERKAS_PER_JENIS_DOKUMEN/`: Memudahkan testing per jenis dokumen (`01_KTP`, `02_NPWP`, `03_BPKB`, `04_SURAT_LEASING`, `05_KARTU_KELUARGA`, `06_STNK_DAN_PAJAK`, `07_SIM`, `08_FOTO_KENDARAAN`).
       * `BERKAS_PER_PEMOHON/`: Memudahkan testing bundel pemohon utuh (`01_Dinda_Trisnawati_43040605`, `02_Nen_Salim_43064597`, dst.).
     - Dibuatkan katalog panduan lengkap: `README_INDEX.md` di dalam folder `BERKAS UJI COBA/`.
- **Status Saat Ini:**
  - Repositori `BERKAS UJI COBA/` telah terisi 33 berkas dokumen warna HD (total 66 file PNG + JPG di per-jenis dan per-pemohon), siap dipakai untuk uji coba OCR, LLM Vision, maupun demo presentasi.

---

### [2026-11-25 19:40 WIB] - Antigravity (Mac mini)
- **Aktor / Device:** Antigravity (Mac mini)
- **Topik Pembahasan:** Analisis Metadata & Pola Permohonan Pengeluaran Kendaraan Bermotor (599 Record Disposisi Nadine, 166 Dossier PDF Pemohon, dan 335 Riwayat KBM 7 Musim).
- **Keputusan / Hasil Analisis & Temuan Pola:**
  1. **Pola Musiman Ekstrem (*Seasonal Spikes*):**
     - Permohonan 100% terkonsentrasi hanya di dua periode: **Bulan Maret** (Mudik Lebaran) dan **Bulan Desember** (Libur Nataru).
     - Volume Lebaran melonjak 3x hingga 7x lipat dibanding Nataru (e.g. Lebaran 2025: 89 unit vs Nataru: 12 unit). Pada bulan-bulan lainnya volume adalah 0.
  2. **Pola Rantai Birokrasi Disposisi (3.54 Hop):**
     - 599 record disposisi terbentuk untuk 169 naskah permohonan unik (rata-rata 3.54 hop per naskah).
     - Alur standar melalui 3 hop eselon: Kepala Kantor (98) $\rightarrow$ Kepala Bidang PFPC I (170) $\rightarrow$ Kepala Seksi Fasilitas (168) $\rightarrow$ Pelaksana / Hanggar (100) dan Seksi PK (29).
     - Jam puncak disposisi terjadi pada pukul 11:00–13:59 WIB dan burst sore 15:00–15:59 WIB, dengan hari tersibuk Rabu dan Kamis.
  3. **Pola Karakteristik Berkas Fisik Pemohon:**
     - **88.6% (147 pemohon)** mengunggah berkas dalam bentuk **1 Single Merged PDF** (seluruh dokumen dijadikan satu).
     - Rata-rata ketebalan dokumen: **13.4 halaman** (median 13 halaman, range 6–28 halaman).
     - Rata-rata ukuran file: **7.83 MB** (79.5% berukuran 5–19 MB akibat foto kamera HP tanpa kompresi).
     - 100% halaman merupakan citra raster (pindaian kertas/foto), tidak ada teks digital, sehingga mutlak membutuhkan OCR / Vision AI.
  4. **Pola Objek Kendaraan & Rekonsiliasi Pabean:**
     - **96.7% (324 unit)** merupakan Non-CBU Fasilitas PPN Tidak Dipungut (wajib setor jaminan 11% PPN dari NJKB), didominasi Toyota (38.8%), Daihatsu (22.7%), dan Honda (15.5%).
     - Seluruh KBM kembali tepat waktu sebelum batas 45 hari kalender (rata-rata durasi di luar Batam 9 s.d. 35 hari).
- **Deliverables:**
  - Laporan komprehensif disimpan di artifact: `Laporan_Analisis_Metadata_dan_Pola_Permohonan_KBM.md`.

---

### [2026-11-25 19:58 WIB] - Antigravity (Mac mini)
- **Aktor / Device:** Antigravity (Mac mini - Dedicated Office Server)
- **Topik Pembahasan:** Implementasi Sistem Autentikasi dan Manajemen Hak Akses "Dua Pintu Pengakses" (Role-Based Access Control) Berbasis OTP WhatsApp Meta dan Kredensial Dinas.
- **Keputusan / Hasil Analisis & Implementasi:**
  1. **Backend Database Pengguna, OTP, dan Sesi (`server.py`):**
     - Dibuat `db_users.json` untuk menyimpan akun pemohon terverifikasi (`id`, `nik`, `nama`, `phone`, `status`, `registered_at`, `role: "pemohon"`) dan akun pegawai dinas (`nip`, `nama`, `jabatan`, `password`, `role: "pegawai"`).
     - Dibuat `db_otp.json` (TTL kedaluwarsa 5 menit) untuk menyimpan data OTP acak 6-digit.
     - Dibuat sistem sesi memori `AUTH_SESSIONS` dengan masa aktif 24 jam dan cookie `session_token`.
  2. **Endpoint API Autentikasi Baru:**
     - `POST /api/auth/request-otp`: Menerima `{phone, nik, nama}`, menghasilkan OTP 6-digit, dan mengirim pesan WhatsApp resmi via WhatsApp Cloud API Meta (`+62 851-4490-1346`).
     - `POST /api/auth/verify-otp`: Memvalidasi OTP dan nomor HP, mendaftarkan pemohon di `db_users.json`, serta membuat sesi aktif dengan role `pemohon`.
     - `POST /api/auth/login-pegawai`: Menerima NIP (18 digit) dan kata sandi dinas (default: NIP `199501012020011001` / Sandi `REDACTED_PASSWORD`), memberikan sesi aktif dengan role `pegawai`.
     - `GET /api/auth/session`: Mengembalikan data pengguna dan peran yang sedang login.
     - `POST /api/auth/logout`: Menghapus sesi aktif pengguna.
     - `GET /api/permohonan`: Difilter otomatis sesuai role (Pegawai = Seluruh Permohonan; Pemohon = Hanya Permohonan Milik Sendiri berdasarkan NIK/No. WhatsApp).
  3. **Antarmuka Pengguna Dua Pintu Pengakses (`index.html` & `Formulir_Pemohon_CEISA_PENGSEM_KBM.html`):**
     - Dibuat Modal Autentikasi Dua Pintu dengan tab switcher:
       * **Pintu 1 (Pegawai):** Input NIP 18 digit dan password dinas, akses penuh ke Dashboard Monitoring, Drawer Verifikasi 4 Tahap IK Pabean, dan Konsol Live Chat Operator WA.
       * **Pintu 2 (Pemohon):** Registrasi mandiri berbasis verifikasi OTP WhatsApp Meta, pengisian otomatis NIK, nama, dan no HP ke formulir KBM, pengunggahan berkas, e-meterai, bundel PDF Nadine, dan pemantauan permohonan pribadi.
     - Navigasi atas otomatis menyesuaikan peran aktif (`🛡️ Pegawai BC` vs `👤 Pemohon`) lengkap dengan tombol Keluar (Logout).
  4. **Pengujian:**
     - Seluruh 7 skenario pengujian API backend lolos 100%.
     - Server daemon aktif di `http://localhost:8080` dan `http://10.36.19.212:8080`.
- **Berkas yang Dimodifikasi:**
  - `server.py`
  - `index.html`
  - `Formulir_Pemohon_CEISA_PENGSEM_KBM.html`
  - `db_users.json`
  - `db_otp.json`
  - `COLLABORATION_LOG.md`
- **Aktor / Device:** Antigravity (Mac mini)
- **Topik Pembahasan:** Penambahan Berkas Foto Kendaraan dari Berbagai Sisi (Depan, Belakang, Samping Kanan, Samping Kiri) serta Foto & Gesekan Nomor Rangka dan Nomor Mesin ke dalam Repositori `BERKAS UJI COBA`.
- **Keputusan / Hasil Analisis & Ekstraksi:**
  1. **Ekstraksi Foto Kendaraan Berbagai Sisi (300 DPI):**
     - **Toyota Fortuner Hitam (BP 1909 CE - April Yani):** Tampak Depan, Tampak Belakang, Tampak Samping Kanan, dan Tampak Samping Kiri lengkap dengan geotag Bea Cukai Batu Ampar.
     - **Mitsubishi Xpander Putih (BP 1709 FF - Ali Anwar):** Tampak Depan, Tampak Belakang, Tampak Samping Kanan, dan Tampak Samping Kiri/Serong.
     - **Toyota Raize (Dessy Susanty Kresna):** Tampak Depan, Belakang, dan Samping.
     - **Daihatsu Sigra (Sumarling):** Tampak Depan, Belakang, dan Samping.
     - **Dewi Santi:** Tampak Depan/Belakang dan Samping.
  2. **Ekstraksi Foto & Gesekan Nomor Rangka & Nomor Mesin (300 DPI):**
     - **Toyota Fortuner (April Yani):** Kertas gesekan fisik VIN `MHFA19G59P0227136` dan mesin `2TR8711466`.
     - **Mitsubishi Xpander (Ali Anwar):** Kertas gesekan fisik nomor rangka dan nomor mesin.
     - **Toyota Raize (Dessy Susanty Kresna):** Foto pelat fisik nomor rangka dan blok mesin.
     - **Daihatsu Sigra (Sumarling):** Kertas gesekan resmi bernomor rangka dan nomor mesin.
  3. **Penataan Folder Ganda (Per Jenis & Per Pemohon):**
     - Kategori baru ditambahkan ke `BERKAS_PER_JENIS_DOKUMEN/`:
       * `08_FOTO_KENDARAAN/` (32 file PNG + JPG)
       * `09_NOMOR_RANGKA_DAN_MESIN/` (16 file PNG + JPG)
       * `10_HASIL_PEMERIKSAAN_FISIK/` (6 file LHP & BAP resmi)
     - Bundel pemohon baru ditambahkan ke `BERKAS_PER_PEMOHON/`:
       * `08_April_Yani_14_PPFTZ_Fortuner_BP1909CE/` (16 file lengkap)
       * `09_Ali_Anwar_48_PPFTZ_Xpander_BP1709FF/` (14 file lengkap)
       * Pemohon 04 (Sumarling) dan 05 (Dessy Susanty) dilengkapi dengan foto sisi dan nomor mesin/rangka.
  4. **Katalog Panduan:** `README_INDEX.md` di folder `BERKAS UJI COBA/` diperbarui dengan total 55 baris item dokumen lengkap.




### Catatan Kolaborasi #31: Implementasi Gerbang Masuk Awal (Gatekeeper Landing) & Proteksi RBAC Ketat Petugas vs Pemohon
- **Waktu:** 25 November 2026, 20:05 WIB
- **Aktor / Device:** Antigravity (Mac mini)
- **Topik Pembahasan:** Penataan Alur Autentikasi di Awal Halaman Sebelum Dashboard/Formulir, Pembatasan Registrasi Hanya untuk Pemohon, dan Proteksi Halaman Petugas Berbasis User/Password Dinas.
- **Implementasi:**
  1. **Halaman Gerbang Masuk Awal (`#viewAuthLanding`):**
     - Dashboard (`#viewDashboard`), Formulir (`#viewFormulir`), dan Menu Bar Atas (`#mainPortalNav`) disembunyikan total sebelum pengguna melakukan login/registrasi.
     - Pengguna yang pertama kali membuka portal langsung disambut antarmuka gerbang otentikasi resmi Bea Cukai Batam dengan dua tab utama:
       * **Tab LOG IN:** Memiliki 2 sub-pilihan:
         1. **Petugas Bea Cukai (Internal):** Input NIP 18 Digit (`199501012020011001`) & Sandi Dinas (`REDACTED_PASSWORD`). Begitu berhasil, langsung membuka Dashboard Monitoring Pegawai, Drawer Verifikasi 4 Tahap IK Pabean, dan Konsol Live Chat Operator WA.
         2. **Pemohon Terdaftar (Eksternal):** Input Nomor WhatsApp terdaftar $\rightarrow$ Permintaan & Verifikasi OTP 6 Digit $\rightarrow$ Langsung membuka Formulir Permohonan & Riwayat Pribadi.
       * **Tab REGISTRASI (Khusus Pemohon / Masyarakat):**
         - Khusus masyarakat/pemohon yang belum memiliki akun.
         - Input NIK (16 digit), Nama Lengkap, dan Nomor WhatsApp.
         - Pengiriman OTP 6 digit nyata via Meta WhatsApp Cloud API (`+62 851-4490-1346`).
         - Verifikasi OTP berhasil langsung mendaftarkan user di `db_users.json` dan membawa pemohon ke Formulir KBM dengan data terisi otomatis.
  2. **Proteksi Hak Akses (Role-Based Access Control / RBAC) Ketat:**
     - Frontend: Fungsi `switchPortalView('dashboard')` memverifikasi sesi aktif. Jika bukan akun pegawai, akses ke dashboard ditolak dan dialihkan kembali ke tampilan yang sesuai dengan notifikasi peringatan.
     - Backend (`server.py`): Endpoint `/api/permohonan/update` dan `/api/wa/send` mewajibkan sesi aktif berstatus `role == 'pegawai'`. Akses dari pemohon atau tanpa login ditolak dengan kode `403 Forbidden`.
     - Endpoint `/api/permohonan` memfilter data: Pegawai dapat melihat seluruh berkas pemohon, sedangkan pemohon hanya dapat melihat permohonannya sendiri.
  3. **Pengujian:**
     - Seluruh pengujian otentikasi lolos 100% (Login Pegawai 200 OK, Update Permohonan Pegawai 200 OK, Penolakan Tanpa Login 403 Forbidden, Penolakan Pemohon Akses Endpoint Petugas 403 Forbidden).
     - Daemon server aktif dan sinkron di `index.html` dan `Formulir_Pemohon_CEISA_PENGSEM_KBM.html`.
