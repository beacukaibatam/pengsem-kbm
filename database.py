import os
import sqlite3
import json
import logging
from datetime import datetime, timedelta

DATABASE_PATH = os.environ.get('DATABASE_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kbm_batam.db'))

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

    # 2. Tabel OTP Sessions
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

    conn.commit()
    conn.close()
    logger.info("Database SQLite WAL initialized at: %s", DATABASE_PATH)

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
                    cursor.execute('''
                        INSERT OR IGNORE INTO permohonan
                        (id, created_at, tanggal_pengajuan, nama_pemohon, nik, npwp, no_wa_pemohon, no_wa_pengirim,
                         nomor_berbeda, nopol, merek_tipe, tahun_warna, no_rangka, no_mesin, pelabuhan_tujuan,
                         keperluan, status, catatan_petugas, no_nadine, no_kep, no_jaminan, no_ppftz, no_sppb,
                         dokumen_json, pemeriksaan_json, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        now_str
                    ))
            conn.commit()
            logger.info("Migrated permohonan from %s into SQLite", permohonan_file)
        except Exception as e:
            logger.error("Error migrating permohonan: %s", e)

    conn.close()

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
            user_data.get('password'),
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
            user_data.get('password', '123456'),
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
    """Memperbarui kata sandi pengguna."""
    user = find_user_by_identifier(identifier)
    if not user:
        return False
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("UPDATE users SET password = ?, updated_at = ? WHERE id = ?", (new_password, now_str, user['id']))
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

# ================= PERMOHONAN MANAGEMENT =================

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
    return d

def save_new_permohonan(p):
    """Menyimpan permohonan baru dari pemohon."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pid = p.get('id') or f"KBM-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    cursor.execute('''
        INSERT INTO permohonan
        (id, created_at, tanggal_pengajuan, nama_pemohon, nik, npwp, no_wa_pemohon, no_wa_pengirim,
         nomor_berbeda, nopol, merek_tipe, tahun_warna, no_rangka, no_mesin, pelabuhan_tujuan,
         keperluan, status, catatan_petugas, no_nadine, no_kep, no_jaminan, no_ppftz, no_sppb,
         dokumen_json, pemeriksaan_json, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

    query = "UPDATE permohonan SET status = ?, updated_at = ?"
    params = [new_status, now_str]

    if catatan:
        query += ", catatan_petugas = ?"
        params.append(catatan)

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

    query += " WHERE id = ?"
    params.append(pid)

    cursor.execute(query, tuple(params))
    conn.commit()
    conn.close()
    return True
