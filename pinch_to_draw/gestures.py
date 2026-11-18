"""Turns hand landmarks into a pinch point and a pinched / open state."""

from pinch_to_draw.geometry import distance

THUMB_TIP, INDEX_TIP, WRIST, MIDDLE_KNUCKLE = 4, 8, 0, 9


def pinch_gap(points):
    """Gap between thumb and index fingertips, relative to palm length, so it
    reads the same whether your hand is near the camera or far away."""
    palm = distance(points[WRIST], points[MIDDLE_KNUCKLE]) or 1e-6
    return distance(points[THUMB_TIP], points[INDEX_TIP]) / palm


def pinch_point(points):
    """Midpoint of thumb and index tips: stays put as the fingers close."""
    (tx, ty), (ix, iy) = points[THUMB_TIP], points[INDEX_TIP]
    return (tx + ix) / 2, (ty + iy) / 2


class PinchDetector:
    """Decides pinched / open with hysteresis and a few frames of patience,
    so a flickering measurement does not start and stop strokes."""

    def __init__(self, close_below=0.25, open_above=0.40, frames_to_close=2,
                 frames_to_open=3):
        self.close_below = close_below
        self.open_above = open_above
        self.frames_to_close = frames_to_close
        self.frames_to_open = frames_to_open
        self.reset()

    def reset(self):
        self.pinched = False
        self._closed = 0
        self._opened = 0

    def update(self, gap):
        threshold = self.open_above if self.pinched else self.close_below
        if gap < threshold:
            self._closed, self._opened = self._closed + 1, 0
        else:
            self._closed, self._opened = 0, self._opened + 1
        if not self.pinched and self._closed >= self.frames_to_close:
            self.pinched = True
        elif self.pinched and self._opened >= self.frames_to_open:
            self.pinched = False
        return self.pinched
