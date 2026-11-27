'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const express = require('express');
const pino = require('pino');
const qrcodeTerminal = require('qrcode-terminal');
const QRCode = require('qrcode');
const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
  Browsers,
} = require('@whiskeysockets/baileys');

// Muat .env lokal (wa_gateway/.env) tanpa menimpa env yang sudah ada di shell
function loadLocalEnv() {
  const envPath = path.join(__dirname, '.env');
  if (!fs.existsSync(envPath)) return;
  try {
    const lines = fs.readFileSync(envPath, 'utf8').split(/\r?\n/);
    for (const raw of lines) {
      const line = raw.trim();
      if (!line || line.startsWith('#') || !line.includes('=')) continue;
      const idx = line.indexOf('=');
      const k = line.slice(0, idx).trim();
      let v = line.slice(idx + 1).trim();
      if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
        v = v.slice(1, -1);
      }
      if (k && process.env[k] === undefined) {
        process.env[k] = v;
      }
    }
  } catch (err) {
    console.error('[!] Gagal membaca wa_gateway/.env:', err.message);
  }
}
loadLocalEnv();

const PORT = parseInt(process.env.PORT || '3001', 10);
const BIND_HOST = process.env.BIND_HOST || '127.0.0.1';
const WA_GATEWAY_SECRET = (process.env.WA_GATEWAY_SECRET || '').trim();
const BACKEND_WEBHOOK_URL = (
  process.env.BACKEND_WEBHOOK_URL || 'https://api-kbm-beacukaibatam.onrender.com/api/webhook/baileys'
).trim();
const MIN_SEND_DELAY_MS = Math.max(500, parseInt(process.env.MIN_SEND_DELAY_MS || '1200', 10));
const AUTH_DIR = path.join(__dirname, 'auth_info');

if (!WA_GATEWAY_SECRET) {
  console.warn('[!] PERINGATAN: WA_GATEWAY_SECRET belum disetel! Endpoint POST /send akan menolak semua permintaan (403) demi keamanan.');
}

// ================= STATE KONEKSI WHATSAPP =================
let sock = null;
let connectionStatus = 'disconnected'; // 'connected' | 'awaiting_qr' | 'disconnected'
let activePhone = '';
let activeName = '';
let connectedSince = null;
let latestQrString = null;
let reconnectAttempt = 0;
let reconnectTimer = null;

// ================= UTILITAS KEAMANAN & NORMALISASI =================
function safeSecretEquals(provided, expected) {
  if (!expected || !provided) return false;
  const a = Buffer.from(String(provided));
  const b = Buffer.from(String(expected));
  if (a.length !== b.length) return false;
  return crypto.timingSafeEqual(a, b);
}

function isLocalhostRequest(req) {
  const ip = (req.socket && req.socket.remoteAddress) || '';
  const forwarded = req.headers['x-forwarded-for'] || req.headers['cf-connecting-ip'];
  if (forwarded) return false;
  return ip === '127.0.0.1' || ip === '::1' || ip === '::ffff:127.0.0.1';
}

function normalizePhoneDigits(raw) {
  const digits = String(raw || '').replace(/[^0-9]/g, '');
  if (!digits) return '';
  if (digits.startsWith('08')) return '628' + digits.slice(2);
  if (digits.startsWith('8')) return '628' + digits.slice(1);
  if (digits.startsWith('62')) return digits;
  return '62' + digits.replace(/^0+/, '');
}

function toWhatsAppJid(raw) {
  const digits = normalizePhoneDigits(raw);
  if (!digits || digits.length < 10) return null;
  return { digits, jid: `${digits}@s.whatsapp.net` };
}

