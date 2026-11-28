#!/usr/bin/env python3
"""
cleanup_contaminated_drafts.py

Script pembersihan satu kali (one-off maintenance script) untuk memeriksa dan
membersihkan draf formulir pemohon (tabel form_drafts di kbm_batam.db) yang
terkontaminasi data/dokumen PII milik akun lain sebelum remediasi session reset
diterapkan.

PENTING:
- Script ini TIDAK otomatis menghapus tanpa konfirmasi interaktif operator.
- Menampilkan daftar draf yang dicurigai terkontaminasi untuk di-review.
- Hanya membersihkan field identitas/PII yang tercemar (KTP, NPWP, NIK, OCR KTP/NPWP, foto KTP/NPWP),
  sedangkan data non-identitas (kendaraan, STNK, BPKB jika sah) tetap dipertahankan.
- Mendukung argumen CLI:
    --dry-run : Menampilkan analisis tanpa melakukan perubahan apa pun
    --all     : Membersihkan semua draf yang terdeteksi tercemar setelah konfirmasi
    --clean-id <identifier> : Membersihkan draf spesifik
"""

import sys
import os
import json
import re
import sqlite3
import argparse

DB_FILE = os.environ.get("DATABASE_PATH", "kbm_batam.db")

def _norm_cmp(s):
    if not s:
        return ""
    return re.sub(r'[^A-Z0-9]', '', str(s).upper())

def _norm_phone(p):
    if not p:
        return ""
    digits = re.sub(r'[^0-9]', '', str(p))
    if digits.startswith("62"):
        digits = "0" + digits[2:]
    return digits

