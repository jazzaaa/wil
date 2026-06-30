from PIL import Image, ImageOps
import numpy as np
import imageio.v2 as imageio
import os

POSTER = "poster.png"
OUTPUT = "Poster_Video_Output.mp4"

W, H = 1080, 1920
FPS = 30
DURATION = 12
ZOOM = 0.06

if not os.path.exists(POSTER):
    raise FileNotFoundError("Please upload your poster as poster.png in the repo root.")

poster = Image.open(POSTER).convert("RGB")
poster = ImageOps.fit(poster, (W, H), method=Image.Resampling.LANCZOS)

total_frames = FPS * DURATION

writer = imageio.get_writer(
    OUTPUT,
    fps=FPS,
    codec="libx264",
    macro_block_size=None,
    ffmpeg_params=["-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20"],
)

try:
    for i in range(total_frames):
        progress = i / max(1, total_frames - 1)

        zoom = 1 + ZOOM * progress
        new_w = int(W * zoom)
        new_h = int(H * zoom)

        frame = poster.resize((new_w, new_h), Image.Resampling.LANCZOS)

        left = (new_w - W) // 2
        top = int((new_h - H) * progress)

        frame = frame.crop((left, top, left + W, top + H))

        writer.append_data(np.array(frame))

finally:
    writer.close()

print(f"Saved: {OUTPUT}")
