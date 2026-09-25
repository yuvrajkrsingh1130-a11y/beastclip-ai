import os
import re
from pathlib import Path
from backend.config import SUBTITLE_PRESETS

KEYWORD_EMOJIS = {
    "speed": "⚡",
    "kai": "👑",
    "ronaldo": "🐐",
    "siu": "⚡",
    "siuuu": "⚡",
    "art": "🎨",
    "rizz": "🔥",
    "insane": "🤯",
    "crazy": "🤪",
    "dead": "💀",
    "skull": "💀",
    "bro": "🗣️",
    "omg": "😱",
    "god": "😱",
    "fire": "🔥",
    "w": "🏆",
    "win": "🏆",
    "clutch": "🎯",
    "money": "💸",
    "run": "🏃",
    "rage": "😡",
    "angry": "🤬",
    "laugh": "😂",
    "funny": "🤣",
    "stream": "📺",
    "gaming": "🎮",
    "kill": "💥",
    "goat": "🐐",
    "hype": "🚀",
    "cap": "🧢",
    "cooked": "🍳",
    "chat": "💬"
}

def format_ass_time(seconds: float) -> str:
    """Converts seconds into ASS timestamp format H:MM:SS.cs"""
    seconds = max(0.0, float(seconds))
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def clean_word_text(raw: str) -> str:
    """Cleans up raw word text for display"""
    return re.sub(r'[\r\n\t]+', ' ', str(raw)).strip()

class SubtitleGenerator:
    def __init__(self, preset_name: str = "hormozi"):
        self.preset_name = preset_name
        self.preset = SUBTITLE_PRESETS.get(preset_name, SUBTITLE_PRESETS["hormozi"])

    def create_ass_subtitles(
        self,
        clip_words: list,
        output_ass_path: str,
        creator_credit: str = "@Creator",
        clip_duration: float = 60.0,
        max_words_per_line: int = 2
    ):
        """
        Generates ultra-fast, frame-perfect kinetic captions (1-2 words per pulse),
        matching high-retention creator formats (IShowSpeed, Kai Cenat, MrBeast).
        """
        fontname = self.preset.get("fontname", "Arial Black")
        fontsize = int(self.preset.get("fontsize", 24) * 2.2)  # ~52px
        primary_color = self.preset.get("primary_color", "&H00FFFFFF&")
        highlight_color = self.preset.get("highlight_color", "&H0000FFFF&")
        outline_color = self.preset.get("outline_color", "&H00000000&")
        outline_width = 4.5
        shadow_width = 2.0
        all_caps = self.preset.get("all_caps", True)
        emojis_enabled = self.preset.get("emojis", True)

        clean_credit = str(creator_credit).replace("{", "").replace("}", "").strip()

        # ASS Script Header (1080x1920 portrait standard)
        ass_content = f"""[Script Info]
Title: BeastClip AI Viral Captions
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{fontname},{fontsize},{primary_color},&H000000FF&,{outline_color},&HB0000000&,-1,0,0,0,100,100,1,0,1,{outline_width},{shadow_width},2,40,40,360,1
Style: CreditBadge,Arial,26,&H00FFFFFF&,&H000000FF&,&H00000000&,&H90000000&,-1,0,0,0,100,100,0,0,1,3,2,8,40,40,90,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,0:00:00.00,{format_ass_time(clip_duration)},CreditBadge,,0,0,0,,ORIGINAL CREDIT: {clean_credit}
"""

        # Filter words
        filtered_words = []
        last_word_str = None
        for w in clip_words:
            raw = clean_word_text(w.get("word", ""))
            if not raw or raw in ["[", "]", "(", ")", "...", "---"]:
                continue
            
            lower_raw = raw.lower().strip("!?,.:;-")
            if lower_raw and lower_raw == last_word_str and len(filtered_words) > 0 and (w["start"] - filtered_words[-1]["start"] < 0.15):
                continue
            last_word_str = lower_raw

            start_t = max(0.0, float(w.get("start", 0.0)))
            end_t = max(start_t + 0.08, float(w.get("end", start_t + 0.25)))
            filtered_words.append({
                "word": raw,
                "start": start_t,
                "end": end_t
            })

        if not filtered_words:
            with open(output_ass_path, "w", encoding="utf-8") as f:
                f.write(ass_content)
            return

        # Frame-Perfect Kinetic Pulse Generation (1 to 2 words per pulse)
        # Each pulse shows only the active word(s) spoken at that exact moment
        i = 0
        n_words = len(filtered_words)

        while i < n_words:
            w1 = filtered_words[i]
            pair = [w1]

            # Check if next word is spoken tightly together without pause (< 0.18s)
            if i + 1 < n_words:
                w2 = filtered_words[i + 1]
                gap = w2["start"] - w1["end"]
                # If short combined length and no gap, pair them
                if gap < 0.18 and (len(w1["word"]) + len(w2["word"]) <= 12) and not w1["word"].endswith((".", "!", "?")):
                    pair.append(w2)
                    i += 1

            # Determine pulse timing
            pulse_start = pair[0]["start"]
            if i + 1 < n_words:
                next_word_start = filtered_words[i + 1]["start"]
                pulse_end = min(pair[-1]["end"] + 0.10, next_word_start)
                if pulse_end <= pulse_start:
                    pulse_end = pulse_start + 0.22
            else:
                pulse_end = min(clip_duration, pair[-1]["end"] + 0.25)

            # Build rendered text
            word_strings = []
            for item in pair:
                raw_w = item["word"]
                display_w = raw_w.upper() if all_caps else raw_w
                clean_kw = raw_w.lower().strip("!?,.:;-")
                emoji_str = f" {KEYWORD_EMOJIS[clean_kw]}" if (emojis_enabled and clean_kw in KEYWORD_EMOJIS) else ""
                word_strings.append(f"{display_w}{emoji_str}")

            line_text = " ".join(word_strings)
            # High-visibility kinetic highlight color
            styled_text = r"{\c" + highlight_color + r"}" + line_text

            start_str = format_ass_time(pulse_start)
            end_str = format_ass_time(pulse_end)
            ass_content += f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{styled_text}\n"

            i += 1

        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write(ass_content)
