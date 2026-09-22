import os
import sys
import json
import subprocess
from pathlib import Path
from backend.config import TEMP_DIR

# Ensure stdout and stderr handle all Unicode and emoji characters without Windows charmap crashes
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def safe_log(msg: str):
    """Safely prints log messages preventing any Windows cp1252 charmap encoding crashes."""
    try:
        print(msg)
    except Exception:
        try:
            print(msg.encode("ascii", "replace").decode("ascii"))
        except Exception:
            pass

class YouTubeDownloader:
    def __init__(self, output_dir=TEMP_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_info(self, url: str) -> dict:
        """Extract video metadata without downloading full media, supporting full UTF-8 emojis."""
        try:
            import yt_dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    "id": info.get("id"),
                    "title": info.get("title", "Stream Highlight"),
                    "uploader": info.get("uploader") or info.get("channel") or "Streamer",
                    "uploader_url": info.get("uploader_url") or info.get("channel_url") or "",
                    "duration": info.get("duration", 0),
                    "thumbnail": info.get("thumbnail"),
                    "description": info.get("description", ""),
                    "view_count": info.get("view_count", 0),
                }
        except Exception:
            # Fallback to subprocess with explicit utf-8 encoding and error replacement
            try:
                cmd = ["yt-dlp", "--dump-json", "--no-playlist", url]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    encoding="utf-8",
                    errors="replace",
                    env=dict(os.environ, PYTHONIOENCODING="utf-8"),
                    check=True
                )
                info = json.loads(result.stdout)
                return {
                    "id": info.get("id"),
                    "title": info.get("title", "Stream Highlight"),
                    "uploader": info.get("uploader") or info.get("channel") or "Streamer",
                    "uploader_url": info.get("uploader_url") or info.get("channel_url") or "",
                    "duration": info.get("duration", 0),
                    "thumbnail": info.get("thumbnail"),
                    "description": info.get("description", ""),
                    "view_count": info.get("view_count", 0),
                }
            except Exception as e2:
                raise RuntimeError(f"Failed to fetch video info: {e2}")

    def download_fast_audio_for_analysis(self, url: str, video_id: str) -> str:
        """
        Downloads lightweight 16kHz mono audio directly from YouTube in seconds
        even for 12-hour mega streams.
        """
        audio_path = self.output_dir / f"{video_id}.wav"
        if audio_path.exists():
            return str(audio_path)

        # Download audio-only stream directly to 16kHz WAV
        cmd = [
            "yt-dlp",
            "-f", "ba/b",
            "-x",
            "--audio-format", "wav",
            "--postprocessor-args", "ffmpeg:-ar 16000 -ac 1",
            "-o", str(self.output_dir / f"{video_id}.%(ext)s"),
            "--no-playlist",
            url
        ]
        subprocess.run(cmd, check=True, capture_output=True, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        return str(audio_path)

    def download_clip_section(self, url: str, video_id: str, start_time: float, duration: float, clip_id: str) -> str:
        """
        Downloads ONLY the specific 30-60 second slice directly from YouTube,
        saving 99% of bandwidth and rendering in seconds!
        """
        clip_section_path = self.output_dir / f"{clip_id}_raw.mp4"
        if clip_section_path.exists():
            return str(clip_section_path)

        start_sec = max(0, int(start_time))
        end_sec = int(start_time + duration + 1)
        
        # Download targeted time slice
        cmd = [
            "yt-dlp",
            "--download-sections", f"*{start_sec}-{end_sec}",
            "-f", "bv*[height<=1080]+ba/b[height<=1080]/best",
            "--merge-output-format", "mp4",
            "-o", str(clip_section_path),
            "--no-playlist",
            url
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
            return str(clip_section_path)
        except Exception as e:
            safe_log(f"[Downloader] Section download notice: {e}, falling back to full stream slice...")
            return None

    def download_video_and_audio(self, url: str, video_id: str = None) -> dict:
        """
        Optimized downloader: For shorter videos, downloads 720p/1080p fast.
        For long streams, downloads audio track first for instant scanning.
        """
        if not video_id:
            info = self.extract_info(url)
            video_id = info["id"]
        else:
            info = self.extract_info(url)

        duration = info.get("duration", 0)
        audio_path = self.output_dir / f"{video_id}.wav"
        video_path = self.output_dir / f"{video_id}.mp4"

        # Download Audio for speech & hype detection
        if not audio_path.exists():
            safe_log(f"[Downloader] Extracting audio stream for '{info.get('title')}' ({duration}s)...")
            audio_cmd = [
                "yt-dlp",
                "-f", "ba/b",
                "-x",
                "--audio-format", "wav",
                "--postprocessor-args", "ffmpeg:-ar 16000 -ac 1",
                "-o", str(self.output_dir / f"{video_id}.%(ext)s"),
                "--no-playlist",
                url
            ]
            subprocess.run(audio_cmd, check=True, capture_output=True, env=dict(os.environ, PYTHONIOENCODING="utf-8"))

        # For videos under 20 minutes, download full video. For longer streams, we snip on demand!
        if duration <= 1200 and not video_path.exists():
            download_cmd = [
                "yt-dlp",
                "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
                "--merge-output-format", "mp4",
                "-o", str(video_path),
                "--no-playlist",
                url
            ]
            subprocess.run(download_cmd, check=True, capture_output=True, env=dict(os.environ, PYTHONIOENCODING="utf-8"))

        return {
            "info": info,
            "video_path": str(video_path) if video_path.exists() else None,
            "audio_path": str(audio_path),
            "video_id": video_id,
            "is_long_stream": bool(duration > 1200)
        }
