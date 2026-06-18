#!/usr/bin/env python3
"""
Auto-patcher untuk halaman supplier-paving/index.html
Menambahkan section "Armada Feature" + update info list.

Cara pakai:
1. Letakkan file ini di root repo solidpaving.id
2. Jalankan: python patch-supplier.py
3. Otomatis backup ke supplier-paving/index.html.bak

Yang berubah:
- Tambah CSS .armada-feature dan related classes di <style>
- Replace section #pengiriman dengan versi baru (armada feature + info upgrade)
"""

from pathlib import Path
import shutil
import sys

TARGET = Path("layanan/supplier-paving/index.html")

# ============================================
# CSS yang akan ditambahkan
# ============================================
NEW_CSS = """
/* Armada feature block */
.armada-feature{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:center;background:linear-gradient(135deg,var(--bg1) 0%,var(--bg2) 100%);border:1px solid var(--bdr);border-radius:var(--rl);padding:40px;margin-bottom:8px;}
.armada-img{position:relative;border-radius:var(--rl);overflow:hidden;border:1px solid var(--bdr);box-shadow:0 8px 32px rgba(46,62,95,.14);}
.armada-img img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block;}
.armada-img-badges{position:absolute;bottom:0;left:0;right:0;padding:32px 14px 14px;background:linear-gradient(transparent,rgba(13,26,46,.7));display:flex;gap:6px;flex-wrap:wrap;}
.armada-content{display:flex;flex-direction:column;}
.armada-tag{display:inline-block;font-size:11px;font-weight:700;letter-spacing:2px;color:var(--blue);background:rgba(46,62,95,.08);padding:5px 12px;border-radius:100px;margin-bottom:14px;align-self:flex-start;}
.armada-title{font-size:22px;font-weight:700;color:var(--tx1);margin-bottom:12px;letter-spacing:-.3px;line-height:1.25;}
.armada-desc{font-size:14px;color:var(--tx2);line-height:1.7;margin-bottom:24px;}
.armada-desc strong{color:var(--tx1);}
.armada-stats{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--bdr);border:1px solid var(--bdr);border-radius:var(--r);overflow:hidden;margin-bottom:20px;}
.armada-stat{background:var(--bg0);padding:18px 16px;text-align:center;}
.armada-stat-num{font-size:28px;font-weight:800;color:var(--blue);letter-spacing:-1px;line-height:1;margin-bottom:6px;}
.armada-stat-label{font-size:11px;color:var(--tx3);line-height:1.4;}
.armada-capacity{background:var(--bg0);border:1px solid var(--bds);border-radius:var(--r);padding:14px 16px;}
.armada-cap-title{font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--tx3);margin-bottom:10px;}
.armada-cap-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;}
.armada-cap-item{display:flex;flex-direction:column;gap:2px;}
.armada-cap-spec{font-size:12px;color:var(--tx2);font-weight:600;}
.armada-cap-val{font-size:16px;font-weight:700;color:var(--blue);}
@media(max-width:768px){.armada-feature{grid-template-columns:1fr;padding:24px;gap:24px;}.armada-title{font-size:20px;}.armada-stats{grid-template-columns:1fr 1fr;}.armada-stat-num{font-size:24px;}}
@media(max-width:480px){.armada-feature{padding:20px;}.armada-stats{grid-template-columns:1fr;}.armada-cap-grid{grid-template-columns:1fr;}}
"""

# Anchor untuk inject CSS (cari kalimat ini, tambah CSS setelahnya)
CSS_ANCHOR = "#pengiriman{background:var(--bg0);}"

# ============================================
# Section pengiriman lama (yang akan di-replace)
# ============================================
OLD_SECTION_START = '<section id="pengiriman">'
OLD_SECTION_END_BEFORE = '<section id="faq">'

