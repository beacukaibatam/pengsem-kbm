import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SIZE = 1024
CENTER = SIZE // 2
RADIUS = 480

FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_REGULAR = "/System/Library/Fonts/Helvetica.ttc"
LOGO_HD_PATH = "logo-bea-cukai-hd.png"

def create_radial_gradient(size, inner_color, outer_color):
    """Membuat latar belakang gradasi radial halus."""
    base = Image.new("RGBA", (size, size), outer_color)
    radial = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(radial)
    cx, cy = size // 2, size // 2
    max_r = int(math.sqrt(cx**2 + cy**2))
    for r in range(max_r, 0, -2):
        ratio = r / max_r
        alpha = int(255 * (1 - ratio**1.4))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=alpha)
    
    inner_img = Image.new("RGBA", (size, size), inner_color)
    base.paste(inner_img, (0, 0), radial)
    return base

def draw_star(draw, x, y, r, color):
    """Menggambar bintang Nataru 4-titik berkilau elegan."""
    points = [
        (x, y - r),
        (x + r * 0.25, y - r * 0.25),
        (x + r, y),
        (x + r * 0.25, y + r * 0.25),
        (x, y + r),
        (x - r * 0.25, y + r * 0.25),
        (x - r, y),
        (x - r * 0.25, y - r * 0.25),
    ]
    draw.polygon(points, fill=color)

def draw_snowflake(draw, x, y, r, color, width=2):
    """Menggambar snowflake minimalis elegan."""
    for angle in [0, 60, 120]:
        rad = math.radians(angle)
        dx = r * math.cos(rad)
        dy = r * math.sin(rad)
        draw.line([x - dx, y - dy, x + dx, y + dy], fill=color, width=width)
        # cabang kecil
        for sign in [-1, 1]:
            bx = x + sign * dx * 0.6
            by = y + sign * dy * 0.6
            for branch_angle in [angle + 45, angle - 45]:
                brad = math.radians(branch_angle)
                bdx = (r * 0.3) * math.cos(brad)
                bdy = (r * 0.3) * math.sin(brad)
                draw.line([bx, by, bx + bdx, by + bdy], fill=color, width=max(1, width-1))

def draw_car_silhouette(draw, x, y, scale=1.0, color="#FFFFFF", has_luggage=True):
    """Menggambar siluet mobil keluarga / SUV mudik modern."""
    # Body mobil
    body = [
        (x - 140*scale, y + 25*scale),
        (x - 135*scale, y - 5*scale),
        (x - 110*scale, y - 10*scale),
        (x - 70*scale, y - 12*scale),
        (x - 45*scale, y - 48*scale),   # kaca depan
        (x + 50*scale, y - 48*scale),   # atap
        (x + 95*scale, y - 15*scale),   # kaca belakang
        (x + 130*scale, y - 10*scale),
        (x + 140*scale, y + 5*scale),
        (x + 140*scale, y + 25*scale),
        # Roda belakang cutout
        (x + 95*scale, y + 25*scale),
        (x + 85*scale, y + 10*scale),
        (x + 55*scale, y + 10*scale),
        (x + 45*scale, y + 25*scale),
        # Tengah
        (x - 45*scale, y + 25*scale),
        # Roda depan cutout
        (x - 55*scale, y + 10*scale),
        (x - 85*scale, y + 10*scale),
        (x - 95*scale, y + 25*scale),
    ]
    draw.polygon(body, fill=color)

    # Jendela
    win_f = [(x - 38*scale, y - 43*scale), (x - 5*scale, y - 43*scale), (x - 5*scale, y - 16*scale), (x - 60*scale, y - 16*scale)]
    win_r = [(x + 5*scale, y - 43*scale), (x + 45*scale, y - 43*scale), (x + 80*scale, y - 18*scale), (x + 5*scale, y - 18*scale)]
    draw.polygon(win_f, fill="#0F172A")
    draw.polygon(win_r, fill="#0F172A")

    # Roda ban
    wheel_r = 18 * scale
    draw.ellipse([x - 70*scale - wheel_r, y + 25*scale - wheel_r, x - 70*scale + wheel_r, y + 25*scale + wheel_r], fill="#1E293B", outline=color, width=int(2*scale))
    draw.ellipse([x + 70*scale - wheel_r, y + 25*scale - wheel_r, x + 70*scale + wheel_r, y + 25*scale + wheel_r], fill="#1E293B", outline=color, width=int(2*scale))
    # Velg emas
    draw.ellipse([x - 70*scale - wheel_r*0.4, y + 25*scale - wheel_r*0.4, x - 70*scale + wheel_r*0.4, y + 25*scale + wheel_r*0.4], fill="#FCB813")
    draw.ellipse([x + 70*scale - wheel_r*0.4, y + 25*scale - wheel_r*0.4, x + 70*scale + wheel_r*0.4, y + 25*scale + wheel_r*0.4], fill="#FCB813")

    # Roof rack & barang bawaan mudik
    if has_luggage:
        # Rel atap
        draw.line([x - 45*scale, y - 50*scale, x + 50*scale, y - 50*scale], fill="#FCB813", width=int(3*scale))
        # Koper 1
        draw.rounded_rectangle([x - 35*scale, y - 66*scale, x + 5*scale, y - 52*scale], radius=3, fill="#F59E0B", outline="#FFFFFF", width=1)
        # Tas / Box 2
        draw.rounded_rectangle([x + 10*scale, y - 62*scale, x + 45*scale, y - 52*scale], radius=2, fill="#0284C7", outline="#FFFFFF", width=1)

