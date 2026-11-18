# Contributing

Bug reports and pull requests are welcome.

## Setup

```bash
git clone https://github.com/markchweya/pinch-to-draw.git
cd pinch-to-draw
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt pytest
```

## Before you open a pull request

- Run `python -m pytest`. All tests should pass.
- Keep the maths and logic in modules that don't need Tk or a camera
  (`geometry.py`, `filters.py`, `gestures.py`, `history.py`), and add tests there.
- Try the change by hand in both Draw and Mouse mode, and with pinch drawing on.

## Project layout

| Path | What's in it |
|---|---|
| `pinch_to_draw/app.py` | The overlay windows, drawing tools and input handling |
| `pinch_to_draw/toolbar.py` | The floating toolbar |
| `pinch_to_draw/air.py` | Turns hand tracking into pen strokes |
| `pinch_to_draw/tracker.py` | Camera and MediaPipe background thread |
| `pinch_to_draw/filters.py` | 1-Euro filter, follower, tail trim |
| `pinch_to_draw/gestures.py` | Pinch detection |
| `pinch_to_draw/win32.py` | Windows window-style helpers |
| `docs/` | User guides |
