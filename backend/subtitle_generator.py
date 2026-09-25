import os
import re
from pathlib import Path
from backend.config import SUBTITLE_PRESETS

# Emoji mapping for viral streamer keywords
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

    def _get_active_word_effect(self, highlight_color: str, animation_type: str) -> str:
        """Returns the ASS override tags for the active animated word."""
        hl_color = highlight_color if highlight_color.endswith('&') else f"{highlight_color}&"
        if animation_type == "bounce":
            # MrBeast Punch Bounce
            return r"{\c" + hl_color + r"\fscx100\fscy100\t(0,70,\fscx124\fscy124)\t(70,140,\fscx108\fscy108)}"
        elif animation_type == "tilt":
            # Kai Cenat Cyber Tilt
            return r"{\c" + hl_color + r"\frz-3\fscx115\fscy115\t(0,70,\frz3)\t(70,140,\frz0\fscx106\fscy106)}"
        elif animation_type == "shake":
            # Speed Fire & Rage Rumble
            return r"{\c" + hl_color + r"\frz3\fscx122\fscy122\t(0,40,\frz-3)\t(40,80,\frz2)\t(80,120,\frz0\fscx110\fscy110)}"
        elif animation_type == "glitch":
            # Cyberpunk Electric Glitch
            return r"{\c" + hl_color + r"\frz-2\fscx95\fscy95\t(0,50,\frz2\fscx122\fscy122)\t(50,110,\frz0\fscx108\fscy108)}"
        elif animation_type == "power":
            # Anime Super Saiyan Aura Punch
            return r"{\c" + hl_color + r"\fscx100\fscy100\t(0,60,\fscx130\fscy130)\t(60,130,\fscx112\fscy112)}"
        elif animation_type == "smooth":
            # Minimalist Clean
            return r"{\c" + hl_color + r"\fscx108\fscy108}"
        else:
            # Hormozi Pop Pulse (Default)
            return r"{\c" + hl_color + r"\fscx120\fscy120\t(0,80,\fscx108\fscy108)}"

    def create_ass_subtitles(
        self,
        clip_words: list,
        output_ass_path: str,
        creator_credit: str = "@Creator",
        clip_duration: float = 60.0,
        max_words_per_line: int = 2
    ):
        """
        Generates zero-lag, frame-perfect ASS subtitles with kinetic creator animations,
        small talk retention, and crisp attribution.
        """
        fontname = self.preset.get("fontname", "Arial Black")
        fontsize = int(self.preset.get("fontsize", 24) * 2.3)  # ~55px for 1080x1920
        primary_color = self.preset.get("primary_color", "&H00FFFFFF&")
        highlight_color = self.preset.get("highlight_color", "&H0000FFFF&")
        outline_color = self.preset.get("outline_color", "&H00000000&")
        outline_width = 5.2
        shadow_width = 2.5
        animation_type = self.preset.get("animation", "pop")
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
Style: Default,{fontname},{fontsize},{primary_color},&H000000FF&,{outline_color},&HB0000000&,-1,0,0,0,100,100,1,0,1,{outline_width},{shadow_width},2,40,40,380,1
Style: CreditBadge,Arial,28,&H00FFFFFF&,&H000000FF&,&H00000000&,&H90000000&,-1,0,0,0,100,100,0,0,1,3,2,8,40,40,90,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,0:00:00.00,{format_ass_time(clip_duration)},CreditBadge,,0,0,0,,ORIGINAL CREDIT: {clean_credit}
"""

        # Filter and normalize raw words
        filtered_words = []
        last_word_str = None
        for w in clip_words:
            raw = clean_word_text(w.get("word", ""))
            if not raw or raw in ["[", "]", "(", ")", "...", "---"]:
                continue
            
            lower_raw = raw.lower().strip("!?,.:;-")
            # Prevent rapid duplicate hallucination spam
            if lower_raw and lower_raw == last_word_str and len(filtered_words) > 0 and (w["start"] - filtered_words[-1]["start"] < 0.20):
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

        # Snappy Viral Chunking (1 to 2 words per chunk for punchy pacing)
        chunks = []
        current_chunk = []

        for i, w in enumerate(filtered_words):
            current_chunk.append(w)
            
            # Check for natural pause or max words
            is_max_len = len(current_chunk) >= max_words_per_line
            has_punctuation = any(w["word"].endswith(p) for p in [".", "!", "?", ","])
            
            is_speech_pause = False
            if i < len(filtered_words) - 1:
                pause_gap = filtered_words[i+1]["start"] - w["end"]
                if pause_gap > 0.28:
                    is_speech_pause = True

            if is_max_len or has_punctuation or is_speech_pause:
                chunks.append(current_chunk)
                current_chunk = []

        if current_chunk:
            chunks.append(current_chunk)

        # Generate Continuous, Zero-Lag Dialogue Events
        for c_idx, chunk in enumerate(chunks):
            chunk_len = len(chunk)
            chunk_end_time = chunk[-1]["end"]
            
            next_chunk_start = chunks[c_idx + 1][0]["start"] if (c_idx < len(chunks) - 1) else clip_duration

            for i, active_w in enumerate(chunk):
                # Apply 25ms vocal onset lead-in to eliminate perceived audio/visual lag
                w_start = max(0.0, active_w["start"] - 0.025)
                
                if i < chunk_len - 1:
                    w_end = max(active_w["end"], chunk[i + 1]["start"] - 0.01)
                    if w_end <= w_start:
                        w_end = w_start + 0.20
                else:
                    # Last word in chunk: hold cleanly until next chunk or speech pause
                    w_end = max(active_w["end"], chunk_end_time)
                    w_end = min(w_end + 0.18, next_chunk_start)
                    if w_end <= w_start:
                        w_end = w_start + 0.30

                # Build the styled chunk line
                line_parts = []
                for j, item in enumerate(chunk):
                    word_str = item["word"]
                    display_text = word_str.upper() if all_caps else word_str
                    
                    clean_kw = word_str.lower().strip("!?,.:;-")
                    emoji_str = f" {KEYWORD_EMOJIS[clean_kw]}" if (emojis_enabled and clean_kw in KEYWORD_EMOJIS) else ""

                    if i == j:
                        # ACTIVE WORD with Creator Animation
                        anim_tag = self._get_active_word_effect(highlight_color, animation_type)
                        line_parts.append(f"{anim_tag}{display_text}{emoji_str}" + r"{\r}")
                    else:
                        # INACTIVE PHRASE WORD
                        line_parts.append(r"{\c" + primary_color + r"}" + f"{display_text}{emoji_str}")

                rendered_line = " ".join(line_parts)
                start_str = format_ass_time(w_start)
                end_str = format_ass_time(w_end)
                ass_content += f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{rendered_line}\n"

        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write(ass_content)
