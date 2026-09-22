import cv2
import numpy as np

class FaceTracker:
    def __init__(self):
        pass

    def detect_streamer_webcam_box(self, video_path: str, sample_time: float = 5.0) -> dict:
        """
        Analyzes video frames to locate the streamer's webcam box (bottom-left, bottom-right, top-left, top-right, or center).
        Returns normalized bounding box dict: {'x': float, 'y': float, 'w': float, 'h': float}
        """
        if not video_path:
            return {"x": 0.25, "y": 0.7, "w": 0.45, "h": 0.55}

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return {"x": 0.25, "y": 0.7, "w": 0.45, "h": 0.55}

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1920.0
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1080.0

        target_frame = int(sample_time * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            return {"x": 0.25, "y": 0.7, "w": 0.45, "h": 0.55}

        # Analyze skin-tone heat density to find streamer cam location
        h, w, _ = frame.shape
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([25, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_skin, upper_skin)

        # Quadrant density scores
        q_bl = np.sum(mask[int(h * 0.4):h, 0:int(w * 0.45)])
        q_br = np.sum(mask[int(h * 0.4):h, int(w * 0.55):w])
        q_tl = np.sum(mask[0:int(h * 0.5), 0:int(w * 0.45)])
        q_tr = np.sum(mask[0:int(h * 0.5), int(w * 0.55):w])

        scores = {
            "bottom_left": q_bl,
            "bottom_right": q_br,
            "top_left": q_tl,
            "top_right": q_tr
        }

        best_pos = max(scores, key=scores.get)

        if best_pos == "bottom_left":
            # Streamer in bottom-left (e.g. IShowSpeed standard setup)
            return {"x": 0.22, "y": 0.72, "w": 0.42, "h": 0.55}
        elif best_pos == "bottom_right":
            # Streamer in bottom-right (e.g. Kai Cenat / Jynxzi setup)
            return {"x": 0.78, "y": 0.72, "w": 0.42, "h": 0.55}
        elif best_pos == "top_left":
            return {"x": 0.22, "y": 0.28, "w": 0.42, "h": 0.55}
        elif best_pos == "top_right":
            return {"x": 0.78, "y": 0.28, "w": 0.42, "h": 0.55}

        # Default center
        return {"x": 0.5, "y": 0.5, "w": 0.5, "h": 0.6}
