#!/usr/bin/env python3
"""
SolidPaving.id Build Script
============================

Cara pakai:
    python build.py              # Build semua file
    python build.py bekasi       # Build cuma 1 folder (untuk test)
    python build.py --dry-run    # Lihat apa yang akan diupdate, tanpa save
    python build.py --check      # Cek file mana yang punya marker, mana yang belum

Apa yang dilakukan:
1. Baca _includes/navbar.html, mob-drawer.html, footer.html
2. Cari semua index.html di repo (kecuali yang di _includes/)
3. Untuk setiap file: replace bagian di antara <!-- NAVBAR:START --> ... <!-- NAVBAR:END -->
   (sama untuk MOB-DRAWER dan FOOTER)
4. Skip file yang TIDAK punya marker (untuk safety)
5. Print laporan lengkap

Safety:
- File tanpa marker DI-SKIP (tidak dirusak)
- --dry-run untuk lihat dulu sebelum save
- Backup otomatis di .build-backup/ sebelum overwrite
"""

import os
import sys
import shutil
import re
from pathlib import Path
from datetime import datetime

# ─── KONFIGURASI ──────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.resolve()
INCLUDES_DIR = ROOT / "_includes"
BACKUP_DIR = ROOT / ".build-backup"

# Marker untuk replacement
MARKERS = {
    "NAVBAR": ("<!-- NAVBAR:START -->", "<!-- NAVBAR:END -->"),
    "MOB-DRAWER": ("<!-- MOB-DRAWER:START -->", "<!-- MOB-DRAWER:END -->"),
    "FOOTER": ("<!-- FOOTER:START -->", "<!-- FOOTER:END -->"),
}

# Files yang akan disumber-kan
SOURCES = {
    "NAVBAR": INCLUDES_DIR / "navbar.html",
    "MOB-DRAWER": INCLUDES_DIR / "mob-drawer.html",
    "FOOTER": INCLUDES_DIR / "footer.html",
    "FOOTER-CSS": INCLUDES_DIR / "footer.css",
}

# Folder yang DI-SKIP saat scan (tidak mau diupdate)
SKIP_DIRS = {"_includes", ".git", ".build-backup", ".add-markers-backup", "node_modules", ".github"}

# ─── ANSI COLORS untuk output (Windows juga support di Python 3.13+) ──────
class C:
    R = '\033[91m'   # Red (error)
    G = '\033[92m'   # Green (success)
    Y = '\033[93m'   # Yellow (warning)
    B = '\033[94m'   # Blue (info)
    DIM = '\033[2m'  # Dim
    END = '\033[0m'  # Reset


def find_html_files(root, filter_subdir=None):
    """Find all index.html files in repo, kecuali di SKIP_DIRS."""
    files = []
    for path in root.rglob("index.html"):
        # Cek apakah ada parent dir yang di-skip
        rel_parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        # Filter by subdir jika ada
        if filter_subdir:
            if filter_subdir not in rel_parts:
                continue
        files.append(path)
    return sorted(files)


def check_markers(file_path):
    """Cek file punya marker apa saja. Return dict: marker_name -> bool."""
    content = file_path.read_text(encoding="utf-8")
    result = {}
    for name, (start, end) in MARKERS.items():
        has_start = start in content
        has_end = end in content
        if has_start and has_end:
            result[name] = "OK"
        elif has_start or has_end:
            result[name] = "PARTIAL"
        else:
            result[name] = "MISSING"
    return result


def replace_block(content, marker_name, replacement):
    """Replace block between markers. Return (new_content, n_replaced)."""
    start, end = MARKERS[marker_name]
    pattern = re.compile(
        re.escape(start) + r".*?" + re.escape(end),
        re.DOTALL
    )
    new_block = f"{start}\n{replacement.strip()}\n{end}"
    new_content, n = pattern.subn(new_block, content)
    return new_content, n


