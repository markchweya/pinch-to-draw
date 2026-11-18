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


class Tooltip:
    def __init__(self, root):
        self.win = floating_window(root)
        self.win.withdraw()
        self.label = tk.Label(self.win, bg="#000000", fg=FG, font=(UI_FONT, 9),
                              padx=8, pady=3)
        self.label.pack()
        root.update_idletasks()
        set_exstyle(self.win, add=PASSIVE)

    def show(self, widget, text):
        self.label.config(text=text)
        self.win.update_idletasks()
        x = widget.winfo_rootx() + widget.winfo_width() // 2 - self.win.winfo_reqwidth() // 2
        y = widget.winfo_rooty() + widget.winfo_height() + 6
        self.win.geometry(f"+{x}+{y}")
        self.win.deiconify()
        self.win.lift()

    def hide(self):
        self.win.withdraw()

    def attach(self, widget, text):
        widget.bind("<Enter>", lambda e: self.show(widget, text), add="+")
        widget.bind("<Leave>", lambda e: self.hide(), add="+")
