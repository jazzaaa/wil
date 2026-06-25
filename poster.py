from PIL import Image, ImageOps, ImageDraw, ImageFont
import os

W, H = 1080, 1920
PANEL_H = H // 4
OUTPUT = "LGP_Poster_Output.png"

PHOTOS = [
    "photos/photo1.jpg",
    "photos/photo2.jpg",
    "photos/photo3.jpg",
    "photos/photo4.jpg",
]

TEXTS = [
    "If you're\na teacher\nlooking for\nsomething",
    "that actually\nworks in\nthe classroom,",
    "come and\nplay it\nfirst.",
    "1 AUGUST\nPRESTON CITY HALL",
]

POSITIONS = [
    (55, 95),
    (55, 105),
    (55, 90),
    ("center", 250),
]

FONT_SIZES = [62, 62, 62, 58]

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

poster = Image.new("RGB", (W, H), "white")
draw = ImageDraw.Draw(poster)

for i, path in enumerate(PHOTOS):
    img = Image.open(path).convert("RGB")
    img = ImageOps.fit(img, (W, PANEL_H), method=Image.Resampling.LANCZOS)
    y = i * PANEL_H
    poster.paste(img, (0, y))

    # divider
    if i > 0:
        draw.rectangle((0, y - 6, W, y + 6), fill="white")

    f = font(FONT_SIZES[i])
    text = TEXTS[i]
    x_pos, y_pos = POSITIONS[i]

    lines = text.split("\n")
    line_gap = int(FONT_SIZES[i] * 0.2)

    total_h = 0
    widths = []
    heights = []

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=f, stroke_width=4)
        widths.append(bbox[2] - bbox[0])
        heights.append(bbox[3] - bbox[1])
        total_h += bbox[3] - bbox[1] + line_gap

    total_h -= line_gap

    if x_pos == "center":
        start_y = y + y_pos
        for line, lw, lh in zip(lines, widths, heights):
            x = (W - lw) // 2
            draw.text(
                (x, start_y),
                line,
                font=f,
                fill="white",
                stroke_width=5,
                stroke_fill="black",
            )
            start_y += lh + line_gap
    else:
        start_y = y + y_pos
        for line, lh in zip(lines, heights):
            draw.text(
                (x_pos, start_y),
                line,
                font=f,
                fill="white",
                stroke_width=5,
                stroke_fill="black",
            )
            start_y += lh + line_gap

poster.save(OUTPUT, quality=95)
print(f"Saved: {OUTPUT}")
