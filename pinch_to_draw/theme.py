"""Colours, sizes, fonts and the tool list."""

# Pixels of exactly this colour are fully see-through on the overlay.
KEY = "#010203"

PALETTE = ["#ff3b30", "#ff9500", "#ffcc00", "#34c759",
           "#0a84ff", "#af52de", "#111111", "#ffffff"]
SIZES = [2, 4, 8, 14]

BAR_BG = "#1c1c21"
BAR_EDGE = "#3a3a44"
BAR_HOVER = "#2e2e36"
BAR_ACTIVE = "#3d3d4a"
FG = "#f2f2f5"
FG_DIM = "#9a9aa6"
ACCENT = "#0a84ff"
MOUSE_GREEN = "#30a46c"

WHITEBOARD = "#ffffff"
BLACKBOARD = "#1e1e22"
HIGHLIGHT_ALPHA = 0.42

ICON_FONT = "Segoe Fluent Icons"
SYM_FONT = "Segoe UI Symbol"
UI_FONT = "Segoe UI"

# key, label, glyph, font, keyboard shortcut
TOOLS = [
    ("pen", "Pen", "", ICON_FONT, "P"),
    ("highlighter", "Highlighter", "", ICON_FONT, "H"),
    ("line", "Line", "╱", SYM_FONT, "L"),
    ("arrow", "Arrow", "↗", SYM_FONT, "A"),
    ("rect", "Rectangle", "▭", SYM_FONT, "R"),
    ("oval", "Ellipse", "◯", SYM_FONT, "O"),
    ("text", "Text", "", ICON_FONT, "T"),
    ("eraser", "Eraser", "", ICON_FONT, "E"),
]

TOOL_SHORTCUTS = {shortcut.lower(): key for key, _, _, _, shortcut in TOOLS}
FREEHAND_TOOLS = ("pen", "highlighter")
