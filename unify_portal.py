import re

# 1. Update index.html to include Live Chat Modal and Navbar button
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add Live Chat button in portal-actions
target_actions = '<div class="portal-actions" style="display:none;">'
replacement_actions = '''<div class="portal-actions">
                <button type="button" class="btn-portal-action" onclick="openLiveChatModal()" style="background:#059669; color:#FFFFFF; border:none; display:flex; align-items:center; gap:6px; font-weight:700; cursor:pointer;">
                    💬 Konsol Live Chat WA (+62 851-4490-1346)
                </button>'''

if target_actions in html:
    html = html.replace(target_actions, replacement_actions, 1)
    print('Added Live Chat button to index.html portal-actions')

# Add liveChatModal before </body> or before script
with open('dashboard_pegawai.html', 'r', encoding='utf-8') as f:
    dash_html = f.read()

# Extract liveChatModal from dashboard_pegawai.html
modal_start = dash_html.find('<!-- KONSOL LIVE CHAT OPERATOR WHATSAPP OFFICIAL META')
modal_end = dash_html.find('<!-- SCRIPT CLIENT LOGIC -->', modal_start)
if modal_start != -1 and modal_end != -1:
    live_chat_modal_code = dash_html[modal_start:modal_end]
    if 'liveChatModal' not in html:
        target_insert = '<!-- DRAWER DETAIL VERIFIKASI PETUGAS -->'
        html = html.replace(target_insert, live_chat_modal_code + '\n    ' + target_insert, 1)
        print('Inserted liveChatModal into index.html')

# Extract Live Chat JS functions from dashboard_pegawai.html
js_start = dash_html.find('// ================= KONSOL OPERATOR LIVE CHAT WHATSAPP RESMI')
js_end = dash_html.find('function promptChangeSenderNumber()', js_start)
if js_end == -1: js_end = dash_html.find('</script>', js_start)

if js_start != -1 and js_end != -1:
    live_chat_js_code = dash_html[js_start:js_end]
    if 'openLiveChatModal' not in html:
        idx_sc = html.rfind('</script>')
        html = html[:idx_sc] + '\n' + live_chat_js_code + '\n' + html[idx_sc:]
        print('Inserted Live Chat JS into index.html')

# Add check for ?view= URL param in window.onload
url_param_js = '''
        // Deteksi parameter URL (?view=formulir atau ?view=dashboard)
        const urlParams = new URLSearchParams(window.location.search);
        const viewParam = urlParams.get('view');
        if (viewParam === 'formulir') {
            switchPortalView('formulir');
        } else if (viewParam === 'dashboard' || window.location.pathname.includes('dashboard')) {
            switchPortalView('dashboard');
        }
'''
if 'urlParams.get(\'view\')' not in html:
    idx_init = html.find('document.addEventListener(\'DOMContentLoaded\', () => {')
    if idx_init != -1:
        html = html[:idx_init] + url_param_js + '\n        ' + html[idx_init:]
        print('Added URL param handling to index.html')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Saved updated index.html')


# 2. Update server.py routing
with open('server.py', 'r', encoding='utf-8') as f:
    server_code = f.read()

# Update /dashboard routing to serve index.html with dashboard view
old_routing = '''        # Halaman Dashboard Pegawai Bea Cukai (Sisi Petugas Pabean)
        if path in ('/dashboard', '/dashboard.html', '/pegawai', '/monitoring'):
            self.path = '/dashboard_pegawai.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)'''

new_routing = '''        # Halaman Portal Terpadu (Dashboard & Formulir KBM Batam)
        if path in ('/dashboard', '/dashboard.html', '/pegawai', '/monitoring', '/formulir'):
            self.path = '/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)'''

if old_routing in server_code:
    server_code = server_code.replace(old_routing, new_routing, 1)
    print('Updated /dashboard routing in server.py to unified index.html')

# Update / routing
old_root = '''        if self.path in ('/', '/index.html'):
            self.path = '/Formulir_Pemohon_CEISA_PENGSEM_KBM.html\''''

new_root = '''        if self.path in ('/', '/index.html'):
            self.path = '/index.html\''''

if old_root in server_code:
    server_code = server_code.replace(old_root, new_root, 1)
    print('Updated root / routing in server.py to unified index.html')

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(server_code)

import py_compile
py_compile.compile('server.py', doraise=True)
print('server.py compiled and verified!')
