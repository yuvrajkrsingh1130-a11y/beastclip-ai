import os
import subprocess
from pathlib import Path
from backend.config import BASE_DIR, TEMP_DIR, OUTPUT_DIR

class CompilationBuilder:
    def __init__(self, output_width: int = 1080, output_height: int = 1920):
        self.output_width = output_width
        self.output_height = output_height

    def create_countdown_ass(
        self,
        output_ass_path: str,
        rank_number: int,
        total_items: int,
        creator_name: str = "",
        segment_duration: float = 10.0,
        style: str = "gold"
    ) -> str:
        """
        Generates an animated ASS countdown badge card in the top center of the clip
        (e.g., '#5 • W MOMENT', '#1 🔥 • INSANE REACTION').
        """
        # Style color schemes
        if style == "cyber":
            badge_color = "&H00FFFF00&" # Cyan
            rank_color = "&H00FF00FF&"  # Pink
        elif style == "fire":
            badge_color = "&H000000FF&" # Bright Red
            rank_color = "&H0000FFFF&"  # Yellow
        elif style == "beast":
            badge_color = "&H0000FF00&" # Green
            rank_color = "&H00FFFFFF&"  # White
        else: # gold
            badge_color = "&H0000D7FF&" # Gold/Amber
            rank_color = "&H00FFFFFF&"  # White

        rank_label = f"#{rank_number}"
        if rank_number == 1:
            rank_label = "#1 BEST MOMENT 🔥"
        else:
            rank_label = f"#{rank_number} MOMENT"

        creator_label = f" • {creator_name.upper()}" if creator_name else ""
        header_text = f"{rank_label}{creator_label}"

        dur_ms = int(segment_duration * 1000)

        ass_content = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: CountdownBadge,Arial Black,48,{badge_color},&H00000000&,&H00000000&,&H80000000&,-1,0,0,0,100,100,2,0,1,6,3,8,40,40,140,1
Style: CountdownSub,Arial,28,&H00E0E0E0&,&H00000000&,&H00000000&,&H80000000&,-1,0,0,0,100,100,1,0,1,3,2,8,40,40,210,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,0:00:00.00,{self._format_ass_time(dur_ms)},CountdownBadge,,0,0,0,,{{\\fad(200,200)\\t(0,250,\\fscx115\\fscy115)\\t(250,500,\\fscx100\\fscy100)}}{header_text}
Dialogue: 0,0:00:00.00,{self._format_ass_time(dur_ms)},CountdownSub,,0,0,0,,{{\\fad(200,200)}}TOP {total_items} COMPILATION
"""
        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write(ass_content)

        return output_ass_path

    def _format_ass_time(self, ms: int) -> str:
        hours = ms // 3600000
        ms %= 3600000
        minutes = ms // 60000
        ms %= 60000
        seconds = ms // 1000
        centiseconds = (ms % 1000) // 10
        return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

    def build_compilation(
        self,
        clip_segments: list,
        output_path: str,
        total_target_duration: int = 50,
        countdown_style: str = "gold"
    ) -> str:
        """
        Compiles multiple video segments into a single 9:16 vertical Short.
        clip_segments: list of dicts with keys:
          - video_path: str
          - start_time: float (optional, default 0)
          - duration: float
          - rank: int (e.g. 5, 4, 3, 2, 1)
          - creator_name: str (optional)
        """
        num_segments = len(clip_segments)
        if num_segments == 0:
            raise ValueError("No video segments provided for compilation")

        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        # Allocate proportional duration per segment (e.g. 5 clips in 50s = 10s each)
        target_per_seg = max(6.0, round(total_target_duration / num_segments, 1))

        processed_parts = []

        for idx, seg in enumerate(clip_segments):
            seg_video = seg["video_path"]
            seg_start = seg.get("start_time", 0.0)
            seg_dur = min(seg.get("duration", target_per_seg), target_per_seg)
            rank_num = seg.get("rank", num_segments - idx)
            creator_name = seg.get("creator_name", "")

            part_out = TEMP_DIR / f"comp_part_{idx}_{rank_num}.mp4"
            badge_ass = TEMP_DIR / f"comp_badge_{idx}_{rank_num}.ass"

            # Create dynamic countdown badge ASS
            self.create_countdown_ass(
                output_ass_path=str(badge_ass),
                rank_number=rank_num,
                total_items=num_segments,
                creator_name=creator_name,
                segment_duration=seg_dur,
                style=countdown_style
            )

            try:
                rel_badge = Path(badge_ass).resolve().relative_to(BASE_DIR.resolve()).as_posix()
            except Exception:
                rel_badge = Path(badge_ass).name

            # Pre-render individual segment to standard 1080x1920 with countdown badge and normalized audio
            vf_seg = (
                f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                f"subtitles={rel_badge}"
            )
            af_seg = (
                "aresample=async=1000,"
                "volume=1.35,"
                "compand=attacks=0.02:decays=0.1:points=-80/-80|-45/-22|-20/-8|0/-1:soft-knee=6,"
                "aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo"
            )

            part_cmd = [
                "ffmpeg", "-y",
                "-ss", str(seg_start),
                "-t", str(seg_dur),
                "-i", str(seg_video),
                "-filter_complex", f"[0:v]{vf_seg}[v]",
                "-map", "[v]",
                "-map", "0:a?",
                "-af", af_seg,
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "22",
                "-c:a", "aac",
                "-b:a", "192k",
                str(part_out)
            ]

            subprocess.run(part_cmd, cwd=str(BASE_DIR), check=True, capture_output=True)
            if part_out.exists():
                processed_parts.append(str(part_out))

        if not processed_parts:
            raise RuntimeError("Failed to process compilation parts")

        # Concat all segments into final compilation
        concat_list_file = TEMP_DIR / "comp_concat_list.txt"
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for p in processed_parts:
                escaped_p = Path(p).as_posix()
                f.write(f"file '{escaped_p}'\n")

        # Progress bar filter on the whole compiled video
        total_dur_calc = len(processed_parts) * target_per_seg
        pbar_filter = f"drawbox=x=0:y=1910:w='(t/{max(1.0, total_dur_calc)})*1080':h=10:color=gold@0.9:t=fill"

        final_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_file),
            "-vf", pbar_filter,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "20",
            "-c:a", "aac",
            "-b:a", "256k",
            str(output_path)
        ]

        subprocess.run(final_cmd, cwd=str(BASE_DIR), check=True, capture_output=True)

        return str(output_path)
