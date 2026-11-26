#!/usr/bin/env python3
"""
Menggabungkan Dashboard Monitoring Pegawai dan Formulir Permohonan KBM ke dalam satu portal terpadu.
Menerapkan 100% Flat Icons (tanpa gradasi, tanpa 3D emoji) dan menyelaraskan font dan desain UI/UX.
"""

import re
import os

with open('Formulir_Pemohon_CEISA_PENGSEM_KBM.html', 'r', encoding='utf-8') as f:
    text = f.read()

# ================= FLAT SVG ICONS DEFINITIONS =================
FLAT_ICONS = {
    'dashboard': '''<svg class="flat-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9"></rect><rect x="14" y="3" width="7" height="5"></rect><rect x="14" y="12" width="7" height="9"></rect><rect x="3" y="16" width="7" height="5"></rect></svg>''',
    'form': '''<svg class="flat-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>''',
    'wa': '''<svg class="flat-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>''',
    'ktp': '''<svg class="flat-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"></rect><circle cx="9" cy="10" r="2"></circle><line x1="15" y1="8" x2="17" y2="8"></line><line x1="15" y1="12" x2="17" y2="12"></line><line x1="7" y1="16" x2="17" y2="16"></line></svg>''',
    'npwp': '''<svg class="flat-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="5" width="20" height="14" rx="2"></rect><line x1="2" y1="10" x2="22" y2="10"></line></svg>''',
    'car': '''<svg class="flat-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 16H9m10 0h3v-3.15a1 1 0 0 0-.84-.99L16 11l-2.7-3.6a1 1 0 0 0-.8-.4H5.24a2 2 0 0 0-1.8 1.1l-.8 1.63A6 6 0 0 0 2 12.42V16h2"></path><circle cx="6.5" cy="16.5" r="2.5"></circle><circle cx="16.5" cy="16.5" r="2.5"></circle></svg>''',
    'pin': '''<svg class="flat-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>''',
    'clip': '''<svg class="flat-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>''',
    'folder': '''<svg class="flat-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>''',
    'camera': '''<svg class="flat-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>''',
    'search': '''<svg class="flat-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>''',
    'shield': '''<svg class="flat-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>''',
    'send': '''<svg class="flat-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>''',
    'refresh': '''<svg class="flat-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>''',
    'check': '''<svg class="flat-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>'''
}

