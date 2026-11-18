"""Finds a webcam that gives a real colour picture at a good frame rate."""

import cv2

# Media Foundation delivers ~30 fps on most laptops; DirectShow often only 10.
BACKENDS = (cv2.CAP_MSMF, cv2.CAP_DSHOW)
MAX_INDEX = 3


def _configure(cap):
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # always hand us the newest frame


def looks_like_colour_picture(frame):
    """False for black frames and for grey infrared (Windows Hello) cameras."""
    b, g, r = (float(frame[..., c].mean()) for c in range(3))
    bright = (b + g + r) / 3 > 25
    colourful = max(abs(b - g), abs(g - r), abs(b - r)) > 1.5
    return bright and colourful


def _test(cap, tries=20):
    for _ in range(tries):  # give auto-exposure a moment
        ok, frame = cap.read()
        if ok and looks_like_colour_picture(frame):
            return True
    return False


def open_camera():
    """Return an opened cv2.VideoCapture, preferring a colour camera."""
    fallback = None
    for backend in BACKENDS:
        for index in range(MAX_INDEX):
            cap = cv2.VideoCapture(index, backend)
            if not cap.isOpened():
                cap.release()
                continue
            _configure(cap)
            if _test(cap):
                if fallback is not None:
                    fallback.release()
                return cap
            if fallback is None:
                fallback = cap
            else:
                cap.release()
    if fallback is not None:
        return fallback
    raise RuntimeError("No webcam found (or another app is using it)")
