import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

class ThumbnailMaker:
    def __init__(self):
        pass

    def extract_best_frame(self, video_path: str, start_time: float, duration: float) -> np.ndarray:
        """Extracts frame near the peak reaction timestamp."""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        # Pick frame around 30% into the clip (usually peak expression)
        target_time = start_time + (duration * 0.3)
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(target_time * fps))
        ret, frame = cap.read()
        cap.release()
        return frame if ret else None

    def generate_vertical_thumbnail(self, frame: np.ndarray, hook_title: str, output_path: str):
        """Creates a viral 1080x1920 vertical thumbnail with bold text banner."""
        if frame is None:
            # Create fallback blank image
            img = Image.new("RGB", (1080, 1920), color=(20, 20, 30))
        else:
            # Crop/Scale to 1080x1920
            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_frame = Image.fromarray(rgb_frame)

            target_ratio = 9.0 / 16.0
            current_ratio = w / float(h)

            if current_ratio > target_ratio:
                # Video is wide (16:9)
                crop_w = int(h * target_ratio)
                start_x = (w - crop_w) // 2
                pil_frame = pil_frame.crop((start_x, 0, start_x + crop_w, h))
            else:
                crop_h = int(w / target_ratio)
                start_y = (h - crop_h) // 2
                pil_frame = pil_frame.crop((0, start_y, w, start_y + crop_h))

            img = pil_frame.resize((1080, 1920), Image.Resampling.LANCZOS)

        draw = ImageDraw.Draw(img)

        # Draw semi-transparent gradient overlays on top & bottom
        overlay = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([(0, 0), (1080, 400)], fill=(0, 0, 0, 140))
        overlay_draw.rectangle([(0, 1500), (1080, 1920)], fill=(0, 0, 0, 160))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)

        # Draw bold hook text banner
        try:
            font = ImageFont.truetype("arialbd.ttf", 64)
            small_font = ImageFont.truetype("arialbd.ttf", 40)
        except Exception:
            font = ImageFont.load_default()
            small_font = font

        # Header Badge
        draw.rounded_rectangle([(100, 120), (980, 240)], radius=20, fill=(255, 0, 80))
        draw.text((540, 180), "VIRAL MOMENT 🔥", font=font, fill=(255, 255, 255), anchor="mm")

        # Bottom Call to Action
        draw.rounded_rectangle([(140, 1650), (940, 1770)], radius=25, fill=(255, 215, 0))
        draw.text((540, 1710), "WATCH TILL THE END 💀", font=small_font, fill=(0, 0, 0), anchor="mm")

        img.save(output_path, "JPEG", quality=95)
        return output_path
