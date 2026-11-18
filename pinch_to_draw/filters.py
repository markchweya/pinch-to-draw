"""Smoothing for the hand-tracking signal.

The webcam gives about 30 noisy positions a second. Three steps turn that
into a smooth 60 fps pen:

1. OneEuro removes jitter while you hold still but barely lags fast moves.
2. Follower glides the on-screen pen towards each new position every
   display frame, filling the gaps between camera frames.
3. trim_tail cuts off the little hook drawn while your fingers open.
"""

import math


class OneEuro:
    """The 1-Euro filter (Casiez et al., 2012) for one value."""

    def __init__(self, min_cutoff=1.0, beta=0.007, d_cutoff=1.0):
        self.min_cutoff, self.beta, self.d_cutoff = min_cutoff, beta, d_cutoff
        self.reset()

    def reset(self):
        self.x = None
        self.dx = 0.0
        self.t = None

    @staticmethod
    def _alpha(dt, cutoff):
        tau = 1.0 / (2 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def __call__(self, x, t):
        if self.x is None:
            self.x, self.dx, self.t = x, 0.0, t
            return x
        dt = max(1e-3, t - self.t)
        self.t = t
        a_d = self._alpha(dt, self.d_cutoff)
        self.dx = a_d * (x - self.x) / dt + (1 - a_d) * self.dx
        a = self._alpha(dt, self.min_cutoff + self.beta * abs(self.dx))
        self.x = a * x + (1 - a) * self.x
        return self.x


class OneEuro2D:
    """A OneEuro filter for an (x, y) point."""

    def __init__(self, **kwargs):
        self.fx, self.fy = OneEuro(**kwargs), OneEuro(**kwargs)

    def reset(self):
        self.fx.reset()
        self.fy.reset()

    def __call__(self, point, t):
        return self.fx(point[0], t), self.fy(point[1], t)


class Follower:
    """Moves a point a fixed fraction of the way to its target each step."""

    def __init__(self, rate=0.5):
        self.rate = rate
        self.pos = None

    def reset(self):
        self.pos = None

    def step(self, target):
        if self.pos is None:
            self.pos = target
        else:
            px, py = self.pos
            self.pos = (px + (target[0] - px) * self.rate,
                        py + (target[1] - py) * self.rate)
        return self.pos


def trim_tail(trail, seconds, keep=2):
    """`trail` is [(t, x, y), ...]. Drop the samples from the last `seconds`
    (keeping at least `keep`) and return the remaining (x, y) points."""
    if not trail:
        return []
    cutoff = trail[-1][0] - seconds
    kept = [(x, y) for t, x, y in trail if t <= cutoff]
    if len(kept) < keep:
        kept = [(x, y) for _, x, y in trail[:keep]]
    return kept
