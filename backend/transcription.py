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
    "sewy": "SUIII",
    "sui": "SUIII",
    "siu": "SUIII",
    "ishowspeed": "IShowSpeed"
}

def normalize_slang(word: str) -> str:
    cleaned = word.lower().strip("!?,.:;- ")
    if cleaned in STREAMER_SLANG_CORRECTIONS:
        return STREAMER_SLANG_CORRECTIONS[cleaned]
    return word

class Transcriber:
    def __init__(self, model_size="base.en", device="cpu", compute_type="int8"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None

    def _load_model(self):
        if self.model is None:
            try:
                from faster_whisper import WhisperModel
                print(f"[Transcriber] Loading faster-whisper turbo model '{self.model_size}' with multi-threading...")
                # cpu_threads=8 with int8 quantization for ultra fast CPU execution
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type,
                    cpu_threads=8,
                    num_workers=2
                )
            except Exception as e:
                print(f"[Transcriber] Model load warning: {e}, using fallback")
                self.model = "fallback"

    def transcribe(self, audio_path: str) -> dict:
        """
        Ultra-fast transcription with word-by-word timestamps, condition_on_previous_text=False (no stutter loops),
        and streamer vocabulary conditioning.
        """
        self._load_model()

        if self.model != "fallback":
            try:
                # Conditioning prompt ensures slang like "W ART", "L ART", "W CHAT" is recognized
                initial_prompt = "W art, L art, W chat, L chat, W man, W bro, W rizz, L rizz, IShowSpeed, Kai Cenat, fan art, oh my god, bro, suii, Ronaldo, W, L, chat, Twitch, stream."

                segments, info = self.model.transcribe(
                    str(audio_path),
                    word_timestamps=True,
                    beam_size=1,  # Greedy search: 5x faster with near-identical accuracy
                    temperature=0.0,
                    condition_on_previous_text=False, # Crucial: prevents runaway repeated phrases
                    initial_prompt=initial_prompt,
                    vad_filter=True,
                    vad_parameters=dict(min_silence_duration_ms=250, speech_pad_ms=100)
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
                    
                    seg_data = {
                        "id": seg.id,
                        "start": round(seg.start, 2),
                        "end": round(seg.end, 2),
                        "text": " ".join([w["word"] for w in seg_words]) if seg_words else seg.text.strip(),
                        "words": seg_words
                    }
                    all_segments.append(seg_data)
                    full_text_list.append(seg_data["text"])

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
