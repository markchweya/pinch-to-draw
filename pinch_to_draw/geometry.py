"""Small pure-math helpers (no Tk, no camera), easy to unit test."""

import math


def clamp(v, lo=0.0, hi=1.0):
    return lo if v < lo else hi if v > hi else v


def snap_45(x0, y0, x, y):
    """End point of a line from (x0, y0) towards (x, y), snapped to 45-degree steps."""
    step = math.pi / 4
    angle = round(math.atan2(y - y0, x - x0) / step) * step
    dist = math.hypot(x - x0, y - y0)
    return x0 + dist * math.cos(angle), y0 + dist * math.sin(angle)
