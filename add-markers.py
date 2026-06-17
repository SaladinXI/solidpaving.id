#!/usr/bin/env python3
"""
Add Markers Script
==================

Script ini OTOMATIS menambahkan marker:
  <!-- NAVBAR:START --> ... <!-- NAVBAR:END -->
  <!-- MOB-DRAWER:START --> ... <!-- MOB-DRAWER:END -->
  <!-- FOOTER:START --> ... <!-- FOOTER:END -->

di semua file index.html yang BELUM punya marker.

Cara pakai:
    python add-markers.py --dry-run     # Preview dulu, jangan save
    python add-markers.py bekasi        # Test 1 folder dulu
    python add-markers.py               # Apply ke semua file

Safety:
- File yang SUDAH punya marker → di-SKIP (tidak dirusak)
- Auto backup ke .add-markers-backup/ sebelum save
- Bisa di-revert kalau salah
"""

import os
import sys
import shutil
import re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.resolve()
BACKUP_DIR = ROOT / ".add-markers-backup"
SKIP_DIRS = {"_includes", ".git", ".build-backup", ".add-markers-backup", "node_modules", ".github"}


class C:
    R = '\033[91m'
    G = '\033[92m'
    Y = '\033[93m'
    B = '\033[94m'
    DIM = '\033[2m'
    END = '\033[0m'


def find_html_files(root, filter_subdir=None):
    files = []
    for path in root.rglob("index.html"):
        rel_parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        if filter_subdir:
            if filter_subdir not in rel_parts:
                continue
        files.append(path)
    return sorted(files)


def find_matching_close(content, start_pos, open_tag, close_tag):
    """
    Find the matching close tag for a nested open tag, starting from start_pos.
    Returns the index right AFTER the close tag.
    """
    depth = 1
    pos = start_pos
    open_pattern = re.compile(r'<' + open_tag + r'(?:\s|>)', re.IGNORECASE)
    close_pattern = re.compile(r'</' + close_tag + r'\s*>', re.IGNORECASE)
    
    while depth > 0 and pos < len(content):
        next_open = open_pattern.search(content, pos)
        next_close = close_pattern.search(content, pos)
        
        if not next_close:
            return -1
        
        if next_open and next_open.start() < next_close.start():
            depth += 1
            pos = next_open.end()
        else:
            depth -= 1
            pos = next_close.end()
            if depth == 0:
                return pos
    return -1


def wrap_navbar(content):
    """Wrap <nav>...</nav> (first occurrence after <body>) with marker."""
    if "<!-- NAVBAR:START -->" in content:
        return content, False, "already has marker"
    
    # Cari <nav> pertama setelah <body>
    body_match = re.search(r'<body[^>]*>', content, re.IGNORECASE)
    if not body_match:
        return content, False, "no <body> found"
    
    nav_match = re.search(r'<nav(?:\s|>)', content[body_match.end():], re.IGNORECASE)
    if not nav_match:
        return content, False, "no <nav> found"
    
    nav_start = body_match.end() + nav_match.start()
    # Find end of <nav> opening tag
    open_end = content.find('>', nav_start) + 1
    # Find matching </nav>
    nav_end = find_matching_close(content, open_end, 'nav', 'nav')
    if nav_end == -1:
        return content, False, "no matching </nav>"
    
    new_content = (
        content[:nav_start]
        + "<!-- NAVBAR:START -->\n"
        + content[nav_start:nav_end]
        + "\n<!-- NAVBAR:END -->"
        + content[nav_end:]
    )
    return new_content, True, "wrapped"


def wrap_mob_drawer(content):
    """Wrap <div class="mob-drawer" ...>...</div> with marker."""
    if "<!-- MOB-DRAWER:START -->" in content:
        return content, False, "already has marker"
    
    # Cari div mob-drawer
    pattern = re.compile(r'<div\s+class="mob-drawer"[^>]*>', re.IGNORECASE)
    match = pattern.search(content)
    if not match:
        return content, False, "no mob-drawer found"
    
    drawer_start = match.start()
    open_end = match.end()
    drawer_end = find_matching_close(content, open_end, 'div', 'div')
    if drawer_end == -1:
        return content, False, "no matching </div>"
    
    new_content = (
        content[:drawer_start]
        + "<!-- MOB-DRAWER:START -->\n"
        + content[drawer_start:drawer_end]
        + "\n<!-- MOB-DRAWER:END -->"
        + content[drawer_end:]
    )
    return new_content, True, "wrapped"