# ============================================
# Section pengiriman baru
# ============================================
NEW_SECTION = '''<section id="pengiriman">
  <div class="container">
    <div class="sec-label">Pengiriman & Cara Order</div>
    <h2>Armada Sendiri, <span class="blue">Langsung ke Lokasi Proyek</span></h2>
    <div class="divider"></div>

    <div class="armada-feature">
      <div class="armada-img">
        <img src="https://ectascom.sirv.com/solidpaving.id/Tentang%20kami%20solidpaving.id/pengiriman%20paving%20UBIN%2021.jpg?w=640&q=85&format=webp" alt="Pengiriman paving block SolidPaving.id menggunakan armada sendiri dengan truk crane dan sistem pallet" loading="lazy" width="640" height="480">
        <div class="armada-img-badges">
          <span class="hbadge">Armada Sendiri</span>
          <span class="hbadge">Truk Crane</span>
          <span class="hbadge">Sistem Pallet</span>
        </div>
      </div>
      <div class="armada-content">
        <div class="armada-tag">🚚 Keunggulan Pengiriman Kami</div>
        <h3 class="armada-title">Armada Truk Crane + Sistem Pallet</h3>
        <p class="armada-desc">Tidak seperti supplier lain yang sewa truk dan kirim material curah, kami punya <strong>armada sendiri dengan truk dilengkapi crane</strong>. Pengiriman pakai <strong>sistem pallet</strong> — paving tetap rapi, tidak retak/rusak di perjalanan, dan crane bisa unloading sendiri tanpa tenaga manual dari proyek Anda.</p>

        <div class="armada-stats">
          <div class="armada-stat">
            <div class="armada-stat-num">2–4</div>
            <div class="armada-stat-label">Truk per pengiriman<br>ke 1 lokasi</div>
          </div>
          <div class="armada-stat">
            <div class="armada-stat-num">2–3</div>
            <div class="armada-stat-label">Truk per hari<br>(max 4 jika tidak padat)</div>
          </div>
        </div>

        <div class="armada-capacity">
          <div class="armada-cap-title">Kapasitas per Truk</div>
          <div class="armada-cap-grid">
            <div class="armada-cap-item">
              <div class="armada-cap-spec">Tebal 6 cm</div>
              <div class="armada-cap-val">≈ 91 m²</div>
            </div>
            <div class="armada-cap-item">
              <div class="armada-cap-spec">Tebal 8 cm</div>
              <div class="armada-cap-val">≈ 63 m²</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="pengiriman-grid" style="margin-top:48px;">
      <div class="info-list">
        <div class="info-item">
          <div class="info-ico">📍</div>
          <div><h3>Area Pengiriman</h3><p>Jabodetabek (Jakarta, Bekasi, Depok, Tangerang, Bogor) dan Jawa Barat (Cikarang, Karawang, Purwakarta, Bandung). Luar area: hubungi kami untuk biaya mobilisasi.</p></div>
        </div>
        <div class="info-item">
          <div class="info-ico">🏗️</div>
          <div><h3>Truk Crane Unloading</h3><p>Setiap truk dilengkapi crane — tidak perlu tenaga manual dari proyek Anda. Cocok untuk lahan yang aksesnya susah dijangkau forklift.</p></div>
        </div>
        <div class="info-item">
          <div class="info-ico">📦</div>
          <div><h3>Sistem Pallet</h3><p>Material disusun di pallet, dibungkus rapi. Paving tidak retak/rusak saat transport. Pallet bisa di-stack di lokasi proyek untuk efisiensi area.</p></div>
        </div>
        <div class="info-item">
          <div class="info-ico">📅</div>
          <div><h3>Pengiriman Terjadwal</h3><p>Untuk proyek besar dengan volume harian terbatas, kami bagi pengiriman bertahap sesuai progress pasang. Tidak menumpuk material di lokasi.</p></div>
        </div>
        <div class="info-item">
          <div class="info-ico">✅</div>
          <div><h3>Jaminan Kualitas</h3><p>Setiap batch produksi melalui quality control. Material yang dikirim sesuai mutu K yang dipesan — bukan substitusi mutu yang lebih rendah.</p></div>
        </div>
      </div>
      <div class="order-box">
        <h3>Cara Order Material</h3>
        <p>Proses mudah, konfirmasi cepat, pengiriman terjadwal.</p>
        <div class="order-steps">
          <div class="order-step"><div class="order-num">1</div><div class="order-text">Chat WhatsApp — sampaikan jenis paving, mutu K, ketebalan, dan estimasi luas lahan</div></div>
          <div class="order-step"><div class="order-num">2</div><div class="order-text">Kami konfirmasi ketersediaan stok dan harga dalam 24 jam kerja</div></div>
          <div class="order-step"><div class="order-num">3</div><div class="order-text">Sepakati harga, jadwal pengiriman, dan alamat lokasi proyek</div></div>
          <div class="order-step"><div class="order-num">4</div><div class="order-text">Material dikirim ke lokasi sesuai jadwal yang disepakati</div></div>
        </div>
        <a href="https://wa.me/6285943492832?text=Halo+SolidPaving.id+saya+mau+order+material+paving+block" class="btn-wa">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="var(--blue)"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
          Order Material via WhatsApp
        </a>
      </div>
    </div>
  </div>
</section>

'''

# ============================================
# MAIN
# ============================================

def main():
    if not TARGET.exists():
        print(f"❌ File tidak ditemukan: {TARGET}")
        print(f"   Pastikan script dijalankan dari root repo solidpaving.id")
        sys.exit(1)

    print(f"📄 Reading: {TARGET}")
    content = TARGET.read_text(encoding="utf-8")
    original_len = len(content)

    # Backup
    backup = TARGET.with_suffix(".html.bak")
    shutil.copy2(TARGET, backup)
    print(f"💾 Backup: {backup}")

    # Step 1: Inject CSS
    if "armada-feature" in content:
        print("⚠️  CSS armada sudah ada, skip inject")
    else:
        if CSS_ANCHOR not in content:
            print(f"❌ CSS anchor tidak ditemukan: '{CSS_ANCHOR}'")
            sys.exit(1)
        content = content.replace(CSS_ANCHOR, CSS_ANCHOR + NEW_CSS, 1)
        print(f"✓ CSS injected ({len(NEW_CSS):,} chars)")

    # Step 2: Replace section #pengiriman
    start_idx = content.find(OLD_SECTION_START)
    end_idx = content.find(OLD_SECTION_END_BEFORE)

    if start_idx == -1 or end_idx == -1:
        print(f"❌ Section pengiriman atau FAQ tidak ditemukan")
        sys.exit(1)

    if 'armada-feature' in content[start_idx:end_idx]:
        print("⚠️  Section pengiriman sudah ter-update, skip replace")
    else:
        content = content[:start_idx] + NEW_SECTION + content[end_idx:]
        print(f"✓ Section #pengiriman replaced")

    # Write
    TARGET.write_text(content, encoding="utf-8")
    new_len = len(content)
    print(f"\n✅ Done!")
    print(f"   Original: {original_len:,} chars")
    print(f"   Updated:  {new_len:,} chars")
    print(f"   Delta:    {new_len - original_len:+,} chars")
    print(f"\n   File: {TARGET}")
    print(f"   Backup: {backup}")
    print(f"\nNext step:")
    print(f"   1. Buka file di browser untuk test")
    print(f"   2. Kalau OK: git add, commit, push")
    print(f"   3. Kalau ada masalah: cp {backup} {TARGET} (rollback)")

if __name__ == "__main__":
    main()
