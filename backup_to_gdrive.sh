#!/bin/zsh
# Backup snapshot lengkap proyek PENGSEM KBM Batam ke Google Drive (Force Majeure Backup)
# Tanpa folder .git/ agar tidak pernah menimbulkan konflik lock Google Drive.

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
GDRIVE_ROOT="$HOME/Library/CloudStorage/GoogleDrive-ridwanmuham17@gmail.com/My Drive/PENGELUARAN_SEMENTARA_KBM_BATAM/BACKUP_WEBSITE"
TS="$(date '+%Y%m%d_%H%M%S')"
ZIP_PATH="$GDRIVE_ROOT/SNAPSHOTS/pengsem_kbm_${TS}.zip"
LATEST_DIR="$GDRIVE_ROOT/LATEST_SOURCE"
SECRETS_DIR="$GDRIVE_ROOT/BACKUP_SECRETS"

if [ ! -d "$HOME/Library/CloudStorage/GoogleDrive-ridwanmuham17@gmail.com/My Drive" ]; then
  echo "[!] Folder Google Drive ridwanmuham17@gmail.com tidak ditemukan di mesin ini."
  exit 1
fi

mkdir -p "$GDRIVE_ROOT/SNAPSHOTS" "$LATEST_DIR" "$SECRETS_DIR"

echo "[*] Menyelaraskan kode sumber terbaru ke $LATEST_DIR (tanpa .git & .env)..."
rsync -a --delete \
  --exclude '.git/' \
  --exclude '.env' \
  --exclude '.env.*' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude '.DS_Store' \
  "$REPO_DIR/" "$LATEST_DIR/"

echo "[*] Membuat arsip ZIP bertanggal: $ZIP_PATH ..."
(cd "$LATEST_DIR" && zip -rq "$ZIP_PATH" .)

if [ -f "$REPO_DIR/.env" ]; then
  cp "$REPO_DIR/.env" "$SECRETS_DIR/env_backup_${TS}.txt"
  cp "$REPO_DIR/.env" "$SECRETS_DIR/env_latest.txt"
  echo "[+] Backup .env tersimpan di $SECRETS_DIR/"
fi

echo "[+] Backup selesai!"
echo "    - Folder terbaru : $LATEST_DIR"
echo "    - Arsip ZIP      : $ZIP_PATH"
