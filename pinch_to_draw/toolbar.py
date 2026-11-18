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

    def _add_tools(self):
        self.tool_btns = {}
        for key, label, glyph, font, shortcut in TOOLS:
            self.tool_btns[key] = self._button(glyph, font, f"{label}  ({shortcut})",
                                               lambda k=key: self.app.set_tool(k))

    def _dot_canvas(self):
        d = self.app.px(20)
        c = tk.Canvas(self.bar, width=d, height=d, bg=BAR_BG, highlightthickness=0,
                      cursor="hand2")
        c.pack(side="left", padx=self.app.px(2))
        return c

    def _add_swatches(self):
        self.swatches = []
        for i, colour in enumerate(PALETTE):
            c = self._dot_canvas()
            c.bind("<ButtonRelease-1>", lambda e, col=colour: self.app.set_color(col))
            self.app.tooltip.attach(c, f"Colour  ({i + 1})")
            self.swatches.append((c, colour))

    def _add_sizes(self):
        self.size_btns = []
        for i in range(len(SIZES)):
            c = self._dot_canvas()
            c.bind("<ButtonRelease-1>", lambda e, i=i: self.app.set_size(i))
            self.app.tooltip.attach(c, "Thickness  ([ and ])")
            self.size_btns.append(c)

    def _add_actions(self):
        app = self.app
        self._button("", ICON_FONT, "Undo  (Ctrl+Z)", app.undo)
        self._button("", ICON_FONT, "Redo  (Ctrl+Y)", app.redo)
        self._button("", ICON_FONT, "Clear all  (Delete / Ctrl+Alt+C)", app.clear)
        self._sep()
        self.white_btn = self._button("□", SYM_FONT, "Whiteboard  (W)",
                                      lambda: app.set_board("white"))
        self.black_btn = self._button("■", SYM_FONT, "Blackboard  (B)",
                                      lambda: app.set_board("black"))
        self.hide_btn = self._button("", ICON_FONT, "Hide / show ink  (Ctrl+Alt+H)",
                                     app.toggle_hidden)
        self.air_btn = self._button("", ICON_FONT,
                                    "Pinch to draw with the webcam  (Ctrl+Alt+A)",
                                    app.toggle_air)
        self._button("", ICON_FONT, "Save screenshot to Pictures\\PinchToDraw",
                     app.screenshot)
        close = self._button("", ICON_FONT, "Quit  (Ctrl+Alt+Q)", app.quit, size=11)
        close.pack_configure(padx=(self.app.px(4), 0))

    def _place(self):
        self.win.update_idletasks()
        sw, _ = primary_screen_size()
        self.win.geometry(f"+{(sw - self.win.winfo_reqwidth()) // 2}+{self.app.px(12)}")

    def _grip_press(self, e):
        self._grip = (e.x_root - self.win.winfo_x(), e.y_root - self.win.winfo_y())

    def _grip_drag(self, e):
        self.win.geometry(f"+{e.x_root - self._grip[0]}+{e.y_root - self._grip[1]}")

    # ------------------------------------------------------------ state
    def refresh(self):
        app = self.app
        for key, button in self.tool_btns.items():
            button.set_active(key == app.tool)
        d = app.px(20)
        for c, colour in self.swatches:
            c.delete("all")
            if colour == app.color:
                c.create_oval(1, 1, d - 1, d - 1, outline=FG, width=2)
            c.create_oval(5, 5, d - 5, d - 5, fill=colour, outline="#55555f")
        for i, c in enumerate(self.size_btns):
            c.delete("all")
            if i == app.size_idx:
                c.create_rectangle(0, 0, d, d, fill=BAR_ACTIVE, outline="")
            r = max(1.5, SIZES[i] * 0.6) * app.scale
            c.create_oval(d / 2 - r, d / 2 - r, d / 2 + r, d / 2 + r, fill=FG, outline="")
        self.white_btn.set_active(app.board == "white")
        self.black_btn.set_active(app.board == "black")
        self.hide_btn.config(text="" if app.ink_hidden else "")
        self.air_btn.set_active(app.air is not None)
        if app.draw_mode:
            self.mode_btn.config(text="✎  Draw", bg=ACCENT)
        else:
            self.mode_btn.config(text="↖  Mouse", bg=MOUSE_GREEN)
