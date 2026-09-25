import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"
FONTS_DIR = BASE_DIR / "fonts"
STATIC_DIR = BASE_DIR / "static"

# Ensure dirs exist
for d in [OUTPUT_DIR, TEMP_DIR, FONTS_DIR, STATIC_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Default Server Settings
HOST = "127.0.0.1"
PORT = 8000

# Video Settings
DEFAULT_VERTICAL_WIDTH = 1080
DEFAULT_VERTICAL_HEIGHT = 1920
DEFAULT_FPS = 30

# Subtitle Styling Presets (Creator Styles)
SUBTITLE_PRESETS = {
    "hormozi": {
        "name": "Hormozi Gold",
        "fontname": "Arial Black",
        "fontsize": 24,
        "primary_color": "&H00FFFFFF&",      # Crisp White
        "highlight_color": "&H0000FFFF&",    # Hormozi Golden Yellow (Pop Yellow)
        "outline_color": "&H00000000&",      # Deep Black Outline
        "outline_width": 4.0,
        "shadow_width": 2.5,
        "bold": True,
        "all_caps": True,
        "emojis": True,
        "animation": "pop"
    },
    "beast": {
        "name": "MrBeast Green",
        "fontname": "Arial Black",
        "fontsize": 25,
        "primary_color": "&H00FFFFFF&",      # Crisp White
        "highlight_color": "&H0022FF33&",    # Electric Neon Green
        "outline_color": "&H00000000&",      # Thick Black Outline
        "outline_width": 4.2,
        "shadow_width": 2.5,
        "bold": True,
        "all_caps": True,
        "emojis": True,
        "animation": "bounce"
    },
    "neon": {
        "name": "Kai Cenat Neon",
        "fontname": "Arial Black",
        "fontsize": 24,
        "primary_color": "&H00FFFFFF&",
        "highlight_color": "&H00FFFF00&",    # Cyber Cyan
        "outline_color": "&H00000000&",
        "outline_width": 4.0,
        "shadow_width": 2.5,
        "bold": True,
        "all_caps": True,
        "emojis": True,
        "animation": "tilt"
    },
    "fire_red": {
        "name": "Speed Fire & Rage",
        "fontname": "Arial Black",
        "fontsize": 26,
        "primary_color": "&H00FFFFFF&",
        "highlight_color": "&H000033FF&",    # Fiery Red / Orange Flame
        "outline_color": "&H00000000&",
        "outline_width": 4.5,
        "shadow_width": 2.8,
        "bold": True,
        "all_caps": True,
        "emojis": True,
        "animation": "shake"
    },
    "clean_pill": {
        "name": "Minimalist Pill",
        "fontname": "Arial Black",
        "fontsize": 22,
        "primary_color": "&H00FFFFFF&",
        "highlight_color": "&H0033CCFF&",    # Warm Amber
        "outline_color": "&H00151515&",
        "outline_width": 3.0,
        "shadow_width": 1.5,
        "bold": True,
        "all_caps": False,
        "emojis": True,
        "animation": "smooth"
    },
    "glitch_purple": {
        "name": "Twitch Purple",
        "fontname": "Arial Black",
        "fontsize": 24,
        "primary_color": "&H00FFFFFF&",
        "highlight_color": "&H00FF33CC&",    # Vivid Violet/Purple
        "outline_color": "&H00000000&",
        "outline_width": 4.0,
        "shadow_width": 2.5,
        "bold": True,
        "all_caps": True,
        "emojis": True,
        "animation": "pop"
    },
    "cyber_glitch": {
        "name": "Cyberpunk Neon",
        "fontname": "Arial Black",
        "fontsize": 24,
        "primary_color": "&H00FFFFFF&",
        "highlight_color": "&H00FF0099&",    # Hot Pink
        "outline_color": "&H00000000&",
        "outline_width": 4.0,
        "shadow_width": 2.5,
        "bold": True,
        "all_caps": True,
        "emojis": True,
        "animation": "glitch"
    },
    "shonen_gold": {
        "name": "Anime Super Saiyan",
        "fontname": "Arial Black",
        "fontsize": 26,
        "primary_color": "&H00FFFFFF&",
        "highlight_color": "&H0000E5FF&",    # Super Saiyan Gold
        "outline_color": "&H00000000&",
        "outline_width": 4.5,
        "shadow_width": 2.8,
        "bold": True,
        "all_caps": True,
        "emojis": True,
        "animation": "power"
    }
}

# Popular Streamer Attribution Presets
CREATOR_PRESETS = {
    "ishowspeed": {
        "name": "IShowSpeed",
        "channel_url": "https://www.youtube.com/@IShowSpeed",
        "credit_tag": "@IShowSpeed",
        "tags": ["#ishowspeed", "#speed", "#speedshorts", "#gaming", "#funny", "#streamer"]
    },
    "kaicenat": {
        "name": "Kai Cenat",
        "channel_url": "https://www.youtube.com/@KaiCenat",
        "credit_tag": "@KaiCenat",
        "tags": ["#kaicenat", "#amp", "#kaiclips", "#streamer", "#twitch", "#funny"]
    },
    "jynxzi": {
        "name": "Jynxzi",
        "channel_url": "https://www.youtube.com/@Jynxzi",
        "credit_tag": "@Jynxzi",
        "tags": ["#jynxzi", "#r6", "#rainbowsix", "#jynxziclips", "#rage", "#gaming"]
    },
    "caseoh": {
        "name": "CaseOh",
        "channel_url": "https://www.youtube.com/@CaseOh",
        "credit_tag": "@CaseOh",
        "tags": ["#caseoh", "#caseohclips", "#caseohgames", "#twitch", "#funny", "#rage"]
    },
    "generic": {
        "name": "Original Creator",
        "channel_url": "",
        "credit_tag": "Original Creator",
        "tags": ["#shorts", "#viral", "#gaming", "#trending", "#fyp", "#funny"]
    }
}
