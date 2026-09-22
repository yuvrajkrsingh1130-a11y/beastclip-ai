import os
import asyncio
import subprocess
from pathlib import Path

VOICE_PROFILES = {
    "hype_trailer": {
        "voice": "en-US-ChristopherNeural",
        "rate": "+4%",
        "pitch": "-4Hz",
        "name": "🎙️ Movie Trailer Hype Announcer"
    },
    "energetic_streamer": {
        "voice": "en-US-GuyNeural",
        "rate": "+10%",
        "pitch": "+0Hz",
        "name": "🔥 Energetic Streamer / Storyteller"
    },
    "tiktok_girl": {
        "voice": "en-US-JennyNeural",
        "rate": "+6%",
        "pitch": "+2Hz",
        "name": "✨ Viral TikTok Female"
    },
    "anime_villain": {
        "voice": "en-US-EricNeural",
        "rate": "-2%",
        "pitch": "-10Hz",
        "name": "⚡ Deep Anime Villain / Narrator"
    },
    "british_documentary": {
        "voice": "en-GB-RyanNeural",
        "rate": "+5%",
        "pitch": "+0Hz",
        "name": "🌟 British High-Society Narrator"
    },
    "mrbeast_action": {
        "voice": "en-US-AndrewNeural",
        "rate": "+14%",
        "pitch": "+2Hz",
        "name": "🚀 MrBeast Action Style"
    },
    "cyber_ai": {
        "voice": "en-US-AnaNeural",
        "rate": "+8%",
        "pitch": "+0Hz",
        "name": "🤖 Cyberpunk AI Voice"
    }
}

class VoiceoverStudio:
    def __init__(self, temp_dir: Path):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def generate_ai_voiceover(self, text: str, voice_key: str = "hype_trailer") -> str:
        """
        Generates studio-mastered, high-impact broadcast voiceover audio using edge-tts and DSP mastering.
        """
        try:
            import edge_tts
            
            profile = VOICE_PROFILES.get(voice_key)
            if profile:
                voice_name = profile["voice"]
                rate = profile.get("rate", "+0%")
                pitch = profile.get("pitch", "+0Hz")
            else:
                voice_name = voice_key if "Neural" in voice_key else "en-US-ChristopherNeural"
                rate = "+6%"
                pitch = "-2Hz"

            raw_mp3_path = self.temp_dir / f"tts_raw_{abs(hash(text + voice_name)) % 100000}.mp3"
            mastered_wav_path = self.temp_dir / f"tts_master_{abs(hash(text + voice_name)) % 100000}.wav"

            communicate = edge_tts.Communicate(text, voice_name, rate=rate, pitch=pitch)
            await communicate.save(str(raw_mp3_path))

            # Studio Audio DSP Chain:
            # 1. highpass=f=80 (cut sub-rumble)
            # 2. equalizer f=300 (cut mud)
            # 3. equalizer f=3400 (boost vocal presence/clarity)
            # 4. equalizer f=9000 (air brilliance)
            # 5. compand (aggressive punchy broadcast compressor)
            # 6. loudnorm (YouTube broadcast loudness mastering: -14 LUFS)
            dsp_filter = (
                "highpass=f=80,"
                "equalizer=f=300:t=q:w=1.2:g=-3,"
                "equalizer=f=3400:t=q:w=1.5:g=4.5,"
                "equalizer=f=9000:t=q:w=1.0:g=3.0,"
                "compand=attacks=0.01:decays=0.08:points=-80/-80|-35/-18|-15/-6|0/-1:gain=4.5,"
                "loudnorm=I=-14:TP=-1.5:LRA=7"
            )

            cmd = [
                "ffmpeg", "-y",
                "-i", str(raw_mp3_path),
                "-af", dsp_filter,
                "-acodec", "pcm_s16le",
                "-ar", "44100",
                "-ac", "2",
                str(mastered_wav_path)
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            return str(mastered_wav_path)
        except Exception as e:
            print(f"[VoiceoverStudio] Studio TTS mastering failed: {e}")
            return None

    def mix_voiceover_with_ducking(self, base_video_path: str, voiceover_audio_path: str, output_video_path: str):
        """
        Mixes studio-mastered voiceover over the clip video with dynamic sidechain ducking
        (reducing original video audio to 20% while elevating voice with crystal clear punch).
        """
        # Multi-stage audio mix with ducking and limiter
        filter_complex = (
            "[0:a]volume=0.20[bg];"
            "[1:a]volume=1.45[fg];"
            "[bg][fg]amix=inputs=2:duration=first:dropout_transition=2,alimiter=limit=0.95[aout]"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", base_video_path,
            "-i", voiceover_audio_path,
            "-filter_complex", filter_complex,
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "256k",
            "-shortest",
            output_video_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_video_path
