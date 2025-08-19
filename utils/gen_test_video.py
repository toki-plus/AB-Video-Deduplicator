import os
import cv2
from PIL import Image, ImageDraw, ImageFont

DURATION = 10
FPS = 30
TOTAL_FRAMES = DURATION * FPS
WIDTH, HEIGHT = 1080, 1920
FONT_SIZE = 200
FONT_COLOR = (0, 0, 0)
BG_COLOR = (255, 255, 255)
VIDEO_PATH = "30-w.mp4"

os.makedirs("frames", exist_ok=True)

for i in range(TOTAL_FRAMES):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", FONT_SIZE)
    text = str(i)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (WIDTH - text_width) / 2
    y = (HEIGHT - text_height) / 2
    draw.text((x, y), text, font=font, fill=FONT_COLOR)
    img.save(f"frames/frame_{i:04d}.png")

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
video = cv2.VideoWriter(VIDEO_PATH, fourcc, FPS, (WIDTH, HEIGHT))

for i in range(TOTAL_FRAMES):
    img = cv2.imread(f"frames/frame_{i:04d}.png")
    video.write(img)

video.release()

for i in range(TOTAL_FRAMES):
    os.remove(f"frames/frame_{i:04d}.png")
os.rmdir("frames")

print(f"视频已保存为 {VIDEO_PATH}")
