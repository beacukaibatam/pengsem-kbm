#!/usr/bin/env python3
"""
AI Vision Knowledge Base Builder & Training Script
Mengekstrak data ground truth dari berkas permohonan riil di folder DATA CONTOH PERMOHONAN
untuk membangun database referensi kepabeanan KBM Batam.
"""

import os
import sys
import fitz
import json
import re
import io
from PIL import Image
import pytesseract
from concurrent.futures import ThreadPoolExecutor

PDF_DIR = "/Users/macridm4/Library/CloudStorage/GoogleDrive-ridwanmuham17@gmail.com/My Drive/PENGELUARAN_SEMENTARA_KBM_BATAM/DATA CONTOH PERMOHONAN"
OUTPUT_KB = "/Users/macridm4/Library/CloudStorage/GoogleDrive-ridwanmuham17@gmail.com/My Drive/PENGELUARAN_SEMENTARA_KBM_BATAM/kbm_domain_knowledge.json"

print(f"[*] Memulai Ekstraksi AI Vision dari: {PDF_DIR}")

files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]
print(f"[*] Total file ditemukan: {len(files)} berkas")

knowledge_base = {
    "total_files_analyzed": len(files),
    "sample_nik_prefixes": set(),
    "known_applicants": [],
    "known_vehicles": [],
    "known_leasing_companies": set(),
    "known_districts_batam": set([
        "BATAM KOTA", "BATU AMPAR", "BENGKONG", "LUBUK BAJA",
        "SEKUPANG", "SAGULUNG", "NONGSA", "BATU AJI",
        "SEI BEDUK", "BELAKANG PADANG", "GALANG", "BULANG"
    ]),
    "vehicle_brands": set([
        "TOYOTA", "HONDA", "MITSUBISHI", "DAIHATSU", "SUZUKI",
        "NISSAN", "MAZDA", "HYUNDAI", "WULING", "ISUZU",
        "BMW", "MERCEDES-BENZ", "FORD", "CHEVROLET", "KIA"
    ]),
    "ports_routes": set([
        "TELAGA PUNGGUR", "KUALA TUNGKAL", "SEI PAKNING", "TANJUNG BUTON",
        "TANJUNG UBAN", "DUMAI", "MENGKAPAN", "KAMPAR"
    ])
}

# Regex Patterns
RE_NIK = re.compile(r'\b(2171\d{12}|[1-9]\d{15})\b')
RE_NPWP = re.compile(r'\b(\d{2}[\.\s]?\d{3}[\.\s]?\d{3}[\.\s]?\d{1}[\.\s\-]?\d{3}[\.\s]?\d{3}|\d{15,16})\b')
RE_NOPOL = re.compile(r'\b(BP\s?[0-9]{1,4}\s?[A-Z]{1,3})\b')
RE_RANGKA = re.compile(r'\b([A-HJ-NPR-Z0-9]{17})\b')
RE_WA = re.compile(r'\b(08[1-9][0-9]{8,11})\b')

def process_file(fname):
    filepath = os.path.join(PDF_DIR, fname)
    extracted = {
        "file": fname,
        "nik": None,
        "nama": None,
        "npwp": None,
        "nopol": None,
        "norangka": None,
        "nomesin": None,
        "merek": None,
        "leasing": None
    }
    
    try:
        doc = fitz.open(filepath)
        full_text = ""
        
        # Cek hingga 8 halaman awal
        max_p = min(len(doc), 8)
        for pno in range(max_p):
            page = doc[pno]
            # Prioritaskan get_text jika ada text layer
            t = page.get_text()
            if len(t.strip()) > 30:
                full_text += "\n" + t
            else:
                # OCR cepat 120 DPI
                pix = page.get_pixmap(dpi=120)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                ocr_t = pytesseract.image_to_string(img, lang="ind+eng")
                full_text += "\n" + ocr_t
        doc.close()
        
        upper = full_text.upper()
        
        # Ekstrak NIK
        nik_match = RE_NIK.search(upper)
        if nik_match:
            extracted["nik"] = nik_match.group(1).replace(" ", "")
            knowledge_base["sample_nik_prefixes"].add(extracted["nik"][:6])
            
        # Ekstrak Nopol
        nopol_match = RE_NOPOL.search(upper)
        if nopol_match:
            extracted["nopol"] = re.sub(r'\s+', ' ', nopol_match.group(1))
            
        # Ekstrak No Rangka
        rangka_match = RE_RANGKA.search(upper)
        if rangka_match:
            extracted["norangka"] = rangka_match.group(1)
            
        # Ekstrak Merek
        for b in knowledge_base["vehicle_brands"]:
            if b in upper:
                extracted["merek"] = b
                break
                
        # Ekstrak Leasing
        for l in ["PEGADAIAN", "BCA FINANCE", "MANDIRI TUNAS FINANCE", "ADIRA", "ACC", "ASTRA SEDAYA", "OTTO", "FIF", "OTO MULTIARTHA", "MEGA FINANCE"]:
            if l in upper:
                extracted["leasing"] = l
                knowledge_base["known_leasing_companies"].add(l)
                break
                
        # Ekstrak Nama Pemohon
        nama_match = re.search(r'(?:NAMA|PEMOHON)[\s\:\=]+([A-Z\s\.]{4,35})', upper)
        if nama_match:
            cand = nama_match.group(1).strip()
            # Bersihkan dari kata kunci formulir
            banned = ["KENDARAAN", "BERMOTOR", "SURAT", "PERMOHONAN", "KEPALA", "KANTOR", "PELAYANAN", "BEA", "CUKAI"]
            if not any(b in cand for b in banned) and len(cand.split()) >= 2:
                extracted["nama"] = cand
                
        return extracted
    except Exception as e:
        return None

# Eksekusi secara multi-threaded (maksimal 4 thread agar stabil di Apple Silicon)
results = []
print("[*] Mengekstrak ground-truth secara multi-threaded...")
with ThreadPoolExecutor(max_workers=4) as executor:
    # Uji 40 berkas representatif pertama
    sample_files = files[:40]
    futures = [executor.submit(process_file, f) for f in sample_files]
    for idx, f in enumerate(futures):
        res = f.result()
        if res:
            results.append(res)
            if idx % 5 == 0:
                print(f"  [+] Diproses {idx+1}/{len(sample_files)} berkas: {res.get('file')} -> Nopol: {res.get('nopol')}, NIK: {res.get('nik')}")

# Konversi set ke list untuk JSON
output_data = {
    "total_files_analyzed": len(results),
    "sample_nik_prefixes": sorted(list(knowledge_base["sample_nik_prefixes"])),
    "known_districts_batam": sorted(list(knowledge_base["known_districts_batam"])),
    "vehicle_brands": sorted(list(knowledge_base["vehicle_brands"])),
    "known_leasing_companies": sorted(list(knowledge_base["known_leasing_companies"])),
    "ports_routes": sorted(list(knowledge_base["ports_routes"])),
    "extracted_entities": results
}

with open(OUTPUT_KB, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"[✓] Knowledge Base berhasil dibuat: {OUTPUT_KB}")
print(f"[✓] Berhasil mengekstrak {len(results)} entitas permohonan riil!")
