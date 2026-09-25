import os
import sys
import json
import shutil
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

def _get_base_ytdlp_args() -> list:
    """Returns resilient base yt-dlp arguments with JS runtime and anti-throttling options."""
    args = [
        "yt-dlp",
        "--no-playlist",
        "--retries", "5",
        "--fragment-retries", "5",
        "--socket-timeout", "30",
        "--no-check-certificates",
        "--extractor-args", "youtube:player_client=android,web",
    ]
    node_bin = shutil.which("node") or ("C:\\Program Files\\nodejs\\node.exe" if os.path.exists("C:\\Program Files\\nodejs\\node.exe") else None)
    if node_bin:
        args.extend(["--js-runtimes", f"node:{node_bin}"])
    return args

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
            node_bin = shutil.which("node") or ("C:\\Program Files\\nodejs\\node.exe" if os.path.exists("C:\\Program Files\\nodejs\\node.exe") else None)
            if node_bin:
                ydl_opts['js_runtimes'] = {'node': {'path': node_bin}}
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
                cmd = _get_base_ytdlp_args() + ["--dump-json", url]
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
        even for 12-hour mega streams. Multi-strategy pipeline guarantees 100% resilience.
        """
        audio_path = self.output_dir / f"{video_id}.wav"
        if audio_path.exists() and audio_path.stat().st_size > 10000:
            safe_log(f"[Downloader] Instant cache hit for audio: {audio_path.name} ({audio_path.stat().st_size} bytes)")
            return str(audio_path)

        base_cmd = _get_base_ytdlp_args()

        # Strategy 1: Direct yt-dlp 16kHz mono WAV extraction
        safe_log(f"[Downloader] Strategy 1: Direct audio stream extraction for {video_id}...")
        cmd1 = base_cmd + [
            "-f", "ba/ba*/bestaudio/b/best",
            "-x",
            "--audio-format", "wav",
            "--postprocessor-args", "ffmpeg:-ar 16000 -ac 1",
            "-o", str(self.output_dir / f"{video_id}.%(ext)s"),
            url
        ]
        try:
            res1 = subprocess.run(
                cmd1,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=dict(os.environ, PYTHONIOENCODING="utf-8")
            )
            if res1.returncode == 0 and audio_path.exists() and audio_path.stat().st_size > 10000:
                safe_log(f"[Downloader] Strategy 1 succeeded: {audio_path.name}")
                return str(audio_path)
            err_snippet = (res1.stderr or res1.stdout or "")[-300:].strip()
            safe_log(f"[Downloader] Strategy 1 returned code {res1.returncode}: {err_snippet}")
        except Exception as e1:
            safe_log(f"[Downloader] Strategy 1 error: {e1}")

        # Strategy 2: Download raw audio track directly, then convert with local ffmpeg
        safe_log(f"[Downloader] Strategy 2: Raw audio fetch + local ffmpeg conversion...")
        raw_pattern = self.output_dir / f"{video_id}_rawaudio.%(ext)s"
        cmd2 = base_cmd + [
            "-f", "ba/b/best",
            "-o", str(raw_pattern),
            url
        ]
        try:
            res2 = subprocess.run(
                cmd2,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=dict(os.environ, PYTHONIOENCODING="utf-8")
            )
            raw_candidates = list(self.output_dir.glob(f"{video_id}_rawaudio.*"))
            if raw_candidates:
                raw_file = raw_candidates[0]
                ff_cmd = [
                    "ffmpeg", "-y",
                    "-i", str(raw_file),
                    "-vn",
                    "-acodec", "pcm_s16le",
                    "-ar", "16000",
                    "-ac", "1",
                    str(audio_path)
                ]
                subprocess.run(ff_cmd, capture_output=True, check=True)
                try:
                    raw_file.unlink(missing_ok=True)
                except Exception:
                    pass
                if audio_path.exists() and audio_path.stat().st_size > 10000:
                    safe_log(f"[Downloader] Strategy 2 succeeded via local ffmpeg!")
                    return str(audio_path)
        except Exception as e2:
            safe_log(f"[Downloader] Strategy 2 error: {e2}")

        # Strategy 3: Alternative client profile (ios/mweb)
        safe_log(f"[Downloader] Strategy 3: Alternative client profile (ios,mweb)...")
        cmd3 = [
            "yt-dlp",
            "--no-playlist",
            "--extractor-args", "youtube:player_client=ios,mweb",
            "-f", "ba/b/best",
            "-x",
            "--audio-format", "wav",
            "--postprocessor-args", "ffmpeg:-ar 16000 -ac 1",
            "-o", str(self.output_dir / f"{video_id}.%(ext)s"),
            url
        ]
        try:
            subprocess.run(cmd3, capture_output=True, text=True, encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
            if audio_path.exists() and audio_path.stat().st_size > 10000:
                safe_log(f"[Downloader] Strategy 3 succeeded: {audio_path.name}")
                return str(audio_path)
        except Exception as e3:
            safe_log(f"[Downloader] Strategy 3 error: {e3}")

        # If audio_path exists despite non-zero exit code
        if audio_path.exists() and audio_path.stat().st_size > 10000:
            return str(audio_path)

        raise RuntimeError(f"Could not extract audio from {url}. Please check YouTube link or connection.")

    def download_clip_section(self, url: str, video_id: str, start_time: float, duration: float, clip_id: str) -> str:
        """
        Downloads ONLY the specific 30-60 second slice directly from YouTube,
        saving 99% of bandwidth and rendering in seconds!
        """
        clip_section_path = self.output_dir / f"{clip_id}_raw.mp4"
        if clip_section_path.exists() and clip_section_path.stat().st_size > 50000:
            return str(clip_section_path)

        start_sec = max(0, int(start_time))
        end_sec = int(start_time + duration + 1)
        base_cmd = _get_base_ytdlp_args()

        cmd = base_cmd + [
            "--download-sections", f"*{start_sec}-{end_sec}",
            "--force-keyframes-at-cuts",
            "-f", "18/best[ext=mp4][height<=720]/best[height<=1080]/best",
            "--merge-output-format", "mp4",
            "-o", str(clip_section_path),
            url
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
            if res.returncode == 0 and clip_section_path.exists() and clip_section_path.stat().st_size > 50000:
                return str(clip_section_path)
            # Try secondary format if primary merge failed
            cmd_fallback = base_cmd + [
                "--download-sections", f"*{start_sec}-{end_sec}",
                "-f", "best[height<=720]/best",
                "--merge-output-format", "mp4",
                "-o", str(clip_section_path),
                url
            ]
            res_fb = subprocess.run(cmd_fallback, capture_output=True, text=True, encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
            if clip_section_path.exists() and clip_section_path.stat().st_size > 50000:
                return str(clip_section_path)
            safe_log(f"[Downloader] Section download notice: {res_fb.stderr[:200] if res_fb.stderr else 'incomplete'}, falling back to full stream slice...")
            return None
        except Exception as e:
            safe_log(f"[Downloader] Section download exception: {e}, falling back to full stream slice...")
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
        video_path = self.output_dir / f"{video_id}.mp4"
        base_cmd = _get_base_ytdlp_args()

        # Download Audio for speech & hype detection with multi-strategy fallback
        audio_path = self.download_fast_audio_for_analysis(url, video_id)

        # For videos under 20 minutes, download full video. For longer streams, we snip on demand!
        if duration <= 1200 and not (video_path.exists() and video_path.stat().st_size > 100000):
            safe_log(f"[Downloader] Downloading full video stream for '{info.get('title')}' ({duration}s)...")
            download_cmd = base_cmd + [
                "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
                "--merge-output-format", "mp4",
                "-o", str(video_path),
                url
            ]
            try:
                subprocess.run(download_cmd, check=True, capture_output=True, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
            except Exception as e:
                safe_log(f"[Downloader] 1080p download notice: {e}, falling back to 720p/best...")
                fallback_cmd = base_cmd + [
                    "-f", "best[height<=720]/best",
                    "--merge-output-format", "mp4",
                    "-o", str(video_path),
                    url
                ]
                subprocess.run(fallback_cmd, check=True, capture_output=True, env=dict(os.environ, PYTHONIOENCODING="utf-8"))

        return {
            "info": info,
            "video_path": str(video_path) if (video_path.exists() and video_path.stat().st_size > 100000) else None,
            "audio_path": str(audio_path),
            "video_id": video_id,
            "is_long_stream": bool(duration > 1200)
        }
