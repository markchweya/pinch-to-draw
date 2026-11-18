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


class AirDrawing:
    def __init__(self, app):
        self.app = app
        self.tracker = None
        self.preview_win = None
        self.cursor = app.canvas.create_oval(0, 0, 0, 0, width=2, state="hidden",
                                             tags=("ui",))
        self.smooth = OneEuro2D(min_cutoff=1.0, beta=0.007)
        self.follow = Follower(rate=0.5)
        self._reset()

    def _reset(self):
        self.seq = -1
        self.target = None
        self.pinched = False
        self.down = False
        self.trail = []
        self.smooth.reset()
        self.follow.reset()

    @property
    def active(self):
        return self.tracker is not None

    # ------------------------------------------------------------ on / off
    def start(self):
        try:
            from PIL import Image, ImageTk  # noqa: F401
            from pinch_to_draw.tracker import HandTracker
        except ImportError:
            self.app.toast("Pinch to draw needs:  pip install opencv-python mediapipe pillow",
                           5000)
            return False
        self._reset()
        self.tracker = HandTracker()
        self.tracker.start()
        self._build_preview()
        self.app.root.after(FRAME_MS, self._tick)
        return True

    def stop(self):
        if self.down:
            self._release()
        if self.tracker:
            self.tracker.stop()
        self.tracker = None
        self.app.canvas.itemconfigure(self.cursor, state="hidden")
        if self.preview_win:
            self.preview_win.destroy()
            self.preview_win = None

    def _build_preview(self):
        from pinch_to_draw.tracker import PREVIEW_H, PREVIEW_W
        app = self.app
        w = self.preview_win = floating_window(app.root, bg=BAR_EDGE)
        # a blank image makes the label size itself in pixels, not characters
        self.preview_img = tk.PhotoImage(width=PREVIEW_W, height=PREVIEW_H)
        self.preview_label = tk.Label(w, bg="#000000", image=self.preview_img, fg=FG,
                                      text="Starting camera...", compound="center",
                                      font=(UI_FONT, 10))
        self.preview_label.pack(padx=1, pady=1)
        sw, sh = primary_screen_size()
        w.geometry(f"+{sw - PREVIEW_W - app.px(24)}+{sh - PREVIEW_H - app.px(70)}")
        app.root.update_idletasks()
        set_exstyle(w, add=PASSIVE)
