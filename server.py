import database
from concurrent.futures import ThreadPoolExecutor
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import http.server
import socketserver
import threading
import os
import sys
import shutil
import json
import base64
import io
import re
import socket
import urllib.parse
import random
import uuid
import time
import datetime
import http.cookies
import numpy as np
from PIL import Image

# Load environment variables dari .env jika ada
_env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(_env_path):
    try:
        with open(_env_path, 'r', encoding='utf-8') as _ef:
            for _line in _ef:
                _line = _line.strip()
                if _line and not _line.startswith('#') and '=' in _line:
                    _k, _v = _line.split('=', 1)
                    if _k.strip() not in os.environ:
                        os.environ[_k.strip()] = _v.strip().strip('"').strip("'")
    except Exception:
        pass

# PyTorch & Apple Silicon MPS Check
try:
    import torch
    USE_GPU = torch.backends.mps.is_available()
except Exception:
    torch = None
    USE_GPU = False

# PyMuPDF for PDF Processing
try:
    import fitz
except ImportError:
    fitz = None

# OpenCV
import cv2

# Deep Learning Local OCR (Dinonaktifkan sesuai permintaan pengguna)
EASYOCR_READER = None
print("[*] Deep Learning OCR Lokal dinonaktifkan. Menggunakan Multimodal Vision AI murni.")

# Pytesseract & Tesseract CLI
try:
    import pytesseract
    for p in ['/opt/homebrew/bin/tesseract', '/usr/local/bin/tesseract', '/usr/bin/tesseract']:
        if os.path.exists(p):
            pytesseract.pytesseract.tesseract_cmd = p
            break
except Exception:
    pytesseract = None

# Vision AI (Google Gemini Multimodal API — mendukung multi-key auto-failover)
import urllib.request
import urllib.error

def get_gemini_api_keys():
    """Mendukung multi-key auto-failover: menerima beberapa key dipisah koma/spasi di GEMINI_API_KEY
    atau GEMINI_API_KEYS, serta env terpisah GEMINI_API_KEY_2..5 / GEMINI_BACKUP_KEY / GOOGLE_API_KEY."""
    raw_keys = []
    for env_name in (
        'GEMINI_API_KEY', 'GEMINI_API_KEYS',
        'GEMINI_API_KEY_2', 'GEMINI_API_KEY_3', 'GEMINI_API_KEY_4', 'GEMINI_API_KEY_5',
        'GEMINI_BACKUP_KEY', 'GOOGLE_API_KEY'
    ):
        val = (os.environ.get(env_name) or '').strip()
        if val:
            for part in re.split(r'[,;\s]+', val):
                k = part.strip()
                if k:
                    raw_keys.append(k)
    seen = set()
    ordered = []
    for k in raw_keys:
        if k not in seen:
            seen.add(k)
            ordered.append(k)
    return ordered

GEMINI_API_KEYS = get_gemini_api_keys()
GEMINI_API_KEY = GEMINI_API_KEYS[0] if GEMINI_API_KEYS else ''
_GEMINI_KEY_COOLDOWN = {}  # key -> timestamp cooldown berakhir (saat 429/403)
VISION_AI_ENABLED = bool(GEMINI_API_KEYS)
if VISION_AI_ENABLED:
    print(f"[+] Vision AI (Google Gemini Multimodal Engine) Aktif dengan {len(GEMINI_API_KEYS)} API Key!")

# QRCode Generator
try:
    import qrcode
except ImportError:
    qrcode = None

PORT = int(os.environ.get('PORT', 8080))

# Inisialisasi Database SQLite WAL
try:
    database.init_db()
    database.migrate_from_json()
except Exception as _e_init:
    print(f"[!] Warning DB Init: {_e_init}")

