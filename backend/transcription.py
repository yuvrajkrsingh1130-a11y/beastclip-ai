import os
import re

STREAMER_SLANG_CORRECTIONS = {
    # Speed / Ronaldo / Football
    "sewy": "SIUUU",
    "sui": "SIUUU",
    "suiii": "SIUUU",
    "siu": "SIUUU",
    "siuuu": "SIUUU",
    "siuu": "SIUUU",
    "ishowspeed": "IShowSpeed",
    "speed": "Speed",
    "ronaldo": "Ronaldo",
    "cristiano": "Cristiano",
    "cr7": "CR7",
    "bellingham": "Bellingham",
    "messi": "Messi",
    
    # Kai Cenat & AMP
    "kaicenat": "Kai Cenat",
    "cenat": "Cenat",
    "amp": "AMP",
    "dukedennis": "Duke Dennis",
    "fanum": "Fanum",
    "agent00": "Agent 00",
    "mafiathon": "Mafiathon",
    "glip": "glip",

    # Jynxzi & CaseOh
    "jynxzi": "Jynxzi",
    "caseoh": "CaseOh",
    
    # Gen-Z & Streamer Slang
    "rizz": "RIZZ",
    "wrizz": "W RIZZ",
    "lrizz": "L RIZZ",
    "gyatt": "GYATT",
    "gyat": "GYATT",
    "ong": "ON GOD",
    "fr": "FR",
    "cap": "CAP",
    "nocap": "NO CAP",
    "cooked": "COOKED",
    "crashout": "CRASH OUT",
    "clutch": "CLUTCH",
    "wr": "W ART",
    "w-r": "W ART",
    "wart": "W ART",
    "w-art": "W ART",
    "l-art": "L ART",
    "lart": "L ART",
    "wchat": "W CHAT",
    "lchat": "L CHAT",
    "wman": "W MAN",
    "lman": "L MAN",
    "wmans": "W MANS",
    "lmans": "L MANS",
    "wplay": "W PLAY",
    "lplay": "L PLAY",
    "wstream": "W STREAM",
    "lstream": "L STREAM",
    "bro": "BRO",
    "bruh": "BRUH",
    "chat": "CHAT",
    "skibidi": "SKIBIDI",
    "sigma": "SIGMA",
    "mewing": "MEWING",
    "mrbeast": "MrBeast"
}

