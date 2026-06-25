from PIL import Image, ImageDraw, ImageFont
import os

ASSET_DIR = "photos"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1080, 1350

image_files = [
    "photo1.jpg",
    "photo2.jpg",
    "photo3.jpg",
    "photo4.jpg",
]

texts = [
    "Play is not\nthe opposite of learning.",
    "It's how curiosity begins.",
    "It's how ideas stick.",
    "1 August\nPreston City Hall",
]

def get_font(size):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def crop_cover(img, width, height):
    img = img.convert("RGB")
    iw, ih = img.size
    scale = max(width / iw, height / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - width) // 2
    top = (nh - height) // 2
    return img.crop((left, top, left + width, top + height))

poster = Image.new("RGB", (W, H), "white")
section_h = H // 4
font = get_font(54)

for i, file in enumerate(image_files):
    img = Image.open(os.path.join(ASSET_DIR, file))
    img = crop_cover(img, W, section_h)
    y = i * section_h
    poster.paste(img, (0, y))

    draw = ImageDraw.Draw(poster)
    text = texts[i]

    x = 55
    ty = y + section_h - 150

    draw.text(
        (x, ty),
        text,
        font=font,
        fill="white",
        stroke_width=6,
        stroke_fill="black",
    )

    if i > 0:
        draw.line((0, y, W, y), fill="white", width=8)

poster.save("output/lgp_poster.png")
