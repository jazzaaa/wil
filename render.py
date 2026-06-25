#!/usr/bin/env python3
import os, json
from PIL import Image, ImageOps, ImageDraw, ImageFont
import numpy as np
import imageio.v2 as imageio

WIDTH = 1080
HEIGHT = 1920
FPS = 30
SECONDS_PER_PHOTO = 3.2
ZOOM_AMOUNT = 0.06
OUTPUT = "LGP_Reel_Output.mp4"

IMAGE_FILES = [
    "photos/photo1.jpg",
    "photos/photo2.jpg",
    "photos/photo3.jpg",
    "photos/photo4.jpg",
]

with open("texts.json", "r", encoding="utf-8") as f:
    TEXTS = json.load(f)

TEXT_POSITIONS = [
    (80, 1120),
    (80, 1120),
    (80, 1120),
    (80, 860),
]

FONT_SIZE = [78, 72, 78, 58]
TEXT_BOX_WIDTH = [850, 850, 850, 860]

def find_font():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

FONT_PATH = find_font()

def load_font(size):
    if FONT_PATH:
        return ImageFont.truetype(FONT_PATH, size)
    return ImageFont.load_default()

def wrap_text(text, font, max_width):
    draw = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    lines = []
    for paragraph in text.split("\n"):
        if paragraph.strip() == "":
            lines.append("")
            continue
        words = paragraph.split()
        current = ""
        for word in words:
            test = word if not current else current + " " + word
            bbox = draw.textbbox((0, 0), test, font=font, stroke_width=5)
            if bbox[2] - bbox[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines

def draw_text(img, text, position, font_size, box_width):
    draw = ImageDraw.Draw(img)
    font = load_font(font_size)
    lines = wrap_text(text, font, box_width)
    x, y = position
    line_gap = int(font_size * 0.35)

    for line in lines:
        if line == "":
            y += int(font_size * 0.75)
            continue
        draw.text((x, y), line, font=font, fill="white", stroke_width=5, stroke_fill="black")
        bbox = draw.textbbox((x, y), line, font=font, stroke_width=5)
        y += (bbox[3] - bbox[1]) + line_gap
    return img

def prepare_image(path):
    img = Image.open(path).convert("RGB")
    return ImageOps.fit(img, (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)

def ken_burns(base_img, progress):
    zoom = 1 + ZOOM_AMOUNT * progress
    new_w = int(WIDTH * zoom)
    new_h = int(HEIGHT * zoom)
    zoomed = base_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - WIDTH) // 2
    top = (new_h - HEIGHT) // 2
    return zoomed.crop((left, top, left + WIDTH, top + HEIGHT))

missing = [p for p in IMAGE_FILES if not os.path.exists(p)]
if missing:
    raise FileNotFoundError("Missing images: " + ", ".join(missing))

frames_per_photo = int(SECONDS_PER_PHOTO * FPS)

writer = imageio.get_writer(
    OUTPUT,
    fps=FPS,
    codec="libx264",
    quality=8,
    macro_block_size=None,
    ffmpeg_params=["-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20"]
)

try:
    for i, img_path in enumerate(IMAGE_FILES):
        print(f"Rendering {img_path}")
        base = prepare_image(img_path)

        for frame_index in range(frames_per_photo):
            progress = frame_index / max(1, frames_per_photo - 1)
            frame = ken_burns(base, progress)
            frame = draw_text(
                frame,
                TEXTS[i],
                TEXT_POSITIONS[i],
                FONT_SIZE[i],
                TEXT_BOX_WIDTH[i],
            )
            writer.append_data(np.array(frame))
finally:
    writer.close()

print(f"Done: {OUTPUT}")
