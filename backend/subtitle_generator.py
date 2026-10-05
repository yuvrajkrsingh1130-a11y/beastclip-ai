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
    def __init__(self, preset_name: str = "hormozi", caption_size: str = "slightly_big"):
        self.preset_name = preset_name
        self.preset = SUBTITLE_PRESETS.get(preset_name, SUBTITLE_PRESETS["hormozi"])
        self.caption_size = caption_size or "slightly_big"

    def create_ass_subtitles(
        self,
        clip_words: list,
        output_ass_path: str,
        creator_credit: str = "@Creator",
        clip_duration: float = 60.0,
        max_words_per_line: int = 2
    ):
        """
        Generates frame-perfect animated kinetic captions with iconic bounce/hover effects
        (IShowSpeed, Kai Cenat, MrBeast style) and zero overlap/lag collisions.
        """
        fontname = self.preset.get("fontname", "Arial Black")
        base_size = self.preset.get("fontsize", 25)

        # Scale font size prominently for 1080x1920 portrait canvas so captions are never too small
        if self.caption_size == "medium":
            scale_mult = 3.1   # ~76-78px (Clean & balanced)
        elif self.caption_size == "large":
            scale_mult = 4.0   # ~96-100px (Extra big / high impact)
        else: # "slightly_big" (default recommended)
            scale_mult = 3.55  # ~86-90px (Perfect prominent mobile size)

        fontsize = int(base_size * scale_mult)
        primary_color = self.preset.get("primary_color", "&H00FFFFFF&")
        highlight_color = self.preset.get("highlight_color", "&H0000FFFF&")
        outline_color = self.preset.get("outline_color", "&H00000000&")
        outline_width = 8.0
        shadow_width = 3.5
        all_caps = self.preset.get("all_caps", True)
        emojis_enabled = self.preset.get("emojis", True)
        anim_type = self.preset.get("animation", "bounce")

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
Style: Default,{fontname},{fontsize},{primary_color},&H000000FF&,{outline_color},&HB0000000&,-1,0,0,0,100,100,1,0,1,{outline_width},{shadow_width},2,40,40,440,1
Style: CreditBadge,Arial,28,&H00FFFFFF&,&H000000FF&,&H00000000&,&H90000000&,-1,0,0,0,100,100,0,0,1,3,2,8,40,40,100,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,0:00:00.00,{format_ass_time(clip_duration)},CreditBadge,,0,0,0,,ORIGINAL CREDIT: {clean_credit}
"""

        # Step 1: Filter, clean, and deduplicate words
        raw_words = []
        for w in clip_words:
            raw = clean_word_text(w.get("word", ""))
            if not raw or raw in ["[", "]", "(", ")", "...", "---"]:
                continue

            s = max(0.0, float(w.get("start", 0.0)))
            e = max(s + 0.08, float(w.get("end", s + 0.25)))
            raw_words.append({
                "word": raw,
                "start": s,
                "end": e
            })

        # Strictly sort words by start time
        raw_words.sort(key=lambda x: x["start"])

        # Deduplicate immediate adjacent identical words (Whisper hallucinations)
        filtered_words = []
        for w in raw_words:
            if filtered_words:
                last_w = filtered_words[-1]
                if w["word"].lower().strip("!?,.:;-") == last_w["word"].lower().strip("!?,.:;-") and (w["start"] - last_w["start"] < 0.20):
                    continue
            filtered_words.append(w)

        if not filtered_words:
            with open(output_ass_path, "w", encoding="utf-8") as f:
                f.write(ass_content)
            return

        # Step 2: Calibrated Synchronization Offset (+0.16s delay)
        # Fixes the lead offset where Whisper token timestamps predict speech ~160ms
        # before the acoustic sound is heard, ensuring captions pop on the exact audible voice.
        SYNC_DELAY = 0.16

        # Step 3: Group words into punchy 1-2 word mobile kinetic pulses
        pulses = []
        i = 0
        n_words = len(filtered_words)

        while i < n_words:
            w1 = filtered_words[i]
            pair = [w1]

            if i + 1 < n_words:
                w2 = filtered_words[i + 1]
                gap = w2["start"] - w1["end"]
                # Pair tightly connected words if short length
                if gap < 0.16 and (len(w1["word"]) + len(w2["word"]) <= 11) and not w1["word"].endswith((".", "!", "?")):
                    pair.append(w2)
                    i += 1

            raw_start = round(pair[0]["start"] + SYNC_DELAY, 2)
            raw_end = round(pair[-1]["end"] + SYNC_DELAY, 2)
            pulses.append({
                "items": pair,
                "start": raw_start,
                "end": max(raw_start + 0.22, raw_end + 0.08)
            })
            i += 1

        # Step 4: Strict Non-Overlapping Dialogue Timeline Generator
        # Eliminates subtitle stacking, screen lagging, and dual-caption collisions
        last_dialogue_end = 0.0
        for p_idx, pulse in enumerate(pulses):
            # Ensure this pulse starts strictly after previous pulse has finished
            if pulse["start"] < last_dialogue_end:
                pulse["start"] = round(last_dialogue_end + 0.02, 2)

            # Cap end time so it never overlaps or touches next pulse start
            if p_idx + 1 < len(pulses):
                next_p = pulses[p_idx + 1]
                next_raw_start = round(next_p["items"][0]["start"] + SYNC_DELAY, 2)
                pulse["end"] = min(pulse["end"], max(pulse["start"] + 0.18, next_raw_start - 0.02))
            else:
                pulse["end"] = min(clip_duration, pulse["end"])

            # Guarantee minimum readable duration
            if pulse["end"] <= pulse["start"]:
                pulse["end"] = round(pulse["start"] + 0.22, 2)

            last_dialogue_end = pulse["end"]

            # Step 5: Speed / MrBeast Kinetic Animation Tag Construction
            # Snappy pop-in bounce scale tag
            if anim_type == "bounce":
                # Iconic Speed & MrBeast bounce: grows from 84% to 124% in 65ms, snaps back to 100%
                anim_tag = r"{\fscx84\fscy84\t(0,65,\fscx124\fscy124)\t(65,135,\fscx100\fscy100)}"
            elif anim_type in ["tilt", "hover"]:
                # Alternating dynamic hover tilt (+/- 2.5 deg) with bounce punch
                tilt_deg = -2.5 if (p_idx % 2 == 0) else 2.5
                anim_tag = r"{\frz" + str(tilt_deg) + r"\fscx86\fscy86\t(0,65,\fscx120\fscy120)\t(65,135,\fscx100\fscy100)}"
            elif anim_type == "shake":
                # High energy Speed rage shake
                anim_tag = r"{\fscx80\fscy80\t(0,45,\fscx128\fscy128\frz-3)\t(45,95,\fscx112\fscy112\frz3)\t(95,145,\fscx100\fscy100\frz0)}"
            elif anim_type == "pop":
                anim_tag = r"{\fscx76\fscy76\t(0,65,\fscx114\fscy114)\t(65,120,\fscx100\fscy100)}"
            elif anim_type == "smooth":
                anim_tag = r"{\fscx92\fscy92\t(0,80,\fscx106\fscy106)\t(80,150,\fscx100\fscy100)}"
            else:
                anim_tag = r"{\fscx84\fscy84\t(0,65,\fscx124\fscy124)\t(65,135,\fscx100\fscy100)}"

            # Step 6: Active Word Highlighting (Karaoke style)
            word_elements = []
            for item in pulse["items"]:
                raw_w = item["word"]
                disp_w = raw_w.upper() if all_caps else raw_w
                clean_kw = raw_w.lower().strip("!?,.:;-")
                emoji_str = f" {KEYWORD_EMOJIS[clean_kw]}" if (emojis_enabled and clean_kw in KEYWORD_EMOJIS) else ""
                word_elements.append(f"{disp_w}{emoji_str}")

            if len(word_elements) == 1:
                # Single punch word: full highlight
                styled_text = anim_tag + r"{\c" + highlight_color + r"}" + word_elements[0]
            else:
                # 2-word punch: lead word in primary white, punchline word in highlight color
                styled_text = anim_tag + r"{\c" + primary_color + r"}" + word_elements[0] + r" {\c" + highlight_color + r"}" + word_elements[1]

            start_str = format_ass_time(pulse["start"])
            end_str = format_ass_time(pulse["end"])
            ass_content += f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{styled_text}\n"

        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write(ass_content)
