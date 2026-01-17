from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode
import math
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = r"C:\Users\richa\.claude\skills\canvas-design\canvas-fonts"

# Canvas dimensions (Letter size at 150 DPI for good print quality)
WIDTH = 1275  # 8.5 inches
HEIGHT = 1650  # 11 inches

# Color palette - vibrant purple, teal, pink, yellow
PURPLE = (155, 89, 182)
PURPLE_DARK = (125, 60, 152)
TEAL = (26, 188, 156)
TEAL_DARK = (22, 160, 133)
PINK = (255, 107, 157)
PINK_LIGHT = (255, 184, 208)
YELLOW = (255, 220, 80)
YELLOW_LIGHT = (255, 240, 150)
CREAM = (255, 249, 245)
WHITE = (255, 255, 255)

def create_gradient_background(draw, width, height):
    """Create a purple gradient background"""
    # Purple gradient from lighter at top to darker at bottom
    PURPLE_TOP = (180, 120, 210)  # Lighter purple
    PURPLE_BOTTOM = (100, 50, 140)  # Darker purple
    for y in range(height):
        ratio = y / height
        r = int(PURPLE_TOP[0] * (1 - ratio) + PURPLE_BOTTOM[0] * ratio)
        g = int(PURPLE_TOP[1] * (1 - ratio) + PURPLE_BOTTOM[1] * ratio)
        b = int(PURPLE_TOP[2] * (1 - ratio) + PURPLE_BOTTOM[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

def draw_doodle_line(draw, start_x, start_y, length, angle, color, thickness=4):
    """Draw a wavy doodle-style line"""
    points = []
    for i in range(int(length)):
        wave = math.sin(i * 0.15) * 8
        x = start_x + i * math.cos(math.radians(angle)) + wave * math.sin(math.radians(angle))
        y = start_y + i * math.sin(math.radians(angle)) - wave * math.cos(math.radians(angle))
        points.append((x, y))
    if len(points) > 1:
        draw.line(points, fill=color, width=thickness)

def draw_spiral(draw, cx, cy, max_radius, color, thickness=3):
    """Draw a spiral pattern"""
    points = []
    for i in range(0, 720, 5):
        angle = math.radians(i)
        radius = (i / 720) * max_radius
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        points.append((x, y))
    if len(points) > 1:
        draw.line(points, fill=color, width=thickness)

def draw_loopy_border(draw, x1, y1, x2, y2, color, loops=20):
    """Draw a loopy decorative border"""
    # Top border
    for i in range(loops):
        cx = x1 + (x2 - x1) * i / loops + (x2 - x1) / loops / 2
        cy = y1
        radius = 15
        draw.arc([cx - radius, cy - radius, cx + radius, cy + radius],
                 start=180, end=360, fill=color, width=3)
    # Bottom border
    for i in range(loops):
        cx = x1 + (x2 - x1) * i / loops + (x2 - x1) / loops / 2
        cy = y2
        radius = 15
        draw.arc([cx - radius, cy - radius, cx + radius, cy + radius],
                 start=0, end=180, fill=color, width=3)

def draw_decorative_circle(draw, cx, cy, radius, color):
    """Draw a decorative circle with inner pattern"""
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 outline=color, width=4)
    # Inner spiral
    draw_spiral(draw, cx, cy, radius * 0.7, color, 2)

def draw_3d_animal_icon(draw, cx, cy, size, animal_type, colors):
    """Draw simple but charming animal representations"""
    if animal_type == "butterfly":
        # Wings
        wing_size = size * 0.4
        draw.ellipse([cx - wing_size * 1.5, cy - wing_size,
                      cx - wing_size * 0.3, cy + wing_size], fill=colors[0], outline=PURPLE_DARK, width=2)
        draw.ellipse([cx + wing_size * 0.3, cy - wing_size,
                      cx + wing_size * 1.5, cy + wing_size], fill=colors[1], outline=PURPLE_DARK, width=2)
        # Body
        draw.ellipse([cx - 8, cy - size * 0.3, cx + 8, cy + size * 0.3], fill=PURPLE_DARK)
        # Antennae
        draw.line([cx - 3, cy - size * 0.3, cx - 15, cy - size * 0.5], fill=PURPLE_DARK, width=2)
        draw.line([cx + 3, cy - size * 0.3, cx + 15, cy - size * 0.5], fill=PURPLE_DARK, width=2)

    elif animal_type == "cat":
        # Head
        head_size = size * 0.35
        draw.ellipse([cx - head_size, cy - head_size, cx + head_size, cy + head_size],
                     fill=colors[0], outline=PURPLE_DARK, width=2)
        # Ears
        ear_points_l = [(cx - head_size * 0.7, cy - head_size * 0.5),
                        (cx - head_size * 0.3, cy - head_size * 1.3),
                        (cx - head_size * 0.1, cy - head_size * 0.6)]
        ear_points_r = [(cx + head_size * 0.7, cy - head_size * 0.5),
                        (cx + head_size * 0.3, cy - head_size * 1.3),
                        (cx + head_size * 0.1, cy - head_size * 0.6)]
        draw.polygon(ear_points_l, fill=colors[1], outline=PURPLE_DARK)
        draw.polygon(ear_points_r, fill=colors[1], outline=PURPLE_DARK)
        # Eyes
        draw.ellipse([cx - head_size * 0.4, cy - head_size * 0.2,
                      cx - head_size * 0.15, cy + head_size * 0.1], fill=TEAL)
        draw.ellipse([cx + head_size * 0.15, cy - head_size * 0.2,
                      cx + head_size * 0.4, cy + head_size * 0.1], fill=TEAL)
        # Nose
        draw.polygon([(cx, cy + head_size * 0.15), (cx - 8, cy + head_size * 0.35),
                      (cx + 8, cy + head_size * 0.35)], fill=PINK)

    elif animal_type == "star":
        # Five-pointed star
        points = []
        for i in range(10):
            angle = math.radians(i * 36 - 90)
            r = size * 0.5 if i % 2 == 0 else size * 0.25
            points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        draw.polygon(points, fill=colors[0], outline=PURPLE_DARK, width=2)
        # Inner details
        draw_spiral(draw, cx, cy, size * 0.15, colors[1], 2)

    elif animal_type == "flower":
        # Petals
        petal_count = 6
        for i in range(petal_count):
            angle = math.radians(i * 60)
            px = cx + math.cos(angle) * size * 0.25
            py = cy + math.sin(angle) * size * 0.25
            petal_r = size * 0.22
            draw.ellipse([px - petal_r, py - petal_r, px + petal_r, py + petal_r],
                        fill=colors[0], outline=PURPLE_DARK, width=2)
        # Center
        draw.ellipse([cx - size * 0.15, cy - size * 0.15, cx + size * 0.15, cy + size * 0.15],
                     fill=colors[1], outline=PURPLE_DARK, width=2)

    elif animal_type == "turtle":
        # Shell
        shell_w = size * 0.5
        shell_h = size * 0.35
        draw.ellipse([cx - shell_w, cy - shell_h, cx + shell_w, cy + shell_h],
                     fill=colors[0], outline=PURPLE_DARK, width=3)
        # Shell pattern
        draw.ellipse([cx - shell_w * 0.5, cy - shell_h * 0.5, cx + shell_w * 0.5, cy + shell_h * 0.5],
                     outline=colors[1], width=2)
        # Head
        draw.ellipse([cx + shell_w * 0.8, cy - 12, cx + shell_w * 1.2, cy + 12],
                     fill=TEAL, outline=PURPLE_DARK, width=2)
        # Legs
        for dx, dy in [(-0.7, 0.6), (-0.7, -0.6), (0.5, 0.7), (0.5, -0.7)]:
            lx = cx + shell_w * dx
            ly = cy + shell_h * dy
            draw.ellipse([lx - 10, ly - 8, lx + 10, ly + 8], fill=TEAL, outline=PURPLE_DARK, width=2)

def create_qr_code(url, size):
    """Generate QR code for the website"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=PURPLE_DARK, back_color=WHITE)
    qr_img = qr_img.convert('RGBA')
    qr_img = qr_img.resize((size, size), Image.LANCZOS)
    return qr_img

def main():
    # Create canvas
    img = Image.new('RGB', (WIDTH, HEIGHT), CREAM)
    draw = ImageDraw.Draw(img)

    # Background gradient
    create_gradient_background(draw, WIDTH, HEIGHT)

    # Load fonts
    try:
        font_title = ImageFont.truetype(os.path.join(FONTS_DIR, "Boldonse-Regular.ttf"), 95)
        font_tagline = ImageFont.truetype(os.path.join(FONTS_DIR, "NothingYouCouldDo-Regular.ttf"), 38)
        font_body = ImageFont.truetype(os.path.join(FONTS_DIR, "Outfit-Regular.ttf"), 32)
        font_body_bold = ImageFont.truetype(os.path.join(FONTS_DIR, "Outfit-Bold.ttf"), 36)
        font_price = ImageFont.truetype(os.path.join(FONTS_DIR, "BricolageGrotesque-Bold.ttf"), 52)
        font_url = ImageFont.truetype(os.path.join(FONTS_DIR, "JetBrainsMono-Regular.ttf"), 28)
    except Exception as e:
        print(f"Font loading error: {e}, using defaults")
        font_title = ImageFont.load_default()
        font_tagline = font_title
        font_body = font_title
        font_body_bold = font_title
        font_price = font_title
        font_url = font_title

    # Decorative corner elements
    draw_spiral(draw, 80, 80, 60, YELLOW, 3)
    draw_spiral(draw, WIDTH - 80, 80, 60, PINK, 3)
    draw_spiral(draw, 80, HEIGHT - 80, 60, PINK, 3)
    draw_spiral(draw, WIDTH - 80, HEIGHT - 80, 60, YELLOW, 3)

    # Additional decorative doodle lines around edges
    for i in range(5):
        draw_doodle_line(draw, 30 + i * 250, 140, 80, 90, TEAL, 3)

    # Header section with loopy border
    header_y = 180
    draw_loopy_border(draw, 100, header_y - 30, WIDTH - 100, header_y + 200, YELLOW, 18)

    # Title: 3Doodle Critters
    title = "3Doodle Critters"
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (WIDTH - title_width) // 2

    # Title shadow
    draw.text((title_x + 4, header_y + 24), title, font=font_title, fill=(60, 30, 80))
    # Title main - white for contrast on purple background
    draw.text((title_x, header_y + 20), title, font=font_title, fill=WHITE)

    # Tagline
    tagline = "Handmade 3D Pen Art"
    tagline_bbox = draw.textbbox((0, 0), tagline, font=font_tagline)
    tagline_width = tagline_bbox[2] - tagline_bbox[0]
    tagline_x = (WIDTH - tagline_width) // 2
    draw.text((tagline_x, header_y + 160), tagline, font=font_tagline, fill=PINK_LIGHT)

    # Info section
    info_y = 500

    # Price banner
    price_text = "$2 - $10"
    price_bbox = draw.textbbox((0, 0), price_text, font=font_price)
    price_width = price_bbox[2] - price_bbox[0]
    price_x = (WIDTH - price_width) // 2

    # Price background bubble
    bubble_padding = 40
    draw.rounded_rectangle(
        [price_x - bubble_padding, info_y - 15,
         price_x + price_width + bubble_padding, info_y + 70],
        radius=35, fill=TEAL, outline=TEAL_DARK, width=3
    )
    draw.text((price_x, info_y), price_text, font=font_price, fill=WHITE)

    # Description text
    desc_y = info_y + 120
    descriptions = [
        "Unique handcrafted creations",
        "Animals, flowers, stars & more!",
        "Perfect gifts for friends & family",
    ]

    for i, desc in enumerate(descriptions):
        desc_bbox = draw.textbbox((0, 0), desc, font=font_body)
        desc_width = desc_bbox[2] - desc_bbox[0]
        desc_x = (WIDTH - desc_width) // 2

        # Bullet point
        bullet_colors = [PINK, TEAL, YELLOW]
        draw.ellipse([desc_x - 30, desc_y + i * 55 + 10, desc_x - 15, desc_y + i * 55 + 25],
                     fill=bullet_colors[i])
        draw.text((desc_x, desc_y + i * 55), desc, font=font_body, fill=WHITE)

    # Order info section
    order_y = 950

    order_title = "How to Order"
    order_bbox = draw.textbbox((0, 0), order_title, font=font_body_bold)
    order_width = order_bbox[2] - order_bbox[0]
    order_x = (WIDTH - order_width) // 2
    draw.text((order_x, order_y + 20), order_title, font=font_body_bold, fill=YELLOW)

    order_methods = [
        "Local pickup only",
        "Pay with cash",
    ]

    for i, method in enumerate(order_methods):
        method_bbox = draw.textbbox((0, 0), method, font=font_body)
        method_width = method_bbox[2] - method_bbox[0]
        method_x = (WIDTH - method_width) // 2
        draw.text((method_x, order_y + 75 + i * 45), method, font=font_body, fill=CREAM)

    # QR Code section
    qr_y = 1230

    # QR code background
    qr_size = 220
    qr_x = (WIDTH - qr_size) // 2

    # Decorative frame around QR
    frame_padding = 25
    draw.rounded_rectangle(
        [qr_x - frame_padding, qr_y - frame_padding,
         qr_x + qr_size + frame_padding, qr_y + qr_size + frame_padding],
        radius=20, fill=WHITE, outline=PURPLE, width=4
    )

    # Generate and paste QR code
    qr_img = create_qr_code("https://rcarlucci1983.github.io/3doodle-critters", qr_size)
    img.paste(qr_img, (qr_x, qr_y), qr_img if qr_img.mode == 'RGBA' else None)

    # Scan prompt
    scan_text = "Scan to visit our shop!"
    scan_bbox = draw.textbbox((0, 0), scan_text, font=font_body)
    scan_width = scan_bbox[2] - scan_bbox[0]
    scan_x = (WIDTH - scan_width) // 2
    draw.text((scan_x, qr_y + qr_size + 35), scan_text, font=font_body, fill=PINK_LIGHT)

    # Save the flyer
    output_path = os.path.join(SCRIPT_DIR, "3doodle-critters-flyer.png")
    img.save(output_path, "PNG", quality=95)
    print(f"Flyer saved to: {output_path}")

    # Also save as PDF
    pdf_path = os.path.join(SCRIPT_DIR, "3doodle-critters-flyer.pdf")
    img_rgb = img.convert('RGB')
    img_rgb.save(pdf_path, "PDF", resolution=150)
    print(f"PDF saved to: {pdf_path}")

if __name__ == "__main__":
    main()
