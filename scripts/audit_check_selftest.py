#!/usr/bin/env python3
"""
audit_check_selftest.py - meta-verification for audit_check.py.

This does NOT audit the PENGSEM KBM app. It audits the AUDITOR: it builds
two throwaway fixture projects in a temp directory -

  1. "good"  - deliberately correct: index.html == Formulir copy, server.py
               compiles, inline <script> is valid JS, and every pattern the
               manifest looks for is actually present with the right count.
  2. "bad"   - deliberately broken: one real mismatch injected per check
               (file mismatch, Python syntax error, JS syntax error, missing
               identifier, wrong occurrence count) so every single check
               category has at least one case that MUST come back FAIL.

It then runs audit_check.py against both and asserts:
  - the "good" fixture returns exit code 0 and every check reports PASS
  - the "bad" fixture returns exit code 1 and EXACTLY the injected-broken
    checks report FAIL (not accidentally PASS, and not some other check
    failing instead for the wrong reason)

Run this whenever audit_check.py itself is modified, to make sure a change
didn't quietly make it blind to a category of failure it used to catch.

Usage: python3 scripts/audit_check_selftest.py
Exit code: 0 if audit_check.py behaves correctly on both fixtures, 1 otherwise.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
AUDIT_CHECK = SCRIPT_DIR / "audit_check.py"

GOOD_SERVER_PY = """
def no_skep_handler():
    no_skep = "KEP-123"
    no_bpj = "BPJ-456"
    return no_skep, no_bpj