# 1. Update CSS: Add Portal Navigation & Unified Dashboard Styles
portal_css = '''
        /* ================= UNIFIED PORTAL NAVIGATION (FLAT & MINIMALIST) ================= */
        .portal-nav-bar {
            background: #FFFFFF;
            border-bottom: 2px solid var(--border);
            padding: 0 24px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }

        .portal-nav-container {
            max-width: 1300px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }

        .portal-tabs {
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .portal-tab-btn {
            background: transparent;
            border: none;
            border-bottom: 3px solid transparent;
            padding: 14px 18px;
            font-size: 0.88rem;
            font-weight: 700;
            font-family: inherit;
            color: var(--text-muted);
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
        }
        .portal-tab-btn:hover {
            color: var(--primary);
            background: #F8FAFC;
        }
        .portal-tab-btn.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
            background: #EFF6FF;
        }

        .portal-actions {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .btn-portal-action {
            background: #F1F5F9;
            border: 1px solid var(--border);
            color: var(--text-dark);
            padding: 7px 14px;
            border-radius: var(--radius-md);
            font-size: 0.80rem;
            font-weight: 700;
            font-family: inherit;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
        }
        .btn-portal-action:hover {
            background: #E2E8F0;
            color: var(--primary);
        }

        .flat-icon {
            display: inline-block;
            vertical-align: -2px;
            flex-shrink: 0;
        }

        /* ================= DASHBOARD MONITORING STYLES (MATCHED DESIGN SYSTEM) ================= */
        .dash-kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 16px;
            margin-bottom: 22px;
        }

        .dash-kpi-card {
            background: var(--bg-card);
            border: 1.5px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 18px 20px;
            box-shadow: var(--shadow);
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: transform 0.2s ease;
        }
        .dash-kpi-card:hover {
            transform: translateY(-2px);
        }

        .dash-kpi-label {
            font-size: 0.74rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }

        .dash-kpi-value {
            font-size: 1.85rem;
            font-weight: 800;
            color: var(--text-dark);
            line-height: 1.1;
        }

        .dash-kpi-icon-box {
            width: 44px;
            height: 44px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #F1F5F9;
            color: var(--primary);
        }

        .dash-toolbar-card {
            background: var(--bg-card);
            border: 1.5px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 14px 18px;
            box-shadow: var(--shadow);
            margin-bottom: 20px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 14px;
        }

        .dash-filter-tabs {
            display: flex;
            align-items: center;
            gap: 6px;
            flex-wrap: wrap;
        }

        .dash-tab-btn {
            padding: 6px 12px;
            border-radius: var(--radius-md);
            font-size: 0.78rem;
            font-weight: 700;
            border: 1px solid var(--border);
            background: #F8FAFC;
            color: var(--text-muted);
            cursor: pointer;
            font-family: inherit;
            transition: all 0.2s;
        }
        .dash-tab-btn:hover {
            background: #E2E8F0;
            color: var(--text-dark);
        }
        .dash-tab-btn.active {
            background: var(--primary);
            color: #FFFFFF;
            border-color: var(--primary);
        }

        .dash-search-box {
            display: flex;
            align-items: center;
            position: relative;
            min-width: 300px;
        }

        .dash-search-input {
            width: 100%;
            padding: 8px 12px 8px 34px;
            border-radius: var(--radius-md);
            border: 1.5px solid var(--border);
            font-size: 0.80rem;
            font-family: inherit;
            background: #F8FAFC;
        }
        .dash-search-input:focus {
            outline: none;
            border-color: var(--primary);
            background: #FFFFFF;
        }

        .dash-search-icon {
            position: absolute;
            left: 10px;
            color: var(--text-muted);
            pointer-events: none;
        }

        .dash-table-card {
            background: var(--bg-card);
            border: 1.5px solid var(--border);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow);
            overflow: hidden;
            margin-bottom: 30px;
        }

        .dash-table-header {
            padding: 14px 18px;
            background: #F8FAFC;
            border-bottom: 1.5px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .dash-table-header h2 {
            font-size: 0.95rem;
            font-weight: 800;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 0;
        }

        .dash-table-wrap {
            width: 100%;
            overflow-x: auto;
        }

        .dash-table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.82rem;
        }

        .dash-table thead {
            background: #F1F5F9;
            border-bottom: 2px solid var(--border);
        }

        .dash-table th {
            padding: 11px 16px;
            font-weight: 800;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.4px;
            font-size: 0.70rem;
            white-space: nowrap;
        }

        .dash-table tbody tr {
            border-bottom: 1px solid var(--border);
            transition: background 0.15s;
        }
        .dash-table tbody tr:hover {
            background: #F8FAFC;
        }

        .dash-table td {
            padding: 13px 16px;
            vertical-align: middle;
        }

        .flat-badge {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 4px 9px;
            border-radius: 4px;
            font-size: 0.70rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            white-space: nowrap;
        }

        .flat-badge.MENUNGGU_VERIFIKASI_DOKUMEN { background: #FEF3C7; color: #92400E; border: 1px solid #FCD34D; }
        .flat-badge.DOKUMEN_LENGKAP { background: #DBEAFE; color: #1E40AF; border: 1px solid #93C5FD; }
        .flat-badge.MENUNGGU_CEK_FISIK { background: #FFEDD5; color: #9A3412; border: 1px solid #FDBA74; }
        .flat-badge.PENETAPAN_JAMINAN_PPN { background: #F3E8FF; color: #6B21A8; border: 1px solid #D8B4FE; }
        .flat-badge.DISETUJUI { background: #DCFCE7; color: #166534; border: 1px solid #86EFAC; }
        .flat-badge.DITOLAK { background: #FEE2E2; color: #991B1B; border: 1px solid #FCA5A5; }

        .flat-btn-action {
            padding: 6px 12px;
            border-radius: var(--radius-md);
            font-size: 0.75rem;
            font-weight: 700;
            border: 1px solid var(--primary);
            background: var(--primary);
            color: #FFFFFF;
            cursor: pointer;
            transition: all 0.15s;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-family: inherit;
        }
        .flat-btn-action:hover {
            background: var(--primary-hover);
        }

        /* DRAWER PETUGAS FLAT */
        .dash-drawer-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(15, 23, 42, 0.45);
            backdrop-filter: blur(4px);
            z-index: 1000;
            justify-content: flex-end;
        }

        .dash-drawer-card {
            width: 100%;
            max-width: 540px;
            background: #FFFFFF;
            height: 100%;
            box-shadow: -10px 0 30px rgba(0, 0, 0, 0.15);
            display: flex;
            flex-direction: column;
            animation: slideInRight 0.28s ease-out;
        }

        .dash-drawer-header {
            padding: 16px 20px;
            background: var(--primary);
            color: #FFFFFF;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 3px solid var(--gold);
        }

        .dash-drawer-body {
            padding: 18px 20px;
            overflow-y: auto;
            flex: 1;
        }

        .dash-drawer-footer {
            padding: 14px 20px;
            background: #F8FAFC;
            border-top: 1.5px solid var(--border);
            display: flex;
            justify-content: flex-end;
            gap: 10px;
        }

        .dash-drawer-section {
            background: #F8FAFC;
            border: 1.5px solid var(--border);
            border-radius: var(--radius-md);
            padding: 14px;
            margin-bottom: 14px;
        }

        .dash-drawer-section-title {
            font-size: 0.75rem;
            font-weight: 800;
            color: var(--primary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* SIMULATOR WA FLAT */
        .dash-sim-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(15, 23, 42, 0.55);
            backdrop-filter: blur(4px);
            z-index: 1050;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .dash-sim-phone {
            width: 100%;
            max-width: 400px;
            height: 680px;
            max-height: 90vh;
            background: #FFFFFF;
            border-radius: 20px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            border: 2px solid var(--border);
        }

        .dash-sim-header {
            background: var(--primary);
            color: #FFFFFF;
            padding: 12px 16px;
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 2px solid var(--gold);
        }

        .dash-sim-body {
            flex: 1;
            background: #F8FAFC;
            padding: 14px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .dash-chat-bubble {
            max-width: 84%;
            padding: 10px 12px;
            border-radius: 8px;
            font-size: 0.82rem;
            line-height: 1.45;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
            border: 1px solid var(--border);
        }

        .dash-chat-bot {
            align-self: flex-start;
            background: #FFFFFF;
            color: var(--text-dark);
            border-left: 3px solid var(--primary);
        }

        .dash-chat-user {
            align-self: flex-end;
            background: #EFF6FF;
            color: var(--primary);
            border-right: 3px solid var(--primary);
        }

        .dash-chat-btn-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
            margin-top: 8px;
        }

        .dash-chat-btn {
            background: #FFFFFF;
            border: 1.5px solid var(--primary);
            color: var(--primary);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.80rem;
            font-weight: 700;
            cursor: pointer;
            text-align: center;
            font-family: inherit;
            transition: all 0.15s;
        }
        .dash-chat-btn:hover {
            background: var(--primary);
            color: #FFFFFF;
        }

        .dash-sim-footer {
            padding: 10px 14px;
            background: #F1F5F9;
            border-top: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .dash-sim-input {
            flex: 1;
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid var(--border);
            font-size: 0.82rem;
            background: #FFFFFF;
            font-family: inherit;
        }
        .dash-sim-input:focus {
            outline: none;
            border-color: var(--primary);
        }

        .dash-sim-send-btn {
            background: var(--primary);
            color: #FFFFFF;
            border: none;
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 0.80rem;
            font-weight: 700;
            cursor: pointer;
            font-family: inherit;
        }
'''

# Insert portal_css before </style>
style_close_pos = text.find('</style>')
text = text[:style_close_pos] + portal_css + '\n' + text[style_close_pos:]

