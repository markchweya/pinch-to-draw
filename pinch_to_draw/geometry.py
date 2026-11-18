"""Small pure-math helpers (no Tk, no camera), easy to unit test."""

import math


def clamp(v, lo=0.0, hi=1.0):
    return lo if v < lo else hi if v > hi else v
