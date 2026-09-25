import os
import subprocess
from pathlib import Path
from backend.config import BASE_DIR

class VideoRenderer:
    def __init__(self):
        pass

    def render_clip(
        self,
        source_video_path: str,
        start_time: float,
        duration: float,
        ass_subtitle_path: str,
        output_clip_path: str,
        cam_box: dict = None,
        layout: str = "split_screen",
        creator_credit: str = "@Creator",
        enable_copyright_protection: bool = True,
        enable_seamless_loop: bool = True
    ) -> str:
        """
        Renders a clean, high-performance 1080x1920 portrait Short with faststart streaming,
        zero-lag subtitle burn-in, and studio audio mastering.
        """
        if not cam_box:
            cam_box = {"x": 0.22, "y": 0.72, "w": 0.42, "h": 0.55}

        # Properly escape ASS path for Windows FFmpeg subtitles filter
        escaped_ass = Path(ass_subtitle_path).resolve().as_posix()
        if os.name == "nt":
            drive, rest = os.path.splitdrive(escaped_ass)
            if drive:
                escaped_ass = f"{drive[0]}\\:{rest}"

        # Clean, natural studio audio filter with strictly zero-based PTS
        audio_filter = (
            "asetpts=PTS-STARTPTS,"
            "aresample=async=1000,"
            "volume=1.15,"
            "aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo"
        )

        # Streamer webcam crop coordinates
        cam_cx = cam_box.get("x", 0.22)
        cam_cy = cam_box.get("y", 0.72)
        
        crop_cam_w = "iw*0.48"
        crop_cam_h = "ih*0.58"
        crop_cam_x = f"max(0, min(iw - {crop_cam_w}, (iw * {cam_cx}) - ({crop_cam_w} / 2)))"
        crop_cam_y = f"max(0, min(ih - {crop_cam_h}, (ih * {cam_cy}) - ({crop_cam_h} / 2)))"

        crop_screen_w = "iw*0.75"
        crop_screen_h = "ih*0.78"
        crop_screen_x = "iw*0.22" if cam_cx < 0.5 else "iw*0.04"
        crop_screen_y = "ih*0.04"

        # Build Video Filter Graph (Split Screen default, or PiP, or Blurred)
        if layout == "gaming_pip":
            vf = (
                f"[0:v]setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[bg];"
                f"[0:v]setpts=PTS-STARTPTS,crop=w={crop_cam_w}:h={crop_cam_h}:x='{crop_cam_x}':y='{crop_cam_y}',scale=380:440:force_original_aspect_ratio=increase,crop=380:440[cam];"
                f"[bg][cam]overlay=W-w-36:48[merged];"
                f"[merged]subtitles='{escaped_ass}'[v]"
            )
        elif layout == "blurred_backdrop":
            vf = (
                f"[0:v]setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=28[bg];"
                f"[0:v]setpts=PTS-STARTPTS,scale=1080:608:force_original_aspect_ratio=decrease[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2[merged];"
                f"[merged]subtitles='{escaped_ass}'[v]"
            )
        else:
            # Default: Clean Split Screen (Cam Top + Gameplay/Screen Bottom)
            vf = (
                f"[0:v]setpts=PTS-STARTPTS,crop=w={crop_cam_w}:h={crop_cam_h}:x='{crop_cam_x}':y='{crop_cam_y}',scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960[top];"
                f"[0:v]setpts=PTS-STARTPTS,crop=w={crop_screen_w}:h={crop_screen_h}:x='{crop_screen_x}':y='{crop_screen_y}',scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960[bot];"
                f"[top][bot]vstack=inputs=2[stacked];"
                f"[stacked]subtitles='{escaped_ass}'[v]"
            )

        cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(start_time),
            "-t", str(duration),
            "-accurate_seek",
            "-i", str(source_video_path),
            "-avoid_negative_ts", "make_zero",
            "-filter_complex", vf,
            "-map", "[v]",
            "-map", "0:a?",
            "-af", audio_filter,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "veryfast",
            "-crf", "20",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            str(output_clip_path)
        ]

        print(f"[VideoRenderer] Rendering Short: {output_clip_path}...")
        res = subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[VideoRenderer] Main render notice: {res.stderr[:200]}")
            fallback_vf = (
                f"[0:v]setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                f"subtitles='{escaped_ass}'[v]"
            )
            fallback_cmd = [
                "ffmpeg", "-y",
                "-ss", str(start_time), "-t", str(duration),
                "-accurate_seek",
                "-i", str(source_video_path),
                "-avoid_negative_ts", "make_zero",
                "-filter_complex", fallback_vf,
                "-map", "[v]", "-map", "0:a?",
                "-af", audio_filter,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-preset", "veryfast",
                "-crf", "22",
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
                str(output_clip_path)
            ]
            subprocess.run(fallback_cmd, cwd=str(BASE_DIR), check=True)

        return str(output_clip_path)
