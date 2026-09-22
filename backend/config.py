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
        "fontsize": 26,
        "primary_color": "&H00FFFFFF",      # Crisp White (BGR)
        "highlight_color": "&H0000FFFF",    # Hormozi Golden Yellow (BGR: B=00, G=FF, R=FF)
        "outline_color": "&H00000000",      # Deep Black Outline
        "outline_width": 4.5,
        "shadow_width": 3.0,
        "bold": True,
        "all_caps": True,
        "emojis": True,
        "animation": "pop"
    },
    "beast": {
        "name": "MrBeast Green",
        "fontname": "Impact",
        "fontsize": 28,
        "primary_color": "&H00FFFFFF",      # Crisp White
        "highlight_color": "&H0022FF33",    # Electric Beast Neon Green (BGR: B=22, G=FF, R=33)
        "outline_color": "&H00000000",      # Thick Outline
        "outline_width": 5.0,
        "shadow_width": 3.5,
        "bold": True,
        "all_caps": True,
        "emojis": True,
        "animation": "bounce"
    },
    "neon": {
        "name": "Kai Cenat Neon",
        "fontname": "Arial Black",
        "fontsize": 26,
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H00FFFF00",    # Cyber Cyan (BGR: B=FF, G=FF, R=00)
        "outline_color": "&H004B0082",      # Indigo Glow
        "outline_width": 4.5,
        "shadow_width": 3.0,
        "bold": True,
        "all_caps": True,
        "emojis": True,
        "animation": "tilt"
    },
    "fire_red": {
        "name": "Speed Fire & Rage",
        "fontname": "Impact",
        "fontsize": 30,
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H000033FF",    # Flaming Fire Orange/Red (BGR: B=00, G=33, R=FF)
        "outline_color": "&H00000000",
        "outline_width": 5.2,
        "shadow_width": 3.5,
        "bold": True,
        "all_caps": True,
        "emojis": True,
        "animation": "shake"
    },
    "clean_pill": {
        "name": "Minimalist Pill",
        "fontname": "Arial Black",
        "fontsize": 24,
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H0033CCFF",    # Warm Amber (BGR: B=33, G=CC, R=FF)
        "outline_color": "&H00151515",
        "outline_width": 3.5,
        "shadow_width": 2.0,
        "bold": True,
        "all_caps": False,
        "emojis": True,
        "animation": "smooth"
    },
    "glitch_purple": {
        "name": "Twitch Purple",
        "fontname": "Arial Black",
        "fontsize": 27,
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H00FF33CC",    # Vivid Violet/Purple (BGR: B=FF, G=33, R=CC)
        "outline_color": "&H00000000",
        "outline_width": 4.5,
        "shadow_width": 3.0,
        "bold": True,
        "all_caps": True,
        "emojis": True,
        "animation": "pop"
    },
    "cyber_glitch": {
        "name": "Cyberpunk Neon",
        "fontname": "Arial Black",
        "fontsize": 26,
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H00FF0099",    # Electric Hot Pink (BGR: B=FF, G=00, R=99)
        "outline_color": "&H00FFFF00",      # Cyan Glow Stroke (BGR: B=FF, G=FF, R=00)
        "outline_width": 4.5,
        "shadow_width": 3.2,
        "bold": True,
        "all_caps": True,
        "emojis": True,
        "animation": "glitch"
    },
    "shonen_gold": {
        "name": "Anime Super Saiyan",
        "fontname": "Impact",
        "fontsize": 30,
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H0000E5FF",    # Bright Golden Glow (BGR: B=00, G=E5, R=FF)
        "outline_color": "&H000000FF",      # Flaming Red Stroke (BGR: B=00, G=00, R=FF)
        "outline_width": 5.5,
        "shadow_width": 3.8,
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