function extractMessageText(msg) {
  if (!msg || !msg.message) return '';
  const m = msg.message;
  if (m.conversation) return m.conversation;
  if (m.extendedTextMessage && m.extendedTextMessage.text) return m.extendedTextMessage.text;
  if (m.imageMessage && m.imageMessage.caption) return `[Foto] ${m.imageMessage.caption}`;
  if (m.videoMessage && m.videoMessage.caption) return `[Video] ${m.videoMessage.caption}`;
  if (m.documentMessage && m.documentMessage.caption) return `[Dokumen] ${m.documentMessage.caption}`;
  if (m.buttonsResponseMessage && m.buttonsResponseMessage.selectedDisplayText) {
    return m.buttonsResponseMessage.selectedDisplayText;
  }
  if (m.listResponseMessage && m.listResponseMessage.title) {
    return m.listResponseMessage.title;
  }
  if (m.imageMessage) return '[Foto dikirim pemohon]';
  if (m.documentMessage) return `[Dokumen: ${m.documentMessage.fileName || 'file'}]`;
  return '';
}

// ================= ANTREAN KIRIM ANTI-SPAM (MIN 1.2 DETIK) =================
let sendQueueTail = Promise.resolve();
let lastSentAt = 0;
let queueLength = 0;

function enqueueSend(jid, text) {
  queueLength += 1;
  const job = sendQueueTail.then(async () => {
    try {
      if (!sock || connectionStatus !== 'connected') {
        const err = new Error(`WhatsApp Gateway belum terhubung (status: ${connectionStatus}).`);
        err.statusCode = 502;
        throw err;
      }
      const elapsed = Date.now() - lastSentAt;
      if (elapsed < MIN_SEND_DELAY_MS) {
        await new Promise((r) => setTimeout(r, MIN_SEND_DELAY_MS - elapsed));
      }
      const sent = await sock.sendMessage(jid, { text: String(text) });
      lastSentAt = Date.now();
      return sent;
    } finally {
      queueLength = Math.max(0, queueLength - 1);
    }
  });
  sendQueueTail = job.catch(() => {});
  return job;
}

// ================= BRIDGE PESAN MASUK KE BACKEND RENDER =================
async function forwardIncomingToBackend(payload) {
  if (!BACKEND_WEBHOOK_URL || !WA_GATEWAY_SECRET) return;
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 12000);
    const res = await fetch(BACKEND_WEBHOOK_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-WA-Gateway-Secret': WA_GATEWAY_SECRET,
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    clearTimeout(timer);
    if (!res.ok) {
      const bodyTxt = await res.text().catch(() => '');
      console.error(`[!] Webhook backend gagal HTTP ${res.status}: ${bodyTxt.slice(0, 200)}`);
    } else {
      console.log(`[<-] Pesan masuk dari +${payload.from} diteruskan ke Live Chat backend.`);
    }
  } catch (err) {
    console.error('[!] Gagal meneruskan pesan masuk ke backend:', err.message);
  }
}

