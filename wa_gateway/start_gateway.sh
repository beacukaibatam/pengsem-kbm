#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

if [ ! -d "node_modules" ]; then
  echo "[*] Menginstal dependensi Node.js (@whiskeysockets/baileys, express, qrcode)..."
  npm install
fi

if [ ! -f ".env" ]; then
  echo "[!] File wa_gateway/.env belum ditemukan."
  echo "    Salin dari .env.example lalu isi WA_GATEWAY_SECRET terlebih dahulu:"
  echo "    cp wa_gateway/.env.example wa_gateway/.env"
  echo "    (atau buat secret acak: openssl rand -hex 32)"
  exit 1
fi

echo "[*] Menjalankan PENGSEM KBM WhatsApp Gateway di http://127.0.0.1:${PORT:-3001} ..."
exec node --dns-result-order=ipv4first --no-network-family-autoselection index.js
