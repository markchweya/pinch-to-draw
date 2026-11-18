"""Turns hand landmarks into a pinch point and a pinched / open state."""

from pinch_to_draw.geometry import distance

THUMB_TIP, INDEX_TIP, WRIST, MIDDLE_KNUCKLE = 4, 8, 0, 9


def pinch_gap(points):
    """Gap between thumb and index fingertips, relative to palm length, so it
    reads the same whether your hand is near the camera or far away."""
    palm = distance(points[WRIST], points[MIDDLE_KNUCKLE]) or 1e-6
    return distance(points[THUMB_TIP], points[INDEX_TIP]) / palm
