# CLAUDE.md: Developer Instructions & Operational Guidelines

Welcome, Claude! This repository hosts the production system for **PENGSEM KBM Batam** (Temporary Motor Vehicle Exit Management Portal - KPU Bea dan Cukai Tipe B Batam).

## ⚠️ MANDATORY COLLABORATION PROTOCOL
1. **Always read `AGENTS_SYNC.md` first** at the start of any conversation/session to understand the current architecture, environment variables, active features, and the latest changes made by Antigravity or previous sessions.
2. **Always update `AGENTS_SYNC.md`** before completing any task. Add an entry to the log table:
   `| YYYY-MM-DD HH:MM | Claude | <modified_files> | <summary_of_changes> | <status> |`
   and update the checklist in section 6.
3. **Always keep `index.html` and `Formulir_Pemohon_CEISA_PENGSEM_KBM.html` 100% synchronized** (`diff -u` must always be 0).

---

## 🚀 Quick Command Reference

```bash
# Start local backend server (daemon or foreground)
python3 server.py

# Check backend health
curl http://localhost:8080/api/health

# Verify zero diff between primary HTML files
diff -u index.html Formulir_Pemohon_CEISA_PENGSEM_KBM.html

# Run automated tests using Playwright
python3 scratch/test_full_rbac.py
```

---

## 🏛️ Architecture & RBAC Highlights
- **Frontend**: Single Page Application (SPA) hosted on GitHub Pages (`https://beacukaibatam.github.io/pengsem-kbm/`) with hash-routing (`#/masuk`, `#/formulir`, `#/dashboard`).
- **Backend**: Python 3.9+ HTTP Server with ThreadPoolExecutor, anti-OOM image processing, and CORS headers.
- **Database**: SQLite 3 with WAL mode enabled (`kbm_batam.db`) for high-concurrency read/write operations.
- **RBAC Roles**: `adminutama`, `frontdesk`, `loket`, `jaminan`, `fasilitas`, `pemeriksabarang`, `pemeriksadokumen`, `gate`, and `pemohon`. (See `AGENTS_SYNC.md` for passwords & specific stages).
- **Communication Gateway**: WhatsApp Meta Cloud API with graceful fallback to SMTP TLS Email upon rate limit (HTTP 429) or network failure.
