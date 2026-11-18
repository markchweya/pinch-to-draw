"""System-wide hotkeys that work even when another app has focus."""

import ctypes
import ctypes.wintypes as wt
import threading

from pinch_to_draw.win32 import kernel32, user32

WM_HOTKEY = 0x0312
WM_QUIT = 0x0012
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_NOREPEAT = 0x4000


class HotkeyThread(threading.Thread):
    """Registers hotkeys and forwards each press, by name, to a queue.

    `bindings` is a list of (modifiers, virtual_key, name). Hotkeys another
    program already owns end up in `failed` instead of raising.
    """

    def __init__(self, bindings, out_queue):
        super().__init__(daemon=True)
        self.bindings = bindings
        self.out = out_queue
        self.failed = []
        self.ready = threading.Event()
        self.tid = None

    def run(self):
        self.tid = kernel32.GetCurrentThreadId()
        for i, (mods, vk, name) in enumerate(self.bindings, start=1):
            if not user32.RegisterHotKey(None, i, mods | MOD_NOREPEAT, vk):
                self.failed.append(name)
        self.ready.set()
        msg = wt.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_HOTKEY and 1 <= msg.wParam <= len(self.bindings):
                self.out.put(self.bindings[msg.wParam - 1][2])
        for i in range(1, len(self.bindings) + 1):
            user32.UnregisterHotKey(None, i)

    def stop(self):
        if self.tid:
            user32.PostThreadMessageW(self.tid, WM_QUIT, 0, 0)
