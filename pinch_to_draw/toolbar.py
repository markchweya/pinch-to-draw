"""The floating toolbar."""

import tkinter as tk

from pinch_to_draw.theme import (ACCENT, BAR_ACTIVE, BAR_BG, BAR_EDGE, FG, FG_DIM,
                                 ICON_FONT, MOUSE_GREEN, PALETTE, SIZES, SYM_FONT, TOOLS,
                                 UI_FONT)
from pinch_to_draw.widgets import BarButton, floating_window
from pinch_to_draw.win32 import (WS_EX_NOACTIVATE, WS_EX_TOOLWINDOW, primary_screen_size,
                                 set_exstyle)


class Toolbar:
    def __init__(self, app):
        self.app = app
        self.win = floating_window(app.root, bg=BAR_EDGE)
        self.bar = tk.Frame(self.win, bg=BAR_BG, padx=app.px(6), pady=app.px(4))
        self.bar.pack(padx=1, pady=1)
        self._add_grip()
        self._add_mode_button()
        self._add_tools()
        self._sep()
        self._add_swatches()
        self._sep()
        self._add_sizes()
        self._sep()
        self._add_actions()
        self._place()

    def apply_styles(self):
        set_exstyle(self.win, add=WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE)

    # ------------------------------------------------------------ building
    def _button(self, glyph, font, tip, command, **kw):
        b = BarButton(self.bar, self.app.tooltip, glyph, font, tip, command, **kw)
        b.pack(side="left")
        return b

    def _sep(self):
        tk.Frame(self.bar, bg=BAR_EDGE, width=1, height=self.app.px(22)).pack(
            side="left", padx=self.app.px(6))

    def _add_grip(self):
        grip = tk.Label(self.bar, text="⋮⋮", font=(UI_FONT, 12), bg=BAR_BG,
                        fg=FG_DIM, cursor="fleur", padx=2)
        grip.pack(side="left", padx=(0, self.app.px(4)))
        grip.bind("<ButtonPress-1>", self._grip_press)
        grip.bind("<B1-Motion>", self._grip_drag)
        self.app.tooltip.attach(grip, "Drag to move the toolbar")

    def _add_mode_button(self):
        self.mode_btn = tk.Label(self.bar, font=(UI_FONT + " Semibold", 10), fg="#ffffff",
                                 padx=self.app.px(10), pady=self.app.px(4), cursor="hand2",
                                 width=7)
        self.mode_btn.pack(side="left", padx=(0, self.app.px(6)))
        self.mode_btn.bind("<ButtonRelease-1>", lambda e: self.app.toggle_mode())
        self.app.tooltip.attach(self.mode_btn, "Switch Draw / Mouse mode  (Ctrl+Alt+D)")
