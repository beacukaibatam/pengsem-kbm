#!/usr/bin/env python3
"""
audit_check.py - Manifest-driven mechanical + existence audit checker
for the PENGSEM KBM Batam project.

Purpose: automate the *mechanical* part of auditing Antigravity's or
Cline's work (zero-diff between the two HTML mirrors, Python syntax,
JS syntax, and "does this specific identifier/pattern actually exist in
the file" checks), so Claude (or Antigravity/Cline themselves, as a
required step before claiming a task done) doesn't have to run the same
grep/diff/py_compile commands by hand every time.

IMPORTANT - what this script does NOT verify (by design, read before trusting it):
  - Whether the LOGIC behind a matched identifier is actually correct.
    An existence check only proves a string is present somewhere in the
    file; it does not prove the function does what it claims.
  - Any regression / side-effect that was not explicitly listed in the
    manifest (e.g. a sequential lock chain quietly gating an unrelated
    optional field). Those require a human/LLM reading the surrounding
    logic - this script cannot discover a check nobody thought to write.
  - It never prints an unqualified "AUDIT PASSED". It always prints an
    explicit reminder of what still needs manual review.

Usage:
    python3 scripts/audit_check.py --manifest scripts/manifests/<task>.json
    python3 scripts/audit_check.py --manifest scripts/manifests/<task>.json --json

Manifest schema (JSON):
{
  "task": "free-text label for this audit run",
  "root": ".",                         // optional, defaults to repo root (CWD)
  "mechanical": {
    "zero_diff_pairs": [["index.html", "Formulir_Pemohon_CEISA_PENGSEM_KBM.html"]],
    "py_compile": ["server.py", "database.py"],
    "node_check_inline_scripts": ["index.html"]   // extracts bare <script>...</script>
                                                    // blocks (no src=, no type=) and
                                                    // runs `node --check` on each
  },
  "existence_checks": [
    {
      "id": "short_unique_id",
      "description": "Human-readable description of what this proves",
      "file": "server.py",
      "pattern": "no_skep",            // plain substring OR /regex/ if wrapped in slashes
      "min_count": 1,                  // default 1
      "max_count": null                // optional upper bound
    }
  ]
}

Exit code: 0 if every mechanical + existence check passes, 1 otherwise.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
import os
from pathlib import Path


class Result:
    def __init__(self, kind, id_, description, ok, detail, evidence=None):
        self.kind = kind
        self.id = id_
        self.description = description
        self.ok = ok
        self.detail = detail
        self.evidence = evidence or []

    def to_dict(self):
        return {
            "kind": self.kind,
            "id": self.id,
            "description": self.description,
            "ok": self.ok,
            "detail": self.detail,
            "evidence": self.evidence,
        }


def run_zero_diff(root: Path, pair):
    file_a, file_b = pair
    path_a, path_b = root / file_a, root / file_b
    id_ = f"zero_diff:{file_a}=={file_b}"
    if not path_a.exists() or not path_b.exists():
        missing = [str(p) for p in (path_a, path_b) if not p.exists()]
        return Result("mechanical", id_, f"{file_a} dan {file_b} harus identik (diff -u = 0)",
                      False, f"File tidak ditemukan: {', '.join(missing)}")
    proc = subprocess.run(["diff", "-u", str(path_a), str(path_b)],
                           capture_output=True, text=True)
    if proc.returncode == 0:
        return Result("mechanical", id_, f"{file_a} dan {file_b} harus identik (diff -u = 0)",
                      True, "diff -u = 0 (identik)")
    diff_lines = proc.stdout.strip().splitlines()
    preview = "\n".join(diff_lines[:20])
    return Result("mechanical", id_, f"{file_a} dan {file_b} harus identik (diff -u = 0)",
                  False, f"Ada perbedaan ({len(diff_lines)} baris diff). Cuplikan:\n{preview}")


def run_py_compile(root: Path, filename):
    path = root / filename
    id_ = f"py_compile:{filename}"
    if not path.exists():
        return Result("mechanical", id_, f"{filename} harus lolos py_compile", False,
                      f"File tidak ditemukan: {path}")
    proc = subprocess.run([sys.executable, "-m", "py_compile", str(path)],
                          capture_output=True, text=True)
    if proc.returncode == 0:
        return Result("mechanical", id_, f"{filename} harus lolos py_compile", True, "py_compile OK")
    return Result("mechanical", id_, f"{filename} harus lolos py_compile", False,
                  f"py_compile gagal:\n{proc.stderr.strip()}")


def extract_bare_script_blocks(html_text: str):
    """Return list of (start_line, js_source) for <script> tags with no src= and no type= attr."""
    blocks = []
    for m in re.finditer(r"<script(?![^>]*\bsrc=)(?![^>]*\btype=)[^>]*>(.*?)</script>",
                          html_text, re.IGNORECASE | re.DOTALL):
        start_line = html_text.count("\n", 0, m.start()) + 1
        blocks.append((start_line, m.group(1)))
    return blocks


def run_node_check_inline(root: Path, filename):
    path = root / filename
    id_ = f"node_check:{filename}"
    if not path.exists():
        return Result("mechanical", id_, f"Blok <script> inline di {filename} harus lolos node --check",
                      False, f"File tidak ditemukan: {path}")
    if subprocess.run(["node", "--version"], capture_output=True).returncode != 0:
        return Result("mechanical", id_, f"Blok <script> inline di {filename} harus lolos node --check",
                      False, "node tidak ditemukan di PATH - lewati atau install Node.js")
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = extract_bare_script_blocks(text)
    if not blocks:
        return Result("mechanical", id_, f"Blok <script> inline di {filename} harus lolos node --check",
                      False, "Tidak ada blok <script> inline (tanpa src=/type=) ditemukan")
    failures = []
    for start_line, js in blocks:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False, encoding="utf-8") as tf:
            tf.write(js)
            tmp_path = tf.name
        try:
            proc = subprocess.run(["node", "--check", tmp_path], capture_output=True, text=True)
            if proc.returncode != 0:
                failures.append(f"Blok mulai baris {start_line}: {proc.stderr.strip()}")
        finally:
            os.unlink(tmp_path)
    if failures:
        return Result("mechanical", id_, f"Blok <script> inline di {filename} harus lolos node --check",
                      False, "\n".join(failures))
    return Result("mechanical", id_, f"Blok <script> inline di {filename} harus lolos node --check",
                  True, f"{len(blocks)} blok <script> inline, semua lolos node --check")


def run_existence_check(root: Path, check: dict):
    id_ = check["id"]
    description = check.get("description", "")
    filename = check["file"]
    pattern = check["pattern"]
    min_count = check.get("min_count", 1)
    max_count = check.get("max_count")
    path = root / filename

    if not path.exists():
        return Result("existence", id_, description, False, f"File tidak ditemukan: {path}")

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    if pattern.startswith("/") and pattern.endswith("/") and len(pattern) > 1:
        regex = re.compile(pattern[1:-1])
        matcher = lambda line: regex.search(line) is not None
    else:
        matcher = lambda line: pattern in line

    hits = [(i + 1, line.strip()) for i, line in enumerate(lines) if matcher(line)]
    count = len(hits)

    ok = count >= min_count and (max_count is None or count <= max_count)
    evidence = [f"{filename}:{ln}: {content[:160]}" for ln, content in hits[:8]]
    extra_note = "" if count <= 8 else f"\n... ({count - 8} kecocokan lainnya tidak ditampilkan)"

    bound_desc = f"min={min_count}" + (f", max={max_count}" if max_count is not None else "")
    detail = f"Ditemukan {count}x (syarat: {bound_desc})." + extra_note
    return Result("existence", id_, description, ok, detail, evidence)


def load_manifest(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", required=True, help="Path ke file manifest JSON")
    ap.add_argument("--json", action="store_true", help="Output sebagai JSON, bukan teks")
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"ERROR: manifest tidak ditemukan: {manifest_path}", file=sys.stderr)
        sys.exit(2)

    manifest = load_manifest(manifest_path)
    root = Path(manifest.get("root", ".")).resolve()

    results = []
    mech = manifest.get("mechanical", {})
    for pair in mech.get("zero_diff_pairs", []):
        results.append(run_zero_diff(root, pair))
    for fname in mech.get("py_compile", []):
        results.append(run_py_compile(root, fname))
    for fname in mech.get("node_check_inline_scripts", []):
        results.append(run_node_check_inline(root, fname))
    for check in manifest.get("existence_checks", []):
        results.append(run_existence_check(root, check))

    if args.json:
        print(json.dumps({
            "task": manifest.get("task", ""),
            "results": [r.to_dict() for r in results],
            "all_passed": all(r.ok for r in results),
        }, indent=2, ensure_ascii=False))
    else:
        print(f"=== audit_check.py — {manifest.get('task', '(tanpa nama tugas)')} ===")
        print(f"Manifest: {manifest_path}")
        print(f"Root: {root}\n")
        for r in results:
            status = "PASS" if r.ok else "FAIL"
            print(f"[{status}] ({r.kind}) {r.id}")
            print(f"    {r.description}")
            for line in r.detail.splitlines():
                print(f"    {line}")
            for ev in r.evidence:
                print(f"      > {ev}")
            print()
        passed = sum(1 for r in results if r.ok)
        total = len(results)
        print(f"Ringkasan: {passed}/{total} cek lolos.")
        print(
            "\nPENTING: cek ini hanya memverifikasi hal MEKANIS (diff/syntax) dan "
            "KEBERADAAN pola/identifier yang disebutkan di manifest. Ini TIDAK "
            "membuktikan logikanya benar, dan TIDAK bisa menemukan regresi/efek "
            "samping yang tidak ditulis di manifest ini. Review manual atas logika "
            "dan potensi regresi tetap wajib dilakukan sebelum menganggap tugas "
            "benar-benar selesai."
        )

    sys.exit(0 if all(r.ok for r in results) else 1)


if __name__ == "__main__":
    main()