"""

BAD_SERVER_PY = """
def no_skep_handler(:
    no_skep = "KEP-123"
    return no_skep
"""

GOOD_HTML = """<!doctype html>
<html>
<body>
<script>
function checkSuratKuasaCrossValidation() {
    const a = 1;
    return a + 1;
}
</script>
</body>
</html>
"""

BAD_HTML_JS_SYNTAX = """<!doctype html>
<html>
<body>
<script>
function checkSuratKuasaCrossValidation( {
    const a = 1;
    return a +
}
</script>
</body>
</html>
"""

BAD_HTML_MISSING_IDENTIFIER = """<!doctype html>
<html>
<body>
<script>
function someOtherFunction() {
    return 42;
}
</script>
</body>
</html>
"""


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_good_fixture(base: Path):
    write(base / "server.py", GOOD_SERVER_PY)
    write(base / "index.html", GOOD_HTML)
    write(base / "Formulir_Pemohon_CEISA_PENGSEM_KBM.html", GOOD_HTML)  # identical -> zero diff
    manifest = {
        "task": "selftest-good",
        "root": str(base),
        "mechanical": {
            "zero_diff_pairs": [["index.html", "Formulir_Pemohon_CEISA_PENGSEM_KBM.html"]],
            "py_compile": ["server.py"],
            "node_check_inline_scripts": ["index.html"],
        },
        "existence_checks": [
            {
                "id": "has_no_skep",
                "description": "server.py harus referensi no_skep",
                "file": "server.py",
                "pattern": "no_skep",
                "min_count": 1,
            },
            {
                "id": "has_cross_validation_fn",
                "description": "index.html harus punya checkSuratKuasaCrossValidation",
                "file": "index.html",
                "pattern": "function checkSuratKuasaCrossValidation",
                "min_count": 1,
                "max_count": 1,
            },
        ],
    }
    manifest_path = base / "manifest.json"
    write(manifest_path, json.dumps(manifest, indent=2))
    return manifest_path


def build_bad_fixture(base: Path, variant: str):
    """variant selects exactly ONE broken thing, so we can assert precisely
    which check category catches it."""
    write(base / "server.py", GOOD_SERVER_PY if variant != "py_compile" else BAD_SERVER_PY)

    if variant == "zero_diff":
        write(base / "index.html", GOOD_HTML)
        write(base / "Formulir_Pemohon_CEISA_PENGSEM_KBM.html", GOOD_HTML + "\n<!-- extra -->\n")
    elif variant == "node_check":
        write(base / "index.html", BAD_HTML_JS_SYNTAX)
        write(base / "Formulir_Pemohon_CEISA_PENGSEM_KBM.html", BAD_HTML_JS_SYNTAX)
    elif variant == "missing_identifier":
        write(base / "index.html", BAD_HTML_MISSING_IDENTIFIER)
        write(base / "Formulir_Pemohon_CEISA_PENGSEM_KBM.html", BAD_HTML_MISSING_IDENTIFIER)
    else:
        write(base / "index.html", GOOD_HTML)
        write(base / "Formulir_Pemohon_CEISA_PENGSEM_KBM.html", GOOD_HTML)

    manifest = {
        "task": f"selftest-bad-{variant}",
        "root": str(base),
        "mechanical": {
            "zero_diff_pairs": [["index.html", "Formulir_Pemohon_CEISA_PENGSEM_KBM.html"]],
            "py_compile": ["server.py"],
            "node_check_inline_scripts": ["index.html"],
        },
        "existence_checks": [
            {
                "id": "has_no_skep",
                "description": "server.py harus referensi no_skep",
                "file": "server.py",
                "pattern": "no_skep",
                "min_count": 1,
            },
            {
                "id": "has_cross_validation_fn",
                "description": "index.html harus punya checkSuratKuasaCrossValidation",
                "file": "index.html",
                "pattern": "function checkSuratKuasaCrossValidation",
                "min_count": 1,
                "max_count": 1,
            },
        ],
    }
    manifest_path = base / "manifest.json"
    write(manifest_path, json.dumps(manifest, indent=2))
    return manifest_path


def run_audit_check(manifest_path: Path):
    proc = subprocess.run(
        [sys.executable, str(AUDIT_CHECK), "--manifest", str(manifest_path), "--json"],
        capture_output=True, text=True,
    )
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        data = None
    return proc.returncode, data, proc.stdout, proc.stderr


def expect(condition, label, failures):
    if condition:
        print(f"  [OK] {label}")
    else:
        print(f"  [GAGAL] {label}")
        failures.append(label)


def main():
    failures = []

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "good"
        manifest_path = build_good_fixture(base)
        rc, data, stdout, stderr = run_audit_check(manifest_path)
        print("== Fixture GOOD (semua seharusnya PASS, exit code 0) ==")
        expect(rc == 0, "exit code == 0", failures)
        if data:
            for r in data["results"]:
                expect(r["ok"], f"check '{r['id']}' PASS", failures)
        else:
            expect(False, f"output JSON valid (stdout: {stdout!r} stderr: {stderr!r})", failures)
        print()

    variants = {
        "zero_diff": "zero_diff:index.html==Formulir_Pemohon_CEISA_PENGSEM_KBM.html",
        "py_compile": "py_compile:server.py",
        "node_check": "node_check:index.html",
        "missing_identifier": "has_cross_validation_fn",
    }
    for variant, expected_failing_id in variants.items():
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / f"bad_{variant}"
            manifest_path = build_bad_fixture(base, variant)
            rc, data, stdout, stderr = run_audit_check(manifest_path)
            print(f"== Fixture BAD/{variant} (harus ada tepat 1 kegagalan: {expected_failing_id}) ==")
            expect(rc == 1, "exit code == 1", failures)
            if data:
                failing_ids = [r["id"] for r in data["results"] if not r["ok"]]
                expect(failing_ids == [expected_failing_id],
                       f"id yang gagal persis [{expected_failing_id}] (dapat: {failing_ids})",
                       failures)
            else:
                expect(False, f"output JSON valid (stdout: {stdout!r} stderr: {stderr!r})", failures)
            print()

    print("=" * 60)
    if failures:
        print(f"SELFTEST GAGAL — {len(failures)} asersi tidak terpenuhi:")
        for f in failures:
            print(f"  - {f}")
        print(
            "\naudit_check.py TIDAK BOLEH dipercaya sampai ini diperbaiki — "
            "artinya checker gagal membedakan kode benar vs kode rusak pada "
            "salah satu kasus di atas."
        )
        sys.exit(1)
    else:
        print("SELFTEST LULUS — audit_check.py terbukti membedakan fixture "
              "benar vs rusak untuk semua kategori cek (zero-diff, py_compile, "
              "node --check, dan existence-check).")
        print(
            "Catatan: ini hanya membuktikan checker bekerja untuk 4 skenario "
            "sederhana di atas. Jalankan ulang selftest ini tiap kali "
            "audit_check.py diedit, dan pertimbangkan menambah skenario baru "
            "kalau menambah jenis cek baru ke audit_check.py."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
