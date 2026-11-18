"""The overlay: three stacked see-through windows plus the toolbar.

  catcher   almost invisible, receives the mouse in Draw mode (or shows the
            whiteboard / blackboard)
  highlight translucent layer for highlighter strokes, never receives clicks
  ink       solid strokes; colour-keyed so everything else is see-through
"""

import os
import queue
import time
import tkinter as tk

from pinch_to_draw import win32
from pinch_to_draw.air import AirDrawing
from pinch_to_draw.geometry import snap_45, square_corner
from pinch_to_draw.history import History
from pinch_to_draw.hotkeys import HotkeyThread, ctrl_alt
from pinch_to_draw.theme import (BLACKBOARD, HIGHLIGHT_ALPHA, KEY, PALETTE, SIZES,
                                 TOOL_SHORTCUTS, UI_FONT, WHITEBOARD)
from pinch_to_draw.toolbar import Toolbar
from pinch_to_draw.widgets import Toast, Tooltip
from pinch_to_draw.win32 import (WS_EX_LAYERED, WS_EX_TOOLWINDOW, WS_EX_TRANSPARENT,
                                 set_click_through, set_exstyle)

SHIFT, CONTROL = 0x0001, 0x0004
CATCHER_ALPHA = 0.01  # invisible to the eye, but still catches the mouse

HOTKEYS = [
    ctrl_alt("D", "toggle"),
    ctrl_alt("Z", "undo"),
    ctrl_alt("C", "clear"),
    ctrl_alt("H", "hide"),
    ctrl_alt("W", "board"),
    ctrl_alt("A", "air"),
    ctrl_alt("Q", "quit"),
]


