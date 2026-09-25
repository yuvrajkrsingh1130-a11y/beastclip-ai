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
        "channel_url": "https://www.youtube.com/@IShowSpeed/streams",
        "credit_tag": "@IShowSpeed",
        "recommended_style": "fire_red",
        "recommended_layout": "split_screen",
        "tags": ["#Shorts", "#IShowSpeed", "#Speed", "#Ronaldo", "#CristianoRonaldo", "#CR7", "#SIUUU", "#Viral", "#Trending", "#FYP", "#Football", "#TwitchClips", "#FunnyMoments", "#SpeedShorts"],
        "featured_videos": [
            {
                "id": "cORnEmFk4JM",
                "title": "iShowSpeed Eats Everything At The One Piece Cafe!",
                "url": "https://www.youtube.com/watch?v=cORnEmFk4JM",
                "thumbnail": "https://i.ytimg.com/vi/cORnEmFk4JM/hqdefault.jpg",
                "duration": "27 mins",
                "badge": "🔥 Viral Food Climax"
            },
            {
                "id": "GfCnZ8cAYvQ",
                "title": "JOIN THIS STREAM, WIN AN IPHONE 18!",
                "url": "https://www.youtube.com/watch?v=GfCnZ8cAYvQ",
                "thumbnail": "https://i.ytimg.com/vi/GfCnZ8cAYvQ/hqdefault.jpg",
                "duration": "3h 50m",
                "badge": "⚡ iPhone 18 Hype Stream"
            },
            {
                "id": "drXRrB4wFRg",
                "title": "BUYING THE NEW iPHONE 18!",
                "url": "https://www.youtube.com/watch?v=drXRrB4wFRg",
                "thumbnail": "https://i.ytimg.com/vi/drXRrB4wFRg/hqdefault.jpg",
                "duration": "2h 48m",
                "badge": "😂 Store Chaos & Rage"
            }
        ]
    },
    "kaicenat": {
        "name": "Kai Cenat",
        "channel_url": "https://www.youtube.com/@KaiCenat/videos",
        "credit_tag": "@KaiCenat",
        "recommended_style": "neon",
        "recommended_layout": "split_screen",
        "tags": ["#Shorts", "#KaiCenat", "#AMP", "#KaiClips", "#Mafiathon", "#Viral", "#Trending", "#FYP", "#Twitch", "#FunnyMoments", "#StreamerClips"],
        "featured_videos": [
            {
                "id": "Dt36OGjw26Y",
                "title": "Don't Quit",
                "url": "https://www.youtube.com/watch?v=Dt36OGjw26Y",
                "thumbnail": "https://i.ytimg.com/vi/Dt36OGjw26Y/hqdefault.jpg",
                "duration": "29 mins",
                "badge": "👑 Top Trending Stream"
            },
            {
                "id": "Hhl74xWssbU",
                "title": "Streamer University LOS ANGELES In Person Applications",
                "url": "https://www.youtube.com/watch?v=Hhl74xWssbU",
                "thumbnail": "https://i.ytimg.com/vi/Hhl74xWssbU/hqdefault.jpg",
                "duration": "43 mins",
                "badge": "😂 Peak Comedy"
            },
            {
                "id": "ACoJ17Pxkfs",
                "title": "Streamer University NEW YORK In Person Applications",
                "url": "https://www.youtube.com/watch?v=ACoJ17Pxkfs",
                "thumbnail": "https://i.ytimg.com/vi/ACoJ17Pxkfs/hqdefault.jpg",
                "duration": "28 mins",
                "badge": "🔥 High Energy NYC"
            }
        ]
    },
    "jynxzi": {
        "name": "Jynxzi",
        "channel_url": "https://www.youtube.com/@Jynxzi/videos",
        "credit_tag": "@Jynxzi",
        "recommended_style": "beast",
        "recommended_layout": "split_screen",
        "tags": ["#Shorts", "#Jynxzi", "#R6", "#RainbowSix", "#JynxziClips", "#JynxziRage", "#Viral", "#Trending", "#Gaming", "#FunnyMoments"],
        "featured_videos": [
            {
                "id": "9md-Dot3D_s",
                "title": "Try Not To Laugh, Viewer Suggested Videos",
                "url": "https://www.youtube.com/watch?v=9md-Dot3D_s",
                "thumbnail": "https://i.ytimg.com/vi/9md-Dot3D_s/hqdefault.jpg",
                "duration": "34 mins",
                "badge": "🎮 Rage & Screams"
            },
            {
                "id": "S8EF5_2ND0A",
                "title": "Your BRUTAL Clips...",
                "url": "https://www.youtube.com/watch?v=S8EF5_2ND0A",
                "thumbnail": "https://i.ytimg.com/vi/S8EF5_2ND0A/hqdefault.jpg",
                "duration": "31 mins",
                "badge": "💀 Instant Reaction"
            }
        ]
    },
    "caseoh": {
        "name": "CaseOh",
        "channel_url": "https://www.youtube.com/@CaseOh_/videos",
        "credit_tag": "@CaseOh",
        "recommended_style": "hormozi",
        "recommended_layout": "split_screen",
        "tags": ["#Shorts", "#CaseOh", "#CaseOhClips", "#CaseOhGames", "#CaseOhRage", "#Viral", "#Trending", "#FYP", "#FunnyMoments", "#TryNotToLaugh"],
        "featured_videos": [
            {
                "id": "B4V68iXJ-kk",
                "title": "Liminal Descent…",
                "url": "https://www.youtube.com/watch?v=B4V68iXJ-kk",
                "thumbnail": "https://i.ytimg.com/vi/B4V68iXJ-kk/hqdefault.jpg",
                "duration": "1h 39m",
                "badge": "🍔 Horror Jumpscares"
            },
            {
                "id": "XYqAx4HhZmU",
                "title": "I Found Another Village… (Skyblock Part 2)",
                "url": "https://www.youtube.com/watch?v=XYqAx4HhZmU",
                "thumbnail": "https://i.ytimg.com/vi/XYqAx4HhZmU/hqdefault.jpg",
                "duration": "1h 17m",
                "badge": "💬 Hilarious Chat Trolling"
            }
        ]
    },
    "generic": {
        "name": "Original Creator",
        "channel_url": "",
        "credit_tag": "Original Creator",
        "recommended_style": "hormozi",
        "recommended_layout": "split_screen",
        "tags": ["#Shorts", "#Viral", "#Trending", "#FYP", "#ForYou", "#ShortsFeed", "#Gaming", "#FunnyMoments", "#TwitchClips", "#Explore"],
        "featured_videos": []
    }
}

