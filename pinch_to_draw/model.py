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


def ensure_model():
    """Path to the model, downloading it first if it is not there yet."""
    path = model_path()
    if os.path.exists(path) and os.path.getsize(path) > 1_000_000:
        return path
    os.makedirs(model_dir(), exist_ok=True)
    tmp = path + ".part"
    urllib.request.urlretrieve(MODEL_URL, tmp)
    os.replace(tmp, path)
    return path
