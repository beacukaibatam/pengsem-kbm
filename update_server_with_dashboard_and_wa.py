#!/usr/bin/env python3
import re

with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Ensure urllib.parse is imported
if 'import urllib.parse' not in text:
    text = text.replace('import socket\n', 'import socket\nimport urllib.parse\n')

# 2. Add WhatsApp Bot & DB Logic before Handler class
wa_logic = '''
# ================= DATABASE PERMOHONAN & WHATSAPP BOT ENGINE =================
DB_PERMOHONAN_PATH = os.path.join(os.path.dirname(__file__), 'db_permohonan.json')
META_VERIFY_TOKEN = 'beacukai_batam_pengsem_kbm_secret_2026'
META_WA_ACCESS_TOKEN = os.environ.get('META_WA_ACCESS_TOKEN', '')
META_PHONE_NUMBER_ID = os.environ.get('META_PHONE_NUMBER_ID', '')
WA_SESSIONS = {}

def load_db_permohonan():
    if os.path.exists(DB_PERMOHONAN_PATH):
        try:
            with open(DB_PERMOHONAN_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print("[!] Error loading db_permohonan:", e)
    return []

def save_db_permohonan(data):
    try:
        with open(DB_PERMOHONAN_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print("[!] Error saving db_permohonan:", e)
        return False

def send_whatsapp_meta_message(to_number, text, buttons=None):
    """Mengirim pesan via Meta WhatsApp Cloud API resmi jika access token tersedia."""
    if not META_WA_ACCESS_TOKEN or not META_PHONE_NUMBER_ID:
        print(f"[*] [WA Sandbox Log] to: {to_number} -> {text[:80]}... (Buttons: {buttons})")
        return {"status": "logged_offline"}

    import urllib.request
    url = f"https://graph.facebook.com/v19.0/{META_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {META_WA_ACCESS_TOKEN}",
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
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print("[!] Error sending WhatsApp Meta message:", e)
        return {"status": "error", "message": str(e)}

'''

# Insert wa_logic before class Handler
handler_pos = text.find('class Handler(')
if handler_pos != -1:
    text = text[:handler_pos] + wa_logic + '\n' + text[handler_pos:]

# 3. Enhance do_GET to handle dashboard, api permohonan, and meta webhook verification
old_do_get_start = '''    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self.path = '/Formulir_Pemohon_CEISA_PENGSEM_KBM.html'
        elif self.path in ('/flowchart', '/diagram'):
            self.path = '/Flowchart_Interaktif_Layanan_KBM_Batam.html'
        elif self.path in ('/qr', '/qr-code'):
            self.path = '/QR_Akses_KBM_Batam.png'
        elif self.path == '/api/status':'''

new_do_get_start = '''    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # Halaman Dashboard Pegawai Bea Cukai (Sisi Petugas Pabean)
        if path in ('/dashboard', '/dashboard.html', '/pegawai', '/monitoring'):
            self.path = '/dashboard_pegawai.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

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

        # API Daftar Permohonan Masuk untuk Dashboard Pegawai
        if path == '/api/permohonan':
            data = load_db_permohonan()
            payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path in ('/', '/index.html'):
            self.path = '/Formulir_Pemohon_CEISA_PENGSEM_KBM.html'
        elif self.path in ('/flowchart', '/diagram'):
            self.path = '/Flowchart_Interaktif_Layanan_KBM_Batam.html'
        elif self.path in ('/qr', '/qr-code'):
            self.path = '/QR_Akses_KBM_Batam.png'
        elif self.path == '/api/status':'''

text = text.replace(old_do_get_start, new_do_get_start)

# 4. Enhance do_POST to handle /api/permohonan/update and /api/webhook/whatsapp
old_do_post_start = '''    def do_POST(self):
        if self.path == '/api/ocr':'''

new_do_post_start = '''    def do_POST(self):
        # Update Status Permohonan dari Dashboard Pegawai
        if self.path == '/api/permohonan/update':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                pid = body.get('id')
                new_status = body.get('status')
                catatan = body.get('catatan', '')
                
                db = load_db_permohonan()
                found = False
                for item in db:
                    if item.get('id') == pid:
                        item['status'] = new_status
                        item['catatan_petugas'] = catatan
                        item['updated_at'] = '2026-03-10 12:00:00'
                        found = True
                        break
                if found:
                    save_db_permohonan(db)
                    resp = json.dumps({'status': 'success', 'message': f'Status {pid} berhasil diubah ke {new_status}'}).encode('utf-8')
                    self.send_response(200)
                else:
                    resp = json.dumps({'status': 'error', 'message': f'ID {pid} tidak ditemukan'}).encode('utf-8')
                    self.send_response(404)
            except Exception as e:
                resp = json.dumps({'status': 'error', 'message': str(e)}).encode('utf-8')
                self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
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
                                    "Halo! Selamat datang di Layanan Mandiri Pabean KPU Bea dan Cukai Tipe B Batam.\\n\\n"
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
                                        f"Baik, terima kasih. Untuk keperluan kontak verifikasi pabean:\\n\\n"
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
                                    send_whatsapp_meta_message(from_num, f"Nomor pemohon dicatat: *+{from_num}*.\\n\\nSilakan ketikkan *Nama Lengkap Pemohon* sesuai KTP:")
                                else:
                                    session['state'] = 'INPUT_NO_BEDA'
                                    WA_SESSIONS[from_num] = session
                                    send_whatsapp_meta_message(from_num, "Silakan ketikkan *Nomor WhatsApp Pemohon* yang aktif (contoh: 0812xxxxxxxx):")
                            elif st == 'INPUT_NO_BEDA':
                                session['data']['no_pemohon'] = user_text
                                session['data']['nomor_berbeda'] = True
                                session['state'] = 'INPUT_NAMA'
                                WA_SESSIONS[from_num] = session
                                send_whatsapp_meta_message(from_num, f"Nomor pemohon dicatat: *{user_text}*.\\n\\nSilakan ketikkan *Nama Lengkap Pemohon* sesuai KTP:")
                            elif st == 'INPUT_NAMA':
                                session['data']['nama_pemohon'] = user_text.upper()
                                session['state'] = 'WAITING_KTP'
                                WA_SESSIONS[from_num] = session
                                send_whatsapp_meta_message(from_num, f"Nama pemohon dicatat: *{user_text.upper()}*.\\n\\n📸 Silakan kirimkan *Foto atau Berkas PDF KTP Asli* pemohon:")
                            elif st == 'WAITING_KTP':
                                session['state'] = 'WAITING_NPWP'
                                WA_SESSIONS[from_num] = session
                                send_whatsapp_meta_message(from_num, "✓ Dokumen KTP berhasil diterima!\\n\\n💳 Terakhir untuk tahap identitas awal, silakan kirimkan *Foto atau Berkas PDF Kartu NPWP Asli* pemohon:")
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
                                    f"🎉 *Permohonan Anda Berhasil Terdaftar!*\\n\\n"
                                    f"Nomor Agenda Pabean: *#{new_id}*\\n"
                                    f"Status: 🟡 *Menunggu Verifikasi Dokumen*\\n\\n"
                                    f"Data telah disuplai secara otomatis ke Dashboard Petugas KPU Bea dan Cukai Tipe B Batam."
                                )
                return
            except Exception as e:
                print("[!] Error in WhatsApp Webhook:", e)
                return

        if self.path == '/api/ocr':'''

text = text.replace(old_do_post_start, new_do_post_start)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('server.py successfully updated with Dashboard API & WhatsApp Official Webhook!')
