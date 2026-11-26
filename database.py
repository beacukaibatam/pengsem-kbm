import os
import shutil
import sqlite3
import json
import logging
from datetime import datetime, timedelta

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.environ.get('DATABASE_PATH', os.path.join(_APP_DIR, 'kbm_batam.db'))

# Migrasi sekali jalan: salin kbm_batam.db lama dari folder repo ke Persistent Disk
# (DATABASE_PATH custom) bila disk masih kosong, agar data tidak hilang saat migrasi.
# os.path.abspath() dipakai agar DATABASE_PATH relatif (mis. "kbm_batam.db" tanpa folder)
# tidak membuat os.path.dirname() mengembalikan string kosong lalu makedirs('') error.
_db_dir = os.path.dirname(os.path.abspath(DATABASE_PATH))
if _db_dir and _db_dir != _APP_DIR:
    os.makedirs(_db_dir, exist_ok=True)
    _legacy_db = os.path.join(_APP_DIR, 'kbm_batam.db')
    if os.path.exists(_legacy_db) and not os.path.exists(DATABASE_PATH):
        try:
            shutil.copy2(_legacy_db, DATABASE_PATH)
            print(f"[+] Migrasi database lama -> Persistent Disk: {DATABASE_PATH}")
        except Exception as e:
            print("[!] Gagal migrasi kbm_batam.db ke DATABASE_PATH:", e)

logger = logging.getLogger("KBM_DB")

