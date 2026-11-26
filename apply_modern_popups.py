#!/usr/bin/env python3
import re

with open('Formulir_Pemohon_CEISA_PENGSEM_KBM.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. New CSS for Popups matching user reference image
new_popup_css = '''
        /* ================= MODERN MINIMALIST POPUP (SUCCESS & OOOOPS) ================= */
        .modern-popup-overlay, .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(15, 23, 42, 0.50);
            backdrop-filter: blur(5px);
            -webkit-backdrop-filter: blur(5px);
            z-index: 99999;
            align-items: center;
            justify-content: center;
            padding: 20px;
            box-sizing: border-box;
        }

        .modern-popup-card {
            background: #FFFFFF;
            width: 100%;
            max-width: 380px;
            border-radius: 20px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 20px 45px -10px rgba(0, 0, 0, 0.22), 0 0 0 1px rgba(0, 0, 0, 0.05);
            animation: popupSpring 0.35s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 36px 26px 44px 26px;
            box-sizing: border-box;
        }

        @keyframes popupSpring {
            0% { transform: scale(0.88) translateY(12px); opacity: 0; }
            100% { transform: scale(1) translateY(0); opacity: 1; }
        }

        .popup-icon-circle {
            width: 66px;
            height: 66px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 18px;
            background: #FFFFFF;
            position: relative;
            z-index: 2;
        }

        .popup-icon-circle.success {
            border: 2.5px solid #2563EB;
            color: #2563EB;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.15);
        }

        .popup-icon-circle.error {
            border: 2.5px solid #DC2626;
            color: #DC2626;
            box-shadow: 0 4px 14px rgba(220, 38, 38, 0.15);
        }

        .popup-title-success {
            margin: 0 0 8px 0;
            font-size: 1.55rem;
            font-weight: 800;
            color: #2563EB;
            letter-spacing: -0.3px;
            line-height: 1.2;
            position: relative;
            z-index: 2;
        }

        .popup-title-error {
            margin: 0 0 8px 0;
            font-size: 1.55rem;
            font-weight: 800;
            color: #DC2626;
            letter-spacing: -0.3px;
            line-height: 1.2;
            position: relative;
            z-index: 2;
        }

        .popup-desc {
            margin: 0 0 20px 0;
            font-size: 0.88rem;
            color: #64748B;
            line-height: 1.5;
            position: relative;
            z-index: 2;
            padding: 0 6px;
        }

        .popup-btn-success {
            width: 100%;
            padding: 12px 20px;
            background: #2563EB;
            color: #FFFFFF;
            border: none;
            border-radius: 10px;
            font-size: 0.95rem;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
            transition: all 0.2s ease;
            position: relative;
            z-index: 2;
        }
        .popup-btn-success:hover {
            background: #1D4ED8;
            transform: translateY(-1px);
            box-shadow: 0 6px 18px rgba(37, 99, 235, 0.45);
        }

        .popup-btn-error {
            width: 100%;
            padding: 12px 20px;
            background: #DC2626;
            color: #FFFFFF;
            border: none;
            border-radius: 10px;
            font-size: 0.95rem;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(220, 38, 38, 0.35);
            transition: all 0.2s ease;
            position: relative;
            z-index: 2;
        }
        .popup-btn-error:hover {
            background: #B91C1C;
            transform: translateY(-1px);
            box-shadow: 0 6px 18px rgba(220, 38, 38, 0.45);
        }

        .popup-wave-bg {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 65px;
            pointer-events: none;
            z-index: 1;
        }

        .popup-close-btn {
            position: absolute;
            top: 14px;
            right: 14px;
            background: transparent;
            border: none;
            font-size: 1.25rem;
            color: #94A3B8;
            cursor: pointer;
            line-height: 1;
            padding: 4px;
            border-radius: 50%;
            transition: color 0.2s;
            z-index: 3;
        }
        .popup-close-btn:hover {
            color: #475569;
        }
'''

# Replace old modal CSS
pos_start = text.find('.mismatch-modal-card {')
pos_end = text.find('</style>', pos_start)
if pos_start != -1 and pos_end != -1:
    text = text[:pos_start] + new_popup_css + '\n    ' + text[pos_end:]

# 2. New HTML for Modals
new_modals_html = '''
    <!-- ================= MODERN POPUP: SUCCESS (BERHASIL) ================= -->
    <div class="modern-popup-overlay" id="modalSuccess">
        <div class="modern-popup-card">
            <button type="button" class="popup-close-btn" onclick="closeSuccessModal()" title="Tutup">&times;</button>
            <div class="popup-icon-circle success">
                <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
            </div>
            <h3 class="popup-title-success" id="successModalTitle">Success!</h3>
            <p class="popup-desc" id="successModalDesc">Just a few more steps left. Please go on.</p>
            
            <button type="button" class="popup-btn-success" id="successModalBtn" onclick="closeSuccessModal()">
                Continue
            </button>

            <svg class="popup-wave-bg" viewBox="0 0 400 65" fill="none" preserveAspectRatio="none">
                <path d="M0 35C60 20 140 45 220 30C290 15 350 40 400 25V65H0V35Z" fill="#EFF6FF" opacity="0.8"/>
                <path d="M0 45C70 30 160 55 240 38C320 22 370 48 400 35V65H0V45Z" fill="#DBEAFE" opacity="0.9"/>
            </svg>
        </div>
    </div>

    <!-- ================= MODERN POPUP: OOOOPS! DATA KURANG / BELUM LENGKAP ================= -->
    <div class="modern-popup-overlay" id="modalValidation">
        <div class="modern-popup-card">
            <button type="button" class="popup-close-btn" onclick="closeValidationModal()" title="Tutup">&times;</button>
            <div class="popup-icon-circle error">
                <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </div>
            <h3 class="popup-title-error">Oooops!</h3>
            <p class="popup-desc" id="validationDescText" style="margin-bottom:12px;">Ada kolom wajib yang belum terisi lengkap:</p>
            
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:12px 14px; margin-bottom:20px; width:100%; text-align:left; box-sizing:border-box; z-index:2; position:relative; max-height:160px; overflow-y:auto;">
                <ul id="validationMissingList" style="margin:0 0 0 16px; padding:0; font-size:0.82rem; color:#DC2626; font-weight:700; line-height:1.65;"></ul>
            </div>

            <button type="button" class="popup-btn-error" onclick="closeValidationModal()">
                Lengkapi Data
            </button>

            <svg class="popup-wave-bg" viewBox="0 0 400 65" fill="none" preserveAspectRatio="none">
                <path d="M0 35C60 20 140 45 220 30C290 15 350 40 400 25V65H0V35Z" fill="#FEF2F2" opacity="0.8"/>
                <path d="M0 45C70 30 160 55 240 38C320 22 370 48 400 35V65H0V45Z" fill="#FEE2E2" opacity="0.9"/>
            </svg>
        </div>
    </div>

    <!-- ================= MODERN POPUP: OOOOPS! KETIDAKSESUAIAN NAMA ================= -->
    <div class="modern-popup-overlay" id="modalNamaMismatch">
        <div class="modern-popup-card">
            <button type="button" class="popup-close-btn" onclick="closeNamaMismatchModal()" title="Tutup">&times;</button>
            <div class="popup-icon-circle error">
                <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </div>
            <h3 class="popup-title-error">Oooops!</h3>
            <p class="popup-desc" style="margin-bottom:12px;">Nama pada NPWP tidak cocok dengan KTP pemohon.</p>
            
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:12px 14px; margin-bottom:20px; width:100%; text-align:left; box-sizing:border-box; z-index:2; position:relative; font-size:0.80rem;">
                <div style="margin-bottom:4px; color:#475569;">Nama KTP: <strong id="mismatchKtpNama" style="color:#00447C;">-</strong></div>
                <div style="margin-bottom:6px; color:#475569;">Nama NPWP: <strong id="mismatchNpwpNama" style="color:#DC2626;">-</strong></div>
                <div style="font-size:0.75rem; color:#64748B; line-height:1.4;">Pemohon dan NPWP wajib orang pribadi yang sama sesuai aturan kepabeanan.</div>
            </div>

            <button type="button" class="popup-btn-error" onclick="closeNamaMismatchModal()">
                Periksa Kembali
            </button>

            <svg class="popup-wave-bg" viewBox="0 0 400 65" fill="none" preserveAspectRatio="none">
                <path d="M0 35C60 20 140 45 220 30C290 15 350 40 400 25V65H0V35Z" fill="#FEF2F2" opacity="0.8"/>
                <path d="M0 45C70 30 160 55 240 38C320 22 370 48 400 35V65H0V45Z" fill="#FEE2E2" opacity="0.9"/>
            </svg>
        </div>
    </div>

    <!-- ================= MODERN POPUP: OOOOPS! FORMAT BERKAS DITOLAK ================= -->
    <div class="modern-popup-overlay" id="modalFormatAlert">
        <div class="modern-popup-card">
            <button type="button" class="popup-close-btn" onclick="closeFormatAlertModal()" title="Tutup">&times;</button>
            <div class="popup-icon-circle error">
                <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </div>
            <h3 class="popup-title-error">Oooops!</h3>
            <p class="popup-desc" style="margin-bottom:12px;">Format berkas yang Anda pilih tidak didukung sistem.</p>
            
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:12px 14px; margin-bottom:20px; width:100%; text-align:left; box-sizing:border-box; z-index:2; position:relative; font-size:0.80rem;">
                <div style="margin-bottom:4px; color:#334155;">Berkas dipilih: <strong id="rejectedFileName" style="color:#DC2626;">-</strong></div>
                <div style="font-size:0.76rem; color:#64748B;">Sistem hanya menerima berkas asli berekstensi <strong>JPG, PNG, atau PDF</strong>.</div>
            </div>

            <button type="button" class="popup-btn-error" onclick="closeFormatAlertModal()">
                Pilih Berkas Lain
            </button>

            <svg class="popup-wave-bg" viewBox="0 0 400 65" fill="none" preserveAspectRatio="none">
                <path d="M0 35C60 20 140 45 220 30C290 15 350 40 400 25V65H0V35Z" fill="#FEF2F2" opacity="0.8"/>
                <path d="M0 45C70 30 160 55 240 38C320 22 370 48 400 35V65H0V45Z" fill="#FEE2E2" opacity="0.9"/>
            </svg>
        </div>
    </div>

    <!-- ================= MODERN POPUP: OOOOPS! DOKUMEN HITAM PUTIH / FOTOKOPI ================= -->
    <div class="modern-popup-overlay" id="colorRejectionModal">
        <div class="modern-popup-card">
            <button type="button" class="popup-close-btn" onclick="closeColorRejectionModal()" title="Tutup">&times;</button>
            <div class="popup-icon-circle error">
                <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </div>
            <h3 class="popup-title-error">Oooops!</h3>
            <p class="popup-desc" style="margin-bottom:12px;">Dokumen terdeteksi hitam-putih atau fotokopi.</p>
            
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:12px 14px; margin-bottom:20px; width:100%; text-align:left; box-sizing:border-box; z-index:2; position:relative; font-size:0.80rem;">
                <div style="margin-bottom:4px; color:#334155;">Dokumen: <strong id="colorRejectionDocName" style="color:#DC2626;">-</strong></div>
                <div style="font-size:0.76rem; color:#64748B;">Sesuai regulasi kepabeanan, seluruh berkas wajib berupa <strong>dokumen asli berwarna</strong>.</div>
            </div>

            <button type="button" class="popup-btn-error" onclick="retryColorUpload()">
                Unggah Berkas Berwarna
            </button>

            <svg class="popup-wave-bg" viewBox="0 0 400 65" fill="none" preserveAspectRatio="none">
                <path d="M0 35C60 20 140 45 220 30C290 15 350 40 400 25V65H0V35Z" fill="#FEF2F2" opacity="0.8"/>
                <path d="M0 45C70 30 160 55 240 38C320 22 370 48 400 35V65H0V45Z" fill="#FEE2E2" opacity="0.9"/>
            </svg>
        </div>
    </div>
'''

# Find the old modal block to replace
h_start = text.find('<!-- MODAL PENOLAKAN BERKAS HITAM PUTIH')
h_end = text.find('<!-- MODAL KAMERA VIEW FINDER -->')
if h_start != -1 and h_end != -1:
    text = text[:h_start] + new_modals_html + '\n    ' + text[h_end:]

# Now remove the old modalNamaMismatch, modalValidation, modalFormatAlert that were after pdfModal
m_end_pos = text.find('<!-- SCRIPT OCR & JS REAL ENGINE -->')
pdf_end_pos = text.find('<!-- MODAL PERINGATAN KETIDAKSESUAIAN NAMA')
if pdf_end_pos != -1 and m_end_pos != -1:
    text = text[:pdf_end_pos] + '\n' + text[m_end_pos:]

# Add JS functions for Success modal
js_success_funcs = '''
        // ================= SUCCESS MODAL LOGIC =================
        let successModalCallback = null;
        function showSuccessModal(title, desc, btnText, callback) {
            const elTitle = document.getElementById('successModalTitle');
            const elDesc = document.getElementById('successModalDesc');
            const elBtn = document.getElementById('successModalBtn');
            if (elTitle) elTitle.innerText = title || 'Success!';
            if (elDesc) elDesc.innerText = desc || 'Just a few more steps left. Please go on.';
            if (elBtn) elBtn.innerText = btnText || 'Continue';
            successModalCallback = callback || null;
            const modal = document.getElementById('modalSuccess');
            if (modal) modal.style.display = 'flex';
        }

        function closeSuccessModal() {
            const modal = document.getElementById('modalSuccess');
            if (modal) modal.style.display = 'none';
            if (typeof successModalCallback === 'function') {
                const cb = successModalCallback;
                successModalCallback = null;
                cb();
            }
        }
'''

# Insert JS before </script>
last_script_pos = text.rfind('</script>')
if last_script_pos != -1:
    text = text[:last_script_pos] + js_success_funcs + '\n    ' + text[last_script_pos:]

# Update the submission button to use showSuccessModal instead of alert
old_alert_str = "alert('✓ Permohonan berhasil dikirim ke sistem! Silakan tunjukkan berkas fisik kepada Petugas Loket di Pelabuhan Telaga Punggur.')"
new_success_str = "showSuccessModal('Success!', 'Permohonan pengeluaran KBM berhasil dikirim ke sistem CEISA! Silakan tunjukkan berkas fisik kepada Petugas Loket di Pelabuhan Telaga Punggur.', 'Continue', () => window.location.reload())"
text = text.replace(old_alert_str, new_success_str)

with open('Formulir_Pemohon_CEISA_PENGSEM_KBM.html', 'w', encoding='utf-8') as f:
    f.write(text)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('Success: Both Formulir_Pemohon_CEISA_PENGSEM_KBM.html and index.html have been updated!')
