"""Small Tk building blocks for the toolbar: tooltip, icon button, toast."""

import tkinter as tk

from pinch_to_draw.theme import BAR_ACTIVE, BAR_BG, BAR_HOVER, ACCENT, FG, UI_FONT
from pinch_to_draw.win32 import (WS_EX_NOACTIVATE, WS_EX_TOOLWINDOW, WS_EX_TRANSPARENT,
                                 set_exstyle)

PASSIVE = WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE | WS_EX_TRANSPARENT


def floating_window(root, **kw):
    """A borderless, always-on-top window."""
    w = tk.Toplevel(root, **kw)
    w.overrideredirect(True)
    w.attributes("-topmost", True)
    return w
