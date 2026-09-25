import os
import sys
import uuid
import asyncio
import json
import traceback
import subprocess
import concurrent.futures
from pathlib import Path
from typing import Optional, List

# Ensure Windows standard I/O handles full UTF-8 emojis and international Unicode characters
os.environ["PYTHONIOENCODING"] = "utf-8"
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

from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import BASE_DIR, OUTPUT_DIR, TEMP_DIR, STATIC_DIR, SUBTITLE_PRESETS, CREATOR_PRESETS
from backend.downloader import YouTubeDownloader
from backend.transcription import Transcriber
from backend.energy_detector import AudioEnergyDetector
from backend.clip_extractor import ClipExtractor
from backend.face_tracker import FaceTracker
from backend.subtitle_generator import SubtitleGenerator
from backend.video_renderer import VideoRenderer
from backend.metadata_generator import MetadataGenerator
from backend.thumbnail_maker import ThumbnailMaker
from backend.tts_voice import VoiceoverStudio
from backend.youtube_publisher import YouTubePublisher
from backend.compilation_builder import CompilationBuilder

app = FastAPI(title="BeastClip AI - Local YouTube Shorts Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file mounts
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")

# In-memory jobs tracker
JOBS = {}
yt_publisher = YouTubePublisher()
compilation_builder = CompilationBuilder()


class ProcessRequest(BaseModel):
    url: str
    target_duration: int = 40        # 30, 40, 60 seconds
    num_clips: int = 5               # 3, 5, 10, 15
    subtitle_style: str = "hormozi"  # hormozi, beast, neon, fire_red
    layout: str = "smart_face"       # smart_face (9:16 full vertical), split_screen, blurred_backdrop
    creator_credit: Optional[str] = None
    enable_copyright_shield: bool = True
    enable_seamless_loop: bool = True

class MultiVideoCompilationRequest(BaseModel):
    urls: List[str]                  # 2 to 5 YouTube URLs
    ranking_header: Optional[str] = "Ranking Best Fails of The Week"
    clip_labels: Optional[List[str]] = None
    target_duration: int = 50        # 40, 50, 60 seconds
    countdown_style: str = "gold"    # gold, cyber, fire, beast
    subtitle_style: str = "hormozi"
    layout: str = "smart_face"
    creator_credit: Optional[str] = None

class StitchClipsRequest(BaseModel):
    clip_ids: List[str]              # List of generated clip IDs in desired countdown order
    target_duration: int = 50
    countdown_style: str = "gold"

class VoiceoverRequest(BaseModel):
    clip_id: str
    voiceover_text: Optional[str] = None
    voice_type: str = "en-US-GuyNeural"

@app.get("/")
def get_index():
    from fastapi.responses import FileResponse
    return FileResponse(
        STATIC_DIR / "index.html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

import concurrent.futures

@app.get("/api/presets")
def get_presets():
    return {
        "subtitle_styles": SUBTITLE_PRESETS,
        "creators": CREATOR_PRESETS,
        "layouts": [
            {"id": "split_screen", "name": "Split Screen (Gaming + Cam)", "desc": "Top half facecam, bottom half gameplay (Twitch/Kick style)"},
            {"id": "gaming_pip", "name": "Gaming PiP Cam (Corner Bubble)", "desc": "Fullscreen gameplay with dynamic rounded facecam in corner"},
            {"id": "smart_face", "name": "Smart Face Track (9:16)", "desc": "Autocenters streamer reaction in full 9:16 screen"},
            {"id": "blurred_backdrop", "name": "Blurred Ambient Backdrop", "desc": "Landscape video with aesthetic blurred vertical background"}
        ]
    }

@app.post("/api/extract-info")
def extract_video_info(req: dict):
    url = req.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Missing URL")
    downloader = YouTubeDownloader(TEMP_DIR)
    info = downloader.extract_info(url)
    return info

@app.post("/api/extract-multi-info")
def extract_multi_video_info(req: dict):
    urls = req.get("urls", [])
    if not urls:
        raise HTTPException(status_code=400, detail="Missing URLs")
    downloader = YouTubeDownloader(TEMP_DIR)
    
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(urls), 5)) as executor:
        future_to_url = {executor.submit(downloader.extract_info, u): u for u in urls if u and u.strip()}
        for future in concurrent.futures.as_completed(future_to_url):
            u = future_to_url[future]
            try:
                info = future.result()
                results[u] = info
            except Exception as e:
                results[u] = {"url": u, "title": "Unknown", "uploader": "Creator", "error": str(e)}
    
    # Return results in same order as requested urls
    ordered_results = [results.get(u, {"url": u, "title": "Unknown", "uploader": "Creator"}) for u in urls if u and u.strip()]
    return {"results": ordered_results}

