#!/usr/bin/env python3
"""
Menerapkan:
1. Full-width Rigid Enterprise Layout (menghilangkan seluruh white space kosong di kanan dan kiri).
2. Mengganti semua emoji lingkaran berwarna (🟡, 🟠, 🟣, 🟢, 🔴, 🔵) menjadi 100% Flat Solid Color Dots (tanpa gradasi, tanpa 3D).
"""

with open('Formulir_Pemohon_CEISA_PENGSEM_KBM.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. ADD CSS FOR FLAT SOLID DOTS & RIGID FULL-WIDTH LAYOUT
flat_dots_and_rigid_css = '''
        /* ================= RIGID FULL-WIDTH EDGE-TO-EDGE LAYOUT ================= */
        html, body {
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow-x: hidden !important;
        }

        .main-container {
            max-width: 100% !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 16px 24px !important;
            box-sizing: border-box !important;
        }

        #viewDashboard {
            max-width: 100% !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 16px 24px !important;
            box-sizing: border-box !important;
        }

        .portal-nav-bar {
            width: 100% !important;
            max-width: 100% !important;
            padding: 0 !important;
            box-sizing: border-box !important;
        }

        .portal-nav-container {
            max-width: 100% !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 24px !important;
            box-sizing: border-box !important;
        }

        .app-header {
            width: 100% !important;
            max-width: 100% !important;
            padding: 12px 24px !important;
            box-sizing: border-box !important;
        }

        .header-container {
            max-width: 100% !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            box-sizing: border-box !important;
        }

        .wizard-sticky-bar {
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }

        .wizard-sticky-inner {
            max-width: 100% !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 24px !important;
            box-sizing: border-box !important;
        }

        .dash-kpi-grid {
            width: 100% !important;
            grid-template-columns: repeat(5, 1fr) !important;
            gap: 14px !important;
        }

        @media (max-width: 1200px) {
            .dash-kpi-grid {
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)) !important;
            }
        }

        .dash-toolbar-card {
            width: 100% !important;
            box-sizing: border-box !important;
        }

        .dash-table-card {
            width: 100% !important;
            box-sizing: border-box !important;
        }

        /* ================= 100% FLAT SOLID DOTS (NO GRADIENTS) ================= */
        .flat-dot {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 6px;
            flex-shrink: 0;
            vertical-align: 0px;
        }
        .dot-yellow { background-color: #D97706; }
        .dot-blue { background-color: #1E40AF; }
        .dot-orange { background-color: #EA580C; }
        .dot-purple { background-color: #7C3AED; }
        .dot-green { background-color: #16A34A; }
        .dot-red { background-color: #DC2626; }
'''

# Insert CSS before </style>
pos_style = text.find('</style>')
text = text[:pos_style] + flat_dots_and_rigid_css + '\n' + text[pos_style:]

# 2. REPLACE EMOJI CIRCLES IN FILTER TABS WITH FLAT SOLID DOTS
text = text.replace(
    '''<button class="dash-tab-btn" onclick="filterByStatus('MENUNGGU_VERIFIKASI_DOKUMEN', this)">🟡 Verifikasi Berkas</button>
                <button class="dash-tab-btn" onclick="filterByStatus('MENUNGGU_CEK_FISIK', this)">🟠 Cek Fisik Lapangan</button>
                <button class="dash-tab-btn" onclick="filterByStatus('PENETAPAN_JAMINAN_PPN', this)">🟣 Penetapan Jaminan</button>
                <button class="dash-tab-btn" onclick="filterByStatus('DISETUJUI', this)">🟢 Disetujui</button>''',
    '''<button class="dash-tab-btn" onclick="filterByStatus('MENUNGGU_VERIFIKASI_DOKUMEN', this)"><span class="flat-dot dot-yellow"></span>Verifikasi Berkas</button>
                <button class="dash-tab-btn" onclick="filterByStatus('MENUNGGU_CEK_FISIK', this)"><span class="flat-dot dot-orange"></span>Cek Fisik Lapangan</button>
                <button class="dash-tab-btn" onclick="filterByStatus('PENETAPAN_JAMINAN_PPN', this)"><span class="flat-dot dot-purple"></span>Penetapan Jaminan</button>
                <button class="dash-tab-btn" onclick="filterByStatus('DISETUJUI', this)"><span class="flat-dot dot-green"></span>Disetujui</button>'''
)

# 3. REPLACE EMOJI CIRCLES IN DRAWER SELECT OPTIONS WITH CLEAN FLAT TEXT
text = text.replace(
    '''<option value="MENUNGGU_VERIFIKASI_DOKUMEN">🟡 Menunggu Verifikasi Dokumen</option>
                        <option value="DOKUMEN_LENGKAP">🔵 Dokumen Lengkap</option>
                        <option value="MENUNGGU_CEK_FISIK">🟠 Menunggu Cek Fisik Lapangan</option>
                        <option value="PENETAPAN_JAMINAN_PPN">🟣 Penetapan Jaminan PPN 11%</option>
                        <option value="DISETUJUI">🟢 Disetujui (Terbitkan Persetujuan)</option>
                        <option value="DITOLAK">🔴 Ditolak / Dokumen Tidak Lengkap</option>''',
    '''<option value="MENUNGGU_VERIFIKASI_DOKUMEN">Menunggu Verifikasi Dokumen</option>
                        <option value="DOKUMEN_LENGKAP">Dokumen Lengkap</option>
                        <option value="MENUNGGU_CEK_FISIK">Menunggu Cek Fisik Lapangan</option>
                        <option value="PENETAPAN_JAMINAN_PPN">Penetapan Jaminan PPN 11%</option>
                        <option value="DISETUJUI">Disetujui (Terbitkan Persetujuan)</option>
                        <option value="DITOLAK">Ditolak / Dokumen Tidak Lengkap</option>'''
)

# 4. REPLACE EMOJI CIRCLES IN JS STATUS LABELS WITH FLAT SOLID DOTS
text = text.replace(
    '''const statusLabels = {
                    'MENUNGGU_VERIFIKASI_DOKUMEN': '🟡 Verifikasi Dokumen',
                    'DOKUMEN_LENGKAP': '🔵 Dokumen Lengkap',
                    'MENUNGGU_CEK_FISIK': '🟠 Cek Fisik Lapangan',
                    'PENETAPAN_JAMINAN_PPN': '🟣 Jaminan PPN 11%',
                    'DISETUJUI': '🟢 Disetujui',
                    'DITOLAK': '🔴 Ditolak'
                };''',
    '''const statusLabels = {
                    'MENUNGGU_VERIFIKASI_DOKUMEN': '<span class="flat-dot dot-yellow"></span>Verifikasi Dokumen',
                    'DOKUMEN_LENGKAP': '<span class="flat-dot dot-blue"></span>Dokumen Lengkap',
                    'MENUNGGU_CEK_FISIK': '<span class="flat-dot dot-orange"></span>Cek Fisik Lapangan',
                    'PENETAPAN_JAMINAN_PPN': '<span class="flat-dot dot-purple"></span>Jaminan PPN 11%',
                    'DISETUJUI': '<span class="flat-dot dot-green"></span>Disetujui',
                    'DITOLAK': '<span class="flat-dot dot-red"></span>Ditolak'
                };'''
)

# 5. REPLACE ANY REMAINING 🟡 in simulator message
text = text.replace('Status: 🟡 *Menunggu Verifikasi Dokumen*', 'Status: *Menunggu Verifikasi Dokumen*')

with open('Formulir_Pemohon_CEISA_PENGSEM_KBM.html', 'w', encoding='utf-8') as f:
    f.write(text)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('Successfully applied rigid full-width layout and flat solid dots!')
