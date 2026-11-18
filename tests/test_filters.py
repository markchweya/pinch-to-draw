from pinch_to_draw.filters import Follower, OneEuro, OneEuro2D, trim_tail


def test_one_euro_first_value_passes_through():
    f = OneEuro()
    assert f(10.0, 0.0) == 10.0


def test_one_euro_damps_jitter():
    f = OneEuro(min_cutoff=1.0, beta=0.0)
    out = [f(100 + (5 if i % 2 else -5), i / 30) for i in range(60)]
    spread = max(out[30:]) - min(out[30:])
    assert spread < 4  # raw input jumps by 10 every frame


def test_one_euro_follows_a_steady_move():
    f = OneEuro(min_cutoff=1.0, beta=0.01)
    for i in range(60):
        last = f(i * 20.0, i / 30)
    assert abs(last - 59 * 20.0) < 40


def test_one_euro_reset_forgets_history():
    f = OneEuro()
    f(0.0, 0.0)
    f.reset()
    assert f(500.0, 1.0) == 500.0


def test_one_euro_2d_filters_both_axes():
    f = OneEuro2D()
    assert f((3.0, 4.0), 0.0) == (3.0, 4.0)


def test_follower_starts_at_target_then_closes_gap():
    fol = Follower(rate=0.5)
    assert fol.step((0.0, 0.0)) == (0.0, 0.0)
    assert fol.step((10.0, 20.0)) == (5.0, 10.0)
    assert fol.step((10.0, 20.0)) == (7.5, 15.0)


def test_follower_reset():
    fol = Follower()
    fol.step((1.0, 1.0))
    fol.reset()
    assert fol.step((9.0, 9.0)) == (9.0, 9.0)


def test_trim_tail_drops_recent_samples():
    trail = [(t / 10, t, t) for t in range(10)]  # 0.0 .. 0.9 s
    assert trim_tail(trail, 0.25)[-1] == (6, 6)


def test_trim_tail_keeps_minimum():
    trail = [(0.0, 1, 1), (0.01, 2, 2), (0.02, 3, 3)]
    assert trim_tail(trail, 1.0) == [(1, 1), (2, 2)]


def test_trim_tail_empty():
    assert trim_tail([], 0.1) == []