def process_single_clip_task(
    clip_tuple,
    req,
    job_id,
    info,
    video_path,
    downloader,
    transcriber,
    face_tracker,
    sub_generator,
    renderer,
    meta_gen,
    thumb_maker
):
    idx, clip = clip_tuple
    clip_idx = idx + 1
    clip_id = f"{job_id}_clip_{clip_idx}"

    # Determine source clip path (either existing local video or fast parallel snipped slice)
    if video_path and os.path.exists(video_path):
        source_for_render = video_path
        render_start = clip["start"]
    else:
        snipped_path = downloader.download_clip_section(req.url, info["id"], clip["start"], clip["duration"], clip_id)
        if snipped_path and os.path.exists(snipped_path):
            source_for_render = snipped_path
            render_start = 0.0
        else:
            full_res = downloader.download_video_and_audio(req.url, info["id"])
            source_for_render = full_res.get("video_path")
            render_start = clip["start"]

    # Frame-Perfect Subtitle Synchronization
    clip_words = clip.get("words", [])
    try:
        clip_audio_tmp = TEMP_DIR / f"{clip_id}_clean.wav"
        ffmpeg_slice_cmd = ["ffmpeg", "-y"]
        if render_start > 0.0:
            ffmpeg_slice_cmd.extend(["-ss", str(render_start), "-t", str(clip["duration"])])
        elif clip.get("duration"):
            ffmpeg_slice_cmd.extend(["-t", str(clip["duration"])])

        ffmpeg_slice_cmd.extend([
            "-accurate_seek",
            "-i", str(source_for_render),
            "-avoid_negative_ts", "make_zero",
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            str(clip_audio_tmp)
        ])
        subprocess.run(ffmpeg_slice_cmd, check=True, capture_output=True)

        exact_trans = transcriber.transcribe(
            str(clip_audio_tmp),
            video_title=info.get("title", ""),
            uploader=info.get("uploader", ""),
            context_prompt=clip.get("text", ""),
            is_clip_slice=True
        )
        exact_words = []
        for s in exact_trans.get("segments", []):
            for w in s.get("words", []):
                exact_words.append(w)
        if exact_words:
            clip_words = exact_words
    except Exception as sync_err:
        print(f"[Sync] Notice: {sync_err}")

    # Detect Streamer Webcam Box
    cam_box = face_tracker.detect_streamer_webcam_box(source_for_render, sample_time=render_start + 2.0)

    # Metadata
    meta = meta_gen.generate_clip_metadata(
        clip_text=clip["text"],
        original_title=info.get("title", "Stream Highlight"),
        uploader=info.get("uploader", ""),
        uploader_url=info.get("uploader_url", ""),
        rank=clip_idx
    )
    credit_tag = req.creator_credit or meta["creator_credit"]

    # Generate ASS Subtitles
    ass_path = TEMP_DIR / f"{clip_id}.ass"
    sub_generator.create_ass_subtitles(
        clip_words=clip_words,
        output_ass_path=str(ass_path),
        creator_credit=credit_tag,
        clip_duration=clip["duration"]
    )

    # Render 9:16 MP4
    out_clip_filename = f"{clip_id}.mp4"
    out_clip_path = OUTPUT_DIR / out_clip_filename
    renderer.render_clip(
        source_video_path=source_for_render,
        start_time=render_start,
        duration=clip["duration"],
        ass_subtitle_path=str(ass_path),
        output_clip_path=str(out_clip_path),
        cam_box=cam_box,
        layout=req.layout,
        creator_credit=credit_tag,
        enable_copyright_protection=req.enable_copyright_shield,
        enable_seamless_loop=req.enable_seamless_loop
    )

    # Thumbnail
    thumb_filename = f"{clip_id}_thumb.jpg"
    thumb_path = OUTPUT_DIR / thumb_filename
    best_frame = thumb_maker.extract_best_frame(source_for_render, render_start, clip["duration"])
    thumb_maker.generate_vertical_thumbnail(best_frame, meta["title"], str(thumb_path))

    return {
        "clip_id": clip_id,
        "rank": clip_idx,
        "start": clip["start"],
        "end": clip["end"],
        "duration": clip["duration"],
        "virality_score": clip["virality_score"],
        "hype_score": clip["hype_score"],
        "transcript": clip["text"],
        "title": meta["title"],
        "title_suggestions": meta.get("title_suggestions", []),
        "description": meta["description"],
        "tags": meta["tags"],
        "tags_string": meta["tags_string"],
        "pinned_comment": meta.get("pinned_comment", ""),
        "viral_hooks": meta.get("viral_hooks", []),
        "hashtag_clusters": meta.get("hashtag_clusters", {}),
        "virality_breakdown": meta.get("virality_breakdown", {}),
        "recommended_sound": meta.get("recommended_sound", ""),
        "optimal_post_time": meta.get("optimal_post_time", ""),
        "full_viral_package": meta.get("full_viral_package", ""),
        "creator_credit": credit_tag,
        "video_url": f"/output/{out_clip_filename}",
        "thumbnail_url": f"/output/{thumb_filename}"
    }