def get_db_connection():
    """Mengembalikan koneksi SQLite dengan mode WAL dan thread-safety aktif."""
    conn = sqlite3.connect(DATABASE_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA busy_timeout=30000;")
    return conn

def init_db():
    """Menginisialisasi tabel-tabel terindeks di basis data SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Tabel Users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        nama TEXT,
        nip TEXT,
        nik TEXT,
        phone TEXT,
        email TEXT,
        jabatan TEXT,
        role TEXT NOT NULL,
        is_officer INTEGER DEFAULT 0,
        created_at TEXT,
        updated_at TEXT
    );
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);')

    # 2. Tabel OTP Sessions & Registrations
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS otp_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        identifier TEXT NOT NULL,
        channel TEXT DEFAULT 'whatsapp',
        otp_code TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        is_used INTEGER DEFAULT 0,
        attempts INTEGER DEFAULT 0,
        created_at TEXT
    );
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_otp_identifier ON otp_sessions(identifier, is_used);')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS otp_registrations (
        phone TEXT PRIMARY KEY,
        otp TEXT NOT NULL,
        expires_at REAL NOT NULL,
        nik TEXT,
        nama TEXT,
        email TEXT,
        password TEXT,
        created_at TEXT
    );
    ''')

    # 3. Tabel Permohonan
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS permohonan (
        id TEXT PRIMARY KEY,
        created_at TEXT,
        tanggal_pengajuan TEXT,
        nama_pemohon TEXT,
        nik TEXT,
        npwp TEXT,
        no_wa_pemohon TEXT,
        no_wa_pengirim TEXT,
        nomor_berbeda INTEGER DEFAULT 0,
        nopol TEXT,
        merek_tipe TEXT,
        tahun_warna TEXT,
        no_rangka TEXT,
        no_mesin TEXT,
        pelabuhan_tujuan TEXT,
        keperluan TEXT,
        status TEXT NOT NULL,
        catatan_petugas TEXT,
        no_nadine TEXT,
        no_kep TEXT,
        no_jaminan TEXT,
        no_ppftz TEXT,
        no_sppb TEXT,
        dokumen_json TEXT,
        pemeriksaan_json TEXT,
        updated_at TEXT
    );
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_permohonan_status ON permohonan(status);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_permohonan_nik ON permohonan(nik);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_permohonan_nopol ON permohonan(nopol);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_permohonan_wa ON permohonan(no_wa_pemohon);')

    # Kolom tangkapan untuk field dinamis yang terus bertambah sepanjang alur petugas
    # (lhp_data, no_skep, no_surat_s, kode_billing, nilai_jaminan, tgl_*, sppb_qr_*, dst.)
    # — skema tabel ini TIDAK punya kolom untuk masing-masing, jadi dulu field-field itu
    # SELALU HILANG begitu dibaca lagi dari SQLite (update_permohonan_status diam-diam
    # membuangnya). ALTER TABLE dibungkus try/except karena SQLite tidak punya
    # "ADD COLUMN IF NOT EXISTS" dan kolom ini mungkin sudah ada dari start sebelumnya.
    try:
        cursor.execute('ALTER TABLE permohonan ADD COLUMN extra_json TEXT')
    except Exception:
        pass

    # 4. Tabel Log Aktivitas — dipantau admin utama untuk deteksi anomali pada
    # akun pemohon maupun petugas (login, aksi tahap, override, kelola akun).
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        actor_username TEXT,
        actor_role TEXT,
        action TEXT NOT NULL,
        detail TEXT,
        target_id TEXT
    );
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_log(timestamp DESC);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity_actor ON activity_log(actor_username);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity_action ON activity_log(action);')

    conn.commit()
    conn.close()
    logger.info("Database SQLite WAL initialized at: %s", DATABASE_PATH)


def log_activity(actor_username, actor_role, action, detail='', target_id=''):
    """Catat satu baris aktivitas untuk dipantau admin utama. Kegagalan mencatat
    TIDAK BOLEH menggagalkan aksi utama yang sedang berjalan — selalu redam error."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO activity_log (timestamp, actor_username, actor_role, action, detail, target_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            actor_username or '-',
            actor_role or '-',
            action,
            detail or '',
            target_id or ''
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error("Error logging activity: %s", e)


def get_activity_log(limit=200, role_filter=None, action_filter=None, search=None):
    """Ambil log aktivitas terbaru, opsional difilter role/aksi/kata kunci pencarian."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM activity_log WHERE 1=1"
    params = []
    if role_filter:
        query += " AND actor_role = ?"
        params.append(role_filter)
    if action_filter:
        query += " AND action = ?"
        params.append(action_filter)
    if search:
        query += " AND (actor_username LIKE ? OR detail LIKE ? OR target_id LIKE ?)"
        like = f"%{search}%"
        params.extend([like, like, like])
    query += " ORDER BY id DESC LIMIT ?"
    params.append(int(limit))
    cursor.execute(query, tuple(params))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def migrate_from_json(users_file='db_users.json', permohonan_file='db_permohonan.json'):
    """Melakukan migrasi data awal dari file JSON ke SQLite bila tabel masih kosong."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    users_path = os.path.join(base_dir, users_file)
    perm_path = os.path.join(base_dir, permohonan_file)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Migrasi Users
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    if user_count == 0 and os.path.exists(users_path):
        try:
            with open(users_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                users_list = []
                if isinstance(data, list):
                    users_list = data
                elif isinstance(data, dict):
                    if 'pegawai' in data or 'pemohon' in data:
                        users_list = data.get('pegawai', []) + data.get('pemohon', [])
                    else:
                        users_list = data.get('users', [])
                now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                for u in users_list:
                    username = u.get('username') or u.get('phone') or u.get('email')
                    if not username:
                        continue
                    cursor.execute('''
                        INSERT OR IGNORE INTO users 
                        (username, password, nama, nip, nik, phone, email, jabatan, role, is_officer, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        username,
                        u.get('password', '123456'),
                        u.get('nama', ''),
                        u.get('nip', ''),
                        u.get('nik', ''),
                        u.get('phone', ''),
                        u.get('email', ''),
                        u.get('jabatan', ''),
                        u.get('role', 'pemohon'),
                        1 if u.get('is_officer') else 0,
                        u.get('created_at', now_str),
                        now_str
                    ))
            conn.commit()
            logger.info("Migrated users from %s into SQLite", users_file)
        except Exception as e:
            logger.error("Error migrating users: %s", e)

    # Migrasi Permohonan
    cursor.execute("SELECT COUNT(*) FROM permohonan")
    perm_count = cursor.fetchone()[0]
    if perm_count == 0 and os.path.exists(perm_path):
        try:
            with open(perm_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                perm_list = data if isinstance(data, list) else data.get('permohonan', [])
                now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                for p in perm_list:
                    pid = p.get('id')
                    if not pid:
                        continue
                    extra = {k: v for k, v in p.items() if k not in KNOWN_PERMOHONAN_COLUMNS}
                    cursor.execute('''
                        INSERT OR IGNORE INTO permohonan
                        (id, created_at, tanggal_pengajuan, nama_pemohon, nik, npwp, no_wa_pemohon, no_wa_pengirim,
                         nomor_berbeda, nopol, merek_tipe, tahun_warna, no_rangka, no_mesin, pelabuhan_tujuan,
                         keperluan, status, catatan_petugas, no_nadine, no_kep, no_jaminan, no_ppftz, no_sppb,
                         dokumen_json, pemeriksaan_json, extra_json, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        pid,
                        p.get('created_at', now_str),
                        p.get('tanggal_pengajuan', ''),
                        p.get('nama_pemohon', ''),
                        p.get('nik', ''),
                        p.get('npwp', ''),
                        p.get('no_wa_pemohon', ''),
                        p.get('no_wa_pengirim', ''),
                        1 if p.get('nomor_berbeda') else 0,
                        p.get('nopol', ''),
                        p.get('merek_tipe', ''),
                        p.get('tahun_warna', ''),
                        p.get('no_rangka', ''),
                        p.get('no_mesin', ''),
                        p.get('pelabuhan_tujuan', ''),
                        p.get('keperluan', ''),
                        p.get('status', 'FRONTDESK_NADINE'),
                        p.get('catatan_petugas', ''),
                        p.get('no_nadine', ''),
                        p.get('no_kep', ''),
                        p.get('no_jaminan', ''),
                        p.get('no_ppftz', ''),
                        p.get('no_sppb', ''),
                        json.dumps(p.get('dokumen', {})),
                        json.dumps(p.get('pemeriksaan', {})),
                        json.dumps(extra),
                        now_str
                    ))
            conn.commit()
            logger.info("Migrated permohonan from %s into SQLite", permohonan_file)
        except Exception as e:
            logger.error("Error migrating permohonan: %s", e)

    conn.close()

# ================= PASSWORD HASHING (PBKDF2-SHA256) =================
import hashlib
import hmac

_PBKDF2_ITERATIONS = 120000

def hash_password(plain):
    """Hash kata sandi dengan PBKDF2-SHA256 + salt acak 16-byte (idempotent jika sudah di-hash)."""
    if plain is None:
        return None
    s = str(plain)
    if not s:
        return s
    if s.startswith('pbkdf2_sha256$'):
        return s
    salt = os.urandom(16).hex()
    dk = hashlib.pbkdf2_hmac('sha256', s.encode('utf-8'), bytes.fromhex(salt), _PBKDF2_ITERATIONS).hex()
    return f"pbkdf2_sha256${_PBKDF2_ITERATIONS}${salt}${dk}"

def verify_password(plain, stored):
    """Verifikasi kata sandi (mendukung hash PBKDF2-SHA256 & fallback migrasi plaintext lama secara constant-time)."""
    if plain is None or stored is None:
        return False
    p = str(plain).strip()
    st = str(stored).strip()
    if not p or not st:
        return False
    if st.startswith('pbkdf2_sha256$'):
        try:
            _, iter_str, salt_hex, hash_hex = st.split('$', 3)
            dk = hashlib.pbkdf2_hmac('sha256', p.encode('utf-8'), bytes.fromhex(salt_hex), int(iter_str)).hex()
            return hmac.compare_digest(dk, hash_hex)
        except Exception:
            return False
    return hmac.compare_digest(p, st)

# ================= CRUD FUNCTIONS =================

def find_user_by_identifier(identifier):
    """Mencari user berdasarkan username, phone, email, nip, atau nik secara normalisasi."""
    if not identifier:
        return None
    ident = str(identifier).strip()
    norm = ident.lower().replace(' ', '').replace('-', '').replace('+', '')

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Exact match
    cursor.execute("""
        SELECT * FROM users 
        WHERE username = ? OR phone = ? OR email = ? OR nip = ? OR nik = ?
    """, (ident, ident, ident, ident, ident))
    row = cursor.fetchone()

    # 2. Normalized match jika exact tidak ketemu
    if not row:
        cursor.execute("SELECT * FROM users")
        all_users = cursor.fetchall()
        for u in all_users:
            u_clean = (u['username'] or '').lower().replace(' ', '').replace('-', '')
            p_clean = (u['phone'] or '').replace('+', '').replace('-', '').replace(' ', '')
            e_clean = (u['email'] or '').lower().strip()
            nip_clean = (u['nip'] or '').strip()
            nik_clean = (u['nik'] or '').strip()
            if norm in [u_clean, p_clean, e_clean, nip_clean, nik_clean]:
                row = u
                break

    conn.close()
    return dict(row) if row else None

def save_or_update_user(user_data):
    """Menyimpan atau memperbarui user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    username = user_data.get('username') or user_data.get('phone') or user_data.get('email')
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    existing = cursor.fetchone()

    raw_pwd = user_data.get('password')
    hashed_pwd = hash_password(raw_pwd) if raw_pwd else None

    if existing:
        cursor.execute('''
            UPDATE users SET 
                password = COALESCE(?, password),
                nama = COALESCE(?, nama),
                nip = COALESCE(?, nip),
                nik = COALESCE(?, nik),
                phone = COALESCE(?, phone),
                email = COALESCE(?, email),
                jabatan = COALESCE(?, jabatan),
                role = COALESCE(?, role),
                is_officer = COALESCE(?, is_officer),
                updated_at = ?
            WHERE id = ?
        ''', (
            hashed_pwd,
            user_data.get('nama'),
            user_data.get('nip'),
            user_data.get('nik'),
            user_data.get('phone'),
            user_data.get('email'),
            user_data.get('jabatan'),
            user_data.get('role'),
            1 if user_data.get('is_officer') else 0,
            now_str,
            existing['id']
        ))
    else:
        cursor.execute('''
            INSERT INTO users 
            (username, password, nama, nip, nik, phone, email, jabatan, role, is_officer, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            username,
            hash_password(user_data.get('password', '123456')),
            user_data.get('nama', ''),
            user_data.get('nip', ''),
            user_data.get('nik', ''),
            user_data.get('phone', ''),
            user_data.get('email', ''),
            user_data.get('jabatan', ''),
            user_data.get('role', 'pemohon'),
            1 if user_data.get('is_officer') else 0,
            now_str,
            now_str
        ))

    conn.commit()
    conn.close()

def update_user_password(identifier, new_password):
    """Memperbarui kata sandi pengguna (tersimpan dalam bentuk hash PBKDF2-SHA256)."""
    user = find_user_by_identifier(identifier)
    if not user:
        return False
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("UPDATE users SET password = ?, updated_at = ? WHERE id = ?", (hash_password(new_password), now_str, user['id']))
    conn.commit()
    conn.close()
    return True

# ================= OTP MANAGEMENT =================

def save_otp_session(identifier, otp_code, channel='whatsapp', duration_minutes=5):
    """Menyimpan sesi kode OTP dengan masa berlaku 5 menit."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now()
    expires_at = (now + timedelta(minutes=duration_minutes)).strftime('%Y-%m-%d %H:%M:%S')
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')

    # Nonaktifkan OTP sebelumnya untuk identifier yang sama
    cursor.execute("UPDATE otp_sessions SET is_used = 1 WHERE identifier = ? AND is_used = 0", (identifier,))
    cursor.execute('''
        INSERT INTO otp_sessions (identifier, channel, otp_code, expires_at, is_used, attempts, created_at)
        VALUES (?, ?, ?, ?, 0, 0, ?)
    ''', (identifier, channel, otp_code, expires_at, now_str))

    conn.commit()
    conn.close()

def verify_otp_session(identifier, input_otp):
    """Memverifikasi kode OTP yang valid dan belum kadaluarsa."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
        SELECT * FROM otp_sessions 
        WHERE identifier = ? AND is_used = 0 AND expires_at > ?
        ORDER BY id DESC LIMIT 1
    ''', (identifier, now_str))
    session = cursor.fetchone()

    if not session:
        conn.close()
        return False, "Kode OTP telah kadaluarsa atau tidak ditemukan."

    if session['otp_code'] == input_otp.strip():
        cursor.execute("UPDATE otp_sessions SET is_used = 1 WHERE id = ?", (session['id'],))
        conn.commit()
        conn.close()
        return True, "Verifikasi OTP Berhasil."
    else:
        cursor.execute("UPDATE otp_sessions SET attempts = attempts + 1 WHERE id = ?", (session['id'],))
        conn.commit()
        conn.close()
        return False, "Kode OTP salah."

def save_registration_otp(phone, otp_data):
    """Menyimpan sesi OTP registrasi ke SQLite WAL untuk persistensi lintas restart/worker."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO otp_registrations (phone, otp, expires_at, nik, nama, email, password, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(phone),
            str(otp_data.get('otp', '')),
            float(otp_data.get('expires_at', 0)),
            str(otp_data.get('nik', '')),
            str(otp_data.get('nama', '')),
            str(otp_data.get('email', '')),
            str(otp_data.get('password', '')),
            str(otp_data.get('created_at', ''))
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print('[!] Error saving registration OTP to SQLite:', e)
        return False

def load_all_registration_otps():
    """Mengambil semua sesi OTP registrasi yang belum kedaluwarsa dari SQLite."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        now = time.time()
        cursor.execute("SELECT * FROM otp_registrations WHERE expires_at > ?", (now,))
        rows = cursor.fetchall()
        result = {}
        for r in rows:
            result[r['phone']] = {
                'otp': r['otp'],
                'expires_at': r['expires_at'],
                'nik': r['nik'],
                'nama': r['nama'],
                'email': r['email'],
                'password': r['password'],
                'created_at': r['created_at']
            }
        conn.close()
        return result
    except Exception as e:
        print('[!] Error loading registration OTPs from SQLite:', e)
        return {}

def delete_registration_otp(phone):
    """Menghapus sesi OTP registrasi dari SQLite setelah diverifikasi."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM otp_registrations WHERE phone = ?", (str(phone),))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print('[!] Error deleting registration OTP from SQLite:', e)
        return False

# ================= PERMOHONAN MANAGEMENT =================

# Kolom tetap tabel `permohonan` (lihat init_db). Field apa pun di luar daftar ini yang
# dikirim dari server.py disimpan sebagai JSON gabungan di kolom extra_json, lalu
# dibongkar kembali di sini supaya hasil baca tetap selengkap data yang ditulis.
KNOWN_PERMOHONAN_COLUMNS = {
    'id', 'created_at', 'tanggal_pengajuan', 'nama_pemohon', 'nik', 'npwp', 'no_wa_pemohon',
    'no_wa_pengirim', 'nomor_berbeda', 'nopol', 'merek_tipe', 'tahun_warna', 'no_rangka',
    'no_mesin', 'pelabuhan_tujuan', 'keperluan', 'status', 'catatan_petugas', 'no_nadine',
    'no_kep', 'no_jaminan', 'no_ppftz', 'no_sppb', 'dokumen', 'pemeriksaan',
    'dokumen_json', 'pemeriksaan_json', 'updated_at', 'extra_json'
}

def _unpack_extra_json(d):
    if d.get('extra_json'):
        try:
            extra = json.loads(d['extra_json'])
            if isinstance(extra, dict):
                for k, v in extra.items():
                    d[k] = v
        except Exception:
            pass
    return d

def get_all_permohonan():
    """Mengambil semua daftar permohonan terurut dari yang terbaru."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM permohonan ORDER BY created_at DESC")
    rows = cursor.fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d['nomor_berbeda'] = bool(d.get('nomor_berbeda'))
        # Parse nested json jika ada
        if d.get('dokumen_json'):
            try: d['dokumen'] = json.loads(d['dokumen_json'])
            except: d['dokumen'] = {}
        if d.get('pemeriksaan_json'):
            try: d['pemeriksaan'] = json.loads(d['pemeriksaan_json'])
            except: d['pemeriksaan'] = {}
        d = _unpack_extra_json(d)
        result.append(d)
    conn.close()
    return result

def get_permohonan_by_id(pid):
    """Mengambil satu permohonan berdasarkan ID agenda."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM permohonan WHERE id = ?", (pid,))
    r = cursor.fetchone()
    conn.close()
    if not r:
        return None
    d = dict(r)
    d['nomor_berbeda'] = bool(d.get('nomor_berbeda'))
    if d.get('dokumen_json'):
        try: d['dokumen'] = json.loads(d['dokumen_json'])
        except: d['dokumen'] = {}
    if d.get('pemeriksaan_json'):
        try: d['pemeriksaan'] = json.loads(d['pemeriksaan_json'])
        except: d['pemeriksaan'] = {}
    d = _unpack_extra_json(d)
    return d

