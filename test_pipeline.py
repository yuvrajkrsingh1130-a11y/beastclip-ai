import os
import sys
import numpy as np
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from backend.config import SUBTITLE_PRESETS, CREATOR_PRESETS, OUTPUT_DIR, TEMP_DIR
from backend.energy_detector import AudioEnergyDetector
from backend.clip_extractor import ClipExtractor
from backend.subtitle_generator import SubtitleGenerator
from backend.metadata_generator import MetadataGenerator
from backend.thumbnail_maker import ThumbnailMaker

def run_tests():
    print("[1/5] Testing Subtitle Generator...")
    sub_gen = SubtitleGenerator("hormozi")
    test_words = [
        {"word": "Bro", "start": 0.0, "end": 0.4},
        {"word": "look", "start": 0.4, "end": 0.8},
        {"word": "at", "start": 0.8, "end": 1.0},
        {"word": "this", "start": 1.0, "end": 1.3},
        {"word": "insane", "start": 1.3, "end": 1.8},
        {"word": "speed", "start": 1.8, "end": 2.2},
        {"word": "clutch", "start": 2.2, "end": 2.6}
    ]
    test_ass = TEMP_DIR / "test_subs.ass"
    sub_gen.create_ass_subtitles(test_words, str(test_ass))
    assert test_ass.exists(), "ASS subtitle file was not created"
    print("  -> Subtitles OK!")

    print("[2/5] Testing Metadata Generator...")
    meta_gen = MetadataGenerator()
    meta = meta_gen.generate_clip_metadata(
        clip_text="bro look at this insane speed clutch",
        original_title="IShowSpeed Plays EA FC 24 and Rages",
        uploader="IShowSpeed",
        uploader_url="https://www.youtube.com/@IShowSpeed",
        rank=1
    )
    assert "@IShowSpeed" in meta["creator_credit"] or "IShowSpeed" in meta["title"]
    assert "#Shorts" in meta["tags"]
    print("  -> Metadata OK!")

    print("[3/5] Testing Clip Extractor & Virality Scoring...")
    extractor = ClipExtractor()
    dummy_transcripts = {
        "segments": [
            {
                "id": 1,
                "start": 5.0,
                "end": 25.0,
                "text": "Bro wait no way what just happened look at speed",
                "words": test_words
            }
        ]
    }
    dummy_timeline = [{"time": float(i), "energy": 0.8 if 5 <= i <= 20 else 0.1, "is_spike": 5 <= i <= 20} for i in range(40)]
    clips = extractor.extract_top_highlights(dummy_transcripts, dummy_timeline, total_duration=40.0, target_clip_duration=30, num_clips=2)
    assert len(clips) >= 1
    print(f"  -> Extracted {len(clips)} highlights with virality score: {clips[0]['virality_score']}% OK!")

    print("[4/5] Testing Thumbnail Maker...")
    thumb_maker = ThumbnailMaker()
    test_thumb = OUTPUT_DIR / "test_thumb.jpg"
    thumb_maker.generate_vertical_thumbnail(None, meta["title"], str(test_thumb))
    assert test_thumb.exists()
    print("  -> Thumbnail OK!")

    print("\n[ALL TESTS PASSED SUCCESSFULLY!]")

if __name__ == "__main__":
    run_tests()
