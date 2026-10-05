import cv2
import numpy as np

class FaceTracker:
    def __init__(self):
        pass

    def detect_streamer_webcam_box(self, video_path: str, sample_time: float = 5.0) -> dict:
        """
        Analyzes video frames across multiple sample points to locate the streamer's webcam box
        (bottom-left, bottom-right, top-left, top-right, or center).
        Returns normalized bounding box dict: {'x': float, 'y': float, 'w': float, 'h': float}
        """
        default_box = {"x": 0.22, "y": 0.72, "w": 0.44, "h": 0.56}
        if not video_path:
            return default_box

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return default_box

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 1000

        # Sample across multiple points to avoid black frames or single-frame transition artifacts
        sample_offsets = [sample_time, sample_time + 4.0, sample_time + 8.0]
        quadrant_totals = {"bottom_left": 0.0, "bottom_right": 0.0, "top_left": 0.0, "top_right": 0.0}
        valid_samples = 0

        for s_t in sample_offsets:
            frame_no = int(max(0.0, s_t) * fps)
            if frame_no >= total_frames:
                frame_no = int(total_frames // 2)

            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
            ret, frame = cap.read()
            if not ret or frame is None:
                continue

            # Skip near-black frames (intro or fade-out)
            if np.mean(frame) < 15:
                continue

            h, w, _ = frame.shape
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([25, 255, 255], dtype=np.uint8)
            mask = cv2.inRange(hsv, lower_skin, upper_skin)

            quadrant_totals["bottom_left"] += float(np.sum(mask[int(h * 0.4):h, 0:int(w * 0.45)]))
            quadrant_totals["bottom_right"] += float(np.sum(mask[int(h * 0.4):h, int(w * 0.55):w]))
            quadrant_totals["top_left"] += float(np.sum(mask[0:int(h * 0.5), 0:int(w * 0.45)]))
            quadrant_totals["top_right"] += float(np.sum(mask[0:int(h * 0.5), int(w * 0.55):w]))
            valid_samples += 1

        cap.release()

        if valid_samples == 0:
            return default_box

        best_pos = max(quadrant_totals, key=quadrant_totals.get)

        if best_pos == "bottom_left":
            # Streamer in bottom-left (e.g. IShowSpeed standard setup)
            return {"x": 0.22, "y": 0.72, "w": 0.44, "h": 0.56}
        elif best_pos == "bottom_right":
            # Streamer in bottom-right (e.g. Kai Cenat / Jynxzi setup)
            return {"x": 0.78, "y": 0.72, "w": 0.44, "h": 0.56}
        elif best_pos == "top_left":
            return {"x": 0.22, "y": 0.28, "w": 0.44, "h": 0.56}
        elif best_pos == "top_right":
            return {"x": 0.78, "y": 0.28, "w": 0.44, "h": 0.56}

        return default_box
