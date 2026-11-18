from pinch_to_draw.gestures import PinchDetector, pinch_gap, pinch_point


def hand(thumb, index):
    pts = [(0.5, 0.5)] * 21
    pts[0] = (0.5, 0.9)  # wrist
    pts[9] = (0.5, 0.5)  # middle knuckle -> palm length 0.4
    pts[4], pts[8] = thumb, index
    return pts


def test_pinch_gap_is_relative_to_palm():
    assert abs(pinch_gap(hand((0.4, 0.3), (0.6, 0.3))) - 0.5) < 1e-9


def test_pinch_point_is_midpoint():
    x, y = pinch_point(hand((0.4, 0.2), (0.6, 0.4)))
    assert abs(x - 0.5) < 1e-9 and abs(y - 0.3) < 1e-9


def test_needs_two_closed_frames_to_pinch():
    d = PinchDetector()
    assert d.update(0.1) is False
    assert d.update(0.1) is True


def test_hysteresis_ignores_gap_between_thresholds():
    d = PinchDetector()
    d.update(0.1)
    d.update(0.1)
    for _ in range(10):
        assert d.update(0.3) is True  # above close, below open: stays pinched


def test_needs_three_open_frames_to_release():
    d = PinchDetector()
    d.update(0.1)
    d.update(0.1)
    assert d.update(0.9) is True
    assert d.update(0.9) is True
    assert d.update(0.9) is False


def test_single_flicker_does_not_release():
    d = PinchDetector()
    d.update(0.1)
    d.update(0.1)
    d.update(0.9)
    assert d.update(0.1) is True
    assert d.update(0.9) is True


def test_reset():
    d = PinchDetector()
    d.update(0.1)
    d.update(0.1)
    d.reset()
    assert d.pinched is False
