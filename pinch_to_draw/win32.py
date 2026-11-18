"""Thin ctypes helpers for the Windows window tricks the overlay relies on."""

import ctypes
import ctypes.wintypes as wt

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_LAYERED = 0x00080000
WS_EX_NOACTIVATE = 0x08000000

HWND_TOPMOST = -1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010

user32.GetWindowLongPtrW.restype = ctypes.c_ssize_t
user32.GetWindowLongPtrW.argtypes = [wt.HWND, ctypes.c_int]
user32.SetWindowLongPtrW.restype = ctypes.c_ssize_t
user32.SetWindowLongPtrW.argtypes = [wt.HWND, ctypes.c_int, ctypes.c_ssize_t]
user32.SetWindowPos.argtypes = [wt.HWND, wt.HWND, ctypes.c_int, ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_uint]


def enable_dpi_awareness():
    """Use real pixels on scaled displays. Must run before Tk starts."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # per-monitor aware
    except Exception:
        try:
            user32.SetProcessDPIAware()
        except Exception:
            pass


def hwnd_of(win):
    """The native handle of a Tk toplevel window."""
    return wt.HWND(int(win.wm_frame(), 16))


def set_exstyle(win, add=0, remove=0):
    """Add and/or remove extended window style bits."""
    h = hwnd_of(win)
    style = user32.GetWindowLongPtrW(h, GWL_EXSTYLE)
    user32.SetWindowLongPtrW(h, GWL_EXSTYLE, (style | add) & ~remove)


def set_click_through(win, on):
    """Let mouse clicks fall through the window to whatever is behind it."""
    if on:
        set_exstyle(win, add=WS_EX_TRANSPARENT | WS_EX_LAYERED)
    else:
        set_exstyle(win, remove=WS_EX_TRANSPARENT)


def virtual_screen():
    """(x, y, width, height) of the rectangle covering every monitor."""
    return (user32.GetSystemMetrics(76), user32.GetSystemMetrics(77),
            user32.GetSystemMetrics(78), user32.GetSystemMetrics(79))


def primary_screen_size():
    """(width, height) of the main monitor."""
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