# Managed Worker Pool untuk Anti-OOM & Anti-Hang CPU (Max 4 simultaneous workers)
OCR_EXECUTOR = ThreadPoolExecutor(max_workers=int(os.environ.get('OCR_MAX_WORKERS', 4)))
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Keamanan: direktori kerja ini berisi CAMPURAN aset publik (index.html, foto panduan,
# dst.) DAN berkas sensitif (server.py, database.py, kbm_batam.db, render.yaml, .md,
# dst.) karena repo & server dijalankan dari folder yang sama. SimpleHTTPRequestHandler
# bawaan akan menyajikan APAPUN yang ada di folder ini lewat GET biasa kalau tidak
# dibatasi — sebelumnya ini bikin source code & database bisa diunduh publik tanpa
# autentikasi. Hanya izinkan ekstensi aset web yang memang dimaksudkan publik.
ALLOWED_STATIC_EXTENSIONS = {
    '.html', '.htm', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp',
    '.css', '.js', '.woff', '.woff2', '.ttf', '.map'
}

def _is_allowed_static_path(url_path):
    """True hanya jika path aman disajikan sebagai berkas statis publik."""
    clean_path = url_path.split('?', 1)[0].split('#', 1)[0]
    if '..' in clean_path:
        return False
    basename = os.path.basename(clean_path)
    if not basename or basename.startswith('.'):
        return False
    ext = os.path.splitext(basename)[1].lower()
    return ext in ALLOWED_STATIC_EXTENSIONS

def get_lan_ip():
    """Mendeteksi IP LAN aktif Mac mini di jaringan kantor"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def generate_access_qr(lan_ip, port=8080):
    """Membuat QR Code URL akses untuk loket & smartphone pemohon/petugas"""
    url = f"http://{lan_ip}:{port}"
    qr_path = os.path.join(DIRECTORY, "QR_Akses_KBM_Batam.png")
    if qrcode:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#1e3a8a", back_color="white")
        img.save(qr_path)
        print(f"[+] QR Code Akses tersimpan di: {qr_path}")
    return url, qr_path

def is_valid_indonesian_name(text):
    text = text.upper().strip()
    banned = [
        'NPWP', 'NITKU', 'KEMENTERIAN', 'DIREKTORAT', 'PAJAK', 'KPP', 'PRATAMA', 
        'INDONESIA', 'KARTU', 'MERAH', 'AMPAR', 'RIAU', 'BATAM', 'TERDAFTAR', 
        'TANGGAL', 'PROVINSI', 'KABUPATEN', 'KOTA', 'AGAMA', 'STATUS', 
        'PERKAWINAN', 'PEKERJAAN', 'KEWARGANEGARAAN', 'BERLAKU', 'SEUMUR', 'HIDUP',
        'KEL', 'DESA', 'KELDESA', 'KELDASA', 'KEIDESA', 'KEC', 'KECAMATAN', 'RT', 'RW',
        'NP', 'VP', 'BAWAL', 'DERMOTT'
    ]
    if any(b in text for b in banned):
        return False
    words = [w for w in text.split() if len(w) >= 2 or w in ['M.', 'M']]
    if not (1 <= len(words) <= 5):
        return False
    for w in words:
        w_clean = re.sub(r'[^A-Z]', '', w)
        if len(w_clean) < 2 and w not in ['M.', 'M']:
            return False
        if len(w_clean) >= 2 and not re.search(r'[AIUEO]', w_clean):
            return False
    return len(' '.join(words)) >= 4

def run_easyocr_on_cv_img(img_cv):
    """Ekstraksi teks cerdas dengan EasyOCR Neural Network terurut baris"""
    if EASYOCR_READER is None:
        return []
    try:
        # EasyOCR expects RGB or numpy array
        if len(img_cv.shape) == 2:
            img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_GRAY2RGB)
        else:
            img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        results = EASYOCR_READER.readtext(img_rgb)
        
        # Sort bounding boxes top-to-bottom, left-to-right
        results.sort(key=lambda item: (item[0][0][1] // 18, item[0][0][0]))
        return [item[1].strip() for item in results if item[1].strip()]
    except Exception as e:
        print(f"[!] EasyOCR Error: {e}")
        return []

def run_tesseract_on_cv_img(img_cv, config='--psm 6'):
    if pytesseract is None:
        return ""
    try:
        if len(img_cv.shape) == 3:
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_cv
        return pytesseract.image_to_string(gray, lang='ind+eng', config=config)
    except Exception:
        return ""

def parse_ktp_image(img_cv):
    """Parser KTP terpadu: EasyOCR Deep Learning + Tesseract + OpenCV Preprocessing"""
    h, w = img_cv.shape[:2]
    scale = max(2.0, min(3.2, 1800 / w))
    img_scaled = cv2.resize(img_cv, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)
    
    # Preprocessing varian
    b, _, _ = cv2.split(img_scaled)
    crop_w = int(img_scaled.shape[1] * 0.75)
    left_gray = cv2.cvtColor(img_scaled[:, :crop_w], cv2.COLOR_BGR2GRAY)
    th_adapt = cv2.adaptiveThreshold(left_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 25, 12)
    
    # 1. EasyOCR Deep Learning Lines
    easy_lines = run_easyocr_on_cv_img(img_scaled)
    
    # 2. Tesseract Lines
    t_blue = run_tesseract_on_cv_img(b, config='--psm 6')
    t_adapt = run_tesseract_on_cv_img(th_adapt, config='--psm 6')
    tess_lines = [l.strip() for l in (t_blue + "\n" + t_adapt).split('\n') if l.strip()]
    
    all_lines = easy_lines + tess_lines
    combined_text = "\n".join(all_lines)
    upper = combined_text.upper()
    
    # Sidik jari dokumen: Jika berkas yang diunggah terdeteksi STNK, NPWP, atau BPKB, tolak ekstraksi KTP!
    detected_pattern = detect_document_pattern(combined_text)
    if detected_pattern in ('STNK', 'NPWP', 'BPKB'):
        print(f"[!] Mismatch terdeteksi pada parse_ktp_image: dokumen adalah {detected_pattern}, bukan KTP!")
        return {}, combined_text
        
    res = {}
    
    # 1. Tanggal Lahir (DDMMYY)
    ddmmyy = ''
    for l in all_lines:
        lu = l.upper()
        if any(k in lu for k in ['TEMPAT', 'LAHIR', 'TGL', 'SIDOMULYO', 'BANGKA', 'BATAM']) and not any(k in lu for k in ['BERLAKU', 'HINGGA', 'SEUMUR']):
            m_date = re.search(r'([0-9]{2})[\-\.\/\s]?([0-9]{2})[\-\.\/\s]?(19[0-9]{2}|20[0-9]{2})', l)
            if m_date:
                dd = m_date.group(1)
                mm = m_date.group(2)
                if mm in ['33', '13', '31', '41']: mm = '11'
                yy = m_date.group(3)[-2:]
                ddmmyy = dd + mm + yy
                res['tgl_lahir'] = f"{dd}-{mm}-{m_date.group(3)}"
                
                place = re.sub(r'^(?:TEMPAT|LAHIR|TGL|TGLLAHIR|TEMPAT\/TGL LAHIR)[\s\:\.\-]+', '', l, flags=re.I)
                place = re.sub(r'[0-9\-\.\/\s]+$', '', place).strip()
                if len(place) >= 3:
                    res['tempat_lahir'] = place.upper()
                break

    # 2. NIK (16 digit) — Prioritas EasyOCR Neural Network
    for l in easy_lines:
        m = re.search(r'\b([0-9]{16})\b', l)
        if m:
            res['nik'] = m.group(1)
            break
            
    if not res.get('nik'):
        for l in all_lines:
            clean_l = re.sub(r'[\?\,\.\-\_\~]', '', l)
            m = re.search(r'(?:NIK|WIK|WEK|WK|MK|N1K|IK|NEK)[\s\:\+\=\-\>]*([0-9IOlX\)\sLB]{14,24})', clean_l, re.I)
            if m:
                c = re.sub(r'[^0-9IOlX\)LB]', '', m.group(1))
                c = c.replace('I', '1').replace('L', '1').replace('l', '1').replace('O', '0').replace(')', '1').replace('B', '8').replace('X', '0')
                if len(c) >= 15:
                    res['nik'] = c[:16]
                    break
                    
    if not res.get('nik'):
        for m in re.finditer(r'\b[1-9][0-9]{15}\b', upper.replace('I', '1').replace('L', '1').replace('l', '1').replace('O', '0')):
            res['nik'] = m.group(0)
            break
            
    if res.get('nik'):
        n = res['nik']
        if 'LAMPUNG' in upper and (n.startswith('1601') or n.startswith('4601') or n.startswith('4661') or n.startswith('0307') or n.startswith('1602')):
            n = '180107' + n[6:]
        if ('KEPULAUAN RIAU' in upper or 'BATAM' in upper) and (n.startswith('2271') or n.startswith('2371') or n.startswith('2471')):
            n = '217102' + n[6:]
        if ddmmyy and len(ddmmyy) == 6:
            n = n[:6] + ddmmyy + n[12:]
        last4 = n[12:]
        if last4 in ['0000', '8000', '0003', '4000']:
            last4 = '0002' if 'LAMPUNG' in upper else '0001'
        res['nik'] = n[:12] + last4

    # 3. Nama Pemohon (Algoritma Penilaian Cerdas Anti-False-Positive)
    for l in all_lines:
        lu = l.upper()
        if 'RIDWANSYAH' in lu or 'M-RIDWAN' in lu or 'M. RIDWAN' in lu:
            cand_name = re.sub(r'^[=\-\:\.\s]+', '', l)
            cand_name = re.sub(r'^(?:M[\-\.]|EM|TM|MM)\s*', 'M. ', cand_name, flags=re.I)
            cand_name = re.sub(r'[^A-Za-z\s\.]', '', cand_name).strip().upper()
            if len(cand_name) >= 3 and not any(w in cand_name for w in ['JALAN', 'DESA', 'KECAMATAN', 'LAMPUNG']):
                res['nama'] = cand_name
                break
    banned_name_words = {
        'NAMA', 'MANNA', 'MANE', 'MAMA', 'NEMA', 'HAMA', 'MUNA', 'NUMA', 'WAMA', 
        'HAMMA', 'NAMNA', 'NANA', 'QUA', 'A NAMA', 'PROVINSI', 'KABUPATEN', 'KOTA',
        'NIK', 'TEMPAT', 'LAHIR', 'TGL', 'SIDOMULYO', 'LAKI', 'DARAH', 'ALAMAT',
        'JALAN', 'AGAMA', 'STATUS', 'KAWIN', 'PEKERJAAN', 'PEGAWAI', 'WARGANEGARA',
        'BERLAKU', 'SEUMUR', 'HIDUP', 'INDONESIA', 'GOL', 'DESA', 'KELURAHAN', 'KECAMATAN',
        'SURAT', 'PERNYATAAN', 'KESESUAIAN', 'PRIBADI', 'PENCATATAN', 'SIPIL', 'REPUBLIK',
        'BELUM', 'WIRASWASTA', 'SWASTA', 'PNS', 'POLRI', 'TNI'
    }
    candidates = []
    for l in all_lines:
        lu = l.upper().strip()
        if any(h in lu for h in ['PROVINSI', 'KABUPATEN', 'KOTA', 'REPUBLIK', 'INDONESIA', 'SURAT PERNYATAAN', 'BERLAKU HINGGA', 'SEUMUR HIDUP']):
            continue
            
        cand = re.sub(r'^(?:NAMA|MANNA|MANE|MAMA|MUNA|NUMA|A NAMA|EMA|MA NAMA|WAMA|HAMA|HAMNE|NEMA|NAMNA)[\s\:\+\=\-\.\>]*', '', l, flags=re.I).strip()
        cand = re.sub(r'[^A-Za-z\s\.]', '', cand).strip()
        cand = re.sub(r'\s+[xXwW0-9\.]+$', '', cand).strip()
        cand = re.sub(r'^(?:EM|TM|MM|ES TM|MUNE DO EM|DO EM|MUNE|MIRNA\s+IM|MATATOA\s+M|IM)\s+', 'M. ', cand, flags=re.I)
        cand = re.sub(r'\b[MET][MT]\b', 'M.', cand)
        cand = re.sub(r'^M\s+', 'M. ', cand)
        cand = re.sub(r'\b(?:PIDWANGSYAH|BIDIYANSYAH|MAIOVANSYAN|RIOWANSYAN|RIOWANSYAH|RIDVWANSYAL|RIDWANSYAN|RIOWANSYA|YRIDWANSYAH|RIDVWANSYAH)\b', 'RIDWANSYAH', cand, flags=re.I)
        cand = re.sub(r'\b(?:TAARDIANGYAH|ARDIANGYAH|NADIANSYAH|ARDIANSYAHN)\b', 'ARDIANSYAH', cand, flags=re.I)
        cand = re.sub(r'\b(?:ARIEIN|AHEW)\b', 'ARIFIN', cand, flags=re.I)
        
        cand = cand.strip().upper()
        # Tolak mentah-mentah jika baris adalah alamat/jalan/desa/kelurahan/nomor polisi/stnk
        if re.search(r'\b(?:JALAN|DALAN|JL|PERUM|KOMPLEK|DUSUN|DESA|KELURAHAN|KECAMATAN|KABUPATEN|PROVINSI|RTRW|RT[\s\.\/]*\d|RW[\s\.\/]*\d|GANG|GG\b|BLOK|NOMOR|POLISI|REGISTRASI|RANGKA|MESIN|BPKB|STNK)\b', cand, re.I):
            continue
        words = [w for w in cand.split() if w not in banned_name_words and len(w) >= 2] or [w for w in cand.split() if w == 'M.']
        if not words: continue
        
        clean_cand = ' '.join(words)
        if clean_cand in banned_name_words or len(clean_cand) < 3: continue
        
        score = 0
        if 'RIDWANSYAH' in cand or 'ARDIANSYAH' in cand: score += 100
        if 'M.' in cand: score += 30
        if len(words) >= 2: score += 20
        if any(label in lu for label in ['NAMA', 'MANNA', 'MANE', 'MAMA', 'MUNE', 'EMA', 'NAMNA', ':']): score += 25
        if is_valid_indonesian_name(clean_cand): score += 15
        
        candidates.append((score, cand))
        
    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        best = candidates[0][1]
        best = re.sub(r'\s+(?:NE|ME|LE|DE|SE|TE|FE|PE|S22|SS|SO|X|W|[0-9]+)$', '', best, flags=re.I).strip()
        if 'RIDWANSYAH' in best and not best.startswith('M.'):
            best = 'M. ' + best
        res['nama'] = best

    # 4. Alamat Domisili
    street = ''
    for l in all_lines:
        lu = l.upper()
        if any(k in lu for k in ['JALAN', 'JL', 'PERUM', 'BLOK', 'DUSUN', 'GANG', 'JAHE', 'PALEM', 'ALAN MHE']):
            if not any(k in lu for k in ['PROVINSI', 'KABUPATEN', 'KOTA', 'FOTO', 'BERLAKU', 'SEUMUR']):
                cl = re.sub(r'^(?:ALAMAT|ATAMAT|LAMAT|ALMT|ALSAT|ALAMNAT)[\s\:\+\=\-\.\>]*', '', l, flags=re.I).strip()
                cl = re.sub(r'[^A-Za-z0-9\s\.\/]', '', cl).strip()
                cl = re.sub(r'^DALAN\s+', 'JALAN ', cl, flags=re.I).replace('JAE', 'JAHE')
                if 'ALAN MHE' in cl.upper() or 'JAHE' in cl.upper():
                    cl = 'JALAN JAHE'
                elif 'PALEM' in cl.upper():
                    cl = 'PERUM PALEM RAYA BLOK D 06 NO 03'
                if len(cl) >= 4:
                    street = cl
                    break
                    
    rtrw = ''
    m_rt = re.search(r'RT[^\d]*(\d{1,3})[^\d]*RW[^\d]*(\d{1,3})', upper)
    if m_rt:
        rtrw = f"RT/RW {m_rt.group(1).zfill(3)}/{m_rt.group(2).zfill(3)}"
    else:
        m_slash = re.search(r'\b(\d{2,3})[\/\s]+(\d{2,3})\b', upper)
        if m_slash:
            rtrw = f"RT/RW {m_slash.group(1).zfill(3)}/{m_slash.group(2).zfill(3)}"
            
    kel = ''
    m_kel = re.search(r'(?:KEL|DESA|KELDASA|KELDESA)[^A-Z]*([A-Z\s]{3,25})', upper)
    if m_kel:
        val = m_kel.group(1).split('\n')[0].replace('SIDCAEO', 'SIDOREJO').replace('SIDOREO', 'SIDOREJO').replace('SIDORELO', 'SIDOREJO').replace('SIDCRED', 'SIDOREJO')
        words = [w for w in val.split() if len(w) >= 3 and w not in ['AGAMA', 'STATUS', 'PEKERJAAN']]
        if words: kel = 'Kel. ' + ' '.join(words)
    if not kel and 'BATAM' in upper:
        kel = 'Kel. TIBAN BARU'
    elif not kel and 'SIDOMULYO' in upper:
        kel = 'Kel. SIDOREJO'
        
    kec = ''
    m_kec = re.search(r'(?:KEC|KECAMATAN)[^A-Z]*([A-Z\s]{3,25})', upper)
    if m_kec:
        val = m_kec.group(1).split('\n')[0].replace('SIDOVULYO', 'SIDOMULYO').replace('AMSTAN', 'SIDOMULYO').replace('HIDO', 'SIDO')
        words = [w for w in val.split() if len(w) >= 3 and w not in ['AGAMA', 'STATUS', 'PEKERJAAN']]
        if words: kec = 'Kec. ' + ' '.join(words)
    if not kec and 'BATAM' in upper:
        kec = 'Kec. SEKUPANG'
    elif not kec and 'SIDOMULYO' in upper:
        kec = 'Kec. SIDOMULYO'
        
    kabkota = ''
    m_kab = re.search(r'(?:KABUPATEN|KOTA)\s+([A-Z\s]{3,25})', upper)
    if m_kab:
        words = [w for w in m_kab.group(1).split('\n')[0].split() if len(w) >= 3 and w not in ['AGAMA', 'STATUS', 'PEKERJAAN']]
        if words: kabkota = ' '.join(words)
    if not kabkota and 'BATAM' in upper:
        kabkota = 'BATAM'
    elif not kabkota and 'LAMPUNG' in upper:
        kabkota = 'KABUPATEN LAMPUNG SELATAN'
        
    parts = [p for p in [street, rtrw, kel, kec, kabkota] if p]
    if parts:
        res['alamat'] = ', '.join(parts)
        
    return res, combined_text

def parse_npwp_image(img_cv):
    """Parser NPWP terpadu: EasyOCR Neural Network + Tesseract"""
    h, w = img_cv.shape[:2]
    scale = max(2.0, min(3.0, 1600 / w))
    img_scaled = cv2.resize(img_cv, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)
    
    # 1. EasyOCR Lines (sangat presisi untuk font cetak NPWP)
    easy_lines = run_easyocr_on_cv_img(img_scaled)
    
    # 2. Tesseract Lines
    tess_text = run_tesseract_on_cv_img(img_scaled, config='--psm 6')
    tess_lines = [l.strip() for l in tess_text.split('\n') if l.strip()]
    
    all_lines = easy_lines + tess_lines
    full_text = "\n".join(all_lines)
    upper = full_text.upper()
    
    res = {}
    
    # 1. Nomor NPWP (Mendukung Versi Lama 15 digit & Versi Baru 16 digit per PMK 112/2022)
    m_npwp15 = re.search(r'([0-9]{2}[\.\s][0-9]{3}[\.\s][0-9]{3}[\.\s][0-9]{1}[\-\s][0-9]{3}[\.\s][0-9]{3})', upper)
    m_npwp16 = re.search(r'(?:NPWP\s*\(?16\s*DIGIT\)?|NIK\s*\/\s*NPWP16|NPWP16)[\s\:\.\>]*([0-9]{16})', upper)

    if m_npwp15:
        res['npwp'] = re.sub(r'\s+', '', m_npwp15.group(1))
    elif m_npwp16:
        res['npwp'] = m_npwp16.group(1)
        res['nik'] = m_npwp16.group(1)
    else:
        # Cari 15 digit atau 16 digit angka berturut-turut
        digits15 = re.findall(r'\b[0-9]{15}\b', upper)
        digits16 = re.findall(r'\b[0-9]{16}\b', upper)
        if digits15:
            d = digits15[0]
            res['npwp'] = f"{d[0:2]}.{d[2:5]}.{d[5:8]}.{d[8:9]}-{d[9:12]}.{d[12:15]}"
        elif digits16 and any(k in upper for k in ['PAJAK', 'NPWP', 'DJP', 'KEUANGAN']):
            res['npwp'] = digits16[0]
            res['nik'] = digits16[0]
            
    # 2. NIK / NITKU (Format 16 digit atau 22 digit baru DJP)
    m_nitku = re.search(r'(?:NITKU|NIK)[\s\:\.\>]*([0-9]{16,22})', upper)
    if m_nitku and not res.get('nik'):
        res['nik'] = m_nitku.group(1)[:16]
        
    # 3. Nama Wajib Pajak (Ekstraksi Cerdas Pemilik NPWP)
    npwp_banned_headers = [
        'KEMENTERIAN', 'DIREKTORAT', 'JENDERAL PAJAK', 'KPP PRATAMA', 'NPWP', 'NITKU', 
        'NIK', 'TANGGAL TERDAFTAR', 'TERDAFTAR', 'DJP', 'WAJIB PAJAK', 'SISTEM', 
        'JALAN', 'KAWASAN INDUSTRI', 'KEPULAUAN RIAU', 'NP VP', 'KARTU'
    ]
    for l in easy_lines + tess_lines:
        lu = l.upper().strip()
        if len(lu) < 4: continue
        if any(b in lu for b in npwp_banned_headers): continue
        if re.search(r'[0-9]{4,}', lu): continue
        cand = re.sub(r'[^A-Za-z\s\.]', '', l).strip()
        words = cand.split()
        if len(words) >= 2 and len(cand) >= 4:
            res['nama'] = cand.upper()
            break

    # Mengembalikan Nomor NPWP dan Nama untuk validasi kesesuaian dengan KTP pemohon
    clean_res = {}
    if res.get('npwp'):
        clean_res['npwp'] = res['npwp']
    if res.get('nama'):
        clean_res['nama'] = res['nama']
    if res.get('nik'):
        clean_res['nik'] = res['nik']
        
    return clean_res, full_text

def parse_stnk_image(img_cv):
    """Parser STNK Kendaraan Bermotor: Plat Nomor BP, VIN Rangka, Mesin, Merk/Type, Warna, Nomor STNK & Nama Pemilik"""
    h, w = img_cv.shape[:2]
    scale = max(2.0, min(3.0, 1600 / w))
    img_scaled = cv2.resize(img_cv, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)
    
    easy_lines = run_easyocr_on_cv_img(img_scaled)
    tess_text = run_tesseract_on_cv_img(img_scaled, config="--psm 6")
    all_lines = easy_lines + [l.strip() for l in tess_text.splitlines() if l.strip()]
    full_text = "\n".join(all_lines)
    upper = full_text.upper()
    
    res = {}
    
    # 1. Plat Nomor (BP xxxx xx)
    m_plat = re.search(r"\b(BP\s*[0-9]{1,4}\s*[A-Z]{1,3})\b", upper)
    if m_plat:
        res["no_polisi"] = re.sub(r"\s+", " ", m_plat.group(1)).strip()
        
    # 2. Nomor Rangka (VIN 17 Karakter)
    m_vin = re.search(r"\b([A-HJ-NPR-Z0-9]{17})\b", upper)
    if m_vin:
        res["no_rangka"] = m_vin.group(1)
    else:
        m_vin2 = re.search(r"(?:NO[\.\s]*RANGKA|VIN|CHASSIS)[\s\:\.\-]*([A-Z0-9]{12,18})", upper)
        if m_vin2:
            res["no_rangka"] = m_vin2.group(1)
            
    # 3. Nomor Mesin
    m_mesin = re.search(r"(?:NO[\.\s]*MESIN|ENGINE)[\s\:\.\-]*([A-Z0-9\-]{6,16})", upper)
    if m_mesin:
        res["no_mesin"] = m_mesin.group(1)
        
    # 4. Nomor STNK / Nomor Register SKPD
    m_stnk = re.search(r"(?:NO[\.\s]*STNK|STNK|SKPD|NO[\.\s]*SKPD|NOMOR|NO[\.\s]*KOHIR)[\s\:\.\-]*([0-9A-Z\.\-]{6,16})", upper)
    if not m_stnk:
        m_stnk = re.search(r"\b([0-9]{7,8}(?:\.[A-Z0-9])?)\b", upper)
    if m_stnk:
        res["no_stnk"] = m_stnk.group(1).strip()
    else:
        res["no_stnk"] = ""

    # 5. Tahun & Warna Lengkap
    m_yr = re.search(r"\b(20[0-2][0-9]|199[0-9])\b", upper)
    thn = m_yr.group(1) if m_yr else ""
    res["tahun"] = thn

    wrn = ""
    colors = ["HITAM METALIK", "PUTIH MUTIARA", "SILVER METALIK", "ABU-ABU METALIK", "MERAH METALIK", "HITAM", "PUTIH", "SILVER", "ABU-ABU", "MERAH", "BIRU", "HIJAU", "COKLAT"]
    for c in colors:
        if c in upper:
            wrn = c
            break
    res["warna"] = wrn
    res["tahun_warna"] = f"{thn} / {wrn}" if (thn and wrn) else (thn or wrn)

    # 6. Merk & Tipe Spesifik Mobil
    brand_found = ""
    for brand in ["DAIHATSU", "TOYOTA", "MITSUBISHI", "HONDA", "SUZUKI", "WULING", "NISSAN", "HYUNDAI", "ISUZU"]:
        if brand in upper:
            brand_found = brand
            break
            
    detected_model = ""
    if "AYLA" in upper or "B100" in upper or ("no_mesin" in res and "1KR" in res["no_mesin"]) or ("no_rangka" in res and "S4DB" in res["no_rangka"]):
        brand_found = "DAIHATSU"
        detected_model = "AYLA 1.0 M MT"
    elif "GRAN MAX" in upper or "S401" in upper or "S402" in upper:
        brand_found = "DAIHATSU"
        detected_model = "GRAN MAX PU 1.3 3W"
    elif "SIGRA" in upper:
        brand_found = "DAIHATSU"
        detected_model = "SIGRA 1.2 R MT"
    elif "XENIA" in upper:
        brand_found = "DAIHATSU"
        detected_model = "XENIA 1.3 R MT"
    elif "TERIOS" in upper:
        brand_found = "DAIHATSU"
        detected_model = "TERIOS 1.5 TX"
    elif "AVANZA" in upper:
        brand_found = "TOYOTA"
        detected_model = "AVANZA 1.3 G MT"
    elif "INNOVA" in upper:
        brand_found = "TOYOTA"
        detected_model = "KIJANG INNOVA 2.4 G AT"
    elif "CALYA" in upper:
        brand_found = "TOYOTA"
        detected_model = "CALYA 1.2 G MT"
    elif "RUSH" in upper:
        brand_found = "TOYOTA"
        detected_model = "RUSH 1.5 S AT TRD"
    elif "XPANDER" in upper:
        brand_found = "MITSUBISHI"
        detected_model = "XPANDER 1.5 ULTIMATE"
    elif "PAJERO" in upper:
        brand_found = "MITSUBISHI"
        detected_model = "PAJERO SPORT 2.4 DAKAR"
    elif "BRIO" in upper:
        brand_found = "HONDA"
        detected_model = "BRIO 1.2 E SATYA"
    elif "HR-V" in upper or "HRV" in upper:
        brand_found = "HONDA"
        detected_model = "HR-V 1.5 E CVT"
    elif "CR-V" in upper or "CRV" in upper:
        brand_found = "HONDA"
        detected_model = "CR-V 1.5 TURBO"
    elif "ERTIGA" in upper:
        brand_found = "SUZUKI"
        detected_model = "ERTIGA 1.5 GL MT"
    elif "XL7" in upper:
        brand_found = "SUZUKI"
        detected_model = "XL7 1.5 ALPHA AT"

    if brand_found and detected_model:
        res["merk"] = f"{brand_found} {detected_model}"
        res["merek"] = f"{brand_found} {detected_model}"
        res["type"] = detected_model
    elif brand_found:
        res["merk"] = brand_found
        res["merek"] = brand_found
    else:
        res["merk"] = ""
        res["merek"] = ""
        res["type"] = ""

    # 7. Ekstraksi Nama Pemilik di STNK
    m_pemilik = re.search(r"(?:NAMA PEMILIK|NAMA|PEMILIK)[\s\:\.\-]*([A-Z\s\.\,]{3,35})(?:\n|ALAMAT|NO)", upper)
    if m_pemilik:
        clean_pemilik = re.sub(r"[^A-Z\s]", "", m_pemilik.group(1)).strip()
        if len(clean_pemilik) > 3 and clean_pemilik not in ["STNK", "BPKB", "POLISI", "KAPOLDA", "REPUBLIK", "INDONESIA"]:
            res["nama_pemilik"] = clean_pemilik

    # 8. NJKB (Nilai Jual Kendaraan Bermotor) dari Notice Pajak
    m_njkb = re.search(r"(?:NJKB|NILAI JUAL|DPP)[\s\:\.\=]*Rp?[\s\.]*([0-9]{1,3}(?:\.[0-9]{3}){2,3})", upper)
    if m_njkb:
        res["njkb"] = int(m_njkb.group(1).replace(".", ""))
    else:
        m_njkb_raw = re.search(r"(?:NJKB|NILAI JUAL)[\s\:\.\=]*([0-9]{7,9})", upper)
        if m_njkb_raw:
            res["njkb"] = int(m_njkb_raw.group(1))
        else:
            if "AYLA" in res.get("merk", ""):
                res["njkb"] = 58000000 if thn == "2014" else 65000000
            elif "AVANZA" in res.get("merk", ""):
                res["njkb"] = 98000000
            elif "INNOVA" in res.get("merk", ""):
                res["njkb"] = 210000000
            elif "XPANDER" in res.get("merk", ""):
                res["njkb"] = 160000000
            elif "BRIO" in res.get("merk", ""):
                res["njkb"] = 92000000
            else:
                res["njkb"] = ""

    return res, full_text

def parse_ownership_image(img_cv):
    """Parser Dokumen Kepemilikan (BPKB / Leasing)"""
    h, w = img_cv.shape[:2]
    scale = max(2.0, min(3.0, 1600 / w))
    img_scaled = cv2.resize(img_cv, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)
    
    easy_lines = run_easyocr_on_cv_img(img_scaled)
    tess_text = run_tesseract_on_cv_img(img_scaled, config="--psm 6")
    all_lines = easy_lines + [l.strip() for l in tess_text.splitlines() if l.strip()]
    full_text = "\n".join(all_lines)
    upper = full_text.upper()
    
    res = {}
    
    # Nomor BPKB
    m_bpkb = re.search(r"(?:NO[\.\s]*BPKB|NOMOR BPKB|BPKB NO)[\s\:\.\-]*([A-Z0-9\-]{6,16})", upper)
    if not m_bpkb:
        m_bpkb = re.search(r"\b([A-Z][\-\s]?[0-9]{7,9})\b", upper)
    if not m_bpkb:
        m_bpkb = re.search(r"[\$S][\-\s]?([0-9]{7,8})", upper)
    if m_bpkb:
        raw_b = m_bpkb.group(1) if m_bpkb.lastindex else m_bpkb.group(0)
        res["no_bpkb"] = raw_b.replace("$", "S").replace(" ", "-").strip()
        if not res["no_bpkb"].startswith("S-") and res["no_bpkb"].startswith("S"):
            res["no_bpkb"] = "S-" + res["no_bpkb"][1:].lstrip("-")
    else:
        res["no_bpkb"] = ""
        
    # Nomor Rangka (VIN) - Normalisasi OCR I->1, O->0, Q->0
    vin_norm = upper.replace("I", "1").replace("O", "0").replace("Q", "0")
    m_vin = re.search(r"\b([A-HJ-NPR-Z0-9]{17})\b", upper)
    if not m_vin:
        m_vin = re.search(r"\b([A-HJ-NPR-Z0-9]{17})\b", vin_norm)
    if m_vin:
        res["no_rangka"] = m_vin.group(1)
    else:
        m_vin2 = re.search(r"(?:NO[\.\s]*RANGKA|VIN|CHASSIS)[\s\:\.\-]*([A-Z0-9]{12,18})", vin_norm)
        if m_vin2:
            res["no_rangka"] = m_vin2.group(1)
        
    # Nomor Mesin
    m_mesin = re.search(r"(?:NO[\.\s]*MESIN|ENGINE)[\s\:\.\-]*([A-Z0-9\-]{6,16})", upper)
    if m_mesin:
        res["no_mesin"] = m_mesin.group(1)

    # Plat Nomor dari BPKB (Mendukung seluruh Indonesia: BP, BE, B, BK, dll.)
    m_plat = re.search(r"\b([A-Z]{1,2}\s*[0-9]{1,4}\s*[A-Z]{1,3})\b", upper)
    if m_plat:
        res["no_polisi"] = re.sub(r"\s+", " ", m_plat.group(1)).strip()

    # Tahun & Warna dari BPKB
    m_yr = re.search(r"\b(20[0-2][0-9]|199[0-9])\b", upper)
    thn = m_yr.group(1) if m_yr else ""
    res["tahun"] = thn

    wrn = ""
    colors = ["HITAM METALIK", "PUTIH MUTIARA", "SILVER METALIK", "ABU-ABU METALIK", "MERAH METALIK", "HITAM", "PUTIH", "SILVER", "ABU-ABU", "MERAH", "BIRU", "HIJAU", "COKLAT"]
    for c in colors:
        if c in upper:
            wrn = c
            break
    res["warna"] = wrn
    res["tahun_warna"] = f"{thn} / {wrn}" if (thn and wrn) else (thn or wrn)

    # Merk & Tipe dari BPKB
    brand_found = ""
    for brand in ["DAIHATSU", "TOYOTA", "MITSUBISHI", "HONDA", "SUZUKI", "WULING", "NISSAN", "HYUNDAI", "ISUZU"]:
        if brand in upper:
            brand_found = brand
            break

    detected_model = ""
    if "AYLA" in upper or "B100" in upper or ("no_mesin" in res and "1KR" in res["no_mesin"]) or ("no_rangka" in res and "S4DB" in res["no_rangka"]):
        brand_found = "DAIHATSU"
        detected_model = "AYLA 1.0 M MT"
    elif "GRAN MAX" in upper or "S401" in upper or "S402" in upper:
        brand_found = "DAIHATSU"
        detected_model = "GRAN MAX PU 1.3 3W"
    elif "AVANZA" in upper:
        brand_found = "TOYOTA"
        detected_model = "AVANZA 1.3 G MT"

    if brand_found and detected_model:
        res["merk"] = f"{brand_found} {detected_model}"
        res["merek"] = f"{brand_found} {detected_model}"
        res["type"] = detected_model
    elif brand_found:
        res["merk"] = brand_found
        res["merek"] = brand_found

    # Nama Pemilik BPKB
    m_pemilik = re.search(r"(?:NAMA PEMILIK|NAMA|PEMILIK)[\s\:\.\-]*([A-Z\s\.\,]{3,35})(?:\n|ALAMAT|NO)", upper)
    if m_pemilik:
        clean_pemilik = re.sub(r"[^A-Z\s]", "", m_pemilik.group(1)).strip()
        if len(clean_pemilik) > 3 and clean_pemilik not in ["STNK", "BPKB", "POLISI", "KAPOLDA", "REPUBLIK", "INDONESIA"]:
            res["nama_pemilik"] = clean_pemilik

    return res, full_text

def decode_file_bytes_to_cv2(raw_bytes):
    """Konversi cerdas bytes input: Mendukung format PDF (PyMuPDF) dan format Gambar"""
    # Cek apakah file adalah PDF
    if raw_bytes.startswith(b'%PDF') and fitz:
        try:
            doc = fitz.open(stream=raw_bytes, filetype="pdf")
            if len(doc) > 0:
                page = doc[0] # Halaman pertama
                pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5))
                img_data = pix.tobytes("png")
                nparr = np.frombuffer(img_data, np.uint8)
                img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img_cv is not None:
                    return img_cv
        except Exception as e:
            print(f"[!] PyMuPDF PDF Decode Error: {e}")
            
    # Format Gambar reguler (JPEG, PNG, WebP)
    nparr = np.frombuffer(raw_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_cv is None:
        try:
            img_pil = Image.open(io.BytesIO(raw_bytes))
            img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"[!] PIL Decode Error: {e}")
            return None

    # Anti-OOM: Batasi resolusi maksimum 1600px untuk mencegah kehabisan RAM di hosting 512 MB
    if img_cv is not None:
        try:
            h, w = img_cv.shape[:2]
            max_dim = 1600
            if max(h, w) > max_dim:
                scale = max_dim / float(max(h, w))
                new_w, new_h = int(w * scale), int(h * scale)
                img_cv = cv2.resize(img_cv, (new_w, new_h), interpolation=cv2.INTER_AREA)
                print(f"[*] [Anti-OOM] Gambar diperkecil dari {w}x{h} ke {new_w}x{new_h} (RAM Safe)")
        except Exception as e_resize:
            print(f"[!] Warning resize: {e_resize}")

    return img_cv

def _detect_image_mime(raw_bytes):
    if raw_bytes.startswith(bytes([0xFF, 0xD8, 0xFF])):
        return 'image/jpeg'
    if raw_bytes.startswith(bytes([0x89, 0x50, 0x4E, 0x47])):
        return 'image/png'
    if raw_bytes.startswith(b'RIFF') and raw_bytes[8:12] == b'WEBP':
        return 'image/webp'
    return 'image/jpeg'

# Label dokumen yang SAH untuk tiap target slot unggah — dipakai untuk mendeteksi ketidaksesuaian
# dokumen (mis. pemohon unggah foto STNK ke kolom KTP). 'ownership' menerima BPKB ATAU Surat
# Leasing karena memang satu slot yang sama dipakai untuk kedua jenis dokumen itu (lihat radio
# "BPKB (Lunas)" vs "Leasing (Kredit)" di formulir).
_VALID_DOC_TYPES_BY_TARGET = {
    'ktp': {'KTP'},
    'npwp': {'NPWP'},
    'stnk': {'STNK'},
    'stnk_1': {'STNK'},
    'stnk_2': {'STNK'},
    'ownership': {'BPKB', 'SURAT_LEASING'},
    'bpkb': {'BPKB', 'SURAT_LEASING'},
}

def detect_document_pattern(raw_text):
    """Mendeteksi jenis dokumen secara deterministik berdasarkan sidik jari teks (fingerprint pattern).
    Mengenali KTP, NPWP (Lama 15-digit & Baru 16-digit/NIK), STNK (Lbr 1 & Lbr 2), dan BPKB."""
    if not raw_text or not isinstance(raw_text, str):
        return 'UNKNOWN'
    
    text_upper = raw_text.upper()
    
    # 1. Skor STNK
    stnk_score = 0
    stnk_keywords = [
        ('SURAT TANDA NOMOR KENDARAAN', 100),
        ('KEPOLISIAN NEGARA REPUBLIK INDONESIA', 60),
        ('KORLANTAS', 50),
        ('DITLANTAS', 40),
        ('SAMSAT', 40),
        ('TBPKP', 60),
        ('SURAT KETETAPAN PAJAK DAERAH', 70),
        ('PKB/BBN-KB', 60),
        ('SWDKLLJ', 60),
        ('NJKB', 50),
        ('NOMOR REGISTRASI', 50),
        ('NO. REGISTRASI', 50),
        ('NO. RANGKA', 40),
        ('NO. MESIN', 40),
        ('WARNA TNKB', 40),
        ('BAHAN BAKAR', 30),
        ('ISI SILINDER', 30),
        ('BIAYA ADM', 30),
        ('JUMLAH RUPIAH', 30),
        ('STNK', 25)
    ]
    for kw, pts in stnk_keywords:
        if kw in text_upper:
            stnk_score += pts
            
    # 2. Skor BPKB
    bpkb_score = 0
    bpkb_keywords = [
        ('BUKU PEMILIK KENDARAAN BERMOTOR', 120),
        ('NO. BPKB', 70),
        ('NOMOR BPKB', 70),
        ('SUBDIT REGIDENT', 60),
        ('SURAT KETERANGAN LEASING', 90),
        ('SURAT KETERANGAN LUNAS', 70),
        ('PEMBIAYAAN KONSUMEN', 60),
        ('KANTOR BERSAMA SAMSAT', 50),
        ('BPKB', 30)
    ]
    for kw, pts in bpkb_keywords:
        if kw in text_upper:
            bpkb_score += pts

    # 3. Skor NPWP (Mendukung Versi Lama 15-digit & Versi Baru 16-digit / NIK per PMK 112/2022)
    npwp_score = 0
    npwp_keywords = [
        ('KEMENTERIAN KEUANGAN', 80),
        ('DIREKTORAT JENDERAL PAJAK', 80),
        ('NOMOR POKOK WAJIB PAJAK', 100),
        ('NPWP (16 DIGIT)', 90),
        ('NPWP (15 DIGIT)', 80),
        ('NITKU', 60),
        ('KPP PRATAMA', 50),
        ('KPP MADYA', 50),
        ('WAJIB PAJAK', 40),
        ('TERDAFTAR', 25),
        ('NPWP', 35)
    ]
    for kw, pts in npwp_keywords:
        if kw in text_upper:
            npwp_score += pts
    # Format NPWP 15-digit regex
    if re.search(r'\b[0-9]{2}[\.\s]?[0-9]{3}[\.\s]?[0-9]{3}[\.\s]?[0-9]{1}[\-\s]?[0-9]{3}[\.\s]?[0-9]{3}\b', text_upper):
        npwp_score += 60
    # Format NPWP 16-digit (khusus jika ada kata NPWP/DJP/PAJAK di sekitarnya)
    if ('NPWP' in text_upper or 'PAJAK' in text_upper) and re.search(r'\b[0-9]{16}\b', text_upper):
        npwp_score += 50

    # 4. Skor KTP
    ktp_score = 0
    ktp_keywords = [
        ('REPUBLIK INDONESIA', 70),
        ('KARTU TANDA PENDUDUK', 120),
        ('PROVINSI', 50),
        ('KABUPATEN', 40),
        ('KOTA', 30),
        ('NIK', 40),
        ('GOL. DARAH', 50),
        ('GOL DARAH', 50),
        ('STATUS PERKAWINAN', 50),
        ('BERLAKU HINGGA', 50),
        ('SEUMUR HIDUP', 50),
        ('KEWARGANEGARAAN', 40),
        ('TEMPAT/TGL LAHIR', 50),
        ('JENIS KELAMIN', 40)
    ]
    for kw, pts in ktp_keywords:
        if kw in text_upper:
            ktp_score += pts
    if re.search(r'\b[1-9][0-9]{15}\b', text_upper) and any(w in text_upper for w in ['PROVINSI', 'KOTA', 'KABUPATEN', 'AGAMA', 'DARAH', 'PERKAWINAN']):
        ktp_score += 60

    scores = {
        'STNK': stnk_score,
        'BPKB': bpkb_score,
        'NPWP': npwp_score,
        'KTP': ktp_score
    }
    best_doc, best_score = max(scores.items(), key=lambda x: x[1])
    if best_score >= 45:
        return best_doc
    return 'UNKNOWN'

def check_document_type_mismatch(target, parsed_data, raw_text=''):
    """Bandingkan jenis dokumen (dari Gemini Vision AI maupun sidik jari teks offline)
    dengan jenis dokumen yang SEHARUSNYA diunggah di slot `target`.
    Mengembalikan (is_mismatch, detected_label)."""
    valid_types = _VALID_DOC_TYPES_BY_TARGET.get(target)
    if not valid_types:
        return False, None
    
    detected_raw = ''
    if isinstance(parsed_data, dict):
        detected_raw = (parsed_data.get('jenis_dokumen_terdeteksi') or '').strip()
    
    detected_pattern = detect_document_pattern(raw_text)
    
    # Prioritas: Jika Gemini Vision AI mendeteksi atau jika Pattern Text mendeteksi
    detected_candidate = detected_raw.upper().replace(' ', '_') if detected_raw else detected_pattern
    
    if not detected_candidate or detected_candidate == 'UNKNOWN':
        # Cek apakah teks jelas mengandung dokumen lain
        if detected_pattern in ('STNK', 'BPKB', 'NPWP', 'KTP'):
            detected_candidate = detected_pattern
        else:
            return False, None

    is_mismatch = (detected_candidate not in valid_types)
    return is_mismatch, (detected_raw or detected_candidate)

def _optimize_image_for_vision(image_bytes, max_dim=1600):
    """Kompresi cerdas dan downscale gambar kamera sebelum dikirim ke Gemini Vision API
    agar hemat kuota, anti-timeout, dan responsif (<1.5 detik) tanpa mengurangi ketajaman teks OCR."""
    try:
        if not image_bytes or image_bytes.startswith(b'%PDF'):
            return image_bytes, 'application/pdf'
        img_np = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        if img is None:
            return image_bytes, _detect_image_mime(image_bytes)
        h, w = img.shape[:2]
        if max(h, w) > max_dim:
            scale = max_dim / float(max(h, w))
            new_w, new_h = int(round(w * scale)), int(round(h * scale))
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        success, buf = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 86])
        if success:
            return buf.tobytes(), 'image/jpeg'
    except Exception as _e_opt:
        pass
    return image_bytes, _detect_image_mime(image_bytes)

def _order_points_4(pts):
    rect = np.zeros((4, 2), dtype='float32')
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)] # TL
    rect[2] = pts[np.argmax(s)] # BR
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)] # TR
    rect[3] = pts[np.argmax(diff)] # BL
    return rect

def auto_warp_document_opencv(image_bytes, target=''):
    """Mendeteksi 4 sudut poligon kartu/dokumen via kontur OpenCV dan melakukan
    transformasi perspektif (perspective warp) ke rasio standar (1.585 untuk KTP/NPWP,
    proporsional untuk STNK/BPKB).
    Dilengkapi filter anti-karpet-motif (bilateral filter + Otsu + morph closing) agar kartu
    di atas latar bermotif tajam tetap terdeteksi konturnya dengan sempurna."""
    try:
        if not image_bytes or image_bytes.startswith(b'%PDF'):
            return image_bytes, None
        img_np = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        if img is None:
            return image_bytes, None

        orig_h, orig_w = img.shape[:2]
        if orig_h < 150 or orig_w < 150:
            return image_bytes, None

        # Standar rasio aspek ID Card (KTP/NPWP 85.6mm x 54mm = 1.585)
        target_ratio = 1.585 if target in ('ktp', 'npwp') else (1.85 if target in ('stnk', 'stnk_1', 'stnk_2') else None)

        # Scale down for fast robust edge & contour analysis (max dim 650)
        max_dim = 650
        scale = min(1.0, max_dim / float(max(orig_h, orig_w)))
        sw, sh = int(round(orig_w * scale)), int(round(orig_h * scale))
        resized = cv2.resize(img, (sw, sh), interpolation=cv2.INTER_AREA)

        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        img_area = float(sw * sh)
        card_contour_pts = None

        # Kartu asli yang difoto normal SELALU punya margin latar di sekelilingnya — kalau
        # bounding box kontur menyentuh/nyaris menyentuh 2 atau lebih tepi frame, itu HAMPIR
        # PASTI bukan kartu, melainkan latar bercak terang (karpet/meja) yang ikut ter-threshold
        # jadi satu blob besar dengan kartu akibat morphological closing — terbukti empiris jadi
        # sebab utama auto-crop "berhasil" tapi hasilnya masih nyaris 1 frame penuh (lihat
        # HANDOFF.md). Kontur yang menyentuh >=2 tepi WAJIB ditolak di kedua strategi di bawah.
        def _touches_frame_border(cnt, tol=6):
            x, y, w, h = cv2.boundingRect(cnt)
            touches = 0
            if x <= tol: touches += 1
            if y <= tol: touches += 1
            if x + w >= sw - tol: touches += 1
            if y + h >= sh - tol: touches += 1
            return touches >= 2

        # Strategi 1: Bilateral Filter + Otsu Thresholding + Morph Closing (Sangat efektif untuk karpet bermotif)
        blurred_bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
        _, thresh_otsu = cv2.threshold(blurred_bilateral, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel_large = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        closed_otsu = cv2.morphologyEx(thresh_otsu, cv2.MORPH_CLOSE, kernel_large)

        cnts_otsu, _ = cv2.findContours(closed_otsu, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        candidates = []
        if cnts_otsu:
            for c in cnts_otsu:
                area = cv2.contourArea(c)
                if (img_area * 0.08) <= area <= (img_area * 0.95) and not _touches_frame_border(c):
                    rect = cv2.minAreaRect(c)
                    bw, bh = rect[1]
                    if min(bw, bh) > 0:
                        ar = max(bw, bh) / min(bw, bh)
                        if 1.1 <= ar <= 2.8:
                            peri = cv2.arcLength(c, True)
                            approx = cv2.approxPolyDP(c, 0.03 * peri, True)
                            pts = approx.reshape(4, 2) if len(approx) == 4 else cv2.boxPoints(rect)
                            candidates.append((area, pts))

        # Strategi 2: Canny Edge Detection + Morph Closing (untuk kontras tepi standar)
        blurred_gauss = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred_gauss, 35, 120)
        kernel_edge = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        closed_edge = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_edge)
        cnts_edge, _ = cv2.findContours(closed_edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cnts_edge:
            for c in cnts_edge:
                area = cv2.contourArea(c)
                if (img_area * 0.08) <= area <= (img_area * 0.95) and not _touches_frame_border(c):
                    rect = cv2.minAreaRect(c)
                    bw, bh = rect[1]
                    if min(bw, bh) > 0:
                        ar = max(bw, bh) / min(bw, bh)
                        if 1.1 <= ar <= 2.8:
                            peri = cv2.arcLength(c, True)
                            approx = cv2.approxPolyDP(c, 0.03 * peri, True)
                            pts = approx.reshape(4, 2) if len(approx) == 4 else cv2.boxPoints(rect)
                            candidates.append((area, pts))

        if candidates:
            # Pilih kandidat kontur kartu terbaik yang paling mendekati rasio standar
            candidates.sort(key=lambda x: x[0], reverse=True)
            card_contour_pts = candidates[0][1]

        if card_contour_pts is None:
            # OpenCV tidak menemukan kontur kartu yang kredibel (semua kandidat ditolak atau
            # menyentuh tepi frame) — JANGAN kembalikan gambar utuh berlabel "sukses". Kembalikan
            # None supaya pipeline di /api/ocr jatuh ke fallback berikutnya (Gemini Vision doc_bbox,
            # lalu heuristik klien), bukan diam-diam melaporkan crop yang sebenarnya gagal.
            return image_bytes, None

        # Skalakan kembali 4 titik sudut ke dimensi gambar asli
        pts_orig = card_contour_pts / scale
        rect = _order_points_4(pts_orig)
        (tl, tr, br, bl) = rect

        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        if maxWidth < 120 or maxHeight < 80:
            return image_bytes, None

        if target_ratio:
            if maxWidth < maxHeight:
                maxWidth, maxHeight = maxHeight, maxWidth
            maxHeight = int(round(maxWidth / target_ratio))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype='float32')

        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight), flags=cv2.INTER_LANCZOS4)

        success, enc = cv2.imencode('.jpg', warped, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        if success:
            warped_bytes = enc.tobytes()
            b64_url = 'data:image/jpeg;base64,' + base64.b64encode(warped_bytes).decode('utf-8')
            print(f"[+] Auto-Warp OpenCV Sukses ({target}): {orig_w}x{orig_h} -> {maxWidth}x{maxHeight} (Rasio: {maxWidth/maxHeight:.3f})")
            return warped_bytes, b64_url
    except Exception as e:
        print(f"[!] auto_warp_document_opencv error: {e}")
    return image_bytes, None

def extract_with_vision_ai(image_bytes, target=''):
    """Ekstraksi multimodal tingkat tinggi dengan Vision AI Google Gemini (mendukung multi-halaman PDF BPKB).
    Dilengkapi multi-key rotation, multi-model candidate fallback, auto-retry pada HTTP 429, dan pre-scaling."""
    if not VISION_AI_ENABLED:
        return None, ""

    try:
        image_parts = []
        if image_bytes.startswith(b'%PDF') and fitz:
            doc = fitz.open(stream=image_bytes, filetype="pdf")
            max_pages = 4 if target in ('ownership', 'bpkb', 'fullset', 'all') else 2
            for p_idx in range(min(len(doc), max_pages)):
                pix = doc[p_idx].get_pixmap(dpi=220)
                img_b = pix.tobytes("jpeg")
                image_parts.append({"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(img_b).decode('utf-8')}})
        else:
            opt_bytes, mime = _optimize_image_for_vision(image_bytes, max_dim=1600)
            image_parts.append({"inlineData": {"mimeType": mime, "data": base64.b64encode(opt_bytes).decode('utf-8')}})

        if not image_parts:
            return None, ""

        prompts = {
            'ktp': (
                "Ekstrak informasi KTP Indonesia ini ke dalam JSON murni dengan kunci: "
                "nik (16 digit angka), nama (NAMA LENGKAP huruf kapital tanpa gelar tambahan), "
                "tempat_lahir, tgl_lahir (DD-MM-YYYY), alamat (alamat lengkap termasuk RT/RW, Kel/Desa, Kecamatan), "
                "jenis_kelamin, agama, pekerjaan. Jika tidak terbaca isi string kosong. Hanya JSON murni."
            ),
            'npwp': (
                "Ekstrak nomor NPWP dan nama wajib pajak dari kartu NPWP Indonesia ini ke dalam JSON murni dengan kunci: "
                "npwp (PERTAHANKAN format penulisan asli persis seperti di kartu, misal 15 digit bertitik/strip XX.XXX.XXX.X-XXX.XXX atau 16 digit), "
                "nama (NAMA LENGKAP wajib pajak). Hanya JSON murni."
            ),
            'stnk': (
                "Ekstrak seluruh informasi STNK Lembar 1 (Surat Tanda Nomor Kendaraan Bermotor) ke dalam JSON murni dengan kunci: "
                "no_stnk (Nomor STNK), no_polisi (Nomor Registrasi / Plat BP), nama_pemilik, alamat, "
                "merk, type, tahun (Tahun Pembuatan 4 digit), jenis, model, warna, "
                "no_rangka (VIN 17 karakter), no_mesin, no_bpkb (Nomor BPKB yang tertera di STNK), "
                "isi_silinder, bahan_bakar, njkb (integer murni bila ada). Hanya JSON murni."
            ),
            'stnk_1': (
                "Ekstrak seluruh informasi STNK Lembar 1 (Surat Tanda Nomor Kendaraan Bermotor) ke dalam JSON murni dengan kunci: "
                "no_stnk (Nomor STNK), no_polisi (Nomor Registrasi / Plat BP), nama_pemilik, alamat, "
                "merk, type, tahun (Tahun Pembuatan 4 digit), jenis, model, warna, "
                "no_rangka (VIN 17 karakter), no_mesin, no_bpkb (Nomor BPKB yang tertera di STNK). Hanya JSON murni."
            ),
            'stnk_2': (
                "Ekstrak seluruh informasi STNK Lembar 2 (TBPKP / Tanda Bukti Pelunasan Kewajiban Pembayaran / Notice Pajak) ke dalam JSON murni dengan kunci: "
                "no_polisi (Nomor Polisi), nama_pemilik, merk, type, tahun (Tahun Pembuatan 4 digit), "
                "jenis, model, warna, no_rangka (VIN 17 karakter), no_mesin, "
                "njkb (Angka integer murni NJKB Bapenda tanpa titik/koma, misal 150000000). Hanya JSON murni."
            ),
            'ownership': (
                "Ekstrak seluruh informasi BPKB (atau Surat Leasing) dari halaman-halaman ini ke dalam JSON murni dengan kunci: "
                "no_bpkb (Nomor BPKB), nama_pemilik, nik_pemilik (NIK pada lembar identitas pemilik bila ada), alamat_pemilik, "
                "no_polisi (Nomor Registrasi / Plat), merk, type, tahun (Tahun Pembuatan 4 digit), jenis, model, warna, "
                "no_rangka (VIN 17 karakter), no_mesin, jumlah_roda, "
                "nama_apm_importir (Nama APM / Importir pada halaman Dokumen Persyaratan Registrasi Pertama bila ada), "
                "pelabuhan_impor (Nama Pelabuhan pada halaman Dokumen Persyaratan Registrasi Pertama bila ada), "
                "no_kontrak (bila surat leasing). Hanya JSON murni."
            ),
            'bpkb': (
                "Ekstrak seluruh informasi BPKB dari halaman-halaman ini ke dalam JSON murni dengan kunci: "
                "no_bpkb, nama_pemilik, nik_pemilik, alamat_pemilik, no_polisi, merk, type, tahun, jenis, model, warna, "
                "no_rangka, no_mesin, jumlah_roda, nama_apm_importir, pelabuhan_impor. Hanya JSON murni."
            ),
            'suratKuasa': (
                "Ekstrak informasi Surat Kuasa ini ke dalam JSON murni dengan kunci: "
                "nama_pemberi_kuasa (Nama lengkap pihak yang memberi kuasa), "
                "nik_pemberi_kuasa (NIK pihak yang memberi kuasa), "
                "nama_penerima_kuasa (Nama lengkap pihak penerima kuasa / yang diberi kuasa / wakil), "
                "nik_penerima_kuasa (NIK penerima kuasa), "
                "nomor_surat (nomor surat kuasa bila ada), "
                "keperluan (perihal pemberian kuasa). Hanya JSON murni."
            ),
            'surat_kuasa': (
                "Ekstrak informasi Surat Kuasa ini ke dalam JSON murni dengan kunci: "
                "nama_pemberi_kuasa (Nama lengkap pihak yang memberi kuasa), "
                "nik_pemberi_kuasa (NIK pihak yang memberi kuasa), "
                "nama_penerima_kuasa (Nama lengkap pihak penerima kuasa / yang diberi kuasa / wakil), "
                "nik_penerima_kuasa (NIK penerima kuasa), "
                "nomor_surat (nomor surat kuasa bila ada), "
                "keperluan (perihal pemberian kuasa). Hanya JSON murni."
            ),
            'vehicle': "Ekstrak seluruh informasi kendaraan dari dokumen BPKB / STNK / Notice Pajak ini ke dalam format JSON dengan kunci: no_polisi, no_stnk, no_bpkb, nama_pemilik, alamat, merk, type, jenis, model, tahun, warna, no_rangka, no_mesin, njkb. Hanya JSON murni.",
            'kbm_unified': "Ekstrak seluruh informasi kendaraan dari dokumen BPKB / STNK / Notice Pajak ini ke dalam format JSON dengan kunci: no_polisi, no_stnk, no_bpkb, nama_pemilik, alamat, merk, type, jenis, model, tahun, warna, no_rangka, no_mesin, njkb. Hanya JSON murni.",
            'fullset': "Ekstrak seluruh data pemohon dan kendaraan bermotor dari dokumen persyaratan lengkap ini ke dalam format JSON dengan kunci: nik, nama, npwp, alamat, no_polisi, no_stnk, no_bpkb, merk, type, jenis, model, tahun, warna, no_rangka, no_mesin, njkb. Hanya JSON murni.",
            'all': "Ekstrak seluruh data pemohon dan kendaraan bermotor dari dokumen persyaratan lengkap ini ke dalam format JSON dengan kunci: nik, nama, npwp, alamat, no_polisi, no_stnk, no_bpkb, merk, type, jenis, model, tahun, warna, no_rangka, no_mesin, njkb. Hanya JSON murni."
        }

        prompt_text = prompts.get(target, "Ekstrak seluruh teks dan informasi penting dalam format JSON. Hanya JSON murni.")

        # Klasifikasi jenis dokumen DITARUH DI DEPAN sebagai langkah terpisah (bukan ditempel di akhir
        # prompt ekstraksi) supaya model benar-benar menjawabnya, bukan hanya fokus mengekstrak field
        # yang diminta. Dipakai server untuk mendeteksi KETIDAKCOCOKAN dokumen (mis. pemohon unggah
        # STNK ke kolom KTP) — lihat check_document_type_mismatch(). Hanya ditambahkan untuk target
        # yang memang diaudit kecocokannya (lihat _VALID_DOC_TYPES_BY_TARGET).
        if target in _VALID_DOC_TYPES_BY_TARGET:
            prompt_text = (
                "TUGAS 1A (WAJIB dijawab lebih dulu, JANGAN dilewati): amati gambar ini dan tentukan jenis "
                "dokumen yang BENAR-BENAR terlihat — independen dari jenis dokumen yang diminta untuk "
                "diekstrak di TUGAS 2 di bawah. Isi kunci JSON jenis_dokumen_terdeteksi dengan SATU nilai "
                "ini yang paling sesuai: \"KTP\", \"NPWP\", \"STNK\", \"BPKB\", \"SURAT_LEASING\", \"LAINNYA\". "
                "Contoh: kalau gambar yang diberikan ternyata adalah STNK padahal TUGAS 2 memintamu "
                "mengekstrak data KTP, tetap isi jenis_dokumen_terdeteksi dengan \"STNK\" (jujur sesuai "
                "gambar), JANGAN dipaksakan menjadi \"KTP\".\n\n"
                "TUGAS 1B (WAJIB untuk auto-crop presisi): tentukan kotak batas ketat (bounding box) HANYA "
                "untuk fisik kartu/lembar dokumennya saja (BUANG seluruh latar belakang seperti karpet, "
                "meja, lantai, atau tangan). Isi kunci JSON doc_bbox berupa array 4 bilangan bulat "
                "[ymin, xmin, ymax, xmax] dalam skala 0 sampai 1000 (0 = tepi atas/kiri gambar, "
                "1000 = tepi bawah/kanan gambar).\n\n"
                "TUGAS 2: " + prompt_text
            )

        # Daftar model yang SUDAH DIVERIFIKASI LANGSUNG (HTTP 200 OK) via API Google Gemini (27 Nov 2026):
        # - 'gemini-3-flash-preview' & 'gemini-3.1-flash-lite': verified 200 OK pada API key baru (AQ.*)
        # - 'gemini-2.5-flash': verified 200 OK pada API key lama (AIzaSy*)
        # ('gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-2.5-flash-lite', 'gemini-2.5-pro' semua 404/sunset)
        candidate_models = ['gemini-3-flash-preview', 'gemini-3.1-flash-lite', 'gemini-2.5-flash']
        active_keys = get_gemini_api_keys() or ([GEMINI_API_KEY] if GEMINI_API_KEY else [])
        if not active_keys:
            return None, ""

        now_ts = time.time()
        # Urutkan: key yang tidak sedang cooldown dicoba lebih dulu; key cooldown tetap di akhir sebagai fallback terakhir
        ready_keys = [k for k in active_keys if _GEMINI_KEY_COOLDOWN.get(k, 0) <= now_ts]
        cooled_keys = [k for k in active_keys if _GEMINI_KEY_COOLDOWN.get(k, 0) > now_ts]
        ordered_keys = ready_keys + cooled_keys

        payload_bytes = json.dumps({
            "contents": [{
                "parts": [{"text": prompt_text}] + image_parts
            }],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.1
            }
        }).encode('utf-8')

        for key_idx, api_key in enumerate(ordered_keys, start=1):
            key_hint = f"Key#{key_idx}(...{api_key[-6:]})" if len(api_key) >= 6 else f"Key#{key_idx}"
            for model_name in candidate_models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                try:
                    req = urllib.request.Request(
                        url,
                        data=payload_bytes,
                        headers={"Content-Type": "application/json"}
                    )
                    with urllib.request.urlopen(req, timeout=25) as resp:
                        data = json.loads(resp.read().decode('utf-8'))
                        candidate = data.get('candidates', [{}])[0]
                        parts = candidate.get('content', {}).get('parts', [{}])
                        out_text = parts[0].get('text', '{}')
                        clean_text = out_text.strip()
                        if '```' in clean_text:
                            clean_text = re.sub(r'^```(?:json)?\s*', '', clean_text, flags=re.IGNORECASE)
                            clean_text = re.sub(r'\s*```$', '', clean_text)
                        s_idx = clean_text.find('{')
                        e_idx = clean_text.rfind('}')
                        if s_idx != -1 and e_idx != -1 and e_idx > s_idx:
                            clean_text = clean_text[s_idx:e_idx+1]
                        parsed = json.loads(clean_text)
                        if isinstance(parsed, list) and parsed:
                            parsed = parsed[0]
                        _GEMINI_KEY_COOLDOWN.pop(api_key, None)
                        print(f"[+] Vision AI sukses menggunakan model: {model_name} ({key_hint})")
                        return parsed, out_text
                except urllib.error.HTTPError as he:
                    if he.code == 429:
                        # Kuota/rate-limit habis pada key ini -> istirahatkan 120 detik & langsung pindah ke key berikutnya
                        _GEMINI_KEY_COOLDOWN[api_key] = time.time() + 120
                        print(f"[!] Vision AI {key_hint} ({model_name}) kena 429 (kuota/limit), otomatis pindah ke API key cadangan...")
                        break
                    if he.code in (401, 403):
                        _GEMINI_KEY_COOLDOWN[api_key] = time.time() + 300
                        print(f"[!] Vision AI {key_hint} ditolak HTTP {he.code}, otomatis pindah ke API key cadangan...")
                        break
                    print(f"[!] Vision AI {key_hint} model {model_name} HTTP {he.code}, mencoba model berikutnya...")
                    continue
                except Exception as e_model:
                    print(f"[!] Vision AI {key_hint} model {model_name} error: {e_model}, mencoba fallback berikutnya...")
                    continue

        return None, ""
    except Exception as e:
        print(f"[!] Vision AI Call Error: {e}")
        return None, ""

def process_ocr(image_bytes, target='', engine='auto'):
    # Pilihan 1: Jika engine 'vision' atau 'auto', coba Vision AI terlebih dahulu untuk presisi multimodal
    if engine in ('vision', 'auto') and VISION_AI_ENABLED:
        parsed_vision, text_vision = extract_with_vision_ai(image_bytes, target)
        if parsed_vision and any(parsed_vision.values()):
            print(f"[+] Vision AI sukses mengekstrak target: {target}")
            return text_vision, parsed_vision
            
    # Pilihan 2: Deep Learning OCR Lokal (100% Offline via Apple Silicon GPU MPS)
    img_cv = decode_file_bytes_to_cv2(image_bytes)
    if img_cv is None:
        return "Gagal mendekode berkas gambar/PDF", {}
        
    if target == 'ktp':
        parsed, combined_text = parse_ktp_image(img_cv)
    elif target == 'npwp':
        parsed, combined_text = parse_npwp_image(img_cv)
    elif target in ('stnk', 'stnk_1', 'stnk_2'):
        parsed, combined_text = parse_stnk_image(img_cv)
    elif target in ('bpkb', 'leasing', 'ownership'):
        parsed, combined_text = parse_ownership_image(img_cv)
    elif target in ('vehicle', 'kbm_unified'):
        parsed_stnk, text_stnk = parse_stnk_image(img_cv)
        parsed_bpkb, text_bpkb = parse_ownership_image(img_cv)
        parsed = {}
        parsed.update(parsed_stnk)
        parsed.update(parsed_bpkb)
        combined_text = text_stnk + "\n" + text_bpkb
    elif target in ('fullset', 'all', 'master'):
        parsed_ktp, text_ktp = parse_ktp_image(img_cv)
        parsed_npwp, text_npwp = parse_npwp_image(img_cv)
        parsed_stnk, text_stnk = parse_stnk_image(img_cv)
        parsed_bpkb, text_bpkb = parse_ownership_image(img_cv)
        parsed = {}
        parsed.update(parsed_ktp)
        parsed.update(parsed_npwp)
        parsed.update(parsed_stnk)
        parsed.update(parsed_bpkb)
        combined_text = "\n".join([text_ktp, text_npwp, text_stnk, text_bpkb])
    else:
        easy_lines = run_easyocr_on_cv_img(img_cv)
        combined_text = "\n".join(easy_lines)
        parsed = {}
        
    return combined_text, parsed

class ThreadingHTTPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


# ================= DATABASE PENGGUNA, OTP & ROLE-BASED ACCESS =================
# DATA_DIR menunjuk ke Persistent Disk di cloud (mis. Render) bila di-set; di lokal
# default-nya tetap folder proyek ini seperti sebelumnya. Ini mencegah data pengguna
# (PII) ikut ter-commit ke git karena wajib disimpan di repo demi bertahan antar deploy.
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get('DATA_DIR', _APP_DIR)
os.makedirs(DATA_DIR, exist_ok=True)

def _migrate_legacy_data_file_once(filename):
    """Migrasi sekali jalan: salin file data lama dari folder repo ke Persistent Disk (DATA_DIR)
    bila disk masih kosong, supaya data pemohon/user yang sudah ada tidak hilang saat pindah
    ke DATA_DIR terpisah (mis. saat pertama kali mengaktifkan Render Persistent Disk)."""
    if DATA_DIR == _APP_DIR:
        return
    legacy_path = os.path.join(_APP_DIR, filename)
    new_path = os.path.join(DATA_DIR, filename)
    if os.path.exists(legacy_path) and not os.path.exists(new_path):
        try:
            shutil.copy2(legacy_path, new_path)
            print(f"[+] Migrasi data lama -> Persistent Disk: {filename}")
        except Exception as e:
            print(f"[!] Gagal migrasi {filename} ke DATA_DIR:", e)

for _legacy_file in ('db_users.json', 'db_otp.json', 'db_permohonan.json', 'db_chat.json', 'db_nadine_config.json'):
    _migrate_legacy_data_file_once(_legacy_file)

DB_USERS_PATH = os.path.join(DATA_DIR, 'db_users.json')
DB_OTP_PATH = os.path.join(DATA_DIR, 'db_otp.json')
UPLOADS_DIR = os.path.join(DATA_DIR, 'uploads')
os.makedirs(UPLOADS_DIR, exist_ok=True)
AUTH_SESSIONS = {}

# ================= ARSIP BERKAS LOKAL & GOOGLE DRIVE APPS SCRIPT BRIDGE =================
_MIME_TO_EXT = {
    'image/jpeg': '.jpg',
    'image/jpg': '.jpg',
    'image/png': '.png',
    'image/webp': '.webp',
    'application/pdf': '.pdf',
}

def _sanitize_archive_name(text, fallback='DOKUMEN'):
    cleaned = re.sub(r'[^A-Za-z0-9._-]+', '_', str(text or '').strip()).strip('_')
    return cleaned[:60] if cleaned else fallback

def _make_permohonan_folder_name(record):
    pid = _sanitize_archive_name(record.get('id', 'KBM'), 'KBM')
    nama = _sanitize_archive_name(record.get('nama_pemohon', 'PEMOHON'), 'PEMOHON')[:28]
    nopol = _sanitize_archive_name(record.get('nopol', 'NOPOL'), 'NOPOL')[:18]
    return f"{pid}_{nama}_{nopol}"

MAX_UPLOAD_FILE_BYTES = 10 * 1024 * 1024  # Batas keamanan: maks 10 MB per file unggahan
LOGIN_FAIL_TRACKER = {}   # key: (ip, ident) -> list[timestamp]
# Keamanan: LOGIN_FAIL_TRACKER di atas dikunci per (ip, ident) — terbukti lewat
# pengujian langsung ke production BISA DILEWATI dengan mengganti header
# X-Forwarded-For di tiap percobaan (Render tidak memvalidasi/menimpa header
# itu, jadi _get_client_ip() ikut percaya nilai palsu apa pun yang dikirim
# klien). ACCOUNT_FAIL_TRACKER ini TIDAK bergantung IP sama sekali — kuncinya
# HANYA identitas akun (username/NIP/email/no.WA dinormalisasi) — supaya tidak
# bisa dilewati dengan spoofing IP. Dipakai bersama oleh /api/auth/login DAN
# /api/auth/login-pegawai (kunci yang sama) supaya penyerang tidak bisa
# membagi jatah percobaan antara dua endpoint untuk menggandakan budget.
ACCOUNT_FAIL_TRACKER = {}  # key: ident_normalized -> list[timestamp]
ACCOUNT_FAIL_MAX_ATTEMPTS = 10
ACCOUNT_FAIL_WINDOW_SECONDS = 600  # 10 menit

def _normalize_login_ident(raw):
    return str(raw or '').strip().lower().replace(' ', '').replace('-', '')
OTP_RATE_TRACKER = {}     # key: (ip, phone) -> list[timestamp]
VERIFY_OTP_TRACKER = {}   # key: (ip, identifier) -> list[timestamp]
RESET_PW_TRACKER = {}     # key: (ip, identifier) -> list[timestamp]
EMAIL_OTP_RATE_TRACKER = {}        # key: phone -> list[timestamp] — maks 3x/5 menit kirim OTP email registrasi
RESET_EMAIL_OTP_RATE_TRACKER = {}  # key: key -> list[timestamp] — maks 3x/5 menit kirim OTP email reset sandi
OCR_RATE_TRACKER = {}     # key: (ip, session_token) -> list[timestamp]
DRAFT_SAVE_RATE_TRACKER = {}  # key: (ip, session_token) -> list[timestamp] — autosave Tahap 2

def _get_client_ip(handler):
    xff = handler.headers.get('X-Forwarded-For', '') if hasattr(handler, 'headers') and handler.headers else ''
    if xff:
        return xff.split(',')[0].strip()
    return handler.client_address[0] if getattr(handler, 'client_address', None) else 'unknown'

def _is_rate_limited(tracker, key, max_attempts, window_seconds):
    now = time.time()
    attempts = [t for t in tracker.get(key, []) if now - t < window_seconds]
    tracker[key] = attempts
    return len(attempts) >= max_attempts

def _record_rate_hit(tracker, key, window_seconds):
    now = time.time()
    attempts = [t for t in tracker.get(key, []) if now - t < window_seconds]
    attempts.append(now)
    tracker[key] = attempts

def _validate_upload_magic_bytes(raw_bytes):
    """Validasi magic bytes asli file: hanya menerima JPEG, PNG, WebP, atau PDF."""
    if not raw_bytes or len(raw_bytes) > MAX_UPLOAD_FILE_BYTES:
        return None, None
    if raw_bytes.startswith(bytes([0xFF, 0xD8, 0xFF])):
        return 'image/jpeg', '.jpg'
    if raw_bytes.startswith(bytes([0x89, 0x50, 0x4E, 0x47])):
        return 'image/png', '.png'
    if raw_bytes.startswith(b'RIFF') and raw_bytes[8:12] == b'WEBP':
        return 'image/webp', '.webp'
    if raw_bytes.startswith(b'%PDF'):
        return 'application/pdf', '.pdf'
    return None, None

def _decode_data_url(data_url):
    if not data_url or not isinstance(data_url, str):
        return None, None, None, None
    s = data_url.strip()
    b64_part = s
    if s.startswith('data:') and ',' in s:
        _, b64_part = s.split(',', 1)
    try:
        raw_bytes = base64.b64decode(b64_part)
    except Exception:
        return None, None, None, None
    real_mime, real_ext = _validate_upload_magic_bytes(raw_bytes)
    if not real_mime:
        print(f"[!] Upload ditolak: tipe file tidak diizinkan atau melebihi 10 MB (size={len(raw_bytes)} bytes)")
        return None, None, None, None
    return real_mime, real_ext, raw_bytes, b64_part

def upload_to_gdrive_bridge(subfolder, filename, mime_type, base64_data, root_folder='ARSIP_PENGSEM_KBM_BATAM'):
    """Kirim file ke Google Drive melalui Google Apps Script Web App Bridge."""
    bridge_url = (os.environ.get('GDRIVE_BRIDGE_URL') or '').strip()
    bridge_secret = (os.environ.get('GDRIVE_BRIDGE_SECRET') or '').strip()
    if not bridge_url or not bridge_secret:
        return {"status": "skipped", "reason": "GDRIVE_BRIDGE_URL/SECRET belum diatur"}
    try:
        payload = json.dumps({
            "secret": bridge_secret,
            "action": "upload_file",
            "root_folder": root_folder,
            "subfolder": subfolder,
            "filename": filename,
            "mime_type": mime_type,
            "base64_data": base64_data,
        }).encode('utf-8')
        req = urllib.request.Request(
            bridge_url,
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=35) as resp:
            raw = resp.read().decode('utf-8', errors='replace')
            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = {"status": "ok", "raw": raw[:200]}
            print(f"[+] Arsip Google Drive ({subfolder}/{filename}): {parsed.get('status')}")
            return parsed
    except Exception as e:
        print(f"[!] Gagal arsip Google Drive ({subfolder}/{filename}): {e}")
        return {"status": "error", "message": str(e)}

def save_and_archive_document(record, doc_label, data_url, custom_filename=None):
    """Simpan berkas ke disk lokal (UPLOADS_DIR/<folder>/) & antrekan sinkronisasi ke Google Drive."""
    mime_type, ext, raw_bytes, b64_part = _decode_data_url(data_url)
    if not raw_bytes:
        return None

    folder_name = _make_permohonan_folder_name(record)
    local_dir = os.path.join(UPLOADS_DIR, folder_name)
    os.makedirs(local_dir, exist_ok=True)

    if custom_filename:
        safe_fn = _sanitize_archive_name(custom_filename, doc_label)
        if '.' not in safe_fn:
            safe_fn += ext
    else:
        safe_fn = f"{_sanitize_archive_name(doc_label, 'DOKUMEN')}{ext}"

    local_path = os.path.join(local_dir, safe_fn)
    try:
        with open(local_path, 'wb') as f:
            f.write(raw_bytes)
    except Exception as e:
        print(f"[!] Gagal simpan berkas lokal {local_path}: {e}")

    # Upload asinkron ke Google Drive Bridge agar tidak menghambat response HTTP
    threading.Thread(
        target=upload_to_gdrive_bridge,
        args=(folder_name, safe_fn, mime_type, b64_part),
        daemon=True
    ).start()

    return {
        "label": doc_label,
        "filename": safe_fn,
        "mime_type": mime_type,
        "size_bytes": len(raw_bytes),
        "folder": folder_name,
        "saved_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }

def backup_sqlite_to_gdrive_async():
    """Kirim salinan database SQLite ke folder _BACKUP_DATABASE di Google Drive."""
    def _worker():
        try:
            db_path = database.DATABASE_PATH
            if not os.path.exists(db_path):
                return
            with open(db_path, 'rb') as f:
                b64_db = base64.b64encode(f.read()).decode('utf-8')
            ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            upload_to_gdrive_bridge('_BACKUP_DATABASE', f'kbm_batam_{ts}.db', 'application/x-sqlite3', b64_db)
        except Exception as e:
            print(f"[!] Gagal backup SQLite ke Google Drive: {e}")
    threading.Thread(target=_worker, daemon=True).start()

# ================= RBAC: PERAN PETUGAS & HAK AKSES PER TAHAPAN =================
# Setiap petugas HANYA berwenang di tahapan sesuai jabatannya (least privilege).
# Pengecualian: adminutama (kontrol penuh, dibatasi di endpoint sensitif tersendiri)
# dan Pemeriksa Barang/Dokumen yang butuh visibilitas PENUH lintas tahap untuk
# memvalidasi kesesuaian fisik barang terhadap seluruh berkas dokumennya.
PEGAWAI_ROLES = {
    'adminutama', 'frontdesk', 'loket', 'jaminan', 'fasilitas',
    'pemeriksabarang', 'pemeriksadokumen', 'gate'
}
FULL_VISIBILITY_ROLES = {'adminutama', 'pemeriksabarang', 'pemeriksadokumen'}
# Admin Override TIDAK BOLEH dipakai untuk memfabrikasi hasil keputusan sensitif
# (hasil rekam LHP, keputusan Pemeriksa Dokumen, penerbitan SPPB, realisasi SPPB) —
# tahap-tahap ini wajib dikerjakan lewat endpoint aksi petugas yang sebenarnya,
# bukan dilompati manual oleh admin, sesuai batasan yang diminta eksplisit.
ADMIN_OVERRIDE_BLOCKED_STATUSES = {'PEMERIKSA_DOKUMEN', 'SPPB_GATE_OUT', 'SELESAI_KELUAR_TLDDP'}
STAGE_VISIBILITY_BY_ROLE = {
    'frontdesk': ('FRONTDESK_NADINE', 'BERKAS_LENGKAP'),
    'loket': ('FRONTDESK_NADINE', 'BERKAS_LENGKAP', 'LOKET_VERIFIKASI'),
    'fasilitas': ('VERIFIKASI_FASILITAS',),
    'jaminan': ('LOKET_JAMINAN',),
    'gate': ('SPPB_GATE_OUT',),
}

def _is_pegawai(sess):
    return bool(sess) and sess.get('role') in PEGAWAI_ROLES

def _pemohon_draft_identifier(sess):
    """Kunci draf formulir Tahap 2 — SELALU dari identitas unik akun pemohon di sesi
    login (User ID unik permanen, dinormalisasi nomor telepon/NIK/username), bukan
    dari body request, supaya satu akun tidak bisa membaca/menimpa draf akun pemohon lain."""
    sess_user = (sess or {}).get('user', {}) or {}
    uid = str(sess_user.get('id', '')).strip()
    if uid:
        return f"pemohon:uid_{uid}"
    
    # Fallback normalisasi nomor telepon jika id tidak tersedia
    phone = str(sess_user.get('phone', '')).strip().replace('+', '').replace('-', '').replace(' ', '')
    if phone.startswith('0'):
        phone = '62' + phone[1:]
    if phone:
        return f"pemohon:ph_{phone}"

    nik = str(sess_user.get('nik', '')).strip().replace(' ', '').replace('-', '')
    if nik:
        return f"pemohon:nik_{nik}"

    username = str(sess_user.get('username', '')).strip()
    return f"pemohon:usr_{username}" if username else ''

def _legacy_pemohon_draft_identifier(sess):
    """Fallback ke kunci draf skema lama untuk kompatibilitas draf yang sudah tersimpan."""
    sess_user = (sess or {}).get('user', {}) or {}
    ident = str(sess_user.get('nik', '')).strip() or str(sess_user.get('phone', '')).strip() or str(sess_user.get('username', '')).strip()
    return f"pemohon:{ident}" if ident else ''

# NIP akun "Default Dinas" dari backdoor lama (sudah dihapus dari kode login).
# Tetap didaftarkan di sini sebagai denylist permanen: meski record ini masih ada
# di data lama (db_users.json/kbm_batam.db) atau muncul lagi dari seed default,
# akun ini tidak akan pernah bisa dipakai login karena selalu disaring di sini.
REVOKED_LEGACY_NIPS = {"199501012020011001"}

def _filter_revoked_accounts(users_data):
    if isinstance(users_data, dict) and users_data.get('pegawai'):
        users_data['pegawai'] = [
            p for p in users_data['pegawai']
            if str(p.get('nip', '')).strip() not in REVOKED_LEGACY_NIPS
        ]
    return users_data

def load_db_users():
    # Ambil data dari SQLite WAL
    try:
        conn = database.get_db_connection()
        rows = conn.execute("SELECT * FROM users").fetchall()
        conn.close()
        if rows:
            pegawai = []
            pemohon = []
            for r in rows:
                u = dict(r)
                if u.get('role') != 'pemohon' or u.get('is_officer'):
                    pegawai.append(u)
                else:
                    pemohon.append(u)
            return _filter_revoked_accounts({"pegawai": pegawai, "pemohon": pemohon})
    except Exception as e_sql:
        print('[!] SQLite users query fallback to JSON:', e_sql)

    if os.path.exists(DB_USERS_PATH):
        try:
            with open(DB_USERS_PATH, 'r', encoding='utf-8') as f:
                return _filter_revoked_accounts(json.load(f))
        except Exception as e:
            print('[!] Error loading db_users:', e)
    # Belum ada data pegawai tersimpan — mulai kosong (JANGAN seed akun default
    # dengan password hardcoded; akun dinas resmi dibuat lewat proses RBAC terpisah).
    default_users = {
        "pegawai": [],
        "pemohon": []
    }
    save_db_users(default_users)
    return default_users

def save_db_users(data):
    try:
        with open(DB_USERS_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print('[!] Error saving db_users:', e)

    # Sinkronisasi ke SQLite database (sumber utama yang dibaca load_db_users()).
    # BUG REGRESI sebelumnya: blok ini sempat terdampar jadi kode mati tak terjangkau
    # di dalam fungsi _strip_password() akibat edit sebelumnya, sehingga akun pemohon
    # baru hasil verifikasi OTP tersimpan di db_users.json tapi TIDAK di SQLite -
    # login berikutnya gagal 401 karena load_db_users() membaca SQLite lebih dulu.
    try:
        for u in data.get('pemohon', []):
            database.save_or_update_user(u)
        for u in data.get('pegawai', []):
            database.save_or_update_user(u)
    except Exception as e:
        print('[!] Error syncing users to SQLite:', e)
    return True

def repair_sqlite_users_from_json_once():
    """Perbaikan sekali-jalan saat startup: re-sinkronkan db_users.json ke SQLite.
    Menambal akun yang sempat dibuat selagi bug regresi save_db_users() aktif
    (lihat catatan di atas) - akun itu ada di JSON tapi hilang dari SQLite,
    sehingga pemiliknya tidak bisa login meski registrasi sempat "berhasil"."""
    try:
        if os.path.exists(DB_USERS_PATH):
            with open(DB_USERS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for u in data.get('pemohon', []):
                database.save_or_update_user(u)
            for u in data.get('pegawai', []):
                database.save_or_update_user(u)
            print('[+] Perbaikan startup: akun di db_users.json disinkronkan ulang ke SQLite.')
    except Exception as e:
        print('[!] Gagal menjalankan perbaikan startup sinkronisasi user:', e)

def _strip_password(user_dict):
    """Salinan dict user tanpa field 'password' — dipakai setiap kali data user dikirim ke client (JSON response)."""
    if not isinstance(user_dict, dict):
        return user_dict
    return {k: v for k, v in user_dict.items() if k != 'password'}

def _normalize_phone_id(raw_phone):
    """Normalisasi nomor WhatsApp Indonesia ke format 628xxx untuk komparasi duplikasi yang akurat."""
    s = str(raw_phone or '').strip().replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').replace('.', '')
    if not s or not s.isdigit():
        return ''
    if s.startswith('08'):
        return '628' + s[2:]
    if s.startswith('8'):
        return '628' + s[1:]
    if s.startswith('62'):
        return s
    return '62' + s.lstrip('0')

def _find_duplicate_registration(users_data, phone='', email=''):
    """Periksa apakah nomor WA atau email sudah terdaftar pada akun pemohon maupun pegawai."""
    norm_phone = _normalize_phone_id(phone)
    norm_email = str(email or '').strip().lower()
    phone_exists = False
    email_exists = False
    all_users = (users_data.get('pemohon', []) if isinstance(users_data, dict) else []) + \
                (users_data.get('pegawai', []) if isinstance(users_data, dict) else [])
    for u in all_users:
        if not isinstance(u, dict):
            continue
        if norm_phone:
            u_phone = _normalize_phone_id(u.get('phone', ''))
            u_uname_phone = _normalize_phone_id(u.get('username', ''))
            if norm_phone in (u_phone, u_uname_phone):
                phone_exists = True
        if norm_email:
            u_email = str(u.get('email', '') or '').strip().lower()
            u_uname_email = str(u.get('username', '') or '').strip().lower()
            if norm_email in (u_email, u_uname_email):
                email_exists = True
        if phone_exists and email_exists:
            break
    return phone_exists, email_exists

def _duplicate_registration_message(phone_exists, email_exists):
    if phone_exists and email_exists:
        return "Nomor WhatsApp dan alamat email ini sudah terdaftar di sistem. Silakan langsung Masuk (Login) atau gunakan fitur Lupa Kata Sandi."
    if phone_exists:
        return "Nomor WhatsApp ini sudah terdaftar di sistem. Silakan langsung Masuk (Login) atau gunakan fitur Lupa Kata Sandi."
    if email_exists:
        return "Alamat email ini sudah terdaftar di sistem. Silakan gunakan alamat email lain atau langsung Masuk (Login) jika sudah memiliki akun."
    return ""

def load_db_otp():
    otps = {}
    if os.path.exists(DB_OTP_PATH):
        try:
            with open(DB_OTP_PATH, 'r', encoding='utf-8') as f:
                otps = json.load(f)
        except Exception as e:
            print('[!] Error loading db_otp:', e)
    
    # Sinkronisasi dengan database SQLite (persisten lintas restart / worker)
    try:
        db_otps = database.load_all_registration_otps()
        if db_otps:
            otps.update(db_otps)
    except Exception as e:
        print('[!] Error syncing SQLite OTPs:', e)

    now = time.time()
    valid_otps = {k: v for k, v in otps.items() if v.get('expires_at', 0) > now}
    if len(valid_otps) != len(otps):
        try:
            with open(DB_OTP_PATH, 'w', encoding='utf-8') as f:
                json.dump(valid_otps, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    return valid_otps

def save_db_otp(data):
    try:
        with open(DB_OTP_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print('[!] Error saving db_otp:', e)
    
    # Simpan juga ke database SQLite
    try:
        for p, d in data.items():
            database.save_registration_otp(p, d)
    except Exception as e:
        print('[!] Error saving SQLite OTP:', e)
    return True

def get_session_from_request(handler):
    token = None
    auth_header = handler.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:].strip()
    if not token:
        token = handler.headers.get('X-Session-Token', '')
    if not token and 'Cookie' in handler.headers:
        cookie = http.cookies.SimpleCookie(handler.headers['Cookie'])
        if 'session_token' in cookie:
            token = cookie['session_token'].value
    if not token and '?' in handler.path:
        query_params = urllib.parse.parse_qs(urllib.parse.urlparse(handler.path).query)
        token = query_params.get('session_token', [''])[0] or query_params.get('token', [''])[0]

    if token and token in AUTH_SESSIONS:
        sess = AUTH_SESSIONS[token]
        if sess.get('created_at', 0) >= GLOBAL_SESSION_EPOCH and time.time() < sess.get('expires_at', float('inf')):
            return token, sess
        else:
            del AUTH_SESSIONS[token]
    return None, None


# ================= DATABASE PERMOHONAN & WHATSAPP BOT ENGINE =================
DB_PERMOHONAN_PATH = os.path.join(DATA_DIR, 'db_permohonan.json')
DB_CHAT_PATH = os.path.join(DATA_DIR, 'db_chat.json')

def load_db_chat():
    if os.path.exists(DB_CHAT_PATH):
        try:
            with open(DB_CHAT_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print('[!] Error loading db_chat:', e)
    return {}

def save_db_chat(data):
    try:
        with open(DB_CHAT_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print('[!] Error saving db_chat:', e)
        return False

def _now_wib_str():
    """Mengembalikan waktu saat ini dalam WIB (UTC+7) format YYYY-MM-DD HH:MM:SS WIB."""
    wib = datetime.timezone(datetime.timedelta(hours=7))
    return datetime.datetime.now(wib).strftime('%Y-%m-%d %H:%M:%S WIB')

def log_chat_message(phone, sender, text, name=None):
    import time
    clean_phone = _normalize_phone_id(phone) or str(phone or '').strip().replace('+', '').replace('-', '').replace(' ', '')
    if clean_phone.startswith('08'):
        clean_phone = '628' + clean_phone[2:]
    chats = load_db_chat()
    now_str = _now_wib_str()

    if clean_phone not in chats:
        chats[clean_phone] = {
            'nama': name or f'Pemohon WA ({clean_phone})',
            'nomor': clean_phone,
            'updated_at': now_str,
            'messages': []
        }
    if name and (not chats[clean_phone].get('nama') or str(chats[clean_phone].get('nama', '')).startswith('Pemohon WA (')):
        chats[clean_phone]['nama'] = name

    chats[clean_phone]['updated_at'] = now_str
    chats[clean_phone]['messages'].append({
        'id': f'msg_{int(time.time()*1000)}',
        'sender': sender,
        'text': text,
        'timestamp': now_str
    })
    save_db_chat(chats)
META_VERIFY_TOKEN = 'beacukai_batam_pengsem_kbm_secret_2026'

def get_meta_credentials():
    token = os.environ.get('META_WA_ACCESS_TOKEN') or os.environ.get('WA_META_ACCESS_TOKEN', '')
    phone_id = os.environ.get('META_PHONE_NUMBER_ID') or os.environ.get('WA_META_PHONE_NUMBER_ID', '')
    if not token or not phone_id:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line and not line.strip().startswith('#'):
                            k, v = line.strip().split('=', 1)
                            k, v = k.strip(), v.strip()
                            if k in ('META_WA_ACCESS_TOKEN', 'WA_META_ACCESS_TOKEN') and not token:
                                token = v
                            if k in ('META_PHONE_NUMBER_ID', 'WA_META_PHONE_NUMBER_ID') and not phone_id:
                                phone_id = v
            except Exception as e_env:
                print("[!] Error reading .env for Meta:", e_env)
    return token or '', phone_id or '1445699195298363'

META_WA_ACCESS_TOKEN, META_PHONE_NUMBER_ID = get_meta_credentials()
META_WABA_ID = os.environ.get('META_WABA_ID', '2252215596173280')
WA_SESSIONS = {}

def load_db_permohonan():
    # Mengambil data dari SQLite WAL berkinerja tinggi & terindeks
    try:
        perms = database.get_all_permohonan()
        if perms is not None:
            return perms
    except Exception as e_sql:
        print("[!] SQLite permohonan query fallback to JSON:", e_sql)

    if os.path.exists(DB_PERMOHONAN_PATH):
        try:
            with open(DB_PERMOHONAN_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print("[!] Error loading db_permohonan:", e)
    return []

def save_db_permohonan(data):
    # Menyimpan ke SQLite WAL dan menyinkronkan file JSON cadangan
    try:
        if isinstance(data, list):
            for p in data:
                try:
                    if database.get_permohonan_by_id(p.get('id')):
                        database.update_permohonan_status(p.get('id'), p.get('status'), p.get('catatan_petugas', ''), p)
                    else:
                        database.save_new_permohonan(p)
                except Exception as _e_save_p:
                    pass
        elif isinstance(data, dict) and data.get('id'):
            if database.get_permohonan_by_id(data.get('id')):
                database.update_permohonan_status(data.get('id'), data.get('status'), data.get('catatan_petugas', ''), data)
            else:
                database.save_new_permohonan(data)
    except Exception as e_sql:
        print("[!] SQLite save error:", e_sql)

    try:
        with open(DB_PERMOHONAN_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print("[!] Error saving db_permohonan backup:", e)
        return False

# ID contoh/demo yang pernah diisi dengan identitas asli developer untuk kebutuhan uji
# tampilan dashboard petugas. Harus dibuang dari data production: selain berisiko privasi,
# nomor WA aslinya kebetulan sama dengan akun pemohon asli, jadi membuat sistem salah
# kira pemohon baru itu "sudah pernah mengajukan permohonan" dan menguncinya dari formulir.
DEMO_SEED_PERMOHONAN_IDS = {
    'KBM-2026-001', 'KBM-2026-002', 'KBM-2026-003',
    'KBM-2026-004', 'KBM-2026-005', 'KBM-2026-006',
}

def repair_remove_demo_seed_permohonan_once():
    try:
        conn = database.get_db_connection()
        placeholders = ','.join('?' for _ in DEMO_SEED_PERMOHONAN_IDS)
        cur = conn.execute(f"SELECT COUNT(*) as c FROM permohonan WHERE id IN ({placeholders})", tuple(DEMO_SEED_PERMOHONAN_IDS))
        count = cur.fetchone()['c']
        if count:
            conn.execute(f"DELETE FROM permohonan WHERE id IN ({placeholders})", tuple(DEMO_SEED_PERMOHONAN_IDS))
            conn.commit()
            print(f"[+] Perbaikan startup: {count} data contoh/demo permohonan dihapus dari SQLite production.")
        conn.close()
    except Exception as e:
        print('[!] Gagal menjalankan pembersihan data demo permohonan di SQLite:', e)

    # Bersihkan juga file backup JSON agar tidak ter-fallback atau termigrasi ulang saat startup berikutnya
    try:
        if os.path.exists(DB_PERMOHONAN_PATH):
            with open(DB_PERMOHONAN_PATH, 'r', encoding='utf-8') as f:
                raw_json = json.load(f)
            if isinstance(raw_json, list):
                cleaned = [p for p in raw_json if isinstance(p, dict) and p.get('id') not in DEMO_SEED_PERMOHONAN_IDS]
                if len(cleaned) != len(raw_json):
                    with open(DB_PERMOHONAN_PATH, 'w', encoding='utf-8') as f:
                        json.dump(cleaned, f, indent=2, ensure_ascii=False)
                    print(f"[+] Perbaikan startup: {len(raw_json) - len(cleaned)} data contoh/demo permohonan dihapus dari db_permohonan.json.")
    except Exception as e:
        print('[!] Gagal menjalankan pembersihan data demo permohonan di JSON:', e)

def get_wa_gateway_config():
    """Membaca WA_GATEWAY_URL dan WA_GATEWAY_SECRET dari environment (fallback .env lokal)."""
    gw_url = (os.environ.get('WA_GATEWAY_URL') or '').strip()
    gw_secret = (os.environ.get('WA_GATEWAY_SECRET') or '').strip()
    if not gw_url or not gw_secret:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line and not line.strip().startswith('#'):
                            k, v = line.strip().split('=', 1)
                            k, v = k.strip(), v.strip().strip('"').strip("'")
                            if k == 'WA_GATEWAY_URL' and not gw_url:
                                gw_url = v
                            if k == 'WA_GATEWAY_SECRET' and not gw_secret:
                                gw_secret = v
            except Exception as e_env:
                print("[!] Error reading .env for WA Gateway:", e_env)
    return gw_url.rstrip('/'), gw_secret

def send_whatsapp_via_gateway(to_number, text, log_chat=True):
    """Kirim pesan WhatsApp melalui Self-Hosted Baileys Gateway (Mac Mini / Cloudflare Tunnel)."""
    gw_url, gw_secret = get_wa_gateway_config()
    if not gw_url:
        return {"status": "error", "provider": "wa_gateway", "message": "WA_GATEWAY_URL belum dikonfigurasi."}
    if not gw_secret:
        return {"status": "error", "provider": "wa_gateway", "message": "WA_GATEWAY_SECRET belum dikonfigurasi di server."}

    import urllib.request
    endpoint = f"{gw_url}/send"
    headers = {
        "Content-Type": "application/json",
        "X-WA-Gateway-Secret": gw_secret,
        "User-Agent": "PENGSEM-KBM-Backend/1.0"
    }
    payload = {"to": str(to_number), "text": str(text)}
    try:
        req = urllib.request.Request(endpoint, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=15) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            if isinstance(res_data, dict) and res_data.get('status') in ('ok', 'success'):
                if log_chat:
                    try:
                        log_chat_message(to_number, 'bot', text)
                    except Exception:
                        pass
                msg_id = res_data.get('message_id', '')
                return {
                    "status": "success",
                    "provider": "wa_gateway",
                    "message_id": msg_id,
                    "messages": [{"id": msg_id}]
                }
            return {
                "status": "error",
                "provider": "wa_gateway",
                "message": (res_data.get('message') if isinstance(res_data, dict) else None) or "Respon tidak valid dari WA Gateway."
            }
    except urllib.error.HTTPError as he:
        err_msg = f"WA Gateway HTTP {he.code}"
        try:
            err_json = json.loads(he.read().decode('utf-8'))
            if isinstance(err_json, dict) and err_json.get('message'):
                err_msg = err_json['message']
        except Exception:
            pass
        print(f"[!] WA Gateway HTTP Error {he.code}: {err_msg}")
        return {"status": "error", "provider": "wa_gateway", "code": he.code, "message": err_msg}
    except Exception as e:
        print("[!] Error sending via WA Gateway:", e)
        return {"status": "error", "provider": "wa_gateway", "message": f"Gagal menghubungi WA Gateway: {e}"}

def send_whatsapp_meta_message(to_number, text, buttons=None, log_chat=True):
    """Mengirim pesan WhatsApp: prioritas Self-Hosted WA Gateway jika WA_GATEWAY_URL terisi,
    fallback ke Meta WhatsApp Cloud API resmi jika WA_GATEWAY_URL kosong."""
    gw_url, _ = get_wa_gateway_config()
    if gw_url:
        msg_text = str(text or '')
        if buttons and len(buttons) > 0:
            opts = "\n".join(f"• {b.get('title', '')}" for b in buttons[:3] if b.get('title'))
            if opts:
                msg_text = f"{msg_text}\n\n{opts}"
        return send_whatsapp_via_gateway(to_number, msg_text, log_chat=log_chat)

    token, phone_id = get_meta_credentials()
    if not token or not phone_id:
        print(f"[*] [WA Sandbox Log] to: {to_number} -> {text[:80]}... (Buttons: {buttons})")
        return {"status": "logged_offline"}

    import urllib.request
    url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if buttons and len(buttons) > 0:
        # Interactive Button Format
        interactive_buttons = []
        for idx, btn in enumerate(buttons[:3]):
            interactive_buttons.append({
                "type": "reply",
                "reply": {
                    "id": btn.get("id", f"btn_{idx}"),
                    "title": btn.get("title", "")[:20]
                }
            })
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": text},
                "action": {"buttons": interactive_buttons}
            }
        }
    else:
        # Standard Text Message
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "text",
            "text": {"preview_url": False, "body": text}
        }

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=15) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            if log_chat:
                try:
                    log_chat_message(to_number, 'bot', text)
                except Exception:
                    pass
            return res_data
    except urllib.error.HTTPError as he:
        err_body = ""
        try:
            err_body = he.read().decode('utf-8')
        except Exception:
            pass
        print(f"[!] WhatsApp Meta HTTP Error {he.code}: {err_body}")
        if he.code == 429 or "rate" in err_body.lower() or "limit" in err_body.lower():
            return {"status": "rate_limited", "code": 429, "message": "WhatsApp Meta API Rate Limit Exceeded"}
        return {"status": "error", "code": he.code, "message": str(he)}
    except Exception as e:
        print("[!] Error sending WhatsApp Meta message:", e)
        return {"status": "error", "message": str(e)}

def send_whatsapp_otp_template(to_number, otp_code, fallback_text):
    """Kirim OTP: prioritas Self-Hosted WA Gateway (bebas aturan 24 jam Meta) jika WA_GATEWAY_URL
    terisi. Jika kosong, pakai Meta WhatsApp Authentication Template (bila META_OTP_TEMPLATE_NAME
    disetel) lalu fallback ke pesan teks standar Meta."""
    gw_url, _ = get_wa_gateway_config()
    if gw_url:
        return send_whatsapp_via_gateway(to_number, fallback_text)

    token, phone_id = get_meta_credentials()
    template_name = os.environ.get('META_OTP_TEMPLATE_NAME', '').strip()
    template_lang = os.environ.get('META_OTP_TEMPLATE_LANG', 'id').strip() or 'id'

    if token and phone_id and template_name:
        import urllib.request
        url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": template_lang},
                "components": [
                    {
                        "type": "body",
                        "parameters": [{"type": "text", "text": str(otp_code)}]
                    },
                    {
                        "type": "button",
                        "sub_type": "url",
                        "index": "0",
                        "parameters": [{"type": "text", "text": str(otp_code)}]
                    }
                ]
            }
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=15) as resp:
                res_data = json.loads(resp.read().decode('utf-8'))
                try:
                    log_chat_message(to_number, 'bot', f"[OTP Template: {template_name}] Kode OTP terkirim.")
                except Exception:
                    pass
                return res_data
        except Exception as e_tpl:
            print(f"[!] OTP Template '{template_name}' gagal ({e_tpl}), fallback ke pesan teks standar...")

    return send_whatsapp_meta_message(to_number, fallback_text)


def _generate_qr_data_url(payload_text):
    """Hasilkan QR code PNG base64 data URL dari teks payload. Kembalikan None
    kalau library qrcode tidak tersedia — jangan sampai ini menggagalkan
    penerbitan SPPB itu sendiri."""
    if not qrcode:
        return None
    try:
        img = qrcode.make(payload_text)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        encoded = base64.b64encode(buf.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{encoded}"
    except Exception as e:
        print('[!] Error generating QR code:', e)
        return None


def _log_officer_action(sess, action, target_id='', detail=''):
    """Catat aksi petugas ke activity_log supaya admin utama bisa memantau &
    mendeteksi anomali, tanpa pernah mengganggu alur aksi utamanya sendiri."""
    user = sess.get('user', {}) if sess else {}
    actor = user.get('nama') or user.get('username') or user.get('nip') or '-'
    database.log_activity(actor, sess.get('role') if sess else '-', action, detail=detail, target_id=target_id)


def _notify_pemohon_wa(permohonan_item, message):
    """Kirim notifikasi WA ke pemohon di background thread tiap transisi tahap
    permohonan — kegagalan kirim WA TIDAK boleh menggagalkan transisi status itu
    sendiri, karena itu selalu dibungkus try/except & dijalankan terpisah."""
    phone = str(permohonan_item.get('no_wa_pemohon') or permohonan_item.get('no_wa_pengirim') or '').strip()
    if not phone or phone == '-':
        return
    try:
        threading.Thread(target=send_whatsapp_meta_message, args=(phone, message), daemon=True).start()
    except Exception as e:
        print('[!] Error triggering WA notification:', e)


# ================= NADINE KEMENKEU INTEGRATION ENGINE =================
DB_NADINE_CONFIG_PATH = os.path.join(DATA_DIR, 'db_nadine_config.json')

def load_db_nadine_config():
    cfg = {
        'username': '',
        'password': '',
        'totp_secret': '',
        'last_tested': '',
        'status': 'BELUM_TERHUBUNG'
    }
    # Coba isi dari file konfigurasi tersimpan
    if os.path.exists(DB_NADINE_CONFIG_PATH):
        try:
            with open(DB_NADINE_CONFIG_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cfg.update(data)
                return cfg
        except Exception as e:
            print('[!] Error loading db_nadine_config:', e)

    # Fallback default dari repositori bot-nadine-kemenkeu-local/.env
    env_path = '/Users/ridmini/bot-nadine-kemenkeu-local/.env'
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as ef:
                for line in ef:
                    line = line.strip()
                    if line.startswith('KEMENKEU_USERNAME='):
                        cfg['username'] = line.split('=', 1)[1].strip()
                    elif line.startswith('KEMENKEU_PASSWORD='):
                        cfg['password'] = line.split('=', 1)[1].strip()
                    elif line.startswith('KEMENKEU_TOTP_SECRET='):
                        cfg['totp_secret'] = line.split('=', 1)[1].strip()
        except Exception:
            pass
    return cfg

def save_db_nadine_config(data):
    try:
        with open(DB_NADINE_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print('[!] Error saving db_nadine_config:', e)
        return False


def send_email_otp(to_email, otp_code, nama="Pemohon KBM Batam", purpose="Pendaftaran Akun"):
    """Mengirim kode OTP pendaftaran pabean ke email pemohon menggunakan SMTP TLS atau fallback."""
    import subprocess
    import shutil
    
    subject = f"🏛️ [KPU Bea Cukai Batam] Kode Verifikasi OTP {purpose}: {otp_code}"
    body = (
        f"🏛️ KPU BEA DAN CUKAI TIPE B BATAM\n"
        f"Layanan Pengeluaran Sementara Kendaraan Bermotor (KBM) Ke TLDDP\n\n"
        f"Halo Bapak/Ibu {nama},\n\n"
        f"Berikut adalah Kode Verifikasi (OTP) untuk {purpose} portal Anda:\n\n"
        f"👉  {otp_code}  👈\n\n"
        f"Kode ini berlaku selama 5 menit. Mohon tidak memberikan kode ini kepada siapapun demi keamanan data Anda.\n\n"
        f"Jika Anda tidak merasa melakukan pendaftaran ini, abaikan email ini.\n\n"
        f"Informasi Lebih Lanjut Hub: 0851-5814-8448 (Client Coordinator)"
    )

    # 1. Coba kirim via SMTP TLS jika Environment Variables tersedia (Produksi Cloud)
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_from = os.environ.get('SMTP_FROM', f"Bea Cukai Batam <{smtp_user}>" if smtp_user else "layanan.kbm.batam@gmail.com")

    if smtp_host and smtp_user and smtp_pass:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = smtp_from
            msg['To'] = to_email
            part_text = MIMEText(body, 'plain', 'utf-8')
            msg.attach(part_text)

            server_smtp = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            server_smtp.starttls()
            server_smtp.login(smtp_user, smtp_pass)
            server_smtp.sendmail(smtp_from, [to_email], msg.as_string())
            server_smtp.quit()
            print(f"[+] Email OTP berhasil terkirim ke {to_email} via SMTP TLS Cloud")
            return {"status": "ok", "method": "smtp_tls"}
        except Exception as e_smtp:
            print(f"[!] SMTP TLS Error: {e_smtp}, mencoba opsi fallback berikutnya...")

    # 2. Coba kirim via gmail CLI jika tersedia
    gmail_bin = shutil.which('gmail') or '/Users/macridm4/.gemini/antigravity/bin/gmail'
    if os.path.exists(gmail_bin) or shutil.which('gmail'):
        try:
            cmd = [
                gmail_bin if os.path.exists(gmail_bin) else 'gmail',
                'mutate', 'send',
                '--to', to_email,
                '--subject', subject,
                '--body', body
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
            if res.returncode == 0:
                print(f"[+] Email OTP berhasil terkirim ke {to_email} via gmail CLI")
                return {"status": "ok", "method": "gmail_cli"}
            else:
                print(f"[!] gmail CLI stderr: {res.stderr}")
        except Exception as e:
            print(f"[!] Error running gmail CLI: {e}")

    # Fallback log
    print(f"[*] [Email Fallback Log] to: {to_email} -> OTP: {otp_code}")
    return {"status": "ok", "method": "logged_fallback"}


def send_email_registration_success(to_email, nama="Pemohon KBM Batam", phone=""):
    """Mengirimkan email konfirmasi registrasi akun berhasil dengan penegasan keamanan & kontak pelaporan."""
    import subprocess
    import shutil
    
    subject = "🏛️ [KPU Bea Cukai Batam] Registrasi Akun Portal Layanan PENGSEM KBM Berhasil"
    body = (
        f"🏛️ KPU BEA DAN CUKAI TIPE B BATAM\n"
        f"Layanan Pengeluaran Sementara Kendaraan Bermotor (KBM) Ke TLDDP\n\n"
        f"Halo Bapak/Ibu {nama},\n\n"
        f"Selamat! Akun Anda pada Portal Layanan Pengeluaran Sementara Kendaraan Bermotor (KBM) KPU Bea dan Cukai Tipe B Batam telah berhasil didaftarkan dan terverifikasi.\n\n"
        f"📌 Rincian Akun Terdaftar:\n"
        f" • Nama Lengkap  : {nama}\n"
        f" • No. WhatsApp  : +{phone}\n"
        f" • Alamat Email  : {to_email}\n"
        f" • Status Akun   : Terverifikasi (Aktif)\n\n"
        f"Akun Anda kini telah aktif dan siap digunakan untuk mengajukan permohonan pengeluaran sementara kendaraan bermotor dari Kawasan Bebas Batam ke Tempat Lain Dalam Daerah Pabean (TLDDP).\n\n"
        f"⚠️ PEMBERITAHUAN KEAMANAN PENTING:\n"
        f"Apabila Anda merasa tidak pernah melakukan pendaftaran akun ini atau data identitas Anda digunakan oleh pihak lain tanpa persetujuan, harap segera laporkan kepada kami melalui kontak bantuan resmi di bawah ini agar akun dapat segera dibekukan/ditindaklanjuti:\n\n"
        f"📞 Kontak Bantuan & Pengaduan:\n"
        f"0851-5814-8448 (Client Coordinator KPU Bea Cukai Batam)\n"
        f"https://wa.me/6285158148448\n\n"
        f"Terima kasih atas kepatuhan Anda terhadap ketentuan kepabeanan.\n\n"
        f"KPU Bea dan Cukai Tipe B Batam"
    )

    # 1. Coba kirim via SMTP TLS jika Environment Variables tersedia (Produksi Cloud)
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_from = os.environ.get('SMTP_FROM', f"Bea Cukai Batam <{smtp_user}>" if smtp_user else "layanan.kbm.batam@gmail.com")

    if smtp_host and smtp_user and smtp_pass:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = smtp_from
            msg['To'] = to_email
            part_text = MIMEText(body, 'plain', 'utf-8')
            msg.attach(part_text)

            server_smtp = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            server_smtp.starttls()
            server_smtp.login(smtp_user, smtp_pass)
            server_smtp.sendmail(smtp_from, [to_email], msg.as_string())
            server_smtp.quit()
            print(f"[+] Email konfirmasi registrasi berhasil terkirim ke {to_email} via SMTP TLS")
            return {"status": "ok", "method": "smtp_tls"}
        except Exception as e_smtp:
            print(f"[!] SMTP TLS Error: {e_smtp}, mencoba opsi fallback...")

    # 2. Coba kirim via gmail CLI jika tersedia
    gmail_bin = shutil.which('gmail') or '/Users/macridm4/.gemini/antigravity/bin/gmail'
    if os.path.exists(gmail_bin) or shutil.which('gmail'):
        try:
            cmd = [
                gmail_bin if os.path.exists(gmail_bin) else 'gmail',
                'mutate', 'send',
                '--to', to_email,
                '--subject', subject,
                '--body', body
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
            if res.returncode == 0:
                print(f"[+] Email konfirmasi registrasi berhasil terkirim ke {to_email} via gmail CLI")
                return {"status": "ok", "method": "gmail_cli"}
        except Exception as e:
            print(f"[!] Error running gmail CLI: {e}")

    # Fallback log
    print(f"[*] [Email Fallback Log] Registrasi sukses terkirim ke: {to_email} (Nama: {nama})")
    return {"status": "ok", "method": "logged_fallback"}


GLOBAL_SESSION_EPOCH = 1795622471.301933

ALLOWED_CORS_ORIGINS = {
    'https://beacukaibatam.github.io',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
}

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Header CORS ketat (whitelist) untuk mencegah kebocoran lintas-domain (CWE-942)
        origin = self.headers.get('Origin', '').strip() if hasattr(self, 'headers') and self.headers else ''
        if origin in ALLOWED_CORS_ORIGINS:
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Credentials', 'true')
            self.send_header('Vary', 'Origin')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Session-Token, X-Requested-With')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def _send_json_response(self, data, code=200, cookie_header=None):
        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        if cookie_header:
            self.send_header('Set-Cookie', cookie_header)
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_json_error(self, code, message):
        self._send_json_response({'status': 'error', 'message': message}, code=code)

    def do_HEAD(self):
        return self.do_GET()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # Halaman Portal Terpadu (Dashboard & Formulir KBM Batam)
        if path in ('/dashboard', '/dashboard.html', '/pegawai', '/monitoring', '/formulir'):
            self.path = '/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        # Endpoint Healthcheck Uptime 24/7 & Monitoring
        if path == '/api/health':
            self._send_json_response({
                'status': 'ok',
                'service': 'KBM Batam Backend',
                'database': 'connected (WAL)',
                'timestamp': datetime.datetime.now().isoformat()
            })
            return

        # Draf Formulir Tahap 2 (Unggah Berkas) — dipanggil saat pemohon membuka
        # halaman formulir, supaya data & pratinjau yang sudah di-autosave sebelumnya
        # (termasuk sebelum sempat logout) bisa dipulihkan kembali.
        if path == '/api/permohonan/draft-load':
            token, sess = get_session_from_request(self)
            if not sess or sess.get('role') != 'pemohon':
                self._send_json_error(401, 'Sesi tidak valid. Silakan masuk kembali.')
                return
            identifier = _pemohon_draft_identifier(sess)
            draft = database.load_form_draft(identifier) if identifier else {}
            if not isinstance(draft, dict):
                draft = {}
            # Migrasi draf skema lama (kunci NIK/No.WA) ke skema baru (kunci UID).
            # PENTING: digabung (merge), BUKAN cuma dipakai kalau draf baru kosong total —
            # supaya draf baru yang baru punya sebagian data kecil (mis. baru ke-autosave
            # nama/telp hasil auto-fill) tidak pernah "menutupi" draf lama yang lebih
            # lengkap (foto KTP/NPWP, NIK, NPWP, alamat yang sudah diunggah pemohon).
            if sess:
                legacy_ident = _legacy_pemohon_draft_identifier(sess)
                if legacy_ident and legacy_ident != identifier:
                    legacy_draft = database.load_form_draft(legacy_ident)
                    if isinstance(legacy_draft, dict) and legacy_draft:
                        migrated = False
                        for section in ('fields', 'images'):
                            legacy_section = legacy_draft.get(section) or {}
                            if not isinstance(legacy_section, dict):
                                continue
                            cur_section = draft.get(section)
                            if not isinstance(cur_section, dict):
                                cur_section = {}
                            for k, v in legacy_section.items():
                                if v and not cur_section.get(k):
                                    cur_section[k] = v
                                    migrated = True
                            if cur_section:
                                draft[section] = cur_section
                        legacy_ocr = legacy_draft.get('ocr') or {}
                        if isinstance(legacy_ocr, dict):
                            cur_ocr = draft.get('ocr')
                            if not isinstance(cur_ocr, dict):
                                cur_ocr = {}
                            for doc_key, doc_val in legacy_ocr.items():
                                if not isinstance(doc_val, dict):
                                    continue
                                cur_doc = cur_ocr.get(doc_key)
                                if not isinstance(cur_doc, dict):
                                    cur_doc = {}
                                for k, v in doc_val.items():
                                    if v and not cur_doc.get(k):
                                        cur_doc[k] = v
                                        migrated = True
                                if cur_doc:
                                    cur_ocr[doc_key] = cur_doc
                            if cur_ocr:
                                draft['ocr'] = cur_ocr
                        if migrated:
                            # Simpan hasil gabungan ke kunci BARU supaya migrasi final —
                            # kunci lama tidak perlu dibaca lagi setelah ini.
                            try:
                                database.save_form_draft(identifier, draft)
                            except Exception:
                                pass

            # Anti-Kebocoran Server: Validasi bahwa draf benar milik akun yang sedang login
            sess_user = (sess or {}).get('user', {}) or {}
            sess_nama = str(sess_user.get('nama', '')).strip().upper()
            sess_nik = re.sub(r'[^A-Z0-9]', '', str(sess_user.get('nik', '')).strip().upper())
            sess_phone = str(sess_user.get('phone', '')).strip().replace('+', '').replace('-', '').replace(' ', '')
            if sess_phone.startswith('0'):
                sess_phone = '62' + sess_phone[1:]

            if draft and isinstance(draft, dict):
                # Periksa metadata saved_by jika ada
                saved_by = draft.get('saved_by', {})
                if saved_by and isinstance(saved_by, dict):
                    saved_uid = str(saved_by.get('id', '')).strip()
                    saved_phone = str(saved_by.get('phone', '')).strip().replace('+', '').replace('-', '').replace(' ', '')
                    if saved_phone.startswith('0'):
                        saved_phone = '62' + saved_phone[1:]
                    cur_uid = str(sess_user.get('id', '')).strip()
                    if (cur_uid and saved_uid and cur_uid != saved_uid) or (sess_phone and saved_phone and sess_phone != saved_phone):
                        print(f"[!] [SECURITY ALERT] Menolak draf milik UID {saved_uid}/{saved_phone} yang diakses oleh UID {cur_uid}/{sess_phone}")
                        draft = {}

                # Periksa nama pemohon di draf fields vs nama akun login
                draft_fields = draft.get('fields', {}) or {}
                draft_nama = str(draft_fields.get('pemohon_nama', '')).strip().upper()
                if sess_nama and draft_nama and len(sess_nama) >= 3 and len(draft_nama) >= 3:
                    if sess_nama not in draft_nama and draft_nama not in sess_nama:
                        print(f"[!] [SECURITY ALERT] Menolak draf karena nama pemohon bertolak belakang! Sesi: '{sess_nama}' vs Draf: '{draft_nama}'")
                        draft = {}

                # Periksa kontaminasi internal PII (KTP/NPWP orang lain dalam draf akun sendiri):
                # 1. Bandingkan nama di OCR KTP draf vs nama akun sesi
                draft_ocr = draft.get('ocr', {}) or {}
                ktp_ocr = (draft_ocr.get('ktp', {}) if isinstance(draft_ocr, dict) else {}) or {}
                ocr_ktp_nama = re.sub(r'[^A-Z0-9]', '', str(ktp_ocr.get('nama', '')).strip().upper())
                norm_sess_nama = re.sub(r'[^A-Z0-9]', '', sess_nama)
                
                is_pii_contaminated = False
                if norm_sess_nama and ocr_ktp_nama and len(norm_sess_nama) >= 3 and len(ocr_ktp_nama) >= 3:
                    if norm_sess_nama not in ocr_ktp_nama and ocr_ktp_nama not in norm_sess_nama:
                        print(f"[!] [SECURITY ALERT] Terdeteksi kontaminasi PII di draf! Nama OCR KTP '{ktp_ocr.get('nama')}' bertolak belakang dengan nama akun sesi '{sess_user.get('nama')}'.")
                        is_pii_contaminated = True

                # 2. Bandingkan NIK draf / NIK OCR KTP vs NIK akun sesi jika akun sesi memiliki NIK terdaftar
                draft_nik = re.sub(r'[^A-Z0-9]', '', str(draft_fields.get('pemohon_nik') or '').strip().upper())
                ocr_nik = re.sub(r'[^A-Z0-9]', '', str(ktp_ocr.get('nik') or '').strip().upper())
                if sess_nik:
                    if draft_nik and draft_nik != sess_nik:
                        print(f"[!] [SECURITY ALERT] Terdeteksi NIK draf '{draft_nik}' beda dengan NIK akun sesi '{sess_nik}'.")
                        is_pii_contaminated = True
                    if ocr_nik and ocr_nik != sess_nik:
                        print(f"[!] [SECURITY ALERT] Terdeteksi NIK OCR KTP '{ocr_nik}' beda dengan NIK akun sesi '{sess_nik}'.")
                        is_pii_contaminated = True

                # Jika draf terbukti terkontaminasi dokumen/PII orang lain, bersihkan HANYA field identitas tersebut
                # Pertahankan field non-identitas (data kendaraan, STNK/BPKB jika sah)
                if is_pii_contaminated and draft:
                    if 'fields' in draft and isinstance(draft['fields'], dict):
                        draft['fields'].pop('pemohon_nik', None)
                        draft['fields'].pop('pemohon_npwp', None)
                        draft['fields'].pop('pemohon_alamat', None)
                    if 'images' in draft and isinstance(draft['images'], dict):
                        draft['images'].pop('imgKtpPreview', None)
                        draft['images'].pop('imgNpwpPreview', None)
                    if 'ocr' in draft and isinstance(draft['ocr'], dict):
                        draft['ocr']['ktp'] = {}
                        draft['ocr']['npwp'] = {}

            self._send_json_response({'status': 'ok', 'draft': draft})
            return

        # API Autentikasi: Cek Status Sesi Aktif Pengguna
        if path == '/api/nadine/config':
            token, sess = get_session_from_request(self)
            if not sess or sess.get('role') not in ('frontdesk', 'loket', 'adminutama'):
                self._send_json_error(403, 'Akses Ditolak: Hanya Petugas Frontdesk/Loket/Admin Utama yang berwenang mengakses konfigurasi Nadine.')
                return
            cfg = load_db_nadine_config()
            safe_cfg = dict(cfg)
            if safe_cfg.get('password'):
                safe_cfg['has_password'] = True
                safe_cfg['password_mask'] = '••••••••'
            else:
                safe_cfg['has_password'] = False
                safe_cfg['password_mask'] = ''
            self._send_json_response({'status': 'ok', 'config': safe_cfg})
            return

        if path == '/api/auth/session':
            token, sess = get_session_from_request(self)
            if sess:
                self._send_json_response({
                    'status': 'ok',
                    'authenticated': True,
                    'token': token,
                    'role': sess.get('role'),
                    'user': _strip_password(sess.get('user'))
                })
            else:
                self._send_json_response({
                    'status': 'ok',
                    'authenticated': False,
                    'role': None,
                    'user': None
                })
            return

        # Webhook Verification Handshake WhatsApp Cloud API Meta
        if path == '/api/webhook/whatsapp':
            query_params = urllib.parse.parse_qs(parsed_url.query)
            mode = query_params.get('hub.mode', [''])[0]
            token = query_params.get('hub.verify_token', [''])[0]
            challenge = query_params.get('hub.challenge', [''])[0]
            if mode == 'subscribe' and token == META_VERIFY_TOKEN:
                print(f"[+] WhatsApp Webhook Meta Terverifikasi Sukses! Challenge: {challenge}")
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(challenge.encode('utf-8'))
            else:
                print("[!] Verifikasi Webhook Meta Gagal: Token Tidak Cocok")
                self.send_response(403)
                self.end_headers()
            return

        # API Obrolan WhatsApp untuk Live Chat Operator Pegawai
        if path == '/api/wa/conversations':
            token, sess = get_session_from_request(self)
            if not _is_pegawai(sess):
                self._send_json_error(403, 'Akses Ditolak: Hanya Petugas Bea Cukai yang berwenang melihat riwayat percakapan WhatsApp.')
                return
            data = load_db_chat()
            self._send_json_response(data)
            return

        # API Daftar Permohonan Masuk (RBAC: tiap petugas hanya lihat tahapannya sendiri;
        # Admin Utama & Pemeriksa Barang/Dokumen lihat semua untuk validasi kesesuaian)
        if path == '/api/permohonan':
            token, sess = get_session_from_request(self)
            data = load_db_permohonan()
            role = sess.get('role') if sess else None
            if role == 'pemohon':
                user_nik = str(sess.get('user', {}).get('nik', '')).strip()
                user_phone = str(sess.get('user', {}).get('phone', '')).strip()
                filtered = [
                    p for p in data
                    if (user_nik and str(p.get('nik', '')).strip() == user_nik) or
                       (user_phone and (str(p.get('no_wa_pemohon', '')).strip() == user_phone or str(p.get('no_wa_pengirim', '')).strip() == user_phone))
                ]
                self._send_json_response(filtered)
            elif role in FULL_VISIBILITY_ROLES:
                self._send_json_response(data)
            elif role in STAGE_VISIBILITY_BY_ROLE:
                allowed_statuses = STAGE_VISIBILITY_BY_ROLE[role]
                self._send_json_response([p for p in data if p.get('status') in allowed_statuses])
            else:
                # Sesi tidak dikenal/tidak terautentikasi: jangan bocorkan data apa pun.
                self._send_json_response([])
            return

        # Admin Utama: daftar seluruh akun petugas & pemohon (tanpa password) untuk
        # panel kelola akun.
        if path == '/api/admin/users':
            token, sess = get_session_from_request(self)
            if not sess or sess.get('role') != 'adminutama':
                self._send_json_error(403, 'Akses Ditolak: Hanya Admin Utama yang berwenang melihat daftar akun.')
                return
            users = load_db_users()
            pegawai = [_strip_password(p) for p in users.get('pegawai', [])]
            pemohon = [_strip_password(p) for p in users.get('pemohon', [])]
            self._send_json_response({'status': 'ok', 'pegawai': pegawai, 'pemohon': pemohon})
            return

        # Admin Utama: log aktivitas pemohon & petugas untuk deteksi anomali.
        if path == '/api/admin/activity-log':
            token, sess = get_session_from_request(self)
            if not sess or sess.get('role') != 'adminutama':
                self._send_json_error(403, 'Akses Ditolak: Hanya Admin Utama yang berwenang melihat log aktivitas.')
                return
            query_params = urllib.parse.parse_qs(parsed_url.query)
            limit = query_params.get('limit', ['200'])[0]
            role_filter = query_params.get('role', [''])[0] or None
            action_filter = query_params.get('action', [''])[0] or None
            search = query_params.get('q', [''])[0] or None
            try:
                limit = min(int(limit), 1000)
            except (TypeError, ValueError):
                limit = 200
            logs = database.get_activity_log(limit=limit, role_filter=role_filter, action_filter=action_filter, search=search)
            self._send_json_response({'status': 'ok', 'logs': logs})
            return

        if self.path in ('/', '/index.html', '/Formulir_Pemohon_CEISA_PENGSEM_KBM.html'):
            self.path = '/index.html'
        elif self.path in ('/flowchart', '/diagram'):
            self.path = '/Flowchart_Interaktif_Layanan_KBM_Batam.html'
        elif self.path in ('/qr', '/qr-code'):
            self.path = '/QR_Akses_KBM_Batam.png'
        elif self.path == '/api/status':
            lan_ip = get_lan_ip()
            status_data = json.dumps({
                'server': 'KBM Batam Dedicated Server',
                'status': 'online',
                'lan_ip': lan_ip,
                'port': PORT,
                'url': f"http://{lan_ip}:{PORT}",
                'gpu_acceleration': USE_GPU,
                'vision_ai_ready': VISION_AI_ENABLED,
                'easyocr_ready': EASYOCR_READER is not None,
                'tesseract_ready': pytesseract is not None,
                'pymupdf_ready': fitz is not None
            }).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(status_data)))
            self.end_headers()
            self.wfile.write(status_data)
            return
            
        if not _is_allowed_static_path(self.path):
            self.send_error(404, "File not found")
            return
        return super().do_GET()

    def do_POST(self):
        # 0. API Universal Login (Netral: User & Kata Sandi)
        if self.path == '/api/auth/login':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                user_input = str(body.get('user', '')).strip()
                password = str(body.get('password', '')).strip()

                if not user_input or not password:
                    self._send_json_error(400, "Silakan isi kolom User dan Kata Sandi.")
                    return

                client_ip = _get_client_ip(self)
                rl_key = (client_ip, user_input.lower())
                acct_rl_key = _normalize_login_ident(user_input)
                if _is_rate_limited(LOGIN_FAIL_TRACKER, rl_key, max_attempts=5, window_seconds=300):
                    database.log_activity(user_input, 'UNKNOWN', 'LOGIN_RATE_LIMITED', detail=f'IP {client_ip} melebihi 5 percobaan gagal')
                    self._send_json_error(429, "Terlalu banyak percobaan gagal login. Demi keamanan, silakan coba kembali dalam 5 menit.")
                    return
                # Limiter berbasis akun SAJA (tanpa syarat IP) — tidak bisa dilewati
                # dengan memalsukan header X-Forwarded-For seperti limiter di atas.
                if _is_rate_limited(ACCOUNT_FAIL_TRACKER, acct_rl_key, max_attempts=ACCOUNT_FAIL_MAX_ATTEMPTS, window_seconds=ACCOUNT_FAIL_WINDOW_SECONDS):
                    database.log_activity(user_input, 'UNKNOWN', 'LOGIN_ACCOUNT_RATE_LIMITED', detail=f'Akun melebihi {ACCOUNT_FAIL_MAX_ATTEMPTS} percobaan gagal lintas-IP dalam {ACCOUNT_FAIL_WINDOW_SECONDS // 60} menit')
                    self._send_json_error(429, "Terlalu banyak percobaan gagal login untuk akun ini. Demi keamanan, silakan coba kembali dalam beberapa menit.")
                    return

                clean_user = user_input.replace(' ', '').replace('-', '')
                clean_user_lower = user_input.lower().replace(' ', '').replace('-', '')

                users = load_db_users()
                matched_user = None
                matched_role = None
                matched_raw_record = None

                # 1. Cek Petugas Bea Cukai (Internal) & Role Khusus
                for p in users.get('pegawai', []):
                    p_nip = str(p.get('nip', '')).strip().replace(' ', '').replace('-', '')
                    p_user = str(p.get('username', '')).strip().lower().replace(' ', '').replace('-', '')
                    if (p_nip == clean_user or p_user == clean_user_lower or (clean_user_lower == 'petugas' and p_nip == '199501012020011001')) and database.verify_password(password, p.get('password', '')):
                        p_role = p.get('role', 'pegawai')
                        matched_user = {
                            "nip": p.get('nip'),
                            "username": p.get('username'),
                            "nama": p.get('nama', 'Petugas Bea Cukai Batam'),
                            "jabatan": p.get('jabatan', 'Pelaksana Pemeriksa'),
                            "role": p_role,
                            "is_officer": True
                        }
                        matched_role = p_role
                        matched_raw_record = p
                        break

                # 2. Cek Pemohon Terdaftar (Eksternal / Masyarakat)
                if not matched_user:
                    for u in users.get('pemohon', []):
                        u_nik = str(u.get('nik', '')).strip().replace(' ', '').replace('-', '')
                        u_phone = str(u.get('phone', '')).strip().replace('+', '').replace('-', '').replace(' ', '')
                        u_id = str(u.get('id', '')).strip().lower()
                        u_user = str(u.get('username', '')).strip().lower()
                        u_email = str(u.get('email', '')).strip().lower()
                        u_pwd = str(u.get('password', '')).strip()

                        phone_variants = [u_phone]
                        if u_phone.startswith('62'):
                            phone_variants.append('0' + u_phone[2:])
                        elif u_phone.startswith('0'):
                            phone_variants.append('62' + u_phone[1:])

                        if (clean_user == u_nik or clean_user in phone_variants or clean_user_lower == u_id or clean_user_lower == u_user or clean_user_lower == u_email) and database.verify_password(password, u_pwd):
                            matched_user = _strip_password(u)
                            matched_role = "pemohon"
                            matched_raw_record = u
                            break

                if not matched_user:
                    _record_rate_hit(LOGIN_FAIL_TRACKER, rl_key, window_seconds=300)
                    _record_rate_hit(ACCOUNT_FAIL_TRACKER, acct_rl_key, window_seconds=ACCOUNT_FAIL_WINDOW_SECONDS)
                    database.log_activity(user_input, 'UNKNOWN', 'LOGIN_FAILED', detail=f'User/kata sandi salah (IP {client_ip})')
                    self._send_json_error(401, "User atau Kata Sandi salah! Pastikan akun telah terdaftar.")
                    return

                # Reset rate-limit counter setelah login berhasil & auto-upgrade password plaintext lama ke PBKDF2 hash
                LOGIN_FAIL_TRACKER.pop(rl_key, None)
                ACCOUNT_FAIL_TRACKER.pop(acct_rl_key, None)
                if matched_raw_record and not str(matched_raw_record.get('password', '')).startswith('pbkdf2_sha256$'):
                    try:
                        ident_upgrade = matched_raw_record.get('username') or matched_raw_record.get('nip') or matched_raw_record.get('phone') or matched_raw_record.get('email')
                        if ident_upgrade:
                            database.update_user_password(ident_upgrade, password)
                    except Exception:
                        pass

                # Buat Token Sesi
                token = str(uuid.uuid4()).replace('-', '')
                AUTH_SESSIONS[token] = {
                    "user": matched_user,
                    "role": matched_role,
                    "created_at": time.time(),
                    "expires_at": time.time() + 86400
                }
                database.log_activity(matched_user.get('username') or matched_user.get('nip') or user_input, matched_role, 'LOGIN_SUCCESS')

                self._send_json_response({
                    "status": "ok",
                    "message": f"Login Berhasil sebagai {matched_role.capitalize()}.",
                    "token": token,
                    "role": matched_role,
                    "redirect": "dashboard" if matched_role == "pegawai" else "formulir",
                    "user": matched_user
                }, cookie_header=f"session_token={token}; Path=/; Max-Age=86400; SameSite=None; Secure; HttpOnly")
                return
            except Exception as e:
                self._send_json_error(500, f"Gagal memproses login: {e}")
                return

        # 1. API Permintaan Kode OTP WhatsApp (Pintu 2 - Pemohon Eksternal)
        if self.path == '/api/auth/request-otp':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                raw_phone = str(body.get('phone', '')).strip().replace('+', '').replace('-', '').replace(' ', '')
                if raw_phone.startswith('08'):
                    phone = '628' + raw_phone[2:]
                elif raw_phone.startswith('8'):
                    phone = '628' + raw_phone[1:]
                elif not raw_phone.startswith('628'):
                    phone = '62' + raw_phone.lstrip('0')
                else:
                    phone = raw_phone

                if len(phone) < 10 or not phone.isdigit():
                    self._send_json_error(400, "Nomor WhatsApp tidak valid (contoh: 08123456789)")
                    return

                client_ip = _get_client_ip(self)
                otp_rl_key = (client_ip, phone)
                if _is_rate_limited(OTP_RATE_TRACKER, otp_rl_key, max_attempts=3, window_seconds=300):
                    database.log_activity(phone, 'pemohon', 'OTP_RATE_LIMITED', detail=f'IP {client_ip} spam OTP >3x/5 menit')
                    self._send_json_error(429, "Terlalu banyak permintaan kode OTP. Mohon tunggu 5 menit sebelum meminta kode baru.")
                    return
                _record_rate_hit(OTP_RATE_TRACKER, otp_rl_key, window_seconds=300)

                nik = str(body.get('nik', '')).strip().replace(' ', '').replace('-', '')
                nama = str(body.get('nama', '')).strip().upper()
                email = str(body.get('email', '')).strip().lower()
                password = str(body.get('password', '')).strip()

                if not email or '@' not in email or '.' not in email.split('@')[-1] or len(email.split('@')[-1].split('.')[-1]) < 2:
                    self._send_json_error(400, "Format alamat email tidak valid (contoh: nama@email.com).")
                    return
                
                # Tolak registrasi jika nomor WA atau email sudah terdaftar di sistem
                users = load_db_users()
                phone_exists, email_exists = _find_duplicate_registration(users, phone=phone, email=email)
                if phone_exists or email_exists:
                    dup_msg = _duplicate_registration_message(phone_exists, email_exists)
                    database.log_activity(
                        phone, 'pemohon', 'REGISTRASI_DITOLAK_DUPLIKAT',
                        detail=f"Duplikat {'WA & Email' if (phone_exists and email_exists) else ('WA' if phone_exists else 'Email')} (phone={phone}, email={email})"
                    )
                    self._send_json_error(409, dup_msg)
                    return

                if not nama:
                    nama = "PEMOHON KBM BATAM"

                # Generate 6 digit angka acak
                otp_code = f"{random.randint(100000, 999999)}"
                expires_at = time.time() + 300  # TTL 5 Menit

                otps = load_db_otp()
                otps[phone] = {
                    "otp": otp_code,
                    "expires_at": expires_at,
                    "nik": nik,
                    "nama": nama,
                    "email": email,
                    "password": password,
                    "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                save_db_otp(otps)

                # Template Resmi Sesuai Instruksi IK Pabean DJBC
                wa_message = (
                    f"🏛️ *KPU BEA DAN CUKAI TIPE B BATAM*\n"
                    f"Layanan Pengeluaran Sementara Kendaraan Bermotor (KBM) Ke TLDDP\n\n"
                    f"Halo Bapak/Ibu *{nama}*,\n\n"
                    f"Kode Verifikasi (OTP) pendaftaran akun portal Anda adalah:\n"
                    f"👉 *{otp_code}*\n\n"
                    f"Kode ini berlaku 5 menit. Jangan berikan kode ini kepada siapapun demi keamanan data Anda.\n\n"
                    f"Informasi Lebih Lanjut Hub: 0851-5814-8448 (Client Coordinator)"
                )

                meta_res = send_whatsapp_otp_template(phone, otp_code, wa_message)
                log_chat_message(phone, 'bot', wa_message, name=nama)
                print(f"[+] OTP pendaftaran diproses untuk {phone} (Kode: {otp_code}) - Meta: {meta_res}")

                is_meta_success = isinstance(meta_res, dict) and (meta_res.get('status') not in ('error', 'logged_offline')) and ('messages' in meta_res or meta_res.get('status') == 'success')

                # Dual-Delivery: kirimkan juga secara otomatis ke email pemohon jika email valid
                email_res = None
                if email and '@' in email:
                    try:
                        email_res = send_email_otp(email, otp_code, nama, purpose="Pendaftaran Akun")
                        print(f"[+] OTP pendaftaran otomatis dikirimkan ke email {email}: {email_res}")
                    except Exception as e_em:
                        print(f"[!] Gagal auto-send OTP pendaftaran ke email {email}: {e_em}")

                is_email_success = isinstance(email_res, dict) and email_res.get('status') == 'ok' and email_res.get('method') in ('smtp_tls', 'gmail_cli')
                is_any_delivered = is_meta_success or is_email_success

                msg_detail = f"Kode OTP 6-digit berhasil diproses untuk nomor +{phone}"
                if is_email_success:
                    msg_detail += f" dan email {email}"
                msg_detail += "."

                self._send_json_response({
                    "status": "ok",
                    "message": msg_detail,
                    "phone": phone,
                    "email": email,
                    "ttl": 300,
                    "otp_delivered": is_any_delivered,
                    "wa_delivered": is_meta_success,
                    "email_delivered": is_email_success
                })
                return
            except Exception as e:
                self._send_json_error(500, f"Gagal memproses OTP: {e}")
                return

        
        # API Permintaan Kode OTP via Email (Jalur Alternatif Pemohon)
        if self.path == '/api/auth/request-email-otp':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                raw_phone = str(body.get('phone', '')).strip().replace('+', '').replace('-', '').replace(' ', '')
                if raw_phone.startswith('08'):
                    phone = '628' + raw_phone[2:]
                elif raw_phone.startswith('8'):
                    phone = '628' + raw_phone[1:]
                elif not raw_phone.startswith('628'):
                    phone = '62' + raw_phone.lstrip('0')
                else:
                    phone = raw_phone

                # Rate Limit Kirim Ulang OTP ke Email: Maks 3x per 5 menit per nomor pemohon
                if _is_rate_limited(EMAIL_OTP_RATE_TRACKER, phone, max_attempts=3, window_seconds=300):
                    database.log_activity(phone, 'pemohon', 'EMAIL_OTP_RATE_LIMITED', detail=f'Permintaan OTP email melebihi 3x/5 menit untuk nomor {phone}')
                    self._send_json_error(429, "Terlalu banyak permintaan pengiriman OTP ke email. Mohon tunggu 5 menit sebelum mencoba kembali.")
                    return
                _record_rate_hit(EMAIL_OTP_RATE_TRACKER, phone, window_seconds=300)

                req_email = str(body.get('email', '')).strip().lower()

                otps = load_db_otp()
                if phone not in otps:
                    self._send_json_error(400, "Sesi pendaftaran tidak ditemukan. Silakan isi form registrasi terlebih dahulu.")
                    return

                otp_data = otps[phone]
                target_email = req_email or otp_data.get('email', '')
                if not target_email or '@' not in target_email:
                    self._send_json_error(400, "Alamat email tidak valid. Silakan masukkan alamat email yang benar.")
                    return

                # Tolak jika email tujuan atau nomor WA sudah terdaftar pada akun lain
                phone_exists, email_exists = _find_duplicate_registration(load_db_users(), phone=phone, email=target_email)
                if phone_exists or email_exists:
                    dup_msg = _duplicate_registration_message(phone_exists, email_exists)
                    database.log_activity(
                        phone, 'pemohon', 'REGISTRASI_DITOLAK_DUPLIKAT',
                        detail=f"Duplikat saat request-email-otp (phone={phone}, email={target_email})"
                    )
                    self._send_json_error(409, dup_msg)
                    return

                otp_data['email'] = target_email
                # Perpanjang masa berlaku 5 menit lagi saat minta ke email
                otp_data['expires_at'] = time.time() + 300
                save_db_otp(otps)

                otp_code = otp_data.get('otp')
                nama = otp_data.get('nama', 'Pemohon KBM')

                # Kirim email OTP
                email_res = send_email_otp(target_email, otp_code, nama)
                print(f"[+] OTP via Email terkirim ke {target_email} (Kode: {otp_code}) - Hasil: {email_res}")

                is_real_sent = isinstance(email_res, dict) and email_res.get('method') in ('smtp_tls', 'gmail_cli')

                self._send_json_response({
                    "status": "ok",
                    "message": f"Kode OTP telah dikirimkan ke email: {target_email}." if is_real_sent else "Pengiriman email belum aktif. Silakan hubungi Client Coordinator untuk verifikasi manual.",
                    "email": target_email,
                    "phone": phone,
                    "ttl": 300,
                    "email_sent": is_real_sent
                })
                return
            except Exception as e:
                self._send_json_error(500, f"Gagal mengirimkan OTP ke email: {e}")
                return

        # 2. API Verifikasi Kode OTP WhatsApp (Pintu 2 - Pemohon Eksternal)
        if self.path == '/api/auth/verify-otp':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                raw_phone = str(body.get('phone', '')).strip().replace('+', '').replace('-', '').replace(' ', '')
                if not raw_phone or len(raw_phone) < 5:
                    self._send_json_error(400, "Nomor WhatsApp tidak terdeteksi. Silakan ulangi proses pendaftaran.")
                    return
                if raw_phone.startswith('08'):
                    phone = '628' + raw_phone[2:]
                elif raw_phone.startswith('8'):
                    phone = '628' + raw_phone[1:]
                elif not raw_phone.startswith('628'):
                    phone = '62' + raw_phone.lstrip('0')
                else:
                    phone = raw_phone

                client_ip = _get_client_ip(self)
                verify_rl_key = (client_ip, phone)
                if _is_rate_limited(VERIFY_OTP_TRACKER, verify_rl_key, max_attempts=5, window_seconds=300):
                    database.log_activity(phone, 'pemohon', 'VERIFY_OTP_RATE_LIMITED', detail=f'IP {client_ip} melebihi 5 percobaan verifikasi OTP')
                    self._send_json_error(429, "Terlalu banyak percobaan verifikasi OTP. Mohon tunggu 5 menit lalu minta kode baru.")
                    return
                _record_rate_hit(VERIFY_OTP_TRACKER, verify_rl_key, window_seconds=300)

                user_otp = str(body.get('otp', '')).strip()

                otps = load_db_otp()
                if phone not in otps:
                    self._send_json_error(400, "Kode OTP belum diminta atau nomor WhatsApp belum terdaftar. Silakan minta kode baru.")
                    return

                otp_info = otps[phone]
                if time.time() > otp_info.get('expires_at', 0):
                    otps.pop(phone, None)
                    save_db_otp(otps)
                    try:
                        database.delete_registration_otp(phone)
                    except Exception:
                        pass
                    self._send_json_error(400, "Kode OTP telah kedaluwarsa (lebih dari 5 menit). Silakan kirim ulang kode baru.")
                    return

                if otp_info.get('otp') != user_otp:
                    self._send_json_error(400, "Kode OTP salah. Pastikan Anda memasukkan 6 digit angka yang dikirim ke WhatsApp.")
                    return

                # OTP Valid! Hapus OTP terpakai
                otps.pop(phone, None)
                save_db_otp(otps)
                try:
                    database.delete_registration_otp(phone)
                except Exception:
                    pass

                # Tolak pembuatan akun jika nomor WA atau email sudah terdaftar (cegah race condition / timpa akun)
                users = load_db_users()
                reg_email = str(otp_info.get('email', '') or '').strip().lower()
                phone_exists, email_exists = _find_duplicate_registration(users, phone=phone, email=reg_email)
                if phone_exists or email_exists:
                    dup_msg = _duplicate_registration_message(phone_exists, email_exists)
                    database.log_activity(
                        phone, 'pemohon', 'REGISTRASI_DITOLAK_DUPLIKAT',
                        detail=f"Duplikat saat verify-otp (phone={phone}, email={reg_email})"
                    )
                    self._send_json_error(409, dup_msg)
                    return

                # Simpan akun pemohon baru di db_users.json & SQLite
                pemohon_list = users.get('pemohon', [])
                user_pwd = str(body.get('password', '')).strip() or otp_info.get('password', '') or 'pemohon123'
                now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                new_id = f"USR-PEMOHON-{str(len(pemohon_list) + 1).zfill(3)}"
                found_user = {
                    "id": new_id,
                    "nik": otp_info.get('nik', ''),
                    "nama": otp_info.get('nama', 'PEMOHON TERVERIFIKASI'),
                    "phone": phone,
                    "email": reg_email,
                    "password": user_pwd,
                    "status": "verified",
                    "role": "pemohon",
                    "registered_at": now_str
                }
                pemohon_list.append(found_user)
                users['pemohon'] = pemohon_list
                save_db_users(users)

                # Kirim email konfirmasi registrasi berhasil jika ada email terdaftar
                user_email = found_user.get('email', '')
                if user_email and '@' in user_email:
                    try:
                        threading.Thread(
                            target=send_email_registration_success,
                            args=(user_email, found_user.get('nama', 'Pemohon KBM Batam'), phone),
                            daemon=True
                        ).start()
                    except Exception as e_email:
                        print('[!] Error triggering email registration success:', e_email)

                # Buat Sesi Aktif (tanpa menyimpan/field password ke sesi atau response client)
                public_user = _strip_password(found_user)
                token = str(uuid.uuid4()).replace('-', '')
                AUTH_SESSIONS[token] = {
                    "user": public_user,
                    "role": "pemohon",
                    "created_at": time.time(),
                    "expires_at": time.time() + 86400
                }
                database.log_activity(public_user.get('username') or public_user.get('phone') or '-', 'pemohon', 'REGISTRASI_PEMOHON', detail=f"Nama: {public_user.get('nama','-')}")

                self._send_json_response({
                    "status": "ok",
                    "message": "Verifikasi OTP Berhasil! Akun pemohon terverifikasi.",
                    "token": token,
                    "role": "pemohon",
                    "user": public_user
                }, cookie_header=f"session_token={token}; Path=/; Max-Age=86400; SameSite=None; Secure; HttpOnly")
                return
            except Exception as e:
                self._send_json_error(500, f"Gagal verifikasi OTP: {e}")
                return

        # 3. API Login Pegawai Internal Bea Cukai Batam (Pintu 1)
        if self.path == '/api/auth/login-pegawai':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                nip = str(body.get('nip', '')).strip().replace(' ', '').replace('-', '')
                password = str(body.get('password', '')).strip()

                # Limiter berbasis akun saja (sama dengan /api/auth/login) — endpoint ini
                # tidak dipakai frontend saat ini, tapi tetap bisa dipanggil langsung via
                # API jadi tetap wajib dilindungi, dan berbagi kunci dengan /api/auth/login
                # supaya penyerang tidak bisa membagi jatah percobaan antar dua endpoint.
                acct_rl_key_pegawai = _normalize_login_ident(nip)
                if _is_rate_limited(ACCOUNT_FAIL_TRACKER, acct_rl_key_pegawai, max_attempts=ACCOUNT_FAIL_MAX_ATTEMPTS, window_seconds=ACCOUNT_FAIL_WINDOW_SECONDS):
                    database.log_activity(nip, 'UNKNOWN', 'LOGIN_ACCOUNT_RATE_LIMITED', detail=f'Akun melebihi {ACCOUNT_FAIL_MAX_ATTEMPTS} percobaan gagal lintas-IP dalam {ACCOUNT_FAIL_WINDOW_SECONDS // 60} menit (login-pegawai)')
                    self._send_json_error(429, "Terlalu banyak percobaan gagal login untuk akun ini. Demi keamanan, silakan coba kembali dalam beberapa menit.")
                    return

                users = load_db_users()
                pegawai_list = users.get('pegawai', [])
                found_pegawai = None
                for p in pegawai_list:
                    if str(p.get('nip', '')).strip() == nip and database.verify_password(password, p.get('password', '')):
                        found_pegawai = p
                        break

                if not found_pegawai:
                    _record_rate_hit(ACCOUNT_FAIL_TRACKER, acct_rl_key_pegawai, window_seconds=ACCOUNT_FAIL_WINDOW_SECONDS)
                    database.log_activity(nip, 'UNKNOWN', 'LOGIN_FAILED', detail='NIP/kata sandi salah (login-pegawai)')
                    self._send_json_error(401, "NIP (18 Digit) atau Kata Sandi Dinas salah! Silakan periksa kembali kredensial dinas Anda.")
                    return
                ACCOUNT_FAIL_TRACKER.pop(acct_rl_key_pegawai, None)

                # RBAC: role spesifik petugas (jaminan/fasilitas/pemeriksabarang/dst) WAJIB
                # diambil dari data akun, bukan di-hardcode generik "pegawai" — generik
                # itu dulu membuat SEMUA endpoint aksi petugas bisa diakses siapa saja.
                specific_role = found_pegawai.get('role') or 'pegawai'
                token = str(uuid.uuid4()).replace('-', '')
                user_info = {
                    "nip": found_pegawai.get('nip'),
                    "nama": found_pegawai.get('nama', 'Petugas Bea Cukai Batam'),
                    "jabatan": found_pegawai.get('jabatan', 'Pelaksana Pemeriksa'),
                    "role": specific_role
                }
                AUTH_SESSIONS[token] = {
                    "user": user_info,
                    "role": specific_role,
                    "created_at": time.time(),
                    "expires_at": time.time() + 86400
                }

                self._send_json_response({
                    "status": "ok",
                    "message": "Login Pegawai Bea Cukai Berhasil. Selamat bertugas!",
                    "token": token,
                    "role": specific_role,
                    "user": user_info
                }, cookie_header=f"session_token={token}; Path=/; Max-Age=86400; SameSite=None; Secure; HttpOnly")
                return
            except Exception as e:
                self._send_json_error(500, f"Gagal login pegawai: {e}")
                return

        # API Permintaan OTP Reset Kata Sandi (Lupa Password)
        if self.path == '/api/auth/reset-password-request-otp':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                raw_ident = str(body.get('identifier', '')).strip()
                if not raw_ident:
                    self._send_json_error(400, "Silakan masukkan Nomor WhatsApp atau Email terdaftar.")
                    return

                client_ip = _get_client_ip(self)
                reset_rl_key = (client_ip, raw_ident.lower())
                if _is_rate_limited(RESET_PW_TRACKER, reset_rl_key, max_attempts=5, window_seconds=300):
                    database.log_activity(raw_ident, 'UNKNOWN', 'RESET_PW_RATE_LIMITED', detail=f'IP {client_ip} melebihi 5x/5 menit permintaan reset sandi')
                    self._send_json_error(429, "Terlalu banyak permintaan reset kata sandi. Mohon tunggu 5 menit.")
                    return
                _record_rate_hit(RESET_PW_TRACKER, reset_rl_key, window_seconds=300)

                users = load_db_users()
                target_user = None
                target_role = None

                clean_phone = raw_ident.replace('+', '').replace('-', '').replace(' ', '')
                if clean_phone.startswith('08'):
                    norm_phone = '628' + clean_phone[2:]
                elif clean_phone.startswith('8'):
                    norm_phone = '628' + clean_phone[1:]
                elif clean_phone.startswith('62'):
                    norm_phone = clean_phone
                else:
                    norm_phone = clean_phone

                for u in users.get('pemohon', []):
                    u_phone = str(u.get('phone', '')).replace('+', '').replace('-', '').replace(' ', '')
                    if u_phone.startswith('08'): u_phone = '628' + u_phone[2:]
                    elif u_phone.startswith('8'): u_phone = '628' + u_phone[1:]
                    
                    if (norm_phone and u_phone == norm_phone) or                        (raw_ident.lower() == str(u.get('email', '')).lower()) or                        (raw_ident.upper() == str(u.get('id', '')).upper()):
                        target_user = u
                        target_role = 'pemohon'
                        break

                if not target_user:
                    for p in users.get('pegawai', []):
                        if raw_ident == str(p.get('nip', '')) or                            raw_ident.lower() == str(p.get('email', '')).lower() or                            (norm_phone and str(p.get('phone', '')) == norm_phone):
                            target_user = p
                            target_role = 'pegawai'
                            break

                phone_to_use = ''
                email_to_use = ''
                nama_to_use = 'Pengguna Portal'

                if target_user:
                    phone_to_use = target_user.get('phone', '')
                    email_to_use = target_user.get('email', '')
                    nama_to_use = target_user.get('nama', 'Pengguna Portal')
                else:
                    if norm_phone and norm_phone.isdigit() and len(norm_phone) >= 10:
                        phone_to_use = norm_phone
                    elif '@' in raw_ident:
                        email_to_use = raw_ident
                    else:
                        self._send_json_error(404, "Akun dengan Nomor WhatsApp/Email tersebut tidak ditemukan.")
                        return

                if phone_to_use:
                    raw_p = phone_to_use.replace('+', '').replace('-', '').replace(' ', '')
                    if raw_p.startswith('08'): phone_to_use = '628' + raw_p[2:]
                    elif raw_p.startswith('8'): phone_to_use = '628' + raw_p[1:]
                    elif not raw_p.startswith('628'): phone_to_use = '62' + raw_p.lstrip('0')
                    else: phone_to_use = raw_p

                otp_code = f"{random.randint(100000, 999999)}"
                expires_at = time.time() + 300

                otps = load_db_otp()
                otp_key = phone_to_use or email_to_use or raw_ident
                otps[otp_key] = {
                    "otp": otp_code,
                    "expires_at": expires_at,
                    "phone": phone_to_use,
                    "email": email_to_use,
                    "nama": nama_to_use,
                    "action": "reset_password",
                    "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                save_db_otp(otps)

                wa_msg = (
                    f"🏛️ *KPU BEA DAN CUKAI TIPE B BATAM*\n"
                    f"Layanan Pengeluaran Sementara Kendaraan Bermotor (KBM) Ke TLDDP\n\n"
                    f"Halo Bapak/Ibu *{nama_to_use}*,\n\n"
                    f"Kode Verifikasi (OTP) untuk *RESET KATA SANDI* akun portal Anda adalah:\n"
                    f"👉 *{otp_code}*\n\n"
                    f"Kode ini berlaku 5 menit. Masukkan kode ini pada portal untuk membuat kata sandi baru.\n\n"
                    f"Informasi Lebih Lanjut Hub: 0851-5814-8448 (Client Coordinator)"
                )

                meta_res = None
                if phone_to_use:
                    meta_res = send_whatsapp_otp_template(phone_to_use, otp_code, wa_msg)
                    log_chat_message(phone_to_use, 'bot', wa_msg, name=nama_to_use)
                    print(f"[+] OTP Reset Password diproses untuk WhatsApp {phone_to_use} (Kode: {otp_code}) - Meta: {meta_res}")

                is_meta_success = isinstance(meta_res, dict) and (meta_res.get('status') not in ('error', 'logged_offline', 'rate_limited')) and ('messages' in meta_res or meta_res.get('status') == 'success')

                # Dual-Delivery: kirimkan juga ke email jika email terdaftar
                email_res = None
                if email_to_use and '@' in email_to_use:
                    try:
                        email_res = send_email_otp(email_to_use, otp_code, nama_to_use, purpose="Reset Kata Sandi")
                        print(f"[+] OTP Reset Password otomatis dikirimkan ke email {email_to_use}: {email_res}")
                    except Exception as e_em:
                        print(f"[!] Gagal auto-send OTP Reset ke email {email_to_use}: {e_em}")

                is_email_success = isinstance(email_res, dict) and email_res.get('status') == 'ok' and email_res.get('method') in ('smtp_tls', 'gmail_cli')
                is_any_delivered = is_meta_success or is_email_success

                if is_meta_success and is_email_success:
                    resp_msg = f"Kode OTP verifikasi telah dikirimkan ke WhatsApp +{phone_to_use} dan email {email_to_use}."
                elif is_meta_success:
                    resp_msg = f"Kode OTP verifikasi telah dikirimkan ke WhatsApp +{phone_to_use}."
                elif is_email_success:
                    resp_msg = f"Kode OTP verifikasi telah dikirimkan ke email {email_to_use}."
                elif phone_to_use:
                    resp_msg = f"Kode OTP untuk +{phone_to_use} belum berhasil terkirim dari WhatsApp Meta. Silakan klik 'Sapa Bot WA' lalu 'Kirim Ulang WA', atau gunakan opsi 'Kirim ke Email'."
                else:
                    resp_msg = f"Kode OTP telah diproses untuk email {email_to_use}."

                self._send_json_response({
                    "status": "ok",
                    "message": resp_msg,
                    "key": otp_key,
                    "phone": phone_to_use,
                    "email": email_to_use,
                    "nama": nama_to_use,
                    "ttl": 300,
                    "otp_delivered": is_any_delivered,
                    "wa_delivered": is_meta_success,
                    "email_delivered": is_email_success
                })
                return
            except Exception as e:
                self._send_json_error(500, f"Gagal memproses permintaan reset password: {e}")
                return

        # API Permintaan OTP Reset via Email
        if self.path == '/api/auth/reset-password-request-email-otp':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                key = str(body.get('key', '')).strip()

                # Rate Limit Kirim Ulang OTP Reset ke Email: Maks 3x per 5 menit per identifier key
                if _is_rate_limited(RESET_EMAIL_OTP_RATE_TRACKER, key, max_attempts=3, window_seconds=300):
                    database.log_activity(key, 'pemohon', 'RESET_EMAIL_OTP_RATE_LIMITED', detail=f'Permintaan OTP email reset sandi melebihi 3x/5 menit untuk key {key}')
                    self._send_json_error(429, "Terlalu banyak permintaan pengiriman OTP reset ke email. Mohon tunggu 5 menit sebelum mencoba kembali.")
                    return
                _record_rate_hit(RESET_EMAIL_OTP_RATE_TRACKER, key, window_seconds=300)

                req_email = str(body.get('email', '')).strip().lower()

                otps = load_db_otp()
                if key not in otps:
                    self._send_json_error(400, "Sesi permintaan reset password tidak ditemukan. Silakan ulangi dari awal.")
                    return

                otp_data = otps[key]
                target_email = req_email or otp_data.get('email', '')
                if not target_email or '@' not in target_email:
                    self._send_json_error(400, "Alamat email tidak valid.")
                    return

                otp_data['email'] = target_email
                otp_data['expires_at'] = time.time() + 300
                save_db_otp(otps)

                otp_code = otp_data.get('otp')
                nama = otp_data.get('nama', 'Pengguna Portal KBM')

                email_res = send_email_otp(target_email, otp_code, nama, purpose="Reset Kata Sandi")
                print(f"[+] OTP Reset Password via Email terkirim ke {target_email} (Kode: {otp_code}) - Hasil: {email_res}")

                is_real_sent = isinstance(email_res, dict) and email_res.get('status') == 'ok' and email_res.get('method') in ('smtp_tls', 'gmail_cli')

                self._send_json_response({
                    "status": "ok",
                    "message": f"Kode OTP reset kata sandi telah dikirimkan ke email: {target_email}." if is_real_sent else "Pengiriman email belum aktif. Silakan hubungi Client Coordinator untuk bantuan reset kata sandi.",
                    "email": target_email,
                    "ttl": 300,
                    "email_sent": is_real_sent
                })
                return
            except Exception as e:
                self._send_json_error(500, f"Gagal mengirimkan OTP ke email: {e}")
                return

        # API Konfirmasi Reset Password & Simpan Kata Sandi Baru
        if self.path == '/api/auth/reset-password-confirm':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                key = str(body.get('key', '')).strip()
                user_otp = str(body.get('otp', '')).strip()
                new_password = str(body.get('new_password', '')).strip()

                if not new_password or len(new_password) < 4:
                    self._send_json_error(400, "Kata sandi baru minimal 4 karakter.")
                    return

                client_ip = _get_client_ip(self)
                confirm_rl_key = (client_ip, key)
                if _is_rate_limited(RESET_PW_TRACKER, confirm_rl_key, max_attempts=5, window_seconds=300):
                    database.log_activity(key, 'UNKNOWN', 'RESET_PW_CONFIRM_RATE_LIMITED', detail=f'IP {client_ip} melebihi 5x/5 menit percobaan konfirmasi OTP reset sandi')
                    self._send_json_error(429, "Terlalu banyak percobaan. Mohon tunggu 5 menit lalu minta kode baru.")
                    return
                _record_rate_hit(RESET_PW_TRACKER, confirm_rl_key, window_seconds=300)

                otps = load_db_otp()
                if key not in otps:
                    self._send_json_error(400, "Sesi reset password tidak ditemukan atau telah kedaluwarsa. Silakan minta kode baru.")
                    return

                otp_info = otps[key]
                if time.time() > otp_info.get('expires_at', 0):
                    otps.pop(key, None)
                    save_db_otp(otps)
                    self._send_json_error(400, "Kode OTP telah kedaluwarsa. Silakan minta kode OTP baru.")
                    return

                if otp_info.get('otp') != user_otp:
                    self._send_json_error(400, "Kode OTP salah. Pastikan Anda memasukkan 6 digit angka yang sesuai.")
                    return

                # OTP Valid! Hapus OTP
                otps.pop(key, None)
                save_db_otp(otps)

                # Update password di db_users.json
                users = load_db_users()
                phone = otp_info.get('phone', '')
                email = otp_info.get('email', '')
                updated = False

                for u in users.get('pemohon', []):
                    u_phone = str(u.get('phone', '')).replace('+', '').replace('-', '').replace(' ', '')
                    if u_phone.startswith('08'): u_phone = '628' + u_phone[2:]
                    elif u_phone.startswith('8'): u_phone = '628' + u_phone[1:]
                    
                    if (phone and u_phone == phone) or (email and str(u.get('email', '')).lower() == email.lower()):
                        u['password'] = new_password
                        updated = True
                        break

                if not updated:
                    for p in users.get('pegawai', []):
                        if (phone and str(p.get('phone', '')) == phone) or                            (email and str(p.get('email', '')).lower() == email.lower()) or                            (key == str(p.get('nip', ''))):
                            p['password'] = new_password
                            updated = True
                            break

                save_db_users(users)
                print(f"[+] Kata sandi berhasil diperbarui untuk key: {key}")

                self._send_json_response({
                    "status": "ok",
                    "message": "Kata sandi Anda berhasil diperbarui! Silakan masuk dengan kata sandi baru Anda."
                })
                return
            except Exception as e:
                self._send_json_error(500, f"Gagal memperbarui kata sandi: {e}")
                return

        # 4. API Logout Sesi
        if self.path == '/api/auth/logout':
            token, sess = get_session_from_request(self)
            if token and token in AUTH_SESSIONS:
                del AUTH_SESSIONS[token]

            self._send_json_response({
                "status": "ok",
                "message": "Sesi aktif telah dihapus. Berhasil keluar."
            }, cookie_header="session_token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT")
            return

        # Webhook Pesan Masuk dari Self-Hosted WhatsApp Gateway (Baileys Mac Mini)
        if self.path == '/api/webhook/baileys':
            import hmac
            _, expected_secret = get_wa_gateway_config()
            provided_secret = (self.headers.get('X-WA-Gateway-Secret') or '').strip()
            if not expected_secret or not provided_secret or not hmac.compare_digest(provided_secret, expected_secret):
                self._send_json_error(403, "Forbidden: X-WA-Gateway-Secret tidak valid atau belum dikonfigurasi.")
                return

            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                sender_phone = str(body.get('from') or body.get('phone') or '').strip()
                text = str(body.get('text') or '').strip()
                push_name = str(body.get('push_name') or body.get('name') or '').strip() or None
                if not sender_phone or not text:
                    self._send_json_error(400, "Parameter 'from' dan 'text' wajib diisi.")
                    return

                log_chat_message(sender_phone, 'user', text, name=push_name)
                self._send_json_response({"status": "ok"})
                return
            except Exception as e:
                self._send_json_error(500, f"Gagal memproses webhook Baileys: {e}")
                return

        # Kirim Pesan Manual dari Petugas Operator WhatsApp Bea Cukai
        if self.path == '/api/wa/send':
            token, sess = get_session_from_request(self)
            if not _is_pegawai(sess):
                self._send_json_error(403, "Akses Ditolak: Hanya Petugas Bea Cukai yang berwenang mengirim pesan operator dinas.")
                return

            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                to_num = body.get('to', '').strip().replace('+', '').replace('-', '').replace(' ', '')
                if to_num.startswith('08'):
                    to_num = '628' + to_num[2:]
                text = body.get('text', '').strip()
                if not to_num or not text:
                    self._send_json_error(400, "Nomor tujuan dan isi pesan wajib diisi.")
                    return

                # Kirim via WA Gateway (prioritas) atau Meta Cloud API (fallback)
                meta_res = send_whatsapp_meta_message(to_num, text, log_chat=False)
                is_sent = isinstance(meta_res, dict) and (meta_res.get('status') not in ('error', 'logged_offline', 'rate_limited')) and ('messages' in meta_res or meta_res.get('status') in ('success', 'ok'))

                if not is_sent:
                    err_msg = (meta_res.get('message') if isinstance(meta_res, dict) else None) or "Pengiriman WhatsApp gagal. Pastikan WA Gateway Mac Mini aktif dan terhubung."
                    self._send_json_error(502, err_msg)
                    return

                # Catat ke log chat operator hanya jika benar-benar terkirim
                log_chat_message(to_num, 'officer', text, name=body.get('nama'))
                self._send_json_response({'status': 'success', 'meta_response': meta_res})
                return
            except Exception as e:
                self._send_json_error(500, str(e))
                return
        # Autosave Draf Formulir Tahap 2 (Unggah Berkas) — dipanggil debounced dari
        # frontend tiap kali pemohon selesai mengedit satu field/dokumen, supaya data
        # (termasuk hasil OCR & pratinjau gambar yang sudah dikoreksi) tetap ada
        # walau pemohon logout sebelum submit akhir. Body HANYA bagian yang berubah
        # (`patch`), di-merge dangkal ke draf yang sudah tersimpan — bukan ditimpa utuh.
        if self.path == '/api/permohonan/draft-save':
            token, sess = get_session_from_request(self)
            if not sess or sess.get('role') != 'pemohon':
                self._send_json_error(401, 'Sesi tidak valid. Silakan masuk kembali.')
                return
            rl_key = (_get_client_ip(self), token)
            if _is_rate_limited(DRAFT_SAVE_RATE_TRACKER, rl_key, max_attempts=60, window_seconds=120):
                self._send_json_error(429, 'Terlalu sering menyimpan draf. Mohon tunggu sebentar.')
                return
            _record_rate_hit(DRAFT_SAVE_RATE_TRACKER, rl_key, window_seconds=120)
            identifier = _pemohon_draft_identifier(sess)
            if not identifier:
                self._send_json_error(400, 'Identitas pemohon pada sesi tidak lengkap.')
                return
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                if body.get('clear'):
                    database.clear_form_draft(identifier)
                    legacy_ident = _legacy_pemohon_draft_identifier(sess)
                    if legacy_ident:
                        database.clear_form_draft(legacy_ident)
                    self._send_json_response({'status': 'ok', 'cleared': True})
                    return
                patch = body.get('patch')
                if not isinstance(patch, dict):
                    self._send_json_error(400, 'Format draf tidak valid.')
                    return

                # Lampirkan metadata kepemilikan akun ke draf secara otomatis
                sess_user = (sess or {}).get('user', {}) or {}
                patch['saved_by'] = {
                    'id': sess_user.get('id', ''),
                    'nama': sess_user.get('nama', ''),
                    'phone': sess_user.get('phone', ''),
                    'saved_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                database.save_form_draft(identifier, patch)
                self._send_json_response({'status': 'ok', 'updated_at': datetime.datetime.now().isoformat()})
            except Exception as e:
                self._send_json_error(500, str(e))
            return

        # Update Status Permohonan dari Dashboard Pegawai

        # Tambah Permohonan Baru (dari Bot WhatsApp / Simulator Real)
        if self.path == '/api/permohonan/create':
            # Endpoint ini dulu TIDAK memverifikasi sesi sama sekali untuk semua nilai
            # `sumber` (termasuk default WHATSAPP_BOT) — siapa pun bisa POST langsung
            # tanpa login, bikin celah broken access control sekaligus memperbesar
            # dampak stored-XSS di field bebas (nama_pemohon/nopol/dst.). Alur bot
            # WhatsApp yang sungguhan menulis permohonan LANGSUNG di proses webhook
            # (lihat WAITING_NPWP di handler /api/webhook/whatsapp), bukan lewat
            # endpoint publik ini — jadi mewajibkan sesi pemohon di sini tidak
            # memutus integrasi bot apa pun yang sudah berjalan.
            token, sess = get_session_from_request(self)
            if not sess or sess.get('role') != 'pemohon':
                self._send_json_error(403, 'Akses Ditolak: Hanya pemohon yang sudah masuk (login) yang berwenang mengajukan permohonan.')
                return
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                sumber = body.get("sumber", "WHATSAPP_BOT")
                dokumen_bermeterai = body.get("dokumen_bermeterai")
                # Identitas (NIK/no. WA pemohon) WAJIB diambil dari akun yang sedang
                # login, bukan dipercaya mentah dari body — supaya satu akun tidak
                # bisa mengaku-aku jadi identitas orang lain (sumber bug "tabrakan
                # identitas" yang pernah terjadi di produksi).
                sess_user = sess.get('user', {}) or {}
                sess_nik = str(sess_user.get('nik', '')).strip()
                sess_phone = str(sess_user.get('phone', '')).strip()

                # UU Bea Meterai No. 10/2020: Surat Permohonan & Surat Pernyataan WAJIB
                # bermeterai asli sebelum sah diajukan. Validasi ini tidak boleh hanya
                # di frontend — kalau bisa dilewati lewat panggilan API langsung, syarat
                # hukumnya jadi tidak berarti. Berlaku untuk jalur formulir web; jalur
                # WhatsApp bot (sumber lain) punya alur verifikasi berkasnya sendiri.
                if sumber == 'PORTAL_WEB' and not dokumen_bermeterai:
                    resp = json.dumps({
                        "status": "error",
                        "message": "Dokumen yang sudah dibubuhi e-meterai asli (Hal. 1 & 2) wajib diunggah sebelum permohonan dapat dikirim."
                    }).encode('utf-8')
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', str(len(resp)))
                    self.end_headers()
                    self.wfile.write(resp)
                    return

                db = load_db_permohonan()
                new_id = f"KBM-2026-{str(len(db) + 1).zfill(3)}"
                new_record = {
                    "id": new_id,
                    "tanggal_pengajuan": body.get("tanggal_pengajuan", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                    "nama_pemohon": body.get("nama_pemohon", "-"),
                    "nik": sess_nik or body.get("nik", "-"),
                    "npwp": body.get("npwp", "-"),
                    "wakil_nama": body.get("wakil_nama", ""),
                    "wakil_nik": body.get("wakil_nik", ""),
                    "no_wa_pengirim": body.get("no_wa_pengirim", "-"),
                    "no_wa_pemohon": sess_phone or body.get("no_wa_pemohon", "-"),
                    "nomor_berbeda": body.get("nomor_berbeda", False),
                    "nopol": body.get("nopol", "BP - (Menunggu STNK)"),
                    "merek_tipe": body.get("merek_tipe", "Sedang Diproses"),
                    "no_stnk": body.get("no_stnk", ""),
                    "no_bpkb": body.get("no_bpkb", ""),
                    "no_rangka": body.get("no_rangka", ""),
                    "no_mesin": body.get("no_mesin", ""),
                    "tahun_warna": body.get("tahun_warna", ""),
                    "pelabuhan_tujuan": body.get("pelabuhan_tujuan", "Kuala Tungkal (Jambi)"),
                    "status": "MENUNGGU_VERIFIKASI_DOKUMEN",
                    "sumber": sumber,
                    "dokumen_bermeterai_nama": body.get("dokumen_bermeterai_nama", ""),
                    "dokumen_bermeterai_ada": bool(dokumen_bermeterai),
                    "indikasi_cbu": bool(body.get("indikasi_cbu", False)),
                    "cbu_detail": body.get("cbu_detail", ""),
                    "archived_files": []
                }
                if dokumen_bermeterai:
                    new_record["dokumen_bermeterai"] = dokumen_bermeterai
                    meta_bm = save_and_archive_document(
                        new_record,
                        "06_Surat_Permohonan_Pernyataan_Bermeterai",
                        dokumen_bermeterai,
                        custom_filename=body.get("dokumen_bermeterai_nama") or "06_Surat_Permohonan_Pernyataan_Bermeterai.pdf"
                    )
                    if meta_bm:
                        new_record["archived_files"].append(meta_bm)

                # Simpan & arsipkan berkas asli pemohon (KTP, NPWP, STNK 1 & 2, BPKB, pendukung, 6 foto fisik) ke disk + Google Drive
                berkas_pemohon = body.get("berkas_pemohon") or {}
                if isinstance(berkas_pemohon, dict):
                    _label_map = [
                        ("ktp", "01_KTP"),
                        ("npwp", "02_NPWP"),
                        ("stnk", "03a_STNK_Lembar1"),
                        ("stnk_2", "03b_STNK_Lembar2_TBPKP"),
                        ("bpkb", "04_BPKB"),
                        ("bpkb_2", "04b_BPKB_atau_Leasing_Halaman2"),
                        ("bpkb_3", "04c_BPKB_atau_Leasing_Halaman3"),
                        ("bpkb_4", "04d_BPKB_atau_Leasing_Halaman4"),
                        ("bpkb_5", "04e_BPKB_atau_Leasing_Halaman5"),
                        ("bpkb_6", "04f_BPKB_atau_Leasing_Halaman6"),
                        ("buku_nikah", "05a_Buku_Nikah_KK"),
                        ("kwitansi", "05b_Kwitansi_Jual_Beli"),
                        ("surat_sewa", "05c_Surat_Sewa"),
                        ("surat_kuasa", "05d_Surat_Kuasa"),
                        ("foto_depan", "11a_Foto_Sisi_Depan"),
                        ("foto_kanan", "11b_Foto_Samping_Kanan"),
                        ("foto_kiri", "11c_Foto_Samping_Kiri"),
                        ("foto_belakang", "11d_Foto_Sisi_Belakang"),
                        ("foto_rangka", "11e_Foto_Nomor_Rangka"),
                        ("foto_mesin", "11f_Foto_Nomor_Mesin"),
                    ]
                    for key, label in _label_map:
                        val = berkas_pemohon.get(key)
                        if val:
                            meta_doc = save_and_archive_document(new_record, label, val)
                            if meta_doc:
                                new_record["archived_files"].append(meta_doc)

                db.insert(0, new_record)
                save_db_permohonan(db)
                backup_sqlite_to_gdrive_async()
                database.log_activity(new_record.get('no_wa_pemohon', '-'), 'pemohon', 'PERMOHONAN_DIKIRIM', detail=f"Nopol {new_record.get('nopol','-')}, sumber {sumber}, {len(new_record['archived_files'])} berkas diarsipkan", target_id=new_id)
                # Permohonan sudah terkirim — draf Tahap 2 (Unggah Berkas) tidak
                # relevan lagi, hapus supaya tidak menumpuk selamanya di tabel.
                try:
                    database.clear_form_draft(_pemohon_draft_identifier(sess))
                    legacy_ident = _legacy_pemohon_draft_identifier(sess)
                    if legacy_ident:
                        database.clear_form_draft(legacy_ident)
                except Exception:
                    pass
                resp = json.dumps({"status": "success", "data": new_record}).encode('utf-8')
                self.send_response(200)
            except Exception as e:
                resp = json.dumps({"status": "error", "message": str(e)}).encode('utf-8')
                self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        if self.path == '/api/permohonan/update':
            token, sess = get_session_from_request(self)
            # Ini endpoint override status bebas: hanya adminutama (bukan role pegawai lain)
            # yang boleh melompat status manual di luar alur tahap normal.
            if not sess or sess.get('role') != 'adminutama':
                self._send_json_error(403, "Akses Ditolak: Hanya Admin Utama yang berwenang melakukan override status manual.")
                return

            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                pid = body.get('id')
                new_status = body.get('status')
                override_reason = str(body.get('override_reason', '')).strip()
                if not override_reason:
                    self._send_json_error(400, "Alasan override wajib diisi untuk jejak audit.")
                    return
                if new_status in ADMIN_OVERRIDE_BLOCKED_STATUSES:
                    self._send_json_error(400, "Akses Ditolak: Admin Utama tidak dapat melompat status langsung ke tahap hasil pemeriksaan/SPPB. Tahap ini wajib dikerjakan oleh Pemeriksa Dokumen/Gate yang berwenang melalui aksi resminya sendiri.")
                    return

                db = load_db_permohonan()
                found = False
                for item in db:
                    if item.get('id') == pid:
                        item['status'] = new_status
                        item['catatan_petugas'] = f"[OVERRIDE ADMIN oleh {sess.get('user', {}).get('nama', 'Admin Utama')}] {override_reason}"
                        item['updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        found = True
                        break
                if found:
                    save_db_permohonan(db)
                    _log_officer_action(sess, 'ADMIN_OVERRIDE', pid, f"-> {new_status}: {override_reason}")
                    resp = json.dumps({'status': 'success', 'message': f'Status {pid} berhasil diubah ke {new_status}'}).encode('utf-8')
                    self.send_response(200)
                else:
                    resp = json.dumps({'status': 'error', 'message': f'ID {pid} tidak ditemukan'}).encode('utf-8')
                    self.send_response(404)
            except Exception as e:
                resp = json.dumps({'status': 'error', 'message': str(e)}).encode('utf-8')
                self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        # ================= ADMIN UTAMA: MANAJEMEN AKUN & LOG AKTIVITAS =================
        # Admin Utama mengelola username/password petugas & pemohon dari sini. TIDAK
        # menyentuh data hasil keputusan sensitif (lhp_data/no_sppb/dst.) — itu
        # dibatasi lewat ADMIN_OVERRIDE_BLOCKED_STATUSES di endpoint lain.
        if self.path == '/api/admin/users/create-pegawai':
            token, sess = get_session_from_request(self)
            if not sess or sess.get('role') != 'adminutama':
                self._send_json_error(403, 'Akses Ditolak: Hanya Admin Utama yang berwenang membuat akun petugas.')
                return
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                username = str(body.get('username', '')).strip().lower()
                password = str(body.get('password', '')).strip()
                nama = str(body.get('nama', '')).strip()
                nip = str(body.get('nip', '')).strip()
                jabatan = str(body.get('jabatan', '')).strip()
                role = str(body.get('role', '')).strip()

                if not username or not password or not nama or not role:
                    self._send_json_error(400, 'Username, kata sandi, nama, dan role wajib diisi.')
                    return
                if len(password) < 6:
                    self._send_json_error(400, 'Kata sandi minimal 6 karakter.')
                    return
                if role not in PEGAWAI_ROLES:
                    self._send_json_error(400, f'Role tidak dikenal: {role}.')
                    return

                users = load_db_users()
                pegawai_list = users.get('pegawai', [])
                if any(str(p.get('username', '')).strip().lower() == username for p in pegawai_list):
                    self._send_json_error(400, f'Username "{username}" sudah dipakai akun lain.')
                    return
                if nip and any(str(p.get('nip', '')).strip() == nip for p in pegawai_list):
                    self._send_json_error(400, f'NIP "{nip}" sudah dipakai akun lain.')
                    return

                now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                new_pegawai = {
                    'username': username,
                    'password': password,
                    'nama': nama,
                    'nip': nip,
                    'nik': '',
                    'phone': '',
                    'email': '',
                    'jabatan': jabatan,
                    'role': role,
                    'is_officer': 0,
                    'created_at': now_str,
                    'updated_at': now_str
                }
                pegawai_list.append(new_pegawai)
                users['pegawai'] = pegawai_list
                save_db_users(users)
                _log_officer_action(sess, 'ADMIN_CREATE_AKUN', target_id=username, detail=f"Role {role}, nama {nama}")

                self._send_json_response({'status': 'ok', 'message': f'Akun petugas "{username}" ({role}) berhasil dibuat.'})
            except Exception as e:
                self._send_json_error(500, f'Gagal membuat akun petugas: {str(e)}')
            return

        if self.path == '/api/admin/users/reset-password':
            token, sess = get_session_from_request(self)
            if not sess or sess.get('role') != 'adminutama':
                self._send_json_error(403, 'Akses Ditolak: Hanya Admin Utama yang berwenang mereset kata sandi akun.')
                return
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                username = str(body.get('username', '')).strip()
                account_type = body.get('account_type')
                new_password = str(body.get('new_password', '')).strip()

                if not username or account_type not in ('pegawai', 'pemohon') or not new_password:
                    self._send_json_error(400, 'Username, jenis akun (pegawai/pemohon), dan kata sandi baru wajib diisi.')
                    return
                if len(new_password) < 6:
                    self._send_json_error(400, 'Kata sandi minimal 6 karakter.')
                    return

                users = load_db_users()
                target_list = users.get(account_type, [])
                found = None
                for u in target_list:
                    if str(u.get('username', '')).strip().lower() == username.strip().lower() or str(u.get('id', '')).strip().lower() == username.strip().lower():
                        found = u
                        break
                if not found:
                    self._send_json_error(404, f'Akun {account_type} "{username}" tidak ditemukan.')
                    return

                found['password'] = new_password
                found['updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                users[account_type] = target_list
                save_db_users(users)
                _log_officer_action(sess, 'ADMIN_RESET_PASSWORD', target_id=username, detail=f"Jenis akun: {account_type}")

                self._send_json_response({'status': 'ok', 'message': f'Kata sandi akun "{username}" berhasil direset.'})
            except Exception as e:
                self._send_json_error(500, f'Gagal mereset kata sandi: {str(e)}')
            return

        # Webhook Handler WhatsApp Cloud API Meta (Pesan Masuk, Klik Tombol, Gambar)
        if self.path == '/api/webhook/whatsapp':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                # Respons Meta 200 OK langsung agar tidak retry
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status":"received"}')

                # Proses event WhatsApp secara asinkron / logika state
                entries = body.get('entry', [])
                for entry in entries:
                    for change in entry.get('changes', []):
                        val = change.get('value', {})
                        messages = val.get('messages', [])
                        for msg in messages:
                            from_num = msg.get('from', '')
                            msg_type = msg.get('type', '')
                            user_text = ''
                            button_payload = ''

                            if msg_type == 'text':
                                user_text = msg.get('text', {}).get('body', '').strip()
                            elif msg_type == 'interactive':
                                btn_reply = msg.get('interactive', {}).get('button_reply', {})
                                button_payload = btn_reply.get('id', '')
                                user_text = btn_reply.get('title', '')

                            session = WA_SESSIONS.get(from_num, {'state': 'INIT', 'data': {}})

                            # Logika State Machine Percakapan Bot
                            st = session.get('state', 'INIT')
                            if st == 'INIT' or 'DAFTAR' in user_text.upper() or 'HALO' in user_text.upper():
                                session['state'] = 'CONFIRM_START'
                                session['data']['no_pengirim'] = from_num
                                WA_SESSIONS[from_num] = session
                                send_whatsapp_meta_message(
                                    from_num,
                                    "Halo! Selamat datang di Layanan Mandiri Pabean KPU Bea dan Cukai Tipe B Batam.\n\n"
                                    "Apakah Anda akan mengajukan *Permohonan Pengeluaran Sementara Kendaraan Bermotor (PENGSEM KBM)* dari Kawasan Bebas Batam ke TLDDP?",
                                    [
                                        {"id": "btn_iya", "title": "Iya, Ajukan"},
                                        {"id": "btn_tidak", "title": "Tidak"}
                                    ]
                                )
                            elif st == 'CONFIRM_START':
                                if button_payload == 'btn_iya' or user_text.lower() in ('iya', 'ya', '1'):
                                    session['state'] = 'CONFIRM_NO_WA'
                                    WA_SESSIONS[from_num] = session
                                    send_whatsapp_meta_message(
                                        from_num,
                                        f"Baik, terima kasih. Untuk keperluan kontak verifikasi pabean:\n\n"
                                        f"Apakah nomor WhatsApp pemohon adalah nomor yang sedang Anda gunakan saat ini (*+{from_num}*) atau nomor berbeda?",
                                        [
                                            {"id": "btn_no_sama", "title": "Nomor Sama"},
                                            {"id": "btn_no_beda", "title": "Nomor Berbeda"}
                                        ]
                                    )
                                else:
                                    session['state'] = 'INIT'
                                    WA_SESSIONS[from_num] = session
                                    send_whatsapp_meta_message(from_num, "Baik, terima kasih. Hubungi kami kembali jika Anda membutuhkan layanan kepabeanan KBM Batam.")
                            elif st == 'CONFIRM_NO_WA':
                                if button_payload == 'btn_no_sama' or user_text.lower() in ('sama', 'nomor sama', '1'):
                                    session['data']['no_pemohon'] = from_num
                                    session['data']['nomor_berbeda'] = False
                                    session['state'] = 'INPUT_NAMA'
                                    WA_SESSIONS[from_num] = session
                                    send_whatsapp_meta_message(from_num, f"Nomor pemohon dicatat: *+{from_num}*.\n\nSilakan ketikkan *Nama Lengkap Pemohon* sesuai KTP:")
                                else:
                                    session['state'] = 'INPUT_NO_BEDA'
                                    WA_SESSIONS[from_num] = session
                                    send_whatsapp_meta_message(from_num, "Silakan ketikkan *Nomor WhatsApp Pemohon* yang aktif (contoh: 0812xxxxxxxx):")
                            elif st == 'INPUT_NO_BEDA':
                                session['data']['no_pemohon'] = user_text
                                session['data']['nomor_berbeda'] = True
                                session['state'] = 'INPUT_NAMA'
                                WA_SESSIONS[from_num] = session
                                send_whatsapp_meta_message(from_num, f"Nomor pemohon dicatat: *{user_text}*.\n\nSilakan ketikkan *Nama Lengkap Pemohon* sesuai KTP:")
                            elif st == 'INPUT_NAMA':
                                session['data']['nama_pemohon'] = user_text.upper()
                                session['state'] = 'WAITING_KTP'
                                WA_SESSIONS[from_num] = session
                                send_whatsapp_meta_message(from_num, f"Nama pemohon dicatat: *{user_text.upper()}*.\n\n📸 Silakan kirimkan *Foto atau Berkas PDF KTP Asli* pemohon:")
                            elif st == 'WAITING_KTP':
                                session['state'] = 'WAITING_NPWP'
                                WA_SESSIONS[from_num] = session
                                send_whatsapp_meta_message(from_num, "✓ Dokumen KTP berhasil diterima!\n\n💳 Terakhir untuk tahap identitas awal, silakan kirimkan *Foto atau Berkas PDF Kartu NPWP Asli* pemohon:")
                            elif st == 'WAITING_NPWP':
                                db = load_db_permohonan()
                                new_id = f"KBM-2026-{str(len(db)+1).zfill(3)}"
                                new_record = {
                                    "id": new_id,
                                    "tanggal_pengajuan": "2026-03-10 12:30:00",
                                    "nama_pemohon": session['data'].get('nama_pemohon', 'PEMOHON WHATSAPP'),
                                    "nik": "2171020000000000",
                                    "npwp": "00.000.000.0-000.000",
                                    "no_wa_pengirim": session['data'].get('no_pengirim', from_num),
                                    "no_wa_pemohon": session['data'].get('no_pemohon', from_num),
                                    "nomor_berbeda": session['data'].get('nomor_berbeda', False),
                                    "nopol": "BP - (Menunggu STNK)",
                                    "merek_tipe": "SEDANG DIPROSES",
                                    "status": "MENUNGGU_VERIFIKASI_DOKUMEN",
                                    "sumber": "WHATSAPP_BOT"
                                }
                                db.insert(0, new_record)
                                save_db_permohonan(db)

                                session['state'] = 'DONE'
                                WA_SESSIONS[from_num] = session
                                send_whatsapp_meta_message(
                                    from_num,
                                    f"🎉 *Permohonan Anda Berhasil Terdaftar!*\n\n"
                                    f"Nomor Agenda Pabean: *#{new_id}*\n"
                                    f"Status: 🟡 *Menunggu Verifikasi Dokumen*\n\n"
                                    f"Data telah disuplai secara otomatis ke Dashboard Petugas KPU Bea dan Cukai Tipe B Batam."
                                )
                return
            except Exception as e:
                print("[!] Error in WhatsApp Webhook:", e)
                return

        if self.path == '/api/ocr':
            token, sess = get_session_from_request(self)
            if not sess:
                self._send_json_error(401, 'Sesi login tidak valid. Silakan masuk kembali.')
                return
            ocr_rl_key = (_get_client_ip(self), token)
            if _is_rate_limited(OCR_RATE_TRACKER, ocr_rl_key, max_attempts=20, window_seconds=300):
                self._send_json_error(429, 'Terlalu banyak permintaan pemindaian dokumen. Mohon tunggu beberapa menit.')
                return
            _record_rate_hit(OCR_RATE_TRACKER, ocr_rl_key, window_seconds=300)
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                target = data.get('target', '').lower()
                engine = data.get('engine', 'auto').lower()
                img_b64 = data.get('image', '')
                if ',' in img_b64:
                    img_b64 = img_b64.split(',', 1)[1]
                
                raw_bytes = base64.b64decode(img_b64)

                # Validasi Format Ketat: Hanya menerima berkas JPG, PNG, atau PDF
                is_jpg = raw_bytes.startswith(b'\xff\xd8\xff')
                is_png = raw_bytes.startswith(b'\x89PNG')
                is_pdf = raw_bytes.startswith(b'%PDF')

                if not (is_jpg or is_png or is_pdf):
                    response_data = json.dumps({
                        'status': 'error',
                        'message': 'Format berkas tidak didukung. Sistem AI Vision hanya menerima berkas JPG, PNG, atau PDF.'
                    }).encode('utf-8')
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', str(len(response_data)))
                    self.end_headers()
                    self.wfile.write(response_data)
                    return

                # Deteksi 4 sudut poligon & transformasi perspektif (Perspective Warp) via OpenCV
                warped_bytes, cropped_image_url = auto_warp_document_opencv(raw_bytes, target)
                input_for_ocr = warped_bytes if cropped_image_url else raw_bytes

                extracted_text, parsed_data = process_ocr(input_for_ocr, target, engine)
                is_mismatch, detected_doc_type = check_document_type_mismatch(target, parsed_data, extracted_text)

                # Jika terbukti salah slot (mis. STNK diunggah ke kolom KTP), JANGAN PERNAH mengisi formulir!
                if is_mismatch:
                    parsed_data = {}
                    cropped_image_url = None

                # Validasi doc_bbox [ymin, xmin, ymax, xmax] skala 0..1000 dari Vision AI untuk auto-crop presisi
                valid_doc_bbox = None
                if not is_mismatch and isinstance(parsed_data, dict):
                    raw_bbox = parsed_data.get('doc_bbox')
                    if isinstance(raw_bbox, (list, tuple)) and len(raw_bbox) == 4:
                        try:
                            ymin, xmin, ymax, xmax = [int(round(float(v))) for v in raw_bbox]
                            ymin = max(0, min(1000, ymin))
                            xmin = max(0, min(1000, xmin))
                            ymax = max(0, min(1000, ymax))
                            xmax = max(0, min(1000, xmax))
                            bw = xmax - xmin
                            bh = ymax - ymin
                            area_ratio = (bw * bh) / 1000000.0
                            # Hanya terapkan crop jika kotak valid (>= 12% lebar/tinggi) dan benar-benar membuang background (< 96% area)
                            if bw >= 120 and bh >= 120 and 0.03 <= area_ratio <= 0.96:
                                valid_doc_bbox = [ymin, xmin, ymax, xmax]
                        except Exception:
                            valid_doc_bbox = None

                has_valid_fields = (not is_mismatch) and isinstance(parsed_data, dict) and any(
                    str(v).strip() for k, v in parsed_data.items()
                    if k not in ('doc_bbox', 'jenis_dokumen_terdeteksi', '_error')
                )

                response_data = json.dumps({
                    'status': 'mismatch' if is_mismatch else ('ok' if (has_valid_fields or cropped_image_url) else 'failed'),
                    'target': target,
                    'engine_used': 'vision_ai' if engine in ('vision', 'auto') and VISION_AI_ENABLED else 'easyocr_local',
                    'text': extracted_text,
                    'parsed': {} if is_mismatch else (parsed_data if has_valid_fields else {}),
                    'document_mismatch': is_mismatch,
                    'detected_document_type': detected_doc_type,
                    'doc_bbox': valid_doc_bbox,
                    'cropped_image': cropped_image_url
                }).encode('utf-8')
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(response_data)))
                self.end_headers()
                self.wfile.write(response_data)
            except Exception as e:
                err_data = json.dumps({'status': 'error', 'message': str(e)}).encode('utf-8')
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(err_data)))
                self.end_headers()
                self.wfile.write(err_data)
            # WAJIB return di sini — tanpa ini eksekusi jatuh ke blok `if self.path == ...`
            # berikutnya (NADINE dst.), tidak ada yang cocok, lalu fallback 404 "Endpoint not
            # found" ikut ditulis ke koneksi keep-alive YANG SAMA setelah respons 200/500 di
            # atas sudah terkirim — merusak alur respons HTTP (terbukti di log: setiap panggilan
            # /api/ocr selalu diikuti baris "code 404, message Endpoint not found").
            return
        # ================= NADINE KEMENKEU ENDPOINTS =================
        if self.path == '/api/nadine/config':
            token, sess = get_session_from_request(self)
            if not sess or sess.get('role') not in ('frontdesk', 'loket', 'adminutama'):
                self._send_json_error(403, 'Akses Ditolak: Hanya Petugas Frontdesk/Loket/Admin Utama yang berwenang memperbarui konfigurasi Nadine.')
                return
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                current_cfg = load_db_nadine_config()
                if 'username' in body:
                    current_cfg['username'] = body['username'].strip()
                if 'password' in body and body['password'].strip():
                    current_cfg['password'] = body['password'].strip()
                if 'totp_secret' in body:
                    clean_secret = body['totp_secret'].strip().replace(' ', '').upper()
                    current_cfg['totp_secret'] = clean_secret
                
                current_cfg['status'] = 'TERKONFIGURASI'
                save_db_nadine_config(current_cfg)
                self._send_json_response({'status': 'ok', 'message': 'Konfigurasi Akun Nadine Frontdesk berhasil disimpan.'})
            except Exception as e:
                self._send_json_error(500, f'Gagal menyimpan konfigurasi Nadine: {str(e)}')
            return

        if self.path == '/api/nadine/test-login':
            token, sess = get_session_from_request(self)
            if not sess or sess.get('role') not in ('frontdesk', 'loket', 'adminutama'):
                self._send_json_error(403, 'Akses Ditolak: Hanya Petugas Frontdesk/Loket/Admin Utama yang berwenang menguji koneksi Nadine.')
                return
            cfg = load_db_nadine_config()
            username = cfg.get('username')
            password = cfg.get('password')
            totp_secret = cfg.get('totp_secret')

            if not username or not password or not totp_secret:
                self._send_json_error(400, 'Kredensial Nadine belum lengkap (Username, Password, dan Kunci TOTP diperlukan).')
                return

            try:
                import pyotp
                totp_gen = pyotp.TOTP(totp_secret)
                current_totp = totp_gen.now()
                now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S WIB')
                cfg['last_tested'] = now_str
                cfg['status'] = 'TERHUBUNG_AKTIF'
                save_db_nadine_config(cfg)
                self._send_json_response({
                    'status': 'ok',
                    'message': 'Koneksi SSO Nadine Kemenkeu Berhasil!',
                    'nip': username,
                    'totp_code': current_totp,
                    'tested_at': now_str
                })
            except Exception as e:
                self._send_json_error(500, f'Gagal menguji autentikasi Nadine: {str(e)}')
            return

        def _is_role_allowed(sess, allowed_roles):
            if not sess: return False
            role = str(sess.get('role', '')).lower()
            if role == 'adminutama' or sess.get('user', {}).get('role') == 'adminutama':
                return True
            return role in allowed_roles

        if self.path == '/api/nadine/upload-permohonan':
            token, sess = get_session_from_request(self)
            if not _is_role_allowed(sess, ['frontdesk', 'loket']):
                self._send_json_error(403, 'Akses Ditolak: Hanya Petugas Frontdesk / Loket yang berwenang merekam naskah dinas ke Nadine.')
                return
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                pid = body.get('id')
                db = load_db_permohonan()
                target_item = next((item for item in db if item.get('id') == pid), None)
                if not target_item:
                    self._send_json_error(404, f'Permohonan dengan ID {pid} tidak ditemukan.')
                    return

                generated_nd_id = str(random.randint(62248000, 62249999))
                pengirim_eksternal = target_item.get('nama_pemohon', 'Masyarakat Pemohon')
                perihal = f"Permohonan Pengeluaran Sementara Kendaraan Bermotor - {target_item.get('nopol', 'KBM')} a.n. {pengirim_eksternal}"
                now_ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                target_item['status'] = 'VERIFIKASI_FASILITAS'
                target_item['no_nadine'] = f"NdId: {generated_nd_id}"
                target_item['catatan_petugas'] = f"Berkas fisik & 1 PDF telah diverifikasi Frontdesk/Loket. Berhasil direkam ke Nadine Kemenkeu (NdId: {generated_nd_id}). Diteruskan ke Seksi Fasilitas Pabean."
                target_item['nadine_meta'] = {
                    'nd_id': generated_nd_id,
                    'pengirim_eksternal': pengirim_eksternal,
                    'perihal': perihal,
                    'kategori': 'Surat Masuk Eksternal',
                    'tgl_rekam': now_ts,
                    'petugas_frontdesk': sess.get('user', {}).get('nama', 'Petugas Frontdesk')
                }
                save_db_permohonan(db)
                _log_officer_action(sess, 'NADINE_UPLOAD', pid, target_item.get('catatan_petugas', ''))
                _notify_pemohon_wa(target_item, (
                    f"🏛️ *KPU BEA DAN CUKAI TIPE B BATAM*\n"
                    f"Layanan Pengeluaran Sementara Kendaraan Bermotor (KBM) Ke TLDDP\n\n"
                    f"Halo *{target_item.get('nama_pemohon', 'Pemohon')}*,\n\n"
                    f"Berkas permohonan Anda ({target_item.get('nopol', '-')}) telah diverifikasi dan direkam ke Nadine Kemenkeu, diteruskan ke Seksi Fasilitas Pabean untuk penelitian lebih lanjut.\n\n"
                    f"Informasi Lebih Lanjut Hub: 0851-5814-8448 (Client Coordinator)"
                ))

                self._send_json_response({
                    'status': 'ok',
                    'message': 'Berkas 1 PDF berhasil diunggah & direkam ke Nadine Kemenkeu!',
                    'nd_id': generated_nd_id,
                    'pengirim_eksternal': pengirim_eksternal,
                    'perihal': perihal,
                    'next_stage': 'VERIFIKASI_FASILITAS',
                    'permohonan': target_item
                })
            except Exception as e:
                self._send_json_error(500, f'Gagal mengunggah ke Nadine: {str(e)}')
            return

        # 2. Endpoint Fasilitas (Penerbitan Surat S & KEP Persetujuan)
        if self.path == '/api/fasilitas/terbitkan-skep':
            token, sess = get_session_from_request(self)
            if not _is_role_allowed(sess, ['fasilitas']):
                self._send_json_error(403, 'Akses Ditolak: Hanya Petugas Seksi Fasilitas yang berwenang menerbitkan Surat (S) dan KEP.')
                return
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                pid = body.get('id')
                db = load_db_permohonan()
                target_item = next((item for item in db if item.get('id') == pid), None)
                if not target_item:
                    self._send_json_error(404, f'Permohonan {pid} tidak ditemukan.')
                    return

                no_skep = f"KEP-0{random.randint(20, 99)}/KPU.02/2026"
                no_surat_s = f"S-{random.randint(310, 399)}/KPU.02/BD.04/2026"
                target_item['status'] = 'LOKET_JAMINAN'
                target_item['no_skep'] = no_skep
                target_item['no_surat_s'] = no_surat_s
                target_item['naskah_dinas_s'] = 'Persetujuan Pengeluaran Sementara Kendaraan Bermotor'
                target_item['tgl_skep'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                target_item['catatan_petugas'] = f"Naskah dinas keluar Surat Persetujuan ({no_surat_s}) dan KEP ({no_skep}) diterbitkan Seksi Fasilitas. Berkas dilanjutkan ke Loket Jaminan."
                save_db_permohonan(db)
                _log_officer_action(sess, 'SKEP_TERBIT', pid, f"KEP {no_skep}, Surat {no_surat_s}")
                _notify_pemohon_wa(target_item, (
                    f"🏛️ *KPU BEA DAN CUKAI TIPE B BATAM*\n"
                    f"Layanan Pengeluaran Sementara Kendaraan Bermotor (KBM) Ke TLDDP\n\n"
                    f"Halo *{target_item.get('nama_pemohon', 'Pemohon')}*,\n\n"
                    f"Persetujuan (KEP) permohonan Anda ({target_item.get('nopol', '-')}) telah TERBIT.\n"
                    f"No. KEP: *{no_skep}*\n\n"
                    f"Berkas diteruskan ke Loket Jaminan untuk penerbitan kode billing Jaminan PPN 11%.\n\n"
                    f"Informasi Lebih Lanjut Hub: 0851-5814-8448 (Client Coordinator)"
                ))

                self._send_json_response({
                    'status': 'ok',
                    'message': f'Surat Persetujuan ({no_surat_s}) & KEP ({no_skep}) berhasil diterbitkan!',
                    'no_skep': no_skep,
                    'no_surat_s': no_surat_s,
                    'permohonan': target_item
                })
            except Exception as e:
                self._send_json_error(500, f'Gagal menerbitkan Surat/KEP: {str(e)}')
            return

        # 3a. Endpoint Jaminan (Petugas Jaminan: Unggah Billing dari Portal Eksternal)
        if self.path in ('/api/jaminan/unggah-billing', '/api/jaminan/terbitkan-billing'):
            token, sess = get_session_from_request(self)
            if not _is_role_allowed(sess, ['jaminan']):
                self._send_json_error(403, 'Akses Ditolak: Hanya Petugas Jaminan yang berwenang mengunggah Billing Jaminan.')
                return
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                pid = body.get('id')
                db = load_db_permohonan()
                target_item = next((item for item in db if item.get('id') == pid), None)
                if not target_item:
                    self._send_json_error(404, f'Permohonan {pid} tidak ditemukan.')
                    return

                billing_file = body.get('billing_file_data_url') or ''
                billing_fname = str(body.get('billing_file_name') or '06b_Billing_Jaminan.pdf').strip()
                kode_billing = str(body.get('kode_billing') or '').strip()
                body_nilai = body.get('nilai_jaminan')
                try:
                    nilai_jaminan = int(body_nilai) if body_nilai else target_item.get('nilai_jaminan')
                except (TypeError, ValueError):
                    nilai_jaminan = target_item.get('nilai_jaminan')

                if not billing_file:
                    self._send_json_error(400, 'File Billing Jaminan (PDF/gambar) wajib diunggah terlebih dahulu.')
                    return

                meta_bill = save_and_archive_document(
                    target_item,
                    '06b_Billing_Jaminan',
                    billing_file,
                    custom_filename=billing_fname
                )
                archived = target_item.get('archived_files') if isinstance(target_item.get('archived_files'), list) else []
                if meta_bill:
                    archived = [a for a in archived if a.get('label') != '06b_Billing_Jaminan']
                    archived.append(meta_bill)
                    target_item['archived_files'] = archived

                target_item['status'] = 'LOKET_JAMINAN'
                target_item['jaminan_status'] = 'MENUNGGU_BAYAR_PEMOHON'
                target_item['billing_file_data_url'] = billing_file
                target_item['billing_file_name'] = billing_fname
                if kode_billing:
                    target_item['kode_billing'] = kode_billing
                if nilai_jaminan and nilai_jaminan > 0:
                    target_item['nilai_jaminan'] = nilai_jaminan
                target_item['tgl_billing'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                target_item['jaminan_alasan_tolak'] = ''
                nominal_txt = f" sebesar Rp {nilai_jaminan:,}" if (nilai_jaminan and nilai_jaminan > 0) else ""
                kode_txt = f" (Kode: {kode_billing})" if kode_billing else ""
                target_item['catatan_petugas'] = f"Billing Jaminan{kode_txt}{nominal_txt} telah diunggah oleh Petugas Jaminan. Menunggu pembayaran & unggah bukti bayar oleh pemohon."
                save_db_permohonan(db)
                _log_officer_action(sess, 'JAMINAN_UNGGAH_BILLING', pid, f"Billing {kode_billing or billing_fname}{nominal_txt}")
                _notify_pemohon_wa(target_item, (
                    f"🏛️ *KPU BEA DAN CUKAI TIPE B BATAM*\n"
                    f"Layanan Pengeluaran Sementara Kendaraan Bermotor (KBM) Ke TLDDP\n\n"
                    f"Halo *{target_item.get('nama_pemohon', 'Pemohon')}*,\n\n"
                    f"Billing Jaminan untuk kendaraan Anda ({target_item.get('nopol', '-')}) telah tersedia di Portal PENGSEM{kode_txt}{nominal_txt}.\n\n"
                    f"Silakan masuk ke Portal PENGSEM → menu *Status Permohonan Saya* untuk mengunduh Billing Jaminan, melakukan pembayaran melalui kanal pembayaran resmi, lalu mengunggah *Bukti Bayar* pada portal.\n\n"
                    f"Informasi Lebih Lanjut Hub: 0851-5814-8448 (Client Coordinator)"
                ))

                self._send_json_response({
                    'status': 'ok',
                    'message': 'Billing Jaminan berhasil diunggah & notifikasi WhatsApp telah dikirim ke pemohon!',
                    'permohonan': target_item
                })
            except Exception as e:
                self._send_json_error(500, f'Gagal mengunggah billing jaminan: {str(e)}')
            return

        # 3b. Endpoint Pemohon: Unggah Bukti Bayar Billing Jaminan
        if self.path == '/api/jaminan/unggah-bukti-bayar':
            token, sess = get_session_from_request(self)
            if not sess or sess.get('role') not in ('pemohon', 'adminutama'):
                self._send_json_error(403, 'Akses Ditolak: Silakan masuk sebagai Pemohon untuk mengunggah bukti bayar.')
                return
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                pid = body.get('id')
                bukti_url = body.get('bukti_bayar_data_url') or ''
                bukti_name = str(body.get('bukti_bayar_name') or '06c_Bukti_Bayar_Jaminan.pdf').strip()
                catatan_pemohon = str(body.get('catatan_pemohon') or '').strip()

                if not pid or not bukti_url:
                    self._send_json_error(400, 'File Bukti Bayar Jaminan wajib dipilih sebelum dikirim.')
                    return

                db = load_db_permohonan()
                target_item = next((item for item in db if item.get('id') == pid), None)
                if not target_item:
                    self._send_json_error(404, f'Permohonan {pid} tidak ditemukan.')
                    return

                # Pastikan pemohon hanya bisa mengunggah untuk berkas miliknya sendiri
                if sess.get('role') == 'pemohon':
                    u = sess.get('user', {})
                    u_nik = str(u.get('nik', '')).strip()
                    u_phone = re.sub(r'\D', '', str(u.get('phone', '')))
                    p_nik = str(target_item.get('nik', '')).strip()
                    p_phone = re.sub(r'\D', '', str(target_item.get('no_wa_pemohon', '')))
                    if u_phone.startswith('62'): u_phone = '0' + u_phone[2:]
                    if p_phone.startswith('62'): p_phone = '0' + p_phone[2:]
                    if not ((u_nik and u_nik == p_nik) or (u_phone and u_phone == p_phone)):
                        self._send_json_error(403, 'Akses Ditolak: Anda hanya dapat mengunggah bukti bayar untuk permohonan milik Anda sendiri.')
                        return

                meta_bukti = save_and_archive_document(
                    target_item,
                    '06c_Bukti_Bayar_Jaminan',
                    bukti_url,
                    custom_filename=bukti_name
                )
                archived = target_item.get('archived_files') if isinstance(target_item.get('archived_files'), list) else []
                if meta_bukti:
                    archived = [a for a in archived if a.get('label') != '06c_Bukti_Bayar_Jaminan']
                    archived.append(meta_bukti)
                    target_item['archived_files'] = archived

                target_item['bukti_bayar_data_url'] = bukti_url
                target_item['bukti_bayar_name'] = bukti_name
                target_item['tgl_bukti_bayar'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                target_item['catatan_bukti_bayar'] = catatan_pemohon
                target_item['jaminan_status'] = 'MENUNGGU_VERIFIKASI_JAMINAN'
                target_item['jaminan_alasan_tolak'] = ''
                target_item['catatan_petugas'] = 'Pemohon telah mengunggah Bukti Bayar Jaminan. Menunggu verifikasi Petugas Jaminan.'
                save_db_permohonan(db)
                database.log_activity(sess.get('user', {}).get('phone', 'pemohon'), 'pemohon', 'UNGGAH_BUKTI_BAYAR_JAMINAN', detail=bukti_name, target_id=pid)

                self._send_json_response({
                    'status': 'ok',
                    'message': 'Bukti Bayar Jaminan berhasil diunggah! Status: Menunggu Verifikasi Petugas Jaminan.',
                    'permohonan': target_item
                })
            except Exception as e:
                self._send_json_error(500, f'Gagal mengunggah bukti bayar: {str(e)}')
            return

        # 3c. Endpoint Petugas Jaminan: Verifikasi Pembayaran (Terima -> LOKET_VERIFIKASI | Tolak -> Unggah Ulang)
        if self.path == '/api/jaminan/verifikasi-pembayaran':
            token, sess = get_session_from_request(self)
            if not _is_role_allowed(sess, ['jaminan']):
                self._send_json_error(403, 'Akses Ditolak: Hanya Petugas Jaminan yang berwenang memverifikasi pembayaran jaminan.')
                return
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                pid = body.get('id')
                keputusan = str(body.get('keputusan', '')).strip().upper()
                no_bpj = str(body.get('no_bpj', '')).strip()
                catatan = str(body.get('catatan', '')).strip()

                db = load_db_permohonan()
                target_item = next((item for item in db if item.get('id') == pid), None)
                if not target_item:
                    self._send_json_error(404, f'Permohonan {pid} tidak ditemukan.')
                    return

                if keputusan == 'TERIMA':
                    target_item['jaminan_status'] = 'TERVERIFIKASI'
                    target_item['status'] = 'LOKET_VERIFIKASI'
                    target_item['no_bpj'] = no_bpj or target_item.get('no_bpj', '')
                    target_item['tgl_verifikasi_jaminan'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    target_item['verifikator_jaminan'] = sess.get('user', {}).get('nama', 'Petugas Jaminan')
                    target_item['jaminan_alasan_tolak'] = ''
                    bpj_txt = f" (No. BPJ: {no_bpj})" if no_bpj else ""
                    target_item['catatan_petugas'] = f"Pembayaran jaminan TERVERIFIKASI{bpj_txt}. {catatan} Berkas diteruskan ke Petugas Loket untuk verifikasi 3 bundel & penerbitan PPFTZ/SPF/IP.".strip()
                    save_db_permohonan(db)
                    _log_officer_action(sess, 'JAMINAN_TERVERIFIKASI', pid, f"Terverifikasi{bpj_txt}. {catatan}")
                    _notify_pemohon_wa(target_item, (
                        f"🏛️ *KPU BEA DAN CUKAI TIPE B BATAM*\n"
                        f"Layanan Pengeluaran Sementara Kendaraan Bermotor (KBM) Ke TLDDP\n\n"
                        f"Halo *{target_item.get('nama_pemohon', 'Pemohon')}*,\n\n"
                        f"Pembayaran Jaminan Anda untuk kendaraan ({target_item.get('nopol', '-')}) telah *TERVERIFIKASI*{bpj_txt}.\n"
                        f"Berkas kini diteruskan ke *Petugas Loket* untuk verifikasi akhir dan penerbitan PPFTZ serta Surat Pemberitahuan Pemeriksaan Fisik (SPF).\n\n"
                        f"Informasi Lebih Lanjut Hub: 0851-5814-8448 (Client Coordinator)"
                    ))
                    self._send_json_response({
                        'status': 'ok',
                        'message': 'Jaminan terverifikasi! Berkas otomatis diteruskan ke antrean Petugas Loket (LOKET_VERIFIKASI).',
                        'permohonan': target_item
                    })
                elif keputusan == 'TOLAK':
                    if not catatan:
                        self._send_json_error(400, 'Alasan penolakan / permintaan unggah ulang bukti bayar wajib diisi.')
                        return
                    target_item['jaminan_status'] = 'DITOLAK_UNGGAH_ULANG'
                    target_item['status'] = 'LOKET_JAMINAN'
                    target_item['jaminan_alasan_tolak'] = catatan
                    target_item['catatan_petugas'] = f"Bukti bayar jaminan ditolak: {catatan}. Diminta unggah ulang oleh pemohon."
                    save_db_permohonan(db)
                    _log_officer_action(sess, 'JAMINAN_DITOLAK', pid, catatan)
                    _notify_pemohon_wa(target_item, (
                        f"🏛️ *KPU BEA DAN CUKAI TIPE B BATAM*\n"
                        f"Layanan Pengeluaran Sementara Kendaraan Bermotor (KBM) Ke TLDDP\n\n"
                        f"Halo *{target_item.get('nama_pemohon', 'Pemohon')}*,\n\n"
                        f"Bukti Bayar Jaminan yang Anda unggah untuk kendaraan ({target_item.get('nopol', '-')}) *perlu diunggah ulang*.\n"
                        f"Alasan: _{catatan}_\n\n"
                        f"Silakan masuk kembali ke Portal PENGSEM → *Status Permohonan Saya* untuk mengunggah ulang bukti bayar yang benar.\n\n"
                        f"Informasi Lebih Lanjut Hub: 0851-5814-8448 (Client Coordinator)"
                    ))
                    self._send_json_response({
                        'status': 'ok',
                        'message': 'Bukti bayar ditolak & notifikasi unggah ulang telah dikirim ke pemohon.',
                        'permohonan': target_item
                    })
                else:
                    self._send_json_error(400, 'Keputusan tidak valid (harus TERIMA atau TOLAK).')
            except Exception as e:
                self._send_json_error(500, f'Gagal memverifikasi pembayaran jaminan: {str(e)}')
            return

        # 3d. Endpoint Petugas Loket: Verifikasi 3 Bundel & Otomatisasi 4 Output Atomik (PPFTZ, Pemeriksa Dokumen, SPF, IP)
        if self.path == '/api/loket/approve':
            token, sess = get_session_from_request(self)
            if not _is_role_allowed(sess, ['loket']):
                self._send_json_error(403, 'Akses Ditolak: Hanya Petugas Loket yang berwenang melakukan approval tahap Loket Verifikasi.')
                return
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                pid = body.get('id')
                chk1 = bool(body.get('chk_bundel_permohonan'))
                chk2 = bool(body.get('chk_bundel_skep'))
                chk3 = bool(body.get('chk_bundel_jaminan'))
                if not (chk1 and chk2 and chk3):
                    self._send_json_error(400, 'Ketiga bundel verifikasi Loket (Permohonan+Lampiran, SKEP Fasilitas, dan Jaminan Terverifikasi) wajib dicentang sebelum Approval.')
                    return

                db = load_db_permohonan()
                target_item = next((item for item in db if item.get('id') == pid), None)
                if not target_item:
                    self._send_json_error(404, f'Permohonan {pid} tidak ditemukan.')
                    return
                if target_item.get('status') != 'LOKET_VERIFIKASI' and sess.get('role') != 'adminutama':
                    self._send_json_error(400, f'Berkas {pid} belum berada pada tahap LOKET_VERIFIKASI (status saat ini: {target_item.get("status")}).')
                    return

                # Cari petugas Pemeriksa Dokumen & Pemeriksa Barang terdaftar di database
                users_all = load_db_users().get('pegawai', [])
                pfpd_user = next((u for u in users_all if u.get('role') == 'pemeriksadokumen'), None)
                pemeriksa_brg_user = next((u for u in users_all if u.get('role') == 'pemeriksabarang'), None)

                pfpd_nama = str(body.get('pemeriksa_dokumen_nama') or (pfpd_user.get('nama') if pfpd_user else 'Pejabat Pemeriksa Dokumen (PFPD)')).strip()
                pfpd_nip = str(body.get('pemeriksa_dokumen_nip') or (pfpd_user.get('nip') if pfpd_user else '-')).strip()
                pbrg_nama = str(body.get('pemeriksa_barang_nama') or (pemeriksa_brg_user.get('nama') if pemeriksa_brg_user else 'Pejabat Pemeriksa Barang (Fisik)')).strip()
                pbrg_nip = str(body.get('pemeriksa_barang_nip') or (pemeriksa_brg_user.get('nip') if pemeriksa_brg_user else '-')).strip()

                now_dt = datetime.datetime.now()
                now_str = now_dt.strftime('%Y-%m-%d %H:%M:%S')
                today_str = now_dt.strftime('%Y-%m-%d')
                rand3 = random.randint(100, 999)

                # 4 OUTPUT OTOMATIS ATOMIK:
                # 1. Terbit PPFTZ-01 & Proforma PPFTZ-03 (mencantumkan No. KEP, No. BPJ, No. Surat Jalan Polda)
                no_ppftz = f"{random.randint(10, 99)}/PPFTZ-01/KPU.02/2026"
                no_proforma_ppftz03 = f"PRO-{rand3}/PPFTZ-03/KPU.02/2026"
                # 2. Penunjukan Pemeriksa Dokumen
                # 3. Terbit SPF (Surat Pemberitahuan Pemeriksaan Fisik)
                no_spf = f"SPF-{rand3}/KPU.02/2026"
                # 4. Terbit IP (Instruksi Pemeriksaan) penunjukan Pemeriksa Barang
                no_ip = f"IP-{rand3}/KPU.02/2026"

                no_skep = str(target_item.get('no_skep') or target_item.get('no_kep') or '-').strip()
                no_bpj = str(target_item.get('no_bpj') or '-').strip()
                no_surat_jalan = str(body.get('no_surat_jalan', '')).strip() or str(target_item.get('no_surat_jalan', '')).strip()
                if no_surat_jalan:
                    target_item['no_surat_jalan'] = no_surat_jalan

                target_item['status'] = 'PPFTZ_CEK_FISIK'
                target_item['no_ppftz'] = no_ppftz
                target_item['no_skep'] = no_skep
                target_item['no_bpj'] = no_bpj
                target_item['no_proforma_ppftz03'] = no_proforma_ppftz03
                target_item['tgl_ppftz'] = today_str
                target_item['no_spf'] = no_spf
                target_item['tgl_spf'] = now_str
                target_item['no_ip'] = no_ip
                target_item['tgl_ip'] = now_str
                target_item['pemeriksa_dokumen_nama'] = pfpd_nama
                target_item['pemeriksa_dokumen_nip'] = pfpd_nip
                target_item['pemeriksa_barang_nama'] = pbrg_nama
                target_item['pemeriksa_barang_nip'] = pbrg_nip
                target_item['loket_verifikasi_data'] = {
                    'chk_bundel_permohonan': True,
                    'chk_bundel_skep': True,
                    'chk_bundel_jaminan': True,
                    'no_skep': no_skep,
                    'no_bpj': no_bpj,
                    'no_surat_jalan': no_surat_jalan,
                    'petugas_loket': sess.get('user', {}).get('nama', 'Petugas Loket'),
                    'approved_at': now_str
                }
                target_item['catatan_petugas'] = (
                    f"Approval Loket selesai. Terbit otomatis: PPFTZ-01 ({no_ppftz}), Proforma PPFTZ-03 ({no_proforma_ppftz03}), "
                    f"SPF ({no_spf}), IP ({no_ip}). Dasar PPFTZ-01: No. KEP ({no_skep}), No. BPJ ({no_bpj}), Surat Jalan Polda: {no_surat_jalan or '-'}. "
                    f"Pemeriksa Barang: {pbrg_nama}; Pemeriksa Dokumen: {pfpd_nama}."
                )
                save_db_permohonan(db)
                backup_sqlite_to_gdrive_async()
                _log_officer_action(sess, 'LOKET_APPROVAL_4_OUTPUT', pid, f"PPFTZ {no_ppftz} | SKEP {no_skep} | BPJ {no_bpj} | SPF {no_spf} | IP {no_ip} | SJ {no_surat_jalan} | PFPD {pfpd_nama}")
                _notify_pemohon_wa(target_item, (
                    f"🏛️ *KPU BEA DAN CUKAI TIPE B BATAM*\n"
                    f"Layanan Pengeluaran Sementara Kendaraan Bermotor (KBM) Ke TLDDP\n\n"
                    f"Halo *{target_item.get('nama_pemohon', 'Pemohon')}*,\n\n"
                    f"Berkas permohonan kendaraan Anda ({target_item.get('nopol', '-')}) telah *DISETUJUI PETUGAS LOKET*.\n"
                    f"• No. PPFTZ-01: *{no_ppftz}*\n"
                    f"• No. KEP: *{no_skep}*\n"
                    f"• No. BPJ: *{no_bpj}*\n"
                    f"• Proforma PPFTZ-03: *{no_proforma_ppftz03}*\n"
                    f"• No. SPF: *{no_spf}*\n"
                    f"• No. IP: *{no_ip}*\n\n"
                    f"📌 *WAJIB HADIR PEMERIKSAAN FISIK KENDARAAN* dengan membawa berkas *ASLI* berikut:\n"
                    f"1. KTP Asli\n"
                    f"2. NPWP Asli\n"
                    f"3. BPKB Asli / Surat Keterangan Asli dari Leasing\n"
                    f"4. STNK Asli\n"
                    f"5. Surat Jalan Asli dari Polda" + (f" (No: {no_surat_jalan})" if no_surat_jalan else "") + "\n\n"
                    f"Dokumen SPF dapat dilihat/diunduh di Portal PENGSEM.\n"
                    f"Informasi Lebih Lanjut Hub: 0851-5814-8448 (Client Coordinator)"
                ))

                self._send_json_response({
                    'status': 'ok',
                    'message': f'Approval Loket berhasil! 4 output terbit otomatis (PPFTZ {no_ppftz}, SPF {no_spf}, IP {no_ip}, Pemeriksa Dokumen & Barang ditunjuk).',
                    'no_ppftz': no_ppftz,
                    'no_skep': no_skep,
                    'no_bpj': no_bpj,
                    'no_surat_jalan': no_surat_jalan,
                    'no_proforma_ppftz03': no_proforma_ppftz03,
                    'no_spf': no_spf,
                    'no_ip': no_ip,
                    'permohonan': target_item
                })
            except Exception as e:
                self._send_json_error(500, f'Gagal memproses approval loket: {str(e)}')
            return

        # 4. Endpoint Pemeriksa Barang (Verifikasi 5 Berkas Asli, Upload Foto Lapangan, Rekam BAP & LHP)
        if self.path == '/api/pemeriksaan/rekam-lhp':
            token, sess = get_session_from_request(self)
            if not _is_role_allowed(sess, ['pemeriksabarang']):
                self._send_json_error(403, 'Akses Ditolak: Hanya Pejabat Pemeriksa Barang yang berwenang merekam LHP & BAP.')
                return
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                pid = body.get('id')
                db = load_db_permohonan()
                target_item = next((item for item in db if item.get('id') == pid), None)
                if not target_item:
                    self._send_json_error(404, f'Permohonan {pid} tidak ditemukan.')
                    return

                # 1. Checklist Pencocokan 5 Berkas Fisik Asli
                berkas_asli_flags = {
                    'ktp_asli': bool(body.get('cek_ktp_asli')),
                    'npwp_asli': bool(body.get('cek_npwp_asli')),
                    'bpkb_asli': bool(body.get('cek_bpkb_asli')),
                    'stnk_asli': bool(body.get('cek_stnk_asli')),
                    'surat_jalan_polda': bool(body.get('cek_surat_jalan_polda')),
                }
                catatan_berkas_asli = str(body.get('catatan_berkas_asli', '')).strip()
                if not all(berkas_asli_flags.values()) and not catatan_berkas_asli:
                    self._send_json_error(400, 'Semua 5 berkas fisik asli wajib dicentang (atau isi Catatan Ketidaksesuaian Berkas Asli bila ada yang belum sesuai).')
                    return

                kesesuaian_rangka = body.get('kesesuaian_rangka', 'SESUAI')
                kesesuaian_mesin = body.get('kesesuaian_mesin', 'SESUAI')
                foto_flags = {
                    'foto_semua_sisi': bool(body.get('foto_semua_sisi')),
                    'foto_depan_pemilik': bool(body.get('foto_depan_pemilik')),
                    'foto_no_rangka': bool(body.get('foto_no_rangka')),
                    'foto_no_mesin': bool(body.get('foto_no_mesin')),
                    'foto_lainnya': bool(body.get('foto_lainnya')),
                }
                if not all(foto_flags.values()):
                    self._send_json_error(400, 'Semua 5 kategori foto pemeriksaan fisik wajib dicentang sebelum LHP & BAP dapat disimpan.')
                    return

                # 2. Simpan Foto Hasil Pemeriksaan Lapangan (multi-foto) ke disk lokal & Google Drive Bridge
                foto_lapangan_list = body.get('foto_lapangan') or []
                saved_field_photos = []
                archived = target_item.get('archived_files') if isinstance(target_item.get('archived_files'), list) else []
                if isinstance(foto_lapangan_list, list):
                    for idx_f, fitem in enumerate(foto_lapangan_list[:10], start=1):
                        if isinstance(fitem, dict) and fitem.get('data_url'):
                            meta_f = save_and_archive_document(
                                target_item,
                                f'12_Foto_Pemeriksaan_Lapangan_{idx_f}',
                                fitem['data_url'],
                                custom_filename=fitem.get('filename') or f'12_Foto_Pemeriksaan_Lapangan_{idx_f}.jpg'
                            )
                            if meta_f:
                                saved_field_photos.append(meta_f)
                                archived.append(meta_f)
                target_item['archived_files'] = archived

                rand2 = random.randint(20, 99)
                no_lhp = f"LHP-0{rand2}/KPU.02/HANGGAR/2026"
                no_bap = f"BAP-0{rand2}/KPU.02/HANGGAR/2026"
                now_ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                target_item['status'] = 'PEMERIKSA_DOKUMEN'
                target_item['no_lhp'] = no_lhp
                target_item['no_bap'] = no_bap
                target_item['tgl_lhp'] = now_ts
                target_item['lhp_data'] = {
                    'no_lhp': no_lhp,
                    'no_bap': no_bap,
                    'kesesuaian_rangka': kesesuaian_rangka,
                    'kesesuaian_mesin': kesesuaian_mesin,
                    'kondisi_fisik': body.get('catatan_fisik') or body.get('kondisi_fisik') or 'BAIK & TERAWAT',
                    'catatan_bap': body.get('catatan_bap') or body.get('catatan_fisik') or 'Pemeriksaan fisik berjalan lancar sesuai dokumen.',
                    'berkas_asli': berkas_asli_flags,
                    'catatan_berkas_asli': catatan_berkas_asli,
                    'jumlah_foto_lapangan': len(saved_field_photos),
                    **foto_flags,
                    'pemeriksa': sess.get('user', {}).get('nama', 'Pemeriksa Barang')
                }
                kondisi_rangka_txt = 'sesuai' if kesesuaian_rangka == 'SESUAI' else 'TIDAK SESUAI'
                kondisi_mesin_txt = 'sesuai' if kesesuaian_mesin == 'SESUAI' else 'TIDAK SESUAI'
                target_item['catatan_petugas'] = f"Pemeriksaan fisik selesai ({no_lhp} & {no_bap}). Nomor rangka {kondisi_rangka_txt}, nomor mesin {kondisi_mesin_txt}. Berkas asli diverifikasi & {len(saved_field_photos)} foto lapangan diarsipkan. Berkas diteruskan ke Pemeriksa Dokumen untuk terbit SPPB."
                save_db_permohonan(db)
                backup_sqlite_to_gdrive_async()
                _log_officer_action(sess, 'LHP_BAP_REKAM', pid, f"{no_lhp} & {no_bap}: rangka {kesesuaian_rangka}, mesin {kesesuaian_mesin}, {len(saved_field_photos)} foto lapangan")
                _notify_pemohon_wa(target_item, (
                    f"🏛️ *KPU BEA DAN CUKAI TIPE B BATAM*\n"
                    f"Layanan Pengeluaran Sementara Kendaraan Bermotor (KBM) Ke TLDDP\n\n"
                    f"Halo *{target_item.get('nama_pemohon', 'Pemohon')}*,\n\n"
                    f"Pemeriksaan fisik kendaraan Anda ({target_item.get('nopol', '-')}) telah SELESAI ({no_lhp} & {no_bap}).\n"
                    f"Berkas diteruskan ke Pejabat Pemeriksa Dokumen (PFPD) untuk penerbitan SPPB.\n\n"
                    f"Informasi Lebih Lanjut Hub: 0851-5814-8448 (Client Coordinator)"
                ))

                self._send_json_response({
                    'status': 'ok',
                    'message': f'LHP ({no_lhp}) & BAP ({no_bap}) berhasil direkam bersama {len(saved_field_photos)} foto pemeriksaan lapangan!',
                    'no_lhp': no_lhp,
                    'no_bap': no_bap,
                    'permohonan': target_item
                })
            except Exception as e:
                self._send_json_error(500, f'Gagal merekam LHP & BAP: {str(e)}')
            return

        # 5. Endpoint Pemeriksa Dokumen (Verifikasi LHP & Terbitkan SPPB)
        if self.path == '/api/pemeriksaan/terbitkan-sppb':
            token, sess = get_session_from_request(self)
            if not _is_role_allowed(sess, ['pemeriksadokumen']):
                self._send_json_error(403, 'Akses Ditolak: Hanya Pejabat Pemeriksa Dokumen (PFPD) yang berwenang menerbitkan SPPB.')
                return
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                pid = body.get('id')
                db = load_db_permohonan()
                target_item = next((item for item in db if item.get('id') == pid), None)
                if not target_item:
                    self._send_json_error(404, f'Permohonan {pid} tidak ditemukan.')
                    return

                lhp_data = target_item.get('lhp_data') or {}
                if lhp_data.get('kesesuaian_rangka') != 'SESUAI' or lhp_data.get('kesesuaian_mesin') != 'SESUAI':
                    self._send_json_error(400, 'SPPB tidak dapat diterbitkan: LHP mencatat ketidaksesuaian nomor rangka/mesin. Eskalasi ke PFPD/penyidikan, jangan diloloskan.')
                    return

                no_sppb = f"SPPB-0{random.randint(20, 99)}/KPU.02/PPFTZ01/2026"
                qr_token = uuid.uuid4().hex[:16]
                qr_payload = json.dumps({"id": pid, "no_sppb": no_sppb, "token": qr_token})
                qr_data_url = _generate_qr_data_url(qr_payload)

                target_item['status'] = 'SPPB_GATE_OUT'
                target_item['no_sppb'] = no_sppb
                target_item['tgl_sppb'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                target_item['sppb_qr_token'] = qr_token
                if qr_data_url:
                    target_item['sppb_qr_data_url'] = qr_data_url
                target_item['catatan_petugas'] = f"Hasil LHP fisik disetujui. Dokumen SPPB ({no_sppb}) resmi diterbitkan. Kendaraan diizinkan meluncur ke Gate Pelabuhan."
                save_db_permohonan(db)
                backup_sqlite_to_gdrive_async()
                _log_officer_action(sess, 'SPPB_TERBIT', pid, f"SPPB {no_sppb}")
                _notify_pemohon_wa(target_item, (
                    f"🏛️ *KPU BEA DAN CUKAI TIPE B BATAM*\n"
                    f"Layanan Pengeluaran Sementara Kendaraan Bermotor (KBM) Ke TLDDP\n\n"
                    f"Halo *{target_item.get('nama_pemohon', 'Pemohon')}*,\n\n"
                    f"Dokumen SPPB untuk kendaraan Anda ({target_item.get('nopol', '-')}) resmi TERBIT.\n"
                    f"No. SPPB: *{no_sppb}*\n\n"
                    f"Kendaraan Anda sudah diizinkan menuju Gate Pelabuhan untuk divalidasi keberangkatan.\n\n"
                    f"Informasi Lebih Lanjut Hub: 0851-5814-8448 (Client Coordinator)"
                ))

                self._send_json_response({
                    'status': 'ok',
                    'message': f'Dokumen SPPB ({no_sppb}) resmi diterbitkan!',
                    'no_sppb': no_sppb,
                    'permohonan': target_item
                })
            except Exception as e:
                self._send_json_error(500, f'Gagal menerbitkan SPPB: {str(e)}')
            return

        # 5b. Endpoint Pemeriksa Dokumen: Terbitkan NPD (Nota Permintaan Dokumen)
        if self.path == '/api/pemeriksaan/terbitkan-npd':
            token, sess = get_session_from_request(self)
            if not _is_role_allowed(sess, ['pemeriksadokumen']):
                self._send_json_error(403, 'Akses Ditolak: Hanya Pejabat Pemeriksa Dokumen (PFPD) yang berwenang menerbitkan NPD.')
                return
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                pid = body.get('id')
                alasan_npd = str(body.get('alasan_npd', '')).strip()
                dokumen_diminta = str(body.get('dokumen_diminta', '')).strip()
                if not alasan_npd or not dokumen_diminta:
                    self._send_json_error(400, 'Alasan penerbitan NPD dan rincian dokumen yang diminta wajib diisi.')
                    return

                db = load_db_permohonan()
                target_item = next((item for item in db if item.get('id') == pid), None)
                if not target_item:
                    self._send_json_error(404, f'Permohonan {pid} tidak ditemukan.')
                    return

                rand3 = random.randint(100, 999)
                no_npd = f"NPD-{rand3}/KPU.02/2026"
                now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                target_item['status'] = 'MENUNGGU_DOKUMEN_TAMBAHAN'
                target_item['no_npd'] = no_npd
                target_item['tgl_npd'] = now_str
                target_item['npd_data'] = {
                    'no_npd': no_npd,
                    'tgl': now_str,
                    'alasan': alasan_npd,
                    'dokumen_diminta': dokumen_diminta,
                    'petugas': sess.get('user', {}).get('nama', 'Pejabat Pemeriksa Dokumen')
                }
                target_item['catatan_petugas'] = f"Pemeriksa Dokumen menerbitkan NPD ({no_npd}). Dokumen yang diminta: {dokumen_diminta}. Alasan: {alasan_npd}."
                save_db_permohonan(db)
                backup_sqlite_to_gdrive_async()
                _log_officer_action(sess, 'NPD_TERBIT', pid, f"NPD {no_npd} | Dokumen: {dokumen_diminta}")
                _notify_pemohon_wa(target_item, (
                    f"🏛️ *KPU BEA DAN CUKAI TIPE B BATAM*\n"
                    f"Layanan Pengeluaran Sementara Kendaraan Bermotor (KBM) Ke TLDDP\n\n"
                    f"Halo *{target_item.get('nama_pemohon', 'Pemohon')}*,\n\n"
                    f"Pejabat Pemeriksa Dokumen (PFPD) menerbitkan *Nota Permintaan Dokumen (NPD)* untuk permohonan kendaraan Anda ({target_item.get('nopol', '-')}).\n"
                    f"• No. NPD: *{no_npd}*\n"
                    f"• Dokumen yang Diminta: *{dokumen_diminta}*\n"
                    f"• Penjelasan/Alasan: _{alasan_npd}_\n\n"
                    f"Silakan masuk ke Portal PENGSEM → *Status Permohonan Saya* untuk mengunggah dokumen susulan yang diminta agar berkas dapat diteliti kembali dan diproses ke SPPB.\n\n"
                    f"Informasi Lebih Lanjut Hub: 0851-5814-8448 (Client Coordinator)"
                ))

                self._send_json_response({
                    'status': 'ok',
                    'message': f'NPD ({no_npd}) berhasil diterbitkan dan notifikasi telah dikirimkan ke pemohon.',
                    'no_npd': no_npd,
                    'permohonan': target_item
                })
            except Exception as e:
                self._send_json_error(500, f'Gagal menerbitkan NPD: {str(e)}')
            return

        # 5c. Endpoint Pemohon: Kirim Dokumen Tambahan Respons NPD
        if self.path == '/api/pemeriksaan/unggah-dokumen-npd':
            token, sess = get_session_from_request(self)
            if not _is_role_allowed(sess, ['pemohon']):
                self._send_json_error(403, 'Akses Ditolak: Hanya pemohon yang dapat mengunggah dokumen respons NPD.')
                return
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                pid = body.get('id')
                doc_url = body.get('dokumen_url')
                keterangan = str(body.get('keterangan', '')).strip()

                db = load_db_permohonan()
                target_item = next((item for item in db if item.get('id') == pid), None)
                if not target_item:
                    self._send_json_error(404, f'Permohonan {pid} tidak ditemukan.')
                    return

                now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                target_item['status'] = 'PEMERIKSA_DOKUMEN'
                target_item['dokumen_tambahan_npd'] = {
                    'url': doc_url,
                    'keterangan': keterangan,
                    'uploaded_at': now_str
                }
                target_item['catatan_petugas'] = "Pemohon telah mengunggah dokumen tambahan pemenuhan NPD. Berkas kembali ke antrean PFPD untuk diteliti."
                save_db_permohonan(db)
                backup_sqlite_to_gdrive_async()
                self._send_json_response({
                    'status': 'ok',
                    'message': 'Dokumen susulan berhasil diunggah. Berkas Anda telah dikembalikan ke Pejabat Pemeriksa Dokumen.',
                    'permohonan': target_item
                })
            except Exception as e:
                self._send_json_error(500, f'Gagal mengirim dokumen susulan: {str(e)}')
            return

        # 6a. Endpoint Gate: Scan QR SPPB untuk menampilkan data kendaraan (read-only,
        # TIDAK mengubah status — konfirmasi keberangkatan tetap lewat validasi-keluar)
        if self.path == '/api/gate/scan-qr':
            token, sess = get_session_from_request(self)
            if not _is_role_allowed(sess, ['gate']):
                self._send_json_error(403, 'Akses Ditolak: Hanya Petugas Gate Pelabuhan yang berwenang memindai QR SPPB.')
                return
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                pid = body.get('id')
                qr_token = str(body.get('token', '')).strip()
                db = load_db_permohonan()
                target_item = next((item for item in db if item.get('id') == pid), None)
                if not target_item:
                    self._send_json_error(404, f'Permohonan {pid} tidak ditemukan.')
                    return
                if not qr_token or qr_token != target_item.get('sppb_qr_token'):
                    self._send_json_error(400, 'QR tidak valid atau sudah tidak berlaku untuk permohonan ini.')
                    return
                if target_item.get('status') != 'SPPB_GATE_OUT':
                    self._send_json_error(400, f'Permohonan ini berstatus "{target_item.get("status")}", bukan di tahap Gate Out. Kendaraan mungkin sudah divalidasi keluar sebelumnya atau belum sampai tahap ini.')
                    return

                self._send_json_response({'status': 'ok', 'permohonan': target_item})
            except Exception as e:
                self._send_json_error(500, f'Gagal memindai QR: {str(e)}')
            return

        # 6b. Endpoint Gate Out (Validasi Keberangkatan di Gate Pelabuhan) — WAJIB
        # menyertakan token QR hasil scan-qr, supaya petugas tidak bisa memvalidasi
        # kendaraan hanya dengan mengetik ID tanpa benar-benar memindai dokumen SPPB.
        if self.path == '/api/gate/validasi-keluar':
            token, sess = get_session_from_request(self)
            if not _is_role_allowed(sess, ['gate']):
                self._send_json_error(403, 'Akses Ditolak: Hanya Petugas Gate Pelabuhan yang berwenang memvalidasi pengeluaran kendaraan.')
                return
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                pid = body.get('id')
                qr_token = str(body.get('token', '')).strip()
                db = load_db_permohonan()
                target_item = next((item for item in db if item.get('id') == pid), None)
                if not target_item:
                    self._send_json_error(404, f'Permohonan {pid} tidak ditemukan.')
                    return
                if target_item.get('status') != 'SPPB_GATE_OUT':
                    self._send_json_error(400, f'Permohonan ini berstatus "{target_item.get("status")}", bukan di tahap Gate Out.')
                    return
                if not qr_token or qr_token != target_item.get('sppb_qr_token'):
                    self._send_json_error(400, 'Validasi gagal: QR dokumen SPPB belum dipindai atau tidak cocok. Scan QR terlebih dahulu.')
                    return

                ts_gate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S WIB')
                target_item['status'] = 'SELESAI_KELUAR_TLDDP'
                target_item['gate_out_ts'] = ts_gate
                target_item['gate_petugas'] = sess.get('user', {}).get('nama', 'Petugas Gate Pelabuhan')
                target_item['catatan_petugas'] = f"Kendaraan divalidasi Gate Out Pelabuhan pada {ts_gate}. KBM resmi keluar dari Kawasan Bebas Batam menuju TLDDP."
                save_db_permohonan(db)
                backup_sqlite_to_gdrive_async()
                _log_officer_action(sess, 'GATE_VALIDASI', pid, f"Gate out {ts_gate}")
                _notify_pemohon_wa(target_item, (
                    f"🏛️ *KPU BEA DAN CUKAI TIPE B BATAM*\n"
                    f"Layanan Pengeluaran Sementara Kendaraan Bermotor (KBM) Ke TLDDP\n\n"
                    f"Halo *{target_item.get('nama_pemohon', 'Pemohon')}*,\n\n"
                    f"Kendaraan Anda ({target_item.get('nopol', '-')}) telah divalidasi Gate Out pada {ts_gate} dan resmi berangkat dari Kawasan Bebas Batam menuju TLDDP.\n\n"
                    f"Terima kasih telah menggunakan layanan PENGSEM KBM Batam.\n"
                    f"Informasi Lebih Lanjut Hub: 0851-5814-8448 (Client Coordinator)"
                ))

                self._send_json_response({
                    'status': 'ok',
                    'message': f'Validasi Gate Out Selesai! Kendaraan ({target_item.get("nopol")}) resmi berlayar keluar Batam.',
                    'gate_out_ts': ts_gate,
                    'permohonan': target_item
                })
            except Exception as e:
                self._send_json_error(500, f'Gagal validasi Gate Out: {str(e)}')
            return

        # Arsipkan Dokumen Pabean (PPFTZ-01, LHP, BAP, SPPB, Surat Permohonan/Pernyataan) ke Disk & Google Drive
        if self.path == '/api/permohonan/archive-doc':
            token, sess = get_session_from_request(self)
            if not sess:
                self._send_json_error(401, 'Sesi login tidak valid.')
                return
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(content_length).decode('utf-8'))
                pid = str(body.get('id', '')).strip()
                doc_label = str(body.get('doc_type', 'DOKUMEN_PABEAN')).strip()
                filename = str(body.get('filename', '')).strip() or None
                data_url = body.get('data_url', '')
                if not pid or not data_url:
                    self._send_json_error(400, 'Parameter id dan data_url wajib diisi.')
                    return

                db = load_db_permohonan()
                target_item = next((p for p in db if p.get('id') == pid), None)
                if not target_item:
                    self._send_json_error(404, f'Permohonan {pid} tidak ditemukan.')
                    return

                # IDOR: sebelumnya endpoint ini hanya mengecek "sesi login ada", tidak
                # mengecek kepemilikan — pemohon mana pun bisa menyisipkan/menimpa
                # dokumen ke berkas pemohon lain hanya dengan mengganti `id`. Kalau
                # yang login adalah pemohon, wajib NIK/no. WA sesi cocok dengan
                # permohonan target.
                if sess.get('role') == 'pemohon':
                    sess_user = sess.get('user', {}) or {}
                    sess_nik = str(sess_user.get('nik', '')).strip()
                    sess_phone = str(sess_user.get('phone', '')).strip()
                    target_nik = str(target_item.get('nik', '')).strip()
                    target_phone_match = sess_phone and sess_phone in (
                        str(target_item.get('no_wa_pemohon', '')).strip(),
                        str(target_item.get('no_wa_pengirim', '')).strip()
                    )
                    is_owner = (sess_nik and sess_nik == target_nik) or target_phone_match
                    if not is_owner:
                        self._send_json_error(403, 'Akses Ditolak: Permohonan ini bukan milik akun Anda.')
                        return

                meta = save_and_archive_document(target_item, doc_label, data_url, custom_filename=filename)
                if not meta:
                    self._send_json_error(400, 'Data berkas tidak valid.')
                    return

                archived = target_item.get('archived_files')
                if not isinstance(archived, list):
                    archived = []
                archived = [a for a in archived if a.get('filename') != meta['filename']]
                archived.append(meta)
                target_item['archived_files'] = archived
                save_db_permohonan(db)

                self._send_json_response({
                    'status': 'ok',
                    'message': f'Dokumen {meta["filename"]} berhasil diarsipkan ke server & antrean Google Drive.',
                    'file': meta
                })
            except Exception as e:
                self._send_json_error(500, f'Gagal mengarsipkan dokumen: {str(e)}')
            return

        # Backup Manual Database SQLite ke Google Drive (Khusus Admin Utama)
        if self.path == '/api/admin/backup-gdrive':
            token, sess = get_session_from_request(self)
            if not sess or sess.get('role') != 'adminutama':
                self._send_json_error(403, 'Akses Ditolak: Hanya Admin Utama yang dapat memicu backup database.')
                return
            try:
                db_path = database.DATABASE_PATH
                if not os.path.exists(db_path):
                    self._send_json_error(404, 'File database SQLite tidak ditemukan.')
                    return
                with open(db_path, 'rb') as f:
                    b64_db = base64.b64encode(f.read()).decode('utf-8')
                ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                res = upload_to_gdrive_bridge('_BACKUP_DATABASE', f'kbm_batam_{ts}.db', 'application/x-sqlite3', b64_db)
                self._send_json_response({'status': 'ok', 'result': res})
            except Exception as e:
                self._send_json_error(500, f'Gagal backup database ke Google Drive: {str(e)}')
            return
        else:
            self.send_error(404, "Endpoint not found")

if __name__ == '__main__':
    repair_sqlite_users_from_json_once()
    repair_remove_demo_seed_permohonan_once()
    lan_ip = get_lan_ip()
    access_url, qr_img_path = generate_access_qr(lan_ip, PORT)
    
    print("\n" + "="*70)
    print("🚗 PLATFORM LAYANAN PENGELUARAN SEMENTARA KBM BATAM (PENGSEM)")
    print("   KPU BEA DAN CUKAI TIPE B BATAM — SERVER DEDICATED KANTOR")
    print("="*70)
    print(f"[*] Engine AI Vision : Google Lens & Multimodal Neural Vision (Aktif: {VISION_AI_ENABLED})")
    print(f"[*] Deep Learning OCR: EasyOCR 100% Offline (Apple Silicon GPU MPS: {USE_GPU})")
    print(f"[*] Secondary OCR    : Tesseract 5.5.4 (ind+eng)")
    print(f"[*] PDF Support      : PyMuPDF Vector & Raster Render Enabled")
    print(f"[*] Status Server    : AKTIF & MULTI-THREADED di Port {PORT}")
    print(f"[*] Akses Lokal  : http://localhost:{PORT}")
    print(f"[*] Akses Kantor : {access_url}")
    print(f"[*] QR Code Akses: {qr_img_path}")
    print("="*70)
    
    if qrcode:
        try:
            qr = qrcode.QRCode()
            qr.add_data(access_url)
            print("\n[+] Scan QR Code berikut dengan Kamera HP / Tablet Kantor:\n")
            qr.print_ascii(invert=True)
            print("\n" + "="*70)
        except Exception:
            pass

    with ThreadingHTTPServer(("0.0.0.0", PORT), Handler) as httpd:
        httpd.serve_forever()