def save_new_permohonan(p):
    """Menyimpan permohonan baru dari pemohon."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pid = p.get('id') or f"KBM-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    extra = {k: v for k, v in p.items() if k not in KNOWN_PERMOHONAN_COLUMNS}

    cursor.execute('''
        INSERT INTO permohonan
        (id, created_at, tanggal_pengajuan, nama_pemohon, nik, npwp, no_wa_pemohon, no_wa_pengirim,
         nomor_berbeda, nopol, merek_tipe, tahun_warna, no_rangka, no_mesin, pelabuhan_tujuan,
         keperluan, status, catatan_petugas, no_nadine, no_kep, no_jaminan, no_ppftz, no_sppb,
         dokumen_json, pemeriksaan_json, extra_json, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        pid,
        p.get('created_at', now_str),
        p.get('tanggal_pengajuan', now_str),
        p.get('nama_pemohon', ''),
        p.get('nik', ''),
        p.get('npwp', ''),
        p.get('no_wa_pemohon', ''),
        p.get('no_wa_pengirim', ''),
        1 if p.get('nomor_berbeda') else 0,
        p.get('nopol', ''),
        p.get('merek_tipe', ''),
        p.get('tahun_warna', ''),
        p.get('no_rangka', ''),
        p.get('no_mesin', ''),
        p.get('pelabuhan_tujuan', ''),
        p.get('keperluan', ''),
        p.get('status', 'FRONTDESK_NADINE'),
        p.get('catatan_petugas', ''),
        p.get('no_nadine', ''),
        p.get('no_kep', ''),
        p.get('no_jaminan', ''),
        p.get('no_ppftz', ''),
        p.get('no_sppb', ''),
        json.dumps(p.get('dokumen', {})),
        json.dumps(p.get('pemeriksaan', {})),
        json.dumps(extra),
        now_str
    ))
    conn.commit()
    conn.close()
    return pid

def update_permohonan_status(pid, new_status, catatan='', updates=None):
    """Memperbarui status dan field terkait permohonan."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Field apa pun di luar kolom tetap (lhp_data, no_skep, kode_billing, nilai_jaminan,
    # tgl_*, sppb_qr_*, nadine_meta, dst.) digabung ke extra_json — dibaca dulu lalu
    # di-merge, supaya nilai lama yang tidak ikut di-update kali ini tidak hilang.
    cursor.execute("SELECT extra_json FROM permohonan WHERE id = ?", (pid,))
    row = cursor.fetchone()
    existing_extra = {}
    if row and row[0]:
        try:
            existing_extra = json.loads(row[0]) or {}
        except Exception:
            existing_extra = {}

    query = "UPDATE permohonan SET status = ?, updated_at = ?"
    params = [new_status, now_str]

    if catatan:
        query += ", catatan_petugas = ?"
        params.append(catatan)

    extra_changed = False
    if updates:
        for k, v in updates.items():
            if k in ['no_nadine', 'no_kep', 'no_jaminan', 'no_ppftz', 'no_sppb']:
                query += f", {k} = ?"
                params.append(v)
            elif k == 'dokumen':
                query += ", dokumen_json = ?"
                params.append(json.dumps(v))
            elif k == 'pemeriksaan':
                query += ", pemeriksaan_json = ?"
                params.append(json.dumps(v))
            elif k not in KNOWN_PERMOHONAN_COLUMNS:
                existing_extra[k] = v
                extra_changed = True

    if extra_changed:
        query += ", extra_json = ?"
        params.append(json.dumps(existing_extra))

    query += " WHERE id = ?"
    params.append(pid)

    cursor.execute(query, tuple(params))
    conn.commit()
    conn.close()
    return True
