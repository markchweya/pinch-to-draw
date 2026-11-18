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


class BarButton(tk.Label):
    """A flat icon button with hover and active states."""

    def __init__(self, parent, tooltip, glyph, font, tip, command, size=13):
        super().__init__(parent, text=glyph, font=(font, size), bg=BAR_BG, fg=FG,
                         width=2, padx=4, pady=4, cursor="hand2")
        self.active = False
        self.command = command
        self.bind("<Enter>", lambda e: self.config(bg=BAR_ACTIVE if self.active else BAR_HOVER))
        self.bind("<Leave>", lambda e: self.config(bg=BAR_ACTIVE if self.active else BAR_BG))
        self.bind("<ButtonRelease-1>", lambda e: self.command())
        tooltip.attach(self, tip)

    def set_active(self, on):
        self.active = on
        self.config(bg=BAR_ACTIVE if on else BAR_BG, fg=ACCENT if on else FG)


class Toast:
    """A short message that appears under the toolbar and fades away."""

    def __init__(self, root, anchor):
        self.root = root
        self.anchor = anchor  # window the toast sits under
        self.win = floating_window(root)
        self.win.attributes("-alpha", 0.92)
        self.label = tk.Label(self.win, bg="#000000", fg=FG, font=(UI_FONT, 10),
                              padx=14, pady=7)
        self.label.pack()
        self.win.withdraw()
        self.job = None
        root.update_idletasks()
        set_exstyle(self.win, add=PASSIVE)

    def show(self, text, ms=1800):
        self.label.config(text=text)
        self.win.update_idletasks()
        a = self.anchor
        x = a.winfo_x() + a.winfo_width() // 2 - self.win.winfo_reqwidth() // 2
        y = a.winfo_y() + a.winfo_height() + 8
        self.win.geometry(f"+{x}+{y}")
        self.win.deiconify()
        self.win.lift()
        if self.job:
            self.root.after_cancel(self.job)
        self.job = self.root.after(ms, self.win.withdraw)

    def hide(self):
        self.win.withdraw()