def run_processing_pipeline(job_id: str, req: ProcessRequest):
    try:
        JOBS[job_id]["status"] = "processing"
        JOBS[job_id]["progress"] = 5
        JOBS[job_id]["message"] = "Scanning stream & extracting high-speed audio..."

        downloader = YouTubeDownloader(TEMP_DIR)
        info = downloader.extract_info(req.url)
        duration = info.get("duration", 0)
        video_id = info["id"]

        # Fast Audio Extraction (3 seconds)
        audio_path = downloader.download_fast_audio_for_analysis(req.url, video_id)
        video_path = None # Will snip in parallel

        # Ensure exact total duration from WAV audio header if metadata was 0
        if not duration or duration <= 0:
            try:
                import wave
                with wave.open(str(audio_path), "rb") as wf:
                    duration = wf.getnframes() / float(wf.getframerate())
            except Exception:
                pass

        # 1. Ultra-fast Whisper Transcription
        JOBS[job_id]["progress"] = 25
        JOBS[job_id]["message"] = "Transcribing Speech with Turbo AI Model..."
        transcriber = Transcriber(model_size="small.en")
        transcript_data = transcriber.transcribe(
            audio_path,
            video_title=info.get("title", ""),
            uploader=info.get("uploader", "")
        )

        # 2. Audio Energy / Screams / Hype Spikes
        JOBS[job_id]["progress"] = 45
        JOBS[job_id]["message"] = "Analyzing Laughs, Screams & Viral Energy Spikes..."
        energy_detector = AudioEnergyDetector()
        energy_timeline = energy_detector.analyze_audio_energy(audio_path)

        # 3. Highlight Extraction
        JOBS[job_id]["progress"] = 60
        JOBS[job_id]["message"] = f"Selecting Top {req.num_clips} Viral Highlight Moments..."
        clip_extractor = ClipExtractor(energy_detector)
        selected_clips = clip_extractor.extract_top_highlights(
            transcript_data,
            energy_timeline,
            total_duration=duration,
            target_clip_duration=req.target_duration,
            num_clips=req.num_clips
        )

        # 4. Multi-Threaded Parallel Rendering (3x - 5x Speedup)
        JOBS[job_id]["progress"] = 70
        JOBS[job_id]["message"] = f"Parallel Rendering {len(selected_clips)} 9:16 Shorts with dynamic captions..."

        face_tracker = FaceTracker()
        sub_generator = SubtitleGenerator(req.subtitle_style)
        renderer = VideoRenderer()
        meta_gen = MetadataGenerator()
        thumb_maker = ThumbnailMaker()

        rendered_clips = []
        max_workers = min(3, max(1, len(selected_clips)))

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    process_single_clip_task,
                    (idx, clip),
                    req,
                    job_id,
                    info,
                    video_path,
                    downloader,
                    transcriber,
                    face_tracker,
                    sub_generator,
                    renderer,
                    meta_gen,
                    thumb_maker
                )
                for idx, clip in enumerate(selected_clips)
            ]

            completed = 0
            for fut in concurrent.futures.as_completed(futures):
                try:
                    res_clip = fut.result()
                    if res_clip:
                        rendered_clips.append(res_clip)
                    completed += 1
                    JOBS[job_id]["progress"] = 70 + int((completed / len(selected_clips)) * 25)
                except Exception as clip_err:
                    print(f"[Pipeline] Notice on parallel clip: {clip_err}")

        # Sort clips back by rank
        rendered_clips.sort(key=lambda x: x["rank"])

        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["progress"] = 100
        JOBS[job_id]["message"] = f"Successfully Generated {len(rendered_clips)} Viral Shorts!"
        JOBS[job_id]["clips"] = rendered_clips

    except Exception as e:
        traceback.print_exc()
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = str(e)
        JOBS[job_id]["message"] = f"Error during processing: {e}"

