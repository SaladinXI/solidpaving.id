# Build System — SolidPaving.id

Sistem ini bikin lo cuma perlu edit **1 file** untuk update navbar/footer di seluruh website (43+ halaman).

## Setup pertama kali (sekali doang)

### 1. Install Python

**Windows:**
1. Download Python 3 dari https://www.python.org/downloads/
2. Saat install, **centang "Add Python to PATH"** — penting!
3. Buka Command Prompt, cek: `python --version` → harus muncul "Python 3.x.x"

**Mac:**
- Python 3 biasanya sudah ada. Cek: `python3 --version`
- Kalau belum, install via Homebrew: `brew install python3`

### 2. Clone / pull repo lo

```bash
cd /path/to/solidpaving.id
git pull
```

### 3. Pastikan struktur folder seperti ini:

```
solidpaving.id/
├── _includes/
│   ├── navbar.html
│   ├── mob-drawer.html
│   ├── footer.html
│   └── footer.css
├── bekasi/index.html
├── cikarang/index.html
├── ... (43+ file)
├── build.py
└── BUILD.md  ← file ini
```

## Workflow sehari-hari

### Skenario 1: Mau ganti satu menu di navbar

```bash
# 1. Buka file navbar.html di text editor
# 2. Edit sesukanya (misal tambah menu baru, ganti emoji, dll)
# 3. Save

# 4. Jalanin build
python build.py

# 5. Cek hasil di browser lokal — buka beberapa file .html
# 6. Kalau OK, commit dan push
git add .
git commit -m "Update navbar"
git push
```

### Skenario 2: Cek file mana yang punya marker, mana yang belum

```bash
python build.py --check
```

Output akan menampilkan tabel: tiap file vs status NAVBAR, MOB-DRAWER, FOOTER.

### Skenario 3: Dry-run dulu sebelum apply

```bash
python build.py --dry-run
```

Akan show apa yang AKAN diupdate, tanpa benar-benar nge-save. Aman untuk preview.

### Skenario 4: Update cuma 1 folder (untuk test)

```bash
python build.py bekasi
```

Hanya akan update file di dalam folder `bekasi/`.

## Cara kerja marker

Setiap file `index.html` yang mau di-manage harus punya marker seperti ini:

```html
<!-- NAVBAR:START -->
... (isi navbar di sini, akan di-replace otomatis) ...
<!-- NAVBAR:END -->
```

Script akan cari teks di antara `NAVBAR:START` dan `NAVBAR:END`, dan replace dengan isi `_includes/navbar.html`.

**File tanpa marker akan DI-SKIP** — tidak akan dirusak. Ini fitur safety.

## Recovery

Setiap kali `python build.py` jalan, dia auto-backup semua file yang berubah ke `.build-backup/`.

Kalau ada yang error / mau revert:

```bash
# Lihat folder backup
ls .build-backup/

# Restore semua
cp -r .build-backup/* .
```

Atau gunakan `git`:

```bash
git checkout .
```

## Troubleshooting

**"Python command not found"**
→ Python belum di-PATH. Install ulang dan centang "Add to PATH".

**"_includes folder not found"**
→ Lo jalanin script dari folder yang salah. Pindah ke root repo dulu.

**"No files updated"**
→ File belum punya marker `<!-- NAVBAR:START -->` dst. Cek dengan `python build.py --check`.

**Hasil di browser kelihatan rusak**
→ Restore dari backup: `cp -r .build-backup/* .` atau `git checkout .`