def wrap_footer(content):
    """Wrap <footer>...</footer> with marker."""
    if "<!-- FOOTER:START -->" in content:
        return content, False, "already has marker"
    
    pattern = re.compile(r'<footer(?:\s|>)', re.IGNORECASE)
    match = pattern.search(content)
    if not match:
        return content, False, "no <footer> found"
    
    footer_start = match.start()
    open_end = content.find('>', footer_start) + 1
    footer_end = find_matching_close(content, open_end, 'footer', 'footer')
    if footer_end == -1:
        return content, False, "no matching </footer>"
    
    new_content = (
        content[:footer_start]
        + "<!-- FOOTER:START -->\n"
        + content[footer_start:footer_end]
        + "\n<!-- FOOTER:END -->"
        + content[footer_end:]
    )
    return new_content, True, "wrapped"


def backup_file(file_path):
    rel = file_path.relative_to(ROOT)
    backup_path = BACKUP_DIR / rel
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(file_path, backup_path)


def process_file(file_path, dry_run=False):
    """Add markers to one file. Return (status, results)."""
    content = file_path.read_text(encoding="utf-8")
    original = content
    results = {}

    content, ok, msg = wrap_navbar(content)
    results['NAVBAR'] = ('✓' if ok else '·', msg)

    content, ok, msg = wrap_mob_drawer(content)
    results['MOB-DRAWER'] = ('✓' if ok else '·', msg)

    content, ok, msg = wrap_footer(content)
    results['FOOTER'] = ('✓' if ok else '·', msg)

    n_changed = sum(1 for k, v in results.items() if v[0] == '✓')

    if content == original:
        return "UNCHANGED", results, n_changed

    if not dry_run:
        backup_file(file_path)
        file_path.write_text(content, encoding="utf-8")

    return "UPDATED", results, n_changed


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    filter_subdir = None

    for a in args:
        if not a.startswith("--"):
            filter_subdir = a
            break

    files = find_html_files(ROOT, filter_subdir=filter_subdir)
    if not files:
        print(f"{C.Y}Tidak ada file index.html ditemukan{C.END}")
        sys.exit(0)

    if not dry_run:
        BACKUP_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        (BACKUP_DIR / ".timestamp").write_text(timestamp)
        print(f"{C.DIM}✓ Backup directory: {BACKUP_DIR.relative_to(ROOT)}{C.END}")

    print(f"\n{C.B}━━━ ADDING MARKERS to {len(files)} FILES ━━━{C.END}")
    if dry_run:
        print(f"{C.Y}DRY RUN — no files will be modified{C.END}")
    if filter_subdir:
        print(f"{C.DIM}Filter: '{filter_subdir}'{C.END}")
    print()

    stats = {"UPDATED": 0, "UNCHANGED": 0}
    total_markers_added = 0

    for f in files:
        rel = f.relative_to(ROOT)
        status, results, n_changed = process_file(f, dry_run=dry_run)
        total_markers_added += n_changed

        if status == "UPDATED":
            stats["UPDATED"] += 1
            details_str = ", ".join(f"{k}:{v[0]}" for k, v in results.items())
            print(f"  {C.G}✓{C.END} {rel}  {C.DIM}[{details_str}]{C.END}")
        else:
            stats["UNCHANGED"] += 1
            details_str = ", ".join(f"{k}:{v[1]}" for k, v in results.items())
            print(f"  {C.DIM}· {rel}  [{details_str}]{C.END}")

    print()
    print(f"{C.B}━━━ SUMMARY ━━━{C.END}")
    print(f"  {C.G}Files updated:{C.END}     {stats['UPDATED']}")
    print(f"  {C.DIM}Files unchanged:{C.END}   {stats['UNCHANGED']}")
    print(f"  {C.G}Total markers added:{C.END} {total_markers_added}")

    if dry_run:
        print(f"\n{C.Y}This was a dry run. Re-run without --dry-run to apply changes.{C.END}")
    elif stats["UPDATED"] > 0:
        print(f"\n{C.G}✓ Backup tersimpan di .add-markers-backup/{C.END}")
        print(f"{C.DIM}  Untuk restore: cp -r .add-markers-backup/* .{C.END}")
        print(f"\n{C.B}Langkah selanjutnya:{C.END}")
        print(f"  1. python build.py --check    (cek semua marker ready)")
        print(f"  2. python build.py bekasi     (test build 1 folder dulu)")
        print(f"  3. python build.py            (apply ke semua)")
    print()


if __name__ == "__main__":
    main()
