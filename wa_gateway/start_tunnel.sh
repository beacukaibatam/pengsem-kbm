#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "[!] cloudflared belum terpasang. Instal dengan: brew install cloudflared"
  exit 1
fi

if [ -f ".env" ]; then
  # Muat variabel opsional dari .env
  set -a
  # shellcheck disable=SC1091
  source ".env"
  set +a
fi

PORT="${PORT:-3001}"

if [ -n "${CLOUDFLARED_TUNNEL_TOKEN:-}" ]; then
  echo "[*] Menjalankan Cloudflare Named Tunnel permanen -> http://127.0.0.1:${PORT} ..."
  exec cloudflared tunnel run --token "$CLOUDFLARED_TUNNEL_TOKEN"
else
  echo "[*] Menjalankan Cloudflare Quick Tunnel gratis -> http://127.0.0.1:${PORT} ..."
  echo "    Salin URL https://....trycloudflare.com yang muncul ke env WA_GATEWAY_URL di Render Dashboard."
  echo "    (Catatan: Quick Tunnel berubah URL bila di-restart; untuk URL permanen gunakan Cloudflare Named Tunnel gratis.)"
  exec cloudflared tunnel --url "http://127.0.0.1:${PORT}"
fi