class PinchToDraw:
    def __init__(self):
        win32.enable_dpi_awareness()
        self.root = tk.Tk()
        self.root.withdraw()
        self.scale = self.root.winfo_fpixels("1i") / 96.0
        self.vx, self.vy, self.vw, self.vh = win32.virtual_screen()

        self.tool, self.color, self.size_idx = "pen", PALETTE[0], 1
        self.draw_mode = True
        self.ink_hidden = False
        self.board = None  # None, "white" or "black"
        self.history = History()
        self.current = None  # (canvas, item) being drawn
        self.text = None  # (item, string) while typing
        self.erased = []
        self.points = []

        self._build_layers()
        self.tooltip = Tooltip(self.root)
        self.toolbar = Toolbar(self)
        self.toaster = Toast(self.root, self.toolbar.win)
        self.air = None
        self.air_drawing = AirDrawing(self)
        self._apply_styles()

        self.root.bind_all("<Key>", self.on_key)
        self.hk_queue = queue.Queue()
        self.hotkeys = HotkeyThread(HOTKEYS, self.hk_queue)
        self.hotkeys.start()
        self.hotkeys.ready.wait(2)

        self.set_mode(True)
        msg = "Draw mode  -  Esc or Ctrl+Alt+D for Mouse mode  -  Ctrl+Alt+A to pinch-draw"
        if self.hotkeys.failed:
            msg += f"   (hotkeys taken by another app: {', '.join(self.hotkeys.failed)})"
        self.toast(msg, 5000)
        self.root.after(50, self.poll_hotkeys)
        self.root.after(1500, self.keep_on_top)

    # ------------------------------------------------------------ windows
    def _layer(self, bg):
        w = tk.Toplevel(self.root, bg=bg)
        w.overrideredirect(True)
        w.geometry(f"{self.vw}x{self.vh}+{self.vx}+{self.vy}")
        w.attributes("-topmost", True)
        return w

    def _build_layers(self):
        self.catcher = self._layer("#000000")
        self.catcher.attributes("-alpha", CATCHER_ALPHA)
        self.catch_canvas = tk.Canvas(self.catcher, bg="#000000", highlightthickness=0,
                                      cursor="crosshair")
        self.catch_canvas.pack(fill="both", expand=True)

        self.hl_win = self._layer(KEY)
        self.hl_win.attributes("-transparentcolor", KEY)
        self.hl_win.attributes("-alpha", HIGHLIGHT_ALPHA)
        self.hl_canvas = tk.Canvas(self.hl_win, bg=KEY, highlightthickness=0)
        self.hl_canvas.pack(fill="both", expand=True)

        self.ink_win = self._layer(KEY)
        self.ink_win.attributes("-transparentcolor", KEY)
        self.canvas = tk.Canvas(self.ink_win, bg=KEY, highlightthickness=0,
                                cursor="crosshair")
        self.canvas.pack(fill="both", expand=True)
        self.eraser_ring = self.canvas.create_oval(0, 0, 0, 0, outline="#888888", width=1,
                                                   dash=(3, 2), state="hidden", tags=("ui",))

        for c in (self.catch_canvas, self.canvas):
            c.bind("<ButtonPress-1>", self.on_press)
            c.bind("<B1-Motion>", self.on_drag)
            c.bind("<ButtonRelease-1>", self.on_release)
            c.bind("<Motion>", self.on_move)

    def _apply_styles(self):
        self.root.update_idletasks()
        for w in (self.catcher, self.hl_win, self.ink_win):
            set_exstyle(w, add=WS_EX_TOOLWINDOW | WS_EX_LAYERED)
        set_exstyle(self.hl_win, add=WS_EX_TRANSPARENT)
        self.toolbar.apply_styles()

    def stacking(self):
        """Bottom to top."""
        preview = self.air_drawing.preview_win
        return [self.catcher, self.hl_win, self.ink_win, preview, self.toolbar.win,
                self.toaster.win]

    def keep_on_top(self):
        win32.raise_topmost(self.stacking())
        self.root.after(1500, self.keep_on_top)

    def px(self, n):
        return max(1, int(round(n * self.scale)))

    def toast(self, text, ms=1800):
        self.toaster.show(text, ms)

    def refresh(self):
        self.toolbar.refresh()

    # ------------------------------------------------------------ state
    def toggle_mode(self):
        self.set_mode(not self.draw_mode)

    def set_mode(self, draw):
        self.finish_text()
        self.draw_mode = draw
        if draw:
            if self.ink_hidden:
                self.toggle_hidden()
            self.catcher.deiconify()
            set_exstyle(self.catcher, add=WS_EX_TOOLWINDOW | WS_EX_LAYERED)
            set_click_through(self.ink_win, False)
            win32.raise_topmost(self.stacking())
            self.ink_win.focus_force()
        else:
            if self.board:
                self.set_board(self.board)  # boards only make sense while drawing
            self.catcher.withdraw()
            set_click_through(self.ink_win, True)
            self.canvas.itemconfigure(self.eraser_ring, state="hidden")
        self.refresh()

    def set_tool(self, tool):
        self.finish_text()
        self.tool = tool
        if not self.draw_mode and not self.air:
            self.set_mode(True)
        cursor = {"text": "xterm", "eraser": "dotbox"}.get(tool, "crosshair")
        self.canvas.config(cursor=cursor)
        self.catch_canvas.config(cursor=cursor)
        if tool != "eraser":
            self.canvas.itemconfigure(self.eraser_ring, state="hidden")
        self.refresh()

    def set_color(self, colour):
        self.color = colour
        if self.text:
            self.canvas.itemconfigure(self.text[0], fill=colour)
        if self.tool == "eraser":
            self.set_tool("pen")
        self.refresh()

    def set_size(self, i):
        self.size_idx = max(0, min(len(SIZES) - 1, i))
        self.refresh()

    def width(self):
        return SIZES[self.size_idx] * self.scale

    def set_board(self, kind):
        self.board = None if self.board == kind else kind
        if self.board:
            if not self.draw_mode:
                self.set_mode(True)
            colour = WHITEBOARD if self.board == "white" else BLACKBOARD
            self.catcher.config(bg=colour)
            self.catch_canvas.config(bg=colour)
            self.catcher.attributes("-alpha", 1.0)
        else:
            self.catcher.config(bg="#000000")
            self.catch_canvas.config(bg="#000000")
            self.catcher.attributes("-alpha", CATCHER_ALPHA)
        self.refresh()

    def toggle_hidden(self):
        self.ink_hidden = not self.ink_hidden
        self.ink_win.attributes("-alpha", 0.0 if self.ink_hidden else 1.0)
        self.hl_win.attributes("-alpha", 0.0 if self.ink_hidden else HIGHLIGHT_ALPHA)
        if self.ink_hidden and self.draw_mode:
            self.set_mode(False)
        self.refresh()
        self.toast("Ink hidden" if self.ink_hidden else "Ink visible")

    # ------------------------------------------------------------ drawing
    def eraser_radius(self):
        return max(8, SIZES[self.size_idx] * 2.5) * self.scale

    def on_move(self, e):
        if self.tool == "eraser" and self.draw_mode:
            r = self.eraser_radius()
            self.canvas.coords(self.eraser_ring, e.x - r, e.y - r, e.x + r, e.y + r)
            self.canvas.itemconfigure(self.eraser_ring, state="normal")
            self.canvas.tag_raise(self.eraser_ring)

    def on_press(self, e):
        x, y = e.x, e.y
        self.start = (x, y)
        tool, colour, w = self.tool, self.color, self.width()
        self.finish_text()
        if tool == "text":
            self.start_text(x, y)
        elif tool == "eraser":
            self.erased = []
            self.erase_at(x, y)
        elif tool == "pen":
            self.points = [x, y, x + 0.5, y + 0.5]
            self.current = (self.canvas, self.canvas.create_line(
                *self.points, fill=colour, width=w, capstyle="round", joinstyle="round",
                smooth=True, splinesteps=8))
        elif tool == "highlighter":
            self.points = [x, y, x + 0.5, y + 0.5]
            self.current = (self.hl_canvas, self.hl_canvas.create_line(
                *self.points, fill=colour, width=w * 4 + 6 * self.scale, capstyle="round",
                joinstyle="round", smooth=True, splinesteps=8))
        elif tool in ("line", "arrow"):
            opts = dict(fill=colour, width=w, capstyle="round")
            if tool == "arrow":
                a = 6 + w * 2.2
                opts.update(arrow="last", arrowshape=(a, a * 1.15, a * 0.45))
            self.current = (self.canvas, self.canvas.create_line(x, y, x, y, **opts))
        elif tool == "rect":
            self.current = (self.canvas, self.canvas.create_rectangle(
                x, y, x, y, outline=colour, width=w))
        elif tool == "oval":
            self.current = (self.canvas, self.canvas.create_oval(
                x, y, x, y, outline=colour, width=w))