def run_multi_video_compilation_pipeline(job_id: str, req: MultiVideoCompilationRequest):
    try:
        urls = [u.strip() for u in req.urls if u.strip()]
        if len(urls) < 2:
            raise ValueError("Please provide at least 2 video URLs for compilation")

        num_videos = min(5, len(urls))
        urls = urls[:num_videos]

        JOBS[job_id]["status"] = "processing"
        JOBS[job_id]["progress"] = 5
        JOBS[job_id]["message"] = f"Scanning {num_videos} videos for Top Viral Moments..."

        downloader = YouTubeDownloader(TEMP_DIR)
        transcriber = Transcriber(model_size="small.en")
        energy_detector = AudioEnergyDetector()
        clip_extractor = ClipExtractor(energy_detector)
        face_tracker = FaceTracker()
        sub_generator = SubtitleGenerator(req.subtitle_style)
        renderer = VideoRenderer()
        meta_gen = MetadataGenerator()
        thumb_maker = ThumbnailMaker()

        per_clip_dur = max(6.0, round(req.target_duration / num_videos, 1))
        extracted_moments = []
        creator_names = []
        clip_labels_dict = {}

        for idx, url in enumerate(urls):
            current_pct = 10 + int((idx / num_videos) * 60)
            JOBS[job_id]["progress"] = current_pct
            JOBS[job_id]["message"] = f"Extracting climax from Video #{idx+1} of {num_videos}..."

            try:
                info = downloader.extract_info(url)
                creator_names.append(info.get("uploader", "Streamer"))
                audio_path = downloader.download_fast_audio_for_analysis(url, info["id"])

                # Determine duration
                vid_dur = info.get("duration", 0)
                if not vid_dur or vid_dur <= 0:
                    try:
                        import wave
                        with wave.open(str(audio_path), "rb") as wf:
                            vid_dur = wf.getnframes() / float(wf.getframerate())
                    except Exception:
                        vid_dur = 300.0

                trans = transcriber.transcribe(
                    audio_path,
                    video_title=info.get("title", ""),
                    uploader=info.get("uploader", "")
                )
                timeline = energy_detector.analyze_audio_energy(audio_path)

                # Extract the single best moment from this video
                top_moments = clip_extractor.extract_top_highlights(
                    trans,
                    timeline,
                    total_duration=vid_dur,
                    target_clip_duration=int(per_clip_dur),
                    num_clips=1
                )

                if top_moments:
                    best_moment = top_moments[0]
                    part_id = f"{job_id}_part_{idx+1}"
                    # Snip section
                    snipped_file = downloader.download_clip_section(
                        url, info["id"], best_moment["start"], best_moment["duration"], part_id
                    )
                    if not snipped_file or not os.path.exists(snipped_file):
                        full_res = downloader.download_video_and_audio(url, info["id"])
                        snipped_file = full_res.get("video_path")
                        r_start = best_moment["start"]
                    else:
                        r_start = 0.0

                    rank_number = num_videos - idx # e.g. 5, 4, 3, 2, 1
                    
                    # Determine clip label
                    user_label = ""
                    if req.clip_labels and idx < len(req.clip_labels):
                        user_label = req.clip_labels[idx].strip()
                    if not user_label:
                        clean_words = re.sub(r'[^a-zA-Z0-9\s]', '', info.get('title', 'Viral Moment')).split()
                        user_label = " ".join(clean_words[:3]).lower() if clean_words else f"Moment #{rank_number}"
                    
                    clip_labels_dict[rank_number] = user_label

                    extracted_moments.append({
                        "video_path": str(snipped_file),
                        "start_time": r_start,
                        "duration": best_moment["duration"],
                        "rank": rank_number,
                        "words": best_moment.get("words", []),
                        "creator_name": info.get("uploader", "")
                    })

            except Exception as single_err:
                print(f"[Compilation] Video {idx+1} error: {single_err}")

        if not extracted_moments:
            raise RuntimeError("Could not extract any highlight moments from the provided videos")

        # Step 2: Stitch all moments with dynamic ranking ladder leaderboard
        JOBS[job_id]["progress"] = 75
        JOBS[job_id]["message"] = f"Rendering Ranking Leaderboard Short ({len(extracted_moments)} moments)..."

        comp_filename = f"{job_id}_compilation.mp4"
        comp_output_path = OUTPUT_DIR / comp_filename

        compilation_builder.build_compilation(
            clip_segments=extracted_moments,
            output_path=str(comp_output_path),
            ranking_header=req.ranking_header or "Ranking Best Fails of The Week",
            clip_labels=clip_labels_dict,
            total_target_duration=req.target_duration,
            countdown_style=req.countdown_style
        )

        # Step 3: Top Compilation Metadata & Thumbnail
        JOBS[job_id]["progress"] = 90
        JOBS[job_id]["message"] = "Generating Top 5 Viral Metadata & Thumbnail..."

        comp_meta = meta_gen.generate_compilation_metadata(creator_names, len(extracted_moments))
        thumb_filename = f"{job_id}_compilation_thumb.jpg"
        thumb_path = OUTPUT_DIR / thumb_filename
        best_frame = thumb_maker.extract_best_frame(str(comp_output_path), 2.0, req.target_duration)
        thumb_maker.generate_vertical_thumbnail(best_frame, comp_meta["title"], str(thumb_path))

        comp_clip_data = {
            "clip_id": f"{job_id}_compilation",
            "rank": 1,
            "start": 0.0,
            "end": float(req.target_duration),
            "duration": float(req.target_duration),
            "virality_score": 98.8,
            "hype_score": 96.5,
            "transcript": f"TOP {len(extracted_moments)} Compilation of {', '.join(creator_names[:2])}",
            "title": comp_meta["title"],
            "title_suggestions": comp_meta.get("title_suggestions", []),
            "description": comp_meta["description"],
            "tags": comp_meta["tags"],
            "tags_string": comp_meta["tags_string"],
            "pinned_comment": comp_meta.get("pinned_comment", ""),
            "hashtag_clusters": comp_meta.get("hashtag_clusters", {}),
            "virality_breakdown": comp_meta.get("virality_breakdown", {}),
            "full_viral_package": comp_meta.get("full_viral_package", ""),
            "creator_credit": f"@{creator_names[0].replace(' ', '')}" if creator_names else "@Creator",
            "video_url": f"/output/{comp_filename}",
            "thumbnail_url": f"/output/{thumb_filename}",
            "is_compilation": True
        }

        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["progress"] = 100
        JOBS[job_id]["message"] = f"Successfully Created Top {len(extracted_moments)} Countdown Compilation!"
        JOBS[job_id]["clips"] = [comp_clip_data]

    except Exception as e:
        traceback.print_exc()
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = str(e)
        JOBS[job_id]["message"] = f"Compilation failed: {e}"