def backup_file(file_path):
    """Backup file ke .build-backup/ dengan struktur folder yang sama."""
    rel = file_path.relative_to(ROOT)
    backup_path = BACKUP_DIR / rel
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(file_path, backup_path)


def build_file(file_path, sources_content, dry_run=False):
    """Update single file. Return (status, details)."""
    content = file_path.read_text(encoding="utf-8")
    original = content
    replacements = {}

    for marker_name in MARKERS.keys():
        start, end = MARKERS[marker_name]
        if start not in content or end not in content:
            replacements[marker_name] = "SKIP (no marker)"
            continue
        new_content, n = replace_block(content, marker_name, sources_content[marker_name])
        if n > 0:
            content = new_content
            replacements[marker_name] = f"REPLACED"
        else:
            replacements[marker_name] = "ERROR (regex failed)"

    # ─── Inject FOOTER-CSS into <style> block ───
    # Cari marker FOOTER-CSS dulu. Kalau gak ada, append sebelum </style>.
    footer_css = sources_content.get("FOOTER-CSS")
    if footer_css:
        css_block = f"\n/* FOOTER-CSS:START — auto-managed by build.py */\n{footer_css.strip()}\n/* FOOTER-CSS:END */\n"
        css_marker_start = "/* FOOTER-CSS:START"
        css_marker_end = "/* FOOTER-CSS:END */"
        
        if css_marker_start in content and css_marker_end in content:
            # Already has marker — replace between markers
            pattern = re.compile(
                re.escape(css_marker_start) + r".*?" + re.escape(css_marker_end),
                re.DOTALL
            )
            new_block = f"/* FOOTER-CSS:START — auto-managed by build.py */\n{footer_css.strip()}\n/* FOOTER-CSS:END */"
            content, n = pattern.subn(new_block, content)
            if n > 0:
                replacements["FOOTER-CSS"] = "REPLACED"
        else:
            # No marker yet — inject before first </style>
            if "</style>" in content:
                content = content.replace("</style>", css_block + "</style>", 1)
                replacements["FOOTER-CSS"] = "INJECTED"
            else:
                replacements["FOOTER-CSS"] = "SKIP (no <style>)"

    if content == original:
        return "UNCHANGED", replacements

    if not dry_run:
        backup_file(file_path)
        file_path.write_text(content, encoding="utf-8")

    return "UPDATED", replacements


def cmd_check(files):
    """Print marker status untuk semua file."""
    print(f"\n{C.B}━━━ MARKER CHECK ━━━{C.END}")
    print(f"Total files: {len(files)}\n")

    headers = ["FILE", "NAVBAR", "MOB-DRAWER", "FOOTER"]
    print(f"{headers[0]:<50} {headers[1]:<10} {headers[2]:<14} {headers[3]:<10}")
    print("─" * 90)

    counts = {"NAVBAR": 0, "MOB-DRAWER": 0, "FOOTER": 0}
    for f in files:
        rel = f.relative_to(ROOT)
        markers = check_markers(f)
        status_strs = []
        for m in ["NAVBAR", "MOB-DRAWER", "FOOTER"]:
            s = markers[m]
            color = C.G if s == "OK" else (C.Y if s == "PARTIAL" else C.R)
            status_strs.append(f"{color}{s:<10}{C.END}")
            if s == "OK":
                counts[m] += 1
        # Manual column align karena ANSI codes
        print(f"{str(rel):<50} {status_strs[0]:<19} {status_strs[1]:<23} {status_strs[2]:<19}")

    print("─" * 90)
    print(f"\n{C.B}Summary:{C.END}")
    for m, n in counts.items():
        pct = (n / len(files) * 100) if files else 0
        print(f"  {m}: {C.G}{n}{C.END}/{len(files)} files ready ({pct:.0f}%)")
    print()


