from PIL import Image, ImageOps, ImageDraw, ImageFont
import os
import json

W, H = 1080, 1920
PANEL_H = H // 4
OUTPUT = "LGP_Poster_Output.png"

PHOTOS = [
    "photos/photo1.jpg",
    "photos/photo2.jpg",
    "photos/photo3.jpg",
    "photos/photo4.jpg",
]

with open("texts.json", "r", encoding="utf-8") as f:
    TEXTS = json.load(f)

if len(TEXTS) != 4:
    raise ValueError("texts.json must contain exactly 4 text items.")

POSITIONS = [
    (55, 95),
    (55, 105),
    (55, 90),
    ("center", 170),
]

FONT_SIZES = [62, 62, 62, 56]

def font(size):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def wrap_text(text, f, max_width, draw):
    lines = []

    for paragraph in text.split("\n"):
        if paragraph.strip() == "":
            lines.append("")
            continue

        words = paragraph.split()
        current = ""

        for word in words:
            test = word if not current else current + " " + word
            bbox = draw.textbbox((0, 0), test, font=f, stroke_width=5)

            if bbox[2] - bbox[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word

        if current:
            lines.append(current)

    return lines

def fit_text(text, start_size, max_width, max_height, draw):
    size = start_size

    while size >= 30:
        f = font(size)
        lines = wrap_text(text, f, max_width, draw)
        line_gap = int(size * 0.25)

        total_h = 0
        max_w = 0

        for line in lines:
            if line == "":
                total_h += int(size * 0.65)
                continue

            bbox = draw.textbbox((0, 0), line, font=f, stroke_width=5)
            max_w = max(max_w, bbox[2] - bbox[0])
            total_h += (bbox[3] - bbox[1]) + line_gap

        if total_h <= max_height and max_w <= max_width:
            return f, lines, line_gap

        size -= 2

    f = font(30)
    return f, wrap_text(text, f, max_width, draw), 8

poster = Image.new("RGB", (W, H), "white")
draw = ImageDraw.Draw(poster)

for i, path in enumerate(PHOTOS):
    img = Image.open(path).convert("RGB")
    img = ImageOps.fit(img, (W, PANEL_H), method=Image.Resampling.LANCZOS)

    y = i * PANEL_H
    poster.paste(img, (0, y))

    if i > 0:
        draw.rectangle((0, y - 6, W, y + 6), fill="white")

    text = TEXTS[i]
    x_pos, y_pos = POSITIONS[i]

    max_text_width = 940
    max_text_height = PANEL_H - 120

    f, lines, line_gap = fit_text(
        text,
        FONT_SIZES[i],
        max_text_width,
        max_text_height,
        draw
    )

    start_y = y + y_pos

    for line in lines:
        if line == "":
            start_y += int(f.size * 0.65)
            continue

        bbox = draw.textbbox((0, 0), line, font=f, stroke_width=5)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]

        if x_pos == "center":
            x = (W - line_w) // 2
        else:
            x = x_pos

        draw.text(
            (x, start_y),
            line,
            font=f,
            fill="white",
            stroke_width=5,
            stroke_fill="black",
        )

        start_y += line_h + line_gap

poster.save(OUTPUT, quality=95)
print(f"Saved: {OUTPUT}")