PHRASE_REPLACEMENTS = [
    (r"(?i)\bwe are home\b", "OH MY GOD RONALDO"),
    (r"(?i)\bwe're home\b", "OH MY GOD RONALDO"),
    (r"(?i)\bwere home\b", "OH MY GOD RONALDO"),
    (r"(?i)\bwhere home\b", "OH MY GOD RONALDO"),
    (r"(?i)\bwhat's the word bro\b", "WHAT'S UP BRO"),
    (r"(?i)\bwhats the word bro\b", "WHAT'S UP BRO"),
    (r"(?i)\bthere is no way\b", "AIN'T NO WAY"),
    (r"(?i)\bis no way\b", "AIN'T NO WAY"),
    (r"(?i)\baint no way\b", "AIN'T NO WAY"),
    (r"(?i)\bon god\b", "ON GOD"),
    (r"(?i)\bfor real for real\b", "FR FR"),
    (r"(?i)\bfor real\b", "FOR REAL"),
    (r"(?i)\bno cap\b", "NO CAP"),
    (r"(?i)\btype of shit\b", "TYPE SHIT"),
    (r"(?i)\btype stuff\b", "TYPE SHIT"),
    (r"(?i)\bmy bad\b", "MY FAULT"),
    (r"(?i)\bhe is him\b", "HE'S HIM"),
    (r"(?i)\bcrashing out\b", "CRASHING OUT"),
    (r"(?i)\bcrash out\b", "CRASH OUT"),
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
    def __init__(self, model_size="base.en", device="cpu", compute_type="int8"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None

    def _load_model(self):
        if self.model is None:
            try:
                from faster_whisper import WhisperModel
                print(f"[Transcriber] Loading faster-whisper model '{self.model_size}' (cpu_threads=6)...")
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type,
                    cpu_threads=6,
                    num_workers=1
                )
            except Exception as e:
                print(f"[Transcriber] Primary model load notice ({e}), falling back to 'base.en'...")
                try:
                    from faster_whisper import WhisperModel
                    self.model = WhisperModel(
                        "base.en",
                        device=self.device,
                        compute_type=self.compute_type,
                        cpu_threads=6,
                        num_workers=1
                    )
                except Exception as e2:
                    print(f"[Transcriber] Fallback load error: {e2}")
                    self.model = "fallback"

    def transcribe(
        self,
        audio_path: str,
        video_title: str = "",
        uploader: str = "",
        context_prompt: str = "",
        is_clip_slice: bool = False
    ) -> dict:
        """
        High-precision transcription with word timestamps, greedy decoding for max speed,
        sensitive acoustic thresholds for capturing small talk/whispers + screams,
        and modern streamer vernacular conditioning.
        """
        self._load_model()

        if self.model != "fallback":
            try:
                # Dynamic conditioning prompt from video metadata & modern streamer vocabulary
                prompt_items = [
                    "IShowSpeed", "Cristiano Ronaldo", "Ronaldo", "Kai Cenat", "Jynxzi", "CaseOh",
                    "SIUUU", "bro", "chat", "rizz", "gyatt", "ain't no way", "on god", "fr", "no cap",
                    "crash out", "cooked", "W art", "L art", "W chat", "L chat", "W bro", "oh my god",
                    "no way", "Portugal"
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

                # When transcribing an extracted clip slice, disable VAD filtering completely
                # so that quiet small talk, whispering, rapid muttering, and trailing screams are NEVER dropped!
                use_vad = not is_clip_slice
                vad_params = dict(min_silence_duration_ms=600, speech_pad_ms=300, threshold=0.2) if use_vad else None

                # Ultra-fast greedy decoding: beam_size=1, best_of=1, temperature=0.0
                segments, info = self.model.transcribe(
                    str(audio_path),
                    word_timestamps=True,
                    beam_size=1,
                    best_of=1,
                    temperature=0.0,
                    condition_on_previous_text=False,
                    initial_prompt=initial_prompt,
                    vad_filter=use_vad,
                    vad_parameters=vad_params,
                    no_speech_threshold=0.30,
                    compression_ratio_threshold=2.4,
                    log_prob_threshold=-1.0
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
                                "start": round(float(w.start), 2),
                                "end": round(float(w.end), 2),
                                "probability": round(float(w.probability), 2) if hasattr(w, "probability") else 1.0
                            })
                    
                    seg_raw_text = " ".join([w["word"] for w in seg_words]) if seg_words else seg.text.strip()
                    seg_clean_text = post_process_transcript_text(seg_raw_text)

                    seg_data = {
                        "id": seg.id,
                        "start": round(float(seg.start), 2),
                        "end": round(float(seg.end), 2),
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
                print(f"[Transcriber] Whisper primary transcribe notice: {e}, retrying with standard baseline...")
                try:
                    segments, info = self.model.transcribe(
                        str(audio_path),
                        word_timestamps=True,
                        beam_size=2,
                        temperature=0.0
                    )
                    all_segments = []
                    full_text_list = []
                    for seg in segments:
                        seg_words = []
                        if seg.words:
                            for w in seg.words:
                                seg_words.append({
                                    "word": normalize_slang(w.word.strip()),
                                    "start": round(float(w.start), 2),
                                    "end": round(float(w.end), 2),
                                    "probability": 1.0
                                })
                        seg_clean = post_process_transcript_text(seg.text.strip())
                        all_segments.append({
                            "id": seg.id,
                            "start": round(float(seg.start), 2),
                            "end": round(float(seg.end), 2),
                            "text": seg_clean,
                            "words": seg_words
                        })
                        full_text_list.append(seg_clean)
                    return {
                        "language": getattr(info, "language", "en"),
                        "language_probability": getattr(info, "language_probability", 1.0),
                        "duration": getattr(info, "duration", 0),
                        "text": " ".join(full_text_list),
                        "segments": all_segments
                    }
                except Exception as e2:
                    print(f"[Transcriber] Whisper retry error: {e2}")

        # Fallback empty transcript if audio is completely silent
        return {
            "language": "en",
            "language_probability": 1.0,
            "duration": 60.0,
            "text": "",
            "segments": []
        }

    def transcribe_candidate_regions(
        self,
        audio_path: str,
        regions: list,
        video_title: str = "",
        uploader: str = ""
    ) -> dict:
        """
        Ultra-fast targeted transcription for long streams:
        Instead of transcribing 1-2 hours of quiet gameplay, slices only the top candidate
        reaction/scream regions and transcribes them in seconds with exact stream timestamps!
        """
        import wave
        from pathlib import Path
        temp_dir = Path(audio_path).parent

        all_segments = []
        full_text_list = []
        seg_id_counter = 0

        try:
            with wave.open(str(audio_path), "rb") as wf:
                params = wf.getparams()
                sample_rate = wf.getframerate()
                total_frames = wf.getnframes()

                for idx, r in enumerate(regions):
                    start_sec = r["start"]
                    dur_sec = r["duration"]
                    start_frame = max(0, min(total_frames - 1, int(start_sec * sample_rate)))
                    num_frames = min(int(dur_sec * sample_rate), total_frames - start_frame)
                    if num_frames <= 0:
                        continue

                    slice_wav = temp_dir / f"scan_slice_{idx}.wav"
                    try:
                        wf.setpos(start_frame)
                        frames = wf.readframes(num_frames)
                        with wave.open(str(slice_wav), "wb") as out_wf:
                            out_wf.setparams(params)
                            out_wf.writeframes(frames)

                        slice_res = self.transcribe(
                            str(slice_wav),
                            video_title=video_title,
                            uploader=uploader,
                            is_clip_slice=True
                        )

                        for s in slice_res.get("segments", []):
                            seg_id_counter += 1
                            aligned_words = []
                            for w in s.get("words", []):
                                aligned_words.append({
                                    "word": w["word"],
                                    "start": round(start_sec + w["start"], 2),
                                    "end": round(start_sec + w["end"], 2),
                                    "probability": w.get("probability", 1.0)
                                })
                            all_segments.append({
                                "id": seg_id_counter,
                                "start": round(start_sec + s["start"], 2),
                                "end": round(start_sec + s["end"], 2),
                                "text": s["text"],
                                "words": aligned_words
                            })
                            full_text_list.append(s["text"])
                    finally:
                        if slice_wav.exists():
                            try:
                                slice_wav.unlink()
                            except Exception:
                                pass
        except Exception as e:
            print(f"[Transcriber] transcribe_candidate_regions notice: {e}, falling back to direct transcribe...")
            return self.transcribe(audio_path, video_title=video_title, uploader=uploader)

        all_segments.sort(key=lambda x: x["start"])

        return {
            "language": "en",
            "language_probability": 1.0,
            "duration": regions[-1].get("end", regions[-1]["start"] + regions[-1]["duration"]) if regions else 60.0,
            "text": " ".join(full_text_list),
            "segments": all_segments
        }