def get_db_connection(db_path=DB_FILE):
    if not os.path.exists(db_path):
        print(f"[!] Database file '{db_path}' tidak ditemukan.")
        sys.exit(1)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def load_all_users(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, nama, role, phone, nik FROM users WHERE role = 'pemohon'")
    users = cursor.fetchall()
    user_list = [dict(u) for u in users]
    return user_list

def find_matching_user(ident, saved_by, fields, user_list):
    """
    Mencari akun pemohon yang sah untuk draf tertentu.
    """
    ident_str = str(ident or "")
    saved_uid = str((saved_by or {}).get("id", "")).strip()
    saved_phone = _norm_phone((saved_by or {}).get("phone", ""))
    field_telp = _norm_phone((fields or {}).get("pemohon_telp", ""))
    field_nik = _norm_cmp((fields or {}).get("pemohon_nik", ""))

    # 1. Cek by UID
    if saved_uid:
        for u in user_list:
            if str(u.get("id")) == saved_uid:
                return u
    if ident_str.startswith("pemohon:uid_"):
        uid_part = ident_str.replace("pemohon:uid_", "").strip()
        for u in user_list:
            if str(u.get("id")) == uid_part:
                return u

    # 2. Cek by Phone
    target_phones = [p for p in (saved_phone, field_telp) if p]
    if ident_str.startswith("pemohon:") and not ident_str.startswith("pemohon:uid_"):
        val = ident_str.replace("pemohon:", "").strip()
        if len(val) >= 9 and len(val) <= 14:
            target_phones.append(_norm_phone(val))

    for p in target_phones:
        for u in user_list:
            u_phone = _norm_phone(u.get("phone", ""))
            if u_phone and (u_phone == p or u_phone.endswith(p[-8:]) or p.endswith(u_phone[-8:])):
                return u

    # 3. Cek by NIK akun di ident
    if ident_str.startswith("pemohon:") and len(ident_str.replace("pemohon:", "").strip()) == 16:
        nik_part = ident_str.replace("pemohon:", "").strip()
        for u in user_list:
            if _norm_cmp(u.get("nik", "")) == _norm_cmp(nik_part):
                return u

    return None

def analyze_drafts(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT pemohon_identifier, data_json, updated_at FROM form_drafts ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    user_list = load_all_users(conn)

    suspects = []

    for idx, r in enumerate(rows, 1):
        ident = r["pemohon_identifier"]
        raw_json = r["data_json"]
        updated_at = r["updated_at"]
        try:
            data = json.loads(raw_json)
        except Exception as e:
            print(f"[!] Gagal decode JSON untuk identifier {ident}: {e}")
            continue

        saved_by = data.get("saved_by", {})
        fields = data.get("fields", {}) or {}
        ocr = data.get("ocr", {}) or {}
        ktp_ocr = (ocr.get("ktp", {}) if isinstance(ocr, dict) else {}) or {}
        images = data.get("images", {}) or {}

        user = find_matching_user(ident, saved_by, fields, user_list)

        # Nilai pembanding
        owner_name = user.get("nama", "") if user else fields.get("pemohon_nama", "")
        owner_nik = user.get("nik", "") if user else ""
        owner_phone = user.get("phone", "") if user else fields.get("pemohon_telp", "")

        ocr_ktp_nama = ktp_ocr.get("nama", "")
        ocr_ktp_nik = ktp_ocr.get("nik", "")
        draft_nik = fields.get("pemohon_nik", "")

        has_ktp_img = bool(images.get("imgKtpPreview"))
        has_npwp_img = bool(images.get("imgNpwpPreview"))

        reasons = []

        norm_owner_name = _norm_cmp(owner_name)
        norm_ocr_name = _norm_cmp(ocr_ktp_nama)

        # Deteksi 1: Nama di KTP OCR bertolak belakang dengan Nama Akun / Nama di Fields
        if norm_owner_name and norm_ocr_name and len(norm_owner_name) >= 3 and len(norm_ocr_name) >= 3:
            if norm_owner_name not in norm_ocr_name and norm_ocr_name not in norm_owner_name:
                reasons.append(f"Nama OCR KTP ('{ocr_ktp_nama}') tidak cocok dengan Nama Akun/Pemohon ('{owner_name}')")

        # Deteksi 2: NIK OCR KTP atau fields tidak cocok dengan NIK Akun terdaftar
        norm_owner_nik = _norm_cmp(owner_nik)
        norm_ocr_nik = _norm_cmp(ocr_ktp_nik)
        norm_draft_nik = _norm_cmp(draft_nik)

        if norm_owner_nik and norm_ocr_nik and norm_owner_nik != norm_ocr_nik:
            reasons.append(f"NIK OCR KTP ('{ocr_ktp_nik}') beda dengan NIK Akun ('{owner_nik}')")
        if norm_owner_nik and norm_draft_nik and norm_owner_nik != norm_draft_nik:
            reasons.append(f"NIK field pemohon ('{draft_nik}') beda dengan NIK Akun ('{owner_nik}')")

        # Deteksi 3: NIK OCR beda dengan draft_nik secara signifikan
        if norm_ocr_nik and norm_draft_nik and norm_ocr_nik != norm_draft_nik:
            reasons.append(f"NIK OCR KTP ('{ocr_ktp_nik}') beda dengan NIK field ('{draft_nik}')")

        if reasons:
            suspects.append({
                "no": idx,
                "identifier": ident,
                "updated_at": updated_at,
                "owner_user": user,
                "owner_name": owner_name,
                "owner_phone": owner_phone,
                "owner_nik": owner_nik,
                "ocr_ktp_nama": ocr_ktp_nama,
                "ocr_ktp_nik": ocr_ktp_nik,
                "draft_nik": draft_nik,
                "has_ktp_img": has_ktp_img,
                "has_npwp_img": has_npwp_img,
                "reasons": reasons,
                "raw_data": data
            })

    return suspects, len(rows)

def clean_draft_pii(data):
    """
    Membersihkan HANYA field-field identitas yang terkontaminasi:
    - fields.pemohon_nik, fields.pemohon_npwp
    - images.imgKtpPreview, images.imgNpwpPreview
    - ocr.ktp, ocr.npwp
    Data kendaraan (kbm_*), STNK, BPKB, dll. dipertahankan.
    """
    cleaned = dict(data)
    
    # 1. Bersihkan fields
    if "fields" in cleaned and isinstance(cleaned["fields"], dict):
        cleaned["fields"] = dict(cleaned["fields"])
        cleaned["fields"].pop("pemohon_nik", None)
        cleaned["fields"].pop("pemohon_npwp", None)

    # 2. Bersihkan images
    if "images" in cleaned and isinstance(cleaned["images"], dict):
        cleaned["images"] = dict(cleaned["images"])
        cleaned["images"].pop("imgKtpPreview", None)
        cleaned["images"].pop("imgNpwpPreview", None)

    # 3. Reset OCR
    if "ocr" in cleaned and isinstance(cleaned["ocr"], dict):
        cleaned["ocr"] = dict(cleaned["ocr"])
        cleaned["ocr"]["ktp"] = {}
        cleaned["ocr"]["npwp"] = {}

    return cleaned

def perform_cleanup(conn, targets):
    cursor = conn.cursor()
    success_count = 0
    for t in targets:
        ident = t["identifier"]
        cleaned_data = clean_draft_pii(t["raw_data"])
        cleaned_json = json.dumps(cleaned_data, ensure_ascii=False)
        cursor.execute("UPDATE form_drafts SET data_json = ? WHERE pemohon_identifier = ?", (cleaned_json, ident))
        success_count += 1
        print(f"[✓] Berhasil membersihkan identitas terkontaminasi pada draf: {ident}")
    conn.commit()
    print(f"\n[DONE] Selesai membersihkan {success_count} draf.")

def main():
    parser = argparse.ArgumentParser(description="Script Pembersihan Draf Terkontaminasi PII")
    parser.add_argument("--dry-run", action="store_true", help="Analisis saja tanpa melakukan modifikasi ke database")
    parser.add_argument("--all", action="store_true", help="Bersihkan seluruh draf tercemar yang terdeteksi")
    parser.add_argument("--clean-id", type=str, help="Bersihkan identifier spesifik")
    args = parser.parse_args()

    conn = get_db_connection()
    suspects, total_count = analyze_drafts(conn)

    print("=" * 80)
    print(f"ANALISIS TABEL form_drafts ({total_count} total draf tersimpan)")
    print("=" * 80)

    if not suspects:
        print("[✓] Aman: Tidak ditemukan draf yang terkontaminasi atau mismatch identitas.")
        conn.close()
        return

    print(f"[!] Ditemukan {len(suspects)} draf dengan anomali/kontaminasi identitas:\n")
    for s in suspects:
        print(f"[{s['no']}] Identifier : {s['identifier']}")
        print(f"    Akun Pemilik: {s['owner_name']} (Telp: {s['owner_phone']}, NIK Akun: {s['owner_nik'] or '-'})")
        print(f"    Data Draf   : NIK Field: {s['draft_nik'] or '-'}")
        print(f"    OCR KTP     : Nama: {s['ocr_ktp_nama'] or '-'}, NIK: {s['ocr_ktp_nik'] or '-'}")
        print(f"    Foto Tersimpan: KTP={'Ya' if s['has_ktp_img'] else 'Tidak'}, NPWP={'Ya' if s['has_npwp_img'] else 'Tidak'}")
        print(f"    Anomali     : {'; '.join(s['reasons'])}")
        print("-" * 80)

    if args.dry_run:
        print("\n[DRY RUN] Mode analisis aktif. Tidak ada perubahan yang disimpan ke database.")
        conn.close()
        return

    targets_to_clean = []

    if args.clean_id:
        match = [s for s in suspects if s["identifier"] == args.clean_id]
        if not match:
            print(f"[!] Identifier '{args.clean_id}' tidak ditemukan di antara draf tercemar.")
            conn.close()
            return
        targets_to_clean = match
    elif args.all:
        confirm = input(f"\nApakah Anda yakin ingin membersihkan SEMUA {len(suspects)} draf di atas? [y/N]: ").strip().lower()
        if confirm == 'y':
            targets_to_clean = suspects
        else:
            print("[x] Dibatalkan oleh pengguna.")
            conn.close()
            return
    else:
        # Pilihan interaktif
        print("\nPilih tindakan pembersihan:")
        print("  - Ketik nomor (misal '1' atau '1,2')")
        print("  - Ketik 'all' untuk membersihkan semua")
        print("  - Ketik 'none' atau kosongkan untuk membatalkan")
        choice = input("Masukkan pilihan: ").strip().lower()
        if not choice or choice in ('none', 'n', 'q', 'exit'):
            print("[x] Tidak ada perubahan yang dilakukan.")
            conn.close()
            return
        if choice == 'all':
            targets_to_clean = suspects
        else:
            indices = [c.strip() for c in choice.split(",") if c.strip()]
            for item in indices:
                try:
                    num = int(item)
                    m = next((s for s in suspects if s["no"] == num), None)
                    if m:
                        targets_to_clean.append(m)
                    else:
                        print(f"[!] Nomor {num} tidak valid.")
                except ValueError:
                    print(f"[!] Input '{item}' bukan nomor yang valid.")

    if not targets_to_clean:
        print("[x] Tidak ada target yang dipilih untuk dibersihkan.")
        conn.close()
        return

    print(f"\nMenyiapkan pembersihan untuk {len(targets_to_clean)} draf...")
    perform_cleanup(conn, targets_to_clean)
    conn.close()

if __name__ == "__main__":
    main()
