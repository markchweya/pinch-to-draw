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