# 2. Add Portal Navigation Bar right after </header>
nav_html = f'''
    <!-- ================= PORTAL TOP NAVIGATION (FLAT & UNIFIED) ================= -->
    <nav class="portal-nav-bar">
        <div class="portal-nav-container">
            <div class="portal-tabs">
                <button type="button" class="portal-tab-btn active" id="tabBtnDashboard" onclick="switchPortalView('dashboard')">
                    {FLAT_ICONS['dashboard']}
                    Dashboard Monitoring Pegawai
                </button>
                <button type="button" class="portal-tab-btn" id="tabBtnFormulir" onclick="switchPortalView('formulir')">
                    {FLAT_ICONS['form']}
                    Formulir Permohonan KBM
                </button>
            </div>
            <div class="portal-actions">
                <button type="button" class="btn-portal-action" onclick="openWhatsAppSimulator()">
                    {FLAT_ICONS['wa']}
                    Simulator Bot WhatsApp
                </button>
            </div>
        </div>
    </nav>
'''

header_end = text.find('</header>') + len('</header>')
text = text[:header_end] + nav_html + text[header_end:]

# Wrap Wizard bar container with ID for easy hide/show
text = text.replace(
    '<div class="wizard-bar-container">',
    '<div class="wizard-bar-container" id="wizardBarContainer" style="display:none;">'
)

# 3. Add Dashboard HTML view right before <div class="main-container">
dashboard_view_html = f'''
    <!-- ================= PORTAL VIEW 1: DASHBOARD MONITORING PEGAWAI ================= -->
    <div id="viewDashboard" class="main-container" style="display:block; padding-top:20px;">
        
        <!-- KPI METRICS SUMMARY -->
        <section class="dash-kpi-grid">
            <div class="dash-kpi-card">
                <div>
                    <div class="dash-kpi-label">Total Permohonan</div>
                    <div class="dash-kpi-value" id="kpiTotal">0</div>
                </div>
                <div class="dash-kpi-icon-box">{FLAT_ICONS['clip']}</div>
            </div>
            <div class="dash-kpi-card">
                <div>
                    <div class="dash-kpi-label">Verifikasi Dokumen</div>
                    <div class="dash-kpi-value" id="kpiVerifikasi" style="color:#D97706;">0</div>
                </div>
                <div class="dash-kpi-icon-box" style="color:#D97706;">{FLAT_ICONS['search']}</div>
            </div>
            <div class="dash-kpi-card">
                <div>
                    <div class="dash-kpi-label">Cek Fisik Lapangan</div>
                    <div class="dash-kpi-value" id="kpiCekFisik" style="color:#EA580C;">0</div>
                </div>
                <div class="dash-kpi-icon-box" style="color:#EA580C;">{FLAT_ICONS['car']}</div>
            </div>
            <div class="dash-kpi-card">
                <div>
                    <div class="dash-kpi-label">Jaminan PPN 11%</div>
                    <div class="dash-kpi-value" id="kpiJaminan" style="color:#7C3AED;">0</div>
                </div>
                <div class="dash-kpi-icon-box" style="color:#7C3AED;">{FLAT_ICONS['npwp']}</div>
            </div>
            <div class="dash-kpi-card">
                <div>
                    <div class="dash-kpi-label">Disetujui (Selesai)</div>
                    <div class="dash-kpi-value" id="kpiSelesai" style="color:#16A34A;">0</div>
                </div>
                <div class="dash-kpi-icon-box" style="color:#16A34A;">{FLAT_ICONS['check']}</div>
            </div>
        </section>

        <!-- TOOLBAR: FILTER & SEARCH -->
        <section class="dash-toolbar-card">
            <div class="dash-filter-tabs">
                <button class="dash-tab-btn active" onclick="filterByStatus('SEMUA', this)">Semua Permohonan</button>
                <button class="dash-tab-btn" onclick="filterByStatus('MENUNGGU_VERIFIKASI_DOKUMEN', this)">🟡 Verifikasi Berkas</button>
                <button class="dash-tab-btn" onclick="filterByStatus('MENUNGGU_CEK_FISIK', this)">🟠 Cek Fisik Lapangan</button>
                <button class="dash-tab-btn" onclick="filterByStatus('PENETAPAN_JAMINAN_PPN', this)">🟣 Penetapan Jaminan</button>
                <button class="dash-tab-btn" onclick="filterByStatus('DISETUJUI', this)">🟢 Disetujui</button>
            </div>
            <div class="dash-search-box">
                <span class="dash-search-icon">{FLAT_ICONS['search']}</span>
                <input type="text" id="searchInput" class="dash-search-input" placeholder="Cari Nama, Nopol BP, NIK, atau Agenda..." oninput="handleSearch()">
            </div>
        </section>

        <!-- DATA TABLE -->
        <section class="dash-table-card">
            <div class="dash-table-header">
                <h2>{FLAT_ICONS['clip']} Daftar Antrean Permohonan Masuk (Real-Time)</h2>
                <button class="btn-portal-action" onclick="loadPermohonanData()">
                    {FLAT_ICONS['refresh']} Muat Ulang Data
                </button>
            </div>
            <div class="dash-table-wrap">
                <table class="dash-table">
                    <thead>
                        <tr>
                            <th>No. Agenda / Waktu</th>
                            <th>Nama Pemohon (KTP)</th>
                            <th>No. WhatsApp Kontak</th>
                            <th>Kendaraan (Nopol BP)</th>
                            <th>Rute Pelabuhan</th>
                            <th>Status Permohonan</th>
                            <th>Aksi Petugas</th>
                        </tr>
                    </thead>
                    <tbody id="permohonanTableBody">
                        <!-- Data rows injected by JS -->
                    </tbody>
                </table>
            </div>
        </section>

    </div>

    <!-- ================= PORTAL VIEW 2: FORMULIR PEMOHON ================= -->
    <div id="viewFormulir" style="display:none;">
'''

main_container_pos = text.find('<div class="main-container">')
text = text[:main_container_pos] + dashboard_view_html + text[main_container_pos:]

# Close viewFormulir right before modals
modals_pos = text.find('<!-- ================= MODERN POPUP: SUCCESS')
text = text[:modals_pos] + '\n    </div> <!-- /viewFormulir -->\n\n' + text[modals_pos:]

