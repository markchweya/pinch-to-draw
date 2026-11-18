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

    # ------------------------------------------------------------ loop
    def _tick(self):
        if not self.tracker:
            return
        if self.tracker.error:
            err = self.tracker.error
            self.app.stop_air()
            self.app.toast(f"Camera problem: {err}", 5000)
            return
        seq, state, frame = self.tracker.latest()
        if frame is None:
            self.preview_label.config(text=self.tracker.status)
        elif seq != self.seq:
            self.seq = seq
            self._show_frame(frame)
            self._sample(state)
        self._frame()
        self.app.root.after(FRAME_MS, self._tick)

    def _show_frame(self, frame):
        from PIL import Image, ImageTk
        self.preview_img = ImageTk.PhotoImage(Image.fromarray(frame))
        self.preview_label.config(image=self.preview_img, text="")

    def _sample(self, st):
        """A new camera reading: update where the pen is heading."""
        if not st["present"]:
            self.target = None
            self.pinched = False
            self.smooth.reset()
            return
        sw, sh = primary_screen_size()
        x, y = self.smooth((st["x"] * sw, st["y"] * sh), st["t"])
        self.target = (x - self.app.vx, y - self.app.vy)
        self.pinched = st["pinch"]

    def _frame(self):
        """Every display frame: glide the pen and extend the stroke."""
        canvas = self.app.canvas
        if self.target is None:
            canvas.itemconfigure(self.cursor, state="hidden")
            self.follow.reset()
            if self.down:
                self._release()
            return
        x, y = self.follow.step(self.target)
        r = self.app.px(10)
        colour = self.app.color
        canvas.coords(self.cursor, x - r, y - r, x + r, y + r)
        canvas.itemconfigure(self.cursor, state="normal", outline=colour,
                             fill=colour if self.pinched else "")
        canvas.tag_raise(self.cursor)
        if self.pinched and not self.down:
            if self.app.tool == "text":
                self.app.set_tool("pen")
            self.down = True
            self.trail = [(time.monotonic(), x, y)]
            self.app.on_press(PointerEvent(x, y))
        elif self.pinched:
            self.trail.append((time.monotonic(), x, y))
            self.app.on_drag(PointerEvent(x, y))
        elif self.down:
            self._release()

    def _release(self):
        """Finish the stroke without the hook drawn while the fingers opened."""
        self.down = False
        app = self.app
        points = trim_tail(self.trail, TAIL_SECONDS)
        self.trail = []
        if points and app.current and app.tool in FREEHAND_TOOLS:
            canvas, item = app.current
            pts = thin_points(points)
            if len(pts) < 2:
                pts = pts * 2
            canvas.coords(item, *flatten(pts))
        elif points and app.current:
            app.on_drag(PointerEvent(*points[-1]))
        x, y = points[-1] if points else (0, 0)
        app.on_release(PointerEvent(x, y))
