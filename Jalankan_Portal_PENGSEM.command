#!/bin/bash
# ==============================================================================
# SCRIPT STANDALONE: JALANKAN PORTAL PENGSEM KBM BATAM
# Jalankan script ini langsung dari Finder (klik ganda) atau Terminal macOS.
# Server akan tetap aktif meskipun aplikasi Antigravity ditutup atau di-restart.
# ==============================================================================

cd "$(dirname "$0")" || exit 1

echo "=========================================================="
echo "  SISTEM PENGELUARAN SEMENTARA KBM (PENGSEM) BATAM"
echo "  KPU Bea dan Cukai Tipe B Batam"
echo "=========================================================="
echo ""

# Cek apakah port 8080 sudah berjalan
PID_EXISTING=$(lsof -ti :8080 2>/dev/null)
if [ -n "$PID_EXISTING" ]; then
    echo "[INFO] Port 8080 sedang aktif (PID: $PID_EXISTING)."
    echo "[INFO] Menghentikan sesi lama untuk refresh..."
    kill -9 $PID_EXISTING 2>/dev/null
    sleep 1
fi

echo "[START] Menyalakan Backend Server Python di Port 8080..."
python3 server.py