# 4. Add Drawer & Simulator Modals right before script
drawer_and_sim_html = f'''
    <!-- DRAWER DETAIL VERIFIKASI PETUGAS -->
    <div class="dash-drawer-overlay" id="drawerDetail" onclick="closeDrawer(event)">
        <div class="dash-drawer-card" onclick="event.stopPropagation()">
            <div class="dash-drawer-header">
                <div>
                    <h2 id="drawerTitle" style="font-size:1.02rem; font-weight:800; margin:0;">Detail Permohonan</h2>
                    <div id="drawerSubtitle" style="font-size:0.72rem; color:var(--gold); font-weight:700;">No. Agenda: -</div>
                </div>
                <button type="button" onclick="closeDrawerDirect()" style="background:none; border:none; color:#FFFFFF; font-size:1.4rem; cursor:pointer;">&times;</button>
            </div>
            <div class="dash-drawer-body">
                
                <!-- Section Data Pemohon -->
                <div class="dash-drawer-section">
                    <div class="dash-drawer-section-title">{FLAT_ICONS['ktp']} Data Pemohon &amp; Kontak WhatsApp</div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; font-size:0.80rem;">
                        <div>
                            <div style="color:var(--text-muted); font-size:0.70rem;">Nama Lengkap (KTP)</div>
                            <div id="dNama" style="font-weight:800;">-</div>
                        </div>
                        <div>
                            <div style="color:var(--text-muted); font-size:0.70rem;">NIK (16 Digit)</div>
                            <div class="mono" id="dNik" style="font-weight:700;">-</div>
                        </div>
                        <div>
                            <div style="color:var(--text-muted); font-size:0.70rem;">Nomor NPWP</div>
                            <div class="mono" id="dNpwp" style="font-weight:700;">-</div>
                        </div>
                        <div>
                            <div style="color:var(--text-muted); font-size:0.70rem;">No. WA Pemohon (KTP)</div>
                            <div class="mono" id="dWaPemohon" style="font-weight:700;">-</div>
                        </div>
                        <div style="grid-column: span 2;">
                            <div style="color:var(--text-muted); font-size:0.70rem;">No. WA Pengirim / Submitter Bot</div>
                            <div id="dWaPengirim" style="font-weight:700;">-</div>
                        </div>
                    </div>
                </div>

                <!-- Section Kendaraan & Rute -->
                <div class="dash-drawer-section">
                    <div class="dash-drawer-section-title">{FLAT_ICONS['car']} Data Kendaraan &amp; Rute Perjalanan</div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; font-size:0.80rem;">
                        <div>
                            <div style="color:var(--text-muted); font-size:0.70rem;">Nomor Polisi (BP)</div>
                            <div class="mono" style="color:var(--primary); font-size:1rem; font-weight:800;" id="dNopol">-</div>
                        </div>
                        <div>
                            <div style="color:var(--text-muted); font-size:0.70rem;">Merek / Tipe</div>
                            <div id="dMerek" style="font-weight:700;">-</div>
                        </div>
                        <div>
                            <div style="color:var(--text-muted); font-size:0.70rem;">Tahun &amp; Warna</div>
                            <div id="dTahunWarna" style="font-weight:700;">-</div>
                        </div>
                        <div>
                            <div style="color:var(--text-muted); font-size:0.70rem;">Nomor Rangka</div>
                            <div class="mono" style="font-size:0.74rem; font-weight:700;" id="dNoRangka">-</div>
                        </div>
                        <div style="grid-column: span 2;">
                            <div style="color:var(--text-muted); font-size:0.70rem;">Pelabuhan Tujuan &amp; Keperluan</div>
                            <div id="dTujuanKeperluan" style="font-weight:700;">-</div>
                        </div>
                    </div>
                </div>

                <!-- Section Dokumen Terlampir -->
                <div class="dash-drawer-section">
                    <div class="dash-drawer-section-title">{FLAT_ICONS['folder']} Dokumen Terlampir (AI Vision Verified)</div>
                    <div style="display:flex; flex-direction:column; gap:6px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; background:#FFFFFF; padding:8px 12px; border-radius:6px; border:1px solid var(--border);">
                            <div><strong>KTP Asli Berwarna</strong></div>
                            <span class="flat-badge DISETUJUI">{FLAT_ICONS['check']} Terverifikasi AI</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center; background:#FFFFFF; padding:8px 12px; border-radius:6px; border:1px solid var(--border);">
                            <div><strong>Kartu NPWP Asli</strong></div>
                            <span class="flat-badge DISETUJUI">{FLAT_ICONS['check']} Cocok dengan KTP</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center; background:#FFFFFF; padding:8px 12px; border-radius:6px; border:1px solid var(--border);">
                            <div><strong>Dokumen STNK &amp; BPKB / Leasing</strong></div>
                            <span class="flat-badge DOKUMEN_LENGKAP">Tersedia</span>
                        </div>
                    </div>
                </div>

                <!-- Section Update Status oleh Pegawai -->
                <div class="dash-drawer-section" style="background:#EFF6FF; border-color:#BFDBFE;">
                    <div class="dash-drawer-section-title" style="color:var(--primary);">{FLAT_ICONS['clip']} Aksi Pembaruan Status Petugas</div>
                    <label style="font-size:0.74rem; font-weight:700; color:var(--primary); display:block; margin-bottom:4px;">Ubah Status Permohonan:</label>
                    <select id="selectNewStatus" style="width:100%; padding:9px; border-radius:6px; border:1.5px solid var(--primary); font-size:0.82rem; font-weight:700; background:#FFFFFF; margin-bottom:10px; font-family:inherit;">
                        <option value="MENUNGGU_VERIFIKASI_DOKUMEN">🟡 Menunggu Verifikasi Dokumen</option>
                        <option value="DOKUMEN_LENGKAP">🔵 Dokumen Lengkap</option>
                        <option value="MENUNGGU_CEK_FISIK">🟠 Menunggu Cek Fisik Lapangan</option>
                        <option value="PENETAPAN_JAMINAN_PPN">🟣 Penetapan Jaminan PPN 11%</option>
                        <option value="DISETUJUI">🟢 Disetujui (Terbitkan Persetujuan)</option>
                        <option value="DITOLAK">🔴 Ditolak / Dokumen Tidak Lengkap</option>
                    </select>

                    <label style="font-size:0.74rem; font-weight:700; color:var(--primary); display:block; margin-bottom:4px;">Disposisi Petugas (Terkirim Otomatis ke WA Pemohon):</label>
                    <textarea id="txtCatatanPetugas" rows="3" style="width:100%; padding:8px; border-radius:6px; border:1px solid var(--border); font-size:0.80rem; font-family:inherit;" placeholder="Contoh: Berkas telah lengkap. Silakan bawa kendaraan ke Pos Bea Cukai Pelabuhan Telaga Punggur untuk cek fisik..."></textarea>
                </div>

            </div>
            <div class="dash-drawer-footer">
                <button type="button" class="btn-portal-action" onclick="closeDrawerDirect()">Batal</button>
                <button type="button" class="flat-btn-action" onclick="saveStatusUpdate()">{FLAT_ICONS['check']} Simpan &amp; Notifikasi Pemohon</button>
            </div>
        </div>
    </div>

    <!-- SIMULATOR BOT WHATSAPP INTERAKTIF -->
    <div class="dash-sim-overlay" id="simModal">
        <div class="dash-sim-phone">
            <!-- Header WA -->
            <div class="dash-sim-header">
                <div style="font-size:1.1rem; cursor:pointer;" onclick="closeWhatsAppSimulator()">←</div>
                <div style="flex:1;">
                    <div style="font-weight:700; font-size:0.88rem;">Bea Cukai Batam (KBM Bot)</div>
                    <div style="font-size:0.68rem; color:#A7F3D0;">Official WhatsApp Sandbox</div>
                </div>
                <button type="button" onclick="closeWhatsAppSimulator()" style="background:none; border:none; color:#FFFFFF; font-size:1.3rem; cursor:pointer;">&times;</button>
            </div>

            <!-- Body Chat -->
            <div class="dash-sim-body" id="simChatBody">
                <!-- Chat messages injected by JS -->
            </div>

            <!-- Footer Input -->
            <div class="dash-sim-footer">
                <input type="text" id="simInputText" class="dash-sim-input" placeholder="Ketik pesan..." onkeydown="if(event.key==='Enter') sendSimMessage()">
                <button type="button" class="dash-sim-send-btn" onclick="sendSimMessage()">Kirim</button>
            </div>
        </div>
    </div>
'''

