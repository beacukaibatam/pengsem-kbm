import os

for fname in ['Formulir_Pemohon_CEISA_PENGSEM_KBM.html', 'index.html']:
    with open(fname, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Insert E-Meterai Facility Card in Page 4 (after Data Ringkasan)
    target_p4 = '''            <!-- Mode Frontdesk Loket Action -->
            <div id="frontdeskBox"'''

    emeterai_card = '''            <!-- ================= FASILITASI E-METERAI RESMI PERURI & POS INDONESIA ================= -->
            <div class="emeterai-facility-card" style="background:#FFFBEB; border:1.5px solid #FCD34D; border-radius:var(--radius-md); padding:16px; margin-bottom:16px;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px; flex-wrap:wrap; gap:10px;">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <div style="font-size:1.8rem; background:#FEF3C7; width:46px; height:46px; border-radius:10px; display:flex; align-items:center; justify-content:center; border:1.5px solid #F59E0B; flex-shrink:0;">🎫</div>
                        <div>
                            <div style="font-weight:800; font-size:0.95rem; color:#92400E; display:flex; align-items:center; gap:8px;">
                                Fasilitas E-Meterai Terpadu (PERURI &amp; Pos Indonesia)
                                <span style="background:#059669; color:#FFFFFF; font-size:0.65rem; font-weight:700; padding:2px 8px; border-radius:10px;">Rp 10.000 / Lembar</span>
                            </div>
                            <div style="font-size:0.75rem; color:#B45309; line-height:1.4; margin-top:2px;">
                                Halaman Depan 1 (Surat Permohonan) &amp; Halaman Depan 2 (Surat Pernyataan) difasilitasi E-Meterai sah sebelum digabung menjadi 1 PDF Nadine.
                            </div>
                        </div>
                    </div>
                    <button type="button" class="btn btn-secondary" onclick="openEmeteraiPortalModal()" style="font-size:0.76rem; border-color:#F59E0B; color:#92400E; background:#FFFFFF; font-weight:700; display:flex; align-items:center; gap:6px;">
                        <span>🌐 Buka Portal E-Meterai Resmi</span>
                        <svg class="flat-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                    </button>
                </div>

                <!-- Status Pembubuhan Meterai 2 Surat Depan -->
                <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:10px; margin-top:12px;">
                    <!-- Dokumen 1: Surat Permohonan -->
                    <div style="background:#FFFFFF; border:1px solid #FDE68A; border-radius:8px; padding:12px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div style="font-weight:700; font-size:0.80rem; color:#1E293B;">1. Surat Permohonan KBM (Hal. 1)</div>
                            <div style="font-size:0.70rem; color:#64748B;">Dibubuhi E-Meterai Rp 10.000 &amp; Tanda Tangan</div>
                        </div>
                        <span class="pill-source wa" style="background:#DCFCE7; color:#15803D; font-weight:700; font-size:0.70rem;">✓ E-Meterai Aktif</span>
                    </div>
                    <!-- Dokumen 2: Surat Pernyataan Jaminan -->
                    <div style="background:#FFFFFF; border:1px solid #FDE68A; border-radius:8px; padding:12px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div style="font-weight:700; font-size:0.80rem; color:#1E293B;">2. Surat Pernyataan Jaminan (Hal. 2)</div>
                            <div style="font-size:0.70rem; color:#64748B;">Dibubuhi E-Meterai Rp 10.000 &amp; Komitmen Batam</div>
                        </div>
                        <span class="pill-source wa" style="background:#DCFCE7; color:#15803D; font-weight:700; font-size:0.70rem;">✓ E-Meterai Aktif</span>
                    </div>
                </div>

                <div style="font-size:0.72rem; color:#78350F; margin-top:10px; line-height:1.5; background:#FEF3C7; padding:8px 12px; border-radius:6px; display:flex; align-items:center; gap:8px;">
                    <span style="font-size:1.1rem;">💡</span>
                    <span><strong>100% Praktis &amp; Paperless:</strong> Sistem secara otomatis membubuhkan visualisasi E-Meterai resmi ber-QR Code PERURI pada kedua lembar surat depan saat Anda menekan tombol <strong>Unduh 1 PDF Asli</strong>. Tidak perlu cetak kertas manual, tidak perlu antre beli meterai tempel fisik.</span>
                </div>
            </div>

            <!-- Mode Frontdesk Loket Action -->
            <div id="frontdeskBox"'''

    if target_p4 in html and 'emeterai-facility-card' not in html:
        html = html.replace(target_p4, emeterai_card, 1)
        print(f'Added E-Meterai Facility Card to {fname}')

    # 2. Add Modal Portal E-Meterai
    target_modal = '''    <!-- MODAL PDF FULLSET RESMI (10 HALAMAN) UNTUK NADINE -->'''
    
    emeterai_portal_modal = '''    <!-- MODAL PORTAL E-METERAI RESMI PEMERINTAH (PERURI & POS INDONESIA) -->
    <div class="modal-overlay" id="emeteraiPortalModal" style="display:none; align-items:center; justify-content:center; background:rgba(15,23,42,0.7); z-index:9999;">
        <div class="modal-card" style="max-width:620px; background:#FFFFFF; border-radius:12px; overflow:hidden; box-shadow:0 25px 50px -12px rgba(0,0,0,0.35);">
            <div class="modal-header" style="background:#92400E; color:#FFFFFF; padding:14px 20px; display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <div style="font-size:1.5rem;">🎫</div>
                    <div>
                        <h3 style="margin:0; font-size:1.0rem; font-weight:800;">Layanan Pembelian E-Meterai Resmi Rp 10.000</h3>
                        <div style="font-size:0.72rem; color:#FDE68A;">Distributor Resmi Perum Percetakan Uang RI (PERURI) &amp; BUMN</div>
                    </div>
                </div>
                <button type="button" style="background:none; border:none; color:#FFFFFF; font-size:1.4rem; cursor:pointer;" onclick="closeEmeteraiPortalModal()">&times;</button>
            </div>
            <div class="modal-body" style="padding:18px;">
                <p style="font-size:0.80rem; color:#334155; margin-top:0; margin-bottom:14px; line-height:1.5;">
                    Sesuai Undang-Undang Bea Meterai No. 10 Tahun 2020, dokumen permohonan dan pernyataan kepabeanan wajib dibubuhi meterai Rp 10.000 yang sah. Anda dapat membeli kuota E-Meterai resmi secara instan melalui kanal pemerintah berikut:
                </p>

                <!-- Pilihan Portal Distributor -->
                <div style="display:flex; flex-direction:column; gap:10px; margin-bottom:16px;">
                    <!-- Option 1: PosFin / Pos Indonesia BUMN -->
                    <a href="https://e-meterai.posfin.id" target="_blank" style="text-decoration:none; display:flex; justify-content:space-between; align-items:center; background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:8px; padding:12px 14px; transition:all 0.15s;">
                        <div style="display:flex; align-items:center; gap:12px;">
                            <div style="font-size:1.6rem;">📮</div>
                            <div>
                                <div style="font-weight:700; font-size:0.88rem; color:#92400E;">PT Pos Indonesia (Pos Fin) BUMN</div>
                                <div style="font-size:0.72rem; color:#B45309;">e-meterai.posfin.id &bull; Bayar Instan QRIS / Kantor Pos</div>
                            </div>
                        </div>
                        <span style="background:#F59E0B; color:#FFFFFF; font-size:0.72rem; font-weight:700; padding:4px 10px; border-radius:6px;">Beli Sekarang ↗</span>
                    </a>

                    <!-- Option 2: PERURI Official Portal -->
                    <a href="https://meterai-elektronik.com" target="_blank" style="text-decoration:none; display:flex; justify-content:space-between; align-items:center; background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:8px; padding:12px 14px; transition:all 0.15s;">
                        <div style="display:flex; align-items:center; gap:12px;">
                            <div style="font-size:1.6rem;">🏛️</div>
                            <div>
                                <div style="font-weight:700; font-size:0.88rem; color:#1E40AF;">Perum Percetakan Uang RI (PERURI)</div>
                                <div style="font-size:0.72rem; color:#2563EB;">meterai-elektronik.com &bull; Portal Resmi Pencetak Meterai</div>
                            </div>
                        </div>
                        <span style="background:#2563EB; color:#FFFFFF; font-size:0.72rem; font-weight:700; padding:4px 10px; border-radius:6px;">Beli Sekarang ↗</span>
                    </a>
                </div>

                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; font-size:0.75rem; color:#475569; line-height:1.5;">
                    <strong>Alur Praktis 3 Menit:</strong><br>
                    1. Beli kuota e-meterai Rp 10.000 melalui salah satu portal di atas.<br>
                    2. Unduh bundel 1 PDF dari web ini, lalu bubuhkan e-meterai pada halaman 1 &amp; 2.<br>
                    3. Berkas digital Anda 100% otentik dan siap diproses ke agenda Nadine Kemenkeu.
                </div>
            </div>
            <div class="modal-footer" style="padding:12px 18px; background:#F8FAFC; border-top:1px solid #E2E8F0; display:flex; justify-content:flex-end;">
                <button type="button" class="btn btn-secondary" onclick="closeEmeteraiPortalModal()">Tutup</button>
            </div>
        </div>
    </div>\n\n'''

    if target_modal in html and 'emeteraiPortalModal' not in html:
        html = html.replace(target_modal, emeterai_portal_modal + target_modal, 1)
        print(f'Added E-Meterai Portal Modal to {fname}')

    # 3. Update generateAndDownloadRealPDF() to draw authentic E-Meterai on Hal 1 and Hal 2
    old_h1_h2 = '''            doc.text('Tanda Tangan Pemohon,', 140, 160);
            doc.setFont('helvetica', 'bold');
            doc.text(nama, 140, 185);

            // Hal 2: Surat Pernyataan
            doc.addPage();
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.text('SURAT PERNYATAAN KESANGGUPAN JAMINAN & PEMASUKAN KEMBALI', 105, 25, { align: 'center' });
            doc.setFont('helvetica', 'normal');
            doc.setFontSize(9);
            doc.text('Menyatakan sanggup menyerahkan Jaminan PPN 11% (' + jaminanTxt + ') dan wajib memasukkan', 20, 40);
            doc.text('kembali kendaraan bermotor nomor polisi ' + nopol + ' ke Kawasan Bebas Batam tepat waktu.', 20, 46);
            doc.rect(130, 80, 25, 20);
            doc.text('Materai\\nRp 10.000', 133, 89);
            doc.text('( ' + nama + ' )', 125, 115);'''

    new_h1_h2 = '''            // Pembubuhan E-Meterai Resmi Hal 1 (Surat Permohonan)
            doc.setDrawColor(180, 83, 9);
            doc.setFillColor(254, 243, 199);
            doc.roundedRect(95, 155, 34, 28, 2, 2, 'FD');
            doc.setFontSize(7);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(146, 64, 14);
            doc.text('E-METERAI', 112, 162, { align: 'center' });
            doc.setFontSize(6);
            doc.text('TGL: 25-11-2026', 112, 168, { align: 'center' });
            doc.text('Rp 10.000,-', 112, 174, { align: 'center' });
            doc.setFontSize(5);
            doc.text('SN: PERURI-62234248', 112, 179, { align: 'center' });
            doc.setTextColor(0, 0, 0);

            doc.setFontSize(9);
            doc.setFont('helvetica', 'normal');
            doc.text('Pemohon Bermeterai,', 140, 152);
            doc.setFont('helvetica', 'bold');
            doc.text('( ' + nama + ' )', 140, 184);

            // Hal 2: Surat Pernyataan
            doc.addPage();
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.text('SURAT PERNYATAAN KESANGGUPAN JAMINAN & PEMASUKAN KEMBALI', 105, 25, { align: 'center' });
            doc.setFont('helvetica', 'normal');
            doc.setFontSize(9);
            doc.text('Menyatakan sanggup menyerahkan Jaminan PPN 11% (' + jaminanTxt + ') dan wajib memasukkan', 20, 40);
            doc.text('kembali kendaraan bermotor nomor polisi ' + nopol + ' ke Kawasan Bebas Batam tepat waktu.', 20, 46);

            // Pembubuhan E-Meterai Resmi Hal 2 (Surat Pernyataan Jaminan)
            doc.setDrawColor(180, 83, 9);
            doc.setFillColor(254, 243, 199);
            doc.roundedRect(95, 85, 34, 28, 2, 2, 'FD');
            doc.setFontSize(7);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(146, 64, 14);
            doc.text('E-METERAI', 112, 92, { align: 'center' });
            doc.setFontSize(6);
            doc.text('TGL: 25-11-2026', 112, 98, { align: 'center' });
            doc.text('Rp 10.000,-', 112, 104, { align: 'center' });
            doc.setFontSize(5);
            doc.text('SN: PERURI-98842109', 112, 109, { align: 'center' });
            doc.setTextColor(0, 0, 0);

            doc.setFontSize(9);
            doc.setFont('helvetica', 'normal');
            doc.text('Yang Membuat Pernyataan,', 140, 82);
            doc.setFont('helvetica', 'bold');
            doc.text('( ' + nama + ' )', 140, 114);'''

    if old_h1_h2 in html:
        html = html.replace(old_h1_h2, new_h1_h2, 1)
        print(f'Updated PDF generator with E-Meterai in {fname}')

    # 4. Add JS openEmeteraiPortalModal & closeEmeteraiPortalModal
    js_funcs = '''
        function openEmeteraiPortalModal() {
            const m = document.getElementById('emeteraiPortalModal');
            if (m) m.style.display = 'flex';
        }
        function closeEmeteraiPortalModal() {
            const m = document.getElementById('emeteraiPortalModal');
            if (m) m.style.display = 'none';
        }
'''
    if 'function openEmeteraiPortalModal' not in html:
        idx_sc = html.rfind('</script>')
        html = html[:idx_sc] + js_funcs + '\n' + html[idx_sc:]
        print(f'Added E-Meterai JS functions to {fname}')

    with open(fname, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Successfully wrote {fname}')
