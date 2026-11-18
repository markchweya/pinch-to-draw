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


def square_corner(x0, y0, x, y):
    """Corner that makes the box from (x0, y0) a square (for squares and circles)."""
    side = max(abs(x - x0), abs(y - y0))
    return (x0 + side * (1 if x >= x0 else -1),
            y0 + side * (1 if y >= y0 else -1))


def map_to_region(x, y, region):
    """Stretch the part of the camera picture inside `region` (left, top,
    right, bottom, all 0..1) to the whole 0..1 range, clamped."""
    left, top, right, bottom = region
    return (clamp((x - left) / (right - left)),
            clamp((y - top) / (bottom - top)))
