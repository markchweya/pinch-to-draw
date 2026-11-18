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