# ==============================================================================
# KONSEP 1: "The Royal Navy & Gold Festive" (Klasik Pabean Modern)
# ==============================================================================
def generate_concept_1():
    img = create_radial_gradient(SIZE, (0, 75, 145, 255), (2, 20, 48, 255))
    draw = ImageDraw.Draw(img)

    # Lingkaran Border Ganda Emas Elegan
    draw.ellipse([CENTER - RADIUS, CENTER - RADIUS, CENTER + RADIUS, CENTER + RADIUS], outline=(252, 184, 19, 255), width=8)
    draw.ellipse([CENTER - RADIUS + 18, CENTER - RADIUS + 18, CENTER + RADIUS - 18, CENTER + RADIUS - 18], outline=(252, 184, 19, 100), width=2)

    # Ornamen Bintang Nataru Halus di Background
    stars_coords = [
        (220, 220, 14), (800, 220, 16), (180, 480, 10), (840, 460, 12),
        (300, 150, 8), (720, 150, 10), (250, 720, 9), (770, 720, 11),
        (512, 110, 18)
    ]
    for sx, sy, sr in stars_coords:
        draw_star(draw, sx, sy, sr, "#FCB813")
        draw_star(draw, sx, sy, sr*0.5, "#FFFFFF")

    # Snowflakes Halus
    snow_coords = [(160, 340, 18), (860, 320, 20), (200, 600, 15), (820, 610, 16)]
    for fx, fy, fr in snow_coords:
        draw_snowflake(draw, fx, fy, fr, (255, 255, 255, 120), width=2)

    # Kurva Jalan Pabean Batam
    road_pts = [(160, 730), (320, 680), (512, 670), (700, 680), (864, 730), (864, 780), (160, 780)]
    draw.polygon(road_pts, fill="#0F172A")
    # Garis marka jalan emas
    for rx in range(240, 800, 70):
        draw.line([rx, 705, rx + 40, 705], fill="#FCB813", width=3)

    # Siluet Mobil Mudik Melaju
    draw_car_silhouette(draw, 512, 655, scale=1.35, color="#FFFFFF", has_luggage=True)

    # Logo Bea Cukai HD di Tengah Atas
    if os.path.exists(LOGO_HD_PATH):
        logo_raw = Image.open(LOGO_HD_PATH).convert("RGBA")
        logo_w = 400
        logo_h = int(logo_raw.height * (logo_w / logo_raw.width))
        logo_resized = logo_raw.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        img.paste(logo_resized, (CENTER - logo_w // 2, 170), logo_resized)

    # Tipografi Resmi
    try:
        font_title = ImageFont.truetype(FONT_BOLD, 42)
        font_sub = ImageFont.truetype(FONT_BOLD, 26)
        font_badge = ImageFont.truetype(FONT_BOLD, 22)
    except:
        font_title = font_sub = font_badge = ImageFont.load_default()

    # Pita Tag Nataru di Bawah Logo
    badge_w, badge_h = 340, 40
    badge_box = [CENTER - badge_w//2, 470, CENTER + badge_w//2, 470 + badge_h]
    draw.rounded_rectangle(badge_box, radius=20, fill="#002D59", outline="#FCB813", width=2)
    draw.text((CENTER, 490), "✨ NATARU 2026 / 2027 ✨", font=font_badge, fill="#FCB813", anchor="mm")

    # Banner Teks Bawah
    draw.text((CENTER, 810), "PENGELUARAN SEMENTARA KBM", font=font_title, fill="#FFFFFF", anchor="mm")
    draw.text((CENTER, 860), "BEA CUKAI BATAM", font=font_sub, fill="#FCB813", anchor="mm")

    return img

# ==============================================================================
# KONSEP 2: "Modern Minimalist Nataru Shield" (Elegan Simetris)
# ==============================================================================
def generate_concept_2():
    img = create_radial_gradient(SIZE, (0, 95, 172, 255), (0, 20, 45, 255))
    draw = ImageDraw.Draw(img)

    # Lingkaran Luar dengan Roda Gigi Pabean Halus
    draw.ellipse([CENTER - RADIUS, CENTER - RADIUS, CENTER + RADIUS, CENTER + RADIUS], outline="#FCB813", width=10)
    
    # Ornamen Wreath / Ranting Emas Simetris (Festive Laurel)
    for i in range(-5, 6):
        if i == 0: continue
        angle_l = 180 + i * 14
        angle_r = 0 - i * 14
        rad_l, rad_r = math.radians(angle_l), math.radians(angle_r)
        leaf_r = RADIUS - 40
        lx, ly = CENTER + leaf_r * math.cos(rad_l), CENTER + leaf_r * math.sin(rad_l)
        rx, ry = CENTER + leaf_r * math.cos(rad_r), CENTER + leaf_r * math.sin(rad_r)
        draw.ellipse([lx - 12, ly - 6, lx + 12, ly + 6], fill=(252, 184, 19, 210))
        draw.ellipse([rx - 12, ry - 6, rx + 12, ry + 6], fill=(252, 184, 19, 210))

    # Bintang Puncak Nataru di Paling Atas
    draw_star(draw, CENTER, 110, 28, "#FCB813")
    draw_star(draw, CENTER, 110, 14, "#FFFFFF")

    # Logo Bea Cukai Besar di Tengah
    if os.path.exists(LOGO_HD_PATH):
        logo_raw = Image.open(LOGO_HD_PATH).convert("RGBA")
        logo_w = 440
        logo_h = int(logo_raw.height * (logo_w / logo_raw.width))
        logo_resized = logo_raw.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        img.paste(logo_resized, (CENTER - logo_w // 2, 180), logo_resized)

    # Lingkaran Pembatas Emas Bawah
    draw.arc([CENTER - 360, CENTER - 100, CENTER + 360, CENTER + 620], start=20, end=160, fill="#FCB813", width=3)

    # Siluet Mobil Mudik di Bagian Bawah
    draw_car_silhouette(draw, CENTER, 650, scale=1.4, color="#FFFFFF", has_luggage=True)

    # Tipografi
    try:
        font_title = ImageFont.truetype(FONT_BOLD, 46)
        font_sub = ImageFont.truetype(FONT_BOLD, 26)
        font_tag = ImageFont.truetype(FONT_BOLD, 20)
    except:
        font_title = font_sub = font_tag = ImageFont.load_default()

    draw.text((CENTER, 785), "LAYANAN KBM", font=font_title, fill="#FCB813", anchor="mm")
    draw.text((CENTER, 835), "KPU BEA DAN CUKAI TIPE B BATAM", font=font_sub, fill="#FFFFFF", anchor="mm")
    draw.text((CENTER, 875), "MUDIK NATARU 2026/2027", font=font_tag, fill="#93C5FD", anchor="mm")

    return img

# ==============================================================================
# KONSEP 3: "Festive Horizon & Jembatan Barelang" (Dinamis Ilustratif)
# ==============================================================================
def generate_concept_3():
    img = create_radial_gradient(SIZE, (10, 80, 160, 255), (2, 15, 38, 255))
    draw = ImageDraw.Draw(img)

    # Lingkaran Border Luar Emas Mewah
    draw.ellipse([CENTER - RADIUS, CENTER - RADIUS, CENTER + RADIUS, CENTER + RADIUS], outline="#FCB813", width=6)
    draw.ellipse([CENTER - RADIUS + 12, CENTER - RADIUS + 12, CENTER + RADIUS - 12, CENTER + RADIUS - 12], outline="#FFFFFF", width=2)

    # Siluet Jembatan Barelang (Ikon Batam) di Latar Belakang
    pylon_left = [(340, 620), (350, 420), (355, 420), (365, 620)]
    pylon_right = [(655, 620), (665, 420), (670, 420), (680, 620)]
    draw.polygon(pylon_left, fill=(255, 255, 255, 60))
    draw.polygon(pylon_right, fill=(255, 255, 255, 60))
    # Kabel kabel jembatan
    for ky in range(440, 600, 30):
        draw.line([352, ky, 220, 620], fill=(252, 184, 19, 75), width=1)
        draw.line([352, ky, 500, 620], fill=(252, 184, 19, 75), width=1)
        draw.line([667, ky, 512, 620], fill=(252, 184, 19, 75), width=1)
        draw.line([667, ky, 780, 620], fill=(252, 184, 19, 75), width=1)

    # Bintang Gemerlap Malam Nataru
    stars = [(180, 240, 12), (280, 180, 15), (740, 190, 14), (840, 260, 12), (512, 120, 20), (512, 420, 10)]
    for sx, sy, sr in stars:
        draw_star(draw, sx, sy, sr, "#FCB813")
        draw_star(draw, sx, sy, sr*0.4, "#FFFFFF")

    # Logo Bea Cukai di Atas Jembatan
    if os.path.exists(LOGO_HD_PATH):
        logo_raw = Image.open(LOGO_HD_PATH).convert("RGBA")
        logo_w = 380
        logo_h = int(logo_raw.height * (logo_w / logo_raw.width))
        logo_resized = logo_raw.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        img.paste(logo_resized, (CENTER - logo_w // 2, 175), logo_resized)

    # Jalan Aspal Melengkung & Siluet Mobil Mudik
    road_box = [(120, 680), (512, 630), (904, 680), (904, 760), (120, 760)]
    draw.polygon(road_box, fill="#0F172A")
    draw_car_silhouette(draw, 512, 640, scale=1.3, color="#FFFFFF", has_luggage=True)

    # Tipografi
    try:
        font_main = ImageFont.truetype(FONT_BOLD, 40)
        font_sub = ImageFont.truetype(FONT_BOLD, 26)
        font_pill = ImageFont.truetype(FONT_BOLD, 20)
    except:
        font_main = font_sub = font_pill = ImageFont.load_default()

    # Pill Nataru
    pill_w, pill_h = 320, 36
    draw.rounded_rectangle([CENTER - pill_w//2, 480, CENTER + pill_w//2, 480 + pill_h], radius=18, fill="#005FAC", outline="#FCB813", width=2)
    draw.text((CENTER, 498), "🎄 POSKO MUDIK NATARU 🎁", font=font_pill, fill="#FFFFFF", anchor="mm")

    draw.text((CENTER, 805), "PENGELUARAN SEMENTARA KBM", font=font_main, fill="#FCB813", anchor="mm")
    draw.text((CENTER, 855), "KPU BEA CUKAI BATAM", font=font_sub, fill="#FFFFFF", anchor="mm")

    return img

# Simpan ketiga konsep
c1 = generate_concept_1()
c1.save("wa_profile_concept_1_royal_navy.png")
print("[+] Saved wa_profile_concept_1_royal_navy.png")

c2 = generate_concept_2()
c2.save("wa_profile_concept_2_gold_emblem.png")
print("[+] Saved wa_profile_concept_2_gold_emblem.png")

c3 = generate_concept_3()
c3.save("wa_profile_concept_3_festive_journey.png")
print("[+] Saved wa_profile_concept_3_festive_journey.png")

# Buat Lembar Mockup WhatsApp Preview Terpadu (3 Avatar Lingkaran Berjajar)
preview_w = 1200
preview_h = 600
preview_img = Image.new("RGBA", (preview_w, preview_h), (15, 23, 42, 255))
pdraw = ImageDraw.Draw(preview_img)

# Judul
try:
    font_header = ImageFont.truetype(FONT_BOLD, 32)
    font_label = ImageFont.truetype(FONT_BOLD, 22)
    font_desc = ImageFont.truetype(FONT_REGULAR, 16)
except:
    font_header = font_label = font_desc = ImageFont.load_default()

pdraw.text((preview_w // 2, 45), "PRATINJAU FOTO PROFIL WHATSAPP RESMI BOT KBM BATAM", font=font_header, fill="#FCB813", anchor="mm")
pdraw.text((preview_w // 2, 85), "Seksi Fasilitas Pabean dan Cukai — KPU Bea dan Cukai Tipe B Batam", font=font_desc, fill="#94A3B8", anchor="mm")

concepts = [
    (c1, "OPSI 1: Royal Navy & Festive", "Klasik Pabean Modern, Mobil Mudik, Bintang Nataru", 230),
    (c2, "OPSI 2: Minimalist Gold Shield", "Simetris Elegan, Laurel Emas, Mobil Melaju", 600),
    (c3, "OPSI 3: Festive Horizon Barelang", "Siluet Jembatan Barelang Batam & Nuansa Malam", 970),
]

# Masking Lingkaran Presisi WhatsApp
mask = Image.new("L", (320, 320), 0)
mask_draw = ImageDraw.Draw(mask)
mask_draw.ellipse([0, 0, 320, 320], fill=255)

for c_img, title, desc, cx in concepts:
    resized = c_img.resize((320, 320), Image.Resampling.LANCZOS)
    circle_img = Image.new("RGBA", (320, 320), (0, 0, 0, 0))
    circle_img.paste(resized, (0, 0), mask)
    
    # Outer WhatsApp ring shadow
    pdraw.ellipse([cx - 165, 260 - 165, cx + 165, 260 + 165], outline="#25D366", width=4) # Warna hijau WA
    preview_img.paste(circle_img, (cx - 160, 260 - 160), circle_img)
    
    pdraw.text((cx, 465), title, font=font_label, fill="#FFFFFF", anchor="mm")
    pdraw.text((cx, 495), desc, font=font_desc, fill="#CBD5E1", anchor="mm")

preview_img.save("wa_profile_preview_all_options.png")
print("[+] Saved wa_profile_preview_all_options.png")