@app.post("/api/compilation/create-multi-video")
def create_multi_video_compilation(req: MultiVideoCompilationRequest, background_tasks: BackgroundTasks):
    job_id = f"comp_{str(uuid.uuid4())[:6]}"
    JOBS[job_id] = {
        "id": job_id,
        "status": "queued",
        "progress": 0,
        "message": "Initializing Top Countdown Compilation pipeline...",
        "clips": [],
        "error": None
    }
    background_tasks.add_task(run_multi_video_compilation_pipeline, job_id, req)
    return {"job_id": job_id, "status": "queued"}

@app.post("/api/compilation/stitch-gallery-clips")
def stitch_gallery_clips(req: StitchClipsRequest):
    """
    Combines already generated gallery clips into a single Top Countdown Short in seconds!
    """
    if not req.clip_ids or len(req.clip_ids) < 2:
        raise HTTPException(status_code=400, detail="Please select at least 2 clips to stitch")

    clip_segments = []
    num_clips = len(req.clip_ids)
    per_clip_dur = max(6.0, round(req.target_duration / num_clips, 1))
    meta_gen = MetadataGenerator()
    thumb_maker = ThumbnailMaker()

    for idx, c_id in enumerate(req.clip_ids):
        v_path = OUTPUT_DIR / f"{c_id}.mp4"
        voiced_path = OUTPUT_DIR / f"{c_id}_voiced.mp4"
        if voiced_path.exists():
            v_path = voiced_path

        if not v_path.exists():
            continue

        rank_num = num_clips - idx # 5, 4, 3, 2, 1
        clip_segments.append({
            "video_path": str(v_path),
            "start_time": 0.0,
            "duration": per_clip_dur,
            "rank": rank_num
        })

    if not clip_segments:
        raise HTTPException(status_code=404, detail="Selected clip video files not found")

    comp_id = f"stitch_{str(uuid.uuid4())[:6]}"
    comp_filename = f"{comp_id}_compilation.mp4"
    comp_output_path = OUTPUT_DIR / comp_filename

    try:
        compilation_builder.build_compilation(
            clip_segments=clip_segments,
            output_path=str(comp_output_path),
            total_target_duration=req.target_duration,
            countdown_style=req.countdown_style
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stitch clips: {e}")

    comp_meta = meta_gen.generate_compilation_metadata(["Streamer"], len(clip_segments))
    thumb_filename = f"{comp_id}_compilation_thumb.jpg"
    thumb_path = OUTPUT_DIR / thumb_filename
    best_frame = thumb_maker.extract_best_frame(str(comp_output_path), 2.0, req.target_duration)
    thumb_maker.generate_vertical_thumbnail(best_frame, comp_meta["title"], str(thumb_path))

    return {
        "status": "success",
        "clip": {
            "clip_id": comp_id,
            "rank": 1,
            "start": 0.0,
            "end": float(req.target_duration),
            "duration": float(req.target_duration),
            "virality_score": 99.2,
            "hype_score": 97.0,
            "transcript": f"TOP {len(clip_segments)} Countdown Compilation",
            "title": comp_meta["title"],
            "title_suggestions": comp_meta.get("title_suggestions", []),
            "description": comp_meta["description"],
            "tags": comp_meta["tags"],
            "tags_string": comp_meta["tags_string"],
            "creator_credit": "@OriginalCreator",
            "video_url": f"/output/{comp_filename}",
            "thumbnail_url": f"/output/{thumb_filename}",
            "is_compilation": True
        }
    }

@app.post("/api/process-video")
def start_processing(req: ProcessRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())[:8]
    JOBS[job_id] = {
        "id": job_id,
        "status": "queued",
        "progress": 0,
        "message": "Initializing BeastClip pipeline...",
        "clips": [],
        "error": None
    }
    background_tasks.add_task(run_processing_pipeline, job_id, req)
    return {"job_id": job_id, "status": "queued"}

@app.get("/api/status/{job_id}")
def get_job_status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return JOBS[job_id]

@app.post("/api/add-voiceover")
async def add_voiceover_to_clip(
    clip_id: str = Form(...),
    voiceover_text: Optional[str] = Form(None),
    voice_type: str = Form("en-US-GuyNeural"),
    audio_file: Optional[UploadFile] = File(None)
):
    """
    Applies custom voiceover commentary to a generated clip with auto-ducking.
    """
    clip_file = OUTPUT_DIR / f"{clip_id}.mp4"
    if not clip_file.exists():
        raise HTTPException(status_code=404, detail="Clip video file not found")

    voice_studio = VoiceoverStudio(TEMP_DIR)
    voice_audio_path = None

    if audio_file:
        voice_audio_path = TEMP_DIR / f"mic_{clip_id}_{audio_file.filename}"
        with open(voice_audio_path, "wb") as f:
            content = await audio_file.read()
            f.write(content)
        voice_audio_path = str(voice_audio_path)
    elif voiceover_text:
        voice_audio_path = await voice_studio.generate_ai_voiceover(voiceover_text, voice_type)

    if not voice_audio_path or not os.path.exists(voice_audio_path):
        raise HTTPException(status_code=400, detail="Failed to provide or generate voiceover audio")

    # Render dubbed clip
    dubbed_filename = f"{clip_id}_voiced.mp4"
    dubbed_path = OUTPUT_DIR / dubbed_filename
    voice_studio.mix_voiceover_with_ducking(
        base_video_path=str(clip_file),
        voiceover_audio_path=voice_audio_path,
        output_video_path=str(dubbed_path)
    )

    return {
        "status": "success",
        "dubbed_video_url": f"/output/{dubbed_filename}"
    }

@app.post("/api/preview-voice")
async def preview_voiceover(req: dict):
    text = req.get("text", "Wait until you see what happens next in this crazy clip!")
    voice_type = req.get("voice_type", "hype_trailer")
    voice_studio = VoiceoverStudio(TEMP_DIR)
    audio_path = await voice_studio.generate_ai_voiceover(text, voice_type)
    if not audio_path or not os.path.exists(audio_path):
        raise HTTPException(status_code=400, detail="Failed to synthesize voice preview")
    
    import shutil
    preview_filename = f"preview_{Path(audio_path).name}"
    preview_dest = OUTPUT_DIR / preview_filename
    shutil.copy2(audio_path, preview_dest)
    return {"audio_url": f"/output/{preview_filename}"}

# ==================== YOUTUBE OAUTH & AUTO-PUBLISHING ROUTES ====================

@app.get("/api/youtube/status")
def get_youtube_status():
    """Returns whether YouTube OAuth is connected and channel info."""
    return yt_publisher.get_channel_info()

@app.post("/api/youtube/setup-credentials")
def setup_youtube_credentials(req: dict):
    """Sets client_id and client_secret directly."""
    client_id = req.get("client_id")
    client_secret = req.get("client_secret")
    if not client_id or not client_secret:
        raise HTTPException(status_code=400, detail="Missing client_id or client_secret")
    yt_publisher.save_client_secrets_from_data(client_id, client_secret)
    return {"status": "saved", "message": "Credentials configured. Ready to authorize."}

@app.get("/api/youtube/auth-url")
def get_youtube_auth_url():
    """Generates the Google OAuth authorization URL."""
    try:
        url = yt_publisher.get_auth_url()
        return {"auth_url": url}
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/youtube/callback")
def handle_youtube_callback(code: str):
    """Google OAuth callback handler that saves the token and redirects to home."""
    from fastapi.responses import RedirectResponse
    try:
        yt_publisher.handle_auth_callback(code)
        return RedirectResponse(url="/?auth=success")
    except Exception as e:
        return RedirectResponse(url=f"/?auth=error&msg={str(e)}")

@app.post("/api/clips/update-metadata")
def update_clip_metadata(req: dict):
    """Updates title, description, and tags for a specific clip in memory."""
    job_id = req.get("job_id")
    clip_id = req.get("clip_id")
    new_title = req.get("title")
    new_description = req.get("description")
    new_tags = req.get("tags")
    new_pinned_comment = req.get("pinned_comment")

    if not clip_id:
        raise HTTPException(status_code=400, detail="clip_id is required")

    updated = False
    for j_id, job in JOBS.items():
        if job_id and j_id != job_id:
            continue
        for clip in job.get("clips", []):
            if clip.get("clip_id") == clip_id:
                if new_title is not None:
                    clip["title"] = new_title.strip()
                if new_description is not None:
                    clip["description"] = new_description.strip()
                if new_pinned_comment is not None:
                    clip["pinned_comment"] = new_pinned_comment.strip()
                if new_tags is not None:
                    if isinstance(new_tags, list):
                        clip["tags"] = new_tags
                        clip["tags_string"] = " ".join(new_tags)
                    else:
                        clip["tags_string"] = str(new_tags).strip()
                        clip["tags"] = [t for t in str(new_tags).split() if t.startswith("#")]
                updated = True
                break

    return {"status": "success", "clip_id": clip_id, "updated": updated}


@app.post("/api/youtube/upload-short")
def upload_single_short(req: dict):
    """Uploads a single generated Short to YouTube with optional custom scheduling."""
    clip_id = req.get("clip_id")
    title = req.get("title", "Viral Stream Highlight #Shorts")
    description = req.get("description", "")
    tags = req.get("tags", ["#Shorts", "#Gaming"])
    privacy = req.get("privacy", "public") # public, private, unlisted
    publish_at = req.get("publish_at") # custom datetime ISO string if scheduled
    
    clip_path = OUTPUT_DIR / f"{clip_id}.mp4"
    if not clip_path.exists():
        # Check if voiced version exists
        voiced_path = OUTPUT_DIR / f"{clip_id}_voiced.mp4"
        if voiced_path.exists():
            clip_path = voiced_path
        else:
            raise HTTPException(status_code=404, detail="Clip video not found")

    thumb_path = OUTPUT_DIR / f"{clip_id}_thumb.jpg"
    thumb_str = str(thumb_path) if thumb_path.exists() else None

    try:
        res = yt_publisher.upload_short(
            video_path=str(clip_path),
            title=title,
            description=description,
            tags=tags,
            privacy_status=privacy,
            publish_at=publish_at,
            thumbnail_path=thumb_str
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/youtube/drip-schedule-all")
def drip_schedule_all_clips(req: dict):
    """
    Schedules all generated clips in a job across multiple days at peak or custom hours
    to prevent spam flags.
    """
    job_id = req.get("job_id")
    shorts_per_day = int(req.get("shorts_per_day", 3))
    start_datetime = req.get("start_datetime")
    custom_hours = req.get("custom_hours")
    interval_hours = req.get("interval_hours")
    
    if job_id not in JOBS or not JOBS[job_id].get("clips"):
        raise HTTPException(status_code=404, detail="Job or clips not found")

    clips = JOBS[job_id]["clips"]
    schedule_times = yt_publisher.compute_drip_schedule(
        num_clips=len(clips),
        shorts_per_day=shorts_per_day,
        start_datetime=start_datetime,
        custom_hours=custom_hours,
        interval_hours=interval_hours
    )

    results = []
    for idx, clip in enumerate(clips):
        clip_id = clip["clip_id"]
        clip_path = OUTPUT_DIR / f"{clip_id}.mp4"
        voiced_path = OUTPUT_DIR / f"{clip_id}_voiced.mp4"
        if voiced_path.exists():
            clip_path = voiced_path

        thumb_path = OUTPUT_DIR / f"{clip_id}_thumb.jpg"
        thumb_str = str(thumb_path) if thumb_path.exists() else None
        target_time = schedule_times[idx]

        try:
            upload_res = yt_publisher.upload_short(
                video_path=str(clip_path),
                title=clip["title"],
                description=clip["description"],
                tags=clip.get("tags", ["#Shorts"]),
                privacy_status="private",
                publish_at=target_time,
                thumbnail_path=thumb_str
            )
            results.append({
                "clip_id": clip_id,
                "scheduled_for": target_time.strftime("%Y-%m-%d %H:%M UTC"),
                "youtube_url": upload_res["youtube_url"],
                "status": "scheduled"
            })
        except Exception as e:
            results.append({
                "clip_id": clip_id,
                "status": "failed",
                "error": str(e)
            })

    return {
        "status": "completed",
        "total_scheduled": sum(1 for r in results if r["status"] == "scheduled"),
        "results": results
    }

if __name__ == "__main__":

    import uvicorn
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
