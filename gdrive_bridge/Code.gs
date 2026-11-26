/**
 * Google Apps Script Web App Bridge — Arsip Otomatis PENGSEM KBM Bea Cukai Batam
 * Akun target: ridwanmuham17@gmail.com (Google Drive)
 *
 * Cara Deploy (1 menit):
 * 1. Buka https://script.google.com menggunakan akun ridwanmuham17@gmail.com
 * 2. Klik "New project" -> beri nama "KBM Batam Drive Bridge"
 * 3. Hapus isi default, tempel seluruh kode ini.
 * 4. Ganti nilai BRIDGE_SECRET di bawah (atau simpan di Project Settings -> Script Properties -> BRIDGE_SECRET).
 * 5. Klik "Deploy" -> "New deployment" -> Type: "Web app":
 *    - Execute as: "Me (ridwanmuham17@gmail.com)"
 *    - Who has access: "Anyone" (keamanan dijaga oleh BRIDGE_SECRET di dalam payload)
 * 6. Salin Web App URL (https://script.google.com/macros/s/.../exec)
 * 7. Pasang di Render Cloud Environment Variables & .env lokal:
 *    - GDRIVE_BRIDGE_URL=<Web App URL>
 *    - GDRIVE_BRIDGE_SECRET=<nilai secret yang sama>
 */

var DEFAULT_ROOT_FOLDER = 'ARSIP_PENGSEM_KBM_BATAM';

function getBridgeSecret_() {
  var props = PropertiesService.getScriptProperties();
  var fromProp = props.getProperty('BRIDGE_SECRET');
  if (fromProp && fromProp.trim()) return fromProp.trim();
  return 'GANTI_DENGAN_SECRET_ACAK_MINIMAL_24_KARAKTER';
}

function getOrCreateFolder_(parent, name) {
  var safeName = String(name || 'LAINNYA').replace(/[\/\\:*?"<>|]/g, '_').trim();
  if (!safeName) safeName = 'LAINNYA';
  var it = parent.getFoldersByName(safeName);
  if (it.hasNext()) return it.next();
  return parent.createFolder(safeName);
}

function jsonResponse_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function doGet(e) {
  return jsonResponse_({
    status: 'ok',
    service: 'KBM Batam Google Drive Archive Bridge',
    note: 'Use POST with valid secret to upload documents.'
  });
}

function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return jsonResponse_({ status: 'error', message: 'Empty POST body' });
    }

    var body = JSON.parse(e.postData.contents);
    var expectedSecret = getBridgeSecret_();
    if (!body.secret || body.secret !== expectedSecret) {
      return jsonResponse_({ status: 'error', message: 'Unauthorized: invalid secret' });
    }

    var action = body.action || 'upload_file';
    if (action === 'ping') {
      var rootPing = getOrCreateFolder_(DriveApp.getRootFolder(), body.root_folder || DEFAULT_ROOT_FOLDER);
      return jsonResponse_({
        status: 'ok',
        message: 'Bridge terhubung ke Google Drive!',
        root_folder_name: rootPing.getName(),
        root_folder_url: rootPing.getUrl()
      });
    }

    if (action === 'upload_file') {
      var filename = String(body.filename || 'dokumen.bin').replace(/[\/\\:*?"<>|]/g, '_').trim();
      var mimeType = String(body.mime_type || 'application/octet-stream');
      var b64 = String(body.base64_data || '');
      if (!b64) {
        return jsonResponse_({ status: 'error', message: 'base64_data is required' });
      }
      // Bersihkan prefix data URL bila ikut terkirim
      var commaIdx = b64.indexOf(',');
      if (commaIdx !== -1 && b64.slice(0, commaIdx).indexOf('base64') !== -1) {
        b64 = b64.slice(commaIdx + 1);
      }

      var rootName = body.root_folder || DEFAULT_ROOT_FOLDER;
      var rootFolder = getOrCreateFolder_(DriveApp.getRootFolder(), rootName);
      var targetFolder = body.subfolder ? getOrCreateFolder_(rootFolder, body.subfolder) : rootFolder;

      // Hindari duplikat dengan nama file sama di subfolder yang sama
      var existing = targetFolder.getFilesByName(filename);
      while (existing.hasNext()) {
        existing.next().setTrashed(true);
      }

      var bytes = Utilities.base64Decode(b64);
      var blob = Utilities.newBlob(bytes, mimeType, filename);
      var created = targetFolder.createFile(blob);

      return jsonResponse_({
        status: 'ok',
        file_id: created.getId(),
        file_name: created.getName(),
        file_url: created.getUrl(),
        folder_url: targetFolder.getUrl(),
        folder_name: targetFolder.getName()
      });
    }

    return jsonResponse_({ status: 'error', message: 'Unknown action: ' + action });
  } catch (err) {
    return jsonResponse_({ status: 'error', message: String(err) });
  }
}
