# DOKUMEN BRIEFING & KONSOLIDASI TRANSFORMATIF
## Pelayanan Pengeluaran Sementara Kendaraan Bermotor (KBM) Dari Kawasan Bebas Batam ke TLDDP
**KPU Bea dan Cukai Tipe B Batam — Bidang Pelayanan dan Fasilitas Pabean dan Cukai I**

---

### 1. Dasar Hukum & Acuan Regulasi Utama
1. **Instruksi Kerja IK 001/KPUB.02/2025** (tertanggal 14 Maret 2025): *Pelayanan Pengeluaran Kendaraan Bermotor Untuk Tujuan Tertentu Dalam Jangka Waktu Tertentu Dari Kawasan Bebas Batam Ke Tempat Lain Dalam Daerah Pabean*.
2. **PMK 34/PMK.04/2021** jo. **PMK 168/PMK.04/2022**: Pemasukan dan Pengeluaran Barang ke dan dari Kawasan Bebas Batam.
3. **PER-15/BC/2022** jo. **PER-20/BC/2022**: Petunjuk Pelaksanaan Tata Laksana Pabean di Kawasan Perdagangan Bebas dan Pelabuhan Bebas.

---

### 2. Ringkasan Diagnostik Masalah Eksisting (Audit Idul Fitri 2025)
1. **Fragmentasi 1.547 Berkas di Google Drive:**
   - 11 subfolder terpisah di Google Drive membuat petugas harus membuka 7–8 tab browser per pemohon.
   - Tidak ada validasi otomatis Non-CBU (eks-TLDDP vs CBU eks-LDP). Mobil CBU kerap lolos di awal lalu tertolak di pelabuhan.
   - Pemohon sering salah menghitung nilai jaminan PPN 11% dari NJKB.
2. **Anomali di Nadine Kemenkeu:**
   - Persetujuan diterbitkan sebagai Surat biasa (`S-302` s.d. `S-319`), KEP hanya diunggah sebagai lampiran PDF di luar register KEP resmi.
   - Field `DataDukung` pada payload Nadine berstatus `null` (kosong).
   - Terjadi pembatalan massal (KEP-02 s.d. KEP-17, S-423, S-460) karena pemohon membatalkan mudik paska KEP selesai diproses.
3. **Birokrasi 14 Langkah Disposisi Rekonsiliasi:**
   - Rekonsiliasi saat KBM kembali ke Batam memicu rantai 14 disposisi berantai antara Seksi Pelayanan, Seksi PK, Seksi Fasilitas, dan Bendahara.
   - Waktu pengembalian jaminan molor hingga 7–14 hari kerja (melampaui SLA 6 Hari Kerja pada IK).

---

### 3. Solusi Terpadu & Arsitektur Sistem (To-Be)
1. **Portal Mandiri "SiKBM Batam" (Web & Mobile):**
   - Single-entry form: Cukup input Plat Batam (BP) & nomor rangka.
   - Pengecekan Non-CBU otomatis via API Samsat Bapenda Kepri.
   - Kalkulator jaminan PPN otomatis: $11\% \times \text{NJKB}$ resmi.
   - 1-Click Dropzone berkas & auto-generate Surat Permohonan & Pernyataan ber-meterai QR.
2. **Middleware & Bot Nadine Automation:**
   - Single-Dossier Compiler menggabungkan berkas menjadi 1 file PDF terstruktur.
   - Payload Bot Nadine menerbitkan draft Surat Persetujuan (S), KEP resmi bernomor, Nota Pengantar otomatis, dan menyematkan Single Dossier ke field `DataDukung`.
   - Konfirmasi jadwal kapal Roro sebelum KEP final untuk mencegah pembatalan sia-sia.
3. **Mobile Scanner di Pelabuhan (Telaga Punggur / Batu Ampar):**
   - Tablet lapangan memindai QR SKEP / Boarding Pass pemohon.
   - Pencocokan nomor rangka/mesin 100% instan; foto gesekan langsung terunggah ke CEISA 4.0.
   - Penerbitan SPPB PPFTZ-01 selesai < 1 jam (SLA IK: 8 Jam).
4. **Auto-Reconciliation Engine (Digital Handshake):**
   - Menggantikan 14 disposisi manual menjadi rekonsiliasi data otomatis (PPFTZ-01 match PPFTZ-03).
   - Pengembalian jaminan tunai/pelepasan garansi bank selesai maksimal **2 hari kerja**.
5. **Early Warning System (EWS) 45 Hari Kalender (IK Poin 10.c):**
   - Radar Kanban: Hijau (>15 hari), Kuning (H-7), Merah (H-3), Hitam (Jatuh tempo).
   - Notifikasi pengingat via WhatsApp Gateway H-10, H-7, dan H-3.
   - Eksekusi otomatis draf klaim pencairan jaminan ke Bank / KPPN Batam saat H+1 jatuh tempo.

---

### 4. Daftar Berkas Deliverable di Folder Ini
1. `Solusi_Komprehensif_Pengeluaran_Sementara_KBM_Batam.pptx` (Presentasi Widescreen 16:9, 12 slide).
2. `Solusi_Komprehensif_Pengeluaran_Sementara_KBM_Batam.pdf` (Versi Landscape untuk layar laptop/paparan).
3. `Solusi_Komprehensif_Pengeluaran_Sementara_KBM_Batam_Mobile_Portrait.pdf` (Versi Portrait tegak untuk dibaca di HP).
4. `IK_001_KPUB02_2025_Pengeluaran_Sementara_KBM.pdf` (Salinan dokumen resmi Instruksi Kerja).
5. `BRIEFING_SESI_BARU_PENGSEM_KBM.md` (Dokumen ini).
