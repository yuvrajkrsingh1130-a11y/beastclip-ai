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
            },
            {
                "id": "dV0OgeSbYPM",
                "title": "I GOT FC27 EARLY!",
                "url": "https://www.youtube.com/watch?v=dV0OgeSbYPM",
                "thumbnail": "https://i.ytimg.com/vi/dV0OgeSbYPM/hqdefault.jpg",
                "duration": "3h 27m",
                "badge": "⚽ FC 27 Early Access"
            },
            {
                "id": "WwZx1LvNwas",
                "title": "LIT STREAM + IRL OHIO STATE VS TEXAS",
                "url": "https://www.youtube.com/watch?v=WwZx1LvNwas",
                "thumbnail": "https://i.ytimg.com/vi/WwZx1LvNwas/hqdefault.jpg",
                "duration": "1h 51m",
                "badge": "🏈 IRL College Football"
            },
            {
                "id": "5CPAtEmHAio",
                "title": "REVEALING THE NEW iPHONE!",
                "url": "https://www.youtube.com/watch?v=5CPAtEmHAio",
                "thumbnail": "https://i.ytimg.com/vi/5CPAtEmHAio/hqdefault.jpg",
                "duration": "2h 08m",
                "badge": "📱 New iPhone Reveal"
            },
            {
                "id": "4zVFht1KbnY",
                "title": "WORLD TALENT SHOW",
                "url": "https://www.youtube.com/watch?v=4zVFht1KbnY",
                "thumbnail": "https://i.ytimg.com/vi/4zVFht1KbnY/hqdefault.jpg",
                "duration": "3h 13m",
                "badge": "🎤 World Talent Show"
            },
            {
                "id": "glOhY5hiOwI",
                "title": "JOIN THIS STREM MESSI RETIRED",
                "url": "https://www.youtube.com/watch?v=glOhY5hiOwI",
                "thumbnail": "https://i.ytimg.com/vi/glOhY5hiOwI/hqdefault.jpg",
                "duration": "3h 08m",
                "badge": "🐐 Messi Retirement Stream"
            },
            {
                "id": "gYzuuGvuvyE",
                "title": "Minecraft, But Chat Controls My Game..",
                "url": "https://www.youtube.com/watch?v=gYzuuGvuvyE",
                "thumbnail": "https://i.ytimg.com/vi/gYzuuGvuvyE/hqdefault.jpg",
                "duration": "1h 12m",
                "badge": "⛏️ Chat Controls Minecraft"
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
            },
            {
                "id": "XHtCaYLWpI0",
                "title": "I Visited Unexplored Places In Iceland",
                "url": "https://www.youtube.com/watch?v=XHtCaYLWpI0",
                "thumbnail": "https://i.ytimg.com/vi/XHtCaYLWpI0/hqdefault.jpg",
                "duration": "1h 01m",
                "badge": "🇮🇸 Iceland Exploration"
            },
            {
                "id": "T0rA72MDRYM",
                "title": "I Hosted The Biggest Streamer Among Us Lobby...",
                "url": "https://www.youtube.com/watch?v=T0rA72MDRYM",
                "thumbnail": "https://i.ytimg.com/vi/T0rA72MDRYM/hqdefault.jpg",
                "duration": "1h 22m",
                "badge": "🚀 Among Us Mega Lobby"
            },
            {
                "id": "JheRzFxeSBg",
                "title": "Blind, Deaf, Mute Challenge With Tota & Ray!",
                "url": "https://www.youtube.com/watch?v=JheRzFxeSBg",
                "thumbnail": "https://i.ytimg.com/vi/JheRzFxeSBg/hqdefault.jpg",
                "duration": "38 mins",
                "badge": "🙈 Blind Deaf Mute Challenge"
            },
            {
                "id": "C47hqdcI-aE",
                "title": "STREAMER LAST TO FALL ASLEEP CHALLENGE",
                "url": "https://www.youtube.com/watch?v=C47hqdcI-aE",
                "thumbnail": "https://i.ytimg.com/vi/C47hqdcI-aE/hqdefault.jpg",
                "duration": "1h 47m",
                "badge": "😴 Sleep Challenge"
            },
            {
                "id": "dpwDrZJGa4M",
                "title": "Kai Cenat & Rakai Become SUPERHEROS...",
                "url": "https://www.youtube.com/watch?v=dpwDrZJGa4M",
                "thumbnail": "https://i.ytimg.com/vi/dpwDrZJGa4M/hqdefault.jpg",
                "duration": "41 mins",
                "badge": "🦸 Kai Superhero Stream"
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
                "id": "S8EF5_2ND0A",
                "title": "Your BRUTAL Clips...",
                "url": "https://www.youtube.com/watch?v=S8EF5_2ND0A",
                "thumbnail": "https://i.ytimg.com/vi/S8EF5_2ND0A/hqdefault.jpg",
                "duration": "31 mins",
                "badge": "💀 Brutal Clips"
            },
            {
                "id": "FDXpzsK0KI4",
                "title": "YOU vs The RANK You Deserve (Rainbow Six Siege)",
                "url": "https://www.youtube.com/watch?v=FDXpzsK0KI4",
                "thumbnail": "https://i.ytimg.com/vi/FDXpzsK0KI4/hqdefault.jpg",
                "duration": "21 mins",
                "badge": "🎮 Deserved Rank"
            },
            {
                "id": "YxxEwpsEwSE",
                "title": "Im Ending Fan Mail...",
                "url": "https://www.youtube.com/watch?v=YxxEwpsEwSE",
                "thumbnail": "https://i.ytimg.com/vi/YxxEwpsEwSE/hqdefault.jpg",
                "duration": "1h 09m",
                "badge": "📦 Fan Mail Madness"
            },
            {
                "id": "BiyIjaqeMh0",
                "title": "Your ABSURD Clips...",
                "url": "https://www.youtube.com/watch?v=BiyIjaqeMh0",
                "thumbnail": "https://i.ytimg.com/vi/BiyIjaqeMh0/hqdefault.jpg",
                "duration": "34 mins",
                "badge": "🤯 Absurd Clips Reaction"
            },
            {
                "id": "o4nlI5ekJYA",
                "title": "Bernard Picks My DECK in Clash Royale",
                "url": "https://www.youtube.com/watch?v=o4nlI5ekJYA",
                "thumbnail": "https://i.ytimg.com/vi/o4nlI5ekJYA/hqdefault.jpg",
                "duration": "52 mins",
                "badge": "👑 Clash Royale Challenge"
            },
            {
                "id": "oF9Tm4LXm3o",
                "title": "3v3 MODE IS HERE (Rainbow Six Siege)",
                "url": "https://www.youtube.com/watch?v=oF9Tm4LXm3o",
                "thumbnail": "https://i.ytimg.com/vi/oF9Tm4LXm3o/hqdefault.jpg",
                "duration": "48 mins",
                "badge": "⚡ 3v3 Siege Mode"
            },
            {
                "id": "MZp4oWnDLII",
                "title": "Trying My Viewers Clash Royale Decks Returns!",
                "url": "https://www.youtube.com/watch?v=MZp4oWnDLII",
                "thumbnail": "https://i.ytimg.com/vi/MZp4oWnDLII/hqdefault.jpg",
                "duration": "42 mins",
                "badge": "🏆 Viewer Decks"
            },
            {
                "id": "ZqFcwTMfIOk",
                "title": "Your SHOCKING Clips...",
                "url": "https://www.youtube.com/watch?v=ZqFcwTMfIOk",
                "thumbnail": "https://i.ytimg.com/vi/ZqFcwTMfIOk/hqdefault.jpg",
                "duration": "35 mins",
                "badge": "😱 Shocking Clips"
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
                "id": "r8MV_JBLEpY",
                "title": "The Fail Rooms",
                "url": "https://www.youtube.com/watch?v=r8MV_JBLEpY",
                "thumbnail": "https://i.ytimg.com/vi/r8MV_JBLEpY/hqdefault.jpg",
                "duration": "1h 21m",
                "badge": "🚪 Fail Rooms Horror"
            },
            {
                "id": "0BpKgtVzP0M",
                "title": "This Familys House Is Terrifying",
                "url": "https://www.youtube.com/watch?v=0BpKgtVzP0M",
                "thumbnail": "https://i.ytimg.com/vi/0BpKgtVzP0M/hqdefault.jpg",
                "duration": "1h 12m",
                "badge": "👻 Terrifying House"
            },
            {
                "id": "B4V68iXJ-kk",
                "title": "Liminal Descent",
                "url": "https://www.youtube.com/watch?v=B4V68iXJ-kk",
                "thumbnail": "https://i.ytimg.com/vi/B4V68iXJ-kk/hqdefault.jpg",
                "duration": "1h 39m",
                "badge": "🍔 Horror Jumpscares"
            },
            {
                "id": "XYqAx4HhZmU",
                "title": "I Found Another Village (Skyblock Part 2)",
                "url": "https://www.youtube.com/watch?v=XYqAx4HhZmU",
                "thumbnail": "https://i.ytimg.com/vi/XYqAx4HhZmU/hqdefault.jpg",
                "duration": "1h 17m",
                "badge": "💬 Hilarious Chat Trolling"
            },
            {
                "id": "lXDm6pFCDb0",
                "title": "I Played Happy Wheels Again",
                "url": "https://www.youtube.com/watch?v=lXDm6pFCDb0",
                "thumbnail": "https://i.ytimg.com/vi/lXDm6pFCDb0/hqdefault.jpg",
                "duration": "2h 05m",
                "badge": "🚲 Happy Wheels Rage"
            },
            {
                "id": "_fH6AZrDoHE",
                "title": "One Of The Best Horror Games This Year (The Plant Shop)",
                "url": "https://www.youtube.com/watch?v=_fH6AZrDoHE",
                "thumbnail": "https://i.ytimg.com/vi/_fH6AZrDoHE/hqdefault.jpg",
                "duration": "1h 43m",
                "badge": "🪴 The Plant Shop Horror"
            },
            {
                "id": "R1nvpbZcuN4",
                "title": "The Family Business",
                "url": "https://www.youtube.com/watch?v=R1nvpbZcuN4",
                "thumbnail": "https://i.ytimg.com/vi/R1nvpbZcuN4/hqdefault.jpg",
                "duration": "46 mins",
                "badge": "🔪 The Family Business"
            },
            {
                "id": "lFZARtBDbRQ",
                "title": "I Played Minecraft Skyblock",
                "url": "https://www.youtube.com/watch?v=lFZARtBDbRQ",
                "thumbnail": "https://i.ytimg.com/vi/lFZARtBDbRQ/hqdefault.jpg",
                "duration": "1h 57m",
                "badge": "⛏️ Minecraft Skyblock"
            },
            {
                "id": "DQwj__k_u5A",
                "title": "I Played The Backrooms Minecraft Mod",
                "url": "https://www.youtube.com/watch?v=DQwj__k_u5A",
                "thumbnail": "https://i.ytimg.com/vi/DQwj__k_u5A/hqdefault.jpg",
                "duration": "58 mins",
                "badge": "🟡 Backrooms Mod"
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

