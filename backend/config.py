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
            },
            {
                "id": "9OhywUe7FzE",
                "title": "iShowSpeed Meets Cristiano Ronaldo In Real Life!",
                "url": "https://www.youtube.com/watch?v=9OhywUe7FzE",
                "thumbnail": "https://i.ytimg.com/vi/9OhywUe7FzE/hqdefault.jpg",
                "duration": "35 mins",
                "badge": "🐐 The Historic Meeting"
            },
            {
                "id": "mQeK6g9jZpk",
                "title": "iShowSpeed IRL Stream In South Korea!",
                "url": "https://www.youtube.com/watch?v=mQeK6g9jZpk",
                "thumbnail": "https://i.ytimg.com/vi/mQeK6g9jZpk/hqdefault.jpg",
                "duration": "4h 12m",
                "badge": "🇰🇷 Seoul Fan Mania"
            },
            {
                "id": "f3j_tF0WbZs",
                "title": "iShowSpeed Plays Five Nights At Freddy's Security Breach",
                "url": "https://www.youtube.com/watch?v=f3j_tF0WbZs",
                "thumbnail": "https://i.ytimg.com/vi/f3j_tF0WbZs/hqdefault.jpg",
                "duration": "2h 21m",
                "badge": "😱 Pure Terror Jumpscares"
            },
            {
                "id": "X7c5l-uIu8Q",
                "title": "iShowSpeed Plays Talking Ben (HE SAID YES?!)",
                "url": "https://www.youtube.com/watch?v=X7c5l-uIu8Q",
                "thumbnail": "https://i.ytimg.com/vi/X7c5l-uIu8Q/hqdefault.jpg",
                "duration": "1h 14m",
                "badge": "🐶 Legendary Talking Ben"
            },
            {
                "id": "pYj6N8wO3y0",
                "title": "iShowSpeed IRL Stream In Brazil Favela!",
                "url": "https://www.youtube.com/watch?v=pYj6N8wO3y0",
                "thumbnail": "https://i.ytimg.com/vi/pYj6N8wO3y0/hqdefault.jpg",
                "duration": "3h 40m",
                "badge": "🇧🇷 Rio Favela Madness"
            },
            {
                "id": "tKp7b7v9YnQ",
                "title": "iShowSpeed IRL Stream In Japan!",
                "url": "https://www.youtube.com/watch?v=tKp7b7v9YnQ",
                "thumbnail": "https://i.ytimg.com/vi/tKp7b7v9YnQ/hqdefault.jpg",
                "duration": "4h 30m",
                "badge": "🇯🇵 Tokyo Fan Stampede"
            },
            {
                "id": "rW8n3Xv0YzA",
                "title": "iShowSpeed Sidemen Charity Match 2023 Highlights",
                "url": "https://www.youtube.com/watch?v=rW8n3Xv0YzA",
                "thumbnail": "https://i.ytimg.com/vi/rW8n3Xv0YzA/hqdefault.jpg",
                "duration": "45 mins",
                "badge": "⚽ Sidemen Match Chaos"
            },
            {
                "id": "k9V2mP4x8Tw",
                "title": "iShowSpeed Tries Extreme Spicy Korean 2X Buldak",
                "url": "https://www.youtube.com/watch?v=k9V2mP4x8Tw",
                "thumbnail": "https://i.ytimg.com/vi/k9V2mP4x8Tw/hqdefault.jpg",
                "duration": "28 mins",
                "badge": "🌶️ Fire Noodle Agony"
            },
            {
                "id": "gP8v4W2k7Zc",
                "title": "iShowSpeed in WWE Royal Rumble Highlights!",
                "url": "https://www.youtube.com/watch?v=gP8v4W2k7Zc",
                "thumbnail": "https://i.ytimg.com/vi/gP8v4W2k7Zc/hqdefault.jpg",
                "duration": "32 mins",
                "badge": "🤼 RKO Announce Table"
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
                "id": "W5Y6k2Z9vPx",
                "title": "Kai Cenat & Kevin Hart Live Stream Madness!",
                "url": "https://www.youtube.com/watch?v=W5Y6k2Z9vPx",
                "thumbnail": "https://i.ytimg.com/vi/W5Y6k2Z9vPx/hqdefault.jpg",
                "duration": "2h 45m",
                "badge": "🏆 Kevin Hart Collab"
            },
            {
                "id": "bL3v8W9r0Pq",
                "title": "Kai Cenat & Druski Hilarious Stream Moments",
                "url": "https://www.youtube.com/watch?v=bL3v8W9r0Pq",
                "thumbnail": "https://i.ytimg.com/vi/bL3v8W9r0Pq/hqdefault.jpg",
                "duration": "3h 10m",
                "badge": "💀 Druski x Kai Roast"
            },
            {
                "id": "gT9k1X4r7Wz",
                "title": "Kai Cenat 7 Days In Jail Stream Marathon",
                "url": "https://www.youtube.com/watch?v=gT9k1X4r7Wz",
                "thumbnail": "https://i.ytimg.com/vi/gT9k1X4r7Wz/hqdefault.jpg",
                "duration": "4h 50m",
                "badge": "🔒 Prison Stream Event"
            },
            {
                "id": "mK2v7R9w4Xp",
                "title": "Kai Cenat Beats Elden Ring Final Boss!",
                "url": "https://www.youtube.com/watch?v=mK2v7R9w4Xp",
                "thumbnail": "https://i.ytimg.com/vi/mK2v7R9w4Xp/hqdefault.jpg",
                "duration": "2h 30m",
                "badge": "🎮 Elden Ring Scream"
            },
            {
                "id": "pL8w3X1v9Qr",
                "title": "Kai Cenat & Nicki Minaj Live On Stream!",
                "url": "https://www.youtube.com/watch?v=pL8w3X1v9Qr",
                "thumbnail": "https://i.ytimg.com/vi/pL8w3X1v9Qr/hqdefault.jpg",
                "duration": "1h 40m",
                "badge": "👑 Barbz Takeover"
            },
            {
                "id": "sK9v2M1w8Rx",
                "title": "Kai Cenat & Ice Spice Hilarious NYC Stream",
                "url": "https://www.youtube.com/watch?v=sK9v2M1w8Rx",
                "thumbnail": "https://i.ytimg.com/vi/sK9v2M1w8Rx/hqdefault.jpg",
                "duration": "1h 50m",
                "badge": "🎤 Ice Spice In The Stu"
            },
            {
                "id": "zT1r8W4k9Vx",
                "title": "Kai Cenat & Snoop Dogg Live Smoke Session",
                "url": "https://www.youtube.com/watch?v=zT1r8W4k9Vx",
                "thumbnail": "https://i.ytimg.com/vi/zT1r8W4k9Vx/hqdefault.jpg",
                "duration": "2h 10m",
                "badge": "🔥 West Coast Legend"
            },
            {
                "id": "xQ8v3M9r1Wz",
                "title": "Kai Cenat Sleep Stream Interrupted by Fire Alarm",
                "url": "https://www.youtube.com/watch?v=xQ8v3M9r1Wz",
                "thumbnail": "https://i.ytimg.com/vi/xQ8v3M9r1Wz/hqdefault.jpg",
                "duration": "1h 05m",
                "badge": "🚨 3AM Fire Alarm Rage"
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
            },
            {
                "id": "bK7w4X9v1Rp",
                "title": "Jynxzi 1v1 Against Beaulo for $10,000",
                "url": "https://www.youtube.com/watch?v=bK7w4X9v1Rp",
                "thumbnail": "https://i.ytimg.com/vi/bK7w4X9v1Rp/hqdefault.jpg",
                "duration": "45 mins",
                "badge": "🏆 The Beaulo Showdown"
            },
            {
                "id": "wT2r8K4m9Vx",
                "title": "Jynxzi Breaks His 50th Controller on Stream",
                "url": "https://www.youtube.com/watch?v=wT2r8K4m9Vx",
                "thumbnail": "https://i.ytimg.com/vi/wT2r8K4m9Vx/hqdefault.jpg",
                "duration": "22 mins",
                "badge": "💥 Controller Smash"
            },
            {
                "id": "pQ9v1M7w4Rx",
                "title": "Jynxzi Reacts To The Worst R6 Clips In History",
                "url": "https://www.youtube.com/watch?v=pQ9v1M7w4Rx",
                "thumbnail": "https://i.ytimg.com/vi/pQ9v1M7w4Rx/hqdefault.jpg",
                "duration": "38 mins",
                "badge": "🤦 Champion Brain Damage"
            },
            {
                "id": "xM4w2K8r7Vp",
                "title": "Jynxzi Blind Dating 10 Girls on Discord",
                "url": "https://www.youtube.com/watch?v=xM4w2K8r7Vp",
                "thumbnail": "https://i.ytimg.com/vi/xM4w2K8r7Vp/hqdefault.jpg",
                "duration": "1h 12m",
                "badge": "❤️ Unhinged Rizz"
            },
            {
                "id": "rT8k9V1w4Xz",
                "title": "Jynxzi Discord Got Talent Season 2",
                "url": "https://www.youtube.com/watch?v=rT8k9V1w4Xz",
                "thumbnail": "https://i.ytimg.com/vi/rT8k9V1w4Xz/hqdefault.jpg",
                "duration": "1h 35m",
                "badge": "🎤 Golden Buzzer Chaos"
            },
            {
                "id": "vL2m7W9r0Pq",
                "title": "Jynxzi 1v5 Champion Ranked Overtime Clutch",
                "url": "https://www.youtube.com/watch?v=vL2m7W9r0Pq",
                "thumbnail": "https://i.ytimg.com/vi/vL2m7W9r0Pq/hqdefault.jpg",
                "duration": "29 mins",
                "badge": "🔥 Insane Ace Clutch"
            },
            {
                "id": "mP9w3X7v2Kp",
                "title": "Jynxzi & Sketch Playing Rainbow Six Siege",
                "url": "https://www.youtube.com/watch?v=mP9w3X7v2Kp",
                "thumbnail": "https://i.ytimg.com/vi/mP9w3X7v2Kp/hqdefault.jpg",
                "duration": "1h 08m",
                "badge": "⚡ Special Teams Unite"
            },
            {
                "id": "tK1v8M4r9Wz",
                "title": "Jynxzi Eats The One Chip Challenge on Live Stream",
                "url": "https://www.youtube.com/watch?v=tK1v8M4r9Wz",
                "thumbnail": "https://i.ytimg.com/vi/tK1v8M4r9Wz/hqdefault.jpg",
                "duration": "25 mins",
                "badge": "🌶️ Carolina Reaper Agony"
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
            },
            {
                "id": "vM8k2W9r4Xp",
                "title": "CaseOh Plays 60 Seconds (YOU CANNOT BE SERIOUS)",
                "url": "https://www.youtube.com/watch?v=vM8k2W9r4Xp",
                "thumbnail": "https://i.ytimg.com/vi/vM8k2W9r4Xp/hqdefault.jpg",
                "duration": "48 mins",
                "badge": "🥫 Timmy Left Behind"
            },
            {
                "id": "wP4r7K1v9Mz",
                "title": "CaseOh Plays Supermarket Simulator (STORE IS IN RUINS)",
                "url": "https://www.youtube.com/watch?v=wP4r7K1v9Mz",
                "thumbnail": "https://i.ytimg.com/vi/wP4r7K1v9Mz/hqdefault.jpg",
                "duration": "1h 22m",
                "badge": "🛒 Cashier Meltdown"
            },
            {
                "id": "zT9v1M4k8Rx",
                "title": "CaseOh Plays Fears to Fathom: Ironbark Lookout",
                "url": "https://www.youtube.com/watch?v=zT9v1M4k8Rx",
                "thumbnail": "https://i.ytimg.com/vi/zT9v1M4k8Rx/hqdefault.jpg",
                "duration": "2h 10m",
                "badge": "🌲 Fire Tower Panic"
            },
            {
                "id": "qK2w8X7v4Mp",
                "title": "CaseOh Bans 50 People in Chat For Weight Jokes",
                "url": "https://www.youtube.com/watch?v=qK2w8X7v4Mp",
                "thumbnail": "https://i.ytimg.com/vi/qK2w8X7v4Mp/hqdefault.jpg",
                "duration": "35 mins",
                "badge": "💀 You're Banned Buddy"
            },
            {
                "id": "rM4v9W1k7Xz",
                "title": "CaseOh Plays Granny Chapter 3 (HEART ATTACK)",
                "url": "https://www.youtube.com/watch?v=rM4v9W1k7Xz",
                "thumbnail": "https://i.ytimg.com/vi/rM4v9W1k7Xz/hqdefault.jpg",
                "duration": "55 mins",
                "badge": "👵 Granny in the Closet"
            },
            {
                "id": "tP8k2M7v4Wp",
                "title": "CaseOh Plays Contraband Police (INSPECTION FAILED)",
                "url": "https://www.youtube.com/watch?v=tP8k2M7v4Wp",
                "thumbnail": "https://i.ytimg.com/vi/tP8k2M7v4Wp/hqdefault.jpg",
                "duration": "1h 30m",
                "badge": "👮 Border Chaos"
            },
            {
                "id": "xL1v7K9w2Rp",
                "title": "CaseOh Plays Night Shift at the Gas Station",
                "url": "https://www.youtube.com/watch?v=xL1v7K9w2Rp",
                "thumbnail": "https://i.ytimg.com/vi/xL1v7K9w2Rp/hqdefault.jpg",
                "duration": "1h 14m",
                "badge": "⛽ Night Shift Horror"
            },
            {
                "id": "cP4w8M1r9Vx",
                "title": "CaseOh Plays Five Nights at Freddy's 1",
                "url": "https://www.youtube.com/watch?v=cP4w8M1r9Vx",
                "thumbnail": "https://i.ytimg.com/vi/cP4w8M1r9Vx/hqdefault.jpg",
                "duration": "1h 02m",
                "badge": "🐻 Foxy Sprints Down The Hall"
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

