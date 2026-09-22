import os
import asyncio
import subprocess
from pathlib import Path

class VoiceoverStudio:
    def __init__(self, temp_dir: Path):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def generate_ai_voiceover(self, text: str, voice: str = "en-US-GuyNeural") -> str:
        """
        Generates realistic voiceover audio using edge-tts.
        """
        try:
            import edge_tts
            output_audio_path = self.temp_dir / f"tts_{abs(hash(text)) % 100000}.wav"
            communicate = edge_tts.Communicate(text, voice)
            mp3_path = self.temp_dir / f"tts_{abs(hash(text)) % 100000}.mp3"
            await communicate.save(str(mp3_path))

            # Convert to WAV
            subprocess.run([
                "ffmpeg", "-y", "-i", str(mp3_path),
                "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2",
                str(output_audio_path)
            ], check=True, capture_output=True)

            return str(output_audio_path)
        except Exception as e:
            print(f"[VoiceoverStudio] TTS generation failed: {e}")
            return None

    def mix_voiceover_with_ducking(self, base_video_path: str, voiceover_audio_path: str, output_video_path: str):
        """
        Mixes user voiceover/commentary over the clip video with smart audio ducking
        (reducing the original video sound by 75% so the voice is crystal clear).
        """
        # FFmpeg sidechaincompress / amix filter graph
        filter_complex = (
            "[0:a]volume=0.25[bg];"
            "[1:a]volume=1.3[fg];"
            "[bg][fg]amix=inputs=2:duration=first:dropout_transition=2[aout]"
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
            "-b:a", "192k",
            "-shortest",
            output_video_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_video_path