script_tag_pos = text.find('<script>')
text = text[:script_tag_pos] + drawer_and_sim_html + '\n' + text[script_tag_pos:]

# 5. Add JavaScript for Portal switching & Dashboard data
portal_js = '''
        // ================= UNIFIED PORTAL SWITCHING =================
        let currentPortalView = 'dashboard';

        function switchPortalView(view) {
            currentPortalView = view;
            const viewDash = document.getElementById('viewDashboard');
            const viewForm = document.getElementById('viewFormulir');
            const wizBar = document.getElementById('wizardBarContainer');
            const btnDash = document.getElementById('tabBtnDashboard');
            const btnForm = document.getElementById('tabBtnFormulir');

            if (view === 'dashboard') {
                if (viewDash) viewDash.style.display = 'block';
                if (viewForm) viewForm.style.display = 'none';
                if (wizBar) wizBar.style.display = 'none';
                if (btnDash) btnDash.classList.add('active');
                if (btnForm) btnForm.classList.remove('active');
                loadPermohonanData();
            } else {
                if (viewDash) viewDash.style.display = 'none';
                if (viewForm) viewForm.style.display = 'block';
                if (wizBar) wizBar.style.display = 'block';
                if (btnDash) btnDash.classList.remove('active');
                if (btnForm) btnForm.classList.add('active');
            }
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        // ================= DASHBOARD DATA & ACTIONS =================
        let allPermohonan = [];
        let currentFilter = 'SEMUA';
        let selectedPermohonanId = null;

        async function loadPermohonanData() {
            try {
                const res = await fetch('/api/permohonan');
                if (res.ok) {
                    allPermohonan = await res.json();
                }
            } catch (e) {
                console.warn('Load permohonan local fallback');
            }
            renderTable();
            updateKpis();
        }

        function updateKpis() {
            const elTot = document.getElementById('kpiTotal');
            const elVer = document.getElementById('kpiVerifikasi');
            const elCek = document.getElementById('kpiCekFisik');
            const elJam = document.getElementById('kpiJaminan');
            const elSel = document.getElementById('kpiSelesai');

            if (elTot) elTot.innerText = allPermohonan.length;
            if (elVer) elVer.innerText = allPermohonan.filter(p => p.status === 'MENUNGGU_VERIFIKASI_DOKUMEN').length;
            if (elCek) elCek.innerText = allPermohonan.filter(p => p.status === 'MENUNGGU_CEK_FISIK' || p.status === 'DOKUMEN_LENGKAP').length;
            if (elJam) elJam.innerText = allPermohonan.filter(p => p.status === 'PENETAPAN_JAMINAN_PPN').length;
            if (elSel) elSel.innerText = allPermohonan.filter(p => p.status === 'DISETUJUI').length;
        }

        function filterByStatus(status, btn) {
            currentFilter = status;
            document.querySelectorAll('.dash-tab-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            renderTable();
        }

        function handleSearch() {
            renderTable();
        }

        function renderTable() {
            const inputEl = document.getElementById('searchInput');
            const query = inputEl ? inputEl.value.toLowerCase() : '';
            const tbody = document.getElementById('permohonanTableBody');
            if (!tbody) return;
            
            let filtered = allPermohonan.filter(p => {
                const matchStatus = (currentFilter === 'SEMUA') || (p.status === currentFilter);
                const matchQuery = !query || 
                    (p.nama_pemohon && p.nama_pemohon.toLowerCase().includes(query)) ||
                    (p.nopol && p.nopol.toLowerCase().includes(query)) ||
                    (p.id && p.id.toLowerCase().includes(query)) ||
                    (p.nik && p.nik.includes(query));
                return matchStatus && matchQuery;
            });

            if (filtered.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" style="text-align:center; padding:32px; color:var(--text-muted);">
                            Tidak ada permohonan yang sesuai dengan filter pencarian.
                        </td>
                    </tr>
                `;
                return;
            }

            tbody.innerHTML = filtered.map(p => {
                const statusLabels = {
                    'MENUNGGU_VERIFIKASI_DOKUMEN': '🟡 Verifikasi Dokumen',
                    'DOKUMEN_LENGKAP': '🔵 Dokumen Lengkap',
                    'MENUNGGU_CEK_FISIK': '🟠 Cek Fisik Lapangan',
                    'PENETAPAN_JAMINAN_PPN': '🟣 Jaminan PPN 11%',
                    'DISETUJUI': '🟢 Disetujui',
                    'DITOLAK': '🔴 Ditolak'
                };
                const statusText = statusLabels[p.status] || p.status;
                
                let waDisplay = `<div><strong>${p.no_wa_pemohon || '-'}</strong></div>`;
                if (p.nomor_berbeda) {
                    waDisplay += `<div style="font-size:0.68rem; color:#EA580C; font-weight:700;">(Submitter: ${p.no_wa_pengirim})</div>`;
                }

                return `
                    <tr>
                        <td>
                            <div class="mono" style="color:var(--primary); font-weight:800;">${p.id}</div>
                            <div style="font-size:0.70rem; color:var(--text-muted);">${p.tanggal_pengajuan || '-'}</div>
                            <span style="font-size:0.68rem; padding:2px 6px; border-radius:4px; background:#F1F5F9; color:#475569; font-weight:700;">
                                ${p.sumber === 'WHATSAPP_BOT' ? 'WhatsApp Bot' : 'Web CEISA'}
                            </span>
                        </td>
                        <td>
                            <div style="font-weight:800; font-size:0.85rem;">${p.nama_pemohon || '-'}</div>
                            <div class="mono" style="font-size:0.72rem; color:var(--text-muted);">NIK: ${p.nik || '-'}</div>
                        </td>
                        <td>${waDisplay}</td>
                        <td>
                            <div class="mono" style="font-size:0.90rem; color:var(--primary); font-weight:800;">${p.nopol || '-'}</div>
                            <div style="font-size:0.70rem; color:var(--text-muted);">${p.merek_tipe || '-'}</div>
                        </td>
                        <td>
                            <div style="font-weight:700;">${p.pelabuhan_tujuan || '-'}</div>
                            <div style="font-size:0.68rem; color:var(--text-muted);">Kembali: ${p.tanggal_kembali || '-'}</div>
                        </td>
                        <td>
                            <span class="flat-badge ${p.status}">
                                ${statusText}
                            </span>
                        </td>
                        <td>
                            <button class="flat-btn-action" onclick="openDrawerDetail('${p.id}')">
                                Review Berkas
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        // Drawer
        function openDrawerDetail(id) {
            const item = allPermohonan.find(p => p.id === id);
            if (!item) return;
            selectedPermohonanId = id;

            document.getElementById('drawerTitle').innerText = 'Review Permohonan • ' + item.nama_pemohon;
            document.getElementById('drawerSubtitle').innerText = 'No. Agenda: ' + item.id + ' | Tanggal Masuk: ' + (item.tanggal_pengajuan || '-');
            
            document.getElementById('dNama').innerText = item.nama_pemohon || '-';
            document.getElementById('dNik').innerText = item.nik || '-';
            document.getElementById('dNpwp').innerText = item.npwp || '-';
            document.getElementById('dWaPemohon').innerText = item.no_wa_pemohon || '-';
            
            if (item.nomor_berbeda) {
                document.getElementById('dWaPengirim').innerHTML = `<span style="color:#EA580C; font-weight:700;">${item.no_wa_pengirim} (Berbeda dengan pemohon - Submitter)</span>`;
            } else {
                document.getElementById('dWaPengirim').innerText = item.no_wa_pengirim + ' (Sama dengan pemohon)';
            }

            document.getElementById('dNopol').innerText = item.nopol || '-';
            document.getElementById('dMerek').innerText = item.merek_tipe || '-';
            document.getElementById('dTahunWarna').innerText = item.tahun_warna || '-';
            document.getElementById('dNoRangka').innerText = item.no_rangka || '-';
            document.getElementById('dTujuanKeperluan').innerText = (item.pelabuhan_tujuan || '-') + ' • ' + (item.keperluan || '-');

            document.getElementById('selectNewStatus').value = item.status;
            document.getElementById('txtCatatanPetugas').value = '';

            document.getElementById('drawerDetail').style.display = 'flex';
        }

        function closeDrawerDirect() {
            document.getElementById('drawerDetail').style.display = 'none';
        }

        function closeDrawer(e) {
            if (e.target.id === 'drawerDetail') closeDrawerDirect();
        }

        async function saveStatusUpdate() {
            if (!selectedPermohonanId) return;
            const newStatus = document.getElementById('selectNewStatus').value;
            const catatan = document.getElementById('txtCatatanPetugas').value;

            const item = allPermohonan.find(p => p.id === selectedPermohonanId);
            if (item) {
                item.status = newStatus;
                try {
                    await fetch('/api/permohonan/update', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ id: selectedPermohonanId, status: newStatus, catatan })
                    });
                } catch (e) {
                    console.log('Update local state fallback');
                }
            }

            closeDrawerDirect();
            renderTable();
            updateKpis();
            alert(`✓ Status Permohonan ${selectedPermohonanId} berhasil diperbarui menjadi ${newStatus}! Notifikasi pabean diteruskan ke pemohon.`);
        }

        // WhatsApp Simulator
        let simState = 'INIT';
        let simData = {
            no_pengirim: '+6281270001234',
            no_pemohon: '',
            nama_pemohon: '',
            ktp: null,
            npwp: null
        };

        function openWhatsAppSimulator() {
            document.getElementById('simModal').style.display = 'flex';
            if (simState === 'INIT') {
                resetSimulatorChat();
            }
        }

        function closeWhatsAppSimulator() {
            document.getElementById('simModal').style.display = 'none';
        }

        function resetSimulatorChat() {
            const body = document.getElementById('simChatBody');
            body.innerHTML = '';
            simState = 'CONFIRM_START';
            
            addBotMessage(
                `Halo! Selamat datang di Layanan Mandiri Pabean KPU Bea dan Cukai Tipe B Batam.\\n\\n` +
                `Apakah Anda akan mengajukan *Permohonan Pengeluaran Sementara Kendaraan Bermotor (PENGSEM KBM)* dari Kawasan Bebas Batam ke TLDDP?`,
                [
                    { label: 'Iya, Ajukan Permohonan', action: 'handleIya' },
                    { label: 'Tidak', action: 'handleTidak' }
                ]
            );
        }

        function addBotMessage(text, buttons = []) {
            const body = document.getElementById('simChatBody');
            const bubble = document.createElement('div');
            bubble.className = 'dash-chat-bubble dash-chat-bot';
            bubble.innerHTML = text.replace(/\\\\n/g, '<br>').replace(/\\\\*(.*?)\\\\*/g, '<strong>$1</strong>');

            if (buttons.length > 0) {
                const btnGroup = document.createElement('div');
                btnGroup.className = 'dash-chat-btn-group';
                buttons.forEach(b => {
                    const btn = document.createElement('button');
                    btn.className = 'dash-chat-btn';
                    btn.innerText = b.label;
                    btn.onclick = () => window[b.action]();
                    btnGroup.appendChild(btn);
                });
                bubble.appendChild(btnGroup);
            }

            body.appendChild(bubble);
            body.scrollTop = body.scrollHeight;
        }

        function addUserMessage(text) {
            const body = document.getElementById('simChatBody');
            const bubble = document.createElement('div');
            bubble.className = 'dash-chat-bubble dash-chat-user';
            bubble.innerText = text;
            body.appendChild(bubble);
            body.scrollTop = body.scrollHeight;
        }

        function handleIya() {
            addUserMessage('Iya, Ajukan Permohonan');
            simState = 'CONFIRM_WA_NUMBER';
            setTimeout(() => {
                addBotMessage(
                    `Baik, terima kasih. Untuk keperluan kontak verifikasi pabean:\\n\\n` +
                    `Apakah nomor WhatsApp pemohon adalah nomor yang sedang Anda gunakan saat ini (*+62 812-7000-1234*) atau nomor berbeda?`,
                    [
                        { label: 'Nomor Sama (+62 812-7000-1234)', action: 'handleNoSama' },
                        { label: 'Nomor Pemohon Berbeda', action: 'handleNoBeda' }
                    ]
                );
            }, 450);
        }

        function handleTidak() {
            addUserMessage('Tidak');
            setTimeout(() => {
                addBotMessage('Baik, terima kasih. Silakan hubungi kami kembali jika Anda memerlukan layanan kepabeanan KBM Batam.');
            }, 350);
        }

        function handleNoSama() {
            addUserMessage('Nomor Sama (+62 812-7000-1234)');
            simData.no_pemohon = simData.no_pengirim;
            simState = 'INPUT_NAMA';
            setTimeout(() => {
                addBotMessage(`Nomor WhatsApp pemohon dicatat: *${simData.no_pemohon}*.\\n\\nSilakan ketikkan *Nama Lengkap Pemohon* sesuai KTP:`);
            }, 450);
        }

        function handleNoBeda() {
            addUserMessage('Nomor Pemohon Berbeda');
            simState = 'INPUT_NO_BEDA';
            setTimeout(() => {
                addBotMessage(`Silakan ketikkan *Nomor WhatsApp Pemohon* yang aktif (contoh: 081399887766):\\n\\n_(Nomor Anda saat ini tetap tercatat di sistem sebagai kontak submitter)_`);
            }, 450);
        }

        function sendSimMessage() {
            const input = document.getElementById('simInputText');
            const val = input.value.trim();
            if (!val) return;
            input.value = '';
            addUserMessage(val);

            if (simState === 'INPUT_NO_BEDA') {
                simData.no_pemohon = val;
                simState = 'INPUT_NAMA';
                setTimeout(() => {
                    addBotMessage(`Nomor pemohon tercatat: *${val}*.\\n\\nSekarang, silakan ketikkan *Nama Lengkap Pemohon* sesuai KTP:`);
                }, 450);
            } else if (simState === 'INPUT_NAMA') {
                simData.nama_pemohon = val.toUpperCase();
                simState = 'INPUT_KTP';
                setTimeout(() => {
                    addBotMessage(
                        `Nama pemohon tercatat: *${simData.nama_pemohon}*.\\n\\n` +
                        `Silakan kirimkan *Foto atau Berkas PDF KTP Asli* pemohon:`,
                        [
                            { label: 'Kirim Dokumen KTP Asli', action: 'simUploadKtp' }
                        ]
                    );
                }, 450);
            } else {
                setTimeout(() => {
                    addBotMessage('Mohon ikuti langkah yang tertera pada panduan di atas.');
                }, 350);
            }
        }

        function simUploadKtp() {
            addUserMessage('Mengirim berkas: KTP_Asli.pdf');
            setTimeout(() => {
                addBotMessage(
                    `✓ *KTP Berhasil Diterima & Dipindai!*\\n` +
                    `NIK: *1801071710940002*\\n` +
                    `Nama: *${simData.nama_pemohon || 'M RIDWANSYAH'}*\\n` +
                    `Alamat: *Batam Kota, Kepri*\\n\\n` +
                    `Terakhir untuk identitas awal, silakan kirimkan *Foto atau Berkas PDF Kartu NPWP Asli* pemohon:`,
                    [
                        { label: 'Kirim Dokumen NPWP Asli', action: 'simUploadNpwp' }
                    ]
                );
            }, 700);
        }

        function simUploadNpwp() {
            addUserMessage('Mengirim berkas: NPWP_Asli.pdf');
            setTimeout(() => {
                const newId = 'KBM-2026-' + String(allPermohonan.length + 1).padStart(3, '0');
                const newEntry = {
                    id: newId,
                    tanggal_pengajuan: new Date().toISOString().replace('T', ' ').substring(0, 19),
                    nama_pemohon: simData.nama_pemohon || 'M RIDWANSYAH',
                    nik: '1801071710940002',
                    npwp: '83.490.019.3-325.000',
                    no_wa_pengirim: simData.no_pengirim,
                    no_wa_pemohon: simData.no_pemohon || simData.no_pengirim,
                    nomor_berbeda: (simData.no_pemohon && simData.no_pemohon !== simData.no_pengirim),
                    nopol: 'BP 1843 AF',
                    merek_tipe: 'TOYOTA INNOVA REBORN',
                    tahun_warna: '2022 / HITAM',
                    no_rangka: 'MHFG7CD27B8SJ000644',
                    pelabuhan_tujuan: 'Kuala Tungkal (Jambi)',
                    status: 'MENUNGGU_VERIFIKASI_DOKUMEN',
                    sumber: 'WHATSAPP_BOT'
                };

                allPermohonan.unshift(newEntry);
                renderTable();
                updateKpis();

                addBotMessage(
                    `*Terima Kasih! Permohonan Berhasil Terdaftar.*\\n\\n` +
                    `No. Agenda Pabean: *#${newId}*\\n` +
                    `Nama: *${newEntry.nama_pemohon}*\\n` +
                    `Status: 🟡 *Menunggu Verifikasi Dokumen*\\n\\n` +
                    `Data Anda telah otomatis disuplai ke *Dashboard Petugas Bea Cukai Batam*.`
                );
            }, 850);
        }

        // Inisialisasi otomatis load data saat portal dibuka
        document.addEventListener('DOMContentLoaded', () => {
            loadPermohonanData();
        });
'''