// ================= INISIALISASI BAILEYS + AUTO-RECONNECT =================
async function startWhatsAppSocket() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }
  fs.mkdirSync(AUTH_DIR, { recursive: true });
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);

  let version;
  try {
    const latest = await fetchLatestBaileysVersion();
    version = latest.version;
  } catch (_) {
    version = undefined;
  }

  const logger = pino({ level: process.env.WA_LOG_LEVEL || 'silent' });
  sock = makeWASocket({
    ...(version ? { version } : {}),
    auth: state,
    logger,
    browser: Browsers.macOS('PENGSEM KBM Batam'),
    printQRInTerminal: false,
    syncFullHistory: false,
    markOnlineOnConnect: false,
    connectTimeoutMs: 30000,
    defaultQueryTimeoutMs: 30000,
  });

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      latestQrString = qr;
      connectionStatus = 'awaiting_qr';
      activePhone = '';
      connectedSince = null;
      console.log('\n==============================================================');
      console.log(' SCAN QR CODE INI DARI WHATSAPP HP -> PERANGKAT TERTAUT');
      console.log(` Atau buka di browser Mac Mini: http://127.0.0.1:${PORT}/qr`);
      console.log('==============================================================');
      qrcodeTerminal.generate(qr, { small: true });
    }

    if (connection === 'open') {
      connectionStatus = 'connected';
      latestQrString = null;
      reconnectAttempt = 0;
      connectedSince = new Date().toISOString();
      const rawId = (sock.user && sock.user.id) || '';
      activePhone = rawId.split(':')[0].split('@')[0];
      activeName = (sock.user && sock.user.name) || '';
      console.log(`[+] WhatsApp Gateway TERHUBUNG! Nomor aktif: +${activePhone} (${activeName || 'WA'})`);
    }

    if (connection === 'close') {
      const statusCode =
        lastDisconnect &&
        lastDisconnect.error &&
        lastDisconnect.error.output &&
        lastDisconnect.error.output.statusCode;
      const shouldReconnect = statusCode !== DisconnectReason.loggedOut;

      connectionStatus = 'disconnected';
      activePhone = '';
      connectedSince = null;

      console.warn(`[!] Koneksi WhatsApp terputus (code=${statusCode}). Reconnect=${shouldReconnect}`);
      if (shouldReconnect) {
        reconnectAttempt += 1;
        const delayMs = Math.min(30000, 3000 * reconnectAttempt);
        console.log(`[*] Mencoba reconnect otomatis dalam ${Math.round(delayMs / 1000)} detik...`);
        reconnectTimer = setTimeout(() => {
          startWhatsAppSocket().catch((err) => console.error('[!] Error reconnect Baileys:', err.message));
        }, delayMs);
      } else {
        console.error('[!] Sesi WhatsApp keluar (Logged Out). Hapus folder wa_gateway/auth_info lalu restart untuk scan QR ulang.');
      }
    }
  });

  sock.ev.on('messages.upsert', async ({ messages, type }) => {
    if (type !== 'notify' || !Array.isArray(messages)) return;
    for (const msg of messages) {
      try {
        if (!msg || !msg.key || msg.key.fromMe) continue;
        const remoteJid = msg.key.remoteJid || '';
        if (!remoteJid || remoteJid === 'status@broadcast' || remoteJid.endsWith('@g.us')) continue;

        const text = extractMessageText(msg).trim();
        if (!text) continue;

        const senderSource =
          (msg.key.remoteJidAlt && msg.key.remoteJidAlt.includes('@s.whatsapp.net') ? msg.key.remoteJidAlt : '') ||
          (msg.key.participant && msg.key.participant.includes('@s.whatsapp.net') ? msg.key.participant : '') ||
          remoteJid;
        const fromDigits = normalizePhoneDigits(senderSource.split(':')[0].split('@')[0]);
        if (!fromDigits) continue;

        const pushName = (msg.pushName || '').trim();
        const tsSec = Number(msg.messageTimestamp || Math.floor(Date.now() / 1000));

        // Teruskan secara asinkron tanpa memblokir event loop Baileys
        forwardIncomingToBackend({
          from: fromDigits,
          text,
          push_name: pushName,
          message_id: msg.key.id || '',
          timestamp: tsSec,
        });
      } catch (err) {
        console.error('[!] Error memproses pesan masuk:', err.message);
      }
    }
  });
}

// ================= HTTP API SERVER (EXPRESS) =================
const app = express();
app.disable('x-powered-by');
app.use(express.json({ limit: '256kb' }));

app.get('/health', (req, res) => {
  res.json({
    status: connectionStatus,
    phone: activePhone || null,
    name: activeName || null,
    connected_since: connectedSince,
    queue_length: queueLength,
  });
});

