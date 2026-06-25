from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, concatenate_videoclips
import os
import numpy as np

ASSET_DIR = "assets"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30

photos = [
    {
        "file": "photo1.jpg",
        "text": "Play is not\nthe opposite\nof learning.",
        "duration": 3.5,
    },
    {
        "file": "photo2.jpg",
        "text": "It's how\ncuriosity\nbegins.",
        "duration": 3.5,
    },
    {
        "file": "photo3.jpg",
        "text": "It's how\nideas\nstick.",
        "duration": 3.5,
    },
    {
        "file": "photo4.png",
        "text": "Come and discover\ngames that belong\nin classrooms.\n\n1 August\nPreston City Hall",
        "duration": 4.5,
    },
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

def fit_cover(img):
    img = img.convert("RGB")
    iw, ih = img.size
    scale = max(W / iw, H / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return img.crop((left, top, left + W, top + H))

def add_text(img, text):
    draw = ImageDraw.Draw(img)
    font = get_font(76)

    lines = text.split("\n")
    line_h = 88
    total_h = len(lines) * line_h

    x = 70
    y = H - total_h - 180

    for line in lines:
        if line.strip() == "":
            y += line_h // 2
            continue

        # black stroke
        draw.text((x, y), line, font=font, fill="white", stroke_width=7, stroke_fill="black")
        y += line_h

    return img

def make_frame(path, text):
    img = Image.open(path)
    img = fit_cover(img)
    img = add_text(img, text)
    return np.array(img)

clips = []

for item in photos:
    path = os.path.join(ASSET_DIR, item["file"])
    frame = make_frame(path, item["text"])

    clip = ImageClip(frame).set_duration(item["duration"])

    # slow Ken Burns zoom
    clip = clip.resize(lambda t: 1 + 0.045 * t)

    clip = clip.fadein(0.25).fadeout(0.25)
    clips.append(clip)

video = concatenate_videoclips(clips, method="compose", padding=-0.25)
video.write_videofile(
    "output/lgp_video.mp4",
    fps=FPS,
    codec="libx264",
    audio=False,
    preset="medium",
    bitrate="6000k",
)