def cmd_build(files, dry_run=False):
    """Build semua file. Print laporan."""
    # Load source files
    sources_content = {}
    for name, path in SOURCES.items():
        if not path.exists():
            print(f"{C.R}ERROR:{C.END} Source file missing: {path}")
            sys.exit(1)
        sources_content[name] = path.read_text(encoding="utf-8")
        print(f"{C.DIM}✓ Loaded {path.relative_to(ROOT)} ({len(sources_content[name])} chars){C.END}")

    if not dry_run:
        BACKUP_DIR.mkdir(exist_ok=True)
        # Tag backup dengan timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        (BACKUP_DIR / ".timestamp").write_text(timestamp)
        print(f"{C.DIM}✓ Backup directory: {BACKUP_DIR.relative_to(ROOT)}{C.END}")

    print(f"\n{C.B}━━━ BUILDING {len(files)} FILES ━━━{C.END}")
    if dry_run:
        print(f"{C.Y}DRY RUN — no files will be modified{C.END}")
    print()

    stats = {"UPDATED": 0, "UNCHANGED": 0, "ERROR": 0}
    skipped_files = []

    for f in files:
        rel = f.relative_to(ROOT)
        status, details = build_file(f, sources_content, dry_run=dry_run)

        if status == "UPDATED":
            stats["UPDATED"] += 1
            details_str = ", ".join(f"{k}:{v}" for k, v in details.items() if v != "SKIP (no marker)")
            print(f"  {C.G}✓{C.END} {rel}  {C.DIM}[{details_str}]{C.END}")
        elif status == "UNCHANGED":
            stats["UNCHANGED"] += 1
            if all(v == "SKIP (no marker)" for v in details.values()):
                skipped_files.append(rel)
            else:
                print(f"  {C.DIM}· {rel}  [no changes]{C.END}")
        else:
            stats["ERROR"] += 1
            print(f"  {C.R}✗{C.END} {rel}  {details}")

    print()
    print(f"{C.B}━━━ SUMMARY ━━━{C.END}")
    print(f"  {C.G}Updated:{C.END}    {stats['UPDATED']} files")
    print(f"  {C.DIM}Unchanged:{C.END}  {stats['UNCHANGED']} files")
    print(f"  {C.R}Errors:{C.END}     {stats['ERROR']} files")

    if skipped_files:
        print(f"\n{C.Y}⚠ {len(skipped_files)} file(s) tidak punya marker apapun — di-skip total:{C.END}")
        for s in skipped_files[:10]:
            print(f"    · {s}")
        if len(skipped_files) > 10:
            print(f"    ... dan {len(skipped_files) - 10} lainnya")
        print(f"\n{C.DIM}  Tambahkan marker dulu di file-file ini, atau jalankan: python build.py --add-markers{C.END}")

    if dry_run:
        print(f"\n{C.Y}This was a dry run. Re-run without --dry-run to apply changes.{C.END}")
    elif stats["UPDATED"] > 0:
        print(f"\n{C.G}✓ Backup tersimpan di .build-backup/{C.END}")
        print(f"{C.DIM}  Untuk restore: cp -r .build-backup/* .{C.END}")
    print()


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    check_only = "--check" in args
    filter_subdir = None

    for a in args:
        if not a.startswith("--"):
            filter_subdir = a
            break

    # Validate _includes exists
    if not INCLUDES_DIR.exists():
        print(f"{C.R}ERROR:{C.END} Folder {INCLUDES_DIR} tidak ditemukan.")
        print(f"Pastikan lo jalanin script ini dari ROOT repo solidpaving.id.")
        sys.exit(1)

    files = find_html_files(ROOT, filter_subdir=filter_subdir)
    if not files:
        print(f"{C.Y}Tidak ada file index.html ditemukan{C.END}")
        if filter_subdir:
            print(f"  Filter aktif: '{filter_subdir}'")
        sys.exit(0)

    if check_only:
        cmd_check(files)
    else:
        cmd_build(files, dry_run=dry_run)


if __name__ == "__main__":
    main()
