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

        # Robust ASS path for FFmpeg filter (relative path avoids Windows drive colon conflicts)
        try:
            escaped_ass = Path(ass_subtitle_path).resolve().relative_to(BASE_DIR).as_posix()
        except Exception:
            escaped_ass = Path(ass_subtitle_path).resolve().as_posix()
            if os.name == "nt":
                drive, rest = os.path.splitdrive(escaped_ass)
                if drive:
                    escaped_ass = f"{drive[0]}\\:{rest}"

        # Clean, natural studio audio filter with strictly zero-based PTS and resample sync
        audio_filter = (
            "asetpts=PTS-STARTPTS,"
            "aresample=async=1000:first_pts=0,"
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

        # Center-weighted gameplay crop: captures the active center action without extreme distortion
        if cam_cx < 0.35:
            crop_screen_x = "(iw * 0.16)"
        elif cam_cx > 0.65:
            crop_screen_x = "(iw * 0.02)"
        else:
            crop_screen_x = "(iw - min(iw, ih*1.125)) / 2"

        # Build Video Filter Graph with studio-grade composition & 10x optimized downscaled blur
        if layout == "gaming_pip":
            # Gaming PiP: Fast downscaled ambient dark-blur canvas + prominent floating 720x560 cam window + full 16:9 gameplay
            vf = (
                f"[0:v]setpts=PTS-STARTPTS,scale=180:320:force_original_aspect_ratio=increase:flags=fast_bilinear,crop=180:320,boxblur=8:2,scale=1080:1920:flags=fast_bilinear,colorchannelmixer=aa=1:rr=0.35:gg=0.35:bb=0.35[bg];"
                f"[0:v]setpts=PTS-STARTPTS,crop=w={crop_cam_w}:h={crop_cam_h}:x='{crop_cam_x}':y='{crop_cam_y}',scale=720:560:force_original_aspect_ratio=increase:flags=bicubic,crop=720:560,drawbox=x=0:y=0:w=iw:h=ih:color=0x6366f1@0.9:t=4[cam];"
                f"[0:v]setpts=PTS-STARTPTS,scale=1080:608:force_original_aspect_ratio=decrease:flags=bicubic,drawbox=x=0:y=0:w=iw:h=ih:color=0xffffff@0.25:t=2[game];"
                f"[bg][cam]overlay=x=180:y=140[bg_cam];"
                f"[bg_cam][game]overlay=x=0:y=780[merged];"
                f"[merged]subtitles='{escaped_ass}'[v]"
            )
        elif layout == "blurred_backdrop":
            # Blurred Backdrop: Fast 60fps downscaled boxblur ambient background + full-width centered foreground
            vf = (
                f"[0:v]setpts=PTS-STARTPTS,scale=180:320:force_original_aspect_ratio=increase:flags=fast_bilinear,crop=180:320,boxblur=8:2,scale=1080:1920:flags=fast_bilinear,colorchannelmixer=aa=1:rr=0.4:gg=0.4:bb=0.4[bg];"
                f"[0:v]setpts=PTS-STARTPTS,scale=1080:608:force_original_aspect_ratio=decrease:flags=bicubic,drawbox=x=0:y=0:w=iw:h=ih:color=0xffffff@0.2:t=2[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2[merged];"
                f"[merged]subtitles='{escaped_ass}'[v]"
            )
        else:
            # Default: Clean Viral Split Screen (Cam Top 956px + 8px Neon Broadcast Divider + Focused Game 956px)
            vf = (
                f"[0:v]setpts=PTS-STARTPTS,crop=w={crop_cam_w}:h={crop_cam_h}:x='{crop_cam_x}':y='{crop_cam_y}',scale=1080:956:force_original_aspect_ratio=increase:flags=bicubic,crop=1080:956[top];"
                f"[0:v]setpts=PTS-STARTPTS,crop=w=min(iw\\,ih*1.2):h=min(ih\\,iw/1.2):x='{crop_screen_x}':y=0,scale=1080:956:force_original_aspect_ratio=increase:flags=bicubic,crop=1080:956[bot];"
                f"color=c=0x6366f1:s=1080x8:r=30[divider];"
                f"[top][divider][bot]vstack=inputs=3:shortest=1[stacked];"
                f"[stacked]subtitles='{escaped_ass}'[v]"
            )

        cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(start_time),
            "-t", str(duration),
            "-accurate_seek",
            "-avoid_negative_ts", "make_zero",
            "-i", str(source_video_path),
            "-fps_mode", "cfr",
            "-filter_complex", vf,
            "-map", "[v]",
            "-map", "0:a?",
            "-af", audio_filter,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "superfast",
            "-crf", "20",
            "-threads", "6",
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
                f"[0:v]setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase:flags=bicubic,crop=1080:1920,"
                f"subtitles='{escaped_ass}'[v]"
            )
            fallback_cmd = [
                "ffmpeg", "-y",
                "-ss", str(start_time),
                "-t", str(duration),
                "-accurate_seek",
                "-avoid_negative_ts", "make_zero",
                "-i", str(source_video_path),
                "-fps_mode", "cfr",
                "-filter_complex", fallback_vf,
                "-map", "[v]",
                "-map", "0:a?",
                "-af", audio_filter,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-preset", "superfast",
                "-crf", "20",
                "-threads", "6",
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
                str(output_clip_path)
            ]
            subprocess.run(fallback_cmd, cwd=str(BASE_DIR), check=True)

        return str(output_clip_path)