// Endpoint QR lokal: hanya dapat dibuka dari localhost (127.0.0.1) atau dengan header secret
app.get('/qr', async (req, res) => {
  const providedSecret = req.headers['x-wa-gateway-secret'] || '';
  if (!isLocalhostRequest(req) && !safeSecretEquals(providedSecret, WA_GATEWAY_SECRET)) {
    return res.status(403).json({ status: 'error', message: 'Akses /qr hanya diizinkan dari localhost Mac Mini.' });
  }

  if (connectionStatus === 'connected') {
    return res.send(
      `<!doctype html><html lang="id"><head><meta charset="utf-8"><title>WA Gateway Connected</title></head>` +
      `<body style="font-family:system-ui,sans-serif;text-align:center;padding:48px;background:#f8fafc;color:#0f172a;">` +
      `<h2 style="color:#059669;">WhatsApp Gateway Terhubung</h2>` +
      `<p>Nomor aktif: <strong>+${activePhone}</strong> (${activeName || 'WhatsApp'})</p>` +
      `<p style="color:#64748b;font-size:14px;">Sejak: ${connectedSince}</p></body></html>`
    );
  }

  if (!latestQrString) {
    return res.send(
      `<!doctype html><html lang="id"><head><meta charset="utf-8"><meta http-equiv="refresh" content="3"><title>Menunggu QR...</title></head>` +
      `<body style="font-family:system-ui,sans-serif;text-align:center;padding:48px;background:#f8fafc;color:#0f172a;">` +
      `<h2>Menyiapkan QR Code WhatsApp...</h2><p>Status: ${connectionStatus}. Halaman otomatis memuat ulang setiap 3 detik.</p></body></html>`
    );
  }

  try {
    const dataUrl = await QRCode.toDataURL(latestQrString, { width: 320, margin: 2 });
    return res.send(
      `<!doctype html><html lang="id"><head><meta charset="utf-8"><meta http-equiv="refresh" content="10"><title>Scan QR WA Gateway</title></head>` +
      `<body style="font-family:system-ui,sans-serif;text-align:center;padding:36px;background:#f8fafc;color:#0f172a;">` +
      `<h2>Scan QR Code — PENGSEM KBM WA Gateway</h2>` +
      `<p>Buka WhatsApp di HP &rarr; <strong>Perangkat Tertaut</strong> &rarr; <strong>Tautkan Perangkat</strong></p>` +
      `<img src="${dataUrl}" alt="QR WhatsApp" style="border:8px solid #fff;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.12);" />` +
      `<p style="color:#64748b;font-size:13px;margin-top:16px;">Halaman ini otomatis refresh setiap 10 detik.</p></body></html>`
    );
  } catch (err) {
    return res.status(500).send('Gagal render QR: ' + err.message);
  }
});

app.post('/send', async (req, res) => {
  const providedSecret = req.headers['x-wa-gateway-secret'] || '';
  if (!WA_GATEWAY_SECRET || !safeSecretEquals(providedSecret, WA_GATEWAY_SECRET)) {
    return res.status(403).json({ status: 'error', message: 'Forbidden: X-WA-Gateway-Secret tidak valid.' });
  }

  const { to, text } = req.body || {};
  const target = toWhatsAppJid(to);
  if (!target) {
    return res.status(400).json({ status: 'error', message: 'Nomor tujuan WhatsApp tidak valid.' });
  }
  const cleanText = String(text || '').trim();
  if (!cleanText) {
    return res.status(400).json({ status: 'error', message: 'Isi pesan (text) tidak boleh kosong.' });
  }

  if (!sock || connectionStatus !== 'connected') {
    return res.status(502).json({
      status: 'error',
      message: `WhatsApp Gateway belum terhubung (status: ${connectionStatus}). Silakan scan QR di Mac Mini.`,
    });
  }

  try {
    const sent = await enqueueSend(target.jid, cleanText);
    const msgId = (sent && sent.key && sent.key.id) || '';
    console.log(`[->] Terkirim ke +${target.digits} (id=${msgId})`);
    return res.json({
      status: 'ok',
      message_id: msgId,
      to: target.digits,
    });
  } catch (err) {
    const code = err.statusCode || 502;
    console.error(`[!] Gagal kirim WA ke +${target.digits}:`, err.message);
    return res.status(code).json({
      status: 'error',
      message: err.message || 'Gagal mengirim pesan via Baileys.',
    });
  }
});

app.listen(PORT, BIND_HOST, () => {
  console.log(`[+] PENGSEM KBM WA Gateway aktif di http://${BIND_HOST}:${PORT}`);
  console.log(`[*] Webhook backend: ${BACKEND_WEBHOOK_URL}`);
  console.log(`[*] Jeda antrean kirim: ${MIN_SEND_DELAY_MS} ms`);
  startWhatsAppSocket().catch((err) => {
    console.error('[!] Gagal memulai Baileys socket:', err);
  });
});
