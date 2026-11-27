# Self-Hosted WhatsApp Gateway (`wa_gateway/`) — Mac Mini

Layanan gateway WhatsApp mandiri berbasis **Node.js + `@whiskeysockets/baileys`** (Rp 0, tanpa Docker, bebas aturan 24 jam & bebas blokir Meta Cloud API). Nomor WhatsApp tetap bisa dipakai seperti biasa di aplikasi WhatsApp HP karena terhubung lewat fitur resmi **Perangkat Tertaut (Linked Devices)**.

---

## 1. Instalasi & Konfigurasi Awal (Sekali Saja)

```bash
cd ~/Projects/pengsem-kbm/wa_gateway
npm install
cp .env.example .env
```

Buat secret acak 64 karakter hex lalu masukkan ke `wa_gateway/.env` pada baris `WA_GATEWAY_SECRET=...`:
```bash
openssl rand -hex 32
```

> **Keamanan:** Folder `wa_gateway/auth_info/` (sesi WhatsApp) dan file `wa_gateway/.env` sudah masuk `.gitignore` dan **tidak akan pernah** ter-commit ke GitHub.

---

## 2. Jalankan Gateway & Scan QR Pertama Kali

```bash
cd ~/Projects/pengsem-kbm/wa_gateway
./start_gateway.sh
```

1. QR Code akan muncul langsung di terminal (atau buka di browser Mac Mini: `http://127.0.0.1:3001/qr`).
2. Di HP yang memiliki nomor WhatsApp layanan: buka **WhatsApp → Perangkat Tertaut → Tautkan Perangkat → Scan QR**.
3. Setelah terhubung, terminal menampilkan:
   `[+] WhatsApp Gateway TERHUBUNG! Nomor aktif: +628...`
4. Cek status kapan saja:
   ```bash
   curl http://127.0.0.1:3001/health
   ```

---

## 3. Ekspos Aman ke Internet via Cloudflare Tunnel (`cloudflared`)

Backend Render Cloud (`https://api-kbm-beacukaibatam.onrender.com`) membutuhkan URL HTTPS publik untuk memanggil gateway Mac Mini.

### Opsi A — Cepat (Quick Tunnel, langsung dapat HTTPS gratis)
Buka tab terminal kedua:
```bash
cd ~/Projects/pengsem-kbm/wa_gateway
./start_tunnel.sh
```
Salin URL `https://<acak>.trycloudflare.com` yang muncul ke Environment Variable `WA_GATEWAY_URL` di Dashboard Render.

### Opsi B — Permanen Gratis (Cloudflare Zero Trust Named Tunnel — Disarankan untuk Produksi)
1. Login ke [Cloudflare Zero Trust Dashboard](https://one.dash.cloudflare.com/) → **Networks → Tunnels → Create a tunnel → Cloudflared**.
2. Beri nama mis. `pengsem-kbm-wa`, salin token tunnel ke `CLOUDFLARED_TUNNEL_TOKEN=...` di `wa_gateway/.env`.
3. Pada tab **Public Hostname**, arahkan subdomain (mis. `wa-gw.domainanda.com`) ke `HTTP://127.0.0.1:3001`.
4. Jalankan `./start_tunnel.sh` — URL permanen tidak berubah meskipun Mac Mini di-restart.

---

## 4. Auto-Start di Mac Mini (`launchd`)

Agar gateway otomatis menyala setiap kali Mac Mini hidup/reboot, simpan file plist berikut di `~/Library/LaunchAgents/id.beacukaibatam.pengsem.wagateway.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>id.beacukaibatam.pengsem.wagateway</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>/Users/ridmini/Projects/pengsem-kbm/wa_gateway/start_gateway.sh</string>
  </array>
  <key>WorkingDirectory</key>
  <string>/Users/ridmini/Projects/pengsem-kbm/wa_gateway</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/Users/ridmini/Projects/pengsem-kbm/wa_gateway/gateway.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/ridmini/Projects/pengsem-kbm/wa_gateway/gateway.err.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
  </dict>
</dict>
</plist>
```

Aktifkan dengan:
```bash
launchctl load -w ~/Library/LaunchAgents/id.beacukaibatam.pengsem.wagateway.plist
```

---

## 5. Variabel Environment di Dashboard Render Cloud

Tambahkan 2 variabel berikut di **Render Dashboard → `api-kbm-beacukaibatam` → Environment**:

| Key | Value |
|---|---|
| `WA_GATEWAY_URL` | URL HTTPS Cloudflare Tunnel (mis. `https://xxxx.trycloudflare.com` atau subdomain permanen, tanpa garis miring di akhir) |
| `WA_GATEWAY_SECRET` | Secret acak yang **sama persis** dengan `WA_GATEWAY_SECRET` di `wa_gateway/.env` Mac Mini |
