"""Pinch-to-draw: turns the hand tracker's output into smooth pen strokes."""

import time
import tkinter as tk

from pinch_to_draw.filters import Follower, OneEuro2D, trim_tail
from pinch_to_draw.geometry import flatten, thin_points
from pinch_to_draw.theme import BAR_EDGE, FG, FREEHAND_TOOLS, UI_FONT
from pinch_to_draw.widgets import PASSIVE, floating_window
from pinch_to_draw.win32 import primary_screen_size, set_exstyle

FRAME_MS = 16  # ~60 updates a second, twice the camera rate
TAIL_SECONDS = 0.12  # stroke end drawn while the fingers were opening


class PointerEvent:
    """Stands in for a mouse event when the webcam does the drawing."""

    def __init__(self, x, y):
        self.x, self.y, self.state = x, y, 0
