"""Background thread that watches the webcam and reports the pinch point."""

import threading
import time

import cv2
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions, vision

from pinch_to_draw.camera import open_camera
from pinch_to_draw.geometry import map_to_region
from pinch_to_draw.gestures import PinchDetector, pinch_gap, pinch_point
from pinch_to_draw.model import ensure_model

# Part of the camera picture that maps onto the whole screen, so you never
# have to reach the edge of the camera's view.
REGION = (0.15, 0.10, 0.85, 0.70)  # left, top, right, bottom (0..1)
PREVIEW_W, PREVIEW_H = 256, 192

BONES = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8), (5, 9),
         (9, 10), (10, 11), (11, 12), (9, 13), (13, 14), (14, 15), (15, 16),
         (13, 17), (17, 18), (18, 19), (19, 20), (0, 17)]

OPEN_COLOUR = (240, 240, 245)
PINCH_COLOUR = (10, 132, 255)


class HandTracker(threading.Thread):
    """Reads the camera, finds one hand and publishes its latest state.

    `latest()` returns (sequence_number, state, preview_rgb). `state` is
    {"present": False} or {"present": True, "x", "y" (0..1 screen), "pinch", "t"}.
    `status` is a short human-readable phase, `error` is set if it gave up.
    """

    def __init__(self):
        super().__init__(daemon=True)
        self.running = True
        self.error = None
        self.status = "Starting camera..."
        self.lock = threading.Lock()
        self.seq = 0
        self.state = {"present": False}
        self.preview = None
        self.pinch = PinchDetector()

    def latest(self):
        with self.lock:
            return self.seq, self.state, self.preview

    def stop(self):
        self.running = False

    def run(self):
        try:
            self.status = "Getting hand model..."
            model = ensure_model()
            self.status = "Starting camera..."
            cap = open_camera()
            try:
                options = vision.HandLandmarkerOptions(
                    base_options=BaseOptions(model_asset_path=model),
                    running_mode=vision.RunningMode.VIDEO,
                    num_hands=1,
                    min_hand_detection_confidence=0.6,
                    min_hand_presence_confidence=0.5,
                    min_tracking_confidence=0.5,
                )
                with vision.HandLandmarker.create_from_options(options) as landmarker:
                    self.status = "Tracking"
                    self._loop(cap, landmarker)
            finally:
                cap.release()
        except Exception as ex:
            self.error = str(ex) or ex.__class__.__name__

    def _loop(self, cap, landmarker):
        start, last_ts = time.monotonic(), -1
        while self.running:
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.01)
                continue
            now = time.monotonic()
            rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)  # mirror view
            ts = max(int((now - start) * 1000), last_ts + 1)
            last_ts = ts
            result = landmarker.detect_for_video(
                mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), ts)
            state = self._read_hand(result, now, rgb)
            preview = cv2.resize(rgb, (PREVIEW_W, PREVIEW_H), interpolation=cv2.INTER_AREA)
            with self.lock:
                self.seq += 1
                self.state = state
                self.preview = preview

    def _read_hand(self, result, now, rgb):
        h, w = rgb.shape[:2]
        left, top, right, bottom = REGION
        cv2.rectangle(rgb, (int(left * w), int(top * h)), (int(right * w), int(bottom * h)),
                      (120, 120, 140), 2)
        if not result.hand_landmarks:
            self.pinch.reset()
            return {"present": False}
        pts = [(p.x, p.y) for p in result.hand_landmarks[0]]
        pinched = self.pinch.update(pinch_gap(pts))
        cx, cy = pinch_point(pts)
        x, y = map_to_region(cx, cy, REGION)
        self._draw_hand(rgb, pts, (cx, cy), pinched)
        return {"present": True, "pinch": pinched, "t": now, "x": x, "y": y}

    @staticmethod
    def _draw_hand(rgb, pts, centre, pinched):
        h, w = rgb.shape[:2]
        colour = PINCH_COLOUR if pinched else OPEN_COLOUR
        for i, j in BONES:
            cv2.line(rgb, (int(pts[i][0] * w), int(pts[i][1] * h)),
                     (int(pts[j][0] * w), int(pts[j][1] * h)), colour, 2)
        cv2.circle(rgb, (int(centre[0] * w), int(centre[1] * h)), 9, colour,
                   -1 if pinched else 2)
