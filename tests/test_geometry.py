import math

from pinch_to_draw.geometry import (clamp, distance, flatten, map_to_region, snap_45,
                                    square_corner, thin_points)


def test_clamp():
    assert clamp(-1) == 0.0 and clamp(2) == 1.0 and clamp(0.3) == 0.3


def test_snap_45_horizontal():
    x, y = snap_45(0, 0, 100, 10)
    assert math.isclose(y, 0, abs_tol=1e-9) and x > 99


def test_snap_45_diagonal():
    x, y = snap_45(0, 0, 100, 90)
    assert math.isclose(x, y, rel_tol=1e-9)


def test_square_corner_keeps_direction():
    assert square_corner(10, 10, 0, 40) == (-20, 40)


def test_map_to_region_centre_and_clamp():
    region = (0.2, 0.2, 0.8, 0.8)
    x, y = map_to_region(0.5, 0.5, region)
    assert math.isclose(x, 0.5) and math.isclose(y, 0.5)
    assert map_to_region(0.0, 1.0, region) == (0.0, 1.0)


def test_distance():
    assert distance((0, 0), (3, 4)) == 5


def test_flatten():
    assert flatten([(1, 2), (3, 4)]) == [1, 2, 3, 4]


def test_thin_points_removes_tiny_steps_but_keeps_ends():
    pts = [(0, 0), (0.5, 0), (1, 0), (5, 0), (5.2, 0)]
    assert thin_points(pts, 2.0) == [(0, 0), (5, 0), (5.2, 0)]


def test_thin_points_short_input():
    assert thin_points([(1, 1)]) == [(1, 1)]