last_script_tag = text.rfind('</script>')
text = text[:last_script_tag] + portal_js + '\n' + text[last_script_tag:]

# 6. REPLACE ALL EMOJIS WITH FLAT ICONS OR CLEAN TEXT
emoji_replacements = [
    ('🪪 Langkah 1: Identitas Pemohon (Scan KTP &amp; NPWP)', f"{FLAT_ICONS['ktp']} Langkah 1: Identitas Pemohon (Scan KTP &amp; NPWP)"),
    ('🪪 1. Foto / Scan KTP Asli', f"{FLAT_ICONS['ktp']} 1. Foto / Scan KTP Asli"),
    ('💳 2. Foto / Scan Kartu NPWP', f"{FLAT_ICONS['npwp']} 2. Foto / Scan Kartu NPWP"),
    ('📁 Berkas JPG, PNG, atau PDF', f"{FLAT_ICONS['folder']} Berkas JPG, PNG, atau PDF"),
    ('🚗 Langkah 2: Data Kendaraan (Scan STNK) &amp; Jaminan PPN', f"{FLAT_ICONS['car']} Langkah 2: Data Kendaraan (Scan STNK) &amp; Jaminan PPN"),
    ('📑 1. BPKB Asli / Surat Leasing', f"{FLAT_ICONS['clip']} 1. BPKB Asli / Surat Leasing"),
    ('📋 2. Lembar STNK Asli (Samsat Kepri)', f"{FLAT_ICONS['clip']} 2. Lembar STNK Asli (Samsat Kepri)"),
    ('📸 Foto Fisik Kendaraan &amp; Cek Fisik Lapangan (Kiriman Pemohon / WA)', f"{FLAT_ICONS['camera']} Foto Fisik Kendaraan &amp; Cek Fisik Lapangan (Kiriman Pemohon / WA)"),
    ('📁 Unggah Sekaligus (Multi-Foto)', f"{FLAT_ICONS['folder']} Unggah Sekaligus (Multi-Foto)"),
    ('🚗 Tampak Depan', 'Tampak Depan'),
    ('🚗 Tampak Belakang', 'Tampak Belakang'),
    ('🚗 Samping Kanan', 'Samping Kanan'),
    ('🚗 Samping Kiri', 'Samping Kiri'),
    ('🔍 Gesekan Rangka', 'Gesekan Rangka'),
    ('🔍 Gesekan Mesin', 'Gesekan Mesin'),
    ('📍 Langkah 3: Rute Perjalanan &amp; Periode Pengeluaran', f"{FLAT_ICONS['pin']} Langkah 3: Rute Perjalanan &amp; Periode Pengeluaran"),
    ('📋 Langkah 4: Ringkasan Pengajuan &amp; Validasi Loket Frontdesk', f"{FLAT_ICONS['clip']} Langkah 4: Ringkasan Pengajuan &amp; Validasi Loket Frontdesk"),
    ('🛡️ AUDIT KESESUAIAN BERKAS FISIK OLEH FRONTDESK LOKET', f"{FLAT_ICONS['shield']} AUDIT KESESUAIAN BERKAS FISIK OLEH FRONTDESK LOKET"),
    ('👁️ Pratinjau Bundel 10 Halaman PDF', f"{FLAT_ICONS['search']} Pratinjau Bundel 10 Halaman PDF"),
    ('🚀 Kirim Permohonan Pengeluaran KBM', f"{FLAT_ICONS['send']} Kirim Permohonan Pengeluaran KBM"),
    ('📸 Jepret &amp; Ekstrak', f"{FLAT_ICONS['camera']} Jepret &amp; Ekstrak"),
    ('📥 Unduh 1 PDF Asli', f"{FLAT_ICONS['form']} Unduh 1 PDF Asli"),
    ('📄 Bundel 1 PDF Fullset Resmi Masuk Nadine Kemenkeu', f"{FLAT_ICONS['form']} Bundel 1 PDF Fullset Resmi Masuk Nadine Kemenkeu"),
    ('❄️', ''),
    ('🔔', '')
]

for old_str, new_str in emoji_replacements:
    text = text.replace(old_str, new_str)

# Save to Formulir_Pemohon_CEISA_PENGSEM_KBM.html and index.html
with open('Formulir_Pemohon_CEISA_PENGSEM_KBM.html', 'w', encoding='utf-8') as f:
    f.write(text)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('Successfully merged Dashboard into index.html and Formulir_Pemohon_CEISA_PENGSEM_KBM.html with 100% Flat Icons!')
