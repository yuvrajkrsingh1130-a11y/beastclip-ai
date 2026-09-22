# ⚡ BeastClip AI Studio
### 100% Free, Localhost, Watermark-Free YouTube Shorts & Clip Generator

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com)
[![Whisper Turbo](https://img.shields.io/badge/AI%20Transcription-faster--whisper-orange)](https://github.com/SYSTRAN/faster-whisper)
[![FFmpeg](https://img.shields.io/badge/Render%20Engine-FFmpeg-green.svg)](https://ffmpeg.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**BeastClip AI Studio** is an automated AI-powered video automation engine that transforms long YouTube videos, gaming streams, and podcasts into high-retention, viral 9:16 vertical YouTube Shorts, TikToks, and Instagram Reels. 

No watermarks, no monthly subscription fees, and no clip limits — runs completely locally on your own machine.

---

## 🌟 Key Features

* 🧠 **Smart AI Highlight & Comedy Detector**:
  - Automatically identifies the funniest, most insane, and loudest screaming moments (screams, laugh fits, rage moments) using adaptive acoustic energy and semantic AI analysis.
  - Automatically avoids repetitive or sequential slicing (0–30s, 30–60s) to deliver only peak viral highlights.

* 📐 **Adaptive 9:16 Vertical Framing**:
  - **Split Screen**: Streamer webcam on the top half + gameplay/content on the bottom half with subtle dynamic zoom pulses.
  - **Gaming PiP**: Fullscreen gameplay with a rounded streamer facecam bubble.
  - **Smart Face Track**: Auto-centers the streamer reaction face in 9:16 vertical view.
  - **Blurred Ambient Backdrop**: Centered widescreen video on an aesthetic blurred background.

* 🎨 **Viral Subtitle Styling (Creator Presets)**:
  - **Alex Hormozi Gold**: High-contrast yellow pop with active word highlights.
  - **MrBeast Green**: Bold green action captions.
  - **Cyberpunk Neon**: Pink & cyan glowing text.
  - **Anime Super Saiyan**: Golden aura bursts.
  - **Kai Cenat & Speed Slanted Neon / Rage Fire**: High-velocity energetic captions.

* 🎙️ **Monetization-Safe Voiceover Studio**:
  - Add original AI text-to-speech commentary or record your own live microphone directly in the browser.
  - Automatic audio-ducking: low-passes background video audio by 75% when voiceover speaks.

* 🚀 **1-Click YouTube Auto-Publisher & Viral Scheduler**:
  - Connect your YouTube channel via Google OAuth with 1 click.
  - **10 Peak Algorithm Viral Slots**: 1-click scheduling presets across the top viral CTR windows (7:30 AM, 9:00 AM, 11:30 AM, 1:00 PM, 3:30 PM, 5:00 PM, 7:30 PM, 9:00 PM, 10:30 PM, 12:00 AM).
  - **Anti-Spam Batch Drip Scheduling**: Distributes all clips across multiple days to maximize channel growth safely.

* 🛡️ **Anti-Copyright & Fair Use Shield**:
  - Automatic on-screen creator attribution badge.
  - Auto-generated Section 107 Fair Use copyright description disclaimer and credit links.

---

## 🚀 Quick Start & Installation

### Prerequisites:
1. **Python 3.10 or 3.11** ([Download Python](https://www.python.org/downloads/)) — *Be sure to check "Add Python to PATH" during install.*
2. **FFmpeg** ([Download FFmpeg](https://ffmpeg.org/download.html)) — *Or install on Windows via `winget install Gyan.FFmpeg`.*

---

### 1-Click Setup (Windows):

1. **Clone or Download this repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/beastclip-ai.git
   cd beastclip-ai
   ```

2. **Run the 1-Click Installer**:
   - Double-click **`setup.bat`** (or run `pip install -r requirements.txt`).

3. **Launch BeastClip AI Studio**:
   - Double-click **`Start_BeastClip_AI.bat`** (or run `python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000`).

4. **Open in your browser**:
   - Open [http://localhost:8000](http://localhost:8000)

---

## 🛠️ Manual CLI Setup (Linux / macOS / Windows)

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/beastclip-ai.git
cd beastclip-ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Start the studio
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

---

## 📁 Repository Structure

```
beastclip-ai/
├── backend/
│   ├── app.py                 # FastAPI Web Server & API Coordinator
│   ├── config.py              # App Configuration & Style Presets
│   ├── downloader.py          # yt-dlp Video & Audio Fast Downloader
│   ├── transcription.py       # faster-whisper AI Transcription
│   ├── energy_detector.py     # RMS volume & hype scream scanner
│   ├── clip_extractor.py      # Highlight selection & virality ranking
│   ├── face_tracker.py        # OpenCV face centering tracker
│   ├── subtitle_generator.py  # ASS animated subtitle generator
│   ├── tts_voice.py           # Voiceover mixer & TTS generator
│   ├── video_renderer.py      # FFmpeg 9:16 vertical video renderer
│   ├── metadata_generator.py  # Viral titles, descriptions, hashtags
│   ├── thumbnail_maker.py     # 1080x1920 thumbnail generator
│   └── youtube_publisher.py   # YouTube OAuth, Auto-Upload & Scheduling
├── static/
│   ├── index.html             # Studio Dashboard Frontend
│   ├── css/styles.css         # Glassmorphism Dark Theme
│   └── js/app.js              # Frontend Interactive Controller
├── fonts/                     # Caption typography
├── output/                    # Generated MP4 Shorts & Thumbnails (.gitignored)
├── temp/                      # Cached video/audio slices (.gitignored)
├── auth/                      # OAuth token directory (.gitignored)
├── setup.bat                  # 1-Click Dependency Installer
├── Start_BeastClip_AI.bat     # 1-Click Windows Studio Launcher
├── requirements.txt           # Python Dependencies
├── .gitignore                 # Secrets & media ignore rules
└── README.md                  # Project Documentation
```

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome! Feel free to open an Issue or submit a Pull Request.

---

## ⚖️ License

Distributed under the **MIT License**. See `LICENSE` for more information.
