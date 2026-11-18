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
