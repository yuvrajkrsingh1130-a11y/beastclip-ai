import re
import numpy as np
from backend.energy_detector import AudioEnergyDetector

class ClipExtractor:
    def __init__(self, energy_detector: AudioEnergyDetector = None):
        self.energy_detector = energy_detector or AudioEnergyDetector()

    def extract_top_highlights(
        self,
        transcription_data: dict,
        energy_timeline: list,
        total_duration: float,
        target_clip_duration: int = 40,
        num_clips: int = 5
    ) -> list:
        """
        Intelligently identifies the absolute funniest, most insane, screaming,
        and high-retention viral moments from anywhere across the entire video.
        Ensures clips are never sequential slices (0-30, 30-60) but rather
        genuine stand-out peaks across the whole timeline.
        """
        segments = transcription_data.get("segments", [])

        # Determine true video duration from all available signals
        if not total_duration or total_duration <= 0:
            if energy_timeline:
                total_duration = energy_timeline[-1]["time"]
            elif segments:
                total_duration = segments[-1]["end"]
            else:
                total_duration = 300.0

        window_size = target_clip_duration
        # High-resolution step (4 to 6 seconds) so no peak is missed
        step_seconds = max(4.0, min(8.0, window_size * 0.15))

        # Compile list of peak energy & reaction burst timestamps
        peak_times = [
            it["time"] for it in energy_timeline
            if it.get("is_spike") or it.get("surge_factor", 1.0) > 2.0 or it.get("energy", 0) > 0.4
        ]

        # Candidate windows storage
        raw_candidates = []

        # 1. Slide fine-grained windows across the entire video timeline
        max_start = max(0.0, total_duration - window_size)
        start_t = 0.0

        while start_t <= max_start:
            end_t = min(total_duration, start_t + window_size)
            if end_t - start_t < 15.0:
                break

            # A. Audio Energy & Scream Intensity Score (0 to 100)
            hype_score = self.energy_detector.get_hype_score_for_range(energy_timeline, start_t, end_t)

            # B. Extract Speech in this Window
            clip_transcript_segments = [
                s for s in segments
                if (start_t <= s["start"] <= end_t) or (start_t <= s["end"] <= end_t) or
                   (s["start"] <= start_t and s["end"] >= end_t)
            ]
            clip_text = " ".join([s["text"] for s in clip_transcript_segments]).strip()
            clip_text_lower = clip_text.lower()

            # C. Multi-Signal Comedy, Rage & Viral Triggers
            funny_keywords = [
                "haha", "hahaha", "lol", "lmao", "crying", "rofl", "giggle", "dead", "skull",
                "bro cooked", "cooked", "what am i watching", "he did not", "bro ain't no way",
                "look at him", "look at this", "ain't no way", "i'm dead", "i'm done", "i can't"
            ]
            shock_keywords = [
                "no way", "oh my god", "omg", "what the", "what is that", "bro what",
                "are you serious", "did he just", "he's hacking", "cheating", "stop it",
                "shut up", "get out", "help me", "nah nah", "holy", "insane", "crazy", "wtf"
            ]
            hype_keywords = [
                "w stream", "w chat", "l chat", "w art", "l art", "clutch", "sui", "suiii",
                "clip that", "watch this", "speed", "kai", "jynxzi", "caseoh", "gg", "w bro"
            ]

            funny_count = sum(clip_text_lower.count(kw) for kw in funny_keywords)
            shock_count = sum(clip_text_lower.count(kw) for kw in shock_keywords)
            hype_count = sum(clip_text_lower.count(kw) for kw in hype_keywords)
            exclamation_count = clip_text.count("!") + clip_text.count("?")

            semantic_bonus = min(
                45.0,
                (funny_count * 8.0) + (shock_count * 7.0) + (hype_count * 5.0) + (exclamation_count * 2.5)
            )

            # D. Hook Intensity in First 4 Seconds
            hook_words = []
            for s in clip_transcript_segments:
                for w in s.get("words", []):
                    if start_t <= w["start"] <= start_t + 4.0:
                        hook_words.append(w["word"])
            hook_text = " ".join(hook_words).lower()
            hook_bonus = 0.0
            if any(kw in hook_text for kw in ["wait", "what", "bro", "no way", "look", "oh", "listen", "chat", "stop"]):
                hook_bonus = 12.0

            # E. Speech Velocity (Words per second excitement spike)
            total_words_in_clip = sum(len(s.get("words", [])) for s in clip_transcript_segments)
            words_per_sec = total_words_in_clip / max(1.0, (end_t - start_t))
            pacing_bonus = min(15.0, max(0.0, (words_per_sec - 2.2) * 5.0))

            # F. Peak Centering Bonus: Give bonus if a major scream/laugh spike is inside the climax zone (25% to 75% of clip)
            peak_center_bonus = 0.0
            mid_start = start_t + (window_size * 0.20)
            mid_end = start_t + (window_size * 0.80)
            peaks_in_mid = sum(1 for pt in peak_times if mid_start <= pt <= mid_end)
            if peaks_in_mid > 0:
                peak_center_bonus = min(15.0, peaks_in_mid * 5.0)

            # Combined Virality Calculation
            raw_score = (
                (hype_score * 0.45) +
                (semantic_bonus * 0.30) +
                (hook_bonus * 0.10) +
                (pacing_bonus * 0.08) +
                (peak_center_bonus * 0.07)
            )
            virality_score = min(99.5, max(15.0, round(raw_score, 1)))

            # Extract normalized words relative to clip start
            clip_words = []
            for s in clip_transcript_segments:
                for w in s.get("words", []):
                    if start_t <= w["start"] <= end_t:
                        clip_words.append({
                            "word": w["word"],
                            "start": max(0.0, round(w["start"] - start_t, 2)),
                            "end": max(0.0, round(w["end"] - start_t, 2))
                        })

            raw_candidates.append({
                "start": round(start_t, 2),
                "end": round(end_t, 2),
                "duration": round(end_t - start_t, 2),
                "virality_score": virality_score,
                "hype_score": hype_score,
                "text": clip_text or "Insane Reaction Highlight",
                "words": clip_words,
            })

            start_t += step_seconds

        if not raw_candidates:
            # Safe fallback if empty
            return [{
                "rank": 1,
                "start": 0.0,
                "end": min(target_clip_duration, total_duration),
                "duration": min(target_clip_duration, total_duration),
                "virality_score": 85.0,
                "hype_score": 80.0,
                "text": "Stream Highlight",
                "words": []
            }]

        # 2. Sort by True Virality / Comedy Score
        raw_candidates.sort(key=lambda x: x["virality_score"], reverse=True)

        # 3. Intelligent Diverse Peak Moment Picker:
        # Prevent clips from overlapping or being consecutive slices!
        # Requires significant time separation between top moments across the stream.
        selected_clips = []
        min_gap_seconds = max(45.0, total_duration / (num_clips * 2.5))

        for cand in raw_candidates:
            # Check if this candidate is too close to an already chosen peak
            is_too_close = False
            for sel in selected_clips:
                # Do not select if overlapping or closer than min_gap
                overlap = max(cand["start"], sel["start"]) < min(cand["end"], sel["end"])
                distance = abs(cand["start"] - sel["start"])
                if overlap or distance < min_gap_seconds:
                    is_too_close = True
                    break

            if not is_too_close:
                cand["rank"] = len(selected_clips) + 1
                selected_clips.append(cand)
                if len(selected_clips) >= num_clips:
                    break

        # If not enough separated candidates found (e.g. shorter video), pick next best non-overlapping
        if len(selected_clips) < num_clips:
            for cand in raw_candidates:
                if cand not in selected_clips:
                    overlap = any(max(cand["start"], s["start"]) < min(cand["end"], s["end"]) for s in selected_clips)
                    if not overlap:
                        cand["rank"] = len(selected_clips) + 1
                        selected_clips.append(cand)
                        if len(selected_clips) >= num_clips:
                            break

        # 4. Final Rank Assignment (Rank 1 = Highest Virality, Rank 2 = Second Highest...)
        selected_clips.sort(key=lambda x: x["virality_score"], reverse=True)
        for idx, clip in enumerate(selected_clips):
            clip["rank"] = idx + 1

        print(f"[ClipExtractor] Successfully picked top {len(selected_clips)} viral highlight moments:")
        for c in selected_clips:
            print(f"  -> Rank #{c['rank']}: {c['start']}s to {c['end']}s | Virality: {c['virality_score']}% | Hype: {c['hype_score']}% | Text: {c['text'][:50]}...")

        return selected_clips
