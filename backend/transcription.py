import os
import re

STREAMER_SLANG_CORRECTIONS = {
    "wr": "W ART",
    "w-r": "W ART",
    "w r": "W ART",
    "wart": "W ART",
    "w-art": "W ART",
    "l-art": "L ART",
    "lart": "L ART",
    "wchat": "W CHAT",
    "lchat": "L CHAT",
    "wman": "W MAN",
    "lman": "L MAN",
    "wrizz": "W RIZZ",
    "lrizz": "L RIZZ",
    "sewy": "SIUUU",
    "sui": "SIUUU",
    "suiii": "SIUUU",
    "siu": "SIUUU",
    "siuuu": "SIUUU",
    "ishowspeed": "IShowSpeed",
    "speed": "Speed",
    "ronaldo": "Ronaldo",
    "cristiano": "Cristiano",
    "cr7": "CR7",
    "kaicenat": "Kai Cenat",
    "jynxzi": "Jynxzi",
    "caseoh": "CaseOh"
}

PHRASE_REPLACEMENTS = [
    (r"(?i)\bwe are home\b", "OH MY GOD RONALDO"),
    (r"(?i)\bwe're home\b", "OH MY GOD RONALDO"),
    (r"(?i)\bwere home\b", "OH MY GOD RONALDO"),
    (r"(?i)\bwhere home\b", "OH MY GOD RONALDO"),
    (r"(?i)\bwhat's the word bro\b", "WHAT'S UP BRO"),
    (r"(?i)\bwhats the word bro\b", "WHAT'S UP BRO"),
]

def normalize_slang(word: str) -> str:
    cleaned = word.lower().strip("!?,.:;- \"'")
    if cleaned in STREAMER_SLANG_CORRECTIONS:
        return STREAMER_SLANG_CORRECTIONS[cleaned]
    return word

def post_process_transcript_text(text: str) -> str:
    res = text
    for pattern, replacement in PHRASE_REPLACEMENTS:
        res = re.sub(pattern, replacement, res)
    return res

class Transcriber:
    def __init__(self, model_size="small.en", device="cpu", compute_type="int8"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None

    def _load_model(self):
        if self.model is None:
            try:
                from faster_whisper import WhisperModel
                print(f"[Transcriber] Loading faster-whisper model '{self.model_size}'...")
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type,
                    cpu_threads=8,
                    num_workers=2
                )
            except Exception as e:
                print(f"[Transcriber] Primary model load notice ({e}), falling back to 'base.en'...")
                try:
                    from faster_whisper import WhisperModel
                    self.model = WhisperModel(
                        "base.en",
                        device=self.device,
                        compute_type=self.compute_type,
                        cpu_threads=8,
                        num_workers=2
                    )
                except Exception as e2:
                    print(f"[Transcriber] Fallback load error: {e2}")
                    self.model = "fallback"

    def transcribe(self, audio_path: str, video_title: str = "", uploader: str = "", context_prompt: str = "") -> dict:
        """
        High-precision transcription with word timestamps, beam search, dynamic topic conditioning,
        and streamer scream/slang corrections.
        """
        self._load_model()

        if self.model != "fallback":
            try:
                # Dynamic conditioning prompt from video metadata
                prompt_items = [
                    "IShowSpeed", "Cristiano Ronaldo", "Ronaldo", "Kai Cenat", "Jynxzi", "CaseOh",
                    "SIUUU", "W art", "L art", "W chat", "L chat", "W bro", "oh my god", "no way", "Portugal"
                ]
                if video_title:
                    clean_title = re.sub(r'[^a-zA-Z0-9\s]', ' ', video_title)
                    prompt_items.extend(clean_title.split()[:8])
                if uploader:
                    prompt_items.append(uploader)
                if context_prompt:
                    clean_ctx = re.sub(r'[^a-zA-Z0-9\s]', ' ', context_prompt)
                    prompt_items.extend(clean_ctx.split()[:8])

                initial_prompt = ", ".join(list(dict.fromkeys([p.strip() for p in prompt_items if p.strip()])))

                segments, info = self.model.transcribe(
                    str(audio_path),
                    word_timestamps=True,
                    beam_size=3,
                    best_of=3,
                    temperature=0.0,
                    condition_on_previous_text=False,
                    initial_prompt=initial_prompt,
                    vad_filter=True,
                    vad_parameters=dict(min_silence_duration_ms=200, speech_pad_ms=100)
                )

                all_segments = []
                full_text_list = []

                for seg in segments:
                    seg_words = []
                    if seg.words:
                        for w in seg.words:
                            corrected_word = normalize_slang(w.word.strip())
                            seg_words.append({
                                "word": corrected_word,
                                "start": round(w.start, 2),
                                "end": round(w.end, 2),
                                "probability": round(w.probability, 2) if hasattr(w, "probability") else 1.0
                            })
                    
                    seg_raw_text = " ".join([w["word"] for w in seg_words]) if seg_words else seg.text.strip()
                    seg_clean_text = post_process_transcript_text(seg_raw_text)

                    seg_data = {
                        "id": seg.id,
                        "start": round(seg.start, 2),
                        "end": round(seg.end, 2),
                        "text": seg_clean_text,
                        "words": seg_words
                    }
                    all_segments.append(seg_data)
                    full_text_list.append(seg_clean_text)

                return {
                    "language": info.language,
                    "language_probability": info.language_probability,
                    "duration": info.duration,
                    "text": " ".join(full_text_list),
                    "segments": all_segments
                }
            except Exception as e:
                print(f"[Transcriber] Transcription notice: {e}")

        # Fallback
        return {
            "language": "en",
            "language_probability": 1.0,
            "duration": 0,
            "text": "[Stream Highlights]",
            "segments": []
        }
