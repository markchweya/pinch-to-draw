"""Gets Google's MediaPipe hand-landmark model (about 8 MB) on first use."""

import os
import urllib.request

MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
             "hand_landmarker/float16/latest/hand_landmarker.task")
MODEL_NAME = "hand_landmarker.task"


def model_dir():
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return os.path.join(base, "PinchToDraw")


def model_path():
    return os.path.join(model_dir(), MODEL_NAME)
