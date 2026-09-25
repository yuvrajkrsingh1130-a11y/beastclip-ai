import os
import re
import subprocess
from pathlib import Path
from backend.config import BASE_DIR, TEMP_DIR, OUTPUT_DIR

class CompilationBuilder:
    def __init__(self, output_width: int = 1080, output_height: int = 1920):
        self.output_width = output_width
        self.output_height = output_height

    def _format_ass_time(self, ms: int) -> str:
        hours = ms // 3600000
        ms %= 3600000
        minutes = ms // 60000
        ms %= 60000
        seconds = ms // 1000
        centiseconds = (ms % 1000) // 10
        return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

    def create_ranking_ladder_ass(
        self,
        output_ass_path: str,
        current_rank: int,
        total_items: int,
        ranking_header: str,
        clip_labels: dict,
        words: list = None,
        segment_duration: float = 10.0,
        style: str = "gold"
    ) -> str:
        """
        Generates an ASS subtitle overlay matching the viral 'Ranking Leaderboard Shorts' style:
        1. Top Center Header: e.g. "Ranking Best Fails of The Week"
        2. Left Vertical Numbered Ladder (1..5): Sticker-styled yellow numbers with progressive clip reveals
        3. Dynamic Spoken Word Subtitles: Centered in lower-third
        """
        # Style color schemes
        if style == "cyber":
            num_color = "&H00FFFF00&" # Cyan
            active_color = "&H00FF00FF&" # Pink
        elif style == "fire":
            num_color = "&H000000FF&" # Red
            active_color = "&H0000FFFF&" # Yellow
        elif style == "beast":
            num_color = "&H0000FF00&" # Green
            active_color = "&H00FFFFFF&" # White
        else: # gold
            num_color = "&H0000D7FF&" # Vibrant Yellow / Gold
            active_color = "&H0000FFFF&" # Pop Yellow

        dur_ms = int(segment_duration * 1000)
        end_ass_time = self._format_ass_time(dur_ms)

        # Header Title formatting
        header_clean = ranking_header.strip() if ranking_header else f"Ranking Top {total_items} Moments"
        # If title has multiple words, highlight keywords (e.g. "Fails", "Moments", "Speed")
        header_display = re.sub(r'(?i)(fails|moments|highlights|reactions|clutches|clips)', r'{\\c&H000000FF&}\1{\\c&H00FFFFFF&}', header_clean)

        ass_lines = [
            "[Script Info]",
            "ScriptType: v4.00+",
            "PlayResX: 1080",
            "PlayResY: 1920",
            "ScaledBorderAndShadow: yes",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            # Header Style (Top Center)
            "Style: RankHeader,Arial Black,46,&H00FFFFFF&,&H00000000&,&H00000000&,&H90000000&,-1,0,0,0,100,100,1,0,1,6,3,8,30,30,95,1",
            # Ladder Row Styles (Left aligned)
            f"Style: LadderNum,Arial Black,48,{num_color},&H00000000&,&H00000000&,&H90000000&,-1,0,0,0,100,100,1,0,1,7,3,7,65,30,260,1",
            "Style: LadderLabel,Arial Black,34,&H00FFFFFF&,&H00000000&,&H00000000&,&H90000000&,-1,0,0,0,100,100,0,0,1,5,2,7,65,30,260,1",
            # Spoken Subtitles (Lower-third Center)
            "Style: SubNormal,Arial Black,50,&H00FFFFFF&,&H00000000&,&H00000000&,&HB0000000&,-1,0,0,0,100,100,1,0,1,6,2,2,40,40,360,1",
            f"Style: SubActive,Arial Black,54,{active_color},&H00000000&,&H00000000&,&HB0000000&,-1,0,0,0,105,105,1,0,1,7,3,2,40,40,360,1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
            # 1. Top Header
            f"Dialogue: 2,0:00:00.00,{end_ass_time},RankHeader,,0,0,0,,{{\\fad(150,150)}}{header_display}"
        ]

        # 2. Left Vertical Number Ladder (Slots 1 to total_items)
        base_y = 250
        y_step = 76

        for i in range(1, total_items + 1):
            slot_rank = i
            slot_y = base_y + ((slot_rank - 1) * y_step)
            label_text = clip_labels.get(slot_rank, "").strip()

            # If this slot has NOT been revealed yet (e.g. slot 1 when slot 5 is playing)
            if slot_rank < current_rank:
                # Show just number "1.", "2.", etc.
                ass_lines.append(
                    f"Dialogue: 1,0:00:00.00,{end_ass_time},LadderNum,,65,30,{slot_y},,{slot_rank}."
                )
            # If this is the CURRENTLY ACTIVE rank playing right now
            elif slot_rank == current_rank:
                display_label = label_text if label_text else f"Moment #{slot_rank}"
                if slot_rank == 1:
                    full_item_text = f"{slot_rank}. {display_label} 🔥"
                    pop_anim = "{\\t(0,250,\\fscx115\\fscy115)\\t(250,500,\\fscx100\\fscy100)\\c&H000000FF&}"
                else:
                    full_item_text = f"{slot_rank}. {display_label}"
                    pop_anim = "{\\t(0,250,\\fscx110\\fscy110)\\t(250,500,\\fscx100\\fscy100)}"

                ass_lines.append(
                    f"Dialogue: 3,0:00:00.00,{end_ass_time},LadderNum,,65,30,{slot_y},,{pop_anim}{full_item_text}"
                )
            # If this slot was ALREADY revealed previously
            else:
                display_label = label_text if label_text else f"Moment #{slot_rank}"
                ass_lines.append(
                    f"Dialogue: 1,0:00:00.00,{end_ass_time},LadderLabel,,65,30,{slot_y},,{{\\c{num_color}}}{slot_rank}. {{\\c&H00E0E0E0&}}{display_label}"
                )

        # 3. Spoken Subtitles (Dynamic word synchronization in center)
        if words and len(words) > 0:
            chunk_size = 3
            for w_idx in range(0, len(words), chunk_size):
                chunk = words[w_idx:w_idx + chunk_size]
                chunk_start = chunk[0].get("start", 0.0)
                chunk_end = chunk[-1].get("end", chunk_start + 1.2)
                if chunk_start >= segment_duration:
                    break
                if chunk_end > segment_duration:
                    chunk_end = segment_duration

                start_str = self._format_ass_time(int(chunk_start * 1000))
                end_str = self._format_ass_time(int(chunk_end * 1000))

                for current_w in chunk:
                    w_start_ms = int(current_w.get("start", chunk_start) * 1000)
                    w_end_ms = int(current_w.get("end", chunk_end) * 1000)
                    w_start_s = self._format_ass_time(w_start_ms)
                    w_end_s = self._format_ass_time(w_end_ms)

                    text_parts = []
                    for w in chunk:
                        w_clean = re.sub(r'[^a-zA-Z0-9\s.,!?\'"-]', '', w.get("word", "")).strip()
                        if w == current_w:
                            text_parts.append(f"{{\\c{active_color}\\fscx112\\fscy112}}{w_clean.upper()}{{\\rSubNormal}}")
                        else:
                            text_parts.append(w_clean.upper())

                    line_text = " ".join(text_parts)
                    ass_lines.append(
                        f"Dialogue: 4,{w_start_s},{w_end_s},SubNormal,,40,40,360,,{line_text}"
                    )

        ass_content = "\n".join(ass_lines) + "\n"
        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write(ass_content)

        return output_ass_path

    def build_compilation(
        self,
        clip_segments: list,
        output_path: str,
        ranking_header: str = "Ranking Best Fails of The Week",
        clip_labels: dict = None,
        total_target_duration: int = 50,
        countdown_style: str = "gold"
    ) -> str:
        """
        Compiles multiple video segments into a viral 9:16 vertical Ranking Leaderboard Short.
        clip_segments: list of dicts:
          - video_path: str
          - start_time: float (default 0)
          - duration: float
          - rank: int (e.g. 5, 4, 3, 2, 1)
          - words: list (optional transcription words)
          - creator_name: str (optional)
        """
        num_segments = len(clip_segments)
        if num_segments == 0:
            raise ValueError("No video segments provided for compilation")

        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        if clip_labels is None:
            clip_labels = {}

        # Default per-segment duration
        target_per_seg = max(6.0, round(total_target_duration / num_segments, 1))
        processed_parts = []

        for idx, seg in enumerate(clip_segments):
            seg_video = seg["video_path"]
            seg_start = seg.get("start_time", 0.0)
            seg_dur = min(seg.get("duration", target_per_seg), target_per_seg)
            rank_num = seg.get("rank", num_segments - idx)
            seg_words = seg.get("words", [])

            part_out = TEMP_DIR / f"comp_part_{idx}_{rank_num}.mp4"
            ladder_ass = TEMP_DIR / f"comp_ladder_{idx}_{rank_num}.ass"

            # Create ranking ladder ASS subtitle script
            self.create_ranking_ladder_ass(
                output_ass_path=str(ladder_ass),
                current_rank=rank_num,
                total_items=num_segments,
                ranking_header=ranking_header,
                clip_labels=clip_labels,
                words=seg_words,
                segment_duration=seg_dur,
                style=countdown_style
            )

            # Properly escape path for Windows FFmpeg subtitles filter
            escaped_ass = Path(ladder_ass).resolve().as_posix()
            if os.name == "nt":
                # Escape drive letter colon (e.g. C:/ -> C\\:/)
                drive, rest = os.path.splitdrive(escaped_ass)
                if drive:
                    escaped_ass = f"{drive[0]}\\:{rest}"

            vf_seg = (
                f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                f"subtitles='{escaped_ass}'"
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

        final_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_file),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "veryfast",
            "-crf", "20",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            str(output_path)
        ]

        subprocess.run(final_cmd, cwd=str(BASE_DIR), check=True, capture_output=True)

        return str(output_path)
